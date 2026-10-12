"""Vínculo do item grudado numa face plana (feature 004, T010; data-delta §1.1, D-02, D-03).

O item é filho Blender do hospedeiro (`host`); o resto do vínculo fica aqui. Os `update` de `u`, `v`, `distance` e
`spin` reposicionam o item (import tardio de `apply`); `_guard` evita recursão quando a aplicação grava de volta.
"""

import bpy  # type: ignore

from ..aggregates import limits

_guard = set()

FACE_ITEMS = [(f, limits.FACE_LABELS[f], "") for f in limits.FACES]
KIND_ITEMS = [('BOX_SIDE', "Lado da caixa", "Um dos seis lados do hospedeiro; acompanha a medida dele"),
              ('PLANE', "Plano", "Plano fixo no hospedeiro (face inclinada)")]
IDENTITY = (1.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 1.0)


def _guarded(name):
    def update(self, context):
        obj = self.id_data
        key = (obj.name, name)
        if key in _guard:
            return
        _guard.add(key)
        try:
            from . import apply
            if name == 'spin':
                apply.update_spin(obj)
            else:
                apply.update_position(obj)
        finally:
            _guard.discard(key)
    return update


class BTM_PG_Stick(bpy.types.PropertyGroup):
    is_stuck: bpy.props.BoolProperty(name="Grudado", default=False)  # type: ignore
    host: bpy.props.PointerProperty(name="Hospedeiro", type=bpy.types.Object)  # type: ignore
    face_kind: bpy.props.EnumProperty(name="Tipo de face", items=KIND_ITEMS, default='BOX_SIDE')  # type: ignore
    face: bpy.props.EnumProperty(name="Face", items=FACE_ITEMS, default='NEG_Y')  # type: ignore
    plane: bpy.props.FloatVectorProperty(name="Plano", size=16, default=IDENTITY)  # type: ignore
    u: bpy.props.FloatProperty(name="Posição U", subtype='DISTANCE', unit='LENGTH',
                               update=_guarded('u'))  # type: ignore
    v: bpy.props.FloatProperty(name="Posição V", subtype='DISTANCE', unit='LENGTH',
                               update=_guarded('v'))  # type: ignore
    distance: bpy.props.FloatProperty(
        name="Distância", subtype='DISTANCE', unit='LENGTH',
        description="Distância à face; negativo = entra no hospedeiro", update=_guarded('distance'))  # type: ignore
    spin: bpy.props.FloatProperty(name="Giro", subtype='ANGLE', unit='ROTATION',
                                  description="Giro do item em torno da normal da face",
                                  update=_guarded('spin'))  # type: ignore
    applied_spin: bpy.props.FloatProperty(subtype='ANGLE')  # type: ignore
    out_of_face: bpy.props.BoolProperty(name="Fora da face", default=False)  # type: ignore
    orig_parent: bpy.props.PointerProperty(type=bpy.types.Object)  # type: ignore
    opt_out: bpy.props.BoolProperty(default=False)  # type: ignore   # desgrudado da parede à mão: a carga não regruda
    last_world: bpy.props.FloatVectorProperty(size=16, default=IDENTITY)  # type: ignore


classes = (BTM_PG_Stick,)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Object.btm_stick = bpy.props.PointerProperty(type=BTM_PG_Stick)


def unregister():
    if hasattr(bpy.types.Object, 'btm_stick'):
        del bpy.types.Object.btm_stick
    for cls in reversed(classes):
        if cls.is_registered:
            bpy.utils.unregister_class(cls)
