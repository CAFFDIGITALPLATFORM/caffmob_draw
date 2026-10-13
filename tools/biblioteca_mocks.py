"""Mocks renderizados da BIBLIOTECA CAFFMOB (feature 014, T006; D-18).

Desenha cada estado do painel com os tokens da direção visual (`design-direction.md`) num `GPUOffScreen` e salva PNG.
Usa o mesmo tipo de desenho do plugin (POST_PIXEL: retângulos, linhas, `blf`, miniaturas como `GPUTexture`), para o
mock já mostrar o que a GPU do Blender entrega. Precisa de janela (contexto de GPU):

    xvfb-run -a blender --factory-startup --python tools/biblioteca_mocks.py -- <saída> [<Sora-SemiBold.ttf>]
"""

import math
import os
import sys
import traceback

import blf
import bpy
import gpu
import numpy as np
from gpu_extras.batch import batch_for_shader
from mathutils import Matrix

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ARGS = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
OUT = ARGS[0] if ARGS else os.path.join(REPO, "_reversa_forward", "014-texturas-fabricantes-grade", "mocks")
SORA = ARGS[1] if len(ARGS) > 1 else ""
THUMBS = os.path.join(REPO, "caffmob_draw", "textures")


def rgb(hexstr, a=1.0):
    h = hexstr.lstrip("#")
    return (int(h[0:2], 16) / 255.0, int(h[2:4], 16) / 255.0, int(h[4:6], 16) / 255.0, a)


# ---------------------------------------------------------------------------------------------------- tokens (D-18)
T = {
    "surface": rgb("#10302F", 0.96),        # Noite CAFF MOBI DRAW
    "surface_raised": rgb("#16403E", 0.98),  # cabeçalho, coluna de filtros
    "surface_hover": rgb("#1F5250", 1.0),
    "surface_sunken": rgb("#0B2322", 1.0),   # fundo da miniatura, campo de busca
    "border": (1.0, 1.0, 1.0, 0.10),
    "border_strong": (1.0, 1.0, 1.0, 0.22),
    "text": rgb("#EEF4F2"),
    "text_muted": rgb("#C9D6D2"),
    "text_subtle": rgb("#93ADA8"),
    "accent": rgb("#F07A2A"),               # laranja CAFF (escuro): seleção, ação principal
    "accent_ink": rgb("#10302F"),           # texto sobre o laranja
    "success": rgb("#1BB3AD"),              # teal: baixada
    "info": rgb("#5BC0FF"),                 # azul digital: progresso, informação
    "error": rgb("#FF6B5E"),                # erro (fora da paleta, quente e legível no Noite)
    "shadow": (0.0, 0.0, 0.0, 0.32),
    "cream": rgb("#FFF4EA"),
    "orange": rgb("#D35400"),
    "blue_spark": rgb("#2EA8F5"),
    "white": (1, 1, 1, 1),
}
S = {"xs": 4, "sm": 8, "md": 12, "lg": 16, "xl": 24}
R = {"panel": 8, "cell": 6, "control": 5, "chip": 10}
F = {"label": 11, "body": 12, "title": 14, "code": 22, "small": 10}
HEADER_H, SIDEBAR_W, CELL_W, CELL_H, GAP, FOOTER_H = 36, 180, 140, 188, 8, 28   # célula: 140 + 2 linhas + estado

SHADER = None
IMG = None
LINE = None
FONT_UI, FONT_TITLE, FONT_MONO = 0, 0, 1
VIEW = (1440, 900)


# ---------------------------------------------------------------------------------------------------- primitivas
def _round_rect_tris(x, y, w, h, r, seg=6):
    r = max(0.0, min(r, w / 2.0, h / 2.0))
    pts = []
    for cx, cy, a0 in ((x + w - r, y + h - r, 0), (x + r, y + h - r, 90), (x + r, y + r, 180), (x + w - r, y + r, 270)):
        for i in range(seg + 1):
            a = math.radians(a0 + 90.0 * i / seg)
            pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    center = (x + w / 2.0, y + h / 2.0)
    verts = [center] + pts
    idx = [(0, i, i + 1) for i in range(1, len(pts))] + [(0, len(pts), 1)]
    return verts, idx


def rect(x, y, w, h, color, r=0):
    verts, idx = _round_rect_tris(x, y, w, h, r) if r else ([(x, y), (x + w, y), (x + w, y + h), (x, y + h)],
                                                            [(0, 1, 2), (0, 2, 3)])
    batch = batch_for_shader(SHADER, 'TRIS', {"pos": verts}, indices=idx)
    gpu.state.blend_set('ALPHA')            # o blf desliga o blend ao desenhar texto
    SHADER.bind()
    SHADER.uniform_float("color", color)
    batch.draw(SHADER)


