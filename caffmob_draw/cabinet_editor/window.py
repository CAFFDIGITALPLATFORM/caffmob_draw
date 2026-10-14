"""Janela do Editor de Armário e o desenho da vista frontal (feature 004, T043; RF-02, D-20, D-23).

A janela é a mesma mecânica do Editor de Paredes (`canvas2d/window.py`): uma janela nova com um Image Editor sem
imagem, os painéis na aba "Editor de Armário" e um handler `POST_PIXEL` global que só desenha na área do editor.

O desenho mostra o módulo de frente (x, z): estrutura, vãos tracejados, prateleiras e divisórias, frentes por cima, o
componente selecionado destacado, os componentes com mensagem marcados em vermelho e as medidas do módulo.

Feature 006 (T024): na aba Divisão, os subvãos livres aparecem tracejados e o escolhido em destaque, com o nome em
texto; as chapas removidas aparecem tracejadas com "removido" (o estado nunca só na cor).

Feature 008 (T034; D-05, D-06, D-09): o vão escolhido aparece em todas as abas; barra "Selecionado: …" no rodapé da
vista; linhas de abertura tracejadas nas portas (do lado da dobradiça ao meio do lado oposto); nas abas Gavetas e
Portas, o vão da biblioteca que vai receber a frente fica contornado, com aviso quando é maior que o vão escolhido.
"""

import bpy  # type: ignore

from ..canvas2d import draw
from ..canvas2d import window as _window
from ..canvas2d.view import View2D
from ..data import units
from ..data.i18n import tr
from ..library_panel import style as _style
from . import elevation, props

_draw_handle = []

FILL = {
    elevation.STRUCTURE: (0.55, 0.42, 0.28, 0.55),
    elevation.SHELF: (0.62, 0.50, 0.34, 0.75),
    elevation.DIVIDER: (0.62, 0.50, 0.34, 0.75),
    elevation.FRONT: (0.82, 0.82, 0.86, 0.35),
    elevation.AGGREGATE: (0.35, 0.65, 0.95, 0.45),
    elevation.PART: (0.6, 0.6, 0.6, 0.4),
}
# Feature 015 (T035; D-12, RN-21): cores da identidade CAFF MOBI (família Noite da 014, `library_panel/style.py`):
# laranja só na seleção, teal no vão, azul na informação; o estado continua também em texto.
EDGE = _style.TEXT_MUTED
OPENING_EDGE = _style.TEXT_SUBTLE
SELECTED = _style.ACCENT
FLAGGED = _style.ERROR
BACKGROUND = _style.hex_rgba("#10302F")
SPACE_EDGE = _style.SUCCESS[:3] + (0.75,)
SPACE_FILL = _style.SUCCESS[:3] + (0.18,)
REMOVED_EDGE = _style.ERROR[:3] + (0.8,)
SWING = _style.SUCCESS
LIBRARY_EDGE = _style.INFO
STATUS_BG = _style.SURFACE_RAISED


def session():
    return props.session()


def editor_area(context):
    return _window.editor_area(context, session())


def is_editor_area(context):
    return _window.is_editor_area(context, session())


def open_editor(context):
    return _window.open_window(context, session(), tr("O Editor de Armário precisa de uma janela do Blender aberta."))


def focus_tab(area):
    return _window.focus_tab(area, props.EDITOR_CATEGORY)


def close_later(s):
    _window.close_later(s.window_ptr, s.area_ptr, s.restore_area_type)


def window_alive(context):
    return _window.window_alive(context, session())


def over_side_panel(area, x, y):
    return _window.over_side_panel(area, x, y)


def _rect(region, area):
    return (0.0, 0.0, _window.visible_width(area, region), float(region.height))


def ensure_view(region, area):
    """Vista 2D da área; reenquadra quando o tamanho da área ou do módulo muda."""
    s = session()
    rect = _rect(region, area)
    bounds = elevation.bounds(s.parts) or (0.0, 0.0, 1.0, 1.0)
    key = (rect, tuple(round(b, 4) for b in bounds))
    if s.view is None or getattr(s, 'view_key', None) != key:
        s.view = View2D(rect)
        s.view.fit(((bounds[0], bounds[1]), (bounds[2], bounds[3])), margin=0.18)
        s.view_key = key
    return s.view


