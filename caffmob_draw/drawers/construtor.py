"""Construtor de gavetas na barra lateral (072 onda B; RF-01, RF-07, RF-08, RF-14, D-20 a D-24).

- `WindowManager.btm_drawer_builder`: quantidade, modelo ou corrediça, e os campos do gaveteiro novo;
- `caffmob.gaveta_espaco`: passar o mouse destaca o espaço livre com as medidas; o clique insere ali;
- `caffmob.gaveta_inserir`: insere no alvo (vão da lista do painel ou o espaço clicado);
- `caffmob.gaveteiro_criar` e `caffmob.gaveta_salvar_modelo`.
"""
import json

import blf
import bpy
import gpu
from bpy_extras import view3d_utils
from gpu_extras.batch import batch_for_shader
from mathutils import Vector

from ..data.i18n import N_, tr
from . import build, catalogo, core, espaco, gaveteiro, gaveteiro_core, inserir, modelos, ops
from .scene import spec

_MODELOS, _CORREDICAS = [], []


def _modelos(_self, _context):
    _MODELOS[:] = [('NENHUM', tr("Sem modelo (corrediça abaixo)"), '')] + \
        [(m.id, m.nome, m.descricao) for m in modelos.todos(build.pasta_do_usuario())]
    return _MODELOS


def _corredicas(_self, _context):
    _CORREDICAS[:] = [(c.id, c.nome, c.carga) for c in catalogo.todas(build.pasta_do_usuario())]
    return _CORREDICAS


class BTM_PG_DrawerBuilder(bpy.types.PropertyGroup):
    quantidade: bpy.props.IntProperty(name=N_("Gavetas"), default=3, min=1, max=8)  # type: ignore
    modelo: bpy.props.EnumProperty(name=N_("Modelo"), items=_modelos)  # type: ignore
    corredica: bpy.props.EnumProperty(name=N_("Corrediça"), items=_corredicas)  # type: ignore
    alvo: bpy.props.StringProperty(options={'HIDDEN'})  # type: ignore
    nome_do_modelo: bpy.props.StringProperty(name=N_("Nome do modelo"), default="Minha gaveta")  # type: ignore
    largura: bpy.props.FloatProperty(name=N_("Largura (mm)"), default=450, min=200, max=1200)  # type: ignore
    altura: bpy.props.FloatProperty(name=N_("Altura (mm)"), default=600, min=200, max=1200)  # type: ignore
    profundidade: bpy.props.FloatProperty(name=N_("Profundidade (mm)"), default=500, min=300, max=800)  # type: ignore
    metodo: bpy.props.EnumProperty(name=N_("Montagem"), items=[  # type: ignore
        ('BASE', N_("Base passante"), ""), ('LATERAL', N_("Lateral passante"), "")])
    tipo: bpy.props.EnumProperty(name=N_("Tipo"), items=[  # type: ignore
        ('volante', N_("Volante"), N_("Rodízios e tampo de 25 mm")), ('fixo', N_("Fixo"), ""),
        ('suspenso', N_("Suspenso"), ""), ('oculto', N_("Oculto"), N_("Frente de 15 mm"))])

    def gaveta(self):
        modelo = modelos.por_id(self.modelo, build.pasta_do_usuario()) if self.modelo != 'NENHUM' else None
        if modelo is not None:
            return core.Gaveta.de_dict(modelo.gaveta)
        return core.Gaveta(corredica=self.corredica or 'telescopica')


def _relatar(op, motivos):
    if motivos:
        op.report({'ERROR'}, ' '.join(motivos))
        return {'CANCELLED'}
    return {'FINISHED'}


class CAFFMOB_OT_gaveta_inserir(bpy.types.Operator):
    """Insere as gavetas do construtor no espaço escolhido"""
    bl_idname = 'caffmob.gaveta_inserir'
    bl_label = "Inserir gavetas"
    bl_options = {'REGISTER', 'UNDO'}

    alvo: bpy.props.StringProperty(options={'HIDDEN', 'SKIP_SAVE'})  # type: ignore

    def execute(self, context):
        b = context.window_manager.btm_drawer_builder
        try:
            alvo = json.loads(self.alvo or b.alvo)
        except ValueError:
            self.report({'ERROR'}, tr("Escolha um espaço primeiro."))
            return {'CANCELLED'}
        return _relatar(self, inserir.inserir(context, alvo, b.quantidade, b.gaveta()))


