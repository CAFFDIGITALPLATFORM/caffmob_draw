"""Operadores da janela própria do construtor de armário v2 (feature 023, T002/T008; RN-02, RN-05, RN-18).

- `caffmob.armario_v2_window_open` abre a **nova janela** (via `window.open_editor`, que usa
  `canvas2d.window.open_window`), inicia a sessão, guarda o instantâneo (ponto de retorno do Cancelar) e lança o
  modal **dentro da janela nova** — o mesmo desenho do Editor de Paredes.
- `caffmob.armario_v2_window_modal` recebe os eventos: timer (fila, foco da aba), clique (seleciona a peça), ESC
  (descarta e avisa) e a morte da área (fecha pelo sistema, também avisando quando havia alteração).
- `caffmob.armario_v2_window_aplicar` grava um passo de desfazer sem fechar.
- `caffmob.armario_v2_window_cancelar` restaura o instantâneo e fecha.
- `caffmob.armario_v2_window_ok` grava um passo de desfazer e fecha.
- `caffmob.armario_v2_window_toggle` liga/desliga Cotas e Mostrar Portas no preview.

OK e Aplicar recusam quando `validar` acusa GEO-001/GEO-002 (RF-03), com o código no aviso.
"""

import json

import bpy  # type: ignore
from bpy_extras.io_utils import ExportHelper  # type: ignore

from ..data.i18n import tr
from . import anim
from . import build
from . import ops as ops_v2
from . import parity_core
from . import validar
from . import window as win_mod

TIMER_STEP = 0.1


def _raiz_da_cena(context):
    """Armário v2 da seleção ou o primeiro da coleção do construtor."""
    raiz = build.raiz_de(getattr(context, 'active_object', None))
    if raiz is not None:
        return raiz
    colecao = bpy.data.collections.get(build.COLECAO)
    if colecao is None:
        return None
    for candidato in colecao.objects:
        if build.e_raiz(candidato):
            return candidato
    return None


class _WindowOperator:
    """Base dos operadores da janela: exigem a sessão ativa."""

    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def _sessao(cls):
        return win_mod.sessao()

    @classmethod
    def poll(cls, context):
        if win_mod.sessao() is None:
            cls.poll_message_set("Janela do construtor não está aberta")
            return False
        return True

    def _avisar(self, avisos):
        for aviso in avisos:
            self.report({'WARNING'}, aviso)

    def _recusar_geometria(self, raiz):
        """True quando há GEO-001/GEO-002; reporta o primeiro código e não deixa confirmar (RF-03)."""
        erros = validar.violacoes_da_raiz(raiz)
        if not erros:
            return False
        primeiro = erros[0]
        self.report({'ERROR'}, f"{primeiro['codigo']}: {primeiro['nome']} {primeiro['detalhe']}")
        return True


class BTM_OT_ArmarioV2WindowOpen(bpy.types.Operator):
    """Abre a janela própria do construtor de armário v2"""
    bl_idname = "caffmob.armario_v2_window_open"
    bl_label = "Abrir Janela do Construtor"
    bl_options = {'REGISTER'}

    @classmethod
    def poll(cls, context):
        if bpy.app.background:
            return False
        if win_mod.janela_existe():
            cls.poll_message_set("Já existe uma janela do construtor aberta")
            return False
        return context.window is not None

    def execute(self, context):
        root = build.raiz_de(getattr(context, 'active_object', None))
        if root is None:
            root = _raiz_da_cena(context)
        if root is None:
            root = build.criar_raiz(context.scene)
        # A janela trabalha no armário da sessão: os operadores do painel (Montar Caixa, inserções, Gerar) usam a
        # seleção ativa, então o armário fica ativo enquanto a janela estiver aberta.
        if getattr(context, 'view_layer', None) is not None:
            context.view_layer.objects.active = root
        root.select_set(True)
        ops_v2.semear_contrato(context.scene)

        s = win_mod.JanelaSessao()
        s.armario_root = root
        s.snapshot = ops_v2.snapshot_de(root)
        s.aberto = True
        win_mod.iniciar_sessao(s)

        try:
            win, area, region = win_mod.open_editor(context, s)
        except RuntimeError as erro:
            self.report({'ERROR'}, str(erro))
            win_mod.encerrar_sessao()
            return {'CANCELLED'}

        with context.temp_override(window=win, area=area, region=region):
            bpy.ops.caffmob.armario_v2_window_modal('INVOKE_DEFAULT')
        return {'FINISHED'}


