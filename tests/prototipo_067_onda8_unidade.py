"""Protótipo da onda 8 (T179; D-37): alinhar o `length_unit` ao `btm_unit` no `load_post`.

Prova, no Blender sem interface:
1. arquivo novo (`read_homefile`) chega com o `length_unit` do `btm_unit`;
2. arquivo salvo com a cena em metros e o projeto em mm abre em mm, com os vértices iguais e `scale_length` igual;
3. registra se abrir deixa o arquivo marcado como alterado (`is_dirty`).
"""
import os
import sys
import tempfile

import bpy
from bpy.app.handlers import persistent

TABELA = {'MILLIMETERS': 'MILLIMETERS', 'CENTIMETERS': 'CENTIMETERS', 'METERS': 'METERS'}


@persistent
def alinhar(*_args):
    scene = bpy.context.scene
    settings = getattr(scene, 'btm_settings', None)
    unidade = TABELA.get(getattr(settings, 'btm_unit', None))
    if unidade is None:
        return
    if scene.unit_settings.system != 'METRIC':
        scene.unit_settings.system = 'METRIC'
    if scene.unit_settings.length_unit != unidade:
        scene.unit_settings.length_unit = unidade


falhas = []


def conferir(ok, texto):
    print(('OK   ' if ok else 'FALHA ') + texto)
    if not ok:
        falhas.append(texto)


sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _blender_env  # noqa: E402,F401  (registra o pacote como os outros ensaios)
bpy.app.handlers.load_post.append(alinhar)

bpy.ops.wm.read_homefile(app_template="", use_empty=True)
cena = bpy.context.scene
conferir(cena.unit_settings.length_unit == 'MILLIMETERS', f"arquivo novo em mm (veio {cena.unit_settings.length_unit})")

bpy.ops.mesh.primitive_cube_add(size=2.6)
vertices = [tuple(v.co) for v in bpy.context.object.data.vertices]
cena.unit_settings.length_unit = 'METERS'
escala = cena.unit_settings.scale_length
caminho = os.path.join(tempfile.mkdtemp(prefix='caffmob_067_unidade_'), 'metros.blend')
bpy.ops.wm.save_as_mainfile(filepath=caminho)
bpy.ops.wm.open_mainfile(filepath=caminho)
cena = bpy.context.scene
conferir(cena.unit_settings.length_unit == 'MILLIMETERS', f"arquivo em metros abre em mm (veio {cena.unit_settings.length_unit})")
conferir(cena.unit_settings.scale_length == escala, "scale_length igual")
obj = next(o for o in cena.objects if o.type == 'MESH')
conferir([tuple(v.co) for v in obj.data.vertices] == vertices, "vértices iguais")
print('INFO is_dirty depois de abrir:', bpy.data.is_dirty)
sys.exit(1 if falhas else 0)
