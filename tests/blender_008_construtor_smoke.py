"""Teste de fumaça da feature 008 (T051): editor de armário no modelo do Construtor de Armários.

Precisa de janela (não roda em --background), numa instância própria (encerra com o código do resultado):
    xvfb-run -a blender --factory-startup --enable-event-simulate --python tests/blender_008_construtor_smoke.py

Para um módulo de cada biblioteca (frameless, face frame, closets, `btm`), pedindo ao editor o mesmo que o botão
Inserir pede (`ops_actions.insert_payload`):
- fluxo: 7 abas com ícones do 5.2, miniaturas do catálogo, barra "Selecionado", Inserir sem vão desabilitado;
- Divisões: inserção múltipla (2 verticais), distanciador de 30 (o vão perde 30 mm sem virar dois), prateleira móvel;
- Fundos: Inteiro Recuado tira 20 mm da profundidade do vão;
- Estrutura: Pés Plásticos ligados = 4 pés na lista de ferragens;
- Internos: apoio de eletro no vão; Gavetas (frameless): gavetões; Portas (closets): porta inteira invertida;
  Deslizantes (`btm`): trilhos na lista de ferragens;
- Aplicar grava e vira a referência do Cancelar; plano de corte com furação da móvel (menos face frame, lacuna
  herdada da 006); JSON 2.2.0 válido com `hardware`;
- `btm` 800 × 2250 × 550 com 3 vãos: vãos iguais de (770 − 2 × divisória) / 3; um Ctrl+Z desfaz o Aplicar inteiro.
"""

import os
import sys
import traceback
from pathlib import Path

import bpy

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _blender_env as env  # noqa: E402
from caffmob_draw import hb_utils  # noqa: E402
from caffmob_draw.cabinet_editor import (bridge, catalog, ops_actions, previews, props,  # noqa: E402
                                         scene_divisions, scene_interiors, scene_slides)
from caffmob_draw.cabinet_editor import window as cew  # noqa: E402
from caffmob_draw.cutting import hardware, json_exporter, part_extractor  # noqa: E402
from caffmob_draw.data.i18n import tr  # noqa: E402
from caffmob_draw.product_libraries.closets import types_closets as tc  # noqa: E402
from caffmob_draw.product_libraries.face_frame import types_face_frame as tff  # noqa: E402
from caffmob_draw.product_libraries.frameless import types_frameless as tf  # noqa: E402

FAILURES = []
ICONS = set(bpy.types.UILayout.bl_rna.functions['label'].parameters['icon'].enum_items.keys())


def check(name, ok, detail=""):
    print(("OK   " if ok else "FALHA ") + name, detail, flush=True)
    if not ok:
        FAILURES.append(name)


def view3d(ctx):
    win = ctx.window_manager.windows[0]
    area = next(a for a in win.screen.areas if a.type == 'VIEW_3D')
    region = next(r for r in area.regions if r.type == 'WINDOW')
    return win, area, region


def make_modules(ctx):
    env.clean_scene()
    base = tf.BaseCabinet()
    base.create("Balcao")
    hb_utils.run_calc_fix_until_stable(ctx, base.obj)
    ff = tff.BaseFaceFrameCabinet()
    ff.create("FaceFrame")
    ff.obj.location.x = 3.0
    starter = tc.BaseClosetStarter()
    starter.create_starter("Roupeiro", bay_qty=2)
    starter.obj.location.x = 6.0
    tc.recalculate_closet_starter(starter.obj)
    win, area, region = view3d(ctx)
    with ctx.temp_override(window=win, area=area, region=region):
        bpy.ops.caffmob.cabinet_builder(width=0.6)
    quick = ctx.object
    quick.location.x = 9.0
    env.settle()
    return [base.obj.name, ff.obj.name, starter.obj.name, quick.name]


def open_editor(ctx, name):
    root = bpy.data.objects[name]
    for obj in ctx.selected_objects:
        obj.select_set(False)
    root.select_set(True)
    ctx.view_layer.objects.active = root
    win, area, region = view3d(ctx)
    with ctx.temp_override(window=win, area=area, region=region, active_object=root, object=root):
        return bpy.ops.caffmob.cabinet_editor('INVOKE_DEFAULT')


