"""Layout do painel BIBLIOTECA CAFFMOB (feature 012, T015; D-14, D-30). Python puro.

Canto superior esquerdo da parte **visível** da viewport (`x_min`, `y_max` de `hb_gpu_draw.get_visible_window_bounds`:
o cabeçalho e a barra de ferramentas se sobrepõem à região e pegariam o clique); com o HUD ligado, à direita do botão
de navegação (`nav_right`).
Fechado: só o rótulo. Aberto: uma coluna de largura única abaixo dele, na ordem de `menu_items`. Retângulos como
(x, y, largura, altura) em pixels da região, com y de baixo para cima (como o desenho `POST_PIXEL`).
"""

from collections import namedtuple

from ..data.i18n import N_
from . import grid_core, style

Layout = namedtuple('Layout', 'label items')
TITLE = "BIBLIOTECA CAFFMOB"         # nome próprio, sem tradução (RNF de i18n)
MARGIN_X, MARGIN_Y, GAP = 8.0, 12.0, 8.0
ROW_HEIGHT, ROW_GAP, PAD_X = 24.0, 2.0, 12.0

CREATE_CABINET, CREATE_CATEGORY, CONVERT_GROUPS = 'CREATE_CABINET', 'CREATE_CATEGORY', 'CONVERT_GROUPS'
LABELS = {CREATE_CABINET: N_("Criar armário"), CREATE_CATEGORY: N_("Criar categoria"),
          CONVERT_GROUPS: N_("Converter grupos antigos")}


def menu_items(category_names, offer_groups=False):
    """[(chave, rótulo)]: (oferta dos grupos antigos), Criar armário, categorias, Criar categoria."""
    items = [(CONVERT_GROUPS, LABELS[CONVERT_GROUPS])] if offer_groups else []
    items.append((CREATE_CABINET, LABELS[CREATE_CABINET]))
    items += [("CAT:" + name, name) for name in category_names]
    items.append((CREATE_CATEGORY, LABELS[CREATE_CATEGORY]))
    return items


def category_of(key):
    return key[4:] if key and key.startswith("CAT:") else None


def panel_layout(x_min, y_max, scale, nav_right, is_open, items, text_width, with_maximize=False):
    """`x_min`, `y_max` = limites visíveis da região; `nav_right` = borda direita do botão de navegação do HUD (None
    sem o HUD); `text_width(texto)` em pixels. `with_maximize`: aberto, o rótulo reserva o botão de maximizar
    (feature 014, RN-09)."""
    s = float(scale)
    row_h, pad = ROW_HEIGHT * s, PAD_X * s
    x = (nav_right + GAP * s) if nav_right is not None else x_min + MARGIN_X * s
    top = y_max - MARGIN_Y * s
    label_w = (text_width(TITLE) + 2 * pad + style.LABEL_LOGO * s
               + (style.MAXIMIZE_W * s if (with_maximize and is_open) else 0.0))
    label = (x, top - row_h, label_w, row_h)
    if not is_open:
        return Layout(label, [])
    col_w = max([label_w] + [text_width(text) + 2 * pad for _key, text in items])
    rects = []
    y = top - row_h
    for key, _text in items:
        y -= row_h + ROW_GAP * s
        rects.append((key, (x, y, col_w, row_h)))
    return Layout((x, top - row_h, col_w, row_h), rects)


def _inside(px, py, rect):
    x, y, w, h = rect
    return x <= px <= x + w and y <= py <= y + h


def maximize_button(layout, scale):
    """Botão de maximizar no canto direito do rótulo do estado aberto (feature 014, design-direction.md)."""
    s = float(scale)
    x, y, w, h = layout.label
    size = 18.0 * s
    return (x + w - 6.0 * s - size, y + (h - size) / 2.0, size, size)


def hit(layout, px, py, maximize_scale=None):
    """'MAXIMIZE' (só com `maximize_scale` e o painel aberto), 'LABEL', a chave do item ou None."""
    if maximize_scale is not None and layout.items and _inside(px, py, maximize_button(layout, maximize_scale)):
        return 'MAXIMIZE'
    if _inside(px, py, layout.label):
        return 'LABEL'
    for key, rect in layout.items:
        if _inside(px, py, rect):
            return key
    return None


def bounds(layout):
    """Retângulo que envolve o painel inteiro (para o clique fora fechar)."""
    rects = [layout.label] + [rect for _key, rect in layout.items]
    x0 = min(r[0] for r in rects)
    y0 = min(r[1] for r in rects)
    x1 = max(r[0] + r[2] for r in rects)
    y1 = max(r[1] + r[3] for r in rects)
    return (x0, y0, x1 - x0, y1 - y0)


# ---------------------------------------------------------------------------------------------------------------------
# Retângulo maximizado (feature 014, T018; RN-08, RN-09, D-01, D-18)
# ---------------------------------------------------------------------------------------------------------------------

MaxLayout = namedtuple('MaxLayout', 'rect header logo title tabs search account buttons body sidebar grid footer compact')
BUTTON_KEYS = ('CLOSE', 'MINIMIZE', 'PIN')        # da direita para a esquerda no cabeçalho


