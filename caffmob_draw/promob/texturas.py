"""Acabamentos do Promob no catálogo de texturas do addon (071, 4ª auditoria), sem bpy.

Os materiais de chapa do Promob seguem o código do catálogo dele: marca, coleção abreviada, cor e veio
(`Dur_Cri_titanio_h`, `dur_des_ver_nogueira_caiena`, `arauco_tx_cinza_cristal`, `mas_carvalho_mel_h`). O catálogo do
addon tem as mesmas chapas no mesmo layout de pastas (`duratex/Cristallo/Titanio_Cristallo.jpg`). A textura do arquivo
não vem no `.promob` (fica na biblioteca instalada do Promob): o acabamento é casado com o item do catálogo do addon.

- Com o caminho da biblioteca (`%PastaTextures%/fabrica/duratex/Thera/...`), vale o arquivo igual;
- sem ele, a marca pelo prefixo e as demais partes do código como começo de palavra da coleção e do nome; aceita-se
  uma parte sem par (a linha do catálogo, como `Mad` de Madeiras), desde que uma parte de 3+ letras case no nome.
"""
import re
import unicodedata

MARCAS = {
    'dur': 'duratex', 'duratex': 'duratex', 'ara': 'arauco', 'arauco': 'arauco', 'mas': 'arauco', 'masisa': 'arauco',
    'ber': 'berneck', 'berneck': 'berneck', 'euc': 'eucatex', 'eucatex': 'eucatex', 'gua': 'guararapes',
    'guararapes': 'guararapes', 'sud': 'sudati', 'sudati': 'sudati', 'fib': 'fibraplac', 'fibraplac': 'fibraplac',
    'flo': 'floraplac', 'floraplac': 'floraplac', 'gre': 'greenplac', 'greenplac': 'greenplac', 'lop': 'lopar',
    'lopar': 'lopar', 'formica': 'formica',
}
LINHAS = ('dor', 'coz', 'ban', 'esc', 'sal', 'lav', 'are', 'ofi', 'inf')   # prefixo da linha no modelo (dor_branco)
VEIOS = {'h': 'H', 'hor': 'H', 'horizontal': 'H', 'v': 'V', 'ver': 'V', 'vertical': 'V'}
ACABAMENTOS = ('lis', 'liso')          # acabamento da chapa no código (`ara_lor_lis` = Arauco Lord, liso), não é cor
CORES = {'branco': (0xF4, 0xF4, 0xF2), 'preto': (0x22, 0x22, 0x22), 'cinza': (0x9A, 0x9A, 0x9A),
         'grafite': (0x3D, 0x3F, 0x42), 'bege': (0xD9, 0xC9, 0xA8), 'areia': (0xD8, 0xC8, 0xA8),
         'marrom': (0x5C, 0x3B, 0x26), 'jacaranda': (0x4B, 0x2A, 0x1A), 'imbuia': (0x4A, 0x30, 0x20),
         'tabaco': (0x6A, 0x4A, 0x30), 'nogueira': (0x6B, 0x4B, 0x33), 'carvalho': (0xA0, 0x7A, 0x4F),
         'freijo': (0xB0, 0x8A, 0x5A), 'tijolo': (0xC4, 0x95, 0x72), 'tijolos': (0xC4, 0x95, 0x72),
         'laminado': (0xD8, 0xCF, 0xBF)}


def fold(texto):
    return unicodedata.normalize('NFKD', str(texto)).encode('ascii', 'ignore').decode().casefold()


def _palavras(texto):
    return [p for p in re.split(r'[^a-z0-9]+', fold(texto)) if p]


def ler_codigo(codigo):
    """(marca do catálogo ou None, partes da cor e da coleção, veio 'H' | 'V' | None)."""
    partes = _palavras(re.sub(r'\(\d+\)$', '', codigo or ''))
    if partes and partes[0] in LINHAS:
        partes = partes[1:]
    marca = MARCAS.get(partes[0]) if partes else None
    if marca:
        partes = partes[1:]
    veio = next((VEIOS[p] for p in partes if p in VEIOS), None)
    return marca, [p for p in partes if p not in VEIOS and p not in ACABAMENTOS], veio


def cor_por_nome(codigo):
    """Cor sólida pelo nome (`dor_branco`, `jacaranda`, `granito_preto_ouro preto`), ou None: a primeira palavra de cor
    conhecida, quando o catálogo do addon não tem a chapa."""
    _marca, partes, _veio = ler_codigo(codigo)
    return next((CORES[p] for p in partes if p in CORES), None)


def _por_caminho(itens, caminho):
    alvo = fold(caminho).replace('\\', '/')
    if '/fabrica/' not in '/' + alvo:
        return None
    alvo = alvo.split('fabrica/', 1)[1]
    return next((i for i in itens if fold(i['file']).replace('\\', '/') == alvo), None)


def resolver(codigo, itens, caminho=None):
    """(item do catálogo, veio) ou (None, veio). `itens`: entradas do catálogo (id, name, file, collection)."""
    marca, partes, veio = ler_codigo(codigo)
    if caminho:
        achado = _por_caminho(itens, caminho)
        if achado is not None:
            return achado, veio
    if not marca or not partes:
        return None, veio
    melhor = None
    for item in itens:
        if not item['id'].startswith(marca + '/'):
            continue
        nome = _palavras(item['name'])
        palavras = set(nome) | set(_palavras(item.get('collection', ''))) | set(_palavras(item['file']))
        casadas = [p for p in partes if any(w.startswith(p) for w in palavras)]
        cor = [p for p in casadas if len(p) >= 3 and any(w.startswith(p) for w in nome)]
        if not cor or len(casadas) < len(partes) - (1 if len(partes) > 2 else 0):
            continue
        sobra = sum(1 for w in nome if not any(w.startswith(p) for p in partes))
        chave = (len(casadas), -sobra, -len(item['name']))
        if melhor is None or chave > melhor[0]:
            melhor = (chave, item)
    return (melhor[1] if melhor else None), veio


def itens_do_catalogo(catalogo):
    """Entradas planas do `catalog.json` do addon, com o nome da coleção."""
    out = []
    for marca in catalogo.get('manufacturers', []):
        for colecao in marca.get('collections', []):
            for item in colecao.get('items', []):
                out.append(dict(item, collection=colecao.get('name', '')))
    return out
