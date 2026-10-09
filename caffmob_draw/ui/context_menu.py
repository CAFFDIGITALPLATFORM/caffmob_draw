"""Menu do botão direito unificado (feature 005, T025; RF-13, RN-09, D-13).

Uma só inserção no menu de contexto de objetos da viewport (no lugar das três de antes): o submenu próprio do objeto
(`MENU_ID`, como já era) e as ações frequentes que valem para o tipo dele, com o mesmo rótulo e ícone da barra lateral
e do HUD (`sidebar_vocab`). Parede, piso, teto e aberturas ficam só com o submenu deles e o plano de inserção.
"""

import bpy  # type: ignore

from ..selection import classify
from .sidebar_vocab import draw_action

_ITEM_KINDS = (classify.MODULE, classify.FRONT, classify.PART, classify.GEOMETRY, classify.OBSTACLE, classify.OTHER)


def item_actions(context):
    """[(chave do vocabulário, argumentos)] das ações frequentes do objeto ativo, em ordem de uso."""
    obj = context.active_object
    info = classify.classify(obj) if obj is not None else None
    if info is None or info.kind not in _ITEM_KINDS or (info.kind == classify.OTHER and obj.type != 'MESH'):
        return []
    from ..stick.ops_stick import item_of
    item = item_of(obj)
    stuck = item is not None and item.btm_stick.is_stuck
    actions = [('RELEASE', {}), ('STICK_MOVE', {})] if stuck else [('STICK', {})]
    actions.append(('MOVE_OVER', {}))
    if info.kind in (classify.MODULE, classify.FRONT, classify.PART):
        from ..customize import adapters
        if adapters.for_object(obj)[1] is not None:
            actions.append(('CABINET_EDITOR', {}))
    actions.append(('CHECK_ITEM', {'scope': 'SELECTED'}))
    if info.kind in (classify.MODULE, classify.FRONT, classify.PART):
        from ..inspection import fronts
        if fronts.fronts_of(info.root, context.scene):
            actions.append(('FRONTS_OPEN', {'scope': 'ACTIVE_MODULE', 'mode': 'OPEN_90'}))
            actions.append(('FRONTS_CLOSE', {'scope': 'ACTIVE_MODULE', 'mode': 'CLOSE'}))
    return actions


def _legacy_menu_hidden(context, obj):
    from ..legacy import gate
    from ..selection import classify
    if gate.legacy_ui(context):
        return False
    _root, library = classify.module_root(obj)
    return library in gate.LEGACY_LIBRARIES


def draw_context_menu(self, context):
    layout = self.layout
    obj = context.object
    menu_id = obj.get("MENU_ID", "") if obj is not None else ""
    if menu_id and _legacy_menu_hidden(context, obj):
        menu_id = ""                                   # feature 012 (T051): menu de armário herdado só para suporte
    if menu_id and hasattr(bpy.types, menu_id):
        layout.operator_context = 'INVOKE_AREA'
        layout.menu(menu_id)
        layout.separator()
    layout.operator_context = 'INVOKE_DEFAULT'
    from .ops_resize import BTM_OT_ResizeWidth
    if BTM_OT_ResizeWidth.poll(context):
        draw_action(layout, 'RESIZE')
    actions = item_actions(context)
    for key, props in actions:
        draw_action(layout, key, **props)
    draw_action(layout, 'INSERTION_PLANE')
    plane = getattr(context.window_manager, 'btm_insertion_plane', None)
    if plane is not None and plane.active:
        draw_action(layout, 'CLEAR_INSERTION_PLANE')
    layout.separator()


def register():
    bpy.types.VIEW3D_MT_object_context_menu.prepend(draw_context_menu)


def unregister():
    bpy.types.VIEW3D_MT_object_context_menu.remove(draw_context_menu)
