"""Galeria de estruturas de caixa na viewport (feature 015, T034 e T041; RN-11, RN-21, RF-11, RF-21, D-10, D-11).

`caffmob.structure_gallery` abre o quadro "Selecione uma estrutura de caixa para iniciar a construção" sobre a
`VIEW_3D` (desenho `POST_PIXEL`, núcleo puro em `gallery_core`). Uma aba por ambiente, uma miniatura por estrutura,
OK e Cancelar:
- OK (ou Enter, ou duplo clique): cria o módulo pelo `caffmob.cabinet_builder` com o `structure_id` (o passo de
  desfazer é do builder) e abre o editor de armário nele, como `library_panel/ops_cabinet.py`;
- Cancelar, Esc, botão direito, clique em outra área ou a área sumir: tira o desenho e não cria nada. O operador
  não tem 'UNDO': cancelar não deixa passo de desfazer.

Miniaturas (D-11): a elevação frontal sai de `structure.carcass_parts` nas medidas de referência e é desenhada ao
vivo em traço (contorno `TEXT_MUTED`, vão em teal `SUCCESS`). O cache guarda a geometria já calculada por estrutura
(milímetros, independente da escala), não uma textura: são poucos retângulos por célula, desenhados com as mesmas
primitivas da biblioteca, sem recurso de GPU a criar e liberar a cada mudança de escala ou tema.
"""

import bpy  # type: ignore
import gpu  # type: ignore

from ..data.i18n import N_, tr
from ..library_panel import draw_kit as kit, grid_core, style
from . import gallery_core as gc, structures_core

WARNING_MORE = N_("{} (mais {})")
WIDTH_MM = N_("{} · {} mm")
NO_VIEW = N_("Abra uma Vista 3D para escolher a estrutura")
BUILD_FAILED = N_("Não foi possível criar o armário pela estrutura escolhida")
BACKDROP = (0.0, 0.0, 0.0, 0.35)

# Sessão aberta (uma por vez). O desenho lê só daqui, nunca do operador: `unregister` pode tirar o desenho com o
# operador já liberado.
_session = {'handle': None, 'area': 0, 'state': None, 'mouse': (-1.0, -1.0)}
_thumbs = {}                        # Structure → elevação em mm (`gallery_core.thumb_shapes`)


def _scale(context):
    try:
        return context.preferences.system.ui_scale
    except AttributeError:
        return 1.0


def _title_font():
    """A Sora já carregada pelo painel da biblioteca (um `blf.load` só para o arquivo)."""
    from ..library_panel import draw as library_draw
    return library_draw._title_font()


def _layout(state, region, s):
    labels = [tr(label) for _id, label in state.tabs]
    return gc.layout(region.width, region.height, s, labels, lambda text: kit.width_of(text, style.FONT_BODY * s))


def _shapes(recipe):
    shapes = _thumbs.get(recipe)
    if shapes is None:
        shapes = _thumbs[recipe] = gc.thumb_shapes(recipe)
    return shapes


def _find(context, area_ptr):
    """(área, região WINDOW) da sessão na janela atual, ou (None, None) se a área sumiu."""
    screen = context.window.screen if context.window else None
    for area in (screen.areas if screen else ()):
        if area.as_pointer() == area_ptr:
            region = next((r for r in area.regions if r.type == 'WINDOW'), None)
            return (area, region) if region is not None else (None, None)
    return None, None


def _stop(context=None):
    """Tira o desenho e fecha a sessão (todos os caminhos de saída e o `unregister`)."""
    if _session['handle'] is not None:
        bpy.types.SpaceView3D.draw_handler_remove(_session['handle'], 'WINDOW')
    area_ptr = _session['area']
    _session.update(handle=None, area=0, state=None, mouse=(-1.0, -1.0))
    if context is not None and area_ptr:
        area, _region = _find(context, area_ptr)
        if area is not None:
            area.tag_redraw()


# Desenho ------------------------------------------------------------------------------------------------------------
def _clip(rect):
    previous = gpu.state.scissor_get()
    x, y, w, h = rect
    gpu.state.scissor_test_set(True)
    gpu.state.scissor_set(int(x), int(y), int(max(0, w)), int(max(0, h)))
    return previous


def _draw_thumb(recipe, box, viewport, s):
    shapes = gc.fit_shapes(_shapes(recipe), box)
    x0, fy, x1 = shapes['floor']
    kit.polyline([(x0, fy), (x1, fy)], style.TEXT_SUBTLE, 1.0, viewport)
    ix, iy, iw, ih = shapes['inner']
    kit.rect(ix, iy, iw, ih, (style.SUCCESS[0], style.SUCCESS[1], style.SUCCESS[2], 0.16))
    kit.outline(ix, iy, iw, ih, style.SUCCESS, viewport, 0.0, 1.0)
    for px, py, pw, ph in shapes['parts'] + shapes['dividers']:
        kit.rect(px, py, pw, ph, style.SURFACE_RAISED)
        kit.outline(px, py, pw, ph, style.TEXT_MUTED, viewport, 0.0, max(1.0, 1.2 * s))


