"""Marcar uma região na parede antes de inserir porta ou janela (feature 011, T018; roadmap D-10, RN-10).

`caffmob.wall_region`: dois cliques em cantos opostos numa parede desenham um retângulo, que fica em
`WindowManager.btm_wall_region` (estado de sessão) até virar porta ou janela ou ser limpo:
- o primeiro clique escolhe a parede e a face (frente ou fundo), e o retângulo é medido no plano dessa face, para não
  ganhar paralaxe;
- os cantos andam na grade de 10 mm (com Shift, 1 mm) e ficam dentro da parede (do piso ao topo, de ponta a ponta);
- Esc ou botão direito cancela a marcação; depois de marcada, Esc na vista 3D (`caffmob.wall_region_clear`) ou
  "Limpar região" na barra lateral a apaga.

Um único desenho `POST_PIXEL` (registrado no `register` e removido no `unregister`) mostra a prévia do modal e a região
marcada; o `load_post` limpa a região do arquivo anterior.
"""

import blf  # type: ignore
import bpy  # type: ignore
import gpu  # type: ignore
from bpy.app.handlers import persistent  # type: ignore
from bpy_extras import view3d_utils  # type: ignore
from gpu_extras.batch import batch_for_shader  # type: ignore
from mathutils import Vector  # type: ignore
from mathutils.geometry import intersect_line_plane  # type: ignore

from .. import hb_placement, hb_snap, hb_types, units
from ..data.i18n import tr
from . import region_props

_draw_handle = [None]
_addon_keymaps = []
_live = {}          # prévia do modal: {'wall', 'side', 'a', 'b'} com cantos locais (x, z)

FILL, LINE, TEXT = (0.2, 0.55, 1.0, 0.18), (0.25, 0.6, 1.0, 0.95), (1.0, 1.0, 1.0, 1.0)


def _face_y(wall, side):
    return hb_types.GeoNodeWall(wall).get_input('Thickness') if side == 'BACK' else 0.0


def _rect_world(wall, side, x0, x1, z0, z1):
    y = _face_y(wall, side)
    m = wall.matrix_world
    return [m @ Vector((x0, y, z0)), m @ Vector((x1, y, z0)), m @ Vector((x1, y, z1)), m @ Vector((x0, y, z1))]


def _draw_rect(context, wall, side, x0, x1, z0, z1):
    region, rv3d = context.region, context.region_data
    if region is None or rv3d is None:
        return
    pts = [view3d_utils.location_3d_to_region_2d(region, rv3d, p) for p in _rect_world(wall, side, x0, x1, z0, z1)]
    if any(p is None for p in pts):
        return
    shader = gpu.shader.from_builtin('UNIFORM_COLOR')
    gpu.state.blend_set('ALPHA')
    shader.bind()
    shader.uniform_float("color", FILL)
    tris = [pts[0], pts[1], pts[2], pts[0], pts[2], pts[3]]
    batch_for_shader(shader, 'TRIS', {"pos": [(p.x, p.y) for p in tris]}).draw(shader)
    gpu.state.line_width_set(2.0)
    shader.uniform_float("color", LINE)
    edges = [pts[k] for i in range(4) for k in (i, (i + 1) % 4)]
    batch_for_shader(shader, 'LINES', {"pos": [(p.x, p.y) for p in edges]}).draw(shader)
    gpu.state.line_width_set(1.0)
    gpu.state.blend_set('NONE')
    unit = context.scene.unit_settings
    text = "{} × {}".format(units.unit_to_string(unit, abs(x1 - x0)), units.unit_to_string(unit, abs(z1 - z0)))
    center = sum(pts, Vector((0.0, 0.0))) / 4.0
    blf.size(0, 14 * context.preferences.system.ui_scale)
    width, height = blf.dimensions(0, text)
    blf.color(0, *TEXT)
    blf.position(0, center.x - width / 2, center.y - height / 2, 0)
    blf.draw(0, text)


def draw_regions():
    context = bpy.context
    if _live:
        wall = bpy.data.objects.get(_live['wall'])
        if wall is not None and _live.get('b') is not None:
            (ax, az), (bx, bz) = _live['a'], _live['b']
            _draw_rect(context, wall, _live['side'], ax, bx, az, bz)
        return
    region, wall = region_props.region_wall(context)
    if region is not None:
        _draw_rect(context, wall, region.side, region.x0, region.x1, region.z0, region.z1)


def _tag_redraw(context):
    for window in context.window_manager.windows:
        for area in window.screen.areas:
            if area.type == 'VIEW_3D':
                area.tag_redraw()


