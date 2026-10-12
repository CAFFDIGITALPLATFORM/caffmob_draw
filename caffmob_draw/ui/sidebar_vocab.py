"""Vocabulário fixo da interface (feature 005, T003; D-10).

Uma ação tem **um** rótulo e **um** ícone, iguais no painel, no menu do botão direito e no HUD. Os títulos das seções e
dos grupos também ficam aqui. Os textos são as chaves do catálogo de tradução (`data/translations/`).
"""

from ..data.i18n import N_

# Seções da barra lateral, na ordem do trabalho (RN-01).
SECTIONS = (
    ('build', N_("Construir"), 'MOD_BUILD'),
    ('insert', N_("Inserir"), 'ASSET_MANAGER'),
    ('selected', N_("Selecionado"), 'RESTRICT_SELECT_OFF'),
    ('check', N_("Verificar"), 'VIEWZOOM'),
    ('project', N_("Produção/Projeto"), 'FILE_TICK'),
)

# Ação frequente → (operador, rótulo, ícone).
ACTIONS = {
    'STICK': ("caffmob.stick_to_face", N_("Grudar"), 'SNAP_FACE'),
    'RELEASE': ("caffmob.stick_release", N_("Desgrudar"), 'UNLINKED'),
    'STICK_MOVE': ("caffmob.stick_move", N_("Mover no plano"), 'SNAP_FACE'),
    'RESIZE': ("caffmob.resize_width", N_("Redimensionar"), 'FULLSCREEN_ENTER'),
    'MOVE_OVER': ("caffmob.move_over_toggle", N_("Mover Sobre"), 'ORIENTATION_VIEW'),
    'CABINET_EDITOR': ("caffmob.cabinet_editor", N_("Abrir editor de armário"), 'MOD_BUILD'),
    'CHECK_ITEM': ("caffmob.check_collisions", N_("Verificar colisões"), 'MOD_PHYSICS'),
    'FRONTS_OPEN': ("caffmob.fronts_set_open", N_("Abrir frentes"), 'TRIA_RIGHT_BAR'),
    'FRONTS_CLOSE': ("caffmob.fronts_set_open", N_("Fechar frentes"), 'TRIA_LEFT_BAR'),
    'CLEAR_INSERTION_PLANE': ("caffmob.clear_insertion_plane", N_("Limpar plano de inserção"), 'X'),
    'INSERTION_PLANE': ("caffmob.set_insertion_plane", N_("Usar como plano de inserção"), 'SNAP_FACE'),
}


def action(key):
    return ACTIONS[key]


def draw_action(layout, key, text=True, **props):
    """Desenha a ação com o rótulo e o ícone do vocabulário; devolve as propriedades do operador."""
    idname, label, icon = ACTIONS[key]
    op = layout.operator(idname, text=label if text else "", icon=icon)
    for name, value in props.items():
        setattr(op, name, value)
    return op
