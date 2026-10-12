"""Operadores do grudar (feature 004, T027, T028; RF-11, RF-13, RF-16, D-05, D-07).

- `caffmob.stick_to_face`: com o item selecionado, clicar numa face plana de outro objeto gruda o item nela.
- `caffmob.stick_release`: desgruda os itens selecionados, mantendo a posição.
- `caffmob.stick_move`: arrasta o item grudado no plano da face; com Ctrl, passar sobre a face de outro objeto troca
  de hospedeiro (ímã). Esc ou botão direito devolvem tudo como estava.
"""

import bpy  # type: ignore
from bpy_extras import view3d_utils  # type: ignore
from mathutils import Vector, geometry  # type: ignore

from ..data.i18n import tr
from ..selection import classify
from . import apply, frame, link, magnet

_STICK_FIELDS = ('is_stuck', 'host', 'face_kind', 'face', 'plane', 'u', 'v', 'distance', 'spin', 'applied_spin',
                 'out_of_face', 'orig_parent', 'last_world')


ITEM_KINDS = (classify.MODULE, classify.FRONT, classify.PART, classify.GEOMETRY, classify.OBSTACLE, classify.OTHER)


def stickable(obj):
    """O que pode ser grudado: o mesmo filtro em todo lugar (menu, operador e painel; questions.md, pergunta 39)."""
    info = classify.classify(obj) if obj is not None else None
    return info is not None and info.kind in ITEM_KINDS and not (info.kind == classify.OTHER and obj.type != 'MESH')


def item_of(obj):
    """O que se gruda: a raiz do módulo para peça ou frente; o próprio objeto nos demais casos."""
    if obj is None:
        return None
    root = classify.movable_root(obj)
    return root if root is not None else obj


def _ray(context, event):
    region, rv3d = context.region, context.region_data
    coord = (event.mouse_region_x, event.mouse_region_y)
    origin = view3d_utils.region_2d_to_origin_3d(region, rv3d, coord)
    direction = view3d_utils.region_2d_to_vector_3d(region, rv3d, coord)
    return origin, direction


def scene_hit(context, origin, direction, exclude):
    """Primeiro acerto na cena fora de `exclude`: (objeto, ponto, normal, vértices do polígono) ou None."""
    depsgraph = context.evaluated_depsgraph_get()
    start = origin
    for _ in range(16):
        hit, location, normal, index, obj, _matrix = context.scene.ray_cast(depsgraph, start, direction)
        if not hit:
            return None
        if obj in exclude or obj.get('IS_CUTTING_OBJ') or obj.get('IS_2D_ANNOTATION'):
            start = location + direction * 0.0001
            continue
        return obj, location, normal, magnet._polygon(obj, index, depsgraph)
    return None


def snapshot(item):
    st = item.btm_stick
    values = {}
    for name in _STICK_FIELDS:
        value = getattr(st, name)
        values[name] = tuple(value) if name in ('plane', 'last_world') else value
    return (item.parent, item.matrix_parent_inverse.copy(), item.matrix_world.copy(), values)


def restore(item, snap):
    parent, inverse, world, values = snap
    item.parent = parent
    item.matrix_parent_inverse = inverse
    item.matrix_world = world
    for name, value in values.items():
        apply.write(item, name, value)
    apply.invalidate()


class BTM_OT_StickToFace(bpy.types.Operator):
    """Clique numa face plana de outro objeto: o item encosta nela e vira elemento filho dela"""
    bl_idname = "caffmob.stick_to_face"
    bl_label = "Grudar"
    bl_options = {'REGISTER', 'UNDO', 'BLOCKING'}

    @classmethod
    def poll(cls, context):
        return (context.area is not None and context.area.type == 'VIEW_3D'
                and stickable(context.active_object))

    def invoke(self, context, event):
        self.item = item_of(context.active_object)
        context.window_manager.modal_handler_add(self)
        context.workspace.status_text_set(
            tr("Grudar {}  |  Clique numa face plana  |  Botão direito/Esc: cancelar").format(self.item.name))
        return {'RUNNING_MODAL'}

    def _finish(self, context):
        context.workspace.status_text_set(None)

    def modal(self, context, event):
        if event.type in {'MIDDLEMOUSE', 'WHEELUPMOUSE', 'WHEELDOWNMOUSE'}:
            return {'PASS_THROUGH'}
        if event.type in {'RIGHTMOUSE', 'ESC'} and event.value == 'PRESS':
            self._finish(context)
            return {'CANCELLED'}
        if event.type == 'LEFTMOUSE' and event.value == 'PRESS':
            origin, direction = _ray(context, event)
            own = {self.item} | set(self.item.children_recursive)
            found = scene_hit(context, origin, direction, own)
            if found is None:
                self.report({'WARNING'}, tr("Nenhuma face sob o cursor"))
                return {'RUNNING_MODAL'}
            obj, location, normal, polygon = found
            try:
                host, _face = link.stick(self.item, obj, location, normal, polygon, center=True)
            except ValueError as exc:
                self.report({'WARNING'}, str(exc))
                self._finish(context)
                return {'CANCELLED'}
            self._finish(context)
            self.report({'INFO'}, tr("Elemento filho de: {}").format(link.face_label(self.item)))
            return {'FINISHED'}
        return {'RUNNING_MODAL'}


