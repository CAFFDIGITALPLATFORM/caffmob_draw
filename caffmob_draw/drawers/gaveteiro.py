"""Criar o gaveteiro novo (072 D-22, RN-12): um módulo rápido com a montagem e as espessuras do tipo e as gavetas.

A caixaria é a do módulo rápido (montagem LATERAL ou BASE, RN-CABINET_EDITOR-20), com o tampo do tipo e os rodízios
pelos extras do Editor de Armário (RN-CABINET_EDITOR-15); as gavetas vão pelo construtor no vão do módulo.
"""
import bpy

from . import core
from .gaveteiro_core import Gaveteiro


def criar(context, g: Gaveteiro, gaveta: core.Gaveta):
    """Cria o gaveteiro na posição do cursor 3D; devolve (raiz, motivos)."""
    e = g.espessuras()
    resultado = bpy.ops.caffmob.cabinet_builder(width=g.largura / 1000, height=g.altura / 1000,
                                                depth=g.profundidade / 1000, thickness=e['lateral'] / 1000,
                                                assembly=g.metodo, door_swing='NONE')
    if resultado != {'FINISHED'}:
        return None, ["O módulo do gaveteiro não pôde ser criado."]
    raiz = context.view_layer.objects.active
    cab = raiz.btm_cabinet
    cab.thickness_top = e['tampo'] / 1000
    cab.thickness_bottom = e['base'] / 1000
    raiz['btm_gaveteiro'] = g.tipo
    if e['rodizios']:
        from ..cabinet_editor import scene_extras
        raiz.btm_structure.extras_from_dict({'CASTERS': {'enabled': True, 'value': 0.10}})
        scene_extras.sync(context, raiz)
    context.view_layer.update()
    from ..customize.adapters import btm
    gaveta = core.Gaveta.de_dict({**gaveta.para_dict(), 'frente_espessura': e['frente']})
    motivos = btm.set_front(context, raiz, raiz, 'DRAWERS', g.gavetas, gaveta.para_dict())
    return raiz, motivos
