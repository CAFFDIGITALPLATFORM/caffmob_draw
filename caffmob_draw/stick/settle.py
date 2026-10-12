"""Depois que o movimento termina (feature 004; D-04, D-06, D-16, RF-12, RF-13, RF-19, RF-23).

O handler de `apply.py` anota os objetos que se moveram; quando nenhum movimento modal está rodando (G nativo,
posicionamento das bibliotecas, mover do plugin), `run` trata cada um uma vez:
1. item grudado → volta ao plano da face na posição em que foi solto (RF-13);
2. módulo novo posto na parede pela biblioteca (filho da parede, sem vínculo) → vira elemento filho dela (RF-19);
3. módulo ou geometria solto perto de uma face plana → ímã (RF-12), com um passo de desfazer próprio;
4. verificação de colisão só com os vizinhos do que se moveu; colidindo, avisa e destaca, sem mover (RF-23).
"""

import bpy  # type: ignore

from ..data.i18n import tr
from ..selection import classify
from . import apply, link, magnet, migrate

# Modais que movem objetos: o assentar espera eles terminarem.
_MOVE_IDS = {'caffmob.stick_move', 'caffmob.stick_to_face', 'caffmob.aggregate_move', 'caffmob.move_on_wall',
             'caffmob.move_over_drag', 'caffmob.move_over_dialog', 'caffmob.cabinet_editor_modal'}
_MAGNET_KINDS = (classify.MODULE, classify.GEOMETRY)


def _idname(op):
    name = getattr(op, 'bl_idname', '') or ''
    if '_OT_' in name:
        prefix, rest = name.split('_OT_', 1)
        return f"{prefix.lower()}.{rest}"
    return name


def is_move_operator(op):
    name = _idname(op)
    if name.startswith('transform.') or name in _MOVE_IDS:
        return True
    from .. import hb_placement
    return isinstance(op, hb_placement.PlacementMixin)


def _undo_push(message):
    try:
        window = bpy.context.window_manager.windows[0]
        with bpy.context.temp_override(window=window):
            bpy.ops.ed.undo_push(message=message)
    except (IndexError, RuntimeError, AttributeError):
        pass


_settled = {}      # nome → matriz de mundo da última vez que o item foi tratado aqui


def _world_key(obj):
    return tuple(round(v, 6) for row in obj.matrix_world for v in row)


def returned_to_rest(obj):
    """O movimento terminou onde o item já estava (Esc no G, desfazer): não é gesto novo, o ímã não age
    (feature 005, prévia do ímã: cancelar não gruda)."""
    return _settled.get(obj.name) == _world_key(obj)


def run(names):
    moved_roots = []
    stuck_now = []
    for name in names:
        obj = bpy.data.objects.get(name)
        if obj is None:
            continue
        if returned_to_rest(obj):
            continue
        if apply.linked(obj):
            apply.project(obj)
            moved_roots.append(obj)
            continue
        if obj.btm_stick.is_stuck or obj.btm_stick.opt_out:
            continue                         # vínculo quebrado (o handler trata) ou desgrudado à mão da parede
        info = classify.classify(obj)
        if info is None or info.root is not obj or info.kind not in _MAGNET_KINDS:
            continue
        wall = migrate.wall_of(obj)
        if wall is not None:
            link.link_in_place(obj, wall, migrate.wall_side(obj, wall))
        elif magnet.try_stick(obj) is not None:
            stuck_now.append(obj)
        moved_roots.append(obj)
    for obj in moved_roots:
        if obj.name in bpy.data.objects:
            _settled[obj.name] = _world_key(obj)
    if stuck_now:
        from ..ui import save_feedback
        for obj in stuck_now:
            save_feedback.show(tr("Elemento filho de: {}").format(link.face_label(obj)))
        _undo_push(tr("Grudar"))
    if moved_roots:
        _check_collisions(moved_roots)


def _check_collisions(objs):
    try:
        from ..collision import scan
    except ImportError:
        return
    scan.check_moved(objs)
