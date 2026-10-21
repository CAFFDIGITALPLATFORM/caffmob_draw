"""Layout em milímetros no plano da face e plano incremental, sem dependência do Blender."""

from dataclasses import asdict, dataclass
import hashlib
import json
import math


@dataclass(frozen=True)
class Params:
    kind: str = 'BOARDS'
    width_mm: float = 150.0
    thickness_mm: float = 15.0
    joint_mm: float = 3.0
    min_gap_mm: float = 18.0
    orientation: str = 'HORIZONTAL'
    angle: float = 45.0
    band: str = 'FULL'
    band_from: str = 'START'
    band_mm: float = 1600.0
    sheet_w_mm: float = 2730.0
    sheet_h_mm: float = 1810.0
    backing: bool = False
    sheet_t_mm: float = 15.0

    def validate(self):
        for name, value in asdict(self).items():
            if isinstance(value, (float, int)) and not math.isfinite(value):
                raise ValueError('Medida não finita: ' + name)
        if self.kind not in {'BOARDS', 'SLATS', 'PANEL', 'PLATES'}:
            raise ValueError('Tipo de revestimento inválido')
        if self.orientation not in {'HORIZONTAL', 'VERTICAL', 'ANGLED'}:
            raise ValueError('Orientação inválida')
        if self.band not in {'FULL', 'PARTIAL'} or self.band_from not in {'START', 'END'}:
            raise ValueError('Faixa inválida')
        if min(self.width_mm, self.thickness_mm, self.sheet_w_mm, self.sheet_h_mm,
               self.sheet_t_mm, self.band_mm) <= 0 or min(self.joint_mm, self.min_gap_mm) < 0:
            raise ValueError('Medidas devem ser positivas e a junta não pode ser negativa')
        if self.kind == 'SLATS' and self.joint_mm < self.min_gap_mm:
            raise ValueError('Vão livre abaixo do mínimo do preset')
        return self


@dataclass(frozen=True)
class Piece:
    key: str
    polygon: tuple
    thickness_mm: float
    role: str = 'FACE'


def digest(value):
    encoded = json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False).encode()
    return hashlib.sha256(encoded).hexdigest()


def area(poly):
    return abs(sum(a[0] * b[1] - b[0] * a[1] for a, b in zip(poly, poly[1:] + poly[:1]))) / 2


def clip(poly, axis, value, keep_greater):
    """Recorte de polígono convexo por semiplano, preservando a ordem do contorno."""
    result = []
    for a, b in zip(poly, poly[1:] + poly[:1]):
        da, db = a[axis] - value, b[axis] - value
        inside_a = da >= -1e-8 if keep_greater else da <= 1e-8
        inside_b = db >= -1e-8 if keep_greater else db <= 1e-8
        if inside_a:
            result.append(a)
        if inside_a != inside_b:
            t = da / (da - db)
            result.append(tuple(a[k] + t * (b[k] - a[k]) for k in (0, 1)))
    # Retirar vértices coincidentes vindos de corte exatamente na borda.
    clean = []
    for point in result:
        if not clean or math.dist(point, clean[-1]) > 1e-7:
            clean.append(point)
    if len(clean) > 1 and math.dist(clean[0], clean[-1]) < 1e-7:
        clean.pop()
    return tuple(clean) if len(clean) >= 3 else ()


def rectangle_clip(poly, bounds):
    x0, y0, x1, y1 = bounds
    for axis, value, greater in ((0, x0, True), (0, x1, False), (1, y0, True), (1, y1, False)):
        poly = clip(poly, axis, value, greater)
    return poly


def rotation(params):
    degrees = {'HORIZONTAL': 0, 'VERTICAL': 90, 'ANGLED': params.angle}[params.orientation]
    return math.radians(degrees)


def rotate(poly, angle):
    c, s = math.cos(angle), math.sin(angle)
    return tuple((c * x - s * y, s * x + c * y) for x, y in poly)


def layout(outline, params=Params()):
    """Células recortadas ao contorno convexo, sem ampliar faixa para fechar modulação.

    O contorno externo não contém furos: estes são tratados na região avaliada pelo gerador. A origem da grade é
    fixa no controlador; alterar um vão não muda as chaves das células externas a ele.
    """
    params.validate()
    outline = tuple(tuple(map(float, p)) for p in outline)
    if len(outline) < 3 or area(outline) < 1:
        raise ValueError('Região vazia ou menor que 1 mm²')
    if not all(math.isfinite(v) for p in outline for v in p):
        raise ValueError('Contorno não finito')
    if params.band == 'PARTIAL':
        start, end = min(x for x, _y in outline), max(x for x, _y in outline)
        boundary = start + params.band_mm if params.band_from == 'START' else end - params.band_mm
        outline = clip(outline, 0, boundary, params.band_from == 'END')
    angle = rotation(params)
    poly = rotate(outline, -angle)
    if not poly:
        return ()
    x0, x1 = min(x for x, _y in poly), max(x for x, _y in poly)
    y0, y1 = min(y for _x, y in poly), max(y for _x, y in poly)
    strips = params.kind in {'BOARDS', 'SLATS'}
    height = min(params.width_mm, params.sheet_h_mm) if strips else params.sheet_h_mm
    pitch_y = height + params.joint_mm
    pitch_x = params.sheet_w_mm + params.joint_mm
    result = []
    for row in range(math.floor(y0 / pitch_y), math.ceil(y1 / pitch_y)):
        for col in range(math.floor(x0 / pitch_x), math.ceil(x1 / pitch_x)):
            cut = rectangle_clip(poly, (col * pitch_x, row * pitch_y,
                                        col * pitch_x + params.sheet_w_mm, row * pitch_y + height))
            if cut and area(cut) >= 1:
                result.append(Piece(f'FACE:{row}:{col}', rotate(cut, angle), params.thickness_mm))
    if params.backing and params.kind == 'SLATS':
        from dataclasses import replace
        back = replace(params, kind='PANEL', backing=False, joint_mm=0, thickness_mm=params.sheet_t_mm)
        result.extend(Piece(p.key.replace('FACE:', 'BACKING:'), p.polygon, p.thickness_mm, 'BACKING')
                      for p in layout(outline, back))
    return tuple(result)


