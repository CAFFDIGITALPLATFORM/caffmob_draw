"""Ensaio da tela limpa e das medidas laterais (feature 066, T012; RF-010, RF-013 a RF-021).

Run: blender --background --factory-startup --python-exit-code 1 --python tests/blender_066_clean_viewport.py

- com 23 ocorrências antigas e desatualizadas na lista, nada de colisão se desenha: o pacote de colisão não tem
  handler de desenho, e o único handler de depsgraph dele é o guarda (RF-010, RF-021);
- as medidas laterais dão no máximo duas cotas, trocam de lado ao girar a vista 180° e somem na vista degenerada
  (RF-015, RF-019); desde a 067 (D-07) não há chave: as cotas fixas aparecem sempre para a seleção e as antigas só
  quando pedidas em "Cotas antigas" (RF-027, RF-030);
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
    # BUG-20261023-HYCE: quatro cotas fixas (eixo do móvel), iguais em qualquer vista, com o nome da referência.
    rec = side_cotas.records(ctx)
    values = {k: (round(v, 4), name) for k, (v, name) in rec.items()}
    check("HYCE: quatro cotas, mesmo com 23 ocorrências antigas", set(rec) == {'LEFT', 'RIGHT', 'TOP', 'BOTTOM'},
          str(values))
    check("RF-016: de superfície a superfície, com o nome", values.get('LEFT') == (0.1, "Esquerda")
          and values.get('RIGHT') == (0.2, "Direita") and values.get('TOP') == (1.25, "Aéreo"), str(values))
    texts = [s.text for s in side_cotas.specs(ctx, Vector((1.0, 0.0, 0.0)))]
    for view in (Vector((-1.0, 0.0, 0.0)), Vector((0.02, 0.0, 1.0))):
        check(f"HYCE: a vista {tuple(view)} não muda as cotas", [s.text for s in side_cotas.specs(ctx, view)] == texts)
    bpy.data.objects.remove(bpy.data.objects["Direita"], do_unlink=True)
    env.settle()
    free = side_cotas.records(ctx)
    check("RF-019: lado livre não mostra 0 fictício", 'RIGHT' not in free and 'LEFT' in free, str(free))
    body.location.x = -0.1
    env.settle()
    touch = side_cotas.records(ctx)
    check("RF-019: contato mostra 0", touch.get('LEFT', (None,))[0] is not None and touch['LEFT'][0] < 1e-6,
          str(touch))


def viewport_scope():
    side_cotas.release()
    area = next(a for a in ctx.window.screen.areas if a.type == 'VIEW_3D')
    with ctx.temp_override(area=area):
        side_cotas.bind(ctx)           # 067 D-07: sem chave, a área é capturada ao mover o alvo (o guarda chama bind)
    check("RF-020: a ação na viewport captura a área", side_cotas._owner[0] == area.as_pointer())
    side_cotas.release()
    check("RF-020: a primeira área fica com as cotas", side_cotas.claims(1, {1, 2}))
    check("RF-020: outra área 3D não desenha", not side_cotas.claims(2, {1, 2}))
    check("RF-020: a área dona sumiu, a outra assume", side_cotas.claims(2, {2}))
    calls = []
    real = side_cotas.specs
    side_cotas.specs = lambda *a, **k: calls.append(a) or []
    try:
        space = types.SimpleNamespace(overlay=types.SimpleNamespace(show_overlays=False))
        area = types.SimpleNamespace(as_pointer=lambda: 2)
        fake = types.SimpleNamespace(scene=ctx.scene, view_layer=ctx.view_layer, area=area, region_data=object(),
                                     space_data=space,
                                     window_manager=ctx.window_manager, region=types.SimpleNamespace(as_pointer=lambda: 2))
        side_cotas.bpy = types.SimpleNamespace(context=fake, types=bpy.types, app=bpy.app)
        side_cotas._draw()
        check("RF-020: sem sobreposições (render da viewport) nada é calculado nem desenhado", not calls)
        # 067 D-07, RF-027: a chave "Medidas laterais" não existe mais na interface e não muda nada; com a seleção,
        # as cotas são desenhadas (a regra RF-013 da 066, "chave desligada não desenha", foi superada).
        ctx.scene.btm_settings.show_side_dimensions = False
        space.overlay.show_overlays = True
        side_cotas._draw()
        check("067 RF-027: sem chave, as cotas da seleção são desenhadas", bool(calls))
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
    # 067 D-07, RF-030: as cotas antigas saem por padrão (as fixas são sempre desenhadas) e voltam só quando pedidas
    # em "Cotas antigas", na Completa; supera a RF-014 da 066 (a chave "Medidas laterais" as suprimia).
    state = ctx.window_manager.btm_target
    state.legacy_cotas = False
    reduced = selection_cotas._specs(ctx)
    state.legacy_cotas = True
    plain = selection_cotas._specs(ctx)
    state.legacy_cotas = False
    check("067 RF-030: cotas antigas só quando pedidas", len(plain) >= 2 and reduced == [],
          f"{[s.text for s in plain]} → {[s.text for s in reduced]}")


for step in (no_collision_drawing, side_dimensions, viewport_scope, selection_without_front_back):
    try:
        step()
    except Exception:
        traceback.print_exc()
        FAILURES.append(f"exceção em {step.__name__}")
print(f"blender_066_clean_viewport: {'OK' if not FAILURES else 'FALHAS: ' + ', '.join(FAILURES)}")
sys.exit(1 if FAILURES else 0)
