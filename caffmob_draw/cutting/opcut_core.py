"""Motor de otimização de corte guilhotinado 2D offline compatível com OpCut (feature 021, T011; RF-02, RN-02).

Baseado na modelagem de cortes guilhotinados ortogonais do OpCut (https://github.com/bozokopic/opcut, GPL-3.0):
- Cada chapa disponível gera uma área útil descontando o refilo perimetral (`margin`).
- Cada colocação gera um corte guilhotinado horizontal ou vertical respeitando a espessura da serra (`kerf`).
- Suporta os métodos `greedy` e `forward_greedy` (lookahead de um passo para minimizar fragmentação).
- Respeita `can_rotate` (veio `NONE` permite rotação de 90°; `VERTICAL`/`HORIZONTAL` trava a orientação).
- Peças maiores que a área útil da chapa vão para `unplaced` sem interromper o cálculo.
"""

from dataclasses import dataclass, field
from typing import List, Optional, Tuple


@dataclass
class CutItem:
    id: str
    label: str
    width: float
    height: float
    quantity: int = 1
    thickness: float = 15.0
    material: str = "MDF Padrão"
    can_rotate: bool = True
    module_ref: str = ""
    edges: Tuple[float, float, float, float] = (0.0, 0.0, 0.0, 0.0)


@dataclass
class PlacedRect:
    item_id: str
    label: str
    module_ref: str
    x: float
    y: float
    width: float
    height: float
    rotated: bool = False
    edges: Tuple[float, float, float, float] = (0.0, 0.0, 0.0, 0.0)


@dataclass
class FreeRect:
    x: float
    y: float
    width: float
    height: float


@dataclass
class CutLine:
    x1: float
    y1: float
    x2: float
    y2: float


@dataclass
class SheetLayout:
    sheet_index: int
    material: str
    thickness: float
    width: float
    height: float
    margin: float
    kerf: float
    used: List[PlacedRect] = field(default_factory=list)
    unused: List[FreeRect] = field(default_factory=list)
    cuts: List[CutLine] = field(default_factory=list)

    @property
    def efficiency_pct(self) -> float:
        usable_area = max((self.width - 2.0 * self.margin) * (self.height - 2.0 * self.margin), 1e-6)
        used_area = sum(r.width * r.height for r in self.used)
        return round(min(100.0, (used_area / usable_area) * 100.0), 2)


@dataclass
class CutPlanResult:
    sheets: List[SheetLayout] = field(default_factory=list)
    unplaced: List[CutItem] = field(default_factory=list)


def _orientations(item: CutItem) -> List[Tuple[float, float, bool]]:
    opts = [(float(item.width), float(item.height), False)]
    if item.can_rotate and abs(item.width - item.height) > 1e-6:
        opts.append((float(item.height), float(item.width), True))
    return opts


def _fits(w: float, h: float, free: FreeRect) -> bool:
    return w <= free.width + 1e-6 and h <= free.height + 1e-6


def _split_free(free: FreeRect, w: float, h: float, kerf: float, horizontal_first: bool) -> Tuple[List[FreeRect], List[CutLine]]:
    """Divide um retângulo livre por cortes guilhotinados (estilo OpCut)."""
    rem_w = free.width - w - kerf
    rem_h = free.height - h - kerf
    new_free: List[FreeRect] = []
    cuts: List[CutLine] = []

    if horizontal_first:
        # Corte horizontal de ponta a ponta em y = free.y + h
        if rem_h > 1e-3:
            cut_y = free.y + h + kerf * 0.5
            cuts.append(CutLine(free.x, cut_y, free.x + free.width, cut_y))
            new_free.append(FreeRect(free.x, free.y + h + kerf, free.width, rem_h))
        # Corte vertical na faixa inferior em x = free.x + w
        if rem_w > 1e-3:
            cut_x = free.x + w + kerf * 0.5
            cuts.append(CutLine(cut_x, free.y, cut_x, free.y + h))
            new_free.append(FreeRect(free.x + w + kerf, free.y, rem_w, h))
    else:
        # Corte vertical de ponta a ponta em x = free.x + w
        if rem_w > 1e-3:
            cut_x = free.x + w + kerf * 0.5
            cuts.append(CutLine(cut_x, free.y, cut_x, free.y + free.height))
            new_free.append(FreeRect(free.x + w + kerf, free.y, rem_w, free.height))
        # Corte horizontal na coluna esquerda em y = free.y + h
        if rem_h > 1e-3:
            cut_y = free.y + h + kerf * 0.5
            cuts.append(CutLine(free.x, cut_y, free.x + w, cut_y))
            new_free.append(FreeRect(free.x, free.y + h + kerf, w, rem_h))

    return new_free, cuts


