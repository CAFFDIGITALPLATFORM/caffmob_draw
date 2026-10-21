"""Identidade do armário autoral e vínculo explícito dos membros (066, T047)."""

import bpy  # type: ignore

from .props import FACE_ITEMS

ROLE_ITEMS = [(key, label, '') for key, label in (
    ('CARCASS', 'Estrutura'), ('SHELF', 'Prateleira'), ('BACK', 'Fundo'), ('LEAF_PART', 'Parte móvel'),
    ('FIXED_FRONT', 'Frente fixa'), ('HARDWARE', 'Ferragem'), ('LED', 'LED'), ('LIGHT', 'Luz'),
    ('CUTTER', 'Cortador'), ('FILLER', 'Complemento'))]
RULE_ITEMS = [(key, label, '') for key, label in (
    ('FIXED', 'Fixo'), ('ANCHORED', 'Ancorado'), ('FIT_BETWEEN', 'Ajustar entre referências'),
    ('DISTRIBUTE', 'Distribuir'))]
FRONT_ITEMS = [(key, label, '') for key, label in (
    ('NEG_Y', '−Y'), ('POS_Y', '+Y'), ('NEG_X', '−X'), ('POS_X', '+X'))]


class BTM_PG_MemberRef(bpy.types.PropertyGroup):
    target: bpy.props.PointerProperty(type=bpy.types.Object)  # type: ignore
    uid: bpy.props.StringProperty()  # type: ignore
    face: bpy.props.EnumProperty(items=FACE_ITEMS, default='NEG_Y')  # type: ignore


class BTM_PG_Authored(bpy.types.PropertyGroup):
    is_authored: bpy.props.BoolProperty(default=False)  # type: ignore
    uid: bpy.props.StringProperty()  # type: ignore
    asset_uid: bpy.props.StringProperty()  # type: ignore
    asset_version: bpy.props.IntProperty(default=0, min=0)  # type: ignore
    front_axis: bpy.props.EnumProperty(name="Frente local", items=FRONT_ITEMS, default='NEG_Y')  # type: ignore
    size_local: bpy.props.FloatVectorProperty(name="Medidas locais (mm)", size=3, min=0)  # type: ignore


class BTM_PG_Member(bpy.types.PropertyGroup):
    uid: bpy.props.StringProperty()  # type: ignore
    owner: bpy.props.PointerProperty(name="Armário dono", type=bpy.types.Object)  # type: ignore
    role: bpy.props.EnumProperty(name="Papel", items=ROLE_ITEMS, default='CARCASS')  # type: ignore
    rule: bpy.props.EnumProperty(name="Regra dimensional", items=RULE_ITEMS, default='FIXED')  # type: ignore
    refs: bpy.props.CollectionProperty(type=BTM_PG_MemberRef)  # type: ignore
    axis: bpy.props.EnumProperty(items=[('X', 'X', ''), ('Y', 'Y', ''), ('Z', 'Z', '')], default='X')  # type: ignore
    offset_mm: bpy.props.FloatProperty(name="Deslocamento (mm)")  # type: ignore
    count: bpy.props.IntProperty(name="Quantidade", default=1, min=1)  # type: ignore


classes = (BTM_PG_MemberRef, BTM_PG_Authored, BTM_PG_Member)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Object.btm_authored = bpy.props.PointerProperty(type=BTM_PG_Authored)
    bpy.types.Object.btm_member = bpy.props.PointerProperty(type=BTM_PG_Member)


def unregister():
    del bpy.types.Object.btm_member
    del bpy.types.Object.btm_authored
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
