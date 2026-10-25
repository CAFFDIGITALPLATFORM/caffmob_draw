"""Operadores do alvo da seleção (feature 067; RF-003, RF-020)."""

import bpy  # type: ignore

from ..data.i18n import tr
from . import capabilities, snapshot


class BTM_OT_TargetSelectOwner(bpy.types.Operator):
    """Seleciona o conjunto dono do selecionado (o módulo, o armário autoral ou a parede)"""
    bl_idname = 'caffmob.target_select_owner'
    bl_label = "Selecionar conjunto"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return capabilities.poll(cls, 'select_owner', snapshot.current(context))

    def execute(self, context):
        target = snapshot.ensure(context)
        owner = snapshot.object_for(context, target.owner_uid) if target is not None else None
        if owner is None:
            self.report({'WARNING'}, tr("O selecionado não tem conjunto dono."))
            return {'CANCELLED'}
        for obj in context.selected_objects:
            obj.select_set(False)
        owner.select_set(True)
        context.view_layer.objects.active = owner
        return {'FINISHED'}


class BTM_OT_TargetCladdingApply(bpy.types.Operator):
    """Refaz o revestimento selecionado com os valores digitados no painel"""
    bl_idname = 'caffmob.target_cladding_apply'
    bl_label = "Aplicar"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        target = snapshot.current(context)
        return target is not None and target.kind == 'CLADDING'

    def execute(self, context):
        from ..cladding import props, sync
        target = snapshot.ensure(context)
        root = snapshot.object_for(context, target.uid) if target is not None else None
        if root is None or not root.btm_cladding.uid:
            self.report({'WARNING'}, tr("Selecione um revestimento."))
            return {'CANCELLED'}
        from types import SimpleNamespace
        from ..cladding.ops import copy_settings
        draft = context.window_manager.btm_cladding_draft
        previous = SimpleNamespace()
        copy_settings(root.btm_cladding, previous)
        try:
            props.parameters(draft).validate()
            copy_settings(draft, root.btm_cladding)
            sync.sync(root)
        except ValueError as exc:
            copy_settings(previous, root.btm_cladding)
            self.report({'ERROR'}, tr(str(exc)))
            return {'CANCELLED'}
        return {'FINISHED'}


classes = (BTM_OT_TargetSelectOwner, BTM_OT_TargetCladdingApply)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
