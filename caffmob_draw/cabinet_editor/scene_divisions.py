"""Divisões na cena (feature 006, T019, T020; D-03, D-06, D-10).

Cada divisão é um `CabinetPart` ("Divisória N") filho direto da raiz do módulo, com `btm_division` e
`btm_component = 'DIV'`. Fica fora das peças que as bibliotecas reconstroem (nenhum `hb_part_role`, nenhum filho de
bay), entra no plano de corte pelo caminho das peças reais e aparece no editor como divisória.

- Material e espessura: os do componente **Divisória** do Configurador de Dimensões na linha do módulo (`btm_line`),
  salvo sobrescrita na própria divisão (RN-10, RN-12).
- `reflow(context, root)`: recalcula subvãos e chapas a partir dos vãos-raiz do adaptador. Sai sem custo quando os
  vãos e as divisões não mudaram (assinatura gravada na raiz).

Orientação da peça (medida no Blender 5.2): sem rotação, ela cresce em +X (comprimento), +Y (largura) e +Z
(espessura); girada −90° em Y e com `Mirror Z`, cresce em +X (espessura), +Y (largura) e +Z (comprimento).
"""

import json
import math

from mathutils import Matrix  # type: ignore

from .. import compat
from ..customize import adapters
from ..customize.adapters import common
from ..data import dimension_schema as schema
from . import divisions as dv

NAME = "Divisória"
COMPONENT = 'DIV'
COMPONENT_PROP = 'btm_component'
SIGNATURE_PROP = 'btm_division_sig'
DEFAULT_LINE = {'FRAMELESS': 'COZ', 'FACE_FRAME': 'COZ', 'CLOSETS': 'DOR', 'BTM': 'COZ'}


# Configurador ------------------------------------------------------------------------------------------------
def line_of(root):
    from ..selection import classify
    return str(root.get('btm_line') or DEFAULT_LINE.get(classify.module_library(root), 'COZ'))


def configured(scene, root):
    """(material, espessura em m) do componente Divisória na linha do módulo."""
    from ..standards import api
    line = line_of(root)
    material = api.get_value(scene, schema.sheet_key(line, COMPONENT, 'material')) or 'MDF'
    thickness = api.get_value_m(scene, schema.sheet_key(line, COMPONENT, 'thickness')) or 0.015
    return str(material), float(thickness)


# Leitura -----------------------------------------------------------------------------------------------------
def objects(root):
    return sorted((o for o in root.children if getattr(o, 'btm_division', None) is not None
                   and o.btm_division.is_division), key=lambda o: o.name)


def read(root):
    """Divisões gravadas no módulo como dicionários (valores crus: espessura 0 = do Configurador)."""
    return [o.btm_division.to_dict() for o in objects(root)]


def to_core(data, default_thickness):
    values = dict(data)
    if values.get('kind') in dv.NO_PART:
        values['thickness'] = 0.0                       # divide sem chapa (feature 015)
    else:
        values['thickness'] = float(values.get('thickness') or 0.0) or default_thickness
    return dv.from_dict(values)


def core(scene, root, data=None):
    _material, thickness = configured(scene, root)
    return [to_core(d, thickness) for d in (read(root) if data is None else data)]


def roots(context, root):
    return common.call(adapters.for_root(root), 'inner_spaces', context, root)


def names(root):
    return {o.btm_division.uid: o.name for o in objects(root)}


# Escrita -----------------------------------------------------------------------------------------------------
def _borrow_material(root, obj):
    """Mesma face da caixa: material da primeira peça da estrutura (ou o slot 0 da malha do `btm`)."""
    source = None
    parts = common.call(adapters.for_root(root), 'structure_parts', root)
    for role in ('LEFT', 'RIGHT', 'BOTTOM', 'TOP'):
        if parts.get(role):
            mod = common.gn_modifier(parts[role][0], 'GeoNodeCutpart')
            source = compat.try_get_gn_input(mod, 'Top Surface', None) if mod is not None else None
            if source is not None:
                break
    if source is None and root.type == 'MESH' and root.data.materials:
        source = root.data.materials[0]
    if source is not None:
        common.set_cutpart_material(obj, source)


