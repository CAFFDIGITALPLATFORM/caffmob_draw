"""Protótipo da premissa 5 (feature 067, T009; D-14): papel por peça nos construtores das bibliotecas.

Run: blender --background --factory-startup --python-exit-code 1 --python tests/blender_067_proto_papeis_hb.py

Para cada família (frameless balcão, aéreo e alto; face frame; closets; módulo rápido BTM) conta as peças com papel
de acabamento (`customize/finish.piece_role`) e as desconhecidas. A premissa vale quando toda família tem papel
INTERNAL ou EXTERNAL suficiente para aplicar Interno e Externo; as famílias com peça desconhecida aparecem na lista
das que caem no assistente (RF-042). O módulo BTM tem papel por face (`btm_face_role`).
"""

import sys
import traceback
from pathlib import Path

import bpy

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _blender_env as env  # noqa: E402
from caffmob_draw import hb_utils  # noqa: E402
from caffmob_draw.customize import finish, finish_core as fc  # noqa: E402
from caffmob_draw.product_libraries.closets import types_closets as tc  # noqa: E402
from caffmob_draw.product_libraries.face_frame import types_face_frame as tff  # noqa: E402
from caffmob_draw.product_libraries.frameless import types_frameless as tf  # noqa: E402

FAILURES = []


def check(condition, message, detail=""):
    print(("OK    " if condition else "FALHA ") + message + (f" ({detail})" if detail and not condition else ""))
    if not condition:
        FAILURES.append(message)


def frameless(cls, name, x):
    cab = cls()
    cab.default_exterior = 'Doors'
    cab.create(name)
    cab.obj.location.x = x
    hb_utils.run_calc_fix_until_stable(bpy.context, cab.obj)
    return cab.obj


def families():
    out = {'frameless balcão': frameless(tf.BaseCabinet, "Balcão", 0.0),
           'frameless aéreo': frameless(tf.UpperCabinet, "Aéreo", 1.0),
           'frameless alto': frameless(tf.TallCabinet, "Alto", 2.0)}
    ff = tff.BaseFaceFrameCabinet()
    ff.create("FaceFrame")
    ff.obj.location.x = 3.0
    out['face frame balcão'] = ff.obj
    starter = tc.BaseClosetStarter()
    starter.create_starter("Roupeiro", bay_qty=2)
    starter.obj.location.x = 5.0
    tc.recalculate_closet_starter(starter.obj)
    out['closets'] = starter.obj
    assert bpy.ops.caffmob.cabinet_builder(width=0.6) == {'FINISHED'}
    out['módulo rápido BTM'] = bpy.context.object
    env.settle()
    return out


def run():
    env.clean_scene()
    assistant = []
    for family, root in families().items():
        pieces = finish.pieces_of(root)
        roles = {}
        for obj in pieces:
            face = finish.face_roles(obj)
            if face is not None:
                for value in face:
                    roles[('face', value)] = roles.get(('face', value), 0) + 1
            else:
                role = finish.piece_role(obj)
                roles[role] = roles.get(role, 0) + 1
        unknown = roles.get(fc.PIECE_UNKNOWN, 0) + roles.get(('face', fc.FACE_UNKNOWN), 0)
        internal = roles.get(fc.PIECE_INTERNAL, 0) + roles.get(('face', fc.FACE_INTERNAL), 0)
        external = (roles.get(fc.PIECE_EXTERNAL, 0) + roles.get(fc.PIECE_FRONT, 0)
                    + roles.get(('face', fc.FACE_EXTERNAL), 0))
        print(f"PAPEIS {family:<20} peças={len(pieces):<3} interno={internal:<3} externo={external:<3} "
              f"desconhecido={unknown}")
        check(bool(pieces), f"{family}: o dono tem peças")
        check(external > 0, f"{family}: há peça ou face aparente para o Externo")
        if unknown:
            assistant.append(family)
        if family == 'módulo rápido BTM':
            check(finish.face_roles(root) is not None, "BTM: o construtor grava btm_face_role")
            check(internal > 0 and roles.get(('face', fc.FACE_EDGE), 0) > 0, "BTM: faces internas e bordas")
    print("PAPEIS famílias que caem no assistente (peças sem papel): " + (", ".join(assistant) or "nenhuma"))


try:
    run()
except Exception:
    traceback.print_exc()
    FAILURES.append("exceção")
print(f"blender_067_proto_papeis_hb: {'OK' if not FAILURES else 'FALHAS: ' + ', '.join(FAILURES)}")
sys.exit(1 if FAILURES else 0)
