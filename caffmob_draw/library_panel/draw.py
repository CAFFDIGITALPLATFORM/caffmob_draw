"""Desenho do painel BIBLIOTECA CAFFMOB no topo da viewport (feature 012, T020; feature 014, T028; D-01, D-18).

Um desenho `POST_PIXEL` sempre registrado (o painel aparece com ou sem o HUD). Ele sai cedo fora da região principal
da `VIEW_3D`. Três estados (`WindowManager.btm_library.mode`, RN-09):
- MIN: só o rótulo, com o ícone CAFF MOBI DRAW;
- OPEN: a coluna de categorias da 012 e o botão de maximizar no rótulo;
- MAX: o retângulo flutuante (`layout_core.max_layout`) com cabeçalho, coluna de fabricantes, grade de miniaturas com
  rolagem recortada e rodapé de download, nos tokens de `style` (design-direction.md).

O desenho só lê: posição inicial, limites e desvio do HUD são calculados aqui sem gravar no estado (gravar fica com o
clique, T030). Layouts em cache por região; o clique (`ops_click`) usa os mesmos layouts.
"""

import os
import time

import blf  # type: ignore
import bpy  # type: ignore
import gpu  # type: ignore

from ..data.i18n import N_, tr
from ..hb_gpu_draw import get_visible_window_bounds
from . import categories, categories_core, draw_kit as kit, grid_core, layout_core, models_core, style, thumbs_gpu

FONT_SIZE = 11
# Cores da 012, mantidas para quem as importa; o desenho usa `style` (feature 014).
BG = (0.13, 0.13, 0.14, 0.95)
BG_HOVER = (0.25, 0.25, 0.27, 0.96)
BG_TITLE = (0.20, 0.43, 0.70, 0.98)
BORDER = (1.0, 1.0, 1.0, 0.14)
TEXT = (0.90, 0.90, 0.90, 1.0)

ASSETS = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets")
LOGO_PATH = os.path.join(ASSETS, "caffmobi_draw_icon.png")
SORA_PATH = os.path.join(ASSETS, "fonts", "Sora-SemiBold.ttf")
LOGO_KEY = "logo:caffmobi_draw"
TABS = (('BLOCKS', N_("Blocos")), ('TEXTURES', N_("Texturas")))
TITLE_MAX = N_("Biblioteca")
SIGN_IN = N_("Entrar com a conta CAFF Mob")
SEARCH_HINT = N_("Buscar acabamento…")
MANUFACTURERS = N_("Fabricantes")
STATUS = {'DOWNLOADED': N_("Baixada"), 'NOT_DOWNLOADED': N_("Não baixada"), 'HOVER': N_("Arraste para aplicar"),
          'DOWNLOADING': N_("Baixando {}%"), 'ERROR': N_("Falhou · tentar de novo")}
NO_RESULTS = N_("Nenhum resultado para “{}”")
NO_RESULTS_HINT = N_("Confira a escrita ou busque em todos os fabricantes.")
BLOCKS_PICK = N_("Escolha uma categoria")
BLOCKS_PICK_HINT = N_("Os modelos prontos e os seus módulos salvos aparecem aqui.")
CATEGORIES = N_("Categorias")
BLOCK_STATUS = {'MODEL': N_("Modelo pronto"), 'MODULE': N_("Meu módulo"), 'HOVER': N_("Arraste para a cena")}
BLOCKS_TTL = 2.0                          # segundos de cache da lista de módulos salvos (lida do disco)
DOWNLOAD_FOOTER = N_("Baixando {} de {} · {} de {} MB")
CANCEL = N_("Cancelar")
LOAD_MORE = N_("Carregar mais texturas")
_more_id = "MOBI:MORE"
_remote = {"manufacturers": None, "thumbs": set(), "query": None, "changed": 0.0,
           "revision": -1, "active": False, "source": None, "requested": False,
           "manufacturers_retry": 0.0, "refresh_at": 0.0, "thumb_retry": {}}

_handle = [None]
_mouse = {'pos': (-1, -1), 'region': 0}
_cache = {}
_font = {'title': 0, 'loaded': False}
_blocks = {}                              # categoria → (hora, entradas)
_model_sizes = {}                         # (linha, tipo) → (hora, (largura, altura, z) em mm) do Padrão de Dimensões
_search = {'active': False}               # digitação da busca ligada (T031)
_selected = {'id': ""}                    # textura selecionada (gravada pelo clique e pelo arraste, T030/T032)


def _scale(context):
    try:
        return context.preferences.system.ui_scale or 1.0
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


def hud_rects(context, area):
    """Retângulos ocupados pelo plugin na região (o painel não os cobre, RN-09, RF-16)."""
    from ..operators import viewport_hud
    try:
        return viewport_hud.occupied_rects(context, area)
    except (AttributeError, TypeError, ValueError):
        return []


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


