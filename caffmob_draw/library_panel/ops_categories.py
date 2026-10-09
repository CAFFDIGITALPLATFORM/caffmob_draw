"""Criar categoria e trocar a linha da categoria (feature 012, T025; RN-03, RN-04, D-17, D-30)."""

import bpy  # type: ignore

from ..data.i18n import tr
from . import categories, categories_core, draw

_LINE_ITEMS = [(code, label, "") for code, label in categories_core.LINE_LABELS.items()]


class BTM_OT_LibraryCategoryCreate(bpy.types.Operator):
    """Cria uma categoria na biblioteca do usuário, com a linha do Padrão de Dimensões que os armários dela usam"""
    bl_idname = "caffmob.library_category_create"
    bl_label = "Criar categoria"
    bl_options = {'REGISTER'}

    name: bpy.props.StringProperty(name="Nome")  # type: ignore
    line: bpy.props.EnumProperty(name="Linha do padrão", items=_LINE_ITEMS, default='COZ')  # type: ignore

    def invoke(self, context, event):
        self.name = ""
        return context.window_manager.invoke_props_dialog(self, title=tr("Criar categoria"))

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "name")
        layout.prop(self, "line")
        if draw.offer_groups() or _has_legacy_groups():
            layout.separator()
            layout.operator("caffmob.legacy_groups_convert", text=tr("Converter grupos antigos"), icon='FILE_REFRESH')

    def execute(self, context):
        reason = categories.create(self.name, self.line)
        if reason:
            self.report({'WARNING'}, tr(reason))
            return {'CANCELLED'}
        self.report({'INFO'}, tr("Categoria criada: {}").format(self.name.strip()))
        draw.tag_redraw(context)
        return {'FINISHED'}


def _has_legacy_groups():
    try:
        from ..legacy import groups
        return bool(groups.pending_files())
    except (ImportError, AttributeError, OSError):
        return False


class BTM_OT_LibraryCategorySetLine(bpy.types.Operator):
    """Troca a linha do Padrão de Dimensões da categoria"""
    bl_idname = "caffmob.library_category_set_line"
    bl_label = "Trocar linha"
    bl_options = {'REGISTER'}

    category: bpy.props.StringProperty()  # type: ignore
    line: bpy.props.EnumProperty(name="Linha do padrão", items=_LINE_ITEMS, default='COZ')  # type: ignore

    def invoke(self, context, event):
        found = categories.find(self.category)
        if found is None or found.fixed:
            self.report({'WARNING'}, tr("Só as categorias do usuário trocam de linha"))
            return {'CANCELLED'}
        self.line = found.line
        return context.window_manager.invoke_props_dialog(self, title=self.category)

    def execute(self, context):
        categories.set_line(self.category, self.line)
        return {'FINISHED'}


classes = (BTM_OT_LibraryCategoryCreate, BTM_OT_LibraryCategorySetLine)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        if cls.is_registered:
            bpy.utils.unregister_class(cls)
