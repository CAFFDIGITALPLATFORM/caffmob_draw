"""Acabamentos por domínio no Blender (feature 067, D-14, D-15; RF-041, RF-043, RN-08, RN-10).

- `pieces_of(owner)`: as malhas que um acabamento do dono atinge: a malha do módulo BTM e as portas dele, as peças
  `GeoNodeCutpart` das bibliotecas HB, os membros de malha do armário autoral, ou o próprio objeto solto.
- `piece_role(obj)`: o papel por peça: `btm_part.finish_role` gravado vence; senão a frente; senão o componente do
  Padrão de Dimensões (`common.part_group`) nas peças das bibliotecas; senão o papel do membro autoral (prateleira,
  fundo, frente). Peça autoral de estrutura sem papel fica desconhecida: o assistente classifica (RF-042).
- `face_roles(obj)`: o atributo `btm_face_role` da malha, ou None (M-04: módulo antigo usa o slot como papel).
- `apply(...)`: aplica um material nos domínios escolhidos, no escopo do dono (Componente) ou só das peças
  escolhidas (Peça), e grava a escolha em `btm_finish` para sobreviver ao rebuild (`reapply`). Malha compartilhada
  com objetos fora do alvo vira cópia antes (material compartilhado não muda objetos fora do alvo, RF-041).
- `summary(owner)`: o material efetivo de cada domínio, lido das faces e peças ("Múltiplos" quando diferem).
"""

import bpy  # type: ignore

from . import finish_core as fc

FACE_ATTR = 'btm_face_role'
ROLE_OF_MEMBER = {'SHELF': fc.PIECE_INTERNAL, 'BACK': fc.PIECE_EXTERNAL, 'FIXED_FRONT': fc.PIECE_FRONT,
                  'LEAF_PART': fc.PIECE_FRONT}
_FRONT_ROLES = ('DOOR', 'DRAWER_FRONT', 'PULLOUT_FRONT', 'TILT_OUT')


def owner_of(obj):
    """Dono do acabamento: a raiz do módulo, o armário autoral do membro, ou o próprio objeto."""
    if obj is None:
        return None
    member_owner = getattr(getattr(obj, 'btm_member', None), 'owner', None)
    if member_owner is not None:
        return member_owner
    from ..selection import classify
    root, _library = classify.module_root(obj)
    return root or obj


def _library(owner):
    from ..selection import classify
    if owner.get('IS_AUTHORED_CABINET') or getattr(getattr(owner, 'btm_authored', None), 'is_authored', False):
        return 'AUTHORED'
    return classify.module_library(owner) or ''


def pieces_of(owner):
    if owner is None:
        return []
    library = _library(owner)
    if library == 'BTM':
        from ..geometry import door_controller
        return [o for o in [owner] + door_controller.doors_of(owner) if o.type == 'MESH']
    if library == 'AUTHORED':
        return [o for o in owner.children_recursive if o.type == 'MESH' and o.btm_member.owner == owner]
    if library:
        from .adapters import common
        return [o for o in owner.children_recursive if common.is_cutpart(o)]
    return [owner] if owner.type == 'MESH' else []


def is_front(obj):
    if obj.get('IS_CABINET_FRONT') or obj.get('hb_part_role') in _FRONT_ROLES:
        return True
    from ..selection import classify
    found = classify.classify(obj)
    return found is not None and found.kind == classify.FRONT


def piece_role(obj):
    explicit = getattr(getattr(obj, 'btm_part', None), 'finish_role', fc.PIECE_UNKNOWN)
    if explicit != fc.PIECE_UNKNOWN:
        return explicit
    if is_front(obj):
        return fc.PIECE_FRONT
    aggregate = getattr(obj, 'btm_aggregate', None)
    if aggregate is not None and aggregate.is_aggregate and aggregate.kind == 'LEAF':
        return fc.PIECE_FRONT               # folha: parte móvel da frente
    from .adapters import common
    if common.is_cutpart(obj):
        return fc.piece_role_of_group(common.part_group(obj))
    member = getattr(obj, 'btm_member', None)
    if member is not None and member.owner is not None:
        return ROLE_OF_MEMBER.get(member.role, fc.PIECE_UNKNOWN)
    if owner_of(obj) is obj:
        return fc.PIECE_EXTERNAL            # objeto solto ou geometria livre: o objeto inteiro é aparente
    return fc.PIECE_UNKNOWN


