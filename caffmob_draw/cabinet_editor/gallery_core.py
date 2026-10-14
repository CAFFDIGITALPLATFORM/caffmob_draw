"""Galeria de estruturas de caixa do construtor (feature 015, T020; RN-11, RN-21, RF-11, RF-21, D-10, D-11).
Python puro, sem `bpy`.

A galeria "Selecione uma estrutura de caixa para iniciar a construção" é um quadro no centro da viewport: título,
uma aba por ambiente do catálogo (na ordem do arquivo), a grade de miniaturas das estruturas do ambiente (ordenadas
por `order`) e o rodapé com o estado em texto, os avisos do catálogo e os botões OK e Cancelar.

Retângulos como (x, y, largura, altura) em pixels da região, y de baixo para cima (desenho `POST_PIXEL`). Medidas em
pixels de escala 1, multiplicadas pela escala da interface (`scale`). A grade usa as medidas e as contas de
`library_panel/grid_core.py` (células de 140 × 188, colunas pela largura, rolagem e células visíveis).

`thumb_shapes` dá a elevação frontal de uma estrutura (peças de `structure.carcass_parts` projetadas em X e Z) em
medidas de referência; `fit_shapes` encaixa essa elevação no quadrado da miniatura.
"""

from collections import namedtuple

from ..data.i18n import N_, tr
from ..library_panel import grid_core
from . import structure as structure_core

TITLE = N_("Selecione uma estrutura de caixa para iniciar a construção")
SELECTED = N_("Selecionado: {}")
NONE_SELECTED = N_("Nenhuma estrutura selecionada")
EMPTY_TITLE = N_("Nenhuma estrutura de caixa no catálogo")
EMPTY_TAB = N_("Nenhuma estrutura neste ambiente")
OK, CANCEL = N_("OK"), N_("Cancelar")
GROUP_LABELS = {'INFERIOR': N_("Inferior"), 'SUPERIOR': N_("Superior"), 'DESPENSEIRO': N_("Despenseiro")}

PREF_W, PREF_H = 780.0, 600.0       # cabem 5 colunas de miniaturas e 2 linhas e meia
MIN_W, MIN_H = 420.0, 360.0
MARGIN = 24.0                       # distância mínima até a borda da região
PAD = 16.0
TITLE_H = 44.0
TABS_H = 30.0
TAB_PAD = 12.0                      # respiro de cada lado do nome da aba
TAB_GAP = 4.0
FOOTER_H = 56.0                     # estado em texto, aviso do catálogo e botões
BUTTON_W, BUTTON_H = 96.0, 26.0
GAP = grid_core.GAP

# Medidas de referência da miniatura (mm): a largura vem da estrutura; a altura do grupo quando o catálogo não dá.
REF_HEIGHT_MM = {'INFERIOR': 720.0, 'SUPERIOR': 700.0, 'DESPENSEIRO': 2400.0}
REF_DEPTH_MM = 550.0
REF_THICK_MM = 15.0
HIDDEN_ROLES = ('BACK', 'RAIL_LOW', 'RAIL_HIGH', 'STRETCHER_BACK')     # atrás do vão: não aparecem de frente
THUMB_PAD = 0.12                    # respiro da elevação dentro do quadrado (fração do lado)

Layout = namedtuple('Layout', 'rect title tabs grid footer status warning ok cancel')


# Catálogo -------------------------------------------------------------------------------------------------------------
def tabs(catalog):
    """[(id do ambiente, rótulo em português)] na ordem do catálogo."""
    return [(env.id, env.label_pt) for env in catalog.environments]


def tab_index(catalog, environment=""):
    """Aba que abre: a do ambiente (ou da linha) pedido; senão a primeira."""
    for index, env in enumerate(catalog.environments):
        if environment and environment in (env.id, env.line):
            return index
    return 0


def entries(catalog, tab):
    envs = catalog.environments
    return catalog.by_environment(envs[tab].id) if 0 <= tab < len(envs) else []


def status_text(structure):
    """Estado da seleção sempre em texto (RN-21), além do contorno laranja."""
    if structure is None:
        return tr(NONE_SELECTED)
    return tr(SELECTED).format(tr(structure.label_pt))


def empty_state(catalog):
    """(título, dica) do estado vazio: o catálogo não trouxe estrutura; a dica é o primeiro aviso, se houver."""
    return tr(EMPTY_TITLE), (catalog.warnings[0] if catalog.warnings else "")


# Quadro ---------------------------------------------------------------------------------------------------------------
def dialog_rect(region_w, region_h, scale):
    """Quadro centrado na região, no tamanho preferido; encolhe até o mínimo e, se a região for menor, até ela."""
    s = float(scale)
    avail_w, avail_h = max(0.0, region_w - 2 * MARGIN * s), max(0.0, region_h - 2 * MARGIN * s)
    w = min(max(min(PREF_W * s, avail_w), MIN_W * s), float(region_w))
    h = min(max(min(PREF_H * s, avail_h), MIN_H * s), float(region_h))
    return ((region_w - w) / 2.0, (region_h - h) / 2.0, w, h)


