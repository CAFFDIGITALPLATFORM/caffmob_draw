"""Operadores "Instalar na parede" e "Desinstalar" da janela importada (feature 007, T023; RN-03, RF-03, D-12, D-13).

Instalar: com a esquadria (grupo FRAME) e uma parede HB selecionadas, a janela vai para a parede na altura do
peitoril, com o vão cortado; depois ela anda só no plano da parede, como as janelas de ambiente.
"""

import bpy  # type: ignore

from ..data.i18n import tr
from . import install


def _selection(context):
    frame, wall = None, None
    from ..selection import classify
    for obj in context.selected_objects:
        if obj.get(install.WALL_FLAG) or classify.classify(obj).kind == classify.WALL:
            wall = obj                              # parede não HB chega a can_install e recebe o aviso (RN-22)
        elif frame is None:
            frame = install.frame_of(obj)
    return frame, wall


class BTM_OT_WindowInstall(bpy.types.Operator):
    """Instala a janela importada na parede selecionada, cortando o vão"""
    bl_idname = "caffmob.window_install"
    bl_label = "Instalar na parede"
    bl_options = {'REGISTER', 'UNDO'}

    sill: bpy.props.FloatProperty(name="Peitoril", default=install.DEFAULT_SILL, min=0.0, subtype='DISTANCE',
                                  unit='LENGTH')  # type: ignore

    @classmethod
    def poll(cls, context):
        frame, wall = _selection(context)
        reason = install.can_install(frame, wall)
        if reason:
            cls.poll_message_set(reason)
            return False
        return True

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)

    def execute(self, context):
        frame, wall = _selection(context)
        reason = install.can_install(frame, wall)
        if reason:
            self.report({'WARNING'}, reason)
            return {'CANCELLED'}
        cage = install.install(context, frame, wall, self.sill)
        for obj in context.selected_objects:
            obj.select_set(False)
        cage.select_set(True)
        context.view_layer.objects.active = cage
        self.report({'INFO'}, tr("{} instalada em {}").format(frame.name, wall.name))
        return {'FINISHED'}


class BTM_OT_WindowUninstall(bpy.types.Operator):
    """Tira a janela da parede: ela fica solta no mesmo lugar e o vão fecha"""
    bl_idname = "caffmob.window_uninstall"
    bl_label = "Desinstalar"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return _cage(context) is not None

    def execute(self, context):
        frame = install.uninstall(context, _cage(context))
        if frame is not None:
            for obj in context.selected_objects:
                obj.select_set(False)
            frame.select_set(True)
            context.view_layer.objects.active = frame
        self.report({'INFO'}, tr("Janela desinstalada"))
        return {'FINISHED'}


def _cage(context):
    obj = context.active_object
    if obj is not None and obj.get(install.WINDOW_FLAG) and obj.btm_window.frame is not None:
        return obj
    return install.cage_of(install.frame_of(obj)) if obj is not None else None


classes = (BTM_OT_WindowInstall, BTM_OT_WindowUninstall)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        if cls.is_registered:
            bpy.utils.unregister_class(cls)
