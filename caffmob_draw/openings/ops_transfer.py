"""Transferência de portal: prévia desenhada, sem objetos temporários; confirmação em um passo de Desfazer."""

import bpy  # type: ignore
from bpy_extras import view3d_utils  # type: ignore
from mathutils import Matrix, Vector  # type: ignore

from .. import hb_types
from ..collision import guard, rules
from ..data.i18n import tr
from ..operators.doors_windows import cut_wall
from . import region, region_core, sync, transfer_core
from .ops import door_of

_live = set()


def endpoints(wall):
    length = hb_types.GeoNodeWall(wall).get_input('Length')
    return tuple(wall.matrix_world @ Vector((0, 0, 0))), tuple(wall.matrix_world @ Vector((length, 0, 0)))


def implantation(door, wall, reference, distance, chosen=None):
    geo = hb_types.GeoNodeWall(wall)
    others = []
    for obj in wall.children:
        if obj != door and sync.is_opening(obj):
            width, _depth, height = sync._dims(obj)
            others.append((obj.location.x, obj.location.x + width, obj.location.z, obj.location.z + height))
    width, _depth, height = sync._dims(door)
    start, end = endpoints(wall)
    fit = transfer_core.destination(start, end, geo.get_input('Height'), width, height,
                                    reference, distance, others, chosen, end_height=geo.get_input('End Height'))
    return fit, transfer_core.reference_corner(start, end, reference, chosen)


def target_matrix(wall, x):
    return wall.matrix_world @ Matrix.Translation((x, 0, 0))


def blocked(context, door, wall, x):
    """Confere a pose completa no destino pelo guarda, mantendo a exclusão porta × parede vinculada."""
    with guard.suspended():
        context.view_layer.update()
        _scene, depsgraph = guard._check_context(door)
        body = guard._body(door, depsgraph)
        carried = guard._carry(body, target_matrix(wall, x) @ door.matrix_world.inverted_safe())
        skip = guard._subtree_uids([door])
        entries = guard._index.near(guard._bounds([carried]), skip) if carried else []
        for item in carried:
            # A exclusão da parede antiga não pode ser carregada para o destino.
            old = door.btm_opening_real.host_wall
            item.linked = frozenset((set(item.linked) - ({old.name} if old else set())) | {wall.name})
            for entry in entries:
                if not rules.excluded(item, entry.item) and guard._deep(item, entry, depsgraph):
                    return True
    return False


def cladding_changed(_door, _old_wall, _new_wall):
    """Recalcula origem e destino no mesmo passo de Desfazer do portal (T083)."""
    from ..cladding import sync as cladding_sync
    bpy.context.view_layer.update()
    cladding_sync.sync_hosts({_old_wall, _new_wall})


