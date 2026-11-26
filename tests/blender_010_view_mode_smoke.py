"""Teste de fumaça do modo de vista (feature 010, T030; RF-08, RN-06).

Precisa de janela (a vista 3D só existe com tela):
    xvfb-run -a blender --factory-startup --enable-event-simulate --python tests/blender_010_view_mode_smoke.py

- Textura com Linhas ligado: `color_type` TEXTURE em todas as vistas 3D e as arestas pretas pelo handler próprio;
- desligar Linhas tira as arestas; voltar a Sólido devolve o `color_type` anterior;
- o estado vai no arquivo (salvar e reler as propriedades em outro Blender) e o `load_post` reaplica;
- a barra lateral desenha o controle sem erro.
"""

import os
import subprocess
import sys
import tempfile
import traceback
from pathlib import Path

import bpy

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _blender_env as env  # noqa: E402,F401
from caffmob_draw.overlays import arestas  # noqa: E402
from caffmob_draw.ui import sidebar_build, view_mode  # noqa: E402
from caffmob_draw.ui import layout_probe  # noqa: E402

FAILURES = []


def check(name, ok, detail=""):
    print(("OK   " if ok else "FALHA ") + name, detail, flush=True)
    if not ok:
        FAILURES.append(name)


def spaces():
    return [s for w in bpy.context.window_manager.windows for a in w.screen.areas if a.type == 'VIEW_3D'
            for s in a.spaces if s.type == 'VIEW_3D']


def main():
    scene = bpy.context.scene
    check("há vista 3D", bool(spaces()))
    for space in spaces():
        space.shading.color_type = 'OBJECT'
    scene.btm_view_mode = 'TEXTURE'
    scene.btm_view_lines = True
    ok = all(s.shading.color_type == 'TEXTURE' and not s.overlay.show_wireframes for s in spaces())
    check("Textura com linha em todas as vistas (arestas próprias, wireframe do Blender desligado)", ok)
    check("handler das arestas pretas registrado", arestas._handler is not None)
    check("espessura da aresta nas preferências", arestas.espessura() >= 0.2, str(arestas.espessura()))
    scene.btm_view_lines = False
    check("desligar Linhas tira as arestas", not scene.btm_view_lines and not any(
        s.overlay.show_wireframes for s in spaces()))
    scene.btm_view_mode = 'SOLID'
    check("Sólido devolve a cor anterior (Objeto)", all(s.shading.color_type == 'OBJECT' for s in spaces()))
    scene.btm_view_mode, scene.btm_view_lines = 'TEXTURE', True
    for space in spaces():                     # como se o arquivo fosse aberto numa vista comum
        space.shading.color_type, space.overlay.show_wireframes = 'MATERIAL', False
    check("load_post registrado", view_mode._on_load in bpy.app.handlers.load_post)
    view_mode._on_load(None)
    check("o load_post reaplica o modo salvo", all(s.shading.color_type == 'TEXTURE' for s in spaces()))
    check("o load_post reaplica o interruptor Linhas", scene.btm_view_lines)
    path = os.path.join(tempfile.mkdtemp(), "vista.blend")
    bpy.ops.wm.save_as_mainfile(filepath=path, copy=True)
    expr = ("import sys; sys.path.insert(0, %r); import _blender_env; import bpy; s = bpy.context.scene; "
            "print('VIEW', s.btm_view_mode, s.btm_view_lines)") % str(Path(__file__).resolve().parent)
    out = subprocess.run([bpy.app.binary_path, "--background", "--factory-startup", path, "--python-expr", expr],
                         capture_output=True, text=True, timeout=300).stdout
    line = next((ln for ln in out.splitlines() if ln.startswith("VIEW ")), "")
    check("o modo vai salvo no arquivo", line == "VIEW TEXTURE True", line)
    probe = layout_probe.Probe()
    sidebar_build.draw_view_mode(probe, bpy.context)
    check("a barra lateral desenha o modo de vista", True)


def tick():
    try:
        main()
    except Exception:
        traceback.print_exc()
        FAILURES.append("exceção no roteiro")
    print(f"blender_010_view_mode_smoke: {'OK' if not FAILURES else 'FALHAS: ' + ', '.join(FAILURES)}", flush=True)
    os._exit(1 if FAILURES else 0)


bpy.app.timers.register(tick, first_interval=1.0)
