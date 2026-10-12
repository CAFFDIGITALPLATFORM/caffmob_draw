"""Criação de placa e caixa por pontos de referência (T032; RF-11, D-18).

`caffmob.geometry_create` (modal na viewport):
1. o primeiro clique marca o canto (raycast na cena por `hb_snap`; Ctrl encaixa em vértices e arestas);
2. o mouse define largura e profundidade no plano horizontal do canto; o segundo clique confirma;
3. na caixa, o mouse define a altura (plano vertical voltado para a vista); o terceiro clique confirma.
Em qualquer passo, digitar um número e Enter fixa a medida do passo (largura, depois profundidade, depois altura).
Esc ou botão direito cancela e não deixa objeto na cena.
"""

import bpy  # type: ignore
from bpy_extras import view3d_utils  # type: ignore
from mathutils import Vector  # type: ignore
from mathutils.geometry import intersect_line_plane  # type: ignore

from ..data.i18n import tr
from .. import hb_snap
from ..data import units
from . import mesh

DRAW_FLAG = 'HB_CURRENT_DRAW_OBJ'
MIN_SIZE = 0.001


class BTM_OT_GeometryCreate(bpy.types.Operator):
    """Cria uma placa ou caixa por pontos de referência no ambiente"""
    bl_idname = "caffmob.geometry_create"
    bl_label = "Criar Geometria"
    bl_options = {'REGISTER', 'UNDO'}

    kind: bpy.props.EnumProperty(name="Forma", items=[('PLACA', "Placa", ""), ('CAIXA', "Caixa", "")],
                                 default='PLACA')  # type: ignore

    @classmethod
    def poll(cls, context):
        return context.area is not None and context.area.type == 'VIEW_3D' and context.mode == 'OBJECT'

    def invoke(self, context, event):
        self.region = context.region
        self.mouse_pos = Vector((event.mouse_region_x, event.mouse_region_y))
        self.step = 0                 # 0 canto, 1 largura/profundidade, 2 altura (caixa)
        self.corner = None
        self.typed = ""
        self.typed_width = None
        self.obj = mesh.create_object(context, self.kind)
        self.obj[DRAW_FLAG] = True
        g = self.obj.btm_geometry
        g.width = g.depth = MIN_SIZE * 10
        if self.kind == 'CAIXA':
            g.height = MIN_SIZE * 10
        context.window_manager.modal_handler_add(self)
        self._header(context)
        return {'RUNNING_MODAL'}

    # Geometria -------------------------------------------------------------------------------------------------
    def _ray(self):
        origin = view3d_utils.region_2d_to_origin_3d(self.region, self.region.data, self.mouse_pos)
        vector = view3d_utils.region_2d_to_vector_3d(self.region, self.region.data, self.mouse_pos)
        return origin, vector

    def _hit(self, context, ctrl):
        hb_snap.main(self, ctrl, context)
        return Vector(self.hit_location) if self.hit_location is not None else None

    def _on_plane(self, point, normal):
        origin, vector = self._ray()
        return intersect_line_plane(origin, origin + vector * 1.0e6, point, normal)

    def _update_footprint(self, point):
        g = self.obj.btm_geometry
        dx, dy = point.x - self.corner.x, point.y - self.corner.y
        g.width = self.typed_width if self.typed_width is not None else max(MIN_SIZE, abs(dx))
        g.depth = max(MIN_SIZE, abs(dy))
        self.negative = (dx < 0, dy < 0)
        self._place_from_corner()

    def _place_from_corner(self):
        """O canto clicado continua canto da peça, com as medidas já limitadas pela propriedade (EC-06, EC-07)."""
        g = self.obj.btm_geometry
        neg_x, neg_y = getattr(self, 'negative', (False, False))
        self.obj.location = (self.corner.x - (g.width if neg_x else 0.0), self.corner.y - (g.depth if neg_y else 0.0),
                             self.corner.z)

    def _update_height(self):
        origin, vector = self._ray()
        normal = Vector((vector.x, vector.y, 0.0))
        if normal.length < 1e-6:
            return
        anchor = self.obj.location.copy()
        point = intersect_line_plane(origin, origin + vector * 1.0e6, anchor, normal.normalized())
        if point is not None:
            self.obj.btm_geometry.height = max(MIN_SIZE, point.z - anchor.z)

    # Eventos ---------------------------------------------------------------------------------------------------
    def modal(self, context, event):
        context.area.tag_redraw()
        if hb_snap.event_is_pass_through(event):
            return {'PASS_THROUGH'}
        if event.type in {'ESC', 'RIGHTMOUSE'} and event.value == 'PRESS':
            return self._cancel(context)
        if event.type == 'MOUSEMOVE':
            self.mouse_pos = Vector((event.mouse_region_x, event.mouse_region_y))
            self._move(context, event.ctrl)
            return {'RUNNING_MODAL'}
        if event.value == 'PRESS' and event.unicode and event.unicode in "0123456789,.":
            self.typed += event.unicode
            self._header(context)
            return {'RUNNING_MODAL'}
        if event.type == 'BACK_SPACE' and event.value == 'PRESS':
            self.typed = self.typed[:-1]
            self._header(context)
            return {'RUNNING_MODAL'}
        if event.type in {'RET', 'NUMPAD_ENTER'} and event.value == 'PRESS' and self.typed and self.step > 0:
            return self._typed_value(context)
        if event.type == 'LEFTMOUSE' and event.value == 'PRESS':
            return self._advance(context)
        return {'RUNNING_MODAL'}

    def _move(self, context, ctrl):
        if self.step == 0:
            hit = self._hit(context, ctrl)
            if hit is not None:
                self.obj.location = hit
        elif self.step == 1:
            point = self._on_plane(self.corner, Vector((0, 0, 1)))
            if point is not None:
                self._update_footprint(point)
        else:
            self._update_height()
        self._header(context)

    def _advance(self, context):
        if self.step == 0:
            self.corner = self.obj.location.copy()
            self.step = 1
        elif self.step == 1 and self.kind == 'CAIXA':
            self.step = 2
        else:
            return self._finish(context)
        self._header(context)
        return {'RUNNING_MODAL'}

    def _typed_value(self, context):
        try:
            value = units.parse_length(self.typed, units.get_scene_length_unit(), allow_zero=False)
        except ValueError as exc:
            self.report({'WARNING'}, str(exc))
            self.typed = ""
            return {'RUNNING_MODAL'}
        self.typed = ""
        g = self.obj.btm_geometry
        if self.step == 1 and self.typed_width is None:
            g.width = value
            self.typed_width = g.width                  # já no limite de 0,001 a 10 m
            self._place_from_corner()
        elif self.step == 1:
            g.depth = value
            self._place_from_corner()
            return self._advance(context)
        else:
            g.height = value
            return self._finish(context)
        self._header(context)
        return {'RUNNING_MODAL'}

    def _header(self, context):
        g = self.obj.btm_geometry
        unit = units.get_scene_length_unit()
        fmt = lambda v: units.format_length(v, unit)  # noqa: E731
        typed = tr("  Digitado: {}").format(self.typed) if self.typed else ""
        if self.step == 0:
            text = tr("Clique o canto da peça (Ctrl encaixa em vértices e arestas). Esc cancela.")
        elif self.step == 1:
            label = tr("Largura") if self.typed_width is None else tr("Profundidade")
            text = tr("Largura {} × Profundidade {} — digite a {} e Enter, ou clique.{}").format(fmt(g.width), fmt(g.depth), label, typed)
        else:
            text = tr("Altura {} — digite e Enter, ou clique.{}").format(fmt(g.height), typed)
        context.area.header_text_set(text)

    def _finish(self, context):
        context.area.header_text_set(None)
        del self.obj[DRAW_FLAG]
        for other in context.selected_objects:
            other.select_set(False)
        self.obj.select_set(True)
        context.view_layer.objects.active = self.obj
        return {'FINISHED'}

    def _cancel(self, context):
        if context.area is not None:
            context.area.header_text_set(None)
        try:
            data = self.obj.data
            bpy.data.objects.remove(self.obj, do_unlink=True)
        except ReferenceError:              # o arquivo já foi trocado: o provisório saiu com ele
            return {'CANCELLED'}
        if data.users == 0:
            bpy.data.meshes.remove(data)
        return {'CANCELLED'}

    def cancel(self, context):
        """O Blender interrompeu o modal (abrir arquivo, fechar janela): o provisório e o cabeçalho não ficam (EC-01)."""
        self._cancel(context)


classes = (BTM_OT_GeometryCreate,)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
