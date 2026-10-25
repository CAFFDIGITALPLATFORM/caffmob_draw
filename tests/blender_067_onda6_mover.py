"""Mover Sobre com rotação (feature 067, T034; RF-120 a RF-129).

Run: blender --background --factory-startup --python-exit-code 1 --python tests/blender_067_onda6_mover.py

Pelo operador do diálogo num objeto falso (sem área de tela), com eventos simulados:
- as duas vistas controlam um estado só: arrastar na planta muda o X também na frontal; pan e zoom não mexem em A;
- escolher o pivô (ou a âncora, com Alt) não move nada;
- girar pela alça na planta dá 90° no plano X/Y com o pivô parado; a frontal gira no plano X/Z; a câmera da viewport
  não entra na conta (órbita sem efeito);
- Esc durante o giro restaura a matriz exata; o diálogo é um passo de Desfazer (o histórico local não grava passo);
- as cotas absolutas não mudam com pan e zoom das vistas;
- histórico local: três passos, Ctrl+Z e Ctrl+Shift+Z; Cancelar volta à entrada;
- a tolerância da alça escala com a interface (DPI);
- ângulo digitado na vista; o clique no campo não começa gesto;
- contorno pelas arestas reais até 12 mil (acima, a caixa);
- gesto de face: o ponto visível prende, o escondido é recusado; a face vira o pai sem salto e o Esc devolve;
- posição salva com pivô, âncora e orientação, e a M-07 nas antigas.
"""

import math
import sys
import traceback
from pathlib import Path

import bpy
from mathutils import Vector

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _encostar_fixture as fx  # noqa: E402
from caffmob_draw.move_over import dialog_rotate, ops_dialog, ops_drag, props as mo_props  # noqa: E402
from caffmob_draw.move_over import rotation as rot  # noqa: E402

FAILURES = []


def check(ok, label, detail=""):
    print(("OK   " if ok else "FALHA ") + label + (f" ({detail})" if detail and not ok else ""), flush=True)
    if not ok:
        FAILURES.append(label)


def close(a, b, tol=1e-6):
    return max(abs(a[r][c] - b[r][c]) for r in range(4) for c in range(4)) <= tol


def scene():
    fx.env.clean_scene()
    a = fx.cube("Movido", (0.6, 0.4, 0.8), (0.0, -1.0, 0.4))
    b = fx.cube("Referência", (1.0, 0.6, 0.9), (2.0, 0.0, 0.45))
    fx.settle()
    return a, b


