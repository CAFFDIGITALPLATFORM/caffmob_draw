"""Controlador persistente e vínculos por ponteiro (data-delta §5)."""
import bpy  # type: ignore
from dataclasses import fields
from .core import Params


class BTM_PG_CladdingOpening(bpy.types.PropertyGroup):
    target: bpy.props.PointerProperty(type=bpy.types.Object)  # type: ignore


class BTM_PG_Cladding(bpy.types.PropertyGroup):
    uid: bpy.props.StringProperty()  # type: ignore
    host: bpy.props.PointerProperty(type=bpy.types.Object)  # type: ignore
    plane_origin: bpy.props.FloatVectorProperty(size=3)  # type: ignore
    plane_normal: bpy.props.FloatVectorProperty(size=3, default=(0, -1, 0))  # type: ignore
    plane_u: bpy.props.FloatVectorProperty(size=3, default=(1, 0, 0))  # type: ignore
    kind: bpy.props.EnumProperty(name='Tipo', items=[('BOARDS', 'Tábuas', ''), ('SLATS', 'Ripado', ''),
                                ('PANEL', 'Painel liso', ''), ('PLATES', 'Placas', '')])  # type: ignore
    width_mm: bpy.props.FloatProperty(name='Largura (mm)', default=150, min=1)  # type: ignore
    thickness_mm: bpy.props.FloatProperty(name='Espessura (mm)', default=15, min=0.1)  # type: ignore
    joint_mm: bpy.props.FloatProperty(name='Junta (mm)', default=3, min=0)  # type: ignore
    min_gap_mm: bpy.props.FloatProperty(name='Vão mínimo (mm)', default=18, min=0)  # type: ignore
    orientation: bpy.props.EnumProperty(name='Orientação', items=[('HORIZONTAL', 'Horizontal', ''),
        ('VERTICAL', 'Vertical', ''), ('ANGLED', 'Inclinada', '')])  # type: ignore
    angle: bpy.props.FloatProperty(name='Inclinação (graus)', default=45)  # type: ignore
    band: bpy.props.EnumProperty(name='Extensão', items=[('FULL', 'Toda a face', ''),
                                                        ('PARTIAL', 'Faixa parcial', '')])  # type: ignore
    band_from: bpy.props.EnumProperty(name='Ponta da faixa', items=[('START', 'Início', ''),
                                                                 ('END', 'Fim', '')])  # type: ignore
    band_mm: bpy.props.FloatProperty(name='Faixa (mm)', default=1600, min=1)  # type: ignore
    backing: bpy.props.BoolProperty(name='Fundo de MDF', default=False)  # type: ignore
    backing_material: bpy.props.PointerProperty(name='Material do fundo', type=bpy.types.Material)  # type: ignore
    sheet_w_mm: bpy.props.FloatProperty(name='Chapa: comprimento (mm)', default=2730, min=1)  # type: ignore
    sheet_h_mm: bpy.props.FloatProperty(name='Chapa: largura (mm)', default=1810, min=1)  # type: ignore
    sheet_t_mm: bpy.props.FloatProperty(name='Chapa: espessura (mm)', default=15, min=0.1)  # type: ignore
    texture: bpy.props.StringProperty(name='Imagem da textura', subtype='FILE_PATH')  # type: ignore
    texture_size_mm: bpy.props.FloatProperty(name='Tamanho da textura (mm)', default=1000, min=1)  # type: ignore
    grain_angle: bpy.props.FloatProperty(name='Veio (graus)', default=0)  # type: ignore
    material: bpy.props.PointerProperty(name='Material', type=bpy.types.Material)  # type: ignore
    material_kind: bpy.props.EnumProperty(name='Material construtivo', items=[('MDF', 'MDF', ''),
        ('SOLID_WOOD', 'Madeira maciça', ''), ('CERAMIC', 'Cerâmica', '')])  # type: ignore
    openings: bpy.props.CollectionProperty(type=BTM_PG_CladdingOpening)  # type: ignore
    params_hash: bpy.props.StringProperty()  # type: ignore
    overrides: bpy.props.StringProperty(default='{}')  # type: ignore
    environment: bpy.props.StringProperty(name='Ambiente', default='Ambiente')  # type: ignore
    link_missing: bpy.props.BoolProperty(default=False)  # type: ignore
    diagnostic: bpy.props.StringProperty()  # type: ignore


def parameters(data):
    return Params(**{f.name: getattr(data, f.name) for f in fields(Params)})


classes = (BTM_PG_CladdingOpening, BTM_PG_Cladding)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Object.btm_cladding = bpy.props.PointerProperty(type=BTM_PG_Cladding)


def unregister():
    del bpy.types.Object.btm_cladding
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
