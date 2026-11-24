"""Reconhecimento puro de proxy de parede rebaixada (feature 021, T018; RF-11, RN-10).

Reconhece tanto o vínculo explícito (`btm_is_lowered_wall` + `btm_lowered_wall_ref`) quanto o padrão legado
(`<parede>_Rebaixada` filho de uma parede com `btm_wall_lowered`).
"""

LOWERED_PROP = 'btm_wall_lowered'
LOWERED_PROXY_FLAG = 'btm_is_lowered_wall'
LOWERED_WALL_REF = 'btm_lowered_wall_ref'
LOWERED_SUFFIX = '_Rebaixada'


def is_lowered_wall_proxy(obj) -> bool:
    """Retorna True se `obj` é um proxy visual de parede rebaixada."""
    if obj is None:
        return False
    if obj.get(LOWERED_PROXY_FLAG):
        return True
    name = getattr(obj, 'name', '') or ''
    parent = getattr(obj, 'parent', None)
    if name.endswith(LOWERED_SUFFIX) and parent is not None and parent.get(LOWERED_PROP):
        return True
    return False


def resolve_lowered_wall(obj, objects_by_name=None):
    """Dado um proxy de parede rebaixada, devolve o objeto da parede original ou `None`."""
    if obj is None:
        return None
    ref_name = obj.get(LOWERED_WALL_REF)
    if ref_name and objects_by_name is not None:
        wall = objects_by_name.get(ref_name)
        if wall is not None:
            return wall
    parent = getattr(obj, 'parent', None)
    if parent is not None and (parent.get(LOWERED_PROP) or parent.get('IS_WALL_BP') or parent.get('caffmob_tipo') == 'parede'):
        if is_lowered_wall_proxy(obj):
            return parent
    return None
