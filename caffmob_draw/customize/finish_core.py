"""Domínios de acabamento (feature 067, D-14, D-15; RF-041, RN-10). Python puro, sem `bpy`.

Quatro domínios: INTERNAL (faces internas da caixa e do fundo, prateleiras e divisórias), EXTERNAL (faces aparentes
da caixa, inclusive a face de trás do fundo, e as frentes), FRONTS (só as frentes, com o veio próprio, que nasce V) e
EDGE (as faces estreitas das chapas: a fita, independente dos outros).

O papel vem do construtor, nunca da normal global nem do nome (RN-10):
- por face, no atributo `btm_face_role` (0 desconhecida, 1 interna, 2 aparente, 3 borda), gravado pelo construtor BTM
  (`geometry/mesh_gen.py`) e pelo assistente em Edit Mode;
- por peça, em `btm_part.finish_role` (UNKNOWN, INTERNAL, EXTERNAL, FRONT), ou derivado do componente do Padrão de
  Dimensões (`customize/spec.group_of_component`) nas bibliotecas que não têm papel por face.
"""

from . import spec

INTERNAL, EXTERNAL, FRONTS, EDGE = 'INTERNAL', 'EXTERNAL', 'FRONTS', 'EDGE'
DOMAINS = (INTERNAL, EXTERNAL, FRONTS, EDGE)

# Papel por face (atributo `btm_face_role`).
FACE_UNKNOWN, FACE_INTERNAL, FACE_EXTERNAL, FACE_EDGE = 0, 1, 2, 3
FACE_ROLES = (FACE_UNKNOWN, FACE_INTERNAL, FACE_EXTERNAL, FACE_EDGE)

# Papel por peça (`btm_part.finish_role`).
PIECE_UNKNOWN, PIECE_INTERNAL, PIECE_EXTERNAL, PIECE_FRONT = 'UNKNOWN', 'INTERNAL', 'EXTERNAL', 'FRONT'
PIECE_ROLES = (PIECE_UNKNOWN, PIECE_INTERNAL, PIECE_EXTERNAL, PIECE_FRONT)

# Que faces e que peças cada domínio cobre (RF-041).
DOMAIN_FACES = {INTERNAL: (FACE_INTERNAL,), EXTERNAL: (FACE_EXTERNAL,), FRONTS: (), EDGE: (FACE_EDGE,)}
DOMAIN_PIECES = {INTERNAL: (PIECE_INTERNAL,), EXTERNAL: (PIECE_EXTERNAL, PIECE_FRONT), FRONTS: (PIECE_FRONT,),
                 EDGE: ()}
DEFAULT_GRAIN = {INTERNAL: 'NONE', EXTERNAL: 'NONE', FRONTS: 'V', EDGE: 'NONE'}
MULTIPLE = '__MULTIPLE__'

# Grupo antigo (`btm_custom.group_materials`) → domínios (M-03, data-delta §5).
LEGACY_GROUP_DOMAINS = {'CAIXA': (EXTERNAL, INTERNAL), 'FUNDO': (EXTERNAL, INTERNAL), 'INTERNO': (INTERNAL,),
                        'FRENTES': (FRONTS,)}
# A ordem de leitura deixa a caixa ganhar do fundo e do interno no mesmo domínio: a caixa é a maior superfície, e
# fundo ou interno diferentes continuam aplicados pelo caminho antigo até a próxima aplicação (D-15).
_LEGACY_ORDER = ('INTERNO', 'FUNDO', 'CAIXA', 'FRENTES')


def domains_for_faces(face_role):
    """Domínios que cobrem uma face com este papel."""
    return tuple(d for d in DOMAINS if face_role in DOMAIN_FACES[d])


def domains_for_piece(piece_role):
    """Domínios que cobrem uma peça com este papel (a frente está no Externo e nas Frentes)."""
    return tuple(d for d in DOMAINS if piece_role in DOMAIN_PIECES[d])


