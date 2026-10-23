# Catálogo MOBI com alternativa embutida da 014 (#30 e #31, versão 1.1.2).
import hashlib
import json
import os
import unicodedata
import uuid
from urllib.parse import urlencode

from ..data.i18n import N_
from . import catalog_core

_cache = {'catalog': catalog_core.empty_catalog(), 'warnings': [], 'by_id': {}, 'items': [],
          'query': None, 'next': None, 'busy': False, 'ticket': None, 'generation': 0, 'revision': 0,
          'manufacturer_ticket': None, 'available': None}

LOCAL_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'textures')
NAMESPACE = uuid.UUID('5b0c7d6e-2f41-4c8a-9e3d-0a62e7f1c062')
LOAD_FAILED = N_('Não foi possível carregar o catálogo do MOBI. Tentaremos novamente.')
_local = {}
_errors = {}


def warn(source, message=LOAD_FAILED):
    if source == 'callback':
        _cache.update(busy=False, query=None, available=False)
    _errors[source] = message
    _cache['warnings'] = list(_errors.values())


def _clear_warning(source):
    _errors.pop(source, None)
    _cache['warnings'] = list(_errors.values())


def embedded():
    if not _local:
        try:
            with open(os.path.join(LOCAL_DIR, 'catalog.json'), encoding='utf-8') as handle:
                data, warnings = catalog_core.parse_catalog(handle.read())
        except OSError:
            data, warnings = catalog_core.empty_catalog(), [catalog_core.INVALID]
        entries = {}
        for entry in catalog_core.iter_items(data):
            entry['mobi_id'] = str(uuid.uuid5(NAMESPACE, unicodedata.normalize('NFC', entry['file'])))
            entries[entry['id']] = entry
        _local.update(catalog=data, by_id=entries, warnings=warnings)
    return _local


def from_mobi(item):
    px = [item['largura'], item['altura']]
    return dict(item, name=item['nome'], ext='jpg' if item['formato'] == 'jpeg' else item['formato'],
                px=px, **{'size-mm': catalog_core.size_mm(px)}, sha256=item['sha256_trabalho'],
                thumb=item['sha256_miniatura'], bump='bump' in item.get('mapas', []), bytes=0,
                url='/api/draw/v1/texturas/{}/imagem?tamanho=trabalho'.format(item['id']))


class PageCache:
    def __init__(self, directory):
        self.directory = directory

    def path(self, key):
        return os.path.join(self.directory, hashlib.sha256(key.encode()).hexdigest() + '.json')

    def read(self, key):
        try:
            with open(self.path(key), encoding='utf-8') as handle:
                data = json.load(handle)
                return data if isinstance(data, dict) else {}
        except (OSError, ValueError):
            return {}

    def write(self, key, body, etag):
        os.makedirs(self.directory, exist_ok=True)
        path = self.path(key)
        with open(path + '.tmp', 'w', encoding='utf-8') as handle:
            json.dump({'body': body, 'etag': etag}, handle, ensure_ascii=False)
        os.replace(path + '.tmp', path)


def invalidate():
    cancel(manufacturers=True)
    _cache['revision'] += 1
    _errors.clear()
    _cache.update(catalog=catalog_core.empty_catalog(), warnings=[], by_id={}, items=[], query=None,
                  next=None, available=None)


def load():
    """Árvore da navegação: sempre o catálogo local, conectado ou não (BUG-20261023-EIAR, RF01). A conta só entra ao
    aplicar ou soltar a textura (`resolve`)."""
    local = embedded()
    return local['catalog'], _cache['warnings'] + local['warnings']


def manufacturers():
    return [(m['id'], m['name']) for m in load()[0]['manufacturers']]


def collections(manufacturer_id):
    for man in load()[0]['manufacturers']:
        if man['id'] == manufacturer_id:
            return [(c['id'], c['name']) for c in man['collections']]
    return []


def item(item_id):
    return _cache['by_id'].get(item_id) or embedded()['by_id'].get(item_id)


def remember(raw):
    entry = from_mobi(raw)
    _cache['by_id'][entry['id']] = entry
    return entry


def search(text='', manufacturer='', collection=''):
    return catalog_core.search(embedded()['catalog'], text, manufacturer, collection)


def thumb_entry(entry):
    return dict(entry, id=entry['id'] + ':miniatura', sha256=entry['sha256_miniatura'],
                url='/api/draw/v1/texturas/{}/imagem?tamanho=miniatura'.format(entry['id']))


def thumb_path(entry):
    if entry.get('file'):
        path = os.path.join(LOCAL_DIR, entry['thumb'])
        return path if os.path.isfile(path) else ''
    from . import downloads
    return downloads.cached(entry['id'] + ':miniatura', thumb_entry(entry))


def default_size(entry):
    return tuple(float(v) for v in entry.get('size-mm', (catalog_core.DEFAULT_SIZE_MM,) * 2))


