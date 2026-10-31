"""Medida física de um módulo (feature 080, D-01; RN-01 a RN-05): Python puro, sem `bpy`.

A medida que o projetista vê e digita é a física: parâmetro do gerador × comprimento do eixo local na `matrix_world`
(escala própria da raiz × escala dos ancestrais). Os eixos são fixos (D-02): X local = largura, Y = profundidade,
Z = altura. A transformação é lida por `part_geometry.scale_axes`, que já recusa escala zero, shear e valor não finito;
aqui as recusas falam em "módulo".

Assar a escala (D-03 = B): depois de uma edição confirmada a raiz fica com escala ±1 por eixo (o sinal do espelho
fica), e o parâmetro passa a valer físico ÷ escala dos ancestrais. A escala dos ancestrais de um eixo é a escala do
eixo no mundo ÷ |escala própria| desse eixo, o que vale também com a raiz girada dentro de um pai não uniforme.

As matrizes são lidas por índice `m[linha][coluna]`, o que serve tanto para `mathutils.Matrix` quanto para listas.
"""

import math
from dataclasses import dataclass

from ..data.i18n import N_
from . import part_geometry

FIELDS = ('width', 'depth', 'height')
AXIS = {'width': 0, 'depth': 1, 'height': 2}
TOLERANCE = 1e-4              # 0,1 mm (RNF-01): pós-condição e "nada mudou"

_MODULE_MESSAGES = {
    N_("A transformação da peça tem valor não finito."):
        N_("A transformação do módulo tem valor não finito."),
    N_("A peça tem escala zero num eixo: aplique a escala antes de editar."):
        N_("O módulo tem escala zero num eixo: aplique a escala antes de editar."),
    N_("A peça está distorcida (shear): aplique a transformação antes de editar."):
        N_("O módulo está distorcido (shear): aplique a transformação antes de editar."),
}


class ModuleGeometryError(ValueError):
    """Medida ou transformação recusada (mensagem pronta para o usuário, antes da tradução)."""


class PhysicalRangeError(ModuleGeometryError):
    """Valor fora da faixa física válida; carrega a faixa para a mensagem."""

    def __init__(self, field, value, low, high):
        super().__init__(N_("Valor fora da faixa física válida."))
        self.field, self.value, self.low, self.high = field, value, low, high


@dataclass(frozen=True)
class BakePlan:
    params: tuple       # novos parâmetros (largura, profundidade, altura), em unidades do gerador
    scale: tuple        # nova escala própria da raiz: ±1 por eixo
    physical: tuple     # medida física depois da edição
    changed: bool       # False quando nada muda (mesma medida e escala já ±1)


def axis_scales(matrix_world):
    """Escala de cada eixo local da raiz no mundo (positiva). Recusa shear, escala zero e não finito."""
    try:
        _units, scales = part_geometry.scale_axes(matrix_world)
    except part_geometry.PartGeometryError as exc:
        raise ModuleGeometryError(_MODULE_MESSAGES.get(str(exc), str(exc))) from None
    return tuple(scales)


def physical(params, world_scales):
    """Medida física (largura, profundidade, altura) a partir dos parâmetros e da escala de cada eixo no mundo."""
    return tuple(float(p) * float(s) for p, s in zip(params, world_scales))


def ancestor_scales(world_scales, own_scale):
    """Parte da escala de cada eixo que vem dos ancestrais (pai, inversa do pai): mundo ÷ |própria|."""
    out = []
    for world, own in zip(world_scales, own_scale):
        own = abs(float(own))
        if not math.isfinite(own) or own < part_geometry._EPS_SCALE:
            raise ModuleGeometryError(N_("O módulo tem escala zero num eixo: aplique a escala antes de editar."))
        out.append(float(world) / own)
    return tuple(out)


def param_for(value, ancestor):
    """Parâmetro que dá a medida física `value` com a raiz em escala ±1 sob ancestrais de escala `ancestor`."""
    return float(value) / float(ancestor)


def validate_value(field, value):
    """Valor digitado: número finito e maior que zero."""
    try:
        number = float(value)
    except (TypeError, ValueError):
        raise ModuleGeometryError(N_("Medida inválida.")) from None
    if not math.isfinite(number):
        raise ModuleGeometryError(N_("Medida não finita."))
    if number <= 0.0:
        raise ModuleGeometryError(N_("A medida precisa ser maior que zero."))
    return number


def physical_range(general, param_range, ancestor):
    """Faixa física de um eixo: os limites gerais (já físicos) cruzados com a faixa do parâmetro do gerador
    convertida pela escala dos ancestrais. `param_range` pode ser None (gerador sem limite próprio)."""
    low, high = float(general[0]), float(general[1])
    if param_range is not None:
        low = max(low, float(param_range[0]) * ancestor)
        high = min(high, float(param_range[1]) * ancestor)
    return low, high


def check_value(field, value, general, param_range, ancestor):
    """Valida o valor físico de um eixo antes de qualquer escrita (RN-05: recusa, nunca corta)."""
    number = validate_value(field, value)
    low, high = physical_range(general, param_range, ancestor)
    # A faixa é conferida com folga de arredondamento de float, nunca com a tolerância de 0,1 mm.
    if not (low - 1e-12 <= number <= high + 1e-12) or low > high:
        raise PhysicalRangeError(field, number, low, high)
    return number


def bake_plan(params, own_scale, world_scales, edits):
    """Plano da edição: parâmetros novos e escala própria ±1 (sinal mantido). `edits` = {campo: medida física};
    os eixos não editados guardam a medida física atual."""
    for field in edits:
        if field not in AXIS:
            raise ModuleGeometryError(N_("Campo de medida desconhecido."))
    ancestor = ancestor_scales(world_scales, own_scale)
    current = physical(params, world_scales)
    target = tuple(float(edits[f]) if f in edits else current[i] for i, f in enumerate(FIELDS))
    new_params = tuple(param_for(target[i], ancestor[i]) for i in range(3))
    signs = tuple(-1.0 if float(s) < 0 else 1.0 for s in own_scale)
    changed = (any(abs(float(s) - sign) > 1e-9 for s, sign in zip(own_scale, signs))
               or any(abs(a - b) > 1e-9 for a, b in zip(new_params, params)))
    return BakePlan(new_params, signs, target, changed)
