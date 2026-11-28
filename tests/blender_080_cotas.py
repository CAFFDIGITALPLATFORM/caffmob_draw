"""Confirmação de cota fixa pelo registro mostrado (feature 080, T023; CA-08 a CA-10, CA-13).

Run: blender --background --factory-startup --python-exit-code 1 --python tests/blender_080_cotas.py

Cena: o item entre dois armários, uma prateleira acima e o piso abaixo (como no ensaio do HYCE). Para cada mudança feita
depois de a cota ser lida (referência movida, girada, escalada, com a caixa alterada, apagada e recriada com o mesmo
nome; alvo girado; altura do teto alterada), confirmar recusa no popup e no campo e nada se move. Renomear a referência
não invalida. Sem mudança, 900 → 920 mm move o item 20 mm, sem redimensionar. O campo de leitura não calcula nada.
"""

import os
import sys
import tempfile
import traceback
from pathlib import Path

_TMP = tempfile.TemporaryDirectory(prefix="caffmob_080_cotas_")
os.environ.setdefault("CAFFMOB_DRAW_STANDARDS_DB", os.path.join(_TMP.name, "padroes.sqlite3"))

import bpy  # noqa: E402
from mathutils import Vector  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _blender_env as env  # noqa: E402
import _encostar_fixture as fx  # noqa: E402
from caffmob_draw.overlays import side_cotas  # noqa: E402
from caffmob_draw.ui import object_properties as op  # noqa: E402

CTX = bpy.context
FAILS = []
FIELD = {'LEFT': 'cota_esquerda', 'RIGHT': 'cota_direita', 'TOP': 'cota_superior', 'BOTTOM': 'cota_inferior'}


def check(cond, msg):
    print(("OK    " if cond else "FALHA ") + msg, flush=True)
    if not cond:
        FAILS.append(msg)


def near(a, b, tol=1e-5):
    return abs(a - b) <= tol


def scene(shelf=True):
    env.clean_scene()
    fx.cube("Armário esquerdo", (0.6, 0.6, 0.8), (-1.0, 0.0, 0.5))
    fx.cube("Armário direito", (0.6, 0.6, 0.8), (2.0, 0.0, 0.5))
    if shelf:
        fx.cube("Prateleira", (0.6, 0.6, 0.2), (0.5, 0.0, 2.0))
    item = fx.cube("Item", (0.6, 0.6, 0.8), (0.5, 0.0, 0.5))      # x 0,2..0,8; esquerda 0,9; direita 0,9
    for obj in CTX.scene.objects:
        obj.select_set(obj == item)
    CTX.view_layer.objects.active = item
    CTX.scene.home_builder.ceiling_height = 2.6
    fx.settle()
    side_cotas.records(CTX)            # o timer calcularia: é o que a tela mostra
    return item


def clear_error():
    wm = CTX.window_manager
    if op.ERROR_KEY in wm:
        del wm[op.ERROR_KEY]


def via_field(side, value):
    clear_error()
    setattr(CTX.scene.btm_selection, FIELD[side], value)
    return CTX.window_manager.get(op.ERROR_KEY)


def reason(side, shown):
    """O motivo que o popup reporta (o `report` não é legível em background)."""
    try:
        token = shown.get('token')
        pose = tuple(token.matrix[i * 4 + 3] for i in range(3))
        side_cotas.check_unchanged(CTX, token.uid, pose, shown, side)
    except ValueError as exc:
        return str(exc)
    return None


def via_popup(side, value, shown, item):
    side_cotas._popup[0] = shown
    result = bpy.ops.caffmob.fixed_cota_edit('EXEC_DEFAULT', side=side, value=value, mover_uid=item.session_uid,
                                             pose=tuple(item.matrix_world.translation))
    return None if result == {'FINISHED'} else "CANCELLED"


def refused_both(label, side, change, shelf=True):
    """A mudança `change(item)` depois da leitura: o popup e o campo recusam, e o item não sai do lugar."""
    for path in ('popup', 'campo'):
        item = scene(shelf)
        shown = side_cotas.shown(CTX)
        value = shown['gaps'][side][0].value + 0.02
        change(item)
        fx.settle()
        before = item.matrix_world.copy()
        error = (via_popup(side, value, shown, item) and reason(side, shown)) if path == 'popup' \
            else via_field(side, value)
        moved = max(abs(before[r][c] - item.matrix_world[r][c]) for r in range(4) for c in range(4))
        check(error is not None and moved < 1e-9, f"{label}: recusado no {path}, nada se move ({error})")


