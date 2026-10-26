"""Snapshot do alvo da seleção (feature 067, D-03, D-04; RF-001).

O alvo é resolvido fora do draw: no msgbus da troca do ativo (`LayerObjects.active`) e no `depsgraph_update_post`,
com a assinatura `(session_uid do ativo, session_uids selecionados, revisão)`. A revisão sobe quando um objeto muda
no depsgraph, e é isso que faz o snapshot ser refeito depois de uma edição. O cache é por `(cena, view layer)`.

- `current(context)`: para draw, getter e poll. Só lê; devolve `None` ("calculando") se a seleção mudou e o
  snapshot ainda não foi refeito.
- `ensure(context)`: para operadores e ensaios. Refaz se precisar.
- `object_for(context, uid)`: o objeto de um `session_uid` do snapshot, para getters e setters (índice refeito com o
  snapshot; recai na busca no view layer).

Undo e abertura de arquivo apagam o cache: as referências a objetos não sobrevivem a eles.
"""

import bpy  # type: ignore
from bpy.app.handlers import persistent  # type: ignore

from . import resolver

_OWNER = object()
_cache = {}
_revision = [0]


class _Entry:
    __slots__ = ('signature', 'target', 'objects', 'pose')

    def __init__(self, signature, target, objects):
        self.signature = signature
        self.target = target
        self.objects = objects
        self.pose = None


def _pose(obj):
    return tuple(round(v, 6) for row in obj.matrix_world for v in row) if obj is not None else None


def _key(context):
    scene, view_layer = context.scene, context.view_layer
    if scene is None or view_layer is None:
        return None
    return scene.as_pointer(), view_layer.name


def signature(view_layer):
    active = view_layer.objects.active
    selected = tuple(sorted(o.session_uid for o in view_layer.objects.selected))
    return (active.session_uid if active is not None else 0, selected, _revision[0])


def refresh(context):
    """Resolve de novo se a assinatura mudou; devolve o alvo (ou None sem seleção)."""
    key = _key(context)
    if key is None:
        return None
    view_layer = context.view_layer
    sig = signature(view_layer)
    entry = _cache.get(key)
    if entry is not None and entry.signature == sig:
        return entry.target
    active = view_layer.objects.active
    selected = list(view_layer.objects.selected)
    from ..cladding import ops_adopt
    target = resolver.resolve(active, selected, cladding_controller=ops_adopt.controller_for)
    objects = {o.session_uid: o for o in ([active] if active is not None else []) + selected}
    _cache[key] = _Entry(sig, target, objects)
    if target is not None and target.kind in resolver.SHEET_KINDS:
        target = _with_measures(context, target)
    elif target is not None and target.kind == resolver.MULTIPLE:
        target = _with_multi(context, target)
    elif target is not None and target.kind == resolver.OPENING and target.library == 'MOBI':
        target = _with_mobi_owner(context, target)
    elif target is not None and target.kind == resolver.WALL and target.library == 'MOBI':
        target = _with_mobi_wall(context, target)
    elif target is not None and target.kind == resolver.OPENING and target.detail == 'DOOR':
        import dataclasses
        from ..openings.ops import door_of
        target = dataclasses.replace(target, has_leaf=door_of(object_for(context, target.uid)) is not None)
    elif target is not None and target.kind == resolver.CLADDING:
        _load_cladding_draft(context, target)
    if target is not None and target.kind in FINISH_KINDS:
        target = _with_finish(context, target)
    entry = _cache[key]
    entry.target = target
    entry.pose = _pose(object_for(context, target.uid)) if target is not None else None
    return target


# Tipos com seção Acabamentos (onda 2, RF-043).
FINISH_KINDS = frozenset({resolver.MODULE, resolver.PART, resolver.MEMBER, resolver.FRONT, resolver.LEAF,
                          resolver.GEOMETRY, resolver.OTHER, resolver.MULTIPLE})


