"""Texturas PBR do pacote (073, D-02, D-03, D-07; data-delta §1). Python puro, sem bpy.

O manifesto `pbr/manifest.json` é a fonte única: slug, UUID, palavras do casamento, tom, tamanho real, origem,
licença e os mapas de cada textura. O mesmo manifesto alimenta a semeadura do MOBI (RN-11).

- `uuid_de(slug)`: UUID v5 do slug no `NAMESPACE_PBR`; o slug nunca muda, então o UUID também não;
- `ler_manifesto(texto)` e `validar_manifesto(dados, pasta=None)`: as regras do data-delta §1, com a lista de
  problemas (vazia = válido);
- `casar(nome, manifesto)` (T013): o material do Promob pela palavra da categoria e pela cor do nome.
"""
import json
import os
import re
import unicodedata
import uuid

NAMESPACE_PBR = uuid.UUID('7c3e9a41-0d52-4f6b-8a1e-2b9f40c73073')
LICENCA = 'CC0-1.0'
CATEGORIAS = ('parede', 'piso', 'metal')
TONS = ('claro', 'medio', 'cinza', 'escuro')
MAPAS = ('cor', 'normal', 'rugosidade', 'metalico', 'miniatura')
OBRIGATORIOS = ('cor', 'normal', 'rugosidade', 'miniatura')
MANIFESTO = 'manifest.json'
SLUG = re.compile(r'[a-z0-9]+(-[a-z0-9]+)*')


def fold(texto):
    return unicodedata.normalize('NFKD', str(texto)).encode('ascii', 'ignore').decode().casefold()


def uuid_de(slug):
    return str(uuid.uuid5(NAMESPACE_PBR, slug))


def ler_manifesto(texto):
    dados = json.loads(texto)
    if not isinstance(dados, dict):
        raise ValueError('manifesto PBR não é um objeto')
    return dados


def carregar(pasta):
    """Manifesto da pasta `pbr/` do pacote, ou None se não houver."""
    try:
        with open(os.path.join(pasta, MANIFESTO), encoding='utf-8') as handle:
            return ler_manifesto(handle.read())
    except (OSError, ValueError):
        return None


def _tamanho_ok(tamanho):
    return (isinstance(tamanho, dict) and
            all(type(tamanho.get(k)) is int and 1 <= tamanho[k] <= 10000 for k in ('largura', 'altura')))


def validar_manifesto(dados, pasta=None, sha256=None):
    """Problemas do manifesto; com `pasta`, confere também a existência dos arquivos e, com `sha256` (função do
    caminho → hex), o conteúdo."""
    problemas = []
    if dados.get('schema-version') != 1:
        problemas.append('schema-version deve ser 1')
    if dados.get('licenca') != LICENCA:
        problemas.append(f'licença do manifesto deve ser {LICENCA}')
    texturas = dados.get('texturas')
    if not isinstance(texturas, list) or not texturas:
        return problemas + ['manifesto sem texturas']
    slugs, padroes = set(), {}
    for t in texturas:
        slug = t.get('slug', '')
        rotulo = slug or '?'
        if not SLUG.fullmatch(slug or ''):
            problemas.append(f'{rotulo}: slug inválido')
        elif slug in slugs:
            problemas.append(f'{rotulo}: slug repetido')
        slugs.add(slug)
        if slug and t.get('uuid') != uuid_de(slug):
            problemas.append(f'{rotulo}: uuid não é uuid5(NAMESPACE_PBR, slug)')
        if not str(t.get('nome', '')).strip():
            problemas.append(f'{rotulo}: sem nome')
        if t.get('categoria') not in CATEGORIAS:
            problemas.append(f'{rotulo}: categoria fora de {CATEGORIAS}')
        if t.get('tom') not in TONS:
            problemas.append(f'{rotulo}: tom fora de {TONS}')
        palavras = t.get('palavras')
        if not isinstance(palavras, list) or not palavras or any(p != fold(p) or not p for p in palavras):
            problemas.append(f'{rotulo}: palavras devem ser uma lista não vazia, em minúsculas e sem acento')
        elif t.get('padrao'):
            chave = (t.get('categoria'), palavras[0])
            if chave in padroes:
                problemas.append(f'{rotulo}: mais de uma textura padrão para "{palavras[0]}"')
            padroes[chave] = slug
        if not _tamanho_ok(t.get('tamanho_mm')):
            problemas.append(f'{rotulo}: tamanho_mm deve ter largura e altura inteiras de 1 a 10000')
        origem = t.get('origem') or {}
        if origem.get('licenca') != LICENCA or not origem.get('id') or not origem.get('url'):
            problemas.append(f'{rotulo}: origem sem id, url ou licença {LICENCA}')
        mapas = t.get('mapas') or {}
        faltam = [m for m in OBRIGATORIOS if m not in mapas] + (['metalico'] if t.get('metal') and
                                                                'metalico' not in mapas else [])
        if faltam:
            problemas.append(f'{rotulo}: faltam os mapas {", ".join(faltam)}')
        for nome, mapa in mapas.items():
            arquivo = (mapa or {}).get('arquivo', '')
            if nome not in MAPAS or not arquivo or os.path.isabs(arquivo) or '..' in arquivo.split('/'):
                problemas.append(f'{rotulo}: mapa {nome} inválido')
                continue
            if pasta is not None:
                caminho = os.path.join(pasta, *arquivo.split('/'))
                if not os.path.isfile(caminho):
                    problemas.append(f'{rotulo}: falta o arquivo {arquivo}')
                elif sha256 is not None and sha256(caminho) != mapa.get('sha256'):
                    problemas.append(f'{rotulo}: sha256 de {arquivo} não confere')
    return problemas


