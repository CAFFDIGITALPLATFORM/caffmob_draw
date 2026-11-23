"""Assinatura do conta-gotas na sessão (feature 018, T015; D-09, RN-11).

`WindowManager.btm_texture_pick` guarda o que foi copiado (imagem, tamanho, veio, origem e os alvos congelados).
PropertyGroup de WindowManager não vai para o `.blend`: copiar textura é gesto de sessão, não dado do projeto.
"""

import bpy  # type: ignore

from ..data.i18n import N_


class BTM_PG_TexturePick(bpy.types.PropertyGroup):
    ativo: bpy.props.BoolProperty(name=N_("Conta-gotas ativo"), default=False)  # type: ignore
    path: bpy.props.StringProperty(name=N_("Arquivo da textura"), subtype='FILE_PATH')  # type: ignore
    nome: bpy.props.StringProperty(name=N_("Nome da textura"))  # type: ignore
    texture_id: bpy.props.StringProperty(name=N_("Item do catálogo"))  # type: ignore
    size_mm: bpy.props.FloatProperty(name=N_("Largura (mm)"), subtype='DISTANCE', unit='LENGTH', min=0.0,
                                     default=0.0)  # type: ignore
    height_mm: bpy.props.FloatProperty(name=N_("Altura (mm)"), subtype='DISTANCE', unit='LENGTH', min=0.0,
                                       default=0.0)  # type: ignore
    angle: bpy.props.FloatProperty(name=N_("Ângulo do veio (graus)"), min=-180.0, max=180.0,
                                   default=0.0)  # type: ignore
    origem: bpy.props.StringProperty(name=N_("Peça de origem"))  # type: ignore
    alvos: bpy.props.StringProperty(name=N_("Alvos"), description=N_("Nomes separados por quebra de linha"))  # type: ignore


classes = (BTM_PG_TexturePick,)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.WindowManager.btm_texture_pick = bpy.props.PointerProperty(type=BTM_PG_TexturePick)


def unregister():
    if hasattr(bpy.types.WindowManager, 'btm_texture_pick'):
        del bpy.types.WindowManager.btm_texture_pick
    for cls in reversed(classes):
        if cls.is_registered:
            bpy.utils.unregister_class(cls)
