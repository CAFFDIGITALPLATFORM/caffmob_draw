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
- UX-04: cotas com o alvo móvel, ou "indisponível para <motivo>";
- MAT-03 (onda 2): seção Acabamentos com o material efetivo por domínio e o rascunho para aplicar, ou, sem papéis,
  o assistente de classificação;
- CMP-01 (onda 2): o comando equivalente ao U está no painel (na seção de agregados), executa na seleção múltipla
  de chapas e mostra o motivo nos outros tipos;
- UX-03 (onda 3): o veio é editável no próprio alvo: a chapa tem o campo do veio e a calibração da imagem; módulo e
  seleção múltipla, o veio das frentes nos acabamentos; o revestimento, o ângulo do veio;
- MAT-01 (onda 3): soltar uma textura no alvo tem destino semântico (dono com acabamentos e peças que recebem a
  textura), com a seção Acabamentos para escolher o domínio;
- MAT-02 (onda 4): a seção Acabamentos tem o botão da fita de borda com o rótulo do estado (criar, mudar cor ou
  misto) e, no misto, quantas bordas faltam;
- UX-05 (onda 5): o movimento é editável no próprio alvo: a folha pelo mecanismo (campos da folha), a frente do
  módulo rápido pela abertura, o módulo e o armário autoral pelo editor animado do componente, a porta de ambiente
  pelos controles da porta; a janela, sem folha gerada, diz isso.

Onda 8 (T187): as linhas `wall_mobi` e `opening_mobi` vêm do ambiente sintético do CAFF MOBI (`_mobi_sintetico`) e
passam pelos mesmos critérios das colunas das ondas 1 a 6.
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


def mat03(target):
    section = next((s for s in view.build(target, view.COMPLETE).sections if s.id == 'finish'), None)
    if section is None:
        return False
    actions = {i.operator for i in section.items if isinstance(i, view.Action)}
    if not target.finish_roles or not target.finish:
        return 'caffmob.finish_classify' in actions
    fields = {(i.data, i.prop) for i in section.items if isinstance(i, view.Field)}
    return bool(target.finish) and 'caffmob.finish_apply_draft' in actions and {
        ('finish_draft', 'domain'), ('finish_draft', 'material'), ('finish_draft', 'scale_mm'),
        ('finish_draft', 'grain')} <= fields


def cmp01(target):
    entry = next((e for e in commands.commands_for(target) if e.operator == 'caffmob.component_from_selection'),
                 None)
    if entry is None:
        return False
    shown = any(a.operator == entry.operator for a in view.actions(view.build(target, view.COMPLETE)))
    return shown and (entry.enabled if target.kind == r.MULTIPLE else bool(entry.reason))


def ux03(target):
    model = view.build(target, view.COMPLETE)
    fields = {(f.data, f.prop) for f in view.fields(model) if not f.read_only}
    operators = {a.operator for a in view.actions(model)}
    if target.kind in r.SHEET_KINDS:
        return ('part', 'grain') in fields and 'caffmob.grain_calibrate' in operators
    if target.kind == r.CLADDING:
        return ('cladding', 'grain_angle') in fields
    if not target.finish_roles:             # sem papéis, o veio das frentes espera o assistente (RF-042)
        return 'caffmob.finish_classify' in operators
    return ('finish_draft', 'grain') in fields


def mat01(target):
    from caffmob_draw.customize import finish
    from caffmob_draw.texture_library import apply
    obj = snapshot.object_for(bpy.context, target.uid)
    sections = {s.id for s in view.build(target, view.COMPLETE).sections}
    if obj is None or 'finish' not in sections:
        return False
    owner = finish.owner_of(obj)
    # O soltar acha peças que recebem a textura (no autoral, os membros; sem papéis, o assistente decide).
    return owner is not None and bool(apply.targets(obj) or finish.pieces_of(owner))


def mat02(target):
    from caffmob_draw.target import adapters
    section = next((s for s in view.build(target, view.COMPLETE).sections if s.id == 'finish'), None)
    if section is None or not target.edgeband_state:
        return False
    state, missing = target.edgeband_state
    labels = {i.label for i in section.items if isinstance(i, view.Action) and i.operator == 'caffmob.edgeband_apply'}
    ok = labels == {adapters.EDGEBAND_LABELS[state]}
    if state == 'MIXED':
        ok &= any(isinstance(i, view.Note) and str(missing) in i.args for i in section.items)
    return ok


def ux05(target):
    model = view.build(target, view.COMPLETE)
    fields = {(f.data, f.prop) for f in view.fields(model) if not f.read_only}
    operators = {a.operator for a in view.actions(model)}
    if target.kind == r.LEAF:
        return ('aggregate', 'open_value') in fields
    if target.kind == r.FRONT:
        return ('front_cabinet', 'door_open') in fields or 'caffmob.fronts_set_open' in operators
    if target.kind == r.MODULE:
        return 'caffmob.fronts_set_open' in operators or 'caffmob.mechanism_set' in operators
    if target.kind == r.OPENING:
        sections = {s.id for s in model.sections}
        return 'opening' in sections
    return False


CHECKS = {'UX-05': ux05, 'MAT-02': mat02, 'UX-01': ux01, 'UX-02': ux02, 'UX-04': ux04, 'MAT-03': mat03, 'CMP-01': cmp01, 'UX-03': ux03,
          'MAT-01': mat01}


def build_targets():
    s = fx.scene_15()
    bpy.context.scene.btm_component_select = False
    _documento, mobi = fx.ambiente_mobi_sintetico()          # onda 8 (T187): parede e porta do MOBI
    out = {}
    for row in DATA['linha_de_base_1_8_0']:
        name = TYPE_OBJECTS.get(row, row)
        if row in ('wall_mobi', 'opening_mobi'):
            fx.select([mobi['parede' if row == 'wall_mobi' else 'portao']])
        elif row == 'multiple':
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
