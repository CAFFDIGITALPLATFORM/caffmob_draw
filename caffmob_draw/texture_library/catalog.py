# (063 RF-03, RF-04; D-07) Catálogo paginado do MOBI, sem catálogo embutido.
import hashlib
import json
import os
from urllib.parse import urlencode

from . import catalog_core

_cache = {'catalog': catalog_core.empty_catalog(), 'warnings': [], 'by_id': {}, 'items': [],
          'query': None, 'next': None, 'busy': False, 'ticket': None, 'generation': 0, 'revision': 0, 'manufacturer_ticket': None}


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
                return json.load(handle)
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
    _cache.update(catalog=catalog_core.empty_catalog(), warnings=[], by_id={}, items=[], query=None, next=None)


def load():
    return _cache['catalog'], _cache['warnings']


def manufacturers():
    return [(m['id'], m['name']) for m in _cache['catalog']['manufacturers']]


def collections(manufacturer_id):
    for man in _cache['catalog']['manufacturers']:
        if man['id'] == manufacturer_id:
            return [(c['id'], c['name']) for c in man['collections']]
    return []


def item(item_id):
    return _cache['by_id'].get(item_id)


def remember(raw):
    entry = from_mobi(raw)
    _cache['by_id'][entry['id']] = entry
    return entry


def search(text='', manufacturer='', collection=''):
    return list(_cache['items'])


def thumb_entry(entry):
    return dict(entry, id=entry['id'] + ':miniatura', sha256=entry['sha256_miniatura'],
                url='/api/draw/v1/texturas/{}/imagem?tamanho=miniatura'.format(entry['id']))


def thumb_path(entry):
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
        elif status == 200:
            disk.write(key, body, incoming.get('ETag', ''))
        done(status, body)
    return downloads.request('GET', path, headers=headers, callback=received, response_headers=True)


def refresh(text='', manufacturer='', collection='', more=False, callback=None):
    query = (text.strip(), manufacturer, collection)
    if query[0] and not 2 <= len(query[0]) <= 80:
        cancel()
        _cache.update(query=query, items=[], next=None)
        return
    if _cache['busy'] and query == _cache['query']:
        return
    if query != _cache['query']:
        cancel()
    elif not more and _cache['query'] is not None:
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
        if status in (200, 304):
            entries = [remember(i) for i in body.get('itens', [])]
            _cache['items'] = (_cache['items'] if more else []) + entries
            _cache['next'] = body.get('proximo')
        else:
            _cache['query'] = None
        if callback:
            callback(status, body)
    _cache['ticket'] = _page('/api/draw/v1/texturas?' + urlencode(params), received)


def refresh_manufacturers(callback=None):
    revision = _cache['revision']
    def received(status, body):
        if revision != _cache['revision']:
            return
        if status in (200, 304):
            _cache['catalog']['manufacturers'] = [
                {'id': m['fabricante'], 'name': m['fabricante'], 'total': m['total'],
                 'collections': [{'id': c['linha'], 'name': c['linha'], 'total': c['total'], 'items': []}
                                 for c in m.get('linhas', [])]} for m in body.get('itens', [])]
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
    return bool(_cache['next'])
