"""Teste de fumaça da feature 006 (T038): editor de armário em abas, Estrutura e Divisão.

**APOSENTADO** (T034 da 017, 2026-11-22). Dirige a interface do editor 2D que a T027 (D-04) tirou do registro: hoje
`bpy.ops.caffmob.cabinet_editor` é o `Abrir` do armário v2 e recusa módulo de biblioteca (RN-23), então a fumaça morre no
primeiro `open_editor`, sem conferência nenhuma. Fica aqui como registro da superfície removida; o motivo, a cobertura
substituta e a lacuna estão em `tests/retired/README.md`.

Precisa de janela (não roda em --background), numa instância própria (encerra com o código do resultado):
    xvfb-run -a blender --factory-startup --enable-event-simulate --python tests/blender_006_cabinet_editor_tabs_smoke.py

Para um módulo de cada biblioteca (frameless, face frame, closets, `btm`):
- abas: Estrutura aberta ao abrir; cada aba desenha os seus painéis (camada falsa da 005) e o rodapé aparece em todas;
- Estrutura: remover e restaurar a lateral direita (Manter tudo); no `btm`, Reduzir o armário tira a espessura da
  largura e Restaurar devolve; no frameless, Estender as vizinhas na base liga o `Remove Bottom`;
- Divisão: vertical com recuo na frente no meio do vão; horizontal só no subvão esquerdo; posição a 20 mm dá
  `DIV-001` e bloqueia Confirmar;
- Cancelar devolve tudo (nenhuma divisão, nada removido, mesma vista);
- Confirmar = um passo de desfazer; plano de corte com as divisões (menos o face frame, lacuna herdada) e sem a
  lateral removida; mudar a altura fora do editor estica a divisão vertical;
- salvar o `.blend` e reabrir noutro Blender: remoção e divisões continuam lá.
"""

import os
import subprocess
import sys
import tempfile
import traceback
from collections import Counter
from pathlib import Path

import bpy

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import _blender_env as env  # noqa: E402
from caffmob_draw import compat, hb_utils  # noqa: E402
from caffmob_draw.cabinet_editor import (bridge, panels, panels_backs, panels_divisions,  # noqa: E402
                                         panels_doors, panels_drawers, panels_interior, panels_sliding,
                                         panels_structure, props, scene_divisions)
from caffmob_draw.cabinet_editor import window as cew  # noqa: E402
from caffmob_draw.customize.adapters import common  # noqa: E402
from caffmob_draw.cutting import part_extractor  # noqa: E402
from caffmob_draw.product_libraries.closets import types_closets as tc  # noqa: E402
from caffmob_draw.product_libraries.face_frame import types_face_frame as tff  # noqa: E402
from caffmob_draw.product_libraries.frameless import types_frameless as tf  # noqa: E402
from caffmob_draw.ui import layout_probe  # noqa: E402

FAILURES = []
ICONS = set(bpy.types.UILayout.bl_rna.functions['label'].parameters['icon'].enum_items.keys())
TABS = {
    'STRUCTURE': {'panels': (panels.BTM_PT_CabinetEditorDimensions, panels_structure.BTM_PT_CabinetEditorStructure),
                  'ops': {'caffmob.cabinet_editor_part_remove', 'caffmob.cabinet_editor_part_edit'}},
    'DIVISIONS': {'panels': (panels_divisions.BTM_PT_CabinetEditorDivisionNew,
                             panels_divisions.BTM_PT_CabinetEditorDivisionList),
                  'ops': {'caffmob.cabinet_editor_insert'}},
    # Feature 008 (T050): a aba Acabamento saiu; cada aba nova tem o seu painel e o Inserir no mesmo lugar.
    'DRAWERS': {'panels': (panels_drawers.BTM_PT_CabinetEditorDrawers,), 'ops': {'caffmob.cabinet_editor_insert'}},
    'INTERIOR': {'panels': (panels_interior.BTM_PT_CabinetEditorInterior,),
                 'ops': {'caffmob.cabinet_editor_insert', 'caffmob.cabinet_editor_pick'}},
    'DOORS': {'panels': (panels_doors.BTM_PT_CabinetEditorDoors,), 'ops': {'caffmob.cabinet_editor_insert'}},
    'SLIDING': {'panels': (panels_sliding.BTM_PT_CabinetEditorSliding,),
                'ops': {'caffmob.cabinet_editor_insert', 'caffmob.cabinet_editor_pick'}},
    'BACKS': {'panels': (panels_backs.BTM_PT_CabinetEditorBacks,), 'ops': {'caffmob.cabinet_editor_insert'}},
}
FOOTER = (panels.BTM_PT_CabinetEditorTabs, panels.BTM_PT_CabinetEditorMessages, panels.BTM_PT_CabinetEditorConfirm)


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


