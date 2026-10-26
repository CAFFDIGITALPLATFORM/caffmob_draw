"""Operadores da importação do `.promob` (071 D-12 a D-17): importar, escolher o ambiente e salvar como `.blend`."""
import hashlib
import os
import traceback

import bpy
from bpy_extras.io_utils import ExportHelper, ImportHelper  # type: ignore

from ..data.i18n import tr
from . import complemento, leitor, para_v2

_PENDENTE = {}
_AMBIENTES = {}      # caminho → itens do enum (o Blender exige manter as strings vivas)


def _ambientes(caminho):
    if caminho not in _AMBIENTES:
        pacote = leitor.abrir(caminho)
        lista = pacote.ambientes()
        _AMBIENTES.clear()
        _AMBIENTES[caminho] = (pacote, [(str(a.indice), f'{a.nome} ({a.contagem} itens)', '') for a in lista],
                               str(pacote.maior_ambiente()))
    return _AMBIENTES[caminho]


def _relatorio(rel):
    linhas = [tr("{} paredes, {} aberturas, {} móveis em caixas, {} lajes, {} malhas").format(
        rel['paredes'], rel['aberturas'], rel['caixas'], rel['lajes'], rel['malhas'])]
    caixas = [i for i in rel['ignorados'] if 'caixa' in i['motivo']]
    if caixas:
        linhas.append(tr("{} itens entraram como caixa: {}").format(len(caixas), caixas[0]['motivo']))
    fora = [i for i in rel['ignorados'] if 'caixa' not in i['motivo']]
    if fora:
        linhas.append(tr("{} itens ficaram fora (forro, luz ou sem medida)").format(len(fora)))
    linhas.extend(rel['avisos'][:3])
    return linhas


def _popup(titulo, linhas, icone='INFO'):
    def desenhar(menu, _context):
        for linha in linhas:
            menu.layout.label(text=linha)
    wm = bpy.context.window_manager
    janela = bpy.context.window or (wm.windows[0] if wm.windows else None)
    if bpy.app.background or janela is None:      # sem janela, o popup derruba o Blender
        print(titulo, *linhas, sep='\n')
        return
    with bpy.context.temp_override(window=janela):
        wm.popup_menu(desenhar, title=titulo, icon=icone)


def _montar():
    pendente = dict(_PENDENTE)
    _PENDENTE.clear()
    if not pendente:
        return None
    context = bpy.context
    try:
        from ..mobi.cena_v2 import construir_cena
        conversao = pendente['conversao']
        construir_cena(context, conversao['documento'])
        complemento.montar(context, pendente['pacote'], conversao)
        complemento.registrar(context, pendente['caminho'], pendente['sha256'], conversao)
        for janela in context.window_manager.windows:
            for area in janela.screen.areas:
                if area.type == 'VIEW_3D':
                    regiao = next((r for r in area.regions if r.type == 'WINDOW'), None)
                    if regiao is not None:
                        with context.temp_override(window=janela, area=area, region=regiao):
                            bpy.ops.view3d.view_all()
        bpy.ops.ed.undo_push(message=tr("Importar projeto do Promob"))
        _popup(tr("Projeto do Promob importado"), _relatorio(conversao['relatorio']))
    except Exception as exc:
        traceback.print_exc()
        _popup(tr("Falha ao montar o projeto do Promob"), [str(exc)[:200]], 'ERROR')
    return None


def importar(caminho, indice):
    """Lê e converte (puro), abre um arquivo novo e monta no timer (D-12). Devolve a mensagem de erro ou None."""
    try:
        pacote = _ambientes(caminho)[0]
        conversao = para_v2.converter(pacote.projeto(indice))
    except leitor.PromobErro as exc:
        return str(exc)
    if conversao['erros']:
        # As paredes não passaram nas regras do editor: o projeto entra sem elas, e o relatório avisa.
        documento = conversao['documento']
        documento['paredes'], documento['aberturas'], documento['materiais'] = [], [], []
        conversao['relatorio']['paredes'] = conversao['relatorio']['aberturas'] = 0
        conversao['relatorio']['avisos'].insert(0, tr("As paredes não passaram nas regras do editor e ficaram fora"))
    with open(caminho, 'rb') as f:
        sha256 = hashlib.sha256(f.read()).hexdigest()
    _PENDENTE.update(pacote=pacote, conversao=conversao, caminho=caminho, sha256=sha256)
    _AMBIENTES.clear()
    bpy.ops.wm.read_homefile(use_empty=True)
    bpy.app.timers.register(_montar, first_interval=0.0)
    return None


def _itens_do_ambiente(self, _context):
    try:
        return _ambientes(self.filepath)[1]
    except leitor.PromobErro:
        return [('0', tr("Ambiente"), '')]