def _with_finish(context, target):
    """Material efetivo de cada domínio, lido das faces e peças (fora do draw)."""
    import dataclasses
    from ..customize import finish
    obj = object_for(context, target.uid)
    if obj is None:
        return target
    if target.kind == resolver.MULTIPLE:
        pieces = [o for o in (object_for(context, u) for u in target.selected_uids) if o is not None
                  and o.type == 'MESH']
        owner = finish.owner_of(obj)
        part = True
    elif target.kind == resolver.MODULE:
        owner, pieces, part = obj, None, False
    else:
        owner = finish.owner_of(obj)
        pieces = [obj] if obj.type == 'MESH' else []
        part = owner is not obj
    if owner is None or (pieces is not None and not pieces):
        return target
    try:
        summary = finish.summary(owner, pieces)
        # Linha no resumo já prova papel no dono; só sem linha é preciso olhar as outras peças.
        roles = any(rows for _m, rows in summary.values()) or finish.has_roles(owner)
    except (AttributeError, ReferenceError, RuntimeError):
        return target
    rows = tuple((domain, summary[domain][0], summary[domain][1]) for domain in summary if summary[domain][1])
    band_state = ()
    try:
        from ..edgeband import ops as band_ops
        state, missing = band_ops.state_for(owner, obj if part and target.kind != resolver.MULTIPLE else None)
        band_state = (state, len(missing))
    except (AttributeError, ReferenceError, RuntimeError, ValueError):
        pass
    return dataclasses.replace(target, finish=rows, finish_roles=roles, finish_scope_part=part,
                               edgeband_state=band_state)


def _load_cladding_draft(context, target):
    """O rascunho do painel recebe os valores do revestimento selecionado (só quando troca de revestimento)."""
    draft = getattr(context.window_manager, 'btm_cladding_draft', None)
    root = object_for(context, target.uid)
    if draft is None or root is None or draft.uid == root.btm_cladding.uid:
        return
    from ..cladding.ops import copy_settings
    copy_settings(root.btm_cladding, draft)
    draft.uid = root.btm_cladding.uid


def pose_matches(context, target):
    """O objeto do alvo continua onde estava quando o snapshot foi feito (D-04: o setter confere a pose)."""
    key = _key(context)
    entry = _cache.get(key) if key is not None else None
    if entry is None or entry.target is None or entry.target.uid != target.uid:
        return False
    return entry.pose == _pose(object_for(context, target.uid))


def _with_mobi_owner(context, target):
    """Abertura do CAFF MOBI (067 onda 8, D-45): dono "em <parede> · trecho N", achado no documento da cena pelo trecho
    da abertura (ela não é filha da parede). Roda só quando o snapshot é refeito, nunca no desenho."""
    import dataclasses
    import json
    from ..data.i18n import tr
    from ..mobi.editar_v2_core import dono_da_abertura
    obj = object_for(context, target.uid)
    try:
        documento = json.loads(context.scene.get('caffmob_ambiente') or '{}')
    except ValueError:
        documento = {}
    dono = dono_da_abertura(documento, obj.get('caffmob_id')) if obj is not None and documento.get('aberturas') else None
    if dono is None:
        return dataclasses.replace(target, has_leaf=target.detail == 'DOOR')
    parede, numero = dono
    wall = next((o for o in context.scene.objects
                 if o.get('caffmob_tipo') == 'parede' and o.get('caffmob_id') == parede['id']), None)
    nome = tr("{} · trecho {}").format(wall.name if wall is not None else tr("Parede"), numero)
    return dataclasses.replace(target, owner_uid=wall.session_uid if wall is not None else 0, owner_name=nome,
                               path=(nome, target.name), has_leaf=target.detail == 'DOOR')


def _with_mobi_wall(context, target):
    """Parede do CAFF MOBI (067 onda 8, D-43): trechos e aberturas lidos do JSON que a montagem gravou no objeto."""
    import dataclasses
    import json
    obj = object_for(context, target.uid)
    try:
        parede = json.loads(obj.get('caffmob_parede') or '{}') if obj is not None else {}
        aberturas = json.loads(obj.get('caffmob_aberturas') or '[]') if obj is not None else []
    except ValueError:
        parede, aberturas = {}, []
    trechos = tuple((k + 1, s['comprimento']) for k, s in enumerate(parede.get('segmentos', [])))
    return dataclasses.replace(target, mobi_trechos=trechos, mobi_aberturas=tuple(
        (a['id'], a['tipo'], a['largura'], a['altura']) for a in aberturas))


