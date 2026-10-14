"""Teste de fumaça da feature 015 (T042): construtor de armário com a arquitetura do Promob.

Precisa de janela (não roda em --background), numa instância própria (encerra com o código do resultado):
    xvfb-run -a blender --factory-startup --enable-event-simulate --python tests/blender_015_construtor_smoke.py

Roteiro:
- galeria "Selecione uma estrutura de caixa": abre com desenho ativo; Esc fecha sem criar nada; Enter cria a estrutura
  selecionada (Inferior c/ Divisória) e abre o editor;
- corte do Inferior c/ Divisória com Sarrafo frontal e traseiro e sem Base superior; Superior com Base superior;
- Armário de dormitório 3000 × 2500 × 550 com 3 vãos: vãos de (interno − 2 divisórias) / 3 e rodapé dentro da altura;
  digitar 900 no vão do meio (os outros dividem o resto); Cabideiro 01 na lista de ferragens; prateleira Invisível
  divide sem peça;
- módulo de antes da 015 (sem estrutura): abrir o editor e Cancelar não muda nada; abrir e OK passa para a estrutura;
- Padrão de Dimensões com sarrafo de 80 reaplicado muda os sarrafos do balcão;
- JSON de produção 2.3.0 válido, com `structure_id`.
"""

import os
import sys
import traceback
from pathlib import Path

import bpy

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _blender_env as env  # noqa: E402
from caffmob_draw.cabinet_editor import gallery, ops_actions, props, scene_divisions  # noqa: E402
from caffmob_draw.cutting import hardware, json_exporter, part_extractor, part_sources  # noqa: E402

FAILURES = []


def check(name, ok, detail=""):
    print(("OK   " if ok else "FALHA ") + name, detail, flush=True)
    if not ok:
        FAILURES.append(name)


def view3d(ctx):
    win = ctx.window_manager.windows[0]
    area = next(a for a in win.screen.areas if a.type == 'VIEW_3D')
    region = next(r for r in area.regions if r.type == 'WINDOW')
    return win, area, region


def key(ctx, kind):
    win, area, region = view3d(ctx)
    x, y = area.x + area.width // 2, area.y + area.height // 2
    win.event_simulate(type='MOUSEMOVE', value='NOTHING', x=x, y=y)
    win.event_simulate(type=kind, value='PRESS', x=x, y=y)
    win.event_simulate(type=kind, value='RELEASE', x=x, y=y)


def build(ctx, structure_id, **kw):
    win, area, region = view3d(ctx)
    with ctx.temp_override(window=win, area=area, region=region):
        bpy.ops.caffmob.cabinet_builder(structure_id=structure_id, **kw)
    return ctx.object


def records(ctx, obj):
    module = next(m for m in part_sources.iter_modules(ctx.scene) if m.obj == obj)
    sheets = {"LAT": 15.0, "BAS": 15.0, "FUN_INF": 6.0, "FUN_SUP": 6.0, "FUN_ALT": 6.0, "PRAT": 15.0, "POR": 18.0,
              "SAR": 15.0, "ROD": 15.0, "TAMP": 15.0, "TRA": 15.0}
    return part_sources.synthetic_records(module, lambda c: sheets.get(c, 15.0))


def open_editor(ctx, obj):
    for other in ctx.selected_objects:
        other.select_set(False)
    obj.select_set(True)
    ctx.view_layer.objects.active = obj
    win, area, region = view3d(ctx)
    with ctx.temp_override(window=win, area=area, region=region, active_object=obj, object=obj):
        return bpy.ops.caffmob.cabinet_editor('INVOKE_DEFAULT')


