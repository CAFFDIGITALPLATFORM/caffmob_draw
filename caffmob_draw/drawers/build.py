"""Montar e regenerar as peças da caixa da gaveta do construtor (072 D-04).

A frente (malha do `subspace_fronts`) recebe o spec e as peças da caixa, como caixas de malha filhas dela, no
referencial da frente: a caixa começa na face de trás da frente e fica centrada no vão pelo desconto da corrediça.
"""
import json
import uuid

import bpy
from mathutils import Matrix

from . import catalogo, core
from .scene import DRAWER_PROP, PART_PROP, UID_PROP

MM = 0.001


def pasta_do_usuario():
    try:
        return bpy.utils.extension_path_user(__package__.rsplit('.', 1)[0], path='gavetas', create=True)
    except (ValueError, RuntimeError, AttributeError):
        return None


def _caixa(nome, tam):
    w, d, h = (v * MM for v in tam)
    v = [(0, 0, 0), (w, 0, 0), (w, d, 0), (0, d, 0), (0, 0, h), (w, 0, h), (w, d, h), (0, d, h)]
    f = [(0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)]
    mesh = bpy.data.meshes.new(nome)
    mesh.from_pydata(v, [], f)
    return mesh


def limpar(front):
    for filho in list(front.children):
        if filho.get(PART_PROP) is None:
            continue
        mesh = filho.data if filho.type == 'MESH' else None
        bpy.data.objects.remove(filho, do_unlink=True)
        if mesh is not None and mesh.users == 0:
            bpy.data.meshes.remove(mesh)


def aplicar(front, espaco, gaveta, altura_da_frente, folga_x_da_frente, espessura_da_frente):
    """Grava o spec na frente e refaz as peças da caixa (sem duplicar). ValueError com os motivos se não cabe.

    `folga_x_da_frente` é a distância da face esquerda do vão à face esquerda da frente (a margem da frente).
    """
    corredica = catalogo.por_id(gaveta.corredica, pasta_do_usuario())
    c = core.caixa(espaco, gaveta, corredica, altura_da_frente)
    limpar(front)
    colecoes = list(front.users_collection) or [bpy.context.scene.collection]
    origem_x = c.deslocamento_x - folga_x_da_frente
    for i, peca in enumerate(c.pecas):
        obj = bpy.data.objects.new(f"{front.name} {peca['nome'].lower()}", _caixa(peca['nome'], peca['tam']))
        for colecao in colecoes:
            colecao.objects.link(obj)
        obj[PART_PROP] = json.dumps(dict(papel=peca['papel'], indice=i, furos=peca['furos']))
        obj['hb_part_role'] = 'CLOSET_DRAWER_BOX'           # o corte genérico pula; a fonte DRAWERS lê pelo spec
        obj.parent = front
        obj.matrix_parent_inverse = Matrix.Identity(4)
        x, y, z = peca['pos']
        obj.location = ((origem_x + x) * MM, (espessura_da_frente + y) * MM, z * MM)
    if not front.get(UID_PROP):
        front[UID_PROP] = str(uuid.uuid4())
    front[DRAWER_PROP] = json.dumps(dict(
        gaveta=gaveta.para_dict(), altura_da_frente=altura_da_frente, comprimento=c.comprimento,
        espaco=dict(largura=espaco.largura, altura=espaco.altura, profundidade=espaco.profundidade),
        folga_x=folga_x_da_frente, espessura_da_frente=espessura_da_frente))
    return c