def signature(ctx, name):
    root = bpy.data.objects[name]
    parts = sorted((p.kind, tuple(round(v, 4) for v in p.lo + p.hi)) for p in bridge.parts(ctx, root))
    return tuple(round(v, 4) for v in bridge.read_state(root).dimensions), parts


class IconProbe(layout_probe.Probe):
    """Camada falsa da 005 que também guarda os ícones pedidos (para conferir que existem no 5.2)."""

    def _child(self):
        return IconProbe(self.recorder)

    def row(self, *args, **kwargs):
        return self._child()

    def column(self, *args, **kwargs):
        return self._child()

    def box(self, *args, **kwargs):
        return self._child()

    def grid_flow(self, *args, **kwargs):
        return self._child()

    def _icon(self, kwargs):
        if kwargs.get('icon'):
            self.recorder.__dict__.setdefault('icons', set()).add(kwargs['icon'])

    def label(self, *args, **kwargs):
        self._icon(kwargs)

    def operator(self, idname, *args, **kwargs):
        self._icon(kwargs)
        return super().operator(idname, *args, **kwargs)


def draw_with_probe(cls, ctx):
    """Desenha o painel na camada falsa (sem tela); devolve os operadores e os ícones usados."""
    probe = IconProbe()
    proxy = type("P", (), {"layout": probe})()
    cls.draw(proxy, ctx)
    return {r['name'] for r in probe.recorder.operators()}, set(getattr(probe.recorder, 'icons', set()))


def check_tabs(ctx, name):
    ewin, earea, _ereg = cew.editor_area(ctx)
    ui = ctx.window_manager.btm_cabinet_editor
    check(f"{name}: abre na aba Estrutura", ui.tab == 'STRUCTURE', ui.tab)
    region = next(r for r in earea.regions if r.type == 'UI')
    for tab, spec in TABS.items():
        ui.tab = tab
        with ctx.temp_override(window=ewin, area=earea, region=region):
            visible = {cls.__name__ for cls in spec['panels'] + FOOTER if cls.poll(bpy.context)}
            hidden = {cls.__name__ for other, ospec in TABS.items() if other != tab for cls in ospec['panels']
                      if cls.poll(bpy.context)}
            ops, icons = set(), set()
            for cls in spec['panels'] + FOOTER:
                found, used = draw_with_probe(cls, bpy.context)
                ops |= found
                icons |= used
        want = {cls.__name__ for cls in spec['panels'] + FOOTER}
        check(f"{name}: aba {tab} mostra os painéis dela e o rodapé", want <= visible and not hidden,
              f"faltam {sorted(want - visible)}; sobram {sorted(hidden)}")
        check(f"{name}: aba {tab} tem as ações", spec['ops'] <= ops, f"faltam {sorted(spec['ops'] - ops)}")
        check(f"{name}: aba {tab} só usa ícones que existem", icons <= ICONS, str(sorted(icons - ICONS)))
    enum_icons = {item.icon for prop in ('tab', 'new_orientation')
                  for item in ui.bl_rna.properties[prop].enum_items}
    check(f"{name}: ícones das abas e da orientação existem", enum_icons <= ICONS, str(sorted(enum_icons - ICONS)))
    ui.tab = 'STRUCTURE'