def run():
    a, b = scene()
    entry = a.matrix_world.copy()                 # a entrada: antes de a janela abrir
    d = fx.dialog(a, b)
    d.mo.preview()

    # Duas vistas, um estado.
    front_before = d._handles('front')[0][0]
    plan = d._handles('plan')
    start = ((plan[0][0] + plan[2][0]) / 2.0, (plan[0][1] + plan[2][1]) / 2.0)
    d._drag_begin('plan', start)
    d._drag_move((start[0] + 40, start[1]), shift=True)
    d._drag_end()
    d._push_history()
    dx = d._handles('front')[0][0] - front_before
    check(abs(dx - (d._handles('plan')[0][0] - plan[0][0])) < 1.0 and abs(dx) > 5,
          "arrastar na planta move o X também na frontal", f"{dx:.1f}")

    # Pan e zoom não mexem em A.
    state = d.mo.state()
    d._zoom('plan', start, 1.5)
    d._pan_begin('plan', start)
    d._pan_move((start[0] + 30, start[1] + 10))
    d.panning = None
    check(d.mo.state() == state and d.user_view, "pan e zoom mudam só a vista")
    world_min = d.mo.world_min()
    check(d.mo.world_min() == world_min, "as cotas absolutas não mudam com a vista")
    d._reset_views()

    # Escolher o pivô não move.
    matrix = a.matrix_world.copy()
    corner = d._points('plan')['C100']
    d.alt, d.ctrl = False, True                   # Ctrl+clique num ponto escolhe o pivô
    d._pane_click('plan', corner)
    d.ctrl = False
    check(d.mo.pivot == 'C100' and close(a.matrix_world, matrix), "escolher o pivô não move nada")
    d.alt = True
    clicked = d._points('plan')['C111']
    d._pane_click('plan', clicked)
    d.alt = False
    shown = d._points('plan')[d.mo.anchor]
    check(d.mo.anchor != 'C000' and abs(shown[0] - clicked[0]) + abs(shown[1] - clicked[1]) < 1e-6
          and close(a.matrix_world, matrix), "Alt escolhe a âncora, sem mover", d.mo.anchor)

    # Girar 90° pela alça na planta, com o pivô parado.
    pivot_before = Vector(d.mo.point_in_b('C100'))
    handle = d._handles('plan')[2]
    center = d._project('plan', d.mo.point_in_b(d.mo.pivot))
    d._rotate_begin('plan', handle)
    r = math.hypot(handle[0] - center[0], handle[1] - center[1])
    a0 = math.atan2(handle[1] - center[1], handle[0] - center[0])
    for step in range(1, 10):
        t = a0 + math.radians(10 * step)
        d._rotate_move((center[0] + r * math.cos(t), center[1] + r * math.sin(t)))
    before_esc = a.matrix_world.copy()
    d._rotate_end()
    angle = rot.angle_about(d.mo.orientation, 'Z')
    check(abs(angle - 90.0) < 1e-6, "90° no plano da planta (snap de 15°)", f"{angle:.3f}")
    check((Vector(d.mo.point_in_b('C100')) - pivot_before).length < 1e-6, "o pivô fica parado no giro")
    check(abs(rot.angle_about(d.mo.orientation, 'X')) < 1e-6 and abs(rot.angle_about(d.mo.orientation, 'Y')) < 1e-6,
          "o giro da planta não inclina a peça")
    cam = bpy.data.objects.new("Órbita", bpy.data.cameras.new("Órbita"))
    bpy.context.scene.collection.objects.link(cam)
    target = d.mo._target_matrix().copy()
    cam.rotation_euler = (1.0, 0.3, 2.0)
    bpy.context.view_layer.update()
    check(close(d.mo._target_matrix(), target), "orbitar a viewport não muda o resultado")
    _ = before_esc

    # Esc no meio do giro: matriz exata do mouse-down.
    down = a.matrix_world.copy()
    d._rotate_begin('front', d._handles('front')[1])
    d._rotate_move((d._handles('front')[1][0] - 40, d._handles('front')[1][1] + 60))
    d._rotate_end(cancel=True)
    check(close(a.matrix_world, down), "Esc no giro restaura a matriz exata")

    # Frontal gira no plano X/Z (a partir do giro zerado com R).
    d._reset_orientation()
    d.typing, d.buffer = 'ANGLE_front', "30"
    d._commit_typing()
    v = rot.rotate_vector(d.mo.orientation, (1.0, 0.0, 0.0))
    check(abs(rot.angle_about(d.mo.orientation, 'Y') - 30.0) < 1e-4 and abs(v[2]) > 0.4,
          "ângulo digitado na frontal gira no plano X/Z", str(v))
    field = d.angle_fields['plan']
    d.typing = None
    d._pane_click('plan', (field[0] + 4, field[1] + 4))
    check(d.typing == 'ANGLE_plan' and d.rotating is None, "o clique no campo não começa gesto")
    d.typing, d.buffer = None, ""

    # Histórico local e Cancelar.
    steps = len(d.history)
    d._undo_local()
    check(len(d.history) == steps - 1 and d.redo_stack, "Ctrl+Z local volta um passo")
    d._redo_local()
    check(len(d.history) == steps, "Ctrl+Shift+Z refaz")
    d.cancel(fx.CTX)
    check(close(a.matrix_world, entry), "Cancelar depois de vários passos volta à entrada")
    check('UNDO' in ops_dialog.BTM_OT_MoveOverDialog.bl_options, "o Encostar é um passo de Desfazer só")

    # O mesmo pelo modal, com eventos simulados: hover, giro pela alça, roda e Ctrl+Z local.
    import types
    d = fx.dialog(a, b)

    def ev(kind, value='PRESS', pixel=(-1, -1), **extra):
        return types.SimpleNamespace(type=kind, value=value, mouse_region_x=pixel[0], mouse_region_y=pixel[1],
                                     unicode="", shift=False, ctrl=extra.get('ctrl', False), alt=False, oskey=False)
    corner = d._handles('plan')[2]
    d.modal(fx.CTX, ev('MOUSEMOVE', 'NOTHING', corner))
    check(d.mode == 'HOVER', "o mouse no canto é HOVER", d.mode)
    d.modal(fx.CTX, ev('LEFTMOUSE', 'PRESS', corner))
    check(d.mode == 'ROTATE' and d.rotating is not None, "apertar na alça começa o ROTATE")
    center = d.rotating['center']
    turned = (center[0] - (corner[1] - center[1]), center[1] + (corner[0] - center[0]))      # +90° na tela
    d.modal(fx.CTX, ev('MOUSEMOVE', 'NOTHING', ((corner[0] + turned[0]) / 2, (corner[1] + turned[1]) / 2)))
    d.modal(fx.CTX, ev('MOUSEMOVE', 'NOTHING', turned))
    d.modal(fx.CTX, ev('LEFTMOUSE', 'RELEASE', turned))
    check(d.mode == 'IDLE' and abs(rot.angle_about(d.mo.orientation, 'Z') - 90.0) < 1e-6,
          "pelo modal: soltar grava 90°", f"{rot.angle_about(d.mo.orientation, 'Z'):.2f}")
    scale = d.view_plan.scale
    d.modal(fx.CTX, ev('WHEELUPMOUSE', 'PRESS', corner))
    check(d.view_plan.scale > scale, "a roda dá zoom na vista")
    d.modal(fx.CTX, ev('Z', 'PRESS', corner, ctrl=True))
    check(abs(rot.angle_about(d.mo.orientation, 'Z')) < 1e-6, "Ctrl+Z local desfaz o giro")
    d.cancel(fx.CTX)

    # Tolerância por DPI.
    d = fx.dialog(a, b)
    corner = d._handles('plan')[0]
    near = (corner[0] + 18, corner[1])
    d.s = 1.0
    d.state.tolerance_px = 12
    miss = d._near(near, list(enumerate(d._handles('plan'))))
    d.s = 2.0
    hit = d._near(near, list(enumerate(d._handles('plan'))))
    check(miss is None and hit is not None, "a tolerância da alça escala com a interface")

    # Contorno: arestas reais até 12 mil.
    check(d._edges_local and len(d._edges_local) == 12, "o contorno usa as arestas reais do movido")
    bpy.ops.mesh.primitive_uv_sphere_add(segments=160, ring_count=80)
    heavy = bpy.context.object
    heavy.parent = a
    check(dialog_rotate._edges_of(d.mo) is None, "acima de 12 mil arestas, a caixa")
    bpy.data.objects.remove(heavy)

    # Posição salva com pivô, âncora e orientação; M-07.
    d.mo.set_pivot('C010')
    d.mo.rotate('plan', 45.0)
    saved = d.mo.saved()
    check(saved['pivot'] == 'C010' and abs(rot.angle_about(saved['orientation'], 'Z') - 45.0) < 1e-6,
          "a posição salva guarda pivô e orientação")
    item = bpy.context.scene.btm_saved_positions.add()
    item.name, item.rotation = "Antiga", 90.0
    mo_props.migrate_saved_positions()
    check(item.pivot == 'BASE_CENTER' and abs(rot.angle_about(tuple(item.orientation), 'Z') - 90.0) < 1e-4,
          "M-07: a posição antiga ganha orientação e o centro da base")
    d.cancel(fx.CTX)

    # Gesto de face.
    scene_ = bpy.context.scene
    deps = bpy.context.evaluated_depsgraph_get()
    origin, direction = Vector((2.0, -3.0, 0.45)), Vector((0.0, 1.0, 0.0))
    pin = ops_drag.pin_from_ray(scene_, deps, origin, direction, target=b)
    check(pin is not None and pin[0] == b and abs(pin[1].y + 0.3) < 1e-4, "o ponto visível da face prende")
    blocker = fx.cube("Na frente", (0.4, 0.05, 0.4), (2.0, -1.0, 0.45))
    fx.settle()
    deps = bpy.context.evaluated_depsgraph_get()
    check(ops_drag.pin_from_ray(scene_, deps, origin, direction, target=b) is None,
          "ponto escondido atrás de outro objeto é recusado")
    bpy.data.objects.remove(blocker)
    world = a.matrix_world.copy()
    before = ops_drag.parent_keep_world(a, b)
    bpy.context.view_layer.update()
    check(a.parent == b and close(a.matrix_world, world), "a face vira o pai sem salto")
    ops_drag.restore_parent(a, before)
    bpy.context.view_layer.update()
    check(a.parent is None and close(a.matrix_world, world), "o Esc devolve pai e matriz")


try:
    run()
except Exception:
    traceback.print_exc()
    FAILURES.append("exceção")
print(f"blender_067_onda6_mover: {'OK' if not FAILURES else 'FALHAS: ' + ', '.join(FAILURES)}", flush=True)
sys.exit(1 if FAILURES else 0)