def module_hardware(ctx, root):
    rows = hardware.collect(ctx.scene)          # grava o `btm_uid` do módulo que ainda não tem
    uid = root.get('btm_uid')
    return {r['code']: r['quantity'] for r in rows if r['module_uid'] == uid}


def insert(ctx, s, tab):
    s.push('edit', ops_actions.insert_payload(ctx, tab))


def leaves(s):
    return sorted(s.spaces)


def check_flow(ctx, name, s, ui):
    tab_icons = {item.icon for item in ui.bl_rna.properties['tab'].enum_items}
    check(f"{name}: 7 abas com ícones do 5.2", len(tab_icons) == 7 and tab_icons <= ICONS,
          str(sorted(tab_icons - ICONS)))
    missing = [i.id for i in catalog.ITEMS if not previews.icon_id(i.thumb)]
    check(f"{name}: miniatura de cada item do catálogo", not missing, str(missing[:5]))
    check(f"{name}: barra de estado diz o selecionado", tr("Selecionado: {}").split("{")[0] in cew.status_text(s),
          cew.status_text(s))
    saved = s.space
    s.space = ""
    check(f"{name}: Inserir sem vão fica desabilitado com o motivo",
          ops_actions.insert_reason(ctx, 'DIVISIONS') == tr(ops_actions.NO_SPACE))
    s.space = saved


def run_divisions(ctx, name, s, ui, root, library):
    ui.tab = 'DIVISIONS'
    s.space = leaves(s)[0]
    # o balcão frameless já tem uma prateleira da biblioteca no meio: verticais a cruzariam (GEO-002)
    orientation = 'HORIZONTAL' if library == 'FRAMELESS' else 'VERTICAL'
    ui.div_mode, ui.new_orientation, ui.div_count, ui.div_kind, ui.catalog_item = 'MULTIPLE', orientation, 2, 'FIXED', ''
    insert(ctx, s, 'DIVISIONS')
    yield 0.8
    check(f"{name}: inserção múltipla cria 2 divisórias", len(scene_divisions.objects(root)) == 2,
          str(len(scene_divisions.objects(root))))
    leaf = leaves(s)[0]
    width = s.spaces[leaf].size(0)
    s.space = leaf
    ui.div_mode, ui.div_kind, ui.catalog_item = 'VERTICAL', 'SPACER', 'SPACER_30'
    insert(ctx, s, 'DIVISIONS')
    yield 0.8
    box = s.spaces.get(leaf)
    check(f"{name}: distanciador 30 tira 30 mm sem dividir o vão",
          box is not None and abs(box.size(0) - (width - 0.03)) < 1e-4,
          f"{width:.4f} → {box.size(0) if box else None}")
    s.space = leaf
    ui.div_mode, ui.div_kind, ui.catalog_item = 'HORIZONTAL', 'MOVABLE', ''
    insert(ctx, s, 'DIVISIONS')
    yield 0.8
    kinds = sorted(o.btm_division.kind for o in scene_divisions.objects(root))
    check(f"{name}: prateleira móvel inserida", kinds.count('MOVABLE') == 1 and kinds.count('SPACER') == 1, str(kinds))


def run_backs(ctx, name, s, ui, root, library):
    depth = max(b.size(1) for b in s.spaces.values())
    ui.tab, ui.back_tab = 'BACKS', 'RECESSED'
    insert(ctx, s, 'BACKS')
    yield 0.8
    after = max(b.size(1) for b in s.spaces.values())
    if library == 'CLOSETS':                    # o roupeiro padrão não tem fundo: avisa e não muda nada
        said = [m.action for m in s.messages if m.code == 'LIB-001']
        check(f"{name}: sem fundo, Fundos avisa e não muda", tr("Este armário não tem fundo") in said
              and root.btm_structure.back_mode == 'FULL' and abs(depth - after) < 1e-6, str(said))
        return
    check(f"{name}: Inteiro Recuado tira 20 mm da profundidade do vão",
          root.btm_structure.back_mode == 'RECESSED' and abs(depth - after - 0.02) < 1e-3, f"{depth:.4f} → {after:.4f}")


