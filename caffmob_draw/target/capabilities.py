"""Capacidades por tipo (feature 067, D-08; RF-002, RN-04): o que cada comando executa no alvo da seleção.

Cada comando é `Command(id, operador, rótulo, disponível)`, com `disponível(target) -> (bool, motivo)`. O motivo é um
msgid (`N_`) que o `poll` mostra por `poll_message_set` e o painel mostra ao lado do botão cinza: um botão nunca
aparece habilitado onde o executor não faz nada. Python puro: recebe o `Target` do resolvedor.
"""

from dataclasses import dataclass
from typing import Callable

from ..data.i18n import N_, tr
from . import resolver as r

_OK = (True, '')
_MODULE_LIKE = frozenset({r.MODULE, r.PART, r.GEOMETRY, r.OTHER, r.MEMBER, r.FRONT})


@dataclass(frozen=True)
class Command:
    id: str
    operator: str
    label: str
    available: Callable


def _when(condition, reason):
    def check(target):
        return _OK if condition(target) else (False, reason)
    return check


def _kinds(*kinds):
    allowed = frozenset(kinds)
    return lambda t: t.kind in allowed


def _adopt(t):
    if t.kind == r.MULTIPLE:
        return True
    return t.kind in _MODULE_LIKE and t.library != 'AUTHORED' and not t.authored_owner


_REASON_AUTHORED = N_("Selecione um armário autoral ou uma peça dele.")
_REASON_MEMBER = N_("Nenhum selecionado é membro de armário autoral.")

COMMANDS = (
    Command('select_owner', 'caffmob.target_select_owner', N_("Selecionar conjunto"),
            _when(lambda t: t.has_owner and t.kind != r.MULTIPLE, N_("O selecionado não tem conjunto dono."))),
    Command('move_over', 'caffmob.move_over', N_("Mover Sobre"),
            _when(lambda t: bool(t.move_uid),
                  N_("Parede, piso, teto, porta, janela, cota, luz e câmera não se movem no Mover Sobre."))),
    Command('cotas', '', N_("Cotas"),
            _when(lambda t: bool(t.move_uid), N_("Este tipo não tem cotas de posição."))),
    # "Agregados e folhas" (aggregates/panels.draw_aggregate), na ordem do painel.
    Command('authored_adopt', 'caffmob_draw.authored_adopt', N_("Adotar como autoral"),
            _when(_adopt, N_("Adotar vale para módulo, peça, geometria ou objeto solto fora de armário autoral."))),
    Command('member_add', 'caffmob_draw.member_add', N_("Adicionar membro"),
            _when(lambda t: t.authored_owner, _REASON_AUTHORED)),
    Command('member_remove', 'caffmob_draw.member_remove', N_("Remover membro"),
            _when(lambda t: t.has_member, _REASON_MEMBER)),
    Command('member_transfer', 'caffmob_draw.member_transfer', N_("Transferir membro"),
            _when(lambda t: t.has_member, _REASON_MEMBER)),
    Command('authored_leaf', 'caffmob_draw.authored_leaf', N_("Folha do armário autoral"),
            _when(lambda t: t.has_member and t.kind in (r.MEMBER, r.LEAF, r.MULTIPLE), _REASON_MEMBER)),
    Command('authored_leaves_open', 'caffmob_draw.authored_leaves_open', N_("Abrir folhas do armário"),
            _when(lambda t: t.authored_owner, _REASON_AUTHORED)),
    Command('authored_update_links', 'caffmob_draw.authored_update_links', N_("Atualizar vínculos"),
            _when(lambda t: t.authored_owner, _REASON_AUTHORED)),
    Command('aggregate_convert', 'caffmob.aggregate_convert', N_("Converter em agregado"),
            _when(lambda t: t.kind in (r.OTHER, r.GEOMETRY, r.MULTIPLE),
                  N_("Converter em agregado vale para objeto solto ou geometria."))),
    Command('leaf_convert', 'caffmob.leaf_convert', N_("Converter em folha"),
            _when(lambda t: t.kind in (r.OTHER, r.GEOMETRY, r.PART, r.MULTIPLE),
                  N_("Converter em folha vale para peça, geometria ou objeto solto."))),
    Command('window_assemble', 'caffmob.window_assemble', N_("Montar janela"),
            _when(lambda t: t.kind in (r.OPENING, r.MULTIPLE), N_("Montar vale para porta ou janela de ambiente."))),
    Command('group_create', 'caffmob.group_create', N_("Criar grupo"),
            _when(lambda t: t.kind == r.MULTIPLE, N_("Selecione dois ou mais objetos para agrupar."))),
    Command('group_dissolve', 'caffmob.group_dissolve', N_("Desfazer grupo"),
            _when(lambda t: t.in_group, N_("O selecionado não está num grupo."))),
)
BY_ID = {c.id: c for c in COMMANDS}
BY_OPERATOR = {c.operator: c for c in COMMANDS if c.operator}
AGGREGATE_COMMANDS = tuple(c.id for c in COMMANDS[3:])


def check(command_id, target):
    """(disponível, motivo) do comando para o alvo; sem alvo, indisponível."""
    if target is None:
        return False, N_("Selecione um objeto na viewport.")
    return BY_ID[command_id].available(target)


def poll(operator_cls, command_id, target):
    """`poll` de operador: falso com o motivo em `poll_message_set` quando o comando não executa no alvo."""
    ok, reason = check(command_id, target)
    if not ok and reason:
        operator_cls.poll_message_set(tr(reason))
    return ok
