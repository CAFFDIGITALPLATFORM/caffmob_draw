"""Propriedades da seleção por componente (feature 011, T001; data-delta §1, D-04, D-08).

- `Scene.btm_component_select`: interruptor "Seleção por componente", salvo no arquivo e ligado por padrão;
  arquivo antigo, sem a propriedade, lê o padrão.
- `WindowManager.btm_component_exempt`: peças escolhidas por Alt + clique (nomes separados por "\\n"), que o
  normalizador deixa selecionadas sem subir para a raiz. Estado de sessão.
"""

import bpy  # type: ignore

from ..data.i18n import tr


def _on_toggle(_self, _context):
    # Ligar de novo promove a seleção atual na próxima atualização (o normalizador compara a assinatura).
    from . import component_select
    component_select.forget()


def draw_toggle(layout, context):
    """Interruptor com o estado escrito, junto dos modos de seleção da barra lateral (T016)."""
    scene = context.scene
    if not hasattr(scene, 'btm_component_select'):
        return
    on = scene.btm_component_select
    row = layout.row(align=True)
    row.prop(scene, "btm_component_select", text=tr("Seleção por componente"),
             icon='CHECKBOX_HLT' if on else 'CHECKBOX_DEHLT', toggle=True)
    hint = layout.row()
    hint.enabled = False
    hint.label(text=tr("Ligada: Alt + clique seleciona uma peça") if on else tr("Desligada: clique seleciona a peça"))


def register():
    bpy.types.Scene.btm_component_select = bpy.props.BoolProperty(
        name="Seleção por componente", default=True, update=_on_toggle,
        description="Clicar numa peça seleciona o componente inteiro (porta, janela, item importado). "
                    "Alt + clique seleciona só a peça")  # type: ignore
    bpy.types.WindowManager.btm_component_exempt = bpy.props.StringProperty()  # type: ignore


def unregister():
    for owner, name in ((bpy.types.WindowManager, 'btm_component_exempt'), (bpy.types.Scene, 'btm_component_select')):
        if hasattr(owner, name):
            delattr(owner, name)