def outline(x, y, w, h, color, r=0, width=1.0):
    if r:
        verts, _idx = _round_rect_tris(x, y, w, h, r)
        pts = verts[1:] + [verts[1]]
    else:
        pts = [(x, y), (x + w, y), (x + w, y + h), (x, y + h), (x, y)]
    polyline(pts, color, width)


def polyline(pts, color, width=1.0):
    coords = []
    for a, b in zip(pts, pts[1:]):
        coords += [a, b]
    batch = batch_for_shader(LINE, 'LINES', {"pos": coords})
    gpu.state.blend_set('ALPHA')
    LINE.bind()
    LINE.uniform_float("color", color)
    LINE.uniform_float("lineWidth", width)
    LINE.uniform_float("viewportSize", VIEW)
    batch.draw(LINE)


def circle(cx, cy, r, color, seg=20):
    verts = [(cx, cy)] + [(cx + r * math.cos(2 * math.pi * i / seg), cy + r * math.sin(2 * math.pi * i / seg))
                          for i in range(seg + 1)]
    idx = [(0, i, i + 1) for i in range(1, seg + 1)]
    batch = batch_for_shader(SHADER, 'TRIS', {"pos": verts}, indices=idx)
    gpu.state.blend_set('ALPHA')
    SHADER.bind()
    SHADER.uniform_float("color", color)
    batch.draw(SHADER)


def shadow(x, y, w, h, r, spread=14):
    """Sombra suave: poucas camadas largas e quase transparentes, deslocadas para baixo."""
    for i in range(spread, 0, -3):
        a = 0.045 * (1.0 - i / (spread + 2))
        rect(x - i, y - i - 3, w + 2 * i, h + 2 * i, (0, 0, 0, a), r + i)


def text(s, x, y, size, color, font=None, max_w=None):
    font = FONT_UI if font is None else font
    blf.size(font, size)
    if max_w is not None:
        s = clip(s, size, max_w, font)
    blf.color(font, *color)
    blf.position(font, x, y, 0)
    blf.draw(font, s)
    return blf.dimensions(font, s)[0]


def width_of(s, size, font=None):
    font = FONT_UI if font is None else font
    blf.size(font, size)
    return blf.dimensions(font, s)[0]


def clip(s, size, max_w, font=None):
    if width_of(s, size, font) <= max_w:
        return s
    while s and width_of(s + "…", size, font) > max_w:
        s = s[:-1]
    return s.rstrip() + "…"


def wrap2(s, size, max_w):
    """Até duas linhas; a segunda corta com reticências."""
    words, lines, cur = s.split(), [], ""
    for word in words:
        trial = (cur + " " + word).strip()
        if width_of(trial, size) <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    lines.append(cur)
    if len(lines) > 2:
        lines = [lines[0], " ".join(lines[1:])]
    return [lines[0]] + ([clip(lines[1], size, max_w)] if len(lines) > 1 else [])


def image(tex, x, y, w, h, alpha=1.0, src=None):
    """Miniatura recortada em quadrado (cover)."""
    u0, v0, u1, v1 = 0, 0, 1, 1
    if src:
        sw, sh = src
        if sw > sh:
            d = (1 - sh / sw) / 2
            u0, u1 = d, 1 - d
        elif sh > sw:
            d = (1 - sw / sh) / 2
            v0, v1 = d, 1 - d
    batch = batch_for_shader(IMG, 'TRI_FAN', {"pos": ((x, y), (x + w, y), (x + w, y + h), (x, y + h)),
                                              "texCoord": ((u0, v0), (u1, v0), (u1, v1), (u0, v1))})
    gpu.state.blend_set('ALPHA')
    IMG.bind()
    IMG.uniform_sampler("image", tex)
    batch.draw(IMG)
    if alpha < 1.0:
        rect(x, y, w, h, (T["surface"][0], T["surface"][1], T["surface"][2], 1.0 - alpha))


