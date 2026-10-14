"""Divisões do armário: subvãos, medidas da chapa e validação (feature 006, T009; D-04, D-05). Python puro, sem `bpy`.

Referencial: o da raiz do módulo, em metros. X = largura, Y = profundidade com a **frente no menor Y**, Z = altura.

- Cada **espaço-raiz** (`s0`, `s1`, …) vem do adaptador da biblioteca (o vão interno de cada bay).
- Uma divisão corta um subvão-**folha** em dois: a vertical em esquerdo (`.a`) e direito (`.b`); a horizontal em de
  baixo (`.a`) e de cima (`.b`). Por isso uma divisão ocupa sempre o subvão inteiro (RN-09).
- `offset` é a distância da face esquerda (vertical) ou de baixo (horizontal) do subvão até a face da chapa (RN-11).
  Quando o espaço-raiz muda de tamanho, o `offset` fica igual e o resto se ajusta (RN-16).
- Os recuos só reduzem a profundidade da chapa (RN-13).

Feature 008 (T018, T055; D-10, D-22):
- `add_many`: N chapas iguais de uma vez (inserção múltipla), em cadeia pelos subvãos da direita/de cima;
- `kind`: `FIXED` (padrão), `MOVABLE` (mesma geometria; a furação sai nas peças vizinhas, `cutting/drilling`) e
  `SPACER` (distanciador: ocupa a faixa a partir da face esquerda/de baixo e **não** divide o vão; o subvão continua
  com o mesmo caminho, menor);
- `follow`: distanciador "p/ Divisão", posto no subvão logo depois da divisória seguida (offset 0), acompanha-a;
- `remove_in_space`: "Sem Divisória" no subvão-folha tira a divisória que o criou e junta as metades.

Feature 015 (T024; RN-15):
- `INVISIBLE` (prateleira Invisível) e `DIVISION_ONLY` (Somente Divisão) dividem o subvão com espessura 0: não viram
  peça nem entram no corte (`makes_part`);
- `variant` guarda a variante do catálogo. `CORTA_SAR` faz a divisória vertical subir até o topo e corta os sarrafos
  (`stretcher_cuts`); `ARAMADA` é ferragem, não chapa; `CORREDICA` é chapa com corrediças; `C_REB`,
  `NAO_DIVIDE_FUNDO` e `MONTANTE` só ficam gravadas (o fundo já é uma peça única atrás das divisórias, 🟡);
- `bay_width`: largura digitada do vão à esquerda de uma divisória de vão (`bays.py`).

Códigos de mensagem: `DIV-001` subvão menor que o mínimo; `DIV-002` chapa com profundidade menor que o mínimo;
`DIV-003` o subvão da divisão não existe mais (todos erro: impedem o Confirmar).
"""

import uuid
from dataclasses import asdict, dataclass, replace

from ..data import units
from ..data.i18n import tr
from .validate import ERROR, Message

MIN_SPACE = 0.05        # m (RN-14)
MIN_DEPTH = 0.05        # m (RN-14)
DEFAULT_SETBACK = 0.02  # m (RN-13)
VERTICAL = 'VERTICAL'
HORIZONTAL = 'HORIZONTAL'
FIXED, MOVABLE, SPACER = 'FIXED', 'MOVABLE', 'SPACER'
INVISIBLE, DIVISION_ONLY = 'INVISIBLE', 'DIVISION_ONLY'
NO_PART = (INVISIBLE, DIVISION_ONLY)
CORTA_SAR, ARAMADA, CORREDICA = 'CORTA_SAR', 'ARAMADA', 'CORREDICA'
_AXIS = {VERTICAL: 0, HORIZONTAL: 2}


@dataclass(frozen=True)
class Box:
    lo: tuple
    hi: tuple

    def size(self, axis):
        return self.hi[axis] - self.lo[axis]

    def contains_front(self, x, z):
        return self.lo[0] <= x <= self.hi[0] and self.lo[2] <= z <= self.hi[2]


@dataclass(frozen=True)
class Division:
    uid: str
    space: str
    orientation: str
    offset: float
    thickness: float
    use_front: bool = False
    front: float = DEFAULT_SETBACK
    use_back: bool = False
    back: float = DEFAULT_SETBACK
    material: str = ""
    kind: str = FIXED
    follow: str = ""
    bay: bool = False
    variant: str = ""
    bay_width: float = 0.0


