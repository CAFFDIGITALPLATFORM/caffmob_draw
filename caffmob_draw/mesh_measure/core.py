"""Núcleo da janela V-Ray Mesh Measure (027, T010 a T014; RF-02). Python puro, sem `bpy`.

Reúne o que não precisa do Blender para ser conferido: as partes soltas da malha (componentes conexos das arestas), as
medidas de cada parte, o encaixe (snap) nas extremidades, a formatação das unidades, as medidas manuais e o leiaute das
folhas de impressão. Quem lê a malha é `scene.py`, quem desenha é `draw.py` e quem trata da janela é `window.py`.
"""

import math

UNITS = ('MM', 'CM', 'M')
REPRESENTATIONS = ('ARAMADO', 'LINHAS_OCULTAS', 'SOLIDO', 'RAIO_X', 'MATERIAL')
PROJECTIONS = ('PERSP', 'ORTHO')
SNAP_MODES = ('OFF', 'OBJETO', 'PARTES', 'AMBOS')

# Folhas de impressão em milímetros (retrato ou paisagem como o nome diz).
SHEETS = {
    'A4_RETRATO': (210.0, 297.0),
    'A4_PAISAGEM': (297.0, 210.0),
    'A3_PAISAGEM': (420.0, 297.0),
    'CARTA': (279.4, 215.9),
}
PROPORTIONS = {'LIVRE': None, '1:1': 1.0, '4:3': 4.0 / 3.0, '3:4': 3.0 / 4.0, '16:9': 16.0 / 9.0}

# Precisão da unidade: "absoluta" mostra 0,1 mm; "arredondada" corta as casas que não se lê no canteiro.
PRECISION_EXACT = {'MM': 1, 'CM': 2, 'M': 3}
PRECISION_ROUNDED = {'MM': 0, 'CM': 1, 'M': 2}


# Partes soltas ----------------------------------------------------------------------------------------------------

def connected_parts(vertex_count, edges):
    """Partes soltas da malha: componentes conexos do grafo de vértices e arestas.

    Devolve uma lista de listas de índices de vértice, cada uma ordenada, e a lista ordenada pelo primeiro vértice (a
    ordem é estável entre leituras, então a cor e o nome de cada parte não trocam de lugar).
    """
    pai = list(range(vertex_count))

    def raiz(i):
        while pai[i] != i:
            pai[i] = pai[pai[i]]
            i = pai[i]
        return i

    for a, b in edges:
        ra = raiz(a)
        rb = raiz(b)
        if ra != rb:
            pai[rb] = ra
    grupos = {}
    for i in range(vertex_count):
        grupos.setdefault(raiz(i), []).append(i)
    partes = [sorted(g) for g in grupos.values() if g]
    partes.sort(key=lambda g: g[0])
    return partes


def bounds(points):
    """((xmin, ymin, zmin), (xmax, ymax, zmax)) dos pontos; caixa degenerada na origem quando não há ponto."""
    xs = [p[0] for p in points]
    ys = [p[1] for p in points]
    zs = [p[2] for p in points]
    if not xs:
        return (0.0, 0.0, 0.0), (0.0, 0.0, 0.0)
    return (min(xs), min(ys), min(zs)), (max(xs), max(ys), max(zs))


def size_mm(lo, hi):
    """As três medidas da caixa em milímetros, na ordem dos eixos."""
    return (round((hi[0] - lo[0]) * 1000.0, 3), round((hi[1] - lo[1]) * 1000.0, 3),
            round((hi[2] - lo[2]) * 1000.0, 3))


def center(lo, hi):
    return ((lo[0] + hi[0]) / 2.0, (lo[1] + hi[1]) / 2.0, (lo[2] + hi[2]) / 2.0)


def measure(a, b):
    """Medida entre dois pontos (metros): distância e as três componentes, em milímetros."""
    dx, dy, dz = (b[0] - a[0]) * 1000.0, (b[1] - a[1]) * 1000.0, (b[2] - a[2]) * 1000.0
    return {'distance_mm': math.sqrt(dx * dx + dy * dy + dz * dz),
            'dx_mm': dx, 'dy_mm': dy, 'dz_mm': dz}


# Unidades ---------------------------------------------------------------------------------------------------------

