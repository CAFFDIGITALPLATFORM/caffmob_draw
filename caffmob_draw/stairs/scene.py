"""A escada na cena (071 D-21, D-22, M-04): leitura das propriedades, sem importar bpy.

A raiz é um Empty com `btm_stair` (JSON do `core.Escada`), `btm_stair_uid` e `btm_stair_corrimao_mm`; as chapas são
filhas com `btm_stair_part`. Nenhum objeto da escada recebe `caffmob_tipo`: a remontagem do ambiente do MOBI os
preserva, e a escada de obra do documento do MOBI continua outra coisa.
"""
import json

from . import core

ROOT_PROP = 'btm_stair'
PART_PROP = 'btm_stair_part'
UID_PROP = 'btm_stair_uid'
HANDRAIL_PROP = 'btm_stair_corrimao_mm'


def is_root(obj):
    return obj is not None and obj.get(ROOT_PROP) is not None


def root_of(obj):
    node = obj
    while node is not None:
        if is_root(node):
            return node
        node = node.parent
    return None


def roots(scene):
    return [o for o in scene.objects if is_root(o)]


def spec(root):
    try:
        return core.Escada.de_dict(json.loads(root[ROOT_PROP]))
    except (KeyError, TypeError, ValueError):
        return core.Escada().normalizada()


def uid(root):
    return str(root.get(UID_PROP) or root.name)


def handrail_mm(root):
    return float(root.get(HANDRAIL_PROP) or 0.0)


def visible(root):
    try:
        return not root.hide_viewport and not root.hide_get()
    except (AttributeError, RuntimeError):
        return not getattr(root, 'hide_viewport', False)