def run_extras(ctx, name, s, root, library):
    s.push('edit', ('TOGGLE_EXTRA', {'key': 'FEET', 'enabled': True}))
    yield 0.8
    if library == 'FACE_FRAME':                 # fora do plano de corte e das ferragens (lacuna herdada da 006)
        check(f"{name}: Pés Plásticos criados", len([o for o in root.children if o.get('btm_hardware')]) == 4)
        return
    feet = module_hardware(ctx, root).get('PE_PLASTICO', 0)
    check(f"{name}: Pés Plásticos = 4 pés na lista de ferragens", feet == 4, str(module_hardware(ctx, root)))


def run_interior(ctx, name, s, ui, root):
    ui.tab, ui.interior_group, ui.catalog_item = 'INTERIOR', 'SUPPORTS', 'SUPPORT'
    s.space = leaves(s)[-1]
    insert(ctx, s, 'INTERIOR')
    yield 0.8
    check(f"{name}: apoio de eletro no vão", len(scene_interiors.entries(root)) == 1,
          str(scene_interiors.entries(root)))


def run_library_fronts(ctx, name, s, ui, root, library):
    if library == 'FRAMELESS':
        ui.tab, ui.drawer_tab, ui.drawer_count = 'DRAWERS', 'TALL', 2
        s.space = leaves(s)[0]
        yield 0.3
        check(f"{name}: vão da biblioteca achado", bool(s.library_path), repr(s.library_path))
        insert(ctx, s, 'DRAWERS')
        yield 1.0
        pairs = module_hardware(ctx, root).get('CORREDICA', 0)
        check(f"{name}: gavetões contam corrediças", pairs >= 2, str(module_hardware(ctx, root)))
    if library == 'CLOSETS':
        ui.tab, ui.door_region, ui.door_scope, ui.invert = 'DOORS', 'LOWER', 'WHOLE', True
        s.space = leaves(s)[0]
        yield 0.3
        insert(ctx, s, 'DOORS')
        yield 1.0
        # a porta traz as prateleiras do roupeiro, que cruzam as divisórias aplicadas antes: GEO-002 é o aviso certo
        errors = [m for m in s.messages if m.severity == 'ERROR' and m.code != 'GEO-002']
        check(f"{name}: porta inteira invertida sem erro", bool(s.library_path) and not errors,
              f"{s.library_path!r} {[m.code for m in errors]}")
    if library == 'BTM':
        ui.tab, ui.slide_family, ui.catalog_item, ui.slide_leaves = 'SLIDING', 'WOOD', 'SLIDE_LISA', 2
        insert(ctx, s, 'SLIDING')
        yield 1.0
        found = module_hardware(ctx, root)
        check(f"{name}: deslizantes com trilhos na lista de ferragens",
              scene_slides.frame_of(root) is not None and found.get('TRILHO_SUP') == 1 and found.get('TRILHO_INF') == 1,
              str(found))


def run_apply(ctx, name, s, root, library):
    check(f"{name}: Aplicar habilitado com mudanças", s.draft.dirty())
    blocking = [(m.code, m.component, m.value) for m in s.messages if m.severity == 'ERROR']
    s.push('apply')
    yield 0.8
    check(f"{name}: Aplicar grava e o rascunho fica limpo", s.applied and not s.draft.dirty(), str(blocking))
    back = 'FULL' if library == 'CLOSETS' else 'RECESSED'
    count = len(scene_divisions.objects(root))
    s.request = 'cancel'
    yield 1.2
    check(f"{name}: Cancelar depois do Aplicar mantém o aplicado", props.session() is None
          and len(scene_divisions.objects(root)) == count and root.btm_structure.back_mode == back,
          f"{count} → {len(scene_divisions.objects(root))}")
    if library != 'FACE_FRAME':
        parts, _bad = part_extractor.extract_production_parts(ctx)
        drilled = [p for p in parts if p.module_ref == root.name and p.drilling]
        check(f"{name}: plano de corte com a furação da prateleira móvel", len(drilled) >= 2,
              str([p.name for p in drilled]))


