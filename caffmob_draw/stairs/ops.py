"""Operadores do editor de escadas (071 D-25, D-28): inserir, aplicar, nova, abrir no editor e medidas confortáveis."""
import math

import bpy
from mathutils import Vector

from .. import hb_snap
from ..data.i18n import tr
from . import build, core
from .scene import root_of, spec

IMA_DA_PAREDE = 0.1          # m: encosta na face da parede a até 100 mm (D-25)


def _e_parede(obj):
    return obj is not None and bool(obj.get('caffmob_tipo') == 'parede' or obj.get('IS_WALL_BP')
                                    or getattr(getattr(obj, 'btm', None), 'kind', '') == 'WALL')


def _normal_da_face(obj, indice):
    try:
        n = obj.matrix_world.to_3x3() @ obj.data.polygons[indice].normal
    except (AttributeError, IndexError, TypeError):
        return None
    n.z = 0
    return n.normalized() if n.length > 1e-6 and abs(obj.data.polygons[indice].normal.z) < 0.5 else None


class CAFFMOB_OT_escada_inserir(bpy.types.Operator):
    """Clique no piso para inserir a escada do editor; R gira 90°, perto de uma parede ela encosta na face"""
    bl_idname = 'caffmob.escada_inserir'
    bl_label = "Inserir escada no ambiente"
    bl_options = {'REGISTER', 'UNDO'}

    def invoke(self, context, event):
        if context.area is None or context.area.type != 'VIEW_3D':
            self.report({'WARNING'}, tr("Use na vista 3D."))
            return {'CANCELLED'}
        self.region = context.region
        self.mouse_pos = Vector((0, 0))
        self.hit_location = self.hit_object = self.hit_face_index = None
        self.hit_grid = False
        self.view_point = None
        self.giro_extra = 0.0
        self.raiz = build.criar_raiz(context)
        build.aplicar(self.raiz, context.window_manager.btm_stairs.escada())
        self._ocultar(True)
        context.area.header_text_set(tr("Clique no piso para inserir | R gira 90° | Esc cancela"))
        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}

    def _ocultar(self, oculto):
        for o in [self.raiz, *self.raiz.children]:
            if o.type == 'MESH' or o is self.raiz:
                o.hide_set(oculto)

    def _posicionar(self):
        if self.hit_location is None:
            self._ocultar(True)
            return
        ponto = Vector(self.hit_location)
        ponto.z = 0
        angulo = self.giro_extra
        normal = _normal_da_face(self.hit_object, self.hit_face_index) if _e_parede(self.hit_object) else None
        if normal is not None:
            angulo += math.atan2(normal.y, normal.x)          # o lado x = 0 da escada encosta na face
        else:
            ponto.x = hb_snap.snap_value_to_grid(ponto.x)
            ponto.y = hb_snap.snap_value_to_grid(ponto.y)
        self.raiz.location = ponto
        self.raiz.rotation_euler = (0, 0, angulo)
        self._ocultar(False)

    def _encerrar(self, context):
        context.area.header_text_set(None)

    def modal(self, context, event):
        context.area.tag_redraw()
        if event.type == 'INBETWEEN_MOUSEMOVE':
            return {'RUNNING_MODAL'}
        self.mouse_pos = Vector((event.mouse_x - self.region.x, event.mouse_y - self.region.y))
        self._ocultar(True)
        hb_snap.main(self, event.ctrl, context)
        self._posicionar()
        if event.type == 'R' and event.value == 'PRESS':
            self.giro_extra += math.radians(90)
            return {'RUNNING_MODAL'}
        if event.type == 'LEFTMOUSE' and event.value == 'PRESS' and self.hit_location is not None:
            self._encerrar(context)
            bpy.ops.object.select_all(action='DESELECT')
            self.raiz.select_set(True)
            context.view_layer.objects.active = self.raiz
            context.window_manager.btm_stairs.editando = self.raiz.name
            return {'FINISHED'}
        if event.type in {'RIGHTMOUSE', 'ESC'}:
            build.limpar(self.raiz)
            bpy.data.objects.remove(self.raiz, do_unlink=True)
            self._encerrar(context)
            return {'CANCELLED'}
        return {'PASS_THROUGH'}

    def execute(self, context):
        """Sem modal (scripts e testes): insere na origem do cursor 3D."""
        raiz = build.criar_raiz(context)
        build.aplicar(raiz, context.window_manager.btm_stairs.escada())
        raiz.location = context.scene.cursor.location.copy()
        context.window_manager.btm_stairs.editando = raiz.name
        return {'FINISHED'}


