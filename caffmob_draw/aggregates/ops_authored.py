"""Adoção autoral com revisão explícita, sem reconstrução de geometria (066, T052)."""

import bpy  # type: ignore

from ..data.i18n import tr
from mathutils import Matrix  # type: ignore

from ..selection import classify
from ..stable_id import ensure_uid
from . import group
from .authored_props import FRONT_ITEMS, ROLE_ITEMS
from .ops_members import owner_of, set_member


def eligible(obj):
    return (obj.type in group.MEMBER_TYPES and not obj.get('IS_WALL_BP') and not obj.get('IS_FLOOR_BP')
            and not obj.get('IS_CEILING_BP') and classify.btm_kind(obj) not in {'WALL', 'FLOOR', 'CEILING'})


def resolve_root(obj):
    owner = owner_of(obj)
    if owner is not None:
        return owner
    if obj is None:
        return None
    while obj.parent is not None and eligible(obj.parent):
        obj = obj.parent
    return obj


def candidates(root, selected):
    objects = [root] + list(root.children_recursive) if root is not None else list(selected)
    return list(dict.fromkeys(o for o in objects if eligible(o)))


def external_references(objects):
    """Lista referências externas sem incorporá-las silenciosamente ao armário."""
    inside = set(objects)
    out = []
    for obj in objects:
        if obj.parent is not None and obj.parent not in inside:
            out.append((obj, 'Pai', obj.parent))
        for mod in obj.modifiers:
            for prop in mod.bl_rna.properties:
                if prop.type == 'POINTER':
                    target = getattr(mod, prop.identifier, None)
                    if isinstance(target, bpy.types.Object) and target not in inside:
                        out.append((obj, 'Modificador', target))
            if mod.type == 'NODES' and mod.node_group:
                from .. import compat
                for item in mod.node_group.interface.items_tree:
                    if (item.item_type == 'SOCKET' and item.in_out == 'INPUT'
                            and item.socket_type == 'NodeSocketObject'):
                        target = compat.try_get_gn_input_by_id(mod, item.identifier)
                        if target is not None and target not in inside:
                            out.append((obj, 'Modificador', target))
                for target in _node_objects(mod.node_group):
                    if target not in inside:
                        out.append((obj, 'Modificador', target))
        for holder in (obj, obj.data):
            animation = getattr(holder, 'animation_data', None)
            for curve in animation.drivers if animation else ():
                for variable in curve.driver.variables:
                    for target in variable.targets:
                        if target.id is not None and target.id not in inside:
                            out.append((obj, 'Driver', target.id))
        for prop in obj.bl_rna.properties:
            if prop.type == 'POINTER':
                holder = getattr(obj, prop.identifier, None)
                if isinstance(holder, bpy.types.PropertyGroup):
                    for target in _property_objects(holder):
                        if target not in inside:
                            out.append((obj, 'Vínculo', target))
    return out


def _property_objects(holder, visited=None):
    visited = set() if visited is None else visited
    key = holder.as_pointer()
    if key in visited:
        return
    visited.add(key)
    for prop in holder.bl_rna.properties:
        if prop.identifier == 'rna_type':
            continue
        if prop.type == 'POINTER':
            value = getattr(holder, prop.identifier, None)
            if isinstance(value, bpy.types.Object):
                yield value
            elif isinstance(value, bpy.types.PropertyGroup):
                yield from _property_objects(value, visited)
        elif prop.type == 'COLLECTION':
            for item in getattr(holder, prop.identifier):
                if isinstance(item, bpy.types.PropertyGroup):
                    yield from _property_objects(item, visited)


def _node_objects(tree, visited=None):
    visited = set() if visited is None else visited
    if tree in visited:
        return
    visited.add(tree)
    for node in tree.nodes:
        for socket in node.inputs:
            target = getattr(socket, 'default_value', None)
            if isinstance(target, bpy.types.Object):
                yield target
            elif isinstance(target, bpy.types.Collection):
                yield from target.all_objects
        nested = getattr(node, 'node_tree', None)
        if nested is not None:
            yield from _node_objects(nested, visited)


def local_size(root, objects):
    inv = root.matrix_world.inverted_safe() if root else Matrix.Identity(4)
    depsgraph = bpy.context.evaluated_depsgraph_get()
    points = [inv @ p for obj in objects if group.is_body(obj) for p in group._world_corners(obj, depsgraph)]
    if not points:
        return (0, 0, 0)
    return tuple((max(p[i] for p in points) - min(p[i] for p in points)) * 1000 for i in range(3))


