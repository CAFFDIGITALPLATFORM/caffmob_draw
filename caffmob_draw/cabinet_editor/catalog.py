"""Catálogo do Construtor de Armários (feature 008, T013; D-01). Python puro, sem `bpy`.

Os itens das abas, com os rótulos das capturas do Promob (`_reversa_forward/008-editor-armario-construtor/inputs/`):
id estável, aba e subaba (`group`), rótulo, descrição, chave da miniatura, parâmetros em mm, medida mínima, se
aceita "inserir invertido" e a ação que o Inserir pede ao editor. Regras geométricas não moram aqui: cada ação tem o
seu núcleo (`divisions`, `appliances`, `slides`…).

Os estilos de porta e de frente de gaveta não estão aqui: vêm da biblioteca do módulo em edição.
"""

from dataclasses import dataclass, field


@dataclass(frozen=True)
class Item:
    id: str
    tab: str
    group: str
    label: str
    description: str = ""
    action: str = ""
    params: tuple = ()                 # ((nome, valor em mm ou texto), …)
    size_mm: tuple = None              # (largura, altura, profundidade) do que o item ocupa
    margin_mm: float = 10.0            # folga de cada lado para caber no vão
    invertible: bool = False
    filter: str = ""                   # subfiltro (ex.: EXTERNAL / BUILT_IN); "" = vale em todos
    groove: bool = False               # deslizante com rasgo vertical (gola, cava, perfil, puxador integrado)
    extra: dict = field(default_factory=dict, compare=False, hash=False)

    @property
    def thumb(self):
        return self.id.lower()

    def param(self, name, default=None):
        return dict(self.params).get(name, default)

    def too_small(self, space_mm):
        """None se cabe no vão (largura, altura, profundidade em mm); senão a medida mínima (0 = sem exigência)."""
        if not self.size_mm:
            return None
        depth = max([self.size_mm[2]] + [APPLIANCE_SIZE_MM[c][2] for c in (self.param('appliances') or ())
                                         if c in APPLIANCE_SIZE_MM])      # o eletro atrás do painel também (EC-15)
        need = (self.size_mm[0] + 2 * self.margin_mm, self.size_mm[1] + 2 * self.margin_mm, depth)
        if (space_mm[0] + 1e-6 >= need[0] and space_mm[1] + 1e-6 >= need[1]
                and (depth <= 0.0 or space_mm[2] + 1e-6 >= depth)):
            return None
        return need


def _spacer(id_, label, thickness, follow=False):
    return Item(id_, 'DIVISIONS', 'SPACER', label, "Ocupa a faixa sem dividir o vão", 'ADD_SPACER',
                params=(('thickness', thickness), ('follow', follow)))


_WOOD = ("Lisa", "Reta", "Almofada", "Fresada", "Colonial", "Bicolor", "Gola Vertical", "Gola Vertical 2L",
         "Borda Alumínio", "Cava Vertical", "Chanfrada", "Country", "Perfil Y Vertical", "Perfil Y Vertical 2L")
_INTEGRATED = ("Obispa", "Contatto", "Torralba", "Altero")
_GROOVE = {"Gola Vertical", "Gola Vertical 2L", "Cava Vertical", "Perfil Y Vertical", "Perfil Y Vertical 2L"}


def _slide_id(label):
    return "SLIDE_" + label.upper().replace(" ", "_").replace("Í", "I").replace("Ç", "C")


def _slides():
    out = [Item(_slide_id(name), 'SLIDING', 'WOOD', name, "Porta de correr em madeira", 'INSERT_SLIDES',
                invertible=True, groove=name in _GROOVE) for name in _WOOD]
    out += [Item(_slide_id(name), 'SLIDING', 'WOOD', name + " — Pux Integrados", "Puxador integrado à folha",
                 'INSERT_SLIDES', invertible=True, groove=True) for name in _INTEGRATED]
    out.append(Item('SLIDE_ALU_FRAME', 'SLIDING', 'ALUMINIUM', "Quadro Alumínio", "Folha com quadro de alumínio",
                    'INSERT_SLIDES', invertible=True))
    return out


