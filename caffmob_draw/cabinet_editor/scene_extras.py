"""Componentes extras da Estrutura na cena (feature 008, T024; RN-07a, D-12 a D-14).

`sync(context, root)` deixa os objetos extras iguais ao estado da árvore (`root.btm_structure.extras`): apaga os de
antes e cria de novo a partir de `extras.layout`, sobre a caixa da carcaça e a espessura da lateral no Configurador.
Chapas viram `CabinetPart` com o componente do Configurador; pés são ferragem (`btm_hardware`).
"""

from . import extras as ex
from . import scene_parts

KINDS = {'BASE_TOP_RECESSED', 'FOOT', 'CASTER', 'KICK_FRONT', 'KICK_LEFT', 'KICK_RIGHT', 'KICK_GRANITE', 'CLOSURE',
         'VIEW_FRONT', 'VIEW_LEFT', 'VIEW_RIGHT', 'VIEW_TALL_LEFT', 'VIEW_TALL_RIGHT', 'VIEW_TALL_FRONT'}
NAMES = {'BASE_TOP_RECESSED': "Base Superior Recuada", 'FOOT': "Pé Plástico", 'CASTER': "Rodízio", 'KICK_FRONT': "Rodapé Frontal",
         'KICK_LEFT': "Rodapé Esquerdo", 'KICK_RIGHT': "Rodapé Direito", 'KICK_GRANITE': "Rodapé Granito",
         'CLOSURE': "Fechamento", 'VIEW_FRONT': "Vista Frontal", 'VIEW_LEFT': "Vista Esquerda",
         'VIEW_RIGHT': "Vista Direita", 'VIEW_TALL_LEFT': "Vista Alta Esquerda", 'VIEW_TALL_RIGHT': "Vista Alta Direita",
         'VIEW_TALL_FRONT': "Vista Alta Frontal"}


def settings_of(root):
    structure = getattr(root, 'btm_structure', None)
    return structure.extras_dict() if structure is not None else {}


def _kick_setback(context, root):
    """Recuo do rodapé (m) do Padrão de Dimensões na linha do módulo; None = reserva do núcleo."""
    try:
        from ..data import dimension_schema as schema
        from ..standards import api
        return api.get_value_m(context.scene, schema.external_key(root.btm_cabinet.line, 'toe_kick_setback'))
    except (AttributeError, KeyError, ValueError):
        return None


def sync(context, root):
    """Recria as peças extras; devolve a lista de objetos criados."""
    from . import bridge
    scene_parts.delete(scene_parts.extras_of(root, KINDS))
    settings = settings_of(root)
    if not any(v.get('enabled') for v in settings.values()):
        return []
    _material, t = bridge.configured_part(context, root, 'LEFT')
    t = t or 0.015
    box = scene_parts.carcass_box(context, root)
    structured = bool(getattr(getattr(root, 'btm_cabinet', None), 'structure_id', ""))     # feature 015
    setback = _kick_setback(context, root) if structured else None
    out = []
    for piece in ex.layout(box, t, settings, structure=structured, kick_setback=setback):
        name = NAMES.get(piece.kind, piece.kind)
        if piece.hardware:
            out.append(scene_parts.make_cylinder(root, name, piece.box, piece.kind, hardware=piece.hardware,
                                                 slot=piece.slot))
        else:
            out.append(scene_parts.make_part(root, name, piece.box, piece.kind, piece.component, piece.material,
                                             slot=piece.slot))
    return out
