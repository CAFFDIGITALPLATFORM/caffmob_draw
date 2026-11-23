"""Contrato de chapas do armário v2 (feature 017, T014; RN-02, D-11, RF-03).

Python puro, em milímetros. O contrato diz qual chapa o fornecedor entrega (`comprimento_max` × `largura_max`), as
espessuras por papel, a montagem e as orientações padrão. Sem contrato (`configurado = False`) o armário não gera:
`pode_gerar` devolve os motivos e o painel os mostra (RN-02).

São **oito** espessuras aqui: as nove do armário menos a `espessura_folha`, que é ferramenta da porta deslizante e não
entra no plano de chapa do fornecedor (`data-delta.md` §4).

`padrao()` é a reserva: chapa 2750 × 1830 mm com as espessuras que o `dimension_schema` brasileiro usa como padrão
(fundo 6 mm, as demais 15 mm). `apply_host_contract(...)` é a função pública de injeção do addon hospedeiro (RF-03):
o que vier sobrescreve, o que não vier mantém a reserva. A leitura de `standards.api.active_definition` precisa da
cena do Blender, então fica no painel (T023), que chama `apply_host_contract` com o que o padrão ativo trouxer.
"""

from dataclasses import dataclass, field

from ..data.i18n import tr

LATERAL_PASSANTE, BASE_PASSANTE = 'LATERAL_PASSANTE', 'BASE_PASSANTE'
EM_PE, DEITADA = 'EM_PE', 'DEITADA'

# Os oito papéis do contrato, na mesma grafia dos campos de `BTM_PG_ContratoChapas`.
PAPEIS = (
    'espessura_lateral',
    'espessura_base_inferior',
    'espessura_base_superior',
    'espessura_divisoria',
    'espessura_prateleira',
    'espessura_fundo',
    'espessura_gaveta',
    'espessura_porta',
)

CHAPA_COMPRIMENTO = 2750.0
CHAPA_LARGURA = 1830.0
ESPESSURAS_PADRAO = {papel: 15.0 for papel in PAPEIS}
ESPESSURAS_PADRAO['espessura_fundo'] = 6.0


@dataclass(frozen=True)
class Contrato:
    """O que o fornecedor entrega e o que o armário deve respeitar. `configurado = False` = sem contrato."""

    comprimento_max: float = 0.0
    largura_max: float = 0.0
    espessuras: dict = field(default_factory=dict)
    montagem_padrao: str = LATERAL_PASSANTE
    orientacao_frente_padrao: str = EM_PE
    orientacao_tras_padrao: str = EM_PE
    configurado: bool = False


def contrato_vazio():
    """Contrato sem nada configurado: o armário não gera até alguém injetar ou semear."""
    return Contrato()


def padrao():
    """Reserva do `dimension_schema` BR: chapa 2750 × 1830 mm, fundo 6 mm e as demais chapas 15 mm."""
    return Contrato(comprimento_max=CHAPA_COMPRIMENTO, largura_max=CHAPA_LARGURA,
                    espessuras=dict(ESPESSURAS_PADRAO), configurado=True)


def apply_host_contract(comprimento_max, largura_max, espessuras=None, montagem=None,
                        orientacao_frente=None, orientacao_tras=None):
    """Contrato novo a partir do que o addon hospedeiro injetou; o que faltar mantém a reserva (RF-03)."""
    base = padrao()
    valores = dict(base.espessuras)
    for papel, valor in (espessuras or {}).items():
        if papel in PAPEIS:
            valores[papel] = float(valor)
    return Contrato(comprimento_max=float(comprimento_max), largura_max=float(largura_max),
                    espessuras=valores,
                    montagem_padrao=montagem or base.montagem_padrao,
                    orientacao_frente_padrao=orientacao_frente or base.orientacao_frente_padrao,
                    orientacao_tras_padrao=orientacao_tras or base.orientacao_tras_padrao,
                    configurado=True)


def pode_gerar(contrato):
    """Motivos que impedem gerar; lista vazia = pode. Contrato ausente vem primeiro (RN-02)."""
    if contrato is None or not contrato.configurado:
        return [tr("Sem contrato de chapas: informe a chapa máxima, as espessuras e a montagem antes de gerar")]
    motivos = []
    if contrato.comprimento_max <= 0.0 or contrato.largura_max <= 0.0:
        motivos.append(tr("Contrato de chapas sem chapa máxima válida"))
    for papel in PAPEIS:
        if papel not in contrato.espessuras:
            motivos.append(tr("Contrato de chapas sem a {}").format(papel))
    return motivos
