"""Layout do painel BIBLIOTECA CAFFMOB (feature 012, T015; D-14, D-30). Python puro.

Canto superior esquerdo da parte **visível** da viewport (`x_min`, `y_max` de `hb_gpu_draw.get_visible_window_bounds`:
o cabeçalho e a barra de ferramentas se sobrepõem à região e pegariam o clique); com o HUD ligado, à direita do botão
de navegação (`nav_right`).
Fechado: só o rótulo. Aberto: uma coluna de largura única abaixo dele, na ordem de `menu_items`. Retângulos como
(x, y, largura, altura) em pixels da região, com y de baixo para cima (como o desenho `POST_PIXEL`).
"""

from collections import namedtuple

from ..data.i18n import N_

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


def panel_layout(x_min, y_max, scale, nav_right, is_open, items, text_width):
    """`x_min`, `y_max` = limites visíveis da região; `nav_right` = borda direita do botão de navegação do HUD (None
    sem o HUD); `text_width(texto)` em pixels."""
    s = float(scale)
    row_h, pad = ROW_HEIGHT * s, PAD_X * s
    x = (nav_right + GAP * s) if nav_right is not None else x_min + MARGIN_X * s
    top = y_max - MARGIN_Y * s
    label_w = text_width(TITLE) + 2 * pad
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


def hit(layout, px, py):
    """'LABEL', a chave do item ou None."""
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