def _draw_cell(recipe, rect, selected, hovered, viewport, s):
    x, y, w, h = rect
    if hovered or selected:
        kit.rect(x - 4 * s, y - 4 * s, w + 8 * s, h + 8 * s, style.SURFACE_HOVER, (style.RADIUS_CELL + 2) * s)
    side = style.CELL_W * s
    ty = y + h - side
    kit.rect(x, ty, side, side, style.SURFACE_SUNKEN, style.RADIUS_CELL * s)
    _draw_thumb(recipe, (x, ty, side, side), viewport, s)
    if selected:
        kit.outline(x - 1, ty - 1, side + 2, side + 2, style.ACCENT, viewport, style.RADIUS_CELL * s, 2.0)
    line_y = ty - 14 * s
    for line in kit.wrap2(tr(recipe.label_pt), style.FONT_LABEL * s, side):
        kit.text(line, x, line_y, style.FONT_LABEL * s, style.TEXT)
        line_y -= 13 * s
    detail = tr(WIDTH_MM).format(tr(gc.GROUP_LABELS.get(recipe.group, recipe.group)), int(round(recipe.width_mm)))
    kit.text(detail, x, line_y - 1 * s, style.FONT_SMALL * s, style.TEXT_MUTED if hovered or selected
             else style.TEXT_SUBTLE, max_w=side)


def _draw_empty(area, title, hint, viewport, s):
    ax, ay, aw, ah = area
    cx, cy = ax + aw / 2.0, ay + ah / 2.0
    kit.icon('ALERT', cx - 14 * s, cy + 40 * s, 28 * s, style.INFO, viewport)
    kit.text(title, cx - kit.width_of(title, style.FONT_TITLE * s) / 2.0, cy + 8 * s, style.FONT_TITLE * s, style.TEXT)
    if hint:
        hint = kit.clip(hint, style.FONT_BODY * s, aw)
        kit.text(hint, cx - kit.width_of(hint, style.FONT_BODY * s) / 2.0, cy - 16 * s, style.FONT_BODY * s,
                 style.TEXT_MUTED)


def _draw_tabs(lay, state, mouse, viewport, s):
    for index, rect in lay.tabs:
        x, y, w, h = rect
        active = index == state.tab
        if active:
            kit.rect(x, y, w, h, style.SURFACE_HOVER, style.RADIUS_CONTROL * s)
            kit.rect(x + 6 * s, y, w - 12 * s, 2 * s, style.SUCCESS)
        elif x <= mouse[0] <= x + w and y <= mouse[1] <= y + h:
            kit.rect(x, y, w, h, style.SURFACE_RAISED, style.RADIUS_CONTROL * s)
        kit.text_centered_y(tr(state.tabs[index][1]), rect, x + gc.TAB_PAD * s, style.FONT_BODY * s,
                            style.TEXT if active else style.TEXT_MUTED)


def _draw_grid(region, lay, state, mouse, viewport, s):
    if state.empty:
        title, hint = gc.empty_state(state.catalog)
        _draw_empty(lay.grid, title, hint, viewport, s)
        return
    if not state.items:
        _draw_empty(lay.grid, tr(gc.EMPTY_TAB), "", viewport, s)
        return
    count = len(state.items)
    content = gc.content_height(lay, count, s)
    state.scroll = grid_core.clamp_scroll(state.scroll, content, lay.grid[3])
    cells = gc.visible_cells(lay, count, s, state.scroll)
    hovered = gc.hit(lay, cells, *mouse)
    hovered = hovered[1] if hovered and hovered[0] == 'CELL' else None
    gx, gy, gw, gh = lay.grid
    previous = _clip((gx - 6 * s, gy, gw + 12 * s, gh + 6 * s))
    try:
        for index, rect in cells:
            _draw_cell(state.items[index], rect, index == state.index, index == hovered, viewport, s)
    finally:
        gpu.state.scissor_set(*previous)
    if content > gh:
        kit.rect(gx + gw - 3 * s, gy, 3 * s, gh, (1.0, 1.0, 1.0, 0.05), 1.5 * s)
        thumb_h = max(24 * s, gh * gh / content)
        thumb_y = gy + (gh - thumb_h) * (1.0 - state.scroll / max(1.0, content - gh))
        kit.rect(gx + gw - 3 * s, thumb_y, 3 * s, thumb_h, (1.0, 1.0, 1.0, 0.22), 1.5 * s)


