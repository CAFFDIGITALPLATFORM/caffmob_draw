"""Câmeras do projeto do Promob e a ferramenta Gerenciar câmeras (071, 5ª auditoria).

O `.promob` guarda as vistas salvas (`VIEWPOINTCOLLECTION`: "CAM 0001"...) e a vista dinâmica do momento em que foi
salvo (`VIEWPOINT`), cada uma com observador, alvo, campo de visão e os cortes anterior e posterior. Cada vista vira
uma câmera do Blender com o alvo num Empty (Track To): mover o alvo ou o observador reapontam a câmera, como o olho e
a mira da Vista Dinâmica do Promob.

A ferramenta lista todas as câmeras da cena (as do Promob e as da pessoa), olha por uma, cria uma da vista atual,
regrava uma pela vista atual, remove e percorre as vistas em sequência (Passo = quadros entre duas vistas; FPS = da
cena). Os campos seguem a Vista Dinâmica: Corte anterior, Corte posterior, Altura do alvo, Altura do observador.
"""
import math

import bpy  # type: ignore
from mathutils import Vector  # type: ignore

from ..data.i18n import N_, tr

MM = 0.001
COLECAO = "Câmeras do Promob"
ALVO_PROP = 'btm_camera_alvo'          # nome do Empty alvo da câmera
PROMOB_PROP = 'btm_camera_promob'      # a câmera veio do .promob
SUFIXO_DO_ALVO = " · alvo"
PERCURSO = "Percurso"


# -- criar (importação) ----------------------------------------------------------------------------------------------
def _colecao(context):
    colecao = bpy.data.collections.get(COLECAO)
    if colecao is None:
        colecao = bpy.data.collections.new(COLECAO)
    if colecao.name not in context.scene.collection.children:
        context.scene.collection.children.link(colecao)
    return colecao


def _nova(context, nome, observador, alvo, colecao=None):
    colecao = colecao or _colecao(context)
    dados = bpy.data.cameras.new(nome)
    cam = bpy.data.objects.new(nome, dados)
    colecao.objects.link(cam)
    mira = bpy.data.objects.new(nome + SUFIXO_DO_ALVO, None)
    mira.empty_display_type = 'SPHERE'
    mira.empty_display_size = 0.05
    colecao.objects.link(mira)
    cam.location, mira.location = observador, alvo
    trava = cam.constraints.new('TRACK_TO')
    trava.target = mira
    trava.track_axis, trava.up_axis = 'TRACK_NEGATIVE_Z', 'UP_Y'
    cam[ALVO_PROP] = mira.name
    return cam


def criar(context, vistas):
    """Câmeras das vistas do Promob; a vista dinâmica vira a câmera ativa da cena. Devolve quantas criou."""
    if not vistas:
        return 0
    colecao = _colecao(context)
    ativa = None
    for vista in vistas:
        nome = tr("Vista dinâmica") if vista.get('atual') else vista['nome']
        cam = _nova(context, nome, Vector(vista['observador']) * MM, Vector(vista['alvo']) * MM, colecao)
        cam[PROMOB_PROP] = True
        dados = cam.data
        dados.sensor_fit = 'VERTICAL'
        dados.angle_y = math.radians(max(1.0, min(170.0, float(vista.get('fov') or 50.0))))
        dados.clip_start = max(float(vista.get('corte_anterior') or 1.0) * MM, 0.001)
        dados.clip_end = max(float(vista.get('corte_posterior') or 50000.0) * MM, dados.clip_start + 0.01)
        if not vista.get('perspectiva', True) and vista.get('largura_ortogonal'):
            dados.type = 'ORTHO'
            dados.ortho_scale = float(vista['largura_ortogonal']) * MM
        if vista.get('atual') or ativa is None:
            ativa = cam
    context.scene.camera = ativa
    sincronizar_linhas(context)
    context.window_manager.btm_cameras.indice = todas(context.scene).index(ativa)
    return len(vistas)


