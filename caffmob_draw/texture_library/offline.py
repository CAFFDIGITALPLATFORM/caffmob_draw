"""Texturas para usar sem rede (BUG-20261023-AFC5; RF05 a RF08 da auditoria da biblioteca estável/offline).

- Índice: o que a conta responde ao resolver um slug do catálogo local (UUID, hashes, mapas) fica gravado em
  `INDEX_FILE`, no cache das texturas, separado por servidor e conta (`scope`). Sem rede, `catalog.resolve` usa o
  índice, então a textura já baixada resolve numa sessão nova. Nada de token, sessão ou resposta de login vai para o
  índice: só os campos de `FIELDS`.
- Preparar: `start(slugs)` põe na fila os itens de uma categoria (ou todos), sem repetir; `step` (no timer) resolve e
  baixa um por vez, com o relevo quando houver, pela mesma fila e o mesmo cache da aplicação (`downloads.fetch`).
  Falhas contam e o lote segue; `cancel` para o agendamento seguinte sem interromper o download que já está em curso
  (ele pode ser de uma aplicação). Trocar de conta ou de servidor interrompe o lote.
"""

import hashlib
import json
import os

import bpy  # type: ignore

from . import catalog, catalog_core

INDEX_FILE = "indice-offline.json"
FIELDS = ('id', 'fabricante', 'linha', 'nome', 'largura', 'altura', 'formato', 'sha256_trabalho', 'sha256_miniatura',
          'mapas')
TICK = 0.2

_batch = {'queue': [], 'seen': set(), 'done': 0, 'failed': 0, 'total': 0, 'busy': False, 'scope': None}


def scope():
    from . import auth, downloads
    return hashlib.sha256((downloads.server_url() + "\n" + auth.titular_nome()).encode()).hexdigest()[:24]


def _path():
    from . import downloads
    return os.path.join(downloads.cache_dir(), INDEX_FILE)


def _read():
    try:
        with open(_path(), encoding='utf-8') as handle:
            data = json.load(handle)
            return data if isinstance(data, dict) else {}
    except (OSError, ValueError):
        return {}


def remember(slug, raw):
    """Grava a resposta da conta para o slug, só com os campos do catálogo, no escopo da conta e do servidor."""
    data = _read()
    data.setdefault(scope(), {})[slug] = {k: raw[k] for k in FIELDS if k in raw}
    path = _path()
    try:
        with open(path + '.tmp', 'w', encoding='utf-8') as handle:
            json.dump(data, handle, ensure_ascii=False)
        os.replace(path + '.tmp', path)
    except OSError:
        pass


def lookup(slug):
    """Resposta gravada para o slug nesta conta e servidor, ou None."""
    return _read().get(scope(), {}).get(slug)


# Preparar ------------------------------------------------------------------------------------------------------------
def slugs(manufacturer='', collection=''):
    return [e['id'] for e in catalog_core.search(catalog.embedded()['catalog'], '', manufacturer, collection)]


def count(manufacturer='', collection=''):
    return len(slugs(manufacturer, collection))


def status():
    return {'done': _batch['done'], 'failed': _batch['failed'], 'total': _batch['total'],
            'running': bool(_batch['queue'] or _batch['busy'])}


def start(items):
    current = scope()
    if _batch['scope'] != current or not (_batch['queue'] or _batch['busy']):
        _batch.update(queue=[], seen=set(), done=0, failed=0, total=0, scope=current)
    for slug in items:
        if slug not in _batch['seen']:
            _batch['seen'].add(slug)
            _batch['queue'].append(slug)
            _batch['total'] += 1
    if not bpy.app.timers.is_registered(_tick):
        bpy.app.timers.register(_tick, first_interval=TICK)


def cancel():
    _batch['queue'].clear()


def _finish(ok):
    _batch['busy'] = False
    _batch['done' if ok else 'failed'] += 1


def step():
    """Resolve e baixa o próximo item; um por vez."""
    from . import bump, downloads
    if _batch['busy'] or not _batch['queue']:
        return
    if _batch['scope'] != scope():                  # outra conta ou servidor: o lote para
        cancel()
        return
    slug = _batch['queue'].pop(0)
    _batch['busy'] = True

    def resolved(remote, error):
        if error or remote is None:
            _finish(False)
            return
        pending = [remote['id']] + ([bump.bump_id(remote['id'])] if remote.get('bump') else [])
        results = []

        def fetched(path, error=None, key=None):
            results.append(error is None and bool(path))
            if len(results) == len(pending):
                _finish(all(results))
        downloads.fetch(remote['id'], fetched, entry=remote)
        if remote.get('bump'):
            downloads.fetch(pending[1], fetched, entry=bump.bump_entry(remote))
    catalog.resolve(slug, resolved)


def _tick():
    step()
    return TICK if (_batch['queue'] or _batch['busy']) else None


def shutdown():
    cancel()
    if bpy.app.timers.is_registered(_tick):
        bpy.app.timers.unregister(_tick)
