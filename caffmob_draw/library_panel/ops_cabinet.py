"""Criar armário (feature 012, T027; D-18, RN-05).

Um diálogo curto, preenchido pelo Padrão de Dimensões ativo: tipo, largura, montagem e linha (padrão: a da última
categoria aberta). Confirmar cria o módulo CAFFMob no cursor 3D (`caffmob.cabinet_builder`, que lê altura,
profundidade e chapas do padrão) e abre o editor de armário nele; cancelar não cria nada.
"""

import bpy  # type: ignore

from ..data.i18n import tr
from . import categories_core

_TYPE_ITEMS = [('BASE', "Balcão", ""), ('WALL', "Aéreo", ""), ('TALL', "Torre", "")]
_ASSEMBLY_ITEMS = [('LATERAL', "Lateral passante", ""), ('BASE', "Base passante", "")]
_LINE_ITEMS = [(code, label, "") for code, label in categories_core.LINE_LABELS.items()]


def _defaults(context, line, cabinet_type):
    from ..operators.cabinet_builder import standard_defaults
    found, _definition = standard_defaults(context, line, cabinet_type)
    return found


class BTM_OT_LibraryCreateCabinet(bpy.types.Operator):
    """Cria um armário CAFFMob pelo Padrão de Dimensões e abre o editor de armário nele"""
    bl_idname = "caffmob.library_create_cabinet"
    bl_label = "Criar armário"
    bl_options = {'REGISTER', 'UNDO'}

    cabinet_type: bpy.props.EnumProperty(name="Tipo", items=_TYPE_ITEMS, default='BASE')  # type: ignore
    width: bpy.props.FloatProperty(name="Largura", default=0.8, min=0.1, max=3.0, subtype='DISTANCE',
                                   unit='LENGTH')  # type: ignore
    assembly: bpy.props.EnumProperty(name="Montagem", items=_ASSEMBLY_ITEMS, default='LATERAL')  # type: ignore
    line: bpy.props.EnumProperty(name="Linha do padrão", items=_LINE_ITEMS, default='COZ')  # type: ignore
    open_editor: bpy.props.BoolProperty(default=True, options={'SKIP_SAVE', 'HIDDEN'})  # type: ignore

    @classmethod
    def poll(cls, context):
        return context.mode == 'OBJECT'

    def invoke(self, context, event):
        # Feature 015 (T036; RN-11): "Criar armário" abre a galeria de estruturas de caixa na aba da linha atual; o
        # diálogo antigo continua para quem chama sem a galeria (EXEC).
        state = getattr(context.window_manager, 'btm_library', None)
        line = state.line if state is not None and state.line in categories_core.LINES else 'COZ'
        if bpy.ops.caffmob.structure_gallery.poll():
            bpy.ops.caffmob.structure_gallery('INVOKE_DEFAULT', environment=line)
            return {'CANCELLED'}                 # o módulo nasce no OK da galeria, com o passo de desfazer dele
        return self._invoke_dialog(context)

    def _invoke_dialog(self, context):
        from ..standards import api
        state = getattr(context.window_manager, 'btm_library', None)
        line = state.line if state is not None and state.line in categories_core.LINES else 'COZ'
        self.line = line
        self.assembly = api.active_assembly(context.scene)
        self.width = _defaults(context, line, self.cabinet_type).width
        return context.window_manager.invoke_props_dialog(self, title=tr("Criar armário"), confirm_text=tr("Criar"))

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "cabinet_type", expand=True)
        layout.prop(self, "width")
        layout.prop(self, "assembly", expand=True)
        layout.prop(self, "line")
        found = _defaults(context, self.line, self.cabinet_type)
        hint = layout.row()
        hint.active = False
        unit = context.scene.unit_settings
        from .. import units
        hint.label(text=tr("Altura {} · profundidade {} (do padrão)").format(
            units.unit_to_string(unit, found.height), units.unit_to_string(unit, found.depth)))

    def execute(self, context):
        result = bpy.ops.caffmob.cabinet_builder(cabinet_type=self.cabinet_type, width=self.width, line=self.line,
                                                 assembly=self.assembly)
        if 'FINISHED' not in result:
            return {'CANCELLED'}
        if self.open_editor and bpy.ops.caffmob.cabinet_editor.poll():
            bpy.ops.caffmob.cabinet_editor('INVOKE_DEFAULT')
        return {'FINISHED'}


classes = (BTM_OT_LibraryCreateCabinet,)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        if cls.is_registered:
            bpy.utils.unregister_class(cls)