def _score_placement(free: FreeRect, w: float, h: float, kerf: float,
                     horizontal_first: bool, next_items: List[CutItem],
                     forward_lookahead: bool) -> Tuple[float, float]:
    """Menor pontuação é melhor: prioriza melhor ajuste e menor fragmentação (lookahead OpCut)."""
    short_side = min(free.width - w, free.height - h)
    waste_area = (free.width * free.height) - (w * h)
    if not forward_lookahead or not next_items:
        return (short_side, waste_area)

    sub_free, _ = _split_free(free, w, h, kerf, horizontal_first)
    # Verifica se a próxima peça cabe em algum sub-retângulo gerado (lookahead de 1 passo)
    nxt = next_items[0]
    fits_next = any(
        _fits(nw, nh, sf)
        for sf in sub_free
        for nw, nh, _ in _orientations(nxt)
    )
    lookahead_penalty = 0.0 if fits_next else 1e6
    largest_rem = max((sf.width * sf.height for sf in sub_free), default=0.0)
    return (lookahead_penalty + short_side, -largest_rem + waste_area * 0.01)


def _choose_best_split(free: FreeRect, w: float, h: float, kerf: float,
                       next_items: List[CutItem], forward_lookahead: bool) -> bool:
    s_h = _score_placement(free, w, h, kerf, True, next_items, forward_lookahead)
    s_v = _score_placement(free, w, h, kerf, False, next_items, forward_lookahead)
    return s_h <= s_v


def _expand_items(items: List[CutItem]) -> List[CutItem]:
    expanded: List[CutItem] = []
    for it in items:
        qty = max(1, int(it.quantity))
        for _ in range(qty):
            expanded.append(CutItem(
                id=it.id,
                label=it.label,
                width=float(it.width),
                height=float(it.height),
                quantity=1,
                thickness=float(it.thickness),
                material=it.material or "MDF Padrão",
                can_rotate=bool(it.can_rotate),
                module_ref=it.module_ref or "",
                edges=tuple(it.edges) if it.edges else (0.0, 0.0, 0.0, 0.0),
            ))
    return expanded


