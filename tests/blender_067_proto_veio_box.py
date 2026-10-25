"""Protótipo da premissa 4 (feature 067, T008; D-20): o nó Attribute (tipo Object) gira o Mapping compartilhado por
objeto, nas projeções BOX e UV, com os 4 mapas PBR.

Run: blender --background --factory-startup --python-exit-code 1 --python tests/blender_067_proto_veio_box.py

Uma imagem de listras horizontais (veio em u, calibração H) vira um material só. Duas chapas em pé usam o mesmo
material, uma com veio H e outra com V; uma lateral (normal X) e uma prateleira deitada (normal Z) completam a
caixa. Cada uma é renderizada em Cycles (32 × 32 px, câmera ortográfica de frente para a face), e a direção das
listras sai da variância das linhas e das colunas: veio H = linhas constantes; veio V = colunas constantes. A chapa
com o mesmo material e veio diferente não muda (RF-063). Com UV, o giro é em Z. Os quatro mapas (cor, rugosidade,
normal e relevo) leem o mesmo Mapping.
"""

import math
import os
import sys
import tempfile
import traceback
from pathlib import Path

import bmesh
import bpy
from mathutils import Vector

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _blender_env as env  # noqa: E402
from caffmob_draw.texture_library import grain  # noqa: E402

FAILURES = []
SIZE = 32


def check(ok, label, detail=""):
    print(("OK   " if ok else "FALHA ") + label + (f" ({detail})" if detail and not ok else ""), flush=True)
    if not ok:
        FAILURES.append(label)


