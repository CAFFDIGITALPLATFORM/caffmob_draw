"""Objetos simulados dos 15 tipos da auditoria para os testes puros do `target/` (feature 067).

Só o que `selection.classify` e `target.resolver` leem: `.get()`, `.parent`, `type`, `session_uid` e os grupos de
propriedades da camada nova. Os nomes são só para leitura do teste: nenhuma regra depende deles.
"""

import itertools
import types

_uids = itertools.count(1)


class Obj:
    def __init__(self, name, parent=None, type='MESH', props=None, **attrs):
        self.name = name
        self.parent = parent
        self.type = type
        self.session_uid = next(_uids)
        self._props = dict(props or {})
        for key, value in attrs.items():
            setattr(self, key, value)

    def get(self, key, default=None):
        return self._props.get(key, default)

    def __contains__(self, key):
        return key in self._props


def plane(kind):
    return types.SimpleNamespace(object_kind=kind, is_property_set=lambda name: True)


def scene():
    """Os 15 tipos, mais um obstáculo (fallback) e os donos."""
    s = types.SimpleNamespace()
    s.btm_module = Obj("Balcão rápido", btm_plane=plane('MODULE'))
    s.hb_module = Obj("Armário HB", props={'IS_FRAMELESS_CABINET_CAGE': True})
    s.part = Obj("Lateral", parent=s.hb_module, props={'hb_part_role': 'LEFT_SIDE'})
    s.front = Obj("Porta HB", parent=s.hb_module, props={'IS_DOOR_FRONT': True})
    s.leaf = Obj("Folha", parent=s.btm_module,
                 btm_aggregate=types.SimpleNamespace(is_aggregate=True, kind='LEAF'))
    s.authored = Obj("Armário Torre", props={'IS_AUTHORED_CABINET': True})
    s.member = Obj("Prateleira 2", parent=s.authored, btm_member=types.SimpleNamespace(owner=s.authored, role='SHELF'))
    s.geometry = Obj("Placa", btm_plane=plane('GEOMETRY'))
    s.wall = Obj("Parede 1", props={'IS_WALL_BP': True})
    s.room_door = Obj("Porta de entrada", parent=s.wall, props={'IS_ENTRY_DOOR_BP': True})
    s.btm_door = Obj("Abertura", btm_plane=plane('OPENING'), btm_opening=types.SimpleNamespace(opening_type='DOOR'))
    s.window = Obj("Janela", parent=s.wall, props={'IS_WINDOW_BP': True})
    s.cladding = Obj("Ripado", parent=s.wall, btm_cladding=types.SimpleNamespace(uid='c1', host=s.wall))
    s.floor = Obj("Piso", props={'IS_FLOOR_BP': True})
    s.ceiling = Obj("Teto", props={'IS_CEILING_BP': True})
    s.light = Obj("Luz", type='LIGHT', data=types.SimpleNamespace(type='AREA'))
    s.camera = Obj("Câmera", type='CAMERA')
    s.annotation = Obj("Cota", type='CURVE', props={'IS_2D_ANNOTATION': True})
    s.free = Obj("Vaso")
    s.obstacle = Obj("Pilar", props={'IS_OBSTACLE': True})
    return s