def sheet_target(context, obj):
    """Alvo com medidas de um objeto qualquer da seleção (edição em lote da seleção múltipla)."""
    target = resolver.resolve(obj, [obj])
    return _with_measures(context, target) if target is not None and target.kind in resolver.SHEET_KINDS else target


def _with_multi(context, target):
    import dataclasses
    values = []
    for uid in target.selected_uids:
        obj = object_for(context, uid)
        sheet = sheet_target(context, obj) if obj is not None else None
        values.append(sheet.measures.thickness.value if sheet is not None and sheet.measures is not None else None)
    return dataclasses.replace(target, multi_thickness=tuple(values))


def _with_measures(context, target):
    """Medidas semânticas da chapa (D-11): caixa local da malha e matriz mundial, no referencial do dono."""
    import dataclasses
    from . import part_geometry
    obj = object_for(context, target.uid)
    if obj is None or obj.type != 'MESH':
        return target
    corners = [tuple(c) for c in obj.bound_box]
    low = tuple(min(c[i] for c in corners) for i in range(3))
    high = tuple(max(c[i] for c in corners) for i in range(3))
    owner = object_for(context, target.owner_uid) if target.owner_uid else None
    reference = owner.matrix_world.to_3x3().normalized() if owner is not None else None
    try:
        measures = part_geometry.measure(low, high, obj.matrix_world, reference)
    except part_geometry.PartGeometryError as exc:
        return dataclasses.replace(target, measure_error=str(exc))
    return dataclasses.replace(target, measures=measures)


def current(context):
    key = _key(context)
    entry = _cache.get(key) if key is not None else None
    if entry is None or entry.signature != signature(context.view_layer):
        return None
    return entry.target


def ensure(context):
    return refresh(context)


def object_for(context, uid):
    if not uid:
        return None
    key = _key(context)
    entry = _cache.get(key) if key is not None else None
    if entry is not None:
        obj = entry.objects.get(uid)
        if obj is not None:
            try:
                if obj.session_uid == uid:
                    return obj
            except ReferenceError:
                entry.objects.pop(uid, None)
    view_layer = context.view_layer
    for obj in (view_layer.objects if view_layer is not None else ()):
        if obj.session_uid == uid:
            if entry is not None:
                entry.objects[uid] = obj
            return obj
    return None


def forget():
    _cache.clear()


# Atualização ----------------------------------------------------------------------------------------------------

def _on_active_changed(*_args):
    try:
        refresh(bpy.context)
    except (AttributeError, ReferenceError):
        forget()


@persistent
def _on_depsgraph_update(_scene, depsgraph=None):
    if depsgraph is not None and any(isinstance(u.id, bpy.types.Object) for u in depsgraph.updates):
        _revision[0] += 1
    _on_active_changed()


@persistent
def _on_reset(*_args):
    forget()
    _subscribe()


def _subscribe():
    bpy.msgbus.clear_by_owner(_OWNER)
    bpy.msgbus.subscribe_rna(key=(bpy.types.LayerObjects, "active"), owner=_OWNER, args=(),
                             notify=_on_active_changed)


_HANDLERS = (
    (bpy.app.handlers.depsgraph_update_post, _on_depsgraph_update),
    (bpy.app.handlers.undo_post, _on_reset),
    (bpy.app.handlers.redo_post, _on_reset),
    (bpy.app.handlers.load_post, _on_reset),
)


def register():
    for handlers, handler in _HANDLERS:
        if handler not in handlers:
            handlers.append(handler)
    _subscribe()


def unregister():
    for handlers, handler in _HANDLERS:
        if handler in handlers:
            handlers.remove(handler)
    bpy.msgbus.clear_by_owner(_OWNER)
    forget()