def _button(rect, label, kind, hovered, viewport, s):
    """`kind`: 'PRIMARY' (laranja, ação principal), 'SECONDARY' ou 'DISABLED'."""
    x, y, w, h = rect
    if kind == 'PRIMARY':
        kit.rect(x, y, w, h, style.ACCENT, style.RADIUS_CONTROL * s)
        color = style.ACCENT_INK
    else:
        kit.rect(x, y, w, h, style.SURFACE_HOVER if hovered and kind != 'DISABLED' else style.SURFACE_RAISED,
                 style.RADIUS_CONTROL * s)
        kit.outline(x, y, w, h, style.BORDER_STRONG if kind != 'DISABLED' else style.BORDER, viewport,
                    style.RADIUS_CONTROL * s)
        color = style.TEXT if kind != 'DISABLED' else style.TEXT_SUBTLE
    text = tr(label)
    kit.text_centered_y(text, rect, x + (w - kit.width_of(text, style.FONT_BODY * s)) / 2.0, style.FONT_BODY * s,
                        color)


def _draw_footer(lay, state, mouse, viewport, s):
    fx, fy, fw, fh = lay.footer
    kit.polyline([(fx, fy + fh), (fx + fw, fy + fh)], style.BORDER, 1.0, viewport)
    kit.text_centered_y(state.status(), lay.status, lay.status[0], style.FONT_BODY * s, style.TEXT,
                        max_w=lay.status[2])
    warnings = state.catalog.warnings
    if warnings:
        wx, wy, ww, wh = lay.warning
        kit.icon('ALERT', wx, wy + (wh - 12 * s) / 2.0, 12 * s, style.INFO, viewport)
        text = warnings[0] if len(warnings) == 1 else tr(WARNING_MORE).format(warnings[0], len(warnings) - 1)
        kit.text_centered_y(text, lay.warning, wx + 18 * s, style.FONT_LABEL * s, style.TEXT_MUTED,
                            max_w=max(0.0, ww - 18 * s))
    hit = gc.hit(lay, [], *mouse)
    _button(lay.ok, gc.OK, 'PRIMARY' if state.selected is not None else 'DISABLED', hit == ('OK',), viewport, s)
    _button(lay.cancel, gc.CANCEL, 'SECONDARY', hit == ('CANCEL',), viewport, s)


def draw_gallery():
    context = bpy.context
    state = _session['state']
    area, region = context.area, context.region
    if state is None or area is None or region is None or region.type != 'WINDOW' \
            or area.as_pointer() != _session['area']:
        return
    s = _scale(context)
    viewport = (region.width, region.height)
    mouse = _session['mouse']
    lay = _layout(state, region, s)
    try:
        kit.rect(0, 0, region.width, region.height, BACKDROP)
        x, y, w, h = lay.rect
        kit.shadow(x, y, w, h, style.RADIUS_PANEL * s, s)
        kit.rect(x, y, w, h, style.SURFACE, style.RADIUS_PANEL * s)
        kit.outline(x, y, w, h, style.BORDER, viewport, style.RADIUS_PANEL * s)
        kit.text_centered_y(tr(gc.TITLE), lay.title, lay.title[0], style.FONT_TITLE * s, style.TEXT, _title_font(),
                            max_w=lay.title[2])
        _draw_tabs(lay, state, mouse, viewport, s)
        _draw_grid(region, lay, state, mouse, viewport, s)
        _draw_footer(lay, state, mouse, viewport, s)
    finally:
        gpu.state.blend_set('NONE')


# Operador -----------------------------------------------------------------------------------------------------------
def _view3d(context):
    """(área, região WINDOW) da Vista 3D: a do contexto, senão a maior da tela."""
    area = context.area
    if area is None or area.type != 'VIEW_3D':
        screen = context.window.screen if context.window else None
        views = [a for a in (screen.areas if screen else ()) if a.type == 'VIEW_3D']
        area = max(views, key=lambda a: a.width * a.height) if views else None
    if area is None:
        return None, None
    return area, next((r for r in area.regions if r.type == 'WINDOW'), None)


