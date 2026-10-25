"""Estado do Editor de Armário (feature 004, T014; data-delta §1.5, D-21, D-22).

- `Session` (em memória, uma por vez): raiz do módulo, rascunho (`state.Draft`), peças da vista frontal, componente
  selecionado, mensagens, ajustes automáticos, vista 2D, janela/área e os pedidos que o modal executa.
- `WindowManager.btm_cabinet_editor`: campos do painel. As medidas são virtuais (`get`/`set`): o `set` só registra um
  pedido na sessão; quem edita o módulo é o modal (D-22), para o Blender criar um passo de desfazer só no Confirmar.
- Feature 006 (D-01, D-13, D-14): aba ativa, opções da próxima divisão (lembradas enquanto o editor está aberto),
  subvão escolhido e os espelhos das listas de componentes externos e de divisões.
"""

import bpy  # type: ignore

EDITOR_CATEGORY = "Editor de Armário"


class Session:
    def __init__(self, root_name, library, draft):
        self.root_name = root_name
        self.library = library
        self.draft = draft
        self.parts = []                   # elevation.Part
        self.initial_parts = []
        self.selected = None              # nome do componente
        self.messages = []                # validate.Message
        self.adjustments = []             # (nome, mudança)
        self.limits = {}
        self.view = None
        self.window_ptr = 0
        self.area_ptr = 0
        self.restore_area_type = None
        self.requests = []                # [(tipo, dados)] executados pelo modal
        self.request = None               # 'ok' | 'cancel'
        self.error = ""
        self.space = ""                   # subvão escolhido na aba Divisão (feature 006)
        self.spaces = {}                  # caminho → caixa (lo, hi) dos subvãos-folha, no referencial da vista
        self.space_labels = {}            # caminho → rótulo
        self.removed_parts = []           # elevation.Part das peças removidas (desenhadas tracejadas)
        self.library_path = None          # vão da biblioteca que contém o vão alvo (feature 008)
        self.library_box = None
        self.last_moved = None            # divisória movida pela última seta (Passo inicial)
        self.applied = False              # houve Aplicar nesta sessão

    def root(self):
        return bpy.data.objects.get(self.root_name)

    def push(self, kind, data=None):
        self.requests.append((kind, data))
        self.redraw()

    def blocking(self):
        return any(m.blocks for m in self.messages)

    def redraw(self):
        wm = bpy.context.window_manager
        for window in wm.windows:
            for area in window.screen.areas:
                if area.as_pointer() == self.area_ptr or area.type == 'VIEW_3D':
                    area.tag_redraw()


_session = [None]


def session():
    return _session[0]


def start(root_name, library, draft):
    _session[0] = Session(root_name, library, draft)
    return _session[0]


def end():
    _session[0] = None


# Campos virtuais ---------------------------------------------------------------------------------------------

_DIM_INDEX = {'width': 0, 'height': 1, 'depth': 2}


def _dim_get(name):
    def get(_self):
        s = session()
        return float(s.draft.current.dimensions[_DIM_INDEX[name]]) if s is not None else 0.0
    return get


def _dim_set(name):
    def set_(_self, value):
        s = session()
        if s is not None:
            s.push('dimension', (name, float(value)))
    return set_


def _index_update(self, context):
    s = session()
    if s is None or not (0 <= self.component_index < len(self.components)):
        return
    s.selected = self.components[self.component_index].name
    s.redraw()


class BTM_PG_CabinetEditorComponent(bpy.types.PropertyGroup):
    kind: bpy.props.StringProperty()  # type: ignore
    label: bpy.props.StringProperty()  # type: ignore
    flagged: bpy.props.BoolProperty()  # type: ignore   # tem mensagem