def format_measure(meters, unit='MM', rounded=False, suffix=True):
    """Medida em metros na unidade pedida. `rounded` corta as casas decimais (1 mm / 0,1 cm / 0,01 m)."""
    from ..data.units import format_length
    unit = unit if unit in PRECISION_EXACT else 'MM'
    precision = (PRECISION_ROUNDED if rounded else PRECISION_EXACT)[unit]
    return format_length(meters, unit, precision=precision, with_suffix=suffix)


def format_mm(milimetros, unit='MM', rounded=False, suffix=True):
    """O mesmo, para quem já tem a medida em milímetros."""
    return format_measure(float(milimetros) / 1000.0, unit=unit, rounded=rounded, suffix=suffix)


def measure_label(result, unit='MM', rounded=False):
    """Rótulo de uma medida manual: a distância em destaque e as componentes."""
    principal = format_mm(result['distance_mm'], unit=unit, rounded=rounded)
    partes = [format_mm(result[key], unit=unit, rounded=rounded) for key in ('dx_mm', 'dy_mm', 'dz_mm')]
    return f"{principal}  ({' × '.join(partes)})"


# Encaixe nas extremidades -----------------------------------------------------------------------------------------

def box_corners(lo, hi):
    """Os oito cantos da caixa."""
    return [(x, y, z) for x in (lo[0], hi[0]) for y in (lo[1], hi[1]) for z in (lo[2], hi[2])]


def snap_candidates(bounds_object, parts_bounds, mode='AMBOS'):
    """Pontos de encaixe: os cantos do objeto e/ou os cantos de cada parte solta, conforme o modo."""
    pontos = []
    if mode in ('OBJETO', 'AMBOS'):
        pontos += box_corners(*bounds_object)
    if mode in ('PARTES', 'AMBOS'):
        for lo, hi in parts_bounds:
            pontos += box_corners(lo, hi)
    return pontos


def snap(point, candidates, threshold):
    """O candidato mais próximo dentro do limite (metros), ou o próprio ponto. Devolve (ponto, encaixou)."""
    melhor, dist = None, float(threshold)
    for candidate in candidates:
        d = math.dist(point, candidate)
        if d <= dist:
            melhor, dist = candidate, d
    return (melhor, True) if melhor is not None else (tuple(point), False)


# Impressão --------------------------------------------------------------------------------------------------------

def sheet_size(key):
    return SHEETS.get(key, SHEETS['A3_PAISAGEM'])


def _fit_proportion(width, height, ratio):
    """Maior retângulo com a proporção pedida dentro de `width` × `height` (LIVRE fica como está)."""
    if not ratio or width <= 0 or height <= 0:
        return width, height
    if width / height > ratio:
        return height * ratio, height
    return width, width / ratio


def print_layout(sheet_key, views, margin_mm=10.0, gap_mm=6.0):
    """Retângulos das views na folha, em milímetros, a partir do canto inferior esquerdo.

    As views se distribuem numa grade de colunas iguais (a raiz quadrada arredondada para cima); cada uma ocupa a
    célula inteira e é reduzida pelo próprio `size_pct` e pela `proportion`, ficando centrada na célula.
    """
    sheet_width, sheet_height = sheet_size(sheet_key)
    count = max(1, len(views))
    cols = max(1, math.ceil(math.sqrt(count)))
    rows = max(1, math.ceil(count / cols))
    inner_width = sheet_width - 2.0 * margin_mm
    inner_height = sheet_height - 2.0 * margin_mm
    cell_w = (inner_width - gap_mm * (cols - 1)) / cols
    cell_h = (inner_height - gap_mm * (rows - 1)) / rows
    result = []
    for index, view in enumerate(views):
        row, col = divmod(index, cols)
        cell_x = margin_mm + col * (cell_w + gap_mm)
        cell_y = sheet_height - margin_mm - (row + 1) * cell_h - row * gap_mm
        scale = max(0.1, min(1.0, float(view.get('size_pct', 100)) / 100.0))
        width, height = _fit_proportion(cell_w * scale, cell_h * scale,
                                        PROPORTIONS.get(view.get('proportion', 'LIVRE')))
        result.append({
            'view': view,
            'rect_mm': (cell_x + (cell_w - width) / 2.0, cell_y + (cell_h - height) / 2.0, width, height),
        })
    return {'sheet_mm': (sheet_width, sheet_height), 'views': result}


def view_name(index):
    """Badge da view: V1, V2, ..."""
    return f"V{index + 1}"
