"""Estado de sessão do painel BIBLIOTECA CAFFMOB (feature 014, T026; data-delta §6, RN-09, D-10).

Run: blender --background --factory-startup --python-exit-code 1 --python tests/blender_014_library_state.py

- os campos novos existem com os padrões do data-delta (MIN, solto, retângulo zerado, aba Texturas);
- `open` é derivado de `mode` e gravar nele faz o que o clique da 012 fazia (True abre a coluna, False minimiza);
- o estado não vai para o arquivo (fica no WindowManager).
"""

import os
import sys
import tempfile
import traceback
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _blender_env  # noqa: E402,F401
import bpy  # noqa: E402

FAILURES = []


def check(name, ok, detail=""):
    print(("OK   " if ok else "FALHA ") + name, detail, flush=True)
    if not ok:
        FAILURES.append(name)


def main():
    state = bpy.context.window_manager.btm_library
    check("padrões", (state.mode, state.pinned, tuple(state.rect), state.scroll, state.tab, state.search)
          == ('MIN', False, (0.0, 0.0, 0.0, 0.0), 0.0, 'TEXTURES', ""),
          str((state.mode, state.pinned, tuple(state.rect), state.tab)))
    check("open derivado: MIN fechado", state.open is False)
    state.open = True
    check("gravar open=True abre a coluna", state.mode == 'OPEN' and state.open is True, state.mode)
    state.mode = 'MAX'
    check("MAX também conta como aberto", state.open is True)
    state.open = False
    check("gravar open=False minimiza", state.mode == 'MIN', state.mode)
    state.mode, state.pinned, state.rect = 'MAX', True, (10.0, 20.0, 800.0, 600.0)
    state.manufacturer, state.collection, state.search, state.scroll = "duratex", "design", "carvalho", 120.0
    path = os.path.join(tempfile.mkdtemp(), "estado.blend")
    bpy.ops.wm.save_as_mainfile(filepath=path)
    bpy.ops.wm.open_mainfile(filepath=path)
    state = bpy.context.window_manager.btm_library
    check("o estado é de sessão: abrir o arquivo não traz o MAX fixo", (state.mode, state.pinned) == ('MIN', False),
          f"{state.mode} {state.pinned}")


try:
    main()
except Exception:
    traceback.print_exc()
    FAILURES.append("exceção no roteiro")
print(f"blender_014_library_state: {'OK' if not FAILURES else 'FALHAS: ' + ', '.join(FAILURES)}")
sys.exit(1 if FAILURES else 0)