def _page(path, done):
    from . import auth, downloads
    disk = PageCache(os.path.join(downloads.cache_dir(), 'paginas'))
    key = downloads.server_url() + ':' + auth.titular_nome() + path
    previous = disk.read(key)
    headers = {'If-None-Match': previous['etag']} if previous.get('etag') else {}

    def received(status, body, incoming):
        if status == 304:
            body = previous.get('body', {})
        elif status == 200 and isinstance(body, dict) and isinstance(body.get('itens'), list):
            try:
                disk.write(key, body, next((v for k, v in incoming.items() if k.lower() == 'etag'), ''))
                _clear_warning('cache')
            except OSError:
                warn('cache')
        done(status, body)
    return downloads.request('GET', path, headers=headers, callback=received, response_headers=True)


# Listagem da conta (páginas e fabricantes). A navegação não usa mais (BUG-20261023-EIAR); fica para a mesclagem das
# texturas exclusivas da conta nas categorias do catálogo local, pendente na auditoria da biblioteca.
def refresh(text='', manufacturer='', collection='', more=False, callback=None, force=False):
    query = (text.strip(), manufacturer, collection)
    if query[0] and not 2 <= len(query[0]) <= 80:
        cancel()
        _cache.update(query=query, items=[], next=None)
        return
    if _cache['busy'] and query == _cache['query']:
        return
    if query != _cache['query']:
        cancel()
    elif not force and not more and _cache['query'] is not None:
        return
    cursor = _cache['next'] if more else None
    if more and not cursor:
        return
    _cache.update(query=query, busy=True)
    generation = _cache['generation']
    params = {k: v for k, v in zip(('busca', 'fabricante', 'linha'), query) if v}
    if cursor:
        params['cursor'] = cursor

    def received(status, body):
        if generation != _cache['generation']:
            return
        _cache['busy'] = False
        try:
            if status not in (200, 304) or not isinstance(body, dict) or not isinstance(body.get('itens'), list):
                raise ValueError('Resposta inválida do catálogo')
            entries = [from_mobi(i) for i in body['itens']]
            _cache['by_id'].update((e['id'], e) for e in entries)
            _cache['items'] = (_cache['items'] if more else []) + entries
            _cache['next'] = body.get('proximo')
            _cache['available'] = 'manufacturers' not in _errors
            _clear_warning('items')
            _clear_warning('callback')
        except (KeyError, TypeError, ValueError):
            _cache.update(query=None, available=False)
            warn('items')
        if callback:
            callback(status, body)
    _cache['ticket'] = _page('/api/draw/v1/texturas?' + urlencode(params), received)


def refresh_manufacturers(callback=None):
    revision = _cache['revision']
    def received(status, body):
        if revision != _cache['revision']:
            return
        try:
            if status not in (200, 304) or not isinstance(body, dict) or not isinstance(body.get('itens'), list):
                raise ValueError('Resposta inválida de fabricantes')
            manufacturers = [
                {'id': m['fabricante'], 'name': m['fabricante'], 'total': m['total'],
                 'collections': [{'id': c['linha'], 'name': c['linha'], 'total': c['total'], 'items': []}
                                 for c in m.get('linhas', [])]} for m in body['itens']]
            _cache['catalog']['manufacturers'] = manufacturers
            _clear_warning('manufacturers')
            if 'items' not in _errors:
                _cache['available'] = True
        except (KeyError, TypeError, ValueError):
            status = None
            _cache['available'] = False
            warn('manufacturers')
        if callback:
            callback(status, body)
    _cache['manufacturer_ticket'] = _page('/api/draw/v1/texturas/fabricantes', received)
    return _cache['manufacturer_ticket']


def cancel(manufacturers=False):
    from . import downloads
    downloads.cancel_request(_cache['ticket'])
    if manufacturers:
        downloads.cancel_request(_cache['manufacturer_ticket'])
        _cache['manufacturer_ticket'] = None
    _cache.update(busy=False, ticket=None, generation=_cache['generation'] + 1)


def has_more():
    return False             # a navegação é local, sem páginas da conta (BUG-20261023-EIAR)


def resolve(item_id, callback):
    """Slug da 014 → UUID da 062; só metadados atuais identificam o derivado de trabalho."""
    from . import downloads
    entry = item(item_id)
    if entry is None or not entry.get('mobi_id'):
        callback(entry, None if entry else {'message': catalog_core.INVALID})
        return
    remote = _cache['by_id'].get(entry['mobi_id'])
    if remote:
        callback(remote, None)
        return
    from . import offline
    saved = offline.lookup(item_id)
    if saved is not None and downloads.unavailable_reason():      # sem rede: o índice da conta (BUG-20261023-AFC5)
        callback(remember(saved), None)
        return

    def received(status, body):
        try:
            if status != 200 or body.get('id') != entry['mobi_id']:
                raise ValueError('Textura indisponível no MOBI')
            remote = remember(body)
            offline.remember(item_id, body)
        except (KeyError, TypeError, ValueError, AttributeError):
            if saved is not None:
                callback(remember(saved), None)           # a rede falhou: vale o que já foi resolvido
                return
            callback(None, {'message': LOAD_FAILED})
            return
        callback(remote, None)
    downloads.request('GET', '/api/draw/v1/texturas/' + entry['mobi_id'], callback=received)