class CAFFMOB_OT_gaveteiro_criar(bpy.types.Operator):
    """Cria um gaveteiro novo com a montagem, o tipo e as gavetas do construtor"""
    bl_idname = 'caffmob.gaveteiro_criar'
    bl_label = "Criar gaveteiro"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        b = context.window_manager.btm_drawer_builder
        g = gaveteiro_core.Gaveteiro(b.largura, b.altura, b.profundidade, b.metodo, b.tipo, b.quantidade)
        _raiz, motivos = gaveteiro.criar(context, g, b.gaveta())
        return _relatar(self, motivos)


class CAFFMOB_OT_gaveta_salvar_modelo(bpy.types.Operator):
    """Salva a gaveta selecionada como modelo seu, para usar em outros projetos"""
    bl_idname = 'caffmob.gaveta_salvar_modelo'
    bl_label = "Salvar como modelo"

    @classmethod
    def poll(cls, context):
        frente = ops.frente_selecionada(context)
        return frente is not None and frente.get('btm_drawer') is not None

    def execute(self, context):
        b = context.window_manager.btm_drawer_builder
        m = modelos.salvar(build.pasta_do_usuario(), b.nome_do_modelo, spec(ops.frente_selecionada(context)))
        self.report({'INFO'}, tr("Modelo salvo: {}").format(m.nome))
        return {'FINISHED'}


# -- espaço sob o mouse -----------------------------------------------------------------------------------------------
_destaque = {'alvo': None, 'handles': []}


def _cantos(alvo):
    raiz = espaco.raiz_do_alvo(alvo)
    if raiz is None:
        return []
    lo, hi = alvo['lo'], alvo['hi']
    pontos = [Vector((x, y, z)) for x in (lo[0], hi[0]) for y in (lo[1], hi[1]) for z in (lo[2], hi[2])]
    return [raiz.matrix_world @ p for p in pontos]


def _desenhar_caixa():
    alvo = _destaque['alvo']
    if not alvo:
        return
    c = _cantos(alvo)
    if not c:
        return
    arestas = [(0, 1), (2, 3), (4, 5), (6, 7), (0, 2), (1, 3), (4, 6), (5, 7), (0, 4), (1, 5), (2, 6), (3, 7)]
    shader = gpu.shader.from_builtin('UNIFORM_COLOR')
    gpu.state.line_width_set(2.0)
    shader.uniform_float('color', (0.95, 0.62, 0.2, 1.0))
    batch_for_shader(shader, 'LINES', {'pos': [c[i] for a in arestas for i in a]}).draw(shader)
    gpu.state.line_width_set(1.0)


def _desenhar_texto():
    alvo = _destaque['alvo']
    if not alvo:
        return
    regiao, r3d = bpy.context.region, bpy.context.region_data
    c = _cantos(alvo)
    if not c or r3d is None:
        return
    centro = sum(c, Vector()) / len(c)
    p = view3d_utils.location_3d_to_region_2d(regiao, r3d, centro)
    if p is None:
        return
    texto = tr("{} × {} × {} mm").format(int(alvo['largura']), int(alvo['altura']), int(alvo['profundidade']))
    blf.size(0, 14)
    blf.color(0, 1, 1, 1, 1)
    blf.position(0, p.x - 60, p.y, 0)
    blf.draw(0, texto)
    if alvo.get('ocupado'):
        blf.position(0, p.x - 60, p.y - 18, 0)
        blf.draw(0, tr("Vão com frentes: inserir substitui"))


def _ligar():
    if not _destaque['handles']:
        _destaque['handles'] = [
            bpy.types.SpaceView3D.draw_handler_add(_desenhar_caixa, (), 'WINDOW', 'POST_VIEW'),
            bpy.types.SpaceView3D.draw_handler_add(_desenhar_texto, (), 'WINDOW', 'POST_PIXEL')]


def _desligar():
    for h, regiao in zip(_destaque['handles'], ('WINDOW', 'WINDOW')):
        bpy.types.SpaceView3D.draw_handler_remove(h, regiao)
    _destaque['handles'] = []
    _destaque['alvo'] = None


