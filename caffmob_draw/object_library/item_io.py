"""Salvar e inserir itens da biblioteca de objetos (feature 009, T018-T019; D-09, D-10, D-11).

Mecânica da biblioteca de módulos (003, `customize/library_io.py`): `bpy.data.libraries.write` com
`path_remap='RELATIVE_ALL'` e `fake_user=True`, miniatura de 256 px e manifesto JSON ao lado.
Contrato: `_reversa_forward/009-mira-calculo-skp-biblioteca/interfaces/object-library-item.md`.

A raiz do item é um grupo de peças (007): uma seleção solta é agrupada antes de salvar. As conversões (folha,
esquadria, agregado, peça de produção) estão nos próprios objetos e voltam ao inserir.
"""

import datetime
import json
import os
import tempfile

import bpy  # type: ignore

from ..aggregates import group
from ..data.i18n import tr
from ..library_common import thumbnail, world_box
from . import catalog, store


def _extension_package():
    return __package__.rsplit('.', 1)[0]


def user_dir(create=True):
    return bpy.utils.extension_path_user(_extension_package(), path="object_library", create=create)


def all_items():
    return store.list_items(store.BUNDLED_DIR, user_dir(create=False))


def _addon_version():
    from ..customize import library_io
    return library_io._addon_version()


def tree(root):
    return [root] + list(root.children_recursive)


def root_of(obj):
    """Raiz de item que contém `obj` (ele mesmo ou um ancestral), ou None."""
    node = obj
    while node is not None:
        data = getattr(node, 'btm_object_item', None)
        if data is not None and data.is_item:
            return node
        node = node.parent
    return None


def prepare_root(objs, name):
    """Raiz para salvar: um item ou grupo já selecionado sozinho, ou um grupo novo com a seleção."""
    tops = [o for o in objs if o.parent not in objs]
    if len(tops) == 1 and (group.is_group(tops[0]) or root_of(tops[0]) is tops[0]):
        return tops[0]
    meshes = [o for o in objs if o.type == 'MESH' and o.parent not in objs]
    return group.create_group(meshes, 'PLAIN', name) if meshes else None


def features_of(objs):
    found = set()
    for obj in objs:
        if group.is_group(obj):
            found.add('FRAME' if obj.btm_group.kind == 'FRAME' else 'GROUP')
        agg = getattr(obj, 'btm_aggregate', None)
        if agg is not None and agg.is_aggregate:
            found.add('AGGREGATE')
            if getattr(agg, 'production_part', False):
                found.add('PRODUCTION_PART')
            if agg.kind == 'LEAF':
                found.add('LEAF_SLIDE' if agg.motion == 'SLIDE' else 'LEAF_SWING')
        if obj.type == 'MESH' and any(m and m.name.startswith("Textura: ") for m in obj.data.materials):
            found.add('TEXTURED')
    return [f for f in catalog.FEATURES if f in found]


def existing_names(category):
    items, _warnings = all_items()
    return [i.entry.name for i in items if i.user and i.entry.category == category]


_REF_GROUPS = ('btm_aggregate', 'btm_stick')


def _outside_refs(objs):
    """[(dono, propriedade)] dos ponteiros de objeto das conversões que apontam para fora do item."""
    inside = {o.as_pointer() for o in objs}
    owners = []
    for obj in objs:
        owners += [g for g in (getattr(obj, name, None) for name in _REF_GROUPS) if g is not None]
        grp = getattr(obj, 'btm_group', None)
        if grp is not None:
            owners += list(grp.members)
    found = []
    for owner in owners:
        for prop in owner.bl_rna.properties:
            if prop.type == 'POINTER' and getattr(prop, 'fixed_type', None) == bpy.types.Object.bl_rna:
                value = getattr(owner, prop.identifier)
                if value is not None and value.as_pointer() not in inside:
                    found.append((owner, prop.identifier, value))
    return found


class _detached:
    """Sem o pai (nem ponteiros para fora) durante a gravação: `libraries.write` expande as referências e levaria o
    pai junto (EC-08)."""

    def __init__(self, root, objs):
        self.root, self.objs = root, objs

    def __enter__(self):
        root = self.root
        self.parent, self.inverse, self.basis = root.parent, root.matrix_parent_inverse.copy(), root.matrix_basis.copy()
        if self.parent is not None:
            world = root.matrix_world.copy()
            root.parent = None
            root.matrix_world = world
        self.refs = _outside_refs(self.objs)
        for owner, name, _value in self.refs:
            setattr(owner, name, None)
        return root

    def __exit__(self, *_exc):
        for owner, name, value in self.refs:
            setattr(owner, name, value)
        if self.parent is not None:
            self.root.parent = self.parent
            self.root.matrix_parent_inverse = self.inverse
            self.root.matrix_basis = self.basis
        return False