def cut_parts(ctx, name):
    parts, _bad = part_extractor.extract_production_parts(ctx)
    return Counter((p.component, round(p.height), round(p.width), round(p.thickness, 1))
                   for p in parts if p.module_ref == name)


def right_hidden(root):
    objs = common.call(bridge.adapter_of(root), 'structure_parts', root).get('RIGHT', [])
    return [o.hide_viewport for o in objs]


def run_library(ctx, name, results):
    library = bridge.info_of(bpy.data.objects[name]).library
    before = signature(ctx, name)
    cut_before = cut_parts(ctx, name)
    check(f"{name}: abre o editor", open_editor(ctx, name) == {'FINISHED'})
    yield 1.2
    s = props.session()
    if s is None:
        check(f"{name}: sessão", False)
        return
    root = s.root()
    check_tabs(ctx, name)
    ui = ctx.window_manager.btm_cabinet_editor
    check(f"{name}: lista os componentes externos", {r.role for r in ui.structure} >= {'LEFT', 'RIGHT'},
          str([r.role for r in ui.structure]))

    # Estrutura: remover e restaurar a lateral direita (Manter tudo)
    s.push('edit', ('REMOVE_PART', {'role': 'RIGHT', 'mode': 'KEEP', 'targets': []}))
    yield 0.6
    row = next((r for r in ui.structure if r.role == 'RIGHT'), None)
    check(f"{name}: lateral direita removida", row is not None and row.removed
          and (library == 'BTM' or all(right_hidden(root))), str(right_hidden(root)))
    s.push('edit', ('RESTORE_PART', {'role': 'RIGHT', 'targets': []}))
    yield 0.6
    row = next((r for r in ui.structure if r.role == 'RIGHT'), None)
    check(f"{name}: Restaurar devolve a lateral", row is not None and not row.removed
          and not any(right_hidden(root)), str(right_hidden(root)))
    if library == 'BTM':
        width = s.draft.current.dimensions[0]
        t = root.btm_cabinet.thickness
        s.push('edit', ('REMOVE_PART', {'role': 'RIGHT', 'mode': 'SHRINK', 'targets': []}))
        yield 0.6
        check(f"{name}: Reduzir o armário tira a espessura da largura",
              abs(s.draft.current.dimensions[0] - (width - t)) < 1e-4, str(s.draft.current.dimensions))
        s.push('edit', ('RESTORE_PART', {'role': 'RIGHT', 'targets': []}))
        yield 0.6
        check(f"{name}: Restaurar devolve a largura", abs(s.draft.current.dimensions[0] - width) < 1e-4)
    if library == 'FRAMELESS':
        s.push('edit', ('REMOVE_PART', {'role': 'BOTTOM', 'mode': 'EXTEND', 'targets': []}))
        yield 0.6
        check(f"{name}: Estender as vizinhas na base liga o Remove Bottom", bool(root.get('Remove Bottom')))
        s.push('edit', ('RESTORE_PART', {'role': 'BOTTOM', 'targets': []}))
        yield 0.6
        check(f"{name}: Restaurar desliga o Remove Bottom", not root.get('Remove Bottom'))

    # Divisão
    ui.tab = 'DIVISIONS'
    space = s.space
    check(f"{name}: vão já escolhido", bool(space) and space in s.spaces, f"{space!r} {sorted(s.spaces)}")
    box = s.spaces.get(space)
    s.push('edit', ('ADD_DIVISION', {'space': space, 'orientation': 'VERTICAL', 'use_front': True, 'front': 0.02,
                                     'use_back': False, 'back': 0.02, 'targets': []}))
    yield 0.8
    divs = scene_divisions.objects(root)
    material, thickness = scene_divisions.configured(ctx.scene, root)
    ok = len(divs) == 1
    if ok:
        mod = common.gn_modifier(divs[0], 'GeoNodeCutpart')
        length = compat.try_get_gn_input(mod, 'Length', 0.0)
        width = compat.try_get_gn_input(mod, 'Width', 0.0)
        ok = (abs(length - box.size(2)) < 1e-4 and abs(width - (box.size(1) - 0.02)) < 1e-4
              and abs(divs[0].btm_division.offset - (box.size(0) - thickness) / 2.0) < 1e-4)
        detail = f"{length:.4f}x{width:.4f} vão {box.size(2):.4f}x{box.size(1):.4f}"
    else:
        detail = str(len(divs))
    check(f"{name}: vertical no meio do vão, altura inteira e recuo na frente", ok, detail)
    left = space + ".a"
    check(f"{name}: subvãos esquerdo e direito", {left, space + ".b"} <= set(s.spaces), str(sorted(s.spaces)))
    s.space = left
    s.push('edit', ('ADD_DIVISION', {'space': left, 'orientation': 'HORIZONTAL', 'targets': []}))
    yield 0.8
    divs = scene_divisions.objects(root)
    horizontal = next((d for d in divs if d.btm_division.orientation == 'HORIZONTAL'), None)
    ok = horizontal is not None and horizontal.btm_division.space == left
    if ok:
        mod = common.gn_modifier(horizontal, 'GeoNodeCutpart')
        ok = abs(compat.try_get_gn_input(mod, 'Length', 0.0) - s.spaces[left + ".a"].size(0)) < 1e-4
    check(f"{name}: horizontal só no subvão esquerdo", ok)
    check(f"{name}: lista de divisões", len(ui.divisions) == 2, str(len(ui.divisions)))
    vertical = next(d for d in divs if d.btm_division.orientation == 'VERTICAL')
    uid = vertical.btm_division.uid
    s.push('edit', ('EDIT_DIVISION', {'uid': uid, 'offset': 0.02, 'targets': []}))
    yield 0.6
    check(f"{name}: DIV-001 impede Confirmar", s.blocking() and any(m.code == 'DIV-001' for m in s.messages),
          str([m.code for m in s.messages]))
    s.push('edit', ('EDIT_DIVISION', {'uid': uid, 'offset': 0.3, 'targets': []}))
    yield 0.6
    check(f"{name}: posição válida libera", not any(m.code.startswith('DIV') for m in s.messages),
          str([m.code for m in s.messages]))

    # Cancelar
    s.request = 'cancel'
    yield 1.0
    check(f"{name}: Cancelar fecha", props.session() is None)
    after = signature(ctx, name)
    check(f"{name}: Cancelar devolve tudo", after == before and not scene_divisions.objects(root)
          and not root.btm_structure.components,
          f"{before[0]} → {after[0]}; divisões {len(scene_divisions.objects(root))}")

    # Confirmar
    open_editor(ctx, name)
    yield 1.2
    s = props.session()
    if s is None:
        check(f"{name}: reabre", False)
        return
    s.push('edit', ('REMOVE_PART', {'role': 'RIGHT', 'mode': 'KEEP', 'targets': []}))
    yield 0.6
    s.push('edit', ('ADD_DIVISION', {'space': s.space, 'orientation': 'VERTICAL', 'use_front': True, 'front': 0.02,
                                     'targets': []}))
    yield 0.8
    s.request = 'ok'
    yield 1.0
    divs = scene_divisions.objects(root)
    check(f"{name}: Confirmar grava divisão e remoção", len(divs) == 1 and bool(root.btm_structure.components))
    cut = cut_parts(ctx, name)
    added, removed = cut - cut_before, cut_before - cut
    if library == 'FACE_FRAME':
        check(f"{name}: face frame segue fora do plano de corte", not cut and not cut_before)
    else:
        check(f"{name}: plano de corte com a divisória e sem a lateral",
              sum(n for k, n in added.items() if k[0] == 'DIV') == 1
              and sum(n for k, n in removed.items() if k[0] == 'LAT') == 1, f"+{dict(added)} -{dict(removed)}")
    # Fora do editor: a altura muda e a divisória vertical acompanha
    if divs:
        mod = common.gn_modifier(divs[0], 'GeoNodeCutpart')
        length0 = compat.try_get_gn_input(mod, 'Length', 0.0)
        height0 = bridge.read_state(root).dimensions[1]
        bridge.set_dimension(ctx, root, 'height', height0 + 0.1)
        if library == 'CLOSETS':
            tc.recalculate_closet_starter(root)
        env.settle(5)
        yield 0.6
        length1 = compat.try_get_gn_input(mod, 'Length', 0.0)
        check(f"{name}: fora do editor a divisória acompanha a altura", abs(length1 - length0 - 0.1) < 2e-3,
              f"{length0:.4f} → {length1:.4f}")
        bridge.set_dimension(ctx, root, 'height', height0)
        if library == 'CLOSETS':
            tc.recalculate_closet_starter(root)
        env.settle(5)
        yield 0.4
        win, area, region = view3d(ctx)
        with ctx.temp_override(window=win, area=area, region=region):
            bpy.ops.ed.undo_push(message="altura de volta")
    results[name] = {'divisions': len(divs), 'removed': [e.role for e in root.btm_structure.components if e.removed]}


