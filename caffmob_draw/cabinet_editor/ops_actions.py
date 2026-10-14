"""Botões internos do Editor de Armário (feature 004, T046; RF-03, RF-04, RF-06, RF-07, D-22).

Não têm `UNDO`: só registram um pedido na sessão (`props.Session.push`); quem edita o módulo é o modal do editor, para
que o Blender crie um passo de desfazer só no Confirmar. As edições são as da 003 sobre o vão do componente
selecionado (frente, estilo, puxador, material, divisões internas) e o desfazer/refazer do rascunho.

Feature 006 (T022): abas Estrutura e Divisão — adicionar, editar e remover divisão; editar, remover (com o modo) e
restaurar componente externo. Também só registram o pedido.
"""

import bpy  # type: ignore

from ..customize import spec
from ..customize.props import PULL_POSITION_ITEMS
from ..data import units
from ..data.i18n import N_, tr
from . import bridge, catalog, props
from .data_props import MATERIAL_ITEMS, MODE_ITEMS as REMOVE_MODE_ITEMS
from .structure import ROLE_LABELS


_ENUM_CACHE = {}


def _session_root():
    s = props.session()
    return (s, s.root()) if s is not None else (None, None)


def _adapter():
    _s, root = _session_root()
    return (root, bridge.adapter_of(root)) if root is not None else (None, None)


def selected_path():
    """Vão da biblioteca da peça selecionada ou, sem peça, o do vão alvo (feature 008, D-05)."""
    s, root = _session_root()
    if root is None:
        return None
    return bridge.opening_of(root, s.selected) or getattr(s, 'library_path', None)


def _front_items(self, context):
    root, adapter = _adapter()
    allowed = adapter.front_types(root) if adapter else []
    items = [(f, spec.FRONT_LABELS[f], "") for f in spec.FRONT_TYPES if f in allowed] or [('OPEN', "Vazio", "")]
    _ENUM_CACHE['front'] = items
    return items


def _style_items(self, context):
    _root, adapter = _adapter()
    names = adapter.style_names() if adapter else []
    items = [("", "Estilo do módulo", "Volta ao estilo da biblioteca")] + [(n, n, "") for n in names]
    _ENUM_CACHE['style'] = items
    return items


def _pull_items(self, context):
    _root, adapter = _adapter()
    pulls = adapter.pull_items() if adapter else []
    items = ([("", "Puxador do projeto", "Usa a escolha geral do projeto"), (spec.NO_PULL, N_("Sem puxador"), "")]
             + [(key, label, "") for key, label in pulls])
    _ENUM_CACHE['pull'] = items
    return items


