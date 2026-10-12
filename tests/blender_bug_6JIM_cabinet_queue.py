"""Reprodução e regressão do lote da fila do editor de armário: BUG-20261011-6JIM, BUG-20261011-N2D4 e
BUG-20261011-E33D.

Run: blender --background --factory-startup --python-exit-code 1 --python tests/blender_bug_6JIM_cabinet_queue.py

- a Montagem entra no rascunho: o Cancelar a desfaz (questions.md, pergunta 42);
- o OK roda a fila antes de fechar e o Cancelar a descarta (pergunta 43);
- o erro definido pela ação continua visível (pergunta 85).
"""

import sys
import traceback
import types
from pathlib import Path

import bpy

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _blender_env  # noqa: E402,F401
from caffmob_draw.cabinet_editor import ops_editor, panels_structure, props, window  # noqa: E402

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
    assert bpy.ops.caffmob.cabinet_builder(width=0.6) == {'FINISHED'}
    root = ctx.object
    return root, ops_editor.start_session(ctx, root)


class Layout:
    def __init__(self, record):
        self.record = record

    def _child(self, *args, **kwargs):
        return Layout(self.record)

    row = column = box = _child

    def prop(self, data, name, **kwargs):
        self.record.append(('prop', name))

    def operator(self, idname, **kwargs):
        self.record.append(('operator', idname))
        return types.SimpleNamespace()

    def label(self, *args, **kwargs):
        pass


def assembly_in_draft():
    root, s = module()
    record = []
    panels_structure.draw_assembly(Layout(record), ctx)
    check("6JIM: o painel não grava a Montagem direto", ('prop', 'assembly') not in record
          and ('operator', 'caffmob.cabinet_editor_assembly') in record, str(record))
    before = root.btm_cabinet.assembly
    other = 'BASE' if before == 'LATERAL' else 'LATERAL'
    s.push('edit', ('SET_ASSEMBLY', {'assembly': other}))
    ops_editor.process(ctx, s)
    changed = root.btm_cabinet.assembly
    ops_editor.rollback(ctx, s)
    check("6JIM: Cancelar desfaz a Montagem", changed == other and root.btm_cabinet.assembly == before,
          f"{before} → {changed} → {root.btm_cabinet.assembly}")
    props.end()


def modal_queue():
    original = window.window_alive
    window.window_alive = lambda context: True
    try:
        for request in ('ok', 'cancel'):
            root, s = module()
            width = root.btm_cabinet.width
            s.push('dimension', ('width', width + 0.1))
            s.request = request
            ended = []
            fake = types.SimpleNamespace(_end=lambda c, keep: ended.append(keep), report=lambda *a: None)
            ops_editor.BTM_OT_CabinetEditorModal.modal(fake, ctx, types.SimpleNamespace(type='TIMER', value='NOTHING'))
            if request == 'ok':
                check("N2D4: o OK roda a fila antes de fechar", ended == [True]
                      and abs(root.btm_cabinet.width - (width + 0.1)) < 1e-6,
                      f"largura {width:.3f} → {root.btm_cabinet.width:.3f}")
            else:
                check("N2D4: o Cancelar descarta a fila", ended == [False] and not s.requests, str(s.requests))
            props.end()
    finally:
        window.window_alive = original


def action_error_kept():
    _root, s = module()
    s.selected = None
    s.push('arrow', ('X', +1))
    ops_editor.process(ctx, s)
    check("E33D: o erro da ação continua visível", "divisória" in (s.error or ""), repr(s.error))
    props.end()


for step in (assembly_in_draft, modal_queue, action_error_kept):
    try:
        step()
    except Exception:
        traceback.print_exc()
        FAILURES.append(f"exceção em {step.__name__}")
props.end()
print(f"blender_bug_6JIM_cabinet_queue: {'OK' if not FAILURES else 'FALHAS: ' + ', '.join(FAILURES)}")
sys.exit(1 if FAILURES else 0)
