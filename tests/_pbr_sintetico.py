"""Manifesto PBR sintético para os testes da 073 (nunca lido do pacote): poucas texturas, com a mesma forma do real.

`manifesto()` devolve o dicionário; `gravar(pasta)` grava manifesto e mapas (JPEGs mínimos) e devolve o dicionário.
"""
import hashlib
import json
import os

import _bootstrap  # noqa: F401
from caffmob_draw.texture_library import pbr_core

# slug, categoria, palavras, tom, padrão, metal
TEXTURAS = (
    ('tijolo-aparente-claro', 'parede', ['tijolo', 'tijolos'], 'claro', False, False),
    ('tijolo-aparente', 'parede', ['tijolo', 'tijolos'], 'medio', True, False),
    ('tijolo-aparente-escuro', 'parede', ['tijolo', 'tijolos'], 'escuro', False, False),
    ('granito-preto', 'piso', ['granito'], 'escuro', False, False),
    ('granito-cinza', 'piso', ['granito'], 'cinza', True, False),
    ('granito-bege', 'piso', ['granito'], 'claro', False, False),
    ('laminado-carvalho', 'piso', ['laminado', 'madeira'], 'medio', True, False),
    ('laminado-nogueira', 'piso', ['laminado', 'madeira'], 'escuro', False, False),
    ('travertino', 'piso', ['travertino'], 'claro', True, False),
    ('inox-escovado', 'metal', ['inox', 'aco', 'ino', 'cromado', 'cro'], 'claro', True, True),
    ('cobre', 'metal', ['cobre'], 'medio', True, True),
)
JPEG = bytes.fromhex('ffd8ffe000104a46494600010100000100010000ffd9')   # JPEG mínimo (cabeçalho e fim)


def _mapas(slug, metal):
    nomes = ('cor', 'normal', 'rugosidade', 'miniatura') + (('metalico',) if metal else ())
    return {m: {'arquivo': f'{slug}/{m}.jpg', 'sha256': hashlib.sha256(JPEG).hexdigest()} for m in nomes}


def manifesto():
    return {
        'schema-version': 1, 'namespace': str(pbr_core.NAMESPACE_PBR), 'licenca': 'CC0-1.0',
        'texturas': [dict(slug=s, uuid=pbr_core.uuid_de(s), nome=s.replace('-', ' ').capitalize(), categoria=c,
                          palavras=p, tom=t, padrao=pad, metal=m,
                          origem=dict(fonte='ambientCG', id='Sintetico' + str(i), url='https://ambientcg.com/a/X',
                                      licenca='CC0-1.0', copiado_em='2026-10-27'),
                          tamanho_mm=dict(largura=1200, altura=1200), mapas=_mapas(s, m))
                     for i, (s, c, p, t, pad, m) in enumerate(TEXTURAS)],
    }


def gravar(pasta):
    dados = manifesto()
    for caminho in pbr_core.arquivos(dados):
        destino = os.path.join(pasta, *caminho.split('/'))
        os.makedirs(os.path.dirname(destino), exist_ok=True)
        with open(destino, 'wb') as f:
            f.write(JPEG)
    with open(os.path.join(pasta, pbr_core.MANIFESTO), 'w', encoding='utf-8') as f:
        json.dump(dados, f)
    return dados
