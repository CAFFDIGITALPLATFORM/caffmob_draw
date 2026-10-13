"""Material de imagem com chapa retangular, veio e id do catálogo (feature 014, T024; D-08, RN-04, RN-06).

Run: blender --background --factory-startup --python-exit-code 1 --python tests/blender_014_image_material.py

- a chamada antiga `image_material(caminho, mm)` continua quadrada e reaproveitada;
- chapa retangular escala cada eixo pelo seu lado; o veio girado tem o nome '<nome> ROTATED' e rotação de 90°;
- o mesmo arquivo, tamanho e veio reaproveitam o material; o id do catálogo fica no material.
"""

import math
import os
import sys
import tempfile
import traceback
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _blender_env  # noqa: E402,F401
import bpy  # noqa: E402
from caffmob_draw.customize.adapters import common  # noqa: E402
from caffmob_draw.object_library import retexture  # noqa: E402

FAILURES = []


def check(name, ok, detail=""):
    print(("OK   " if ok else "FALHA ") + name, detail, flush=True)
    if not ok:
        FAILURES.append(name)


def mapping_of(mat):
    return next(n for n in mat.node_tree.nodes if n.type == 'MAPPING')


def main():
    image = bpy.data.images.new("chapa_014", 8, 8)
    path = os.path.join(tempfile.mkdtemp(), "chapa_014.png")
    image.filepath_raw, image.file_format = path, 'PNG'
    image.save()

    square = retexture.image_material(path, 600.0)
    scale = tuple(round(v, 4) for v in mapping_of(square).inputs['Scale'].default_value)
    check("quadrado: escala 1/0,6 nos 3 eixos", scale == (1.6667, 1.6667, 1.6667), str(scale))
    check("quadrado: tamanho gravado como número", isinstance(square.get('btm_texture_size_mm'), float))
    check("quadrado: reaproveitado", retexture.image_material(path, 600.0) == square)

    sheet = retexture.image_material(path, 1850.0, 2750.0, texture_id="arauco/tons-do-brasil/matt-jalapao")
    scale = tuple(round(v, 4) for v in mapping_of(sheet).inputs['Scale'].default_value)
    check("chapa: escala por eixo", scale == (round(1 / 1.85, 4), round(1 / 2.75, 4), round(1 / 2.75, 4)), str(scale))
    check("chapa: nome com os dois lados", sheet.name == "Textura: chapa_014.png 1850 × 2750 mm", sheet.name)
    check("chapa: id do catálogo", sheet.get('btm_texture_id') == "arauco/tons-do-brasil/matt-jalapao")
    check("chapa: material diferente do quadrado", sheet != square)

    turned = retexture.image_material(path, 1850.0, 2750.0, rotated=True)
    rotation = round(math.degrees(mapping_of(turned).inputs['Rotation'].default_value[2]), 3)
    check("veio: nome ROTATED e 90°", turned.name == sheet.name + " ROTATED" and rotation == 90.0,
          f"{turned.name} {rotation}")
    check("veio: common.rotated acha a variante", common.rotated(sheet) == turned)
    check("veio: reaproveitado sem trocar com o normal",
          retexture.image_material(path, 1850.0, 2750.0, rotated=True) == turned
          and retexture.image_material(path, 1850.0, 2750.0) == sheet)


try:
    main()
except Exception:
    traceback.print_exc()
    FAILURES.append("exceção no roteiro")
print(f"blender_014_image_material: {'OK' if not FAILURES else 'FALHAS: ' + ', '.join(FAILURES)}")
sys.exit(1 if FAILURES else 0)
