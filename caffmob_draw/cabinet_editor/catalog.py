"""Catálogo do Construtor de Armários (feature 008, T013; D-01). Python puro, sem `bpy`.

Os itens das abas, com os rótulos das capturas do Promob (`_reversa_forward/008-editor-armario-construtor/inputs/`):
id estável, aba e subaba (`group`), rótulo, descrição, chave da miniatura, parâmetros em mm, medida mínima, se
aceita "inserir invertido" e a ação que o Inserir pede ao editor. Regras geométricas não moram aqui: cada ação tem o
seu núcleo (`divisions`, `appliances`, `slides`…).

Os estilos de porta e de frente de gaveta não estão aqui: vêm da biblioteca do módulo em edição.

Feature 015 (T021; RN-15 a RN-17, D-13): cada item pode valer só em alguns ambientes (`environments`, ids do catálogo
de estruturas: COZ, DOR; vazio = todos) e as abas filtram pelo ambiente da estrutura do módulo. Entram as variantes de
divisão da cozinha (Corta Sar, c/ Reb, Não Divide o Fundo) e do dormitório (Montante, Invisível, Corrediça, Aramada),
Somente Divisão, as gavetas de dormitório e os internos de roupeiro (cabideiros, calceiros, sapateira, porta-cintos).
A árvore da Estrutura ganha as peças das estruturas (sarrafos, tampo linear, rodapé, rodízios).
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
    environments: tuple = ()           # ambientes onde o item aparece (feature 015); () = todos
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
                params=(('appliances', appliances),), size_mm=cutout, filter=filter_, environments=_KITCHEN)


_OVEN, _MICRO, _COFFEE = (595.0, 595.0, 560.0), (595.0, 390.0, 400.0), (595.0, 455.0, 400.0)
_KITCHEN, _BEDROOM = ('COZ',), ('DOR',)


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
                 'INSERT_INTERIOR', filter=filter_, environments=_KITCHEN),
        ]
    out += [
        Item('OVEN', 'INTERIOR', 'PANELS', "Forno", "Forno de referência (fora do corte)", 'INSERT_INTERIOR',
             size_mm=_OVEN, environments=_KITCHEN),
        Item('MICRO', 'INTERIOR', 'PANELS', "Microondas", "Microondas de referência (fora do corte)",
             'INSERT_INTERIOR', size_mm=_MICRO, environments=_KITCHEN),
        Item('COFFEE', 'INTERIOR', 'PANELS', "Cafeteira", "Cafeteira de referência (fora do corte)",
             'INSERT_INTERIOR', size_mm=_COFFEE, environments=_KITCHEN),
        Item('VENT', 'INTERIOR', 'PANELS', "Respiro", "Painel com rasgo de ventilação", 'INSERT_INTERIOR',
             size_mm=(440.0, 30.0, 0.0), environments=_KITCHEN),
        Item('SUPPORT', 'INTERIOR', 'SUPPORTS', "Apoio de eletro", "Prateleira de apoio", 'INSERT_INTERIOR',
             environments=_KITCHEN),
        Item('PISTON', 'INTERIOR', 'PISTONS', "Pistão", "Pistão para porta basculante (ferragem)",
             'INSERT_INTERIOR'),
    ]
    out += _wardrobe()
    return out


def _wardrobe():
    """Internos de roupeiro (feature 015, RN-16): `kind` = papel no núcleo `wardrobe.py`."""
    def item(id_, label, description, kind, **params):
        return Item(id_, 'INTERIOR', 'WARDROBE', label, description, 'INSERT_WARDROBE',
                    params=(('kind', kind),) + tuple(params.items()), environments=_BEDROOM)
    return [
        item('HANGER_01', "Cabideiro 01", "Tubo de cabide abaixo da prateleira de cima", 'HANGER_ROD'),
        item('HANGER_02', "Cabideiro 02", "Tubo de cabide oval", 'HANGER_ROD', profile='OVAL'),
        item('HANGER_EXT', "Cab Extensível", "Cabideiro que puxa para fora (ferragem)", 'HANGER_ROD',
             profile='EXTENSIVEL'),
        item('ROD', "Tubo", "Tubo com suporte de reforço no meio", 'HANGER_ROD', profile='TUBO'),
        item('ROD_PLAIN', "Tubo s/ Reforço", "Tubo só com os suportes das pontas", 'HANGER_ROD', profile='TUBO_SR'),
        item('PANTS_WOOD_L', "Calceiro Madeira Esquerdo", "Calceiro de madeira, saída pela esquerda", 'PANTS_RACK',
             material='WOOD', side='LEFT'),
        item('PANTS_WOOD_C', "Calceiro Madeira Central", "Calceiro de madeira no meio do vão", 'PANTS_RACK',
             material='WOOD', side='CENTER'),
        item('PANTS_WOOD_R', "Calceiro Madeira Direito", "Calceiro de madeira, saída pela direita", 'PANTS_RACK',
             material='WOOD', side='RIGHT'),
        item('PANTS_WIRE_L', "Calceiro Aramado Esquerdo", "Calceiro aramado (ferragem)", 'PANTS_RACK',
             material='WIRE', side='LEFT'),
        item('PANTS_WIRE_R', "Calceiro Aramado Direito", "Calceiro aramado (ferragem)", 'PANTS_RACK',
             material='WIRE', side='RIGHT'),
        item('SHOE_RACK', "Sapateira", "Prateleira inclinada para sapatos", 'SHOE_RACK'),
        item('BELT_RACK', "Porta Cintos/Gravatas", "Suporte na lateral do vão (ferragem)", 'BELT_RACK'),
    ]


def _division(id_, label, description, environments=(), **params):
    """Variante de divisória ou prateleira do catálogo (feature 015, RN-15)."""
    return Item(id_, 'DIVISIONS', 'RECESS', label, description, 'ADD_DIVISION', params=tuple(params.items()),
                environments=environments)


APPLIANCE_SIZE_MM = {'OVEN': _OVEN, 'MICRO': _MICRO, 'COFFEE': _COFFEE}

ITEMS = tuple([
    Item('DIV_NO_RECESS', 'DIVISIONS', 'RECESS', "Interna s/ Recuo — Tras 15mm", "Divisória sem recuo frontal",
         'ADD_DIVISION', params=(('front', 0.0), ('back', 15.0))),
    Item('DIV_RECESS', 'DIVISIONS', 'RECESS', "Interna c/ Recuo — Tras 15mm", "Divisória com recuo frontal",
         'ADD_DIVISION', params=(('front', 20.0), ('back', 15.0))),
    _division('DIV_CORTA_SAR', "Interna s/ Recuo Tras Corta Sar 15mm", "Sobe até o topo e corta o sarrafo",
              _KITCHEN, front=0.0, back=15.0, variant='CORTA_SAR', orientation='VERTICAL'),
    _division('DIV_C_REB', "Interna c/ Reb 15mm", "Divisória com rebaixo para o fundo passar", _KITCHEN,
              front=0.0, back=0.0, variant='C_REB'),
    _division('DIV_KEEP_BACK', "Não Divide o Fundo c/ Recuo Front", "Prateleira fixa; o fundo continua inteiro",
              _KITCHEN, front=20.0, back=0.0, variant='NAO_DIVIDE_FUNDO', orientation='HORIZONTAL'),
    _division('DIV_MONTANTE', "Montante 18mm", "Divisória vertical de dormitório", _BEDROOM, front=0.0, back=0.0,
              variant='MONTANTE', orientation='VERTICAL'),
    _division('SHELF_INVISIBLE', "Invisível", "Divide o vão; não aparece no 3D nem no corte", _BEDROOM,
              kind='INVISIBLE', orientation='HORIZONTAL'),
    _division('SHELF_SLIDE', "Corrediça", "Prateleira sobre corrediças", _BEDROOM, front=20.0, back=0.0,
              variant='CORREDICA', orientation='HORIZONTAL'),
    _division('SHELF_WIRE', "Aramada", "Prateleira aramada (ferragem, fora do corte)", _BEDROOM,
              variant='ARAMADA', orientation='HORIZONTAL'),
    _division('DIVISION_ONLY', "Somente Divisão", "Divide o vão para agregados, sem peça", (),
              kind='DIVISION_ONLY'),
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
    Item('DRAWER_TRACK', 'DRAWERS', 'INTERNAL', "Interna p/ trilho",
         "Gaveta interna com a de baixo mais alta, para passar o trilho da porta de correr", 'INSERT_DRAWERS',
         params=(('track', True),), environments=_BEDROOM),
    Item('DRAWER_SHOE', 'DRAWERS', 'INTERNAL', "Sapateira", "Gaveta sapateira", 'INSERT_DRAWERS',
         environments=_BEDROOM),
    Item('DRAWER_SHELF_SLIDE', 'DRAWERS', 'INTERNAL', "Prateleira Corrediça", "Prateleira que corre para fora",
         'INSERT_DRAWERS', environments=_BEDROOM),
    Item('DRAWER_EXTERNAL', 'DRAWERS', 'DRAWERS', "Externas", "Gaveta externa de dormitório", 'INSERT_DRAWERS',
         environments=_BEDROOM),
    Item('FRONT_RETA', 'DRAWERS', 'FRONTS', "Reta", "Frente Reta"),
    Item('BACK_FULL', 'BACKS', 'FULL', "Fundo Inteiro", "Fundo de chapa inteira", 'SET_BACK'),
    Item('BACK_RECESSED', 'BACKS', 'RECESSED', "Fundo Inteiro Recuado", "Fundo recuado para dentro", 'SET_BACK'),
] + _interior() + _slides())

_BY_ID = {item.id: item for item in ITEMS}


# 067 (T079; RF-107): só é oferecido o item cuja ação tem executor validado no editor (`bridge.EDIT_006`/`EDIT_008`;
# o distanciador e o roupeiro passam pelos executores da divisão e do interior). O resto aparece com o motivo.
EXECUTOR_OF = {'ADD_DIVISION': 'ADD_DIVISION', 'ADD_SPACER': 'ADD_DIVISION', 'INSERT_DRAWERS': 'INSERT_DRAWERS',
               'INSERT_DOORS': 'INSERT_DOORS', 'INSERT_INTERIOR': 'INSERT_INTERIOR',
               'INSERT_WARDROBE': 'INSERT_INTERIOR', 'INSERT_SLIDES': 'INSERT_SLIDES', 'SET_BACK': 'SET_BACK'}
NO_EXECUTOR = "Sem executor nesta versão: o item ainda não pode ser inserido"
INTERNAL_ONLY_FRAMELESS = "Gaveta interna só existe no frameless"


def unavailable_reason(item, library=""):
    """Por que o item não pode ser inserido (msgid), ou None."""
    if item.id in DISABLED:
        return DISABLED[item.id]
    if not item.action or item.action not in EXECUTOR_OF:
        return NO_EXECUTOR
    if item.tab == 'DRAWERS' and item.group == 'INTERNAL' and library and library != 'FRAMELESS':
        return INTERNAL_ONLY_FRAMELESS
    return None


def get(item_id):
    return _BY_ID.get(item_id)


def items(tab, group=None, filter_=None, environment=None):
    """Itens da aba (e subaba); com `filter_`, só os do filtro ou sem filtro; com `environment`, só os desse
    ambiente ou de todos (feature 015)."""
    return [i for i in ITEMS if i.tab == tab and (group is None or i.group == group)
            and (filter_ is None or i.filter in ("", filter_))
            and (environment is None or not i.environments or environment in i.environments)]


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
    # Feature 015 (D-03): peças das estruturas de caixa; aparecem só nos módulos com estrutura (`STRUCTURE_KEYS`)
    ('STRETCHER_FRONT', "Sarrafo Frontal", None, None),
    ('STRETCHER_BACK', "Sarrafo Traseiro", None, None),
    ('STRETCHER_FULL', "Sarrafo Inteiro", None, None),
    ('TOP_LINEAR', "Tampo Linear", None, None),
    ('TOE_KICK', "Rodapés", None, None),
    ('CASTERS', "Rodízios", None, 0.10),
    ('SIDES_EXTENDED', "Laterais Engrossuradas", None, None),
)
STRUCTURE_KEYS = ('STRETCHER_FRONT', 'STRETCHER_BACK', 'STRETCHER_FULL', 'TOP_LINEAR', 'TOE_KICK', 'CASTERS',
                  'SIDES_EXTENDED')
# Item da árvore que aparece desabilitado, com o motivo (princípio VIII)
DISABLED = {'SIDES_EXTENDED': "Ainda não disponível nesta versão"}
# Nos módulos com estrutura, "Rodapés" é o rodapé da estrutura (TOE_KICK); os da 008 ficam para os sem estrutura
LEGACY_ONLY_KEYS = ('KICKS', 'KICK_FRONT', 'KICK_LEFT', 'KICK_RIGHT')
TREE_GROUPS = {key for key, _l, parent, _v in TREE for key2, _l2, parent2, _v2 in TREE if parent2 == key}
CHILDREN = {key: [k for k, _l, parent, _v in TREE if parent == key] for key, *_ in TREE}
DEFAULT_ON = {'FOOT_1', 'FOOT_2', 'FOOT_3', 'FOOT_4'}     # posições dos pés começam ligadas

