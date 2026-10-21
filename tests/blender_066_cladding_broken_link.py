"""T033/T070: adoção, cancelamento, salvar/reabrir e hospedeiro excluído."""
import sys
import tempfile
from pathlib import Path
from types import SimpleNamespace
sys.path.insert(0, str(Path(__file__).resolve().parent))
import bpy
import _cladding_env as a
from caffmob_draw.cladding import ops, ops_adopt, sync
from caffmob_draw.collision import guard

walls, wall, door, window, root = a.scene()
source = next(iter(a.pieces(root).values()))
manual = bpy.data.objects.new('Revestimento manual', source.data.copy())
bpy.context.collection.objects.link(manual)
manual.location=(.1,.3,.4)
material = bpy.data.materials.new('Autoral')
manual.data.materials.append(material)
with guard.suspended():
    a.env.settle()
before = manual.data.as_pointer(), manual.matrix_world.copy(), tuple(manual.data.materials), manual.parent
with guard.suspended():
    adopted = ops_adopt.adopt([manual], wall)
    sync.sync(adopted)
a.check((manual.data.as_pointer(),manual.matrix_world,tuple(manual.data.materials),manual.parent)==before,
        'adotar preserva malha, pose, material e hierarquia')
a.check(not manual['btm_cladding_piece']['generated'], 'adoção permanece manual')
a.check(manual.btm_plane.collision_override == 'OFF', 'acabamento adotado usa a exclusão existente de colisão')
# Executar o caminho modal de Esc sem uma janela: não há criação anterior à confirmação.
names = set(bpy.data.objects.keys())
op = SimpleNamespace(_end=lambda: None)
result = ops.BTM_OT_CladdingFace.modal(op, bpy.context, SimpleNamespace(type='ESC',value='PRESS'))
a.check(result=={'CANCELLED'} and set(bpy.data.objects.keys())==names, 'cancelar não cria nem altera objeto')
other = next(o for o in walls if o != wall)
with guard.suspended():
    bpy.data.objects.remove(wall, do_unlink=True)
    a.env.settle()
    sync.sync(root)
a.check(root.btm_cladding.host is None and root.btm_cladding.link_missing,
        'exclusão detectada sem escolher outra parede')
a.check('Reassociar' in root.btm_cladding.diagnostic, 'diagnóstico oferece reassociar')
a.check('Reassociar' in __import__('inspect').getsource(ops.BTM_PT_Cladding.draw),
        'painel oferece reassociação explícita')
# Reassociar o adotado não muda a peça manual.
ops_adopt.reassociate(adopted, other, (0,0,0), (0,-1,0), (1,0,0))
sync.sync(adopted)
a.check(manual.data.as_pointer()==before[0] and manual.matrix_world==before[1], 'reassociar preserva peça adotada')
with tempfile.TemporaryDirectory() as folder:
    name, uid = root.name, root.btm_cladding.uid
    bpy.ops.wm.save_as_mainfile(filepath=str(Path(folder)/'revestimento.blend'))
    bpy.ops.wm.open_mainfile(filepath=str(Path(folder)/'revestimento.blend'))
    a.check(bpy.data.objects[name].btm_cladding.uid==uid and bpy.data.objects[name].btm_cladding.host is None,
            'vínculo quebrado e identidade persistem ao reabrir')
print('T033/T070 OK', flush=True)
