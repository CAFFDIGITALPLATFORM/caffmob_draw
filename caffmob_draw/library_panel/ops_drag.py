"""Arrastar uma célula da BIBLIOTECA CAFFMOB para a cena (feature 014, T032, T034; RN-10, D-07).

O clique numa célula (`ops_click`) vira este modal depois de 6 px × escala. A miniatura acompanha o cursor.

- **Textura** (T032): na soltura, um ray-cast acha o objeto sob o mouse e `texture_library.apply` aplica a textura
  ao alvo dele (peça, frente, módulo ou objeto). Soltar sobre o painel, no vazio ou numa cota não muda nada e mostra
  um aviso curto. Imagem ainda não baixada entra na fila e é aplicada ao concluir (etapa de desfazer própria).
- **Bloco** (T034): ao sair do retângulo, o módulo salvo passa para a inserção existente em
  `INVOKE_DEFAULT`, que segue o mouse e confirma na soltura do botão (`from_drag`, T033). Modelo pronto não tem
  inserção que acompanhe o mouse: entra no ponto da soltura (ray-cast, ou o piso), com o Padrão de Dimensões.
- Esc ou botão direito cancela. Cada soltura é uma etapa só de desfazer.
"""

import bpy  # type: ignore
import gpu  # type: ignore
from bpy_extras import view3d_utils  # type: ignore
from mathutils import Vector, geometry  # type: ignore

from ..data.i18n import N_, tr
from . import draw, draw_kit as kit, style, thumbs_gpu

EMPTY_DROP = N_("Solte sobre uma peça, frente, módulo ou objeto")
BLOCK_HINT = N_("Solte na cena para inserir")
TEXTURE_HINT = N_("Solte sobre a peça para aplicar a textura")


def _inside(rect, x, y):
    return rect[0] <= x <= rect[0] + rect[2] and rect[1] <= y <= rect[1] + rect[3]


def _entry(context, key):
    state = context.window_manager.btm_library
    for entry in draw.grid_entries(state):
        if draw.entry_key(entry) == key:
            return entry
    if not key.startswith("BLK:"):
        from ..texture_library import catalog
        return catalog.item(key)
    return None


def ray_hit(context, x, y):
    """(objeto, ponto) sob o pixel da região, ou (None, ponto no piso z=0 / None)."""
    region, rv3d = context.region, context.region_data
    if region is None or rv3d is None:
        return None, None
    origin = view3d_utils.region_2d_to_origin_3d(region, rv3d, (x, y))
    direction = view3d_utils.region_2d_to_vector_3d(region, rv3d, (x, y))
    hit, location, _normal, _index, obj, _matrix = context.scene.ray_cast(context.evaluated_depsgraph_get(), origin,
                                                                          direction)
    if hit:
        return obj, location
    floor = geometry.intersect_line_plane(origin, origin + direction * 1000.0, Vector((0, 0, 0)), Vector((0, 0, 1)))
    return None, floor