# ---------------------------------------------------------------------------------------------------- ícones (traço)
def icon(name, x, y, s=14, color=None):
    c = color or T["text_muted"]
    m = s / 14.0
    P = lambda px, py: (x + px * m, y + py * m)  # noqa: E731
    if name == "pin":                      # alfinete: cabeça, corpo e ponta
        polyline([P(4.5, 12.5), P(9.5, 12.5)], c, 1.6)
        polyline([P(5.5, 12.5), P(5.5, 8), P(3.5, 6), P(10.5, 6), P(8.5, 8), P(8.5, 12.5)], c, 1.5)
        polyline([P(7, 6), P(7, 1.5)], c, 1.6)
    elif name == "minimize":
        polyline([P(3, 7), P(11, 7)], c, 1.6)
    elif name == "close":
        polyline([P(3, 3), P(11, 11)], c, 1.6)
        polyline([P(11, 3), P(3, 11)], c, 1.6)
    elif name == "maximize":
        outline(x + 3 * m, y + 3 * m, 8 * m, 8 * m, c, 1, 1.5)
    elif name == "search":
        pts = [P(6 + 4 * math.cos(a), 8 + 4 * math.sin(a)) for a in [i * math.pi / 8 for i in range(17)]]
        polyline(pts, c, 1.5)
        polyline([P(9, 5), P(12, 2)], c, 1.6)
    elif name == "cloud":
        pts = [P(4, 4), P(11, 4)] + [P(11 + 2.2 * math.cos(a), 6.2 + 2.2 * math.sin(a))
                                     for a in [-math.pi / 2 + i * math.pi / 6 for i in range(7)]]
        pts += [P(7.5 + 3 * math.cos(a), 8.5 + 3 * math.sin(a)) for a in [i * math.pi / 8 for i in range(1, 9)]]
        pts += [P(4 + 2 * math.cos(a), 6 + 2 * math.sin(a)) for a in [math.pi / 2 + i * math.pi / 6 for i in range(7)]]
        polyline(pts, c, 1.3)
    elif name == "check":
        polyline([P(3, 7), P(6, 4), P(11, 10)], c, 1.8)
    elif name == "alert":
        polyline([P(7, 12), P(1.5, 2.5), P(12.5, 2.5), P(7, 12)], c, 1.4)
        polyline([P(7, 9.5), P(7, 6)], c, 1.6)
        circle(x + 7 * m, y + 4.4 * m, 0.9 * m, c)
    elif name == "chevron_down":
        polyline([P(3, 9), P(7, 5), P(11, 9)], c, 1.5)
    elif name == "chevron_right":
        polyline([P(5, 3), P(9, 7), P(5, 11)], c, 1.5)
    elif name == "offline":
        icon("cloud", x, y, s, c)
        polyline([P(2, 12), P(12, 1)], c, 1.4)


def logo(x, y, size=20):
    """Ícone CAFF MOBI DRAW (canvas da família CAFF): quadrado creme, caneca laranja com planta de paredes, faíscas."""
    k = size / 64.0
    rect(x, y, size, size, T["cream"], 14 * k)
    def tf(px, py):  # coordenadas SVG (y para baixo) → tela, com a rotação de −6° em torno de (29, 54)
        a = math.radians(-6)
        dx, dy = px - 29, py - 54
        rx, ry = 29 + dx * math.cos(a) - dy * math.sin(a), 54 + dx * math.sin(a) + dy * math.cos(a)
        return (x + rx * k, y + (64 - ry) * k)
    body = [tf(12, 18), tf(46, 18), tf(44, 50), tf(40, 54), tf(18, 54), tf(14, 50)]
    batch = batch_for_shader(SHADER, 'TRI_FAN', {"pos": body})
    gpu.state.blend_set('ALPHA')
    SHADER.bind()
    SHADER.uniform_float("color", T["orange"])
    batch.draw(SHADER)
    polyline([tf(45.6, 25), tf(50, 25), tf(54, 28), tf(55, 33), tf(54, 39), tf(50, 42), tf(44.6, 42)], T["orange"],
             max(1.0, 4.5 * k))
    w = max(1.0, 3 * k)
    polyline([tf(18, 26), tf(40, 26), tf(40, 46), tf(26, 46)], T["white"], w)
    polyline([tf(18, 26), tf(18, 38)], T["white"], w)
    polyline([tf(30, 26), tf(30, 34)], T["white"], w)
    for px, py in ((18, 38), (40, 46), (26, 46)):
        cx, cy = tf(px, py)
        circle(cx, cy, 2.3 * k, T["white"], 10)
    for a, b in (((7, 13), (3.5, 9.5)), ((13.5, 11), (13.5, 5.5)), ((5.5, 18), (2, 17))):
        polyline([(x + a[0] * k, y + (64 - a[1]) * k), (x + b[0] * k, y + (64 - b[1]) * k)], T["blue_spark"],
                 max(1.0, 2.8 * k))


# ---------------------------------------------------------------------------------------------------- cena e HUD
def scene(w, h, cabinet=True, highlight=False):
    for i in range(h):
        if i % 6 == 0:
            t = i / h
            g = 0.20 + 0.05 * t
            rect(0, i, w, 6, (g, g, g + 0.005, 1))
    for gx in range(0, w, 60):
        polyline([(gx, 0), (gx, h)], (1, 1, 1, 0.035), 1)
    for gy in range(0, h, 60):
        polyline([(0, gy), (w, gy)], (1, 1, 1, 0.035), 1)
    if cabinet:
        cx, cy = w * 0.62, h * 0.18
        rect(cx, cy, 360, 300, (0.62, 0.62, 0.60, 1))
        rect(cx + 6, cy + 6, 171, 288, (0.70, 0.69, 0.67, 1))
        rect(cx + 183, cy + 6, 171, 288, (0.70, 0.69, 0.67, 1))
        rect(cx, cy + 300, 360, 18, (0.55, 0.55, 0.53, 1))
        for px in (cx + 160, cx + 200):
            rect(px, cy + 140, 4, 40, (0.35, 0.35, 0.35, 1))
        if highlight:
            outline(cx + 183, cy + 6, 171, 288, T["accent"], 0, 3)