class BTM_OT_ArmarioV2WindowAba(bpy.types.Operator):
    """Troca a aba ativa da janela do construtor (e grava a escolha na cena)"""
    bl_idname = "caffmob.armario_v2_window_aba"
    bl_label = "Aba do construtor"
    bl_options = {'REGISTER'}

    alvo: bpy.props.EnumProperty(
        name="Aba",
        items=[('ESTRUTURA', "Estrutura", ""), ('DIVISOES', "Divisões", ""), ('GAVETAS', "Gavetas", ""),
               ('INTERNOS', "Internos", ""), ('PORTAS', "Portas", ""),
               ('DESLIZANTES', "Deslizantes", ""), ('FUNDOS', "Fundos", "")],
        default='ESTRUTURA')  # type: ignore

    def execute(self, context):
        if not win_mod.definir_aba(context, win_mod.sessao(), self.alvo):
            return {'CANCELLED'}
        return {'FINISHED'}


class BTM_OT_ArmarioV2WindowSelecionar(bpy.types.Operator):
    """Seleciona uma peça pelo nome (o clique do modal usa o mesmo núcleo)"""
    bl_idname = "caffmob.armario_v2_window_selecionar"
    bl_label = "Selecionar peça"
    bl_options = {'REGISTER'}

    nome: bpy.props.StringProperty(name="Peça")  # type: ignore
    vista: bpy.props.EnumProperty(name="Vista", items=[('FRONTAL', "Frontal", ""),
                                                        ('LATERAL', "Corte lateral", "")],
                                  default='FRONTAL')  # type: ignore
    acumular: bpy.props.BoolProperty(name="Acumular", default=False)  # type: ignore

    def execute(self, context):
        s = win_mod.sessao()
        if s is None or not self.nome:
            return {'CANCELLED'}
        item = {'nome': self.nome, 'vista': self.vista}
        atuais = s.selecionados if self.acumular else []
        if any((i.get('nome'), i.get('vista')) == (self.nome, self.vista) for i in atuais):
            atuais = [i for i in atuais if (i.get('nome'), i.get('vista')) != (self.nome, self.vista)]
        else:
            atuais = list(atuais) + [item]
        win_mod.definir_selecao(s, atuais)
        return {'FINISHED'}


class BTM_OT_ArmarioV2WindowLote(bpy.types.Operator):
    """Aplica mover / espelhar / apagar a todas as peças selecionadas, num passo de desfazer"""
    bl_idname = "caffmob.armario_v2_window_lote"
    bl_label = "Ação em lote"
    bl_options = {'REGISTER', 'UNDO'}

    acao: bpy.props.EnumProperty(
        name="Ação",
        items=[('MOVER_ESQ', "Mover para a esquerda", ""), ('MOVER_DIR', "Mover para a direita", ""),
               ('MOVER_CIMA', "Mover para cima", ""), ('MOVER_BAIXO', "Mover para baixo", ""),
               ('ESPELHAR', "Espelhar no eixo X", ""), ('APAGAR', "Apagar peças", "")],
        default='MOVER_DIR')  # type: ignore
    delta: bpy.props.FloatProperty(name="Passo (mm)", default=win_mod.DELTA_LOTE, min=0.1, max=1000.0)  # type: ignore

    def execute(self, context):
        s = win_mod.sessao()
        root = s.armario_root if s is not None else None
        if root is None:
            return {'CANCELLED'}
        try:
            quantas = win_mod.aplicar_lote(root, s, self.acao, self.delta)
        except ValueError as erro:
            self.report({'WARNING'}, str(erro))
            return {'CANCELLED'}
        bpy.ops.ed.undo_push(message="Armário: edição em lote")
        _janela, area, _region = win_mod._area_da_sessao()
        if area is not None:
            area.tag_redraw()
        self.report({'INFO'}, tr("{} peça(s): {}").format(quantas, self.acao.lower()))
        return {'FINISHED'}


