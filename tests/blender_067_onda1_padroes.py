"""Padrão de Dimensões no banco local, na abertura de arquivos (feature 067, T130; D-27, R11, RN-15).

Run: blender --background --factory-startup --python-exit-code 1 --python tests/blender_067_onda1_padroes.py

Tudo roda com o banco num diretório temporário (D-35). Confere:
- arquivo novo recebe as definições do banco e a última ativa;
- arquivo antigo (só com as embutidas ativas e um módulo) mantém a ativa e os módulos e ganha só os uids que não tem;
- uid igual com conteúdo diferente: vale o do arquivo, e o banco não muda;
- abrir nunca grava no banco;
- gravar uma definição mais antiga que a do banco é recusado até alguém confirmar (R11).
"""

import os
import sqlite3
import sys
import tempfile
import traceback
from pathlib import Path

import bpy

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _blender_env as env  # noqa: E402,F401
import _fixtures_067 as fx  # noqa: E402
from caffmob_draw.standards import api, store  # noqa: E402

FAILURES = []
LAT = 'COZ.sheets.LAT.thickness'


def check(ok, label, detail=""):
    print(("OK   " if ok else "FALHA ") + label + (f" ({detail})" if detail and not ok else ""), flush=True)
    if not ok:
        FAILURES.append(label)


def db_rows(path):
    store.close()
    with sqlite3.connect(path) as con:
        return (sorted(con.execute("SELECT uid, documento, atualizado_em, sujo, excluida FROM definicao").fetchall()),
                sorted(con.execute("SELECT chave, valor FROM meta").fetchall()))


def scene():
    return api.main_scene(bpy.context.scene)


def run(path, folder):
    # 1. Arquivo antigo, gravado antes do banco: só a embutida ativa, uma definição própria e um módulo.
    bpy.ops.wm.read_homefile(use_empty=True)
    s = scene()
    api.ensure_ready(s)
    old = api.duplicate_definition(s, api.find_definition(s, uid='builtin-br'), "Antiga do arquivo")
    api.set_value(old, LAT, 15.0)
    api.set_active(s, api.find_definition(s, uid='builtin-br'))
    assert bpy.ops.caffmob.cabinet_builder(width=0.6) == {'FINISHED'}
    module_name = bpy.context.object.name
    old_file = os.path.join(folder, "antigo_1_8_0.blend")
    shared_uid = old.uid
    bpy.ops.wm.save_as_mainfile(filepath=old_file, copy=True)

    # 2. O titular cria o padrão da marcenaria em outra sessão: vai ao banco pelos operadores.
    bpy.ops.wm.read_homefile(use_empty=True)
    s = scene()
    api.ensure_ready(s)
    api.set_active(s, api.find_definition(s, uid='builtin-br'))
    assert bpy.ops.caffmob.standards_duplicate() == {'FINISHED'}
    own = api.active_definition(s)
    own.name = "Marcenaria X"
    api.set_value(own, LAT, 18.0)
    check(store.persist(s, own) == 'SAVED', "duplicar grava a definição no banco")
    own_uid = own.uid
    assert bpy.ops.caffmob.standards_set_active(definition=own_uid) == {'FINISHED'}
    # A mesma definição do arquivo antigo, editada no banco com outro valor e versão mais nova.
    document = api.find_definition(s, uid=own_uid)
    from caffmob_draw.standards import io_json
    twin = dict(io_json.definition_document(document), uid=shared_uid, name="Antiga do arquivo", version=3)
    twin['lines'] = {'COZ': {'external': {}, 'components': {}, 'sheets': {'LAT': {'thickness': 25.0,
                                                                                  'edges': [0, 0, 0, 0]}}}}
    store.get().put(twin)
    check(store.get().last_active == own_uid, "a ativa vai ao banco como última ativa")

    # 3. Arquivo novo: recebe as definições do banco e a última ativa.
    before = db_rows(path)
    bpy.ops.wm.read_homefile(use_empty=True)
    s = scene()
    from caffmob_draw.standards import migration
    migration.run(s)
    names = {d.name for d in api.standards(s).definitions}
    check("Marcenaria X" in names, "arquivo novo recebe as definições do banco", str(names))
    active = api.active_definition(s)
    check(active is not None and active.uid == own_uid, "arquivo novo fica com a última ativa",
          active.name if active else None)
    check(abs(api.get_definition_value(active, LAT) - 18.0) < 1e-6, "com os valores do banco")
    check(db_rows(path) == before, "abrir um arquivo novo não grava no banco")

    # 4. Arquivo antigo: mantém a ativa e os módulos; ganha só os uids que não tem; o uid igual vale o do arquivo.
    before = db_rows(path)
    bpy.ops.wm.open_mainfile(filepath=old_file)
    s = scene()
    check(api.active_definition(s).uid == 'builtin-br', "arquivo antigo mantém a ativa")
    check(module_name in bpy.data.objects, "arquivo antigo mantém os módulos")
    check(api.find_definition(s, uid=own_uid) is not None, "arquivo antigo ganha a definição que não tinha")
    mine = api.find_definition(s, uid=shared_uid)
    check(mine is not None and abs(api.get_definition_value(mine, LAT) - 15.0) < 1e-6,
          "uid igual com conteúdo diferente: vale o do arquivo")
    check(db_rows(path) == before, "abrir um arquivo antigo não grava no banco")

    # 5. Gravar a versão mais antiga do arquivo por cima da mais nova do banco pede confirmação (R11).
    check(store.persist(s, mine) == 'OLDER', "versão mais antiga que a do banco não é gravada sem confirmar")
    check(abs(store.get().get(shared_uid)['lines']['COZ']['sheets']['LAT']['thickness'] - 25.0) < 1e-6,
          "o banco continua com a versão dele")
    check(store.persist(s, mine, confirmed=True) == 'SAVED', "confirmada, a versão do arquivo é gravada")


try:
    with fx.banco_temporario() as db_path, tempfile.TemporaryDirectory(prefix="caffmob_067_arquivos_") as folder:
        run(db_path, folder)
except Exception:
    traceback.print_exc()
    FAILURES.append("exceção")
print(f"blender_067_onda1_padroes: {'OK' if not FAILURES else 'FALHAS: ' + ', '.join(FAILURES)}", flush=True)
sys.exit(1 if FAILURES else 0)
