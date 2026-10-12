"""Aviso de medidas, tecla I da porta e Redimensionar com agregados.

Run: blender --background --factory-startup --python-exit-code 1 --python tests/blender_toast_resize_invert.py

- aviso: porta 80 × 210 na parede de 15 cm, módulo e grupo de peças (SketchUp) com as medidas certas;
- tecla I com a folha real selecionada: a dobradiça troca de lado (giro invertido) e a seleção continua numa peça;
- Redimensionar: porta pela folha; módulo com agregado na frente (esticado e reposicionado na proporção); grupo de
  peças esticado em X; o operador e o atalho registrados.
"""

import sys
import traceback
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _blender_env as env  # noqa: E402
import _openings_env as oe  # noqa: E402
import bpy  # noqa: E402
from caffmob_draw import hb_utils  # noqa: E402
from caffmob_draw.aggregates import convert, group  # noqa: E402
from caffmob_draw.openings import ops as openings_ops  # noqa: E402
from caffmob_draw.openings import sync  # noqa: E402
from caffmob_draw.overlays import element_toast  # noqa: E402
from caffmob_draw.product_libraries.frameless import types_frameless as tf  # noqa: E402
from caffmob_draw.selection import element_size, resize  # noqa: E402

ctx = bpy.context
FAILURES = []


def check(name, ok, detail=""):
    print(("OK   " if ok else "FALHA ") + name, detail, flush=True)
    if not ok:
        FAILURES.append(name)


def close(a, b, tol=1e-3):
    return abs(a - b) < tol


def select(obj):
    for o in ctx.selected_objects:
        o.select_set(False)
    obj.select_set(True)
    ctx.view_layer.objects.active = obj


def box_mesh(name, size, location):
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=location)
    obj = ctx.active_object
    obj.name = name
    obj.dimensions = size
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    return obj


def leaf_body(cage):
    sashes = [o for o in cage.btm_opening_real.assembly.children_recursive
              if o.btm_aggregate.is_aggregate and o.btm_aggregate.kind == 'LEAF']
    return sashes[0], next(o for o in sashes[0].children_recursive if o.type == 'MESH')


try:
    env.clean_scene()

    # Aviso ------------------------------------------------------------------------------------------------------
    door = oe.make_cage('DOOR', left=False)
    sync.sync(ctx, door, force=True)
    env.settle()
    _sash, body = leaf_body(door)
    el = element_size.element(body)
    w, h, d = element_size.size(el)
    check("aviso: clique na folha mede a porta", el.obj == door and close(w, 0.80) and close(h, 2.10)
          and close(d, 0.15), (el.obj.name, w, h, d))
    check("aviso: texto", "Door" in (element_toast.message(body) or ""), element_toast.message(body))

    cabinet = tf.BaseCabinet()
    cabinet.create("Balcao")
    cabinet.obj.location.x = 3.0
    hb_utils.run_calc_fix_until_stable(ctx, cabinet.obj)
    env.settle()
    cab = cabinet.obj
    cw = element_size.size(element_size.element(cab))[0]
    check("aviso: módulo tem largura", cw > 0.1, cw)

    part = box_mesh("Tampo SKP", (1.2, 0.6, 0.04), (8.0, 0.0, 0.9))
    env.settle()
    skp = group.create_group([part], 'PLAIN', "Mesa SKP")
    env.settle()
    gw, gh, gd = element_size.size(element_size.element(part))
    check("aviso: grupo de peças mede as malhas", close(gw, 1.2) and close(gh, 0.04) and close(gd, 0.6), (gw, gh, gd))
    check("aviso: cota não tem aviso", element_size.element(None) is None)

    # Tecla I ----------------------------------------------------------------------------------------------------
    sash, body = leaf_body(door)
    hinge_before = sash.btm_aggregate.hinge
    select(body)
    check("I: atalho registrado no Object Mode",
          any(kmi.idname == 'caffmob.door_invert_hand' and kmi.type == 'I' for _km, kmi in openings_ops._addon_keymaps))
    check("I: poll com a folha selecionada", bpy.ops.caffmob.door_invert_hand.poll())
    bpy.ops.caffmob.door_invert_hand()
    env.settle()
    sash, body = leaf_body(door)
    check("I: dobradiça trocou de lado", sash.btm_aggregate.hinge != hinge_before,
          (hinge_before, sash.btm_aggregate.hinge))
    check("I: continua com uma peça da porta ativa", ctx.view_layer.objects.active is not None
          and openings_ops.door_of(ctx.view_layer.objects.active) == door)
    bpy.ops.caffmob.door_invert_hand()
    env.settle()
    check("I: de novo volta ao lado original", leaf_body(door)[0].btm_aggregate.hinge == hinge_before)
    select(cab)
    check("I: sem porta, o I fica com o Blender", not bpy.ops.caffmob.door_invert_hand.poll())

    # Redimensionar: porta ----------------------------------------------------------------------------------------
    resize.resize(ctx, element_size.element(door), 0.90)
    env.settle()
    w = element_size.size(element_size.element(door))[0]
    _sash, body = leaf_body(door)
    lo, hi = group.world_box([body])
    check("redimensionar: porta 90 pela folha", close(w, 0.90), w)
    check("redimensionar: folha real refeita com 90", close(hi.x - lo.x, 0.90, 0.02), hi.x - lo.x)

    # Redimensionar: módulo com agregado na frente ----------------------------------------------------------------
    handle = box_mesh("Puxador", (0.20, 0.02, 0.03), (3.0 + cw / 2.0, -0.70, 0.5))
    env.settle()
    convert.convert(handle, cab, 'NEG_Y')
    env.settle()
    agg = handle.btm_aggregate
    u0, size0 = agg.u, agg.size[0]
    select(cab)
    check("redimensionar: poll no módulo", bpy.ops.caffmob.resize_width.poll())
    bpy.ops.caffmob.resize_width(width=cw * 2.0)
    env.settle()
    cw2 = element_size.size(element_size.element(cab))[0]
    check("redimensionar: módulo com a largura nova", close(cw2, cw * 2.0), (cw, cw2))
    check("redimensionar: agregado esticado", close(agg.size[0], size0 * 2.0), (size0, agg.size[0]))
    check("redimensionar: agregado reposicionado na proporção", close(agg.u, u0 * 2.0), (u0, agg.u))
    hlo, hhi = group.world_box([handle])
    check("redimensionar: malha do agregado com a largura nova", close(hhi.x - hlo.x, size0 * 2.0),
          hhi.x - hlo.x)

    # Redimensionar: grupo de peças (SketchUp) --------------------------------------------------------------------
    select(part)
    check("redimensionar: poll no grupo", bpy.ops.caffmob.resize_width.poll())
    bpy.ops.caffmob.resize_width(width=1.5)
    env.settle()
    gw = element_size.size(element_size.element(part))[0]
    check("redimensionar: grupo esticado em X", close(gw, 1.5) and skp.scale.x > 1.0, (gw, tuple(skp.scale)))
    try:
        resize.resize(ctx, element_size.element(part), 0.0)
        check("redimensionar: largura 0 recusada", False)
    except ValueError:
        check("redimensionar: largura 0 recusada", True)
except Exception:
    traceback.print_exc()
    FAILURES.append("exceção")

print("RESULTADO:", "FALHOU " + ", ".join(FAILURES) if FAILURES else "TUDO OK", flush=True)
sys.exit(1 if FAILURES else 0)