class BTM_OT_LibraryDrag(bpy.types.Operator):
    """Arraste uma textura ou um bloco da biblioteca para a cena"""
    bl_idname = "caffmob.library_drag"
    bl_label = "Arrastar da biblioteca"
    bl_options = {'REGISTER', 'UNDO'}

    key: bpy.props.StringProperty(options={'HIDDEN', 'SKIP_SAVE'})  # type: ignore
    start_x: bpy.props.FloatProperty(options={'HIDDEN', 'SKIP_SAVE'})  # type: ignore
    start_y: bpy.props.FloatProperty(options={'HIDDEN', 'SKIP_SAVE'})  # type: ignore

    @classmethod
    def poll(cls, context):
        return context.area is not None and context.area.type == 'VIEW_3D' and context.region is not None \
            and context.region.type == 'WINDOW'

    def invoke(self, context, event):
        # O `event` de um operador chamado por outro modal não é confiável: a posição vem das propriedades.
        self.entry = _entry(context, self.key)
        if self.entry is None:
            return {'CANCELLED'}
        self.block = self.key.startswith("BLK:")
        self.pos = (self.start_x, self.start_y)
        self.panel = draw.max_rect(context, context.area)
        self.region = context.region
        draw._selected['id'] = self.key
        self._handle = bpy.types.SpaceView3D.draw_handler_add(self._draw, (), 'WINDOW', 'POST_PIXEL')
        context.window.cursor_modal_set('HAND')
        context.area.header_text_set(tr("{}  ·  Esc: cancelar").format(tr(BLOCK_HINT if self.block else TEXTURE_HINT)))
        context.window_manager.modal_handler_add(self)
        context.area.tag_redraw()
        return {'RUNNING_MODAL'}

    # Miniatura sob o cursor ------------------------------------------------------------------------------------------
    def _draw(self):
        if bpy.context.region != self.region:
            return
        s = draw._scale(bpy.context)
        side = 56 * s
        x, y = self.pos[0] + 12 * s, self.pos[1] - side - 12 * s
        kit.shadow(x, y, side, side, style.RADIUS_CELL * s, s)
        kit.rect(x, y, side, side, style.SURFACE_SUNKEN, style.RADIUS_CELL * s)
        path = self.entry.get("thumb_file") if self.block else None
        if not self.block:
            from ..texture_library import catalog
            path = catalog.thumb_path(self.entry)
        tex = thumbs_gpu.texture(self.key, path) if path else None
        if tex is not None:
            kit.image(tex, x, y, side, side, src_size=self.entry.get("px"))
        kit.outline(x, y, side, side, style.ACCENT, (self.region.width, self.region.height), style.RADIUS_CELL * s,
                    2.0)
        gpu.state.blend_set('NONE')

    def _cleanup(self, context):
        if self._handle is not None:
            bpy.types.SpaceView3D.draw_handler_remove(self._handle, 'WINDOW')
            self._handle = None
        try:
            context.window.cursor_modal_restore()
            context.area.header_text_set(None)
            context.area.tag_redraw()
        except (AttributeError, ReferenceError):
            pass

    def cancel(self, context):
        self._cleanup(context)

    # Modal ----------------------------------------------------------------------------------------------------------
    def modal(self, context, event):
        if event.type in ('ESC', 'RIGHTMOUSE') and event.value == 'PRESS':
            self._cleanup(context)
            return {'CANCELLED'}
        if event.type in ('MOUSEMOVE', 'INBETWEEN_MOUSEMOVE'):
            self.pos = (event.mouse_region_x, event.mouse_region_y)
            context.area.tag_redraw()
            if self.block and self.entry.get("kind") != 'MODEL' and not _inside(self.panel, *self.pos):
                return self._hand_off(context)
            return {'RUNNING_MODAL'}
        if event.type == 'LEFTMOUSE' and event.value == 'RELEASE':
            self.pos = (event.mouse_region_x, event.mouse_region_y)
            self._cleanup(context)
            return self.drop(context, *self.pos)
        if event.type in ('MIDDLEMOUSE', 'WHEELUPMOUSE', 'WHEELDOWNMOUSE'):
            return {'PASS_THROUGH'}
        return {'RUNNING_MODAL'}

    def _hand_off(self, context):
        """Bloco que sai do retângulo: a inserção existente segue o mouse e confirma na soltura (T033, T034)."""
        self._cleanup(context)
        entry = self.entry
        if entry["kind"] == 'MODULE':
            bpy.ops.caffmob.module_insert('INVOKE_DEFAULT', filepath=entry["blend"], from_drag=True)
        return {'CANCELLED'}                              # a etapa de desfazer é da inserção

    def drop(self, context, x, y):
        """Soltura em (x, y) da região (também chamado pelos testes)."""
        if _inside(self.panel, x, y):
            return {'CANCELLED'}                          # voltou para o painel: nada muda
        obj, point = ray_hit(context, x, y)
        if self.block:
            return self._drop_model(context, point)
        from ..texture_library import apply
        if obj is None or not apply.targets(obj):
            self.report({'WARNING'}, tr(EMPTY_DROP))
            return {'CANCELLED'}
        # (067 RF-040) Pergunta onde aplicar; nada muda antes de confirmar, e o download espera o OK.
        bpy.ops.caffmob.finish_drop('INVOKE_DEFAULT', key=self.key, object_name=obj.name)
        return {'CANCELLED'}                              # o passo de Undo é o da aplicação

    def _drop_model(self, context, point):
        if self.entry.get("kind") != 'MODEL' or point is None:
            self.report({'WARNING'}, tr(EMPTY_DROP))
            return {'CANCELLED'}
        cursor = context.scene.cursor
        before = cursor.location.copy()
        cursor.location = (point.x, point.y, 0.0)        # no piso; o aéreo sobe para a altura do padrão
        try:
            result = bpy.ops.caffmob.library_insert_model('EXEC_DEFAULT', model_id=self.entry["model"],
                                                         line=self.entry.get("line", 'COZ'))
        finally:
            cursor.location = before
        return {'FINISHED'} if 'FINISHED' in result else {'CANCELLED'}


classes = (BTM_OT_LibraryDrag,)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        if cls.is_registered:
            bpy.utils.unregister_class(cls)
