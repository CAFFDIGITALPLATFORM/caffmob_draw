"""Gera as miniaturas do catálogo do Construtor de Armários (feature 008, T048; D-19).

Uso:
    blender --background --factory-startup --python tools/render_cabinet_thumbnails.py [-- --only-missing]

`--only-missing` gera só as miniaturas que ainda não existem (feature 015), sem regravar as outras.

Saída: caffmob_draw/cabinet_editor/thumbnails/<id em minúsculas>.png (chave = `catalog.Item.thumb`), 128 × 128.
Cada item vira um esquema em caixas sobre um armário de referência (600 × 700 × 500 mm): a peça do item em destaque e
a carcaça em cinza claro. Workbench, vista 3/4 ortográfica, fundo transparente.
"""

import importlib.util
import math
import sys
from pathlib import Path

import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "caffmob_draw" / "cabinet_editor" / "thumbnails"

spec = importlib.util.spec_from_file_location("catalog", ROOT / "caffmob_draw/cabinet_editor/catalog.py")
catalog = importlib.util.module_from_spec(spec)
sys.modules["catalog"] = catalog
spec.loader.exec_module(catalog)

CARCASS = (0.82, 0.82, 0.80, 1.0)
WOOD = (0.62, 0.40, 0.22, 1.0)
ACCENT = (0.20, 0.45, 0.85, 1.0)
DARK = (0.12, 0.12, 0.12, 1.0)
METAL = (0.60, 0.62, 0.66, 1.0)
GLASS = (0.55, 0.75, 0.85, 1.0)

W, H, D, T = 0.6, 0.7, 0.5, 0.018          # armário de referência


def reset_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    scene.render.engine = 'BLENDER_WORKBENCH'
    scene.display.shading.light = 'STUDIO'
    scene.display.shading.color_type = 'OBJECT'
    scene.display.shading.show_object_outline = True
    scene.display.shading.object_outline_color = (0.15, 0.15, 0.15)
    scene.render.resolution_x = scene.render.resolution_y = 128
    scene.render.film_transparent = True
    scene.render.image_settings.file_format = 'PNG'
    scene.render.image_settings.color_mode = 'RGBA'
    scene.render.image_settings.compression = 100
    return scene


def box(lo, hi, color):
    """Caixa de `lo` a `hi` (m; X largura, Y profundidade com a frente em 0, Z altura)."""
    size = [max(1e-4, hi[i] - lo[i]) for i in range(3)]
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=[(lo[i] + hi[i]) / 2.0 for i in range(3)])
    obj = bpy.context.active_object
    obj.scale = size
    obj.color = color
    return obj


def cylinder(lo, hi, color, rotation=(0.0, 0.0, 0.0)):
    radius = min(hi[0] - lo[0], hi[1] - lo[1]) / 2.0
    bpy.ops.mesh.primitive_cylinder_add(radius=radius, depth=hi[2] - lo[2], rotation=rotation,
                                        location=[(lo[i] + hi[i]) / 2.0 for i in range(3)])
    obj = bpy.context.active_object
    obj.color = color
    return obj


def carcass(back=True, top=True):
    box((0, 0, 0), (T, D, H), CARCASS)
    box((W - T, 0, 0), (W, D, H), CARCASS)
    box((T, 0, 0), (W - T, D, T), CARCASS)
    if top:
        box((T, 0, H - T), (W - T, D, H), CARCASS)
    if back:
        box((T, D - T, T), (W - T, D, H - T), CARCASS)


def fronts(count, color=WOOD, gap=0.003, z0=0.0, z1=H, x0=0.0, x1=W, pull=True):
    step = (z1 - z0) / count
    for i in range(count):
        lo, hi = z0 + i * step + gap, z0 + (i + 1) * step - gap
        box((x0 + gap, -T, lo), (x1 - gap, 0, hi), color)
        if pull:
            mid = (lo + hi) / 2.0 if count > 1 else hi - 0.08
            box(((x0 + x1) / 2 - 0.06, -T - 0.012, mid - 0.006), ((x0 + x1) / 2 + 0.06, -T, mid + 0.006), METAL)


