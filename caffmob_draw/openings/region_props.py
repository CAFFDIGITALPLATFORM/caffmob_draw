"""Região marcada na parede antes de inserir porta ou janela (feature 011, T002; data-delta §1, D-10).

`WindowManager.btm_wall_region` é estado de sessão: não vai para o arquivo nem para o undo. Guarda o nome da parede,
e não um ponteiro; parede apagada ou renomeada descarta a região sem erro. Medidas no espaço local da parede
(X ao longo dela a partir da origem, Z a partir do piso), com `x0 < x1` e `z0 < z1`.
"""

import bpy  # type: ignore

SIDE_ITEMS = [('FRONT', "Frente", ""), ('BACK', "Fundo", "")]


class BTM_PG_WallRegion(bpy.types.PropertyGroup):
    active: bpy.props.BoolProperty(default=False)  # type: ignore
    wall: bpy.props.StringProperty()  # type: ignore
    x0: bpy.props.FloatProperty(subtype='DISTANCE', unit='LENGTH')  # type: ignore
    x1: bpy.props.FloatProperty(subtype='DISTANCE', unit='LENGTH')  # type: ignore
    z0: bpy.props.FloatProperty(subtype='DISTANCE', unit='LENGTH')  # type: ignore
    z1: bpy.props.FloatProperty(subtype='DISTANCE', unit='LENGTH')  # type: ignore
    side: bpy.props.EnumProperty(items=SIDE_ITEMS, default='FRONT')  # type: ignore


classes = (BTM_PG_WallRegion,)


def region_wall(context, invalidate=True):
    """(região, parede) se há uma região marcada numa parede que ainda existe; senão (None, None).

    Parede que sumiu desliga a região, menos com `invalidate=False` (o desenho não grava dados, DT-04).
    """
    region = getattr(context.window_manager, 'btm_wall_region', None)
    if region is None or not region.active:
        return None, None
    wall = bpy.data.objects.get(region.wall)
    if wall is None or not wall.get('IS_WALL_BP'):
        if invalidate:
            region.active = False
        return None, None
    return region, wall


def clear(context):
    region = getattr(context.window_manager, 'btm_wall_region', None)
    if region is not None:
        region.active = False


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.WindowManager.btm_wall_region = bpy.props.PointerProperty(type=BTM_PG_WallRegion)


def unregister():
    if hasattr(bpy.types.WindowManager, 'btm_wall_region'):
        del bpy.types.WindowManager.btm_wall_region
    for cls in reversed(classes):
        if cls.is_registered:
            bpy.utils.unregister_class(cls)
