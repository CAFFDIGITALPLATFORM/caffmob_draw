"""Painéis da região lateral do Editor de Paredes (T030; RF-05, RF-08 a RF-10, D-07).

Só aparecem na área do Image Editor marcada como editor (`window.is_editor_area`):
- Ferramentas: Selecionar/Mover, Construir Parede, Inverter Sentido, Adicionar/Remover Vértice, Enquadrar;
- Painel: campos do trecho selecionado (comprimento na linha escolhida, ângulos, espessura, pés-direitos, orientação,
  tipo); ângulo do arco desabilitado, porque as paredes do Home Builder 5 são retas;
- Grid: tamanho e linhas magnéticas; padrões do lápis;
- OK / Cancelar, com o erro do último campo e a lista de itens que não cabem.

Na cena do CAFF MOBI os mesmos painéis (mais "Portas e Janelas") são desenhados por `classico_v2`, sobre o documento v2.
"""

import bpy  # type: ignore

from ..data.i18n import tr
from . import props, window


class _EditorPanel:
    bl_space_type = 'IMAGE_EDITOR'
    bl_region_type = 'UI'
    bl_category = "Editor de Paredes"

    @classmethod
    def poll(cls, context):
        return window.is_editor_area(context)


def _v2(context, layout, nome):
    """Cena do CAFF MOBI: o mesmo painel, desenhado por `classico_v2` sobre o documento v2. Devolve se desenhou."""
    s = props.session()
    if not (s and s.v2):
        return False
    from . import classico_v2
    getattr(classico_v2, 'painel_' + nome)(layout, context, s)
    return True


class BTM_PT_WallEditorTools(_EditorPanel, bpy.types.Panel):
    bl_label = "Ferramentas"
    bl_idname = "BTM_PT_wall_editor_tools"
    bl_order = 0

    def draw(self, context):
        if _v2(context, self.layout, 'ferramentas'):
            return
        state = context.window_manager.btm_wall_editor
        col = self.layout.column(align=True)
        col.prop(state, "tool", expand=True)
        self.layout.operator("caffmob.wall_editor_fit", icon='ZOOM_ALL')


class BTM_PT_WallEditorSegment(_EditorPanel, bpy.types.Panel):
    bl_label = "Painel"
    bl_idname = "BTM_PT_wall_editor_segment"
    bl_order = 1

    def draw(self, context):
        layout = self.layout
        if _v2(context, layout, 'trecho'):
            return
        state = context.window_manager.btm_wall_editor
        s = props.session()
        chain, i = s.segment() if s else (None, None)
        if chain is None:
            layout.label(text="Selecione um trecho na planta.", icon='INFO')
            return
        layout.use_property_split = True
        layout.use_property_decorate = False
        if s.lote():
            _painel_lote(layout, state, s)          # 067 onda 8 (D-40, RF-163)
            return
        layout.prop(state, "line")
        layout.prop(state, "length_text")
        angles = layout.column()
        angles.enabled = not chain.segments[i].lock_angle      # com a trava, o ângulo não muda (questions.md, pergunta 11)
        angles.prop(state, "angle_abs")
        angles.prop(state, "angle_rel")
        row = layout.row()
        row.enabled = False
        row.label(text="Ângulo do Arco: paredes curvas não são suportadas")
        layout.prop(state, "lock_angle")
        layout.prop(state, "thickness_text")
        layout.prop(state, "height_text")
        layout.prop(state, "end_height_text")
        layout.prop(state, "direction", expand=True)
        layout.prop(state, "wall_type")


