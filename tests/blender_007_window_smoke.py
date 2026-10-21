"""Teste de fumaça da feature 007 (T029): janela OBJ com folhas de correr, grupos, colisão e instalação na parede.

Run: blender --background --factory-startup --python-exit-code 1 --python tests/blender_007_window_smoke.py

Com o arquivo real `_reversa_forward/007-janela-obj-folhas-colisao/inputs/janela_preta_1400mm.obj`:
- importar (Automática + Z): 1400 × 850 × 80 mm em pé, 46 peças com os nomes e os 4 materiais do arquivo;
- Montar esquadria: Esquadria 16 + Folha_Esquerda 15 + Folha_Direita 15, folhas já de correr;
- sentido padrão para o próprio lado, com curso livre de ~2 mm e o aviso de pouco curso;
- invertida, a folha esquerda corre até o marco direito e cita a peça; 0% volta exatamente à pose do arquivo;
- com a direita invertida e aberta no caminho, a esquerda para ao fechar e cita a folha direita;
- folhas e esquadria fora do plano de corte;
- instalar numa parede HB (vão cortado, centrada na espessura, acompanha a espessura) e desinstalar;
- desfazer o grupo devolve as 15 peças à posição importada;
- os operadores novos têm `UNDO` e os ícones usados existem no 5.2.
O desfazer de verdade (Ctrl+Z) precisa de janela e fica no roteiro do onboarding.
"""

import sys
import traceback
from pathlib import Path

import bpy
from mathutils import Vector

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _blender_env as env  # noqa: E402
from caffmob_draw import hb_types  # noqa: E402
from caffmob_draw.aggregates import group, install, leaf, ops_group, ops_import, ops_install  # noqa: E402
from caffmob_draw.cutting import part_extractor  # noqa: E402

OBJ = Path(__file__).resolve().parents[1] / "_reversa_forward/007-janela-obj-folhas-colisao/inputs/janela_preta_1400mm.obj"
FAILURES = []
MM = 0.001


def check(name, ok, detail=""):
    print(("OK   " if ok else "FALHA ") + name, detail, flush=True)
    if not ok:
        FAILURES.append(name)


def box(objs):
    pts = [o.matrix_world @ Vector(c) for o in objs for c in o.bound_box]
    return [min(p[i] for p in pts) for i in range(3)], [max(p[i] for p in pts) for i in range(3)]


