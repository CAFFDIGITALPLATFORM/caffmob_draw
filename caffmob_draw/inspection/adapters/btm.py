"""Adaptador do módulo rápido `btm_cabinet` (T060; D-32).

As portas do módulo rápido giram por drivers que leem o Y local do Empty controlador (0 a 0,2 m → 0° a 90°;
`geometry/door_controller.py`). 067 D-25: o Empty é achado pela marca `btm_door_controller` e a porta pela
dobradiça gravada (`btm_front_hinge`), nunca pelo nome. O adaptador escreve nesse Empty;
`btm_cabinet.door_open` acompanha pelo driver de sincronização. Uma `Front` é o módulo inteiro (todas as folhas
abrem juntas).
"""

from mathutils import Vector  # type: ignore

from ...geometry import door_controller
from .. import fronts, pivot_math

TRAVEL = 0.2  # m de curso do controlador para 90°


def _controller(module):
    return next((c for c in module.children if c.get('btm_door_controller')), None)


def _doors(module):
    return [c for c in module.children if c.type == 'MESH' and c.get('btm_front_hinge') in ('L', 'R', 'FLIP')]


def _is_module(obj):
    plane = getattr(obj, 'btm_plane', None)
    cabinet = getattr(obj, 'btm_cabinet', None)
    return (plane is not None and plane.object_kind == 'MODULE' and cabinet is not None
            and cabinet.door_swing != 'NONE' and _controller(obj) is not None and bool(_doors(obj)))


class BtmFront(fronts.Front):
    library = 'BTM'

    def __init__(self, module):
        kind = fronts.FLIP_UP if module.btm_cabinet.door_swing == 'FLIP' else fronts.DOOR
        doors = _doors(module)
        super().__init__(kind, module, doors[0], f"BTM:{module.name}")

    def get(self):
        controller = _controller(self.module_root)
        if controller is None:
            return 0.0
        closed = door_controller.closed_door_y(self.module_root)
        return pivot_math.fraction_to_degrees((closed - controller.location.y) / TRAVEL, pivot_math.BTM_MAX_ANGLE)

    def apply(self, value):
        # O Empty parte da face da folha fechada e corre para fora (−Y); a posição antiga (a partir de 0) era desfeita
        # pela limitação do Empty e a porta não girava (067 T136).
        controller = _controller(self.module_root)
        if controller is not None:
            closed = door_controller.closed_door_y(self.module_root)
            controller.location.y = closed - pivot_math.degrees_to_fraction(value, pivot_math.BTM_MAX_ANGLE) * TRAVEL

    def commit(self, value):
        self.apply(value)
        self.module_root['btm_open'] = float(self.clamp(value))

    def hinge_frame(self):
        world = self.module_root.matrix_world
        rot = world.to_3x3()
        door = self.obj
        point = world @ Vector(door.location)
        if self.kind == fronts.FLIP_UP:
            return point, (rot @ Vector((-1.0, 0.0, 0.0))).normalized(), (rot @ Vector((0.0, 0.0, -1.0))).normalized()
        if door.get('btm_front_hinge') == 'R':
            return point, (rot @ Vector((0.0, 0.0, -1.0))).normalized(), (rot @ Vector((-1.0, 0.0, 0.0))).normalized()
        return point, (rot @ Vector((0.0, 0.0, 1.0))).normalized(), (rot @ Vector((1.0, 0.0, 0.0))).normalized()

    def objects(self):
        return _doors(self.module_root)


def find_fronts(scene):
    return [BtmFront(obj) for obj in scene.objects if obj.type == 'MESH' and _is_module(obj)]


def front_for_object(obj, scene):
    current = obj
    while current is not None:
        if current.type == 'MESH' and _is_module(current):
            return BtmFront(current)
        current = current.parent
    return None