class CAFFMOB_OT_promob_importar(bpy.types.Operator, ImportHelper):
    """Abre um projeto do Promob (.promob) num arquivo novo, com paredes, portas, janelas e móveis"""
    bl_idname = 'caffmob.promob_importar'
    bl_label = "Importar projeto do Promob"
    bl_options = {'REGISTER'}

    filename_ext = '.promob'
    filter_glob: bpy.props.StringProperty(default='*.promob', options={'HIDDEN'})  # type: ignore
    filepath: bpy.props.StringProperty(subtype='FILE_PATH', options={'SKIP_SAVE'})  # type: ignore

    def invoke(self, context, event):
        if self.filepath:                         # arrastado para a janela (FileHandler)
            return self.execute(context)
        return ImportHelper.invoke(self, context, event)

    def execute(self, context):
        try:
            _pacote, itens, _maior = _ambientes(self.filepath)
        except (leitor.PromobErro, OSError) as exc:
            self.report({'ERROR'}, str(exc))
            return {'CANCELLED'}
        if len(itens) > 1 or bpy.data.is_dirty:
            bpy.ops.caffmob.promob_confirmar('INVOKE_DEFAULT', filepath=self.filepath)
            return {'FINISHED'}
        erro = importar(self.filepath, None)
        if erro:
            self.report({'ERROR'}, erro)
            return {'CANCELLED'}
        return {'FINISHED'}


class CAFFMOB_OT_promob_confirmar(bpy.types.Operator):
    """Escolhe o ambiente do projeto do Promob e confirma o fechamento do arquivo atual"""
    bl_idname = 'caffmob.promob_confirmar'
    bl_label = "Importar projeto do Promob"
    bl_options = {'INTERNAL'}

    filepath: bpy.props.StringProperty(options={'HIDDEN', 'SKIP_SAVE'})  # type: ignore
    ambiente: bpy.props.EnumProperty(name="Ambiente", items=_itens_do_ambiente)  # type: ignore

    def invoke(self, context, event):
        try:
            self.ambiente = _ambientes(self.filepath)[2]
        except leitor.PromobErro as exc:
            self.report({'ERROR'}, str(exc))
            return {'CANCELLED'}
        return context.window_manager.invoke_props_dialog(self, width=460)

    def draw(self, context):
        layout = self.layout
        if len(_itens_do_ambiente(self, context)) > 1:
            layout.prop(self, 'ambiente')
        if bpy.data.is_dirty:
            layout.label(text=tr("O arquivo atual tem alterações não salvas, que serão descartadas."), icon='ERROR')
        layout.label(text=tr("O projeto abre num arquivo novo do Blender."))

    def execute(self, context):
        erro = importar(self.filepath, int(self.ambiente))
        if erro:
            self.report({'ERROR'}, erro)
            return {'CANCELLED'}
        return {'FINISHED'}


class CAFFMOB_OT_promob_salvar_blend(bpy.types.Operator, ExportHelper):
    """Salva o projeto importado do Promob como arquivo do Blender, com as texturas embutidas"""
    bl_idname = 'caffmob.promob_salvar_blend'
    bl_label = "Salvar como .blend"

    filename_ext = '.blend'
    filter_glob: bpy.props.StringProperty(default='*.blend', options={'HIDDEN'})  # type: ignore

    @classmethod
    def poll(cls, context):
        return complemento.lido(context) is not None

    def invoke(self, context, event):
        dados = complemento.lido(context) or {}
        nome = os.path.splitext(dados.get('arquivo') or 'projeto')[0] + '.blend'
        self.filepath = os.path.join(dados.get('pasta') or os.path.expanduser('~'), nome)
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

    def execute(self, context):
        try:
            bpy.ops.file.pack_all()
            bpy.ops.wm.save_as_mainfile(filepath=self.filepath, check_existing=False)
        except RuntimeError as exc:
            self.report({'ERROR'}, str(exc))
            return {'CANCELLED'}
        self.report({'INFO'}, tr("Projeto salvo em {}").format(self.filepath))
        return {'FINISHED'}


class CAFFMOB_FH_promob(bpy.types.FileHandler):
    bl_idname = 'CAFFMOB_FH_promob'
    bl_label = "Projeto do Promob"
    bl_import_operator = 'caffmob.promob_importar'
    bl_file_extensions = '.promob'

    @classmethod
    def poll_drop(cls, context):
        return context.area is not None and context.area.type == 'VIEW_3D'


def menu_importar(self, _context):
    self.layout.operator(CAFFMOB_OT_promob_importar.bl_idname, text=tr("Projeto do Promob (.promob)"))


classes = (CAFFMOB_OT_promob_importar, CAFFMOB_OT_promob_confirmar, CAFFMOB_OT_promob_salvar_blend, CAFFMOB_FH_promob)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.TOPBAR_MT_file_import.append(menu_importar)


def unregister():
    bpy.types.TOPBAR_MT_file_import.remove(menu_importar)
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
