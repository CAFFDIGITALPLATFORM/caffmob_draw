"""Modelos de gaveta (072 D-24, RN-10, RF-07, RF-08), sem bpy.

Seis modelos de fábrica com a corrediça recomendada pela matriz do guia do titular (`tipos_de_gavetas_e_corredicas.md`
§2) e as espessuras e o puxador de cada uso. Os modelos da pessoa ficam em `gavetas.json` na pasta de usuário da
extensão, com id prefixado por `usuario:`.
"""
import json
import os
from dataclasses import asdict, dataclass

from . import core

PREFIXO_USUARIO = 'usuario:'
ARQUIVO = 'gavetas.json'


@dataclass(frozen=True)
class Modelo:
    id: str
    nome: str
    descricao: str
    gaveta: dict
    quantidade: int = 1


def _g(**k):
    return core.Gaveta(**k).para_dict()


FABRICA = (
    Modelo('talheres', "Gaveta de talheres", "Rasa, abertura frequente: telescópica soft close",
           _g(corredica='telescopica_soft', modelo='talheres'), 1),
    Modelo('panelas', "Gavetão de panelas", "Alta carga: oculta, fundo de 15 mm parafusado",
           _g(corredica='oculta_soft', fundo=15, fundo_tipo='parafusado', modelo='panelas'), 2),
    Modelo('joias', "Gaveta de joias e maquiagem", "Estética limpa: oculta toque, sem puxador",
           _g(corredica='oculta_toque', puxador='sem', modelo='joias'), 1),
    Modelo('interna', "Gaveta interna (closet)", "Atrás da porta: telescópica padrão, frente de 15 mm",
           _g(corredica='telescopica', frente_espessura=15, modelo='interna'), 1),
    Modelo('secreta', "Gaveta secreta", "Sem puxador nem fresta: oculta toque",
           _g(corredica='oculta_toque', puxador='sem', modelo='secreta'), 1),
    Modelo('pasta', "Gaveteiro de pasta suspensa", "Extração total: telescópica padrão reforçada",
           _g(corredica='telescopica', lateral=18, contra_frente=18, modelo='pasta'), 1),
)


def ler_usuario(pasta):
    if not pasta:
        return ()
    try:
        with open(os.path.join(pasta, ARQUIVO), encoding='utf-8') as f:
            dados = json.load(f)
    except (OSError, ValueError):
        return ()
    saida = []
    for d in dados if isinstance(dados, list) else []:
        try:
            m = Modelo(**{k: d[k] for k in Modelo.__dataclass_fields__ if k in d})
        except TypeError:
            continue
        if m.id.startswith(PREFIXO_USUARIO):
            saida.append(m)
    return tuple(saida)


def salvar(pasta, nome, gaveta, quantidade=1):
    """Grava um modelo da pessoa (o id vem do nome); substitui o de mesmo nome."""
    ident = PREFIXO_USUARIO + ''.join(ch if ch.isalnum() else '_' for ch in nome.lower()).strip('_')
    novo = Modelo(ident, nome, "Modelo salvo", gaveta.para_dict(), int(quantidade))
    atuais = [m for m in ler_usuario(pasta) if m.id != ident] + [novo]
    os.makedirs(pasta, exist_ok=True)
    caminho = os.path.join(pasta, ARQUIVO)
    with open(caminho + '.tmp', 'w', encoding='utf-8') as f:
        json.dump([asdict(m) for m in atuais], f, ensure_ascii=False, indent=1)
    os.replace(caminho + '.tmp', caminho)
    return novo


def todos(pasta=None):
    return FABRICA + ler_usuario(pasta)


def por_id(mid, pasta=None):
    return next((m for m in todos(pasta) if m.id == mid), None)
