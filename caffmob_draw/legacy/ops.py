"""Comandos de conversão das bibliotecas herdadas (feature 012, T060 e T068; D-25, D-26, D-29, D-30).

- `caffmob.legacy_convert`: converte os armários herdados da cena (ou só o ativo) em módulos CAFFMob, numa etapa de
  desfazer, e mostra o relatório de perdas;
- `caffmob.legacy_groups_convert`: grupos salvos nas bibliotecas herdadas (T068); abrir a confirmação já grava a
  oferta como feita, aceitando ou não (D-30).

O aviso ao abrir um arquivo com armários herdados sai do `load_post` (`legacy/__init__.py`) por `notify_legacy`.
"""

import bpy  # type: ignore

from ..data.i18n import tr
from . import convert, gate


def _show_report(context, title, lines):
    from ..operators import ops_standards
    ops_standards._set_report(title, lines)
    if not bpy.app.background and context.window is not None:
        bpy.ops.caffmob.standards_report('INVOKE_DEFAULT')


def notify_legacy():
    """Aviso (uma vez por arquivo aberto) quando há armários de bibliotecas antigas na cena."""
    from ..ui import save_feedback
    scene = bpy.context.scene
    if scene is None or gate.legacy_ui():
        return None
    count = len(gate.legacy_roots(scene))
    if count:
        save_feedback.show(tr("{} armário(s) de bibliotecas antigas: use Converter para CAFFMob na barra lateral")
                           .format(count))
    return None


class BTM_OT_LegacyConvert(bpy.types.Operator):
    """Converte armários frameless, face frame e closets em armários CAFFMob, com o relatório do que se perdeu"""
    bl_idname = "caffmob.legacy_convert"
    bl_label = "Converter para CAFFMob"
    bl_options = {'REGISTER', 'UNDO'}

    only_active: bpy.props.BoolProperty(
        name="Só o armário selecionado", default=False, options={'SKIP_SAVE'})  # type: ignore

    @classmethod
    def poll(cls, context):
        return context.mode == 'OBJECT' and context.scene is not None and bool(gate.legacy_roots(context.scene))

    def invoke(self, context, event):
        count = 1 if self.only_active else len(gate.legacy_roots(context.scene))
        return context.window_manager.invoke_confirm(
            self, event, title=tr("Converter para CAFFMob"),
            message=tr("{} armário(s) de bibliotecas antigas viram armários CAFFMob. Ctrl+Z desfaz.").format(count),
            confirm_text=tr("Converter"))

    def execute(self, context):
        roots = None
        if self.only_active:
            from ..selection import classify
            root, library = classify.module_root(context.active_object)
            if root is None or library not in gate.LEGACY_LIBRARIES:
                self.report({'WARNING'}, tr("Selecione um armário de biblioteca antiga"))
                return {'CANCELLED'}
            roots = [root]
        try:
            results = convert.convert_scene(context, roots)
        except convert.ConvertError as exc:
            self.report({'ERROR'}, str(exc))
            return {'CANCELLED'}
        lost = sum(1 for result in results if result.losses)
        self.report({'INFO'}, tr("{} armário(s) convertidos; {} com perdas").format(len(results), lost))
        _show_report(context, tr("Conversão para CAFFMob"), convert.report_lines(results))
        return {'FINISHED'}


class BTM_OT_LegacyGroupsConvert(bpy.types.Operator):
    """Converte os grupos salvos nas bibliotecas antigas em módulos CAFFMob da categoria Geral"""
    bl_idname = "caffmob.legacy_groups_convert"
    bl_label = "Converter grupos antigos"
    bl_options = {'REGISTER'}

    @classmethod
    def poll(cls, context):
        return context.mode == 'OBJECT'

    def invoke(self, context, event):
        from . import groups
        count = len(groups.pending_files())
        if not count:
            self.report({'INFO'}, tr("Nenhum grupo antigo para converter"))
            return {'CANCELLED'}
        groups.dismiss()          # a oferta do painel não volta, aceitando ou não (o comando fica em Criar categoria)
        return context.window_manager.invoke_confirm(
            self, event, title=tr("Converter grupos antigos"),
            message=tr("{} grupo(s) salvos nas bibliotecas antigas viram módulos CAFFMob em Geral. Os arquivos "
                       "originais ficam na pasta.").format(count), confirm_text=tr("Converter"))

    def execute(self, context):
        from ..library_panel import categories
        from . import groups
        saved, lines = groups.convert_pending(context)
        categories.invalidate()
        self.report({'INFO'}, tr("{} módulo(s) salvos em Geral").format(len(saved)))
        _show_report(context, tr("Conversão dos grupos antigos"), lines)
        return {'FINISHED'}


classes = (BTM_OT_LegacyConvert, BTM_OT_LegacyGroupsConvert)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        if cls.is_registered:
            bpy.utils.unregister_class(cls)