def transfer(context, door, wall, reference='START', distance=0.0, chosen=None):
    fit, corner = implantation(door, wall, reference, distance, chosen)
    if not fit.ok:
        return False, tr(region_core.REASONS[fit.reason])
    if blocked(context, door, wall, fit.x):
        return False, tr("O portal não cabe nesta posição")
    data = door.btm_opening_real
    old = data.host_wall
    old_parent, old_world = door.parent, door.matrix_world.copy()
    old_depth = sync._dims(door)[1]
    old_reference = (data.corner_ref, data.corner_dist_mm, tuple(data.corner_world))
    angles = {o.btm_aggregate.leaf_index: o.btm_aggregate.open_value * o.btm_aggregate.max_angle
              for o in sync.door_leaves(door)}
    with guard.suspended():
        try:
            if old:
                for mod in list(old.modifiers):
                    if mod.type == 'BOOLEAN' and mod.object == door:
                        old.modifiers.remove(mod)
            door.parent = wall
            door.matrix_parent_inverse = Matrix.Identity(4)
            door.location = (fit.x, 0, 0)
            door.rotation_euler = (0, 0, 0)
            data.host_wall = wall
            data.corner_ref, data.corner_dist_mm, data.corner_world = reference, distance, corner
            hb_types.GeoNodeCage(door).set_input('Dim Y', hb_types.GeoNodeWall(wall).get_input('Thickness'))
            cut_wall(wall, door)
            context.view_layer.update()
            sync.sync(context, door)
            context.view_layer.update()
            changed_angle = any(abs(o.btm_aggregate.open_value * o.btm_aggregate.max_angle
                                    - angles.get(o.btm_aggregate.leaf_index, 0)) > 0.1
                                for o in sync.door_leaves(door))
            if changed_angle or blocked(context, door, wall, fit.x):
                raise ValueError(tr("O portal não cabe nesta posição"))
            guard.accept(door)
        except Exception as exc:
            for mod in list(wall.modifiers):
                if mod.type == 'BOOLEAN' and mod.object == door:
                    wall.modifiers.remove(mod)
            door.parent = old_parent
            door.matrix_world = old_world
            data.host_wall = old
            data.corner_ref, data.corner_dist_mm, data.corner_world = old_reference
            hb_types.GeoNodeCage(door).set_input('Dim Y', old_depth)
            if old:
                cut_wall(old, door)
            context.view_layer.update()
            sync.sync(context, door)
            for sash in sync.door_leaves(door):
                sash.btm_aggregate.open_value = angles[sash.btm_aggregate.leaf_index] / sash.btm_aggregate.max_angle
            context.view_layer.update()
            guard.accept(door)
            return False, str(exc)
        cladding_changed(door, old, wall)
    return True, ''


