"""Edição do documento do CAFF MOBI pelo painel de propriedades (067 onda 8, T203; D-42, D-43, D-45).

Sem Blender: recebe e devolve o documento `caffmob.ambiente/v2` em mm. Toda gravação passa pelas mesmas funções e pela
mesma validação do editor de parede (`caffmob/v2/paredes_edicao.py`), então o painel não tem regra própria.
"""
from ..caffmob.v2 import paredes_edicao as pe

CAMPOS_DA_ABERTURA = ('largura', 'altura', 'peitoril', 'posicao')
CAMPOS_DA_PAREDE = ('altura', 'espessura')


def parede(d, parede_id):
    return next((p for p in d['paredes'] if p['id'] == parede_id), None)


def trechos_da_parede(d, parede_id):
    """Trechos na ordem da parede, numerados a partir de 1 (o "trecho N" do cabeçalho)."""
    p = parede(d, parede_id)
    return [] if p is None else [dict(id=s['id'], numero=k + 1, comprimento=s['comprimento'])
                                 for k, s in enumerate(p['segmentos'])]


def aberturas_da_parede(d, parede_id):
    p = parede(d, parede_id)
    ids = {s['id'] for s in p['segmentos']} if p else set()
    return [a for a in d['aberturas'] if a['segmento_id'] in ids]


def dono_da_abertura(d, abertura_id):
    """(parede, número do trecho) da abertura, ou None: a abertura aponta para o trecho, não para a parede (D-45)."""
    a = next((a for a in d['aberturas'] if a['id'] == abertura_id), None)
    if a is None:
        return None
    for p in d['paredes']:
        for k, s in enumerate(p['segmentos']):
            if s['id'] == a['segmento_id']:
                return p, k + 1
    return None


def valor_da_parede(d, parede_id, campo):
    """Valor comum dos trechos (altura = pé-direito inicial e final iguais), ou None quando diferem ("Múltiplos")."""
    p = parede(d, parede_id)
    if p is None:
        return None
    if campo == 'altura':
        valores = {v for s in p['segmentos'] for v in (s['pe_direito_inicial'], s['pe_direito_final'])}
    else:
        valores = {s[campo] for s in p['segmentos']}
    return next(iter(valores)) if len(valores) == 1 else None


def editar(d, tipo, entidade_id, campo, valor_mm):
    """Resultado no formato de `paredes_edicao` ({ok, valor, avisos} ou {ok: False, erros})."""
    if tipo == 'abertura' and campo in CAMPOS_DA_ABERTURA:
        return pe.editar_abertura(d, entidade_id, {campo: valor_mm})
    if tipo == 'parede' and campo in CAMPOS_DA_PAREDE:
        p = parede(d, entidade_id)
        if p is None:
            return pe.falha('paredes', 'REFERENCIA_ORFA', 'Parede inexistente.')
        return pe.editar_paredes_em_lote(d, p['pavimento_id'], [s['id'] for s in p['segmentos']], {campo: valor_mm})
    return pe.falha(campo, 'ESQUEMA', 'Campo que o painel não edita.')


def mensagem(resultado):
    """Texto da recusa para o usuário: as mensagens da validação, sem repetir."""
    return ' '.join(dict.fromkeys(e.get('mensagem') or e['codigo'] for e in resultado.get('erros', [])))
