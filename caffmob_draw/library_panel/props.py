"""Estado de sessão do painel BIBLIOTECA CAFFMOB (feature 012, T003; data-delta §1).

`WindowManager.btm_library`: painel aberto ou fechado e a última categoria aberta, com a linha dela (o Criar armário
usa essa linha como padrão). Não vai para o arquivo.
"""

import bpy  # type: ignore


class BTM_PG_LibraryState(bpy.types.PropertyGroup):
    open: bpy.props.BoolProperty(default=False)  # type: ignore
    category: bpy.props.StringProperty()  # type: ignore
    line: bpy.props.StringProperty(default='COZ')  # type: ignore


classes = (BTM_PG_LibraryState,)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.WindowManager.btm_library = bpy.props.PointerProperty(type=BTM_PG_LibraryState)


def unregister():
    if hasattr(bpy.types.WindowManager, 'btm_library'):
        del bpy.types.WindowManager.btm_library
    for cls in reversed(classes):
        if cls.is_registered:
            bpy.utils.unregister_class(cls)