def face_roles(obj):
    if obj.type != 'MESH':
        return None
    attr = obj.data.attributes.get(FACE_ATTR)
    if attr is None or attr.domain != 'FACE' or attr.data_type != 'INT' or len(attr.data) != len(obj.data.polygons):
        return None                         # em Edit Mode a malha do objeto fica vazia até sair do modo
    values = [0] * len(obj.data.polygons)
    attr.data.foreach_get('value', values)
    return values


def legacy_face_roles(obj):
    """M-04: módulo BTM sem o atributo; o slot antigo diz a peça (caixa e fundo aparentes, prateleira interna)."""
    to_face = {fc.PIECE_EXTERNAL: fc.FACE_EXTERNAL, fc.PIECE_INTERNAL: fc.FACE_INTERNAL}
    return [to_face.get(fc.piece_role_of_legacy_slot(p.material_index), fc.FACE_UNKNOWN) for p in obj.data.polygons]


def has_roles(owner):
    """Há papel cadastrado (por face ou por peça) em alguma peça do dono? Sem papel, o assistente (RF-042)."""
    pieces = pieces_of(owner)
    if any(piece_role(obj) != fc.PIECE_UNKNOWN for obj in pieces):
        return True
    for obj in pieces:
        roles = face_roles(obj)
        if roles is not None and any(r != fc.FACE_UNKNOWN for r in roles):
            return True
    return False


# Aplicação ------------------------------------------------------------------------------------------------------

def _isolate(obj, inside):
    """Malha compartilhada com objeto fora do alvo vira cópia só deste (RF-041)."""
    data = obj.data
    if data is None or data.users <= 1:
        return
    if all(o in inside for o in bpy.data.objects if o.data == data):
        return
    obj.data = data.copy()


def _slot_for(obj, material):
    materials = obj.data.materials
    for index, current in enumerate(materials):
        if current == material:
            return index
    # Slot novo depois dos que as faces já usam: um slot vazio usado por face não pode virar o material novo.
    used = max((p.material_index for p in obj.data.polygons), default=-1)
    while len(materials) <= used:
        materials.append(None)
    materials.append(material)
    return len(materials) - 1


def _apply_faces(obj, roles, domains, material):
    wanted = {role for d in domains for role in fc.DOMAIN_FACES[d]}
    faces = [i for i, role in enumerate(roles) if role in wanted]
    if not faces:
        return False
    index = _slot_for(obj, material)
    polygons = obj.data.polygons
    for i in faces:
        polygons[i].material_index = index
    obj.data.update()
    return True


def _apply_piece(obj, domains, material):
    if not set(fc.domains_for_piece(piece_role(obj))) & set(domains):
        return False
    if obj.parent is not None and _library(obj.parent) == 'BTM':
        from ..geometry import door_controller
        if obj in door_controller.doors_of(obj.parent):
            door_controller.set_door_material(obj, material)
            return True
    from .adapters import common
    return common.set_cutpart_material(obj, material)


def apply_to(objs, domains, material, inside=None):
    """Aplica `material` nas faces e peças de `objs` cobertas pelos domínios; devolve quantas malhas mudaram."""
    inside = set(inside if inside is not None else objs)
    changed = 0
    for obj in objs:
        if obj.type != 'MESH':
            continue
        _isolate(obj, inside)
        roles = face_roles(obj)
        done = _apply_faces(obj, roles, domains, material) if roles is not None else _apply_piece(obj, domains,
                                                                                                 material)
        if done:
            from ..texture_library import grain
            grain.sync(obj)                     # intenção de veio guardada sem material vira giro (D-30, RF-065)
        changed += bool(done)
    return changed


def remember(holder, domain, material, scale_mm=0.0, grain=None, source='USER'):
    """Grava (ou troca) a escolha do domínio em `holder.btm_finish` (D-15)."""
    for item in holder.btm_finish:
        if item.domain == domain:
            break
    else:
        item = holder.btm_finish.add()
        item.domain = domain
        item.grain = fc.DEFAULT_GRAIN[domain]
    item.material = material
    item.scale_mm = float(scale_mm or 0.0)
    if grain is not None:
        item.grain = grain
    item.source = source
    return item