def run_gallery(ctx):
    before = set(bpy.data.objects.keys())
    win, area, region = view3d(ctx)
    with ctx.temp_override(window=win, area=area, region=region):
        result = bpy.ops.caffmob.structure_gallery('INVOKE_DEFAULT', environment='COZ')
    yield 0.5
    check("galeria abre com o desenho ativo", result == {'RUNNING_MODAL'} and gallery._session['handle'] is not None,
          str(result))
    key(ctx, 'ESC')
    yield 0.6
    check("Esc fecha a galeria sem criar nada",
          gallery._session['handle'] is None and set(bpy.data.objects.keys()) == before)
    with ctx.temp_override(window=win, area=area, region=region):
        bpy.ops.caffmob.structure_gallery('INVOKE_DEFAULT', environment='COZ')
    yield 0.5
    key(ctx, 'RET')
    yield 1.5
    new = [bpy.data.objects[n] for n in set(bpy.data.objects.keys()) - before
           if getattr(bpy.data.objects[n], 'btm_cabinet', None) is not None and bpy.data.objects[n].btm_cabinet.width]
    obj = next((o for o in new if o.btm_cabinet.structure_id), None)
    check("Enter cria a estrutura escolhida", obj is not None and obj.btm_cabinet.structure_id ==
          'coz_inferior_divisoria', str([o.name for o in new]))
    check("Enter abre o editor no módulo novo", props.session() is not None)
    if props.session() is not None:
        props.session().request = 'cancel'
        yield 1.0


def run_kitchen(ctx):
    base = build(ctx, 'coz_inferior_divisoria')
    base.location.x = 2.0
    names = [r.name for r in records(ctx, base)]
    check("Inferior: corte com os dois sarrafos e sem Base superior",
          "Sarrafo frontal" in names and "Sarrafo traseiro" in names and "Base superior" not in names, str(names))
    check("Inferior: altura e profundidade do padrão (D-19)", abs(base.btm_cabinet.width - 0.5) < 1e-6)
    upper = build(ctx, 'coz_superior_divisoria', width=0.8, height=0.7, depth=0.55)
    upper.location.x = 3.0
    names = [r.name for r in records(ctx, upper)]
    check("Superior com as mesmas medidas tem Base superior", "Base superior" in names
          and "Sarrafo frontal" not in names, str(names))
    yield 0.3
    return base


def run_wardrobe(ctx):
    obj = build(ctx, 'dor_armario', width=3.0, height=2.5, depth=0.55)
    obj.location.x = 5.0
    env.settle()
    check("Armário: abre o editor", open_editor(ctx, obj) == {'FINISHED'})
    yield 1.2
    s = props.session()
    root = s.root()
    s.push('edit', ('SET_BAYS', {'count': 3}))
    yield 1.0
    _material, t = scene_divisions.configured(ctx.scene, root)
    roots = scene_divisions.roots(ctx, root)
    inner = roots[min(roots)].size(0)
    widths = sorted(round(b.size(0), 4) for b in s.spaces.values())
    want = (inner - 2 * t) / 3.0
    check("Armário: 3 vãos iguais", len(widths) == 3 and all(abs(w - want) < 1e-3 for w in widths),
          f"{widths} esperado {want:.4f}")
    height = roots[min(roots)].size(2)
    kick = obj.btm_cabinet.height - height - 2 * obj.btm_cabinet.thickness
    check("Armário: rodapé dentro da altura total", kick > 0.05 and abs(obj.dimensions.z - 2.5) < 1e-3,
          f"rodapé {kick:.3f}; altura {obj.dimensions.z:.3f}")
    middle = sorted(s.spaces)[1]
    s.space = middle
    s.push('edit', ('SET_BAY_WIDTH', {'index': 1, 'width': 0.9}))
    yield 1.0
    widths = [round(s.spaces[p].size(0), 4) for p in sorted(s.spaces)]
    check("Armário: 900 digitado no vão do meio", any(abs(w - 0.9) < 1e-3 for w in widths), str(widths))
    ui = ctx.window_manager.btm_cabinet_editor
    ui.tab, ui.interior_group, ui.catalog_item = 'INTERIOR', 'WARDROBE', 'HANGER_01'
    s.space = sorted(s.spaces)[0]
    s.push('edit', ops_actions.insert_payload(ctx, 'INTERIOR'))
    yield 1.0
    s.request = 'ok'
    yield 1.2
    rows = hardware.collect(ctx.scene)
    uid = obj.get('btm_uid')
    codes = {r['code'] for r in rows if r['module_uid'] == uid}
    check("Cabideiro 01 na lista de ferragens", 'TUBO_CABIDEIRO' in codes, str(codes))
    check("Armário: abre de novo", open_editor(ctx, obj) == {'FINISHED'})
    yield 1.2
    s = props.session()
    before = len([o for o in scene_divisions.objects(root) if not o.hide_viewport])
    ui.tab, ui.div_mode, ui.div_kind, ui.catalog_item = 'DIVISIONS', 'HORIZONTAL', 'FIXED', 'SHELF_INVISIBLE'
    s.space = sorted(s.spaces)[-1]
    count = len(s.spaces)
    s.push('edit', ops_actions.insert_payload(ctx, 'DIVISIONS'))
    yield 1.0
    visible = len([o for o in scene_divisions.objects(root) if not o.hide_viewport])
    check("prateleira Invisível divide o vão sem peça visível", len(s.spaces) == count + 1 and visible == before,
          f"vãos {count}→{len(s.spaces)}; visíveis {before}→{visible}")
    s.request = 'cancel'
    yield 1.0


