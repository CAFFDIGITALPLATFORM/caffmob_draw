"""Janela própria do construtor de armário v2 (feature 023, T001/T005/T019/T021; RN-01, RN-02, RN-06, RN-07, D-01).

Abre uma **nova janela do sistema** pelo mesmo caminho do Editor de Paredes (`canvas2d.window.open_window`: duplica a
área 3D com `screen.area_dupli` e troca o tipo da nova área para Image Editor sem imagem), e não converte a Vista 3D
do usuário.

A sessão guarda ponteiros, o instantâneo do armário para o Cancelar, o desenho do preview dividido (frontal + corte
lateral) e o estado de interface da janela: os hits do último desenho, a **seleção** (uma ou várias peças), a aba ativa
e as opções Cotas / Mostrar Portas.

Desde a Fase 7:

- os botões do painel **enfileiram** pedidos (`enfileirar`); o modal executa a fila e é quem escreve na cena (RN-02);
- o clique com Shift/Ctrl acumula peças e as ações em lote (mover, espelhar, apagar) valem para o conjunto (RN-06);
- a aba e o tamanho da janela ficam gravados **por cena**; ao abrir, a aba volta, e o tamanho é registrado para
  inspeção, porque o Blender expõe `Window.width/height` só como leitura (RN-07).
"""

import bpy  # type: ignore

from ..canvas2d import window as canvas_window
from . import fila as fila_mod
from . import preview as preview_mod
from . import selecao

MEMORIA_CHAVE = "caffmob_armario_v2_janela"
ABAS = ('ESTRUTURA', 'DIVISOES', 'GAVETAS', 'INTERNOS', 'PORTAS', 'DESLIZANTES', 'FUNDOS')
ABA_PADRAO = 'ESTRUTURA'
DELTA_LOTE = 10.0           # mm por toque nas ações de mover


class JanelaSessao:
    """Estado da janela própria do construtor."""

    def __init__(self):
        self.window_ptr = 0
        self.area_ptr = 0
        self.region_ptr = 0
        self.restore_area_type = None
        self.armario_root = None
        self.snapshot = None
        self.aberto = False
        self.suja = False
        self.draw_handler = None
        self.fila = []
        self.hits = []              # retângulos das peças desenhados no preview, em pixels da região
        self.selecionado = None     # último item escolhido (compatibilidade com a barra de uma peça)
        self.selecionados = []      # itens escolhidos, na ordem do clique (RN-06)
        self.aba = ABA_PADRAO       # aba ativa da janela (persistida por cena, RN-07)
        self.mostrar_cotas = True
        self.mostrar_portas = True


_sessao = [None]


def sessao():
    """Devolve a sessão ativa, ou None."""
    return _sessao[0]


def iniciar_sessao(s=None):
    """Define a sessão ativa. Se `s` for fornecido, usa esse objeto; caso contrário, cria um novo."""
    if s is not None:
        _sessao[0] = s
    else:
        _sessao[0] = JanelaSessao()


def encerrar_sessao():
    _sessao[0] = None


def janela_existe():
    """True quando uma janela própria do construtor está aberta."""
    s = _sessao[0]
    return s is not None and s.area_ptr != 0


def _area_da_sessao():
    """(janela, área, região) da sessão, ou (None, None, None)."""
    return canvas_window.editor_area(bpy.context, _sessao[0])


def _desenhar_preview():
    """Callback do draw handler: desenha o preview quando a área existe."""
    s = _sessao[0]
    if s is None or s.area_ptr == 0:
        return
    _janela, area, region = _area_da_sessao()
    if area is None or region is None:
        return
    preview_mod.desenhar_preview(region, s.armario_root, area, s)


def open_editor(context, s):
    """Abre a janela própria do construtor. Devolve (janela, área, região) ou levanta RuntimeError."""
    alvo = "O Construtor de Armários precisa de uma janela do Blender aberta."
    janela, area, region = canvas_window.open_window(context, s, alvo)
    space = area.spaces.active
    try:
        s.draw_handler = space.draw_handler_add(_desenhar_preview, (), 'WINDOW', 'POST_PIXEL')
    except (RuntimeError, AttributeError):
        s.draw_handler = None
    aplicar_memoria(context.scene, s)
    focar_categoria(context, s)
    gravar_memoria(context.scene, s, janela)
    return janela, area, region


