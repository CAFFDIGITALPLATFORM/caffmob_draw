"""Materiais imutáveis em escala física; o controlador é a referência comum (D-21/RN-14)."""
import math
import bpy  # type: ignore
from ..object_library import retexture


def resolve(controller, role='FACE'):
    data = controller.btm_cladding
    if role == 'BACKING' and data.backing_material:
        return data.backing_material
    if not data.texture:
        return data.material
    path = bpy.path.abspath(data.texture)
    image = bpy.data.images.load(path, check_existing=True)
    width, height = image.size
    height_mm = data.texture_size_mm * height / width if width else data.texture_size_mm
    base = retexture.image_material(path, data.texture_size_mm, height_mm)
    # O material base de retexture nunca é alterado, mesmo se ainda não tiver usuários.
    signature = (data.uid, data.texture, float(data.texture_size_mm), float(data.grain_angle))
    key = repr(signature)
    for mat in bpy.data.materials:
        if mat.get('btm_cladding_texture') == key:
            return mat
    mat = base.copy()
    mat.name = 'Revestimento: ' + base.name
    mat['btm_cladding_texture'] = key
    coords = next(n for n in mat.node_tree.nodes if n.type == 'TEX_COORD')
    mapping = next(n for n in mat.node_tree.nodes if n.type == 'MAPPING')
    coords.object = controller
    mapping.inputs['Rotation'].default_value.z = math.radians(data.grain_angle)
    return mat


def apply(obj, mat):
    if mat is not None:
        obj.data.materials.clear()
        obj.data.materials.append(mat)