def adopt(root, objects, front_axis='NEG_Y', size=None, roles=None):
    objects = list(dict.fromkeys(objects))
    if not objects or any(not eligible(o) for o in objects):
        raise ValueError("Revise os membros do armário")
    if root is not None and not eligible(root):
        raise ValueError("A raiz não pode ser um elemento do ambiente")
    if root is not None:
        for obj in objects:
            if obj != root and (root in obj.children_recursive or obj.get('IS_AUTHORED_CABINET')):
                raise ValueError("Revise os membros do armário")
    if root is None:
        root = bpy.data.objects.new('Armário autoral', None)
        bpy.context.collection.objects.link(root)
    data = root.btm_authored
    data.is_authored = True
    ensure_uid(data)
    data.front_axis = front_axis
    data.size_local = size if size is not None else local_size(root, objects)
    root['IS_AUTHORED_CABINET'] = True
    inside = set(objects) | {root}
    # A exclusão na revisão deve tirar o objeto da árvore movível também.
    excluded = [o for o in root.children_recursive if o not in inside]
    worlds = {o: o.matrix_world.copy() for o in excluded}
    for obj in excluded:
        if obj.parent in inside:
            obj.parent = root.parent
            obj.matrix_world = worlds[obj]
        if obj.btm_member.owner == root:
            obj.btm_member.owner = None
    for obj in objects:
        if obj == root:
            continue
        # Preserva hierarquias internas (pivôs manuais inclusive).
        role = (roles or {}).get(obj, 'CUTTER' if obj.get('IS_CUTTING_OBJ') else
                                 'LIGHT' if obj.type == 'LIGHT' else 'CARCASS')
        set_member(obj, root, role, reparent=obj.parent not in inside)
    return root


class BTM_PG_AdoptEntry(bpy.types.PropertyGroup):
    object_name: bpy.props.StringProperty()  # type: ignore

    @property
    def obj(self):
        return bpy.data.objects.get(self.object_name)

    @obj.setter
    def obj(self, value):
        self.object_name = value.name

    include: bpy.props.BoolProperty(name="Incluir", default=True)  # type: ignore
    role: bpy.props.EnumProperty(name="Papel", items=ROLE_ITEMS)  # type: ignore


def _refresh_review(self, context):
    BTM_OT_AuthoredAdopt._review(self, context)


class BTM_OT_AuthoredAdopt(bpy.types.Operator):
    """Registra uma montagem livre sem modificar malhas ou acabamentos"""
    bl_idname = 'caffmob_draw.authored_adopt'
    bl_label = "Adotar como armário"
    bl_options = {'REGISTER', 'UNDO'}

    root: bpy.props.StringProperty(name="Raiz existente", update=_refresh_review)  # type: ignore
    new_root: bpy.props.BoolProperty(
        name="Criar raiz para as peças soltas", default=False, update=_refresh_review)  # type: ignore
    front_axis: bpy.props.EnumProperty(name="Frente local", items=FRONT_ITEMS, default='NEG_Y')  # type: ignore
    size_local: bpy.props.FloatVectorProperty(name="Medidas locais (mm)", size=3, min=0)  # type: ignore
    entries: bpy.props.CollectionProperty(type=BTM_PG_AdoptEntry)  # type: ignore

    @classmethod
    def poll(cls, context):
        # (067 D-08) Habilitado só onde executa; o motivo aparece na dica do botão.
        from ..target import capabilities, snapshot
        return capabilities.poll(cls, 'authored_adopt', snapshot.current(context))

    def _review(self, context):
        self.entries.clear()
        for obj in candidates(None if self.new_root else bpy.data.objects.get(self.root), context.selected_objects):
            entry = self.entries.add()
            entry.obj = obj
            entry.role = 'CUTTER' if obj.get('IS_CUTTING_OBJ') else 'LIGHT' if obj.type == 'LIGHT' else 'CARCASS'
        root = None if self.new_root else bpy.data.objects.get(self.root)
        self.size_local = local_size(root, [e.obj for e in self.entries])

    def invoke(self, context, event):
        obj = context.object
        root = resolve_root(obj)
        self.root = root.name if root else ''
        self.new_root = obj is not None and not obj.children and len(context.selected_objects) > 1
        self._review(context)
        return context.window_manager.invoke_props_dialog(self, width=650)

    def draw(self, context):
        layout = self.layout
        layout.prop(self, 'new_root')
        if not self.new_root:
            layout.prop_search(self, 'root', bpy.data, 'objects')
        layout.prop(self, 'front_axis')
        layout.prop(self, 'size_local')
        for entry in self.entries:
            row = layout.row(align=True)
            row.prop(entry, 'include', text=entry.obj.name if entry.obj else '')
            row.prop(entry, 'role', text='')
        objects = [e.obj for e in self.entries if e.include and e.obj]
        for obj, kind, target in external_references(objects):
            layout.label(text=tr('{}: {} → {}').format(tr(kind), obj.name, target.name), icon='LINKED')

    def execute(self, context):
        root = bpy.data.objects.get(self.root) if self.root else resolve_root(context.object)
        root = None if self.new_root else root
        objects = [e.obj for e in self.entries if e.include and e.obj] if self.entries else candidates(
            root, context.selected_objects)
        roles = {e.obj: e.role for e in self.entries if e.include and e.obj}
        try:
            root = adopt(root, objects, self.front_axis,
                         self.size_local if any(self.size_local) else None, roles)
        except ValueError as exc:
            self.report({'ERROR'}, tr(str(exc)))
            return {'CANCELLED'}
        context.view_layer.objects.active = root
        root.select_set(True)
        return {'FINISHED'}


classes = (BTM_PG_AdoptEntry, BTM_OT_AuthoredAdopt)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