def _measure(size, font=0):
    def width(text):
        blf.size(font, size)
        return blf.dimensions(font, text)[0]
    return width


def layout(context, area, region):
    """Layout do rótulo e da coluna (estados MIN e OPEN), em cache por região."""
    state = context.window_manager.btm_library
    scale = _scale(context)
    is_open = state.mode == 'OPEN'
    entries = items(context) if is_open else []
    x_min, _x_max, _y_min, y_max = get_visible_window_bounds(area)
    key = ('COL', x_min, y_max, scale, is_open, tuple(entries), _nav_right(context, area))
    cached = _cache.get(region.as_pointer())
    if cached is not None and cached[0] == key:
        return cached[1]
    result = layout_core.panel_layout(x_min, y_max, scale, key[6], is_open, entries, _measure(FONT_SIZE * scale),
                                      with_maximize=True)
    _cache[region.as_pointer()] = (key, result)
    return result


def max_rect(context, area, state=None):
    """Retângulo do MAX já limitado à região visível e fora do HUD (sem gravar no estado)."""
    state = state or context.window_manager.btm_library
    scale = _scale(context)
    x_min, x_max, y_min, y_max = get_visible_window_bounds(area)
    bounds = (x_min, y_min, x_max - x_min, y_max - y_min)
    rect = tuple(state.rect)
    if rect[2] <= 0 or rect[3] <= 0:
        rect = grid_core.initial_rect(bounds, scale)
    return grid_core.clamp_rect(rect, bounds, hud_rects(context, area), scale)


def _account():
    """(rótulo, conectada?) da conta CAFF Mob (T023); sem o módulo da conta, desconectada."""
    try:
        from ..texture_library import auth
        email = auth.account_email()
    except (ImportError, AttributeError):
        email = ""
    return (email, True) if email else (tr(SIGN_IN), False)


def _downloads():
    """(concluídos, total, MB recebidos, MB total) quando há download em andamento (T021); senão None."""
    try:
        from ..texture_library import downloads
        return downloads.summary()
    except (ImportError, AttributeError):
        return None


def max_layout(context, area):
    state = context.window_manager.btm_library
    scale = _scale(context)
    rect = max_rect(context, area, state)
    account_label, _connected = _account()
    footer = _downloads() is not None
    tabs = [(k, tr(label)) for k, label in TABS]
    return layout_core.max_layout(rect, scale, _measure(style.FONT_BODY * scale), tabs, account_label, footer=footer)


# Catálogo e estado das texturas ------------------------------------------------------------------------------------
def _catalog():
    from ..texture_library import catalog
    return catalog


def texture_tree():
    cat = _catalog()
    data, _warnings = cat.load()
    return [(m["id"], m["name"], m.get("total", sum(len(c["items"]) for c in m["collections"])),
             [(c["id"], c["name"], c.get("total", len(c["items"]))) for c in m["collections"]]) for m in data["manufacturers"]]


def texture_items(state):
    cat = _catalog()
    found = cat.search(state.search, manufacturer=state.manufacturer, collection=state.collection)
    return found + ([{"id": _more_id, "name": tr(LOAD_MORE)}] if cat.has_more() else [])


def _module_entries(category):
    hit = _blocks.get(category)
    if hit is not None and time.monotonic() - hit[0] < BLOCKS_TTL:
        return hit[1]
    from ..customize import library_io
    try:
        modules = [e for e in library_io.list_modules() if e["category"].casefold() == category.casefold()]
    except (OSError, ValueError):
        modules = []
    entries = [{"id": "BLK:MODULE:" + e["blend"], "name": e["name"], "kind": 'MODULE', "blend": e["blend"],
                "thumb_file": e["png"] if os.path.exists(e["png"]) else ""} for e in modules]
    _blocks[category] = (time.monotonic(), entries)
    return entries


def _model_size(line, cabinet_type):
    """(largura, altura, z) em mm do Padrão de Dimensões ativo para a linha e o tipo (em cache por alguns segundos)."""
    key = (line, cabinet_type)
    hit = _model_sizes.get(key)
    if hit is not None and time.monotonic() - hit[0] < BLOCKS_TTL:
        return hit[1]
    try:
        from ..operators.cabinet_builder import standard_defaults
        found, _definition = standard_defaults(bpy.context, line, cabinet_type)
        size = (found.width * 1000.0, found.height * 1000.0, found.z * 1000.0)
    except (ImportError, AttributeError, KeyError, TypeError, ValueError):
        size = {'WALL': (800.0, 700.0, 1500.0), 'TALL': (600.0, 2200.0, 0.0)}.get(cabinet_type, (800.0, 720.0, 0.0))
    _model_sizes[key] = (time.monotonic(), size)
    return size


