"""Seção Verificar (feature 005, T018; RF-05, RN-06, D-08).

Junta a inspeção de frentes (abrir/fechar todas, ângulo do clique, interferência) e a colisão de corpo: a chave
"Impedir atravessamento" e o botão "Diagnóstico técnico" (feature 066, RF-022, RF-024).
"""

from ..data.i18n import N_
from .sidebar import group_scope


def draw(layout, context):
    from . import panels
    with group_scope(layout, context, 'check_fronts', N_("Portas e gavetas"), 'HIDE_OFF') as body:
        if body is not None:
            panels.draw_inspection_box(body, context)
    with group_scope(layout, context, 'check_collisions', N_("Colisões"), 'MOD_PHYSICS') as body:
        if body is not None:
            from ..collision import panels as collision_panels
            collision_panels.draw_tools(body, context)
