"""Desenho da janela V-Ray Mesh Measure (027, T011 a T014; RF-02).

Tudo aqui roda dentro do handler `POST_PIXEL` da janela: nada escreve na cena. A malha é projetada pela `Camera`
(`camera.py`) e desenhada em `UNIFORM_COLOR`, com as cinco representações pedidas:

- **Aramado**: só as arestas dos triângulos;
- **Linhas Ocultas**: as faces pintadas na cor do papel, de trás para a frente, e depois só o contorno das faces
  voltadas para a câmera — é o que esconde as arestas que estão atrás;
- **Sólido**: as faces pintadas com a cor sólida de cada parte, sombreadas;
- **Raio-X**: as faces translúcidas, com as arestas por cima;
- **Material**: as faces com a cor do material do objeto.

Por cima vão as medidas de cada parte solta, as medidas manuais e, na impressão, a folha com as views e o badge de cada
uma. O desenho não altera a malha do usuário: sem decimar, sem mexer em modificadores.
"""

import math

from gpu_extras.batch import batch_for_shader  # type: ignore

from ..canvas2d import draw
from ..data.i18n import tr
from . import core
from . import scene as scene_mod

TOPO = 30                       # faixa do cabeçalho, em pixels
RODAPE = 26                     # faixa do rodapé
LIGHT = (0.35, -0.45, 0.82)     # luz fixa do sombreado (não é a luz da cena: é leitura, não renderização)

COR = {
    'fundo': (0.09, 0.10, 0.12, 1.0),
    'faixa': (0.13, 0.14, 0.16, 1.0),
    'papel': (0.97, 0.97, 0.96, 1.0),
    'filme': (0.11, 0.12, 0.14, 1.0),
    'tinta': (0.10, 0.11, 0.13, 1.0),
    'aresta': (0.08, 0.09, 0.11, 1.0),
    'aresta_clara': (0.85, 0.87, 0.90, 1.0),
    'texto': (0.93, 0.93, 0.93, 1.0),
    'mudo': (0.62, 0.63, 0.66, 1.0),
    'hover': (1.0, 0.76, 0.20, 1.0),
    'selecionado': (0.35, 0.85, 1.0, 1.0),
    'medida': (0.99, 0.55, 0.20, 1.0),
    'badge': (0.11, 0.12, 0.14, 0.92),
}


def _shade(color, normal, levels=4):
    """Cor da face com luz fixa, em degraus (menos lotes de desenho, mesmo relevo)."""
    light = math.sqrt(sum(component * component for component in LIGHT))
    factor = abs(sum(normal[i] * LIGHT[i] / light for i in range(3)))
    factor = 0.45 + 0.55 * factor
    step = round(factor * levels) / levels
    return (min(1.0, color[0] * step), min(1.0, color[1] * step), min(1.0, color[2] * step), color[3])


def _normal(a, b, c):
    ux, uy, uz = b[0] - a[0], b[1] - a[1], b[2] - a[2]
    vx, vy, vz = c[0] - a[0], c[1] - a[1], c[2] - a[2]
    nx, ny, nz = uy * vz - uz * vy, uz * vx - ux * vz, ux * vy - uy * vx
    length = math.sqrt(nx * nx + ny * ny + nz * nz)
    return (nx / length, ny / length, nz / length) if length > 1e-12 else (0.0, 0.0, 1.0)


def _triangles(s, camera, rect):
    """Triângulos visíveis projetados, do mais distante para o mais próximo.

    Cada item é `(pontos na tela, profundidade, parte, cor do material, normal, centro no mundo)`.
    """
    projected = camera.project_all(s.malha.vertices, rect)
    out = []
    for a, b, c, part_index, material in s.malha.triangles:
        part = s.malha.part(part_index)
        if part is None or not part.visible:
            continue
        pa, pb, pc = projected[a], projected[b], projected[c]
        if pa is None or pb is None or pc is None:
            continue
        vertices = (s.malha.vertices[a], s.malha.vertices[b], s.malha.vertices[c])
        centroid = tuple(sum(v[i] for v in vertices) / 3.0 for i in range(3))
        out.append(([(pa[0], pa[1]), (pb[0], pb[1]), (pc[0], pc[1])], (pa[2] + pb[2] + pc[2]) / 3.0,
                    part, material, _normal(*vertices), centroid))
    out.sort(key=lambda item: item[1], reverse=True)
    return out