class BTM_OT_StickRelease(bpy.types.Operator):
    """Solta o item da face: ele fica onde está e deixa de acompanhar o hospedeiro"""
    bl_idname = "caffmob.stick_release"
    bl_label = "Desgrudar"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return any(item_of(o) is not None and item_of(o).btm_stick.is_stuck for o in context.selected_objects)

    def execute(self, context):
        items = {item_of(o) for o in context.selected_objects} - {None}
        count = sum(1 for item in items if link.release(item))
        self.report({'INFO'}, tr("{} item(ns) desgrudado(s)").format(count))
        return {'FINISHED'}


class BTM_OT_StickMove(bpy.types.Operator):
    """Arrasta o item no plano da face; com Ctrl, sobre a face de outro objeto ele troca de hospedeiro"""
    bl_idname = "caffmob.stick_move"
    bl_label = "Mover no plano"
    bl_options = {'REGISTER', 'UNDO', 'BLOCKING'}

    @classmethod
    def poll(cls, context):
        item = item_of(context.active_object)
        return (context.area is not None and context.area.type == 'VIEW_3D' and item is not None
                and apply.linked(item))

    def _plane(self):
        st = self.item.btm_stick
        fr, _extent = apply.face_of(self.item)
        world = st.host.matrix_world
        origin = world @ Vector(fr[0])
        normal = (world.to_3x3() @ Vector(fr[3])).normalized()
        return fr, origin + normal * st.distance, normal

    def _plane_coords(self, context, event):
        origin, direction = _ray(context, event)
        fr, co, no = self._plane()
        hit = geometry.intersect_line_plane(origin, origin + direction, co, no)
        if hit is None:
            return None
        local = self.item.btm_stick.host.matrix_world.inverted_safe() @ hit
        return frame.to_frame(fr, tuple(local))

    def invoke(self, context, event):
        self.item = item_of(context.active_object)
        self.snap = snapshot(self.item)
        self.anchor = self._plane_coords(context, event)
        if self.anchor is None:
            self.report({'WARNING'}, tr("Gire a vista para enxergar a face"))
            return {'CANCELLED'}
        st = self.item.btm_stick
        self.start = (st.u, st.v)
        context.window_manager.modal_handler_add(self)
        context.workspace.status_text_set(tr("Mover no plano  |  Ctrl: trocar de face  |  Clique: confirmar  |  Botão direito/Esc: cancelar"))
        return {'RUNNING_MODAL'}

    def _switch_face(self, context, event):
        enabled, _distance = magnet.preferences()
        if not enabled or not event.ctrl:
            return False
        origin, direction = _ray(context, event)
        own = {self.item} | set(self.item.children_recursive)
        found = scene_hit(context, origin, direction, own)
        if found is None:
            return False
        obj, location, normal, polygon = found
        if link.host_for(obj) == self.item.btm_stick.host:
            return False
        try:
            link.stick(self.item, obj, location, normal, polygon, center=True)
        except ValueError:
            return False
        self.anchor = self._plane_coords(context, event)
        st = self.item.btm_stick
        self.start = (st.u, st.v)
        return self.anchor is not None

    def modal(self, context, event):
        if event.type in {'MIDDLEMOUSE', 'WHEELUPMOUSE', 'WHEELDOWNMOUSE'}:
            return {'PASS_THROUGH'}
        if event.type == 'MOUSEMOVE':
            if self._switch_face(context, event):
                return {'RUNNING_MODAL'}
            coords = self._plane_coords(context, event)
            if coords is not None:
                st = self.item.btm_stick
                st.u = self.start[0] + coords[0] - self.anchor[0]       # o update reposiciona (RN-06)
                st.v = self.start[1] + coords[1] - self.anchor[1]
            return {'RUNNING_MODAL'}
        if event.type == 'LEFTMOUSE' and event.value == 'PRESS':
            context.workspace.status_text_set(None)
            return {'FINISHED'}
        if event.type in {'RIGHTMOUSE', 'ESC'} and event.value == 'PRESS':
            restore(self.item, self.snap)
            context.workspace.status_text_set(None)
            return {'CANCELLED'}
        return {'RUNNING_MODAL'}


classes = (BTM_OT_StickToFace, BTM_OT_StickRelease, BTM_OT_StickMove)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        if cls.is_registered:
            bpy.utils.unregister_class(cls)

