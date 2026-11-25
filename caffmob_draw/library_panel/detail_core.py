"""Detalhe do módulo na Biblioteca: fundo branco, medidas e ambiente antes de inserir.

Python puro, sem `bpy`: o desenho (`draw`), o clique (`ops_click`) e o operador de digitação (`ops_detail`) usam este
módulo. O card fica no centro da grade, em branco, com o nome do módulo, o ambiente escolhido, largura, altura e
profundidade em milímetros e o seletor de ambiente (Cozinha, Dormitório, Banheiro, Sala, Home office).

A validação compara com o Padrão de Dimensões: as medidas do módulo (`module_*_max`), as três faces de chapa
(largura × altura, largura × profundidade, altura × profundidade) contra o par máximo de chapa do fornecedor e a
espessura da lateral. Nada é criado quando a validação recusa.
"""

from collections import namedtuple

from ..data.i18n import N_, tr

AMBIENTES = (('COZ', N_("Cozinha")), ('DOR', N_("Dormitório")), ('BAN', N_("Banheiro")),
             ('SAL', N_("Sala")), ('ESC', N_("Home office")))
CAMPOS = (('width', N_("Largura (mm)")), ('height', N_("Altura (mm)")), ('depth', N_("Profundidade (mm)")))

# Fundo branco moderno do card (o painel continua escuro em volta).
FUNDO = (1.0, 1.0, 1.0, 0.98)
TINTA = (0.09, 0.10, 0.12, 1.0)
TINTA_FRACA = (0.42, 0.45, 0.50, 1.0)
CAMPO = (0.955, 0.965, 0.975, 1.0)
BORDA = (0.84, 0.86, 0.89, 1.0)
ERRO = (0.78, 0.15, 0.12, 1.0)
PAD = 18.0
CARD_H = 360.0

DetailLayout = namedtuple('DetailLayout', 'card title subtitle campos chips erro espessura ok cancelar')


def _inside(rect, px, py):
    x, y, w, h = rect
    return x <= px <= x + w and y <= py <= y + h


def layout(grid, scale):
    """Partes do card dentro da grade `grid` = (x, y, largura, altura) da região, em pixels já na escala."""
    s = float(scale)
    gx, gy, gw, gh = grid
    w = min(500.0 * s, max(300.0 * s, gw - 24.0 * s))
    h = min(CARD_H * s, max(240.0 * s, gh - 24.0 * s))
    x, y = gx + (gw - w) / 2.0, gy + (gh - h) / 2.0
    pad = PAD * s
    card = (x, y, w, h)
    top = y + h
    title = (x + pad, top - 40.0 * s, w - 2 * pad, 22.0 * s)
    subtitle = (x + pad, top - 62.0 * s, w - 2 * pad, 14.0 * s)
    inner = (x + pad, y, w - 2 * pad, h)
    campos, row_top = [], top - 108.0 * s
    for key, _label in CAMPOS:
        campos.append((key, (inner[0], row_top, inner[2], 34.0 * s)))
        row_top -= 44.0 * s
    chips, cx = [], inner[0]
    chip_w = (inner[2] - 4 * 6.0 * s) / 5.0
    chips_y = row_top + 6.0 * s
    for code, _label in AMBIENTES:
        chips.append((code, (cx, chips_y, chip_w, 24.0 * s)))
        cx += chip_w + 6.0 * s
    erro = (inner[0], y + 62.0 * s, inner[2], 30.0 * s)
    espessura = (inner[0], y + 44.0 * s, inner[2], 14.0 * s)
    ok = (x + w - pad - 100.0 * s, y + 14.0 * s, 100.0 * s, 26.0 * s)
    cancelar = (ok[0] - 8.0 * s - 100.0 * s, ok[1], 100.0 * s, 26.0 * s)
    return DetailLayout(card, title, subtitle, campos, chips, erro, espessura, ok, cancelar)


def hit(lay, px, py):
    """'FIELD:<campo>', 'LINE:<código>', 'OK', 'CANCEL', 'CARD' ou None (fora do card)."""
    if not _inside(lay.card, px, py):
        return None
    for key, rect in lay.campos:
        if _inside(rect, px, py):
            return 'FIELD:' + key
    for code, rect in lay.chips:
        if _inside(rect, px, py):
            return 'LINE:' + code
    if _inside(lay.ok, px, py):
        return 'OK'
    if _inside(lay.cancelar, px, py):
        return 'CANCEL'
    return 'CARD'


def fmt(value):
    """Medida em mm como texto curto: 800, 720.5."""
    text = "{:.1f}".format(float(value))
    return text[:-2] if text.endswith(".0") else text


def parse_mm(text):
    """Número digitado (aceita vírgula) em mm; None quando não é número."""
    try:
        value = float(str(text).strip().replace(',', '.'))
    except (TypeError, ValueError):
        return None
    return value


def ambiente_label(code):
    return dict(AMBIENTES).get(code, code)


def validate(width, height, depth, sheet, module_max, thickness):
    """(True, "") ou (False, mensagem) comparando com o Padrão de Dimensões.

    `sheet` = par ordenado (menor, maior) da chapa máxima; `module_max` = (largura, altura, profundidade) máximas do
    módulo; `thickness` = espessura da lateral em mm.
    """
    medidas = ((tr("Largura"), width, module_max[0]), (tr("Altura"), height, module_max[1]),
               (tr("Profundidade"), depth, module_max[2]))
    for nome, valor, limite in medidas:
        if valor <= 0:
            return False, tr("Informe medidas maiores que zero")
        if valor > float(limite) + 1e-6:
            return False, tr("{} acima do máximo do módulo ({} mm)").format(nome, fmt(limite))
    menor, maior = sorted((float(sheet[0]), float(sheet[1])))
    for face_w, face_h in ((width, height), (width, depth), (height, depth)):
        longo, curto = max(face_w, face_h), min(face_w, face_h)
        if longo > maior + 1e-6 or curto > menor + 1e-6:
            return False, tr("A peça de {} × {} mm excede a chapa máxima do padrão ({} × {} mm)").format(
                fmt(face_w), fmt(face_h), fmt(maior), fmt(menor))
    if thickness <= 0 or 2.0 * float(thickness) >= min(width, height, depth):
        return False, tr("A espessura de {} mm não cabe nas medidas do módulo").format(fmt(thickness))
    return True, ""
