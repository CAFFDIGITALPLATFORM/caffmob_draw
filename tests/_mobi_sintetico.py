"""Ambiente sintético do CAFF MOBI para a onda 8 da 067 (T178; D-44), sem bpy.

Equivale ao ambiente que o titular relatou: muro de 30 × 10 m num objeto só (quatro trechos de 150 mm e 2600 mm), um
portão de 3500 × 2500 mm a 1000 mm do início do trecho 2 (o de 10 m), uma janela no trecho 3 e, a pedido, um módulo.
Gerado aqui, nunca lido de produção (RNF Privacidade).
"""
import copy
import itertools
import json
from pathlib import Path

import _bootstrap  # noqa: F401
from caffmob_draw.caffmob.v2 import paredes_edicao as pe
from caffmob_draw.caffmob.v2.validacao import validar_documento

PASTA = Path(__file__).resolve().parent / 'casos_ouro_v2'
PORTAO = '06800000-0000-4000-8000-0000000000a1'
JANELA = '06800000-0000-4000-8000-0000000000a2'
MATERIAL = '06800000-0000-4000-8000-0000000000c1'


def _ids():
    contador = itertools.count(1)
    return lambda: f'06800000-0000-4000-8000-{next(contador):012x}'


def _base():
    caso = json.loads((PASTA / 'parede-retangulo.json').read_text(encoding='utf-8'))
    d = copy.deepcopy(caso['entrada'])
    d['paredes'], d['aberturas'], d['modulos'], d['vinculos'] = [], [], [], []
    d['materiais'] = [dict(id=MATERIAL, nome='Reboco', tipo='cor', cor='#e8e2d6', classe_visual='gesso')]
    return d


def _modulo(d):
    caso = json.loads((PASTA / 'invalido-ciclo.json').read_text(encoding='utf-8'))
    m = copy.deepcopy(caso['entrada']['modulos'][0])
    m.update(id='06800000-0000-4000-8000-0000000000b1', pavimento_id=d['pavimentos'][0]['id'],
             posicao=dict(x=2000, y=1000, z=0), rotacao_z=0, camada_id=None)
    m['parametros']['plano_pai'] = dict(tipo='FLOOR', id=d['pavimentos'][0]['id'])
    return m


def ambiente(com_modulo=False):
    d = _base()
    piso = d['pavimentos'][0]['id']
    r = pe.criar_modelo_de_parede(d, dict(modelo='retangulo', pavimento_id=piso, origem=dict(x=0, y=0),
                                          largura=30000, profundidade=10000, espessura=150, pe_direito=2600,
                                          sentido='LEFT', gerar_id=_ids()))
    assert r['ok'], r
    d = r['valor']
    trechos = d['paredes'][0]['segmentos']
    for abertura in (dict(id=PORTAO, tipo='DOOR', largura=3500, altura=2500, peitoril=0, posicao=1000,
                          segmento_id=trechos[1]['id']),
                     dict(id=JANELA, tipo='WINDOW', largura=1200, altura=1000, peitoril=1100, posicao=5000,
                          segmento_id=trechos[2]['id'])):
        r = pe.inserir_abertura(d, abertura)
        assert r['ok'], r
        d = r['valor']
    if com_modulo:
        d = dict(d, modulos=[_modulo(d)])
        erros = validar_documento(d)
        assert not erros, erros
    return d
