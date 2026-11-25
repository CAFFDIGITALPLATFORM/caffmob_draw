"""Lista de materiais de todos os objetos do projeto aberto (feature 026).

Núcleo puro (`registro`, `agrupar`, `tabela`) e o coletor da cena (`coletar`). A lista cobre **todo** objeto de malha
da cena aberta, e não só as chapas do plano de corte:

- peça de armário v2: papel ou ferragem gravados em `btm_armario_parte` (a dobradiça entra como `DOBRADICA`);
- peça de módulo de biblioteca: papel de `hb_part_role` e a marca de ferragem `btm_hardware`;
- malha sem marca (parede, importado, geometria livre): papel `OUTRO`, só com o material do primeiro slot.

As medidas vêm da caixa de mundo de cada objeto, em milímetros, ordenadas: a maior é o comprimento, a do meio é a
largura e a menor é a espessura. Linhas iguais (mesmo nome, papel, material e medidas) são somadas numa quantidade,
que é o que uma lista de materiais de compra precisa.
"""

from ..data.i18n import N_

OUTRO = 'OUTRO'
CABECALHO = (N_("OBJETO"), N_("PAPEL"), N_("MATERIAL"), N_("COMP. mm"), N_("LARG. mm"), N_("ESP. mm"), N_("QTD"))


def registro(nome, papel, material, comprimento, largura, espessura, quantidade=1):
    """Uma linha da lista, em milímetros."""
    return {'nome': str(nome or ''), 'papel': str(papel or OUTRO), 'material': str(material or '—'),
            'comprimento': round(float(comprimento), 1), 'largura': round(float(largura), 1),
            'espessura': round(float(espessura), 1), 'quantidade': max(1, int(quantidade))}


def _chave(linha):
    return (linha['nome'], linha['papel'], linha['material'], linha['comprimento'], linha['largura'],
            linha['espessura'])


def agrupar(registros):
    """Soma a quantidade das linhas iguais e ordena por papel e nome (a lista fica estável entre execuções)."""
    somadas = {}
    for linha in registros:
        chave = _chave(linha)
        if chave in somadas:
            somadas[chave]['quantidade'] += linha['quantidade']
        else:
            somadas[chave] = dict(linha)
    return sorted(somadas.values(), key=lambda item: (item['papel'], item['nome'], item['comprimento'],
                                                      item['largura']))


def _texto(valor, largura):
    """Valor alinhado à esquerda e cortado no tamanho da coluna (tabela monoespaçada)."""
    texto = str(valor)
    return texto[:largura].ljust(largura)


def tabela(linhas, titulo=""):
    """Texto monoespaçado da lista, com cabeçalho, total de peças e total de linhas."""
    colunas = (28, 14, 26, 10, 10, 9, 5)
    partes = []
    if titulo:
        partes.append(titulo)
    partes.append("".join(_texto(nome, largura) for nome, largura in zip(CABECALHO, colunas)))
    partes.append("-" * sum(colunas))
    for linha in linhas:
        partes.append(_texto(linha['nome'], colunas[0]) + _texto(linha['papel'], colunas[1])
                      + _texto(linha['material'], colunas[2])
                      + _texto(f"{linha['comprimento']:g}", colunas[3])
                      + _texto(f"{linha['largura']:g}", colunas[4])
                      + _texto(f"{linha['espessura']:g}", colunas[5])
                      + _texto(linha['quantidade'], colunas[6]))
    partes.append("-" * sum(colunas))
    partes.append(f"{len(linhas)} " + N_("linha(s)") + f" · {sum(item['quantidade'] for item in linhas)} "
                  + N_("peça(s)"))
    return "\n".join(partes)


# Coletor da cena -------------------------------------------------------------------------------------------------
def _medidas_mm(obj):
    """(comprimento, largura, espessura) em milímetros da caixa de mundo do objeto, da maior para a menor."""
    from mathutils import Vector  # type: ignore

    cantos = [obj.matrix_world @ Vector(canto) for canto in obj.bound_box]
    medidas = sorted((max(c[i] for c in cantos) - min(c[i] for c in cantos)) * 1000.0 for i in range(3))
    return medidas[2], medidas[1], medidas[0]


def _papel(obj):
    """Papel da peça: o do armário v2 (ou a ferragem dele), o do módulo de biblioteca, ou `OUTRO`."""
    parte = getattr(obj, 'btm_armario_parte', None)
    if parte is not None:
        papel = str(parte.papel or '')
        if not papel:
            ferragem = str(parte.ferragem or '')
            papel = '' if ferragem == 'NENHUMA' else ferragem
        if papel:
            return papel
    for chave in ('hb_part_role', 'btm_component', 'btm_hardware'):
        valor = obj.get(chave)
        if valor:
            return str(valor)
    return OUTRO


def _material(obj):
    """Material da peça: o gravado no armário v2, o do primeiro slot da malha, ou `—`."""
    parte = getattr(obj, 'btm_armario_parte', None)
    if parte is not None and str(parte.material or '').strip():
        return str(parte.material)
    if obj.type == 'MESH' and obj.data.materials:
        primeiro = obj.data.materials[0]
        if primeiro is not None:
            return primeiro.name
    return '—'


def coletar(scene):
    """Linhas da lista de todos os objetos de malha da cena aberta, já agrupadas."""
    registros = []
    for obj in sorted(scene.objects, key=lambda item: item.name):
        if obj.type != 'MESH':
            continue
        comprimento, largura, espessura = _medidas_mm(obj)
        registros.append(registro(obj.name, _papel(obj), _material(obj), comprimento, largura, espessura))
    return agrupar(registros)
