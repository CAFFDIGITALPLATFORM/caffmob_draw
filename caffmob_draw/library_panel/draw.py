"""Desenho do painel BIBLIOTECA CAFFMOB no topo da viewport (feature 012, T020; D-13, D-14, RN-01).

Um desenho `POST_PIXEL` sempre registrado (o painel aparece com ou sem o HUD). Ele sai cedo fora da região principal
da `VIEW_3D`. O layout por região fica em cache (chave: tamanho, escala, aberto, itens) para não refazer contas a cada
quadro; o clique (`ops_click`) usa o mesmo layout.
"""

import blf  # type: ignore
import bpy  # type: ignore
import gpu  # type: ignore

from ..data.i18n import tr
from ..hb_gpu_draw import draw_rect, draw_rect_outline, draw_text, get_visible_window_bounds
from . import categories, layout_core

FONT_SIZE = 11
BG = (0.13, 0.13, 0.14, 0.95)
BG_HOVER = (0.25, 0.25, 0.27, 0.96)
BG_TITLE = (0.20, 0.43, 0.70, 0.98)
BORDER = (1.0, 1.0, 1.0, 0.14)
TEXT = (0.90, 0.90, 0.90, 1.0)

_handle = [None]
_mouse = {'pos': (-1, -1), 'region': 0}
_cache = {}


def _scale(context):
    try:
        return context.preferences.system.ui_scale
    except AttributeError:
        return 1.0


def _nav_right(context, area):
    """Borda direita do botão de navegação do HUD, quando o HUD está ligado; senão None."""
    from ..operators import viewport_hud
    if not viewport_hud._hud_enabled():
        return None
    for widget, rect in viewport_hud.compute_layout(context, area):
        if isinstance(widget, viewport_hud._NavButton):
            return rect[0] + rect[2]
    return None


def offer_groups():
    """Há grupos salvos das bibliotecas herdadas para oferecer converter (D-30)?"""
    try:
        from ..legacy import groups
        return groups.should_offer()
    except (ImportError, AttributeError, OSError):
        return False


def items(context):
    names = [c.name for c in categories.all_categories()]
    return [(key, tr(label)) for key, label in layout_core.menu_items(names, offer_groups())]


def layout(context, area, region):
    state = context.window_manager.btm_library
    scale = _scale(context)
    entries = items(context) if state.open else []
    x_min, _x_max, _y_min, y_max = get_visible_window_bounds(area)
    key = (x_min, y_max, scale, state.open, tuple(entries), _nav_right(context, area))
    cached = _cache.get(region.as_pointer())
    if cached is not None and cached[0] == key:
        return cached[1]
    size = FONT_SIZE * scale
    blf.size(0, size)
    result = layout_core.panel_layout(x_min, y_max, scale, key[5], state.open, entries,
                                      lambda text: blf.dimensions(0, text)[0])
    _cache[region.as_pointer()] = (key, result)
    return result


def _text(rect, label, size):
    x, y, _w, h = rect
    blf.size(0, size)
    _tw, th = blf.dimensions(0, label)
    draw_text(0, x + layout_core.PAD_X * size / FONT_SIZE, y + (h - th) / 2.0, size, TEXT, label)


def draw_panel():
    context = bpy.context
    area, region = context.area, context.region
    if area is None or area.type != 'VIEW_3D' or region is None or region.type != 'WINDOW':
        return
    state = getattr(context.window_manager, 'btm_library', None)
    if state is None:
        return
    lay = layout(context, area, region)
    mouse = _mouse['pos'] if _mouse['region'] == region.as_pointer() else (-1, -1)
    hovered = layout_core.hit(lay, *mouse)
    size = FONT_SIZE * _scale(context)
    labels = dict(items(context)) if state.open else {}
    gpu.state.blend_set('ALPHA')
    shader = gpu.shader.from_builtin('UNIFORM_COLOR')
    shader.bind()
    draw_rect(shader, *lay.label, BG_HOVER if hovered == 'LABEL' else BG_TITLE)
    draw_rect_outline(shader, *lay.label, BORDER)
    for key, rect in lay.items:
        draw_rect(shader, *rect, BG_HOVER if hovered == key else BG)
        draw_rect_outline(shader, *rect, BORDER)
    gpu.state.blend_set('NONE')
    _text(lay.label, layout_core.TITLE, size)
    for key, rect in lay.items:
        _text(rect, labels.get(key, key), size)


def tag_redraw(context):
    for window in context.window_manager.windows:
        for area in window.screen.areas:
            if area.type == 'VIEW_3D':
                area.tag_redraw()


def register():
    if _handle[0] is None:
        _handle[0] = bpy.types.SpaceView3D.draw_handler_add(draw_panel, (), 'WINDOW', 'POST_PIXEL')


def unregister():
    if _handle[0] is not None:
        bpy.types.SpaceView3D.draw_handler_remove(_handle[0], 'WINDOW')
        _handle[0] = None
    _cache.clear()
