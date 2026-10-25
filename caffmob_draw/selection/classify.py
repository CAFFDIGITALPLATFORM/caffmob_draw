"""Tipo do objeto selecionado, para todas as bibliotecas (T001; D-09, RN-01).

Dado um objeto, `classify(obj)` devolve `Classified(kind, obj, root, library)`:
- `kind`: o que o usuário selecionou (ver KINDS);
- `obj`: o objeto que representa o tipo (a frente, a porta de ambiente, a parede…);
- `root`: o módulo dono (para frente e peça interna) ou o próprio objeto;
- `library`: FRAMELESS, FACE_FRAME, CLOSETS, BTM (módulo rápido/camada nova) ou HB (estrutura do ambiente).

A precedência segue RN-01: frente e peça antes do módulo, módulo antes da parede. Isso importa porque gabinetes são
filhos da parede e subir pela hierarquia passa por ela (mesma razão da exclusão em `operators/ops_general.py`).
Só usa `.get()`, `.parent` e atributos simples, então funciona com objetos simulados nos testes.
"""

from collections import namedtuple
from ..data.i18n import N_

Classified = namedtuple('Classified', 'kind obj root library')

ANNOTATION, FRONT, PART, MODULE = 'ANNOTATION', 'FRONT', 'PART', 'MODULE'
ROOM_DOOR, WINDOW, GEOMETRY, OBSTACLE = 'ROOM_DOOR', 'WINDOW', 'GEOMETRY', 'OBSTACLE'
WALL, FLOOR, CEILING, OTHER = 'WALL', 'FLOOR', 'CEILING', 'OTHER'
KINDS = (ANNOTATION, FRONT, PART, MODULE, ROOM_DOOR, WINDOW, GEOMETRY, OBSTACLE, WALL, FLOOR, CEILING, OTHER)

KIND_LABELS = {
    ANNOTATION: N_("Cota / anotação"), FRONT: N_("Frente"), PART: N_("Peça"), MODULE: N_("Módulo"), ROOM_DOOR: N_("Porta"),
    WINDOW: N_("Janela"), GEOMETRY: N_("Geometria"), OBSTACLE: N_("Obstáculo"), WALL: N_("Parede"), FLOOR: N_("Piso"),
    CEILING: N_("Teto"), OTHER: N_("Objeto"),
}
LIBRARY_LABELS = {'FRAMELESS': N_("Frameless"), 'FACE_FRAME': N_("Face frame"), 'CLOSETS': N_("Closets"),
                  'BTM': N_("Módulo rápido"), 'HB': N_("Ambiente"), 'AUTHORED': N_("Armário autoral")}

MODULE_TAGS = (
    ('IS_AUTHORED_CABINET', 'AUTHORED'),
    ('IS_FRAMELESS_CABINET_CAGE', 'FRAMELESS'),
    ('IS_FACE_FRAME_CABINET_CAGE', 'FACE_FRAME'),
    ('IS_FACE_FRAME_PRODUCT_CAGE', 'FACE_FRAME'),
    ('IS_CLOSET_STARTER_CAGE', 'CLOSETS'),
)
FRONT_TAGS = ('IS_DOOR_FRONT', 'IS_DRAWER_FRONT', 'IS_PULLOUT_FRONT', 'IS_FLIP_UP_DOOR', 'IS_CABINET_FRONT')
FRONT_ROLES = frozenset({'DOOR', 'DRAWER_FRONT', 'PULLOUT_FRONT', 'TILT_OUT', 'FRONT_PIVOT',
                         'CLOSET_DOOR_FRONT', 'CLOSET_DRAWER_FRONT'})


def btm_kind(obj):
    """Tipo da camada nova (`btm_plane.object_kind`) só quando foi gravado de propósito; senão "".

    O enum tem padrão 'WALL' em todo objeto: sem esta checagem, qualquer objeto sem marcação passava por parede
    (BUG-20261007-TBY3).
    """
    plane = getattr(obj, 'btm_plane', None)
    if plane is None:
        return ''
    is_set = getattr(plane, 'is_property_set', None)
    if is_set is not None and not is_set('object_kind'):
        return ''
    return getattr(plane, 'object_kind', '')


_btm_kind = btm_kind


def module_library(obj):
    """Biblioteca se `obj` é a raiz de um módulo; senão None."""
    for tag, library in MODULE_TAGS:
        if obj.get(tag):
            return library
    if _btm_kind(obj) == 'MODULE':
        return 'BTM'
    return None


