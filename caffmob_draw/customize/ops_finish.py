"""Aplicar acabamento por domínio num passo de Undo (feature 067, T060; RF-041, RF-043, RN-08).

- `caffmob.finish_apply` recebe os domínios, o escopo (Peça selecionada ou Componente), o material e a escala, e
  aplica pela `customize/finish.apply`. O alvo vem por nome (`object_name`), porque o soltar de textura chama o
  operador ao fim do download, quando a seleção pode ter mudado (D-16).
- `caffmob.finish_apply_draft`: o "Aplicar" da seção Acabamentos, com o rascunho `WindowManager.btm_finish_draft`.

Dono sem papel nenhum é recusado com o motivo: quem chama abre o assistente de classificação (RF-042). Recusa nunca
termina `FINISHED` (RNF Confiabilidade).
"""

import bpy  # type: ignore

from ..data.i18n import N_, tr
from . import finish, finish_core as fc
from .finish_props import DOMAIN_ITEMS

SCOPE_ITEMS = (
    ('PART', N_("Peça selecionada"), N_("Só a peça em que a textura caiu")),
    ('COMPONENT', N_("Componente"), N_("Todas as peças do móvel nos domínios escolhidos")),
)
NO_ROLES = N_("Este móvel não tem papéis de acabamento: classifique as peças no assistente")
NO_DOMAIN = N_("Escolha ao menos um domínio")
NO_MATERIAL = N_("Escolha um material")
NOTHING = N_("Nenhuma face ou peça do alvo pertence aos domínios escolhidos")


def run(operator, obj, domains, material, scope, scale_mm=0.0, source='USER', grain=None):
    owner = finish.owner_of(obj)
    if owner is None:
        operator.report({'WARNING'}, tr("Selecione um móvel, uma peça ou um objeto"))
        return {'CANCELLED'}
    domains = tuple(d for d in fc.DOMAINS if d in domains)
    if not domains:
        operator.report({'WARNING'}, tr(NO_DOMAIN))
        return {'CANCELLED'}
    if material is None:
        operator.report({'WARNING'}, tr(NO_MATERIAL))
        return {'CANCELLED'}
    if not finish.has_roles(owner):
        operator.report({'WARNING'}, tr(NO_ROLES))
        return {'CANCELLED'}
    pieces = [obj] if scope == 'PART' and obj is not owner else None
    changed = finish.apply(owner, domains, material, pieces, scale_mm, source, grain)
    if not changed:
        operator.report({'WARNING'}, tr(NOTHING))
        return {'CANCELLED'}
    operator.report({'INFO'}, tr("Acabamento {} aplicado em {} peça(s)").format(material.name, changed))
    return {'FINISHED'}


class BTM_OT_FinishApply(bpy.types.Operator):
    """Aplica um material nos domínios escolhidos (Interno, Externo, Frentes, Fita) do móvel ou da peça"""
    bl_idname = 'caffmob.finish_apply'
    bl_label = N_("Aplicar acabamento")
    bl_options = {'REGISTER', 'UNDO'}

    domains: bpy.props.EnumProperty(name=N_("Domínios"), items=DOMAIN_ITEMS, options={'ENUM_FLAG'})  # type: ignore
    scope: bpy.props.EnumProperty(name=N_("Escopo"), items=SCOPE_ITEMS, default='COMPONENT')  # type: ignore
    material: bpy.props.StringProperty(name=N_("Material"))  # type: ignore
    scale_mm: bpy.props.FloatProperty(name=N_("Escala (mm)"), min=0.0)  # type: ignore
    source: bpy.props.EnumProperty(name=N_("Origem"), items=(('USER', N_("Usuário"), ""), ('LIBRARY', N_("Biblioteca"), "")),
                                   default='USER', options={'HIDDEN'})  # type: ignore
    object_name: bpy.props.StringProperty(options={'HIDDEN', 'SKIP_SAVE'})  # type: ignore

    def execute(self, context):
        obj = bpy.data.objects.get(self.object_name) if self.object_name else context.active_object
        return run(self, obj, self.domains, bpy.data.materials.get(self.material), self.scope, self.scale_mm,
                   self.source)


class BTM_OT_FinishApplyDraft(bpy.types.Operator):
    """Aplica o acabamento escolhido na seção Acabamentos ao selecionado"""
    bl_idname = 'caffmob.finish_apply_draft'
    bl_label = N_("Aplicar acabamento")
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        draft = context.window_manager.btm_finish_draft
        grain = draft.grain if fc.FRONTS in draft.domain and draft.grain != 'NONE' else None
        return run(self, context.active_object, draft.domain, draft.material, draft.scope, draft.scale_mm,
                   'USER', grain)


classes = (BTM_OT_FinishApply, BTM_OT_FinishApplyDraft)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        if cls.is_registered:
            bpy.utils.unregister_class(cls)
