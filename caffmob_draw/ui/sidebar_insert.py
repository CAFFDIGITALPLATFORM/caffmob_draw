"""Seção Inserir (feature 005, T015; RF-03, RN-04, D-06).

Feature 012 (T049; D-02, D-19): a biblioteca de módulos fica no painel BIBLIOTECA CAFFMOB, no topo da viewport. Aqui
ficam o Módulo Rápido, Importar, Meus módulos e Objetos. O seletor das bibliotecas herdadas (frameless, face frame,
closets) e as galerias delas só aparecem com a preferência de suporte (`legacy/gate.py`).
"""

from ..data.i18n import N_, tr
from . import my_modules
from .sidebar import group_scope


def draw(layout, context):
    scene = context.scene
    hb_scene = getattr(scene, 'home_builder', None)
    row = layout.row(align=True)
    row.scale_y = 1.2
    row.operator("caffmob.cabinet_builder", text=N_("Módulo Rápido"), icon='OUTLINER_OB_MESH')
    row.operator("caffmob.import_model", text=N_("Importar modelo 3D"), icon='IMPORT')
    hint = layout.row()
    hint.active = False
    hint.label(text=tr("Biblioteca no topo da viewport: BIBLIOTECA CAFFMOB"), icon='ASSET_MANAGER')
    from ..legacy import gate
    if hb_scene is not None and gate.legacy_ui(context):
        row = layout.row(align=True)
        row.scale_y = 1.3
        row.prop(hb_scene, "product_tab", text="")
        if hb_scene.product_tab == 'FRAMELESS' and hasattr(scene, 'hb_frameless'):
            scene.hb_frameless.draw_library_ui(layout, context, include_user=False)
        elif hb_scene.product_tab == 'FACE FRAME' and hasattr(scene, 'hb_face_frame'):
            scene.hb_face_frame.draw_library_ui(layout, context, include_user=False)
        elif hasattr(scene, 'hb_closets'):
            scene.hb_closets.draw_library_ui(layout, context, include_user=False)
    with group_scope(layout, context, 'my_modules', N_("Meus módulos"), 'USER') as body:
        if body is not None:
            my_modules.draw(body, context)
    with group_scope(layout, context, 'objects', N_("Objetos"), 'ASSET_MANAGER') as body:   # feature 009 (D-14)
        if body is not None:
            from ..object_library import panels as object_panels
            object_panels.draw_insert(body, context)