def block_entries(state):
    """Blocos da categoria aberta (T040): modelos prontos na linha da categoria e os módulos salvos nela."""
    name = state.category
    if not name:
        return []
    found = categories.find(name)
    line = found.line if found is not None else categories_core.DEFAULT_LINE
    models, _warnings = models_core.load_default()
    entries = []
    for m in models:
        width, height, z = _model_size(line, m.cabinet_type)
        entries.append({"id": "BLK:MODEL:" + m.id, "name": tr(m.label), "kind": 'MODEL', "model": m.id, "line": line,
                        "thumb_file": "", "cabinet_type": m.cabinet_type, "door_swing": m.door_swing,
                        "shelves": m.shelves, "size_mm": (m.width_mm or width, height, z)})
    entries += _module_entries(name)
    text = state.search.strip().casefold()
    return [e for e in entries if text in e["name"].casefold()] if text else entries


def grid_entries(state):
    """Entradas da grade na aba atual (texturas do catálogo ou blocos da categoria)."""
    return texture_items(state) if state.tab == 'TEXTURES' else block_entries(state)


def entry_key(entry):
    return entry["id"]


def sidebar_tree(state):
    """Árvore da coluna de filtros: fabricantes e coleções (Texturas) ou categorias (Blocos, chave 'MAN:<nome>')."""
    if state.tab == 'TEXTURES':
        return texture_tree()
    return [(c.name, c.name, 0, []) for c in categories.all_categories()]


def texture_state(item):
    """('DOWNLOADED' | 'NOT_DOWNLOADED' | 'DOWNLOADING' | 'ERROR', progresso 0–1), pela ponte de download (T021)."""
    try:
        from ..texture_library import downloads
        found = downloads.state(item["id"])
        if downloads.state(item["id"] + ":miniatura") == 'FAILED':
            found = 'FAILED'
        progress = downloads.progress(item["id"])
    except (ImportError, AttributeError, ValueError, RuntimeError):
        return 'NOT_DOWNLOADED', 0.0
    if found == 'DONE':
        return 'DOWNLOADED', 1.0
    if found in ('PENDING', 'ACTIVE'):
        return 'DOWNLOADING', progress or 0.0
    if found == 'FAILED':
        return 'ERROR', 0.0
    return 'NOT_DOWNLOADED', 0.0


# Desenho -----------------------------------------------------------------------------------------------------------
def _logo(x, y, size):
    tex = thumbs_gpu.texture(LOGO_KEY, LOGO_PATH)
    if tex is not None:
        kit.image(tex, x, y, size, size)
    else:
        kit.rect(x, y, size, size, style.CREAM, size * 0.22)


def _title_font():
    if not _font['loaded']:
        _font['loaded'] = True
        if os.path.exists(SORA_PATH):
            font_id = blf.load(SORA_PATH)
            _font['title'] = font_id if font_id != -1 else 0
    return _font['title']


def _draw_column(context, region, state, mouse, viewport):
    s = _scale(context)
    lay = layout(context, context.area, region)
    hovered = layout_core.hit(lay, *mouse, maximize_scale=s)
    x, y, w, h = lay.label
    if not lay.items:
        kit.shadow(x, y, w, h, style.RADIUS_CONTROL * s, s)
    kit.rect(x, y, w, h, style.SURFACE_HOVER if hovered == 'LABEL' else style.SURFACE, style.RADIUS_CONTROL * s)
    kit.outline(x, y, w, h, style.BORDER, viewport, style.RADIUS_CONTROL * s)
    _logo(x + 8 * s, y + (h - 16 * s) / 2.0, 16 * s)
    kit.text_centered_y(layout_core.TITLE, lay.label, x + (layout_core.PAD_X + style.LABEL_LOGO - 4) * s,
                        style.FONT_LABEL * s, style.TEXT)
    if not lay.items:
        return
    bx, by, bw, bh = layout_core.maximize_button(lay, s)
    if hovered == 'MAXIMIZE':
        kit.rect(bx, by, bw, bh, style.SURFACE_HOVER, style.RADIUS_CONTROL * s)
    kit.icon('MAXIMIZE', bx + 2 * s, by + 2 * s, 14 * s, style.TEXT_MUTED, viewport)
    rects = [r for _k, r in lay.items]
    bottom = min(r[1] for r in rects) - 4 * s
    col_top = y - 2 * s
    kit.shadow(x, bottom, w, col_top - bottom, style.RADIUS_PANEL * s, s)
    kit.rect(x, bottom, w, col_top - bottom, style.SURFACE, style.RADIUS_PANEL * s)
    kit.outline(x, bottom, w, col_top - bottom, style.BORDER, viewport, style.RADIUS_PANEL * s)
    labels = dict(items(context))
    for key, rect in lay.items:
        if key == hovered:
            kit.rect(rect[0] + 4 * s, rect[1] + 1 * s, rect[2] - 8 * s, rect[3] - 2 * s, style.SURFACE_HOVER,
                     style.RADIUS_CONTROL * s)
        muted = key == layout_core.CREATE_CATEGORY
        kit.text_centered_y(labels.get(key, key), rect, rect[0] + style.SPACE_MD * s, style.FONT_BODY * s,
                            style.TEXT_SUBTLE if muted else style.TEXT)


