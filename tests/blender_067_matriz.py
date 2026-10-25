"""Matriz Requisito x Tipo (feature 067, T003, T095; RF-142).

Run: blender --background --factory-startup --python-exit-code 1 --python tests/blender_067_matriz.py -- --onda 1

`tests/data/067_matriz.json` guarda a linha de base da 1.8.0 (a matriz da auditoria, vermelha onde ela diz FALTA ou
PARCIAL) e as colunas de cada onda. O ensaio refaz a matriz pelo snapshot, pelo ViewModel e pela camada falsa
(`ui/layout_probe.py`) e exige, até a onda pedida, cada célula em OK ou N/A; as colunas das ondas seguintes aparecem
como "pendente". Os critérios por coluna:
- UX-01: cabeçalho com tipo e escopo; caminho do dono quando há dono; Essencial contido na Completa; o menu do botão
  direito sai do mesmo CommandRouter;
- UX-02: o painel mostra as propriedades do próprio selecionado (adaptador próprio; chapa com as medidas dela, nunca
  as do módulo);
- UX-04: cotas com o alvo móvel, ou "indisponível para <motivo>".
"""

import json
import sys
import traceback
from pathlib import Path

import bpy

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _blender_env as env  # noqa: E402,F401
import _desempenho_067 as perf  # noqa: E402
import _fixtures_067 as fx  # noqa: E402
from caffmob_draw.target import commands, snapshot, view  # noqa: E402
from caffmob_draw.target import resolver as r  # noqa: E402
from caffmob_draw.ui import layout_probe  # noqa: E402
from caffmob_draw.ui import object_properties as op  # noqa: E402

DATA = json.loads((Path(__file__).resolve().parent / "data" / "067_matriz.json").read_text(encoding='utf-8'))
TYPE_OBJECTS = {'module': 'btm_module', 'multiple': None}
MODULE_DIMS = {('selection', 'width'), ('selection', 'height'), ('selection', 'depth')}


def wave():
    argv = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
    return int(argv[argv.index('--onda') + 1]) if '--onda' in argv else 1


def ux01(target):
    essential, complete = view.build(target, view.ESSENTIAL), view.build(target, view.COMPLETE)
    header = complete.header
    ok = bool(header.kind_label and header.scope_label)
    ok &= (len(header.path) >= 2) == target.has_owner or target.kind in (r.MULTIPLE, r.CLADDING)
    ok &= {(f.data, f.prop) for f in view.fields(essential)} <= {(f.data, f.prop) for f in view.fields(complete)}
    ok &= all(entry.enabled for entry in commands.menu_items(target))
    return ok


def ux02(target):
    if target.adapter == 'FALLBACK':
        return False
    fields = {(f.data, f.prop) for f in view.fields(view.build(target, view.COMPLETE))}
    if target.kind in r.SHEET_KINDS:
        return target.measures is not None and not (fields & MODULE_DIMS)
    return bool(fields)


def ux04(target):
    sections = {s.id: s for s in view.build(target, view.COMPLETE).sections}
    cotas = sections.get('cotas')
    if cotas is None:
        return False
    fields = [i for i in cotas.items if isinstance(i, view.Field)]
    notes = [i for i in cotas.items if isinstance(i, view.Note) and "indisponível" in i.text]
    return bool(fields) == bool(target.move_uid) and (bool(fields) or bool(notes))


CHECKS = {'UX-01': ux01, 'UX-02': ux02, 'UX-04': ux04}


def build_targets():
    s = fx.scene_15()
    bpy.context.scene.btm_component_select = False
    out = {}
    for row in DATA['linha_de_base_1_8_0']:
        name = TYPE_OBJECTS.get(row, row)
        if row == 'multiple':
            fx.select([s.part, s.member, s.geometry], s.part)
        else:
            fx.select([getattr(s, name)])
        bpy.context.view_layer.update()
        out[row] = snapshot.ensure(bpy.context)
        recorder = layout_probe.Recorder()
        op.panel_mode = lambda _c: 'COMPLETE'
        op.draw_selected(layout_probe.Probe(recorder), perf.CTX)       # o draw não pode falhar em nenhum tipo
    return out


def main():
    current = wave()
    active = [c for w, cols in DATA['colunas_por_onda'].items() if int(w) <= current for c in cols]
    targets = build_targets()
    failures, lines = [], []
    for row, baseline in DATA['linha_de_base_1_8_0'].items():
        cells = []
        for column in DATA['colunas']:
            if baseline[column] == 'N/A':
                cells.append('N/A')
            elif column not in active:
                cells.append('pendente')
            else:
                ok = CHECKS[column](targets[row])
                cells.append('OK' if ok else 'FALHA')
                if not ok:
                    failures.append(f"{row} × {column} (1.8.0: {baseline[column]})")
        lines.append(f"MATRIZ {row:<11} " + " ".join(f"{c:<8}" for c in cells))
    print("MATRIZ tipo        " + " ".join(f"{c:<8}" for c in DATA['colunas']), flush=True)
    for line in lines:
        print(line, flush=True)
    return failures


try:
    FAILURES = main()
except Exception:
    traceback.print_exc()
    FAILURES = ["exceção"]
print(f"blender_067_matriz: {'OK' if not FAILURES else 'FALHAS: ' + ', '.join(FAILURES)}", flush=True)
sys.exit(1 if FAILURES else 0)