def _fill(sh, triangles, color_of):
    """Desenha os triângulos agrupados por cor (um lote por cor)."""
    batches = {}
    for points, _depth, part, material, normal, _centroid in triangles:
        color = color_of(part, material, normal)
        batches.setdefault(color, []).extend(points)
    for color, positions in batches.items():
        sh.uniform_float("color", color)
        batch_for_shader(sh, 'TRIS', {'pos': positions}).draw(sh)


def _edges(sh, triangles, color):
    points = []
    for (a, b, c), _depth, _part, _material, _normal_, _centroid in triangles:
        points += [a, b, b, c, c, a]
    draw.lines(sh, points, color)


def _front_facing(triangles, camera):
    """Triângulos voltados para a câmera (a normal aponta para o olho)."""
    eye = camera.eye()
    out = []
    for points, depth, part, material, normal, centroid in triangles:
        to_eye = (eye[0] - centroid[0], eye[1] - centroid[1], eye[2] - centroid[2])
        if normal[0] * to_eye[0] + normal[1] * to_eye[1] + normal[2] * to_eye[2] >= 0.0:
            out.append((points, depth, part, material, normal, centroid))
    return out


def draw_mesh(sh, s, camera, rect, labels=True, measures=True, background=None):
    """Desenha a malha na representação escolhida dentro de `rect` (pixels)."""
    body = (float(rect[0]), float(rect[1]), float(rect[2]), float(rect[3]))
    draw.rect(sh, body, background or COR['filme'])
    triangles = _triangles(s, camera, body)
    representation = s.representation
    if representation == 'ARAMADO':
        _edges(sh, triangles, COR['aresta_clara'])
    elif representation == 'LINHAS_OCULTAS':
        draw.rect(sh, body, COR['papel'])
        _edges(sh, triangles, COR['tinta'])
        _fill(sh, triangles, lambda part, material, normal: COR['papel'])
        _edges(sh, _front_facing(triangles, camera), COR['tinta'])
    elif representation == 'RAIO_X':
        _fill(sh, triangles, lambda part, material, normal: tuple(part.color[:3]) + (0.22,))
        _edges(sh, triangles, COR['aresta_clara'])
    elif representation == 'MATERIAL':
        _fill(sh, triangles, lambda part, material, normal: _shade(material, normal))
        _edges(sh, _front_facing(triangles, camera), COR['aresta'])
    else:                                                   # SÓLIDO
        _fill(sh, triangles, lambda part, material, normal: _shade(part.color, normal))
        _edges(sh, _front_facing(triangles, camera), COR['aresta'])
    if labels:
        _part_labels(sh, s, camera, body)
    if measures:
        _manual_measures(sh, s, camera, body)


def _part_labels(sh, s, camera, rect):
    """Medidas de cada parte visível: os três eixos no centro da caixa."""
    for part in s.visible_parts():
        point = camera.project(part.center, rect)
        if point is None:
            continue
        x, y = point[0], point[1]
        if not (rect[0] <= x <= rect[0] + rect[2] and rect[1] <= y <= rect[1] + rect[3]):
            continue
        text = " × ".join(core.format_mm(value, s.unit, s.rounded, suffix=False) for value in part.size_mm)
        label = f"{text} {s.unit.lower()}"
        width = draw.text_width(label, 10) + 10
        draw.rounded_rect(sh, (x - width / 2.0, y - 7, width, 14), 4.0, COR['badge'])
        draw.text(x - width / 2.0 + 5, y - 4, label, COR['texto'], size=10)
        if part is s.selected:
            draw.outline(sh, (x - width / 2.0 - 1, y - 8, width + 2, 16), COR['selecionado'])


