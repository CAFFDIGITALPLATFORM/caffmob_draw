"""BUG-20261017-5GYF: frente, fundo, pivô, abertura e corte no Blender sem janela.

Reprodução: as folhas antigas ficam em Y positivo, atrás do fundo; mede todos os casos antes de falhar.
Regressão: fecha o vão em -profundidade, preserva fundo/corte e abre para fora, inclusive após resize.
MOBI: baixa pelo operador 063 com transporte simulado, sem rede nem conversão para a 015.
"""
import hashlib
import json
import math
import sys
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _blender_env as env
import bpy
from caffmob_draw.geometry import door_controller as dc, mesh_gen
from caffmob_draw.cutting import part_sources
from caffmob_draw.texture_library import downloads

FAILURES = []
EPS = 1e-5


def check(label, condition):
    if not condition:
        FAILURES.append(label)
        print('FALHA ' + label, flush=True)


def settle():
    for _ in range(3):
        bpy.context.view_layer.update()


def bounds(points):
    return tuple(min(p[i] for p in points) for i in range(3)), tuple(max(p[i] for p in points) for i in range(3))


def leaf_box(root, leaf):
    ob = leaf.evaluated_get(bpy.context.evaluated_depsgraph_get())
    matrix = root.matrix_world.inverted() @ ob.matrix_world
    return bounds([matrix @ v.co for v in ob.data.vertices])


def records(root):
    module = next(m for m in part_sources.iter_modules(bpy.context.scene) if m.obj == root)
    return part_sources.synthetic_records(module, lambda c: 15.0)


def verify(root, label):
    cab = root.btm_cabinet
    settle()
    doors = dc.doors_of(root)
    boxes = [leaf_box(root, d) for d in doors]
    back_points = [root.data.vertices[i].co for p in root.data.polygons
                   if p.material_index == mesh_gen.MAT_BACK for i in p.vertices]
    check(label + ' fundo existe', bool(back_points))
    if not back_points:
        return
    back = bounds(back_points)
    print('MEDIDA ' + json.dumps({'caso': label, 'eixo': 'Y local', 'frente': -cab.depth,
          'portas': [[round(lo[1], 6), round(hi[1], 6)] for lo, hi in boxes],
          'fundo': [round(back[0][1], 6), round(back[1][1], 6)]}, ensure_ascii=False), flush=True)
    check(label + ' folhas na face frontal', bool(boxes) and all(
        abs(hi[1] + cab.depth) < EPS and abs(lo[1] + cab.depth + cab.thickness) < EPS
        for lo, hi in boxes))
    # Dois pontos dentro do vão, longe da folga central de portas duplas.
    for x in (-cab.width / 4, cab.width / 4):
        check(label + f' frente fechada em x={x:.3f}', any(
            lo[0] < x < hi[0] and lo[2] < cab.height / 2 < hi[2]
            and abs(hi[1] + cab.depth) < EPS for lo, hi in boxes))
    check(label + ' fundo no lado oposto', -cab.depth / 2 < back[0][1] <= back[1][1] <= EPS)
    recs = records(root)
    fronts = [r for r in recs if r.component == 'POR']
    check(label + ' folhas e corte mesma quantidade', len(fronts) == len(doors))
    for r, (lo, hi) in zip(fronts, boxes):
        check(label + ' dimensões das portas no corte', abs(r.width - (hi[0] - lo[0]) * 1000) < .01
              and abs(r.length - (hi[2] - lo[2]) * 1000) < .01
              and abs(r.thickness - (hi[1] - lo[1]) * 1000) < .01)
    check(label + ' corte contém fundo', any(r.component.startswith('FUN') for r in recs))
    signature = sorted((r.component, r.name, round(r.length, 3), round(r.width, 3),
                        round(r.thickness, 3), r.quantity, tuple(r.edges_present)) for r in recs)
    print('CORTE ' + label + ' ' + hashlib.sha256(json.dumps(signature).encode()).hexdigest(), flush=True)
    controller = dc.get_child_by_name(root, '_Controller')
    evaluated = controller.evaluated_get(bpy.context.evaluated_depsgraph_get())
    position = root.matrix_world.inverted() @ evaluated.matrix_world.translation
    check(label + ' controlador na frente', abs(position.y + cab.depth + cab.thickness) < EPS)
    check(label + ' controlador no puxador', abs(position.x - (cab.width / 2 - .03)) < EPS
          and abs(position.z - cab.height / 2) < EPS)
    # O mesmo método usado pelo callback do slider, com avaliação real dos drivers.
    cab.door_open = 1.0
    dc.update_door_rotation_from_property(root)
    settle()
    for leaf in doors:
        lo, hi = leaf_box(root, leaf)
        check(label + ' abre para fora ' + leaf.name, lo[1] < -cab.depth - .1 and hi[1] <= -cab.depth + EPS)
        axis = 0 if leaf.name.endswith('_Door_Flip') else 2
        angle = leaf.evaluated_get(bpy.context.evaluated_depsgraph_get()).rotation_euler[axis]
        check(label + ' abertura 90 graus', abs(abs(angle) - math.pi / 2) < 1e-4)
    # O gesto no controlador também atualiza as folhas e o slider (sentido inverso).
    controller.location.y += .1
    settle()
    check(label + ' gesto sincroniza 50 por cento', abs(root.evaluated_get(
        bpy.context.evaluated_depsgraph_get()).btm_cabinet.door_open - .5) < EPS)
    for leaf in doors:
        axis = 0 if leaf.name.endswith('_Door_Flip') else 2
        angle = leaf.evaluated_get(bpy.context.evaluated_depsgraph_get()).rotation_euler[axis]
        check(label + ' gesto abre 45 graus', abs(abs(angle) - math.pi / 4) < 1e-4)
    cab.door_open = 1.0
    dc.update_door_rotation_from_property(root)
    settle()
    check(label + ' slider sincronizado', abs(root.evaluated_get(
        bpy.context.evaluated_depsgraph_get()).btm_cabinet.door_open - 1.0) < EPS)
    cab.door_open = 0.0
    dc.update_door_rotation_from_property(root)
    settle()
    for leaf in doors:
        pull = dc.set_door_pull(root, leaf, pull_source)
        settle()
        lo, hi = leaf_box(root, pull)
        check(label + ' puxador fora da folha', lo[1] < -cab.depth - cab.thickness - .01
              and hi[1] <= -cab.depth - cab.thickness + EPS)


