"""Montar e regenerar a escada na cena (071 D-21, D-22): Empty raiz com o spec e chapas filhas."""
import json
import uuid

import bpy
from mathutils import Matrix

from . import core
from .scene import HANDRAIL_PROP, PART_PROP, ROOT_PROP, UID_PROP, is_root

MM = 0.001


def _caixa(nome, tam):
    w, d, h = (v * MM for v in tam)
    v = [(0, 0, 0), (w, 0, 0), (w, d, 0), (0, d, 0), (0, 0, h), (w, 0, h), (w, d, h), (0, d, h)]
    f = [(0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)]
    mesh = bpy.data.meshes.new(nome)
    mesh.from_pydata(v, [], f)
    return mesh


def _material(nome):
    return bpy.data.materials.get(nome) if nome else None


def criar_raiz(context, nome="Escada"):
    raiz = bpy.data.objects.new(nome, None)
    raiz.empty_display_type = 'PLAIN_AXES'
    raiz.empty_display_size = 0.1
    (context.collection or context.scene.collection).objects.link(raiz)
    raiz[UID_PROP] = str(uuid.uuid4())
    return raiz


def limpar(raiz):
    for filho in list(raiz.children):
        if filho.get(PART_PROP) is None:
            continue
        mesh = filho.data if filho.type == 'MESH' else None
        bpy.data.objects.remove(filho, do_unlink=True)
        if mesh is not None and mesh.users == 0:
            bpy.data.meshes.remove(mesh)


def aplicar(raiz, escada):
    """Regenera as peças da escada a partir do spec, sem duplicar (RF-29). Devolve quantas chapas."""
    escada = escada.normalizada()
    limpar(raiz)
    pecas, corrimao = core.pecas(escada)
    colecoes = list(raiz.users_collection) or [bpy.context.scene.collection]
    materiais = {'frente': _material(escada.material_frente), 'corpo': _material(escada.material_corpo)}
    for peca in pecas:
        obj = bpy.data.objects.new(peca['nome'], _caixa(peca['nome'], peca['tam']))
        for colecao in colecoes:
            colecao.objects.link(obj)
        material = materiais.get(peca['material'])
        if material is not None:
            obj.data.materials.append(material)
        obj[PART_PROP] = json.dumps(dict(papel=peca['papel'], indice=peca['indice']))
        obj.parent = raiz
        obj.matrix_parent_inverse = Matrix.Identity(4)
        obj.location = tuple(v * MM for v in peca['pos'])
    if corrimao > 0:
        trilho = bpy.data.objects.new("Corrimão", None)
        for colecao in colecoes:
            colecao.objects.link(trilho)
        trilho[PART_PROP] = json.dumps(dict(papel='corrimao', indice=0, comprimento=round(corrimao, 1)))
        trilho.parent = raiz
        trilho.matrix_parent_inverse = Matrix.Identity(4)
        trilho.location = (0, 0, escada.z * MM)
        trilho.hide_viewport = trilho.hide_render = True
    raiz[ROOT_PROP] = json.dumps(escada.para_dict())
    raiz[HANDRAIL_PROP] = round(corrimao, 1)
    return len(pecas)


def raizes_selecionadas(context):
    from .scene import root_of
    vistas = []
    for obj in [context.active_object, *context.selected_objects]:
        raiz = root_of(obj) if obj is not None else None
        if raiz is not None and raiz not in vistas:
            vistas.append(raiz)
    return vistas


def e_escada(obj):
    return is_root(obj)