def max_layout(rect, scale, text_width, tabs, account_label, footer=False):
    """Partes do retângulo maximizado: cabeçalho (ícone, título, abas, busca, conta, botões), coluna de filtros,
    grade e rodapé de download (opcional). `tabs` = [(chave, rótulo)]; medidas de `style` vezes a escala."""
    s = float(scale)
    x, y, w, h = rect
    head_h = style.HEADER_H * s
    hy = y + h - head_h
    header = (x, hy, w, head_h)
    logo = (x + style.SPACE_MD * s, hy + (head_h - style.LOGO * s) / 2.0, style.LOGO * s, style.LOGO * s)
    title_x = logo[0] + logo[2] + style.TITLE_GAP * s
    tab_x = x + style.TABS_X * s
    title = (title_x, hy, max(0.0, tab_x - title_x - style.SPACE_SM * s), head_h)
    tab_rects = []
    for key, label in tabs:
        tw = text_width(label)
        tab_rects.append((key, (tab_x, hy, tw, head_h)))
        tab_x += tw + style.TAB_GAP * s
    buttons = []
    bx = x + w - style.SPACE_MD * s - style.BUTTON * s
    by = hy + (head_h - style.BUTTON * s) / 2.0
    for key in BUTTON_KEYS:
        buttons.append((key, (bx, by, style.BUTTON * s, style.BUTTON * s)))
        bx -= style.BUTTON_STEP * s
    control_y = hy + (head_h - style.CONTROL_H * s) / 2.0
    account_right = buttons[-1][1][0] - style.SPACE_SM * s
    tabs_end = tab_rects[-1][1][0] + tab_rects[-1][1][2] if tab_rects else title[0] + title[2]
    room = account_right - tabs_end - 2 * style.SPACE_MD * s          # entre as abas e os botões
    account_w = text_width(account_label) + style.CHIP_PAD * s
    compact = room - account_w < style.SEARCH_MIN * s                  # sem espaço: a conta vira só o ponto
    if compact:
        account_w = style.CHIP_PAD * s
    account = (account_right - account_w, control_y, account_w, style.CONTROL_H * s)
    search_right = account[0] - style.SPACE_MD * s
    search_w = max(style.SEARCH_MIN * s, min(style.SEARCH_W * s, search_right - tabs_end - style.SPACE_MD * s))
    search = (search_right - search_w, control_y, search_w, style.CONTROL_H * s)
    foot_h = style.FOOTER_H * s if footer else 0.0
    body = (x, y + foot_h, w, h - head_h - foot_h)
    sidebar = (x, body[1], style.SIDEBAR_W * s, body[3])
    grid = grid_core.grid_area((x, y + foot_h, w, h - foot_h), scale)
    foot = (x, y, w, foot_h) if footer else None
    return MaxLayout(rect, header, logo, title, tab_rects, search, account, buttons, body, sidebar, grid, foot, compact)


def hit_max(layout, px, py, scale):
    """Parte do retângulo sob o ponto: borda ('LEFT', 'RIGHT', 'TOP', 'BOTTOM'), botão ('CLOSE', 'MINIMIZE', 'PIN'),
    'TAB:<chave>', 'SEARCH', 'ACCOUNT', 'HEADER', 'FOOTER', 'SIDEBAR', 'GRID', 'BODY' ou None (fora)."""
    region = grid_core.region_at(layout.rect, px, py, scale)
    if region is None:
        return None
    if region in ('LEFT', 'RIGHT', 'TOP', 'BOTTOM'):
        return region
    for key, rect in layout.buttons:
        if _inside(px, py, rect):
            return key
    for key, rect in layout.tabs:
        if _inside(px, py, rect):
            return 'TAB:' + key
    if _inside(px, py, layout.search):
        return 'SEARCH'
    if _inside(px, py, layout.account):
        return 'ACCOUNT'
    if _inside(px, py, layout.header):
        return 'HEADER'
    if layout.footer is not None and _inside(px, py, layout.footer):
        return 'FOOTER'
    if _inside(px, py, layout.sidebar):
        return 'SIDEBAR'
    if _inside(px, py, layout.grid):
        return 'GRID'
    return 'BODY'


def sidebar_rows(sidebar, tree, open_id, scale):
    """[(chave, retângulo, profundidade)] das linhas da coluna de filtros, de cima para baixo.

    `tree` = [(id, nome, contagem, [(id da coleção, nome, contagem)])]; só o fabricante `open_id` mostra as coleções
    (profundidade 1). Chaves 'MAN:<id>' e 'COL:<fabricante>/<coleção>'. Linhas que passariam do fundo ficam de fora.
    """
    s = float(scale)
    x, y, w, h = sidebar
    row = style.ROW_H * s
    top = y + h - style.CAPTION_H * s
    rows = []

    def add(key, depth):
        nonlocal top
        if top - row < y:
            return False
        top -= row
        rows.append((key, (x, top, w, row), depth))
        return True
    for man_id, _name, _count, collections in tree:
        if not add('MAN:' + man_id, 0):
            break
        if man_id == open_id:
            if not all(add('COL:{}/{}'.format(man_id, col_id), 1) for col_id, _cn, _n in collections):
                break
    return rows


def hit_rows(rows, px, py):
    for key, rect, _depth in rows:
        if _inside(px, py, rect):
            return key
    return None