def hud(h):
    """HUD do plugin no topo esquerdo (o painel não pode cobri-lo, RN-09)."""
    y = h - 12 - 28
    rect(12, y, 128, 28, (0.13, 0.13, 0.14, 0.95), 4)
    outline(12, y, 128, 28, (1, 1, 1, 0.14), 4)
    text("Navegar", 24, y + 9, 11, (0.9, 0.9, 0.9, 1))
    icon("chevron_down", 116, y + 7, 12, (0.9, 0.9, 0.9, 1))
    return 140  # borda direita do botão de navegação


# ---------------------------------------------------------------------------------------------------- painel
def label_minimized(x, top, hover=False, with_maximize=False):
    w = width_of("BIBLIOTECA CAFFMOB", F["label"]) + 2 * S["md"] + 22 + (26 if with_maximize else 0)
    y = top - 28
    shadow(x, y, w, 28, R["control"], 8)
    rect(x, y, w, 28, T["surface_hover"] if hover else T["surface"], R["control"])
    outline(x, y, w, 28, T["border"], R["control"])
    logo(x + 8, y + 6, 16)
    text("BIBLIOTECA CAFFMOB", x + 30, y + 10, F["label"], T["text"])
    return (x, y, w, 28)


def column_open(x, top, items, hover_key):
    lx, ly, lw, lh = label_minimized(x, top, with_maximize=True)
    col_w = max(lw, max(width_of(t, F["body"]) for _k, t in items) + 2 * S["md"] + 24)
    y = ly
    rows = []
    for key, label in items:
        y -= 26
        rows.append((key, label, y))
    body_y = y - 4
    shadow(x, body_y, col_w, ly - body_y - 2, R["panel"], 10)
    rect(x, body_y, col_w, ly - body_y - 2, T["surface"], R["panel"])
    outline(x, body_y, col_w, ly - body_y - 2, T["border"], R["panel"])
    for key, label, ry in rows:
        if key == hover_key:
            rect(x + 4, ry + 1, col_w - 8, 24, T["surface_hover"], R["control"])
        muted = key.startswith("ACTION:")
        text(label, x + S["md"], ry + 8, F["body"], T["text_subtle"] if muted else T["text"])
    # botão de maximizar no rótulo
    icon("maximize", lx + lw - 20, ly + 7, 14, T["text_muted"])
    return col_w


def header(x, y, w, tab, search, account, pinned):
    top = y
    rect(x + 1, top - HEADER_H, w - 2, HEADER_H - 1, T["surface_raised"], R["panel"] - 2)
    polyline([(x, top - HEADER_H), (x + w, top - HEADER_H)], T["border"], 1)
    logo(x + S["md"], top - HEADER_H + 8, 20)
    text("Biblioteca", x + S["md"] + 28, top - HEADER_H + 12, F["title"], T["text"], FONT_TITLE)
    tx = x + 150
    for name in ("Blocos", "Texturas"):
        active = name == tab
        tw = text(name, tx, top - HEADER_H + 12, F["body"], T["text"] if active else T["text_subtle"])
        if active:
            rect(tx, top - HEADER_H + 2, tw, 2, T["accent"])
        tx += tw + S["xl"]
    # botões à direita
    bx = x + w - S["md"] - 22
    for ic, on in (("close", False), ("minimize", False), ("pin", pinned)):
        if on:
            rect(bx - 4, top - HEADER_H + 7, 22, 22, (T["accent"][0], T["accent"][1], T["accent"][2], 0.18),
                 R["control"])
        icon(ic, bx, top - HEADER_H + 11, 14, T["accent"] if on else T["text_muted"])
        bx -= 30
    # conta
    acc_w = width_of(account[0], F["label"]) + 30
    ax = bx - acc_w + 6
    rect(ax, top - HEADER_H + 7, acc_w, 22, T["surface_sunken"], R["chip"])
    circle(ax + 11, top - HEADER_H + 18, 3.5, account[1])
    text(account[0], ax + 20, top - HEADER_H + 14, F["label"], T["text_muted"])
    # busca
    sw = 230
    sx = ax - sw - S["md"]
    rect(sx, top - HEADER_H + 7, sw, 22, T["surface_sunken"], R["control"])
    outline(sx, top - HEADER_H + 7, sw, 22, T["border_strong"] if search else T["border"], R["control"])
    icon("search", sx + 7, top - HEADER_H + 11, 13, T["text_subtle"])
    if search:
        text(search, sx + 26, top - HEADER_H + 14, F["label"], T["text"])
    else:
        text("Buscar acabamento…", sx + 26, top - HEADER_H + 14, F["label"], T["text_subtle"])


