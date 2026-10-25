"""Resolvedor único da seleção (feature 067, D-02; RF-001, RF-003, RN-04).

`resolve(active, selected)` devolve um `Target` congelado com o que o painel, o menu contextual e as cotas precisam:
tipo, escopo, dono, papel, caminho e os dados que as capacidades consultam. Compõe `selection.classify` com o que
ele não vê: luz e câmera, revestimento, folha (`btm_aggregate.kind == 'LEAF'`), membro de armário autoral
(`btm_member.owner`) e seleção múltipla. Só usa `.get()`, `.parent`, `getattr` e `session_uid`, então roda com
objetos simulados nos testes; quem chama é o snapshot (`target/snapshot.py`), nunca um getter ou o draw.
"""

from dataclasses import dataclass

from ..data.i18n import N_
from ..selection import classify as cls

# Os 15 tipos da auditoria, mais seleção múltipla e o fallback rotulado.
MODULE, MEMBER, PART, GEOMETRY, FRONT, LEAF = 'MODULE', 'MEMBER', 'PART', 'GEOMETRY', 'FRONT', 'LEAF'
WALL, OPENING, CLADDING, FLOOR, CEILING = 'WALL', 'OPENING', 'CLADDING', 'FLOOR', 'CEILING'
LIGHT, CAMERA, ANNOTATION, OTHER, OBSTACLE, MULTIPLE = 'LIGHT', 'CAMERA', 'ANNOTATION', 'OTHER', 'OBSTACLE', 'MULTIPLE'
KINDS = (MODULE, MEMBER, PART, GEOMETRY, FRONT, LEAF, WALL, OPENING, CLADDING, FLOOR, CEILING, LIGHT, CAMERA,
         ANNOTATION, OTHER, OBSTACLE, MULTIPLE)

# Escopo mostrado no cabeçalho (RF-003): o que uma edição atinge.
SCOPE_PART, SCOPE_LEAF, SCOPE_ASSEMBLY, SCOPE_OBJECT, SCOPE_MULTIPLE = 'PART', 'LEAF', 'ASSEMBLY', 'OBJECT', 'MULTIPLE'

KIND_LABELS = {
    MODULE: N_("Módulo"), MEMBER: N_("Peça"), PART: N_("Peça"), GEOMETRY: N_("Geometria"), FRONT: N_("Frente"),
    LEAF: N_("Folha"), WALL: N_("Parede"), OPENING: N_("Abertura"), CLADDING: N_("Revestimento"), FLOOR: N_("Piso"),
    CEILING: N_("Teto"), LIGHT: N_("Luz"), CAMERA: N_("Câmera"), ANNOTATION: N_("Cota / anotação"),
    OTHER: N_("Objeto"), OBSTACLE: N_("Obstáculo"), MULTIPLE: N_("Seleção múltipla"),
}
SCOPE_LABELS = {SCOPE_PART: N_("Peça"), SCOPE_LEAF: N_("Folha"), SCOPE_ASSEMBLY: N_("Conjunto"),
                SCOPE_OBJECT: N_("Objeto"), SCOPE_MULTIPLE: N_("{} objetos")}
# Tipos com adaptador próprio; o resto cai no fallback rotulado (RN-04).
ADAPTED = frozenset(KINDS) - {OBSTACLE}
# Tipos cujo painel mostra as medidas próprias da chapa (RF-006, RF-011, RF-014, RF-016).
SHEET_KINDS = frozenset({PART, MEMBER, FRONT, LEAF, GEOMETRY})


