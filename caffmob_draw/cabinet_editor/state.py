"""Estado do editor de armário e o histórico do rascunho (feature 004, T009; D-21). Python puro, sem `bpy`.

O módulo é editado ao vivo; o rascunho é a pilha de instantâneos `EditorState` (medidas + personalização da 003 como
dicionário + estrutura e divisões da 006). Desfazer e refazer no editor devolvem um instantâneo, que a ponte com a cena reaplica. O instantâneo
inicial é o que Cancelar reaplica. O histórico é o mesmo do editor de paredes, com a assinatura deste estado.
"""

import copy
import json
from dataclasses import dataclass, field

from ..walls2d import history as _history

PRECISION = 6       # casas (m) na assinatura: 1 µm


@dataclass
class EditorState:
    dimensions: tuple = (0.0, 0.0, 0.0)      # largura, altura, profundidade (m)
    spec: dict = field(default_factory=dict)
    structure: dict = field(default_factory=dict)     # papel → {removed, mode, thickness, material} (feature 006)
    divisions: list = field(default_factory=list)     # [{uid, space, orientation, offset, …}] (feature 006)
    extras: dict = field(default_factory=dict)        # árvore de extras da Estrutura {kind: {enabled, value}} (008)
    slides: dict = field(default_factory=dict)        # deslizantes {family, style, leaves, invert, opens} (008)
    interiors: list = field(default_factory=list)     # internos [{catalog_id, space, …}] (008)
    backs: dict = field(default_factory=dict)         # fundo {mode, setback, auto} (008)
    assembly: str = ""                                # montagem do armário CAFFMob; vazio nas outras bibliotecas (012)
    structure_id: str = ""                            # estrutura de caixa do CAFFMob; vazio = construção antiga (015)
    present: dict = field(default_factory=dict)       # chapas da caixa presentes do CAFFMob {papel: bool} (015)

    def copy(self):
        return copy.deepcopy(self)


def _rounded(value):
    if isinstance(value, float):
        return round(value, PRECISION)
    if isinstance(value, dict):
        return {k: _rounded(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_rounded(v) for v in value]
    return value


def signature(state):
    dims = [round(float(v), PRECISION) for v in state.dimensions]
    return json.dumps({"dims": dims, "spec": state.spec, "structure": _rounded(state.structure),
                       "divisions": _rounded(state.divisions), "extras": _rounded(state.extras),
                       "slides": _rounded(state.slides), "interiors": _rounded(state.interiors),
                       "backs": _rounded(state.backs), "assembly": state.assembly,
                       "structure_id": state.structure_id, "present": state.present}, sort_keys=True, default=str)


class Draft:
    """Instantâneo inicial + histórico do rascunho."""

    def __init__(self, initial):
        self.initial = initial.copy()
        self.current = initial.copy()
        self.history = _history.History(self.current, signature=signature)

    def checkpoint(self, state):
        self.current = state.copy()
        return self.history.checkpoint(self.current)

    def undo(self):
        state = self.history.undo()
        if state is not None:
            self.current = state
        return state

    def redo(self):
        state = self.history.redo()
        if state is not None:
            self.current = state
        return state

    def dirty(self):
        return signature(self.current) != signature(self.initial)

    def apply_point(self):
        """Aplicar (feature 008, D-04): o estado atual vira a referência do Cancelar e o histórico recomeça dele."""
        self.initial = self.current.copy()
        self.history = _history.History(self.current, signature=signature)
