"""Material liso da chapa nova (feature 067, D-29; RF-012).

"MDF Branco": Principled BSDF branco, sem textura, igual em toda instalação (não depende da biblioteca de texturas nem
de rede). É achado pela marca `btm_builtin_material`, não pelo nome: renomear o material não cria outro.
"""

import bpy  # type: ignore

MARK = 'btm_builtin_material'
MDF_BRANCO = 'MDF_BRANCO'
NAME = "MDF Branco"
WHITE = (0.9, 0.9, 0.88, 1.0)


def find(mark=MDF_BRANCO):
    return next((m for m in bpy.data.materials if m.get(MARK) == mark and m.library is None), None)


def ensure_mdf_branco():
    """O material "MDF Branco" do arquivo; cria na primeira vez e reaproveita depois."""
    material = find()
    if material is not None:
        return material
    material = bpy.data.materials.new(NAME)
    material[MARK] = MDF_BRANCO
    material.use_nodes = True
    material.diffuse_color = WHITE
    bsdf = next((n for n in material.node_tree.nodes if n.type == 'BSDF_PRINCIPLED'), None)
    if bsdf is not None:
        bsdf.inputs['Base Color'].default_value = WHITE
        bsdf.inputs['Roughness'].default_value = 0.6
    return material