class BTM_OT_WallRegion(bpy.types.Operator, hb_placement.PlacementMixin):
    """Marca na parede, com dois cliques, a região onde a próxima porta ou janela vai entrar"""
    bl_idname = "caffmob.wall_region"
    bl_label = "Marcar região"
    bl_options = {'REGISTER'}

    @classmethod
    def poll(cls, context):
        return context.mode == 'OBJECT' and any(o.get('IS_WALL_BP') for o in context.scene.objects)

    def _ray(self):
        coord = (self.mouse_pos.x, self.mouse_pos.y)
        rv3d = self.region.data
        origin = view3d_utils.region_2d_to_origin_3d(self.region, rv3d, coord)
        return origin, view3d_utils.region_2d_to_vector_3d(self.region, rv3d, coord)

    def _wall_hit(self, context):
        origin, direction = self._ray()
        hit, location, _normal, _index, obj, _matrix = context.scene.ray_cast(
            context.evaluated_depsgraph_get(), origin, direction)
        while hit and obj is not None:
            if obj.get('IS_WALL_BP'):
                return obj, location
            obj = obj.parent
        return None, None

    def _local(self, wall, side, snap_fine):
        """Ponto do mouse no plano da face escolhida, em (x, z) locais da parede, na grade."""
        origin, direction = self._ray()
        m = wall.matrix_world
        y = _face_y(wall, side)
        plane_point = m @ Vector((0.0, y, 0.0))
        normal = (m.to_3x3() @ Vector((0.0, 1.0, 0.0))).normalized()
        point = intersect_line_plane(origin, origin + direction, plane_point, normal)
        if point is None:
            return None
        local = m.inverted() @ point
        unit = bpy.context.scene.unit_settings
        geo = hb_types.GeoNodeWall(wall)
        x = hb_snap.snap_value_to_grid(local.x, unit, fine=snap_fine)
        z = hb_snap.snap_value_to_grid(local.z, unit, fine=snap_fine)
        # Clique um pouco fora da parede (abaixo do piso, além da ponta) vale como a borda.
        return min(max(x, 0.0), geo.get_input('Length')), min(max(z, 0.0), geo.get_input('Height'))

    def _header(self, context):
        text = tr("Clique no primeiro canto da região numa parede") if 'a' not in _live else \
            tr("Clique no canto oposto | Shift: grade de 1 mm")
        hb_placement.draw_header_text(context, text + " | " + tr("Esc: cancelar"))

    def _end(self, context):
        _live.clear()
        hb_placement.clear_header_text(context)
        context.window.cursor_set('DEFAULT')
        _tag_redraw(context)

    def invoke(self, context, _event):
        self.init_placement(context)
        _live.clear()
        region_props.clear(context)
        context.window_manager.modal_handler_add(self)
        self._header(context)
        return {'RUNNING_MODAL'}

    def modal(self, context, event):
        context.window.cursor_set('CROSSHAIR')
        if event.type in {'MIDDLEMOUSE', 'WHEELUPMOUSE', 'WHEELDOWNMOUSE'}:
            return {'PASS_THROUGH'}
        if event.type in {'RIGHTMOUSE', 'ESC'} and event.value == 'PRESS':
            self._end(context)
            return {'CANCELLED'}
        if event.type == 'INBETWEEN_MOUSEMOVE':
            return {'RUNNING_MODAL'}
        self.update_snap(context, event)
        if 'a' not in _live:
            wall, location = self._wall_hit(context)
            if event.type == 'LEFTMOUSE' and event.value == 'PRESS' and wall is not None:
                thickness = hb_types.GeoNodeWall(wall).get_input('Thickness')
                side = 'BACK' if (wall.matrix_world.inverted() @ location).y > thickness / 2.0 else 'FRONT'
                corner = self._local(wall, side, event.shift)
                if corner is not None:
                    _live.update(wall=wall.name, side=side, a=corner, b=corner)
                    self._header(context)
        else:
            wall = bpy.data.objects.get(_live['wall'])
            if wall is None:
                self._end(context)
                return {'CANCELLED'}
            point = self._local(wall, _live['side'], event.shift)
            if point is not None:
                _live['b'] = point
            if event.type == 'LEFTMOUSE' and event.value == 'PRESS':
                (ax, az), (bx, bz) = _live['a'], _live['b']
                region = context.window_manager.btm_wall_region
                region.wall, region.side = wall.name, _live['side']
                region.x0, region.x1 = min(ax, bx), max(ax, bx)
                region.z0, region.z1 = min(az, bz), max(az, bz)
                region.active = True
                self._end(context)
                unit = context.scene.unit_settings
                self.report({'INFO'}, tr("Região marcada: {} × {}. Escolha a porta ou a janela").format(
                    units.unit_to_string(unit, region.x1 - region.x0), units.unit_to_string(unit, region.z1 - region.z0)))
                return {'FINISHED'}
        _tag_redraw(context)
        return {'RUNNING_MODAL'}


class BTM_OT_WallRegionClear(bpy.types.Operator):
    """Apaga a região marcada na parede"""
    bl_idname = "caffmob.wall_region_clear"
    bl_label = "Limpar região"
    bl_options = {'REGISTER'}

    @classmethod
    def poll(cls, context):
        region = getattr(context.window_manager, 'btm_wall_region', None)
        return region is not None and region.active

    def execute(self, context):
        region_props.clear(context)
        _tag_redraw(context)
        return {'FINISHED'}


classes = (BTM_OT_WallRegion, BTM_OT_WallRegionClear)


@persistent
def on_load_post(*_args):
    _live.clear()
    if bpy.context.window_manager is not None:
        region_props.clear(bpy.context)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    if _draw_handle[0] is None:
        _draw_handle[0] = bpy.types.SpaceView3D.draw_handler_add(draw_regions, (), 'WINDOW', 'POST_PIXEL')
    if on_load_post not in bpy.app.handlers.load_post:
        bpy.app.handlers.load_post.append(on_load_post)
    wm = bpy.context.window_manager
    kc = wm.keyconfigs.addon if wm else None
    if kc is not None:
        km = kc.keymaps.new(name='3D View', space_type='VIEW_3D')
        _addon_keymaps.append((km, km.keymap_items.new(BTM_OT_WallRegionClear.bl_idname, 'ESC', 'PRESS')))


def unregister():
    for km, kmi in _addon_keymaps:
        try:
            km.keymap_items.remove(kmi)
        except (ReferenceError, RuntimeError):
            pass
    _addon_keymaps.clear()
    if on_load_post in bpy.app.handlers.load_post:
        bpy.app.handlers.load_post.remove(on_load_post)
    if _draw_handle[0] is not None:
        bpy.types.SpaceView3D.draw_handler_remove(_draw_handle[0], 'WINDOW')
        _draw_handle[0] = None
    _live.clear()
    for cls in reversed(classes):
        if cls.is_registered:
            bpy.utils.unregister_class(cls)