def sidebar(x, y_top, h, tree, open_man, sel_col):
    rect(x + 1, y_top - h, SIDEBAR_W - 1, h, T["surface_raised"])
    polyline([(x + SIDEBAR_W, y_top - h), (x + SIDEBAR_W, y_top)], T["border"], 1)
    y = y_top - S["lg"] - 4
    text("Fabricantes", x + S["md"], y, F["small"], T["text_subtle"])
    y -= 22
    for man, count, cols in tree:
        is_open = man == open_man
        icon("chevron_down" if is_open else "chevron_right", x + 8, y - 3, 12, T["text_subtle"])
        text(man, x + 26, y, F["body"], T["text"] if is_open else T["text_muted"])
        cw = width_of(str(count), F["small"])
        text(str(count), x + SIDEBAR_W - S["md"] - cw, y + 1, F["small"], T["text_subtle"])
        y -= 22
        if is_open:
            for col, n in cols:
                sel = col == sel_col
                if sel:
                    rect(x + 6, y - 6, SIDEBAR_W - 12, 22, (T["accent"][0], T["accent"][1], T["accent"][2], 0.18),
                         R["control"])
                text(col, x + 34, y, F["label"], T["text"] if sel else T["text_muted"], max_w=SIDEBAR_W - 80)
                nw = width_of(str(n), F["small"])
                text(str(n), x + SIDEBAR_W - S["md"] - nw, y + 1, F["small"], T["text_subtle"])
                y -= 22
        if y < y_top - h + 20:
            break


def cell(x, y, item, tex, state, progress=0.0):
    """Célula da grade: miniatura 140 × 140, nome em até 2 linhas e a linha de estado (texto, além da cor)."""
    hover = state == "hover"
    selected = state == "selected"
    if hover or selected:
        rect(x - 4, y - 4, CELL_W + 8, CELL_H + 8, T["surface_hover"], R["cell"] + 2)
    th_y = y + CELL_H - CELL_W
    rect(x, th_y, CELL_W, CELL_W, T["surface_sunken"], R["cell"])
    if tex is not None:
        image(tex, x, th_y, CELL_W, CELL_W, alpha=0.45 if state == "dragging" else 1.0, src=item.get("px"))
    if selected:
        outline(x - 1, th_y - 1, CELL_W + 2, CELL_W + 2, T["accent"], R["cell"], 2.0)
    # selo de estado sobre a miniatura (cantos), discreto
    if state in ("not_downloaded", "hover", "selected", "dragging"):
        rect(x + CELL_W - 24, th_y + CELL_W - 24, 20, 20, (0.04, 0.12, 0.12, 0.72), 10)
        icon("cloud", x + CELL_W - 21, th_y + CELL_W - 21, 14, T["text_muted"])
    elif state == "downloaded":
        rect(x + CELL_W - 24, th_y + CELL_W - 24, 20, 20, (0.04, 0.12, 0.12, 0.72), 10)
        icon("check", x + CELL_W - 21, th_y + CELL_W - 21, 14, T["success"])
    elif state == "error":
        rect(x + CELL_W - 24, th_y + CELL_W - 24, 20, 20, (0.04, 0.12, 0.12, 0.72), 10)
        icon("alert", x + CELL_W - 21, th_y + CELL_W - 21, 14, T["error"])
    if state == "downloading":
        rect(x, th_y, CELL_W, 4, (0, 0, 0, 0.5))
        rect(x, th_y, CELL_W * progress, 4, T["info"])
    lines = wrap2(item["name"], F["label"], CELL_W)
    ty = th_y - 14
    for line in lines:
        text(line, x, ty, F["label"], T["text"])
        ty -= 13
    status_y = ty - 1                        # a linha de estado vem logo abaixo do nome
    status = {"downloaded": ("Baixada", T["success"]), "not_downloaded": ("Não baixada", T["text_subtle"]),
              "hover": ("Arraste para aplicar", T["text_muted"]),
              "selected": ("Não baixada", T["text_muted"]),   # fundo de hover: text_subtle cai a 3,7:1
              "dragging": ("Arrastando…", T["text_subtle"]),
              "downloading": ("Baixando {}%".format(int(progress * 100)), T["info"]),
              "error": ("Falhou · tentar de novo", T["error"])}[state]
    text(status[0], x, status_y, F["small"], status[1], max_w=CELL_W)


