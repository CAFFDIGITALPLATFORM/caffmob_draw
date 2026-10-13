"""Grade e retângulo maximizado da BIBLIOTECA CAFFMOB (feature 014, T017; RN-08, RN-09, D-01, D-06, D-11).
Python puro.

Retângulos como (x, y, largura, altura) em pixels da região, com y de baixo para cima (desenho `POST_PIXEL`). As
medidas são em pixels de escala 1 e multiplicadas pela escala da interface (`scale`).

- Três estados (`next_mode`): MIN (só o rótulo), OPEN (coluna de categorias) e MAX (retângulo com a grade). Fixo, o
  MAX não fecha com clique fora nem com Esc.
- O retângulo fica dentro da região visível e fora dos retângulos proibidos (HUD, navegação, avisos), movendo-se
  para o lado livre mais próximo ou encolhendo até o mínimo (`clamp_rect`).
- A grade preenche colunas pela largura, rola pela altura do conteúdo e devolve só as células visíveis.
"""

MIN_W, MIN_H = 560.0, 300.0           # cabe o cabeçalho com abas, busca mínima, conta compacta e botões
CELL_W, CELL_H = 140.0, 188.0            # miniatura de 140 px + nome em 2 linhas + estado (design-direction.md)
GAP = 8.0
PAD = 12.0
HEADER_H = 36.0                          # cabeçalho: título, abas, busca e botões
SIDEBAR_W = 180.0                        # coluna de fabricantes e coleções
EDGE = 6.0                               # faixa da borda que redimensiona
MARGIN = 12.0
INITIAL_W, INITIAL_H = 0.55, 0.7         # fração da região visível na primeira abertura

MIN, OPEN, MAX = 'MIN', 'OPEN', 'MAX'


def next_mode(mode, event, pinned):
    """Estado depois do evento: 'LABEL', 'MAXIMIZE', 'MINIMIZE', 'OUTSIDE' (clique fora) ou 'ESC'."""
    if event == 'MAXIMIZE':
        return MAX
    if event == 'MINIMIZE':
        return MIN
    if event == 'LABEL':
        return OPEN if mode == MIN else MIN
    if event in ('OUTSIDE', 'ESC'):
        return MAX if (mode == MAX and pinned) else MIN
    return mode


def _overlap(a, b):
    return a[0] < b[0] + b[2] and b[0] < a[0] + a[2] and a[1] < b[1] + b[3] and b[1] < a[1] + a[3]


def _fit(rect, bounds):
    """Move (sem encolher além dos limites) para dentro de `bounds`."""
    x, y, w, h = rect
    bx, by, bw, bh = bounds
    w, h = min(w, bw), min(h, bh)
    x = min(max(x, bx), bx + bw - w)
    y = min(max(y, by), by + bh - h)
    return (x, y, w, h)


def _inside(rect, bounds):
    bx, by, bw, bh = bounds
    return rect[0] >= bx - 1e-6 and rect[1] >= by - 1e-6 and rect[0] + rect[2] <= bx + bw + 1e-6 \
        and rect[1] + rect[3] <= by + bh + 1e-6


def clamp_rect(rect, bounds, forbidden, scale):
    """Retângulo dentro de `bounds`, com o tamanho mínimo, fora de `forbidden`."""
    s = float(scale)
    min_w, min_h, gap = MIN_W * s, MIN_H * s, GAP * s
    x, y, w, h = rect
    rect = _fit((x, y, max(w, min_w), max(h, min_h)), bounds)
    if not any(_overlap(rect, f) for f in forbidden):
        return rect
    for _round in range(2):                 # 1ª: só mover; 2ª: mover e encolher a altura até o mínimo
        best = None
        for f in forbidden:
            x, y, w, h = rect
            candidates = [(x, f[1] - gap - h, w, h), (x, f[1] + f[3] + gap, w, h),
                          (f[0] - gap - w, y, w, h), (f[0] + f[2] + gap, y, w, h)]
            if _round:
                below = f[1] - gap - bounds[1]
                above = bounds[1] + bounds[3] - (f[1] + f[3] + gap)
                if below >= min_h:
                    candidates.append((x, bounds[1], w, min(h, below)))
                if above >= min_h:
                    candidates.append((x, f[1] + f[3] + gap, w, min(h, above)))
            for cand in candidates:
                cand = _fit(cand, bounds)
                if not _inside(cand, bounds) or any(_overlap(cand, g) for g in forbidden):
                    continue
                cost = abs(cand[0] - rect[0]) + abs(cand[1] - rect[1]) + (rect[3] - cand[3]) * 2
                if best is None or cost < best[0]:
                    best = (cost, cand)
        if best is not None:
            return best[1]
    return rect                              # sem lugar livre: fica onde dá (região menor que o HUD)