env.clean_scene()
pull_mesh = bpy.data.meshes.new('Puxador teste')
pull_mesh.from_pydata([(x, y, z) for x in (-.05, .05) for y in (-.02, 0) for z in (-.005, .005)], [], [])
pull_source = bpy.data.objects.new('Fonte de puxador não instanciada', pull_mesh)
recipes = {'BASE': 'coz_inferior_divisoria', 'WALL': 'coz_superior_divisoria', 'TALL': 'coz_torre_eletros'}
for structured in (False, True):
    for kind, recipe in recipes.items():
        for swing in ('LEFT', 'RIGHT', 'DOUBLE', 'FLIP'):
            env.clean_scene()
            kwargs = {'cabinet_type': kind, 'door_swing': swing, 'width': .8,
                      'height': 2.1 if kind == 'TALL' else .72, 'depth': .55, 'thickness': .015}
            if structured:
                kwargs['structure_id'] = recipe
            assert bpy.ops.caffmob.cabinet_builder(**kwargs) == {'FINISHED'}
            root = bpy.context.object
            root.btm_cabinet.has_back = True
            # Coordenadas mundiais deslocadas/rotacionadas não mudam a convenção local.
            root.location = (1.2, -2.3, .9)
            root.rotation_euler.z = .4
            label = ('015' if structured else 'legado') + '/' + kind + '/' + swing
            verify(root, label)
            # A edição paramétrica deve reconstruir pivôs e drivers com a nova profundidade.
            root.btm_cabinet.depth = .63
            verify(root, label + '/resize')

# Baixa de modelo com o operador real da 063; só o transporte é substituído.
env.clean_scene()
mod = json.loads((Path(__file__).parent / 'casos_ouro/pecas-addon/pecas-addon-base-double.json').read_text())['entrada']
pending = []
def request(method, path, body=None, **kwargs):
    pending.append(kwargs['callback'])
    return {'rid': len(pending)}

with patch.object(downloads, 'request', side_effect=request):
    assert bpy.ops.caffmob.mobi_baixar_modelo(modelo_id=mod['id'], escopo='titular') == {'FINISHED'}
    pending.pop()(200, mod, {'ETag': '"1"'})
root = bpy.context.object
settle()
check('MOBI baixado pela 063', bool(root.get('caffmob_modulo')) and not root.children
      and not root.btm_cabinet.structure_id)
# Cada chapa é um componente conexo na malha recebida. Mede a malha de verdade, sem usar caixas do gerador.
neighbors = {v.index: set() for v in root.data.vertices}
for edge in root.data.edges:
    a, b = edge.vertices
    neighbors[a].add(b)
    neighbors[b].add(a)
components = []
while neighbors:
    stack, seen = [next(iter(neighbors))], set()
    while stack:
        i = stack.pop()
        if i in seen:
            continue
        seen.add(i)
        stack.extend(neighbors[i] - seen)
    components.append(bounds([root.data.vertices[i].co for i in seen]))
    for i in seen:
        del neighbors[i]
fronts = [(lo, hi) for lo, hi in components if hi[1] <= -.55 + EPS]
backs = [(lo, hi) for lo, hi in components if abs((hi[1] - lo[1]) - .006) < EPS]
print('MEDIDA MOBI ' + json.dumps({'frente': -.55, 'portas': fronts, 'fundo': backs}), flush=True)
check('MOBI frente fechada', len(fronts) == 2 and all(abs(hi[1] + .55) < EPS for lo, hi in fronts))
check('MOBI fundo no fundo', len(backs) == 1 and backs[0][0][1] > -.03)
module = next(m for m in part_sources.iter_modules(bpy.context.scene) if m.obj == root)
parts = part_sources.caffmob_parts(module)
expected = json.loads((Path(__file__).parent / 'casos_ouro/pecas-addon/pecas-addon-base-double.json').read_text())['esperado']['pecas']
check('MOBI corte preservado', len(parts) == len(expected) and all(
    all(getattr(part, k) == entry[k] for k in ('width', 'height', 'thickness', 'quantity'))
    for part, entry in zip(parts, expected)))
print(f'BUG_5GYF: {len(FAILURES)} falhas; 24 cenários, 48 medições do construtor e 1 modelo MOBI', flush=True)
assert not FAILURES, '\n'.join(FAILURES)