class BTM_OT_CabinetEditorEdit(bpy.types.Operator):
    """Edita o vão do componente selecionado no Editor de Armário"""
    bl_idname = "caffmob.cabinet_editor_edit"
    bl_label = "Editar componente"
    bl_options = {'REGISTER', 'INTERNAL'}

    action: bpy.props.EnumProperty(items=[('FRONT', "Frente", ""), ('STYLE', "Estilo", ""), ('PULL', "Puxador", ""),
                                          ('MATERIAL', "Material", ""), ('INTERIOR', "Divisões internas", "")])  # type: ignore
    front: bpy.props.EnumProperty(name="Frente", items=_front_items)  # type: ignore
    drawer_count: bpy.props.IntProperty(name="Gavetas", default=1, min=1, max=spec.MAX_DRAWERS)  # type: ignore
    kind: bpy.props.EnumProperty(name="Frente", items=[('DOOR', "Porta", ""), ('DRAWER', "Gaveta", "")])  # type: ignore
    style: bpy.props.EnumProperty(name="Estilo", items=_style_items)  # type: ignore
    model: bpy.props.EnumProperty(name="Modelo", items=_pull_items)  # type: ignore
    position: bpy.props.EnumProperty(name="Posição", items=PULL_POSITION_ITEMS)  # type: ignore
    all_fronts: bpy.props.BoolProperty(name="Aplicar a todas as frentes", default=False)  # type: ignore
    target: bpy.props.EnumProperty(name="Aplicar em", items=[('FRONTS', "Frentes do vão", ""),
                                                            ('GROUP', "Grupo de peças", "")])  # type: ignore
    group: bpy.props.EnumProperty(name="Grupo", items=[(g, spec.GROUP_LABELS[g], "") for g in spec.GROUPS])  # type: ignore
    material: bpy.props.StringProperty(name="Material", description="Vazio = volta ao material da biblioteca")  # type: ignore
    shelves: bpy.props.IntProperty(name="Prateleiras", min=0, max=spec.MAX_SHELVES)  # type: ignore
    dividers: bpy.props.IntProperty(name="Divisórias", min=0, max=spec.MAX_DIVIDERS)  # type: ignore
    drawers: bpy.props.IntProperty(name="Gavetas internas", min=0, max=spec.MAX_DRAWERS)  # type: ignore
    heights: bpy.props.StringProperty(
        name="Alturas", description="Alturas das prateleiras a partir da base do vão, separadas por ';'. "
        "Vazio = espaçamento igual")  # type: ignore

    @classmethod
    def poll(cls, context):
        return props.session() is not None

    def invoke(self, context, event):
        needs_opening = self.action != 'MATERIAL' or self.target == 'FRONTS'
        if needs_opening and selected_path() is None:
            self.report({'WARNING'}, tr("Selecione um vão ou uma frente na vista"))
            return {'CANCELLED'}
        if self.action == 'INTERIOR':
            root, adapter = _adapter()
            current = adapter.read(root).opening(selected_path()) if adapter else None
            inner = current.interior if current is not None and current.interior else spec.Interior()
            self.shelves, self.dividers, self.drawers = inner.shelves, inner.dividers, inner.drawers
            unit = units.get_scene_length_unit(context.scene)
            self.heights = "; ".join(units.format_length(h, unit=unit) for h in inner.heights)
        if self.action == 'FRONT' and self.front != 'DRAWERS':
            return self.execute(context)
        return context.window_manager.invoke_props_dialog(self)

    def draw(self, context):
        layout = self.layout
        if self.action == 'FRONT':
            layout.prop(self, "drawer_count")
        elif self.action == 'STYLE':
            layout.prop(self, "kind", expand=True)
            layout.prop(self, "style")
        elif self.action == 'PULL':
            layout.prop(self, "model")
            layout.prop(self, "position")
            layout.prop(self, "all_fronts")
        elif self.action == 'MATERIAL':
            layout.prop(self, "target", expand=True)
            if self.target == 'GROUP':
                layout.prop(self, "group")
            layout.prop_search(self, "material", bpy.data, "materials")
        else:
            layout.prop(self, "shelves")
            layout.prop(self, "dividers")
            layout.prop(self, "drawers")
            layout.prop(self, "heights")

    def execute(self, context):
        s = props.session()
        path = selected_path() or ""
        data = {'path': path, 'targets': [s.selected] if s.selected else []}
        if self.action == 'FRONT':
            data.update(front=self.front, drawer_count=self.drawer_count)
        elif self.action == 'STYLE':
            data.update(kind=self.kind, style=self.style)
        elif self.action == 'PULL':
            data.update(model=self.model, position=self.position, all_fronts=self.all_fronts)
        elif self.action == 'MATERIAL':
            data.update(target=self.target, group=self.group, material=self.material)
        else:
            unit = units.get_scene_length_unit(context.scene)
            try:
                heights = [units.parse_length(raw.strip(), default_unit=unit)
                           for raw in self.heights.split(";") if raw.strip()]
            except ValueError:
                self.report({'WARNING'}, tr("Alturas inválidas"))
                return {'CANCELLED'}
            data.update(shelves=self.shelves, dividers=self.dividers, drawers=self.drawers, heights=heights)
        s.push('edit', (self.action, data))
        return {'FINISHED'}