class BTM_PG_CabinetEditorMessage(bpy.types.PropertyGroup):
    code: bpy.props.StringProperty()  # type: ignore
    severity: bpy.props.StringProperty()  # type: ignore
    component: bpy.props.StringProperty()  # type: ignore
    parameter: bpy.props.StringProperty()  # type: ignore
    value: bpy.props.StringProperty()  # type: ignore
    range: bpy.props.StringProperty()  # type: ignore
    action: bpy.props.StringProperty()  # type: ignore
    blocks: bpy.props.BoolProperty()  # type: ignore


class BTM_PG_CabinetEditorAdjustment(bpy.types.PropertyGroup):
    component: bpy.props.StringProperty()  # type: ignore
    change: bpy.props.StringProperty()  # type: ignore


# Feature 008 (T003; D-02): as 7 abas do Construtor de Armários. O número de cada item continua estável: o antigo
# FINISH (2) da 006 não existe mais e um editor salvo nele cai em STRUCTURE.
TAB_ITEMS = [
    ('STRUCTURE', "Estrutura", "Tipo, medidas e componentes do armário", 'MOD_BUILD', 0),
    ('DIVISIONS', "Divisões", "Divisórias, distanciadores e inserção múltipla", 'MOD_LATTICE', 1),
    ('DRAWERS', "Gavetas", "Gavetas, gavetões, internas e Blum", 'NLA_PUSHDOWN', 3),
    ('INTERIOR', "Internos", "Painéis para eletros, apoios e pistões", 'OUTLINER_OB_LIGHTPROBE', 4),
    ('DOORS', "Portas", "Portas e puxadores", 'MESH_PLANE', 5),
    ('SLIDING', "Deslizantes", "Portas de correr", 'ARROW_LEFTRIGHT', 6),
    ('BACKS', "Fundos", "Fundo inteiro ou recuado", 'MOD_SOLIDIFY', 7),
]
DIV_MODE_ITEMS = [('VERTICAL', "Vertical", ""), ('HORIZONTAL', "Horizontal", ""),
                  ('MULTIPLE', "Inserção múltipla", "Várias chapas iguais de uma vez")]
DIV_KIND_ITEMS = [('MOVABLE', "Divisórias Móveis", "Reguláveis, com furação nas peças vizinhas"),
                  ('FIXED', "Divisórias Fixas", ""), ('SPACER', "Distanciador", "Ocupa a faixa sem dividir o vão"),
                  ('NONE', "Sem Divisória", "Remove a divisória do vão")]
DRAWER_TAB_ITEMS = [('DRAWERS', "Gavetas", ""), ('TALL', "Gavetões", "Gavetas de frente alta"),
                    ('INTERNAL', "Internas", "Gaveta atrás da porta"), ('BLUM', "Blum", "Corrediça Blum")]
DOOR_REGION_ITEMS = [('LOWER', "Inferior", ""), ('UPPER', "Superior", ""), ('TALL', "Alta", ""),
                     ('FLIP', "Basculante", "")]
DOOR_SCOPE_ITEMS = [('BOTH', "Ambas", "Duas portas"), ('WHOLE', "Inteira", "Uma porta no vão"),
                    ('LEFT', "Esquerda", "Dobradiça à esquerda"), ('RIGHT', "Direita", "Dobradiça à direita")]
INTERIOR_GROUP_ITEMS = [('PANELS', "Painel p/ Eletros", ""), ('LIBRARY', "Biblioteca", ""),
                        ('SUPPORTS', "Apoios", ""), ('PISTONS', "Pistões", ""),
                        ('WARDROBE', "Cabideiros e Calceiros", "Internos de roupeiro (feature 015)")]
INTERIOR_FILTER_ITEMS = [('EXTERNAL', "Externos", ""), ('BUILT_IN', "Embutidos", "")]
SLIDE_FAMILY_ITEMS = [('WOOD', "Madeira", ""), ('ALUMINIUM', "Alumínio", "")]
BACK_TAB_ITEMS = [('FULL', "Inteiro", ""), ('RECESSED', "Inteiro Recuado", "")]


