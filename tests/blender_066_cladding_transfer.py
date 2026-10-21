"""T083: transferir portal, criar/redimensionar/excluir vão e sincronização automática."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import bpy
import _cladding_env as a
from caffmob_draw.cladding import ops_adopt, sync
from caffmob_draw.collision import guard
from caffmob_draw.openings import ops_transfer


def front_area(root):
    return sum(f.area for obj in a.pieces(root).values() for f in obj.data.polygons if f.normal.z > .99)


walls, source, door, window, origin = a.scene()
with guard.suspended():
    target = next(w for w in walls if w != source and abs(w.rotation_euler.z-source.rotation_euler.z) > .1)
    destination = ops_adopt.create(target)
    sync.sync(destination)
    a.env.settle()
before = front_area(origin), front_area(destination)
ok, reason = ops_transfer.transfer(bpy.context, door, target, distance=1600)
a.check(ok, 'portal transferido: '+reason)
a.env.settle()
a.check(front_area(origin)>before[0]+1 and front_area(destination)<before[1]-1,
        'tábuas voltam na origem e se interrompem no destino')
# A revisão do hash é automática pelo depsgraph, sem chamar sync explicitamente.
previous = origin.btm_cladding.params_hash
with guard.suspended():
    window.location.x += .15
    a.env.settle()
a.check(origin.btm_cladding.params_hash != previous, 'mover janela dispara sincronização')
previous = origin.btm_cladding.params_hash
with guard.suspended():
    a.hb_types.GeoNodeCage(window).set_input('Dim X', 1.4)
    a.env.settle()
a.check(origin.btm_cladding.params_hash != previous, 'redimensionar janela dispara sincronização')
previous = front_area(origin)
with guard.suspended():
    bpy.data.objects.remove(window,do_unlink=True)
    a.env.settle()
a.check(front_area(origin)>previous+.5, 'excluir janela recompõe as tábuas automaticamente')
previous = front_area(origin)
with guard.suspended():
    new = a.oe.make_cage(kind='WINDOW')
    new.parent, new.location = source, (2.5,0,.8)
    a.dw.cut_wall(source,new)
    a.env.settle()
a.check(front_area(origin)<previous-.5, 'criar janela interrompe as tábuas automaticamente')
print('T083 OK',flush=True)