class BTM_OT_CabinetEditorHistory(bpy.types.Operator):
    """Desfaz ou refaz no rascunho do editor (Ctrl+Z / Ctrl+Shift+Z)"""
    bl_idname = "caffmob.cabinet_editor_history"
    bl_label = "Desfazer no editor"
    bl_options = {'REGISTER', 'INTERNAL'}

    redo: bpy.props.BoolProperty(default=False)  # type: ignore

    @classmethod
    def poll(cls, context):
        return props.session() is not None

    def execute(self, context):
        props.session().push('redo' if self.redo else 'undo')
        return {'FINISHED'}


class BTM_OT_CabinetEditorSaveModule(bpy.types.Operator):
    """Salva o armário como está no editor na biblioteca do usuário (Salvar como módulo da 003)"""
    bl_idname = "caffmob.cabinet_editor_save_module"
    bl_label = "Salvar como módulo"
    bl_options = {'REGISTER', 'INTERNAL'}

    @classmethod
    def poll(cls, context):
        return props.session() is not None and props.session().root() is not None

    def invoke(self, context, event):
        root = props.session().root()
        for obj in context.selected_objects:
            obj.select_set(False)
        root.select_set(True)
        context.view_layer.objects.active = root
        return bpy.ops.caffmob.module_save('INVOKE_DEFAULT')


# Feature 006 --------------------------------------------------------------------------------------------------
def _push(action, data, targets=()):
    s = props.session()
    s.push('edit', (action, dict(data, targets=list(targets))))


def _division(uid):
    _s, root = _session_root()
    if root is None:
        return None
    return next((o for o in root.children if getattr(o, 'btm_division', None) is not None
                 and o.btm_division.is_division and o.btm_division.uid == uid), None)


class _SessionOperator:
    bl_options = {'REGISTER', 'INTERNAL'}

    @classmethod
    def poll(cls, context):
        return props.session() is not None and props.session().root() is not None


class BTM_OT_CabinetEditorAssembly(_SessionOperator, bpy.types.Operator):
    """Troca a montagem do armário pelo rascunho do editor (Ctrl+Z, Cancelar e Aplicar a tratam)"""
    bl_idname = "caffmob.cabinet_editor_assembly"
    bl_label = "Montagem"

    assembly: bpy.props.EnumProperty(name="Montagem", items=[('LATERAL', "Lateral passante", ""),
                                                            ('BASE', "Base passante", "")])  # type: ignore

    def execute(self, context):
        _push('SET_ASSEMBLY', {'assembly': self.assembly})
        return {'FINISHED'}


class BTM_OT_CabinetEditorDivisionAdd(_SessionOperator, bpy.types.Operator):
    """Adiciona uma chapa de divisão no vão escolhido, com a orientação e os recuos marcados"""
    bl_idname = "caffmob.cabinet_editor_division_add"
    bl_label = "Adicionar divisão"

    def execute(self, context):
        s = props.session()
        ui = context.window_manager.btm_cabinet_editor
        if not s.space or s.space not in s.spaces:
            self.report({'WARNING'}, tr("Escolha um vão livre: clique nele na vista ou escolha na lista"))
            return {'CANCELLED'}
        _push('ADD_DIVISION', {'space': s.space, 'orientation': ui.new_orientation,
                               'use_front': ui.new_use_front, 'front': ui.new_front,
                               'use_back': ui.new_use_back, 'back': ui.new_back})
        return {'FINISHED'}