def arquivos(dados):
    """Caminhos relativos (com `/`) de todos os mapas listados."""
    return {m['arquivo'] for t in dados.get('texturas', []) for m in (t.get('mapas') or {}).values()
            if isinstance(m, dict) and m.get('arquivo')}


# Palavra de cor ou de pedra no nome do Promob → tom da textura (aproximação, D-12).
TOM_DA_PALAVRA = {
    'branco': 'claro', 'branca': 'claro', 'bege': 'claro', 'creme': 'claro', 'marfim': 'claro', 'areia': 'claro',
    'amarelo': 'claro', 'perola': 'claro', 'gelo': 'claro', 'off': 'claro',
    'cinza': 'cinza', 'prata': 'cinza', 'chumbo': 'cinza', 'concreto': 'cinza',
    'preto': 'escuro', 'preta': 'escuro', 'negro': 'escuro', 'absoluto': 'escuro', 'grafite': 'escuro',
    'verde': 'escuro', 'ubatuba': 'escuro', 'marrom': 'escuro', 'cafe': 'escuro', 'tabaco': 'escuro',
    'nogueira': 'escuro', 'imbuia': 'escuro', 'jacaranda': 'escuro', 'ipe': 'escuro', 'wenge': 'escuro',
    'carvalho': 'medio', 'freijo': 'medio', 'cumaru': 'medio', 'vermelho': 'medio', 'ocre': 'medio',
    'dourado': 'medio', 'terracota': 'medio',
}
_VIZINHOS = {'claro': ('claro', 'medio', 'cinza', 'escuro'), 'medio': ('medio', 'cinza', 'claro', 'escuro'),
             'cinza': ('cinza', 'medio', 'escuro', 'claro'), 'escuro': ('escuro', 'cinza', 'medio', 'claro')}


def _partes(texto):
    return [p for p in re.split(r'[^a-z0-9]+', fold(texto)) if p]


def casar(nome, manifesto):
    """(textura, aproximada) para o nome de um material do Promob, ou (None, False).

    A primeira parte do nome que é palavra de alguma textura escolhe o grupo (as texturas com essa palavra). No
    grupo, vence a variação cujo slug tem uma parte do nome que só ela tem (`granito_preto` → granito-preto). Sem
    ela, a palavra de cor do nome escolhe pelo tom, o mais próximo (`granito verde ubatuba` → o granito escuro) e
    a escolha é aproximada; sem cor, vale a `padrao` do grupo.
    """
    texturas = (manifesto or {}).get('texturas') or []
    partes = _partes(nome)
    for parte in partes:
        grupo = [t for t in texturas if parte in (t.get('palavras') or [])]
        if not grupo:
            continue
        if len(grupo) == 1:
            return grupo[0], False
        palavras_do_slug = [set(t['slug'].split('-')) for t in grupo]
        for t, proprias in zip(grupo, palavras_do_slug):
            outras = set().union(*(s for s in palavras_do_slug if s is not proprias))
            if (proprias - outras) & set(partes):
                return t, False
        tom = next((TOM_DA_PALAVRA[p] for p in partes if p in TOM_DA_PALAVRA), None)
        if tom is not None:
            for vizinho in _VIZINHOS[tom]:
                achou = next((t for t in grupo if t.get('tom') == vizinho), None)
                if achou is not None:
                    return achou, True
        return next((t for t in grupo if t.get('padrao')), grupo[0]), False
    return None, False