class BTM_OT_DoorMoveToWall(bpy.types.Operator):
    bl_idname = 'caffmob.door_move_to_wall'
    bl_label = "Mover para outra parede"
    bl_options = {'REGISTER', 'UNDO'}

    target: bpy.props.StringProperty()  # type: ignore
    distance: bpy.props.FloatProperty(name="Distância ao canto (mm)", min=0.0)  # type: ignore
    reference: bpy.props.EnumProperty(name="Referência ao canto", items=[
        ('START', "Primeiro canto", ""), ('END', "Segundo canto", "")], default='START')  # type: ignore

    @classmethod
    def poll(cls, context):
        door = door_of(context.active_object)
        return door is not None and door.btm_opening_real.host_wall is not None

    def execute(self, context):
        door = door_of(context.active_object)
        wall = bpy.data.objects.get(self.target)
        if door is None or wall is None or not wall.get('IS_WALL_BP'):
            return {'CANCELLED'}
        ok, reason = transfer(context, door, wall, self.reference, self.distance)
        if not ok:
            self.report({'WARNING'}, reason)
            return {'CANCELLED'}
        door.select_set(True)
        context.view_layer.objects.active = door
        return {'FINISHED'}

    def invoke(self, context, _event):
        door = door_of(context.active_object)
        self._door_uid = door.btm_opening_real.uid
        self.distance = door.btm_opening_real.corner_dist_mm
        self.reference = door.btm_opening_real.corner_ref if door.btm_opening_real.corner_ref != 'EDGE' else 'START'
        self._area = context.area
        self._region = next(r for r in context.area.regions if r.type == 'WINDOW')
        self._fit = None
        self.target = ''
        self._reason = ''
        self._typed = ''
        self._cancelled = False
        self._handle = bpy.types.SpaceView3D.draw_handler_add(self._draw, (), 'WINDOW', 'POST_PIXEL')
        _live.add(self)
        context.window_manager.modal_handler_add(self)
        self._header(context)
        return {'RUNNING_MODAL'}

    def _door(self, context):
        return next((o for o in context.scene.objects if o.get(sync.DOOR_FLAG)
                     and o.btm_opening_real.uid == self._door_uid), None)

    def _header(self, context):
        context.area.header_text_set(tr("Aponte a parede | Clique: confirmar | Esc: cancelar") + ' | '
                                     + tr("Distância: {:.1f} mm | Tab: trocar canto").format(self.distance)
                                     + ' | ' + tr("Primeiro canto" if self.reference == 'START' else "Segundo canto")
                                     + '  ' + self._reason)

    def _draw(self):
        context = bpy.context
        wall = bpy.data.objects.get(self.target)
        if context.area == self._area and context.region == self._region and wall and self._fit:
            fit = self._fit
            region._draw_rect(context, wall, 'FRONT', fit.x, fit.x + fit.width, 0, fit.height)

    def _end(self):
        self._cancelled = True
        if getattr(self, '_handle', None) is not None:
            bpy.types.SpaceView3D.draw_handler_remove(self._handle, 'WINDOW')
            self._handle = None
        if self._area:
            self._area.header_text_set(None)
            self._area.tag_redraw()
        _live.discard(self)

    def cancel(self, _context):
        self._end()

    def modal(self, context, event):
        if self._cancelled:
            return {'CANCELLED'}
        if event.type in {'ESC', 'RIGHTMOUSE'} and event.value == 'PRESS':
            self._end()
            return {'CANCELLED'}
        if event.type in {'MIDDLEMOUSE', 'WHEELUPMOUSE', 'WHEELDOWNMOUSE'}:
            return {'PASS_THROUGH'}
        door = self._door(context)
        if door is None:
            self._end()
            return {'CANCELLED'}
        try:
            edited = False
            if event.value == 'PRESS':
                char = getattr(event, 'unicode', '')
                if char and char in '0123456789.,':
                    candidate = self._typed + char.replace(',', '.')
                    if candidate.count('.') <= 1:
                        self._typed = candidate
                        self.distance = float(candidate) if candidate != '.' else 0
                        edited = True
                elif event.type == 'BACK_SPACE':
                    self._typed = self._typed[:-1]
                    self.distance = float(self._typed) if self._typed and self._typed != '.' else 0
                    edited = True
                elif event.type == 'TAB':
                    self.reference = 'END' if self.reference == 'START' else 'START'
                    edited = True
            if event.type == 'MOUSEMOVE':
                coord = (event.mouse_x - self._region.x, event.mouse_y - self._region.y)
                rv3d = self._region.data
                origin = view3d_utils.region_2d_to_origin_3d(self._region, rv3d, coord)
                direction = view3d_utils.region_2d_to_vector_3d(self._region, rv3d, coord)
                hit, point, _normal, _index, obj, _matrix = context.scene.ray_cast(
                    context.evaluated_depsgraph_get(), origin, direction)
                self.target = obj.name if hit and obj.get('IS_WALL_BP') else ''
            if event.type == 'MOUSEMOVE' or edited:
                self._fit = None
                self._reason = ''
                if self.target:
                    wall = bpy.data.objects[self.target]
                    start, end = endpoints(wall)
                    corner = transfer_core.reference_corner(start, end, self.reference)
                    if event.type == 'MOUSEMOVE' and not self._typed:
                        local = wall.matrix_world.inverted() @ point
                        width = sync._dims(door)[0]
                        self.distance = max(0.0, transfer_core.distance_mm(start, end, corner, local.x, width))
                    fit, _corner = implantation(door, wall, self.reference, self.distance)
                    self._fit = fit if fit.ok else None
                    self._reason = tr(region_core.REASONS[fit.reason]) if not fit.ok else ''
                    if fit.ok and blocked(context, door, wall, fit.x):
                        self._reason = tr("O portal não cabe nesta posição")
                self._header(context)
                self._area.tag_redraw()
            if event.type == 'LEFTMOUSE' and event.value == 'PRESS' and self._fit and not self._reason:
                result = self.execute(context)
                self._end()
                return result
        except Exception:
            self._end()
            raise
        return {'RUNNING_MODAL'}


def register():
    bpy.utils.register_class(BTM_OT_DoorMoveToWall)


def unregister():
    for op in list(_live):
        op._end()
    if BTM_OT_DoorMoveToWall.is_registered:
        bpy.utils.unregister_class(BTM_OT_DoorMoveToWall)
