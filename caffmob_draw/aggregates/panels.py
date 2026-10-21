"""Painel do agregado e da folha de porta (feature 003, T054; RF-11 a RF-19).

Subpainel de "Propriedades" (`BTM_PT_object_properties`, feature 002): importar, converter e, para o objeto ativo
convertido, pai, face, posição com mínimo/máximo, afastamento, Perfurar, Furo real, Peça de produção; para a folha,
movimento, eixo, sentido, máximo ou curso, a barra de abertura e o aviso de batida.

Feature 007 (T025): Criar grupo, Desfazer grupo e Montar esquadria junto de Converter; a folha ativa pode ser uma peça
de um grupo-folha; aviso de pouco curso; contato "bateu em"/"encostou em"; Instalar/Desinstalar para a esquadria.
"""

import bpy  # type: ignore

from ..data.i18n import tr
from ..data import units
from . import apply, install, leaf, limits, perforate


def _active_aggregate(context):
    obj = context.active_object
    if obj is not None:
        obj = next((c for c in obj.children if leaf.pivot_of(c) == obj), obj)
    node = obj
    while node is not None:                       # peça de um grupo: sobe até o grupo convertido (feature 007)
        agg = getattr(node, 'btm_aggregate', None)
        if agg is not None and agg.is_aggregate:
            return node
        node = node.parent
    return None


def _draw_frame(layout, context):
    """Esquadria (grupo FRAME) ativa ou instalada: Instalar / Desinstalar (feature 007, RN-03)."""
    obj = context.active_object
    frame = install.frame_of(obj) if obj is not None else None
    if obj is not None and obj.get(install.WINDOW_FLAG) and obj.btm_window.frame is not None:
        frame = obj.btm_window.frame
    if frame is None:
        return
    box = layout.box()
    box.label(text=tr("Esquadria: {}").format(frame.name), icon='MOD_WIREFRAME')
    if install.cage_of(frame) is not None:
        box.operator("caffmob.window_uninstall", icon='UNLINKED')
    else:
        box.operator("caffmob.window_install", icon='MOD_BOOLEAN')


def _fmt(context, value):
    return units.format_value(value, context.scene)


def draw_aggregate(layout, context, include_import=True):
    if include_import:        # na barra lateral da 005, importar fica em Inserir
        row = layout.row(align=True)
        row.operator("caffmob.import_model", icon='IMPORT')
    col = layout.column(align=True)
    col.operator('caffmob_draw.authored_adopt')
    col.operator('caffmob_draw.member_add')
    col.operator('caffmob_draw.member_remove')
    col.operator('caffmob_draw.member_transfer')
    col.operator('caffmob_draw.authored_leaf')
    col.operator('caffmob_draw.authored_leaves_open')
    col.operator("caffmob.aggregate_convert", icon='LINKED')
    col.operator("caffmob.leaf_convert", icon='MOD_SIMPLEDEFORM')
    col.operator("caffmob.window_assemble", icon='MOD_BUILD')
    row = col.row(align=True)
    row.operator("caffmob.group_create", icon='GROUP')
    row.operator("caffmob.group_dissolve", text=tr("Desfazer grupo"), icon='X')
    _draw_frame(layout, context)
    obj = _active_aggregate(context)
    if obj is None:
        layout.label(text="Selecione a malha e, por último, o elemento pai.", icon='INFO')
        return
    agg = obj.btm_aggregate
    box = layout.box()
    box.label(text=tr("{} — pai: {}").format(obj.name, agg.parent_ref.name if agg.parent_ref else '—'), icon='OBJECT_DATA')
    if obj.btm_member.owner is not None and agg.kind == 'LEAF':
        box.operator('caffmob_draw.authored_leaf')
        box.prop(agg, 'open_value', slider=True)
        return
    if agg.kind == 'AGGREGATE':
        box.prop(agg, "face")
        box_p = apply.parent_box(obj)
        lim = limits.limits(box_p, tuple(agg.size), agg.face) if box_p else None
        for name in ('u', 'v'):
            row = box.row(align=True)
            row.prop(agg, name)
            if lim:
                row.label(text=f"{_fmt(context, lim[name][0])} a {_fmt(context, lim[name][1])}")
        row = box.row(align=True)
        row.prop(agg, "offset")
        if lim:
            row.label(text=tr("mín. {}").format(_fmt(context, lim['offset'][0])))
        box.operator("caffmob.aggregate_move", icon='VIEW_PAN')
        box.prop(agg, "perforate")
        row = box.row()
        reason = perforate.real_hole_reason(obj)
        row.enabled = agg.perforate and reason is None
        row.prop(agg, "real_hole")
        if agg.perforate and reason:
            box.label(text=reason, icon='INFO')
        box.prop(agg, "production_part")
        if agg.production_part:
            geometry = getattr(obj, 'btm_geometry', None)
            if geometry is not None:
                box.prop(geometry, "component")
                box.prop(geometry, "material")
    else:
        box.prop(agg, "motion", expand=True)
        if agg.motion == 'SWING':
            box.prop(agg, "hinge")
            box.prop(agg, "swing_sign")
            box.prop(agg, "max_angle")
        else:
            box.prop(agg, "slide_dir")
            box.prop(agg, "travel")
            if leaf.low_travel(obj):
                row = box.row()
                row.alert = True
                row.label(text=tr("Pouco curso para este lado: inverta o sentido"), icon='INFO')
        box.prop(agg, "open_value", slider=True)
        if agg.contact_name:
            row = box.row()
            row.alert = True
            message = "Folha encostou em {}" if agg.contact_kind == 'CLOSE' else "Folha bateu em {}"
            row.label(text=tr(message).format(agg.contact_name), icon='ERROR')
        if leaf.pivot_of(obj) is None:
            box.label(text="Pivô ausente; desconverta e converta de novo", icon='ERROR')
    layout.operator("caffmob.aggregate_unconvert", icon='UNLINKED')


class BTM_PT_Aggregate(bpy.types.Panel):
    bl_label = "Agregados e folhas"
    bl_idname = "BTM_PT_aggregate"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "CAFFMob Draw"
    bl_parent_id = "BTM_PT_object_properties"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        draw_aggregate(self.layout, context)


# Desenhados na barra lateral única (feature 005) pelas funções de desenho e pelo proxy; não registrados.
classes = ()


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        if cls.is_registered:
            bpy.utils.unregister_class(cls)