def initial_rect(bounds, scale):
    s = float(scale)
    bx, by, bw, bh = bounds
    w, h = max(MIN_W * s, bw * INITIAL_W), max(MIN_H * s, bh * INITIAL_H)
    return _fit((bx + MARGIN * s, by + bh - MARGIN * s - h, w, h), bounds)


def move(rect, dx, dy, bounds, forbidden, scale):
    x, y, w, h = rect
    return clamp_rect((x + dx, y + dy, w, h), bounds, forbidden, scale)


def resize(rect, edge, dx, dy, bounds, forbidden, scale):
    """Arrasta a borda `edge` ('LEFT', 'RIGHT', 'TOP', 'BOTTOM'); a borda oposta fica parada."""
    s = float(scale)
    min_w, min_h = MIN_W * s, MIN_H * s
    x, y, w, h = rect
    if edge == 'RIGHT':
        w = max(min_w, w + dx)
    elif edge == 'LEFT':
        right = x + w
        w = max(min_w, w - dx)
        x = right - w
    elif edge == 'TOP':
        h = max(min_h, h + dy)
    elif edge == 'BOTTOM':
        top = y + h
        h = max(min_h, h - dy)
        y = top - h
    return clamp_rect((x, y, w, h), bounds, forbidden, scale)


def region_at(rect, px, py, scale):
    """'LEFT', 'RIGHT', 'TOP', 'BOTTOM' (bordas), 'HEADER', 'BODY' ou None (fora)."""
    s = float(scale)
    x, y, w, h = rect
    if not (x <= px <= x + w and y <= py <= y + h):
        return None
    edge = EDGE * s
    if px <= x + edge:
        return 'LEFT'
    if px >= x + w - edge:
        return 'RIGHT'
    if py <= y + edge:
        return 'BOTTOM'
    if py >= y + h - edge:
        return 'TOP'
    if py >= y + h - HEADER_H * s:
        return 'HEADER'
    return 'BODY'


def grid_area(rect, scale, sidebar=True):
    """Área da grade dentro do retângulo (sem o cabeçalho, a coluna de filtros e o respiro)."""
    s = float(scale)
    x, y, w, h = rect
    left = x + PAD * s + (SIDEBAR_W * s if sidebar else 0.0)
    return (left, y + PAD * s, max(0.0, x + w - PAD * s - left), max(0.0, h - HEADER_H * s - 2 * PAD * s))


def columns(width, scale):
    s = float(scale)
    return max(1, int((width + GAP * s) // ((CELL_W + GAP) * s)))


def content_height(width, count, scale):
    s = float(scale)
    rows = -(-count // columns(width, scale)) if count else 0
    return max(0.0, rows * (CELL_H + GAP) * s - GAP * s)


def clamp_scroll(scroll, content, view):
    return min(max(0.0, float(scroll)), max(0.0, float(content) - float(view)))


def visible_cells(area, count, scale, scroll):
    """[(índice, (x, y, w, h))] das células que aparecem na área, de cima para baixo, rolada por `scroll` px."""
    s = float(scale)
    ax, ay, aw, ah = area
    cols = columns(aw, scale)
    cw, ch, gap = CELL_W * s, CELL_H * s, GAP * s
    step = ch + gap
    top = ay + ah
    cells = []
    row = int(max(0.0, scroll) // step)      # primeira linha que ainda aparece no topo
    while row * cols < count:
        y_top = top - row * step + scroll
        if y_top <= ay:                       # a linha começa abaixo da área: acabou
            break
        for col in range(cols):
            index = row * cols + col
            if index >= count:
                break
            cells.append((index, (ax + col * (cw + gap), y_top - ch, cw, ch)))
        row += 1
    return cells


def hit_cell(cells, px, py):
    for index, (x, y, w, h) in cells:
        if x <= px <= x + w and y <= py <= y + h:
            return index
    return None