def _draw_header(lay, state, mouse, viewport, s):
    hx, hy, hw, hh = lay.header
    kit.rect(hx + 1, hy, hw - 2, hh - 1, style.SURFACE_RAISED, (style.RADIUS_PANEL - 2) * s)
    kit.polyline([(hx, hy), (hx + hw, hy)], style.BORDER, 1.0, viewport)
    lx, ly, lsize, _ = lay.logo
    _logo(lx, ly, lsize)
    kit.text_centered_y(tr(TITLE_MAX), lay.header, lay.title[0], style.FONT_TITLE * s, style.TEXT, _title_font(),
                        max_w=lay.title[2])
    for key, rect in lay.tabs:
        active = state.tab == key
        label = tr(dict(TABS)[key])
        kit.text_centered_y(label, rect, rect[0], style.FONT_BODY * s, style.TEXT if active else style.TEXT_SUBTLE)
        if active:
            kit.rect(rect[0], hy + 2 * s, rect[2], 2 * s, style.ACCENT)
    sx, sy, sw, sh = lay.search
    kit.rect(sx, sy, sw, sh, style.SURFACE_SUNKEN, style.RADIUS_CONTROL * s)
    typing = _search['active']
    kit.outline(sx, sy, sw, sh, style.ACCENT if typing else (style.BORDER_STRONG if state.search else style.BORDER),
                viewport, style.RADIUS_CONTROL * s)
    kit.icon('SEARCH', sx + 7 * s, sy + (sh - 13 * s) / 2.0, 13 * s, style.TEXT_SUBTLE, viewport)
    hint = state.search or ("" if typing else tr(SEARCH_HINT))
    shown = kit.text_centered_y(hint, lay.search, sx + 26 * s, style.FONT_LABEL * s,
                                style.TEXT if state.search else style.TEXT_SUBTLE, max_w=sw - 40 * s)
    if typing:                                          # cursor da digitação
        cx = sx + 26 * s + (shown if state.search else 0.0) + 1 * s
        kit.rect(cx, sy + 5 * s, 1.5 * s, sh - 10 * s, style.TEXT)
    ax, ay, aw, ah = lay.account
    label, connected = _account()
    kit.rect(ax, ay, aw, ah, style.SURFACE_SUNKEN, style.RADIUS_CHIP * s)
    if lay.compact:                                     # cabeçalho estreito: só o ponto de estado
        kit.circle(ax + aw / 2.0, ay + ah / 2.0, 3.5 * s, style.SUCCESS if connected else style.TEXT_SUBTLE)
    else:
        kit.circle(ax + 11 * s, ay + ah / 2.0, 3.5 * s, style.SUCCESS if connected else style.TEXT_SUBTLE)
        kit.text_centered_y(label, lay.account, ax + 20 * s, style.FONT_LABEL * s, style.TEXT_MUTED,
                            max_w=aw - 24 * s)
    hovered = layout_core.hit_max(lay, *mouse, scale=s)
    for key, (bx, by, bw, bh) in lay.buttons:
        on = key == 'PIN' and state.pinned
        if on:
            kit.rect(bx, by, bw, bh, style.ACCENT_TINT, style.RADIUS_CONTROL * s)
        elif hovered == key:
            kit.rect(bx, by, bw, bh, style.SURFACE_HOVER, style.RADIUS_CONTROL * s)
        kit.icon(key, bx + 4 * s, by + 4 * s, 14 * s, style.ACCENT if on else style.TEXT_MUTED, viewport)