PEDIDOS = {
    'MONTAR_CAIXA': 'caffmob.armario_v2_montar_caixa',
    'LIMPAR': 'caffmob.armario_v2_limpar',
    'DIVISORIA': 'caffmob.armario_v2_inserir_divisoria',
    'PRATELEIRA': 'caffmob.armario_v2_inserir_prateleira',
    'BLOCO_GAVETAS': 'caffmob.armario_v2_criar_bloco_gavetas',
    'INTERNO': 'caffmob.armario_v2_inserir_interno',
    'PLANO_CORTE': 'caffmob.opcut_generate',
}


class BTM_OT_ArmarioV2WindowPedido(bpy.types.Operator):
    """Enfileira um pedido do painel; quem escreve na cena é o modal (RN-02)"""
    bl_idname = "caffmob.armario_v2_window_pedido"
    bl_label = "Pedido do construtor"
    bl_options = {'REGISTER'}

    acao: bpy.props.EnumProperty(
        name="Pedido",
        items=[('MONTAR_CAIXA', "Montar Caixa", ""), ('LIMPAR', "Limpar", ""),
               ('DIVISORIA', "Inserir divisória", ""), ('PRATELEIRA', "Inserir prateleira", ""),
               ('BLOCO_GAVETAS', "Criar bloco de gavetas", ""), ('INTERNO', "Inserir interno", ""),
               ('PLANO_CORTE', "Gerar plano de corte", "")],
        default='MONTAR_CAIXA')  # type: ignore

    def execute(self, context):
        s = win_mod.sessao()
        if s is None:
            return {'CANCELLED'}
        win_mod.enfileirar(s, (PEDIDOS[self.acao], {}))
        return {'FINISHED'}