def piece_role_of_group(group):
    """Papel por peça a partir do grupo de material: o fundo segue a caixa (2ª rodada), interno é interno."""
    return {'FRENTES': PIECE_FRONT, 'INTERNO': PIECE_INTERNAL, 'CAIXA': PIECE_EXTERNAL,
            'FUNDO': PIECE_EXTERNAL}.get(group, PIECE_UNKNOWN)


def piece_role_of_component(component, is_front=False):
    """Papel por peça de um componente do Padrão de Dimensões (`cutting/part_roles`)."""
    if is_front:
        return PIECE_FRONT
    if not component:
        return PIECE_UNKNOWN
    return piece_role_of_group(spec.group_of_component(component))


def piece_role_of_legacy_slot(slot):
    """Módulo BTM sem `btm_face_role` (M-04): o slot antigo diz a peça (0 caixa, 1 prateleira, 2 fundo)."""
    return {0: PIECE_EXTERNAL, 1: PIECE_INTERNAL, 2: PIECE_EXTERNAL}.get(slot, PIECE_UNKNOWN)


def migrate_groups(group_materials, front_material=''):
    """M-03: `{grupo: material}` e o material das frentes → `{domínio: material}` (origem MIGRATED).

    CAIXA → EXTERNAL e INTERNAL com o mesmo material; FUNDO → o mesmo par; INTERNO → INTERNAL; FRENTES e
    `front_material` → FRONTS (o `front_material` vence, como no `reapply` antigo do módulo BTM).
    """
    out = {}
    for group in _LEGACY_ORDER:
        material = group_materials.get(group) or ''
        if not material:
            continue
        for domain in LEGACY_GROUP_DOMAINS[group]:
            out[domain] = material
    if front_material:
        out[FRONTS] = front_material
    return out


def legacy_face_material(slot, group_materials):
    """Material que o caminho antigo dá a uma face do módulo BTM pelo slot (para conferir que M-03 não muda nada)."""
    carcass = group_materials.get('CAIXA') or ''
    if slot == 1:
        return group_materials.get('INTERNO') or carcass
    if slot == 2:
        return group_materials.get('FUNDO') or carcass
    return carcass


def summarize(values):
    """Material efetivo de um domínio a partir dos materiais das peças ou faces: um só, MULTIPLE ou ''."""
    found = {v for v in values if v}
    if not found:
        return ''
    return next(iter(found)) if len(found) == 1 else MULTIPLE


def box_face_roles(low, high, inner_low, inner_high, inside=False, eps=1e-6):
    """Papel das seis faces de uma chapa em caixa, na ordem de `mesh_gen.add_box`: base, topo, frente (−Y), direita
    (+X), trás (+Y), esquerda (−X).

    A espessura é o menor eixo. As duas faces largas: a que olha para o vão interno é interna; a outra, aparente.
    As quatro estreitas são borda. Uma chapa dentro do vão (prateleira, divisória) tem as duas faces largas internas.
    """
    sizes = [high[i] - low[i] for i in range(3)]
    axis = min(range(3), key=lambda i: sizes[i])
    center = [(inner_low[i] + inner_high[i]) / 2.0 for i in range(3)]
    # Face → (eixo, lado): lado −1 é a face no mínimo do eixo.
    faces = ((2, -1), (2, +1), (1, -1), (0, +1), (1, +1), (0, -1))
    roles = []
    for face_axis, side in faces:
        if face_axis != axis:
            roles.append(FACE_EDGE)
            continue
        if inside:
            roles.append(FACE_INTERNAL)
            continue
        face_pos = high[axis] if side > 0 else low[axis]
        other_pos = low[axis] if side > 0 else high[axis]
        # A face mais perto do centro do vão olha para dentro.
        roles.append(FACE_INTERNAL if abs(face_pos - center[axis]) < abs(other_pos - center[axis]) - eps
                     else FACE_EXTERNAL)
    return tuple(roles)


def inside_box(low, high, inner_low, inner_high, eps=1e-6):
    """A chapa está dentro do vão interno (prateleira, divisória)?"""
    return all(low[i] >= inner_low[i] - eps and high[i] <= inner_high[i] + eps for i in range(3))
