"""Spec do armário v2 em milímetros (feature 017, T012; RN-04, RN-05, RN-15).

Python puro, sem `bpy`: o painel lê estes campos do `BTM_PG_ArmarioV2` (T003) e os testes rodam fora do Blender. O
spec **não converte unidade**; quem converte é a geração das malhas, em `build.py` (T020), dividindo por 1000 num
único ponto.

Dezessete medidas: as nove espessuras por papel (`THICKNESS_FIELDS`, restritas a 6, 15, 18 e 25 mm) e as oito medidas
com faixa (`RANGES`). O `data-delta.md` §2 é a verdade; o texto de T005/T012 fala em "dezesseis", contagem que não
fecha com a tabela.

Encontro das chapas (RN-04, D-10): em "lateral passante" as laterais vão do piso ao topo e as bases ficam entre elas;
em "base passante" **as duas bases** cobrem a largura e as laterais ficam entre elas. `carcass_lengths` delega para
`cabinet_editor.structure.carcass_lengths` na montagem lateral passante; na base passante a conta é feita aqui porque
a função antiga (feature 012) mantém o topo entre as laterais, enquanto a RN-04 desta feature manda as duas bases
passarem. A divergência está registrada nas notas de execução do `actions.md`.

Fundo (RN-15): encaixado em canal, o recuo afasta o painel da face de trás sem consumir a profundidade útil além da
própria chapa; sobreposto, ele fica na face de trás e o recuo sai da profundidade útil.
"""

from dataclasses import dataclass

from ..cabinet_editor import structure

# Encontros, orientações, fixação do fundo e origem das frestas (mesmas grafias dos enums de `props.py`).
LATERAL_PASSANTE, BASE_PASSANTE = 'LATERAL_PASSANTE', 'BASE_PASSANTE'
EM_PE, DEITADA = 'EM_PE', 'DEITADA'
CANAL, SOBREPOSTO = 'CANAL', 'SOBREPOSTO'

THICKNESSES = (6, 15, 18, 25)

# As nove espessuras do armário (§2). O contrato de chapas grava oito: a `espessura_folha` é ferragem da deslizante.
THICKNESS_FIELDS = (
    'espessura_lateral',
    'espessura_base_inferior',
    'espessura_base_superior',
    'espessura_divisoria',
    'espessura_prateleira',
    'espessura_fundo',
    'espessura_gaveta',
    'espessura_porta',
    'espessura_folha',
)

RANGES = {
    'largura': (100.0, 6000.0),
    'altura': (100.0, 3000.0),
    'profundidade': (100.0, 1200.0),
    'porta_folhas': (1, 4),
    'deslizante_folhas': (2, 4),
    'deslizante_sobreposicao': (10.0, 60.0),
    'trilho_profundidade': (30.0, 120.0),
    'fundo_recuo': (0.0, 40.0),
}

# Nome de cada medida com faixa nas mensagens de `validate`.
RANGE_LABELS = {
    'largura': "Largura",
    'altura': "Altura",
    'profundidade': "Profundidade",
    'porta_folhas': "Folhas da porta",
    'deslizante_folhas': "Folhas da deslizante",
    'deslizante_sobreposicao': "Sobreposição da deslizante",
    'trilho_profundidade': "Profundidade do trilho",
    'fundo_recuo': "Recuo do fundo",
}

# Nome de cada espessura nas mensagens de `validate`.
THICKNESS_LABELS = {
    'espessura_lateral': "Espessura da lateral",
    'espessura_base_inferior': "Espessura da base inferior",
    'espessura_base_superior': "Espessura da base superior",
    'espessura_divisoria': "Espessura da divisória",
    'espessura_prateleira': "Espessura da prateleira",
    'espessura_fundo': "Espessura do fundo",
    'espessura_gaveta': "Espessura da gaveta",
    'espessura_porta': "Espessura da porta",
    'espessura_folha': "Espessura da folha",
}


@dataclass(frozen=True)
class Spec:
    """O armário em milímetros: medidas externas, montagem, espessuras por papel, portas, deslizante e fundo."""

    largura: float = 1000.0
    altura: float = 2400.0
    profundidade: float = 510.0
    tipo_montagem: str = LATERAL_PASSANTE
    orientacao_frente: str = EM_PE
    orientacao_tras: str = EM_PE

    espessura_lateral: float = 15.0
    espessura_base_inferior: float = 15.0
    espessura_base_superior: float = 15.0
    espessura_divisoria: float = 15.0
    espessura_prateleira: float = 15.0
    espessura_fundo: float = 6.0
    espessura_gaveta: float = 15.0
    espessura_porta: float = 15.0
    espessura_folha: float = 15.0
    bloquear_chapa: bool = True

    # Presença das chapas da caixa (RN-01, D-18): Montar Caixa liga as quatro, o usuário alterna peça por peça.
    lateral_esq_ativa: bool = False
    lateral_dir_ativa: bool = False
    base_inf_ativa: bool = False
    base_sup_ativa: bool = False

    porta_ativa: bool = False
    porta_folhas: int = 1
    porta_dobradica: str = 'ESQUERDA'

    deslizante_ativa: bool = False
    deslizante_folhas: int = 2
    deslizante_sobreposicao: float = 30.0
    deslizante_material: str = 'MDF'
    deslizante_base: str = 'DENTRO'
    trilho_profundidade: float = 70.0

    fundo_ativo: bool = False
    fundo_fixacao: str = CANAL
    fundo_recuo: float = 10.0

    acabamento: str = 'MADEIRADO'