def run():
    ctx = bpy.context
    env.clean_scene()
    bpy.ops.caffmob.import_model(filepath=str(OBJ))
    meshes = [o for o in ctx.scene.objects if o.type == 'MESH']
    lo, hi = box(meshes)
    size = [round((hi[i] - lo[i]) / MM, 1) for i in range(3)]
    check("importa em mm e em pé", size == [1400.0, 80.0, 850.0], str(size))
    materials = sorted({m.name for o in meshes for m in o.data.materials if m})
    check("46 peças e 4 materiais", len(meshes) == 46 and len(materials) == 4, f"{len(meshes)} {materials}")
    rest = {o.name: o.matrix_world.copy() for o in meshes}

    imported = ctx.view_layer.objects.active            # feature 011 (D-09): o OBJ entra num grupo, já selecionado
    check("importação vira um grupo", group.is_group(imported) and set(group.members(imported)) == set(meshes),
          imported.name if imported else "nada")
    imported_name = imported.name if imported else ""
    check("Montar esquadria", bpy.ops.caffmob.window_assemble('EXEC_DEFAULT') == {'FINISHED'})
    check("o grupo da importação sai", imported_name and imported_name not in bpy.data.objects, imported_name)
    frame = ctx.view_layer.objects.active
    sashes = {o.name: o for o in frame.children_recursive if group.is_group(o)}
    counts = sorted([(frame.name, len(group.members(frame)))] + [(n, len(group.members(s))) for n, s in sashes.items()])
    check("grupos 16/15/15", counts == [("Folha_Direita", 15), ("Folha_Esquerda", 15), ("Janela", 16)], str(counts))
    left, right = sashes["Folha_Esquerda"], sashes["Folha_Direita"]
    la, ra = left.btm_aggregate, right.btm_aggregate
    check("folhas de correr para o próprio lado", (la.motion, la.slide_dir, ra.slide_dir) == ('SLIDE', 'NEG_X', 'POS_X'))
    check("curso livre ~2 mm e aviso", la.free_travel < 0.005 and leaf.low_travel(left), f"{la.free_travel:.4f}")
    check("sobreposição dos montantes 32 mm", abs(la.rest_overlap - 0.032) < 1e-4 and abs(ra.rest_overlap - 0.032) < 1e-4)

    la.slide_dir = 'POS_X'
    check("invertida: curso até o marco direito", 0.6 < la.free_travel < 0.7, f"{la.free_travel:.4f}")
    la.open_value = 1.0
    check("abre e bate no marco direito", la.open_value == 1.0 and la.contact_name == "Marco_Externo_Direita"
          and la.contact_kind == 'OPEN', f"{la.contact_name} {la.contact_kind}")
    la.open_value = 0.0
    env.settle()
    parts = group.members(left)
    drift = max((o.matrix_world.translation - rest[o.name].translation).length for o in parts)
    check("0% volta exatamente ao arquivo", drift < 1e-4 and not la.contact_name, f"{drift * 1000:.3f} mm")

    la.slide_dir = 'NEG_X'
    ra.slide_dir = 'NEG_X'
    ra.open_value = 0.4
    la.open_value = 1.0
    la.open_value = 0.0
    check("fechar para no montante da outra folha", la.open_value > 0.0 and la.contact_name == right.name
          and la.contact_kind == 'CLOSE', f"{la.open_value:.3f} {la.contact_name} {la.contact_kind}")
    ra.open_value = 0.0
    la.open_value = 0.0

    parts_cut, _bad = part_extractor.extract_production_parts(ctx)
    names = {o.name for o in meshes}
    check("fora do plano de corte", not any(p.module_ref in names or p.name in names for p in parts_cut))

    wall = hb_types.GeoNodeWall()
    wall.create("Parede")
    wall.set_input('Length', 4.0)
    wall.set_input('Thickness', 0.15)
    wall.set_input('Height', 2.6)
    frame.location = (2.0, -0.5, 0.0)
    env.settle()
    for o in ctx.selected_objects:
        o.select_set(False)
    frame.select_set(True)
    wall.obj.select_set(True)
    ctx.view_layer.objects.active = frame
    check("Instalar na parede", bpy.ops.caffmob.window_install('EXEC_DEFAULT') == {'FINISHED'})
    cage = install.cage_of(frame)
    cut = [m for m in wall.obj.modifiers if m.type == 'BOOLEAN' and m.object == cage]
    flo, fhi = group.group_box(frame, wall.obj.matrix_world)
    check("vão cortado e janela centrada na espessura", bool(cut) and abs((flo.y + fhi.y) / 2 - 0.075) < 1e-4
          and abs(flo.z - 1.0) < 1e-4, f"y {flo.y:.3f}..{fhi.y:.3f} z {flo.z:.3f}")
    hb_types.GeoNodeCage(cage).set_input('Dim Y', 0.25)           # o que o editor de paredes faz (apply.py)
    env.settle()
    flo, fhi = group.group_box(frame, wall.obj.matrix_world)
    check("acompanha a espessura nova", abs((flo.y + fhi.y) / 2 - 0.125) < 1e-4, f"{(flo.y + fhi.y) / 2:.3f}")
    la.open_value = 1.0
    check("instalada, a folha continua batendo na esquadria", la.contact_name.startswith("Marco_Externo"),
          la.contact_name)
    la.open_value = 0.0
    ctx.view_layer.objects.active = cage
    check("Desinstalar", bpy.ops.caffmob.window_uninstall('EXEC_DEFAULT') == {'FINISHED'})
    check("parede sem o corte e janela solta", frame.parent is None and not any(
        m.type == 'BOOLEAN' for m in wall.obj.modifiers))

    # 066 (RN-03): a janela solta está dentro da parede fechada; levá-la de volta à origem atravessaria a parede.
    # O ensaio a teletransporta com "Impedir atravessamento" desligado, só para comparar com a posição importada.
    ctx.scene.btm_settings.block_penetration = False
    frame.location = (0.0, 0.0, 0.0)
    env.settle()
    ctx.scene.btm_settings.block_penetration = True
    for o in ctx.selected_objects:
        o.select_set(False)
    ctx.view_layer.objects.active = frame
    check("Desfazer grupo", bpy.ops.caffmob.group_dissolve('EXEC_DEFAULT') == {'FINISHED'})
    env.settle()
    loose = [o for o in ctx.scene.objects if o.type == 'MESH' and o.name in rest]
    drift = max((o.matrix_world.translation - rest[o.name].translation).length for o in loose)
    check("peças soltas na posição importada", len(loose) == 46 and all(o.parent is None for o in loose)
          and drift < 1e-4, f"{len(loose)} {drift * 1000:.3f} mm")

    for o in ctx.selected_objects:
        o.select_set(False)
    ctx.view_layer.objects.active = None
    check("sem peças selecionadas, Criar grupo fica indisponível", not bpy.ops.caffmob.group_create.poll())

    ops = (ops_import.BTM_OT_ImportModel, ops_group.BTM_OT_GroupCreate, ops_group.BTM_OT_GroupDissolve,
           ops_group.BTM_OT_WindowAssemble, ops_install.BTM_OT_WindowInstall, ops_install.BTM_OT_WindowUninstall)
    check("operadores com UNDO", all('UNDO' in cls.bl_options for cls in ops))
    icons = set(bpy.types.UILayout.bl_rna.functions['label'].parameters['icon'].enum_items.keys())
    used = {'MOD_BUILD', 'GROUP', 'X', 'MOD_WIREFRAME', 'UNLINKED', 'MOD_BOOLEAN', 'INFO', 'ERROR'}
    check("ícones existem no 5.2", used <= icons, str(sorted(used - icons)))


try:
    run()
except Exception:
    traceback.print_exc()
    FAILURES.append("exceção no roteiro")
print(f"blender_007_window_smoke: {'OK' if not FAILURES else 'FALHAS: ' + ', '.join(FAILURES)}", flush=True)
if FAILURES:
    sys.exit(1)
