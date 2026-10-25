"""Calibração do veio da imagem (feature 067, onda 3; RF-061).

`caffmob.grain_calibrate` grava no material de imagem da peça ativa o eixo do veio na imagem fonte (H ou V) e refaz o
giro de todas as peças que usam esse material, num passo de Undo. H e V da peça não supõem imagem horizontal.
"""

import bpy  # type: ignore

from ..data.i18n import N_, tr
from . import grain


class BTM_OT_GrainCalibrate(bpy.types.Operator):
    """Diz em que eixo corre o veio na imagem da textura (H ou V); as peças com essa textura giram de novo"""
    bl_idname = 'caffmob.grain_calibrate'
    bl_label = N_("Calibrar o veio da imagem")
    bl_options = {'REGISTER', 'UNDO'}

    axis: bpy.props.EnumProperty(name=N_("Veio na imagem"), items=(
        ('H', N_("Horizontal"), N_("O veio corre na largura da imagem")),
        ('V', N_("Vertical"), N_("O veio corre na altura da imagem"))), default='H')  # type: ignore

    @classmethod
    def poll(cls, context):
        obj = context.active_object
        if obj is None or not grain.image_materials(obj):
            cls.poll_message_set(tr("A peça ativa não tem textura de imagem"))
            return False
        return True

    def execute(self, context):
        materials = grain.image_materials(context.active_object)
        for mat in materials:
            grain.calibrate(mat, self.axis)
        count = 0
        for obj in bpy.data.objects:
            if obj.type == 'MESH' and any(m in materials for m in grain.image_materials(obj)):
                grain.sync(obj)
                count += 1
        self.report({'INFO'}, tr("Veio da imagem: {}; {} peça(s) refeitas").format(self.axis, count))
        return {'FINISHED'}


classes = (BTM_OT_GrainCalibrate,)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        if cls.is_registered:
            bpy.utils.unregister_class(cls)