class CAFFMOB_OT_escada_aplicar(bpy.types.Operator):
    """Aplica as medidas do editor à escada em edição, regenerando as peças"""
    bl_idname = 'caffmob.escada_aplicar'
    bl_label = "Aplicar à escada"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        nome = context.window_manager.btm_stairs.editando
        return bool(nome) and bpy.data.objects.get(nome) is not None

    def execute(self, context):
        state = context.window_manager.btm_stairs
        n = build.aplicar(bpy.data.objects[state.editando], state.escada())
        self.report({'INFO'}, tr("Escada regenerada: {} peças").format(n))
        return {'FINISHED'}


class CAFFMOB_OT_escada_nova(bpy.types.Operator):
    """Começa uma escada nova no editor, com as medidas confortáveis"""
    bl_idname = 'caffmob.escada_nova'
    bl_label = "Nova escada"

    def execute(self, context):
        context.window_manager.btm_stairs.inicial()
        return {'FINISHED'}


class CAFFMOB_OT_escada_editar(bpy.types.Operator):
    """Abre a escada selecionada no editor de escadas"""
    bl_idname = 'caffmob.escada_editar'
    bl_label = "Abrir no editor de escadas"

    @classmethod
    def poll(cls, context):
        return context.active_object is not None and root_of(context.active_object) is not None

    def execute(self, context):
        raiz = root_of(context.active_object)
        context.window_manager.btm_stairs.carregar(spec(raiz), raiz.name)
        try:
            from ..ui import sidebar
            st = sidebar.state(context)
            st.open_group_stairs = True
        except (AttributeError, ImportError):
            pass
        return {'FINISHED'}


class CAFFMOB_OT_escada_confortavel(bpy.types.Operator):
    """Largura e comprimento pela regra de Blondel (2 espelhos + 1 piso ≈ 63 cm)"""
    bl_idname = 'caffmob.escada_confortavel'
    bl_label = "Medidas confortáveis para a altura"

    def execute(self, context):
        state = context.window_manager.btm_stairs
        x, y = core.planta_confortavel(state.escada())
        state['mm_largura_total'], state['mm_comprimento'] = x, y
        return {'FINISHED'}


class CAFFMOB_OT_escada_campo(bpy.types.Operator):
    """Muda uma medida da escada selecionada e regenera as peças"""
    bl_idname = 'caffmob.escada_campo'
    bl_label = "Editar escada"
    bl_options = {'INTERNAL'}

    escada: bpy.props.StringProperty(options={'HIDDEN'})  # type: ignore
    campo: bpy.props.StringProperty(options={'HIDDEN'})  # type: ignore
    valor: bpy.props.StringProperty(options={'HIDDEN'})  # type: ignore

    def execute(self, context):
        raiz = bpy.data.objects.get(self.escada)
        if raiz is None or root_of(raiz) is not raiz:
            return {'CANCELLED'}
        e = spec(raiz)
        if self.campo == 'tipo':
            e.tipo = self.valor
            e.x, e.y = core.planta_confortavel(e.normalizada())
        elif self.campo in ('x', 'y', 'z', 'largura'):
            setattr(e, self.campo, float(self.valor))
        else:
            return {'CANCELLED'}
        build.aplicar(raiz, e)
        return {'FINISHED'}


classes = (CAFFMOB_OT_escada_inserir, CAFFMOB_OT_escada_aplicar, CAFFMOB_OT_escada_nova, CAFFMOB_OT_escada_editar,
           CAFFMOB_OT_escada_confortavel, CAFFMOB_OT_escada_campo)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
