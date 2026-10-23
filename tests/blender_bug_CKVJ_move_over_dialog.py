"""Reprodução e regressão do lote da janela Mover Sobre: BUG-20261011-CKVJ, BUG-20261011-JMDR e BUG-20261011-CNTL.

Run: blender --background --factory-startup --python-exit-code 1 --python tests/blender_bug_CKVJ_move_over_dialog.py

O modal é exercitado sem janela: um objeto falso recebe os métodos da classe e um MoveOver falso registra as chamadas.
- Tab grava e vai ao próximo campo; inválido fica no campo com o aviso (questions.md, pergunta 15);
- setas e Page Up/Down zeram o aviso da janela (pergunta 18); feature 066 (T014): não existe mais aviso de
  sobreposição nem segundo Confirmar; Confirmar grava a pose que o guarda permite (`guard.clamp`), mesmo confirmando
  duas vezes;
- rotação inválida mostra mensagem traduzida, não o erro do float() (move_over EC-08).
"""

import sys
import traceback
import types
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _blender_env  # noqa: E402,F401
from caffmob_draw.move_over import ops_dialog  # noqa: E402

FAILURES = []
CTX = types.SimpleNamespace(area=types.SimpleNamespace(tag_redraw=lambda: None))


def check(name, ok, detail=""):
    print(("OK   " if ok else "FALHA ") + name, detail, flush=True)
    if not ok:
        FAILURES.append(name)


def dialog():
    methods = {k: v for k, v in vars(ops_dialog.BTM_OT_MoveOverDialog).items() if callable(v)}
    fake = type('Dialog', (), methods)()
    calls = []
    fake.mo = types.SimpleNamespace(set_world=lambda *a: calls.append(('world',) + a),
                                    set_gap=lambda *a: calls.append(('gap',) + a),
                                    set_rotation=lambda *a: calls.append(('rot',) + a),
                                    nudge=lambda *a: calls.append(('nudge',) + a))
    fake.state = types.SimpleNamespace(step=0.01, show_relative=False, snap_on=True, glue=False)
    fake.side, fake.glue, fake.snap_on = None, False, True         # janela Encostar (BUG-20261022-RQR5)
    fake.panel = (0, 0, 0, 0)
    fake.typing, fake.buffer, fake.warning = None, "", ""
    fake._fit_views = lambda: None
    return fake, calls


def press(fake, kind, char=""):
    event = types.SimpleNamespace(type=kind, value='PRESS', unicode=char, mouse_region_x=-1, mouse_region_y=-1)
    return fake.modal(CTX, event)


def tab_moves_on():
    fake, calls = dialog()
    fake.typing, fake.buffer = 0, "0.5"
    press(fake, 'TAB')
    check("CKVJ: Tab com valor válido grava e vai ao próximo campo", fake.typing == 1 and calls
          and calls[0][0] == 'world', f"campo={fake.typing} chamadas={calls}")
    fake, calls = dialog()
    fake.typing, fake.buffer = 1, "abc"
    press(fake, 'TAB')
    check("CKVJ: Tab com valor inválido fica no campo com o aviso", fake.typing == 1 and fake.buffer == "abc"
          and bool(fake.warning), f"campo={fake.typing} texto={fake.buffer!r} aviso={fake.warning!r}")


def arrows_reset_warning():
    fake, _calls = dialog()
    fake.warning = "Posição 1 aplicada."
    press(fake, 'RIGHT_ARROW')
    check("JMDR: seta depois do aviso zera o aviso", fake.warning == "", f"aviso={fake.warning!r}")
    check("066: a janela não tem mais o estado do segundo Confirmar", not hasattr(fake, 'warned'))


def confirm_twice_never_overlaps():
    """RF-003: Mover Sobre com o destino sobreposto; confirmar duas vezes grava a última pose sem penetração."""
    import bpy
    from mathutils import Vector
    from caffmob_draw.collision import guard
    from caffmob_draw.move_over.scene import MoveOver
    ctx = bpy.context
    _blender_env.clean_scene()
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0.0, 0.0, 0.5))
    a = ctx.object
    a.name = "A"
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(3.0, 0.0, 0.5))
    b = ctx.object
    b.name = "B"
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(1.5, 0.0, 0.5))
    c = ctx.object
    c.name = "C"                       # entre A e o destino
    _blender_env.settle()
    for o in (a, b):                   # A e B viram "geometria" para o Mover Sobre reconhecê-los
        o.btm_plane.object_kind = 'GEOMETRY'
    fake, _calls = dialog()
    fake.mo = MoveOver(ctx, a, b)
    fake.report = lambda *args: None
    fake._finish = lambda context: None
    fake.mo.delta = fake.mo.b_frame_inv @ Vector((1.2, 0.0, 0.5)) - fake.mo.origin_in_b    # A em x = 1,2: dentro de C
    fake.typing = None
    with guard.suspended():            # como com a janela aberta: o modal posiciona e o guarda não corrige no meio
        fake.mo.preview()
        first = fake._confirm(ctx)
        second = fake._confirm(ctx)
    # BUG-20261023-TAMR (RF02): o Encostar é ferramenta assistida; o destino pedido vale, mesmo dentro de C.
    _blender_env.settle()
    x = a.matrix_world.translation.x
    check("RF02: confirmar grava o destino pedido", first == {'FINISHED'} and second == {'FINISHED'}
          and abs(x - 1.2) < 1e-4, f"{first} {second} x={x:.4f}")


def rotation_message():
    fake, _calls = dialog()
    fake.typing, fake.buffer = ops_dialog.ROTATION, "1.2.3"
    fake._commit_typing()
    check("CNTL: rotação inválida mostra mensagem traduzida", fake.warning.startswith("Valor Inválido")
          and "could not convert" not in fake.warning, repr(fake.warning))


for step in (tab_moves_on, arrows_reset_warning, rotation_message, confirm_twice_never_overlaps):
    try:
        step()
    except Exception:
        traceback.print_exc()
        FAILURES.append(f"exceção em {step.__name__}")
print(f"blender_bug_CKVJ_move_over_dialog: {'OK' if not FAILURES else 'FALHAS: ' + ', '.join(FAILURES)}")
sys.exit(1 if FAILURES else 0)
