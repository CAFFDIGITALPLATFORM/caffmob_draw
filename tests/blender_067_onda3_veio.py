"""Veio da textura (feature 067, T027; RF-060 a RF-065).

    xvfb-run -a blender --factory-startup --enable-event-simulate --python tests/blender_067_onda3_veio.py

Com o catálogo do servidor falso local do MOBI:
- fixture V/H/V (três frentes em pé com a mesma textura): um material só, as três com o mesmo tamanho físico (a
  escala do Mapping não muda), e o giro por objeto segue o veio de cada uma;
- a calibração da imagem (H ou V) inverte o giro (RF-061);
- os mapas de imagem do material (cor e relevo) leem o mesmo Mapping (RF-062);
- mudar o veio de uma chapa não muda as irmãs com o mesmo material; a projeção é BOX (RF-063);
- o veio visual e o de corte são o mesmo dado: mudar `btm_part.grain` muda o `grain_direction` do corte (RF-064);
- peça sem material guarda a intenção V; a textura aplicada depois sai em V, num passo de Desfazer que restaura
  materiais e metadados (RF-065);
- a variante `<nome> ROTATED` não é mais criada (M-05: a existente é lida e migrada).
"""

import math
import sys
from pathlib import Path

import bpy

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _authored_env as authored_env  # noqa: E402
import _blender_env as env  # noqa: E402
import _janela_067 as j  # noqa: E402
from _mobi_texture_fixture import TextureServer  # noqa: E402
from caffmob_draw.customize import finish_core as fc  # noqa: E402
from caffmob_draw.cutting import part_sources  # noqa: E402
from caffmob_draw.object_library import retexture  # noqa: E402
from caffmob_draw.texture_library import catalog, grain, grain_migration  # noqa: E402

server = TextureServer()
QUARTER = round(math.pi / 2, 4)


def rot(obj):
    return tuple(round(v, 4) for v in obj.get(grain.ATTR, (0.0, 0.0, 0.0)))


def mapping_of(mat):
    return next(n for n in mat.node_tree.nodes if n.type == 'MAPPING')


def front(name, x):
    obj = authored_env.cube(name, (0.4, 0.018, 0.7), (x, 0, 0.35))
    return obj


def drop(obj, item, **domains):
    authored_env.select([obj])
    bpy.context.view_layer.update()
    return bpy.ops.caffmob.finish_drop('EXEC_DEFAULT', key=item, object_name=obj.name, **domains)