def _dynamic(name):
    """Itens de enum vindos dos operadores (estilos e puxadores da biblioteca do módulo em edição)."""
    def items(self, context):
        from . import ops_actions
        return getattr(ops_actions, name)(self, context)
    return items
_SPACE_CACHE = []


def _space_items(self, context):
    s = session()
    items = [(path, s.space_labels.get(path, path), "") for path in sorted(s.spaces)] if s is not None else []
    _SPACE_CACHE[:] = items or [("", "Sem vão interno", "")]
    return _SPACE_CACHE


def _space_get(self):
    s = session()
    if s is None or not s.space:
        return 0
    for index, item in enumerate(_space_items(self, None)):
        if item[0] == s.space:
            return index
    return 0


def _space_set(self, value):
    s = session()
    items = _space_items(self, None)
    if s is not None and 0 <= value < len(items):
        s.space = items[value][0]
        s.redraw()


class BTM_PG_CabinetEditorStructureRow(bpy.types.PropertyGroup):
    role: bpy.props.StringProperty()  # type: ignore
    label: bpy.props.StringProperty()  # type: ignore
    size: bpy.props.StringProperty()  # type: ignore          # medidas da chapa, já formatadas
    material: bpy.props.StringProperty()  # type: ignore      # material da chapa em uso
    thickness: bpy.props.StringProperty()  # type: ignore     # espessura em uso, formatada
    removed: bpy.props.BoolProperty()  # type: ignore
    mode: bpy.props.StringProperty()  # type: ignore          # modo usado na remoção
    changed: bpy.props.BoolProperty()  # type: ignore         # alterado neste armário
    reason_remove: bpy.props.StringProperty()  # type: ignore  # vazio = pode remover
    reason_edit: bpy.props.StringProperty()  # type: ignore    # vazio = pode editar espessura


class BTM_PG_CabinetEditorDivisionRow(bpy.types.PropertyGroup):
    uid: bpy.props.StringProperty()  # type: ignore
    label: bpy.props.StringProperty()  # type: ignore
    detail: bpy.props.StringProperty()  # type: ignore
    flagged: bpy.props.BoolProperty()  # type: ignore


# Campos virtuais da Estrutura e das cotas (feature 008, T033; D-07, D-15, D-16) ----------------------------------
def _root():
    s = session()
    return s.root() if s is not None else None


def _extra_enabled(root, key):
    from . import catalog
    holder = getattr(root, 'btm_structure', None)
    if holder is None:
        return False
    if key in catalog.TREE_GROUPS and key not in ('FEET',):
        return any(_extra_enabled(root, child) for child in catalog.CHILDREN[key])
    entry = holder.extra(key)
    if entry is not None:
        return bool(entry.enabled)
    if key in catalog.STRUCTURE_KEYS:                   # feature 015: sem marca própria vale a estrutura
        from . import structures_core
        recipe = structures_core.get(getattr(getattr(root, 'btm_cabinet', None), 'structure_id', ""))
        return recipe.has(key) if recipe is not None else False
    return key in catalog.DEFAULT_ON


def _tree_get(key):
    def get(_self):
        root = _root()
        return _extra_enabled(root, key) if root is not None else False
    return get


def _tree_set(key):
    def set_(_self, value):
        from . import catalog
        s = session()
        if s is None:
            return
        keys = catalog.CHILDREN[key] if key in catalog.TREE_GROUPS and key != 'FEET' else [key]
        for k in keys:
            s.push('edit', ('TOGGLE_EXTRA', {'key': k, 'enabled': bool(value), 'targets': []}))
    return set_


def _value_get(key):
    def get(_self):
        from . import extras
        root = _root()
        entry = root.btm_structure.extra(key) if root is not None else None
        return float(entry.value) if entry is not None and entry.value else extras.DEFAULTS.get(key, 0.0)
    return get


def _value_set(key):
    def set_(_self, value):
        s = session()
        if s is not None:
            s.push('edit', ('TOGGLE_EXTRA', {'key': key, 'value': float(value), 'targets': []}))
    return set_