def _painel_lote(layout, state, s):
    """Várias paredes (D-40): espessura, pés-direitos e tipo em lote, com "Múltiplos" quando diferem. Comprimento,
    ângulos, direção e trava valem um trecho por vez. O material não entra: o trecho do projeto do addon não o guarda,
    e ele continua aplicado depois, no 3D."""
    from .studio_ui import campo_texto
    layout.label(text=tr("{} paredes selecionadas").format(len(s.lote())), icon='STICKY_UVS_LOC')
    for field, prop in (('thickness', 'thickness_text'), ('height', 'height_text'), ('end_height', 'end_height_text')):
        campo_texto(layout, state, prop, tr("Múltiplos") if props.multiplos(s, field) else "")
    row = layout.row()
    row.prop(state, "wall_type")
    if props.multiplos(s, 'wall_type'):
        row.label(text=tr("Múltiplos"))
    single = layout.column()
    single.enabled = False
    single.prop(state, "length_text")
    single.prop(state, "angle_abs")
    single.label(text=tr("Um trecho por vez"), icon='INFO')


class BTM_PT_WallEditorOpenings(_EditorPanel, bpy.types.Panel):
    bl_label = "Portas e Janelas"
    bl_idname = "BTM_PT_wall_editor_openings"
    bl_order = 2

    @classmethod
    def poll(cls, context):
        s = props.session()
        return window.is_editor_area(context) and bool(s and s.v2)      # só a cena do CAFF MOBI guarda aberturas aqui

    def draw(self, context):
        _v2(context, self.layout, 'aberturas')


class BTM_PT_WallEditorGrid(_EditorPanel, bpy.types.Panel):
    bl_label = "Grid"
    bl_idname = "BTM_PT_wall_editor_grid"
    bl_order = 3

    def draw(self, context):
        layout = self.layout
        if _v2(context, layout, 'grade'):
            return
        state = context.window_manager.btm_wall_editor
        layout.use_property_split = True
        layout.use_property_decorate = False
        layout.prop(state, "grid_size")
        layout.prop(state, "magnetic")
        layout.separator()
        layout.label(text="Novas paredes")
        layout.prop(state, "new_direction")
        layout.prop(state, "new_thickness")
        layout.prop(state, "new_height")


class BTM_PT_WallEditorConfirm(_EditorPanel, bpy.types.Panel):
    bl_label = "Confirmar"
    bl_idname = "BTM_PT_wall_editor_confirm"
    bl_order = 99      # OK/Cancelar no fim do painel (D-30); com HIDE_HEADER o Blender ignora bl_order e põe no topo

    def draw(self, context):
        layout = self.layout
        if _v2(context, layout, 'confirmar'):
            return
        s = props.session()
        if s is not None and s.error:
            layout.label(text=s.error, icon='ERROR')
        if s is not None and s.warnings:
            box = layout.box()
            box.label(text="Itens que não cabem:", icon='ERROR')
            for text in s.warnings[:8]:
                box.label(text=text)
            if len(s.warnings) > 8:
                box.label(text=tr("… e mais {}").format(len(s.warnings) - 8))
        if s is not None and s.removed_modules:
            box = layout.box()
            box.label(text="Módulos em trechos apagados:", icon='QUESTION')
            for text in s.removed_modules[:8]:
                box.label(text=text)
            if len(s.removed_modules) > 8:
                box.label(text=tr("… e mais {}").format(len(s.removed_modules) - 8))
            box.prop(context.window_manager.btm_wall_editor, "remove_modules")
            box.label(text="Desmarcado, os módulos ficam soltos no lugar.")
        if s is not None and s.height_mismatches:
            box = layout.box()
            from ..data import units
            box.label(text=tr("Pé-direito do projeto: {}").format(units.format_value(s.project_height)), icon='INFO')
            box.label(text="Paredes com outra altura:")
            for text in s.height_mismatches[:8]:
                box.label(text=text)
            if len(s.height_mismatches) > 8:
                box.label(text=tr("… e mais {}").format(len(s.height_mismatches) - 8))
            box.prop(context.window_manager.btm_wall_editor, "equalize_height")
        row = layout.row(align=True)
        row.scale_y = 1.4
        row.operator("caffmob.wall_editor_ok", text="OK", icon='CHECKMARK')
        row.operator("caffmob.wall_editor_cancel", text="Cancelar", icon='CANCEL')


classes = (BTM_PT_WallEditorTools, BTM_PT_WallEditorSegment, BTM_PT_WallEditorOpenings, BTM_PT_WallEditorGrid,
           BTM_PT_WallEditorConfirm)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