def new_uid():
    return uuid.uuid4().hex[:8]


def to_dict(division):
    return asdict(division)


def from_dict(data):
    names = Division.__dataclass_fields__
    return Division(**{k: v for k, v in data.items() if k in names})


def makes_part(division):
    """A divisão vira chapa no 3D e no corte? Invisível, Somente Divisão e prateleira Aramada não (feature 015)."""
    return division.kind not in NO_PART and division.variant != ARAMADA


def stretcher_cuts(cuts, divisions):
    """[(x0, x1)] das divisórias verticais "Corta Sar": a faixa que corta os sarrafos da estrutura (feature 015).

    `cuts` = {uid: (subvão, chapa Box)} do `resolve`.
    """
    out = []
    for division in divisions:
        if division.variant == CORTA_SAR and division.orientation == VERTICAL and division.uid in cuts:
            plate = cuts[division.uid][1]
            out.append((plate.lo[0], plate.hi[0]))
    return sorted(out)


def children(path):
    return path + ".a", path + ".b"


def depth_of(path):
    return path.count(".")


def _split(box, division):
    axis = _AXIS[division.orientation]
    lo, hi = list(box.lo), list(box.hi)
    cut0 = box.lo[axis] + division.offset
    cut1 = cut0 + division.thickness
    a_hi = list(hi)
    a_hi[axis] = cut0
    b_lo = list(lo)
    b_lo[axis] = cut1
    plate_lo, plate_hi = list(lo), list(hi)
    plate_lo[axis], plate_hi[axis] = cut0, cut1
    return Box(tuple(lo), tuple(a_hi)), Box(tuple(b_lo), tuple(hi)), Box(tuple(plate_lo), tuple(plate_hi))


def resolve(roots, divisions):
    """(folhas {caminho: Box}, cortes {uid: (Box do subvão, Box da chapa sem recuo)}, órfãs [uid]).

    `roots` = {caminho-raiz: Box}. Divisões cujo subvão não existe (ou já foi cortado por outra) ficam órfãs.
    """
    spaces = dict(roots)
    cuts = {}
    orphans = []
    for division in sorted(divisions, key=lambda d: (depth_of(d.space), d.space)):
        box = spaces.get(division.space)
        if box is None:
            orphans.append(division.uid)
            continue
        a, b, plate = _split(box, division)
        if division.kind == SPACER:            # ocupa a faixa; o subvão continua inteiro do lado maior
            axis = _AXIS[division.orientation]
            spaces[division.space] = b if b.size(axis) >= a.size(axis) else a
        else:
            del spaces[division.space]
            first, second = children(division.space)
            spaces[first], spaces[second] = a, b
        cuts[division.uid] = (box, plate)
    return spaces, cuts, orphans


def place(plate, division):
    """Caixa final da chapa: a profundidade perde os recuos marcados (a frente é o menor Y)."""
    lo, hi = list(plate.lo), list(plate.hi)
    if division.use_front:
        lo[1] += division.front
    if division.use_back:
        hi[1] -= division.back
    return Box(tuple(lo), tuple(hi))


def middle_offset(space, orientation, thickness):
    """Posição que deixa a chapa no meio do subvão (RN-11)."""
    return max(0.0, (space.size(_AXIS[orientation]) - thickness) / 2.0)


def add(roots, divisions, space, orientation, thickness, *, use_front=False, front=DEFAULT_SETBACK, use_back=False,
        back=DEFAULT_SETBACK, uid=None, kind=FIXED, follow="", bay=False, offset=None, variant=""):
    """Nova divisão no subvão-folha `space`: no meio, ou encostada na face esquerda/de baixo se for distanciador.

    Erro (ValueError) se o subvão não for uma folha.
    """
    leaves, _cuts, _orphans = resolve(roots, divisions)
    box = leaves.get(space)
    if box is None:
        raise ValueError(tr("Escolha um vão livre para a divisão"))
    if kind in NO_PART:
        thickness = 0.0                         # divide sem chapa (feature 015)
    if offset is None:
        offset = 0.0 if kind == SPACER else middle_offset(box, orientation, thickness)
    division = Division(uid or new_uid(), space, orientation, float(offset), float(thickness), bool(use_front),
                        float(front), bool(use_back), float(back), kind=kind, follow=follow, bay=bay,
                        variant=variant)
    return list(divisions) + [division]