class BTM_OT_CabinetEditorDivisionEdit(_SessionOperator, bpy.types.Operator):
    """Edita a posição, os recuos, o material e a espessura da divisão"""
    bl_idname = "caffmob.cabinet_editor_division_edit"
    bl_label = "Editar divisão"

    uid: bpy.props.StringProperty(options={'HIDDEN'})  # type: ignore
    offset: bpy.props.FloatProperty(
        name="Posição", subtype='DISTANCE', unit='LENGTH', min=0.0,
        description="Distância da face esquerda (vertical) ou de baixo (horizontal) do vão até a chapa")  # type: ignore
    use_front: bpy.props.BoolProperty(name="Recuo na frente")  # type: ignore
    front: bpy.props.FloatProperty(name="Recuo da frente", subtype='DISTANCE', unit='LENGTH', min=0.0)  # type: ignore
    use_back: bpy.props.BoolProperty(name="Recuo atrás")  # type: ignore
    back: bpy.props.FloatProperty(name="Recuo de trás", subtype='DISTANCE', unit='LENGTH', min=0.0)  # type: ignore
    thickness: bpy.props.FloatProperty(
        name="Espessura", subtype='DISTANCE', unit='LENGTH', min=0.0,
        description="0 = a espessura da Divisória no Configurador de Dimensões")  # type: ignore
    material: bpy.props.EnumProperty(name="Material da chapa", items=MATERIAL_ITEMS)  # type: ignore

    def invoke(self, context, event):
        obj = _division(self.uid)
        if obj is None:
            return {'CANCELLED'}
        d = obj.btm_division
        self.offset, self.use_front, self.front = d.offset, d.use_front, d.front
        self.use_back, self.back, self.thickness = d.use_back, d.back, d.thickness
        self.material = d.material if d.material in {i[0] for i in MATERIAL_ITEMS} else ''
        return context.window_manager.invoke_props_dialog(self, title=obj.name)

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.prop(self, "offset")
        row = layout.row(heading=tr("Recuo na frente"))
        row.prop(self, "use_front", text="")
        sub = row.row()
        sub.active = self.use_front
        sub.prop(self, "front", text="")
        row = layout.row(heading=tr("Recuo atrás"))
        row.prop(self, "use_back", text="")
        sub = row.row()
        sub.active = self.use_back
        sub.prop(self, "back", text="")
        layout.prop(self, "thickness")
        layout.prop(self, "material")

    def execute(self, context):
        obj = _division(self.uid)
        _push('EDIT_DIVISION', {'uid': self.uid, 'offset': self.offset, 'use_front': self.use_front,
                                'front': self.front, 'use_back': self.use_back, 'back': self.back,
                                'thickness': self.thickness, 'material': self.material},
              [obj.name] if obj is not None else ())
        return {'FINISHED'}


class BTM_OT_CabinetEditorDivisionRemove(_SessionOperator, bpy.types.Operator):
    """Remove a divisão (e as que estão dentro dos vãos dela)"""
    bl_idname = "caffmob.cabinet_editor_division_remove"
    bl_label = "Remover divisão"

    uid: bpy.props.StringProperty(options={'HIDDEN'})  # type: ignore

    def execute(self, context):
        _push('REMOVE_DIVISION', {'uid': self.uid})
        return {'FINISHED'}


