"""Biblioteca autoral: preserva a geometria, sem personalização paramétrica (066, RN-10).

067 (onda 2, D-18; RF-044): os materiais passam a valer quando há papéis de acabamento cadastrados nas peças (pelo
assistente `caffmob.finish_classify` ou pelo papel do membro); sem papéis, o motivo aponta o assistente. Frentes,
puxadores, divisões e estilos continuam recusados até a onda 5.
"""

from ...data.i18n import N_, tr
from .. import spec

LIBRARY = 'AUTHORED'
REASON = N_("O armário autoral usa regras dos membros; a personalização paramétrica não se aplica")


NO_ROLES = N_("Classifique as peças no assistente de acabamento para aplicar materiais neste armário")


def capabilities(root):
    from .. import finish
    caps = dict.fromkeys(('FRONTS', 'PULLS', 'MATERIALS', 'INTERIOR', 'STYLES'), REASON)
    caps['MATERIALS'] = None if finish.has_roles(root) else NO_ROLES
    return caps


def read(root):
    return spec.Spec(library=LIBRARY)


def openings(root):
    return []


def front_types(root):
    return []


def style_names():
    return []


def pull_items():
    return []


def set_front(context, root, opening, front, drawer_count=1):
    return [tr(REASON)]


def set_interior(context, root, opening, interior):
    return [tr(REASON)]


def reapply(context, root):
    return []