def thickness_ok(value):
    """A espessura é uma das quatro aceitas (6, 15, 18 ou 25 mm, RN-05)?"""
    return value in THICKNESSES


def _fmt(value):
    """Número em milímetros sem zero à toa: 100.0 → "100", 12.5 → "12.5"."""
    return f"{value:g}"


def validate(spec):
    """Lista dos problemas do spec (vazia = pode gerar). Medidas de faixa, espessuras e exclusividade das portas."""
    problemas = []
    for campo, (lo, hi) in RANGES.items():
        valor = getattr(spec, campo)
        if not lo - 1e-9 <= valor <= hi + 1e-9:
            problemas.append("{} fora da faixa: {} mm (use {}–{} mm)".format(
                RANGE_LABELS[campo], _fmt(valor), _fmt(lo), _fmt(hi)))
    for campo in THICKNESS_FIELDS:
        valor = getattr(spec, campo)
        if not thickness_ok(valor):
            problemas.append("{} fora das espessuras aceitas: {} mm (use 6, 15, 18 ou 25 mm)".format(
                THICKNESS_LABELS[campo], _fmt(valor)))
    if spec.porta_ativa and spec.deslizante_ativa:
        problemas.append("Porta de abrir e porta deslizante não podem estar ativas ao mesmo tempo")
    return problemas


# Encontro das chapas -------------------------------------------------------------------------------------------


def _side_thickness(spec):
    """Espessura que cada lateral ocupa, ou 0 quando a chapa não existe."""
    espessura = spec.espessura_lateral
    return (espessura if spec.lateral_esq_ativa else 0.0, espessura if spec.lateral_dir_ativa else 0.0)


def _base_thickness(spec):
    """Espessura da base inferior e da superior, ou 0 quando a chapa não existe."""
    return (spec.espessura_base_inferior if spec.base_inf_ativa else 0.0,
            spec.espessura_base_superior if spec.base_sup_ativa else 0.0)


def largura_interna(spec):
    """Largura livre entre as laterais que existem, em milímetros."""
    esq, dir_ = _side_thickness(spec)
    return spec.largura - esq - dir_


def altura_interna(spec):
    """Altura livre entre as bases que existem, em milímetros."""
    inf, sup = _base_thickness(spec)
    return spec.altura - inf - sup


def carcass_lengths(spec):
    """Comprimento de corte de cada chapa da caixa pela montagem (RN-04, D-10).

    Chaves `LEFT`, `RIGHT`, `BOTTOM` e `TOP`, em milímetros, mesmo quando a chapa não existe (o comprimento dela só é
    usado se ela for gerada). Na lateral passante delega para `cabinet_editor.structure.carcass_lengths`, que aplica a
    mesma regra já testada na feature 012; na base passante as duas bases cobrem a largura e as laterais ficam entre
    elas, conta que a função antiga não faz (ela mantém o topo entre as laterais).
    """
    esq, dir_ = _side_thickness(spec)
    inf, sup = _base_thickness(spec)
    if spec.tipo_montagem == BASE_PASSANTE:
        comprimento_lateral = spec.altura - inf - sup
        return {'LEFT': comprimento_lateral, 'RIGHT': comprimento_lateral,
                'BOTTOM': spec.largura, 'TOP': spec.largura}
    return dict(structure.carcass_lengths(spec.largura, spec.altura, esq, dir_, inf, structure.LATERAL))


def lateral_offset_z(spec):
    """Altura em que a lateral começa: 0 na lateral passante, a base inferior na base passante."""
    if spec.tipo_montagem == BASE_PASSANTE and spec.base_inf_ativa:
        return spec.espessura_base_inferior
    return 0.0


# Contra-frente, peça de trás e fundo -----------------------------------------------------------------------------


def _painel_de_fundo(spec, orientacao):
    """Medidas do painel que fica no plano de trás: em pé segue a altura; deitada, a profundidade (RN-04)."""
    return {'comprimento': largura_interna(spec),
            'altura': spec.altura if orientacao == EM_PE else spec.profundidade}


def contra_frente(spec):
    """Contra-frente: comprimento entre as laterais e altura pela orientação dela (RN-04)."""
    return _painel_de_fundo(spec, spec.orientacao_frente)


def peca_de_tras(spec):
    """Peça de trás: mesma conta da contra-frente, com a orientação própria dela (RN-04)."""
    return _painel_de_fundo(spec, spec.orientacao_tras)


def fundo(spec):
    """Medidas de corte do fundo encaixado (entre as chapas da caixa) ou sobreposto (nas medidas externas, RN-15)."""
    if spec.fundo_fixacao == SOBREPOSTO:
        return {'comprimento': spec.largura, 'largura': spec.altura, 'recuo': spec.fundo_recuo}
    return {'comprimento': largura_interna(spec), 'largura': altura_interna(spec),
            'recuo': spec.fundo_recuo}


def profundidade_util(spec):
    """Profundidade que sobra para os internos, descontado o fundo (RN-15).

    Encaixado em canal o recuo não consome vão nenhum: só a chapa do fundo ocupa profundidade. Sobreposto, o painel
    fica na face de trás e tanto o recuo quanto a chapa saem da profundidade útil.
    """
    if not spec.fundo_ativo:
        return spec.profundidade
    if spec.fundo_fixacao == SOBREPOSTO:
        return spec.profundidade - spec.fundo_recuo - spec.espessura_fundo
    return spec.profundidade - spec.espessura_fundo
