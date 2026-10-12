"""Elemento tocado e as medidas dele (largura, altura e profundidade), para o aviso na viewport e o Redimensionar.

`element(obj)` devolve o elemento que o clique representa e como medir:
- módulo, frente e peça: o módulo (as medidas da biblioteca, `editing.get_dimension`);
- porta: a medida da folha (80 × 210, como o campo da porta); janela, geometria e obstáculo: as da caixa;
- parede: comprimento, pé-direito e espessura;
- o resto: o grupo de peças de topo (SketchUp, biblioteca de objetos) ou o próprio objeto, pela caixa nos eixos dele.
Cotas e anotações não contam.
"""

from collections import namedtuple

import bpy  # type: ignore

from . import classify, editing

Element = namedtuple('Element', 'obj info label')

_GN_KINDS = (classify.MODULE, classify.ROOM_DOOR, classify.WINDOW, classify.GEOMETRY, classify.OBSTACLE)


def element(obj):
    """O elemento que `obj` representa, ou None (nada selecionado, cota)."""
    info = classify.classify(obj) if obj is not None else None
    if info is None or info.kind == classify.ANNOTATION:
        return None
    if info.kind in (classify.FRONT, classify.PART):
        info = classify.classify(info.root)
    if info.kind in _GN_KINDS or info.kind == classify.WALL:
        return Element(info.obj, info, classify.KIND_LABELS[info.kind])
    target = classify.free_group(obj) or obj
    return Element(target, info, classify.KIND_LABELS[classify.OTHER])


def _door_kind(cage):
    from ..openings import sync
    return sync.kind_of(cage)


def box_size(obj):
    """(largura, altura, profundidade) da caixa do objeto nos eixos dele, com a escala."""
    from ..aggregates import group
    corners = group.object_corners(obj, bpy.context.evaluated_depsgraph_get())
    scale = obj.matrix_world.to_scale()
    x, y, z = (max(c[i] for c in corners) - min(c[i] for c in corners) for i in range(3))
    return abs(x * scale.x), abs(z * scale.z), abs(y * scale.y)


def size(el):
    """(largura, altura, profundidade) do elemento, em metros."""
    info = el.info
    if info.kind == classify.WALL and info.library == 'HB':
        return editing.get_wall(info, 'length'), editing.get_wall(info, 'height'), editing.get_wall(info, 'thickness')
    if info.kind in _GN_KINDS:
        # Porta HB: `get_dimension` já devolve a medida da folha (BUG-20261011-IDPP).
        return tuple(editing.get_dimension(info, f) for f in ('width', 'height', 'depth'))
    return box_size(el.obj)