def body(w):
    env.clean_scene()
    bpy.context.scene.btm_component_select = False
    server.connect()
    item = next(i["id"] for i in catalog._cache['items'] if i["px"][0] == i["px"][1])
    server.download(item)

    # V/H/V: mesma textura, um material só, mesmo tamanho físico.
    sheets = [front(f"Frente {g} {i}", i * 0.5) for i, g in enumerate("VHV")]
    for obj, wanted in zip(sheets, "VHV"):
        obj.btm_part.grain = wanted
        j.check(drop(obj, item, external=True) == {'FINISHED'}, f"textura em {obj.name}")
    mats = {obj.data.materials[0] for obj in sheets}
    j.check(len(mats) == 1, "V/H/V com um material só (sem cópia por peça)", str([m.name for m in mats]))
    mat = next(iter(mats))
    mat_name = mat.name
    j.check(not any(m.name.endswith(" ROTATED") for m in bpy.data.materials), "nenhuma variante ROTATED criada")
    j.check([rot(o) for o in sheets] == [(0.0, QUARTER, 0.0), (0.0, 0.0, 0.0), (0.0, QUARTER, 0.0)],
            "o giro por objeto segue V/H/V", str([rot(o) for o in sheets]))
    scale = tuple(round(v, 4) for v in mapping_of(mat).inputs['Scale'].default_value)
    j.check(scale[0] == scale[1], "o tamanho físico é o mesmo nos dois eixos da imagem (sem esticar)", str(scale))
    rotate = mat.node_tree.nodes.get(grain.ROTATE_NODE)
    attribute = mat.node_tree.nodes.get(grain.ATTR_NODE)
    j.check(rotate is not None and attribute is not None and attribute.attribute_type == 'OBJECT'
            and rotate.outputs['Vector'].links[0].to_node == mapping_of(mat),
            "o giro (Attribute Object → Vector Rotate) vem antes da escala métrica")
    images = [n for n in mat.node_tree.nodes if n.type == 'TEX_IMAGE']
    j.check(all(n.projection == 'BOX' for n in images), "projeção BOX")
    j.check(all(any(link.from_node == mapping_of(mat) for link in n.inputs['Vector'].links) for n in images),
            "todos os mapas de imagem leem o mesmo Mapping")

    # Mudar o veio de uma chapa não muda as irmãs.
    before = [rot(o) for o in sheets]
    sheets[1].btm_part.grain = 'V'
    j.check(rot(sheets[1]) == (0.0, QUARTER, 0.0) and [rot(sheets[0]), rot(sheets[2])] == [before[0], before[2]],
            "mudar o veio de uma chapa não muda as irmãs", str([rot(o) for o in sheets]))
    sheets[1].btm_part.grain = 'H'

    # Calibração: imagem com veio vertical, calibrada como tal, produz H correto.
    grain.calibrate(mat, 'V')
    for obj in sheets:
        grain.sync(obj)
    j.check([rot(o) for o in sheets] == [(0.0, 0.0, 0.0), (0.0, QUARTER, 0.0), (0.0, 0.0, 0.0)],
            "calibração V inverte o giro", str([rot(o) for o in sheets]))
    grain.calibrate(mat, 'H')
    for obj in sheets:
        grain.sync(obj)

    # Veio visual = veio de corte (a geometria livre entra no corte com o veio da peça).
    from caffmob_draw.geometry_free import mesh as geometry_mesh
    plate = geometry_mesh.create_object(bpy.context, 'PLACA')
    plate.btm_geometry.fabrication = True
    plate.btm_part.grain = 'V'
    records = [r for r in part_sources.geometry_records(bpy.context.scene) if r.name == plate.name]
    j.check(records and records[0].grain == 'VERTICAL', "o corte lê o mesmo veio da peça",
            str([(r.name, r.grain) for r in records]))
    from caffmob_draw.cutting import csv_exporter, nesting, part_extractor
    part = part_extractor.record_to_part(records[0], part_extractor._active_values(bpy.context.scene))
    j.check("COMPRIMENTO" in csv_exporter.parts_csv_text([part]), "o CSV de corte mostra o veio no comprimento")
    part.height, part.width = 1900.0, 500.0         # o veio da chapa (2750 × 1830) corre nos 2750 (071, motor OpenMob)
    deitada = nesting.optimize_nesting([part], respect_grain=True)
    j.check(deitada['stats']['unplaced_count'] == 0 and deitada['sheets'][0]['shelves'][0]['parts'][0]['width'] == 1900,
            "veio no comprimento: a peça de 1900 mm corre ao longo dos 2750 da chapa", f"{deitada['stats']}")
    part.grain_direction = 'HORIZONTAL'             # veio na largura: a largura vai nos 2750, e 1900 não cabe nos 1810
    placed = nesting.optimize_nesting([part], respect_grain=True)
    loose = nesting.optimize_nesting([part], respect_grain=False)
    j.check(placed['stats']['unplaced_count'] == 1 and loose['stats']['unplaced_count'] == 0,
            "respect_grain: a peça com veio na largura não gira; sem ele, gira",
            f"{placed['stats']} {loose['stats']}")
    plate.btm_part.grain = 'H'
    records = [r for r in part_sources.geometry_records(bpy.context.scene) if r.name == plate.name]
    j.check(records and records[0].grain == 'HORIZONTAL', "mudar o veio na peça muda o corte")
    part = part_extractor.record_to_part(records[0], part_extractor._active_values(bpy.context.scene))
    j.check("LARGURA" in csv_exporter.parts_csv_text([part]), "o CSV muda para o veio na largura")

    # Intenção sem material, Undo.
    blank = front("Sem material", 2.0)
    blank.btm_part.grain = 'V'
    j.check(rot(blank) == (0.0, 0.0, 0.0) and not blank.data.materials, "sem material: só a intenção V")
    name = blank.name
    w.push("Antes da textura")
    j.check(drop(blank, item, external=True) == {'FINISHED'}, "textura depois da intenção")
    w.push("Textura")
    j.check(rot(blank) == (0.0, QUARTER, 0.0), "a textura aplicada depois sai em V", str(rot(blank)))
    w.undo()
    blank = bpy.data.objects[name]
    j.check(not [m for m in blank.data.materials if m] and not any(i.domain == fc.EXTERNAL for i in blank.btm_finish),
            "um Desfazer restaura material e metadados")

    # M-05: a variante antiga é lida e migrada.
    legacy = front("Antiga", 3.0)
    mat = bpy.data.materials[mat_name]                  # o Desfazer refez os dados
    old = retexture.image_material(mat[retexture.PATH_PROP], 200, 200)
    rotated = old.copy()
    rotated.name = old.name + " ROTATED"
    legacy.data.materials.append(rotated)
    j.check(grain_migration.migrate_object(legacy) and legacy.btm_part.grain == 'V'
            and rot(legacy) == (0.0, 0.0, QUARTER) and legacy.data.materials[0] == rotated,
            "M-05: veio V e giro equivalente, com o material antigo mantido")
    legacy.btm_part.grain = 'H'
    j.check(legacy.data.materials[0] == old, "M-05: a primeira edição de veio volta ao material de origem",
            legacy.data.materials[0].name)
    server.close()


j.run("blender_067_onda3_veio", body)
