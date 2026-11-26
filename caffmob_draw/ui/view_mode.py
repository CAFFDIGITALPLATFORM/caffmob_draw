"""Modo de vista Sólido · Textura e o interruptor Linhas (feature 010, T023; RN-06, D-05; 027, RF-03).

O estado fica na cena (vai junto com o arquivo): `Scene.btm_view_mode`, `btm_view_lines` e o `color_type` que a vista
tinha antes de Textura (`btm_view_prev_color`). Mudar qualquer um aplica em todas as vistas 3D abertas; um
`load_post` reaplica ao abrir o arquivo. Os valores vêm de `view_mode_core.settings`; as arestas pretas do interruptor
Linhas são desenhadas por `overlays/arestas.py`, que lê a mesma `btm_view_lines`.
"""

import bpy  # type: ignore
from bpy.app.handlers import persistent  # type: ignore

from . import view_mode_core as core


def _spaces(context):
    wm = context.window_manager if context else bpy.context.window_manager
    for window in wm.windows:
        for area in window.screen.areas:
            if area.type == 'VIEW_3D':
                for space in area.spaces:
                    if space.type == 'VIEW_3D':
                        yield space


def _redraw():
    wm = getattr(bpy.context, 'window_manager', None)
    if wm is None:
        return
    for window in wm.windows:
        if window.screen is None:
            continue
        for area in window.screen.areas:
            if area.type == 'VIEW_3D':
                area.tag_redraw()


def apply(context, scene=None):
    scene = scene or context.scene
    for space in _spaces(context):
        if scene.btm_view_mode == 'TEXTURE' and space.shading.color_type != 'TEXTURE':
            scene.btm_view_prev_color = space.shading.color_type
        values = core.settings(scene.btm_view_mode, scene.btm_view_lines, scene.btm_view_prev_color)
        if space.shading.type in ('WIREFRAME', 'SOLID'):
            space.shading.type = values['shading_type']
        space.shading.color_type = values['color_type']
        space.overlay.show_wireframes = values['show_wireframes']      # as arestas são as nossas, não as do Blender


def _update(self, context):
    apply(context, self)
    _redraw()


@persistent
def _on_load(_dummy):
    scene = bpy.context.scene
    if scene is not None and (scene.btm_view_mode != 'SOLID' or scene.btm_view_lines):
        apply(bpy.context, scene)


def register():
    bpy.types.Scene.btm_view_mode = bpy.props.EnumProperty(
        name="Modo de vista", items=[(key, label, "") for key, label in core.MODES], default='SOLID',
        update=_update)
    bpy.types.Scene.btm_view_lines = bpy.props.BoolProperty(
        name="Linhas", description="Mostra as arestas de todos os objetos sobre a vista", default=False, update=_update)
    bpy.types.Scene.btm_view_prev_color = bpy.props.StringProperty(default="")
    if _on_load not in bpy.app.handlers.load_post:
        bpy.app.handlers.load_post.append(_on_load)


def unregister():
    if _on_load in bpy.app.handlers.load_post:
        bpy.app.handlers.load_post.remove(_on_load)
    for name in ('btm_view_prev_color', 'btm_view_lines', 'btm_view_mode'):
        if hasattr(bpy.types.Scene, name):
            delattr(bpy.types.Scene, name)
