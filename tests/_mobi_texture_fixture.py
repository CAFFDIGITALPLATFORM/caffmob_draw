"""Texturas sintéticas obtidas pelo protocolo MOBI, somente em 127.0.0.1 (063 T058)."""
import threading
import time

import fake_texture_server as fake


class TextureServer:
    def __init__(self, *flags):
        self.httpd = fake.make_server(fake.parse_args(['--port', '0', *flags]))
        self.thread = threading.Thread(target=self.httpd.serve_forever, daemon=True)
        self.thread.start()
        self.base = 'http://127.0.0.1:{}'.format(self.httpd.server_port)

    @property
    def store(self):
        return self.httpd.RequestHandlerClass.store

    @staticmethod
    def wait(condition, timeout=20):
        from caffmob_draw.texture_library import auth, downloads
        deadline = time.monotonic() + timeout
        while not condition() and time.monotonic() < deadline:
            downloads._tick()
            auth._poll()
            time.sleep(0.01)
        assert condition(), 'A ponte não respondeu dentro do prazo'

    def connect(self):
        from caffmob_draw.texture_library import auth, catalog, downloads
        # O modo de rede é injetado somente no teste; a ponte real continua usando online_access.
        self.online = downloads.online
        downloads.online = lambda: True
        downloads.set_server(self.base)
        auth.reload()
        catalog.invalidate()
        result = []
        auth.start_login(on_done=lambda ok, msg: result.append((ok, msg)))
        self.wait(lambda: result)
        assert result[0][0], result
        catalog.refresh_manufacturers()
        self.wait(lambda: bool(catalog.manufacturers()))
        catalog.refresh()
        self.wait(lambda: not catalog._cache['busy'])
        while catalog.has_more():
            catalog.refresh(more=True)
            self.wait(lambda: not catalog._cache['busy'])
        return catalog.search()

    def download(self, tid, entry=None):
        from caffmob_draw.texture_library import downloads
        result = []
        downloads.fetch(tid, lambda path, err: result.append((path, err)), entry=entry)
        self.wait(lambda: result)
        assert result[0][0] and result[0][1] is None, result
        return result[0][0]

    def close(self):
        from caffmob_draw.texture_library import auth, downloads
        result = []
        auth.logout(result.append)
        self.wait(lambda: result)
        downloads.shutdown()
        downloads.online = self.online
        downloads.set_server(None)
        self.httpd.shutdown()
        self.httpd.server_close()
        self.thread.join(timeout=5)
        assert all(not line.split(' ', 1)[-1].startswith('/v1/') for line in self.store.log), self.store.log