class BTM_OT_ArmarioV2WindowModal(bpy.types.Operator):
    """Interação da janela do construtor: timer, seleção, ESC e fechamento"""
    bl_idname = "caffmob.armario_v2_window_modal"
    bl_label = "Construtor de Armários"
    bl_options = {'REGISTER', 'INTERNAL'}

    _timer = None
    _tab_pronta = False
    _drag = None

    def invoke(self, context, event):
        if win_mod.sessao() is None:
            return {'CANCELLED'}
        self._timer = context.window_manager.event_timer_add(TIMER_STEP, window=context.window)
        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}

    def _end(self, context, keep):
        if self._timer is not None:
            try:
                context.window_manager.event_timer_remove(self._timer)
            except RuntimeError:
                pass
            self._timer = None
        s = win_mod.sessao()
        if s is not None:
            win_mod.gravar_memoria(context.scene, s)
        if not keep and s is not None:
            if s.suja:
                self.report({'WARNING'}, "Editor fechado: alterações descartadas")
            if s.armario_root is not None and s.snapshot:
                try:
                    ops_v2.aplicar_snapshot(s.armario_root, s.snapshot)
                    if not s.armario_root.btm_armario.gerado:
                        build.limpar(s.armario_root)
                except ValueError:
                    pass
        win_mod.close_window(s)
        win_mod.encerrar_sessao()

    def modal(self, context, event):
        s = win_mod.sessao()
        if s is None or not win_mod.janela_ativa(context, s):
            self._end(context, keep=False)
            return {'CANCELLED'}

        if event.type == 'TIMER':
            if not self._tab_pronta:
                self._tab_pronta = win_mod.focar_categoria(context, s)
            for aviso in win_mod.processar_fila(s):
                self.report({'WARNING'}, aviso)
            return {'PASS_THROUGH'}

        if event.type == 'LEFTMOUSE' and event.value == 'PRESS':
            escolhido = win_mod.selecionar_no_ponto(context, s, event.mouse_x, event.mouse_y,
                                                    acumular=bool(event.shift or event.ctrl))
            alvos = win_mod.objetos_da_selecao(s.armario_root, s) if escolhido is not None else []
            if alvos:
                obj = alvos[-1]
                self._drag = {'obj': obj, 'x': event.mouse_x, 'y': event.mouse_y,
                              'loc': obj.location.copy(), 'vista': (escolhido or {}).get('vista', 'FRONTAL'),
                              'dx': 0.0, 'dy': 0.0, 'dz': 0.0, 'moved': False}
            return {'PASS_THROUGH'}

        if event.type == 'MOUSEMOVE' and self._drag is not None:
            drag = self._drag
            obj = drag['obj']
            if obj.name not in bpy.data.objects:
                self._drag = None
                return {'PASS_THROUGH'}
            dx_px = event.mouse_x - drag['x']
            dy_px = event.mouse_y - drag['y']
            if not drag['moved'] and abs(dx_px) + abs(dy_px) < win_mod.ARRASTE_MIN_PX:
                return {'PASS_THROUGH'}
            drag['moved'] = True
            lateral = drag['vista'] == 'LATERAL'
            escala = max(1e-6, s.escala_lateral if lateral else s.escala_frontal)
            dx_mm = dx_px / escala
            dz_mm = dy_px / escala
            if lateral:
                drag['dy'] = dx_mm
                obj.location.y = drag['loc'].y + dx_mm * 0.001
            else:
                drag['dx'] = dx_mm
                obj.location.x = drag['loc'].x + dx_mm * 0.001
            drag['dz'] = dz_mm
            obj.location.z = drag['loc'].z + dz_mm * 0.001
            return {'PASS_THROUGH'}

        if event.type == 'LEFTMOUSE' and event.value == 'RELEASE' and self._drag is not None:
            drag = self._drag
            self._drag = None
            if drag['moved']:
                win_mod.registrar_movimento(s.armario_root, drag['obj'], drag['dx'], drag['dz'], drag['dy'])
                s.suja = True
                bpy.ops.ed.undo_push(message="Armário: arrastar peça")
                _janela, area, _region = win_mod._area_da_sessao()
                if area is not None:
                    area.tag_redraw()
            return {'PASS_THROUGH'}

        if event.type == 'RIGHTMOUSE' and event.value == 'PRESS':
            escolhido = win_mod.selecionar_no_ponto(context, s, event.mouse_x, event.mouse_y, acumular=False)
            if escolhido is not None:
                bpy.ops.wm.call_menu(name=BTM_MT_ArmarioV2WindowContext.bl_idname)
                return {'RUNNING_MODAL'}
            return {'PASS_THROUGH'}

        if event.type == 'N' and event.value == 'PRESS':
            bpy.ops.caffmob.armario_v2_window_painel()
            return {'RUNNING_MODAL'}

        if event.type == 'ESC' and event.value == 'PRESS':
            self._end(context, keep=False)
            return {'CANCELLED'}

        return {'PASS_THROUGH'}


class BTM_OT_ArmarioV2WindowLimparAjustes(_WindowOperator, bpy.types.Operator):
    """Esquece os ajustes manuais do lote e refaz as peças a partir do spec (T020)"""
    bl_idname = "caffmob.armario_v2_window_limpar_ajustes"
    bl_label = "Limpar ajustes manuais"

    def execute(self, context):
        s = win_mod.sessao()
        root = s.armario_root if s is not None else None
        if root is None:
            return {'CANCELLED'}
        quantos = len(root.btm_armario.ajustes)
        if not quantos:
            self.report({'INFO'}, "Nenhum ajuste manual para limpar")
            return {'CANCELLED'}
        while len(root.btm_armario.ajustes):
            root.btm_armario.ajustes.remove(0)
        s.selecionados = []
        s.selecionado = None
        s.suja = True
        if root.btm_armario.gerado:
            gerou, avisos = ops_v2.gerar_armario(root, context)
            self._avisar(avisos)
            if not gerou:
                return {'CANCELLED'}
        _janela, area, _region = win_mod._area_da_sessao()
        if area is not None:
            area.tag_redraw()
        self.report({'INFO'}, tr("{} ajuste(s) manual(is) removido(s)").format(quantos))
        return {'FINISHED'}


