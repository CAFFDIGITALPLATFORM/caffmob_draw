"""Resultado de colisão desatualizado (feature 004, T038; D-15, RN-14, RF-25).

Handler `depsgraph_update_post` (`@persistent`), no padrão de `cutting/stale.py`: quando um item verificado (ou
qualquer objeto dentro dele) muda de posição ou de geometria depois da verificação, liga `btm_collision.stale`.
A verificação dos itens que acabaram de se mover (assentar do grudar) tira esses itens da conta; se nada mais mudou,
o resultado volta a estar em dia. Objeto novo (que a colisão verificaria), apagado ou renomeado também deixa o
resultado desatualizado (questions.md, pergunta 34).
"""

import bpy  # type: ignore
from bpy.app.handlers import persistent  # type: ignore

_changed = set()


def reset():
    _changed.clear()


def rechecked(names):
    _changed.difference_update(names)
    state = bpy.context.window_manager.btm_collision
    if state.checked >= 0:
        state.stale = bool(_changed)


def _checked_root(obj, names):
    current = obj
    while current is not None:
        if current.name in names:
            return current.name
        current = current.parent
    return None


@persistent
def on_depsgraph_update(scene, depsgraph):
    try:
        state = bpy.context.window_manager.btm_collision
    except AttributeError:
        return
    if state.checked < 0:
        return
    names = set(state.checked_names.split("\n")) if state.checked_names else set()
    names.update(r.name_a for r in state.items)
    names.update(r.name_b for r in state.items)
    names.discard("")
    _changed.update(name for name in names if name not in bpy.data.objects)      # apagado ou renomeado
    from .scan import _kind_of
    for update in depsgraph.updates:
        if not isinstance(update.id, bpy.types.Object):
            continue
        obj = update.id.original
        root = _checked_root(obj, names)
        if root is not None:
            if update.is_updated_geometry or update.is_updated_transform:
                _changed.add(root)
        elif obj.name in scene.objects and _kind_of(obj) is not None:
            _changed.add(obj.name)                     # item novo, ou com o nome novo, fora da verificação
    if _changed and not state.stale:
        state.stale = True


def register():
    if on_depsgraph_update not in bpy.app.handlers.depsgraph_update_post:
        bpy.app.handlers.depsgraph_update_post.append(on_depsgraph_update)


def unregister():
    if on_depsgraph_update in bpy.app.handlers.depsgraph_update_post:
        bpy.app.handlers.depsgraph_update_post.remove(on_depsgraph_update)
    reset()
