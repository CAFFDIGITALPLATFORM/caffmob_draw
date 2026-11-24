"""Decisão da frente do objeto de referência no Mover Sobre (feature 022, RN-01 a RN-06). Python puro, sem `bpy`.

A frente é o lado do objeto que olha para a sala. A precedência é fixa:

1. `btm_front_yaw` gravada pelo usuário — a escolha dele vence sempre (RN-02);
2. a parede atrás de B: a face que aponta para B define a frente, **sem limite de distância** (decisão do titular
   em 2026-11-24); vale a parede mais próxima cujo pé se sobrepõe ao pé de B em planta;
3. o eixo do objeto (a convenção −Y local, `yaw = 0`);
4. sem evidência (objeto que não é módulo de biblioteca e sem parede) ou desacordo parede × eixo acima de
   `DISAGREE_MAX` → a janela pergunta (`ambíguo`).

Ângulos em graus no plano XY do projeto; caixas são `((xmin, ymin, zmin), (xmax, ymax, zmax))` em metros, e uma parede
é `(caixa_mínima, caixa_máxima, yaw_graus)` — o yaw é o da matriz do objeto, com a espessura no Y local.
"""

from math import atan2, cos, degrees, hypot, radians, sin

PROPRIEDADE, PAREDE, EIXO = 'PROPRIEDADE', 'PAREDE', 'EIXO'

DISAGREE_MAX = 45.0        # desacordo entre a parede e o eixo antes de perguntar (D2, 2026-11-24)

# Lado escolhido no diálogo → yaw que leva a frente do objeto (−Y local) para aquele lado.
FRONT_YAW = {'NEG_Y': 0.0, 'POS_X': 90.0, 'POS_Y': 180.0, 'NEG_X': 270.0}
FACE_VECTORS = {'NEG_Y': (0.0, -1.0), 'POS_Y': (0.0, 1.0), 'NEG_X': (-1.0, 0.0), 'POS_X': (1.0, 0.0)}


def normalize_deg(angle):
    return float(angle) % 360.0


def angular_distance(first, second):
    """Menor diferença entre dois ângulos, em graus (0 a 180)."""
    return abs((normalize_deg(first - second) + 180.0) % 360.0 - 180.0)


def yaw_from_normal(nx, ny):
    """Yaw que leva a frente do objeto (−Y local) para a normal `(nx, ny)`."""
    if abs(nx) < 1e-12 and abs(ny) < 1e-12:
        return 0.0
    return normalize_deg(degrees(atan2(ny, nx)) + 90.0)


def normal_of(yaw_deg, sign=1.0):
    """Normal horizontal do eixo Y local (o eixo da espessura) de um objeto com `yaw_deg`."""
    angle = radians(yaw_deg)
    return (-sin(angle) * sign, cos(angle) * sign)


def plan_center(box):
    return ((box[0][0] + box[1][0]) / 2.0, (box[0][1] + box[1][1]) / 2.0)


def _span(box, axis):
    """Intervalo ocupado pelo pé na direção `axis` (projetando os quatro cantos da planta)."""
    values = [corner[0] * axis[0] + corner[1] * axis[1]
              for corner in ((box[0][0], box[0][1]), (box[1][0], box[0][1]),
                             (box[0][0], box[1][1]), (box[1][0], box[1][1]))]
    return min(values), max(values)


def wall_candidate(wall, box_b, tolerance=0.05):
    """A parede corre atrás de B: o comprimento dela (perpendicular à espessura) cobre o pé de B."""
    box_min, box_max, yaw = wall
    nx, ny = normal_of(yaw)
    length_axis = (ny, -nx)
    wall_span = _span((box_min, box_max), length_axis)
    b_span = _span(box_b, length_axis)
    return wall_span[1] >= b_span[0] - tolerance and b_span[1] >= wall_span[0] - tolerance


def plan_gap(box_a, box_b):
    """Distância em planta entre dois pés (0 quando se tocam ou se sobrepõem)."""
    dx = max(0.0, box_a[0][0] - box_b[1][0], box_b[0][0] - box_a[1][0])
    dy = max(0.0, box_a[0][1] - box_b[1][1], box_b[0][1] - box_a[1][1])
    return hypot(dx, dy)


def wall_yaw(wall, box_b):
    """Yaw da frente de B vinda da parede: a face da parede que olha para B."""
    box_min, box_max, yaw = wall
    wall_center = plan_center((box_min, box_max))
    b_center = plan_center(box_b)
    nx, ny = normal_of(yaw)
    if (b_center[0] - wall_center[0]) * nx + (b_center[1] - wall_center[1]) * ny < 0.0:
        nx, ny = -nx, -ny
    return yaw_from_normal(nx, ny)


def nearest_wall(box_b, walls):
    """Parede candidata atrás de B: a mais próxima entre as que correm atrás do pé de B (sem limite de distância)."""
    candidates = [wall for wall in walls if wall_candidate(wall, box_b)]
    if not candidates:
        return None

    def distance(wall):
        return (round(plan_gap(wall[0:2], box_b), 6), round(plan_gap(wall[0:2], box_b), 6))

    return min(candidates, key=distance)


def face_of(face, yaw_deg):
    """Face de B (no referencial dele) que corresponde à face da vista girada pelo `yaw`.

    A janela trabalha no referencial girado; o `stick` grava a face no referencial de B. Com `yaw = 0` a face não
    muda, e com a frente trocada "Na frente" gruda na face certa.
    """
    vx, vy = FACE_VECTORS[face]
    angle = radians(-yaw_deg)
    rx, ry = vx * cos(angle) - vy * sin(angle), vx * sin(angle) + vy * cos(angle)
    if abs(rx) >= abs(ry):
        return 'POS_X' if rx > 0.0 else 'NEG_X'
    return 'POS_Y' if ry > 0.0 else 'NEG_Y'


def decide(box_b, walls, stored_yaw, module_like):
    """Frente de B: `(yaw, origem, ambíguo)`. `stored_yaw` None quando o usuário nunca escolheu."""
    if stored_yaw is not None:
        return normalize_deg(stored_yaw), PROPRIEDADE, False
    wall = nearest_wall(box_b, walls)
    if wall is not None:
        yaw = wall_yaw(wall, box_b)
        return yaw, PAREDE, angular_distance(yaw, 0.0) > DISAGREE_MAX
    return 0.0, EIXO, not module_like


def decide_for_wall(box_b, box_a, from_drag, stored_yaw, wall_yaw_deg=0.0):
    """Frente quando a referência é a própria parede (RN-06): o lado de onde A chegou.

    Sem arraste (janela aberta pelo menu) não há evidência de intenção: pergunta (D5, 2026-11-24). A sobre a
    espessura da parede também pergunta.
    """
    if stored_yaw is not None:
        return normalize_deg(stored_yaw), PROPRIEDADE, False
    if not from_drag:
        return 0.0, EIXO, True
    if plan_gap(box_b, box_a) < 0.02:
        return 0.0, EIXO, True
    return wall_yaw((box_b[0], box_b[1], wall_yaw_deg), box_a), PAREDE, False
