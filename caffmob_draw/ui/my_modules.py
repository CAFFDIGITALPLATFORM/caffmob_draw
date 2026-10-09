"""Inserir › Meus módulos (feature 005, T014; RN-04, D-06).

Junta num lugar as três bibliotecas do usuário, com a origem de cada uma e um filtro:
- **Módulos salvos** pelo Personalizar módulo (feature 003, `customize/library_io`);
- **Grupos frameless** do usuário (`hb_frameless.draw_user_library_ui`);
- **Grupos face frame** do usuário (`hb_face_frame.draw_user_library_ui`).
Cada bloco usa os operadores da própria origem para inserir, renomear e apagar; as galerias das bibliotecas deixam de
mostrar a parte do usuário (`draw_library_ui(include_user=False)`).
"""

from ..data.i18n import N_, tr

ORIGINS = (
    ('MODULES', N_("Módulos salvos"), 'FILE_BLEND'),
    ('FRAMELESS', N_("Grupos frameless"), 'MESH_CUBE'),
    ('FACE_FRAME', N_("Grupos face frame"), 'MESH_GRID'),
)


def _draw_origin(layout, context, origin):
    scene = context.scene
    if origin == 'MODULES':
        from ..customize import panels as customize_panels
        customize_panels.draw_library(layout, context)
    elif origin == 'FRAMELESS':
        props = getattr(scene, 'hb_frameless', None)
        if props is not None:
            props.draw_user_library_ui(layout, context)
    elif origin == 'FACE_FRAME':
        props = getattr(scene, 'hb_face_frame', None)
        if props is not None:
            props.draw_user_library_ui(layout, context)


def draw(layout, context):
    st = context.window_manager.btm_sidebar
    from ..legacy import gate
    legacy = gate.legacy_ui(context)         # feature 012 (T049): grupos herdados só com a preferência de suporte
    if legacy:
        layout.prop(st, "my_modules_filter", text="")
    for origin, label, icon in ORIGINS:
        if origin != 'MODULES' and not legacy:
            continue
        if legacy and st.my_modules_filter not in ('ALL', origin):
            continue
        box = layout.box()
        box.label(text=tr(label), icon=icon)
        _draw_origin(box, context, origin)
