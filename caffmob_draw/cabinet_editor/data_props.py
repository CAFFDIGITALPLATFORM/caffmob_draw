"""Dados gravados no módulo pelas abas Estrutura e Divisão (feature 006, T001; data-delta §1.1, §1.2).

- `Object.btm_structure` (na raiz do módulo): só os componentes externos que o usuário mexeu. Ausente = como a
  biblioteca faz.
- `Object.btm_division` (em cada chapa de divisão): subvão, orientação, posição e recuos. A chapa é um `CabinetPart`
  filho da raiz (D-03); o objeto é desenhado e lido como qualquer peça.

Medidas em metros. Espessura 0 e material vazio = segue o Configurador de Dimensões.

Feature 008 (T001, T002): `Object.btm_extra` (peças das abas novas: extras da Estrutura, internos, deslizantes);
`btm_structure` ganha o fundo (inteiro/recuado, automático) e o estado da árvore de extras; `btm_division` ganha `bay`
(Número de vãos), `kind` (fixa, móvel, distanciador) e `follow` (distanciador p/ divisão).
"""

import bpy  # type: ignore

ROLE_ITEMS = [
    ('TOP', "Tampo", "Chapa de cima"),
    ('BOTTOM', "Base", "Chapa de baixo"),
    ('BACK', "Fundo", "Chapa de trás"),
    ('LEFT', "Lateral esquerda", ""),
    ('RIGHT', "Lateral direita", ""),
]
MODE_ITEMS = [
    ('KEEP', "Manter tudo", "Medidas e demais chapas ficam onde estão; só a chapa sai"),
    ('EXTEND', "Estender as vizinhas", "As chapas vizinhas avançam até a borda; o vão interno cresce"),
    ('SHRINK', "Reduzir o armário", "As medidas externas diminuem pela espessura da chapa; o vão interno fica igual"),
]
ORIENTATION_ITEMS = [
    ('VERTICAL', "Vertical", "Chapa em pé: separa esquerda e direita"),
    ('HORIZONTAL', "Horizontal", "Chapa deitada: separa cima e baixo"),
]
MATERIAL_ITEMS = [('', "Do Configurador", "Segue o Configurador de Dimensões")] + [
    (m, m, "") for m in ('MDF', 'MDP', 'COMPENSADO', 'OSB', 'VIDRO', 'OUTRO')]


EXTRA_KIND_ITEMS = [(k, k, "") for k in (
    'BASE_TOP_RECESSED', 'FOOT', 'KICK_FRONT', 'KICK_LEFT', 'KICK_RIGHT', 'KICK_GRANITE', 'CLOSURE', 'VIEW_FRONT',
    'VIEW_LEFT', 'VIEW_RIGHT', 'VIEW_TALL_LEFT', 'VIEW_TALL_RIGHT', 'VIEW_TALL_FRONT', 'APPLIANCE_PANEL', 'APPLIANCE',
    'APPLIANCE_SUPPORT', 'PISTON', 'SLIDE_TRACK', 'SLIDE_LEAF',
    # Feature 015 (data-delta §1.3): sempre no fim, para o índice gravado nos arquivos não mudar.
    'HANGER_ROD', 'PANTS_RACK', 'SHOE_RACK', 'BELT_RACK', 'CASTER', 'STRETCHER', 'TOE_KICK_STRUCT')]
DIVISION_KIND_ITEMS = [('FIXED', "Fixa", ""), ('MOVABLE', "Móvel", "Regulável, com furação nas peças vizinhas"),
                       ('SPACER', "Distanciador", "Ocupa a faixa sem dividir o vão"),
                       # Feature 015 (RN-15): dividem o vão sem gerar peça nem entrar no corte
                       ('INVISIBLE', "Invisível", "Divide o vão; não aparece no 3D nem no corte"),
                       ('DIVISION_ONLY', "Somente Divisão", "Divide o vão para agregados, sem peça")]
BACK_MODE_ITEMS = [('FULL', "Inteiro", ""), ('RECESSED', "Inteiro Recuado", "")]


class BTM_PG_Extra(bpy.types.PropertyGroup):
    is_extra: bpy.props.BoolProperty(default=False)  # type: ignore
    kind: bpy.props.EnumProperty(items=EXTRA_KIND_ITEMS)  # type: ignore
    catalog_id: bpy.props.StringProperty()  # type: ignore
    space: bpy.props.StringProperty()  # type: ignore
    slot: bpy.props.IntProperty()  # type: ignore
    params: bpy.props.StringProperty()  # type: ignore        # JSON


class BTM_PG_StructureExtra(bpy.types.PropertyGroup):
    kind: bpy.props.StringProperty()  # type: ignore          # chave da árvore (catalog.TREE)
    enabled: bpy.props.BoolProperty(default=False)  # type: ignore
    value: bpy.props.FloatProperty(subtype='DISTANCE', unit='LENGTH')  # type: ignore


class BTM_PG_StructureItem(bpy.types.PropertyGroup):
    role: bpy.props.EnumProperty(name="Componente", items=ROLE_ITEMS)  # type: ignore
    removed: bpy.props.BoolProperty(name="Removido", default=False)  # type: ignore
    mode: bpy.props.EnumProperty(name="Ao remover", items=MODE_ITEMS, default='KEEP')  # type: ignore
    thickness: bpy.props.FloatProperty(name="Espessura", subtype='DISTANCE', unit='LENGTH', min=0.0,
                                       description="0 = segue o Configurador")  # type: ignore
    material: bpy.props.StringProperty(name="Material da chapa",
                                       description="Vazio = segue o Configurador")  # type: ignore