# -- consulta -----------------------------------------------------------------------------------------------------------
def alvo_de(cam):
    nome = cam.get(ALVO_PROP) if cam is not None else None
    return bpy.data.objects.get(nome) if nome else None


def todas(scene):
    return sorted((o for o in scene.objects if o.type == 'CAMERA'), key=lambda o: o.name)


def ativa(context):
    lista = todas(context.scene)
    i = context.window_manager.btm_cameras.indice
    return lista[i] if 0 <= i < len(lista) else None


def _ver_pela(context, cam):
    context.scene.camera = cam
    for area in (context.screen.areas if context.screen else []):
        if area.type == 'VIEW_3D':
            area.spaces.active.region_3d.view_perspective = 'CAMERA'
            area.tag_redraw()


# -- campos da Vista Dinâmica (sobre a câmera da lista) -------------------------------------------------------------
def _get(campo):
    def get(self):
        cam = ativa(bpy.context)
        if cam is None:
            return 0.0
        mira = alvo_de(cam)
        if campo == 'corte_anterior':
            return cam.data.clip_start
        if campo == 'corte_posterior':
            return cam.data.clip_end
        if campo == 'altura_do_observador':
            return cam.matrix_world.translation.z
        if campo == 'altura_do_alvo':
            return mira.matrix_world.translation.z if mira is not None else 0.0
        return cam.data.angle_y
    return get


def _set(campo):
    def set_(self, valor):
        cam = ativa(bpy.context)
        if cam is None:
            return
        mira = alvo_de(cam)
        if campo == 'corte_anterior':
            cam.data.clip_start = max(valor, 0.001)
        elif campo == 'corte_posterior':
            cam.data.clip_end = max(valor, cam.data.clip_start + 0.01)
        elif campo == 'altura_do_observador':
            cam.location.z = valor
        elif campo == 'altura_do_alvo' and mira is not None:
            mira.location.z = valor
        elif campo == 'campo_de_visao':
            cam.data.sensor_fit = 'VERTICAL'
            cam.data.angle_y = max(math.radians(1.0), min(valor, math.radians(170.0)))
    return set_


def _escolher(self, context):
    cam = ativa(context)
    if cam is not None:
        _ver_pela(context, cam)


class BTM_PG_Cameras(bpy.types.PropertyGroup):
    indice: bpy.props.IntProperty(name=N_("Câmera"), default=0, min=0, update=_escolher)  # type: ignore
    corte_anterior: bpy.props.FloatProperty(name=N_("Corte anterior"), subtype='DISTANCE', min=0.001,  # type: ignore
                                            get=_get('corte_anterior'), set=_set('corte_anterior'))
    corte_posterior: bpy.props.FloatProperty(name=N_("Corte posterior"), subtype='DISTANCE', min=0.01,  # type: ignore
                                             get=_get('corte_posterior'), set=_set('corte_posterior'))
    altura_do_alvo: bpy.props.FloatProperty(name=N_("Altura do alvo"), subtype='DISTANCE',  # type: ignore
                                            get=_get('altura_do_alvo'), set=_set('altura_do_alvo'))
    altura_do_observador: bpy.props.FloatProperty(name=N_("Altura do observador"), subtype='DISTANCE',  # type: ignore
                                                  get=_get('altura_do_observador'), set=_set('altura_do_observador'))
    campo_de_visao: bpy.props.FloatProperty(name=N_("Campo de visão"), subtype='ANGLE',  # type: ignore
                                            get=_get('campo_de_visao'), set=_set('campo_de_visao'))
    passo: bpy.props.IntProperty(name=N_("Passo"), description=N_("Quadros entre duas vistas no percurso"),  # type: ignore
                                 default=50, min=1, max=1000)
    fps: bpy.props.IntProperty(name=N_("FPS"), default=5, min=1, max=120)  # type: ignore


# -- operadores ---------------------------------------------------------------------------------------------------------
class CAFFMOB_OT_camera_ver(bpy.types.Operator):
    """Olha pela câmera escolhida na lista"""
    bl_idname = 'caffmob.camera_ver'
    bl_label = N_("Ver pela câmera")

    def execute(self, context):
        cam = ativa(context)
        if cam is None:
            self.report({'ERROR'}, tr("Nenhuma câmera na cena."))
            return {'CANCELLED'}
        _ver_pela(context, cam)
        return {'FINISHED'}


