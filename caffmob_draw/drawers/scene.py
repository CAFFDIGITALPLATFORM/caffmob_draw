"""A gaveta do construtor na cena (072 D-04, M-03), sem importar bpy.

A frente é a raiz da gaveta: tem `btm_drawer` (JSON com o spec e o espaço) e as peças da caixa como filhas, com
`btm_drawer_part`. Assim a caixa corre junto com a frente (folha `DRAWER`) e o seletor reconhece a frente pelo
`hb_part_role`.
"""
import json

from . import catalogo, core

DRAWER_PROP = 'btm_drawer'
PART_PROP = 'btm_drawer_part'
UID_PROP = 'btm_drawer_uid'


def is_drawer(obj):
    return obj is not None and obj.get(DRAWER_PROP) is not None


def drawer_of(obj):
    node = obj
    while node is not None:
        if is_drawer(node):
            return node
        node = node.parent
    return None


def dados(front):
    try:
        d = json.loads(front[DRAWER_PROP])
    except (KeyError, TypeError, ValueError):
        return None
    return d if isinstance(d, dict) else None


def spec(front):
    d = dados(front) or {}
    return core.Gaveta.de_dict(d.get('gaveta') or {})


def espaco(front):
    e = (dados(front) or {}).get('espaco') or {}
    return core.Espaco(e.get('largura', 0), e.get('altura', 0), e.get('profundidade', 0))


def altura(front):
    return float((dados(front) or {}).get('altura_da_frente', 0))


def comprimento(front):
    return float((dados(front) or {}).get('comprimento', 0))


def corredica(front, pasta=None):
    return catalogo.por_id(spec(front).corredica, pasta)


def uid(front):
    return str(front.get(UID_PROP) or front.name)


def drawers(scene):
    return [o for o in scene.objects if is_drawer(o)]


def visible(obj):
    try:
        return not obj.hide_viewport and not obj.hide_get()
    except (AttributeError, RuntimeError):
        return not getattr(obj, 'hide_viewport', False)
