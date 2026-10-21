"""Biblioteca autoral: preserva a geometria, sem personalização paramétrica (066, RN-10)."""

from ...data.i18n import N_, tr
from .. import spec

LIBRARY = 'AUTHORED'
REASON = N_("O armário autoral usa regras dos membros; a personalização paramétrica não se aplica")


def capabilities(root):
    return dict.fromkeys(('FRONTS', 'PULLS', 'MATERIALS', 'INTERIOR', 'STYLES'), REASON)


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