def _draw_sidebar(lay, state, mouse, viewport, s):
    x, y, w, h = lay.sidebar
    kit.rect(x + 1, y, w - 1, h, style.SURFACE_RAISED)
    kit.polyline([(x + w, y), (x + w, y + h)], style.BORDER, 1.0, viewport)
    blocks = state.tab != 'TEXTURES'
    kit.text(tr(CATEGORIES if blocks else MANUFACTURERS), x + style.SPACE_MD * s, y + h - 20 * s,
             style.FONT_SMALL * s, style.TEXT_SUBTLE)
    tree = sidebar_tree(state)
    rows = layout_core.sidebar_rows(lay.sidebar, tree, "" if blocks else state.manufacturer, s)
    names = {('MAN:' + m): (n, c) for m, n, c, _cols in tree}
    names.update({'COL:{}/{}'.format(m, cid): (cn, cc) for m, _n, _c, cols in tree for cid, cn, cc in cols})
    hovered = layout_core.hit_rows(rows, *mouse)
    selected = 'COL:{}/{}'.format(state.manufacturer, state.collection) if state.collection else ""
    if blocks:
        selected = 'MAN:' + state.category if state.category else ""
    for key, rect, depth in rows:
        name, count = names.get(key, (key, 0))
        rx, ry, rw, rh = rect
        if key == selected:
            kit.rect(rx + 6 * s, ry, rw - 12 * s, rh, style.ACCENT_TINT, style.RADIUS_CONTROL * s)
        elif key == hovered:
            kit.rect(rx + 6 * s, ry, rw - 12 * s, rh, style.SURFACE_HOVER, style.RADIUS_CONTROL * s)
        if blocks:
            kit.text_centered_y(name, rect, rx + style.SPACE_MD * s, style.FONT_BODY * s,
                                style.TEXT if key == selected else style.TEXT_MUTED, max_w=rw - 24 * s)
            continue
        if depth == 0:
            is_open = key == 'MAN:' + state.manufacturer
            kit.icon('CHEVRON_DOWN' if is_open else 'CHEVRON_RIGHT', rx + 8 * s, ry + (rh - 12 * s) / 2.0, 12 * s,
                     style.TEXT_SUBTLE, viewport)
            kit.text_centered_y(name, rect, rx + 26 * s, style.FONT_BODY * s,
                                style.TEXT if is_open else style.TEXT_MUTED, max_w=rw - 70 * s)
        else:
            kit.text_centered_y(name, rect, rx + (style.INDENT + 8) * s, style.FONT_LABEL * s,
                                style.TEXT if key == selected else style.TEXT_MUTED, max_w=rw - 80 * s)
        number = str(count)
        kit.text_centered_y(number, rect, rx + rw - style.SPACE_MD * s - kit.width_of(number, style.FONT_SMALL * s),
                            style.FONT_SMALL * s, style.TEXT_SUBTLE)


def _clip(region, rect):
    """Liga o recorte da área e devolve o recorte anterior para restaurar.

    No desenho POST_PIXEL o framebuffer tem o tamanho da região (viewport em 0, 0; medido no Blender 5.2), então o
    recorte usa coordenadas da região. O teste de scissor é ligado aqui: a região não o deixa ligado. Restaurar a caixa
    cheia da região deixa o teste ligado sem efeito para quem desenha depois.
    """
    previous = gpu.state.scissor_get()
    x, y, w, h = rect
    gpu.state.scissor_test_set(True)
    gpu.state.scissor_set(int(x), int(y), int(max(0, w)), int(max(0, h)))
    return previous


def _draw_cell(item, rect, state_kind, progress, hovered, viewport, s):
    x, y, w, h = rect
    if item["id"] == _more_id:
        kit.text_centered_y(tr(LOAD_MORE), rect, x, style.FONT_LABEL * s, style.TEXT)
        return
    selected = item["id"] == _selected['id']
    if hovered or selected:
        kit.rect(x - 4 * s, y - 4 * s, w + 8 * s, h + 8 * s, style.SURFACE_HOVER, (style.RADIUS_CELL + 2) * s)
    side = style.CELL_W * s
    ty = y + h - side
    kit.rect(x, ty, side, side, style.SURFACE_SUNKEN, style.RADIUS_CELL * s)
    tex = thumbs_gpu.texture(item["id"], _catalog().thumb_path(item))
    if tex is not None:
        kit.image(tex, x, ty, side, side, src_size=item.get("px"))
    if selected:
        kit.outline(x - 1, ty - 1, side + 2, side + 2, style.ACCENT, viewport, style.RADIUS_CELL * s, 2.0)
    badge = {'DOWNLOADED': ('CHECK', style.SUCCESS), 'ERROR': ('ALERT', style.ERROR),
             'NOT_DOWNLOADED': ('CLOUD', style.TEXT_MUTED)}.get(state_kind)
    if badge:
        bx, by = x + side - 24 * s, ty + side - 24 * s
        kit.rect(bx, by, 20 * s, 20 * s, (0.04, 0.12, 0.12, 0.72), 10 * s)
        kit.icon(badge[0], bx + 3 * s, by + 3 * s, 14 * s, badge[1], viewport)
    if state_kind == 'DOWNLOADING':
        kit.rect(x, ty, side, 4 * s, (0.0, 0.0, 0.0, 0.5))
        kit.rect(x, ty, side * max(0.0, min(1.0, progress)), 4 * s, style.INFO)
    line_y = ty - 14 * s
    for line in kit.wrap2(item["name"], style.FONT_LABEL * s, side):
        kit.text(line, x, line_y, style.FONT_LABEL * s, style.TEXT)
        line_y -= 13 * s
    on_hover_bg = hovered or selected            # sobre SURFACE_HOVER, TEXT_SUBTLE cai a 3,7:1 (design-direction.md)
    if state_kind == 'DOWNLOADING':
        label, color = tr(STATUS['DOWNLOADING']).format(int(progress * 100)), style.INFO
    elif state_kind == 'ERROR':
        label, color = tr(STATUS['ERROR']), (style.TEXT_MUTED if on_hover_bg else style.ERROR)
    elif hovered:
        label, color = tr(STATUS['HOVER']), style.TEXT_MUTED
    elif state_kind == 'DOWNLOADED':
        label, color = tr(STATUS['DOWNLOADED']), (style.TEXT_MUTED if on_hover_bg else style.SUCCESS)
    else:
        label, color = tr(STATUS['NOT_DOWNLOADED']), (style.TEXT_MUTED if on_hover_bg else style.TEXT_SUBTLE)
    kit.text(label, x, line_y - 1 * s, style.FONT_SMALL * s, color, max_w=side)


