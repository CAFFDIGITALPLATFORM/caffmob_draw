"""Operadores e painel do Plano de Corte OpCut offline + Lista por Módulo (feature 021, T021; RF-01, RF-02)."""

import os
import bpy  # type: ignore

from ..data.i18n import tr
from . import module_list_core, opcut_core, part_extractor, plan_export, plan_render

_last_result = {
    'plan': None,
    'groups': [],
}


def _compute_scene_plan(context):
    scene = context.scene
    settings = getattr(scene, 'btm_settings', None)
    sheet_w = float(getattr(settings, 'sheet_width', 2750.0) or 2750.0)
    sheet_h = float(getattr(settings, 'sheet_height', 1830.0) or 1830.0)
    margin = float(getattr(settings, 'sheet_margin', 10.0) or 10.0)
    kerf = float(getattr(settings, 'kerf', 4.0) or 4.0)
    parts, _incompatible = part_extractor.extract_production_parts(context)
    groups = module_list_core.group_by_module(parts)
    items = opcut_core.from_nesting_parts(parts)
    plan = opcut_core.calculate(
        items,
        sheet_width=sheet_w,
        sheet_height=sheet_h,
        margin=margin,
        kerf=kerf,
        method='forward_greedy',
    )
    _last_result['plan'] = plan
    _last_result['groups'] = groups
    if plan.sheets:
        idx = min(getattr(settings, 'cutting_preview_sheet_index', 0) if settings else 0, len(plan.sheets) - 1)
        if settings is not None:
            settings.cutting_preview_sheet_index = idx
        plan_render.update_blender_preview_image(plan.sheets[idx])
    return plan, groups


class BTM_OT_GenerateOpCutPlan(bpy.types.Operator):
    """Gera a lista de peças agrupadas por módulo e o plano de corte otimizado offline (OpCut)"""
    bl_idname = "caffmob.opcut_generate"
    bl_label = "Gerar Plano de Corte (OpCut)"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        plan, groups = _compute_scene_plan(context)
        if not groups:
            self.report({'WARNING'}, tr("Nenhuma peça de corte encontrada na cena."))
            return {'CANCELLED'}
        msg = tr("Plano de corte OpCut gerado: {} chapa(s), {} módulo(s).").format(len(plan.sheets), len(groups))
        if plan.unplaced:
            msg += " " + tr("Atenção: {} peça(s) excedem a área útil da chapa.").format(len(plan.unplaced))
            self.report({'WARNING'}, msg)
        else:
            self.report({'INFO'}, msg)
        return {'FINISHED'}


class BTM_OT_OpCutPreviewStep(bpy.types.Operator):
    """Alterna a chapa exibida na prévia interna do plano de corte"""
    bl_idname = "caffmob.opcut_preview_step"
    bl_label = "Alternar Chapa da Prévia"
    bl_options = {'INTERNAL'}

    delta: bpy.props.IntProperty(default=1)  # type: ignore

    def execute(self, context):
        plan = _last_result.get('plan')
        if plan is None or not plan.sheets:
            return {'CANCELLED'}
        settings = context.scene.btm_settings
        idx = (settings.cutting_preview_sheet_index + self.delta) % len(plan.sheets)
        settings.cutting_preview_sheet_index = idx
        plan_render.update_blender_preview_image(plan.sheets[idx])
        return {'FINISHED'}