def run_legacy(ctx):
    win, area, region = view3d(ctx)
    with ctx.temp_override(window=win, area=area, region=region):
        bpy.ops.caffmob.cabinet_builder(width=0.8)             # sem estrutura: como antes da 015
    obj = ctx.object
    obj.location.x = 9.0
    env.settle()
    before = sorted((r.name, round(r.length, 1)) for r in records(ctx, obj))
    check("módulo antigo: sem estrutura", not obj.btm_cabinet.structure_id and obj.btm_cabinet.has_top)
    check("módulo antigo: abre o editor", open_editor(ctx, obj) == {'FINISHED'})
    yield 1.2
    check("módulo antigo: o editor converte ao abrir", obj.btm_cabinet.structure_id == 'coz_inferior_divisoria')
    props.session().request = 'cancel'
    yield 1.2
    after = sorted((r.name, round(r.length, 1)) for r in records(ctx, obj))
    check("módulo antigo: Cancelar devolve a construção antiga",
          not obj.btm_cabinet.structure_id and obj.btm_cabinet.has_top and after == before, str(after[:4]))
    check("módulo antigo: abre de novo", open_editor(ctx, obj) == {'FINISHED'})
    yield 1.2
    props.session().request = 'ok'
    yield 1.2
    names = [r.name for r in records(ctx, obj)]
    check("módulo antigo: OK passa para a estrutura", obj.btm_cabinet.structure_id == 'coz_inferior_divisoria'
          and "Sarrafo frontal" in names and "Base superior" not in names, str(names))


def run_standard(ctx, base):
    from caffmob_draw.data import dimension_schema as schema
    from caffmob_draw.standards import api, sync
    definition = api.active_definition(ctx.scene)
    if definition is not None and definition.builtin:
        api.duplicate_definition(ctx.scene, definition)       # a cópia é do usuário e fica ativa (RN-STANDARDS-03)
        definition = api.active_definition(ctx.scene)
    if definition is None or definition.builtin:
        check("padrão editável para o teste", False, "sem definição de usuário")
        return
    api.set_values(definition, {schema.external_key('COZ', 'stretcher_width'): 80.0})
    sync.apply_definition(ctx.scene, definition, modules=[base])
    yield 0.6
    front = next((r for r in records(ctx, base) if r.name == "Sarrafo frontal"), None)
    check("padrão com sarrafo de 80 reaplicado", front is not None and abs(front.width - 80.0) < 1e-3,
          str(front.width if front else None))


def script():
    ctx = bpy.context
    env.clean_scene()
    yield 0.5
    yield from run_gallery(ctx)
    base = yield from run_kitchen(ctx)
    yield from run_wardrobe(ctx)
    yield from run_legacy(ctx)
    yield from run_standard(ctx, base)
    parts, _bad = part_extractor.extract_production_parts(ctx)
    modules = part_extractor.module_entries(ctx.scene)
    payload = json_exporter.build_global_payload(project={"name": "015"}, standard={}, parts=parts, modules=modules,
                                                 hardware=hardware.collect(ctx.scene))
    check("JSON 2.3.0 válido com structure_id",
          payload["schema_version"] == "2.3.0" and not json_exporter.validate_global_json(payload)
          and any(m.get("structure_id") for m in payload["modules"]),
          str(json_exporter.validate_global_json(payload)[:3]))


_gen = script()


def tick():
    try:
        return next(_gen)
    except StopIteration:
        pass
    except Exception:
        traceback.print_exc()
        FAILURES.append("exceção no roteiro")
    print(f"blender_015_construtor_smoke: {'OK' if not FAILURES else 'FALHAS: ' + ', '.join(FAILURES)}", flush=True)
    os._exit(1 if FAILURES else 0)


bpy.app.timers.register(tick, first_interval=2.0)