def add_many(roots, divisions, space, orientation, count, thickness, **options):
    """`count` chapas iguais no subvão (inserção múltipla): `count + 1` subvãos de mesma medida."""
    leaves, _cuts, _orphans = resolve(roots, divisions)
    box = leaves.get(space)
    if box is None:
        raise ValueError(tr("Escolha um vão livre para a divisão"))
    gap = (box.size(_AXIS[orientation]) - count * thickness) / (count + 1)
    out = list(divisions)
    target = space
    for _index in range(int(count)):
        out = add(roots, out, target, orientation, thickness, offset=max(gap, 0.0), **options)
        target = children(target)[1]
    return out


def remove_in_space(divisions, leaf):
    """"Sem Divisória": tira a divisória que criou o subvão `leaf` (e as de dentro dela)."""
    if "." not in leaf:
        return list(divisions), []
    parent = leaf.rsplit(".", 1)[0]
    target = next((d for d in divisions if d.space == parent and d.kind != SPACER), None)
    if target is None:
        return list(divisions), []
    return remove(divisions, target.uid)


def update(divisions, uid, **changes):
    return [replace(d, **changes) if d.uid == uid else d for d in divisions]


def remove(divisions, uid):
    """(divisões restantes, uids removidos). Quem estava dentro das metades da removida sai junto."""
    target = next((d for d in divisions if d.uid == uid), None)
    if target is None:
        return list(divisions), []
    inside = tuple(children(target.space))
    removed = [d.uid for d in divisions
               if d.uid == uid or any(d.space == p or d.space.startswith(p + ".") for p in inside)]
    return [d for d in divisions if d.uid not in removed], removed


def offset_range(space, division):
    """(mínimo, máximo) do `offset` que deixa os dois lados com o subvão mínimo (distanciador: pode encostar)."""
    size = space.size(_AXIS[division.orientation])
    if division.kind == SPACER:
        return 0.0, max(0.0, size - division.thickness)
    return MIN_SPACE, size - division.thickness - MIN_SPACE


def validate(roots, divisions, unit='MM', names=None):
    """Mensagens `DIV-*`; `names` = {uid: nome da chapa} para o campo componente."""
    names = names or {}
    leaves, cuts, orphans = resolve(roots, divisions)
    out = []
    for d in divisions:
        name = names.get(d.uid, d.uid)
        if d.uid in orphans:
            out.append(Message('DIV-003', ERROR, name, 'space', d.space, '', tr("Remova a divisão ou escolha outro vão")))
            continue
        space, plate = cuts[d.uid]
        lo, hi = offset_range(space, d)
        if not (lo - 1e-9 <= d.offset <= hi + 1e-9):
            span = "{} – {}".format(units.format_length(lo, unit), units.format_length(max(lo, hi), unit))
            out.append(Message('DIV-001', ERROR, name, 'offset', units.format_length(d.offset, unit), span,
                               tr("Deixe pelo menos {} de cada lado").format(units.format_length(MIN_SPACE, unit))))
        depth = place(plate, d).size(1)
        if depth < MIN_DEPTH - 1e-9:
            out.append(Message('DIV-002', ERROR, name, 'setback', units.format_length(depth, unit),
                               "≥ " + units.format_length(MIN_DEPTH, unit), tr("Diminua os recuos")))
    return out


def space_at(leaves, x, z):
    """Subvão-folha sob o ponto (x, z) da vista frontal, ou None."""
    inside = [(path, box) for path, box in leaves.items() if box.contains_front(x, z)]
    if not inside:
        return None
    return min(inside, key=lambda item: (item[1].size(0) * item[1].size(2), item[0]))[0]


def space_tokens(path, divisions):
    """[('ROOT', n), ('LEFT'|'RIGHT'|'BOTTOM'|'TOP'), …] para montar o rótulo do subvão na interface."""
    by_space = {d.space: d.orientation for d in divisions}
    parts = path.split(".")
    tokens = [('ROOT', int(parts[0][1:] or 0) + 1)]
    current = parts[0]
    for part in parts[1:]:
        orientation = by_space.get(current, VERTICAL)
        if orientation == VERTICAL:
            tokens.append(('LEFT',) if part == 'a' else ('RIGHT',))
        else:
            tokens.append(('BOTTOM',) if part == 'a' else ('TOP',))
        current = current + "." + part
    return tokens
