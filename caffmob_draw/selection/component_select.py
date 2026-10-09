"""Normalizador da seleção por componente (feature 011, T009; roadmap D-02, D-07, RN-05).

Um `depsgraph_update_post` troca as peças selecionadas pelas raízes dos componentes (`component.component_root`),
venha a seleção de onde vier: clique, caixa, laço, lista de objetos ou script. Para não pesar a cada atualização,
compara a assinatura da seleção (nomes selecionados + ativo) com a última vista e sai cedo se nada mudou; uma trava
evita reentrar quando o próprio `select_set` dispara outra atualização.

Não age:
- com o interruptor `Scene.btm_component_select` desligado;
- fora do modo objeto;
- com um modal da extensão ou um `transform` rodando (inserção, "Mover sobre", editor de armário, arraste).

Peças escolhidas por Alt + clique (`WindowManager.btm_component_exempt`) ficam como estão enquanto continuam
selecionadas.
"""

from contextlib import contextmanager

import bpy  # type: ignore
from bpy.app.handlers import persistent  # type: ignore

from . import component

_busy = [False]
_last = [None]


def forget():
    """Esquece a última assinatura: a próxima atualização reavalia a seleção inteira."""
    _last[0] = None


@contextmanager
def suspended():
    """Bloco em que o normalizador não age (ex.: o `view3d.select` do Alt + clique)."""
    previous = _busy[0]
    _busy[0] = True
    try:
        yield
    finally:
        _busy[0] = previous


def cabinet_modes(scene):
    """{biblioteca: está no modo gabinete} para `component_root` (D-07). Modo desligado conta como gabinete.

    Feature 012 (T053, D-05): sem a interface herdada, os modos dela não existem para o usuário; todo módulo sobe.
    """
    from ..legacy import gate
    if not gate.legacy_ui():
        return {}
    modes = {}
    frameless = getattr(scene, 'hb_frameless', None)
    if frameless is not None:
        modes['FRAMELESS'] = frameless.frameless_selection_mode == 'Cabinets'
    face_frame = getattr(scene, 'hb_face_frame', None)
    if face_frame is not None:
        modes['FACE_FRAME'] = (not face_frame.face_frame_selection_mode_enabled
                               or face_frame.face_frame_selection_mode == 'Cabinets')
    closets = getattr(scene, 'hb_closets', None)
    if closets is not None:
        modes['CLOSETS'] = (not closets.closet_selection_mode_enabled
                            or closets.closet_selection_mode == 'Starters')
    return modes


def exempt_names(context):
    raw = getattr(context.window_manager, 'btm_component_exempt', "")
    return {name for name in raw.split("\n") if name}


def set_exempt(context, names):
    context.window_manager.btm_component_exempt = "\n".join(sorted(names))


def _modal_running(context):
    for window in context.window_manager.windows:
        for op in window.modal_operators:
            idname = op.bl_idname.lower()
            if 'transform' in idname or 'caffmob' in idname or idname.startswith('btm'):
                return True
    return False


def _selected(context, view_layer):
    selected = getattr(context, 'selected_objects', None)
    if selected is None:                    # sem janela (fundo): lê pela camada de vista
        selected = [o for o in view_layer.objects if o.select_get(view_layer=view_layer)]
    out = []
    for obj in selected:                    # um contexto sobrescrito pode trazer um objeto já apagado
        try:
            if obj is not None and obj.name in view_layer.objects:
                out.append(obj)
        except ReferenceError:
            continue
    return out


def _signature(context, view_layer):
    active = view_layer.objects.active
    return frozenset(o.name for o in _selected(context, view_layer)), active.name if active is not None else ""


def normalize(context, scene):
    """Promove a seleção atual às raízes; devolve quantas peças subiram. Usado pelo handler e pelos testes."""
    view_layer = context.view_layer
    selected = _selected(context, view_layer)
    names = {o.name for o in selected}
    exempt = exempt_names(context)
    if exempt - names:
        exempt &= names
        set_exempt(context, exempt)
    modes = cabinet_modes(scene)
    promoted = 0
    for obj in selected:
        if obj.name in exempt:
            continue
        root = component.component_root(obj, modes)
        if root is None or root is obj or root.name not in view_layer.objects:
            continue
        try:
            root.select_set(True, view_layer=view_layer)
        except RuntimeError:
            continue
        if root.select_get(view_layer=view_layer):
            obj.select_set(False, view_layer=view_layer)
            promoted += 1
    active = view_layer.objects.active
    if active is not None and active.name not in exempt:
        root = component.component_root(active, modes)
        if root is not None and root is not active and root.select_get(view_layer=view_layer):
            view_layer.objects.active = root
    return promoted


@persistent
def on_depsgraph_update(scene, _depsgraph=None):
    if _busy[0]:
        return
    context = bpy.context
    if not getattr(scene, 'btm_component_select', False):
        _last[0] = None
        return
    view_layer = context.view_layer
    if view_layer is None or context.mode != 'OBJECT' or context.window_manager is None:
        return
    if _modal_running(context):
        return
    signature = _signature(context, view_layer)
    if signature == _last[0]:
        return
    _busy[0] = True
    try:
        normalize(context, scene)
    finally:
        _busy[0] = False
    _last[0] = _signature(context, view_layer)


@persistent
def on_load_post(*_args):
    forget()
    wm = bpy.context.window_manager
    if wm is not None and hasattr(wm, 'btm_component_exempt'):
        wm.btm_component_exempt = ""


def register():
    if on_depsgraph_update not in bpy.app.handlers.depsgraph_update_post:
        bpy.app.handlers.depsgraph_update_post.append(on_depsgraph_update)
    if on_load_post not in bpy.app.handlers.load_post:
        bpy.app.handlers.load_post.append(on_load_post)


def unregister():
    if on_load_post in bpy.app.handlers.load_post:
        bpy.app.handlers.load_post.remove(on_load_post)
    if on_depsgraph_update in bpy.app.handlers.depsgraph_update_post:
        bpy.app.handlers.depsgraph_update_post.remove(on_depsgraph_update)
    forget()