class BTM_OT_ArmarioV2WindowToggle(bpy.types.Operator):
    """Liga/desliga Cotas ou Mostrar Portas no preview da janela"""
    bl_idname = "caffmob.armario_v2_window_toggle"
    bl_label = "Alternar Exibição"
    bl_options = {'REGISTER'}

    alvo: bpy.props.EnumProperty(
        name="Alvo",
        items=[('COTAS', "Cotas", "Mostra as cotas das vistas"),
               ('PORTAS', "Portas", "Mostra as portas no preview")],
        default='COTAS')  # type: ignore

    def execute(self, context):
        s = win_mod.sessao()
        if s is None:
            return {'CANCELLED'}
        if self.alvo == 'COTAS':
            s.mostrar_cotas = not s.mostrar_cotas
        else:
            s.mostrar_portas = not s.mostrar_portas
        _janela, area, _region = win_mod._area_da_sessao()
        if area is not None:
            area.tag_redraw()
        return {'FINISHED'}


class BTM_OT_ArmarioV2WindowVista(_WindowOperator, bpy.types.Operator):
    """Troca o preview entre dividido, frontal e corte lateral (toolbar do mockup)"""
    bl_idname = "caffmob.armario_v2_window_vista"
    bl_label = "Vista do preview"

    vista: bpy.props.EnumProperty(
        name="Vista",
        items=[('SPLIT', "Dividida", "Frontal e corte lateral"), ('FRONTAL', "Frontal", "Só a elevação"),
               ('LATERAL', "Lateral", "Só o corte lateral")],
        default='SPLIT')  # type: ignore

    def execute(self, context):
        s = win_mod.sessao()
        if s is None:
            return {'CANCELLED'}
        s.vista = parity_core.vista_valida(self.vista)
        _janela, area, _region = win_mod._area_da_sessao()
        if area is not None:
            area.tag_redraw()
        return {'FINISHED'}


class BTM_OT_ArmarioV2WindowTema(_WindowOperator, bpy.types.Operator):
    """Alterna o tema do preview entre Light e Dark (o chrome nativo segue o tema do Blender)"""
    bl_idname = "caffmob.armario_v2_window_tema"
    bl_label = "Tema do preview"

    tema: bpy.props.EnumProperty(
        name="Tema", items=[('LIGHT', "Light", ""), ('DARK', "Dark", "")], default='LIGHT')  # type: ignore
    alternar: bpy.props.BoolProperty(name="Alternar", default=True)  # type: ignore

    def execute(self, context):
        s = win_mod.sessao()
        if s is None:
            return {'CANCELLED'}
        s.tema = parity_core.alternar_tema(s.tema) if self.alternar else parity_core.tema_valido(self.tema)
        win_mod.preview_mod.aplicar_tema(s.tema)
        _janela, area, _region = win_mod._area_da_sessao()
        if area is not None:
            area.tag_redraw()
        return {'FINISHED'}


