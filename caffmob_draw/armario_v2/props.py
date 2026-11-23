"""PropertyGroups do construtor de armário v2 (feature 017, T003; data-delta §2 a §4).

Três grupos persistidos no `.blend`, cada um no seu dono:

- `Object.btm_armario` (`BTM_PG_ArmarioV2`): o spec completo do armário, as quatro flags de presença das chapas da
  caixa (D-18: presença por peça, sem enum de montagem rápida), o estado de abertura, a aba ativa e o snapshot.
- `Object.btm_armario_parte` (`BTM_PG_ArmarioParte`): uma instância por chapa gerada, fonte do corte (RN-24) e do
  alvo de animação (RN-10).
- `Scene.btm_armario_contrato` (`BTM_PG_ContratoChapas`): chapa máxima, as oito espessuras por papel, a montagem e as
  orientações padrão (RN-02).

Medidas em milímetros, como no motor de referência: o spec não converte unidade, quem converte é a geração (T020).
Os rótulos são desenhados pelo painel, que lê o texto do catálogo `data/translations/armario_v2.json`; aqui ficam só o
dado e os itens dos enums, lidos por atributo (`obj.btm_armario.largura`), nunca por `obj["..."]`.
"""

import bpy  # type: ignore

# Itens dos enums --------------------------------------------------------------------------------------------------

THICKNESS_ITEMS = [
    ('6', "6 mm", ""),
    ('15', "15 mm", ""),
    ('18', "18 mm", ""),
    ('25', "25 mm", ""),
]
MOUNT_ITEMS = [
    ('LATERAL_PASSANTE', "Lateral passante", "Laterais do piso ao topo"),
    ('BASE_PASSANTE', "Base passante", "Bases cobrem as laterais"),
]
ORIENTATION_ITEMS = [
    ('EM_PE', "Em pé", "Chapa em pé"),
    ('DEITADA', "Deitada", "Chapa deitada"),
]
TAB_ITEMS = [
    ('ESTRUTURA', "Estrutura", ""),
    ('DIVISOES', "Divisões", ""),
    ('GAVETAS', "Gavetas", ""),
    ('INTERNOS', "Internos", ""),
    ('PORTAS', "Portas", ""),
    ('DESLIZANTES', "Deslizantes", ""),
    ('FUNDOS', "Fundos", ""),
]
SUBTAB_DIVISION_ITEMS = [
    ('VERTICAL', "Vertical", ""),
    ('HORIZONTAL', "Horizontal", ""),
    ('MULTIPLA', "Múltipla", ""),
]
SUBTAB_DRAWER_ITEMS = [
    ('INTERNAS', "Internas", ""),
    ('SAPATEIRAS', "Sapateiras", ""),
    ('PRAT_CORREDICA', "Prat. c/ Corrediça", ""),
    ('EXTERNAS', "Externas", ""),
]
DIVISION_AXIS_ITEMS = [
    ('VERTICAL', "Vertical", ""),
    ('HORIZONTAL', "Horizontal", ""),
]
DIVISION_TYPE_ITEMS = [
    ('FIXA', "Fixa", ""),
    ('MOVEL', "Móvel", ""),
    ('ESPACADOR', "Distanciador", ""),
]
DOOR_HINGE_ITEMS = [
    ('ESQUERDA', "Esquerda", ""),
    ('DIREITA', "Direita", ""),
    ('ALTERNADA', "Alternada", ""),
]
SLIDING_MATERIAL_ITEMS = [
    ('MDF', "MDF", ""),
    ('VIDRO', "Vidro", ""),
    ('ALUMINIO', "Alumínio", ""),
]
SLIDING_BASE_ITEMS = [
    ('DENTRO', "Dentro", ""),
    ('FRENTE', "Frente", ""),
]
BACK_FIX_ITEMS = [
    ('CANAL', "Em canal", ""),
    ('SOBREPOSTO', "Sobreposto", ""),
]
FINISH_ITEMS = [
    ('MADEIRADO', "Madeirado", ""),
    ('BRANCO', "Branco", ""),
    ('CINZA', "Cinza", ""),
    ('PRETO', "Preto", ""),
]
INTERIOR_TYPE_ITEMS = [
    ('CABIDEIRO', "Cabideiro", ""),
    ('CALCEIRO', "Calceiro", ""),
    ('SAPATEIRA', "Sapateira", ""),
    ('MALEIRO', "Maleiro", ""),
]
DRAWER_MODEL_ITEMS = [
    ('s_cf_reta', "s/ CF Reta", "Gaveta sem contra-frente, puxador reto"),
    ('s_cf_normal', "s/ CF Normal", "Gaveta sem contra-frente, normal"),
    ('s_cf_vidro', "s/ CF Vidro", "Gaveta sem contra-frente, frente vidro"),
    ('s_cf_gola', "s/ CF Gola", "Gaveta sem contra-frente, perfil gola"),
    ('s_cf_cava', "s/ CF Cava", "Gaveta sem contra-frente, puxador cava"),
    ('c_cf_reta', "c/ CF Reta", "Gaveta com contra-frente, puxador reto"),
    ('c_cf_normal', "c/ CF Normal", "Gaveta com contra-frente, normal"),
    ('c_cf_vidro', "c/ CF Vidro", "Gaveta com contra-frente, frente vidro"),
    ('c_cf_gola', "c/ CF Gola", "Gaveta com contra-frente, perfil gola"),
    ('c_cf_cava', "c/ CF Cava", "Gaveta com contra-frente, puxador cava"),
]
GRAIN_ITEMS = [
    ('NONE', "Sem veio", ""),
    ('HORIZONTAL', "Horizontal", ""),
    ('VERTICAL', "Vertical", ""),
]
AXIS_ITEMS = [
    ('Y', "Y", ""),
    ('X', "X", ""),
    ('GIRO', "Giro", ""),
]