def _comp_get(role):
    def get(_self):
        root = _root()
        entry = root.btm_structure.item(role) if root is not None else None
        return not (entry is not None and entry.removed)
    return get


def _comp_set(role):
    def set_(_self, value):
        s = session()
        if s is not None:
            action = 'RESTORE_PART' if value else 'REMOVE_PART'
            s.push('edit', (action, {'role': role, 'mode': 'KEEP', 'targets': []}))
    return set_


def _bays_get(_self):
    from . import bays, scene_divisions
    root = _root()
    if root is None:
        return 1
    return bays.count(scene_divisions.core(bpy.context.scene, root))


def _bays_set(_self, value):
    s = session()
    if s is not None:
        s.push('edit', ('SET_BAYS', {'count': int(value), 'targets': []}))


def environment():
    """Ambiente (COZ, DOR…) da estrutura de caixa do módulo em edição, ou None (feature 015, D-13)."""
    from . import structures_core
    root = _root()
    recipe = structures_core.get(getattr(getattr(root, 'btm_cabinet', None), 'structure_id', "")) if root else None
    return recipe.environment if recipe is not None else None


def _bay_of_selection():
    """(índice do vão do subvão selecionado, número de vãos, largura atual em m) ou None (feature 015)."""
    from . import bays, divisions as dv, scene_divisions
    s, root = session(), _root()
    if s is None or root is None or not s.space:
        return None
    core = scene_divisions.core(bpy.context.scene, root)
    total = bays.count(core)
    if total < 2:
        return None
    index = bays.bay_index(s.space, total)
    leaves, _cuts, _orphans = dv.resolve(scene_divisions.roots(bpy.context, root), [d for d in core if d.bay])
    box = leaves.get(bays.chain(index) + ".a") if index < total - 1 else leaves.get(bays.chain(index))
    return index, total, (box.size(0) if box is not None else 0.0)


def _bay_width_get(_self):
    found = _bay_of_selection()
    return found[2] if found is not None else 0.0


def _bay_width_set(_self, value):
    found, s = _bay_of_selection(), session()
    if found is not None and s is not None:
        s.push('edit', ('SET_BAY_WIDTH', {'index': found[0], 'width': float(value), 'targets': []}))


def _selected_division():
    from . import divisions as dv, scene_divisions
    s, root = session(), _root()
    if s is None or root is None or not s.selected:
        return None, None
    obj = bpy.data.objects.get(s.selected)
    if obj is None or obj.parent != root or not obj.btm_division.is_division:
        return None, None
    roots = scene_divisions.roots(bpy.context, root)
    core = scene_divisions.core(bpy.context.scene, root)
    _leaves, cuts, _o = dv.resolve(roots, core)
    division = next((d for d in core if d.uid == obj.btm_division.uid), None)
    if division is None or division.uid not in cuts:
        return None, None
    return division, cuts[division.uid][0]


def _pos_get(which):
    def get(_self):
        from . import position
        division, space = _selected_division()
        return position.cotas(space, division)[which] if division is not None else 0.0
    return get


def _pos_set(which):
    def set_(_self, value):
        from . import position
        s = session()
        division, space = _selected_division()
        if s is None or division is None:
            return
        if which == 'front':
            data = {'use_front': value > 0.0, 'front': float(value) or division.front}
        elif which == 'back':
            data = {'use_back': value > 0.0, 'back': float(value) or division.back}
        else:
            data = {'offset': position.offset_from_cota(space, division, which, value)}
        s.push('edit', ('EDIT_DIVISION', dict(data, uid=division.uid, targets=[])))
    return set_


def has_position():
    return _selected_division()[0] is not None


