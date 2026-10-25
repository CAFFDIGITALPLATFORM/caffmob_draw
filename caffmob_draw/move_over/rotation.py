"""Núcleo puro da rotação do Mover Sobre (feature 067, T080; D-24; RF-121 a RF-125). Sem `bpy` nem `mathutils`.

- Orientação por quaternion (w, x, y, z) no referencial de B; girar em torno do pivô P pelo eixo N:
  `M = T(P)·R(N,θ)·T(−P)·M0`, o que deixa P parado (90° e depois 180° mantêm o pivô).
- O pivô e a âncora são pontos locais de A (cantos e centro da caixa local), não cantos da caixa alinhada ao mundo:
  escolher outro ponto não move nada.
- Ângulo do arraste por `atan2` no plano da vista, com desdobramento (sem salto ao cruzar ±180°) e sem NaN com o
  mouse em cima do pivô (raio quase nulo: o ângulo fica o anterior).
- Coordenadas relativas `r = Rb⁻¹(world(pA) − world(pB))` ou absolutas do mesmo pA: trocar de modo não move.
"""

import math

IDENTITY = (1.0, 0.0, 0.0, 0.0)
AXES = {'X': (1.0, 0.0, 0.0), 'Y': (0.0, 1.0, 0.0), 'Z': (0.0, 0.0, 1.0)}
VIEW_AXIS = {'plan': 'Z', 'front': 'Y'}          # a planta gira em torno do vertical; a frontal, do eixo de profundidade
SNAP_DEG = 15.0
MIN_RADIUS = 1e-6

# Pontos locais escolhíveis: o centro, o centro da base e os oito cantos (índices de mín./máx. por eixo).
CORNERS = tuple((ix, iy, iz) for iz in (0, 1) for iy in (0, 1) for ix in (0, 1))
POINT_KEYS = ('CENTER', 'BASE_CENTER') + tuple(f"C{ix}{iy}{iz}" for ix, iy, iz in CORNERS)


def axis_angle(axis, degrees):
    x, y, z = axis
    n = math.sqrt(x * x + y * y + z * z) or 1.0
    half = math.radians(degrees) / 2.0
    s = math.sin(half) / n
    return (math.cos(half), x * s, y * s, z * s)


def multiply(a, b):
    aw, ax, ay, az = a
    bw, bx, by, bz = b
    return (aw * bw - ax * bx - ay * by - az * bz, aw * bx + ax * bw + ay * bz - az * by,
            aw * by - ax * bz + ay * bw + az * bx, aw * bz + ax * by - ay * bx + az * bw)


def normalize(q):
    n = math.sqrt(sum(v * v for v in q)) or 1.0
    q = tuple(v / n for v in q)
    return q if q[0] >= 0.0 else tuple(-v for v in q)


def rotate_vector(q, v):
    w, x, y, z = q
    vx, vy, vz = v
    # v' = q v q*
    tx = 2.0 * (y * vz - z * vy)
    ty = 2.0 * (z * vx - x * vz)
    tz = 2.0 * (x * vy - y * vx)
    return (vx + w * tx + (y * tz - z * ty), vy + w * ty + (z * tx - x * tz), vz + w * tz + (x * ty - y * tx))


def add(a, b):
    return tuple(a[i] + b[i] for i in range(3))


def sub(a, b):
    return tuple(a[i] - b[i] for i in range(3))


def local_point(box, key):
    """Ponto local de A pela chave (box = (lo, hi) na caixa local de A)."""
    lo, hi = box
    if key == 'CENTER':
        return tuple((lo[i] + hi[i]) / 2.0 for i in range(3))
    if key == 'BASE_CENTER':
        return ((lo[0] + hi[0]) / 2.0, (lo[1] + hi[1]) / 2.0, lo[2])
    if key.startswith('C') and len(key) == 4:
        return tuple((lo, hi)[int(key[1 + i])][i] for i in range(3))
    raise ValueError(f"ponto local desconhecido: {key}")


def world_point(origin, orientation, point):
    """Ponto local de A no referencial de B, para a origem e a orientação dadas."""
    return add(origin, rotate_vector(orientation, point))


def rotate_about(origin, orientation, pivot_local, axis, degrees):
    """`T(P)·R(N,θ)·T(−P)·M0`: (origem, orientação) novas depois de girar `degrees` em torno do pivô."""
    q = axis_angle(axis, degrees)
    pivot = world_point(origin, orientation, pivot_local)
    new_origin = add(pivot, rotate_vector(q, sub(origin, pivot)))
    return new_origin, normalize(multiply(q, orientation))


def signed_angle(center, point, previous=0.0):
    """Ângulo (graus) do ponto em torno do centro no plano da vista; raio quase nulo devolve `previous`."""
    dx, dy = point[0] - center[0], point[1] - center[1]
    if dx * dx + dy * dy < MIN_RADIUS * MIN_RADIUS:
        return previous
    return math.degrees(math.atan2(dy, dx))


def unwrap(previous, current):
    """Ângulo contínuo: `current` (em −180..180) ajustado para ficar a menos de 180° de `previous`."""
    delta = (current - previous + 180.0) % 360.0 - 180.0
    return previous + delta


def snap(degrees, step=SNAP_DEG, fine=False):
    """Snap angular (15° por padrão); com precisão fina, décimo de grau."""
    if fine:
        return round(degrees, 1)
    return round(degrees / step) * step


def relative(world_a, world_b, b_rotation_inverse):
    """`r = Rb⁻¹(world(pA) − world(pB))` (b_rotation_inverse é o quaternion inverso de B)."""
    return rotate_vector(b_rotation_inverse, sub(world_a, world_b))


def conjugate(q):
    return (q[0], -q[1], -q[2], -q[3])


def angle_about(orientation, axis):
    """Componente do giro em torno de um eixo (graus, −180..180), para mostrar no campo da vista."""
    w, x, y, z = orientation
    component = {'X': x, 'Y': y, 'Z': z}[axis]
    return math.degrees(2.0 * math.atan2(component, w))
