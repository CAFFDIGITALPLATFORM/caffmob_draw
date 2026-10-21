"""Redimensionar a largura do elemento selecionado (menu do botão direito).

O pai muda pela medida própria dele, sem distorcer a estrutura:
- módulo: a largura da biblioteca (`editing.set_dimension`);
- porta: a largura da folha (a caixa ganha o marco e a porta real é refeita); janela: a largura da caixa;
- geometria livre: `btm_geometry.width`; parede: o comprimento;
- grupo de peças (SketchUp, biblioteca de objetos) e malha solta: esticados em X (os filhos vão junto).

Os agregados (003) do pai e das peças dele são esticados no eixo da largura do pai e reposicionados na proporção:
cada peça que tem agregados é medida antes e depois, e a razão entre as larguras vale para os agregados dela.
Agregado preso numa face lateral (normal em X) só é reposicionado.
"""

import bpy  # type: ignore

from .. import hb_types
from ..data.i18n import tr
from . import classify, editing, element_size

MIN_WIDTH, MAX_WIDTH = 0.01, 100.0


def can_resize(el):
    if el is None:
        return False
    kind = el.info.kind
    if kind == classify.WALL:
        return el.info.library == 'HB'
    if kind == classify.MODULE:
        return 'width' in editing.editable_dimensions(el.info)
    if kind in (classify.FLOOR, classify.CEILING):
        return False
    if classify.btm_kind(el.info.obj) == 'OPENING':
        return False                          # janela BTM: sem caminho próprio de redimensionar (pergunta 21)
    return True


def _parents_with_aggregates(root):
    from ..aggregates import apply
    return [o for o in [root] + list(root.children_recursive) if apply.aggregates_of(o)]


def _width_x(obj):
    from ..aggregates import apply
    lo, hi = apply.local_box(obj)
    return hi[0] - lo[0]


def _stretch_aggregate(child, factor, u, v):
    """Estica o agregado no eixo X do pai e leva a posição (`u`, `v` de antes da mudança) na mesma proporção."""
    from ..aggregates import apply, limits
    agg = child.btm_aggregate
    if agg.kind == 'LEAF':
        return
    normal, _sign, u_axis, v_axis = limits.face_axes(agg.face)
    if normal != 0:
        to_parent = (agg.parent_ref.matrix_world.inverted() @ child.matrix_world).to_3x3()
        axis = max(range(3), key=lambda j: abs(to_parent.col[j].normalized()[0]))    # eixo local ao longo do X do pai
        scale = child.scale.copy()
        scale[axis] *= factor
        child.scale = scale
        size, rest = list(agg.size), list(agg.rest_offset)
        size[0] *= factor
        rest[0] *= factor
        agg.size, agg.rest_offset = size, rest
    apply._write(child, 'u', u * factor if u_axis == 0 else u)
    apply._write(child, 'v', v * factor if v_axis == 0 else v)
    apply.update_position(child)


def _stretched(el):
    """O elemento não tem largura própria: é esticado em X (grupo de peças, malha solta, obstáculo sem caixa)."""
    obj = el.obj
    if el.info.kind == classify.GEOMETRY:
        return getattr(obj, 'btm_geometry', None) is None
    if el.info.kind == classify.OBSTACLE:
        return not getattr(getattr(obj, 'home_builder', None), 'mod_name', '')
    return el.info.kind == classify.OTHER


def _set_width(context, el, width):
    info = el.info
    obj = el.obj
    if _stretched(el):
        current = element_size.size(el)[0]
        if current <= 1e-9:
            raise ValueError(tr("Valor Inválido: o objeto não tem largura para redimensionar."))
        scale = obj.scale.copy()
        scale.x *= width / current
        obj.scale = scale
    elif info.kind == classify.MODULE:
        editing.set_dimension(context, info, 'width', width)
    elif info.kind in (classify.ROOM_DOOR, classify.WINDOW):
        from ..operators import doors_windows as dw
        if info.kind == classify.ROOM_DOOR:
            width = dw._leaf_to_hole(element_size._door_kind(obj), 'X', width)
        hb_types.GeoNodeCage(obj).set_input('Dim X', width)
        dw._sync_opening(context, obj)
    elif info.kind == classify.WALL:
        editing.set_wall(info, 'length', width)
    elif info.kind == classify.GEOMETRY:
        obj.btm_geometry.width = width
    else:
        hb_types.GeoNodeObject(obj).set_input('Dim X', width)


def resize(context, el, width):
    """066 RF-012: largura e agregados voltam juntos se o novo corpo penetrar."""
    if not can_resize(el) or not MIN_WIDTH <= width <= MAX_WIDTH:
        return _resize(context, el, width)       # mantém a validação e as mensagens de domínio
    if el.info.library == 'AUTHORED':
        return editing.set_dimension(context, el.info, 'width', width)
    from ..collision import guard
    old = element_size.size(el)[0]
    return guard.reconfigure(el.obj, lambda: _resize(context, el, width), lambda: _resize(context, el, old))


def _resize(context, el, width):
    """Muda a largura do elemento para `width` (m) e adapta os agregados; levanta ValueError se não der."""
    if not can_resize(el):
        raise ValueError(tr("Valor Inválido: este elemento não pode ser redimensionado por aqui."))
    if not MIN_WIDTH <= width <= MAX_WIDTH:
        raise ValueError(tr("Valor Inválido: a largura deve estar entre {} e {} m.").format(MIN_WIDTH, MAX_WIDTH))
    from ..aggregates import apply
    # Esticado em X, os filhos acompanham a escala do pai; com largura própria, os agregados são adaptados aqui.
    # `u`/`v` guardados antes: o gancho dos agregados ajusta a posição ao limite assim que o pai muda.
    before = {} if _stretched(el) else {
        o.name: (_width_x(o), {c.name: (c.btm_aggregate.u, c.btm_aggregate.v) for c in apply.aggregates_of(o)})
        for o in _parents_with_aggregates(el.obj)}
    _set_width(context, el, width)
    context.view_layer.update()
    for name, (old, positions) in before.items():
        parent = bpy.data.objects.get(name)
        if parent is None or old <= 1e-9:
            continue
        factor = _width_x(parent) / old
        if abs(factor - 1.0) < 1e-6:
            continue
        for child in apply.aggregates_of(parent):
            if child.name in positions:
                _stretch_aggregate(child, factor, *positions[child.name])
    context.view_layer.update()
