"""Sincronização incremental transacional: preparar antes de trocar; somente generated do mesmo dono."""
from dataclasses import asdict
import bpy  # type: ignore
from bpy.app.handlers import persistent  # type: ignore
from .. import stable_id
from ..collision import guard
from . import build, core, material, props, region

_busy = [False]


def controllers(scene=None):
    return [o for o in (scene or bpy.context.scene).objects if o.btm_cladding.uid]


def prepare(controller, depsgraph=None):
    data = controller.btm_cladding
    params = props.parameters(data).validate()
    basis, triangles = region.extract(data, depsgraph)
    pieces = core.layout(region.bounds(triangles), params)
    desired, selected = {}, {}
    material_sig = (data.texture, data.texture_size_mm, data.grain_angle,
                    data.material.name if data.material else '',
                    data.backing_material.name if data.backing_material else '')
    for piece in pieces:
        fragments = [core.intersection(tri, piece.polygon) for tri in triangles]
        fragments = [p for p in fragments if p]
        if not fragments:
            continue
        contour = core.boundary_signature(fragments)
        signature = core.digest((contour, piece.thickness_mm, piece.role, params.backing,
                                 params.sheet_t_mm, material_sig, data.overrides))
        desired[piece.key] = signature
        selected[piece.key] = piece
    opening_ids = sorted(o.btm_opening_real.uid or str(o.session_uid) for o in data.host.children
                         if o.get('IS_ENTRY_DOOR_BP') or o.get('IS_WINDOW_BP'))
    signature = core.digest((asdict(params), desired, tuple(tuple(row) for row in basis),
                             data.environment, opening_ids))
    return basis, triangles, selected, desired, signature


def sync(controller, depsgraph=None):
    data = controller.btm_cladding
    if data.host is None:
        data.link_missing = True
        data.diagnostic = 'Hospedeiro excluído; escolha Reassociar'
        return core.SyncPlan()
    if controller.get('btm_cladding_adopted'):
        data.link_missing = False
        data.diagnostic = ''
        return core.SyncPlan()
    # Sem atualizações de depsgraph dentro desta seção: o handler não pode observar um estado intermediário.
    with guard.suspended():
        basis, triangles, pieces, desired, signature = prepare(controller, depsgraph)
        existing = [(o, o.get('btm_cladding_piece'), o.get('btm_cladding_signature', ''))
                    for o in bpy.context.scene.objects if o.get('btm_cladding_piece')]
        plan = core.sync_plan(data.uid, desired, existing, data.params_hash, signature)
        if not (plan.create or plan.update or plan.remove):
            if signature != data.params_hash:
                controller.matrix_world = basis
                data.params_hash = signature
                data.link_missing = False
                data.diagnostic = ''
            return plan
        pending = {}
        try:
            for key in plan.create + tuple(key for _obj, key in plan.update):
                mesh = build.mesh_for(triangles, pieces[key], data.sheet_t_mm if data.backing else 0)
                if mesh is None:
                    raise ValueError('Recorte produziu uma peça vazia')
                pending[key] = mesh
            mats = {role: material.resolve(controller, role) for role in {p.role for p in pieces.values()}}
        except Exception:
            for mesh in pending.values():
                bpy.data.meshes.remove(mesh)
            raise
        for obj, key in plan.update:
            old = obj.data
            obj.data = pending.pop(key)
            if old.users == 0:
                bpy.data.meshes.remove(old)
            obj['btm_cladding_signature'] = desired[key]
            material.apply(obj, mats[pieces[key].role])
        for key in plan.create:
            obj = build.attach(controller, pieces[key], pending.pop(key))
            obj['btm_cladding_signature'] = desired[key]
            material.apply(obj, mats[pieces[key].role])
        for obj in plan.remove:
            build.remove(obj)
        controller.matrix_world = basis
        data.openings.clear()
        for opening in data.host.children:
            if opening.get('IS_ENTRY_DOOR_BP') or opening.get('IS_WINDOW_BP'):
                data.openings.add().target = opening
        data.params_hash = signature
        data.link_missing = False
        data.diagnostic = ''
        return plan


def sync_hosts(hosts):
    for controller in controllers():
        if controller.btm_cladding.host in hosts:
            sync(controller)


@persistent
def on_update(scene, depsgraph):
    if _busy[0] or not any(True for _u in depsgraph.updates):
        return
    _busy[0] = True
    try:
        roots = controllers(scene)
        previous = {o.session_uid: o.btm_cladding.uid for o in roots}
        stable_id.renew_duplicates([(o.session_uid, o.btm_cladding) for o in roots])
        for root in roots:
            old = previous[root.session_uid]
            if old != root.btm_cladding.uid:
                for obj in root.children:
                    mark = obj.get('btm_cladding_piece')
                    if mark and mark.get('owner') == old and mark.get('generated'):
                        mark['owner'] = root.btm_cladding.uid
                root.btm_cladding.params_hash = ''
            try:
                sync(root, depsgraph)
            except (ValueError, RuntimeError) as exc:
                root.btm_cladding.diagnostic = str(exc)
    finally:
        _busy[0] = False


@persistent
def on_load(*_args):
    _busy[0] = False
    # Não migrar conteúdo manual. A cena só ganha revestimento por confirmação explícita.


def register():
    for handlers, callback in ((bpy.app.handlers.depsgraph_update_post, on_update),
                               (bpy.app.handlers.load_post, on_load)):
        if callback not in handlers:
            handlers.append(callback)


def unregister():
    for handlers, callback in ((bpy.app.handlers.depsgraph_update_post, on_update),
                               (bpy.app.handlers.load_post, on_load)):
        if callback in handlers:
            handlers.remove(callback)
