"""Reprodução e regressão do lote de customize: BUG-20261011-UJ5Q, BUG-20261011-XMUG, BUG-20261011-MNX3,
BUG-20261011-GL62 e BUG-20261011-ODY2.

Run: blender --background --factory-startup --python-exit-code 1 --python tests/blender_bug_UJ5Q_customize.py

- trocar para 2 a 4 gavetas no frameless mantém a personalização nos vãos novos, menos o interior (pergunta 41);
- o painel oferece o estilo de gaveta (RF-03, EC-06);
- interior com valor não numérico não quebra (EC-09);
- R na inserção gira o conjunto, não só a raiz (EC-12);
- interior inválido pelo operador devolve CANCELLED (EC-20).
"""

import math
import sys
import traceback
import types
from pathlib import Path

import bpy
from mathutils import Vector

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _blender_env as env  # noqa: E402
from caffmob_draw import hb_utils  # noqa: E402
from caffmob_draw.customize import ops_library, panels, spec  # noqa: E402
from caffmob_draw.customize.adapters import frameless as fa  # noqa: E402
from caffmob_draw.product_libraries.frameless import types_frameless as tf  # noqa: E402

ctx = bpy.context
FAILURES = []


def check(name, ok, detail=""):
    print(("OK   " if ok else "FALHA ") + name, detail, flush=True)
    if not ok:
        FAILURES.append(name)


def cabinet(kind=tf.BaseCabinet, exterior='Doors'):
    env.clean_scene()
    base = kind()
    base.default_exterior = exterior
    base.create("Balcao")
    hb_utils.run_calc_fix_until_stable(ctx, base.obj)
    for obj in ctx.view_layer.objects:
        obj.select_set(False)
    base.obj.select_set(True)
    ctx.view_layer.objects.active = base.obj
    return base.obj


def drawers_keep_custom():
    root = cabinet()
    _path, opening = fa.openings(root)[0]
    opening.btm_custom.front_material = "Laca branca"
    opening.btm_custom.pull_model = fa.pull_items()[0][0]
    opening.btm_custom.interior = spec.interior_to_json(spec.Interior(shelves=2))
    pull = opening.btm_custom.pull_model
    messages = fa.set_front(ctx, root, opening, 'DRAWERS', 3)
    news = [o for _p, o in fa.openings(root)]
    check("UJ5Q: os vãos novos herdam material e puxador", not messages and len(news) == 3 and all(
        o.btm_custom.front_material == "Laca branca" and o.btm_custom.pull_model == pull for o in news),
        f"{messages} {[(o.btm_custom.front_material, o.btm_custom.pull_model) for o in news]}")
    check("UJ5Q: o interior não passa para as gavetas", all(not o.btm_custom.interior for o in news))
    return root


class Layout:
    def __init__(self, record):
        self.record, self.enabled = record, True

    def _child(self, *args, **kwargs):
        return Layout(self.record)

    row = column = box = split = _child

    def operator_menu_enum(self, idname, prop, text="", **kwargs):
        op = types.SimpleNamespace(idname=idname, text=text)
        self.record.append(op)
        return op

    def operator(self, *args, **kwargs):
        return types.SimpleNamespace()

    def label(self, *args, **kwargs):
        pass

    prop = separator = label


def drawer_style_menu():
    root = cabinet()
    fa.set_front(ctx, root, fa.openings(root)[0][1], 'DRAWERS', 3)
    record = []
    panels.draw_customize(Layout(record), ctx)
    kinds = [getattr(op, 'kind', None) for op in record if op.idname == "caffmob.customize_set_style"]
    check("XMUG: o painel oferece o estilo de gaveta", 'DRAWER' in kinds, str(kinds))
    _ = root


def bad_interior():
    try:
        value = spec.interior_from_json('{"shelves": "x"}')
        ok, detail = value is None, repr(value)
    except ValueError as exc:
        ok, detail = False, repr(exc)
    check("MNX3: interior com valor não numérico é ignorado", ok, detail)


def rotate_set():
    methods = {k: v for k, v in vars(ops_library.BTM_OT_ModuleInsert).items() if callable(v)}
    fake = type('Insert', (), methods)()
    root = bpy.data.objects.new("Raiz", None)
    other = bpy.data.objects.new("Solto", None)
    for obj in (root, other):
        ctx.scene.collection.objects.link(obj)
    root.location = (1.0, 0.0, 0.0)
    other.location = (2.0, 0.0, 0.0)
    fake.root, fake.others, fake.hit_location = root, {other: Vector((1.0, 0.0, 0.0))}, None
    fake.update_snap = lambda context, event: None
    fake._hide = lambda hide: None
    context = types.SimpleNamespace(area=types.SimpleNamespace(tag_redraw=lambda: None))
    fake.modal(context, types.SimpleNamespace(type='R', value='PRESS'))
    where = tuple(round(v, 6) for v in other.location)
    check("GL62: R gira também os outros objetos e o offset", abs(other.rotation_euler.z - math.radians(90)) < 1e-6
          and where == (1.0, 1.0, 0.0), f"rot={math.degrees(other.rotation_euler.z):.0f}° pos={where}")


def interior_cancelled():
    root = cabinet(kind=tf.TallCabinet)
    path, _opening = fa.openings(root)[0]
    with ctx.temp_override(active_object=root, object=root):
        result = bpy.ops.caffmob.customize_set_interior('EXEC_DEFAULT', path=path, shelves=1, heights="5 m")
    check("ODY2: interior inválido devolve CANCELLED", result == {'CANCELLED'}, str(result))


for step in (drawers_keep_custom, drawer_style_menu, bad_interior, rotate_set, interior_cancelled):
    try:
        step()
    except Exception:
        traceback.print_exc()
        FAILURES.append(f"exceção em {step.__name__}")
print(f"blender_bug_UJ5Q_customize: {'OK' if not FAILURES else 'FALHAS: ' + ', '.join(FAILURES)}")
sys.exit(1 if FAILURES else 0)
