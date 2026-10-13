"""Primitivas de desenho da BIBLIOTECA CAFFMOB na viewport (feature 014, T028; design-direction.md).

Retângulos (com canto arredondado), contornos, linhas, círculos, imagens recortadas em quadrado, texto com corte e
quebra em duas linhas, sombra suave e os ícones de traço da direção visual.

Toda primitiva translúcida religa `gpu.state.blend_set('ALPHA')` antes de desenhar: o `blf` desliga o blend ao
desenhar texto, e o que vem depois sairia opaco (achado da T006). Coordenadas em pixels da região, y para cima.
"""

import math

import blf  # type: ignore
import gpu  # type: ignore
from gpu_extras.batch import batch_for_shader  # type: ignore

from . import style

_shaders = {}


def _shader(name):
    if name not in _shaders:
        _shaders[name] = gpu.shader.from_builtin(name)
    return _shaders[name]


def _round_rect(x, y, w, h, r, seg=5):
    r = max(0.0, min(r, w / 2.0, h / 2.0))
    if r <= 0.5:
        return [(x, y), (x + w, y), (x + w, y + h), (x, y + h)], [(0, 1, 2), (0, 2, 3)]
    pts = []
    for cx, cy, a0 in ((x + w - r, y + h - r, 0), (x + r, y + h - r, 90), (x + r, y + r, 180), (x + w - r, y + r, 270)):
        for i in range(seg + 1):
            a = math.radians(a0 + 90.0 * i / seg)
            pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    verts = [(x + w / 2.0, y + h / 2.0)] + pts
    idx = [(0, i, i + 1) for i in range(1, len(pts))] + [(0, len(pts), 1)]
    return verts, idx


def rect(x, y, w, h, color, r=0.0):
    if w <= 0 or h <= 0:
        return
    verts, idx = _round_rect(x, y, w, h, r)
    shader = _shader('UNIFORM_COLOR')
    batch = batch_for_shader(shader, 'TRIS', {"pos": verts}, indices=idx)
    gpu.state.blend_set('ALPHA')
    shader.bind()
    shader.uniform_float("color", color)
    batch.draw(shader)


def polyline(points, color, width, viewport):
    if len(points) < 2:
        return
    coords = []
    for a, b in zip(points, points[1:]):
        coords += [a, b]
    shader = _shader('POLYLINE_UNIFORM_COLOR')
    batch = batch_for_shader(shader, 'LINES', {"pos": coords})
    gpu.state.blend_set('ALPHA')
    shader.bind()
    shader.uniform_float("color", color)
    shader.uniform_float("lineWidth", width)
    shader.uniform_float("viewportSize", viewport)
    batch.draw(shader)


def outline(x, y, w, h, color, viewport, r=0.0, width=1.0):
    verts, _idx = _round_rect(x, y, w, h, r)
    pts = verts[1:] + [verts[1]] if len(verts) > 4 else verts + [verts[0]]
    polyline(pts, color, width, viewport)


def circle(cx, cy, radius, color, seg=16):
    verts = [(cx, cy)] + [(cx + radius * math.cos(2 * math.pi * i / seg), cy + radius * math.sin(2 * math.pi * i / seg))
                          for i in range(seg + 1)]
    idx = [(0, i, i + 1) for i in range(1, seg + 1)]
    shader = _shader('UNIFORM_COLOR')
    batch = batch_for_shader(shader, 'TRIS', {"pos": verts}, indices=idx)
    gpu.state.blend_set('ALPHA')
    shader.bind()
    shader.uniform_float("color", color)
    batch.draw(shader)


def shadow(x, y, w, h, r, scale):
    """Sombra quase imperceptível: 5 camadas de 3 px, deslocadas para baixo (design-direction.md)."""
    for i in (15, 12, 9, 6, 3):
        d = i * scale
        rect(x - d, y - d - 3 * scale, w + 2 * d, h + 2 * d, (0.0, 0.0, 0.0, 0.045 * (1.0 - i / 17.0)), r + d)


def image(tex, x, y, w, h, src_size=None, dim=0.0):
    """Imagem recortada em quadrado (cover); `dim` escurece com a cor do painel (célula sendo arrastada)."""
    u0, v0, u1, v1 = 0.0, 0.0, 1.0, 1.0
    if src_size:
        sw, sh = float(src_size[0]), float(src_size[1])
        if sw > sh > 0:
            d = (1.0 - sh / sw) / 2.0
            u0, u1 = d, 1.0 - d
        elif sh > sw > 0:
            d = (1.0 - sw / sh) / 2.0
            v0, v1 = d, 1.0 - d
    shader = _shader('IMAGE')
    batch = batch_for_shader(shader, 'TRI_FAN', {"pos": ((x, y), (x + w, y), (x + w, y + h), (x, y + h)),
                                                 "texCoord": ((u0, v0), (u1, v0), (u1, v1), (u0, v1))})
    gpu.state.blend_set('ALPHA')
    shader.bind()
    shader.uniform_sampler("image", tex)
    batch.draw(shader)
    if dim > 0.0:
        rect(x, y, w, h, (style.SURFACE[0], style.SURFACE[1], style.SURFACE[2], dim))