# Coleções do armário ---------------------------------------------------------------------------------------------


class BTM_PG_ArmarioDivisao(bpy.types.PropertyGroup):
    uid: bpy.props.StringProperty()  # type: ignore
    eixo: bpy.props.EnumProperty(items=DIVISION_AXIS_ITEMS, default='VERTICAL')  # type: ignore
    vao: bpy.props.StringProperty()  # type: ignore
    posicao: bpy.props.FloatProperty(subtype='DISTANCE', unit='LENGTH', default=0.0)  # type: ignore
    tipo: bpy.props.EnumProperty(items=DIVISION_TYPE_ITEMS, default='FIXA')  # type: ignore
    espessura: bpy.props.EnumProperty(items=THICKNESS_ITEMS, default='15')  # type: ignore


class BTM_PG_ArmarioGaveta(bpy.types.PropertyGroup):
    uid: bpy.props.StringProperty()  # type: ignore
    vao: bpy.props.StringProperty()  # type: ignore
    indice: bpy.props.IntProperty(min=0, default=0)  # type: ignore
    altura: bpy.props.FloatProperty(subtype='DISTANCE', unit='LENGTH', default=0.0)  # type: ignore
    modelo: bpy.props.EnumProperty(items=DRAWER_MODEL_ITEMS, default='s_cf_reta')  # type: ignore
    separador_colunas: bpy.props.IntProperty(min=1, max=6, default=1)  # type: ignore
    separador_linhas: bpy.props.IntProperty(min=1, max=5, default=1)  # type: ignore
    afastador_frente: bpy.props.BoolProperty(default=True)  # type: ignore
    afastador_tras: bpy.props.BoolProperty(default=True)  # type: ignore
    afastador_esq: bpy.props.BoolProperty(default=True)  # type: ignore
    afastador_dir: bpy.props.BoolProperty(default=True)  # type: ignore
    corredica_3d: bpy.props.BoolProperty(default=True)  # type: ignore


class BTM_PG_ArmarioInterno(bpy.types.PropertyGroup):
    uid: bpy.props.StringProperty()  # type: ignore
    vao: bpy.props.StringProperty()  # type: ignore
    tipo: bpy.props.EnumProperty(items=INTERIOR_TYPE_ITEMS, default='CABIDEIRO')  # type: ignore
    altura: bpy.props.FloatProperty(subtype='DISTANCE', unit='LENGTH', default=0.0)  # type: ignore


# Spec do armário -------------------------------------------------------------------------------------------------