class BTM_OT_CabinetEditorPartRemove(_SessionOperator, bpy.types.Operator):
    """Remove o componente externo do armário"""
    bl_idname = "caffmob.cabinet_editor_part_remove"
    bl_label = "Remover componente"

    role: bpy.props.StringProperty(options={'HIDDEN'})  # type: ignore
    mode: bpy.props.EnumProperty(name="Ao remover", items=REMOVE_MODE_ITEMS, default='KEEP')  # type: ignore

    def _caps(self):
        _s, root = _session_root()
        if root is None:
            return {}
        from ..customize.adapters import common
        return common.call(bridge.adapter_of(root), 'structure_caps', root).get(self.role, {}).get('modes', {})

    def invoke(self, context, event):
        self.mode = 'KEEP'
        title = tr("Remover {}").format(tr(ROLE_LABELS.get(self.role, self.role)).lower())
        return context.window_manager.invoke_props_dialog(self, title=title, confirm_text=tr("Remover"))

    def draw(self, context):
        caps = self._caps()
        col = self.layout.column()
        for key, label, help_text in REMOVE_MODE_ITEMS:
            reason = caps.get(key, tr("Indisponível"))
            row = col.row()
            row.enabled = reason is None
            row.prop_enum(self, "mode", key, text=tr(label))
            sub = col.row()
            sub.enabled = False
            sub.label(text=reason if reason else tr(help_text))
            col.separator(factor=0.5)

    def execute(self, context):
        reason = self._caps().get(self.mode, tr("Indisponível"))
        if reason is not None:
            self.report({'WARNING'}, reason)
            return {'CANCELLED'}
        _push('REMOVE_PART', {'role': self.role, 'mode': self.mode})
        return {'FINISHED'}


class BTM_OT_CabinetEditorPartRestore(_SessionOperator, bpy.types.Operator):
    """Devolve o componente removido (e desfaz o ajuste de medidas do modo usado)"""
    bl_idname = "caffmob.cabinet_editor_part_restore"
    bl_label = "Restaurar componente"

    role: bpy.props.StringProperty(options={'HIDDEN'})  # type: ignore

    def execute(self, context):
        _push('RESTORE_PART', {'role': self.role})
        return {'FINISHED'}


class BTM_OT_CabinetEditorPartEdit(_SessionOperator, bpy.types.Operator):
    """Edita o material e a espessura do componente neste armário"""
    bl_idname = "caffmob.cabinet_editor_part_edit"
    bl_label = "Editar componente"

    role: bpy.props.StringProperty(options={'HIDDEN'})  # type: ignore
    thickness: bpy.props.FloatProperty(
        name="Espessura", subtype='DISTANCE', unit='LENGTH', min=0.0, max=0.06,
        description="0 = volta ao valor do Configurador de Dimensões")  # type: ignore
    material: bpy.props.EnumProperty(name="Material da chapa", items=MATERIAL_ITEMS)  # type: ignore

    def invoke(self, context, event):
        _s, root = _session_root()
        entry = root.btm_structure.item(self.role) if root is not None else None
        self.thickness = entry.thickness if entry is not None else 0.0
        material = entry.material if entry is not None else ''
        self.material = material if material in {i[0] for i in MATERIAL_ITEMS} else ''
        return context.window_manager.invoke_props_dialog(self, title=tr(ROLE_LABELS.get(self.role, self.role)))

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.prop(self, "thickness")
        layout.prop(self, "material")

    def execute(self, context):
        _push('EDIT_PART', {'role': self.role, 'thickness': self.thickness, 'material': self.material})
        return {'FINISHED'}


# Feature 008 (T032; D-21) ---------------------------------------------------------------------------------------
NO_SPACE = N_("Selecione um vão na vista")
NO_LIBRARY = N_("Este vão não pertence a um vão da biblioteca")
INSERT_TABS = [('DIVISIONS', "Divisões", ""), ('DRAWERS', "Gavetas", ""), ('INTERIOR', "Internos", ""),
               ('DOORS', "Portas", ""), ('SLIDING', "Deslizantes", ""), ('BACKS', "Fundos", "")]


def insert_reason(context, tab):
    """Motivo de o Inserir da aba estar desabilitado, ou None (D-21)."""
    s = props.session()
    if s is None:
        return tr(NO_SPACE)
    if tab in ('DIVISIONS', 'DRAWERS', 'INTERIOR', 'DOORS') and (not s.space or s.space not in s.spaces):
        return tr(NO_SPACE)
    if tab in ('DRAWERS', 'DOORS') and not s.library_path:
        return tr(NO_LIBRARY)
    ui = context.window_manager.btm_cabinet_editor
    item = catalog.get(ui.catalog_item)
    if tab in ('INTERIOR', 'SLIDING') and (item is None or item.tab != tab):     # item de outra aba (EC-05)
        return tr("Escolha um item do catálogo")
    return None


