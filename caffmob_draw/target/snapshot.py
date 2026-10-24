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
    __slots__ = ('signature', 'target', 'objects')

    def __init__(self, signature, target, objects):
        self.signature = signature
        self.target = target
        self.objects = objects


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
    target = resolver.resolve(active, selected)
    objects = {o.session_uid: o for o in ([active] if active is not None else []) + selected}
    _cache[key] = _Entry(sig, target, objects)
    return target


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