def run_bays_case(ctx):
    """Caso da elicitação: 800 × 2250 × 550 (vão interno 770 com laterais de 15), 3 vãos iguais, num módulo novo."""
    win, area, region = view3d(ctx)
    with ctx.temp_override(window=win, area=area, region=region):
        bpy.ops.caffmob.cabinet_builder(width=0.8)
    name = ctx.object.name
    ctx.object.location.x = 12.0
    env.settle()
    check(f"{name}: abre o editor", open_editor(ctx, name) == {'FINISHED'})
    yield 1.2
    s = props.session()
    root = s.root()
    for field, value in (('width', 0.8), ('height', 2.25), ('depth', 0.55)):
        s.push('dimension', (field, value))
        yield 0.6
    s.push('edit', ('SET_BAYS', {'count': 3}))
    yield 1.0
    _material, t = scene_divisions.configured(ctx.scene, root)
    roots = scene_divisions.roots(ctx, root)
    inner = roots[min(roots)].size(0)
    side = root.btm_cabinet.thickness
    widths = sorted(round(b.size(0), 4) for b in s.spaces.values())
    want = (inner - 2 * t) / 3.0
    check(f"{name}: 3 vãos iguais de (interno − 2 divisórias) / 3",
          len(widths) == 3 and abs(inner - (0.8 - 2 * side)) < 1e-3 and all(abs(w - want) < 1e-3 for w in widths),
          f"interno {inner:.4f}; vãos {widths}; esperado {want:.4f}")
    s.request = 'cancel'
    yield 1.2


def run_library(ctx, name):
    library = bridge.info_of(bpy.data.objects[name]).library
    check(f"{name}: abre o editor", open_editor(ctx, name) == {'FINISHED'})
    yield 1.2
    s = props.session()
    if s is None:
        check(f"{name}: sessão", False)
        return
    root = s.root()
    ui = ctx.window_manager.btm_cabinet_editor
    check_flow(ctx, name, s, ui)
    yield from run_divisions(ctx, name, s, ui, root, library)
    yield from run_backs(ctx, name, s, ui, root, library)
    yield from run_extras(ctx, name, s, root, library)
    yield from run_interior(ctx, name, s, ui, root)
    yield from run_apply(ctx, name, s, root, library)
    # Frentes da biblioteca numa segunda abertura (a biblioteca cria peças próprias, como o separador dos gavetões e
    # as prateleiras da porta do roupeiro, que cruzariam as divisórias acima: GEO-002 bloquearia o Aplicar).
    if library in ('FRAMELESS', 'CLOSETS', 'BTM'):
        check(f"{name}: reabre para as frentes", open_editor(ctx, name) == {'FINISHED'})
        yield 1.2
        s = props.session()
        yield from run_library_fronts(ctx, name, s, ui, root, library)
        s.request = 'cancel'
        yield 1.2


def script():
    ctx = bpy.context
    names = make_modules(ctx)
    win, area, region = view3d(ctx)
    with ctx.temp_override(window=win, area=area, region=region):
        bpy.ops.ed.undo_push(message="Módulos de teste")
    yield 0.5
    for name in names:
        yield from run_library(ctx, name)
    parts, _bad = part_extractor.extract_production_parts(ctx)
    payload = json_exporter.build_global_payload(project={"name": "008"}, standard={}, parts=parts,
                                                 modules=part_extractor.module_entries(ctx.scene),
                                                 hardware=hardware.collect(ctx.scene))
    check("JSON 2.3.0 válido, com ferragens e furação",
          payload["schema_version"] == "2.3.0" and not json_exporter.validate_global_json(payload)
          and payload["hardware"] and any(p["drilling"] for p in payload["parts"]),
          str(json_exporter.validate_global_json(payload)[:3]))
    name = names[-1]
    with ctx.temp_override(window=win, area=area, region=region):
        bpy.ops.ed.undo()
    yield 0.8
    root = bpy.data.objects.get(name)
    check("um Ctrl+Z desfaz o Aplicar inteiro", root is not None and not scene_divisions.objects(root)
          and root.btm_structure.back_mode == 'FULL',
          str(len(scene_divisions.objects(root))) if root is not None else "sem raiz")
    with ctx.temp_override(window=win, area=area, region=region):
        bpy.ops.ed.redo()
    yield 0.8
    yield from run_bays_case(ctx)


_gen = script()


def tick():
    try:
        return next(_gen)
    except StopIteration:
        pass
    except Exception:
        traceback.print_exc()
        FAILURES.append("exceção no roteiro")
    print(f"blender_008_construtor_smoke: {'OK' if not FAILURES else 'FALHAS: ' + ', '.join(FAILURES)}", flush=True)
    os._exit(1 if FAILURES else 0)


bpy.app.timers.register(tick, first_interval=2.0)