def _is_front(obj):
    # 067 D-25 (RF-102): frente só pela tag ou pelo papel gravado; o sufixo do nome não conta mais (M-08 gravou o
    # papel nas portas antigas do módulo rápido).
    return any(obj.get(tag) for tag in FRONT_TAGS) or obj.get('hb_part_role') in FRONT_ROLES


def _ancestors(obj):
    current = obj
    while current is not None:
        yield current
        current = current.parent


def module_root(obj):
    """Raiz do módulo que contém `obj` (ou o próprio), com a biblioteca; (None, None) se não houver."""
    for node in _ancestors(obj):
        library = module_library(node)
        if library:
            return node, library
    return None, None


def classify(obj):
    if obj is None:
        return None
    if obj.get('IS_2D_ANNOTATION'):
        return Classified(ANNOTATION, obj, obj, 'HB')

    root, library = module_root(obj)
    if root is not None:
        # Frente: o primeiro ancestral (até o módulo) que é frente.
        for node in _ancestors(obj):
            if node is root:
                break
            if _is_front(node):
                return Classified(FRONT, node, root, library)
        if obj is root:
            return Classified(MODULE, root, root, library)
        return Classified(PART, obj, root, library)

    for node in _ancestors(obj):
        if node.get('IS_ENTRY_DOOR_BP'):
            return Classified(ROOM_DOOR, node, node, 'HB')
        if node.get('IS_WINDOW_BP'):
            return Classified(WINDOW, node, node, 'HB')
        kind = _btm_kind(node)
        if kind == 'OPENING':
            return Classified(WINDOW, node, node, 'BTM')
        if kind == 'GEOMETRY':
            return Classified(GEOMETRY, node, node, 'BTM')
        if node.get('IS_OBSTACLE') or node.get('IS_SOFFIT_BP'):
            return Classified(OBSTACLE, node, node, 'HB')
        if node.get('IS_WALL_BP'):
            return Classified(WALL, node, node, 'HB')
        if kind == 'WALL':
            return Classified(WALL, node, node, 'BTM')
        if node.get('IS_FLOOR_BP') or kind == 'FLOOR':
            return Classified(FLOOR, node, node, 'HB' if node.get('IS_FLOOR_BP') else 'BTM')
        if node.get('IS_CEILING_BP'):
            return Classified(CEILING, node, node, 'HB')
    return Classified(OTHER, obj, obj, '')


def free_group(obj):
    """Grupo de peças de topo (`btm_group`) que contém `obj`: SketchUp importado, item da biblioteca de objetos."""
    top = None
    for node in _ancestors(obj):
        data = getattr(node, 'btm_group', None)
        if data is not None and getattr(data, 'is_group', False):
            top = node
    return top


BODY_TYPES = frozenset({'MESH', 'CURVE', 'FONT'})


def movable_root(obj):
    """Objeto que se move no "Mover Sobre" (RN-05): o módulo para frentes e peças; geometria e obstáculo; para o
    objeto solto, o item da biblioteca de objetos, o grupo de peças (SketchUp) ou ele mesmo, se tiver corpo
    (BUG-20261022-7KFP); None para parede, piso, teto, porta, janela, cota, câmera, luz e empty sem grupo."""
    info = classify(obj)
    if info is None:
        return None
    if info.kind in (FRONT, PART, MODULE, GEOMETRY, OBSTACLE):
        return info.root
    if info.kind == OTHER:
        for node in _ancestors(obj):
            if getattr(getattr(node, 'btm_object_item', None), 'is_item', False):
                return node
        group = free_group(obj)
        if group is not None:
            return group
        return obj if getattr(obj, 'type', None) in BODY_TYPES else None
    return None


def move_over_denial(obj):
    """Motivo (msgid) de `obj` não poder ser arrastado no "Mover Sobre"; None se pode."""
    if obj is None or movable_root(obj) is not None:
        return None
    if classify(obj).kind == OTHER:
        return N_("Câmera, luz e objeto sem corpo não se movem no Mover Sobre.")
    return N_("Parede, piso, teto, porta, janela e cota não se movem no Mover Sobre.")


def reference_root(obj):
    """Objeto que pode ser referência (B) no "Mover Sobre": tudo que é movível e também paredes."""
    info = classify(obj)
    if info is None:
        return None
    if info.kind == WALL:
        return info.obj
    return movable_root(obj)