class BTM_OT_ArmarioV2WindowApenasLaterais(_WindowOperator, bpy.types.Operator):
    """Liga só as duas laterais (e desliga base/fundo), opcionalmente gerando o armário"""
    bl_idname = "caffmob.armario_v2_window_apenas_laterais"
    bl_label = "Apenas Laterais"

    criar: bpy.props.BoolProperty(name="Criar caixa só com laterais", default=False)  # type: ignore

    def execute(self, context):
        s = win_mod.sessao()
        root = s.armario_root if s is not None else None
        if root is None:
            return {'CANCELLED'}
        armario = root.btm_armario
        if not self.criar:
            s.apenas_laterais = not s.apenas_laterais
            _janela, area, _region = win_mod._area_da_sessao()
            if area is not None:
                area.tag_redraw()
            return {'FINISHED'}
        s.apenas_laterais = True
        if self.criar:
            armario.lateral_esq_ativa = True
            armario.lateral_dir_ativa = True
            armario.base_inf_ativa = False
            armario.base_sup_ativa = False
            armario.fundo_ativo = False
            s.suja = True
            if armario.gerado:
                gerou, avisos = ops_v2.gerar_armario(root, context)
                self._avisar(avisos)
                if not gerou:
                    return {'CANCELLED'}
        _janela, area, _region = win_mod._area_da_sessao()
        if area is not None:
            area.tag_redraw()
        return {'FINISHED'}


class BTM_OT_ArmarioV2WindowAbrirTudo(_WindowOperator, bpy.types.Operator):
    """Abre todas as peças animáveis; se já estão abertas, fecha todas"""
    bl_idname = "caffmob.armario_v2_window_abrir_tudo"
    bl_label = "Abrir/Fechar tudo"

    def execute(self, context):
        s = win_mod.sessao()
        root = s.armario_root if s is not None else None
        if root is None:
            return {'CANCELLED'}
        alvos = [obj for obj in root.children if anim.animavel(obj)]
        if not alvos:
            self.report({'INFO'}, tr("Nenhuma peça animável"))
            return {'CANCELLED'}
        alvo = not all(anim.estado(obj) for obj in alvos)
        for obj in alvos:
            if anim.estado(obj) != alvo:
                anim.alternar(obj)
        s.suja = True
        _janela, area, _region = win_mod._area_da_sessao()
        if area is not None:
            area.tag_redraw()
        return {'FINISHED'}


class BTM_OT_ArmarioV2WindowPainel(_WindowOperator, bpy.types.Operator):
    """Mostra/oculta o painel lateral da janela (restaurável pela tecla N)"""
    bl_idname = "caffmob.armario_v2_window_painel"
    bl_label = "Painel lateral"

    def execute(self, context):
        area = context.area
        space = area.spaces.active if area is not None else None
        if space is None or not hasattr(space, 'show_region_ui'):
            return {'CANCELLED'}
        space.show_region_ui = not space.show_region_ui
        return {'FINISHED'}


class BTM_OT_ArmarioV2WindowMedida(_WindowOperator, bpy.types.Operator):
    """Popover de medida: altera largura/altura/profundidade do armário e regenera"""
    bl_idname = "caffmob.armario_v2_window_medida"
    bl_label = "Medida do armário"

    medida: bpy.props.FloatProperty(name="Medida (mm)", default=600.0, min=1.0, max=10000.0)  # type: ignore
    eixo: bpy.props.EnumProperty(
        name="Eixo", items=[('LARGURA', "Largura", ""), ('ALTURA', "Altura", ""),
                            ('PROFUNDIDADE', "Profundidade", "")], default='LARGURA')  # type: ignore

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, width=320)

    def draw(self, context):
        self.layout.prop(self, 'eixo')
        self.layout.prop(self, 'medida')

    def execute(self, context):
        s = win_mod.sessao()
        root = s.armario_root if s is not None else None
        if root is None:
            return {'CANCELLED'}
        armario = root.btm_armario
        campo = {'LARGURA': 'largura', 'ALTURA': 'altura', 'PROFUNDIDADE': 'profundidade'}[self.eixo]
        setattr(armario, campo, float(self.medida))
        s.suja = True
        if armario.gerado:
            gerou, avisos = ops_v2.gerar_armario(root, context)
            self._avisar(avisos)
            if not gerou:
                return {'CANCELLED'}
        _janela, area, _region = win_mod._area_da_sessao()
        if area is not None:
            area.tag_redraw()
        return {'FINISHED'}


