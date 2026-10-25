"""Migração M-08 (feature 067, T154; D-25, RF-102, RF-141): frente do módulo rápido sem papel → papel gravado.

No `load_post`, uma vez só: a porta filha de um módulo BTM, sem `hb_part_role` e com o nome terminado em `_Door_L`,
`_Door_R` ou `_Door_Flip`, recebe `hb_part_role` (`DOOR` ou `TILT_OUT`) e `btm_front_hinge` (`L`, `R` ou `FLIP`); o
Empty filho de módulo BTM terminado em `_Controller` recebe `btm_door_controller`. Os sufixos vêm de
`geometry/door_names.py`. Depois disso o classificador, o aviso de corte e a inspeção leem só os campos gravados.
Objeto com o sufixo fora de módulo BTM não ganha nada (continua Peça).
"""

import bpy  # type: ignore
from bpy.app.handlers import persistent  # type: ignore

from ..geometry import door_names as names


def _is_btm(obj):
    from . import classify
    return classify.module_library(obj) == 'BTM'


def migrate_object(obj):
    parent = obj.parent
    if parent is None or not _is_btm(parent):
        return False
    suffix = names.suffix_of(obj.name)
    if obj.type == 'MESH' and suffix and not obj.get('hb_part_role'):
        obj['hb_part_role'] = names.ROLE_BY_SUFFIX[suffix]
        if not obj.get(names.HINGE_PROP):
            obj[names.HINGE_PROP] = names.HINGE_BY_SUFFIX[suffix]
        return True
    if obj.type == 'EMPTY' and obj.name.endswith(names.CONTROLLER_SUFFIX) and not obj.get(names.CONTROLLER_PROP):
        obj[names.CONTROLLER_PROP] = True
        return True
    return False


def run():
    return sum(1 for obj in bpy.data.objects if migrate_object(obj))


@persistent
def _on_load(*_args):
    try:
        run()
    except (AttributeError, ReferenceError, RuntimeError) as exc:
        print(f"CAFFMob Draw: migração das frentes (M-08) não rodou: {exc}")


def register():
    if _on_load not in bpy.app.handlers.load_post:
        bpy.app.handlers.load_post.insert(0, _on_load)     # antes de quem classifica


def unregister():
    if _on_load in bpy.app.handlers.load_post:
        bpy.app.handlers.load_post.remove(_on_load)
