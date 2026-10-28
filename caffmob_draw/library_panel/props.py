"""Estado de sessão do painel BIBLIOTECA CAFFMOB (feature 012, T003; feature 014, T026; data-delta §6).

`WindowManager.btm_library`: estado do painel e a última categoria aberta, com a linha dela (o Criar armário usa essa
linha como padrão). Não vai para o arquivo.

Feature 014 (RN-09, D-10): três estados em `mode` (MIN só o rótulo, OPEN a coluna de categorias, MAX o retângulo com
a grade), `pinned` (fixo, o MAX não fecha com clique fora nem Esc), `rect` do retângulo (zeros = posição inicial),
`scroll` da grade, a aba (`tab`) e os filtros da área Texturas. `open` passa a ser derivado de `mode`: ler dá
`mode != 'MIN'`; gravar True abre a coluna e False minimiza, como o clique da 012 já fazia.
"""

import bpy  # type: ignore

MODES = [('MIN', "Minimizado", "Só o rótulo BIBLIOTECA CAFFMOB"),
         ('OPEN', "Aberto", "Coluna de categorias"),
         ('MAX', "Maximizado", "Retângulo com a grade")]
OPENING_MATERIALS = [
    ('madeira', "Madeira", "Esquadria em madeira"),
    ('aluminio', "Alumínio", "Esquadria em alumínio"),
    ('blindex', "Blindex", "Esquadria em vidro temperado"),
]


def _get_open(self):
    return self.mode != 'MIN'


def _set_open(self, value):
    self.mode = 'OPEN' if value else 'MIN'


class BTM_PG_LibraryState(bpy.types.PropertyGroup):
    mode: bpy.props.EnumProperty(items=MODES, default='MIN')  # type: ignore
    open: bpy.props.BoolProperty(get=_get_open, set=_set_open)  # type: ignore
    pinned: bpy.props.BoolProperty(default=False)  # type: ignore
    rect: bpy.props.FloatVectorProperty(size=4, default=(0.0, 0.0, 0.0, 0.0))  # type: ignore
    scroll: bpy.props.FloatProperty(default=0.0, min=0.0)  # type: ignore
    tab: bpy.props.StringProperty(default='TEXTURES')  # type: ignore
    manufacturer: bpy.props.StringProperty()  # type: ignore
    collection: bpy.props.StringProperty()  # type: ignore
    search: bpy.props.StringProperty()  # type: ignore
    category: bpy.props.StringProperty()  # type: ignore
    line: bpy.props.StringProperty(default='COZ')  # type: ignore
    opening_material: bpy.props.EnumProperty(name="Material da esquadria", items=OPENING_MATERIALS,
                                             default='madeira')  # type: ignore


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
