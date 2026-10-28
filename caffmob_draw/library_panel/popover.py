"""Conteúdo de uma categoria da Biblioteca CAFFMob (feature 012, T024; D-15, D-16, RN-02, RN-15).

Abre num popover nativo (`WindowManager.popover`) com:
- os modelos prontos CAFFMob (`models_core`), montados pelo Padrão de Dimensões na linha da categoria;
- os módulos que o usuário salvou nessa categoria (`customize/library_io`).

A biblioteca de objetos (009) continua separada, em Inserir › Objetos.
"""

import bpy  # type: ignore

from ..data.i18n import tr
from . import categories, categories_core, models_core

_open = {'category': "", 'drawn': 0}       # `drawn`: quantas vezes o popover desenhou (testes de interface)


def _draw(self, context):
    layout = self.layout
    _open['drawn'] += 1
    name = _open['category']
    found = categories.find(name)
    line = found.line if found is not None else categories_core.DEFAULT_LINE
    head = layout.row(align=True)
    head.label(text=name, icon='ASSET_MANAGER')
    head.label(text=tr("Linha: {}").format(tr(categories_core.LINE_LABELS.get(line, line))))
    if found is not None and not found.fixed:
        op = head.operator("caffmob.library_category_set_line", text="", icon='PREFERENCES')
        op.category = name
    layout.separator()
    layout.label(text=tr("Modelos prontos"))
    models, warnings = models_core.load_default()
    grid = layout.grid_flow(columns=2, align=True)
    for model in models:
        op = grid.operator("caffmob.library_insert_model", text=tr(model.label), icon='MESH_CUBE')
        op.model_id, op.line = model.id, line
    for warning in warnings:
        layout.label(text=warning, icon='ERROR')
    layout.separator()
    layout.label(text=tr("Meus módulos"))
    from ..customize import library_io
    try:
        entries = [e for e in library_io.list_modules() if e["category"].casefold() == name.casefold()]
    except (OSError, ValueError) as exc:
        layout.label(text=tr("Biblioteca indisponível: {}").format(exc), icon='ERROR')
        return
    if not entries:
        hint = layout.row()
        hint.active = False
        hint.label(text=tr("Nenhum módulo salvo nesta categoria"))
    col = layout.column(align=True)
    for entry in entries:
        col.operator("caffmob.module_insert", text=entry["name"], icon='IMPORT').filepath = entry["blend"]


def show(context, category):
    _open['category'] = category
    context.window_manager.popover(_draw, ui_units_x=16)


class BTM_OT_LibraryInsertModel(bpy.types.Operator):
    """Insere o modelo pronto com as medidas, as chapas e a montagem do Padrão de Dimensões da linha"""
    bl_idname = "caffmob.library_insert_model"
    bl_label = "Inserir modelo"
    bl_options = {'REGISTER', 'UNDO'}

    model_id: bpy.props.StringProperty()  # type: ignore
    line: bpy.props.StringProperty(default='COZ')  # type: ignore

    def execute(self, context):
        model = models_core.find_any(self.model_id)
        if model is None:
            self.report({'ERROR'}, tr("Modelo não encontrado: {}").format(self.model_id))
            return {'CANCELLED'}
        if model.kind in ('DOOR', 'WINDOW'):
            from ..openings import build, door_core, window_core
            state = getattr(context.window_manager, 'btm_library', None) if context.window_manager else None
            mat = (getattr(state, 'opening_material', "") if state is not None else "") or model.default_material
            w, h, wall = model.width_mm / 1000.0, model.height_mm / 1000.0, 0.15
            if model.kind == 'WINDOW':
                parts = window_core.window_parts(w, h, wall, model=model.opening_model, material=mat)
            else:
                lw, lh = door_core.leaf_size(w, h, model=model.opening_model)
                parts = door_core.door_parts(lw, lh, wall, model=model.opening_model, material=mat)
            col = context.collection or context.scene.collection
            root = bpy.data.objects.new(model.label, None)
            col.objects.link(root)
            root.location = context.scene.cursor.location.copy()
            if model.kind == 'WINDOW' and abs(root.location.z) < 1e-9:
                root.location.z = model.sill_mm / 1000.0
            root.btm_plane.object_kind = 'OPENING'
            root.btm_opening_real['opening_model'] = model.opening_model
            if mat in ('madeira', 'aluminio', 'blindex'):
                root.btm_opening_real['opening_material'] = ('madeira', 'aluminio', 'blindex').index(mat)
            for key, child in build.build(parts, col, window=model.kind == 'WINDOW').items():
                child.parent = root
                child['caffmob_papel'] = str(key)
            for other in list(context.selected_objects):
                other.select_set(False)
            root.select_set(True)
            context.view_layer.objects.active = root
            return {'FINISHED'}

        kwargs = dict(cabinet_type=model.cabinet_type, line=self.line if self.line in categories_core.LINES else 'COZ',
                      door_swing=model.door_swing, shelves=model.shelves)
        if model.width_mm:
            kwargs['width'] = model.width_mm / 1000.0
        kwargs['structure_id'] = models_core.model_structure(model, kwargs['line'])     # feature 015 (RN-13)
        res = bpy.ops.caffmob.cabinet_builder(**kwargs)
        if 'FINISHED' in res and context.active_object is not None:
            obj = context.active_object
            obj['btm_model_id'] = model.id
            obj['btm_drawers'] = int(model.drawers)
            obj['btm_corner_kind'] = model.corner_kind
            obj['btm_right_width_mm'] = float(model.right_width_mm)
            from . import ops_replace
            ops_replace.sync_preset_extras(obj)
        return res


classes = (BTM_OT_LibraryInsertModel,)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        if cls.is_registered:
            bpy.utils.unregister_class(cls)