# Texto ----------------------------------------------------------------------------------------------------------------
def width_of(text, size, font=0):
    blf.size(font, size)
    return blf.dimensions(font, text)[0]


def clip(text, size, max_w, font=0):
    if width_of(text, size, font) <= max_w:
        return text
    while text and width_of(text + "…", size, font) > max_w:
        text = text[:-1]
    return text.rstrip() + "…"


def wrap2(text, size, max_w, font=0):
    """Até duas linhas; a segunda corta com reticências."""
    lines, current = [], ""
    for word in text.split():
        trial = (current + " " + word).strip()
        if not current or width_of(trial, size, font) <= max_w:
            current = trial
        else:
            lines.append(current)
            current = word
    lines.append(current)
    if len(lines) > 2:
        lines = [lines[0], " ".join(lines[1:])]
    return [clip(lines[0], size, max_w, font)] + ([clip(lines[1], size, max_w, font)] if len(lines) > 1 else [])


def text(value, x, y, size, color, font=0, max_w=None):
    if max_w is not None:
        value = clip(value, size, max_w, font)
    blf.size(font, size)
    blf.color(font, *color)
    blf.position(font, x, y, 0)
    blf.draw(font, value)
    return blf.dimensions(font, value)[0]


def text_centered_y(value, rect_, x, size, color, font=0, max_w=None):
    """Texto com a altura centrada no retângulo (linha base pela altura de 'Aj')."""
    blf.size(font, size)
    height = blf.dimensions(font, "Aj")[1]
    return text(value, x, rect_[1] + (rect_[3] - height) / 2.0 + height * 0.15, size, color, font, max_w)


# Ícones de traço (design-direction.md, regra 7) ----------------------------------------------------------------------
def icon(name, x, y, size, color, viewport):
    m = size / 14.0

    def p(px, py):
        return (x + px * m, y + py * m)

    def line(points, w=1.5):
        polyline([p(*pt) for pt in points], color, max(1.0, w * m), viewport)

    if name == 'PIN':
        line([(4.5, 12.5), (9.5, 12.5)], 1.6)
        line([(5.5, 12.5), (5.5, 8), (3.5, 6), (10.5, 6), (8.5, 8), (8.5, 12.5)])
        line([(7, 6), (7, 1.5)], 1.6)
    elif name == 'MINIMIZE':
        line([(3, 7), (11, 7)], 1.6)
    elif name == 'CLOSE':
        line([(3, 3), (11, 11)], 1.6)
        line([(11, 3), (3, 11)], 1.6)
    elif name == 'MAXIMIZE':
        line([(3, 3), (11, 3), (11, 11), (3, 11), (3, 3)])
    elif name == 'SEARCH':
        line([(6 + 4 * math.cos(a * math.pi / 8), 8 + 4 * math.sin(a * math.pi / 8)) for a in range(17)])
        line([(9, 5), (12, 2)], 1.6)
    elif name == 'CLOUD':
        pts = [(4, 4), (11, 4)]
        pts += [(11 + 2.2 * math.cos(-math.pi / 2 + i * math.pi / 6), 6.2 + 2.2 * math.sin(-math.pi / 2 + i * math.pi / 6))
                for i in range(7)]
        pts += [(7.5 + 3 * math.cos(i * math.pi / 8), 8.5 + 3 * math.sin(i * math.pi / 8)) for i in range(1, 9)]
        pts += [(4 + 2 * math.cos(math.pi / 2 + i * math.pi / 6), 6 + 2 * math.sin(math.pi / 2 + i * math.pi / 6))
                for i in range(7)]
        line(pts, 1.3)
    elif name == 'CHECK':
        line([(3, 7), (6, 4), (11, 10)], 1.8)
    elif name == 'ALERT':
        line([(7, 12), (1.5, 2.5), (12.5, 2.5), (7, 12)], 1.4)
        line([(7, 9.5), (7, 6)], 1.6)
        circle(x + 7 * m, y + 4.4 * m, 0.9 * m, color)
    elif name == 'CHEVRON_DOWN':
        line([(3, 9), (7, 5), (11, 9)])
    elif name == 'CHEVRON_RIGHT':
        line([(5, 3), (9, 7), (5, 11)])
    elif name == 'OFFLINE':
        icon('CLOUD', x, y, size, color, viewport)
        line([(2, 12), (12, 1)], 1.4)