class BTM_OT_ArmarioV2WindowDuplicar(_WindowOperator, bpy.types.Operator):
    """Duplica a(s) peça(s) selecionada(s) e grava a duplicata para sobreviver ao Gerar"""
    bl_idname = "caffmob.armario_v2_window_duplicar"
    bl_label = "Duplicar peça"

    def execute(self, context):
        s = win_mod.sessao()
        root = s.armario_root if s is not None else None
        if root is None:
            return {'CANCELLED'}
        alvos = win_mod.objetos_da_selecao(root, s)
        if not alvos:
            self.report({'WARNING'}, "Nenhuma peça selecionada")
            return {'CANCELLED'}
        for obj in alvos:
            copia = obj.copy()
            copia.data = obj.data.copy()
            obj.users_collection[0].objects.link(copia)
            copia.parent = root
            copia.name = obj.name + " (cópia)"
            copia.location.x += 0.02
            win_mod.registrar_duplicata(root, obj)
        s.suja = True
        bpy.ops.ed.undo_push(message="Armário: duplicar peça")
        _janela, area, _region = win_mod._area_da_sessao()
        if area is not None:
            area.tag_redraw()
        return {'FINISHED'}


class BTM_OT_ArmarioV2WindowExportJson(_WindowOperator, ExportHelper, bpy.types.Operator):
    """Exporta spec, peças e cutlist do armário para JSON"""
    bl_idname = "caffmob.armario_v2_window_export_json"
    bl_label = "Exportar armário em JSON"
    filename_ext = ".json"
    filter_glob: bpy.props.StringProperty(default="*.json", options={'HIDDEN'})  # type: ignore
    filepath: bpy.props.StringProperty(subtype='FILE_PATH')  # type: ignore

    def invoke(self, context, event):
        if not self.filepath:
            self.filepath = "armario.json"
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

    def execute(self, context):
        s = win_mod.sessao()
        root = s.armario_root if s is not None else None
        if root is None or not self.filepath:
            return {'CANCELLED'}
        spec, itens = validar.pecas_da_raiz(root)
        if spec is None:
            return {'CANCELLED'}
        with open(self.filepath, 'w', encoding='utf-8') as arquivo:
            json.dump(parity_core.payload(spec, itens), arquivo, ensure_ascii=False, indent=2)
        self.report({'INFO'}, tr("Armário exportado: {}").format(self.filepath))
        return {'FINISHED'}


class BTM_MT_ArmarioV2WindowContext(bpy.types.Menu):
    """Menu de contexto da janela 023 (botão direito sobre a peça)"""
    bl_idname = "BTM_MT_ArmarioV2WindowContext"
    bl_label = "Peça do armário"

    def draw(self, context):
        layout = self.layout
        layout.operator("caffmob.armario_v2_window_duplicar", text="Duplicar", icon="DUPLICATE")
        layout.operator("caffmob.armario_v2_window_medida", text="Medida do armário", icon="DRIVER_DISTANCE")
        layout.separator()
        layout.operator("caffmob.armario_v2_window_lote", text="Espelhar", icon="MOD_MIRROR").acao = 'ESPELHAR'
        layout.operator("caffmob.armario_v2_window_lote", text="Apagar", icon="TRASH").acao = 'APAGAR'


class BTM_OT_ArmarioV2WindowAplicar(_WindowOperator, bpy.types.Operator):
    """Grava um passo de desfazer e fixa o estado atual como ponto de retorno, sem fechar"""
    bl_idname = "caffmob.armario_v2_window_aplicar"
    bl_label = "Aplicar"

    def execute(self, context):
        s = win_mod.sessao()
        root = s.armario_root if s is not None else None
        if root is None:
            return {'CANCELLED'}
        if self._recusar_geometria(root):
            return {'CANCELLED'}
        bpy.ops.ed.undo_push(message="Armário: Aplicar")
        root.btm_armario.snapshot = ops_v2.snapshot_de(root)
        s.snapshot = root.btm_armario.snapshot
        s.suja = False
        win_mod.gravar_memoria(context.scene, s)
        self.report({'INFO'}, "Estado aplicado: este vira o ponto de retorno do Cancelar")
        # Feature 025: a janela do construtor também pergunta onde adicionar; o popup abre na Vista 3D principal,
        # porque a janela 023 é um Image Editor e não tem o plano do piso para o mouse.
        try:
            from . import ops_placement
            ops_placement.abrir_prompt(context)
        except Exception as erro:
            self.report({'WARNING'}, tr("Não foi possível abrir o posicionamento: {}").format(erro))
        return {'FINISHED'}


