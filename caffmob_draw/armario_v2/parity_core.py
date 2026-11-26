"""Núcleo puro da paridade do Construtor (feature 026).

Exportação JSON, cutlist e validação de vista/tema sem `bpy`, para os ensaios rodarem fora do Blender. As peças
vêm de `build.pecas` (dicionários em milímetros), a mesma fonte do preview, do plano de corte e do Gerar.
"""

CAMPOS_SPEC = ('largura', 'altura', 'profundidade', 'tipo_montagem', 'acabamento', 'porta_ativa',
               'porta_folhas', 'deslizante_ativa', 'deslizante_folhas', 'fundo_ativo', 'fundo_fixacao',
               'fundo_recuo')


def spec_para_dict(spec):
    """Campos estáveis do spec do armário, em mm, para o JSON (não depende da versão do PropertyGroup)."""
    if spec is None:
        return {}
    dados = {}
    for campo in CAMPOS_SPEC:
        if hasattr(spec, campo):
            valor = getattr(spec, campo)
            try:
                dados[campo] = round(float(valor), 3) if isinstance(valor, (int, float)) else str(valor)
            except (TypeError, ValueError):
                dados[campo] = str(valor)
    return dados


def peca_para_dict(item):
    """Uma peça da cutlist: nome, papel, caixa em mm, espessura e material."""
    (x0, y0, z0), (x1, y1, z1) = item['box']
    return {
        'nome': str(item.get('nome') or ''),
        'papel': str(item.get('papel') or ''),
        'comprimento_mm': round(max(0.0, x1 - x0), 3),
        'altura_mm': round(max(0.0, z1 - z0), 3),
        'profundidade_mm': round(max(0.0, y1 - y0), 3),
        'espessura_mm': round(float(item.get('espessura') or 0.0), 3),
        'material': str(item.get('material') or ''),
        'ferragem': str(item.get('ferragem') or ''),
    }


def cutlist(itens):
    """Agrupa peças iguais (nome, papel, espessura, comprimento, altura) e conta a quantidade."""
    grupos = {}
    for item in itens or ():
        peca = peca_para_dict(item)
        chave = (peca['nome'], peca['papel'], peca['espessura_mm'], peca['comprimento_mm'], peca['altura_mm'])
        if chave in grupos:
            grupos[chave]['quantidade'] += 1
        else:
            grupos[chave] = dict(peca, quantidade=1)
    return sorted(grupos.values(), key=lambda p: (p['papel'], p['nome'], -p['comprimento_mm']))


def payload(spec, itens):
    """JSON exportável: spec, peças e cutlist agregada, com o schema versionado."""
    pecas = [peca_para_dict(item) for item in itens or ()]
    return {
        'schema': 'caffmob.armario.v1',
        'armario': spec_para_dict(spec),
        'pecas': pecas,
        'cutlist': cutlist(itens),
        'totais': {'pecas': len(pecas), 'grupos_cutlist': len(cutlist(itens))},
    }


def vista_valida(vista):
    """Normaliza a vista do preview para SPLIT/FRONTAL/LATERAL."""
    return vista if vista in ('SPLIT', 'FRONTAL', 'LATERAL') else 'SPLIT'


def tema_valido(tema):
    """Normaliza o tema para LIGHT/DARK."""
    return tema if tema in ('LIGHT', 'DARK') else 'LIGHT'


def alternar_tema(tema):
    """Tema oposto, para o botão da toolbar."""
    return 'DARK' if tema_valido(tema) == 'LIGHT' else 'LIGHT'