def _panel(id_, label, filter_, cutout, appliances):
    return Item(id_, 'INTERIOR', 'PANELS', label, "Painel com recorte para eletro", 'INSERT_INTERIOR',
                params=(('appliances', appliances),), size_mm=cutout, filter=filter_)


_OVEN, _MICRO, _COFFEE = (595.0, 595.0, 560.0), (595.0, 390.0, 400.0), (595.0, 455.0, 400.0)


def _interior():
    out = []
    for suffix, filter_, word in (("EXT", 'EXTERNAL', "Externo"), ("BI", 'BUILT_IN', "Embutido")):
        out += [
            _panel(f"PANEL_OVEN_MICRO_{suffix}", f"Painel Forno/Micro {word}", filter_,
                   (595.0, _OVEN[1] + _MICRO[1], 0.0), ('OVEN', 'MICRO')),
            _panel(f"PANEL_OVEN_{suffix}", f"Painel Forno {word}", filter_, (595.0, _OVEN[1], 0.0), ('OVEN',)),
            _panel(f"PANEL_MICRO_{suffix}", f"Painel Micro {word}", filter_, (595.0, _MICRO[1], 0.0), ('MICRO',)),
            _panel(f"PANEL_COFFEE_{suffix}", f"Painel Cafeteira {word}", filter_, (595.0, _COFFEE[1], 0.0),
                   ('COFFEE',)),
            Item(f"FRONT_{suffix}", 'INTERIOR', 'PANELS', f"Frontal {word}", "Chapa frontal sem recorte",
                 'INSERT_INTERIOR', filter=filter_),
        ]
    out += [
        Item('OVEN', 'INTERIOR', 'PANELS', "Forno", "Forno de referência (fora do corte)", 'INSERT_INTERIOR',
             size_mm=_OVEN),
        Item('MICRO', 'INTERIOR', 'PANELS', "Microondas", "Microondas de referência (fora do corte)",
             'INSERT_INTERIOR', size_mm=_MICRO),
        Item('COFFEE', 'INTERIOR', 'PANELS', "Cafeteira", "Cafeteira de referência (fora do corte)",
             'INSERT_INTERIOR', size_mm=_COFFEE),
        Item('VENT', 'INTERIOR', 'PANELS', "Respiro", "Painel com rasgo de ventilação", 'INSERT_INTERIOR',
             size_mm=(440.0, 30.0, 0.0)),
        Item('SUPPORT', 'INTERIOR', 'SUPPORTS', "Apoio de eletro", "Prateleira de apoio", 'INSERT_INTERIOR'),
        Item('PISTON', 'INTERIOR', 'PISTONS', "Pistão", "Pistão para porta basculante (ferragem)",
             'INSERT_INTERIOR'),
    ]
    return out


APPLIANCE_SIZE_MM = {'OVEN': _OVEN, 'MICRO': _MICRO, 'COFFEE': _COFFEE}

