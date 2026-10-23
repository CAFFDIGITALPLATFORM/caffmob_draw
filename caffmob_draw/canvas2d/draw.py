"""Desenho das telas 2D (T018; D-01). Usado dentro de handlers `POST_PIXEL`.

Primitivas em pixels sobre `hb_gpu_draw.py` (retângulo, contorno, linhas, texto) e em coordenadas do mundo 2D por
uma `canvas2d.view.View2D`. Todas as cores são RGBA. A unidade dos rótulos é a do usuário (`data/units.py`).
"""

import math

import blf  # type: ignore
import gpu  # type: ignore
from gpu_extras.batch import batch_for_shader  # type: ignore

from .. import compat, hb_gpu_draw
from ..data import units
from ..data.i18n import tr

FONT = 0
FONT_SIZE = 12

COLORS = {
    'panel': (0.11, 0.11, 0.12, 0.94),
    'pane': (0.17, 0.17, 0.18, 1.0),
    'border': (1.0, 1.0, 1.0, 0.18),
    'text': (0.92, 0.92, 0.92, 1.0),
    'muted': (0.65, 0.65, 0.68, 1.0),
    'reference': (0.25, 0.65, 1.0, 1.0),      # B
    'moving': (1.0, 0.62, 0.15, 1.0),         # A
    'target': (0.55, 0.55, 0.6, 0.55),
    'target_hot': (0.35, 1.0, 0.45, 1.0),
    'warning': (1.0, 0.35, 0.3, 1.0),
    'button': (0.26, 0.26, 0.28, 1.0),
    'button_hot': (0.36, 0.36, 0.40, 1.0),
    'button_primary': (0.2, 0.45, 0.8, 1.0),
}


def shader():
    sh = compat.get_builtin_shader('UNIFORM_COLOR')
    sh.bind()
    return sh


def begin():
    gpu.state.blend_set('ALPHA')
    return shader()


def end():
    gpu.state.blend_set('NONE')


# Pixels --------------------------------------------------------------------------------------------------------

def rect(sh, r, color):
    hb_gpu_draw.draw_rect(sh, r[0], r[1], r[2], r[3], color)


def outline(sh, r, color):
    hb_gpu_draw.draw_rect_outline(sh, r[0], r[1], r[2], r[3], color)


def lines(sh, points, color):
    if points:
        hb_gpu_draw.draw_lines(sh, points, color)


def dashed(p0, p1, dash=6.0, gap=4.0):
    """Pontos (pares) de uma linha tracejada entre p0 e p1, em pixels."""
    length = math.hypot(p1[0] - p0[0], p1[1] - p0[1])
    if length < 1e-6:
        return []
    ux, uy = (p1[0] - p0[0]) / length, (p1[1] - p0[1]) / length
    pts, t = [], 0.0
    while t < length:
        e = min(t + dash, length)
        pts += [(p0[0] + ux * t, p0[1] + uy * t), (p0[0] + ux * e, p0[1] + uy * e)]
        t = e + gap
    return pts


def text(x, y, value, color=None, size=FONT_SIZE):
    """Texto na tela, traduzido para o idioma da interface (o catálogo tem o texto do código como chave)."""
    hb_gpu_draw.draw_text(FONT, x, y, size, color or COLORS['text'], tr(value))


def text_width(value, size=FONT_SIZE):
    blf.size(FONT, size)
    return blf.dimensions(FONT, tr(value))[0]


def button(sh, r, label, hot=False, primary=False):
    rect(sh, r, COLORS['button_primary'] if primary else (COLORS['button_hot'] if hot else COLORS['button']))
    outline(sh, r, COLORS['border'])
    w = text_width(label)
    text(r[0] + (r[2] - w) / 2.0, hb_gpu_draw.vcenter_baseline(r, FONT, FONT_SIZE), label)


def length_label(meters):
    return units.format_value(meters)


# Mundo 2D (por View2D) --------------------------------------------------------------------------------------------

def box(sh, view, lo, hi, color, fill=None):
    """Retângulo do mundo 2D (lo = (x, y) mínimo, hi = máximo) com contorno e preenchimento opcional."""
    a = view.to_screen(lo)
    b = view.to_screen(hi)
    r = (min(a[0], b[0]), min(a[1], b[1]), abs(b[0] - a[0]), abs(b[1] - a[1]))
    if fill:
        rect(sh, r, fill)
    outline(sh, r, color)
    return r