def _create(context, root, data):
    from ..product_libraries.frameless.types_frameless import CabinetPart
    part = CabinetPart()
    index = len(objects(root)) + 1
    part.create(f"{NAME} {index}")
    obj = part.obj
    obj.parent = root
    obj.matrix_parent_inverse = Matrix.Identity(4)
    obj[COMPONENT_PROP] = COMPONENT
    obj.btm_division.from_dict(data)
    _borrow_material(root, obj)
    for collection in root.users_collection:
        if obj.name not in collection.objects:
            collection.objects.link(obj)
    for collection in list(obj.users_collection):
        if collection not in root.users_collection:
            collection.objects.unlink(obj)
    return obj


def _delete(obj):
    import bpy  # type: ignore
    bpy.data.objects.remove(obj, do_unlink=True)


def apply(context, root, wanted):
    """Deixa as divisões do módulo iguais a `wanted` (lista de dicionários) e reposiciona."""
    existing = {o.btm_division.uid: o for o in objects(root)}
    keep = set()
    for data in wanted:
        obj = existing.get(data['uid'])
        if obj is None:
            obj = _create(context, root, data)
        else:
            obj.btm_division.from_dict(data)
        keep.add(data['uid'])
    for uid, obj in existing.items():
        if uid not in keep:
            _delete(obj)
    return reflow(context, root, force=True)


def _place(obj, box, orientation, material):
    mod = common.gn_modifier(obj, 'GeoNodeCutpart')
    size = [box.hi[i] - box.lo[i] for i in range(3)]
    obj.location = box.lo
    if orientation == dv.VERTICAL:
        obj.rotation_euler = (0.0, math.radians(-90.0), 0.0)
        values = {'Length': size[2], 'Width': size[1], 'Thickness': size[0], 'Mirror Y': False, 'Mirror Z': True}
    else:
        obj.rotation_euler = (0.0, 0.0, 0.0)
        values = {'Length': size[0], 'Width': size[1], 'Thickness': size[2], 'Mirror Y': False, 'Mirror Z': False}
    if mod is not None:
        for name, value in values.items():
            compat.try_set_gn_input(mod, name, value)
    obj[common.RAW_MATERIAL_PROP] = material
    obj.update_tag()


def _signature(spaces, data, material, thickness):
    rounded = {k: [round(v, 6) for v in b.lo + b.hi] for k, b in spaces.items()}
    return json.dumps({"spaces": rounded, "divisions": data, "material": material, "thickness": round(thickness, 6)},
                      sort_keys=True, default=str)


def reflow(context, root, force=False):
    """Reposiciona as chapas nos subvãos atuais; devolve os uids órfãos (subvão que não existe mais)."""
    scene = context.scene
    data = read(root)
    if not data:
        if SIGNATURE_PROP in root:
            del root[SIGNATURE_PROP]
        return []
    material, thickness = configured(scene, root)
    spaces = roots(context, root)
    signature = _signature(spaces, data, material, thickness)
    if not force and root.get(SIGNATURE_PROP) == signature:
        return []
    core_divs = [to_core(d, thickness) for d in data]
    _leaves, cuts, orphans = dv.resolve(spaces, core_divs)
    by_uid = {o.btm_division.uid: o for o in objects(root)}
    for division in core_divs:
        obj = by_uid.get(division.uid)
        if obj is None or division.uid not in cuts:
            continue
        box = dv.place(cuts[division.uid][1], division)
        cab = getattr(root, 'btm_cabinet', None)
        if division.variant == dv.CORTA_SAR and division.orientation == dv.VERTICAL and cab is not None:
            box = dv.Box(box.lo, (box.hi[0], box.hi[1], float(cab.height)))   # sobe até o topo, entre os sarrafos
        _place(obj, box, division.orientation, division.material or material)
        hidden = not dv.makes_part(division)            # Invisível, Somente Divisão, Aramada (feature 015)
        obj.hide_viewport = obj.hide_render = hidden
    root[SIGNATURE_PROP] = signature
    return orphans
