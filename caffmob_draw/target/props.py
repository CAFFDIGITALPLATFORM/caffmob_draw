"""Propriedades do alvo da seleção (feature 067, data-delta §1).

- `Object.btm_part.grain`: veio da peça (NONE/H/V), guardado por objeto e lido pelo corte (D-13). Até a onda 3 é só
  dado: a textura não gira.
- `WindowManager.btm_target`: estado de interface fora do arquivo e do Undo: o escopo das cotas (Peça ou Conjunto,
  D-07) e o último erro de um setter (D-04).
- `WindowManager.btm_cladding_draft`: rascunho do revestimento selecionado (RF-020), carregado pelo snapshot.
"""

import bpy  # type: ignore

from ..data.i18n import N_

GRAIN_ITEMS = (
    ('NONE', N_("Nenhum"), N_("Peça sem veio")),
    ('H', N_("Horizontal"), N_("Veio na horizontal da peça instalada")),
    ('V', N_("Vertical"), N_("Veio na vertical da peça instalada")),
)
COTA_SCOPE_ITEMS = (
    ('PART', N_("Peça"), N_("As cotas medem e movem a peça selecionada")),
    ('ASSEMBLY', N_("Conjunto"), N_("As cotas medem e movem o conjunto da peça")),
)


class BTM_PG_Part(bpy.types.PropertyGroup):
    # Sem 'ANIMATABLE': o veio é intenção de fabricação, não muda por quadro (RNF da 067).
    grain: bpy.props.EnumProperty(name=N_("Veio"), items=GRAIN_ITEMS, default='NONE', options=set())  # type: ignore


class BTM_PG_Target(bpy.types.PropertyGroup):
    cota_scope: bpy.props.EnumProperty(name=N_("Escopo das cotas"), items=COTA_SCOPE_ITEMS, default='PART',
                                       options=set())  # type: ignore
    error: bpy.props.StringProperty(name=N_("Erro"), options=set())  # type: ignore
    legacy_cotas: bpy.props.BoolProperty(
        name=N_("Cotas antigas"), description=N_("Mostra as cotas de afastamento e Mover na Parede do módulo"),
        default=False, options=set())  # type: ignore


_CLASSES = (BTM_PG_Part, BTM_PG_Target)


def register():
    for cls in _CLASSES:
        bpy.utils.register_class(cls)
    bpy.types.Object.btm_part = bpy.props.PointerProperty(type=BTM_PG_Part)
    bpy.types.WindowManager.btm_target = bpy.props.PointerProperty(type=BTM_PG_Target)
    # Rascunho do revestimento selecionado (RF-020): digitar aqui não refaz nada; "Aplicar" leva ao revestimento.
    from ..cladding import props as cladding_props
    bpy.types.WindowManager.btm_cladding_draft = bpy.props.PointerProperty(type=cladding_props.BTM_PG_Cladding)


def unregister():
    for owner, name in ((bpy.types.WindowManager, 'btm_cladding_draft'), (bpy.types.WindowManager, 'btm_target'),
                        (bpy.types.Object, 'btm_part')):
        if hasattr(owner, name):
            delattr(owner, name)
    for cls in reversed(_CLASSES):
        bpy.utils.unregister_class(cls)