def apply(owner, domains, material, pieces=None, scale_mm=0.0, source='USER', grain=None):
    """Aplica no escopo Componente (`pieces` None: todas as peças do dono) ou Peça (`pieces` escolhidas)."""
    if owner is None or material is None:
        return 0
    ensure_face_roles(owner)
    targets = pieces_of(owner) if pieces is None else [p for p in pieces if p is not None]
    changed = apply_to(targets, domains, material)
    holders = [owner] if pieces is None else targets
    for holder in holders:
        for domain in domains:
            remember(holder, domain, material, scale_mm, grain=grain, source=source)
    if fc.FRONTS in domains:
        # A frente nasce com veio vertical (RF-041); quem já escolheu o veio dela fica como está.
        wanted = grain or fc.DEFAULT_GRAIN[fc.FRONTS]
        for obj in targets:
            part = getattr(obj, 'btm_part', None)
            if part is not None and piece_role(obj) == fc.PIECE_FRONT and part.grain == 'NONE':
                part.grain = wanted
    return changed


def reapply(owner):
    """Depois de um rebuild: as escolhas não migradas voltam (as migradas já estão no caminho antigo, M-03)."""
    if owner is None:
        return 0
    changed = 0
    base = [(i.domain, i.material) for i in owner.btm_finish if i.source != 'MIGRATED' and i.material is not None]
    pieces = pieces_of(owner)
    for domain, material in base:
        changed += apply_to(pieces, (domain,), material, inside=pieces)
    for obj in pieces:
        for item in obj.btm_finish if obj is not owner else ():
            if item.material is not None:
                changed += apply_to([obj], (item.domain,), item.material)
    return changed


def ensure_face_roles(owner):
    """M-04: módulo BTM antigo ganha o atributo no rebuild; a malha refeita sai com o mesmo material (reapply)."""
    if _library(owner) != 'BTM' or owner.type != 'MESH' or face_roles(owner) is not None:
        return False
    from ..data.properties import update_cabinet_geom
    update_cabinet_geom(owner.btm_cabinet, bpy.context)
    return face_roles(owner) is not None


# Leitura para o painel --------------------------------------------------------------------------------------------

def _face_materials_by_role(obj, roles):
    """{papel da face: [nome do material]} numa passada só pelos polígonos."""
    count = len(obj.data.polygons)
    indices = [0] * count
    obj.data.polygons.foreach_get('material_index', indices)
    names = [m.name if m is not None else '' for m in obj.data.materials]
    out = {}
    for index, role in zip(indices, roles):
        if role != fc.FACE_UNKNOWN and index < len(names):
            out.setdefault(role, set()).add(names[index])
    return out


def _piece_material(obj):
    from .adapters import common
    mod = common.gn_modifier(obj, 'GeoNodeCutpart')
    if mod is not None:
        from .. import compat
        mat = compat.get_gn_input(mod, 'Top Surface')
        return mat.name if mat is not None else ''
    mats = [m for m in obj.data.materials if m is not None] if obj.type == 'MESH' else []
    return mats[0].name if mats else ''


def summary(owner, pieces=None):
    """{domínio: (material ou MULTIPLE ou '', [(peça, material)])} lido da cena. Chamado fora do draw (snapshot)."""
    pieces = pieces_of(owner) if pieces is None else pieces
    btm = _library(owner) == 'BTM'
    per_piece = []
    for obj in pieces:
        roles = face_roles(obj)
        if roles is None and btm and obj is owner:
            roles = legacy_face_roles(obj)
        if roles is not None:
            per_piece.append((obj.name, _face_materials_by_role(obj, roles), None))
        else:
            per_piece.append((obj.name, None, (piece_role(obj), _piece_material(obj))))
    out = {}
    for domain in fc.DOMAINS:
        wanted = fc.DOMAIN_FACES[domain]
        values, rows = [], []
        for name, by_role, piece in per_piece:
            if by_role is not None:
                found = set().union(*(by_role.get(r, set()) for r in wanted)) if wanted else set()
                if found:
                    material = fc.summarize(found)
                    values.append(material)
                    rows.append((name, material))
            elif domain in fc.domains_for_piece(piece[0]):
                values.append(piece[1])
                rows.append((name, piece[1]))
        out[domain] = (fc.summarize(values) if all(v != fc.MULTIPLE for v in values) else fc.MULTIPLE, tuple(rows))
    return out
