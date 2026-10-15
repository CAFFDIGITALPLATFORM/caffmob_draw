"""Sessão e texturas da 014 pelo servidor falso MOBI (063 T058), sem janela.

Roda com --background; bombeia os timers da ponte explicitamente. Só 127.0.0.1.
"""
import json
import stat
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _blender_env
from _mobi_texture_fixture import TextureServer
from caffmob_draw.texture_library import auth, catalog, downloads

server = TextureServer('--expire-access', '2', '--rate-limit-once')
try:
    entries = server.connect()
    assert len(entries) == 3 and auth.titular_nome() == 'Oficina de teste'
    session = Path(auth.session_path())
    assert stat.S_IMODE(session.stat().st_mode) == 0o600
    saved = json.loads(session.read_text())
    assert saved['tokens']['access_token'] and saved['refresh_token'] and saved['titular']['nome']
    assert 'password' not in json.dumps(saved) and 'account' not in saved
    entry = entries[0]
    result = server.download(entry['id'])
    calls = len(server.store.log)
    assert server.download(entry['id']) == result
    assert len(server.store.log) == calls
    assert not Path(result + '.part').exists()
    auth.reload()
    assert auth.signed_in()
    renewed = []
    auth.with_access(renewed.append)
    server.wait(lambda: renewed)
    assert renewed[0]
    assert any('/api/draw/aparelho/token' in line for line in server.store.log)
    # A página salva usa If-None-Match e a resposta HTTP 304 mantém o catálogo.
    catalog._cache['query'] = None
    catalog.refresh()
    server.wait(lambda: not catalog._cache['busy'])
    assert catalog.search()
    original = downloads.online
    downloads.online = lambda: False
    got = []
    downloads.request('GET', '/api/draw/v1/texturas', callback=lambda status, body:got.append(status))
    assert got == [None]
    downloads.online = original
    assert auth.signed_in()
finally:
    server.close()
assert not auth.signed_in() and not session.exists() and not downloads.process_alive()
assert not server.store.refresh

server = TextureServer('--forbid')
try:
    entries = server.connect()
    entry = dict(entries[0], id='denied', sha256='f' * 64)
    got = []
    downloads.fetch('denied', lambda path, error:got.append(error), entry)
    server.wait(lambda: got)
    assert got[0]['status'] == 403
finally:
    server.close()
print('BLENDER_014_TEXTURES_NET_OK', flush=True)
