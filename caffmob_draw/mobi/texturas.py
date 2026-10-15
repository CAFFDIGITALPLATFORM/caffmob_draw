# (063 RF-04; D-09) Acabamento do contrato e materiais com escala real da 014.
from ..caffmob.chapas import aplicar_textura, texturas_do_modulo
from ..caffmob.contrato import ler_documento, serializar
from ..texture_library import catalog, downloads


def remember(obj, textura_id, grupo='TODAS'):
    if not obj.get('caffmob_modulo'):
        return False
    modulo = aplicar_textura(ler_documento(obj['caffmob_modulo']), grupo, textura_id)
    obj['caffmob_modulo'] = serializar(modulo)
    return True


class TextureBatch:
    """Prepara os arquivos; o chamador só altera a cena depois do último retorno."""
    def __init__(self, modulos, callback, progress=None):
        self.ids = sorted({t for m in modulos for t in texturas_do_modulo(m)})
        self.callback, self.progress = callback, progress
        self.images, self.pending, self.tickets, self.downloads = {}, len(self.ids), [], []
        self.cancelled = False

    def start(self):
        if not self.ids:
            self.callback({})
            return
        for tid in self.ids:
            def metadata(status, body, tid=tid):
                if self.cancelled:
                    return
                if status != 200:
                    self._finished(tid)
                    return
                entry = catalog.remember(body)
                def image(path, error):
                    if self.cancelled:
                        return
                    if path and not error:
                        self.images[tid] = {'imagem': path}
                    if not error and entry.get('bump'):
                        from ..texture_library.bump import bump_entry
                        bump = bump_entry(entry)
                        self.downloads.append(bump['id'])
                        downloads.fetch(bump['id'], lambda path, error: self._bump(tid, path), entry=bump)
                    else:
                        self._finished(tid)
                self.downloads.append(tid)
                downloads.fetch(tid, image, entry=entry)
            self.tickets.append(downloads.request('GET', '/api/draw/v1/texturas/' + tid, callback=metadata))

    def _bump(self, tid, path):
        if self.cancelled:
            return
        if tid in self.images and path:
            self.images[tid]['bump'] = path
        self._finished(tid)

    def _finished(self, tid):
        if self.cancelled:
            return
        self.pending -= 1
        if self.progress:
            self.progress((len(self.ids) - self.pending) / max(1, len(self.ids)))
        if not self.pending:
            self.callback(self.images)

    def cancel(self):
        self.cancelled = True
        for ticket in self.tickets:
            downloads.cancel_request(ticket)
        for item_id in self.downloads:
            downloads.cancel(item_id)