def segment(sh, view, p0, p1, color, dashed_line=False):
    a, b = view.to_screen(p0), view.to_screen(p1)
    lines(sh, dashed(a, b) if dashed_line else [a, b], color)


# Aparência clara do artefato (janela Encostar, BUG-20261022-RQR5) ------------------------------------------------

def _rgb(hex_value, alpha=1.0):
    v = int(hex_value.lstrip('#'), 16)
    return ((v >> 16 & 255) / 255.0, (v >> 8 & 255) / 255.0, (v & 255) / 255.0, alpha)


LIGHT = {
    'cream': _rgb('#F7F3EE'), 'paper': _rgb('#FFFFFF'), 'ink': _rgb('#1F2A2A'), 'muted': _rgb('#55605F'),
    'line': _rgb('#E6E1DA'), 'line_strong': _rgb('#CFC6BA'), 'orange': _rgb('#D35400'),
    'orange_ink': _rgb('#B04600'), 'orange_tint': _rgb('#FBE9DC'), 'teal': _rgb('#0B8582'),
    'teal_ink': _rgb('#075E5C'), 'teal_tint': _rgb('#E0F1EF'), 'blue': _rgb('#3AB0FF'), 'danger': _rgb('#B3261E'),
    'shadow': (0.04, 0.12, 0.12, 0.28),
}


def _arc(cx, cy, radius, start, segments=8):
    return [(cx + radius * math.cos(start + i * (math.pi / 2) / segments),
             cy + radius * math.sin(start + i * (math.pi / 2) / segments)) for i in range(segments + 1)]


def _rounded_outline_points(r, radius):
    x, y, w, h = r
    radius = max(0.0, min(radius, w / 2.0, h / 2.0))
    return (_arc(x + w - radius, y + radius, radius, -math.pi / 2) + _arc(x + w - radius, y + h - radius, radius, 0.0)
            + _arc(x + radius, y + h - radius, radius, math.pi / 2) + _arc(x + radius, y + radius, radius, math.pi))


def rounded_rect(sh, r, radius, color):
    """Retângulo preenchido com cantos arredondados (leque de triângulos a partir do centro)."""
    pts = _rounded_outline_points(r, radius)
    c = (r[0] + r[2] / 2.0, r[1] + r[3] / 2.0)
    tris = []
    for i, p in enumerate(pts):
        tris += [c, p, pts[(i + 1) % len(pts)]]
    sh.uniform_float("color", color)
    batch_for_shader(sh, 'TRIS', {"pos": tris}).draw(sh)


def rounded_outline(sh, r, radius, color, dashed_line=False):
    pts = _rounded_outline_points(r, radius)
    segs = []
    for i, p in enumerate(pts):
        q = pts[(i + 1) % len(pts)]
        segs += dashed(p, q, 4.0, 3.0) if dashed_line else [p, q]
    lines(sh, segs, color)


def circle(sh, center, radius, color, outline_color=None, segments=24):
    pts = [(center[0] + radius * math.cos(2 * math.pi * i / segments),
            center[1] + radius * math.sin(2 * math.pi * i / segments)) for i in range(segments)]
    tris = []
    for i, p in enumerate(pts):
        tris += [center, p, pts[(i + 1) % segments]]
    sh.uniform_float("color", color)
    batch_for_shader(sh, 'TRIS', {"pos": tris}).draw(sh)
    if outline_color:
        lines(sh, [v for i, p in enumerate(pts) for v in (p, pts[(i + 1) % segments])], outline_color)


def pill(sh, cx, cy, label, background, foreground, size=11):
    """Etiqueta em pílula centrada em (cx, cy), como as cotas do artefato. Devolve o retângulo."""
    w = text_width(label, size) + 2 * size
    h = size * 1.9
    r = (cx - w / 2.0, cy - h / 2.0, w, h)
    rounded_rect(sh, r, h / 2.0, background)
    text(r[0] + size, hb_gpu_draw.vcenter_baseline(r, FONT, size), label, foreground, size=size)
    return r