class BTM_PG_ArmarioV2(bpy.types.PropertyGroup):
    largura: bpy.props.FloatProperty(subtype='DISTANCE', unit='LENGTH', default=1000.0,
                                     min=100.0, max=6000.0)  # type: ignore
    altura: bpy.props.FloatProperty(subtype='DISTANCE', unit='LENGTH', default=2400.0,
                                    min=100.0, max=3000.0)  # type: ignore
    profundidade: bpy.props.FloatProperty(subtype='DISTANCE', unit='LENGTH', default=510.0,
                                          min=100.0, max=1200.0)  # type: ignore
    tipo_montagem: bpy.props.EnumProperty(items=MOUNT_ITEMS, default='LATERAL_PASSANTE')  # type: ignore
    orientacao_frente: bpy.props.EnumProperty(items=ORIENTATION_ITEMS, default='EM_PE')  # type: ignore
    orientacao_tras: bpy.props.EnumProperty(items=ORIENTATION_ITEMS, default='EM_PE')  # type: ignore

    espessura_lateral: bpy.props.EnumProperty(items=THICKNESS_ITEMS, default='15')  # type: ignore
    espessura_base_inferior: bpy.props.EnumProperty(items=THICKNESS_ITEMS, default='15')  # type: ignore
    espessura_base_superior: bpy.props.EnumProperty(items=THICKNESS_ITEMS, default='15')  # type: ignore
    espessura_divisoria: bpy.props.EnumProperty(items=THICKNESS_ITEMS, default='15')  # type: ignore
    espessura_prateleira: bpy.props.EnumProperty(items=THICKNESS_ITEMS, default='15')  # type: ignore
    espessura_fundo: bpy.props.EnumProperty(items=THICKNESS_ITEMS, default='6')  # type: ignore
    espessura_gaveta: bpy.props.EnumProperty(items=THICKNESS_ITEMS, default='15')  # type: ignore
    espessura_porta: bpy.props.EnumProperty(items=THICKNESS_ITEMS, default='15')  # type: ignore
    espessura_folha: bpy.props.EnumProperty(items=THICKNESS_ITEMS, default='15')  # type: ignore
    bloquear_chapa: bpy.props.BoolProperty(default=True)  # type: ignore

    # Presença das chapas da caixa (RN-01, D-18). Montar Caixa liga as quatro; o usuário alterna peça por peça.
    lateral_esq_ativa: bpy.props.BoolProperty(default=False)  # type: ignore
    lateral_dir_ativa: bpy.props.BoolProperty(default=False)  # type: ignore
    base_inf_ativa: bpy.props.BoolProperty(default=False)  # type: ignore
    base_sup_ativa: bpy.props.BoolProperty(default=False)  # type: ignore

    divisoes: bpy.props.CollectionProperty(type=BTM_PG_ArmarioDivisao)  # type: ignore
    gavetas: bpy.props.CollectionProperty(type=BTM_PG_ArmarioGaveta)  # type: ignore
    internos: bpy.props.CollectionProperty(type=BTM_PG_ArmarioInterno)  # type: ignore

    porta_ativa: bpy.props.BoolProperty(default=False)  # type: ignore
    porta_folhas: bpy.props.IntProperty(min=1, max=4, default=1)  # type: ignore
    porta_dobradica: bpy.props.EnumProperty(items=DOOR_HINGE_ITEMS, default='ESQUERDA')  # type: ignore

    deslizante_ativa: bpy.props.BoolProperty(default=False)  # type: ignore
    deslizante_folhas: bpy.props.IntProperty(min=2, max=4, default=2)  # type: ignore
    deslizante_sobreposicao: bpy.props.FloatProperty(subtype='DISTANCE', unit='LENGTH', default=30.0,
                                                    min=10.0, max=60.0)  # type: ignore
    deslizante_material: bpy.props.EnumProperty(items=SLIDING_MATERIAL_ITEMS, default='MDF')  # type: ignore
    deslizante_base: bpy.props.EnumProperty(items=SLIDING_BASE_ITEMS, default='DENTRO')  # type: ignore
    trilho_profundidade: bpy.props.FloatProperty(subtype='DISTANCE', unit='LENGTH', default=70.0,
                                                 min=30.0, max=120.0)  # type: ignore

    fundo_ativo: bpy.props.BoolProperty(default=False)  # type: ignore
    fundo_fixacao: bpy.props.EnumProperty(items=BACK_FIX_ITEMS, default='CANAL')  # type: ignore
    fundo_recuo: bpy.props.FloatProperty(subtype='DISTANCE', unit='LENGTH', default=10.0,
                                         min=0.0, max=40.0)  # type: ignore

    acabamento: bpy.props.EnumProperty(items=FINISH_ITEMS, default='MADEIRADO')  # type: ignore

    aba: bpy.props.EnumProperty(items=TAB_ITEMS, default='ESTRUTURA')  # type: ignore
    subaba_divisoes: bpy.props.EnumProperty(items=SUBTAB_DIVISION_ITEMS, default='VERTICAL')  # type: ignore
    subaba_gavetas: bpy.props.EnumProperty(items=SUBTAB_DRAWER_ITEMS, default='INTERNAS')  # type: ignore

    aberto: bpy.props.BoolProperty(default=False)  # type: ignore
    gerado: bpy.props.BoolProperty(default=False)  # type: ignore
    origem: bpy.props.StringProperty()  # type: ignore
    snapshot: bpy.props.StringProperty()  # type: ignore