class BTM_PG_CabinetEditorState(bpy.types.PropertyGroup):
    width: bpy.props.FloatProperty(name="Largura", subtype='DISTANCE', unit='LENGTH',
                                   get=_dim_get('width'), set=_dim_set('width'))  # type: ignore
    height: bpy.props.FloatProperty(name="Altura", subtype='DISTANCE', unit='LENGTH',
                                    get=_dim_get('height'), set=_dim_set('height'))  # type: ignore
    depth: bpy.props.FloatProperty(name="Profundidade", subtype='DISTANCE', unit='LENGTH',
                                   get=_dim_get('depth'), set=_dim_set('depth'))  # type: ignore
    components: bpy.props.CollectionProperty(type=BTM_PG_CabinetEditorComponent)  # type: ignore
    component_index: bpy.props.IntProperty(default=-1, update=_index_update)  # type: ignore
    messages: bpy.props.CollectionProperty(type=BTM_PG_CabinetEditorMessage)  # type: ignore
    adjustments: bpy.props.CollectionProperty(type=BTM_PG_CabinetEditorAdjustment)  # type: ignore
    # Feature 006
    tab: bpy.props.EnumProperty(name="Aba", items=TAB_ITEMS, default='STRUCTURE')  # type: ignore
    measures_open: bpy.props.BoolProperty(name="Medidas", default=True)  # type: ignore   # 067 RF-106
    new_orientation: bpy.props.EnumProperty(
        name="Orientação", items=[('VERTICAL', "Vertical", "Chapa em pé: separa esquerda e direita", 'SNAP_EDGE', 0),
                                  ('HORIZONTAL', "Horizontal", "Chapa deitada: separa cima e baixo", 'SNAP_FACE',
                                   1)])  # type: ignore
    new_use_front: bpy.props.BoolProperty(name="Recuo na frente", default=False)  # type: ignore
    new_front: bpy.props.FloatProperty(name="Recuo da frente", subtype='DISTANCE', unit='LENGTH', default=0.02,
                                       min=0.0, max=1.0)  # type: ignore
    new_use_back: bpy.props.BoolProperty(name="Recuo atrás", default=False)  # type: ignore
    new_back: bpy.props.FloatProperty(name="Recuo de trás", subtype='DISTANCE', unit='LENGTH', default=0.02,
                                      min=0.0, max=1.0)  # type: ignore
    space: bpy.props.EnumProperty(name="Vão", items=_space_items, get=_space_get, set=_space_set)  # type: ignore
    structure: bpy.props.CollectionProperty(type=BTM_PG_CabinetEditorStructureRow)  # type: ignore
    structure_index: bpy.props.IntProperty(default=-1)  # type: ignore
    divisions: bpy.props.CollectionProperty(type=BTM_PG_CabinetEditorDivisionRow)  # type: ignore
    division_index: bpy.props.IntProperty(default=-1)  # type: ignore
    # Feature 008: opções das abas do Construtor (data-delta §1.4)
    catalog_item: bpy.props.StringProperty(name="Item")  # type: ignore
    invert: bpy.props.BoolProperty(name="Inserir invertido", default=False)  # type: ignore
    div_mode: bpy.props.EnumProperty(name="Modo", items=DIV_MODE_ITEMS, default='VERTICAL')  # type: ignore
    div_kind: bpy.props.EnumProperty(name="Tipo", items=DIV_KIND_ITEMS, default='FIXED')  # type: ignore
    div_count: bpy.props.IntProperty(name="Quantidade", default=2, min=1, max=10)  # type: ignore
    drawer_tab: bpy.props.EnumProperty(name="Gavetas", items=DRAWER_TAB_ITEMS, default='DRAWERS')  # type: ignore
    drawer_count: bpy.props.IntProperty(name="Número de gavetas", default=4, min=1, max=8)  # type: ignore
    drawer_style: bpy.props.EnumProperty(name="Frente", items=_dynamic('_style_items'))  # type: ignore
    drawer_pull: bpy.props.EnumProperty(name="Puxador", items=_dynamic('_pull_items'))  # type: ignore
    door_region: bpy.props.EnumProperty(name="Região", items=DOOR_REGION_ITEMS, default='LOWER')  # type: ignore
    door_scope: bpy.props.EnumProperty(name="Portas", items=DOOR_SCOPE_ITEMS, default='BOTH')  # type: ignore
    door_style: bpy.props.EnumProperty(name="Estilo", items=_dynamic('_style_items'))  # type: ignore
    door_pull: bpy.props.EnumProperty(name="Puxador", items=_dynamic('_pull_items'))  # type: ignore
    interior_group: bpy.props.EnumProperty(name="Internos", items=INTERIOR_GROUP_ITEMS,
                                           default='PANELS')  # type: ignore
    interior_filter: bpy.props.EnumProperty(name="Filtro", items=INTERIOR_FILTER_ITEMS,
                                            default='EXTERNAL')  # type: ignore
    slide_family: bpy.props.EnumProperty(name="Família", items=SLIDE_FAMILY_ITEMS, default='WOOD')  # type: ignore
    slide_leaves: bpy.props.IntProperty(name="Folhas", default=2, min=2, max=3)  # type: ignore
    back_tab: bpy.props.EnumProperty(name="Fundo", items=BACK_TAB_ITEMS, default='FULL')  # type: ignore
    step: bpy.props.FloatProperty(name="Passo", subtype='DISTANCE', unit='LENGTH', default=0.01,
                                  min=0.0001)  # type: ignore
    step_initial: bpy.props.FloatProperty(name="Passo inicial", subtype='DISTANCE', unit='LENGTH',
                                          default=0.0, min=0.0)  # type: ignore


