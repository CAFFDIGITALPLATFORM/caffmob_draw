"""Reprodução e regressão do lote dos padrões (2ª rodada): BUG-20261011-MTPU, BUG-20261011-QO2H, BUG-20261011-64UD e
BUG-20261011-ZATR.

Run: blender --background --factory-startup --python-exit-code 1 --python tests/blender_bug_MTPU_standards.py

- falha inesperada na migração é registrada e não interrompe o load_file_post (standards EC-14);
- a 2ª pergunta de "Definir ativa" não reaplica os módulos que a 1ª já levou ao padrão novo (questions.md, 50);
- importar com substituição uma homônima que está antes da ativa não troca a ativa (standards EC-06);
- projeto só com armários face frame é reconhecido como legado e recebe o padrão EUA (pergunta 52).
"""

import os
import sys
import tempfile
import traceback
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _blender_env as env  # noqa: E402
import bpy  # noqa: E402
from caffmob_draw.standards import api, builtin, io_json, migration  # noqa: E402

ctx = bpy.context
FAILURES = []


def check(name, ok, detail=""):
    print(("OK   " if ok else "FALHA ") + name, detail, flush=True)
    if not ok:
        FAILURES.append(name)


def migration_failure():
    original = migration.migrate_scene

    def broken(scene):
        raise RuntimeError("falha simulada")
    migration.migrate_scene = broken
    try:
        try:
            result = migration.run(ctx.scene)
            check("MTPU: falha inesperada na migração não sobe para o load_file_post", result == [], str(result))
        except Exception as exc:
            check("MTPU: falha inesperada na migração não sobe para o load_file_post", False, repr(exc))
    finally:
        migration.migrate_scene = original


def balcao():
    assert bpy.ops.caffmob.cabinet_builder(cabinet_type='BASE', width=0.6, line='COZ') == {'FINISHED'}
    return ctx.view_layer.objects.active


def second_question():
    env.clean_scene()
    api.ensure_ready(ctx.scene)
    mods = [balcao() for _ in range(3)]
    own = mods[2]
    own.btm_cabinet.assembly = 'BASE'                      # padrão próprio: vai para a 2ª pergunta
    env.settle()
    previous = api.active_definition(ctx.scene)
    copy = api.duplicate_definition(ctx.scene, previous, name="Padrão 25")
    api.set_value(copy, "COZ.sheets.LAT.thickness", 25.0)
    api.set_active(ctx.scene, copy)
    assert bpy.ops.caffmob.standards_apply_scene('EXEC_DEFAULT', previous_uid=previous.uid) == {'FINISHED'}
    check("QO2H: a 1ª pergunta leva os que seguem ao padrão novo",
          all(m.get('btm_standard_uid') == copy.uid for m in mods[:2]))
    del mods[0]['btm_line']                                # marca: só uma nova aplicação regrava a linha
    assert bpy.ops.caffmob.standards_apply_differ('EXEC_DEFAULT', previous_uid=previous.uid) == {'FINISHED'}
    check("QO2H: a 2ª pergunta não reaplica os já aplicados na 1ª", 'btm_line' not in mods[0],
          str(mods[0].get('btm_line')))
    check("QO2H: a 2ª pergunta aplica o módulo de padrão próprio",
          abs(own.btm_cabinet.thickness - 0.025) < 1e-6 and own.get('btm_standard_uid') == copy.uid,
          f"{own.btm_cabinet.thickness:.4f}")


def replace_keeps_active():
    api.ensure_ready(ctx.scene)
    first = api.duplicate_definition(ctx.scene, api.active_definition(ctx.scene), name="Homônima ZATR")
    for name in ("Ativa ZATR", "Depois ZATR"):                         # a ativa não é a última da lista
        api.duplicate_definition(ctx.scene, api.find_definition(ctx.scene, name="Homônima ZATR"), name=name)
    api.set_active(ctx.scene, api.find_definition(ctx.scene, name="Ativa ZATR"))
    first = api.find_definition(ctx.scene, name="Homônima ZATR")     # add() pode realocar a coleção
    path = os.path.join(tempfile.mkdtemp(), "homonima.btmdim.json")
    io_json.export_definition(path, first)
    io_json.import_definition(ctx.scene, path, on_conflict='replace')
    active = api.active_definition(ctx.scene)
    check("ZATR: import com substituição mantém a ativa", active is not None and active.name == "Ativa ZATR",
          active.name if active is not None else "nenhuma")


def face_frame_is_legacy():
    env.clean_scene()
    data = api.standards(ctx.scene)
    data.definitions.clear()
    if migration.MIGRATED_FLAG in ctx.scene:
        del ctx.scene[migration.MIGRATED_FLAG]
    cage = bpy.data.objects.new("Armário face frame", None)
    ctx.scene.collection.objects.link(cage)
    cage['IS_FACE_FRAME_CABINET_CAGE'] = True
    migration.migrate_scene(ctx.scene)
    active = api.active_definition(ctx.scene)
    check("64UD: projeto só com face frame recebe o padrão EUA", active is not None
          and active.uid == builtin.BUILTIN_US_UID, active.name if active is not None else "nenhuma")


def main():
    migration_failure()
    second_question()
    replace_keeps_active()
    face_frame_is_legacy()


try:
    main()
except Exception:
    traceback.print_exc()
    FAILURES.append("exceção no roteiro")
print(f"blender_bug_MTPU_standards: {'OK' if not FAILURES else 'FALHAS: ' + ', '.join(FAILURES)}")
sys.exit(1 if FAILURES else 0)
