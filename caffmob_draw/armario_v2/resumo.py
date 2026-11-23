"""Resumo do armário v2: linha de estado e lista de peças (feature 017, T019; RN-16, RN-19).

Python puro, em milímetros. A linha de estado é texto, não só cor: dimensões, montagem por extenso, vão e peça
escolhidos e a conformidade com a chapa (RF-18). A lista de peças entrega nome, comprimento, largura, espessura e a
marca de fora-da-chapa de cada peça, pronta para o painel, o inspetor e o adaptador de corte usarem sem recalcular
(RF-19). Peça de ferragem (papel vazio) fica fora da lista.
"""

from . import conferencia as conferencia_mod

MONTAGENS = {'LATERAL_PASSANTE': "Lateral passante", 'BASE_PASSANTE': "Base passante"}


def linha_estado(spec, vao='', peca='', violacoes=()):
    """Linha única de estado do armário, com a conformidade de chapa escrita por extenso."""
    partes = [
        f"{spec.largura:g} × {spec.altura:g} × {spec.profundidade:g} mm",
        MONTAGENS.get(spec.tipo_montagem, spec.tipo_montagem),
        f"vão {vao}" if vao else "sem vão",
        f"peça {peca}" if peca else "sem peça",
    ]
    if violacoes:
        partes.append("chapa: fora da chapa — " + "; ".join(v.texto() for v in violacoes))
    else:
        partes.append("chapa conforme")
    return ' · '.join(partes)


def lista_de_pecas(pecas, contrato):
    """Itens do painel: só peças de chapa, cada uma com a marca de fora-da-chapa conferida no contrato."""
    itens = []
    for peca in pecas:
        if not str(peca.papel or '').strip():
            continue
        fora = bool(conferencia_mod.conferir([peca], contrato))
        itens.append({'nome': peca.nome, 'comprimento': peca.comprimento, 'largura': peca.largura,
                      'espessura': peca.espessura, 'fora_da_chapa': fora})
    return itens
