"""Atribuição de acabamento por domínio (feature 067, D-15; data-delta §1).

`Object.btm_finish` fica na raiz do dono (escopo Componente) ou na própria peça (escopo Peça, que vence o dono):
`{domain, material, scale_mm, grain, source}`. O material vai por ponteiro; a escolha sobrevive ao rebuild porque
`customize/finish.reapply` a aplica de novo. `source` MIGRATED marca o que veio de `btm_custom.group_materials`
(M-03): a aparência continua pelo caminho antigo, e a entrada só mostra o estado no painel.
"""

import bpy  # type: ignore

from ..data.i18n import N_
from . import finish_core as fc

DOMAIN_ITEMS = (
    (fc.INTERNAL, N_("Interno"), N_("Faces internas da caixa e do fundo, prateleiras e divisórias")),
    (fc.EXTERNAL, N_("Externo"), N_("Faces aparentes da caixa, a face de trás do fundo e as frentes")),
    (fc.FRONTS, N_("Frentes"), N_("Só as frentes, com o veio próprio delas")),
    (fc.EDGE, N_("Fita"), N_("As bordas das chapas")),
)
SOURCE_ITEMS = (
    ('LIBRARY', N_("Biblioteca"), N_("Textura da biblioteca")),
    ('USER', N_("Usuário"), N_("Escolhido no painel")),
    ('MIGRATED', N_("Migrado"), N_("Veio dos grupos de material de uma versão anterior")),
)


class BTM_PG_FinishAssignment(bpy.types.PropertyGroup):
    domain: bpy.props.EnumProperty(name=N_("Domínio"), items=DOMAIN_ITEMS, options=set())  # type: ignore
    material: bpy.props.PointerProperty(name=N_("Material"), type=bpy.types.Material, options=set())  # type: ignore
    scale_mm: bpy.props.FloatProperty(name=N_("Escala (mm)"), description=N_("Tamanho físico da imagem; 0 = o "
                                      "do catálogo"), min=0.0, options=set())  # type: ignore
    grain: bpy.props.EnumProperty(name=N_("Veio"), items=(
        ('NONE', N_("Nenhum"), ""), ('H', N_("Horizontal"), ""), ('V', N_("Vertical"), "")),
        default='NONE', options=set())  # type: ignore
    source: bpy.props.EnumProperty(name=N_("Origem"), items=SOURCE_ITEMS, default='USER', options=set())  # type: ignore


classes = (BTM_PG_FinishAssignment,)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Object.btm_finish = bpy.props.CollectionProperty(type=BTM_PG_FinishAssignment)


def unregister():
    if hasattr(bpy.types.Object, 'btm_finish'):
        del bpy.types.Object.btm_finish
    for cls in reversed(classes):
        if cls.is_registered:
            bpy.utils.unregister_class(cls)