def _vista_3d(context):
    for area in (context.screen.areas if context.screen else []):
        if area.type == 'VIEW_3D':
            return area.spaces.active.region_3d
    return None


class CAFFMOB_OT_camera_nova(bpy.types.Operator):
    """Cria uma câmera na vista atual, com o alvo no centro da vista"""
    bl_idname = 'caffmob.camera_nova'
    bl_label = N_("Nova câmera da vista")
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        rv3d = _vista_3d(context)
        if rv3d is None:
            observador, alvo = Vector((0.0, -5.0, 1.6)), Vector((0.0, 0.0, 1.2))
        else:
            inversa = rv3d.view_matrix.inverted()
            observador, alvo = inversa.translation.copy(), rv3d.view_location.copy()
        nome = "CAM %04d" % (len(todas(context.scene)) + 1)
        cam = _nova(context, nome, observador, alvo)
        sincronizar_linhas(context)
        lista = todas(context.scene)
        context.window_manager.btm_cameras.indice = lista.index(cam)
        return {'FINISHED'}


class CAFFMOB_OT_camera_atualizar(bpy.types.Operator):
    """Regrava a câmera escolhida com a vista atual (observador e alvo)"""
    bl_idname = 'caffmob.camera_atualizar'
    bl_label = N_("Atualizar pela vista")
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        cam, rv3d = ativa(context), _vista_3d(context)
        if cam is None or rv3d is None:
            return {'CANCELLED'}
        if rv3d.view_perspective == 'CAMERA':
            self.report({'INFO'}, tr("Saia da vista da câmera e enquadre antes de atualizar."))
            return {'CANCELLED'}
        cam.location = rv3d.view_matrix.inverted().translation
        mira = alvo_de(cam)
        if mira is not None:
            mira.location = rv3d.view_location
        return {'FINISHED'}


class CAFFMOB_OT_camera_remover(bpy.types.Operator):
    """Remove a câmera escolhida e o alvo dela"""
    bl_idname = 'caffmob.camera_remover'
    bl_label = N_("Remover câmera")
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        cam = ativa(context)
        if cam is None:
            return {'CANCELLED'}
        mira = alvo_de(cam)
        dados = cam.data
        bpy.data.objects.remove(cam, do_unlink=True)
        if mira is not None:
            bpy.data.objects.remove(mira, do_unlink=True)
        if dados is not None and dados.users == 0:
            bpy.data.cameras.remove(dados)
        sincronizar_linhas(context)
        estado = context.window_manager.btm_cameras
        estado.indice = max(0, min(estado.indice, len(todas(context.scene)) - 1))
        return {'FINISHED'}


class CAFFMOB_OT_camera_percorrer(bpy.types.Operator):
    """Anima uma câmera de percurso passando por todas as vistas, na ordem da lista, e toca"""
    bl_idname = 'caffmob.camera_percorrer'
    bl_label = N_("Percorrer as vistas")
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        cena, estado = context.scene, context.window_manager.btm_cameras
        vistas = [c for c in todas(cena) if c.name != PERCURSO and alvo_de(c) is not None]
        if len(vistas) < 2:
            self.report({'ERROR'}, tr("O percurso precisa de duas câmeras ou mais."))
            return {'CANCELLED'}
        cam = bpy.data.objects.get(PERCURSO)
        if cam is None:
            cam = _nova(context, PERCURSO, vistas[0].matrix_world.translation, alvo_de(vistas[0]).location)
        mira = alvo_de(cam)
        for o in (cam, mira):
            o.animation_data_clear()
        for i, vista in enumerate(vistas):
            quadro = 1 + i * estado.passo
            cam.location = vista.matrix_world.translation
            mira.location = alvo_de(vista).matrix_world.translation
            cam.data.angle_y = vista.data.angle_y
            cam.keyframe_insert('location', frame=quadro)
            mira.keyframe_insert('location', frame=quadro)
        cena.render.fps = estado.fps
        cena.frame_start, cena.frame_end = 1, 1 + (len(vistas) - 1) * estado.passo
        cena.frame_set(1)
        _ver_pela(context, cam)
        if context.screen is not None and not context.screen.is_animation_playing:
            bpy.ops.screen.animation_play()
        return {'FINISHED'}


