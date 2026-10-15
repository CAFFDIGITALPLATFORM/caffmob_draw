# (063 RN-04, RN-05, RN-06; D-05) Persistência pura da sessão única do aparelho.
import json
import os

CLIENT_ID = 'caffmob-draw'
PENDENTE = 'Desconectado neste Blender. Desconecte também em Aparelhos conectados no MOBI'


def payload(tokens, base, saved_at=''):
    return {'schema-version': 1, 'server': base.rstrip('/'), 'saved-at': saved_at,
            'tokens': dict(tokens), 'refresh_token': str(tokens['refresh_token']),
            'titular': dict(tokens.get('titular') or {}),
            'pessoa': dict(tokens.get('pessoa') or {})}


def load(data, base):
    if not isinstance(data, dict) or data.get('schema-version') != 1:
        return None
    if data.get('server') != base.rstrip('/') or not data.get('refresh_token'):
        return None
    return data


def read(path, base):
    try:
        with open(path, encoding='utf-8') as handle:
            return load(json.load(handle), base)
    except (OSError, ValueError):
        return None


def save(path, data):
    os.makedirs(os.path.dirname(path) or '.', exist_ok=True)
    tmp = path + '.tmp'
    fd = os.open(tmp, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    os.chmod(tmp, 0o600)
    with os.fdopen(fd, 'w', encoding='utf-8') as handle:
        json.dump(data, handle, ensure_ascii=False)
    os.replace(tmp, path)


def revogacao(session):
    return {'client_id': CLIENT_ID, 'token': session['refresh_token']}


def disconnect(path, status):
    try:
        os.remove(path)
    except FileNotFoundError:
        pass
    return '' if status == 200 else PENDENTE


def refresh_outcome(status, body):
    if status == 200 and isinstance(body, dict) and all(body.get(k) for k in ('access_token', 'refresh_token')):
        return 'OK', body
    if status == 400 and isinstance(body, dict) and body.get('error') == 'invalid_grant':
        return 'LOGOUT', None
    return 'RETRY', None
