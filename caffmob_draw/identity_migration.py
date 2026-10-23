"""Migração idempotente dos vínculos de portas (066, T078); sem reconstruir geometria ao abrir."""

import bpy  # type: ignore
from bpy.app.handlers import persistent  # type: ignore

from . import stable_id

_busy = False
_known = [None]        # quantos objetos o arquivo tinha na última migração; None = rodar na próxima atualização


def migrate_door(cage):
    from .openings import sync
    data = cage.btm_opening_real
    stable_id.ensure_uid(data)
    if data.host_wall is None:
        parent = cage.parent
        if parent is not None and parent.get('IS_WALL_BP'):
            data.host_wall = parent
        else:
            hosts = [o for o in bpy.data.objects if o.get('IS_WALL_BP')
                     and any(m.type == 'BOOLEAN' and m.object == cage for m in o.modifiers)]
            if len(hosts) == 1:
                data.host_wall = hosts[0]
    wall = data.host_wall
    matches = [m for m in wall.modifiers if m.type == 'BOOLEAN' and m.object == cage] if wall else []
    data.link_missing = not bool(matches)
    for mod in matches:
        mod.name = 'Boolean_' + stable_id.short(data.uid)
    # Arquivos antigos não têm índice. A pose fechada local ordena as folhas, mesmo já renomeadas.
    leaves = sync.door_leaves(cage)
    leaves.sort(key=lambda o: tuple(o.get('btm_leaf_rest', [0.0] * 16))[3])
    used = {o.btm_aggregate.leaf_index for o in leaves if o.btm_aggregate.leaf_index >= 0}
    for obj in leaves:
        if obj.btm_aggregate.leaf_index < 0:
            index = next(i for i in range(len(leaves)) if i not in used)
            obj.btm_aggregate.leaf_index = index
            used.add(index)


def migrate_authored():
    objects = [o for o in bpy.data.objects if o.library is None]
    roots = [o for o in objects if o.btm_authored.is_authored]
    stable_id.renew_duplicates([(o.session_uid, o.btm_authored) for o in roots])
    members = [o for o in objects if o.btm_member.owner is not None or
               (o.btm_aggregate.is_aggregate and o.btm_aggregate.kind == 'LEAF')]
    stable_id.renew_duplicates([(o.session_uid, o.btm_member) for o in members])
    for pivot in objects:
        if 'btm_leaf' not in pivot:
            continue
        for obj in pivot.children:
            agg = obj.btm_aggregate
            if agg.is_aggregate and agg.kind == 'LEAF':
                agg.pivot = pivot
        del pivot['btm_leaf']
    # As referências de membro também acompanham a renovação do uid após duplicação.
    for obj in members:
        for ref in obj.btm_member.refs:
            if ref.target is not None:
                uid = stable_id.ensure_uid(ref.target.btm_member)
                if ref.uid != uid:
                    ref.uid = uid


def migrate():
    migrate_authored()
    from .openings import sync
    cages = [o for o in bpy.data.objects if sync.is_opening(o) and o.library is None]
    stable_id.renew_duplicates([(o.session_uid, o.btm_opening_real) for o in cages])
    for cage in cages:
        migrate_door(cage)


@persistent
def on_load(*_args):
    migrate()
    _known[0] = len(bpy.data.objects)


@persistent
def on_undo(*_args):
    _known[0] = None


@persistent
def on_update(_scene, depsgraph):
    global _busy
    if _busy or not any(isinstance(u.id, bpy.types.Object) for u in depsgraph.updates):
        return
    count = len(bpy.data.objects)
    if count == _known[0]:
        return            # sem objeto novo (duplicar, importar, colar): nada a renovar (BUG-20261023-TU4V)
    _known[0] = count
    _busy = True
    try:
        migrate_authored()
        from .openings import sync
        cages = [o for o in bpy.data.objects if sync.is_opening(o) and o.library is None]
        renewed = stable_id.renew_duplicates([(o.session_uid, o.btm_opening_real) for o in cages])
        for cage in cages:
            if cage.btm_opening_real in renewed:
                migrate_door(cage)
    finally:
        _busy = False


_HANDLERS = (('load_post', on_load), ('depsgraph_update_post', on_update), ('undo_post', on_undo),
             ('redo_post', on_undo))


def register():
    for name, callback in _HANDLERS:
        handlers = getattr(bpy.app.handlers, name)
        if callback not in handlers:
            handlers.append(callback)


def unregister():
    for name, callback in _HANDLERS:
        handlers = getattr(bpy.app.handlers, name)
        if callback in handlers:
            handlers.remove(callback)
