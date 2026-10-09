"""Aba Estrutura do Editor de Armário (feature 006, T027; feature 008, T038; RN-07 a RN-08, D-07, D-16, D-25).

Feature 008: no modelo do Construtor, as chapas da caixa viram uma árvore com caixas de marcar (desmarcar remove em
Manter tudo; ✎ edita; ▾ abre os outros modos de remoção) seguida dos extras (base recuada, pés, rodapés, fechamentos,
vistas); depois Posição (cotas da divisória selecionada), Movimentação (passo das setas) e Materiais.

Texto da 006:

Uma linha por chapa que o módulo tem (tampo, base, fundo, laterais): medidas, material e espessura em uso, Editar e
Remover; removida mostra "removido · <modo>" e Restaurar. O que a biblioteca não faz fica desabilitado, com o motivo
no tooltip (RN-07). Brief: `_reversa_forward/006-editor-armario-abas/design/editor-abas.md`.
"""

import bpy  # type: ignore

from ..data.i18n import tr
from . import props
from . import catalog
from .panels import _TabPanel, draw_materials
from .structure import MODE_LABELS

FACE_FRAME_NOTE = "Face frame ainda não entra no plano de corte"


def face_frame_note(layout):
    s = props.session()
    if s is not None and s.library == 'FACE_FRAME':
        row = layout.row()
        row.active = False
        row.label(text=tr(FACE_FRAME_NOTE), icon='INFO')


def draw_assembly(layout, context):
    """Montagem do armário CAFFMob e a marca "Padrão próprio" (feature 012, T029; RN-08, RN-09)."""
    from . import bridge
    s = props.session()
    root = s.root() if s is not None else None
    if not bridge.is_caffmob_module(root):
        return
    box = layout.box()
    row = box.row(align=True)
    row.label(text=tr("Montagem"))
    row.prop(root.btm_cabinet, "assembly", expand=True)
    if bridge.is_own_standard(context, root):
        note = box.row()
        note.active = False
        note.label(text=tr("Padrão próprio: difere do Padrão de Dimensões global"), icon='MODIFIER')


class BTM_PT_CabinetEditorStructure(_TabPanel, bpy.types.Panel):
    bl_label = "Componentes"
    bl_idname = "BTM_PT_cabinet_editor_structure"
    bl_order = 2
    TAB = 'STRUCTURE'

    def draw(self, context):
        ui = context.window_manager.btm_cabinet_editor
        layout = self.layout
        draw_assembly(layout, context)
        if not ui.structure:
            row = layout.row()
            row.active = False
            row.label(text=tr("Esta biblioteca não tem estrutura editável"), icon='INFO')
        col = layout.column(align=True)
        for item in ui.structure:               # caixa = presente; desmarcar remove (Manter tudo) (D-07, RN-07)
            row = col.row(align=True)
            label = "{} {}".format(item.label, item.thickness)
            if item.changed:
                label += "  ·  " + tr("alterado")
            if item.removed and item.mode != 'KEEP':
                label += "  ·  " + tr(MODE_LABELS.get(item.mode, item.mode))
            check = row.row(align=True)
            check.enabled = not item.reason_remove
            check.prop(ui, "comp_" + item.role, text=label)
            edit = row.row(align=True)
            edit.enabled = not item.reason_edit and not item.removed
            edit.operator("caffmob.cabinet_editor_part_edit", text="", icon='GREASEPENCIL').role = item.role
            more = row.row(align=True)
            more.enabled = not item.reason_remove and not item.removed
            more.operator("caffmob.cabinet_editor_part_remove", text="", icon='DOWNARROW_HLT').role = item.role
        layout.separator()
        _draw_tree(layout, ui)
        face_frame_note(layout)


def _value_row(layout, ui, key, label):
    row = layout.row(align=True)
    row.prop(ui, "tree_" + key, text=tr(label))
    if hasattr(ui, "value_" + key):
        sub = row.row(align=True)
        sub.active = getattr(ui, "tree_" + key)
        sub.prop(ui, "value_" + key, text="")


def _draw_tree(layout, ui):
    """Extras do Construtor (RN-07a): grupos recolhíveis com os filhos; o valor ao lado de quem tem."""
    for key, label, parent, _default in catalog.TREE:
        if parent is not None:
            continue
        children = catalog.CHILDREN.get(key)
        if not children:
            _value_row(layout, ui, key, label)
            continue
        header, body = layout.panel("btm_tree_" + key, default_closed=True)
        _value_row(header, ui, key, label)
        if body is not None:
            for child in children:
                child_label = next(lbl for k, lbl, _p, _d in catalog.TREE if k == child)
                _value_row(body, ui, child, child_label)


class BTM_PT_CabinetEditorPosition(_TabPanel, bpy.types.Panel):
    bl_label = "Posição"
    bl_idname = "BTM_PT_cabinet_editor_position"
    bl_order = 3
    TAB = 'STRUCTURE'

    def draw(self, context):
        ui = context.window_manager.btm_cabinet_editor
        layout = self.layout
        layout.label(text=tr("Livre"), icon='OBJECT_ORIGIN')
        col = layout.column(align=True)
        col.enabled = props.has_position()           # como no Construtor: só com uma divisória selecionada
        for which in ('front', 'low', 'back', 'high'):
            col.prop(ui, "pos_" + which)
        if not col.enabled:
            hint = layout.row()
            hint.active = False
            hint.label(text=tr("Selecione uma divisória na vista"))


class BTM_PT_CabinetEditorMovement(_TabPanel, bpy.types.Panel):
    bl_label = "Movimentação"
    bl_idname = "BTM_PT_cabinet_editor_movement"
    bl_order = 4
    bl_options = {'DEFAULT_CLOSED'}
    TAB = 'STRUCTURE'

    def draw(self, context):
        ui = context.window_manager.btm_cabinet_editor
        col = self.layout.column(align=True)
        col.prop(ui, "step_initial")
        col.prop(ui, "step")
        hint = self.layout.row()
        hint.active = False
        hint.label(text=tr("Setas movem a divisória selecionada"))


class BTM_PT_CabinetEditorMaterials(_TabPanel, bpy.types.Panel):
    bl_label = "Materiais"
    bl_idname = "BTM_PT_cabinet_editor_materials"
    bl_order = 5
    bl_options = {'DEFAULT_CLOSED'}
    TAB = 'STRUCTURE'

    def draw(self, context):
        draw_materials(self.layout, context)


classes = (BTM_PT_CabinetEditorStructure, BTM_PT_CabinetEditorPosition, BTM_PT_CabinetEditorMovement,
           BTM_PT_CabinetEditorMaterials)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        if cls.is_registered:
            bpy.utils.unregister_class(cls)
