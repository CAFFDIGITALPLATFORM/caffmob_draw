"""Menu do botão direito unificado (feature 005, T025; RF-13, RN-09, D-13).

Uma só inserção no menu de contexto de objetos da viewport (no lugar das três de antes): o submenu próprio do objeto
(`MENU_ID`, como já era) e as ações frequentes que valem para o tipo dele, com o mesmo rótulo e ícone da barra lateral
e do HUD (`sidebar_vocab`). Parede, piso, teto e aberturas ficam só com o submenu deles e o plano de inserção.
"""

import bpy  # type: ignore

from ..selection import classify
from .sidebar_vocab import draw_action

def item_actions(context):
    """[(chave do vocabulário, argumentos)] das ações frequentes do alvo, em ordem de uso.

    (067 D-09) Vem do CommandRouter para o snapshot do alvo, o mesmo que o painel usa: só o que executa nele, e na
    chapa as ações da chapa, nunca as do módulo (RF-005).
    """
    from ..target import commands, snapshot
    target = snapshot.current(context)
    obj = snapshot.object_for(context, target.uid) if target is not None else None
    if obj is None:
        return []
    enabled = {entry.operator for entry in commands.menu_items(target)}
    actions = []
    if 'caffmob.stick_to_face' in enabled:
        from ..stick.ops_stick import item_of, stickable
        if stickable(obj):
            item = item_of(obj)
            stuck = item is not None and item.btm_stick.is_stuck
            actions += [('RELEASE', {}), ('STICK_MOVE', {})] if stuck else [('STICK', {})]
    if 'caffmob.move_over_toggle' in enabled:
        actions.append(('MOVE_OVER', {}))
    if 'caffmob.cabinet_editor' in enabled:
        from ..customize import adapters
        if adapters.for_object(obj)[1] is not None:
            actions.append(('CABINET_EDITOR', {}))
    if 'caffmob.check_collisions' in enabled:
        actions.append(('CHECK_ITEM', {'scope': 'SELECTED'}))
    if target.kind in (classify.MODULE, classify.FRONT):
        from ..inspection import fronts
        root = snapshot.object_for(context, target.owner_uid) if target.kind == classify.FRONT else obj
        scope = 'SELECTED' if target.kind == classify.FRONT else 'ACTIVE_MODULE'
        if root is not None and fronts.fronts_of(root, context.scene):
            actions.append(('FRONTS_OPEN', {'scope': scope, 'mode': 'OPEN_DEFAULT'}))
            actions.append(('FRONTS_CLOSE', {'scope': scope, 'mode': 'CLOSE'}))
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