def calculate(
    items: List[CutItem],
    sheet_width: float = 2750.0,
    sheet_height: float = 1830.0,
    margin: float = 10.0,
    kerf: float = 4.0,
    method: str = 'forward_greedy',
) -> CutPlanResult:
    """Calcula o plano de corte guilhotinado 2D agrupado por `(material, thickness)`."""
    if not items:
        return CutPlanResult()

    usable_w = float(sheet_width) - 2.0 * float(margin)
    usable_h = float(sheet_height) - 2.0 * float(margin)
    if usable_w <= 0 or usable_h <= 0:
        return CutPlanResult(sheets=[], unplaced=list(items))

    forward_lookahead = (method == 'forward_greedy')
    result = CutPlanResult()
    groups = {}

    for it in _expand_items(items):
        # Valida se cabe na área útil da chapa em alguma orientação permitida
        can_ever_fit = any(
            (w <= usable_w + 1e-6 and h <= usable_h + 1e-6)
            for w, h, _ in _orientations(it)
        )
        if not can_ever_fit:
            result.unplaced.append(it)
            continue
        key = (it.material, round(it.thickness, 2))
        groups.setdefault(key, []).append(it)

    sheet_counter = 1
    for (material, thickness), group_items in sorted(groups.items(), key=lambda kv: (kv[0][0], kv[0][1])):
        # Ordena peças maiores primeiro (área decrescente, depois maior lado)
        remaining = sorted(
            group_items,
            key=lambda p: (p.width * p.height, max(p.width, p.height)),
            reverse=True,
        )
        active_sheets: List[SheetLayout] = []

        for idx, item in enumerate(remaining):
            next_items = remaining[idx + 1:idx + 2]
            best_choice: Optional[Tuple[Tuple[float, float], int, int, float, float, bool, bool]] = None

            for s_idx, sheet in enumerate(active_sheets):
                for f_idx, free in enumerate(sheet.unused):
                    for w, h, rotated in _orientations(item):
                        if not _fits(w, h, free):
                            continue
                        horiz = _choose_best_split(free, w, h, kerf, next_items, forward_lookahead)
                        score = _score_placement(free, w, h, kerf, horiz, next_items, forward_lookahead)
                        if best_choice is None or score < best_choice[0]:
                            best_choice = (score, s_idx, f_idx, w, h, rotated, horiz)

            if best_choice is None:
                # Abre nova chapa
                new_sheet = SheetLayout(
                    sheet_index=sheet_counter,
                    material=material,
                    thickness=thickness,
                    width=float(sheet_width),
                    height=float(sheet_height),
                    margin=float(margin),
                    kerf=float(kerf),
                    unused=[FreeRect(float(margin), float(margin), usable_w, usable_h)],
                )
                sheet_counter += 1
                active_sheets.append(new_sheet)
                free = new_sheet.unused[0]
                # Escolhe orientação que cabe na chapa nova
                placed_opt = None
                for w, h, rotated in _orientations(item):
                    if _fits(w, h, free):
                        horiz = _choose_best_split(free, w, h, kerf, next_items, forward_lookahead)
                        placed_opt = (w, h, rotated, horiz)
                        break
                if placed_opt is None:
                    result.unplaced.append(item)
                    continue
                w, h, rotated, horiz = placed_opt
                s_idx, f_idx = len(active_sheets) - 1, 0
            else:
                _, s_idx, f_idx, w, h, rotated, horiz = best_choice

            sheet = active_sheets[s_idx]
            free = sheet.unused.pop(f_idx)
            sheet.used.append(PlacedRect(
                item_id=item.id,
                label=item.label,
                module_ref=item.module_ref,
                x=free.x,
                y=free.y,
                width=w,
                height=h,
                rotated=rotated,
                edges=item.edges,
            ))
            new_free, cuts = _split_free(free, w, h, kerf, horiz)
            sheet.unused.extend(new_free)
            sheet.cuts.extend(cuts)

        result.sheets.extend(active_sheets)

    return result


def from_nesting_parts(parts) -> List[CutItem]:
    """Converte uma sequência de `NestingPart` (ou objetos compatíveis) em `CutItem` para o OpCut."""
    out: List[CutItem] = []
    for p in parts:
        if getattr(p, 'is_hardware', False) or getattr(p, 'cut_exclude', False):
            continue
        if str(getattr(p, 'component', '')).upper() in ('FER', 'HARDWARE', 'FERRAGEM'):
            continue
        grain = str(getattr(p, 'grain_direction', 'NONE') or 'NONE').upper()
        edges = getattr(p, 'edges', (0.0, 0.0, 0.0, 0.0))
        edges_t = tuple(float(e or 0.0) for e in list(edges)[:4])
        if len(edges_t) < 4:
            edges_t = edges_t + (0.0,) * (4 - len(edges_t))
        out.append(CutItem(
            id=str(getattr(p, 'uid', None) or getattr(p, 'id', '')),
            label=str(getattr(p, 'name', 'Peça')),
            width=float(getattr(p, 'width', 0.0)),
            height=float(getattr(p, 'height', 0.0)),
            quantity=int(getattr(p, 'quantity', 1)),
            thickness=float(getattr(p, 'thickness', 15.0)),
            material=str(getattr(p, 'material', 'MDF Padrão') or 'MDF Padrão'),
            can_rotate=(grain == 'NONE'),
            module_ref=str(getattr(p, 'module_ref', '') or ''),
            edges=edges_t,
        ))
    return out
