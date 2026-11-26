"""Operadores do posicionamento do armário v2 depois do Aplicar (feature 025).

O fluxo tem três operadores:

- `caffmob.armario_v2_place_prompt` é o aviso: um popup com **Escolher na viewport** e **Cursor 3D**. Ele não escreve
  na cena; só encaminha para um dos dois modos.
- `caffmob.armario_v2_place_cursor` coloca a raiz na posição do Cursor 3D, preservando a orientação do armário.
- `caffmob.armario_v2_place_choose` entra no modo de escolha: esconde o armário real, mostra a caixa de arame nas
  medidas do spec e deixa o mouse posicionar. As setas apontam para as quatro direções cardeais (cima 0°, direita 90°,
  baixo 180°, esquerda 270°), `R` gira de 90 em 90 graus, o clique confirma e Esc/botão direito cancelam restaurando
  a posição e a visibilidade anteriores.

Sem uma janela 3D (scripts e `--background`), o modo de escolha cai no Cursor 3D, que é o único caminho determinístico.
"""

import bpy  # type: ignore

from ..data.i18n import tr
from . import build
from . import ops as ops_v2
from . import placement


def _raiz(context):
    """Raiz v2 da seleção ativa ou a primeira da coleção do construtor."""
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


def _selecionar(context, root):
    for obj in list(context.selected_objects):
        obj.select_set(False)
    root.select_set(True)
    context.view_layer.objects.active = root


def _area_3d(context):
    """(área, região) de uma Vista 3D na janela atual ou em qualquer janela aberta."""
    area = getattr(context, 'area', None)
    if area is not None and area.type == 'VIEW_3D':
        regiao = next((r for r in area.regions if r.type == 'WINDOW'), None)
        if regiao is not None:
            return area, regiao
    janela = getattr(context, 'window', None)
    if janela is not None:
        for area in janela.screen.areas:
            if area.type == 'VIEW_3D':
                regiao = next((r for r in area.regions if r.type == 'WINDOW'), None)
                if regiao is not None:
                    return area, regiao
    for janela in context.window_manager.windows:
        for area in janela.screen.areas:
            if area.type == 'VIEW_3D':
                regiao = next((r for r in area.regions if r.type == 'WINDOW'), None)
                if regiao is not None:
                    return area, regiao
    return None, None


def abrir_prompt(context):
    """Agenda o aviso de posicionamento na Vista 3D; devolve False quando não há janela gráfica.

    O aviso é adiado para o próximo ciclo da interface: chamá-lo de dentro do `execute` do Aplicar fazia o popup
    nascer e morrer junto com o operador que o abriu. O timer guarda a janela/área/região e abre o popup com o
    contexto certo, sem prender o Aplicar.
    """
    if bpy.app.background:
        return False
    area, regiao = _area_3d(context)
    if area is None or regiao is None:
        return False
    janela = None
    for candidata in context.window_manager.windows:
        if any(candidata_area == area for candidata_area in candidata.screen.areas):
            janela = candidata
            break
    if janela is None:
        return False

    def _abrir():
        try:
            with bpy.context.temp_override(window=janela, area=area, region=regiao):
                bpy.ops.caffmob.armario_v2_place_prompt('INVOKE_DEFAULT')
        except (AttributeError, ReferenceError, RuntimeError):
            pass
        return None

    bpy.app.timers.register(_abrir, first_interval=0.05)
    return True


class BTM_OT_ArmarioV2PlacePrompt(bpy.types.Operator):
    """Pergunta onde adicionar o armário: escolher na viewport ou no Cursor 3D"""

    bl_idname = "caffmob.armario_v2_place_prompt"
    bl_label = "Onde adicionar o armário?"
    bl_options = {'REGISTER'}

    @classmethod
    def poll(cls, context):
        return _raiz(context) is not None and context.window is not None

    def invoke(self, context, event):
        return context.window_manager.invoke_popup(self, width=300)

    def draw(self, context):
        layout = self.layout
        layout.label(text=tr("Onde adicionar o armário?"), icon='QUESTION')
        layout.label(text=tr("O armário já está montado; escolha o ponto de entrada."))
        coluna = layout.column(align=True)
        coluna.scale_y = 1.4
        coluna.operator("caffmob.armario_v2_place_choose", text=tr("Escolher na viewport"),
                        icon='RESTRICT_SELECT_OFF')
        coluna.operator("caffmob.armario_v2_place_cursor", text=tr("Cursor 3D"), icon='PIVOT_CURSOR')


class BTM_OT_ArmarioV2PlaceCursor(bpy.types.Operator):
    """Coloca o armário na posição do Cursor 3D"""

    bl_idname = "caffmob.armario_v2_place_cursor"
    bl_label = "Posicionar no Cursor 3D"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        root = _raiz(context)
        if root is None:
            self.report({'WARNING'}, tr("Selecione o armário v2"))
            return {'CANCELLED'}
        placement.no_cursor(root, context.scene)
        bpy.ops.ed.undo_push(message=tr("Armário: posicionar no cursor 3D"))
        _selecionar(context, root)
        self.report({'INFO'}, tr("Armário posicionado no Cursor 3D"))
        return {'FINISHED'}