@dataclass(frozen=True)
class Target:
    uid: int                    # session_uid do objeto que o painel edita
    kind: str
    name: str
    scope: str
    library: str = ''           # BTM, HB, FRAMELESS, FACE_FRAME, CLOSETS, AUTHORED ou ''
    role: str = ''              # papel da peça (hb_part_role, papel do membro, porta ou janela)
    owner_uid: int = 0          # dono: o módulo, o armário autoral ou a parede do revestimento; 0 sem dono
    owner_name: str = ''
    path: tuple = ()            # nomes do dono até o alvo, para "Prateleira 2 · em Armário Torre"
    move_uid: int = 0           # o que o Mover Sobre e as cotas movem; 0 = não se move (RF-024)
    selected_uids: tuple = ()   # a seleção inteira, o ativo primeiro
    count: int = 1
    authored_owner: bool = False    # há um armário autoral em jogo (raiz ou dono do membro)
    has_member: bool = False        # algum selecionado é membro de armário autoral
    in_group: bool = False          # o alvo está num grupo de peças (btm_group)
    detail: str = ''                # subtipo: tipo de luz, LIBRARY/AUTHORED da peça, DOOR/WINDOW da abertura
    measures: object = None         # PartMeasures da chapa (preenchido pelo snapshot, que lê a malha)
    measure_error: str = ''         # motivo quando a medida foi recusada (shear, escala zero…)
    multi_thickness: tuple = ()     # espessuras das chapas da seleção múltipla, na ordem de `selected_uids`
    has_leaf: bool = False          # porta com folha gerada (`openings.ops.door_of`; preenchido pelo snapshot)

    @property
    def adapter(self):
        return self.kind if self.kind in ADAPTED else 'FALLBACK'

    @property
    def has_owner(self):
        return bool(self.owner_uid)


def uid_of(obj):
    return int(getattr(obj, 'session_uid', 0) or 0) if obj is not None else 0


def _name(obj):
    return getattr(obj, 'name', '') if obj is not None else ''


def _is_member(obj):
    member = getattr(obj, 'btm_member', None)
    return member is not None and getattr(member, 'owner', None) is not None


def _is_leaf(obj):
    agg = getattr(obj, 'btm_aggregate', None)
    return agg is not None and getattr(agg, 'is_aggregate', False) and getattr(agg, 'kind', '') == 'LEAF'


def _is_cladding(obj):
    data = getattr(obj, 'btm_cladding', None)
    return data is not None and bool(getattr(data, 'uid', ''))


def _authored_root(obj):
    root, library = cls.module_root(obj)
    return root if library == 'AUTHORED' else None


def _opening_type(obj, info):
    if info.kind == cls.ROOM_DOOR:
        return 'DOOR'
    if info.kind == cls.WINDOW and info.library == 'HB':
        return 'WINDOW'
    opening = getattr(obj, 'btm_opening', None)
    return getattr(opening, 'opening_type', 'WINDOW') if opening is not None else 'WINDOW'


