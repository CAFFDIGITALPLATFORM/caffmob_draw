# (063 RF-10; RN-07) Mensagens das respostas do MOBI.
from ..data.i18n import N_, tr

HTTP = N_('HTTP {}: {}')
NETWORK = N_('Sem rede: o MOBI não respondeu. A sessão foi mantida')
CONTRACT = N_('Contrato incompatível. Atualize o CAFFMob Draw')
REASONS = {
    401: N_('Conecte o Blender ao MOBI novamente'),
    409: N_('Há duas versões. Escolha a versão do Blender ou a do MOBI'),
    413: N_('O ambiente passa do limite de 1 MB'),
    429: N_('Limite de chamadas. Aguarde o intervalo informado pelo MOBI'),
    500: N_('O MOBI está indisponível. A sessão foi mantida'),
}
INVALID = N_('O aparelho foi desconectado. Conecte o Blender ao MOBI novamente')
UNKNOWN = N_('O MOBI recusou o pedido')
DETAIL = N_('{} ({})')


def compatible(headers):
    value = next((v for k, v in (headers or {}).items() if k.lower() == 'x-caffmob-contrato'), None)
    return value is None or all(c in {v.strip() for v in value.split(',')} for c in ('ambiente/v1', 'modulo/v1'))


def message(status, body=None, headers=None):
    body = body if isinstance(body, dict) else {}
    if not compatible(headers):
        reason = tr(CONTRACT)
    elif status is None:
        return tr(HTTP).format('—', tr(body.get('message') or NETWORK))
    elif status == 400 and body.get('error') == 'invalid_grant':
        reason = tr(INVALID)
    else:
        reason = tr(REASONS.get(500 if status >= 500 else status, UNKNOWN))
    detail = body.get('erro') or body.get('error')
    if detail:
        reason = tr(DETAIL).format(reason, detail)
    return tr(HTTP).format(status, reason)