def focar_categoria(context, s):
    """Põe a região lateral na aba do construtor; só funciona depois do primeiro desenho (por isso o retry no timer)."""
    from . import panel_window

    _janela, area, _region = canvas_window.editor_area(context, s)
    if area is None:
        return False
    return canvas_window.focus_tab(area, panel_window.CATEGORIA)


# Memória por cena (RN-07, T021) -----------------------------------------------------------------------------------

def _memoria(scene):
    """Dicionário gravado na cena (ou vazio); só aceita os campos conhecidos."""
    dados = scene.get(MEMORIA_CHAVE) if scene is not None else None
    if dados is None:
        return {}
    try:                                     # o IDProperty da cena não é `dict`, mas tem as mesmas chaves
        return {chave: dados[chave] for chave in dados.keys()}
    except (AttributeError, TypeError, KeyError):
        return {}


def ler_memoria(scene):
    """{'aba', 'largura', 'altura'} gravados na cena; campos ausentes não aparecem."""
    dados = _memoria(scene)
    memoria = {}
    if dados.get('aba') in ABAS:
        memoria['aba'] = dados['aba']
    for campo in ('largura', 'altura'):
        valor = dados.get(campo)
        if isinstance(valor, int) and valor > 0:
            memoria[campo] = valor
    return memoria


def gravar_memoria(scene, s, janela=None):
    """Grava a aba ativa e, quando há janela, o tamanho atual — por cena."""
    if scene is None or s is None:
        return {}
    dados = {'aba': s.aba if s.aba in ABAS else ABA_PADRAO}
    janela = janela if janela is not None else _janela_da_area(s)
    if janela is not None:
        try:
            dados['largura'] = int(janela.width)
            dados['altura'] = int(janela.height)
        except (AttributeError, TypeError, ValueError):
            pass
    scene[MEMORIA_CHAVE] = dados
    return dados


def _janela_da_area(s):
    janela, _area, _region = canvas_window.editor_area(bpy.context, s)
    return janela


def aplicar_memoria(scene, s):
    """Devolve a aba gravada na cena (Estrutura quando não há histórico)."""
    if s is None:
        return ABA_PADRAO
    s.aba = ler_memoria(scene).get('aba', ABA_PADRAO)
    return s.aba


def definir_aba(context, s, aba):
    """Troca a aba ativa, redesenha e grava a escolha na cena."""
    if s is None or aba not in ABAS:
        return False
    s.aba = aba
    gravar_memoria(context.scene, s)
    _janela, area, _region = _area_da_sessao()
    if area is not None:
        area.tag_redraw()
    return True


# Seleção (RN-06, T020) ---------------------------------------------------------------------------------------------

def selecionar_no_ponto(context, s, mouse_x, mouse_y, acumular=False):
    """Atualiza a seleção com o clique; devolve o item escolhido ou None (fora do desenho / sobre o painel)."""
    _janela, area, region = canvas_window.editor_area(context, s)
    if area is None or region is None:
        return None
    if not (region.x <= mouse_x < region.x + region.width and region.y <= mouse_y < region.y + region.height):
        return None
    if canvas_window.over_side_panel(area, mouse_x, mouse_y):
        return None
    itens = selecao.aplicar_clique(s.hits, mouse_x - region.x, mouse_y - region.y, s.selecionados,
                                   acumular=acumular)
    s.selecionados = itens
    s.selecionado = itens[-1] if itens else None
    area.tag_redraw()
    return s.selecionado


def definir_selecao(s, itens):
    """Define a seleção direto pelos itens (usado pelos testes e pelo operador de seleção)."""
    s.selecionados = [item for item in itens or () if item]
    s.selecionado = s.selecionados[-1] if s.selecionados else None
    return s.selecionados


def objetos_da_selecao(root, s):
    """Objetos das peças geradas cujo nome está na seleção (o preview usa os mesmos nomes)."""
    if root is None or s is None:
        return []
    nomes = {item.get('nome') for item in s.selecionados if item.get('nome')}
    return [filho for filho in root.children
            if getattr(filho, 'btm_armario_parte', None) is not None and filho.name in nomes]


def _ajuste_de(root, obj):
    """Ajuste gravado no armário para a peça, criando-o na primeira edição (chave uid + papel + nome)."""
    armario = getattr(root, 'btm_armario', None)
    if armario is None:
        return None
    parte = obj.btm_armario_parte
    for ajuste in armario.ajustes:
        if ajuste.uid == parte.uid and ajuste.papel == parte.papel and ajuste.nome == obj.name:
            return ajuste
    ajuste = armario.ajustes.add()
    ajuste.uid, ajuste.nome, ajuste.papel = parte.uid, obj.name, parte.papel
    return ajuste