class BTM_OT_ExportOpCutPlan(bpy.types.Operator):
    """Exporta o plano de corte OpCut e a lista agrupada por módulo em HTML, SVG ou PDF"""
    bl_idname = "caffmob.opcut_export"
    bl_label = "Exportar Plano de Corte"
    bl_options = {'REGISTER'}

    filepath: bpy.props.StringProperty(subtype='FILE_PATH')  # type: ignore
    export_format: bpy.props.EnumProperty(
        name="Formato",
        items=[('HTML', "HTML", ""), ('SVG', "SVG", ""), ('PDF', "PDF", "")],
        default='HTML',
    )  # type: ignore

    def invoke(self, context, event):
        ext = self.export_format.lower()
        self.filepath = bpy.path.abspath(f"//plano_de_corte_caffmob.{ext}")
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

    def execute(self, context):
        plan = _last_result.get('plan')
        groups = _last_result.get('groups')
        if plan is None:
            plan, groups = _compute_scene_plan(context)
        if not plan.sheets:
            self.report({'WARNING'}, tr("Nenhuma chapa disponível para exportar."))
            return {'CANCELLED'}
        path = bpy.path.abspath(self.filepath)
        try:
            if self.export_format == 'SVG':
                idx = min(context.scene.btm_settings.cutting_preview_sheet_index, len(plan.sheets) - 1)
                plan_export.write_svg(plan.sheets[idx], path)
            elif self.export_format == 'PDF':
                plan_export.write_pdf(plan, groups, path)
            else:
                plan_export.write_html(plan, groups, path)
        except OSError as exc:
            self.report({'ERROR'}, tr("Erro ao gravar arquivo: {}").format(exc))
            return {'CANCELLED'}
        self.report({'INFO'}, tr("Plano de corte exportado em {}.").format(os.path.basename(path)))
        return {'FINISHED'}


class BTM_PT_OpCutPanel(bpy.types.Panel):
    """Painel de Lista de Peças por Módulo e Plano de Corte OpCut offline"""
    bl_label = "Plano de Corte (OpCut)"
    bl_idname = "BTM_PT_OpCutPanel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "CAFFMob Draw"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        settings = getattr(context.scene, 'btm_settings', None)
        if settings is None:
            return
        layout.prop(settings, "cutting_engine", text=tr("Motor"))
        layout.prop(settings, "cutting_group_by_module", text=tr("Agrupar peças por módulo"))
        layout.operator("caffmob.opcut_generate", text=tr("Gerar Plano de Corte (OpCut)"), icon='MOD_ARRAY')

        plan = _last_result.get('plan')
        groups = _last_result.get('groups') or []
        if settings.cutting_group_by_module and groups:
            box = layout.box()
            box.label(text=tr("Lista de Peças por Módulo ({})").format(len(groups)), icon='OUTLINER_OB_GROUP_INSTANCE')
            for grp in groups[:8]:
                row = box.row()
                row.label(text=tr("{}: {} pç ({:.2f} m²)").format(grp.module_name, grp.total_pieces, grp.total_area_m2))

        if plan and plan.sheets:
            idx = min(settings.cutting_preview_sheet_index, len(plan.sheets) - 1)
            sh = plan.sheets[idx]
            pbox = layout.box()
            nav = pbox.row(align=True)
            nav.operator("caffmob.opcut_preview_step", text="", icon='TRIA_LEFT').delta = -1
            nav.label(text=tr("Chapa {}/{} — {} {:.0f}mm ({:.1f}%)").format(
                idx + 1, len(plan.sheets), sh.material, sh.thickness, sh.efficiency_pct
            ))
            nav.operator("caffmob.opcut_preview_step", text="", icon='TRIA_RIGHT').delta = 1
            img = bpy.data.images.get("CAFFMob_PlanoCorte_Preview")
            if img is not None:
                pbox.template_ID_preview(context.scene, "name") if False else None
                pbox.label(text=tr("Prévia disponível no Image Editor: CAFFMob_PlanoCorte_Preview"), icon='IMAGE_DATA')

            exp = layout.row(align=True)
            for fmt in ('HTML', 'SVG', 'PDF'):
                op = exp.operator("caffmob.opcut_export", text=fmt, icon='EXPORT')
                op.export_format = fmt


classes = (
    BTM_OT_GenerateOpCutPlan,
    BTM_OT_OpCutPreviewStep,
    BTM_OT_ExportOpCutPlan,
    BTM_PT_OpCutPanel,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        if cls.is_registered:
            bpy.utils.unregister_class(cls)
