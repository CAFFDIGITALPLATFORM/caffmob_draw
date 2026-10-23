"""Regras dimensionais no Blender: LEDs, recortes, UV e RF-012 (T026)."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import _authored_env as a
import bpy
from mathutils import Vector
from caffmob_draw.aggregates import leaf, ops_authored, ops_authored_leaf, ops_members, stretch
from caffmob_draw.selection import classify, editing, element_size, resize
from caffmob_draw.collision import guard


def check(condition, message):
    assert condition, message
    print('OK:', message, flush=True)


def part(root, name, size, location, rule='FIXED', role='CARCASS', refs=()):
    obj = a.cube(name, size, location, root)
    ops_members.set_member(obj, root, role, reparent=False)
    obj.btm_member.rule = rule
    for target, face in refs:
        ref = obj.btm_member.refs.add()
        ref.target, ref.uid, ref.face = target, target.btm_member.uid, face
    return obj


def box(obj):
    return stretch._box(root, obj, bpy.context.evaluated_depsgraph_get())


a.env.clean_scene()
root = bpy.data.objects.new('Armário', None)
bpy.context.collection.objects.link(root)
left = a.cube('Lateral esquerda', (.015, .4, 2.6), (.0075, 0, 1.3), root)
right = a.cube('Lateral direita', (.015, .4, 2.6), (.6075, 0, 1.3), root)
ops_authored.adopt(root, [root, left, right])
right.btm_member.rule = 'ANCHORED'
panel = part(root, 'Tampo com 16 rasgos', (.585, .4, .015), (.3075, 0, 2.5925), 'FIT_BETWEEN',
             refs=[(left, 'POS_X'), (right, 'NEG_X')])
# UV afim explícita, em escala física: um metro = uma repetição.
layer = panel.data.uv_layers.active
for loop in panel.data.loops:
    point = panel.data.vertices[loop.vertex_index].co
    layer.data[loop.index].uv = (point.x, point.y)
material = bpy.data.materials.new('Madeira UV')
material.use_nodes = True
coords = material.node_tree.nodes.new('ShaderNodeTexCoord')
tex = material.node_tree.nodes.new('ShaderNodeTexChecker')
material.node_tree.links.new(coords.outputs['UV'], tex.inputs['Vector'])
material.node_tree.links.new(tex.outputs['Color'], material.node_tree.nodes.get('Principled BSDF').inputs['Base Color'])
panel.data.materials.append(material)
leds, cutters = [], []
for index in range(16):
    x = .03 + index * .035
    led = part(root, 'LED {:02}'.format(index), (.01, .01, .005), (x, 0, 2.6), 'DISTRIBUTE', 'LED',
               [(left, 'POS_X'), (right, 'NEG_X')])
    led.btm_member.count = 16
    led.btm_member.offset_mm = 10
    cutter = part(root, 'Rasgo {:02}'.format(index), (.012, .012, .03), (x, 0, 2.6), 'ANCHORED', 'CUTTER',
                  [(led, 'POS_X')])
    cutter['IS_CUTTING_OBJ'] = True
    cutter.hide_render = True
    cutter.display_type = 'WIRE'
    mod = panel.modifiers.new('Rasgo {:02}'.format(index), 'BOOLEAN')
    mod.object = cutter
    leds.append(led)
    cutters.append(cutter)
hardware = part(root, 'Ferragem', (.02, .03, .04), (.58, 0, 1.3), 'ANCHORED', 'HARDWARE',
                [(right, 'NEG_X')])
a.env.settle()
# Compartilhamento de malha e material: a outra cópia não pode mudar.
other = bpy.data.objects.new('Outra chapa', panel.data)
bpy.context.collection.objects.link(other)
other.location = (4, 0, 0)
original_uvs = [tuple(v.uv) for v in panel.data.uv_layers.active.data]
original_scale = {o: tuple(o.scale) for o in root.children_recursive}
vertices = [tuple(v.co) for v in panel.data.vertices]
light = bpy.data.objects.new('Fita AREA', bpy.data.lights.new('Área', 'AREA'))
bpy.context.collection.objects.link(light)
ops_members.set_member(light, root, 'LIGHT')
light.btm_member.rule = 'FIT_BETWEEN'
for target, face in [(left, 'POS_X'), (right, 'NEG_X')]:
    ref = light.btm_member.refs.add()
    ref.target, ref.uid, ref.face = target, target.btm_member.uid, face
light.data.size = .585
before_hw = tuple(hardware.dimensions)
check(editing.set_dimension(bpy.context, classify.classify(root), 'width', .835), 'redimensionar AUTHORED pela edição')
a.env.settle()
check(abs(editing.get_dimension(classify.classify(root), 'width') - .835) < 1e-6, 'medida dimensional atualizada')
check(all(tuple(o.scale) == scale for o, scale in original_scale.items()), 'nenhuma escala alterada')
check(tuple(hardware.dimensions) == before_hw, 'ferragem mantém seção e espessura')
check(len(leds) == len(cutters) == 16 and all(abs(led.matrix_world.translation.x - cutter.matrix_world.translation.x)
      < 1e-6 for led, cutter in zip(leds, cutters)), '16 LEDs seguem alinhados com seus rasgos')
check(sum(m.type == 'BOOLEAN' for m in panel.modifiers) == 16, '16 cortadores continuam vinculados')
check(panel.modifiers[0].name.startswith('Esticar'), 'Esticar precede os recortes')
from mathutils.bvhtree import BVHTree
bvh = BVHTree.FromObject(panel, bpy.context.evaluated_depsgraph_get())
inv = panel.matrix_world.inverted_safe()
check(all(bvh.ray_cast(inv @ Vector((led.matrix_world.translation.x, 0, 2.7)), Vector((0, 0, -1)), 1)[0] is None
          for led in leds), '16 rasgos reais permanecem vazados na chapa avaliada')
check([tuple(v.co) for v in panel.data.vertices] == vertices, 'malha autoral original intacta')
check(abs((box(panel)[1][0] - box(panel)[0][0]) - 805) < .05, 'vértices estendidos por 220 mm')
check(abs((box(panel)[1][2] - box(panel)[0][2]) - 15) < .01, 'MDF continua 15 mm')
check(abs(light.data.size - .805) < 1e-5, 'luz AREA muda size')
check(panel.data is not other.data and other.data.materials[0] == material,
      'cópia compartilha material e preserva malha')
check([tuple(v.uv) for v in other.data.uv_layers.active.data] == original_uvs, 'UV da outra cópia intacta')
uvs = [tuple(v.uv) for v in panel.data.uv_layers.active.data]
check(abs(max(v[0] for v in uvs) - min(v[0] for v in uvs) - .805) < 1e-5,
      'UV repete em escala física, sem esticar textura')
# Voltar e repetir não acumula modificadores nem deriva.
check(resize.resize(bpy.context, element_size.element(panel), .615), 'Redimensionar pela seleção do membro')
check(abs((box(panel)[1][0] - box(panel)[0][0]) - 585) < .05, 'voltar restaura comprimento')
check(all(abs(v.uv[k] - base[k]) < 1e-6 for v, base in zip(panel.data.uv_layers.active.data, original_uvs)
          for k in range(2)), 'voltar restaura UV')
# A parede está fora da pose original e dentro da nova medida.
wall = a.cube('Obstáculo', (.05, 1, 3), (.8, 0, 1.5))
a.env.settle()
# BUG-20261023-TAMR (RF03): a medida que sobrepõe vale; editar medida não é deslocamento.
check(editing.set_dimension(bpy.context, classify.classify(root), 'width', .835), 'RF03 aceita a medida que sobrepõe')
check(abs(root.btm_authored.size_local[0] - 835) < .01, 'RF03 grava a medida pedida')
check(resize.resize(bpy.context, element_size.element(panel), .615), 'voltar à medida anterior')
bpy.data.objects.remove(wall, do_unlink=True)
# Regras impossíveis e coordenadas Generated não deixam uma edição parcial.
ref = left.btm_member.refs.add()
ref.target, ref.face = panel, 'POS_X'
try:
    editing.set_dimension(bpy.context, classify.classify(root), 'width', .835)
except ValueError as exc:
    check('Ciclo' in str(exc), 'ciclo dimensional recusado')
else:
    raise AssertionError('Ciclo deveria recusar')
left.btm_member.refs.clear()
check(abs(root.btm_authored.size_local[0] - 615) < .01, 'ciclo mantém medida anterior')
material.node_tree.links.new(coords.outputs['Generated'], tex.inputs['Vector'])
try:
    editing.set_dimension(bpy.context, classify.classify(root), 'width', .835)
except ValueError:
    pass
else:
    raise AssertionError('Generated deveria pedir coordenadas físicas')
check(abs(root.btm_authored.size_local[0] - 615) < .01, 'Generated recusado antes de esticar textura')
material.node_tree.links.new(coords.outputs['UV'], tex.inputs['Vector'])
# A folha aberta conserva a abertura e passa a fechar na nova geometria, sem deriva.
front = part(root, 'Folha dimensional', (.585, .01, 2.5), (.3075, -.25, 1.3), 'FIT_BETWEEN',
             'LEAF_PART', [(left, 'POS_X'), (right, 'NEG_X')])
ops_authored_leaf.configure([front], root, closed_pose=True)
front.btm_aggregate.open_value = .4
a.env.settle()
check(editing.set_dimension(bpy.context, classify.classify(root), 'width', .835), 'redimensionar com folha aberta')
check(abs(leaf.current_fraction(front) - .4) < 1e-6, 'regra preserva abertura da folha')
front.btm_aggregate.open_value = 0
a.env.settle()
closed = front.matrix_world.copy()
check(abs(box(front)[1][0] - box(front)[0][0] - 805) < .1, 'folha fecha com a nova largura')
for _ in range(5):
    leaf.apply_fraction(front, .4)
    leaf.apply_fraction(front, 0)
    a.env.settle()
check(a.matrix_error(front.matrix_world, closed) < 1e-6, 'nova pose fechada sem deriva')
from caffmob_draw.customize import library_io
paths, errors = library_io.save(bpy.context, root, 'Regras com Esticar', 'Ensaio', thumbnail=False)
check(not errors, 'biblioteca salva GN Esticar: ' + str(errors))
with guard.suspended():
    instance, objects, errors = library_io.load(bpy.context, dict(paths, has_manifest=True))
check(instance is not None and not errors, 'biblioteca reinserida conserva regras e Esticar: ' + str(errors))
# Um vão entre membros de outro armário passa de 579,4 a 799,4 mm.
a.env.clean_scene()
root = bpy.data.objects.new('Complemento', None)
bpy.context.collection.objects.link(root)
ops_authored.adopt(root, [root], size=(579.4, 400, 1000))
tower, tower_body = a.tower('Torre externa', x=1)
left = part(root, 'Referência fixa', (.015, .1, .1), (.0075, 0, .05))
tower_body.location.x = -.1056  # face mínima: 594,4 mm no referencial do complemento
refs = [(left, 'POS_X'), (tower_body, 'NEG_X')]
slab = part(root, 'Bancada entre componentes', (.5794, .4, .015), (.3047, 0, .5), 'FIT_BETWEEN', refs=refs)
a.env.settle()
with guard.suspended():
    tower.location.x += .220
    a.env.settle()
check(stretch.update_links(bpy.context), 'Atualizar vínculos aceita referência de outro componente')
a.env.settle()
check(abs(box(slab)[1][0] - box(slab)[0][0] - 799.4) < .1, 'vão externo de 579,4 para 799,4 mm')
with guard.suspended():
    tower.location.x -= 2
    a.env.settle()
before = box(slab)
try:
    stretch.update_links(bpy.context)
except ValueError:
    pass
else:
    raise AssertionError('Vão negativo deveria recusar')
check(box(slab) == before, 'vão negativo bloqueia sem mutação')
print('PASSOU: regras dimensionais 066')