def stripes_image(folder):
    img = bpy.data.images.new("listras", 64, 64)
    pixels = []
    for y in range(64):
        value = 1.0 if (y // 8) % 2 else 0.0          # listras horizontais: o veio corre em x (u)
        pixels += [value, value, value, 1.0] * 64
    img.pixels[:] = pixels
    path = os.path.join(folder, "listras.png")
    img.filepath_raw = path
    img.file_format = 'PNG'
    img.save()
    return path


def material(path, uv=False):
    mat = bpy.data.materials.new("Veio UV" if uv else "Veio BOX")
    tree = mat.node_tree
    bsdf = next(n for n in tree.nodes if n.type == 'BSDF_PRINCIPLED')
    coords = tree.nodes.new('ShaderNodeTexCoord')
    mapping = tree.nodes.new('ShaderNodeMapping')
    mapping.inputs['Scale'].default_value = (1 / 0.2, 1 / 0.2, 1 / 0.2)   # 200 mm de imagem
    image = bpy.data.images.load(path, check_existing=True)
    textures = []
    for socket in ('Base Color', 'Roughness', 'Normal', 'Bump'):
        tex = tree.nodes.new('ShaderNodeTexImage')
        tex.image = image
        tex.projection = 'FLAT' if uv else 'BOX'
        textures.append(tex)
        if socket == 'Base Color':
            tree.links.new(tex.outputs['Color'], bsdf.inputs['Base Color'])
            bsdf.inputs['Emission Color'].default_value = (0, 0, 0, 1)
        elif socket == 'Roughness':
            tree.links.new(tex.outputs['Color'], bsdf.inputs['Roughness'])
    tree.links.new(coords.outputs['UV' if uv else 'Object'], mapping.inputs['Vector'])
    tree.links.new(mapping.outputs['Vector'], textures[0].inputs['Vector'])
    # Emissão = cor: a luz não interfere na leitura das listras.
    emission = tree.nodes.new('ShaderNodeEmission')
    tree.links.new(textures[0].outputs['Color'], emission.inputs['Color'])
    out = next(n for n in tree.nodes if n.type == 'OUTPUT_MATERIAL')
    tree.links.new(emission.outputs['Emission'], out.inputs['Surface'])
    grain.calibrate(mat, 'H')
    check(grain.ensure_graph(mat), f"{mat.name}: grafo do giro ligado")
    return mat


def sheet(name, size, location, mat):
    mesh = bpy.data.meshes.new(name)
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    for v in bm.verts:
        v.co = Vector((v.co.x * size[0], v.co.y * size[1], v.co.z * size[2]))
    uv = bm.loops.layers.uv.new()
    for face in bm.faces:
        for loop in face.loops:                     # UV = (x, y) local normalizados pela própria peça
            loop[uv].uv = (loop.vert.co.x / size[0] + 0.5, loop.vert.co.y / max(size[1], 1e-6) + 0.5)
    bm.to_mesh(mesh)
    bm.free()
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    obj.location = location
    mesh.materials.append(mat)
    return obj


def render(obj, view_dir, folder):
    """Renderiza só `obj`, com a câmera olhando ao longo de `view_dir`; devolve a imagem em tons de cinza."""
    scene = bpy.context.scene
    for other in scene.objects:
        if other.type == 'MESH':
            other.hide_render = other is not obj
    cam = scene.camera
    bpy.context.view_layer.update()                 # a matriz de um objeto recém-criado só vale depois do update
    center = obj.matrix_world.translation
    cam.location = center - Vector(view_dir) * 3.0
    cam.rotation_euler = Vector(view_dir).to_track_quat('-Z', 'Z' if abs(view_dir[2]) < 0.9 else 'Y').to_euler()
    path = os.path.join(folder, f"{obj.name}.png")
    scene.render.filepath = path
    bpy.ops.render.render(write_still=True)
    img = bpy.data.images.load(path)
    px = list(img.pixels)
    gray = [[px[(y * SIZE + x) * 4] for x in range(SIZE)] for y in range(SIZE)]
    bpy.data.images.remove(img)
    return gray


def orientation(gray):
    """'H' se as linhas são constantes (listras horizontais), 'V' se as colunas são."""
    def variance(values):
        mean = sum(values) / len(values)
        return sum((v - mean) ** 2 for v in values) / len(values)
    rows = sum(variance(r) for r in gray) / SIZE
    cols = sum(variance([gray[y][x] for y in range(SIZE)]) for x in range(SIZE)) / SIZE
    return ('H' if rows < cols else 'V'), rows, cols


def setup_scene():
    scene = bpy.context.scene
    scene.render.engine = 'CYCLES'
    scene.cycles.device = 'CPU'
    scene.cycles.samples = 4
    scene.render.resolution_x = scene.render.resolution_y = SIZE
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = 'PNG'
    scene.render.image_settings.color_mode = 'RGBA'
    scene.view_settings.view_transform = 'Standard'
    cam_data = bpy.data.cameras.new("Câmera")
    cam_data.type = 'ORTHO'
    cam_data.ortho_scale = 0.3
    cam = bpy.data.objects.new("Câmera", cam_data)
    scene.collection.objects.link(cam)
    scene.camera = cam


def run(folder):
    env.clean_scene()
    setup_scene()
    path = stripes_image(folder)
    box = material(path)
    tree = box.node_tree
    mapping = next(n for n in tree.nodes if n.type == 'MAPPING')
    images = [n for n in tree.nodes if n.type == 'TEX_IMAGE']
    check(len(images) == 4 and all(any(link.from_node == mapping for link in n.inputs['Vector'].links)
                                   for n in images), "os 4 mapas leem o mesmo Mapping")

    cases = (  # nome, medida, normal da face vista, papel dos eixos (rótulos), veio, esperado na imagem
        ("Frente H", (0.6, 0.018, 0.6), (0, 1, 0), 'H'),
        ("Frente V", (0.6, 0.018, 0.6), (0, 1, 0), 'V'),
        ("Lateral V", (0.018, 0.6, 0.6), (1, 0, 0), 'V'),
        ("Prateleira V", (0.6, 0.6, 0.018), (0, 0, -1), 'V'),
    )
    objects = {}
    for i, (name, size, view_dir, wanted) in enumerate(cases):
        obj = sheet(name, size, (i * 1.5, 0, 0), box)
        obj.btm_part.grain = wanted                 # o update chama grain.sync
        grain.sync(obj)
        objects[name] = (obj, view_dir, wanted)
    bpy.context.view_layer.update()
    for name, (obj, view_dir, wanted) in objects.items():
        found, rows, cols = orientation(render(obj, view_dir, folder))
        # Prateleira deitada: V corre na profundidade (Y), que a câmera de cima vê como vertical.
        check(found == wanted, f"{name}: listras na direção do veio {wanted} (BOX)",
              f"achado {found}, linhas {rows:.3f}, colunas {cols:.3f}, giro {tuple(obj.get(grain.ATTR))}")
    check(tuple(objects["Frente H"][0].get(grain.ATTR)) == (0.0, 0.0, 0.0),
          "irmã com o mesmo material e veio H não gira")

    uv_mat = material(path, uv=True)
    plate = sheet("UV V", (0.6, 0.6, 0.018), (8, 0, 0), uv_mat)
    plate.btm_part.grain = 'V'
    value = grain.sync(plate)
    check(tuple(round(v, 4) for v in value) == (0.0, 0.0, round(math.pi / 2, 4)), "UV gira em Z", str(value))
    found, rows, cols = orientation(render(plate, (0, 0, -1), folder))
    check(found == 'V', "UV: listras na direção do veio V", f"{found} {rows:.3f} {cols:.3f}")
    plate.btm_part.grain = 'H'
    grain.sync(plate)
    found, rows, cols = orientation(render(plate, (0, 0, -1), folder))
    check(found == 'H', "UV: veio H volta às listras horizontais", f"{found} {rows:.3f} {cols:.3f}")


try:
    with tempfile.TemporaryDirectory(prefix="caffmob_067_veio_") as tmp:
        run(tmp)
except Exception:
    traceback.print_exc()
    FAILURES.append("exceção")
print(f"blender_067_proto_veio_box: {'OK' if not FAILURES else 'FALHAS: ' + ', '.join(FAILURES)}", flush=True)
sys.exit(1 if FAILURES else 0)
