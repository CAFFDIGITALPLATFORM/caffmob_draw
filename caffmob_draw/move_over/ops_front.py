"""Frente do objeto no Mover Sobre (feature 022): pergunta o lado e grava `btm_front_yaw` (RN-02, RF-02, RN-05).

Diálogo de quatro lados (Frente, Direita, Trás, Esquerda) e "Usar o eixo" para voltar à convenção −Y do objeto
(D3, decisão do titular em 2026-11-24). A escolha é um idprop no objeto, gravado num único passo de desfazer; cancelar
não grava nada. Com `then_open`, o operador devolve o usuário à janela do Mover Sobre depois de responder.
"""

import bpy  # type: ignore

from ..data.i18n import N_, tr
from . import frente_core

SIDE_ITEMS = [
    ('NEG_Y', N_("Frente (−Y)"), ""),
    ('POS_X', N_("Direita (+X)"), ""),
    ('POS_Y', N_("Trás (+Y)"), ""),
    ('NEG_X', N_("Esquerda (−X)"), ""),
    ('AXIS', N_("Usar o eixo"), ""),
]


def side_of(yaw):
    """Lado do diálogo que corresponde a um yaw gravado (ou 'AXIS' quando não há escolha)."""
    if yaw is None:
        return 'AXIS'
    for key, value in frente_core.FRONT_YAW.items():
        if frente_core.angular_distance(value, yaw) < 1.0:
            return key
    return 'AXIS'


class BTM_OT_MoveOverFront(bpy.types.Operator):
    """Escolhe o lado que o add-on deve tratar como frente do objeto de referência"""
    bl_idname = "caffmob.move_over_front"
    bl_label = "Frente do objeto"
    bl_options = {'REGISTER', 'UNDO'}

    a_name: bpy.props.StringProperty(options={'HIDDEN', 'SKIP_SAVE'})  # type: ignore
    b_name: bpy.props.StringProperty(options={'HIDDEN', 'SKIP_SAVE'})  # type: ignore
    then_open: bpy.props.BoolProperty(default=False, options={'HIDDEN', 'SKIP_SAVE'})  # type: ignore
    side: bpy.props.EnumProperty(items=SIDE_ITEMS, default='AXIS')  # type: ignore

    @classmethod
    def poll(cls, context):
        return getattr(context, 'scene', None) is not None

    def _target(self, context):
        return context.scene.objects.get(self.b_name) or getattr(context, 'active_object', None)

    def invoke(self, context, event):
        obj = self._target(context)
        self.side = side_of(None if obj is None else obj.get('btm_front_yaw'))
        return context.window_manager.invoke_props_dialog(self, width=320)

    def draw(self, context):
        self.layout.label(text=tr("Qual lado de “{}” é a frente?").format(self.b_name or tr("objeto")))
        self.layout.prop(self, "side", expand=True)
        if self.side == 'AXIS':
            self.layout.label(text=tr("Sem escolha gravada: vale o eixo do objeto."), icon='INFO')

    def _reopen(self):
        if self.then_open:
            bpy.ops.caffmob.move_over_dialog('INVOKE_DEFAULT', a_name=self.a_name, b_name=self.b_name,
                                             skip_front=True)

    def execute(self, context):
        obj = self._target(context)
        if obj is not None:
            if self.side == 'AXIS':
                if 'btm_front_yaw' in obj:
                    del obj['btm_front_yaw']
            else:
                obj['btm_front_yaw'] = frente_core.FRONT_YAW[self.side]
        self._reopen()
        return {'FINISHED'}

    def cancel(self, context):
        self._reopen()


classes = (BTM_OT_MoveOverFront,)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        if cls.is_registered:
            bpy.utils.unregister_class(cls)