def aplicar_lote(root, s, acao, delta=DELTA_LOTE):
    """Aplica mover / espelhar / apagar à seleção e devolve quantas peças mudaram (RN-06).

    Mover desloca em X/Z, espelhar inverte o eixo X no lugar e apagar remove o objeto. Cada alteração fica gravada
    em `Armário v2.ajustes`, então o **Gerar** recria as peças e reaplica o ajuste (T020); Cancelar restaura o
    instantâneo com a coleção de ajustes junto.
    """
    alvos = objetos_da_selecao(root, s)
    if not alvos:
        raise ValueError("Nenhuma peça selecionada")
    if acao in ('MOVER_ESQ', 'MOVER_DIR', 'MOVER_CIMA', 'MOVER_BAIXO'):
        sinal = -1.0 if acao in ('MOVER_ESQ', 'MOVER_BAIXO') else 1.0
        eixo = 2 if acao in ('MOVER_CIMA', 'MOVER_BAIXO') else 0
        campo = 'dz' if eixo == 2 else 'dx'
        for obj in alvos:
            passo = sinal * abs(delta)
            obj.location[eixo] += passo
            ajuste = _ajuste_de(root, obj)
            if ajuste is not None:
                ajuste.removida = False
                setattr(ajuste, campo, getattr(ajuste, campo) + passo)
    elif acao == 'ESPELHAR':
        # Reflexo em torno do centro do módulo (x = 0), não do pivô do objeto: peças fora do centro (portas,
        # ferragens com deslocamento) precisam trocar de lado, e isso é loc.x = −loc.x com scale.x = −scale.x.
        for obj in alvos:
            obj.location.x = -obj.location.x
            obj.scale.x *= -1.0
            ajuste = _ajuste_de(root, obj)
            if ajuste is not None:
                ajuste.espelho_x = obj.scale.x < 0.0
    elif acao == 'APAGAR':
        for obj in alvos:
            ajuste = _ajuste_de(root, obj)
            if ajuste is not None:
                ajuste.removida = True
            bpy.data.objects.remove(obj, do_unlink=True)
        s.selecionados = []
        s.selecionado = None
    else:
        raise ValueError(f"Ação em lote desconhecida: {acao}")
    s.suja = True
    return len(alvos)


# Fila de pedidos (RN-02, T019) -------------------------------------------------------------------------------------

def enfileirar(s, acao):
    """Acrescenta uma ação (callable ou (idname, kwargs)) à fila da sessão."""
    if s is not None:
        fila_mod.enfileirar(s.fila, acao)
        s.suja = True
    return acao


def _executar_pedido(acao):
    """Executa um pedido da fila: callable direto ou operador `grupo.nome` do `bpy.ops`."""
    if callable(acao):
        return acao()
    idname, kwargs = acao
    grupo, nome = idname.split('.', 1)
    return getattr(getattr(bpy.ops, grupo), nome)(**(kwargs or {}))


def processar_fila(s, executar=None):
    """Executa as ações enfileiradas e devolve a lista de avisos."""
    if s is None:
        return []
    return fila_mod.processar(s.fila, executar or _executar_pedido)


def close_window(s):
    """Fecha a janela própria e restaura o tipo da área (via timer, fora do modal)."""
    if s is None or s.area_ptr == 0:
        return
    if s.draw_handler is not None:
        try:
            for window in bpy.context.window_manager.windows:
                for area in window.screen.areas:
                    if area.as_pointer() == s.area_ptr:
                        space = area.spaces.active
                        space.draw_handler_remove(s.draw_handler, 'WINDOW')
                        break
        except (RuntimeError, AttributeError):
            pass
        s.draw_handler = None
    canvas_window.close_later(s.window_ptr, s.area_ptr, s.restore_area_type)


def janela_ativa(context, s):
    """A área do editor ainda existe (o usuário pode ter fechado a janela do sistema)."""
    return canvas_window.window_alive(context, s)


def register():
    """Nenhuma classe para registrar; mantido para compatibilidade com _MODULES."""
    pass


def unregister():
    """Nenhuma classe para desregistrar; mantido para compatibilidade com _MODULES."""
    pass
