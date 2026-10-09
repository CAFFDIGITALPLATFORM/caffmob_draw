"""Converter armários herdados em módulos CAFFMob (feature 012, T059; D-23, D-25, RN-13).

Para cada raiz de armário frameless, face frame ou closets:
1. lê as medidas pela caixa da raiz (o `bound_box` avaliado da caixa, no espaço dela) e o tipo da biblioteca;
2. lê a especificação pelo adaptador da personalização (`customize/adapters/<lib>.read`): frentes, gavetas,
   prateleiras;
3. traduz (`convert_core.translate`) e cria o módulo CAFFMob (`cabinet_builder.build_module`) com as chapas e a
   montagem do padrão ativo, na mesma posição, rotação e pai (a parede);
4. apaga o herdado pela exclusão em profundidade da 011 (`delete_components`), que solta os itens grudados no lugar.

Devolve um relatório por armário. Quem chama faz isso dentro de um operador com UNDO: uma etapa de desfazer para
o lote.
"""

from collections import namedtuple

import bpy  # type: ignore
from mathutils import Matrix, Vector  # type: ignore

from ..data.i18n import N_, tr
from . import convert_core, gate

Result = namedtuple('Result', 'legacy_name library module_name losses')

LIBRARY_LABELS = {'FRAMELESS': N_("Frameless"), 'FACE_FRAME': N_("Face frame"), 'CLOSETS': N_("Closets")}
AGGREGATES = 'AGGREGATES'
convert_core.LOSS_LABELS.setdefault(AGGREGATES, N_("Agregados presos ao armário"))
SPECIAL_FACE_FRAME = ('PULLOUT', 'TILT_OUT', 'INSET_PANEL', 'APPLIANCE')


def _local_box(root):
    """(mín, máx) da caixa da raiz no espaço dela, pela geometria avaliada; None se a raiz não tem volume."""
    depsgraph = bpy.context.evaluated_depsgraph_get()
    corners = [Vector(c) for c in root.evaluated_get(depsgraph).bound_box]
    lo = Vector((min(c.x for c in corners), min(c.y for c in corners), min(c.z for c in corners)))
    hi = Vector((max(c.x for c in corners), max(c.y for c in corners), max(c.z for c in corners)))
    if min(hi - lo) <= 1e-6:
        return None
    return lo, hi


def _cabinet_type(root, library):
    if library == 'FACE_FRAME' and getattr(root, 'face_frame_cabinet', None) is not None:
        return root.face_frame_cabinet.cabinet_type
    if library == 'CLOSETS' and getattr(root, 'hb_closet_starter', None) is not None:
        return root.hb_closet_starter.closet_type
    return str(root.get('CABINET_TYPE', 'BASE'))


def _openings(root):
    from ..customize import adapters
    _root, adapter = adapters.for_object(root)
    if adapter is None:
        return []
    try:
        spec = adapter.read(root)
    except Exception:         # leitor herdado com dado inesperado: converte sem frentes
        return []
    openings = []
    for item in spec.openings:
        shelves = item.interior.shelves if item.interior is not None else 0
        openings.append(convert_core.LegacyOpening(item.front or 'OPEN', item.drawer_count or 0, shelves))
    return openings


def _other_fronts(root, library):
    if library != 'FACE_FRAME':
        return []
    found = []
    for obj in root.children_recursive:
        opening = getattr(obj, 'face_frame_opening', None)
        if obj.get('IS_FACE_FRAME_OPENING_CAGE') and opening is not None and opening.front_type in SPECIAL_FACE_FRAME:
            found.append(opening.front_type)
    return found


def read_cabinet(root):
    """(`LegacyCabinet`, caixa local) do armário herdado."""
    from ..selection import classify, editing
    library = classify.module_library(root)
    box = _local_box(root)
    if box is not None:
        lo, hi = box
        width, depth, height = hi.x - lo.x, hi.y - lo.y, hi.z - lo.z
    else:
        info = classify.classify(root)
        width, height, depth = (editing.get_dimension(info, f) for f in ('width', 'height', 'depth'))
        lo, hi = Vector((0.0, -depth, 0.0)), Vector((width, 0.0, height))
    cabinet = convert_core.LegacyCabinet(
        library=library, cabinet_type=_cabinet_type(root, library), width=width, height=height, depth=depth,
        line=str(root.get('btm_line', "")), openings=_openings(root),
        other_fronts=_other_fronts(root, library))
    return cabinet, (lo, hi)


Reading = namedtuple('Reading', 'name library cabinet box world parent collection aggregates')


def _read(context, root):
    from ..selection import component
    cabinet, box = read_cabinet(root)
    collection = root.users_collection[0] if root.users_collection else context.collection
    return Reading(root.name, cabinet.library, cabinet, box, root.matrix_world.copy(), root.parent, collection,
                   len(component.own_aggregates(root)))


def _build(context, reading):
    from ..operators.cabinet_builder import build_module, standard_defaults
    from ..standards import api
    fields, losses = convert_core.translate(reading.cabinet)
    if reading.aggregates:
        losses.append(convert_core.Loss(AGGREGATES, reading.aggregates))
    found, definition = standard_defaults(context, fields['line'], fields['cabinet_type'])
    obj = build_module(context, width=fields['width'], height=fields['height'], depth=fields['depth'],
                       carcass=found.carcass, cabinet_type=fields['cabinet_type'], line=fields['line'],
                       assembly=api.active_assembly(context.scene), door_swing=fields['door_swing'],
                       shelves=fields['shelves'], role_thickness=found.thickness, definition=definition,
                       collection=reading.collection)
    # O módulo CAFFMob vai de −largura/2 a +largura/2 em X, de −profundidade a 0 em Y e de 0 à altura em Z.
    lo, hi = reading.box
    world = reading.world @ Matrix.Translation(((lo.x + hi.x) / 2.0, hi.y, lo.z))
    obj.parent = reading.parent
    if reading.parent is not None:
        obj.matrix_parent_inverse = reading.parent.matrix_world.inverted()
    obj.matrix_world = world
    return obj, losses


def convert_scene(context, roots=None):
    """Converte as raízes dadas (ou todas as da cena); devolve a lista de `Result`.

    Lê todos os armários numa avaliação só da cena, cria os módulos e só então apaga os herdados de uma vez: apagar
    um a um forçaria a reavaliar a cena (com os drivers herdados) a cada armário (princípio IX).
    """
    from ..aggregates.ops_aggregate import delete_components
    roots = list(roots) if roots is not None else gate.legacy_roots(context.scene)
    roots = [root for root in roots if root.name in bpy.data.objects and gate.is_legacy(root)]
    readings = [_read(context, root) for root in roots]
    built = [_build(context, reading) for reading in readings]
    delete_components(roots, keep_aggregates=False)
    results = []
    for reading, (obj, losses) in zip(readings, built):
        obj.name = reading.name                # o nome do armário original, que já saiu
        results.append(Result(reading.name, reading.library, obj.name, losses))
    return results


def report_lines(results):
    lines = []
    for result in results:
        head = tr("{} ({}) → {}").format(result.legacy_name, tr(LIBRARY_LABELS.get(result.library, result.library)),
                                         result.module_name)
        if not result.losses:
            lines.append(head + "  ·  " + tr("sem perdas"))
            continue
        lost = ", ".join("{} {}".format(loss.count, tr(convert_core.LOSS_LABELS.get(loss.key, loss.key)))
                         for loss in result.losses)
        lines.append(head + "  ·  " + tr("perdas: {}").format(lost))
    return lines
