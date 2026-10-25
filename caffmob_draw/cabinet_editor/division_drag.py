"""Arrastar uma divisória na vista do editor de armário (feature 067, T078; RF-106).

Clicar numa divisória e arrastar move a posição dela ao vivo; soltar grava um passo no histórico do rascunho do
editor (o Desfazer do editor volta ao antes do arraste de uma vez); Esc durante o arraste restaura a posição de
antes. O movimento respeita a faixa válida do subvão (`divisions.offset_range`), como as setas.
"""

from dataclasses import dataclass

from . import divisions as dv


@dataclass
class Drag:
    uid: str
    vertical: bool
    start: float                 # coordenada do mouse no clique (x na divisória vertical, z na horizontal), em m
    offset: float                # `offset` da divisão no clique
    state: object                # instantâneo do rascunho antes do arraste
    moved: bool = False


def division_of(s, root, board_name):
    """O objeto de divisória sob o clique (filho do módulo, com `btm_division`), ou None."""
    import bpy  # type: ignore
    obj = bpy.data.objects.get(board_name) if board_name else None
    if obj is None or obj.parent != root or not obj.btm_division.is_division:
        return None
    return obj


def begin(context, s, root, obj, x, z):
    from . import bridge
    roots, core, _raw, _names = bridge.division_context(context, root)
    division = next((d for d in core if d.uid == obj.btm_division.uid), None)
    if division is None:
        return None
    vertical = obj.btm_division.orientation == dv.VERTICAL
    return Drag(division.uid, vertical, x if vertical else z, division.offset, s.draft.current.copy())


def update(context, s, root, drag, x, z):
    """Leva a divisória à posição do mouse (sem passo no histórico); devolve o `offset` aplicado."""
    from . import bridge, scene_divisions
    roots, core, _raw, _names = bridge.division_context(context, root)
    division = next((d for d in core if d.uid == drag.uid), None)
    _leaves, cuts, _orphans = dv.resolve(roots, core)
    if division is None or division.uid not in cuts:
        return None
    lo, hi = dv.offset_range(cuts[division.uid][0], division)
    offset = min(max(drag.offset + ((x if drag.vertical else z) - drag.start), lo), max(lo, hi))
    if abs(offset - division.offset) < 1e-6:
        return offset
    bridge.edit(context, root, 'EDIT_DIVISION', {'uid': drag.uid, 'offset': offset})
    scene_divisions.reflow(context, root, force=True)
    drag.moved = True
    return offset


def end(context, s, root, drag, refresh):
    """Soltar: um passo no histórico do rascunho, só se a divisória andou."""
    if drag.moved:
        refresh(context, s, checkpoint=True)
    return drag.moved


def cancel(context, s, root, drag, refresh):
    """Esc: volta ao instantâneo de antes do arraste, sem passo no histórico."""
    from . import bridge
    if drag.moved:
        bridge.apply_state(context, root, drag.state)
        refresh(context, s, checkpoint=False)
        s.draft.current = drag.state
    return True
