"""Reprodução e regressão do lote do editor de armário: BUG-20261011-5R7U, BUG-20261011-FHQN, BUG-20261011-HF2J,
BUG-20261011-HR3U, BUG-20261011-HLV6 e BUG-20261011-FYXD (HVYM e TFC7 estão em test_cabinet_appliances.py e
test_cabinet_catalog.py).

Run: blender --background --factory-startup --python-exit-code 1 --python tests/blender_bug_5R7U_cabinet_editor.py
"""

import sys
import traceback
from pathlib import Path

import bpy

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _blender_env  # noqa: E402,F401
from caffmob_draw.cabinet_editor import bays, bridge, ops_actions, ops_editor, props, scene_slides  # noqa: E402

ctx = bpy.context
FAILURES = []


def check(name, ok, detail=""):
    print(("OK   " if ok else "FALHA ") + name, detail, flush=True)
    if not ok:
        FAILURES.append(name)


def module():
    for obj in list(ctx.scene.objects):
        bpy.data.objects.remove(obj, do_unlink=True)
    props.end()
    assert bpy.ops.caffmob.cabinet_builder(width=0.9) == {'FINISHED'}
    root = ctx.object
    return root, ops_editor.start_session(ctx, root)


def count(root):
    _roots, core, _raw, _names = bridge.division_context(ctx, root)
    return bays.count(core)


def bays_with_common_division():
    root, _s = module()
    bridge.add_division(ctx, root, {'space': bays.ROOT, 'orientation': 'HORIZONTAL', 'offset': 0.3})
    try:
        bridge.set_bays(ctx, root, {'count': 2})
        ok, detail = False, f"aceitou ({count(root)} vãos)"
    except ValueError as exc:
        ok, detail = count(root) == 1, str(exc)
    check("5R7U: Número de vãos com s0 cortado por divisória comum é recusado", ok, detail)
    props.end()


def slides_with_bays():
    root, _s = module()
    bridge.set_bays(ctx, root, {'count': 2})
    msgs = bridge.insert_slides(ctx, root, {'item': 'SLIDE_LISA', 'leaves': 2})
    check("FHQN: deslizantes em armário com vãos são recusados", bool(msgs) and scene_slides.frame_of(root) is None,
          str(msgs))
    props.end()


def back_15mm():
    _root, s = module()
    ui = ctx.window_manager.btm_cabinet_editor
    s.space = bays.ROOT
    ui.div_kind, ui.div_mode, ui.catalog_item = 'FIXED', 'VERTICAL', 'DIV_NO_RECESS'
    action, payload = ops_actions._division_payload(ui, s)
    check("HF2J: 'Tras 15mm' aplica 15 mm de recuo atrás", payload.get('use_back') is True
          and abs(payload.get('back', 0) - 0.015) < 1e-9, str({k: payload.get(k) for k in ('use_back', 'back')}))
    props.end()


def other_tab_item():
    _root, _s = module()
    ctx.window_manager.btm_cabinet_editor.catalog_item = 'OVEN'
    reason = ops_actions.insert_reason(ctx, 'SLIDING')
    check("HR3U: item de Internos não serve na aba Deslizantes", reason is not None, repr(reason))
    props.end()


def apply_state_keeps_parts():
    root, _s = module()
    bridge.insert_interior(ctx, root, {'catalog_id': 'SUPPORT', 'space': bays.ROOT})
    bridge.insert_slides(ctx, root, {'item': 'SLIDE_LISA', 'leaves': 2})
    before = {o.as_pointer() for o in root.children_recursive}
    bridge.apply_state(ctx, root, bridge.read_state(root))
    after = {o.as_pointer() for o in root.children_recursive}
    check("HLV6: apply_state sem mudança não recria internos nem deslizantes", scene_slides.frame_of(root) is not None
          and before == after,
          f"{len(before - after)} objeto(s) recriado(s)")
    props.end()


def remove_bay_division():
    root, _s = module()
    bridge.set_bays(ctx, root, {'count': 2})
    msgs = bridge.remove_in_space(ctx, root, {'space': bays.ROOT + ".a"})
    check("FYXD: 'Sem Divisória' não tira uma divisória de vão sem aviso", count(root) == 2 and bool(msgs), str(msgs))
    props.end()


for step in (bays_with_common_division, slides_with_bays, back_15mm, other_tab_item, apply_state_keeps_parts,
             remove_bay_division):
    try:
        step()
    except Exception:
        traceback.print_exc()
        FAILURES.append(f"exceção em {step.__name__}")
props.end()
print(f"blender_bug_5R7U_cabinet_editor: {'OK' if not FAILURES else 'FALHAS: ' + ', '.join(FAILURES)}")
sys.exit(1 if FAILURES else 0)
