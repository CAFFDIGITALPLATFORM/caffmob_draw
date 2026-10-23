"""Reprodução e regressão de BUG-20261023-TU4V (#149): atualização comum não percorre o arquivo inteiro.

Run: blender --background --factory-startup --python-exit-code 1 --python tests/blender_bug_TU4V_handlers_sem_varredura.py
"""

import sys
import traceback
from pathlib import Path

import bpy

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _blender_env as env  # noqa: E402
import _encostar_fixture as fx  # noqa: E402
from caffmob_draw import identity_migration  # noqa: E402
from caffmob_draw.collision import guard  # noqa: E402

FAILURES = []
ctx = bpy.context


def check(name, ok, detail=""):
    print(("OK   " if ok else "FALHA ") + name, detail, flush=True)
    if not ok:
        FAILURES.append(name)


try:
    env.clean_scene()
    cube = fx.cube("Cubo", (0.5, 0.5, 0.5), (0.0, 0.0, 0.25))
    fx.settle()
    maps, migrations = [0], [0]
    real_map, real_migrate = guard._children_map, identity_migration.migrate_authored

    def count_map():
        maps[0] += 1
        return real_map()

    def count_migrate():
        migrations[0] += 1
        return real_migrate()
    guard._children_map = count_map
    identity_migration.migrate_authored = count_migrate
    try:
        ctx.scene.render.resolution_x += 1             # atualização sem objeto nem geometria
        fx.settle()
        check("reprodução: atualização sem objeto não monta o mapa de filhos", maps[0] == 0, maps[0])
        cube.location.x += 0.1                          # mexer num objeto: sem objeto novo
        fx.settle()
        check("reprodução: mover um objeto não roda a migração do arquivo", migrations[0] == 0, migrations[0])
        bpy.ops.object.duplicate()                      # objeto novo: a migração roda
        fx.settle()
        check("regressão: duplicar roda a migração (uid renovado)", migrations[0] >= 1, migrations[0])
    finally:
        guard._children_map = real_map
        identity_migration.migrate_authored = real_migrate
except Exception:
    traceback.print_exc()
    FAILURES.append("exceção")

print("RESULTADO:", "FALHAS " + ", ".join(FAILURES) if FAILURES else "OK", flush=True)
sys.exit(1 if FAILURES else 0)