def alvo_no_mouse(context, x, y):
    regiao, r3d = context.region, context.region_data
    origem = view3d_utils.region_2d_to_origin_3d(regiao, r3d, (x, y))
    direcao = view3d_utils.region_2d_to_vector_3d(regiao, r3d, (x, y))
    achou, ponto, _normal, _indice, obj, _matriz = context.scene.ray_cast(context.evaluated_depsgraph_get(), origem,
                                                                         direcao)
    if not achou:
        return None
    return espaco.no_ponto(context, obj, ponto, direcao)


class CAFFMOB_OT_gaveta_espaco(bpy.types.Operator):
    """Passe o mouse sobre um vão: o espaço livre fica destacado com as medidas; clique para inserir as gavetas"""
    bl_idname = 'caffmob.gaveta_espaco'
    bl_label = "Escolher espaço na vista 3D"
    bl_options = {'REGISTER', 'UNDO'}

    def invoke(self, context, event):
        if context.area is None or context.area.type != 'VIEW_3D':
            self.report({'WARNING'}, tr("Use na vista 3D."))
            return {'CANCELLED'}
        _ligar()
        context.area.header_text_set(tr("Passe o mouse sobre um vão | clique insere | Esc cancela"))
        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}

    def _sair(self, context):
        _desligar()
        context.area.header_text_set(None)
        context.area.tag_redraw()

    def modal(self, context, event):
        if event.type == 'MOUSEMOVE':
            _destaque['alvo'] = alvo_no_mouse(context, event.mouse_region_x, event.mouse_region_y)
            context.area.tag_redraw()
            return {'RUNNING_MODAL'}
        if event.type == 'LEFTMOUSE' and event.value == 'PRESS':
            alvo = _destaque['alvo']
            self._sair(context)
            if alvo is None:
                return {'CANCELLED'}
            b = context.window_manager.btm_drawer_builder
            b.alvo = json.dumps(alvo)
            return _relatar(self, inserir.inserir(context, alvo, b.quantidade, b.gaveta()))
        if event.type in {'RIGHTMOUSE', 'ESC'}:
            self._sair(context)
            return {'CANCELLED'}
        return {'PASS_THROUGH'}


def draw(layout, context):
    """Grupo "Gavetas" da barra lateral (D-21)."""
    b = context.window_manager.btm_drawer_builder
    col = layout.column()
    col.prop(b, 'modelo')
    if b.modelo == 'NENHUM':
        col.prop(b, 'corredica')
    col.prop(b, 'quantidade')
    col.operator('caffmob.gaveta_espaco', icon='RESTRICT_SELECT_OFF')
    from ..selection import classify
    raiz, library = classify.module_root(context.active_object) if context.active_object else (None, None)
    if raiz is not None and library == 'BTM':
        caixa = col.box()
        caixa.label(text=tr("Vãos de {}").format(raiz.name), icon='MESH_CUBE')
        for alvo in espaco.vaos_do_modulo(context, raiz):
            linha = caixa.row(align=True)
            linha.label(text=tr("{} × {} × {} mm").format(int(alvo['largura']), int(alvo['altura']),
                                                          int(alvo['profundidade'])))
            op = linha.operator('caffmob.gaveta_inserir', text=tr("Inserir"), icon='ADD')
            op.alvo = json.dumps(alvo)
    col.separator()
    caixa = col.box()
    caixa.label(text=tr("Gaveteiro novo"), icon='MOD_ARRAY')
    grade = caixa.column(align=True)
    grade.prop(b, 'largura')
    grade.prop(b, 'altura')
    grade.prop(b, 'profundidade')
    caixa.prop(b, 'metodo', expand=True)
    caixa.prop(b, 'tipo')
    caixa.operator('caffmob.gaveteiro_criar', icon='ADD')
    col.separator()
    linha = col.row(align=True)
    linha.prop(b, 'nome_do_modelo', text="")
    linha.operator('caffmob.gaveta_salvar_modelo', text=tr("Salvar modelo"), icon='FILE_TICK')


classes = (BTM_PG_DrawerBuilder, CAFFMOB_OT_gaveta_inserir, CAFFMOB_OT_gaveteiro_criar,
           CAFFMOB_OT_gaveta_salvar_modelo, CAFFMOB_OT_gaveta_espaco)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.WindowManager.btm_drawer_builder = bpy.props.PointerProperty(type=BTM_PG_DrawerBuilder)


def unregister():
    if _destaque['handles']:
        _desligar()
    del bpy.types.WindowManager.btm_drawer_builder
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
