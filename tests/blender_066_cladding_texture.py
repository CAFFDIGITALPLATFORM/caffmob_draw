"""T032/T068: imagem local temporária, continuidade e materiais compartilhados imutáveis."""
import sys
import tempfile
import math
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import bpy
import _cladding_env as a
from caffmob_draw.cladding import ops, presets, sync
from caffmob_draw.object_library import retexture

walls, wall, door, window, root = a.scene()
with tempfile.TemporaryDirectory() as folder:
    path = str(Path(folder)/'madeira.png')
    image = bpy.data.images.new('Imagem sintética', width=8, height=8)
    image.filepath_raw, image.file_format = path, 'PNG'
    image.save()
    shared = retexture.image_material(path, 1000)
    before = [(n.type,tuple(n.inputs['Scale'].default_value)) for n in shared.node_tree.nodes if n.type=='MAPPING']
    root.btm_cladding.texture = path
    root.btm_cladding.grain_angle = 23
    sync.sync(root)
    items = a.pieces(root)
    mat = next(iter(items.values())).data.materials[0]
    a.check(mat != shared and all(o.data.materials[0] == mat for o in items.values()),
            'material independente e comum às peças')
    coords = next(n for n in mat.node_tree.nodes if n.type=='TEX_COORD')
    mapping = next(n for n in mat.node_tree.nodes if n.type=='MAPPING')
    a.check(coords.object == root, 'coordenada Object do controlador preserva continuidade entre módulos')
    a.check(abs(mapping.inputs['Rotation'].default_value.z-math.radians(23)) < 1e-6, 'veio pelo ângulo configurado')
    root.btm_cladding.width_mm = 230
    sync.sync(root)
    a.check(all(o.data.materials[0] == mat for o in a.pieces(root).values()),
            'redimensionar altera recorte sem esticar padrão')
    root.btm_cladding.texture_size_mm = 500
    sync.sync(root)
    newer = next(iter(a.pieces(root).values())).data.materials[0]
    a.check(newer != mat, 'escala nova gera material novo')
    newer_mapping = next(n for n in newer.node_tree.nodes if n.type=='MAPPING')
    a.check(tuple(newer_mapping.inputs['Scale'].default_value)==(2,2,2), 'escala de 500 mm em metros')
    shared_now = [(n.type, tuple(n.inputs['Scale'].default_value))
                  for n in shared.node_tree.nodes if n.type == 'MAPPING']
    a.check(shared_now == before,
            'material compartilhado original intacto')
    a.check(tuple(mapping.inputs['Scale'].default_value)==(1,1,1), 'material anterior também intacto')
    rectangular = bpy.data.images.new('Imagem retangular', width=16, height=8)
    rectangular.filepath_raw, rectangular.file_format = str(Path(folder)/'retangular.png'), 'PNG'
    rectangular.save()
    root.btm_cladding.texture = rectangular.filepath_raw
    root.btm_cladding.texture_size_mm = 1000
    sync.sync(root)
    rect_mat = next(iter(a.pieces(root).values())).data.materials[0]
    rect_mapping = next(n for n in rect_mat.node_tree.nodes if n.type == 'MAPPING')
    a.check(tuple(rect_mapping.inputs['Scale'].default_value) == (1, 2, 2),
            'imagem retangular mantém a proporção física original')
    result = bpy.ops.caffmob.cladding_preset(action='COMPANY', preset='ripado_mdf')
    staged = bpy.context.scene.btm_cladding_settings
    a.check(result == {'FINISHED'} and staged.kind == 'SLATS' and staged.backing
            and staged.material is not None and staged.backing_material is not None,
            'preset da empresa reaplica parâmetros e acabamentos no Blender')
    value = ops.preset_from(staged, 'Ripado salvo')
    presets.save(Path(folder)/'preset.json', value)
    ops.apply_preset(staged, presets.load(Path(folder)/'preset.json'))
    a.check(ops.preset_from(staged, 'Ripado salvo') == value, 'gravar e reaplicar conserva os acabamentos')
print('T032/T068 OK', flush=True)
