"""Núcleo da janela do plano de corte (027, T009; RF-01). Python puro, sem `bpy`.

O resultado do otimizador (`cutting/nesting.py`, cache `btm_nesting_json_cache` da cena) guarda as peças em faixas
(`shelves`) com coordenadas absolutas em milímetros na chapa. Aqui as faixas são achatadas em retângulos, a chapa é
enquadrada numa `View2D` (milímetros entram, pixels saem) e o cursor responde qual peça está embaixo. Quem desenha é
`plan_window.py`; quem calcula ou lê o cache é `operators/ops_cutting.py`.
"""

from ..canvas2d.view import View2D
from ..data.i18n import tr
from ..data.units import format_length

MARGEM = 0.05                  # folga relativa em volta da chapa, no enquadramento


def sheets_of(payload):
    """Chapas do resultado do otimizador, na ordem em que ele as numerou."""
    return list((payload or {}).get('sheets') or [])


def placed(sheet):
    """Peças da chapa em retângulos absolutos (mm), na ordem de colocação.

    Cada retângulo leva `x`, `y`, `width`, `height` (já trocados quando a peça foi girada), o nome, o módulo dono e
    as arestas de fita, que o painel mostra ao selecionar a peça.
    """
    result = []
    for shelf in sheet.get('shelves') or []:
        for part in shelf.get('parts') or []:
            result.append({
                'x': float(part.get('x', 0.0)), 'y': float(part.get('y', 0.0)),
                'width': float(part.get('width', 0.0)), 'height': float(part.get('height', 0.0)),
                'name': part.get('name', ''), 'module': part.get('module_ref', ''),
                'part_id': str(part.get('part_id') or part.get('id') or ''),
                'rotated': bool(part.get('rotated')), 'edges': dict(part.get('edges') or {}),
            })
    return result


def bounds(sheet):
    """((0, 0), (largura, altura)) nominais da chapa, em milímetros."""
    return (0.0, 0.0), (float(sheet.get('width', 0.0)), float(sheet.get('height', 0.0)))


def fit(view, sheet, margin=MARGEM):
    """Enquadra a chapa na `view` e devolve a própria `view` (encadeável)."""
    view.fit(bounds(sheet), margin=margin)
    return view


def part_at(parts, x, y):
    """Peça sob o ponto (mm) ou None. A última colocada vence, como no desenho (ela fica por cima)."""
    found = None
    for part in parts:
        if part['x'] <= x <= part['x'] + part['width'] and part['y'] <= y <= part['y'] + part['height']:
            found = part
    return found


def used_area(sheet):
    """Área ocupada pelas peças, em mm²."""
    return sum(part['width'] * part['height'] for part in placed(sheet))


def utilization(sheet):
    """Aproveitamento da chapa em % (área das peças sobre a área nominal), arredondado a 1 decimal."""
    width, height = float(sheet.get('width', 0.0)), float(sheet.get('height', 0.0))
    if width <= 0.0 or height <= 0.0:
        return 0.0
    return round(used_area(sheet) / (width * height) * 100.0, 1)


def summary(sheet):
    """Números do cabeçalho e do painel: peças, área aproveitada e aproveitamento."""
    parts = placed(sheet)
    return {
        'parts': len(parts),
        'used_area_m2': round(used_area(sheet) / 1_000_000.0, 3),
        'utilization': utilization(sheet),
        'sheets_count': len(sheet.get('shelves') or []),
    }


def sheet_title(sheet, index, total):
    """Rótulo da chapa no cabeçalho: `Chapa 2/5 · MDF Branco 18 mm`."""
    material = sheet.get('material') or tr("Material não informado")
    thickness = format_length(float(sheet.get('thickness', 0.0)) / 1000.0, 'MM')
    return tr("Chapa {}/{} · {} {}").format(index + 1, total, material, thickness)


def part_size_label(part):
    """Medidas da peça como saem no plano: `560 × 720 mm`."""
    width = format_length(part['width'] / 1000.0, 'MM', with_suffix=False)
    height = format_length(part['height'] / 1000.0, 'MM', with_suffix=False)
    return tr("{} × {} mm").format(width, height)


def part_title(part):
    """Nome da peça com o módulo dono, para o painel e o balão de hover."""
    if part.get('module'):
        return tr("{} › {}").format(part['module'], part['name'])
    return part.get('name') or tr("Peça sem nome")


def sheet_view(rect, sheet, margin=MARGEM):
    """`View2D` em milímetros já enquadrada na chapa para o retângulo de desenho em pixels."""
    return fit(View2D(rect, scale=1.0), sheet, margin=margin)
