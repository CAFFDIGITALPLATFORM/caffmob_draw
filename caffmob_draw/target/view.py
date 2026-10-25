"""ViewModel da janela de propriedades (feature 067, D-02; RF-003, RF-004): Python puro.

`build(target, mode)` descreve o que o painel mostra para o alvo: o cabeçalho (nome, tipo, escopo, caminho do dono e
"Selecionar conjunto") e as seções, cada uma com campos, ações e notas. O draw (`ui/object_properties.draw_selected`)
só traduz isso em `layout`. As seções de campos vêm do adaptador do tipo (`target/adapters`); as ações vêm do
CommandRouter, avaliadas para o mesmo alvo.

Modos (D-05): a Completa mostra tudo; o Essencial mostra só as seções e os itens marcados `essential`, então o
Essencial está sempre contido na Completa.
"""

from dataclasses import dataclass, field

from ..data.i18n import N_
from . import commands as cmd
from . import resolver as r

ESSENTIAL, COMPLETE = 'ESSENTIAL', 'COMPLETE'

# Onde cada `data` dos campos mora; o draw resolve, os testes comparam com o inventário (classe RNA).
DATA_OWNERS = {
    'selection': 'BTM_PG_SelectionEdit',      # Scene.btm_selection (campos virtuais pelo snapshot)
    'object': 'Object',                       # o objeto do alvo
    'part': 'BTM_PG_Part',                    # Object.btm_part
    'geometry': 'BTM_PG_GeometryProps',       # Object.btm_geometry
    'aggregate': 'BTM_PG_Aggregate',          # Object.btm_aggregate
    'member': 'BTM_PG_Member',                # Object.btm_member
    'cladding': 'BTM_PG_Cladding',            # WindowManager.btm_cladding_draft: rascunho do revestimento (RF-020)
    'door': 'BTM_PG_Opening',                 # Object.btm_opening_real da caixa da porta de ambiente
    'move_over': 'BTM_PG_MoveOverState',      # WindowManager.btm_move_over
    'insertion': 'BTM_PG_InsertionPlane',     # Object.btm_plane (a colisão do próprio objeto: Herdar/Ativa/Desativada)
    'target': 'BTM_PG_Target',                # WindowManager.btm_target
    'light': 'Light',                         # Object.data da luz
    'camera': 'Camera',                       # Object.data da câmera
    'wall': 'BTM_PG_WallSegment',             # Object.btm_wall da parede da camada nova
    'btm_opening': 'BTM_PG_OpeningProperties',  # Object.btm_opening da abertura da camada nova
}


@dataclass(frozen=True)
class Field:
    data: str
    prop: str
    label: str = ''             # msgid; vazio = o nome da propriedade
    read_only: bool = False
    reason: str = ''            # por que está somente leitura
    essential: bool = False
    index: int = -1             # componente de um vetor (-1 = todos)
    mixed: bool = False         # seleção múltipla: o draw mostra "Múltiplos" quando os valores diferem


@dataclass(frozen=True)
class Action:
    operator: str
    label: str = ''
    enabled: bool = True
    reason: str = ''
    essential: bool = False
    args: tuple = ()            # pares (propriedade, valor) do operador


@dataclass(frozen=True)
class Note:
    text: str                   # msgid, com `{}` preenchidos por `args`
    icon: str = 'INFO'
    essential: bool = True
    args: tuple = ()


@dataclass(frozen=True)
class Section:
    id: str
    label: str
    items: tuple = ()
    essential: bool = False
    scope: str = ''             # msgid do escopo quando difere do alvo (ex.: ações do módulo dono numa peça)


@dataclass(frozen=True)
class Header:
    name: str
    kind_label: str
    scope_label: str
    scope_args: tuple = ()
    path: tuple = ()
    select_owner: object = None     # Action ou None
    adapter: str = ''


@dataclass(frozen=True)
class ViewModel:
    header: object = None
    sections: tuple = field(default_factory=tuple)
    empty: str = ''             # msgid do estado vazio ("Selecione…", "Calculando…")


EMPTY_SELECTION = N_("Selecione um objeto na viewport")
CALCULATING = N_("Calculando…")


def _header(target):
    owner = cmd.evaluate(cmd.BY_OPERATOR['caffmob.target_select_owner'], target)
    select_owner = (Action(owner.operator, N_("Selecionar conjunto"), True, '', True)
                    if owner.enabled else None)
    scope_args = (target.count,) if target.scope == r.SCOPE_MULTIPLE else ()
    kind_label = r.KIND_LABELS.get(target.kind, r.KIND_LABELS[r.OTHER])
    if target.kind == r.OPENING:                 # a abertura BTM DOOR é Porta (RF-019)
        kind_label = N_("Porta") if target.detail == 'DOOR' else N_("Janela")
    return Header(target.name, kind_label, r.SCOPE_LABELS[target.scope], scope_args, target.path, select_owner,
                  target.adapter)


_OWNER_SCOPED = {cmd.S_MODULE: N_("Conjunto")}


def _action_sections(target):
    grouped = {}
    for entry in cmd.commands_for(target):
        if entry.section == cmd.S_HEADER:
            continue
        grouped.setdefault(entry.section, []).append(
            Action(entry.operator, '', entry.enabled, entry.reason, entry.essential))
    return grouped


def build(target, mode=ESSENTIAL, calculating=False):
    if target is None:
        return ViewModel(empty=CALCULATING if calculating else EMPTY_SELECTION)
    from . import adapters
    sections = list(adapters.sections_for(target))
    by_id = {s.id: i for i, s in enumerate(sections)}
    for section_id, actions in _action_sections(target).items():
        # Botão que não executa neste tipo some do painel; o motivo continua na dica do operador (RF-002).
        visible = tuple(a for a in actions if a.enabled or section_id == cmd.S_AGGREGATES)
        if not visible:
            continue
        if any(a.operator == 'caffmob.set_insertion_plane' for a in visible):
            # O plano de inserção vale para todo tipo, e a colisão dele vai junto do botão (como na 1.8.0).
            existing = sections[by_id[section_id]].items if section_id in by_id else ()
            if not any(isinstance(i, Field) and i.data == 'insertion' for i in existing):
                visible = visible + (Field('insertion', 'collision_override'),)
        if section_id in by_id:
            current = sections[by_id[section_id]]
            sections[by_id[section_id]] = Section(current.id, current.label, current.items + visible,
                                                  current.essential, current.scope)
        else:
            scope = _OWNER_SCOPED.get(section_id, '') if target.kind != r.MODULE else ''
            essential = any(a.essential and a.enabled for a in visible)
            by_id[section_id] = len(sections)
            sections.append(Section(section_id, cmd.SECTION_LABELS[section_id], visible, essential, scope))
    if mode == ESSENTIAL:
        sections = [Section(s.id, s.label, tuple(i for i in s.items if i.essential), s.essential, s.scope)
                    for s in sections if s.essential]
        sections = [s for s in sections if s.items]
    return ViewModel(_header(target), tuple(sections))


def fields(view):
    """Todos os campos do ViewModel, em ordem (para testes e para o inventário)."""
    return [item for s in view.sections for item in s.items if isinstance(item, Field)]


def actions(view):
    found = [item for s in view.sections for item in s.items if isinstance(item, Action)]
    if view.header is not None and view.header.select_owner is not None:
        found.insert(0, view.header.select_owner)
    return found
