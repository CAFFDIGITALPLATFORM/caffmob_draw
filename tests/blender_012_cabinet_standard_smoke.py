"""Fumaça de Criar armário pelo Padrão de Dimensões (feature 012, T038; RF-04 a RF-07, RF-15).

Roda em segundo plano:
    blender --background --factory-startup --python-exit-code 1 --python tests/blender_012_cabinet_standard_smoke.py

Com o padrão do titular (`fixtures/dimensionexport_me_moveis.xml`) importado e ativo:
- balcão, aéreo e torre com as medidas externas e as espessuras da linha;
- Criar armário sem diálogo (`EXEC`) cria e não abre editor; Cancelar não cria (o diálogo só existe com janela);
- base passante na malha e na lista de corte; padrão próprio;
- categoria Lavanderia (DOR) e modelo pronto em Banheiro (BAN) dão as chapas da linha.
"""

import sys
import traceback
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _blender_env as env  # noqa: E402
import bpy  # noqa: E402
from caffmob_draw.cabinet_editor import bridge  # noqa: E402
from caffmob_draw.cutting import part_sources  # noqa: E402
from caffmob_draw.library_panel import categories  # noqa: E402
from caffmob_draw.standards import api  # noqa: E402

ctx = bpy.context
FAILURES = []
FIXTURE = Path(__file__).resolve().parent / "fixtures" / "dimensionexport_me_moveis.xml"


def check(name, ok, detail=""):
    print(("OK   " if ok else "FALHA ") + name, detail, flush=True)
    if not ok:
        FAILURES.append(name)


def mm(key):
    return float(api.get_value(ctx.scene, key)) / 1000.0


def close(a, b):
    return abs(a - b) < 1e-5


def last_module():
    return ctx.view_layer.objects.active


def mesh_x_span(obj, z_from, z_to):
    xs = [v.co.x for v in obj.data.vertices if z_from - 1e-6 <= v.co.z <= z_to + 1e-6]
    return round(max(xs) - min(xs), 6) if xs else 0.0


def main():
    env.clean_scene()
    assert bpy.ops.caffmob.standards_import_promob(filepath=str(FIXTURE)) == {'FINISHED'}
    imported = next(d for d in api.standards(ctx.scene).definitions if d.source == 'PROMOB_IMPORT')
    api.set_active(ctx.scene, imported)

    for kind, h_key, d_key in (('BASE', 'base_height', 'base_depth'), ('WALL', 'upper_mid_height', 'upper_depth'),
                               ('TALL', 'tall_height', 'tall_depth')):
        assert bpy.ops.caffmob.library_create_cabinet(cabinet_type=kind, width=0.6, line='COZ',
                                                      open_editor=False) == {'FINISHED'}
        cab = last_module().btm_cabinet
        check(f"{kind}: altura e profundidade do padrão",
              close(cab.height, mm(f"COZ.external.{h_key}")) and close(cab.depth, mm(f"COZ.external.{d_key}")),
              f"{cab.height:.3f} {cab.depth:.3f}")
    wall = [o for o in ctx.scene.objects if o.get('btm_line') and o.btm_cabinet.cabinet_type == 'WALL'][0]
    check("aéreo na altura de instalação", close(wall.location.z, mm("COZ.external.install_height_upper")),
          f"{wall.location.z:.3f}")
    base = [o for o in ctx.scene.objects if o.get('btm_line') and o.btm_cabinet.cabinet_type == 'BASE'][0]
    cab = base.btm_cabinet
    check("chapas da linha COZ", close(cab.thickness, mm("COZ.sheets.LAT.thickness"))
          and close(cab.thickness_back or cab.thickness, mm("COZ.sheets.FUN_INF.thickness")),
          f"lat={cab.thickness:.4f} fundo={cab.thickness_back:.4f}")
    check("padrão de origem gravado", base.get('btm_standard_uid') == imported.uid)
    check("montagem do padrão (lateral)", cab.assembly == 'LATERAL')

    # Base passante na malha e na lista de corte.
    t = cab.thickness
    cab.assembly = 'BASE'
    check("base passante na malha: base com a largura toda", close(mesh_x_span(base, 0.0, t), cab.width),
          f"{mesh_x_span(base, 0.0, t)}")
    module = next(m for m in part_sources.iter_modules(ctx.scene) if m.obj == base)
    records = part_sources.synthetic_records(module, lambda comp: mm(f"COZ.sheets.{comp}.thickness") * 1000.0)
    sizes = {r.name: r.length for r in records}
    check("lista de corte: base 600, lateral altura − base",
          abs(sizes.get("Base inferior", 0) - 600.0) < 0.01
          and abs(sizes.get("Lateral esquerda", 0) - (cab.height * 1000.0 - t * 1000.0)) < 0.01, str(sizes))
    check("padrão próprio depois de trocar a montagem", bridge.is_own_standard(ctx, base))

    # Categoria do usuário e modelo pronto.
    reason = categories.create("Lavanderia", 'DOR')
    check("criar categoria Lavanderia (DOR)", reason is None, str(reason))
    check("categoria repetida recusada", categories.create("cozinha", 'COZ') is not None)
    assert bpy.ops.caffmob.library_create_cabinet(cabinet_type='BASE', width=0.5, line='DOR',
                                                  open_editor=False) == {'FINISHED'}
    check("armário em DOR tem chapas de DOR", close(last_module().btm_cabinet.thickness,
                                                     mm("DOR.sheets.LAT.thickness")))
    assert bpy.ops.caffmob.library_insert_model(model_id='balcao_2p', line='BAN') == {'FINISHED'}
    model = last_module().btm_cabinet
    check("modelo balcão 2 portas em Banheiro", model.door_swing == 'DOUBLE' and close(model.width, 0.8)
          and close(model.thickness, mm("BAN.sheets.LAT.thickness")) and model.line == 'BAN')


try:
    main()
except Exception:
    traceback.print_exc()
    FAILURES.append("exceção no roteiro")
print(f"blender_012_cabinet_standard_smoke: {'OK' if not FAILURES else 'FALHAS: ' + ', '.join(FAILURES)}")
sys.exit(1 if FAILURES else 0)