def _ref(name):
    return bpy.data.objects[name]


def move_ref(_item):
    _ref("Armário esquerdo").location.x -= 0.05


def rotate_ref(_item):
    _ref("Armário esquerdo").rotation_euler.z += 0.02


def scale_ref(_item):
    _ref("Armário esquerdo").scale.x = 1.1


def resize_ref(_item):
    data = _ref("Armário esquerdo").data
    for vertex in data.vertices:
        vertex.co.x *= 1.1
    data.update()


def recreate_ref(item):
    old = _ref("Armário esquerdo")
    name = old.name
    bpy.data.objects.remove(old, do_unlink=True)
    fx.cube(name, (0.6, 0.6, 0.8), (-1.0, 0.0, 0.5))
    for obj in CTX.scene.objects:                      # a seleção volta ao item: só a referência mudou
        obj.select_set(obj == item)
    CTX.view_layer.objects.active = item


def rotate_target(item):
    item.rotation_euler.z += 0.02


def raise_ceiling(_item):
    CTX.scene.home_builder.ceiling_height = 2.7


def main():
    # Sem mudança: o campo move pela diferença do registro mostrado, sem redimensionar.
    item = scene()
    size = tuple(item.dimensions)
    check(via_field('LEFT', 0.92) is None, "campo: 900 → 920 mm aceito")
    fx.settle()
    check(near(item.location.x, 0.52) and tuple(item.dimensions) == size,
          f"campo: o item andou 20 mm sem redimensionar (x = {item.location.x:.4f})")
    check(near(side_cotas.records(CTX, compute=False)['LEFT'][0], 0.92), "depois de mover, a tela já mostra 920 mm")
    check(via_field('LEFT', 0.95) is None, "a edição seguinte confere contra a pose nova")

    item = scene()
    shown = side_cotas.shown(CTX)
    check(via_popup('RIGHT', 0.92, shown, item) is None and near(item.location.x, 0.48),
          f"popup: 900 → 920 mm à direita move 20 mm (x = {item.location.x:.4f})")

    refused_both("referência movida", 'LEFT', move_ref)
    refused_both("referência girada", 'LEFT', rotate_ref)
    refused_both("referência escalada", 'LEFT', scale_ref)
    refused_both("referência com a caixa alterada", 'LEFT', resize_ref)
    refused_both("referência apagada e recriada com o mesmo nome", 'LEFT', recreate_ref)
    refused_both("alvo girado", 'LEFT', rotate_target)
    refused_both("altura do teto alterada", 'TOP', raise_ceiling, shelf=False)

    # Só renomear a referência não invalida.
    for path in ('popup', 'campo'):
        item = scene()
        shown = side_cotas.shown(CTX)
        _ref("Armário esquerdo").name = "Armário renomeado"
        fx.settle()
        error = via_popup('LEFT', 0.92, shown, item) if path == 'popup' else via_field('LEFT', 0.92)
        check(error is None and near(item.location.x, 0.52), f"renomear a referência: aceito no {path} ({error})")

    # O campo de leitura não calcula: com o cálculo proibido, ler devolve o registro mostrado sem avaliar.
    item = scene()
    original = side_cotas._compute

    def forbidden(*_args, **_kwargs):
        raise AssertionError("o leitor avaliou a cena")
    side_cotas._compute = forbidden
    try:
        value = CTX.scene.btm_selection.cota_esquerda
        check(near(value, 0.9), f"o campo lê o registro mostrado sem avaliar ({value:.4f})")
    except AssertionError as exc:
        check(False, str(exc))
    finally:
        side_cotas._compute = original

    # Abrir um arquivo não restaura driver nos campos virtuais (a quarentena da GAVK continua).
    path = os.path.join(_TMP.name, "080_cotas.blend")
    bpy.ops.wm.save_as_mainfile(filepath=path, copy=True)
    bpy.ops.wm.open_mainfile(filepath=path)
    anim = bpy.context.scene.animation_data
    drivers = [fc.data_path for fc in anim.drivers] if anim is not None else []
    check(not any(p.startswith('btm_selection.') for p in drivers), "reabrir não restaura driver nos campos")


try:
    main()
except Exception:
    traceback.print_exc()
    FAILS.append("o ensaio levantou")
if FAILS:
    print(f"blender_080_cotas: {len(FAILS)} falha(s)")
    for item_ in FAILS:
        print("  - " + item_)
    sys.exit(1)
print("blender_080_cotas: OK")
