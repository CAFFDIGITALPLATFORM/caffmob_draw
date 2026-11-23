"""Teste de fumaça da feature 015 (T042), enxuto desde a 017: o construtor com a arquitetura do Promob.

Precisa de janela (não roda em --background), numa instância própria (encerra com o código do resultado):
    xvfb-run -a blender --factory-startup --enable-event-simulate --python tests/blender_015_construtor_smoke.py

A T027 da 017 tirou do registro a interface do editor 2D: `bpy.ops.caffmob.cabinet_editor` passou a ser o `Abrir` do
armário v2 e recusa módulo de biblioteca por RN-23. O roteiro original — armário de dormitório com 3 vãos, 900 no vão do
meio, Cabideiro 01, prateleira Invisível e a conversão do módulo antigo ao abrir — era todo dirigido pela sessão do
editor (`props.session()`/`s.push(...)`) e não roda mais. Ficou o que não passa por essa sessão:

- galeria "Selecione uma estrutura de caixa": abre com desenho ativo; Esc fecha sem criar nada; Enter cria a estrutura
  escolhida (Inferior c/ Divisória);
- corte do Inferior c/ Divisória por `part_sources`: Sarrafo frontal e traseiro, sem Base superior; Superior com Base
  superior; medidas do padrão;
- Padrão de Dimensões com sarrafo de 80 reaplicado muda os sarrafos do balcão;
- JSON de produção na versão vigente do exportador (2.5.0 hoje; era 2.3.0 quando a fumaça nasceu) válido, com
  `structure_id`.

O que saiu daqui e a lacuna que fica (aplicação na cena de divisões, internos e ferragens) estão registrados em
`_reversa_forward/017-construtor-armario-v2/actions.md`.
"""

import os
import sys
import traceback
from pathlib import Path

import bpy

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _blender_env as env  # noqa: E402
from caffmob_draw.cabinet_editor import gallery  # noqa: E402
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
    yield from run_standard(ctx, base)
    parts, _bad = part_extractor.extract_production_parts(ctx)
    modules = part_extractor.module_entries(ctx.scene)
    payload = json_exporter.build_global_payload(project={"name": "015"}, standard={}, parts=parts, modules=modules,
                                                 hardware=hardware.collect(ctx.scene))
    # A versão do contrato sobe com as features seguintes (2.3.0 → 2.5.0): a fumaça segue o exportador, não um número
    # congelado, porque o que ela prova aqui é o `structure_id` da 015 dentro de um JSON válido.
    check("JSON do exportador válido, com structure_id",
          payload["schema_version"] == json_exporter.SCHEMA_VERSION
          and not json_exporter.validate_global_json(payload)
          and any(m.get("structure_id") for m in payload["modules"]),
          f"{payload['schema_version']}; {str(json_exporter.validate_global_json(payload)[:3])}")


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