@dataclass(frozen=True)
class SyncPlan:
    create: tuple = ()
    update: tuple = ()
    remove: tuple = ()


def sync_plan(owner, desired, existing, previous_hash='', params_hash=''):
    """`desired`: chave → assinatura; `existing`: (id, marca, assinatura). RN-15 antes de qualquer decisão.

    IDs são opacos. Duplicatas geradas são removidas, mas uma marca manual nunca autoriza remoção nem atualização.
    """
    if params_hash and previous_hash == params_hash:
        return SyncPlan()
    found, remove, update = {}, [], []
    for ident, mark, signature in existing:
        if not mark or mark.get('owner') != owner or not mark.get('generated', False):
            continue
        key = mark.get('key')
        if key not in desired or key in found:
            remove.append(ident)
        else:
            found[key] = ident
            if signature != desired[key]:
                update.append((ident, key))
    return SyncPlan(tuple(k for k in desired if k not in found), tuple(update), tuple(remove))


def intersection(poly, boundary):
    """Interseção convexa por semiplanos; usada para assinatura antes de alocar malha no Blender."""
    for a, b in zip(boundary, boundary[1:] + boundary[:1]):
        result = []
        dx, dy = b[0] - a[0], b[1] - a[1]
        for p, q in zip(poly, poly[1:] + poly[:1]):
            dp = dx * (p[1] - a[1]) - dy * (p[0] - a[0])
            dq = dx * (q[1] - a[1]) - dy * (q[0] - a[0])
            if dp >= -1e-6:
                result.append(p)
            if (dp >= -1e-6) != (dq >= -1e-6):
                t = dp / (dp - dq)
                result.append(tuple(p[k] + t * (q[k] - p[k]) for k in (0, 1)))
        poly = tuple(result)
        if len(poly) < 3:
            return ()
    return poly if area(poly) >= 1 else ()


def boundary_signature(polygons):
    """Contorno sem arestas internas e sem vértices colineares: independe da triangulação do Boolean.

    Divide arestas em T antes de cancelar pares. Tolerância de 0,0001 mm, menor que a precisão de aceite.
    """
    polygons = [tuple((round(x, 4), round(y, 4)) for x, y in p) for p in polygons]
    points = set(p for poly in polygons for p in poly)
    edges = {}
    for poly in polygons:
        for a, b in zip(poly, poly[1:] + poly[:1]):
            dx, dy = b[0] - a[0], b[1] - a[1]
            length2 = dx*dx + dy*dy
            if length2 < 1e-8:
                continue
            split = [(0, a), (1, b)]
            for p in points - {a, b}:
                t = ((p[0]-a[0])*dx + (p[1]-a[1])*dy) / length2
                if 0 < t < 1 and abs(dx*(p[1]-a[1]) - dy*(p[0]-a[0])) < .001 * math.sqrt(length2):
                    split.append((t, p))
            split.sort()
            for (_ta, pa), (_tb, pb) in zip(split, split[1:]):
                key = tuple(sorted((pa, pb)))
                edges[key] = edges.get(key, 0) + 1
    boundary = {edge for edge, count in edges.items() if count % 2}
    # Fundir segmentos colineares de grau 2. Funciona também com furos e ilhas desconectadas.
    changed = True
    while changed:
        changed = False
        adjacent = {}
        for a, b in boundary:
            adjacent.setdefault(a, []).append(b)
            adjacent.setdefault(b, []).append(a)
        for p, neighbors in adjacent.items():
            if len(neighbors) != 2:
                continue
            a, b = neighbors
            cross = (a[0]-p[0])*(b[1]-p[1]) - (a[1]-p[1])*(b[0]-p[0])
            if abs(cross) > .001 * max(math.dist(a, b), 1):
                continue
            boundary.remove(tuple(sorted((a, p))))
            boundary.remove(tuple(sorted((b, p))))
            boundary.add(tuple(sorted((a, b))))
            changed = True
            break
    return tuple(sorted(boundary))
