"""Reprodução e regressão de BUG-20261023-EIAR (#153): conectar a conta não troca o catálogo de texturas nem zera o
fabricante e a coleção escolhidos; a navegação usa o catálogo local e a conta só entra ao aplicar (RF01 e RF02 da
auditoria da biblioteca estável/offline).

Run: blender --background --factory-startup --python-exit-code 1 --python tests/blender_bug_EIAR_catalogo_estavel.py
"""

import sys
import traceback
from pathlib import Path
from unittest.mock import patch

import bpy

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _blender_env  # noqa: E402,F401
from caffmob_draw.library_panel import draw  # noqa: E402
from caffmob_draw.texture_library import auth, catalog, downloads  # noqa: E402

FAILURES = []
REMOTE = {'itens': [{'fabricante': 'Fabricante da conta', 'total': 1, 'linhas': [{'linha': 'Linha X', 'total': 1}]}]}


def check(name, ok, detail=""):
    print(("OK   " if ok else "FALHA ") + name, detail, flush=True)
    if not ok:
        FAILURES.append(name)


try:
    catalog.invalidate()
    state = bpy.context.window_manager.btm_library
    state.mode, state.tab, state.search = 'MAX', 'TEXTURES', ''
    local_ids = [m[0] for m in catalog.manufacturers()]
    state.manufacturer, state.collection = 'arauco', 'colecao-realce'
    local_items = [e['id'] for e in draw.texture_items(state)]
    check("desconectado: catálogo local com o filtro", len(local_items) == 14, len(local_items))

    draw._remote_tick()                                # painel aberto, ainda desconectado
    calls = []

    def request(method, path, body=None, callback=None, **kwargs):
        calls.append(path)
        if callback is not None:
            if kwargs.get('response_headers'):
                callback(200, REMOTE if 'fabricantes' in path else {'itens': [], 'proximo': None}, {})
            else:
                callback(200, REMOTE if 'fabricantes' in path else {'itens': [], 'proximo': None})
        return {'rid': None, 'cancelled': False}
    with patch.object(auth, 'signed_in', return_value=True), \
            patch.object(downloads, 'unavailable_reason', return_value=''), \
            patch.object(downloads, 'request', side_effect=request), \
            patch.object(draw.time, 'monotonic', side_effect=[100.0 + k for k in range(200)]):
        draw._remote_tick()                            # conectou
        for _ in range(4):
            draw._remote_tick()
        after_ids = [m[0] for m in catalog.manufacturers()]
        after_items = [e['id'] for e in draw.texture_items(state)]
        check("reprodução: conectar não troca os fabricantes", after_ids == local_ids, after_ids[:3])
        check("reprodução: conectar não zera o fabricante e a coleção",
              (state.manufacturer, state.collection) == ('arauco', 'colecao-realce'),
              (state.manufacturer, state.collection))
        check("reprodução: as texturas do filtro continuam as mesmas", after_items == local_items, len(after_items))
        check("navegar não chama a rede", not calls, calls[:3])
        term = after_items and draw.texture_items(state)[0]['name'].split()[0]
        state.search = term
        found = [e['id'] for e in draw.texture_items(state)]
        state.manufacturer = state.collection = ''
        everywhere = [e['id'] for e in draw.texture_items(state)]
        check("busca dentro do fabricante e da coleção escolhidos", found and set(found) <= set(local_items)
              and len(everywhere) >= len(found), (term, len(found), len(everywhere)))
    state.search = state.manufacturer = state.collection = ''
except Exception:
    traceback.print_exc()
    FAILURES.append("exceção")

print("RESULTADO:", "FALHAS " + ", ".join(FAILURES) if FAILURES else "OK", flush=True)
sys.exit(1 if FAILURES else 0)
