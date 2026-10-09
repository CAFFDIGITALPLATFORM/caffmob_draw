"""Clique, hover e Esc do painel BIBLIOTECA CAFFMOB (feature 012, T021; D-13, D-30).

Itens de keymap em "3D View" na frente (`head=True`), como o HUD: cada evento chama um operador curto, que trata o
clique quando ele cai no painel e devolve `PASS_THROUGH` fora dele (sem modal permanente, o salvamento automático
continua). Com o painel aberto, clique fora ou Esc fecha.
"""

import bpy  # type: ignore

from . import categories, draw, layout_core

_addon_keymaps = []


def _in_viewport(context):
    return (context.area is not None and context.area.type == 'VIEW_3D' and context.region is not None
            and context.region.type == 'WINDOW' and hasattr(context.window_manager, 'btm_library'))


def _hit(context, event):
    lay = draw.layout(context, context.area, context.region)
    return lay, layout_core.hit(lay, event.mouse_region_x, event.mouse_region_y)


def _run(op_idname):
    namespace, name = op_idname.split('.')
    operator = getattr(getattr(bpy.ops, namespace), name)
    if operator.poll():
        operator('INVOKE_DEFAULT')


def dispatch(context, key):
    """O que o item faz (também usado pelos testes)."""
    state = context.window_manager.btm_library
    category = layout_core.category_of(key)
    if key == 'LABEL':
        state.open = not state.open
        if state.open:
            categories.invalidate()
        return
    state.open = False
    if key == layout_core.CREATE_CABINET:
        _run("caffmob.library_create_cabinet")
    elif key == layout_core.CREATE_CATEGORY:
        _run("caffmob.library_category_create")
    elif key == layout_core.CONVERT_GROUPS:
        _run("caffmob.legacy_groups_convert")
    elif category is not None:
        found = categories.find(category)
        state.category = category
        state.line = found.line if found is not None else 'COZ'
        from . import popover
        popover.show(context, category)


class BTM_OT_LibraryClick(bpy.types.Operator):
    """Clique no painel BIBLIOTECA CAFFMOB"""
    bl_idname = "caffmob.library_click"
    bl_label = "Biblioteca CAFFMob"
    bl_options = {'INTERNAL'}

    @classmethod
    def poll(cls, context):
        return _in_viewport(context)

    def invoke(self, context, event):
        _lay, key = _hit(context, event)
        state = context.window_manager.btm_library
        if key is None:
            if state.open:
                state.open = False                # clique fora fecha e segue para a seleção
                draw.tag_redraw(context)
            return {'PASS_THROUGH'}
        dispatch(context, key)
        draw.tag_redraw(context)
        return {'FINISHED'}


class BTM_OT_LibraryHover(bpy.types.Operator):
    bl_idname = "caffmob.library_hover"
    bl_label = "Biblioteca CAFFMob (hover)"
    bl_options = {'INTERNAL'}

    @classmethod
    def poll(cls, context):
        return _in_viewport(context)

    def invoke(self, context, event):
        lay, key = _hit(context, event)
        before = layout_core.hit(lay, *draw._mouse['pos']) if draw._mouse['region'] == context.region.as_pointer() \
            else None
        draw._mouse['pos'] = (event.mouse_region_x, event.mouse_region_y)
        draw._mouse['region'] = context.region.as_pointer()
        if key != before:
            context.region.tag_redraw()
        return {'PASS_THROUGH'}


class BTM_OT_LibraryClose(bpy.types.Operator):
    """Fecha o painel BIBLIOTECA CAFFMOB"""
    bl_idname = "caffmob.library_close"
    bl_label = "Fechar biblioteca"
    bl_options = {'INTERNAL'}

    @classmethod
    def poll(cls, context):
        return _in_viewport(context) and context.window_manager.btm_library.open

    def execute(self, context):
        context.window_manager.btm_library.open = False
        draw.tag_redraw(context)
        return {'FINISHED'}


classes = (BTM_OT_LibraryClick, BTM_OT_LibraryHover, BTM_OT_LibraryClose)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    wm = bpy.context.window_manager
    kc = wm.keyconfigs.addon if wm else None
    if kc is None:
        return
    km = kc.keymaps.new(name='3D View', space_type='VIEW_3D')
    for idname, event, value in ((BTM_OT_LibraryClick.bl_idname, 'LEFTMOUSE', 'PRESS'),
                                 (BTM_OT_LibraryHover.bl_idname, 'MOUSEMOVE', 'ANY'),
                                 (BTM_OT_LibraryClose.bl_idname, 'ESC', 'PRESS')):
        kmi = km.keymap_items.new(idname, event, value, any=(event != 'ESC'), head=True)
        _addon_keymaps.append((km, kmi))


def unregister():
    for km, kmi in _addon_keymaps:
        try:
            km.keymap_items.remove(kmi)
        except (ReferenceError, RuntimeError):
            pass
    _addon_keymaps.clear()
    for cls in reversed(classes):
        if cls.is_registered:
            bpy.utils.unregister_class(cls)