def _dashed_rect(sh, view, x0, z0, x1, z1, color):
    a, b = view.to_screen((x0, z0)), view.to_screen((x1, z1))
    pts = []
    for p, q in (((a[0], a[1]), (b[0], a[1])), ((b[0], a[1]), (b[0], b[1])),
                 ((b[0], b[1]), (a[0], b[1])), ((a[0], b[1]), (a[0], a[1]))):
        pts += draw.dashed(p, q)
    draw.lines(sh, pts, color)
    return a, b


def _draw_006(sh, view, s, divisions_tab):
    """Chapas removidas e, na aba Divisão, os subvãos; devolve os textos a escrever depois do `draw.end()`."""
    labels = []
    for part in s.removed_parts:
        x0, z0, x1, z1 = part.rect
        a, b = _dashed_rect(sh, view, x0, z0, x1, z1, REMOVED_EDGE)
        labels.append(((a[0] + b[0]) / 2.0, (a[1] + b[1]) / 2.0, tr("removido"), REMOVED_EDGE))
    for path, box in s.spaces.items():
        x0, z0, x1, z1 = box.lo[0], box.lo[2], box.hi[0], box.hi[2]
        if path == s.space:
            r = draw.box(sh, view, (x0, z0), (x1, z1), SELECTED, fill=SPACE_FILL)
            draw.outline(sh, (r[0] - 2, r[1] - 2, r[2] + 4, r[3] + 4), SELECTED)
            a, b = view.to_screen((x0, z0)), view.to_screen((x1, z1))
            label = s.space_labels.get(path, path)
            labels.append(((a[0] + b[0]) / 2.0, (a[1] + b[1]) / 2.0, label, SELECTED))
        elif divisions_tab:
            _dashed_rect(sh, view, x0, z0, x1, z1, SPACE_EDGE)
    return labels


def _hinge(name):
    low = name.lower()
    if 'flip' in low or 'bascul' in low:
        return 'TOP'
    if 'right' in low or '_r' in low[-4:] or 'direit' in low:
        return 'RIGHT'
    return 'LEFT'


def _swing_lines(sh, view, s):
    """Linhas de abertura das portas (D-09): do lado da dobradiça até o meio do lado oposto."""
    pts = []
    for part in s.parts:
        if part.kind != elevation.FRONT or 'drawer' in part.name.lower() or 'gaveta' in part.name.lower():
            continue
        x0, z0, x1, z1 = part.rect
        xm, zm = (x0 + x1) / 2.0, (z0 + z1) / 2.0
        hinge = _hinge(part.name)
        if hinge == 'TOP':
            segs = (((x0, z1), (xm, z0)), ((x1, z1), (xm, z0)))
        elif hinge == 'RIGHT':
            segs = (((x1, z1), (x0, zm)), ((x1, z0), (x0, zm)))
        else:
            segs = (((x0, z1), (x1, zm)), ((x0, z0), (x1, zm)))
        for a, b in segs:
            pts += draw.dashed(view.to_screen(a), view.to_screen(b))
    if pts:
        draw.lines(sh, pts, SWING)


def _library_outline(sh, view, s, labels):
    box = s.library_box
    if box is None:
        return
    a, b = view.to_screen((box.lo[0], box.lo[2])), view.to_screen((box.hi[0], box.hi[2]))
    draw.outline(sh, (a[0] - 3, a[1] - 3, b[0] - a[0] + 6, b[1] - a[1] + 6), LIBRARY_EDGE)
    space = s.spaces.get(s.space)
    if space is not None and (box.size(0) > space.size(0) + 1e-4 or box.size(2) > space.size(2) + 1e-4):
        labels.append(((a[0] + b[0]) / 2.0, a[1] + 8, tr("A frente ocupa o vão inteiro da biblioteca"),
                       LIBRARY_EDGE))


def status_text(s):
    """Texto da barra "Selecionado: …" (D-06)."""
    if s.selected:
        return tr("Selecionado: {}").format(s.selected)
    if s.space and s.space in s.spaces:
        return tr("Selecionado: {}").format(s.space_labels.get(s.space, s.space))
    return tr("Selecionado: (nenhum)")


