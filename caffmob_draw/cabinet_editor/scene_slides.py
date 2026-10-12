"""Portas de correr (deslizantes) na cena (feature 008, T026; RN-13b, D-18).

Reaproveita a 007: os trilhos formam um grupo **FRAME** ("Deslizantes") filho da raiz, e cada folha é um `CabinetPart`
(componente `POR`) num grupo **LEAF** de correr. Abrir para na lateral e nas divisões do armário e fechar para no
montante da outra folha (batentes da 007). As folhas abrem para o centro. Reinserir troca o conjunto inteiro.

O estado (`slides`) fica no grupo FRAME: `{item, leaves, invert, opens}`.
"""

import json

import bpy  # type: ignore

from ..aggregates import convert, group, leaf
from . import scene_divisions, scene_parts
from . import slides as sl

FRAME_TAG = 'btm_slides'
TRACK_NAMES = ("Trilho Inferior", "Trilho Superior")
TRACK_CODES = ("TRILHO_INF", "TRILHO_SUP")


def frame_of(root):
    return next((o for o in root.children if o.get(FRAME_TAG)), None)


def state_of(root):
    frame = frame_of(root)
    if frame is None:
        return {}
    data = json.loads(frame.get(FRAME_TAG) or "{}")
    data["opens"] = [round(s.btm_aggregate.open_value, 6) for s in _sashes(frame)]
    return data


def _sashes(frame):
    return sorted((o for o in frame.children_recursive if group.is_group(o) and o.btm_group.kind == 'LEAF'),
                  key=lambda o: o.name)


def clear(root):
    frame = frame_of(root)
    if frame is None:
        return
    for sash in _sashes(frame):
        if sash.btm_aggregate.is_aggregate:
            convert.unconvert(sash)
    bpy.context.view_layer.update()
    victims = [frame] + list(frame.children_recursive)
    victims += [o for o in root.children if getattr(o, 'btm_extra', None) is not None and o.btm_extra.is_extra
                and o.btm_extra.kind in ('SLIDE_TRACK', 'SLIDE_LEAF')]
    for obj in victims:
        if obj.name in bpy.data.objects:
            bpy.data.objects.remove(obj, do_unlink=True)


def missing_depth(context, root, leaves):
    spaces = scene_divisions.roots(context, root)
    if not spaces:
        return None
    return sl.missing_depth(spaces[min(spaces)], leaves)


def apply(context, root, wanted):
    """Deixa os deslizantes iguais a `wanted` ({} = sem deslizantes); devolve avisos."""
    clear(root)
    if not wanted:
        return []
    spaces = scene_divisions.roots(context, root)
    if not spaces:
        return [('NO_SPACE',)]
    space = spaces[min(spaces)]
    leaves_n = int(wanted.get("leaves", 2))
    need = sl.missing_depth(space, leaves_n)
    if need is not None:
        return [('DEPTH', need)]
    lay = sl.layout(space, leaves_n, wanted["item"], bool(wanted.get("invert")))
    tracks = [scene_parts.make_box(root, TRACK_NAMES[i], t.box, 'SLIDE_TRACK', hardware=TRACK_CODES[i],
                                   catalog_id=wanted["item"]) for i, t in enumerate(lay.tracks)]
    bpy.context.view_layer.update()
    frame = group.create_group(tracks, 'FRAME', "Deslizantes")
    frame[FRAME_TAG] = json.dumps({"item": wanted["item"], "leaves": leaves_n,
                                   "invert": bool(wanted.get("invert"))}, sort_keys=True)
    center = (space.lo[0] + space.hi[0]) / 2.0
    created = []
    for spec in lay.leaves:
        part = scene_parts.make_part(root, f"Folha Deslizante {spec.index + 1}", spec.box, 'SLIDE_LEAF', 'POR',
                                     catalog_id=wanted["item"], slot=spec.index)
        bpy.context.view_layer.update()
        sash = group.create_group([part], 'LEAF', f"Folha {spec.index + 1}")
        world = sash.matrix_world.copy()
        sash.parent = frame
        sash.matrix_parent_inverse = frame.matrix_world.inverted()
        sash.matrix_world = world
        created.append((sash, spec))
    bpy.context.view_layer.update()
    opens = list(wanted.get("opens") or [])
    warnings = []
    for index, (sash, spec) in enumerate(created):
        mid = (spec.box[0][0] + spec.box[1][0]) / 2.0
        leaf.make_leaf(sash, frame, 'SLIDE', slide_dir='POS_X' if mid < center else 'NEG_X', travel=0.5)
        if leaf.measure_free_travel(sash) < sl.TRACK_HEIGHT:          # parada logo no início: algo no caminho
            warnings.append(("BLOCKED", sash.name, sash.get(leaf.FREE_CONTACT_KEY, "")))
        if index < len(opens) and opens[index] > 0.0:
            sash.btm_aggregate.open_value = opens[index]
    return warnings


def reflow(context, root):
    state = state_of(root)
    if not state:
        return []
    return apply(context, root, state)
