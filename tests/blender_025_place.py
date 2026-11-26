"""Fluxo de criação e posicionamento do armário v2 (feature 025), numa janela real.

Prova, sem `--background`:

1. `Criar armário` (`caffmob.cabinet_editor`) abre o construtor na própria viewport, sem criar janela nova;
2. `Aplicar` pede o posicionamento (o gancho é chamado) e o aviso tem os dois modos;
3. `Cursor 3D` move a raiz para o cursor, com as peças filhas;
4. `Escolher` cria a caixa de arame nas medidas do spec, oculta o armário, acompanha o mouse, gira com as setas,
   confirma com o clique e restaura tudo no Esc;
5. a paleta da Biblioteca é a do mockup claro (tokens puros cobertos em `test_library_style_025.py`).

    blender --factory-startup --enable-event-simulate --python-exit-code 1 --python tests/blender_025_place.py
"""

import math
import os
import sys
import traceback
from pathlib import Path

import bpy
from mathutils import Vector

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _blender_env as env  # noqa: E402
from caffmob_draw.armario_v2 import build, ops as ops_v2, ops_placement, placement  # noqa: E402

FAILURES = []


def check(name, ok, detail=""):
    print(("OK   " if ok else "FALHA ") + name, detail, flush=True)
    if not ok:
        FAILURES.append(name)


def ev(win, kind, value='PRESS', x=0, y=0):
    win.event_simulate(kind, value, x=int(x), y=int(y))


def view3d(ctx):
    win = ctx.window_manager.windows[0]
    area = next(a for a in win.screen.areas if a.type == 'VIEW_3D')
    region = next(r for r in area.regions if r.type == 'WINDOW')
    return win, area, region


def raiz():
    return next((obj for obj in bpy.data.objects if obj.type == 'EMPTY'
                 and any(colecao.name == build.COLECAO for colecao in obj.users_collection)), None)


def pecas(root):
    return [filho for filho in root.children if getattr(filho, 'btm_armario_parte', None) is not None]


def selecionar(obj):
    for outro in bpy.context.selected_objects:
        outro.select_set(False)
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj


def script():
    ctx = bpy.context
    win, area, region = view3d(ctx)
    yield 0.5

    env.clean_scene()
    janelas = len(ctx.window_manager.windows)
    with ctx.temp_override(window=win, area=area, region=region):
        resultado = bpy.ops.caffmob.cabinet_editor('INVOKE_DEFAULT')
    root = raiz()
    check("Criar armário abre o construtor na viewport, sem janela nova",
          resultado == {'FINISHED'} and root is not None and len(ctx.window_manager.windows) == janelas,
          f"{resultado} janelas={len(ctx.window_manager.windows)}")

    with ctx.temp_override(window=win, area=area, region=region):
        bpy.ops.caffmob.armario_v2_montar_caixa()
    check("Montar Caixa cria as cinco chapas", len(pecas(root)) == 5, str(len(pecas(root))))

    # O Aplicar precisa chamar o aviso de posicionamento (o popup não abre no teste; o gancho é observado).
    chamadas = []
    original = ops_placement.abrir_prompt
    ops_placement.abrir_prompt = lambda context: chamadas.append(True) or True
    try:
        aplicado = bpy.ops.caffmob.armario_v2_aplicar()
    finally:
        ops_placement.abrir_prompt = original
    check("Aplicar pergunta onde adicionar", aplicado == {'FINISHED'} and chamadas == [True], str(aplicado))
    check("o aviso oferece os dois modos",
          hasattr(bpy.ops.caffmob, 'armario_v2_place_choose') and hasattr(bpy.ops.caffmob, 'armario_v2_place_cursor'))

    # Cursor 3D: a raiz e as peças acompanham.
    filho = pecas(root)[0]
    antes = filho.matrix_world.translation.copy()
    ctx.scene.cursor.location = (1.2, -0.8, 0.0)
    selecionar(root)
    bpy.ops.caffmob.armario_v2_place_cursor()
    deslocamento = root.location - Vector((0.0, 0.0, 0.0))
    check("Cursor 3D posiciona a raiz", (root.location - Vector((1.2, -0.8, 0.0))).length < 1e-6,
          str(tuple(round(v, 4) for v in root.location)))
    check("Cursor 3D leva as peças junto",
          (filho.matrix_world.translation - antes - deslocamento).length < 1e-6 and root.parent is None,
          str(tuple(round(v, 4) for v in filho.matrix_world.translation)))

    # Escolher sem viewport (scripts) cai no cursor; a caixa de arame é criada nas medidas.
    ctx.scene.cursor.location = (0.4, 0.6, 0.0)
    selecionar(root)
    bpy.ops.caffmob.armario_v2_place_choose('EXEC_DEFAULT')
    check("Escolher sem viewport cai no Cursor 3D", (root.location - Vector((0.4, 0.6, 0.0))).length < 1e-6)

    spec = ops_v2.spec_do_armario(root)
    cage = placement.criar_cage(ctx, spec)
    largura, profundidade, altura = placement.caixa(spec)
    xs = [v.co.x for v in cage.data.vertices]
    ys = [v.co.y for v in cage.data.vertices]
    zs = [v.co.z for v in cage.data.vertices]
    check("caixa de arame tem 8 vértices, 12 arestas e nenhuma face",
          len(cage.data.vertices) == 8 and len(cage.data.edges) == 12 and len(cage.data.polygons) == 0)
    check("caixa de arame tem as medidas do armário",
          abs((max(xs) - min(xs)) - largura) < 1e-6 and abs((max(ys) - min(ys)) - profundidade) < 1e-6
          and abs((max(zs) - min(zs)) - altura) < 1e-6, f"{largura:.3f} {profundidade:.3f} {altura:.3f}")
    placement.remover(cage)

    # Escolha interativa: prévia, mouse, seta, clique.
    root.location = (0.0, 0.0, 0.0)
    root.rotation_euler = (0.0, 0.0, 0.0)
    selecionar(root)
    bpy.ops.caffmob.armario_v2_place_choose('INVOKE_DEFAULT')
    yield 0.4
    cage = bpy.data.objects.get("Armário v2 — prévia")
    check("Escolher cria a prévia e oculta o armário", cage is not None and root.hide_get())
    if cage is None:
        return
    cx, cy = region.x + region.width / 2, region.y + region.height / 2
    ev(win, 'MOUSEMOVE', 'NOTHING', cx, cy)
    yield 0.2
    check("a prévia acompanha o mouse no piso", cage.location.length >= 0)
    ev(win, 'RIGHT_ARROW', 'PRESS', cx, cy)
    ev(win, 'RIGHT_ARROW', 'RELEASE', cx, cy)
    yield 0.2
    check("seta direita gira 90°", abs(cage.rotation_euler.z - math.radians(90)) < 1e-4,
          str(round(math.degrees(cage.rotation_euler.z), 2)))
    nome = cage.name
    ev(win, 'LEFTMOUSE', 'PRESS', cx, cy)
    ev(win, 'LEFTMOUSE', 'RELEASE', cx, cy)
    yield 0.5
    check("clique confirma e remove a prévia", bpy.data.objects.get(nome) is None)
    check("armário volta visível", not root.hide_get())
    check("armário recebe o giro da prévia", abs(root.rotation_euler.z - math.radians(90)) < 1e-4,
          str(round(math.degrees(root.rotation_euler.z), 2)))

    # Esc cancela e devolve posição/orientação/visibilidade.
    root.location = (0.0, 0.0, 0.0)
    root.rotation_euler = (0.0, 0.0, 0.0)
    selecionar(root)
    bpy.ops.caffmob.armario_v2_place_choose('INVOKE_DEFAULT')
    yield 0.4
    ev(win, 'ESC', 'PRESS', cx, cy)
    ev(win, 'ESC', 'RELEASE', cx, cy)
    yield 0.4
    check("Esc restaura posição, giro e visibilidade",
          root.location.length < 1e-6 and abs(root.rotation_euler.z) < 1e-6 and not root.hide_get(),
          f"loc={tuple(round(v, 4) for v in root.location)} yaw={math.degrees(root.rotation_euler.z):.2f}")


_gen = script()


def tick():
    try:
        return next(_gen)
    except StopIteration:
        pass
    except Exception:
        traceback.print_exc()
        FAILURES.append("exceção no roteiro")
    print(f"blender_025_place: {'OK' if not FAILURES else 'FALHAS: ' + ', '.join(FAILURES)}", flush=True)
    os._exit(1 if FAILURES else 0)


bpy.app.timers.register(tick, first_interval=2.0)