def _status_bar(region, s):
    sh = draw.begin()
    draw.rect(sh, (0, 0, region.width, 24), STATUS_BG)
    draw.end()
    draw.text(10, 7, status_text(s), color=_style.TEXT)
    _type_header(region, s)


def _type_header(region, s):
    """"Tipo: <estrutura>" no alto da vista, em Sora (feature 015, D-12); sem a fonte, a da interface."""
    from ..library_panel import draw as library_draw
    from .panels import cabinet_type
    root = s.root()
    if root is None:
        return
    try:
        label = tr("Tipo: {}").format(cabinet_type(root, s.library))
    except (AttributeError, KeyError):
        return
    from .. import hb_gpu_draw
    hb_gpu_draw.draw_text(library_draw._title_font(), 12, region.height - 24, 14, _style.TEXT, label)


def draw_editor(context):
    s = session()
    region = context.region
    if s is None or region is None:
        return
    view = ensure_view(region, context.area)
    flagged = {m.component for m in s.messages if m.component}
    sh = draw.begin()
    draw.rect(sh, (0, 0, region.width, region.height), BACKGROUND)
    for part in elevation.draw_order(s.parts):
        x0, z0, x1, z1 = part.rect
        if part.kind == elevation.OPENING:
            a, b = view.to_screen((x0, z0)), view.to_screen((x1, z1))
            pts = []
            for p, q in (((a[0], a[1]), (b[0], a[1])), ((b[0], a[1]), (b[0], b[1])),
                         ((b[0], b[1]), (a[0], b[1])), ((a[0], b[1]), (a[0], a[1]))):
                pts += draw.dashed(p, q)
            draw.lines(sh, pts, OPENING_EDGE)
            continue
        color = FLAGGED if part.name in flagged else EDGE
        draw.box(sh, view, (x0, z0), (x1, z1), color, fill=FILL.get(part.kind, FILL[elevation.PART]))
    tab = context.window_manager.btm_cabinet_editor.tab
    divisions_tab = tab == 'DIVISIONS'
    labels = _draw_006(sh, view, s, divisions_tab)
    _swing_lines(sh, view, s)
    if tab in ('DRAWERS', 'DOORS'):
        _library_outline(sh, view, s, labels)
    if s.selected:
        part = next((p for p in s.parts if p.name == s.selected), None)
        if part is not None:
            x0, z0, x1, z1 = part.rect
            r = draw.box(sh, view, (x0, z0), (x1, z1), SELECTED)
            draw.outline(sh, (r[0] - 2, r[1] - 2, r[2] + 4, r[3] + 4), SELECTED)
    draw.end()
    for x, y, text, color in labels:
        draw.text(x - draw.text_width(text) / 2.0, y, text, color=color)
    _labels(view, s)
    _status_bar(region, s)


def _labels(view, s):
    bounds = elevation.bounds(s.parts)
    if bounds is None:
        return
    x0, z0, x1, z1 = bounds
    width, height, depth = s.draft.current.dimensions
    bottom = view.to_screen(((x0 + x1) / 2.0, z0))
    label = units.format_value(width)
    draw.text(bottom[0] - draw.text_width(label) / 2.0, bottom[1] - 20, label)
    side = view.to_screen((x1, (z0 + z1) / 2.0))
    draw.text(side[0] + 8, side[1], units.format_value(height))
    title = "{}  —  {} × {} × {}".format(s.root_name, units.format_value(width), units.format_value(height),
                                         units.format_value(depth))
    top = view.to_screen((x0, z1))
    draw.text(top[0], top[1] + 16, title)
    status = tr("Rascunho alterado") if s.draft.dirty() else tr("Sem alterações")
    if s.blocking():
        status = tr("{} — corrija os erros para confirmar").format(status)
    draw.text(top[0], top[1] + 34, status, color=FLAGGED if s.blocking() else draw.COLORS['muted'])


def _draw():
    if is_editor_area(bpy.context):
        draw_editor(bpy.context)


def register():
    if not _draw_handle:
        _draw_handle.append(bpy.types.SpaceImageEditor.draw_handler_add(_draw, (), 'WINDOW', 'POST_PIXEL'))


def unregister():
    while _draw_handle:
        bpy.types.SpaceImageEditor.draw_handler_remove(_draw_handle.pop(), 'WINDOW')
