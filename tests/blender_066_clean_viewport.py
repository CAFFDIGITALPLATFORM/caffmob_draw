"""Ensaio da tela limpa e das medidas laterais (feature 066, T012; RF-010, RF-013 a RF-021).

Run: blender --background --factory-startup --python-exit-code 1 --python tests/blender_066_clean_viewport.py

- com 23 ocorrências antigas e desatualizadas na lista, nada de colisão se desenha: o pacote de colisão não tem
  handler de desenho, e o único handler de depsgraph dele é o guarda (RF-010, RF-021);
- as medidas laterais dão no máximo duas cotas, trocam de lado ao girar a vista 180°, somem na vista degenerada e com
  a chave desligada; ligadas, as cotas anterior e posterior saem (RF-014, RF-015, RF-019);
- só a área dona desenha; outra área 3D e o render (sobreposições desligadas) não (RF-020).
"""

import sys
import traceback
import types
from pathlib import Path

import bpy
from mathutils import Vector

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _blender_env as env  # noqa: E402
from caffmob_draw import hb_types  # noqa: E402
from caffmob_draw.overlays import selection_cotas, side_cotas  # noqa: E402
from caffmob_draw.product_libraries.frameless import types_frameless as tf  # noqa: E402

ctx = bpy.context
FAILURES = []
PACKAGE = Path(__file__).resolve().parents[1] / "caffmob_draw"


def check(name, ok, detail=""):
    print(("OK   " if ok else "FALHA ") + name, detail, flush=True)
    if not ok:
        FAILURES.append(name)


def cube(name, loc, scale=(1.0, 1.0, 1.0)):
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=loc)
    obj = ctx.object
    obj.name, obj.scale = name, scale
    return obj


def stale_results():
    state = ctx.window_manager.btm_collision
    state.items.clear()
    for i in range(23):
        row = state.items.add()
        row.kind, row.name_a, row.name_b, row.depth = 'ITEM', f"A{i}", f"B{i}", 0.01
    state.checked, state.stale = 23, True


def no_collision_drawing():
    stale_results()
    sources = {p.name: p.read_text() for p in (PACKAGE / "collision").glob("*.py")}
    check("RF-010: overlay.py e stale.py saíram", 'overlay.py' not in sources and 'stale.py' not in sources,
          str(sorted(sources)))
    drawing = [n for n, text in sources.items() if 'draw_handler_add' in text or 'blf.' in text]
    check("RF-021: nenhum handler de desenho no pacote de colisão", not drawing, str(drawing))
    mine = [f.__module__ for f in bpy.app.handlers.depsgraph_update_post
            if f.__module__.startswith('caffmob_draw.collision.')]
    check("RF-024: o único handler de depsgraph da colisão é o guarda", mine == ['caffmob_draw.collision.guard'],
          str(mine))
    from caffmob_draw.ui import save_feedback
    check("D-07: salvar não traz nota de colisão", not hasattr(save_feedback, '_collision_note'))


def _select(obj):
    for other in ctx.view_layer.objects:
        other.select_set(False)
    obj.select_set(True)
    ctx.view_layer.objects.active = obj


