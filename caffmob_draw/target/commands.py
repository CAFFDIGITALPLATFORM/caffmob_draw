"""CommandRouter (feature 067, D-08, D-09; RF-002, RF-005): os comandos do painel e do menu do botão direito.

A lista sai do inventário da 1.8.0 (`tests/data/067_inventario_1_8_0.json`): todo operador que o painel mostrava para
um tipo continua tendo rota para ele, numa seção com escopo. Cada rota tem o operador, a seção e a condição. Os
botões de "Agregados e folhas", o "Mover Sobre" e o "Selecionar conjunto" usam a condição de `capabilities`; os de
módulo, parede, porta e geometria valem pelo tipo do alvo; os que já têm `poll` próprio no operador (por exemplo
`caffmob.resize_width`) ficam com a condição do próprio operador (`None`). O painel e o menu leem a mesma rota para o
mesmo snapshot.
"""

from dataclasses import dataclass

from ..data.i18n import N_
from . import capabilities as caps
from . import resolver as r

# Seções, na ordem do painel.
S_HEADER, S_MODULE, S_POSITION, S_GEOMETRY, S_WALL, S_OPENING, S_LEAF, S_AGGREGATES = (
    'header', 'module', 'position', 'geometry', 'wall', 'opening', 'leaf', 'aggregates')
SECTION_LABELS = {
    S_HEADER: N_("Selecionado"), S_MODULE: N_("Módulo"), S_POSITION: N_("Posição e vínculo"),
    S_GEOMETRY: N_("Geometria"), S_WALL: N_("Parede"), S_OPENING: N_("Porta"), S_LEAF: N_("Folha"),
    S_AGGREGATES: N_("Agregados e folhas"),
}

_IN_MODULE = frozenset({r.MODULE, r.PART, r.FRONT, r.LEAF, r.MEMBER})
_MOVABLE = frozenset({r.MODULE, r.PART, r.FRONT, r.LEAF, r.MEMBER, r.GEOMETRY, r.OTHER})
_REASON_MODULE = N_("Vale para módulo e para as peças dele.")


@dataclass(frozen=True)
class Route:
    operator: str
    section: str
    condition: object = None        # callable(target) -> (bool, motivo), ou None = o poll do operador decide
    essential: bool = False
    menu: bool = True               # também no menu do botão direito


def _kinds(kinds, reason):
    allowed = frozenset(kinds)
    return lambda t: (True, '') if t.kind in allowed else (False, reason)


def _hb_module(t):
    owner_library = t.library
    ok = t.kind in _IN_MODULE and owner_library not in ('AUTHORED', 'BTM', '')
    return (True, '') if ok else (False, N_("Vale para módulo das bibliotecas e para as peças dele."))


def _module_customize(t):
    ok = t.kind in (r.MODULE, r.PART, r.FRONT, r.LEAF) and t.library != 'AUTHORED'
    return (True, '') if ok else (False, N_("Personalizar vale para módulo de biblioteca e módulo rápido."))


def _cap(command_id):
    return lambda t: caps.check(command_id, t)


def _room_door(t):
    ok = t.kind == r.OPENING and t.detail == 'DOOR' and t.library == 'HB'
    return (True, '') if ok else (False, N_("Vale para porta de ambiente."))


