"""Assistente de classificação de acabamento (feature 067, T062; D-17, RF-042).

- `caffmob.finish_classify`: em Object Mode marca o papel das peças selecionadas (`btm_part.finish_role`); em Edit
  Mode marca o papel das faces selecionadas (`btm_face_role`). Um passo de Undo.
- `caffmob.finish_classify_preview`: liga e desliga a prévia por cor das peças e faces do móvel ativo (interno azul,
  externo laranja, frente verde, borda cinza). Face ou peça desconhecida não é pintada. Os triângulos são montados
  pelo operador (fora do draw); o draw só desenha o que está em cache.
"""

import bmesh  # type: ignore
import bpy  # type: ignore

from ..data.i18n import N_, tr
from . import finish, finish_core as fc

PIECE_ITEMS = (
    (fc.PIECE_INTERNAL, N_("Interno"), N_("Peça interna")),
    (fc.PIECE_EXTERNAL, N_("Externo"), N_("Peça aparente")),
    (fc.PIECE_FRONT, N_("Frente"), N_("Frente do móvel")),
    (fc.PIECE_UNKNOWN, N_("Desconhecido"), N_("Tira o papel")),
)
FACE_OF_PIECE = {fc.PIECE_INTERNAL: fc.FACE_INTERNAL, fc.PIECE_EXTERNAL: fc.FACE_EXTERNAL,
                 fc.PIECE_FRONT: fc.FACE_EXTERNAL, fc.PIECE_UNKNOWN: fc.FACE_UNKNOWN}
COLORS = {fc.FACE_INTERNAL: (0.25, 0.55, 1.0, 0.45), fc.FACE_EXTERNAL: (1.0, 0.55, 0.15, 0.45),
          fc.FACE_EDGE: (0.6, 0.6, 0.6, 0.45), 'FRONT': (0.2, 0.85, 0.35, 0.45)}

_preview = {'handle': None, 'tris': {}, 'owner': '', 'batches': None}


def _role_triangles(obj, owner_is_btm=False):
    """{chave de cor: [vértices em mundo]} das faces com papel conhecido (desconhecida não entra)."""
    out = {}
    roles = finish.face_roles(obj)
    mesh = obj.data
    mesh.calc_loop_triangles()
    world = obj.matrix_world
    if roles is None:
        role = finish.piece_role(obj)
        if role == fc.PIECE_UNKNOWN:
            return out
        key = 'FRONT' if role == fc.PIECE_FRONT else FACE_OF_PIECE[role]
        out[key] = [tuple(world @ mesh.vertices[i].co) for tri in mesh.loop_triangles for i in tri.vertices]
        return out
    for tri in mesh.loop_triangles:
        role = roles[tri.polygon_index]
        if role == fc.FACE_UNKNOWN:
            continue
        out.setdefault(role, []).extend(tuple(world @ mesh.vertices[i].co) for i in tri.vertices)
    return out


def build_preview(owner):
    """Monta o cache da prévia para o móvel (chamado pelos operadores, nunca pelo draw)."""
    tris = {}
    for obj in finish.pieces_of(owner):
        for key, points in _role_triangles(obj).items():
            tris.setdefault(key, []).extend(points)
    _preview['tris'] = tris
    _preview['owner'] = owner.name if owner is not None else ''
    _preview['batches'] = None             # o draw monta os lotes uma vez, na próxima pintura
    return tris


def _draw():
    import gpu  # type: ignore
    from gpu_extras.batch import batch_for_shader  # type: ignore
    shader = gpu.shader.from_builtin('UNIFORM_COLOR')
    if _preview['batches'] is None:
        _preview['batches'] = [(COLORS.get(key, (1, 1, 1, 0.3)), batch_for_shader(shader, 'TRIS', {"pos": points}))
                               for key, points in _preview['tris'].items() if points]
    gpu.state.blend_set('ALPHA')
    gpu.state.depth_test_set('LESS_EQUAL')
    for color, batch in _preview['batches']:
        shader.uniform_float("color", color)
        batch.draw(shader)
    gpu.state.depth_test_set('NONE')
    gpu.state.blend_set('NONE')


def preview_on():
    return _preview['handle'] is not None


def stop_preview():
    if _preview['handle'] is not None:
        bpy.types.SpaceView3D.draw_handler_remove(_preview['handle'], 'WINDOW')
        _preview['handle'] = None
    _preview['tris'] = {}
    _preview['batches'] = None


def _refresh(context, owner):
    build_preview(owner)
    if preview_on() and context.screen is not None:
        for area in context.screen.areas:
            if area.type == 'VIEW_3D':
                area.tag_redraw()


class BTM_OT_FinishClassify(bpy.types.Operator):
    """Marca o papel de acabamento das peças (Object Mode) ou das faces (Edit Mode) selecionadas"""
    bl_idname = 'caffmob.finish_classify'
    bl_label = N_("Classificar acabamento")
    bl_options = {'REGISTER', 'UNDO'}

    role: bpy.props.EnumProperty(name=N_("Papel"), items=PIECE_ITEMS, default=fc.PIECE_EXTERNAL)  # type: ignore
    edge: bpy.props.BoolProperty(name=N_("Borda"), description=N_("Em Edit Mode, marca as faces como borda (fita)"),
                                 default=False)  # type: ignore

    @classmethod
    def poll(cls, context):
        if not any(o.type == 'MESH' for o in context.selected_objects):
            cls.poll_message_set(tr("Selecione as peças a classificar"))
            return False
        return True

    def execute(self, context):
        if context.mode == 'EDIT_MESH':
            value = fc.FACE_EDGE if self.edge else FACE_OF_PIECE[self.role]
            count = 0
            for obj in context.objects_in_mode_unique_data:
                bm = bmesh.from_edit_mesh(obj.data)
                layer = bm.faces.layers.int.get(finish.FACE_ATTR) or bm.faces.layers.int.new(finish.FACE_ATTR)
                for face in bm.faces:
                    if face.select:
                        face[layer] = value
                        count += 1
                bmesh.update_edit_mesh(obj.data, loop_triangles=False, destructive=False)
            if not count:
                self.report({'WARNING'}, tr("Selecione as faces a classificar"))
                return {'CANCELLED'}
            owner = finish.owner_of(context.active_object)
        else:
            pieces = [o for o in context.selected_objects if o.type == 'MESH']
            for obj in pieces:
                obj.btm_part.finish_role = self.role
            count = len(pieces)
            owner = finish.owner_of(context.active_object)
        if context.mode != 'EDIT_MESH':
            _refresh(context, owner)
        self.report({'INFO'}, tr("{} item(ns) classificado(s)").format(count))
        return {'FINISHED'}


class BTM_OT_FinishClassifyPreview(bpy.types.Operator):
    """Liga ou desliga a prévia por cor dos papéis de acabamento do móvel ativo"""
    bl_idname = 'caffmob.finish_classify_preview'
    bl_label = N_("Prévia dos papéis")

    def execute(self, context):
        if preview_on():
            stop_preview()
        else:
            build_preview(finish.owner_of(context.active_object))
            if not bpy.app.background:
                _preview['handle'] = bpy.types.SpaceView3D.draw_handler_add(_draw, (), 'WINDOW', 'POST_VIEW')
        for area in (context.screen.areas if context.screen else ()):
            if area.type == 'VIEW_3D':
                area.tag_redraw()
        return {'FINISHED'}


classes = (BTM_OT_FinishClassify, BTM_OT_FinishClassifyPreview)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    stop_preview()
    for cls in reversed(classes):
        if cls.is_registered:
            bpy.utils.unregister_class(cls)