def layout(region_w, region_h, scale, tab_labels, measure):
    """`Layout` do quadro. `measure(texto)` = largura do texto do rótulo da aba em pixels (já na escala)."""
    s = float(scale)
    x, y, w, h = dialog_rect(region_w, region_h, scale)
    top = y + h
    pad = PAD * s
    title = (x + pad, top - TITLE_H * s, w - 2 * pad, TITLE_H * s)
    tabs_y = top - (TITLE_H + TABS_H) * s
    tab_rects, tx = [], x + pad
    for index, label in enumerate(tab_labels):
        tw = measure(label) + 2 * TAB_PAD * s
        tab_rects.append((index, (tx, tabs_y, tw, TABS_H * s)))
        tx += tw + TAB_GAP * s
    footer = (x, y, w, FOOTER_H * s)
    grid_bottom = y + FOOTER_H * s + GAP * s
    grid_top = tabs_y - pad
    grid = (x + pad, grid_bottom, max(0.0, w - 2 * pad), max(0.0, grid_top - grid_bottom))
    bw, bh, gap = BUTTON_W * s, BUTTON_H * s, GAP * s
    by = y + (FOOTER_H * s - bh) / 2.0
    cancel = (x + w - pad - bw, by, bw, bh)
    ok = (cancel[0] - gap - bw, by, bw, bh)
    text_w = max(0.0, ok[0] - gap - (x + pad))
    half = FOOTER_H * s / 2.0
    status = (x + pad, y + half, text_w, half - 4 * s)
    warning = (x + pad, y + 4 * s, text_w, half - 4 * s)
    return Layout((x, y, w, h), title, tab_rects, grid, footer, status, warning, ok, cancel)


def _inside(rect, px, py):
    x, y, w, h = rect
    return x <= px <= x + w and y <= py <= y + h


def visible_cells(lay, count, scale, scroll):
    return grid_core.visible_cells(lay.grid, count, scale, scroll)


def hit(lay, cells, px, py):
    """('OK',), ('CANCEL',), ('TAB', i), ('CELL', i), ('INSIDE',) ou None (fora do quadro)."""
    if not _inside(lay.rect, px, py):
        return None
    if _inside(lay.ok, px, py):
        return ('OK',)
    if _inside(lay.cancel, px, py):
        return ('CANCEL',)
    for index, rect in lay.tabs:
        if _inside(rect, px, py):
            return ('TAB', index)
    if _inside(lay.grid, px, py):                # célula cortada pela borda da grade só vale na parte visível
        index = grid_core.hit_cell(cells, px, py)
        if index is not None:
            return ('CELL', index)
    return ('INSIDE',)


def content_height(lay, count, scale):
    return grid_core.content_height(lay.grid[2], count, scale)


def scroll_by(scroll, delta, lay, count, scale):
    return grid_core.clamp_scroll(scroll + delta, content_height(lay, count, scale), lay.grid[3])