def _division_payload(ui, s):
    from . import divisions as dv
    base = {'space': s.space, 'use_front': ui.new_use_front, 'front': ui.new_front, 'use_back': ui.new_use_back,
            'back': ui.new_back}
    item = catalog.get(ui.catalog_item)
    if ui.div_kind == 'NONE':
        return 'REMOVE_IN_SPACE', {'space': s.space}
    if ui.div_kind == 'SPACER':
        item = item if item is not None and item.group == 'SPACER' else catalog.get('SPACER_15')
        orientation = ui.new_orientation if ui.div_mode == 'MULTIPLE' else ui.div_mode
        return 'ADD_DIVISION', {'space': s.space, 'orientation': orientation, 'kind': dv.SPACER,
                                'thickness': item.param('thickness') / 1000.0, 'follow': bool(item.param('follow'))}
    kind = dv.MOVABLE if ui.div_kind == 'MOVABLE' else dv.FIXED
    orientation = ui.div_mode
    if item is not None and item.group == 'RECESS':
        front = item.param('front') or 0.0
        base.update(use_front=front > 0, front=front / 1000.0 or ui.new_front)
        if item.param('back'):                     # "Tras 15mm" (questions.md, pergunta 46)
            base.update(use_back=True, back=item.param('back') / 1000.0)
        base['variant'] = item.param('variant') or ""                   # feature 015 (RN-15)
        kind = item.param('kind') or kind                               # Invisível, Somente Divisão
        if item.param('orientation') and ui.div_mode != 'MULTIPLE':
            orientation = item.param('orientation')
        if kind == dv.MOVABLE and item.param('front') is None:          # item sem recuo próprio: o do padrão
            base.update(use_front=True, front=_shelf_setback(s))
    if ui.div_mode == 'MULTIPLE':
        return 'ADD_MANY', dict(base, orientation=ui.new_orientation, count=ui.div_count, kind=kind)
    return 'ADD_DIVISION', dict(base, orientation=orientation, kind=kind)


def _shelf_setback(s):
    """Recuo frontal da prateleira móvel (m) do Padrão de Dimensões na linha do módulo (feature 015, Q5)."""
    from ..standards import api, cabinet_defaults
    from . import scene_divisions
    root = s.root()
    definition = api.active_definition(bpy.context.scene)
    values = api.definition_values(definition) if definition is not None else {}
    line = scene_divisions.line_of(root) if root is not None else 'COZ'
    return cabinet_defaults.structure_params(values, line)['shelf_setback']


def insert_payload(context, tab):
    s = props.session()
    ui = context.window_manager.btm_cabinet_editor
    if tab == 'DIVISIONS':
        return _division_payload(ui, s)
    if tab == 'DRAWERS':
        return 'INSERT_DRAWERS', {'space': s.space, 'count': ui.drawer_count, 'variant': ui.drawer_tab,
                                  'style': ui.drawer_style, 'pull': ui.drawer_pull}
    if tab == 'DOORS':
        scope = 'FLIP' if ui.door_region == 'FLIP' else ui.door_scope
        return 'INSERT_DOORS', {'space': s.space, 'scope': scope, 'region': ui.door_region, 'style': ui.door_style,
                                'invert': ui.invert, 'pull': ui.door_pull}
    if tab == 'INTERIOR':
        return 'INSERT_INTERIOR', {'catalog_id': ui.catalog_item, 'space': s.space}
    if tab == 'SLIDING':
        return 'INSERT_SLIDES', {'item': ui.catalog_item, 'leaves': ui.slide_leaves, 'invert': ui.invert}
    root = s.root()
    holder = root.btm_structure if root is not None else None
    return 'SET_BACK', {'mode': ui.back_tab, 'setback': holder.back_setback if holder else 0.02,
                        'auto': holder.auto_back if holder else True, 'insert': True}


