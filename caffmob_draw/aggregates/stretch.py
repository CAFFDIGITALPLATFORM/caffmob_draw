"""Aplicação dimensional por translação de vértices, sem escala (066, T060/T061).

O modificador precede recortes e ferragens; cada eixo guarda seu plano e deslocamento acumulado.
Coordenadas UV são prolongadas na mesma densidade de texel, sem reconstruir a malha autoral.
"""

import bpy  # type: ignore
from mathutils import Vector  # type: ignore

from .. import compat
from ..collision import guard
from ..data.i18n import tr
from . import group, leaf, rules
from .apply import _write

MARKER = 'btm_stretch_axis'
_busy = False


def _group():
    tree = bpy.data.node_groups.new('Esticar', 'GeometryNodeTree')
    tree.interface.new_socket(name='Geometria', in_out='INPUT', socket_type='NodeSocketGeometry')
    tree.interface.new_socket(name='Geometria', in_out='OUTPUT', socket_type='NodeSocketGeometry')
    for name, kind in (('Normal', 'NodeSocketVector'), ('Plano', 'NodeSocketFloat'),
                       ('Deslocamento', 'NodeSocketVector')):
        tree.interface.new_socket(name=name, in_out='INPUT', socket_type=kind)
    nodes, links = tree.nodes, tree.links
    inp, out = nodes.new('NodeGroupInput'), nodes.new('NodeGroupOutput')
    position = nodes.new('GeometryNodeInputPosition')
    dot = nodes.new('ShaderNodeVectorMath')
    dot.operation = 'DOT_PRODUCT'
    compare = nodes.new('ShaderNodeMath')
    compare.operation = 'GREATER_THAN'
    move = nodes.new('GeometryNodeSetPosition')
    links.new(position.outputs['Position'], dot.inputs[0])
    links.new(inp.outputs['Normal'], dot.inputs[1])
    links.new(dot.outputs['Value'], compare.inputs[0])
    links.new(inp.outputs['Plano'], compare.inputs[1])
    links.new(inp.outputs['Geometria'], move.inputs['Geometry'])
    links.new(compare.outputs[0], move.inputs['Selection'])
    links.new(inp.outputs['Deslocamento'], move.inputs['Offset'])
    links.new(move.outputs['Geometry'], out.inputs['Geometria'])
    return tree


def _modifier(obj, root, axis):
    found = next((m for m in obj.modifiers if m.type == 'NODES' and m.node_group
                  and m.node_group.get(MARKER) == axis), None)
    if found:
        return found
    if obj.type != 'MESH':
        raise ValueError(tr("Não é possível esticar este membro: {}").format(obj.name))
    matrix = root.matrix_world.inverted_safe() @ obj.matrix_world
    normal = matrix.to_3x3().row[axis].copy()
    points = [normal.dot(v.co) for v in obj.data.vertices]
    if not points or max(points) - min(points) < 1e-8:
        raise ValueError(tr("Não é possível esticar este membro: {}").format(obj.name))
    mod = obj.modifiers.new('Esticar ' + 'XYZ'[axis], 'NODES')
    mod.node_group = _group()
    mod.node_group[MARKER] = axis
    compat.set_gn_input(mod, 'Normal', normal)
    compat.set_gn_input(mod, 'Plano', (min(points) + max(points)) / 2)
    compat.set_gn_input(mod, 'Deslocamento', (0, 0, 0))
    # As ferramentas de corte veem a chapa já esticada.
    obj.modifiers.move(len(obj.modifiers) - 1, 0)
    return mod


