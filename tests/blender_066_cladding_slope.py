"""T031/T069: superfície inclinada com escala/rotação e sem fresta entre hospedeiro e acabamento."""
import sys
import math
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import bpy
from mathutils import Matrix
import _cladding_env as a
from caffmob_draw.cladding import ops_adopt, sync
from caffmob_draw.collision import guard

with guard.suspended():
    a.env.clean_scene()
    mesh = bpy.data.meshes.new('Teto inclinado')
    # Plano qualquer, duas faces coplanares, uma delas triangulada.
    mesh.from_pydata([(0,0,0),(5.41,0,0),(5.41,3,0),(0,3,0)], [], [(0,1,2),(0,2,3)])
    host = bpy.data.objects.new('Teto', mesh)
    bpy.context.collection.objects.link(host)
    host.matrix_world = Matrix.Translation((.4,.7,2.6)) @ Matrix.Rotation(math.radians(27),4,'X')
    a.env.settle()
    root = ops_adopt.create(host, normal=(0,0,-1))
    root.btm_cladding.orientation = 'ANGLED'
    root.btm_cladding.angle = 33
    root.btm_cladding.joint_mm = 0
    sync.sync(root)
    a.env.settle()
    items = a.pieces(root)
    a.check(bool(items), 'tábuas inclinadas geradas')
    front_area = 0
    for obj in items.values():
        for face in obj.data.polygons:
            if face.normal.z > .99:
                front_area += face.area
        for vertex in obj.data.vertices:
            a.check(min(abs(vertex.co.z),abs(vertex.co.z-.015)) < 1e-6, 'espessura e base no plano')
            if abs(vertex.co.z) < 1e-6:
                world = obj.matrix_world @ vertex.co
                local = host.matrix_world.inverted() @ world
                a.check(abs(local.z) < 1e-6, 'sem fresta no teto inclinado')
    a.check(abs(front_area - 5.41*3) < .0001, 'área integral do teto coberta sem junta')
    old = root.matrix_world.copy()
    meshes = {key: obj.data.as_pointer() for key, obj in a.pieces(root).items()}
    host.location.x += .3
    a.env.settle()
    a.check(abs(root.matrix_world.translation.x-old.translation.x-.3) < 1e-6,
            'mover hospedeiro leva o controlador sem reconstruir malhas')
    a.check(all(obj.data.as_pointer()==meshes[key] for key,obj in a.pieces(root).items()),
            'translação do hospedeiro preserva as malhas')
print('T031/T069 OK', flush=True)
