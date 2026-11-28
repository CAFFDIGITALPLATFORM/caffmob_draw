"""Registro conferível da cota fixa (feature 080, D-13; RF-08 a RF-10, RNF-02): Python puro, sem `bpy`.

O cálculo das cotas guarda, junto do valor mostrado, a identidade e a pose completa do alvo móvel (uid de sessão,
`matrix_world` 4x4, escopo, pai, cena) e, por lado, a da referência medida (uid, `matrix_world` e caixa, ou a altura do
teto no lado do Teto). Antes de mover, a confirmação (popup e campo) compara o registro mostrado com o atual: qualquer
diferença acima da tolerância recusa, e o projetista lê de novo. Renomear não muda o uid, então não invalida; apagar e
recriar com o mesmo nome muda o uid, então invalida.

Tolerâncias (RNF-02): translação 0,001 mm (1e-6 m); cada componente da 3x3 e da caixa 1e-6.
"""

from dataclasses import dataclass, field

from ..data.i18n import N_

TRANSLATION_TOL = 1e-6
LINEAR_TOL = 1e-6
OBJECT, FLOOR, CEILING = 'OBJECT', 'FLOOR', 'CEILING'

TARGET_CHANGED = N_("O item mudou desde que a cota foi lida: confira a cota e digite de novo. Nada foi alterado.")
REFERENCE_CHANGED = N_("A referência da cota mudou desde que foi lida: confira a cota e digite de novo. "
                       "Nada foi alterado.")
CEILING_CHANGED = N_("A altura do teto mudou desde que a cota foi lida: confira a cota e digite de novo. "
                     "Nada foi alterado.")
NOT_CHECKABLE = N_("A cota não pode ser conferida: confira a cota e digite de novo. Nada foi alterado.")


def flat(matrix):
    """4x4 (`mathutils.Matrix` ou listas) → 16 floats por linha."""
    return tuple(float(matrix[r][c]) for r in range(4) for c in range(4))


@dataclass(frozen=True)
class RefToken:
    kind: str                       # OBJECT, FLOOR ou CEILING
    uid: int = 0
    matrix: tuple = ()              # 16 floats
    box: tuple = ()                 # (min xyz, max xyz) no mundo
    ceiling: float = 0.0


@dataclass(frozen=True)
class CotaToken:
    uid: int
    matrix: tuple                   # 16 floats
    scope: str
    parent: int                     # uid de sessão do pai, 0 sem pai
    scene: int                      # scene.as_pointer()
    refs: dict = field(default_factory=dict)      # lado → RefToken


def _matrix_differs(a, b):
    if len(a) != 16 or len(b) != 16:
        return True
    for index in range(16):
        row, col = divmod(index, 4)
        tol = TRANSLATION_TOL if col == 3 and row < 3 else LINEAR_TOL
        if abs(a[index] - b[index]) > tol:
            return True
    return False


def _box_differs(a, b):
    if len(a) != len(b):
        return True
    return any(abs(x - y) > LINEAR_TOL for pa, pb in zip(a, b) for x, y in zip(pa, pb))


def compare(shown, now, side):
    """Motivo (msgid) para recusar a edição do lado `side`, ou None quando o registro mostrado continua valendo."""
    if shown is None or now is None:
        return NOT_CHECKABLE
    if (shown.scene != now.scene or shown.uid != now.uid or shown.scope != now.scope
            or shown.parent != now.parent or _matrix_differs(shown.matrix, now.matrix)):
        return TARGET_CHANGED
    before, after = shown.refs.get(side), now.refs.get(side)
    if before is None:
        return NOT_CHECKABLE
    if after is None or after.kind != before.kind:
        return REFERENCE_CHANGED
    if before.kind == OBJECT:
        if after.uid != before.uid or _matrix_differs(before.matrix, after.matrix) or _box_differs(before.box, after.box):
            return REFERENCE_CHANGED
    elif before.kind == CEILING and abs(after.ceiling - before.ceiling) > LINEAR_TOL:
        return CEILING_CHANGED
    return None
