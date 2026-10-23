"""Ensaio do padrão de "Impedir atravessamento" (feature 066, T011; RF-009, D-06).

Run: blender --background --factory-startup --python-exit-code 1 --python tests/blender_066_block_default.py

- projeto novo: ligado; `property_unset` volta ao padrão ligado;
- arquivo que nunca gravou a propriedade (como um .blend do 1.2.0) abre ligado, mesmo com o antigo "Evitar
  Sobreposição" (`collision_global`) gravado desligado; o guarda não lê mais essa chave;
- desligado de propósito, a escolha é salva, e a edição fica livre;
- as medidas laterais nascem desligadas e não mudam com a colisão (RF-013).
"""

import os
import sys
import tempfile
import traceback
from pathlib import Path

import bpy

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _blender_env as env  # noqa: E402
from caffmob_draw.collision import guard as _guard  # noqa: E402
# Estes cenários movem por código no lugar do G: o guarda só limita G e gizmo (BUG-20261023-TAMR, RF01).
_guard._direct_move_running = lambda: True

FAILURES = []
FOLDER = tempfile.mkdtemp(prefix="caffmob_066_")


def check(name, ok, detail=""):
    print(("OK   " if ok else "FALHA ") + name, detail, flush=True)
    if not ok:
        FAILURES.append(name)


def settings():
    return bpy.context.scene.btm_settings


def reopen(name):
    path = os.path.join(FOLDER, name)
    bpy.ops.wm.save_as_mainfile(filepath=path)
    bpy.ops.wm.open_mainfile(filepath=path)
    return settings()


def push_against_plate():
    """Cubo de 1 m levado 2 m em X contra uma chapa de 15 mm em x = 1,0; devolve o x final."""
    env.clean_scene()
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0.0, 0.0, 0.0))
    mover = bpy.context.object
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(1.0075, 0.0, 0.0))
    bpy.context.object.scale = (0.015, 2.0, 2.0)
    env.settle()
    mover.location.x = 2.0
    env.settle()
    return mover.location.x


def defaults():
    s = settings()
    check("RF-009: projeto novo abre com Impedir atravessamento ligado", s.block_penetration is True)
    check("RF-013: medidas laterais nascem desligadas", s.show_side_dimensions is False)
    s.block_penetration = False
    s.property_unset('block_penetration')
    check("D-06: property_unset volta ao padrão ligado", s.block_penetration is True)


def old_file():
    s = settings()
    s.property_unset('block_penetration')
    s.collision_global = False                      # projeto antigo com "Evitar Sobreposição" desligado
    s = reopen("antigo.blend")
    check("RF-009: arquivo sem a propriedade gravada abre ligado", s.block_penetration is True
          and not s.is_property_set('block_penetration'), f"valor={s.block_penetration}")
    check("D-06: collision_global continua registrada e lida do arquivo", s.collision_global is False)
    x = push_against_plate()
    check("D-06: o guarda bloqueia com collision_global desligada", abs(x - 0.5) < 1e-4, f"x={x:.4f}")


def turned_off():
    s = settings()
    s.block_penetration = False
    s = reopen("desligado.blend")
    check("RF-009: desligado de propósito continua desligado ao reabrir", s.block_penetration is False)
    side = s.show_side_dimensions
    x = push_against_plate()
    check("RF-009: desligado, a edição fica livre", abs(x - 2.0) < 1e-6, f"x={x:.4f}")
    check("RF-013: desligar a colisão não mexe nas medidas laterais", settings().show_side_dimensions == side)
    settings().show_side_dimensions = True
    check("RF-013: ligar as medidas não liga a colisão", settings().block_penetration is False)
    settings().block_penetration = True


for step in (defaults, old_file, turned_off):
    try:
        step()
    except Exception:
        traceback.print_exc()
        FAILURES.append(f"exceção em {step.__name__}")
print(f"blender_066_block_default: {'OK' if not FAILURES else 'FALHAS: ' + ', '.join(FAILURES)}")
sys.exit(1 if FAILURES else 0)