ROUTES = (
    Route('caffmob.target_select_owner', S_HEADER, _cap('select_owner'), essential=True),
    # Módulo (as peças continuam chegando às ações do módulo dono, no escopo Conjunto).
    Route('caffmob.cabinet_editor', S_MODULE, _kinds(_IN_MODULE, _REASON_MODULE), essential=True),
    Route('caffmob.module_save', S_MODULE, _kinds(_IN_MODULE, _REASON_MODULE)),
    Route('caffmob.fronts_set_open', S_MODULE, _module_customize),
    Route('caffmob.customize_set_front', S_MODULE, _module_customize),
    Route('caffmob.customize_set_interior', S_MODULE, _module_customize),
    Route('caffmob.customize_set_material', S_MODULE, _module_customize),
    Route('caffmob.customize_set_pull', S_MODULE, _module_customize),
    Route('caffmob.customize_clear', S_MODULE, _module_customize),
    Route('caffmob.customize_set_style', S_MODULE, _hb_module),
    # Posição e vínculo.
    Route('caffmob.move_over_toggle', S_POSITION, _cap('move_over'), essential=True),
    Route('caffmob.stick_to_face', S_POSITION, _kinds(_MOVABLE, N_("Este tipo não gruda em face."))),
    Route('caffmob.set_insertion_plane', S_POSITION),
    Route('caffmob.resize_width', S_POSITION),
    Route('caffmob.check_collisions', S_POSITION, _kinds(_MOVABLE, N_("Este tipo não tem colisão."))),
    # Geometria livre.
    Route('caffmob.geometry_duplicate', S_GEOMETRY, _kinds((r.GEOMETRY,), N_("Vale para geometria livre.")),
          essential=True),
    Route('caffmob.geometry_mirror', S_GEOMETRY, _kinds((r.GEOMETRY,), N_("Vale para geometria livre."))),
    Route('caffmob.geometry_delete', S_GEOMETRY, _kinds((r.GEOMETRY,), N_("Vale para geometria livre."))),
    # Parede.
    Route('caffmob.wall_visibility', S_WALL, _kinds((r.WALL,), N_("Vale para parede.")), essential=True),
    Route('caffmob.wall_lower', S_WALL, _kinds((r.WALL,), N_("Vale para parede."))),
    Route('caffmob.wall_remove', S_WALL, _kinds((r.WALL,), N_("Vale para parede."))),
    # Porta de ambiente.
    Route('caffmob.door_set_angle', S_OPENING, _room_door, essential=True),
    Route('caffmob.door_move_to_wall', S_OPENING, _room_door),
    Route('caffmob_doors_windows.flip_door_hand', S_OPENING, _room_door),
    Route('caffmob_doors_windows.flip_door_swing', S_OPENING, _room_door),
    Route('caffmob.remove_opening', S_OPENING,
          lambda t: (True, '') if t.kind == r.OPENING and t.library == 'BTM' else
          (False, N_("Vale para abertura da camada nova."))),
    # Folha.
    Route('caffmob.aggregate_unconvert', S_LEAF, _kinds((r.LEAF,), N_("Vale para folha convertida."))),
    # Agregados e folhas (capacidades).
    Route('caffmob_draw.authored_rule_reference', S_AGGREGATES,
          _kinds((r.MEMBER,), N_("Vale para membro de armário autoral.")), menu=False),
) + tuple(Route(caps.BY_ID[c].operator, S_AGGREGATES, None if c in caps.DELEGATED else _cap(c))
          for c in caps.AGGREGATE_COMMANDS)

BY_OPERATOR = {route.operator: route for route in ROUTES}


@dataclass(frozen=True)
class Entry:
    """Uma rota avaliada para o alvo: o botão e se ele executa."""
    operator: str
    section: str
    enabled: bool
    reason: str
    essential: bool


def evaluate(route, target):
    if target is None:
        return Entry(route.operator, route.section, False, N_("Selecione um objeto na viewport."), route.essential)
    if route.condition is None:
        return Entry(route.operator, route.section, True, '', route.essential)
    ok, reason = route.condition(target)
    return Entry(route.operator, route.section, ok, reason, route.essential)


def commands_for(target, menu=False):
    """Rotas avaliadas para o alvo, na ordem do painel; `menu=True` filtra as que vão ao botão direito."""
    return [evaluate(route, target) for route in ROUTES if not menu or route.menu]


def menu_items(target):
    """O que o menu do botão direito oferece: só o que executa no alvo, e as ações do módulo só no módulo; na chapa,
    as ações da chapa, nunca as do módulo (RF-005)."""
    return [entry for entry in commands_for(target, menu=True)
            if entry.enabled and (entry.section != S_MODULE or target.kind == r.MODULE)]