def _draw_model_front(entry, box, viewport, s):
    """Frente do modelo pronto no traço da marca: piso, rodapé, caixa, portas, puxadores e prateleiras."""
    width, height, z = entry["size_mm"]
    shapes = models_core.thumb_shapes(entry["cabinet_type"], width, height, z, entry["door_swing"], entry["shelves"],
                                      box)
    x0, fy, x1 = shapes["floor"]
    kit.polyline([(x0, fy), (x1, fy)], style.TEXT_SUBTLE, 1.0, viewport)
    cx, cy, cw, ch = shapes["carcass"]
    kit.rect(cx, cy, cw, ch, style.SURFACE_RAISED, 1.5 * s)
    if shapes["plinth"] is not None:
        px, py, pw, ph = shapes["plinth"]
        kit.rect(px, py, pw, ph, style.SURFACE_SUNKEN)
    for y in shapes["shelves"]:
        kit.polyline([(cx + 3 * s, y), (cx + cw - 3 * s, y)], style.TEXT_SUBTLE, 1.0, viewport)
    for dx, dy, dw, dh in shapes["doors"]:
        kit.rect(dx, dy, dw, dh, style.SURFACE_HOVER, 1.0 * s)
        kit.outline(dx, dy, dw, dh, style.BORDER_STRONG, viewport, 1.0 * s)
    kit.outline(cx, cy, cw, ch, style.TEXT_MUTED, viewport, 1.5 * s, 1.5)
    for hx, hy in shapes["handles"]:
        kit.circle(hx, hy, max(1.5, 1.8 * s), style.ACCENT)


def _draw_block_cell(entry, rect, hovered, viewport, s):
    x, y, w, h = rect
    selected = entry["id"] == _selected['id']
    if hovered or selected:
        kit.rect(x - 4 * s, y - 4 * s, w + 8 * s, h + 8 * s, style.SURFACE_HOVER, (style.RADIUS_CELL + 2) * s)
    side = style.CELL_W * s
    ty = y + h - side
    kit.rect(x, ty, side, side, style.SURFACE_SUNKEN, style.RADIUS_CELL * s)
    tex = thumbs_gpu.texture(entry["id"], entry["thumb_file"]) if entry["thumb_file"] else None
    if tex is not None:
        kit.image(tex, x, ty, side, side)
    elif entry["kind"] == 'MODEL':                     # modelo pronto: a frente dele em escala (BUG-20261014-RWU2)
        _draw_model_front(entry, (x, ty, side, side), viewport, s)
    else:                                               # sem miniatura: o desenho de um módulo em traço
        m = side / 140.0
        bx, by, bw, bh = x + 38 * m, ty + 30 * m, 64 * m, 80 * m
        kit.outline(bx, by, bw, bh, style.TEXT_SUBTLE, viewport, 2 * m, 1.5)
        kit.polyline([(bx + bw / 2.0, by + 6 * m), (bx + bw / 2.0, by + bh - 6 * m)], style.TEXT_SUBTLE, 1.5, viewport)
        kit.circle(bx + bw / 2.0 - 6 * m, by + bh / 2.0, 2 * m, style.TEXT_SUBTLE)
        kit.circle(bx + bw / 2.0 + 6 * m, by + bh / 2.0, 2 * m, style.TEXT_SUBTLE)
    if selected:
        kit.outline(x - 1, ty - 1, side + 2, side + 2, style.ACCENT, viewport, style.RADIUS_CELL * s, 2.0)
    line_y = ty - 14 * s
    for line in kit.wrap2(entry["name"], style.FONT_LABEL * s, side):
        kit.text(line, x, line_y, style.FONT_LABEL * s, style.TEXT)
        line_y -= 13 * s
    label = tr(BLOCK_STATUS['HOVER' if hovered else entry["kind"]])
    kit.text(label, x, line_y - 1 * s, style.FONT_SMALL * s, style.TEXT_MUTED if hovered or selected
             else style.TEXT_SUBTLE, max_w=side)


def _draw_empty(area, title, hint, viewport, s):
    ax, ay, aw, ah = area
    cx, cy = ax + aw / 2.0, ay + ah / 2.0
    kit.icon('SEARCH', cx - 14 * s, cy + 40 * s, 28 * s, style.TEXT_SUBTLE, viewport)
    kit.text(title, cx - kit.width_of(title, style.FONT_TITLE * s) / 2.0, cy + 8 * s, style.FONT_TITLE * s, style.TEXT)
    if hint:
        kit.text(hint, cx - kit.width_of(hint, style.FONT_BODY * s) / 2.0, cy - 16 * s, style.FONT_BODY * s,
                 style.TEXT_MUTED)