def _pack_own_images(objs):
    """Empacota as imagens de textura própria: o item fica portátil (questions.md, pergunta 60)."""
    from .retexture import PATH_PROP
    for obj in objs:
        if obj.type != 'MESH':
            continue
        for mat in obj.data.materials:
            if mat is None or not mat.get(PATH_PROP) or mat.node_tree is None:
                continue
            for node in mat.node_tree.nodes:
                image = getattr(node, 'image', None)
                if image is not None and image.source == 'FILE' and image.packed_file is None:
                    image.pack()


def save(context, root, name, category, source="", license_text="", author="", replace_id=None, thumb=True,
         folder=None, item_id=None):
    """Grava o item (na pasta do usuário, ou em `folder`). Devolve (store.Item ou None, mensagens de erro)."""
    objs = tree(root)
    data = root.btm_object_item
    item_id = item_id or replace_id or catalog.new_item_id(name)
    data.is_item, data.item_id, data.category = True, item_id, category
    data.source, data.license = source, license_text
    lo, hi = world_box(objs)
    entry = catalog.Entry(item_id, name, category, root.name, source, author, license_text,
                          [round((hi[i] - lo[i]) * 1000.0, 1) for i in (0, 1, 2)], features_of(objs),
                          sorted({m.name for o in objs if o.type == 'MESH' for m in o.data.materials if m}),
                          datetime.datetime.now().astimezone().isoformat(timespec='seconds'), _addon_version())
    folder = folder or user_dir()
    paths = store.paths_for(folder, category, item_id)
    os.makedirs(os.path.dirname(paths["blend"]), exist_ok=True)
    written = []
    try:
        fd, tmp_blend = tempfile.mkstemp(suffix=".blend", dir=os.path.dirname(paths["blend"]))
        os.close(fd)
        written.append(tmp_blend)
        _pack_own_images(objs)
        with _detached(root, objs):
            bpy.data.libraries.write(tmp_blend, set(objs), path_remap='RELATIVE_ALL', fake_user=True)
        fd, tmp_json = tempfile.mkstemp(suffix=".json", dir=os.path.dirname(paths["json"]))
        written.append(tmp_json)            # antes de escrever: uma falha no dump também apaga o temporário
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(catalog.to_manifest(entry), handle, ensure_ascii=False, indent=1)
        os.replace(tmp_blend, paths["blend"])
        os.replace(tmp_json, paths["json"])
        written = []
    except (OSError, RuntimeError) as exc:
        for path in written:
            if os.path.exists(path):
                os.remove(path)
        return None, [tr("Não foi possível gravar o item em {}: {}").format(folder, exc)]
    if thumb:
        thumbnail(context, objs, paths["png"])
    return store.Item(entry, folder != store.BUNDLED_DIR, paths["blend"], paths["json"],
                      paths["png"] if os.path.isfile(paths["png"]) else None), []


def insert(context, item, location=None):
    """Anexa os objetos do item à coleção ativa; devolve (raiz, objetos). `ValueError` se o item estiver corrompido."""
    with bpy.data.libraries.load(item.blend, link=False) as (data_from, data_to):
        data_to.objects = list(data_from.objects)
    loaded = [obj for obj in data_to.objects if obj is not None]
    root = next((o for o in loaded if o.name == item.entry.root or o.name.split(".")[0] == item.entry.root), None)
    if root is None:
        root = next((o for o in loaded if o.parent is None and getattr(o, 'btm_object_item', None) is not None
                     and o.btm_object_item.is_item), None)
    if root is None:
        for obj in loaded:
            bpy.data.objects.remove(obj, do_unlink=True)
        raise ValueError(tr("Item corrompido: {}").format(item.entry.name))
    collection = context.collection or context.scene.collection
    for obj in loaded:
        obj.use_fake_user = False
        if obj.name not in collection.objects:
            collection.objects.link(obj)
    if location is not None:
        root.location = location
    context.view_layer.update()
    return root, loaded