class BTM_OT_ArmarioV2PlaceChoose(bpy.types.Operator):
    """Escolhe a posição do armário com a caixa de arame acompanhando o mouse"""

    bl_idname = "caffmob.armario_v2_place_choose"
    bl_label = "Escolher posição do armário"
    bl_options = {'REGISTER', 'UNDO'}

    _root = None
    _cage = None
    _ocultos = None
    _original = None
    _area = None
    _region = None
    _rv3d = None

    @classmethod
    def poll(cls, context):
        return _raiz(context) is not None

    def invoke(self, context, event):
        area, regiao = _area_3d(context)
        if area is None or regiao is None:
            return self.execute(context)
        root = _raiz(context)
        if root is None:
            return {'CANCELLED'}
        self._root = root
        self._area, self._region = area, regiao
        self._rv3d = regiao.data
        self._original = (root.location.copy(), root.rotation_euler.copy())
        try:
            self._cage = placement.criar_cage(context, ops_v2.spec_do_armario(root))
        except Exception as erro:  # a prévia não pode impedir o Aplicar de terminar
            self.report({'ERROR'}, tr("Não foi possível criar a prévia: {}").format(erro))
            return {'CANCELLED'}
        self._cage.location = root.location.copy()
        self._cage.rotation_euler = root.rotation_euler.copy()
        self._ocultos = placement.esconder(root, True)
        self._area.header_text_set(
            tr("Mouse: posicionar · setas: orientar · clique: confirmar · Esc: cancelar"))
        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}

    def execute(self, context):
        """Sem interação (scripts e testes): posiciona no Cursor 3D."""
        root = _raiz(context)
        if root is None:
            return {'CANCELLED'}
        placement.no_cursor(root, context.scene)
        bpy.ops.ed.undo_push(message=tr("Armário: posicionar"))
        _selecionar(context, root)
        return {'FINISHED'}

    def _mover(self, context, event):
        if self._cage is None or self._region is None or self._rv3d is None:
            return
        ponto = placement.chao(self._region, self._rv3d, event.mouse_x - self._region.x,
                               event.mouse_y - self._region.y)
        if ponto is not None:
            self._cage.location = ponto

    def _limpar(self):
        if self._cage is not None:
            placement.remover(self._cage)
            self._cage = None
        if self._ocultos is not None:
            placement.restaurar(self._ocultos)
            self._ocultos = None
        if self._area is not None:
            try:
                self._area.header_text_set(None)
            except (AttributeError, ReferenceError):
                pass
        self._area = None
        self._region = None
        self._rv3d = None

    def _encerrar(self, context, confirmar):
        if confirmar and self._root is not None and self._cage is not None:
            self._root.location = self._cage.location.copy()
            self._root.rotation_euler = self._cage.rotation_euler.copy()
            _selecionar(context, self._root)
        elif not confirmar and self._root is not None and self._original is not None:
            self._root.location, self._root.rotation_euler = self._original
        self._limpar()
        if confirmar:
            bpy.ops.ed.undo_push(message=tr("Armário: posicionar"))
            self.report({'INFO'}, tr("Armário posicionado"))

    def modal(self, context, event):
        if self._root is None or self._cage is None:
            self._limpar()
            return {'CANCELLED'}
        if event.type == 'INBETWEEN_MOUSEMOVE':
            return {'RUNNING_MODAL'}
        if event.type == 'MOUSEMOVE':
            self._mover(context, event)
            if self._area is not None:
                self._area.tag_redraw()
            return {'RUNNING_MODAL'}
        if event.type in placement.ORIENTACOES and event.value == 'PRESS':
            self._cage.rotation_euler.z = placement.seta_para_yaw(event.type)
            if self._area is not None:
                self._area.tag_redraw()
            return {'RUNNING_MODAL'}
        if event.type == 'R' and event.value == 'PRESS':
            self._cage.rotation_euler.z = placement.girar(self._cage.rotation_euler.z)
            return {'RUNNING_MODAL'}
        if event.type == 'LEFTMOUSE' and event.value == 'PRESS':
            self._encerrar(context, True)
            return {'FINISHED'}
        if event.type in {'ESC', 'RIGHTMOUSE'} and event.value == 'PRESS':
            self._encerrar(context, False)
            return {'CANCELLED'}
        return {'PASS_THROUGH'}


classes = (BTM_OT_ArmarioV2PlacePrompt, BTM_OT_ArmarioV2PlaceCursor, BTM_OT_ArmarioV2PlaceChoose)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        if cls.is_registered:
            bpy.utils.unregister_class(cls)