class CAFFMOB_UL_cameras(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index=0):
        cam = todas(context.scene)[index] if index < len(todas(context.scene)) else None
        if cam is None:
            return
        layout.label(text=cam.name, icon='VIEW_CAMERA' if cam == context.scene.camera else 'CAMERA_DATA')


class BTM_PG_CameraLinha(bpy.types.PropertyGroup):
    pass


def sincronizar_linhas(context=None):
    """A lista da UIList espelha as câmeras da cena (a UIList precisa de uma coleção de propriedades)."""
    context = context or bpy.context
    linhas = context.window_manager.btm_camera_linhas
    n = len(todas(context.scene))
    while len(linhas) < n:
        linhas.add()
    while len(linhas) > n:
        linhas.remove(len(linhas) - 1)


def _sincronizar_depois():
    sincronizar_linhas()
    return None


class CAFFMOB_PT_cameras(bpy.types.Panel):
    bl_label = N_("Gerenciar câmeras")
    bl_idname = 'CAFFMOB_PT_cameras'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "CAFFMob Draw"    # uma aba só para o addon (identidade)
    bl_order = 90

    def draw(self, context):
        layout = self.layout
        estado = context.window_manager.btm_cameras
        lista = todas(context.scene)
        if len(context.window_manager.btm_camera_linhas) != len(lista) and \
                not bpy.app.timers.is_registered(_sincronizar_depois):
            bpy.app.timers.register(_sincronizar_depois, first_interval=0.0)   # o desenho não pode mexer em dados
        linha = layout.row()
        linha.template_list('CAFFMOB_UL_cameras', '', context.window_manager, 'btm_camera_linhas', estado, 'indice',
                            rows=4)
        botoes = linha.column(align=True)
        botoes.operator('caffmob.camera_nova', text="", icon='ADD')
        botoes.operator('caffmob.camera_remover', text="", icon='REMOVE')
        botoes.separator()
        botoes.operator('caffmob.camera_atualizar', text="", icon='FILE_REFRESH')
        botoes.operator('caffmob.camera_ver', text="", icon='HIDE_OFF')
        if ativa(context) is None:
            layout.label(text=tr("Nenhuma câmera na cena."))
            return
        col = layout.column(align=True)
        col.prop(estado, 'corte_anterior')
        col.prop(estado, 'corte_posterior')
        col = layout.column(align=True)
        col.prop(estado, 'altura_do_alvo')
        col.prop(estado, 'altura_do_observador')
        col.prop(estado, 'campo_de_visao')
        linha = layout.row(align=True)
        linha.prop(estado, 'passo')
        linha.prop(estado, 'fps')
        linha = layout.row(align=True)
        linha.operator('caffmob.camera_percorrer', icon='PLAY')
        linha.operator('screen.animation_cancel', text="", icon='PAUSE').restore_frame = True


classes = (BTM_PG_Cameras, BTM_PG_CameraLinha, CAFFMOB_OT_camera_ver, CAFFMOB_OT_camera_nova, CAFFMOB_OT_camera_atualizar,
           CAFFMOB_OT_camera_remover, CAFFMOB_OT_camera_percorrer, CAFFMOB_UL_cameras, CAFFMOB_PT_cameras)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.WindowManager.btm_cameras = bpy.props.PointerProperty(type=BTM_PG_Cameras)
    bpy.types.WindowManager.btm_camera_linhas = bpy.props.CollectionProperty(type=BTM_PG_CameraLinha)


def unregister():
    del bpy.types.WindowManager.btm_camera_linhas
    del bpy.types.WindowManager.btm_cameras
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