def panel(x, y, w, h, *, tab="Texturas", search="", account=("Entrar com a conta CAFF Mob", None), pinned=False,
          tree=(), open_man="", sel_col="", body=None, footer=None):
    shadow(x, y, w, h, R["panel"], 16)
    rect(x, y, w, h, T["surface"], R["panel"])
    outline(x, y, w, h, T["border"], R["panel"])
    header(x, y + h, w, tab, search, (account[0], account[1] or T["text_subtle"]), pinned)
    footer_h = FOOTER_H if footer else 0
    sidebar(x, y + h - HEADER_H, h - HEADER_H - footer_h, tree, open_man, sel_col)
    area = (x + SIDEBAR_W + S["md"], y + footer_h + S["md"], w - SIDEBAR_W - 2 * S["md"],
            h - HEADER_H - footer_h - 2 * S["md"])
    if body:
        body(area)
    if footer:
        polyline([(x, y + FOOTER_H), (x + w, y + FOOTER_H)], T["border"], 1)
        footer(x, y, w)
    # alça de redimensionar (canto inferior direito)
    for i in range(3):
        polyline([(x + w - 4 - 4 * i, y + 3), (x + w - 3, y + 4 + 4 * i)], T["text_subtle"], 1)


def grid(area, cells):
    ax, ay, aw, ah = area
    cols = max(1, int((aw + GAP) // (CELL_W + GAP)))
    top = ay + ah
    gpu.state.scissor_test_set(True)        # recorte da rolagem (D-06)
    gpu.state.scissor_set(int(ax - 6), int(ay), int(aw + 12), int(ah + 6))
    for i, (item, tex, state, prog) in enumerate(cells):
        r, c = divmod(i, cols)
        cx = ax + c * (CELL_W + GAP)
        cy = top - (r + 1) * (CELL_H + GAP) + GAP
        if cy + CELL_H < ay:
            break
        cell(cx, cy, item, tex, state, prog)
    gpu.state.scissor_test_set(False)
    # barra de rolagem fina
    rect(ax + aw - 3, ay, 3, ah, (1, 1, 1, 0.05), 1.5)
    rect(ax + aw - 3, ay + ah * 0.55, 3, ah * 0.45, (1, 1, 1, 0.22), 1.5)


def download_footer(done, total, mb, mb_total):
    def draw(x, y, w):
        text("Baixando {} de {} · {} de {} MB".format(done, total, mb, mb_total), x + S["md"], y + 10, F["label"],
             T["text_muted"])
        bx = x + 300
        rect(bx, y + 12, 220, 4, (1, 1, 1, 0.10), 2)
        rect(bx, y + 12, 220 * (float(mb.replace(",", ".")) / float(mb_total.replace(",", "."))), 4, T["info"], 2)
        cw = width_of("Cancelar", F["label"])
        text("Cancelar", x + w - S["md"] - cw - 12, y + 10, F["label"], T["text_muted"])
    return draw


# ---------------------------------------------------------------------------------------------------- dados reais
def load_catalog():
    import json
    with open(os.path.join(THUMBS, "catalog.json"), encoding="utf-8") as handle:
        cat = json.load(handle)
    tree = []
    for m in cat["manufacturers"]:
        tree.append((m["name"], sum(len(c["items"]) for c in m["collections"]),
                     [(c["name"], len(c["items"])) for c in m["collections"]]))
    duratex = next(m for m in cat["manufacturers"] if m["id"] == "duratex")
    items = [i for c in duratex["collections"] for i in c["items"] if c["name"] in ("Design", "Essencial Wood")]
    return tree, items


_tex_cache = {}


def tex_of(item):
    path = os.path.join(THUMBS, item["thumb"])
    if path not in _tex_cache:
        img = bpy.data.images.load(path, check_existing=True)
        _tex_cache[path] = gpu.texture.from_image(img)
    return _tex_cache[path]


# ---------------------------------------------------------------------------------------------------- render
def render(name, w, h, draw):
    global VIEW
    VIEW = (w, h)
    off = gpu.types.GPUOffScreen(w, h)
    with off.bind():
        fb = gpu.state.active_framebuffer_get()
        fb.clear(color=(0.0, 0.0, 0.0, 1.0))
        with gpu.matrix.push_pop():
            gpu.matrix.load_matrix(Matrix.Identity(4))
            with gpu.matrix.push_pop_projection():
                proj = Matrix(((2.0 / w, 0, 0, -1), (0, 2.0 / h, 0, -1), (0, 0, 1, 0), (0, 0, 0, 1)))
                gpu.matrix.load_projection_matrix(proj)
                gpu.state.blend_set('ALPHA')
                draw(w, h)
                gpu.state.blend_set('NONE')
        buf = fb.read_color(0, 0, w, h, 4, 0, 'UBYTE')
    off.free()
    buf.dimensions = w * h * 4
    pixels = np.array(buf, dtype=np.float32) / 255.0
    img = bpy.data.images.new(name, w, h, alpha=False)
    img.pixels.foreach_set(pixels)
    os.makedirs(OUT, exist_ok=True)
    img.filepath_raw = os.path.join(OUT, name + ".png")
    img.file_format = 'PNG'
    img.save()
    path = img.filepath_raw
    bpy.data.images.remove(img)
    print("MOCK", path, flush=True)


def build():
    global SHADER, IMG, LINE, FONT_TITLE
    SHADER = gpu.shader.from_builtin('UNIFORM_COLOR')
    IMG = gpu.shader.from_builtin('IMAGE')
    LINE = gpu.shader.from_builtin('POLYLINE_UNIFORM_COLOR')
    if SORA and os.path.exists(SORA):
        FONT_TITLE = blf.load(SORA)
    tree, items = load_catalog()
    cats = [("CREATE_CABINET", "Criar armário"), ("CAT:Cozinha", "Cozinha"), ("CAT:Banheiro", "Banheiro"),
            ("CAT:Sala", "Sala"), ("CAT:Home office", "Home office"), ("CAT:TEXTURAS", "Texturas"),
            ("ACTION:CREATE_CATEGORY", "Criar categoria")]

    def minimized(w, h):
        scene(w, h)
        nav = hud(h)
        label_minimized(nav + 8, h - 12)
    render("01-minimizado", 900, 420, minimized)

    def opened(w, h):
        scene(w, h)
        nav = hud(h)
        column_open(nav + 8, h - 12, cats, "CAT:TEXTURAS")
    render("02-aberto", 900, 420, opened)

    states = (["downloaded", "hover", "selected", "not_downloaded", "downloading", "error"]
              + ["not_downloaded"] * 4 + ["downloaded"] * 2 + ["not_downloaded"] * 8)
    prog = {4: 0.62}
    cells = [(it, tex_of(it), states[i % len(states)], prog.get(i, 0.0)) for i, it in enumerate(items[:20])]
    acc_on = ("leo@caff.digital", T["success"])

    def maximized(w, h):
        scene(w, h)
        hud(h)
        panel(150, 70, 1040, 770, tab="Texturas", search="", account=acc_on, pinned=True, tree=tree,
              open_man="Duratex", sel_col="Design", body=lambda a: grid(a, cells),
              footer=download_footer(1, 3, "2,4", "4,0"))
    render("03-maximizado-texturas", 1440, 900, maximized)

    def login(w, h):
        scene(w, h)
        hud(h)

        def body(area):
            ax, ay, aw, ah = area
            cx, cy = ax + aw / 2, ay + ah / 2
            logo(cx - 24, cy + 110, 48)
            msg = "Entre com a conta CAFF Mob para baixar as texturas"
            text(msg, cx - width_of(msg, F["title"]) / 2, cy + 76, F["title"], T["text"])
            sub = "Abra a página abaixo no navegador e digite o código. A senha fica só no site da CAFF."
            text(sub, cx - width_of(sub, F["body"]) / 2, cy + 52, F["body"], T["text_muted"])
            code = "WDJB-MJHT"
            blf.size(FONT_MONO, F["code"])
            cw = blf.dimensions(FONT_MONO, code)[0]
            rect(cx - cw / 2 - 20, cy - 4, cw + 40, 44, T["surface_sunken"], R["control"] + 2)
            outline(cx - cw / 2 - 20, cy - 4, cw + 40, 44, T["border_strong"], R["control"] + 2)
            text(code, cx - cw / 2, cy + 10, F["code"], T["text"], FONT_MONO)
            bw = width_of("Abrir o navegador", F["body"]) + 32
            rect(cx - bw - 6, cy - 52, bw, 30, T["accent"], R["control"])
            text("Abrir o navegador", cx - bw - 6 + 16, cy - 42, F["body"], T["accent_ink"])
            cw2 = width_of("Cancelar", F["body"]) + 32
            outline(cx + 6, cy - 52, cw2, 30, T["border_strong"], R["control"])
            text("Cancelar", cx + 6 + 16, cy - 42, F["body"], T["text_muted"])
            wait = "Aguardando a confirmação no navegador…"
            text(wait, cx - width_of(wait, F["label"]) / 2, cy - 84, F["label"], T["info"])
        panel(150, 70, 1040, 770, tab="Texturas", account=("Entrar com a conta CAFF Mob", T["text_subtle"]),
              pinned=False, tree=tree, open_man="Duratex", sel_col="Design", body=body)
    render("04-login-conta", 1440, 900, login)

    def dragging(w, h):
        scene(w, h, highlight=True)
        hud(h)
        drag_cells = list(cells)
        drag_cells[2] = (cells[2][0], cells[2][1], "dragging", 0.0)
        panel(60, 70, 760, 770, tab="Texturas", account=acc_on, pinned=True, tree=tree, open_man="Duratex",
              sel_col="Design", body=lambda a: grid(a, drag_cells))
        gx, gy = 1010, 360
        shadow(gx, gy, 72, 72, R["cell"], 10)
        image(cells[2][1], gx, gy, 72, 72, src=cells[2][0].get("px"))
        outline(gx, gy, 72, 72, T["accent"], R["cell"], 2)
        pill = "Soltar na porta: Carvalho Avela Design"
        pw = width_of(pill, F["label"]) + 20
        rect(gx + 80, gy + 24, pw, 24, T["surface"], R["chip"])
        text(pill, gx + 90, gy + 32, F["label"], T["text"])
        polyline([(gx - 6, gy + 80), (gx + 2, gy + 70), (gx - 2, gy + 70), (gx - 6, gy + 80)], T["white"], 1.5)
    render("05-arrastando", 1440, 900, dragging)

    def empty_offline(w, h):
        scene(w, h)
        hud(h)

        def body(area):
            ax, ay, aw, ah = area
            bh = 34
            rect(ax, ay + ah - bh, aw - 8, bh, (T["info"][0], T["info"][1], T["info"][2], 0.14), R["control"])
            icon("offline", ax + 10, ay + ah - bh + 10, 14, T["info"])
            text("Sem acesso à internet: só as texturas já baixadas podem ser aplicadas.", ax + 32,
                 ay + ah - bh + 12, F["body"], T["text"])
            cx, cy = ax + aw / 2, ay + ah / 2
            icon("search", cx - 14, cy + 40, 28, T["text_subtle"])
            msg = "Nenhum resultado para “nogueira xyz”"
            text(msg, cx - width_of(msg, F["title"]) / 2, cy + 8, F["title"], T["text"])
            sub = "Confira a escrita ou busque em todos os fabricantes."
            text(sub, cx - width_of(sub, F["body"]) / 2, cy - 16, F["body"], T["text_muted"])
            bw = width_of("Limpar busca", F["body"]) + 32
            outline(cx - bw / 2, cy - 60, bw, 30, T["border_strong"], R["control"])
            text("Limpar busca", cx - bw / 2 + 16, cy - 50, F["body"], T["text"])
        panel(150, 70, 1040, 770, tab="Texturas", search="nogueira xyz", account=acc_on, pinned=False, tree=tree,
              open_man="", sel_col="", body=body)
    render("06-vazio-sem-internet", 1440, 900, empty_offline)

    def tokens_sheet(w, h):
        rect(0, 0, w, h, rgb("#0A1E1E"))
        text("Tokens · BIBLIOTECA CAFFMOB", 32, h - 48, 18, T["text"], FONT_TITLE)
        swatches = [("surface", "#10302F · 96%"), ("surface_raised", "#16403E"), ("surface_hover", "#1F5250"),
                    ("surface_sunken", "#0B2322"), ("text", "#EEF4F2"), ("text_muted", "#C9D6D2"),
                    ("text_subtle", "#93ADA8"), ("accent", "#F07A2A"), ("success", "#1BB3AD"),
                    ("info", "#5BC0FF"), ("error", "#FF6B5E"), ("cream", "#FFF4EA")]
        for i, (key, label) in enumerate(swatches):
            r_, c_ = divmod(i, 6)
            x, y = 32 + c_ * 150, h - 160 - r_ * 110
            rect(x, y, 130, 56, T[key], R["cell"])
            outline(x, y, 130, 56, (1, 1, 1, 0.12), R["cell"])
            text(key, x, y - 18, F["body"], T["text"])
            text(label, x, y - 34, F["small"], T["text_subtle"])
        y = h - 420
        for size, use in ((F["small"], "10 px · contagens, linha de estado"), (F["label"], "11 px · rótulos, nomes"),
                          (F["body"], "12 px · abas, coluna de filtros"),
                          (F["title"], "14 px Sora SemiBold · título")):
            font = FONT_TITLE if size == F["title"] else FONT_UI
            text("Carvalho Avela Design", 32, y, size, T["text"], font)
            text(use, 360, y, F["label"], T["text_subtle"])
            y -= 34
        logo(760, h - 520, 64)
        text("Ícone CAFF MOBI DRAW", 840, h - 490, F["body"], T["text"])
    render("00-tokens", 1100, 640, tokens_sheet)


def tick():
    try:
        build()
        code = 0
    except Exception:
        traceback.print_exc()
        code = 1
    os._exit(code)


bpy.app.timers.register(tick, first_interval=1.0)