def _manual_measures(sh, s, camera, rect):
    """Medidas manuais: linha entre as extremidades, com traços e o valor em pílula."""
    for item in s.medidas:
        a = camera.project(item['a'], rect)
        b = camera.project(item['b'], rect)
        if a is None or b is None:
            continue
        draw.lines(sh, [(a[0], a[1]), (b[0], b[1])], COR['medida'])
        for point in (a, b):
            draw.circle(sh, (point[0], point[1]), 3.0, COR['medida'])
        draw.pill(sh, (a[0] + b[0]) / 2.0, (a[1] + b[1]) / 2.0, item['label'], COR['medida'], COR['tinta'], size=10)
    if s.pending is not None:
        point = camera.project(s.pending, rect)
        if point is not None:
            draw.circle(sh, (point[0], point[1]), 4.0, COR['medida'], outline_color=COR['texto'])


def draw_print(sh, s, region):
    """Folha de impressão: o papel, as views com o badge e o carimbo com o nome do objeto."""
    draw.rect(sh, (0, 0, region.width, region.height), COR['fundo'])
    layout = s.layout()
    sheet_w, sheet_h = layout['sheet_mm']
    avail_w = region.width - 40
    avail_h = region.height - TOPO - RODAPE - 20
    scale = min(avail_w / sheet_w, avail_h / sheet_h) * s.sheet_zoom
    page_w, page_h = sheet_w * scale, sheet_h * scale
    page_x = (region.width - page_w) / 2.0
    page_y = RODAPE + (region.height - TOPO - RODAPE - page_h) / 2.0
    draw.rect(sh, (page_x, page_y, page_w, page_h), COR['papel'])
    draw.outline(sh, (page_x, page_y, page_w, page_h), COR['tinta'])
    for entry in layout['views']:
        x, y, w, h = entry['rect_mm']
        rect = (page_x + x * scale, page_y + y * scale, w * scale, h * scale)
        draw.outline(sh, rect, COR['mudo'])
        camera = s.view_camera(entry['view'])
        draw_mesh(sh, s, camera, rect, labels=False, measures=False, background=COR['papel'])
        draw.outline(sh, rect, COR['tinta'])
        draw.pill(sh, rect[0] + 18, rect[1] + rect[3] - 12, entry['view']['name'], COR['badge'], COR['texto'], size=10)
    carimbo = tr("{} · {} · {} parte(s)").format(s.malha.name, s.sheet.lower(), len(s.malha.parts))
    draw.text(page_x + 8, page_y + 6, carimbo, COR['tinta'], size=10)
    if not layout['views']:
        draw.text(page_x + 12, page_y + page_h / 2.0, tr("Crie uma view para montar a folha."), COR['tinta'], size=11)


def draw_window(context):
    """Desenho completo da janela (handler POST_PIXEL)."""
    s = scene_mod.sessao()
    region = context.region
    if s is None or region is None or region.width < 40 or region.height < 40:
        return
    sh = draw.begin()
    draw.rect(sh, (0, 0, region.width, region.height), COR['fundo'])
    draw.rect(sh, (0, region.height - TOPO, region.width, TOPO), COR['faixa'])
    titulo = tr("◎ {} · {} parte(s) · {} triângulo(s)").format(
        s.malha.name, len(s.malha.parts), s.malha.triangle_count())
    draw.text(12, region.height - TOPO + 9, titulo, COR['texto'], size=12)
    estado = tr("{} · {} · {}").format(s.representation.lower(), s.camera.projection.lower(), s.unit.lower())
    if s.print_preview:
        estado = tr("impressão · {}").format(s.sheet.lower())
    draw.text(region.width - draw.text_width(estado, 11) - 12, region.height - TOPO + 10, estado, COR['mudo'])

    if s.print_preview:
        draw_print(sh, s, region)
    else:
        rect = (0.0, float(RODAPE), float(region.width), float(region.height - TOPO - RODAPE))
        s.rect = rect
        if not s.fitted:
            s.camera.fit(s.malha.bounds, rect)
            s.fitted = True
        draw_mesh(sh, s, s.camera, rect, labels=s.mostrar_medidas)

    draw.rect(sh, (0, 0, region.width, RODAPE), COR['faixa'])
    if s.print_preview:
        dica = tr("P: voltar ao modelo  ·  Esc: fechar")
    else:
        dica = tr("arraste: orbitar  ·  Shift+arraste: mover  ·  roda: zoom  ·  clique: parte  ·  "
                  "Ctrl+clique: medida  ·  Esc: fechar")
    draw.text(12, 8, dica, COR['mudo'], size=10)
    draw.end()