def leaf(x0, x1, y, style, overlap=False):
    """Folha de correr com o detalhe do estilo (rasgo, quadro de alumínio, puxador integrado)."""
    box((x0, y, 0.02), (x1, y + T, H - 0.02), WOOD)
    face = y - 0.002
    if style.id == 'SLIDE_ALU_FRAME':
        box((x0 + 0.03, face, 0.05), (x1 - 0.03, y, H - 0.05), GLASS)
        return
    if style.groove:
        edge = x1 - 0.04 if not overlap else x0 + 0.02
        box((edge, face, 0.04), (edge + 0.02, y, H - 0.04), DARK)
    label = style.label.lower()
    if "almofada" in label or "colonial" in label or "country" in label:
        box((x0 + 0.04, face, 0.06), (x1 - 0.04, y, H - 0.06), (0.55, 0.35, 0.19, 1.0))
    elif "bicolor" in label:
        box((x0, face, H / 2), (x1, y, H - 0.02), (0.90, 0.88, 0.84, 1.0))
    elif "borda" in label:
        box((x0, face, 0.02), (x0 + 0.01, y, H - 0.02), METAL)
        box((x1 - 0.01, face, 0.02), (x1, y, H - 0.02), METAL)
    elif "fresada" in label or "chanfrada" in label:
        for z in (0.2, 0.35, 0.5):
            box((x0 + 0.03, face, z), (x1 - 0.03, y, z + 0.006), DARK)


def scene_for(item):
    group, tab = item.group, item.tab
    if tab == 'DIVISIONS' and group == 'RECESS' and (item.param('orientation') == 'HORIZONTAL'
                                                      or item.param('kind') in ('INVISIBLE', 'DIVISION_ONLY')):
        carcass()                                   # feature 015: prateleiras e divisões sem peça
        front = (item.param('front') or 0.0) / 1000.0
        z = H / 2
        if item.param('kind') in ('INVISIBLE', 'DIVISION_ONLY'):
            for x in range(6):                      # linha tracejada: divide sem chapa
                x0 = T + x * (W - 2 * T) / 6
                box((x0, 0.02, z), (x0 + (W - 2 * T) / 12, D - T, z + 0.004), ACCENT)
        elif item.param('variant') == 'ARAMADA':
            for k in range(7):
                y = 0.03 + k * (D - 0.08) / 6
                box((T, y, z), (W - T, y + 0.006, z + 0.006), METAL)
        else:
            box((T, front, z), (W - T, D - T, z + T), ACCENT)
            if item.param('variant') == 'CORREDICA':
                box((T, 0.02, z - 0.012), (T + 0.012, D - 0.04, z), METAL)
                box((W - T - 0.012, 0.02, z - 0.012), (W - T, D - 0.04, z), METAL)
    elif tab == 'DIVISIONS' and group == 'RECESS':
        carcass(top=item.param('variant') != 'CORTA_SAR')
        front = (item.param('front') or 0.0) / 1000.0
        top = H if item.param('variant') == 'CORTA_SAR' else H - T
        box((W / 2 - T / 2, front, T), (W / 2 + T / 2, D - T - 0.015, top), ACCENT)
        if item.param('variant') == 'CORTA_SAR':
            box((T, 0.0, H - T), (W / 2 - T / 2, 0.1, H), CARCASS)
            box((W / 2 + T / 2, 0.0, H - T), (W - T, 0.1, H), CARCASS)
    elif tab == 'DIVISIONS' and group == 'SPACER':
        carcass()
        thick = item.param('thickness', 15.0) / 1000.0
        layers = 2 if thick > 0.02 else 1
        for i in range(layers):
            box((T + i * 0.015, 0.02, T), (T + (i + 1) * 0.015, D - T, H - T), ACCENT)
        if item.param('follow'):
            box((W / 2 - T / 2, 0.02, T), (W / 2 + T / 2, D - T, H - T), CARCASS)
    elif tab == 'DRAWERS':
        carcass()
        if group == 'TALL':
            fronts(2)
        elif group == 'INTERNAL':
            for i in range(3):
                z = T + 0.02 + i * 0.2
                box((T + 0.01, 0.03, z), (W - T - 0.01, D - 0.04, z + 0.15), ACCENT)
            box((0.003, -T, 0.003), (W / 2 - 0.003, 0, H - 0.003), (0.62, 0.40, 0.22, 0.35))
        elif group == 'FRONTS':
            box((0.0, -T, 0.0), (W, 0, H / 3), WOOD)
        else:
            fronts(3 if group == 'BLUM' else 4)
            if group == 'BLUM':
                for z in (0.12, 0.35, 0.58):
                    box((T, 0.02, z), (T + 0.012, D - 0.04, z + 0.02), METAL)
    elif tab == 'BACKS':
        carcass(back=False)
        setback = 0.06 if group == 'RECESSED' else 0.0
        box((T, D - T - setback, T), (W - T, D - setback, H - T), ACCENT)
    elif tab == 'INTERIOR':
        interior(item)
    elif tab == 'SLIDING':
        carcass()
        leaf(0.0, W / 2 + 0.03, -2 * T - 0.01, item)
        leaf(W / 2 - 0.03, W, -T, item, overlap=True)
        box((0, -2 * T - 0.02, H), (W, 0, H + 0.015), METAL)
    else:
        carcass()