ITEMS = tuple([
    Item('DIV_NO_RECESS', 'DIVISIONS', 'RECESS', "Interna s/ Recuo — Tras 15mm", "Divisória sem recuo frontal",
         'ADD_DIVISION', params=(('front', 0.0), ('back', 15.0))),
    Item('DIV_RECESS', 'DIVISIONS', 'RECESS', "Interna c/ Recuo — Tras 15mm", "Divisória com recuo frontal",
         'ADD_DIVISION', params=(('front', 20.0), ('back', 15.0))),
    _spacer('SPACER_15', "Distanciador 15mm", 15.0),
    _spacer('SPACER_30', "Distanciador Duplo 30mm", 30.0),
    _spacer('SPACER_DIV', "Distanciador p/ Divisão 15mm", 15.0, follow=True),
    Item('DRAWER_CF', 'DRAWERS', 'DRAWERS', "Gaveta c/ CF", "Caixa Gaveta c/ Contra Frente", 'INSERT_DRAWERS'),
    Item('DRAWER_TALL', 'DRAWERS', 'TALL', "Gavetão", "Gaveta de frente alta (2 a 4 por vão)", 'INSERT_DRAWERS',
         params=(('min', 2), ('max', 4))),
    Item('DRAWER_INTERNAL', 'DRAWERS', 'INTERNAL', "Gaveta interna", "Gaveta atrás da porta, sem puxador",
         'INSERT_DRAWERS'),
    Item('DRAWER_BLUM', 'DRAWERS', 'BLUM', "Gaveta Blum", "Gaveta com corrediça Blum", 'INSERT_DRAWERS',
         params=(('slide', 'BLUM'),)),
    Item('FRONT_RETA', 'DRAWERS', 'FRONTS', "Reta", "Frente Reta"),
    Item('BACK_FULL', 'BACKS', 'FULL', "Fundo Inteiro", "Fundo de chapa inteira", 'SET_BACK'),
    Item('BACK_RECESSED', 'BACKS', 'RECESSED', "Fundo Inteiro Recuado", "Fundo recuado para dentro", 'SET_BACK'),
] + _interior() + _slides())

_BY_ID = {item.id: item for item in ITEMS}


def get(item_id):
    return _BY_ID.get(item_id)


def items(tab, group=None, filter_=None):
    """Itens da aba (e subaba); com `filter_`, só os do filtro ou sem filtro."""
    return [i for i in ITEMS if i.tab == tab and (group is None or i.group == group)
            and (filter_ is None or i.filter in ("", filter_))]


# Árvore de componentes extras da Estrutura (RN-07a): (chave, rótulo, chave-pai, valor padrão em m ou None).
# Pai sem valor próprio (Rodapés, Vistas, Vistas altas) liga e desliga os filhos.
TREE = (
    ('BASE_TOP_RECESSED', "Base Superior Recuada", None, None),
    ('FEET', "Pés Plásticos", None, 0.15),
    ('FOOT_1', "Posição 01", 'FEET', None),
    ('FOOT_2', "Posição 02", 'FEET', None),
    ('FOOT_3', "Posição 03", 'FEET', None),
    ('FOOT_4', "Posição 04", 'FEET', None),
    ('KICKS', "Rodapés", None, None),
    ('KICK_FRONT', "Frontal", 'KICKS', None),
    ('KICK_LEFT', "Esquerdo", 'KICKS', None),
    ('KICK_RIGHT', "Direito", 'KICKS', None),
    ('KICK_GRANITE', "Rodapés Granito", None, None),
    ('CLOSURE', "Fechamentos", None, 0.05),
    ('VIEWS', "Vistas", None, None),
    ('VIEW_FRONT', "Frontal", 'VIEWS', 0.15),
    ('VIEW_LEFT', "Esquerda", 'VIEWS', 0.15),
    ('VIEW_RIGHT', "Direita", 'VIEWS', 0.15),
    ('VIEWS_TALL', "Vistas (alto)", None, None),
    ('VIEW_TALL_LEFT', "Esquerda", 'VIEWS_TALL', 0.15),
    ('VIEW_TALL_RIGHT', "Direita", 'VIEWS_TALL', 0.15),
    ('VIEW_TALL_FRONT', "Frontal", 'VIEWS_TALL', 0.15),
)
TREE_GROUPS = {key for key, _l, parent, _v in TREE for key2, _l2, parent2, _v2 in TREE if parent2 == key}
CHILDREN = {key: [k for k, _l, parent, _v in TREE if parent == key] for key, *_ in TREE}
DEFAULT_ON = {'FOOT_1', 'FOOT_2', 'FOOT_3', 'FOOT_4'}     # posições dos pés começam ligadas

