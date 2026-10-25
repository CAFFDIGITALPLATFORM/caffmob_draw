"""Seção Selecionado (feature 005, T017; RF-04, RN-05, D-07).

Os grupos por tipo vêm de `object_properties.draw_selected` (no máximo 4 abertos). Para um módulo face frame, as
opções da biblioteca (dimensões, construção, padrões, vãos, seleção…) entram como o grupo recolhido "Opções do face
frame", com os subpainéis do face frame desenhados pelo proxy, no lugar do antigo painel "Face Frame Cabinet".
"""

from ..data.i18n import N_, tr
from . import object_properties, sidebar_proxy
from .sidebar import group_scope

_FACE_FRAME_CHILDREN = ('HB_FACE_FRAME_PT_dimensions', 'HB_FACE_FRAME_PT_selection', 'HB_FACE_FRAME_PT_all_bays',
                        'HB_FACE_FRAME_PT_construction', 'HB_FACE_FRAME_PT_face_frame_defaults',
                        'HB_FACE_FRAME_PT_leg_product', 'HB_FACE_FRAME_PT_floating_shelf')


def _draw_face_frame(layout, context):
    from ..product_libraries.face_frame import ui_face_frame as uff
    parent = uff.HB_FACE_FRAME_PT_active_cabinet
    if not sidebar_proxy.visible(parent, context):
        return
    with group_scope(layout, context, 'sel_library', N_("Opções do face frame"), 'MESH_GRID') as body:
        if body is None:
            return
        sidebar_proxy.draw_panel(parent, body, context)
        for name in _FACE_FRAME_CHILDREN:
            child = getattr(uff, name, None)
            if child is None or not sidebar_proxy.visible(child, context):
                continue
            box = body.box()
            box.label(text=sidebar_proxy.label_of(child))
            sidebar_proxy.draw_panel(child, box, context, header=True)


def _draw_standard(layout, context):
    """Padrão de origem, montagem e "Padrão próprio" do armário CAFFMob ativo (feature 012, T036; RF-07)."""
    from ..cabinet_editor import bridge
    from ..selection import classify
    root, library = classify.module_root(context.active_object)
    if library != 'BTM' or not bridge.is_caffmob_module(root):
        return
    box = layout.box()
    origin = bridge.origin_definition(context, root)
    box.label(text=tr("Padrão: {}").format(origin.name if origin is not None else "—"), icon='PRESET')
    row = box.row(align=True)
    row.prop(root.btm_cabinet, "assembly", expand=True)
    if bridge.is_own_standard(context, root):
        note = box.row()
        note.active = False
        note.label(text=tr("Padrão próprio: difere do Padrão de Dimensões global"), icon='MODIFIER')


def _draw_legacy(layout, context):
    """Armário de biblioteca antiga selecionado: botão para converter só ele (feature 012, T061; D-26)."""
    from ..legacy import gate
    from ..selection import classify
    _root, library = classify.module_root(context.active_object)
    if library not in gate.LEGACY_LIBRARIES:
        return
    box = layout.box()
    box.label(text=tr("Armário de biblioteca antiga"), icon='INFO')
    op = box.operator("caffmob.legacy_convert", text=tr("Converter este para CAFFMob"), icon='FILE_REFRESH')
    op.only_active = True


def _draw_mode(layout, context):
    """Essencial ou Completa (067 D-05, RF-004): preferência do usuário, então trocar não gera passo de Desfazer."""
    addon = context.preferences.addons.get(__package__.rsplit('.', 1)[0])
    prefs = getattr(addon, 'preferences', None)
    if prefs is not None and 'panel_mode' in prefs.bl_rna.properties:
        layout.row(align=True).prop(prefs, 'panel_mode', expand=True)


def draw(layout, context):
    _draw_mode(layout, context)
    object_properties.draw_selected(layout, context)
    if context.active_object is not None:
        from ..legacy import gate
        _draw_standard(layout, context)
        if gate.legacy_ui(context):
            _draw_face_frame(layout, context)
        else:
            _draw_legacy(layout, context)
    if any(o.type == 'MESH' for o in context.selected_objects):        # feature 009 (RN-12)
        with group_scope(layout, context, 'sel_retexture', N_("Retexturizar"), 'MATERIAL') as body:
            if body is not None:
                from ..object_library import panels as object_panels
                object_panels.draw_retexture(body, context)