def _single(obj, cladding_controller=None):
    if obj.get('btm_cladding_piece') and cladding_controller is not None:
        controller = cladding_controller(obj)       # peça gerada: o painel edita o revestimento dono
        if controller is not None:
            target = _single(controller)
            return Target(**{**target.__dict__, 'detail': 'PIECE', 'selected_uids': (uid_of(obj),)})
    uid = uid_of(obj)
    move = cls.movable_root(obj)
    base = dict(uid=uid, name=_name(obj), move_uid=uid_of(move), selected_uids=(uid,),
                in_group=cls.free_group(obj) is not None)
    if _is_cladding(obj):
        host = getattr(obj.btm_cladding, 'host', None)
        return Target(kind=CLADDING, scope=SCOPE_OBJECT, owner_uid=uid_of(host), owner_name=_name(host),
                      path=(_name(host), _name(obj)) if host is not None else (), **{**base, 'move_uid': 0})
    if _is_member(obj):
        owner = obj.btm_member.owner
        kind = LEAF if _is_leaf(obj) else MEMBER
        return Target(kind=kind, scope=SCOPE_LEAF if kind == LEAF else SCOPE_PART, library='AUTHORED',
                      role=getattr(obj.btm_member, 'role', ''), owner_uid=uid_of(owner), owner_name=_name(owner),
                      path=(_name(owner), _name(obj)), authored_owner=True, has_member=True, detail='AUTHORED',
                      **base)

    # Luz e câmera soltas; dentro de um módulo ou armário (membro, peça) valem como parte dele (RN-01, 066).
    obj_type = getattr(obj, 'type', '')
    if obj_type in ('LIGHT', 'CAMERA') and cls.module_root(obj)[0] is None:
        if obj_type == 'LIGHT':
            light = getattr(obj, 'data', None)
            return Target(kind=LIGHT, scope=SCOPE_OBJECT, detail=getattr(light, 'type', ''), **{**base, 'move_uid': 0})
        return Target(kind=CAMERA, scope=SCOPE_OBJECT, **{**base, 'move_uid': 0})
    info = cls.classify(obj)
    root = info.root
    owned = dict(owner_uid=uid_of(root), owner_name=_name(root), path=(_name(root), _name(info.obj)))
    if _is_leaf(obj) and root is not obj and cls.module_root(obj)[0] is not None:
        return Target(kind=LEAF, scope=SCOPE_LEAF, library=info.library, **owned, **base)
    if info.kind == cls.MODULE:
        return Target(kind=MODULE, scope=SCOPE_ASSEMBLY, library=info.library,
                      authored_owner=info.library == 'AUTHORED', **base)
    if info.kind == cls.FRONT:
        return Target(kind=FRONT, scope=SCOPE_PART, library=info.library, role=str(info.obj.get('hb_part_role') or ''),
                      **owned, **{**base, 'uid': uid_of(info.obj), 'name': _name(info.obj)})
    if info.kind == cls.PART:
        authored = info.library == 'AUTHORED'
        return Target(kind=PART, scope=SCOPE_PART, library=info.library, role=str(obj.get('hb_part_role') or ''),
                      authored_owner=authored, detail='AUTHORED' if authored else 'LIBRARY', **owned, **base)
    simple = {cls.GEOMETRY: GEOMETRY, cls.WALL: WALL, cls.FLOOR: FLOOR, cls.CEILING: CEILING,
              cls.ANNOTATION: ANNOTATION, cls.OBSTACLE: OBSTACLE, cls.OTHER: OTHER}
    if info.kind in (cls.ROOM_DOOR, cls.WINDOW):
        kind_of_opening = _opening_type(info.obj, info)
        return Target(kind=OPENING, scope=SCOPE_OBJECT, library=info.library, role=kind_of_opening,
                      detail=kind_of_opening, **{**base, 'uid': uid_of(info.obj), 'name': _name(info.obj)})
    kind = simple[info.kind]
    target_obj = info.obj
    return Target(kind=kind, scope=SCOPE_OBJECT, library=info.library,
                  authored_owner=_authored_root(obj) is not None,
                  **{**base, 'uid': uid_of(target_obj), 'name': _name(target_obj)})


def resolve(active, selected=(), cladding_controller=None):
    """Alvo da seleção. `active` é o objeto ativo; `selected`, os selecionados (o ativo pode não estar entre eles).
    `cladding_controller(peça)` acha o revestimento dono de uma peça gerada (precisa da cena; vem do snapshot)."""
    others = [o for o in selected if o is not None and o is not active]
    if active is None and not others:
        return None
    objects = ([active] if active is not None else []) + others
    if len(objects) == 1:
        return _single(objects[0], cladding_controller)
    primary = _single(objects[0], cladding_controller)
    uids = tuple(uid_of(o) for o in objects)
    return Target(uid=primary.uid, kind=MULTIPLE, name=primary.name, scope=SCOPE_MULTIPLE, selected_uids=uids,
                  count=len(objects), move_uid=primary.move_uid,
                  authored_owner=any(_is_member(o) or _authored_root(o) is not None for o in objects),
                  has_member=any(_is_member(o) for o in objects), in_group=primary.in_group)
