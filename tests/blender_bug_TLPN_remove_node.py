"""Reprodução e regressão do lote do editor de paredes: BUG-20261011-TLPN e BUG-20261011-GKUE.

Run: blender --background --factory-startup --python-exit-code 1 --python tests/blender_bug_TLPN_remove_node.py

- Remover Vértice registra o `source` do trecho eliminado em `removed_sources` (questions.md, pergunta 1): depois do
  OK, a parede antiga sai da cena em vez de ficar órfã e sobreposta ao trecho novo (EC-01).
- Delete numa cadeia fechada limpa a seleção, para um segundo Delete não remover outra parede (EC-02).
"""

import sys
import traceback
import types
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _blender_env as env  # noqa: E402
import bpy  # noqa: E402
from caffmob_draw.walls2d import apply, model, ops_editor, scene_io  # noqa: E402

ctx = bpy.context
FAILURES = []


def check(name, ok, detail=""):
    print(("OK   " if ok else "FALHA ") + name, detail, flush=True)
    if not ok:
        FAILURES.append(name)


def walls():
    return sorted(o.name for o in ctx.scene.objects if o.get('IS_WALL_BP'))


def room():
    env.clean_scene()
    apply.apply_plan(ctx, model.WallPlan([model.rectangle(4.0, 3.0)]))
    env.settle()
    return types.SimpleNamespace(plan=scene_io.read_plan(ctx.scene), selected=(0, 1), error="")


def remove_vertex():
    s = room()
    before = walls()
    chain = s.plan.chains[0]
    kept = chain.segments[1].source
    try:
        ops_editor.remove_node(s, 0, 2)          # o nó entre os trechos 1 e 2: o trecho 2 deixa de existir
    except AttributeError:
        chain.remove_node(2)                     # caminho antigo da ferramenta, sem registrar o source
    check("TLPN: o trecho eliminado vai para removed_sources", len(s.plan.removed_sources) == 1,
          str(s.plan.removed_sources))
    apply.apply_plan(ctx, s.plan)
    env.settle()
    after = walls()
    check("TLPN: depois do OK a cena tem uma parede a menos (sem órfã)", len(after) == len(before) - 1,
          f"{len(before)} → {len(after)}: {after}")
    check("TLPN: a parede do trecho que continua fica", kept in after, kept)
    check("TLPN: o rascunho lido de novo bate com a cena", len(scene_io.read_plan(ctx.scene).chains[0].segments) == 3)


def delete_closed():
    s = room()
    ops_editor.remove_segment(s, 0, 1)
    check("GKUE: Delete numa cadeia fechada limpa a seleção", s.selected is None, str(s.selected))


try:
    remove_vertex()
    delete_closed()
except Exception:
    traceback.print_exc()
    FAILURES.append("exceção no roteiro")
print(f"blender_bug_TLPN_remove_node: {'OK' if not FAILURES else 'FALHAS: ' + ', '.join(FAILURES)}")
sys.exit(1 if FAILURES else 0)
