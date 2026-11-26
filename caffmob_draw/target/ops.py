"""Operadores do alvo da seleção (feature 067; RF-003, RF-020)."""

import bpy  # type: ignore

from ..data.i18n import N_, tr
from . import capabilities, snapshot

MULTI_LABELS = {'width': N_("Largura"), 'height': N_("Altura"), 'depth': N_("Profundidade"),
                'thickness': N_("Espessura")}


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


class BTM_OT_TargetMultiApply(bpy.types.Operator):
    """Aplica a medida digitada em todos os objetos ativos, com confirmação (027, RF-04)"""
    bl_idname = 'caffmob.target_multi_apply'
    bl_label = "Aplicar em todos os selecionados"
    bl_options = {'REGISTER', 'UNDO'}

    field: bpy.props.EnumProperty(
        name="Medida",
        items=[(code, label, "") for code, label in MULTI_LABELS.items()],
        default='width',
    )  # type: ignore
    value: bpy.props.StringProperty(name="Valor", description="Medida na unidade do projeto, com mm, cm ou m")  # type: ignore

    @classmethod
    def poll(cls, context):
        return snapshot.current(context) is not None

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(
            self, width=380,
            title=tr("Você está prestes a aplicar transformação em todos os objetos ativos: Confirma?"),
            confirm_text=tr("Sim"))

    def draw(self, context):
        target = snapshot.current(context)
        count = target.count if target is not None else 0
        self.layout.label(text=tr("{} em {} objeto(s)").format(tr(MULTI_LABELS.get(self.field, '')), count),
                          icon='INFO')
        self.layout.prop(self, 'value')

    def execute(self, context):
        from ..data import units
        from . import multi_apply

        target = snapshot.ensure(context)
        uids = tuple(target.selected_uids) if target is not None and target.selected_uids else \
            ((target.uid,) if target is not None else ())
        try:
            meters = units.parse_length(self.value or "", default_unit=units.get_scene_length_unit(context.scene))
        except ValueError as exc:
            self.report({'ERROR'}, str(exc))
            return {'CANCELLED'}
        done, ignored, failures = multi_apply.apply(context, uids, self.field, meters)
        for name, reason in failures:
            self.report({'WARNING'}, tr("{}: {}").format(name, reason))
        if not done:
            self.report({'ERROR'}, tr("Nenhum objeto aceitou a medida.") if not failures else failures[0][1])
            return {'CANCELLED'}
        self.report({'INFO'}, tr("Medida aplicada em {} objeto(s).").format(done))
        return {'FINISHED'}


classes = (BTM_OT_TargetSelectOwner, BTM_OT_TargetCladdingApply, BTM_OT_TargetMultiApply)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
