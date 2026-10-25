"""Fixtures da feature 067 nos ensaios Blender (T002, T171).

- `scene_15()`: cena descartável com os 15 tipos da auditoria (módulo BTM, módulo HB, armário autoral com membro,
  chapa de módulo, geometria livre, frente, folha, parede, porta e janela, revestimento, piso e teto, luz, câmera,
  anotação e objeto livre), montada por código. Cada objeto é achado pelo que ele é (marca, papel, tipo), nunca
  pelo nome: os nomes daqui são só para leitura das mensagens.
- `banco_temporario()`: o banco do Padrão de Dimensões num diretório temporário (D-35); todo ensaio da 067 que toca
  o padrão passa por ele, e o banco de quem roda o ensaio nunca é aberto.
"""

import contextlib
import os
import tempfile
import types

import bpy

import _blender_env as env
import _authored_env as authored_env
import _cladding_env as cladding_env
from caffmob_draw import hb_details, hb_utils
from caffmob_draw.collision import guard
from caffmob_draw.geometry_free import mesh as geometry_mesh
from caffmob_draw.product_libraries.frameless import types_frameless as tf
from caffmob_draw.selection import classify


@contextlib.contextmanager
def banco_temporario():
    """Liga `standards.store.override_path` a um arquivo num diretório temporário e restaura no fim."""
    from caffmob_draw.standards import store
    previous = store.override_path
    store.close()
    with tempfile.TemporaryDirectory(prefix="caffmob_067_padroes_") as directory:
        store.override_path = os.path.join(directory, store.FILENAME)
        try:
            yield store.override_path
        finally:
            store.close()
            store.override_path = previous


def _first(objects, test):
    return next((o for o in objects if test(o)), None)


def _plane(name, flag, z):
    data = bpy.data.meshes.new(name)
    data.from_pydata([(0, 0, z), (4, 0, z), (4, 4, z), (0, 4, z)], [], [(0, 1, 2, 3)])
    obj = bpy.data.objects.new(name, data)
    bpy.context.collection.objects.link(obj)
    obj[flag] = True
    return obj


@guard.suspended()
def scene_15():
    """Monta a cena e devolve os objetos por papel (SimpleNamespace)."""
    _walls, wall, door, window, cladding = cladding_env.scene()        # limpa a cena antes
    s = types.SimpleNamespace(wall=wall, room_door=door, window=window, cladding=cladding)

    assert bpy.ops.caffmob.cabinet_builder(width=0.6, door_swing='LEFT') == {'FINISHED'}
    s.btm_module = bpy.context.object
    s.btm_module.location = (1.0, 2.0, 0.0)

    base = tf.BaseCabinet()
    base.default_exterior = 'Doors'
    base.create("Armário HB")
    hb_utils.run_calc_fix_until_stable(bpy.context, base.obj)
    s.hb_module = base.obj
    s.hb_module.location = (2.5, 2.0, 0.0)
    children = list(s.hb_module.children_recursive)
    s.front = _first(children, lambda o: classify.classify(o).kind == classify.FRONT)
    s.part = _first(children, lambda o: o.type == 'MESH' and classify.classify(o).kind == classify.PART
                    and any(m.type == 'NODES' and m.node_group and 'Cutpart' in m.node_group.name
                            for m in o.modifiers))

    s.authored, s.member = authored_env.tower("Armário Torre", x=-1.5)

    s.geometry = geometry_mesh.create_object(bpy.context, 'PLACA')
    s.geometry.location = (0.0, 3.0, 0.0)

    bpy.ops.mesh.primitive_cube_add(size=0.3, location=(0.1, 0.0, 0.4))
    s.leaf = bpy.context.object
    s.leaf.parent = s.btm_module
    s.leaf.btm_aggregate.is_aggregate = True
    s.leaf.btm_aggregate.kind = 'LEAF'

    s.floor = _plane("Piso", 'IS_FLOOR_BP', 0.0)
    s.ceiling = _plane("Teto", 'IS_CEILING_BP', 2.6)

    s.light = bpy.data.objects.new("Luz", bpy.data.lights.new("Luz", 'AREA'))
    bpy.context.collection.objects.link(s.light)
    s.camera = bpy.data.objects.new("Câmera", bpy.data.cameras.new("Câmera"))
    bpy.context.collection.objects.link(s.camera)

    line = hb_details.GeoNodeLine()
    line.create("Cota")
    s.annotation = line.obj

    bpy.ops.mesh.primitive_cube_add(size=0.4, location=(-3.0, -3.0, 0.2))
    s.free = bpy.context.object
    env.settle()
    missing = [k for k, v in vars(s).items() if v is None]
    assert not missing, f"fixture sem: {missing}"
    return s


def select(objects, active=None):
    authored_env.select(list(objects), active)
