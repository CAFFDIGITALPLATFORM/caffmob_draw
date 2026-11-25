"""Prova no Blender do acervo por ambiente da Biblioteca (2026-11-25).

Roda com janela, para o painel desenhar:

    blender.exe --factory-startup --enable-event-simulate --python-exit-code 1 --python tests/blender_biblioteca_ambiente.py

Confere que cada categoria fixa mostra o próprio acervo (Cozinha não mostra banheiro, Banheiro não mostra cozinha), que
a busca respeita o ambiente e que Dormitório existe como categoria fixa. No fim, abre o painel MAX na categoria
Banheiro, salva um PNG da janela em `%TEMP%/caffmob_biblioteca_banheiro.png` e encerra.
"""

import os
import sys
import tempfile
from pathlib import Path

import bpy  # type: ignore

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _blender_env  # noqa: E402,F401
from caffmob_draw.library_panel import categories_core, draw  # noqa: E402

FAILURES = []


def check(name, ok, detail=""):
    print(("OK   " if ok else "FALHA ") + name, detail, flush=True)
    if not ok:
        FAILURES.append(name)


def _state():
    return bpy.context.window_manager.btm_library


def entries(category, search=""):
    state = _state()
    state.tab, state.category, state.search, state.scroll = 'BLOCKS', category, search, 0.0
    return [entry["name"] for entry in draw.block_entries(state)]


def run_checks():
    fixed = {category.name: category.line for category in categories_core.FIXED}
    check("Dormitório é categoria fixa", fixed.get("Dormitório") == 'DOR', str(fixed))

    cozinha, banheiro = entries("Cozinha"), entries("Banheiro")
    dormitorio, sala, escritorio = entries("Dormitório"), entries("Sala"), entries("Home office")
    for label, names in (("Cozinha", cozinha), ("Banheiro", banheiro), ("Dormitório", dormitorio),
                         ("Sala", sala), ("Home office", escritorio)):
        print("ACERVO", label, names, flush=True)

    check("Cozinha tem balcão de pia", "Balcão de pia 2 portas" in cozinha)
    check("Cozinha não mostra banheiro", not (set(cozinha) & set(banheiro)))
    check("Banheiro tem gabinete e espelheira próprios",
          {"Gabinete de banheiro", "Espelheira de banheiro"} <= set(banheiro))
    check("Banheiro não mostra cozinha", "Balcão de pia 2 portas" not in banheiro)
    check("Dormitório tem roupeiro e cômoda", {"Roupeiro 2 portas", "Cômoda 4 gavetas"} <= set(dormitorio))
    check("Sala tem buffet e estante", {"Buffet de sala", "Estante de sala"} <= set(sala))
    check("Home office tem armário de arquivo", "Armário de arquivo" in escritorio)
    check("Busca dentro do ambiente", entries("Cozinha", "roupeiro") == [], str(entries("Cozinha", "roupeiro")))

    state = _state()
    state.tab, state.category, state.search = 'BLOCKS', "Banheiro", ""
    state.mode, state.pinned, state.scroll, state.rect = 'MAX', True, 0.0, (0.0, 0.0, 0.0, 0.0)


def capture():
    path = os.path.join(tempfile.gettempdir(), "caffmob_biblioteca_banheiro.png")
    for window in bpy.context.window_manager.windows:
        for area in window.screen.areas:
            if area.type == 'VIEW_3D':
                area.tag_redraw()
    try:
        bpy.ops.screen.screenshot(filepath=path)
        print("PRINT", path, flush=True)
    except Exception as exc:                    # a prova de comportamento não depende da imagem
        print("PRINT FALHOU", exc, flush=True)
    print("RESULTADO", "OK" if not FAILURES else "FALHA", flush=True)
    os._exit(1 if FAILURES else 0)


run_checks()
bpy.app.timers.register(capture, first_interval=2.5)
