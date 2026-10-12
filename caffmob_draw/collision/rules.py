"""Regras de colisão de corpo (feature 004, T005; RN-11, RN-12, RN-13, D-12). Python puro, sem `bpy`.

Entrada: lista de `Item` (cada objeto que conta na verificação, com a caixa orientada no mundo). Saída: ocorrências, uma
por par, já classificadas e em ordem estável.

- Encostar (sobreposição até `TOLERANCE`) não é colisão (RN-11).
- Não contam (RN-12): dois estáticos (paredes, piso, teto, obstáculos entre si); itens da mesma raiz (peças do mesmo
  módulo); pares ligados (agregado × pai, item grudado × hospedeiro, porta/janela × parede, em `Item.linked`); item com
  "Colisão: Desativada".
- Ordem (RN-13): penetração em parede ou obstáculo → colisão entre itens → piso/teto; dentro do tipo, maior
  profundidade primeiro; empate pelo nome.
"""

from dataclasses import dataclass, field

from . import obb as _obb

TOLERANCE = 0.001      # m; mesma de `inspection/interference.py`

# Tipos de item
ITEM = 'ITEM'
WALL = 'WALL'
OBSTACLE = 'OBSTACLE'
FLOOR = 'FLOOR'
CEILING = 'CEILING'
STATIC = {WALL, OBSTACLE, FLOOR, CEILING}

# Tipos de ocorrência, na ordem de RN-13
KIND_WALL = 'WALL'
KIND_ITEM = 'ITEM'
KIND_FLOOR_CEILING = 'FLOOR_CEILING'
_ORDER = {KIND_WALL: 0, KIND_ITEM: 1, KIND_FLOOR_CEILING: 2}


@dataclass
class Item:
    name: str
    box: _obb.OBB
    kind: str = ITEM
    root: str = ''                  # raiz do módulo (vazio = o próprio item)
    linked: frozenset = field(default_factory=frozenset)   # nomes (ou raízes) que ele pode tocar sem conflito
    override: str = 'INHERIT'       # INHERIT / ON / OFF

    @property
    def static(self):
        return self.kind in STATIC

    @property
    def group(self):
        return self.root or self.name


@dataclass(frozen=True)
class Conflict:
    kind: str
    name_a: str
    name_b: str
    depth: float
    push: tuple             # deslocamento de A que tira a sobreposição
    location: tuple


def excluded(a, b):
    """RN-12: o par não conta como colisão."""
    if a.static and b.static:
        return True
    if a.override == 'OFF' or b.override == 'OFF':
        return True
    if a.group == b.group:
        return True
    if b.name in a.linked or b.group in a.linked or a.name in b.linked or a.group in b.linked:
        return True
    return False


def conflict_kind(a, b):
    kinds = {a.kind, b.kind}
    if kinds & {WALL, OBSTACLE}:
        return KIND_WALL
    if kinds & {FLOOR, CEILING}:
        return KIND_FLOOR_CEILING
    return KIND_ITEM


def candidate_pairs(items, only=None):
    """Pares cujas caixas alinhadas ao mundo se tocam (varredura ordenada em X); `only` restringe aos que envolvem
    esses nomes (verificação do item que acabou de ser solto)."""
    boxes = [(it, it.box.aabb()) for it in items]
    boxes.sort(key=lambda entry: (entry[1][0][0], entry[0].name))
    out = []
    for i, (a, box_a) in enumerate(boxes):
        for b, box_b in boxes[i + 1:]:
            if box_b[0][0] > box_a[1][0] + TOLERANCE:
                break
            if only is not None and a.name not in only and b.name not in only:
                continue
            if excluded(a, b) or not _obb.aabb_overlap(box_a, box_b, TOLERANCE):
                continue
            out.append((a, b))
    return out


def evaluate(a, b):
    """Ocorrência do par, ou None quando só encostam ou não se tocam."""
    result = _obb.overlap(a.box, b.box)
    if result is None or result['depth'] <= TOLERANCE + 1e-9:     # 1,0 mm estável como encostar (pergunta 31)
        return None
    first, second, push = a, b, result['push']
    if (first.static and not second.static) or (first.static == second.static and second.name < first.name):
        first, second, push = b, a, tuple(-p for p in push)
    location = tuple((a.box.center[k] + b.box.center[k]) / 2.0 for k in range(3))
    return Conflict(conflict_kind(a, b), first.name, second.name, result['depth'], push, location)


def sort_key(conflict):
    return (_ORDER[conflict.kind], -round(conflict.depth, 6), conflict.name_a, conflict.name_b)


def conflicts(items, confirm=None, only=None):
    """Ocorrências em ordem estável; `confirm(a, b)` (opcional) confirma o par com a malha real (BVH)."""
    found = []
    for a, b in candidate_pairs(items, only):
        conflict = evaluate(a, b)
        if conflict is None:
            continue
        if confirm is not None and not confirm(a, b):
            continue
        found.append(conflict)
    found.sort(key=sort_key)
    return found