def check_reopen(ctx, results):
    path = os.path.join(tempfile.mkdtemp(prefix="caffmob_006_"), "projeto.blend")
    bpy.ops.wm.save_as_mainfile(filepath=path, copy=True)
    expr = ("import sys, json; sys.path.insert(0, %r); import _blender_env; import bpy; "
            "from caffmob_draw.cabinet_editor import scene_divisions as sd; "
            "print('RESULT', json.dumps({n: {'divisions': len(sd.objects(bpy.data.objects[n])), "
            "'removed': [e.role for e in bpy.data.objects[n].btm_structure.components if e.removed]} "
            "for n in %r}))") % (str(Path(__file__).resolve().parents[1]), sorted(results))
    out = subprocess.run([bpy.app.binary_path, "--background", "--factory-startup", path, "--python-expr", expr],
                         capture_output=True, text=True, timeout=300).stdout
    line = next((ln for ln in out.splitlines() if ln.startswith("RESULT ")), "RESULT {}")
    import json
    reopened = json.loads(line[len("RESULT "):])
    check("reabrir o .blend mantém remoções e divisões", reopened == results, f"{results} → {reopened}")


def script():
    ctx = bpy.context
    names = make_modules(ctx)
    win, area, region = view3d(ctx)
    with ctx.temp_override(window=win, area=area, region=region):
        bpy.ops.ed.undo_push(message="Módulos de teste")
    yield 0.5
    results = {}
    for name in names:
        yield from run_library(ctx, name, results)
    # Um passo de desfazer: o último Confirmar (btm) volta inteiro com um Ctrl+Z antes do empurrão da altura
    check_reopen(ctx, results)
    name = names[-1]
    root = bpy.data.objects[name]
    with ctx.temp_override(window=win, area=area, region=region):
        bpy.ops.ed.undo()         # desfaz o empurrão "altura de volta"
        bpy.ops.ed.undo()         # desfaz o Confirmar
    yield 0.8
    root = bpy.data.objects.get(name)
    check("um Ctrl+Z desfaz o Confirmar inteiro", root is not None and not scene_divisions.objects(root)
          and not root.btm_structure.components)


_gen = script()


def tick():
    try:
        return next(_gen)
    except StopIteration:
        pass
    except Exception:
        traceback.print_exc()
        FAILURES.append("exceção no roteiro")
    print(f"blender_006_cabinet_editor_tabs_smoke: {'OK' if not FAILURES else 'FALHAS: ' + ', '.join(FAILURES)}",
          flush=True)
    os._exit(1 if FAILURES else 0)


bpy.app.timers.register(tick, first_interval=2.0)