class BTM_OT_StructureGallery(bpy.types.Operator):
    """Escolha a estrutura de caixa para iniciar a construção de um armário"""
    bl_idname = "caffmob.structure_gallery"
    bl_label = "Novo armário pelo construtor"
    bl_options = {'REGISTER'}           # sem 'UNDO': o passo de desfazer é do `caffmob.cabinet_builder`

    environment: bpy.props.StringProperty(name="Ambiente", description="Aba que abre (ambiente ou linha, ex.: COZ)",
                                          default="", options={'SKIP_SAVE'})  # type: ignore

    @classmethod
    def poll(cls, context):
        return context.mode == 'OBJECT' and context.window is not None

    def invoke(self, context, event):
        area, region = _view3d(context)
        if area is None or region is None:
            self.report({'WARNING'}, tr(NO_VIEW))
            return {'CANCELLED'}
        _stop(context)                                  # uma galeria por vez
        _thumbs.clear()                                 # o catálogo pode ter mudado desde a última abertura
        _session.update(area=area.as_pointer(), state=gc.GalleryState(structures_core.load(), self.environment),
                        mouse=(event.mouse_x - region.x, event.mouse_y - region.y))
        _session['handle'] = bpy.types.SpaceView3D.draw_handler_add(draw_gallery, (), 'WINDOW', 'POST_PIXEL')
        context.window_manager.modal_handler_add(self)
        area.tag_redraw()
        return {'RUNNING_MODAL'}

    def cancel(self, context):
        _stop(context)

    def _close(self, context):
        _stop(context)
        return {'CANCELLED'}

    def _confirm(self, context):
        state = _session['state']
        recipe = state.selected if state is not None else None
        if recipe is None:
            return {'RUNNING_MODAL'}
        area, region = _find(context, _session['area'])
        _stop(context)
        try:
            with context.temp_override(window=context.window, area=area, region=region):
                result = bpy.ops.caffmob.cabinet_builder('EXEC_DEFAULT', structure_id=recipe.id)
                if 'FINISHED' not in result:
                    self.report({'WARNING'}, tr(BUILD_FAILED))
                    return {'CANCELLED'}
                if bpy.ops.caffmob.cabinet_editor.poll():
                    bpy.ops.caffmob.cabinet_editor('INVOKE_DEFAULT')
        except (RuntimeError, TypeError) as error:
            self.report({'ERROR'}, "{}: {}".format(tr(BUILD_FAILED), error))
            return {'CANCELLED'}
        return {'FINISHED'}

    def modal(self, context, event):
        state = _session['state']
        if state is None or _session['handle'] is None:
            return {'CANCELLED'}                        # fechada por fora (`unregister`, outra galeria)
        area, region = _find(context, _session['area'])
        if area is None:
            return self._close(context)                 # a área sumiu (fechada, trocou a tela)
        if event.type.startswith('TIMER'):
            return {'PASS_THROUGH'}
        mx, my = event.mouse_x - region.x, event.mouse_y - region.y
        inside_area = 0 <= mx <= region.width and 0 <= my <= region.height
        if event.type in ('MOUSEMOVE', 'INBETWEEN_MOUSEMOVE'):
            _session['mouse'] = (mx, my) if inside_area else (-1.0, -1.0)
            area.tag_redraw()
            return {'RUNNING_MODAL'} if inside_area else {'PASS_THROUGH'}
        s = _scale(context)
        lay = _layout(state, region, s)
        if event.value in ('PRESS', 'DOUBLE_CLICK') and event.type in ('LEFTMOUSE', 'RIGHTMOUSE') \
                and not inside_area:
            return self._close(context)                 # clique em outra área: sai sem criar nada
        if event.type == 'RIGHTMOUSE' and event.value == 'PRESS':
            return self._close(context)
        if event.type == 'LEFTMOUSE' and event.value in ('PRESS', 'DOUBLE_CLICK'):
            cells = gc.visible_cells(lay, len(state.items), s, state.scroll)
            target = gc.hit(lay, cells, mx, my)
            area.tag_redraw()
            if target == ('OK',):
                return self._confirm(context)
            if target == ('CANCEL',):
                return self._close(context)
            if target and target[0] == 'TAB':
                state.set_tab(target[1])
            elif target and target[0] == 'CELL':
                state.select(target[1])
                if event.value == 'DOUBLE_CLICK':
                    return self._confirm(context)
            return {'RUNNING_MODAL'}
        if event.type in ('WHEELUPMOUSE', 'WHEELDOWNMOUSE') and inside_area:
            step = (grid_core.CELL_H + grid_core.GAP) * s / 2.0
            delta = step if event.type == 'WHEELDOWNMOUSE' else -step
            state.scroll = gc.scroll_by(state.scroll, delta, lay, len(state.items), s)
            area.tag_redraw()
            return {'RUNNING_MODAL'}
        if event.value == 'PRESS' and event.type == 'TAB':
            state.next_tab(-1 if event.shift else 1)
            area.tag_redraw()
            return {'RUNNING_MODAL'}
        if event.value == 'PRESS':
            action = state.key(event.type, lay, s)
            area.tag_redraw()
            if action == 'OK':
                return self._confirm(context)
            if action == 'CANCEL':
                return self._close(context)
        return {'RUNNING_MODAL'} if inside_area else {'PASS_THROUGH'}


classes = (BTM_OT_StructureGallery,)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    _stop()
    _thumbs.clear()
    for cls in reversed(classes):
        if cls.is_registered:
            bpy.utils.unregister_class(cls)