def scroll_to(index, lay, count, scale, scroll):
    """Rolagem que deixa a célula `index` inteira à vista (mexendo o mínimo)."""
    if index < 0:
        return scroll
    s = float(scale)
    cols = grid_core.columns(lay.grid[2], scale)
    step = (grid_core.CELL_H + grid_core.GAP) * s
    row_top = (index // cols) * step
    row_bottom = row_top + grid_core.CELL_H * s
    view = lay.grid[3]
    if row_top < scroll:
        scroll = row_top
    elif row_bottom > scroll + view:
        scroll = row_bottom - view
    return grid_core.clamp_scroll(scroll, content_height(lay, count, scale), view)


# Teclado --------------------------------------------------------------------------------------------------------------
def key_action(key, index, count, cols):
    """(novo índice, ação) da tecla: setas andam na grade; Enter = 'OK' (com seleção); Esc = 'CANCEL'."""
    if key == 'ESC':
        return index, 'CANCEL'
    if key in ('RET', 'NUMPAD_ENTER'):
        return index, ('OK' if 0 <= index < count else None)
    if count <= 0:
        return -1, None
    if index < 0:
        return 0, None
    step = {'LEFT_ARROW': -1, 'RIGHT_ARROW': 1, 'UP_ARROW': -cols, 'DOWN_ARROW': cols}.get(key)
    if step is None:
        return index, None
    target = index + step
    if 0 <= target < count:
        return target, None
    if key == 'DOWN_ARROW' and index // cols < (count - 1) // cols:
        return count - 1, None                    # última linha incompleta: vai para a última célula
    return index, None


class GalleryState:
    """Aba, seleção e rolagem da galeria aberta (o operador modal guarda uma instância)."""

    def __init__(self, catalog, environment=""):
        self.catalog = catalog
        self.tabs = tabs(catalog)
        self.tab = tab_index(catalog, environment)
        self.items = entries(catalog, self.tab)
        self.index = 0 if self.items else -1
        self.scroll = 0.0

    @property
    def empty(self):
        return not self.catalog.structures

    @property
    def selected(self):
        return self.items[self.index] if 0 <= self.index < len(self.items) else None

    def set_tab(self, tab):
        if not 0 <= tab < len(self.tabs) or tab == self.tab:
            return
        self.tab = tab
        self.items = entries(self.catalog, tab)
        self.index = 0 if self.items else -1
        self.scroll = 0.0

    def next_tab(self, step=1):
        if self.tabs:
            self.set_tab((self.tab + step) % len(self.tabs))

    def select(self, index):
        if 0 <= index < len(self.items):
            self.index = index

    def key(self, key, lay, scale):
        """Aplica a tecla; devolve 'OK', 'CANCEL' ou None."""
        cols = grid_core.columns(lay.grid[2], scale)
        self.index, action = key_action(key, self.index, len(self.items), cols)
        self.scroll = scroll_to(self.index, lay, len(self.items), scale, self.scroll)
        return action

    def status(self):
        return status_text(self.selected)


# Miniatura ------------------------------------------------------------------------------------------------------------
def reference_size(recipe):
    """(largura, altura, profundidade) em mm da miniatura."""
    height = recipe.height_mm or REF_HEIGHT_MM.get(recipe.group, 720.0)
    return recipe.width_mm, height, recipe.depth_mm or REF_DEPTH_MM


def thumb_shapes(recipe):
    """Elevação frontal em mm: {'parts': [(x0, z0, x1, z1)], 'inner': (x0, z0, x1, z1), 'dividers': [...],
    'bounds': (x0, z0, x1, z1)}. Peças de `carcass_parts` nas medidas de referência, sem as que ficam atrás do vão;
    os vãos (`bays`) aparecem separados por divisórias da mesma espessura."""
    width, height, depth = reference_size(recipe)
    t = REF_THICK_MM
    thick = {key: t for key in ('LEFT', 'RIGHT', 'BOTTOM', 'TOP', 'BACK', 'SAR', 'ROD', 'TAMP', 'TRA')}
    parts, inner = structure_core.carcass_parts(recipe, width, height, depth, thick,
                                                params=structure_core.default_params())
    rects = [(p.box[0][0], p.box[0][2], p.box[1][0], p.box[1][2]) for p in parts if p.role not in HIDDEN_ROLES]
    ix0, iz0, ix1, iz1 = inner[0][0], inner[0][2], inner[1][0], inner[1][2]
    dividers = []
    bays = max(1, int(getattr(recipe, 'bays', 1) or 1))
    if bays > 1:
        bay = (ix1 - ix0 - (bays - 1) * t) / bays
        for i in range(1, bays):
            dx = ix0 + i * bay + (i - 1) * t
            dividers.append((dx, iz0, dx + t, iz1))
    every = rects + [(ix0, iz0, ix1, iz1)]
    bounds = (min(r[0] for r in every), min(min(r[1] for r in every), 0.0), max(r[2] for r in every),
              max(r[3] for r in every))
    return {'parts': rects, 'inner': (ix0, iz0, ix1, iz1), 'dividers': dividers, 'bounds': bounds}


def fit_shapes(shapes, box):
    """Mesmas formas em pixels, centradas no quadrado `box` (x, y, lado, lado), proporção mantida: retângulos
    (x, y, largura, altura) e a linha do piso (x0, y, x1)."""
    bx, by, bw, bh = box
    x0, z0, x1, z1 = shapes['bounds']
    span_w, span_h = max(1e-6, x1 - x0), max(1e-6, z1 - z0)
    usable_w, usable_h = bw * (1.0 - 2 * THUMB_PAD), bh * (1.0 - 2 * THUMB_PAD)
    k = min(usable_w / span_w, usable_h / span_h)
    ox = bx + (bw - span_w * k) / 2.0 - x0 * k
    oy = by + (bh - span_h * k) / 2.0 - z0 * k

    def px(r):
        return (ox + r[0] * k, oy + r[1] * k, (r[2] - r[0]) * k, (r[3] - r[1]) * k)

    return {'parts': [px(r) for r in shapes['parts']], 'inner': px(shapes['inner']),
            'dividers': [px(r) for r in shapes['dividers']],
            'floor': (ox + x0 * k - 4.0, oy, ox + x1 * k + 4.0)}
