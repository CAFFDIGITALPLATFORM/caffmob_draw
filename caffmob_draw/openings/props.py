"""Dados da porta e da janela reais na caixa da parede (feature 010, T001; data-delta §2).

`Object.btm_opening_real` fica na caixa (`GeoNodeCage` com `IS_ENTRY_DOOR_BP`/`IS_WINDOW_BP`): o que foi montado nela, a
assinatura das medidas da última montagem (igual = não refaz) e a versão do gerador. `kind = NONE` = caixa antiga,
ainda sem a porta real ("Atualizar portas e janelas").
"""

import bpy  # type: ignore

KIND_ITEMS = [('NONE', "Nenhum", "Caixa antiga, sem a porta real"), ('DOOR', "Porta", ""),
              ('DOUBLE_DOOR', "Porta dupla", ""), ('OPEN_DOOR', "Vão aberto", ""), ('WINDOW', "Janela", "")]
MODEL_VERSION = 1


def _limit_changed(self, context):
    from . import sync
    sync.update_limit(self.id_data, context)


def _get_angle(self):
    from . import sync
    leaves = sync.door_leaves(self.id_data)
    return max((o.btm_aggregate.open_value * o.btm_aggregate.max_angle for o in leaves), default=0.0)


def _set_angle(self, value):
    from . import sync
    if value > self.swing_limit + 1e-6:
        return
    for sash in sync.door_leaves(self.id_data):
        sash.btm_aggregate.open_value = value / sash.btm_aggregate.max_angle


class BTM_PG_Opening(bpy.types.PropertyGroup):
    angle: bpy.props.FloatProperty(name="Abertura (graus)", min=0.0, max=180.0,
                                   get=_get_angle, set=_set_angle)  # type: ignore
    uid: bpy.props.StringProperty()  # type: ignore
    host_wall: bpy.props.PointerProperty(type=bpy.types.Object)  # type: ignore
    swing_limit: bpy.props.FloatProperty(name="Limite de giro", default=90.0, min=1.0, max=180.0,
                                         update=_limit_changed)  # type: ignore
    corner_ref: bpy.props.EnumProperty(name="Referência ao canto", items=[
        ('START', "Primeiro canto", ""), ('END', "Segundo canto", ""),
        ('EDGE', "Canto escolhido", "")], default='START')  # type: ignore
    corner_dist_mm: bpy.props.FloatProperty(name="Distância ao canto (mm)", min=0.0)  # type: ignore
    corner_world: bpy.props.FloatVectorProperty(size=3, subtype='XYZ')  # type: ignore
    link_missing: bpy.props.BoolProperty(default=False)  # type: ignore
    kind: bpy.props.EnumProperty(items=KIND_ITEMS, default='NONE')  # type: ignore
    signature: bpy.props.StringProperty()  # type: ignore
    model_version: bpy.props.IntProperty(default=0)  # type: ignore
    assembly: bpy.props.PointerProperty(type=bpy.types.Object)  # type: ignore


classes = (BTM_PG_Opening,)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Object.btm_opening_real = bpy.props.PointerProperty(type=BTM_PG_Opening)


def unregister():
    if hasattr(bpy.types.Object, 'btm_opening_real'):
        del bpy.types.Object.btm_opening_real
    for cls in reversed(classes):
        if cls.is_registered:
            bpy.utils.unregister_class(cls)
