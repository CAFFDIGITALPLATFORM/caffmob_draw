"""Retexturizar uma parte ou um item inteiro (feature 009, T020; RN-12, D-12).

- **Acabamento do plugin:** os materiais das bibliotecas de chapas (frameless, face frame, closets) e os que já estão no
  arquivo. Um material que ainda não está no arquivo é anexado do `.blend` de origem. Peças `GeoNodeCutpart` recebem o
  material nas duas faces (`common.set_cutpart_material`); as outras malhas, em todos os slots.
- **Imagem própria:** material "Textura: <arquivo> <tamanho> mm", com Image Texture em projeção de caixa (Box) sobre
  coordenadas de objeto e escala real (`1 / tamanho em metros`), o que serve para malha importada sem UV boa. Um
  material com o mesmo arquivo e o mesmo tamanho é reaproveitado.

A troca vale para a cópia na cena: salvar de novo na biblioteca é opcional.
"""

import math
import os

import bpy  # type: ignore

from ..customize.adapters import common

PACKAGE = os.path.dirname(os.path.dirname(__file__))
LIBRARIES = ("product_libraries/frameless/frameless_assets/materials/cabinet_material.blend",
             "product_libraries/face_frame/face_frame_assets/materials/cabinet_material.blend",
             "product_libraries/closets/assets/materials/library.blend")
PATH_PROP = 'btm_texture_path'
SIZE_PROP = 'btm_texture_size_mm'
ROTATED_PROP = 'btm_texture_rotated'
TEXTURE_ID_PROP = 'btm_texture_id'
_names_cache = {}


def library_materials():
    """{nome: caminho do .blend} dos acabamentos do plugin (lido uma vez por sessão)."""
    if not _names_cache:
        for rel in LIBRARIES:
            path = os.path.join(PACKAGE, rel)
            if not os.path.isfile(path):
                continue
            with bpy.data.libraries.load(path, link=False) as (data_from, _data_to):
                for name in data_from.materials:
                    _names_cache.setdefault(name, path)
    return _names_cache


def finish_names():
    """Acabamentos para escolher: os do plugin e os do arquivo (sem os de miniatura e os internos)."""
    names = set(library_materials()) | {m.name for m in bpy.data.materials if not m.name.startswith(".")}
    return sorted(names, key=str.lower)


def _finish(name):
    mat = bpy.data.materials.get(name)
    if mat is not None:
        return mat
    path = library_materials().get(name)
    if path is None:
        return None
    with bpy.data.libraries.load(path, link=False) as (_data_from, data_to):
        data_to.materials = [name]
    return data_to.materials[0] if data_to.materials else None


def targets(objs):
    return [o for o in objs if o.type == 'MESH']


def apply_finish(objs, name):
    """Aplica o acabamento `name`; devolve quantas malhas mudaram (0 se o material não existe)."""
    mat = _finish(name)
    if mat is None:
        return 0
    return sum(1 for obj in targets(objs) if common.set_cutpart_material(obj, mat))


def _size_of(mat):
    """(largura, altura) em mm gravados no material: float (imagem própria quadrada) ou par (feature 014)."""
    raw = mat.get(SIZE_PROP, 0.0)
    try:
        width, height = float(raw[0]), float(raw[1])
    except (TypeError, IndexError, KeyError):
        width = height = float(raw)
    return width, height


def material_name(path, width_mm, height_mm, rotated=False):
    size = "{:g} mm".format(width_mm) if abs(width_mm - height_mm) < 1e-6 else \
        "{:g} × {:g} mm".format(width_mm, height_mm)
    name = "Textura: {} {}".format(os.path.basename(path), size)
    return name + " ROTATED" if rotated else name      # convenção do veio girado ('<nome> ROTATED', common.rotated)


def image_material(path, size_mm, height_mm=None, rotated=False, texture_id=""):
    """Material de textura com escala real; reaproveita um igual (mesmo arquivo e tamanho).

    `size_mm` é a largura (e a altura, se `height_mm` faltar); chapa retangular escala cada eixo pelo seu lado
    (feature 014, D-08). `texture_id` marca o material como do catálogo de texturas (D-09).

    067 (onda 3, D-20; RF-063): o veio é girado por objeto pelo serviço de veio (`texture_library/grain`), num
    material só por textura. A variante '<nome> ROTATED' não é mais criada: `rotated` só reaproveita uma que já exista
    no arquivo (arquivos antigos, M-05); sem ela, devolve o material comum.
    """
    from ..texture_library import grain, grain_core
    path = os.path.abspath(path)
    width = float(size_mm)
    height = float(height_mm) if height_mm is not None else width
    for wanted in ((True, False) if rotated else (False,)):
        for mat in bpy.data.materials:
            if mat.get(PATH_PROP) == path and bool(mat.get(ROTATED_PROP, False)) == wanted:
                w, h = _size_of(mat)
                if abs(w - width) < 1e-6 and abs(h - height) < 1e-6:
                    if not wanted:
                        grain.ensure_graph(mat)
                    _attach_pbr(mat, texture_id)
                    return mat
    rotated = False
    image = bpy.data.images.load(path, check_existing=True)
    mat = bpy.data.materials.new(material_name(path, width, height, rotated))
    mat[PATH_PROP] = path
    mat[SIZE_PROP] = width if abs(width - height) < 1e-6 else [width, height]
    if rotated:
        mat[ROTATED_PROP] = True
    if texture_id:
        mat[TEXTURE_ID_PROP] = texture_id
    tree = mat.node_tree
    bsdf = next(n for n in tree.nodes if n.type == 'BSDF_PRINCIPLED')
    coords = tree.nodes.new('ShaderNodeTexCoord')
    mapping = tree.nodes.new('ShaderNodeMapping')
    tex = tree.nodes.new('ShaderNodeTexImage')
    tex.image = image
    tex.projection = 'BOX'
    tex.projection_blend = 0.2
    sx, sy = 1.0 / max(width / 1000.0, 1e-4), 1.0 / max(height / 1000.0, 1e-4)
    mapping.inputs['Scale'].default_value = (sx, sy, sy)
    if rotated:
        mapping.inputs['Rotation'].default_value = (0.0, 0.0, math.radians(90.0))
    coords.location, mapping.location, tex.location = (-900, 0), (-700, 0), (-450, 0)
    tree.links.new(coords.outputs['Object'], mapping.inputs['Vector'])
    tree.links.new(mapping.outputs['Vector'], tex.inputs['Vector'])
    tree.links.new(tex.outputs['Color'], bsdf.inputs['Base Color'])
    # Calibração inicial pela proporção da imagem (RF-061; editável no painel da peça).
    mat[grain.CALIBRATION] = grain_core.calibration_from_size(*image.size)
    grain.ensure_graph(mat)
    _attach_pbr(mat, texture_id)
    return mat


def _attach_pbr(mat, texture_id):
    """073 (T018): normal, rugosidade e metálico da textura do pacote, no mesmo mapeamento da cor."""
    if not texture_id:
        return
    from ..texture_library import catalog, pbr
    entry = catalog.pbr_item(texture_id)
    if entry and pbr.attach(mat, entry):
        from ..texture_library import grain
        grain.ensure_graph(mat)


def apply_image(objs, path, size_mm):
    mat = image_material(path, size_mm)
    return sum(1 for obj in targets(objs) if common.set_cutpart_material(obj, mat))
