"""Fixture da 072 (T002): o balcão de 600 × 720 × 560 mm com laterais de 18 mm dos guias do titular, sem bpy.

Espaço livre do vão: 564 mm de largura (600 − 2 × 18), 684 mm de altura e 530 mm de profundidade; e um nicho de
280 mm de profundidade para a recusa. Para os ensaios no Blender, `balcao(context)` cria o módulo rápido.
"""
import _bootstrap  # noqa: F401
from caffmob_draw.drawers import catalogo, core

LARGURA, ALTURA, PROFUNDIDADE, LATERAL = 600, 720, 560, 18
VAO = core.Espaco(largura=564, altura=684, profundidade=530)
NICHO_RASO = core.Espaco(largura=564, altura=300, profundidade=280)


def corredica(cid):
    return catalogo.por_id(cid)


def balcao(context, largura=LARGURA, altura=ALTURA, profundidade=PROFUNDIDADE):
    """Módulo rápido (BTM) sem frente, no Blender; devolve a raiz."""
    import bpy
    bpy.ops.caffmob.parametric_insert(width=largura / 1000, height=altura / 1000, depth=profundidade / 1000)
    return context.view_layer.objects.active