def wardrobe(item):
    """Internos de roupeiro (feature 015)."""
    carcass()
    kind = item.param('kind')
    box((T, 0.0, H - 0.12), (W - T, D - T, H - 0.12 + T), CARCASS)     # prateleira de cima
    if kind == 'HANGER_ROD':
        box((T + 0.01, 0.04, H - 0.3), (W - T - 0.01, 0.07, H - 0.27), ACCENT)     # à frente, para aparecer
    elif kind == 'PANTS_RACK':
        color = METAL if item.param('material') == 'WIRE' else ACCENT
        for k in range(5):
            x = T + 0.04 + k * (W - 2 * T - 0.08) / 4
            box((x, 0.05, H - 0.25), (x + 0.012, D - T, H - 0.238), color)
    elif kind == 'SHOE_RACK':
        box((T, 0.05, T), (W - T, D - T, T + 0.03), ACCENT)
        box((T, 0.05, T + 0.15), (W - T, D - T, T + 0.18), ACCENT)
    elif kind == 'BELT_RACK':
        box((T, 0.05, H / 2 - 0.04), (T + 0.03, 0.45, H / 2 + 0.04), METAL)


def interior(item):
    if item.group == 'WARDROBE':
        wardrobe(item)
        return
    carcass()
    if item.group == 'PISTONS':
        box((0.003, -T, H * 0.55), (W - 0.003, 0, H), WOOD)
        cylinder((T + 0.01, 0.05, 0.2), (T + 0.04, 0.08, 0.55), METAL, rotation=(math.radians(-25), 0, 0))
        return
    if item.group == 'SUPPORTS':
        box((T, 0.0, 0.3), (W - T, D - T, 0.3 + T), ACCENT)
        return
    size = item.size_mm
    if item.id in catalog.APPLIANCE_SIZE_MM:
        w, h = size[0] / 1000.0 * 0.8, size[1] / 1000.0 * 0.8
        box((W / 2 - w / 2, 0.02, 0.1), (W / 2 + w / 2, D - 0.05, 0.1 + h), DARK)
        box((W / 2 - w / 2 + 0.03, 0.015, 0.13), (W / 2 + w / 2 - 0.03, 0.02, 0.1 + h - 0.06), GLASS)
        return
    if item.id == 'VENT':
        box((T, -T, 0.0), (W - T, 0.0, H), WOOD)
        box((0.12, -T - 0.002, 0.08), (W - 0.12, -T + 0.004, 0.11), DARK)
        return
    inset = item.filter == 'BUILT_IN'
    y0 = 0.02 if inset else -T
    box((T if inset else 0.0, y0, 0.0), (W - T if inset else W, y0 + T, H), WOOD)
    appliances = item.param('appliances', ()) or ()
    z = 0.08
    for key in appliances:
        h = catalog.APPLIANCE_SIZE_MM[key][1] / 1000.0 * 0.5
        box((0.08, y0 - 0.002, z), (W - 0.08, y0 + T + 0.002, z + h), DARK)
        z += h + 0.04


def camera(scene):
    bpy.ops.object.camera_add()
    cam = bpy.context.active_object
    cam.data.type = 'ORTHO'
    cam.data.ortho_scale = 1.15
    target = Vector((W / 2, D / 2, H / 2))
    cam.location = target + Vector((0.9, -1.6, 0.8))
    cam.rotation_euler = (target - cam.location).to_track_quat('-Z', 'Y').to_euler()
    scene.camera = cam


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    count = 0
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    only_missing = "--only-missing" in argv
    for item in catalog.ITEMS:
        if only_missing and (OUT / (item.thumb + ".png")).exists():
            continue
        scene = reset_scene()
        scene_for(item)
        camera(scene)
        scene.render.filepath = str(OUT / (item.thumb + ".png"))
        bpy.ops.render.render(write_still=True)
        count += 1
    print(f"{count} miniaturas em {OUT}")


main()