def _draw_grid(region, lay, state, mouse, viewport, s):
    area = lay.grid
    blocks = state.tab != 'TEXTURES'
    if blocks and not state.category:
        _draw_empty(area, tr(BLOCKS_PICK), tr(BLOCKS_PICK_HINT), viewport, s)
        return
    warnings = [] if blocks else _catalog().load()[1]
    entries = grid_entries(state)
    if not entries:
        if warnings:
            _draw_empty(area, tr(warnings[0]), "", viewport, s)
        else:
            _draw_empty(area, tr(NO_RESULTS).format(state.search), tr(NO_RESULTS_HINT) if state.search else "",
                        viewport, s)
        return
    if warnings:
        kit.text(tr(warnings[0]), area[0] + 4 * s, area[1] + area[3] + 4 * s,
                 style.FONT_SMALL * s, style.TEXT, max_w=area[2])
    content = grid_core.content_height(area[2], len(entries), s)
    scroll = grid_core.clamp_scroll(state.scroll, content, area[3])
    cells = grid_core.visible_cells(area, len(entries), s, scroll)
    hovered = grid_core.hit_cell(cells, *mouse)
    previous = _clip(region, (area[0] - 6 * s, area[1], area[2] + 12 * s, area[3] + 6 * s))
    try:
        for index, rect in cells:
            if blocks:
                _draw_block_cell(entries[index], rect, index == hovered, viewport, s)
                continue
            kind, progress = texture_state(entries[index])
            _draw_cell(entries[index], rect, kind, progress, index == hovered, viewport, s)
    finally:
        gpu.state.scissor_set(*previous)
    if content > area[3]:
        ax, ay, aw, ah = area
        kit.rect(ax + aw - 3 * s, ay, 3 * s, ah, (1.0, 1.0, 1.0, 0.05), 1.5 * s)
        thumb_h = max(24 * s, ah * ah / content)
        thumb_y = ay + (ah - thumb_h) * (1.0 - scroll / max(1.0, content - ah))
        kit.rect(ax + aw - 3 * s, thumb_y, 3 * s, thumb_h, (1.0, 1.0, 1.0, 0.22), 1.5 * s)


def _draw_footer(lay, viewport, s):
    summary = _downloads()
    if summary is None or lay.footer is None:
        return
    done, total, received_mb, total_mb = summary
    fx, fy, fw, fh = lay.footer
    kit.polyline([(fx, fy + fh), (fx + fw, fy + fh)], style.BORDER, 1.0, viewport)
    label = tr(DOWNLOAD_FOOTER).format(done, total, "{:.1f}".format(received_mb).replace(".", ","),
                                       "{:.1f}".format(total_mb).replace(".", ","))
    kit.text_centered_y(label, lay.footer, fx + style.SPACE_MD * s, style.FONT_LABEL * s, style.TEXT_MUTED)
    bar_x = fx + 300 * s
    kit.rect(bar_x, fy + 12 * s, 220 * s, 4 * s, (1.0, 1.0, 1.0, 0.10), 2 * s)
    kit.rect(bar_x, fy + 12 * s, 220 * s * (received_mb / total_mb if total_mb else 0.0), 4 * s, style.INFO, 2 * s)
    cancel = tr(CANCEL)
    kit.text_centered_y(cancel, lay.footer, fx + fw - style.SPACE_MD * s - kit.width_of(cancel, style.FONT_LABEL * s),
                        style.FONT_LABEL * s, style.TEXT_MUTED)


def _draw_max(context, region, state, mouse, viewport):
    s = _scale(context)
    lay = max_layout(context, context.area)
    x, y, w, h = lay.rect
    kit.shadow(x, y, w, h, style.RADIUS_PANEL * s, s)
    kit.rect(x, y, w, h, style.SURFACE, style.RADIUS_PANEL * s)
    kit.outline(x, y, w, h, style.BORDER, viewport, style.RADIUS_PANEL * s)
    _draw_header(lay, state, mouse, viewport, s)
    _draw_sidebar(lay, state, mouse, viewport, s)
    _draw_grid(region, lay, state, mouse, viewport, s)
    _draw_footer(lay, viewport, s)
    for i in range(3):                                   # alça de redimensionar
        kit.polyline([(x + w - (4 + 4 * i) * s, y + 3 * s), (x + w - 3 * s, y + (4 + 4 * i) * s)], style.TEXT_SUBTLE,
                     1.0, viewport)


