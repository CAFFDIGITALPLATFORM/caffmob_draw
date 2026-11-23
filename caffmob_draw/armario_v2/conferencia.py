"""Conferência das peças contra a chapa máxima (feature 017, T015; RN-03, RN-16, RF-04).

Python puro, em milímetros. A comparação é uma só: maior lado da peça com o maior limite da chapa e menor lado com o
menor. É a mesma regra de `cutting/part_extractor.limit_status`, que passa a delegar para cá (D-09) — a dependência
aponta do corte para o núcleo, nunca o contrário, porque `part_extractor` carrega `bpy` e este módulo não.

`decidir` fecha a conta: com `bloquear_chapa` ligado, qualquer violação impede gerar; desligado, gera e devolve os
avisos com a mesma medida que a lista de peças mostra (RN-16).
"""

from dataclasses import dataclass, field

from ..data.i18n import tr
from . import chapas as chapas_mod

TOLERANCIA = 1e-6


@dataclass(frozen=True)
class Peca:
    """Uma chapa do armário a conferir. `papel` vazio = ferragem, que não entra no plano de chapa."""

    papel: str
    nome: str
    comprimento: float
    largura: float
    espessura: float


@dataclass(frozen=True)
class Violacao:
    """Uma peça que passa da chapa: papel, nome e a medida que estourou, com o limite dela."""

    papel: str
    nome: str
    medida: float
    limite: float

    def texto(self):
        return tr("{}: {} mm passa da chapa de {} mm").format(
            self.nome, f"{self.medida:g}", f"{self.limite:g}")


@dataclass(frozen=True)
class Decisao:
    """Resultado da conferência: gera ou não, as violações e os avisos a mostrar."""

    gera: bool
    violacoes: tuple = field(default_factory=tuple)
    avisos: tuple = field(default_factory=tuple)


def conferir(pecas, contrato):
    """Violações das peças contra a chapa máxima do contrato, na ordem das peças."""
    if contrato is None or not contrato.configurado:
        return []
    limites = [valor for valor in (contrato.comprimento_max, contrato.largura_max) if valor > 0.0]
    if not limites:
        return []
    maior_limite = max(limites)
    menor_limite = min(limites)
    violacoes = []
    for peca in pecas:
        if not str(peca.papel or '').strip():
            continue
        comprimento, largura = float(peca.comprimento), float(peca.largura)
        maior_lado, menor_lado = max(comprimento, largura), min(comprimento, largura)
        if maior_lado > maior_limite + TOLERANCIA:
            violacoes.append(Violacao(peca.papel, peca.nome, maior_lado, maior_limite))
        elif menor_lado > menor_limite + TOLERANCIA:
            violacoes.append(Violacao(peca.papel, peca.nome, menor_lado, menor_limite))
    return violacoes


def decidir(pecas, contrato, bloquear_chapa=True):
    """Gera ou recusa: sem contrato não gera; com violação, `bloquear_chapa` decide entre recusar e avisar (RN-03)."""
    motivos = chapas_mod.pode_gerar(contrato)
    if motivos:
        return Decisao(False, (), tuple(motivos))
    violacoes = tuple(conferir(pecas, contrato))
    if violacoes and bloquear_chapa:
        return Decisao(False, violacoes, tuple(v.texto() for v in violacoes))
    return Decisao(True, violacoes, tuple(v.texto() for v in violacoes))
