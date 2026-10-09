"""Bibliotecas herdadas (feature 012): porta da interface e conversão para CAFFMob.

- `gate`: a interface de frameless, face frame, closets e molduras só aparece com a preferência de suporte;
- `convert_core`, `convert`: armário herdado → módulo CAFFMob, com o relatório de perdas;
- `groups_core`, `groups`: grupos salvos nas bibliotecas herdadas → módulos da biblioteca do usuário;
- `ops`: comandos de conversão e o aviso ao abrir um arquivo com armários herdados.

O `load_post` (T054, D-04) põe `product_tab = 'FRAMELESS'` com a porta fechada: é o valor de fábrica do enum, e com
ele os keymaps herdados (que exigem FACE FRAME ou CLOSET) ficam inertes. Os itens do enum ficam até a remoção do
código herdado, para os arquivos antigos abrirem.
"""

import bpy  # type: ignore
from bpy.app.handlers import persistent  # type: ignore

NEUTRAL_TAB = 'FRAMELESS'


# Modos de seleção herdados no valor de gabinete: num arquivo antigo salvo em "Parts", a caixa do armário fica sem
# seleção e a seleção por componente (011) não a alcançaria; sem a interface herdada, o usuário não troca o modo.
NEUTRAL_MODES = (('hb_frameless', 'frameless_selection_mode', 'Cabinets'),
                 ('hb_face_frame', 'face_frame_selection_mode', 'Cabinets'),
                 ('hb_closets', 'closet_selection_mode', 'Starters'))


def neutralize_product_tab(context=None):
    """Com a porta fechada: `product_tab` e os modos de seleção herdados nos valores de fábrica. Devolve se mudou."""
    from . import gate
    context = context or bpy.context
    if gate.legacy_ui(context):
        return False
    changed = False
    for scene in bpy.data.scenes:
        hb = getattr(scene, 'home_builder', None)
        if hb is not None and getattr(hb, 'product_tab', NEUTRAL_TAB) != NEUTRAL_TAB:
            hb.product_tab = NEUTRAL_TAB
            changed = True
        for group_name, prop, value in NEUTRAL_MODES:
            group = getattr(scene, group_name, None)
            if group is not None and getattr(group, prop, value) != value:
                setattr(group, prop, value)
                changed = True
    return changed


@persistent
def on_load_post(*_args):
    neutralize_product_tab()
    from . import ops
    if not bpy.app.timers.is_registered(ops.notify_legacy):
        bpy.app.timers.register(ops.notify_legacy, first_interval=1.0)   # depois da interface pronta (D-26)


def _modules():
    from . import ops
    return (ops,)


def register():
    for module in _modules():
        module.register()
    if on_load_post not in bpy.app.handlers.load_post:
        bpy.app.handlers.load_post.append(on_load_post)


def unregister():
    from . import ops
    if bpy.app.timers.is_registered(ops.notify_legacy):
        bpy.app.timers.unregister(ops.notify_legacy)
    if on_load_post in bpy.app.handlers.load_post:
        bpy.app.handlers.load_post.remove(on_load_post)
    for module in reversed(_modules()):
        module.unregister()
