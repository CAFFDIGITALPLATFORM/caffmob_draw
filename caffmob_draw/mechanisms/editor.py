"""Editor animado (feature 067, T077; RF-100).

`caffmob.mechanism_set` leva a frente, a folha ou a gaveta selecionada (ou todas as folhas do componente) à abertura
pedida, em percentual ou ângulo, num passo de Undo. A pose fica sincronizada com o valor: abrir 0 → 50 → 100 → 0%
volta à pose exata.
"""

import bpy  # type: ignore

from ..data.i18n import N_, tr
from . import all_of, of


class BTM_OT_MechanismSet(bpy.types.Operator):
    """Abre ou fecha a frente, a folha ou a gaveta selecionada (ou todas as do componente)"""
    bl_idname = 'caffmob.mechanism_set'
    bl_label = N_("Abertura")
    bl_options = {'REGISTER', 'UNDO'}

    percent: bpy.props.FloatProperty(name=N_("Abertura (%)"), min=0.0, max=100.0, default=0.0,
                                     subtype='PERCENTAGE')  # type: ignore
    scope: bpy.props.EnumProperty(name=N_("Escopo"), items=(
        ('SELECTED', N_("Selecionada"), N_("Só a frente ou folha selecionada")),
        ('COMPONENT', N_("Componente"), N_("Todas as folhas e portas do componente"))),
        default='SELECTED')  # type: ignore

    @classmethod
    def poll(cls, context):
        obj = context.active_object
        if of(obj) is None and not all_of(obj):
            cls.poll_message_set(tr("Selecione uma porta, folha ou gaveta"))
            return False
        return True

    def execute(self, context):
        obj = context.active_object
        targets = all_of(obj) if self.scope == 'COMPONENT' or of(obj) is None else [of(obj)]
        if not targets:
            return {'CANCELLED'}
        for mech in targets:
            mech.set_fraction(self.percent / 100.0)
        self.report({'INFO'}, tr("Abertura: {}%").format(round(self.percent)))
        return {'FINISHED'}


classes = (BTM_OT_MechanismSet,)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        if cls.is_registered:
            bpy.utils.unregister_class(cls)