def side_dimensions():
    env.clean_scene()
    stale_results()
    body = cube("Corpo", (0.0, 0.0, 0.5))
    cube("Esquerda", (-0.8, 0.0, 0.5), (0.4, 1.0, 1.0))           # face direita em x = −0,6: 100 mm
    cube("Direita", (1.0, 0.0, 0.5), (0.6, 1.0, 1.0))             # face esquerda em x = 0,7: 200 mm
    cube("Aéreo", (0.0, 0.0, 2.5), (3.0, 1.0, 0.5))               # fora da faixa de altura
    env.settle()
    _select(body)
    ctx.scene.btm_settings.show_side_dimensions = True
    front = side_cotas.specs(ctx, Vector((1.0, 0.0, 0.0)))
    texts = [s.text for s in front]
    check("RF-014: no máximo duas cotas, mesmo com 23 ocorrências antigas", len(front) == 2, str(texts))
    lefts = sorted(front, key=lambda s: s.start.x)
    values = [round((s.end - s.start).length, 4) for s in lefts]
    check("RF-016: de superfície a superfície", values == [0.1, 0.2], str(values))
    back = side_cotas.specs(ctx, Vector((-1.0, 0.0, 0.0)))
    check("RF-015: girar a vista 180° troca os lados com os mesmos valores",
          [s.text for s in back] == list(reversed(texts)), f"{texts} → {[s.text for s in back]}")
    check("RF-019: vista degenerada não mostra cota", side_cotas.specs(ctx, Vector((0.02, 0.0, 1.0))) == [])
    bpy.data.objects.remove(bpy.data.objects["Direita"], do_unlink=True)
    env.settle()
    free = side_cotas.specs(ctx, Vector((1.0, 0.0, 0.0)))
    check("RF-019: lado livre não mostra 0 fictício", len(free) == 1 and free[0].start.x < 0, str(free))
    body.location.x = -0.1
    env.settle()
    touch = side_cotas.specs(ctx, Vector((1.0, 0.0, 0.0)))
    check("RF-019: contato mostra 0", len(touch) == 1 and (touch[0].end - touch[0].start).length < 1e-6,
          str([s.text for s in touch]))


def viewport_scope():
    side_cotas.release()
    area = next(a for a in ctx.window.screen.areas if a.type == 'VIEW_3D')
    with ctx.temp_override(area=area):
        ctx.scene.btm_settings.show_side_dimensions = False
        ctx.scene.btm_settings.show_side_dimensions = True
    check("RF-020: ligar pela interface captura a área da ação", side_cotas._owner[0] == area.as_pointer())
    side_cotas.release()
    check("RF-020: a primeira área fica com as cotas", side_cotas.claims(1, {1, 2}))
    check("RF-020: outra área 3D não desenha", not side_cotas.claims(2, {1, 2}))
    check("RF-020: a área dona sumiu, a outra assume", side_cotas.claims(2, {2}))
    calls = []
    real = side_cotas.specs
    side_cotas.specs = lambda *a: calls.append(a) or []
    try:
        space = types.SimpleNamespace(overlay=types.SimpleNamespace(show_overlays=False))
        area = types.SimpleNamespace(as_pointer=lambda: 2)
        fake = types.SimpleNamespace(scene=ctx.scene, area=area, region_data=object(), space_data=space,
                                     window_manager=ctx.window_manager)
        side_cotas.bpy = types.SimpleNamespace(context=fake, types=bpy.types, app=bpy.app)
        side_cotas._draw()
        check("RF-020: sem sobreposições (render da viewport) nada é calculado nem desenhado", not calls)
        ctx.scene.btm_settings.show_side_dimensions = False
        space.overlay.show_overlays = True
        side_cotas._draw()
        check("RF-013: chave desligada não desenha", not calls and side_cotas._owner[0] is None)
    finally:
        side_cotas.bpy = bpy
        side_cotas.specs = real


def selection_without_front_back():
    env.clean_scene()
    wall = hb_types.GeoNodeWall()
    wall.create("Parede")
    wall.set_input('Length', 4.0)
    wall.set_input('Thickness', 0.15)
    cab = tf.BaseCabinet()
    cab.create("Balcao")
    cab.obj.parent = wall.obj
    cab.obj.location = (1.0, 0.0, 0.0)
    env.settle()
    _select(cab.obj)
    ctx.scene.btm_settings.show_side_dimensions = False
    plain = selection_cotas._specs(ctx)
    ctx.scene.btm_settings.show_side_dimensions = True
    reduced = selection_cotas._specs(ctx)
    check("RF-014: medidas laterais suprimem todas as cotas de seleção", len(plain) >= 2 and reduced == [],
          f"{[s.text for s in plain]} → {[s.text for s in reduced]}")
    ctx.scene.btm_settings.show_side_dimensions = False


for step in (no_collision_drawing, side_dimensions, viewport_scope, selection_without_front_back):
    try:
        step()
    except Exception:
        traceback.print_exc()
        FAILURES.append(f"exceção em {step.__name__}")
print(f"blender_066_clean_viewport: {'OK' if not FAILURES else 'FALHAS: ' + ', '.join(FAILURES)}")
sys.exit(1 if FAILURES else 0)