def _uv_density(obj):
    """Prolonga o mapeamento afim de cada face na geometria final; materiais compartilhados ficam intactos."""
    if obj.type != 'MESH' or not obj.data.uv_layers:
        return
    if obj.data.users > 1:
        obj.data = obj.data.copy()
    mesh = obj.data
    modifiers = [m for m in obj.modifiers if m.type == 'NODES' and m.node_group and MARKER in m.node_group]
    for layer in mesh.uv_layers:
        key = 'btm_stretch_uv_' + layer.name
        if key not in obj:
            obj[key] = [v for loop in layer.data for v in loop.uv]
        base = list(obj[key])
        if len(base) != len(layer.data) * 2:
            raise ValueError(tr("A topologia do membro mudou: {}").format(obj.name))
        for polygon in mesh.polygons:
            indices = list(polygon.loop_indices)
            if len(indices) < 3:
                continue
            origin = mesh.vertices[mesh.loops[indices[0]].vertex_index].co
            edges = [(i, mesh.vertices[mesh.loops[i].vertex_index].co - origin) for i in indices[1:]]
            pair = next(((i, e, j, f) for i, e in edges for j, f in edges if e.cross(f).length > 1e-9), None)
            if pair is None:
                continue
            i, e, j, f = pair
            ee, ef, ff = e.dot(e), e.dot(f), f.dot(f)
            determinant = ee * ff - ef * ef
            for index in indices:
                original = mesh.vertices[mesh.loops[index].vertex_index].co
                final = original.copy()
                for mod in modifiers:
                    normal = Vector(compat.get_gn_input(mod, 'Normal'))
                    if normal.dot(final) > compat.get_gn_input(mod, 'Plano'):
                        final += Vector(compat.get_gn_input(mod, 'Deslocamento'))
                delta = final - original
                a = (delta.dot(e) * ff - delta.dot(f) * ef) / determinant
                b = (delta.dot(f) * ee - delta.dot(e) * ef) / determinant
                uv = [base[index * 2 + k] + a * (base[i * 2 + k] - base[indices[0] * 2 + k])
                      + b * (base[j * 2 + k] - base[indices[0] * 2 + k]) for k in range(2)]
                layer.data[index].uv = uv
    mesh.update()


def _box(root, obj, depsgraph):
    inv = root.matrix_world.inverted_safe()
    if group.is_body(obj):
        points = [inv @ p for p in group._world_corners(obj, depsgraph)]
    else:
        points = [inv @ obj.matrix_world.translation]
        if obj.type == 'LIGHT' and obj.data.type == 'AREA':
            axis = 'XYZ'.index(obj.btm_member.axis)
            points = [points[0].copy(), points[0].copy()]
            points[0][axis] -= obj.data.size / 2
            points[1][axis] += obj.data.size / 2
    return tuple(tuple((min if k == 0 else max)(p[i] for p in points) * 1000 for i in range(3))
                 for k in range(2))


def _inputs(context, root):
    depsgraph = context.evaluated_depsgraph_get()
    objects = list(root.children_recursive)
    inside = set(objects)
    # As referências externas entram na ordenação e validação, mas não recebem a mudança deste armário.
    for obj in objects:
        for ref in obj.btm_member.refs:
            if ref.target is None or ref.target.btm_member.uid != ref.uid:
                raise ValueError(tr("Referência dimensional ausente: {}").format(obj.name))
            if ref.target not in objects:
                objects.append(ref.target)
    entries = []
    for obj in objects:
        data = obj.btm_member
        entries.append({'uid': data.uid, 'box': _box(root, obj, depsgraph), 'role': data.role,
                        'rule': data.rule if obj in inside else 'FIXED',
                        'refs': [{'uid': r.uid, 'face': r.face} for r in data.refs],
                        'params': {'axis': data.axis, 'offset_mm': data.offset_mm, 'count': data.count,
                                   **({'min_size_mm': 1} if obj.type == 'LIGHT' else {})}})
    distributed = {}
    for entry in entries:
        if entry['rule'] == 'DISTRIBUTE':
            key = (entry['params']['axis'], tuple((r['uid'], r['face']) for r in entry['refs']))
            distributed.setdefault(key, []).append(entry)
    for (axis, _refs), peers in distributed.items():
        peers.sort(key=lambda e: (e['box'][0]['XYZ'.index(axis)], e['uid']))
        for index, entry in enumerate(peers):
            if entry['params']['count'] != len(peers):
                raise ValueError(tr("Quantidade incompatível com os membros distribuídos"))
            entry['params']['index'] = index
    return objects, inside, entries