def draw_panel():
    context = bpy.context
    area, region = context.area, context.region
    if area is None or area.type != 'VIEW_3D' or region is None or region.type != 'WINDOW':
        return
    state = getattr(context.window_manager, 'btm_library', None)
    if state is None:
        return
    mouse = _mouse['pos'] if _mouse['region'] == region.as_pointer() else (-1, -1)
    viewport = (region.width, region.height)
    try:
        if state.mode == 'MAX':
            _draw_max(context, region, state, mouse, viewport)
        else:
            _draw_column(context, region, state, mouse, viewport)
    finally:
        gpu.state.blend_set('NONE')


def tag_redraw(context):
    for window in context.window_manager.windows:
        for area in window.screen.areas:
            if area.type == 'VIEW_3D':
                area.tag_redraw()


# (063 RF-03, RF-11; D-07) O timer agenda rede e miniaturas; draw só lê.
def _remote_tick():
    from ..texture_library import auth, downloads
    cat = _catalog()
    state = getattr(bpy.context.window_manager, 'btm_library', None)
    opened = state is not None and state.mode == 'MAX' and state.tab == 'TEXTURES'
    if not opened:
        if _remote['active']:
            cat.cancel(manufacturers=True)
        _remote['active'] = False
        return 0.4
    source = cat.remote_source()
    if _remote['source'] is not None and source != _remote['source']:
        state.manufacturer = state.collection = ''
        state.scroll = 0
    _remote['source'] = source
    if not auth.signed_in() or downloads.unavailable_reason():
        _remote['active'] = False
        return 0.4
    if not _remote['active'] or _remote['revision'] != cat._cache['revision']:
        cat.cancel(manufacturers=True)
        _remote.update(manufacturers=None, thumbs=set(), query=None, revision=cat._cache['revision'],
                       active=True, requested=False, manufacturers_retry=0.0, refresh_at=0.0, thumb_retry={})
    now = time.monotonic()
    if _remote['manufacturers'] is None and now >= _remote['manufacturers_retry']:
        _remote['manufacturers'] = True
        revision = cat._cache['revision']
        def manufacturers_done(status, body):
            if revision == cat._cache['revision']:
                _remote['manufacturers'] = True if status in (200, 304) else None
                _remote['manufacturers_retry'] = time.monotonic() + 5.0
        cat.refresh_manufacturers(manufacturers_done)
    query = (state.search, state.manufacturer, state.collection)
    if _remote['query'] != query:
        _remote.update(query=query, changed=now, requested=False, refresh_at=0.0)
        cat.cancel()
    if now - _remote['changed'] >= 0.4 and now >= _remote['refresh_at']:
        cat.refresh(*query, force=not _remote['requested'])
        _remote.update(requested=True, refresh_at=now + 5.0)
    entries = texture_items(state)
    for window in bpy.context.window_manager.windows:
        for area in window.screen.areas:
            if area.type != 'VIEW_3D':
                continue
            lay = max_layout(bpy.context, area)
            scale = _scale(bpy.context)
            content = grid_core.content_height(lay.grid[2], len(entries), scale)
            scroll = grid_core.clamp_scroll(state.scroll, content, lay.grid[3])
            for index, _rect in grid_core.visible_cells(lay.grid, len(entries), scale, scroll):
                entry = entries[index]
                if entry['id'] == _more_id or entry.get('file'):
                    continue
                thumb = cat.thumb_entry(entry)
                if (thumb['id'] in _remote['thumbs'] or cat.thumb_path(entry)
                        or now < _remote['thumb_retry'].get(thumb['id'], 0.0)):
                    continue
                _remote['thumbs'].add(thumb['id'])
                revision = cat._cache['revision']
                def thumbnail_done(path, error, tid=thumb['id'], revision=revision):
                    if revision != cat._cache['revision']:
                        return
                    _remote['thumbs'].discard(tid)
                    if error:
                        _remote['thumb_retry'][tid] = time.monotonic() + 5.0
                downloads.fetch(thumb['id'], thumbnail_done, entry=thumb)
    tag_redraw(bpy.context)
    return 0.4


def register():
    if not bpy.app.timers.is_registered(_remote_tick):
        bpy.app.timers.register(_remote_tick, first_interval=0.4, persistent=True)
    if _handle[0] is None:
        _handle[0] = bpy.types.SpaceView3D.draw_handler_add(draw_panel, (), 'WINDOW', 'POST_PIXEL')


def unregister():
    if bpy.app.timers.is_registered(_remote_tick):
        bpy.app.timers.unregister(_remote_tick)
    _remote.update(manufacturers=None, thumbs=set(), query=None, revision=-1, active=False, source=None,
                   requested=False, manufacturers_retry=0.0, refresh_at=0.0, thumb_retry={})
    if _handle[0] is not None:
        bpy.types.SpaceView3D.draw_handler_remove(_handle[0], 'WINDOW')
        _handle[0] = None
    _cache.clear()
    thumbs_gpu.free()
    if _font['loaded'] and _font['title']:
        blf.unload(SORA_PATH)
    _font.update(title=0, loaded=False)
