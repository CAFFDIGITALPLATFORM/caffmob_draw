# (063 RF-01; D-03) Um único estado de tela do MOBI no WindowManager.
import bpy  # type: ignore


class MOBI_PG_Item(bpy.types.PropertyGroup):
    id: bpy.props.StringProperty()  # type: ignore
    nome: bpy.props.StringProperty()  # type: ignore
    version: bpy.props.IntProperty()  # type: ignore
    schema: bpy.props.StringProperty(default='caffmob.ambiente/v1')  # type: ignore
    categoria: bpy.props.StringProperty()  # type: ignore
    escopo: bpy.props.StringProperty()  # type: ignore
    imagem: bpy.props.StringProperty()  # type: ignore


class MOBI_PG_Estado(bpy.types.PropertyGroup):
    situacao: bpy.props.StringProperty()  # type: ignore
    relatorio_v2: bpy.props.StringProperty()  # type: ignore
    codigo: bpy.props.StringProperty()  # type: ignore
    endereco: bpy.props.StringProperty()  # type: ignore
    ocupado: bpy.props.BoolProperty()  # type: ignore
    progresso: bpy.props.FloatProperty(min=0.0, max=1.0)  # type: ignore
    biblioteca: bpy.props.EnumProperty(name="Biblioteca", items=[
        ('titular', "Do titular", ""), ('pessoal', "Pessoal", "")], default='titular')  # type: ignore
    ambientes: bpy.props.CollectionProperty(type=MOBI_PG_Item)  # type: ignore
    modelos: bpy.props.CollectionProperty(type=MOBI_PG_Item)  # type: ignore
    proximo_ambiente: bpy.props.StringProperty()  # type: ignore
    conflito_local: bpy.props.StringProperty()  # type: ignore
    conflito_mobi: bpy.props.StringProperty()  # type: ignore
    conflito_tipo: bpy.props.StringProperty()  # type: ignore
    conflito_id: bpy.props.StringProperty()  # type: ignore
    conflito_versao: bpy.props.IntProperty()  # type: ignore
    conflito_objeto: bpy.props.StringProperty()  # type: ignore


classes = (MOBI_PG_Item, MOBI_PG_Estado)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.WindowManager.btm_caffmob = bpy.props.PointerProperty(type=MOBI_PG_Estado)


def unregister():
    if hasattr(bpy.types.WindowManager, 'btm_caffmob'):
        del bpy.types.WindowManager.btm_caffmob
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