class Snapshot:
    def __init__(self, root):
        self.root = root
        self.size = tuple(root.btm_authored.size_local)
        self.state = []
        for obj in [root] + list(root.children_recursive):
            mods = [(m, tuple(compat.get_gn_input(m, 'Deslocamento'))) for m in obj.modifiers
                    if m.type == 'NODES' and m.node_group and MARKER in m.node_group]
            self.state.append((obj, obj.matrix_basis.copy(), list(obj.modifiers), mods, obj.data,
                               [[tuple(v.uv) for v in layer.data] for layer in obj.data.uv_layers]
                               if obj.type == 'MESH' else None,
                               obj.data.size if obj.type == 'LIGHT' and obj.data.type == 'AREA' else None,
                               {key: list(obj[key]) for key in obj.keys() if key.startswith('btm_stretch_uv_')},
                               obj.btm_aggregate.open_value,
                               {key: obj[key].to_list() if hasattr(obj[key], 'to_list') else obj[key]
                                for key in (leaf.REST_KEY, leaf.OPEN_KEY, 'btm_leaf_base', 'btm_leaf_manual_base')
                                if key in obj}))

    def restore(self):
        self.root.btm_authored.size_local = self.size
        for obj, matrix, old_mods, mods, data, uvs, size, custom, opening, leaf_data in self.state:
            for mod in list(obj.modifiers):
                if mod not in old_mods:
                    tree = mod.node_group if mod.type == 'NODES' else None
                    obj.modifiers.remove(mod)
                    if tree and tree.users == 0:
                        bpy.data.node_groups.remove(tree)
            for mod, offset in mods:
                compat.set_gn_input(mod, 'Deslocamento', offset)
            current_data = obj.data
            obj.data = data
            if current_data != data and current_data.users == 0:
                if obj.type == 'MESH':
                    bpy.data.meshes.remove(current_data)
                elif obj.type == 'LIGHT':
                    bpy.data.lights.remove(current_data)
            if uvs is not None:
                for layer, values in zip(obj.data.uv_layers, uvs):
                    for loop, value in zip(layer.data, values):
                        loop.uv = value
                obj.data.update()
            if size is not None:
                obj.data.size = size
            for key in list(obj.keys()):
                if key.startswith('btm_stretch_uv_') and key not in custom:
                    del obj[key]
            for key, value in custom.items():
                obj[key] = value
            _write(obj, 'open_value', opening)
            for key in (leaf.REST_KEY, leaf.OPEN_KEY, 'btm_leaf_base', 'btm_leaf_manual_base'):
                if key in leaf_data:
                    obj[key] = leaf_data[key]
                elif key in obj:
                    del obj[key]
            obj.matrix_basis = matrix


def _check_texture(obj):
    # Generated normaliza pela caixa avaliada e mudaria a densidade ao esticar.
    # UV e Object mantêm escala física; uma montagem desconhecida é recusada antes da escrita (R9).
    for slot in obj.material_slots:
        tree = slot.material.node_tree if slot.material else None
        if tree is not None and any(n.type == 'TEX_COORD' and n.outputs['Generated'].is_linked for n in tree.nodes):
            raise ValueError(tr("Use coordenadas UV ou de objeto antes de esticar: {}").format(obj.name))


def resize(context, root, size_mm):
    """Valida antes de alterar e usa a proteção RF-012; devolve False quando a medida é revertida."""
    snapshot = Snapshot(root)
    leaves = [(o, o.btm_aggregate.open_value, leaf.current_fraction(o)) for o in root.children_recursive
              if o.btm_aggregate.is_aggregate and o.btm_aggregate.kind == 'LEAF']
    with guard.suspended():
        for obj, _value, _fraction in leaves:
            _write(obj, 'open_value', 0.0)
            leaf.apply_fraction(obj, 0.0)
        context.view_layer.update()
    try:
        objects, inside, entries = _inputs(context, root)
        plan = rules.solve(entries, tuple(root.btm_authored.size_local), tuple(size_mm))
    except Exception:
        with guard.suspended():
            snapshot.restore()
            context.view_layer.update()
        raise
    matrices = {o: o.matrix_world.copy() for o in inside}
    # Falha de domínio tem motivo legível e não deve ser engolida pelo guarda de colisão.
    try:
        for obj in inside:
            if any(abs(v) > 1e-5 for v in plan[obj.btm_member.uid].extension):
                _check_texture(obj)
    except ValueError:
        with guard.suspended():
            snapshot.restore()
            context.view_layer.update()
        raise
    for obj in inside:
        change = plan[obj.btm_member.uid]
        if any(abs(v) > 1e-5 for v in change.extension) and obj.type != 'MESH' and not (
                obj.type == 'LIGHT' and obj.data.type == 'AREA'):
            snapshot.restore()
            context.view_layer.update()
            raise ValueError(tr("Não é possível esticar este membro: {}").format(obj.name))

    failures = []

    def depth(obj):
        value = 0
        while obj.parent is not None:
            value += 1
            obj = obj.parent
        return value

    def apply():
        try:
            for obj in sorted(inside, key=depth):
                data = obj.btm_member
                change = plan[data.uid]
                if data.rule != 'FIXED':
                    matrix = matrices[obj].copy()
                    matrix.translation += root.matrix_world.to_3x3() @ (Vector(change.shift) / 1000)
                    obj.matrix_world = matrix
                    context.view_layer.update()
                for axis, delta in enumerate(change.extension):
                    if abs(delta) < 1e-5:
                        continue
                    if obj.type == 'LIGHT':
                        if obj.data.users > 1:
                            obj.data = obj.data.copy()
                        obj.data.size += delta / 1000
                    else:
                        mod = _modifier(obj, root, axis)
                        direction = Vector((0, 0, 0))
                        direction[axis] = delta / 1000
                        vector = obj.matrix_world.to_3x3().inverted_safe() @ root.matrix_world.to_3x3() @ direction
                        total = Vector(compat.get_gn_input(mod, 'Deslocamento')) + vector
                        compat.set_gn_input(mod, 'Deslocamento',
                                            [0.0 if abs(v) < 1e-7 else v for v in total])
                if any(abs(v) > 1e-5 for v in change.extension):
                    _uv_density(obj)
            root.btm_authored.size_local = size_mm
            context.view_layer.update()
            for obj, value, fraction in leaves:
                parent = obj.btm_aggregate.parent_ref
                rest = leaf.front_frame(parent).inverted() @ parent.matrix_world.inverted_safe() @ obj.matrix_world
                obj[leaf.REST_KEY] = [v for row in rest for v in row]
                if 'btm_leaf_manual_base' in obj:
                    pivot = leaf.pivot_of(obj)
                    base = (leaf.front_frame(parent).inverted() @ parent.matrix_world.inverted_safe()
                            @ pivot.matrix_world).translation
                    obj['btm_leaf_manual_base'] = list(base)
                leaf.rebuild_pivot(obj)
                _write(obj, 'open_value', value)
                leaf.apply_fraction(obj, fraction)
            context.view_layer.update()
        except Exception as exc:
            failures.append(exc)
            snapshot.restore()
            raise

    # Mantém o núcleo puro e o snapshot disponíveis para operadores e scripts fora da UI.
    success = guard.reconfigure(root, apply, snapshot.restore)
    if failures:
        raise ValueError(tr("Não foi possível aplicar as regras: {}").format(failures[0])) from failures[0]
    return success