class BTM_OT_ArmarioV2WindowCancelar(_WindowOperator, bpy.types.Operator):
    """Restaura o estado da abertura e fecha a janela"""
    bl_idname = "caffmob.armario_v2_window_cancelar"
    bl_label = "Cancelar"

    def execute(self, context):
        s = win_mod.sessao()
        root = s.armario_root if s is not None else None
        if root is None or not s.snapshot:
            self.report({'WARNING'}, "Sem estado guardado: nada para cancelar")
            return {'CANCELLED'}
        try:
            ops_v2.aplicar_snapshot(root, s.snapshot)
        except ValueError as erro:
            self.report({'WARNING'}, str(erro))
            return {'CANCELLED'}
        if root.btm_armario.gerado:
            gerou, avisos = ops_v2.gerar_armario(root, context)
            self._avisar(avisos)
            if not gerou:
                return {'CANCELLED'}
        else:
            build.limpar(root)
        s.suja = False
        self.report({'INFO'}, "Alterações descartadas: armário voltou ao estado da abertura")
        win_mod.close_window(s)
        win_mod.encerrar_sessao()
        return {'FINISHED'}


class BTM_OT_ArmarioV2WindowOK(_WindowOperator, bpy.types.Operator):
    """Confirma: grava um passo de desfazer e fecha a janela"""
    bl_idname = "caffmob.armario_v2_window_ok"
    bl_label = "OK"

    def execute(self, context):
        s = win_mod.sessao()
        root = s.armario_root if s is not None else None
        if root is None:
            return {'CANCELLED'}
        if self._recusar_geometria(root):
            return {'CANCELLED'}
        bpy.ops.ed.undo_push(message="Armário: OK")
        root.btm_armario.snapshot = ops_v2.snapshot_de(root)
        root.btm_armario.gerado = True
        s.suja = False
        win_mod.gravar_memoria(context.scene, s)
        self.report({'INFO'}, "Armário atualizado")
        win_mod.close_window(s)
        win_mod.encerrar_sessao()
        return {'FINISHED'}


classes = (
    BTM_OT_ArmarioV2WindowOpen,
    BTM_OT_ArmarioV2WindowModal,
    BTM_OT_ArmarioV2WindowAba,
    BTM_OT_ArmarioV2WindowSelecionar,
    BTM_OT_ArmarioV2WindowLote,
    BTM_OT_ArmarioV2WindowLimparAjustes,
    BTM_OT_ArmarioV2WindowPedido,
    BTM_OT_ArmarioV2WindowToggle,
    BTM_OT_ArmarioV2WindowVista,
    BTM_OT_ArmarioV2WindowTema,
    BTM_OT_ArmarioV2WindowApenasLaterais,
    BTM_OT_ArmarioV2WindowAbrirTudo,
    BTM_OT_ArmarioV2WindowPainel,
    BTM_OT_ArmarioV2WindowMedida,
    BTM_OT_ArmarioV2WindowDuplicar,
    BTM_OT_ArmarioV2WindowExportJson,
    BTM_MT_ArmarioV2WindowContext,
    BTM_OT_ArmarioV2WindowAplicar,
    BTM_OT_ArmarioV2WindowCancelar,
    BTM_OT_ArmarioV2WindowOK,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        if cls.is_registered:
            bpy.utils.unregister_class(cls)