def _add_virtual_fields():
    """Campos da árvore (um por chave do catálogo e por papel da estrutura), vãos e cotas, criados antes do registro."""
    from . import catalog
    notes = BTM_PG_CabinetEditorState.__annotations__
    for key, label, _parent, default in catalog.TREE:
        notes['tree_' + key] = bpy.props.BoolProperty(name=label, get=_tree_get(key), set=_tree_set(key))
        if default is not None:
            notes['value_' + key] = bpy.props.FloatProperty(
                name=label, subtype='DISTANCE', unit='LENGTH', min=0.0, get=_value_get(key), set=_value_set(key))
    for role in ('TOP', 'BOTTOM', 'BACK', 'LEFT', 'RIGHT'):
        notes['comp_' + role] = bpy.props.BoolProperty(get=_comp_get(role), set=_comp_set(role))
    notes['bays'] = bpy.props.IntProperty(name="Número de vãos", min=1, max=10, get=_bays_get, set=_bays_set)
    notes['bay_width'] = bpy.props.FloatProperty(name="Largura do vão", subtype='DISTANCE', unit='LENGTH', min=0.0,
                                                 get=_bay_width_get, set=_bay_width_set)     # feature 015 (RN-14)
    for which, label in (('front', "Cota anterior"), ('low', "Cota inferior"), ('back', "Cota posterior"),
                         ('high', "Cota superior")):
        notes['pos_' + which] = bpy.props.FloatProperty(name=label, subtype='DISTANCE', unit='LENGTH',
                                                        get=_pos_get(which), set=_pos_set(which))


_add_virtual_fields()

classes = (BTM_PG_CabinetEditorComponent, BTM_PG_CabinetEditorMessage, BTM_PG_CabinetEditorAdjustment,
           BTM_PG_CabinetEditorStructureRow, BTM_PG_CabinetEditorDivisionRow, BTM_PG_CabinetEditorState)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.WindowManager.btm_cabinet_editor = bpy.props.PointerProperty(type=BTM_PG_CabinetEditorState)


def unregister():
    end()
    if hasattr(bpy.types.WindowManager, 'btm_cabinet_editor'):
        del bpy.types.WindowManager.btm_cabinet_editor
    for cls in reversed(classes):
        if cls.is_registered:
            bpy.utils.unregister_class(cls)