class BTM_OT_CabinetEditorInsert(_SessionOperator, bpy.types.Operator):
    """Insere no vão escolhido o item da aba, com as opções marcadas"""
    bl_idname = "caffmob.cabinet_editor_insert"
    bl_label = "Inserir"

    tab: bpy.props.EnumProperty(items=INSERT_TABS, options={'HIDDEN'})  # type: ignore

    @classmethod
    def poll(cls, context):
        s = props.session()
        if s is None or s.root() is None:
            return False
        return True

    @classmethod
    def description(cls, context, properties):
        return insert_reason(context, properties.tab) or tr("Insere no vão escolhido o item da aba")

    def execute(self, context):
        reason = insert_reason(context, self.tab)
        if reason:
            self.report({'WARNING'}, reason)
            return {'CANCELLED'}
        action, data = insert_payload(context, self.tab)
        _push(action, data)
        return {'FINISHED'}


class BTM_OT_CabinetEditorApply(_SessionOperator, bpy.types.Operator):
    """Grava as alterações no armário sem fechar o editor (um passo de desfazer)"""
    bl_idname = "caffmob.cabinet_editor_apply"
    bl_label = "Aplicar"

    @classmethod
    def poll(cls, context):
        s = props.session()
        if s is None or s.root() is None:
            return False
        if s.blocking():
            cls.poll_message_set(tr("Corrija os erros para aplicar"))
            return False
        if not s.draft.dirty():
            cls.poll_message_set(tr("Nada para aplicar"))
            return False
        return True

    def execute(self, context):
        props.session().push('apply')
        return {'FINISHED'}


class BTM_OT_CabinetEditorPick(_SessionOperator, bpy.types.Operator):
    """Escolhe o item do catálogo"""
    bl_idname = "caffmob.cabinet_editor_pick"
    bl_label = "Escolher item"

    item: bpy.props.StringProperty(options={'HIDDEN'})  # type: ignore

    @classmethod
    def description(cls, context, properties):
        found = catalog.get(properties.item)
        return found.description or found.label if found is not None else ""

    def execute(self, context):
        context.window_manager.btm_cabinet_editor.catalog_item = self.item
        props.session().redraw()
        return {'FINISHED'}


class BTM_OT_CabinetEditorRemoveItem(_SessionOperator, bpy.types.Operator):
    """Remove o interno ou as portas deslizantes"""
    bl_idname = "caffmob.cabinet_editor_remove_item"
    bl_label = "Remover"

    kind: bpy.props.EnumProperty(items=[('INTERIOR', "Interno", ""), ('SLIDES', "Deslizantes", "")],
                                 options={'HIDDEN'})  # type: ignore
    slot: bpy.props.IntProperty(options={'HIDDEN'})  # type: ignore

    def execute(self, context):
        _push('REMOVE_INTERIOR' if self.kind == 'INTERIOR' else 'REMOVE_SLIDES', {'slot': self.slot})
        return {'FINISHED'}


classes = (BTM_OT_CabinetEditorEdit, BTM_OT_CabinetEditorHistory, BTM_OT_CabinetEditorSaveModule,
           BTM_OT_CabinetEditorDivisionAdd, BTM_OT_CabinetEditorDivisionEdit, BTM_OT_CabinetEditorDivisionRemove,
           BTM_OT_CabinetEditorPartRemove, BTM_OT_CabinetEditorPartRestore, BTM_OT_CabinetEditorPartEdit,
           BTM_OT_CabinetEditorInsert, BTM_OT_CabinetEditorApply, BTM_OT_CabinetEditorPick,
           BTM_OT_CabinetEditorRemoveItem, BTM_OT_CabinetEditorAssembly)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        if cls.is_registered:
            bpy.utils.unregister_class(cls)
