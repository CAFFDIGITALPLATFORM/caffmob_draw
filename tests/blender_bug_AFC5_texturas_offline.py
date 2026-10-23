"""Reprodução e regressão de BUG-20261023-AFC5 (#156): preparar as texturas para usar sem rede, por categoria ou
todas, com índice persistente que resolve o slug sem rede numa sessão nova (RF05 a RF08 da auditoria da biblioteca).

Run: blender --background --factory-startup --python-exit-code 1 --python tests/blender_bug_AFC5_texturas_offline.py
"""

import sys
import tempfile
import traceback
from pathlib import Path
from unittest.mock import patch

import bpy

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _blender_env  # noqa: E402,F401
from caffmob_draw.texture_library import auth, catalog, downloads  # noqa: E402

FAILURES = []
RAW = {'fabricante': 'Arauco', 'linha': 'Colecao Realce', 'nome': 'Anis', 'largura': 1200, 'altura': 1200,
       'formato': 'jpeg', 'sha256_trabalho': 'a' * 64, 'sha256_miniatura': 'b' * 64, 'mapas': ['bump']}


def check(name, ok, detail=""):
    print(("OK   " if ok else "FALHA ") + name, detail, flush=True)
    if not ok:
        FAILURES.append(name)


try:
    from caffmob_draw.texture_library import offline           # noqa: E402
except ImportError as exc:
    offline = None
    check("reprodução: existe a preparação offline", False, repr(exc))

directory = tempfile.TemporaryDirectory()
requests, fetched = [], []


def request(method, path, body=None, callback=None, **kwargs):
    requests.append(path)
    slug_uuid = path.rsplit('/', 1)[-1]
    callback(200, dict(RAW, id=slug_uuid))
    return {'rid': None, 'cancelled': False}


def fetch(item_id, callback=None, entry=None):
    fetched.append(item_id)
    if callback:
        callback('/tmp/fake.jpg', None)


try:
    if offline is not None:
        catalog.invalidate()
        local = catalog.search('', 'arauco', 'colecao-realce')
        with patch.object(auth, 'signed_in', return_value=True), \
                patch.object(auth, 'titular_nome', return_value='leo@caff.digital'), \
                patch.object(downloads, 'cache_dir', return_value=directory.name), \
                patch.object(downloads, 'unavailable_reason', return_value=''), \
                patch.object(downloads, 'request', side_effect=request), \
                patch.object(downloads, 'fetch', side_effect=fetch):
            check("a categoria escolhida tem a contagem certa", offline.count('arauco', 'colecao-realce') == len(local),
                  (offline.count('arauco', 'colecao-realce'), len(local)))
            offline.start(offline.slugs('arauco', 'colecao-realce'))
            offline.start(offline.slugs('arauco', 'colecao-realce'))       # pedir de novo não duplica
            for _ in range(len(local) * 3):
                offline.step()
            status = offline.status()
            check("reprodução: baixa a cor e o relevo de cada textura da categoria, uma vez",
                  len([f for f in fetched if not f.endswith('.bump')]) == len(local)
                  and len([f for f in fetched if f.endswith('.bump')]) == len(local), (len(fetched), status))
            check("progresso: concluídos e falhas", status['done'] == len(local) and status['failed'] == 0
                  and not status['running'], status)

            # Sessão nova, sem rede: o slug resolve pelo índice gravado.
            catalog.invalidate()
            requests.clear()
            got = []
            with patch.object(downloads, 'unavailable_reason', return_value='sem internet'):
                catalog.resolve(local[0]['id'], lambda entry, error: got.append((entry, error)))
            check("reprodução: sem rede, o slug resolve pelo índice", got and got[0][1] is None and not requests
                  and got[0][0]['sha256'] == 'a' * 64, (got, requests))
            with patch.object(auth, 'titular_nome', return_value='outra@conta'), \
                    patch.object(downloads, 'unavailable_reason', return_value='sem internet'), \
                    patch.object(downloads, 'request',
                                 side_effect=lambda *a, callback=None, **k: callback(None, {'error': 'network'})):
                other = []
                catalog.invalidate()
                catalog.resolve(local[0]['id'], lambda entry, error: other.append((entry, error)))
            check("o índice é da conta: outra conta não usa", other and other[0][1] is not None, other)
            text = (Path(directory.name) / offline.INDEX_FILE).read_text(encoding='utf-8')
            check("o índice não guarda token", 'token' not in text.lower() and 'bearer' not in text.lower())

            # Cancelar para o agendamento seguinte; falhas são contadas.
            fetched.clear()
            offline.start(offline.slugs('arauco', ''))
            offline.step()
            offline.cancel()
            for _ in range(10):
                offline.step()
            check("cancelar para os próximos", len(fetched) <= 2 and not offline.status()['running'], len(fetched))
        check("comando no menu da conta", hasattr(bpy.ops.caffmob, 'texture_offline_prepare')
              and bpy.ops.caffmob.texture_offline_prepare.get_rna_type() is not None)
except Exception:
    traceback.print_exc()
    FAILURES.append("exceção")
finally:
    directory.cleanup()

print("RESULTADO:", "FALHAS " + ", ".join(FAILURES) if FAILURES else "OK", flush=True)
sys.exit(1 if FAILURES else 0)
