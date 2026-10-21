"""Medidas laterais do item ativo, pela vista (feature 066, T040; D-10, RF-013 a RF-020, RF-023).

Com `btm_settings.show_side_dimensions` ligado e um item ativo com corpo, desenha no máximo duas cotas: da superfície
do item até o primeiro obstáculo à esquerda e à direita da vista (`measure/side.py`), no mesmo desenho das cotas de
posicionamento (`hb_placement.draw_placement_dimensions`: unidade, precisão, cor, traço e escala de interface).
Sem eixo lateral estável, nada é desenhado; lado livre não tem cota.

Desenha só na viewport da operação, capturada ao ligar a chave ou mover o ativo (RF-020).
Nada durante o render nem com as sobreposições desligadas.
A chave não mexe na colisão, e a colisão não mexe nela (RF-013).
"""

import bpy  # type: ignore
from mathutils import Vector  # type: ignore

_handles = []
_owner = [None]        # ponteiro da área que desenha as cotas


def claims(area_ptr, alive):
    """A área `area_ptr` desenha? A dona continua enquanto existir; sem dona viva, a primeira que pedir fica."""
    owner = _owner[0]
    if owner is None or owner not in alive:
        _owner[0] = owner = area_ptr
    return owner == area_ptr


def release():
    _owner[0] = None


def bind(context):
    """Prende à área da ação; callbacks de desenho nunca roubam uma dona ainda viva."""
    area = getattr(context, 'area', None)
    if area is not None and area.type == 'VIEW_3D':
        _owner[0] = area.as_pointer()


def update_enabled(settings, context):
    release()
    if settings.show_side_dimensions:
        bind(context)
    for window in context.window_manager.windows:
        for area in window.screen.areas:
            if area.type == 'VIEW_3D':
                area.tag_redraw()


def _alive(context):
    try:
        return {a.as_pointer() for w in context.window_manager.windows for a in w.screen.areas
                if a.type == 'VIEW_3D'}
    except AttributeError:
        return set()


def _mover(obj):
    from ..selection import classify
    return classify.movable_root(obj) or obj


def _plane_normal(obj):
    """Item na parede: o plano de trabalho é a face da parede; solto, o piso."""
    node = obj.parent
    while node is not None:
        if node.get('IS_WALL_BP'):
            return tuple(node.matrix_world.to_3x3().col[1].normalized())
        node = node.parent
    return (0.0, 0.0, 1.0)


def specs(context, view_right):
    """Cotas (`PlacementDimSpec`) do ativo para a vista com a direita `view_right`; lista vazia sem cota válida."""
    from ..collision import guard, rules
    from ..data import units
    from ..hb_placement import PlacementDimSpec
    from ..measure import side
    obj = context.active_object
    if obj is None or not obj.select_get():
        return []
    mover = _mover(obj)
    depsgraph = context.evaluated_depsgraph_get()
    guard._index.refresh(context.scene, depsgraph, {})
    body = guard._body(mover, depsgraph)
    if not body:
        return []
    axis = side.lateral_axis(tuple(view_right), plane_normal=_plane_normal(mover))
    if axis is None:
        return []
    skip = guard._subtree_uids([mover])
    everywhere = ((-1.0e9,) * 3, (1.0e9,) * 3)
    obstacles = [e.item.box.corners() for e in guard._index.near(everywhere, skip)
                 if not any(rules.excluded(it, e.item) for it in body)]
    result = side.gaps(axis, [c for it in body for c in it.box.corners()], obstacles)
    out = []
    for gap in (result.left, result.right) if result is not None else ():
        if gap is not None:
            out.append(PlacementDimSpec(Vector(gap.start), Vector(gap.end), units.format_value(gap.value)))
    return out


class _Specs:
    def __init__(self, items):
        self._placement_dim_specs = items
        self._placement_dim_safe_labels = True


def _draw():
    context = bpy.context
    settings = getattr(context.scene, 'btm_settings', None)
    if settings is None or not settings.show_side_dimensions:
        release()
        return
    area, rv3d = context.area, context.region_data
    overlay = getattr(context.space_data, 'overlay', None)
    if area is None or rv3d is None or (overlay is not None and not overlay.show_overlays):
        return
    if bpy.app.is_job_running('RENDER'):
        return
    if not claims(area.as_pointer(), _alive(context)):
        return
    try:
        items = specs(context, rv3d.view_rotation @ Vector((1.0, 0.0, 0.0)))
    except (ReferenceError, AttributeError, ValueError):
        return
    if items:
        from ..hb_placement import draw_placement_dimensions
        draw_placement_dimensions(_Specs(items), context)


def register():
    if not _handles:
        _handles.append(bpy.types.SpaceView3D.draw_handler_add(_draw, (), 'WINDOW', 'POST_PIXEL'))


def unregister():
    while _handles:
        bpy.types.SpaceView3D.draw_handler_remove(_handles.pop(), 'WINDOW')
    release()
