"""Grupo de peças na cena (feature 007, T013; RN-04, D-03).

`create_group` cria um Empty no centro da base da caixa das peças e as torna filhas dele, sem mexer na posição de
nenhuma; o pai e a matriz do mundo de cada peça ficam guardados em `btm_group.members`. `ungroup` devolve tudo.
`group_box` é a caixa da união das peças (avaliadas) num espaço dado: é o que a folha e a colisão usam para um grupo.
"""

import bpy  # type: ignore
from mathutils import Matrix, Vector  # type: ignore


MEMBER_TYPES = {'MESH', 'CURVE', 'FONT', 'SURFACE', 'EMPTY', 'LIGHT'}
BODY_TYPES = {'MESH', 'CURVE', 'FONT'}


def is_body(obj):
    member = getattr(obj, 'btm_member', None)
    return (obj.type in BODY_TYPES and getattr(member, 'role', '') != 'CUTTER'
            and not obj.get('IS_CUTTING_OBJ'))


def is_group(obj):
    group = getattr(obj, 'btm_group', None) if obj is not None else None
    return group is not None and group.is_group


def members(group):
    return [m.obj for m in group.btm_group.members if m.obj is not None and m.obj.name in bpy.data.objects
            and m.obj in group.children_recursive]


def _world_corners(obj, depsgraph):
    evaluated = obj.evaluated_get(depsgraph)
    return [evaluated.matrix_world @ Vector(c) for c in evaluated.bound_box]


def object_corners(obj, depsgraph):
    """Cantos da caixa do objeto no espaço local dele. Um Empty (grupo de peças do SketchUp ou da biblioteca de
    objetos) não tem volume: a caixa é a das malhas dentro dele."""
    if obj.type != 'EMPTY':
        return [Vector(c) for c in obj.evaluated_get(depsgraph).bound_box]
    to_local = obj.matrix_world.inverted_safe()
    corners = [to_local @ p for child in obj.children_recursive if is_body(child)
               for p in _world_corners(child, depsgraph)]
    return corners or [Vector()] * 8


def world_box(objs):
    depsgraph = bpy.context.evaluated_depsgraph_get()
    pts = [p for o in objs if is_body(o) for p in _world_corners(o, depsgraph)]
    if not pts:
        return None
    return Vector([min(p[i] for p in pts) for i in range(3)]), Vector([max(p[i] for p in pts) for i in range(3)])


def group_box(group, space=None):
    """Caixa (lo, hi) das peças do grupo no espaço da matriz `space` (padrão: o próprio grupo)."""
    depsgraph = bpy.context.evaluated_depsgraph_get()
    to_space = (space if space is not None else group.matrix_world).inverted_safe()
    bodies = dict.fromkeys(c for m in members(group)
                           for c in ([m] if m.type in BODY_TYPES else [m] + list(m.children_recursive)))
    pts = [to_space @ p for o in bodies if is_body(o) for p in _world_corners(o, depsgraph)]
    if not pts:
        return None
    return Vector([min(p[i] for p in pts) for i in range(3)]), Vector([max(p[i] for p in pts) for i in range(3)])


def create_group(objs, kind='PLAIN', name="Grupo"):
    """Agrupa `objs` (malhas) num Empty novo; devolve o grupo."""
    objs = [o for o in objs if o.type in MEMBER_TYPES]
    if not objs:
        return None
    lo, hi = world_box(objs) or (Vector(), Vector())
    group = bpy.data.objects.new(name, None)
    group.empty_display_type = 'CUBE'
    group.empty_display_size = 0.05
    collections = objs[0].users_collection or (bpy.context.scene.collection,)
    for collection in collections:
        collection.objects.link(group)
    group.location = ((lo.x + hi.x) / 2.0, (lo.y + hi.y) / 2.0, lo.z)
    common = {o.parent for o in objs}
    if len(common) == 1 and next(iter(common)) is not None:
        parent = next(iter(common))
        world = group.matrix_world.copy()
        group.parent = parent
        group.matrix_parent_inverse = Matrix.Identity(4)
        group.matrix_basis = parent.matrix_world.inverted() @ world
    bpy.context.view_layer.update()
    data = group.btm_group
    data.is_group, data.kind = True, kind
    selected = set(objs)
    for obj in objs:
        entry = data.members.add()
        entry.obj, entry.orig_parent = obj, obj.parent
        entry.orig_matrix = [v for row in obj.matrix_world for v in row]
        ancestor = obj.parent
        while ancestor is not None and ancestor not in selected:
            ancestor = ancestor.parent
        if ancestor is not None:
            continue                    # hierarquia móvel interna, inclusive pivô manual, permanece intacta
        world = obj.matrix_world.copy()
        obj.parent = group
        obj.matrix_parent_inverse = Matrix.Identity(4)
        obj.matrix_basis = group.matrix_world.inverted() @ world
    return group


def ungroup(group):
    """Devolve as peças ao pai e à posição do mundo **atuais** e apaga o grupo; devolve as peças."""
    bpy.context.view_layer.update()            # a desconversão logo antes mexe no pivô: matrizes em dia
    out = []
    for entry in group.btm_group.members:
        obj = entry.obj
        if obj is None or obj.name not in bpy.data.objects:
            continue
        world = obj.matrix_world.copy()
        obj.parent = entry.orig_parent
        obj.matrix_parent_inverse = Matrix.Identity(4)
        obj.matrix_world = world
        out.append(obj)
    bpy.data.objects.remove(group, do_unlink=True)
    return out


def box_corners(lo, hi):
    """Os 8 cantos na ordem do `Object.bound_box` do Blender (as faces e arestas da colisão dependem dela)."""
    from mathutils import Vector  # type: ignore
    (x0, y0, z0), (x1, y1, z1) = lo, hi
    return [Vector(c) for c in ((x0, y0, z0), (x0, y0, z1), (x0, y1, z1), (x0, y1, z0),
                                (x1, y0, z0), (x1, y0, z1), (x1, y1, z1), (x1, y1, z0))]