class BTM_PG_Structure(bpy.types.PropertyGroup):
    components: bpy.props.CollectionProperty(type=BTM_PG_StructureItem)  # type: ignore
    back_mode: bpy.props.EnumProperty(name="Fundo", items=BACK_MODE_ITEMS, default='FULL')  # type: ignore
    back_setback: bpy.props.FloatProperty(name="Recuo do fundo", subtype='DISTANCE', unit='LENGTH', default=0.02,
                                          min=0.0)  # type: ignore
    auto_back: bpy.props.BoolProperty(name="Inserir automaticamente", default=True)  # type: ignore
    extras: bpy.props.CollectionProperty(type=BTM_PG_StructureExtra)  # type: ignore

    def extra(self, kind, create=False):
        for entry in self.extras:
            if entry.kind == kind:
                return entry
        if not create:
            return None
        entry = self.extras.add()
        entry.kind = kind
        return entry

    def extras_dict(self):
        return {e.kind: {"enabled": bool(e.enabled), "value": float(e.value)} for e in self.extras}

    def extras_from_dict(self, data):
        self.extras.clear()
        for kind, values in sorted((data or {}).items()):
            entry = self.extras.add()
            entry.kind, entry.enabled, entry.value = kind, bool(values.get("enabled")), float(values.get("value", 0.0))

    def backs_dict(self):
        return {"mode": self.back_mode, "setback": float(self.back_setback), "auto": bool(self.auto_back)}

    def backs_from_dict(self, data):
        data = data or {}
        self.back_mode = data.get("mode", 'FULL') or 'FULL'
        self.back_setback = float(data.get("setback", 0.02))
        self.auto_back = bool(data.get("auto", True))

    def item(self, role, create=False):
        for entry in self.components:
            if entry.role == role:
                return entry
        if not create:
            return None
        entry = self.components.add()
        entry.role = role
        return entry

    def to_dict(self):
        return {e.role: {"removed": bool(e.removed), "mode": e.mode, "thickness": float(e.thickness),
                         "material": e.material} for e in self.components}

    def from_dict(self, data):
        self.components.clear()
        for role, values in sorted((data or {}).items()):
            entry = self.components.add()
            entry.role = role
            entry.removed = bool(values.get("removed", False))
            entry.mode = values.get("mode", 'KEEP') or 'KEEP'
            entry.thickness = float(values.get("thickness", 0.0) or 0.0)
            entry.material = str(values.get("material", "") or "")


class BTM_PG_Division(bpy.types.PropertyGroup):
    is_division: bpy.props.BoolProperty(default=False)  # type: ignore
    uid: bpy.props.StringProperty()  # type: ignore
    space: bpy.props.StringProperty(name="Subvão", default="s0")  # type: ignore
    orientation: bpy.props.EnumProperty(name="Orientação", items=ORIENTATION_ITEMS)  # type: ignore
    offset: bpy.props.FloatProperty(name="Posição", subtype='DISTANCE', unit='LENGTH')  # type: ignore
    use_front: bpy.props.BoolProperty(name="Recuo na frente", default=False)  # type: ignore
    front: bpy.props.FloatProperty(name="Recuo da frente", subtype='DISTANCE', unit='LENGTH', default=0.02,
                                   min=0.0)  # type: ignore
    use_back: bpy.props.BoolProperty(name="Recuo atrás", default=False)  # type: ignore
    back: bpy.props.FloatProperty(name="Recuo de trás", subtype='DISTANCE', unit='LENGTH', default=0.02,
                                  min=0.0)  # type: ignore
    thickness: bpy.props.FloatProperty(name="Espessura", subtype='DISTANCE', unit='LENGTH', min=0.0,
                                       description="0 = segue o Configurador")  # type: ignore
    material: bpy.props.StringProperty(name="Material da chapa",
                                       description="Vazio = segue o Configurador")  # type: ignore
    bay: bpy.props.BoolProperty(default=False)  # type: ignore            # gerada pelo Número de vãos (008)
    kind: bpy.props.EnumProperty(items=DIVISION_KIND_ITEMS, default='FIXED')  # type: ignore
    follow: bpy.props.StringProperty()  # type: ignore                    # uid da divisória seguida (008)
    # Feature 015 (data-delta §1.3, §1.4): variante de catálogo (CORTA_SAR, C_REB, NAO_DIVIDE_FUNDO, CORREDICA,
    # ARAMADA, MONTANTE; vazio = como antes) e largura digitada do vão à esquerda da divisória de vão (0 = igual).
    variant: bpy.props.StringProperty()  # type: ignore
    bay_width: bpy.props.FloatProperty(subtype='DISTANCE', unit='LENGTH', default=0.0, min=0.0)  # type: ignore

    FIELDS = ('uid', 'space', 'orientation', 'offset', 'use_front', 'front', 'use_back', 'back', 'thickness',
              'material', 'bay', 'kind', 'follow', 'variant', 'bay_width')

    def to_dict(self):
        return {name: getattr(self, name) for name in self.FIELDS}

    def from_dict(self, data):
        for name in self.FIELDS:
            if name in data:
                setattr(self, name, data[name])
        self.is_division = True


classes = (BTM_PG_Extra, BTM_PG_StructureExtra, BTM_PG_StructureItem, BTM_PG_Structure, BTM_PG_Division)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Object.btm_structure = bpy.props.PointerProperty(type=BTM_PG_Structure)
    bpy.types.Object.btm_division = bpy.props.PointerProperty(type=BTM_PG_Division)
    bpy.types.Object.btm_extra = bpy.props.PointerProperty(type=BTM_PG_Extra)


def unregister():
    for name in ('btm_extra', 'btm_division', 'btm_structure'):
        if hasattr(bpy.types.Object, name):
            delattr(bpy.types.Object, name)
    for cls in reversed(classes):
        if cls.is_registered:
            bpy.utils.unregister_class(cls)