# Chapa gerada e contrato de chapas -------------------------------------------------------------------------------


class BTM_PG_ArmarioParte(bpy.types.PropertyGroup):
    papel: bpy.props.StringProperty()  # type: ignore
    componente: bpy.props.StringProperty()  # type: ignore
    comprimento_mm: bpy.props.FloatProperty(subtype='DISTANCE', unit='LENGTH', default=0.0)  # type: ignore
    largura_mm: bpy.props.FloatProperty(subtype='DISTANCE', unit='LENGTH', default=0.0)  # type: ignore
    espessura_mm: bpy.props.FloatProperty(subtype='DISTANCE', unit='LENGTH', default=0.0)  # type: ignore
    material: bpy.props.StringProperty()  # type: ignore
    veio: bpy.props.EnumProperty(items=GRAIN_ITEMS, default='NONE')  # type: ignore
    fita_l1: bpy.props.BoolProperty(default=False)  # type: ignore
    fita_l2: bpy.props.BoolProperty(default=False)  # type: ignore
    fita_w1: bpy.props.BoolProperty(default=False)  # type: ignore
    fita_w2: bpy.props.BoolProperty(default=False)  # type: ignore
    uid: bpy.props.StringProperty()  # type: ignore
    movel: bpy.props.BoolProperty(default=False)  # type: ignore
    curso_mm: bpy.props.FloatProperty(subtype='DISTANCE', unit='LENGTH', default=0.0)  # type: ignore
    eixo: bpy.props.EnumProperty(items=AXIS_ITEMS, default='Y')  # type: ignore


class BTM_PG_ContratoChapas(bpy.types.PropertyGroup):
    comprimento_max: bpy.props.FloatProperty(subtype='DISTANCE', unit='LENGTH', default=2750.0,
                                             min=0.0)  # type: ignore
    largura_max: bpy.props.FloatProperty(subtype='DISTANCE', unit='LENGTH', default=1830.0, min=0.0)  # type: ignore
    espessura_lateral: bpy.props.EnumProperty(items=THICKNESS_ITEMS, default='15')  # type: ignore
    espessura_base_inferior: bpy.props.EnumProperty(items=THICKNESS_ITEMS, default='15')  # type: ignore
    espessura_base_superior: bpy.props.EnumProperty(items=THICKNESS_ITEMS, default='15')  # type: ignore
    espessura_divisoria: bpy.props.EnumProperty(items=THICKNESS_ITEMS, default='15')  # type: ignore
    espessura_prateleira: bpy.props.EnumProperty(items=THICKNESS_ITEMS, default='15')  # type: ignore
    espessura_fundo: bpy.props.EnumProperty(items=THICKNESS_ITEMS, default='6')  # type: ignore
    espessura_gaveta: bpy.props.EnumProperty(items=THICKNESS_ITEMS, default='15')  # type: ignore
    espessura_porta: bpy.props.EnumProperty(items=THICKNESS_ITEMS, default='15')  # type: ignore
    montagem_padrao: bpy.props.EnumProperty(items=MOUNT_ITEMS, default='LATERAL_PASSANTE')  # type: ignore
    orientacao_frente_padrao: bpy.props.EnumProperty(items=ORIENTATION_ITEMS, default='EM_PE')  # type: ignore
    orientacao_tras_padrao: bpy.props.EnumProperty(items=ORIENTATION_ITEMS, default='EM_PE')  # type: ignore
    configurado: bpy.props.BoolProperty(default=False)  # type: ignore


classes = (BTM_PG_ArmarioDivisao, BTM_PG_ArmarioGaveta, BTM_PG_ArmarioInterno, BTM_PG_ArmarioV2,
           BTM_PG_ArmarioParte, BTM_PG_ContratoChapas)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Object.btm_armario = bpy.props.PointerProperty(type=BTM_PG_ArmarioV2)
    bpy.types.Object.btm_armario_parte = bpy.props.PointerProperty(type=BTM_PG_ArmarioParte)
    bpy.types.Scene.btm_armario_contrato = bpy.props.PointerProperty(type=BTM_PG_ContratoChapas)


def unregister():
    for owner, name in ((bpy.types.Scene, 'btm_armario_contrato'), (bpy.types.Object, 'btm_armario_parte'),
                        (bpy.types.Object, 'btm_armario')):
        if hasattr(owner, name):
            delattr(owner, name)
    for cls in reversed(classes):
        if cls.is_registered:
            bpy.utils.unregister_class(cls)
