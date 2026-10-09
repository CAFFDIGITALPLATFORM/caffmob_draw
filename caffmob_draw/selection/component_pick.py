"""Alt + clique seleciona só a peça (feature 011, T010; roadmap D-04, RN-06).

Com a seleção por componente ligada:
- Alt + clique (`caffmob.component_pick`) seleciona a peça sob o cursor pelo `view3d.select` e a marca como isenta, para
  o normalizador não subir para a raiz; Alt + Shift + clique soma a peça;
- um clique sem modificador, havendo peça isenta, limpa a isenção (`caffmob.component_click_reset`) e deixa o clique
  seguir para o `view3d.select`: o componente volta a ser selecionado inteiro.

Com o interruptor desligado, os dois saem pelo poll e o Alt + clique volta ao do Blender (lista os objetos sob o
cursor). Os itens de keymap ficam no "3D View", na frente (`head=True`), e saem no `unregister`.
"""

import bpy  # type: ignore

from . import component_select

_addon_keymaps = []


def _enabled(context):
    return (context.mode == 'OBJECT' and context.area is not None and context.area.type == 'VIEW_3D'
            and getattr(context.scene, 'btm_component_select', False))


class BTM_OT_ComponentPick(bpy.types.Operator):
    """Seleciona só a peça sob o cursor, sem subir para o componente"""
    bl_idname = "caffmob.component_pick"
    bl_label = "Selecionar peça"
    bl_options = {'REGISTER', 'UNDO'}

    extend: bpy.props.BoolProperty(name="Somar à seleção", default=False)  # type: ignore

    @classmethod
    def poll(cls, context):
        return _enabled(context)

    def invoke(self, context, event):
        exempt = component_select.exempt_names(context) if self.extend else set()
        # O `view3d.select` aninhado pode avaliar o depsgraph na hora: o normalizador fica suspenso até a peça
        # estar marcada como isenta, senão ela subiria para a raiz antes de ser lida.
        with component_select.suspended():
            result = bpy.ops.view3d.select(extend=self.extend, deselect_all=not self.extend,
                                           location=(event.mouse_region_x, event.mouse_region_y))
            obj = context.view_layer.objects.active
            if 'FINISHED' in result and obj is not None and obj.select_get():
                exempt.add(obj.name)
            component_select.set_exempt(context, exempt)
        component_select.forget()
        return {'FINISHED'}


class BTM_OT_ComponentClickReset(bpy.types.Operator):
    """Clique sem Alt: a peça escolhida deixa de ser isenta e o componente volta a ser selecionado"""
    bl_idname = "caffmob.component_click_reset"
    bl_label = "Voltar à seleção por componente"
    bl_options = {'INTERNAL'}

    @classmethod
    def poll(cls, context):
        return _enabled(context) and bool(getattr(context.window_manager, 'btm_component_exempt', ""))

    def invoke(self, context, _event):
        component_select.set_exempt(context, set())
        component_select.forget()
        return {'PASS_THROUGH'}


classes = (BTM_OT_ComponentPick, BTM_OT_ComponentClickReset)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    wm = bpy.context.window_manager
    kc = wm.keyconfigs.addon if wm else None
    if kc is None:
        return
    km = kc.keymaps.new(name='3D View', space_type='VIEW_3D')
    for shift in (False, True):
        kmi = km.keymap_items.new(BTM_OT_ComponentPick.bl_idname, 'LEFTMOUSE', 'CLICK', alt=True, shift=shift,
                                  head=True)
        kmi.properties.extend = shift
        _addon_keymaps.append((km, kmi))
    kmi = km.keymap_items.new(BTM_OT_ComponentClickReset.bl_idname, 'LEFTMOUSE', 'PRESS', head=True)
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
