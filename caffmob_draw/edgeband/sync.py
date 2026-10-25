"""Sincronia incremental da fita (feature 067, T071; D-21; RF-083).

Cada faixa guarda as chaves das bordas que cobre. Quando uma peça do componente muda (geometria ou posição dentro do
dono), as faixas do dono são refeitas a partir das bordas expostas de agora: a malha só é reescrita quando o
`params_hash` muda, e a faixa cujas bordas deixaram de existir (peça apagada ou encostada) é removida, sem fita
flutuante. O movimento do componente inteiro não pede nada: a faixa é filha do dono. O handler do depsgraph só anota;
a sincronia roda num timer, fora da avaliação.
"""

import bpy  # type: ignore
from bpy.app.handlers import persistent  # type: ignore

from . import build, core, pieces

_busy = [False]


def exposed_faces(owner, create_uids=False):
    """{chave: Face} das bordas expostas do componente agora."""
    found = pieces.boxes(owner, create_uids)
    return {face.key: face for face in core.exposed([box for box, _obj in found])}


def sync_band(obj, faces=None, remove=True):
    """Refaz uma faixa; devolve 'KEPT', 'REBUILT' ou 'REMOVED' (`remove=False`: nunca apaga, só refaz)."""
    data = obj.btm_edgeband
    owner = data.owner
    if owner is None:
        if remove:
            bpy.data.objects.remove(obj)
            return 'REMOVED'
        return 'KEPT'
    faces = exposed_faces(owner) if faces is None else faces
    current = [faces[k] for k in core.loads(data.edge_keys) if k in faces]
    if not current:
        if remove:
            bpy.data.objects.remove(obj)
            return 'REMOVED'
        return 'KEPT'
    merged = max(core.merge(current), key=lambda b: len(b.keys))
    return 'REBUILT' if build.update(obj, merged) else 'KEPT'


def sync_owner(owner):
    bands = pieces.bands_of(owner)
    if not bands:
        return {}
    faces = exposed_faces(owner)
    return {obj.name: sync_band(obj, faces) for obj in list(bands)}


def _owners_touched(depsgraph):
    owners = {}
    structural = False
    for update in depsgraph.updates:
        if isinstance(update.id, (bpy.types.Collection, bpy.types.Scene)):
            structural = True                # peça apagada não aparece como update do objeto
            continue
        obj = update.id
        if not isinstance(obj, bpy.types.Object):
            continue
        obj = obj.original
        band = getattr(obj, 'btm_edgeband', None)
        if band is not None and band.visual:
            continue
        if not (update.is_updated_geometry or update.is_updated_transform):
            continue
        owner = pieces.owner_for(obj)
        if owner is None or (obj is owner and not update.is_updated_geometry):
            continue                     # o componente inteiro andou: a faixa vai junto, como filha
        if pieces.bands_of(owner):
            owners[owner.name] = owner
    if structural:
        for obj in bpy.data.objects:
            band = getattr(obj, 'btm_edgeband', None)
            if band is not None and band.visual and band.owner is not None:
                owners[band.owner.name] = band.owner
    return list(owners.values())


_pending = set()


def flush():
    """Refaz agora as faixas dos componentes anotados (o timer chama; os ensaios também)."""
    names = list(_pending)
    _pending.clear()
    _busy[0] = True
    try:
        for name in names:
            owner = bpy.data.objects.get(name)
            if owner is None:
                continue
            try:
                sync_owner(owner)
            except (ReferenceError, RuntimeError, ValueError) as exc:
                print(f"CAFFMob Draw: fita de {name} não sincronizada: {exc}")
    finally:
        _busy[0] = False
    return None


@persistent
def on_update(_scene, depsgraph):
    """Só anota os componentes tocados: mudar malha ou apagar objeto dentro da avaliação do depsgraph derruba o
    Blender (visto no ensaio da onda 4); o trabalho vai para um timer, fora dela."""
    if _busy[0]:
        return
    for owner in _owners_touched(depsgraph):
        _pending.add(owner.name)
    if _pending and not bpy.app.timers.is_registered(flush):
        bpy.app.timers.register(flush, first_interval=0.0)


@persistent
def on_load(*_args):
    _busy[0] = False
    _pending.clear()


_HANDLERS = ((bpy.app.handlers.depsgraph_update_post, on_update), (bpy.app.handlers.load_post, on_load))


def register():
    for handlers, callback in _HANDLERS:
        if callback not in handlers:
            handlers.append(callback)


def unregister():
    for handlers, callback in _HANDLERS:
        if callback in handlers:
            handlers.remove(callback)
    if bpy.app.timers.is_registered(flush):
        bpy.app.timers.unregister(flush)
    _pending.clear()
