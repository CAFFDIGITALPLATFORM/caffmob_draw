"""Janela importada instalada numa parede (feature 007, T022; RN-03, D-12 a D-14).

"Instalar" cria a mesma jaula das janelas de ambiente (`hb_types.GeoNodeCage` com `IS_WINDOW_BP`, filha da parede HB,
Dim X/Z = largura/altura da esquadria, Dim Y = espessura da parede) e corta o vão com `cut_wall`. A esquadria vira
filha da jaula, centrada nela por drivers (x = Dim X/2, y = Dim Y/2): quando o editor de paredes muda a espessura
(`walls2d/apply.py`), a esquadria continua no meio. Com a jaula vêm do legado: deslizar no plano da parede com limite
no segmento, apagar junto com a parede e a colisão de cena da 004.

"Desinstalar" solta a esquadria onde está, tira o corte e apaga a jaula.
"""

import bpy  # type: ignore
from mathutils import Matrix  # type: ignore

from .. import hb_types
from ..data.i18n import N_, tr
from . import group

WINDOW_FLAG = 'IS_WINDOW_BP'
WALL_FLAG = 'IS_WALL_BP'
DEFAULT_SILL = 1.0
NOT_HB_WALL = N_("Converta a parede pelo editor de paredes antes de instalar")


def is_frame(obj):
    return group.is_group(obj) and obj.btm_group.kind == 'FRAME'


def frame_of(obj):
    while obj is not None and not is_frame(obj):
        obj = obj.parent
    return obj


def cage_of(frame):
    parent = frame.parent if frame is not None else None
    return parent if parent is not None and parent.get(WINDOW_FLAG) and parent.btm_window.frame == frame else None


def can_install(frame, wall):
    if frame is None:
        return tr("Selecione a esquadria (Montar esquadria) e a parede")
    if cage_of(frame) is not None:
        return tr("A janela já está instalada")
    if wall is None:
        return tr("Selecione também a parede")
    if not wall.get(WALL_FLAG):
        return tr(NOT_HB_WALL)
    if group.group_box(frame) is None:              # esquadria sem peças (EC-10)
        return tr("A esquadria não tem peças para instalar")
    return None


def install(context, frame, wall, sill=DEFAULT_SILL):
    """Instala `frame` em `wall`; devolve a jaula."""
    from ..operators.doors_windows import cut_wall
    lo, hi = group.group_box(frame)
    width, height = hi.x - lo.x, hi.z - lo.z
    wall_geo = hb_types.GeoNodeWall(wall)
    length, thickness = wall_geo.get_input('Length'), wall_geo.get_input('Thickness')
    center = frame.matrix_world @ ((lo + hi) / 2.0)
    x = (wall.matrix_world.inverted() @ center).x - width / 2.0
    x = max(0.0, min(x, length - width))
    saved = [v for row in frame.matrix_world for v in row]

    cage = hb_types.GeoNodeCage()
    cage.create("Window")
    cage.obj[WINDOW_FLAG] = True
    cage.obj.display_type = 'WIRE'
    cage.set_input('Dim X', width)
    cage.set_input('Dim Y', thickness)
    cage.set_input('Dim Z', height)
    cage.obj.parent = wall
    cage.obj.matrix_parent_inverse = Matrix.Identity(4)
    cage.obj.location = (x, 0.0, sill)
    cage.obj.rotation_euler = (0.0, 0.0, 0.0)
    cage.obj.btm_window.frame = frame
    cage.obj.btm_window.frame_matrix = saved

    frame.parent = cage.obj
    frame.matrix_parent_inverse = Matrix.Identity(4)
    frame.rotation_euler = (0.0, 0.0, 0.0)
    frame.location = (0.0, 0.0, -lo.z)
    fg = hb_types.GeoNodeObject(frame)
    fg.driver_location('x', 'dim_x/2', [cage.var_input('Dim X', 'dim_x')])
    fg.driver_location('y', 'dim_y/2', [cage.var_input('Dim Y', 'dim_y')])
    cut_wall(wall, cage.obj)
    context.view_layer.update()
    return cage.obj


def uninstall(context, cage):
    """Solta a esquadria na posição do mundo, tira o corte e apaga a jaula; devolve a esquadria."""
    frame = cage.btm_window.frame
    wall = cage.parent
    if frame is not None:
        world = frame.matrix_world.copy()
        for index in (0, 1):
            frame.driver_remove('location', index)
        frame.parent = None
        frame.matrix_parent_inverse = Matrix.Identity(4)
        frame.matrix_world = world
    if wall is not None:
        for mod in list(wall.modifiers):
            if mod.type == 'BOOLEAN' and mod.object == cage:
                wall.modifiers.remove(mod)
    for child in list(cage.children):
        if child is not frame:
            bpy.data.objects.remove(child, do_unlink=True)
    bpy.data.objects.remove(cage, do_unlink=True)
    context.view_layer.update()
    return frame