def _restore_all(context, snapshots):
    with guard.suspended():
        for snapshot in reversed(snapshots):
            snapshot.restore()
        context.view_layer.update()
        for snapshot in snapshots:
            guard.accept(snapshot.root)


def update_links(context):
    """Atualização explícita em ordem de dependências entre armários, protegida contra reentrada."""
    global _busy
    if _busy:
        return False
    _busy = True
    snapshots = []
    try:
        roots = [o for o in context.scene.objects if o.btm_authored.is_authored]
        entries = []
        for root in roots:
            refs = {r.target.btm_member.owner for o in root.children_recursive for r in o.btm_member.refs
                    if r.target is not None and r.target.btm_member.owner != root}
            entries.append({'uid': root.btm_authored.uid,
                            'refs': [{'uid': other.btm_authored.uid} for other in refs if other is not None]})
        ordered = rules.topological(entries)
        by_uid = {r.btm_authored.uid: r for r in roots}
        for uid in ordered:
            root = by_uid[uid]
            snapshots.append(Snapshot(root))
            if not resize(context, root, tuple(root.btm_authored.size_local)):
                _restore_all(context, snapshots)
                return False
        return True
    except Exception:
        _restore_all(context, snapshots)
        raise
    finally:
        _busy = False


class BTM_OT_UpdateLinks(bpy.types.Operator):
    """Recalcula as regras e os vãos referenciados sem escalar os membros"""
    bl_idname = 'caffmob_draw.authored_update_links'
    bl_label = "Atualizar vínculos"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        # (067 D-08) Habilitado só onde executa; o motivo aparece na dica do botão.
        from ..target import capabilities, snapshot
        return capabilities.poll(cls, 'authored_update_links', snapshot.current(context))

    def execute(self, context):
        try:
            update_links(context)
        except ValueError as exc:
            self.report({'ERROR'}, str(exc))
            return {'CANCELLED'}
        return {'FINISHED'}


class BTM_OT_RuleReference(bpy.types.Operator):
    """Acrescenta ou remove uma referência da regra do membro ativo"""
    bl_idname = 'caffmob_draw.authored_rule_reference'
    bl_label = "Referência dimensional"
    bl_options = {'REGISTER', 'UNDO'}
    index: bpy.props.IntProperty(default=-1, options={'HIDDEN'})  # type: ignore

    @classmethod
    def poll(cls, context):
        return context.object is not None and context.object.btm_member.owner is not None

    def execute(self, context):
        refs = context.object.btm_member.refs
        if self.index < 0:
            refs.add()
        elif self.index < len(refs):
            refs.remove(self.index)
        return {'FINISHED'}


def register():
    bpy.utils.register_class(BTM_OT_UpdateLinks)
    bpy.utils.register_class(BTM_OT_RuleReference)


def unregister():
    bpy.utils.unregister_class(BTM_OT_RuleReference)
    bpy.utils.unregister_class(BTM_OT_UpdateLinks)
