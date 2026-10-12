"""Reprodução e regressão do lote de uid e espessura na produção: BUG-20261011-3VD7, BUG-20261011-SKDL e
BUG-20261011-L6YN.

Run: blender --background --factory-startup --python-exit-code 1 --python tests/blender_bug_3VD7_production_uid.py

- Geometria livre convertida em agregado e marcada como peça sai uma vez, como geometria (questions.md, pergunta 67);
- cópia nativa (Shift+D) de uma geometria não repete o uid da original (geometry_free EC-12);
- a placa sai sempre com `thickness` como espessura, e o painel avisa a medida menor que ela (pergunta 66).
"""

import sys
import traceback
from pathlib import Path

import bpy

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _blender_env as env  # noqa: E402
from caffmob_draw.aggregates import apply as agg_apply  # noqa: E402
from caffmob_draw.aggregates import convert, production  # noqa: E402
from caffmob_draw.cutting import json_exporter, part_extractor, part_sources  # noqa: E402
from caffmob_draw.geometry_free import mesh  # noqa: E402

ctx = bpy.context
FAILURES = []


def check(name, ok, detail=""):
    print(("OK   " if ok else "FALHA ") + name, detail, flush=True)
    if not ok:
        FAILURES.append(name)


def placa(name, width=0.8, depth=0.5, thickness=0.018):
    obj = mesh.create_object(ctx, 'PLACA', name)
    g = obj.btm_geometry
    g.width, g.depth, g.thickness, g.fabrication = width, depth, thickness, True
    return obj


def payload_errors():
    parts, _bad = part_extractor.extract_production_parts(ctx)
    payload = json_exporter.build_global_payload(project={"name": "Lote 5", "uid": "P", "rooms": []},
                                                 standard={"uid": "S", "name": "S"}, parts=parts,
                                                 modules=part_extractor.module_entries(ctx.scene))
    return json_exporter.validate_global_json(payload)


def converted_geometry():
    env.clean_scene()
    pai = bpy.data.objects.new("Tampo", bpy.data.meshes.new("Tampo"))
    ctx.scene.collection.objects.link(pai)
    geo = placa("Prateleira")
    env.settle()
    convert.convert(geo, pai)
    agg_apply._write(geo, 'production_part', True)
    production.sync(geo)
    env.settle()
    uid = geo.get(part_sources.UID_PROP) or part_sources.ensure_module_uid(geo)
    records = [r for r in part_sources.geometry_records(ctx.scene) if r.uid.startswith(f"{uid}/")]
    check("3VD7: geometria convertida em agregado sai uma vez", len(records) == 1, str([r.uid for r in records]))
    check("3VD7: o JSON global valida", payload_errors() == [], str(payload_errors()))


def native_copy():
    env.clean_scene()
    original = placa("Placa")
    part_sources.geometry_records(ctx.scene)                 # extrai uma vez: a placa ganha btm_uid
    uid = original[part_sources.UID_PROP]
    copy = original.copy()                                   # Shift+D: idprops vêm junto
    copy.data = original.data.copy()
    ctx.scene.collection.objects.link(copy)
    env.settle()
    uids = [r.uid for r in part_sources.geometry_records(ctx.scene)]
    check("SKDL: cópia nativa não repete o uid", len(uids) == len(set(uids)) == 2, str(uids))
    check("SKDL: a original mantém o uid", original[part_sources.UID_PROP] == uid)
    check("SKDL: o JSON global valida", payload_errors() == [], str(payload_errors()))


def board_thickness():
    sheets = mesh.sheets('PLACA', 'XY', 0.6, 0.01, 0.0, 0.018)
    check("L6YN: a espessura da placa é sempre thickness", [tuple(round(v, 6) for v in s[1:]) for s in sheets]
          == [(0.6, 0.01, 0.018)], str(sheets))
    check("L6YN: placa comum continua igual", mesh.sheets('PLACA', 'XZ', 0.8, 0.0, 0.5, 0.018)[0][1:]
          == (0.8, 0.5, 0.018))
    warn = getattr(mesh, 'thinner_than_thickness', None)
    check("L6YN: o painel sabe avisar a medida menor que a espessura",
          warn is not None and warn('PLACA', 'XY', 0.6, 0.01, 0.0, 0.018)
          and not warn('PLACA', 'XY', 0.6, 0.5, 0.0, 0.018))


try:
    converted_geometry()
    native_copy()
    board_thickness()
except Exception:
    traceback.print_exc()
    FAILURES.append("exceção no roteiro")
print(f"blender_bug_3VD7_production_uid: {'OK' if not FAILURES else 'FALHAS: ' + ', '.join(FAILURES)}")
sys.exit(1 if FAILURES else 0)
