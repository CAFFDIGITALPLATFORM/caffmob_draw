"""HUD do construtor de armário v2 na vista 3D (feature 017, T025; RN-22, RF-25).

O estado da montagem fica à mão, desenhado sobre a própria vista 3D num handler `POST_PIXEL`, sem janela separada (RN-22):

- **Alternadores da estrutura**: enquanto o armário está vazio — nenhuma das quatro chapas da caixa ligada (D-18) —,
  cinco botões no canto inferior esquerdo ligam e desligam lateral esquerda, lateral direita, base inferior, base
  superior e fundo. Os botões ficam acesos com a chapa ligada e o clique é entregue ao operador pela keymap da vista, com
  `hb_gpu_draw.point_in_rect`; clique fora dos botões passa direto para a cena (`PASS_THROUGH`), então seleção, box
  select e menu de contexto seguem funcionando. Com qualquer chapa da caixa ligada os alternadores saem de cena e quem
  manda é o painel.
- **Inspetor da peça escolhida**: o cartão acima dos alternadores mostra o nome da peça, comprimento × largura ×
  espessura em mm, o papel por extenso e, quando a peça passa da chapa do contrato, o aviso `Fora da chapa` em vermelho.
  As medidas vêm gravadas em `btm_armario_parte`, sem recalcular nada (RF-19).
- **Realce da seleção**: as doze arestas do volume da peça escolhida, projetadas para a tela com
  `view3d_utils.location_3d_to_region_2d`, em laranja. Só desenha quando os oito cantos projetam dentro da vista.

O desenho é leitura pura: nada no armário é escrito por desenhar, e o único caminho que muda a cena é o clique nos
alternadores, que passa por operador com `UNDO`. Os dois penduricalhos do módulo — o handler de desenho e o item de
keymap — são removidos no `unregister()`; nada sobra no Blender depois de desregistrar.
"""

import bpy  # type: ignore
from bpy_extras import view3d_utils  # type: ignore
from mathutils import Vector  # type: ignore

from .. import hb_gpu_draw
from ..canvas2d import draw
from ..data.i18n import tr
from . import conferencia
from . import ops
from . import panel

# Alternadores: campo do armário e rótulo (o texto do código é a chave do catálogo).
CAMPOS_DA_ESTRUTURA = (
    ('lateral_esq_ativa', "Lateral esquerda"),
    ('lateral_dir_ativa', "Lateral direita"),
    ('base_inf_ativa', "Base inferior"),
    ('base_sup_ativa', "Base superior"),
    ('fundo_ativo', "Fundo"),
)
# As quatro chapas que definem a caixa; o fundo é presença à parte.
CAMPOS_DA_CAIXA = CAMPOS_DA_ESTRUTURA[:4]

# Papel da peça por extenso no inspetor (os papéis de `build.pecas`, sem ferragem).
ROTULOS = {
    'LATERAL': "Lateral",
    'BASE_INF': "Base inferior",
    'BASE_SUP': "Base superior",
    'FUNDO': "Fundo",
    'DIVISORIA': "Divisória",
    'PRATELEIRA': "Prateleira",
    'FRENTE_GAVETA': "Frente da gaveta",
    'SEPARADOR': "Separador",
    'AFASTADOR': "Afastador",
    'FOLHA': "Folha",
    'PORTA': "Porta",
}

LARGURA = 240            # largura máxima do cartão e das duas colunas de botões, em pixels
MARGEM = 14              # afastamento do canto inferior esquerdo da vista
ESPACO = 4               # entre botões da mesma linha e entre linhas
PILHA = 10               # entre os alternadores e o cartão do inspetor
ALTURA_BOTAO = 22
ALTURA_LINHA = 15
ENCHIMENTO = 8
CORES_DAS_LINHAS = {'text': 'text', 'muted': 'muted', 'warning': 'warning'}

# Arestas do volume da peça, na ordem dos cantos de `Object.bound_box` (menor x, y, z primeiro).
ARESTAS = ((0, 1), (2, 3), (4, 5), (6, 7), (0, 2), (1, 3), (4, 6), (5, 7), (0, 4), (1, 5), (2, 6), (3, 7))

_handles = []       # handler de desenho em `SpaceView3D`
_keymaps = []       # [(keymap, item)] do clique nos alternadores


# Estado -----------------------------------------------------------------------------------------------------------
def _vazio(armario):
    """Armário vazio: nenhuma das quatro chapas da caixa ligada (RN-01)."""
    return not any(bool(getattr(armario, campo)) for campo, _rotulo in CAMPOS_DA_CAIXA)


def _peca(context):
    """Peça escolhida do armário v2: o critério de `panel.peca_da_selecao` (papel gravado e raiz v2 acima)."""
    return panel.peca_da_selecao(context)


def _em_vista(context):
    """O contexto é uma região de janela de uma vista 3D — o que o handler e o clique exigem."""
    espaco = getattr(context, 'space_data', None)
    regiao = getattr(context, 'region', None)
    return (getattr(espaco, 'type', None) == 'VIEW_3D' and getattr(regiao, 'type', None) == 'WINDOW')


# Layout (em pixels da região) --------------------------------------------------------------------------------------
def _coluna(largura_px):
    return min((largura_px - 2 * MARGEM - ESPACO) / 2.0, (LARGURA - ESPACO) / 2.0)


def botoes_da_estrutura(armario, largura_px):
    """[(campo, rótulo, (x, y, w, h))] dos alternadores, do canto inferior esquerdo para cima.

    Vazio com a caixa já montada: com qualquer chapa ligada, os alternadores saem de cena.
    """
    if not _vazio(armario):
        return []
    coluna = _coluna(largura_px)
    if coluna <= 0:
        return []
    saida = []
    for linha, inicio in enumerate(range(0, len(CAMPOS_DA_ESTRUTURA), 2)):
        for indice in range(2):
            posicao = inicio + indice
            if posicao >= len(CAMPOS_DA_ESTRUTURA):
                break
            campo, rotulo = CAMPOS_DA_ESTRUTURA[posicao]
            retangulo = (MARGEM + indice * (coluna + ESPACO), MARGEM + linha * (ALTURA_BOTAO + ESPACO),
                         coluna, ALTURA_BOTAO)
            saida.append((campo, rotulo, retangulo))
    return saida


def campo_no_ponto(armario, largura_px, x, y):
    """Campo do armário sob o ponto (x, y) da região, ou `None` fora dos botões."""
    for campo, _rotulo, retangulo in botoes_da_estrutura(armario, largura_px):
        if hb_gpu_draw.point_in_rect(x, y, retangulo):
            return campo
    return None


def linhas_do_inspetor(peca, contrato):
    """[(texto, tipo)] do cartão do inspetor: nome, medidas, papel e o aviso de chapa."""
    parte = getattr(peca, 'btm_armario_parte', None)
    if parte is None:
        return []
    linhas = [
        (peca.name, 'text'),
        (tr("{} × {} × {} mm").format(f"{parte.comprimento_mm:g}", f"{parte.largura_mm:g}",
                                      f"{parte.espessura_mm:g}"), 'muted'),
        (tr(ROTULOS.get(parte.papel, parte.papel)), 'text'),
    ]
    conferida = conferencia.Peca(parte.papel, peca.name, parte.comprimento_mm, parte.largura_mm, parte.espessura_mm)
    if conferencia.conferir([conferida], contrato):
        linhas.append((tr("Fora da chapa"), 'warning'))
    return linhas


def cartao_do_inspetor(peca, armario, largura_px, contrato):
    """(x, y, w, h) do cartão do inspetor acima dos alternadores, ou `None` sem peça escolhida."""
    if peca is None:
        return None
    linhas = linhas_do_inspetor(peca, contrato)
    if not linhas:
        return None
    botoes = botoes_da_estrutura(armario, largura_px)
    y = MARGEM + (max(retangulo[1] + retangulo[3] for _campo, _rotulo, retangulo in botoes) + PILHA
                  if botoes else 0)
    largura = min(LARGURA, largura_px - 2 * MARGEM)
    return (MARGEM, y, largura, len(linhas) * ALTURA_LINHA + 2 * ENCHIMENTO)


# Desenho ----------------------------------------------------------------------------------------------------------
def _botao(sh, retangulo, rotulo, ligado):
    draw.rect(sh, retangulo, draw.COLORS['button_primary'] if ligado else draw.COLORS['button'])
    draw.outline(sh, retangulo, draw.COLORS['border'])
    x = retangulo[0] + (retangulo[2] - draw.text_width(rotulo)) / 2.0
    draw.text(x, hb_gpu_draw.vcenter_baseline(retangulo, draw.FONT, draw.FONT_SIZE), rotulo)


def _cartao(sh, retangulo, linhas):
    draw.rect(sh, retangulo, draw.COLORS['panel'])
    draw.outline(sh, retangulo, draw.COLORS['border'])
    y = retangulo[1] + retangulo[3] - ENCHIMENTO - ALTURA_LINHA
    for texto, tipo in linhas:
        draw.text(retangulo[0] + ENCHIMENTO, y, texto, draw.COLORS[CORES_DAS_LINHAS.get(tipo, 'text')])
        y -= ALTURA_LINHA


def _pontos_da_peca(peca):
    """Cantos do volume da peça no mundo."""
    return [peca.matrix_world @ Vector(canto) for canto in peca.bound_box]


def _realce(sh, context, peca):
    regiao, dados = context.region, getattr(context, 'region_data', None)
    if dados is None:
        return
    pontos = [view3d_utils.location_3d_to_region_2d(regiao, dados, canto) for canto in _pontos_da_peca(peca)]
    if any(ponto is None for ponto in pontos):
        return                       # canto fora da vista: nada a realçar
    segmentos = []
    for inicio, fim in ARESTAS:
        segmentos += [(pontos[inicio][0], pontos[inicio][1]), (pontos[fim][0], pontos[fim][1])]
    draw.lines(sh, segmentos, draw.COLORS['moving'])


def desenhar_hud():
    """Corpo do handler: realce da seleção, alternadores e inspetor. Só lê a cena."""
    context = bpy.context
    if not _em_vista(context):
        return
    raiz = panel.raiz_da_cena(context)
    if raiz is None:
        return
    armario = raiz.btm_armario
    peca = _peca(context)
    contrato = ops.contrato_da_cena(context.scene)
    sh = draw.begin()
    try:
        if peca is not None:
            _realce(sh, context, peca)
        for campo, rotulo, retangulo in botoes_da_estrutura(armario, context.region.width):
            _botao(sh, retangulo, rotulo, getattr(armario, campo))
        cartao = cartao_do_inspetor(peca, armario, context.region.width, contrato)
        if cartao is not None:
            _cartao(sh, cartao, linhas_do_inspetor(peca, contrato))
    finally:
        draw.end()


def _desenhar():
    try:
        desenhar_hud()
    except (ReferenceError, RuntimeError):
        return                       # região saindo da tela ou objeto apagado no meio do desenho


# Clique nos alternadores ------------------------------------------------------------------------------------------
class BTM_OT_ArmarioV2HudAlternar(bpy.types.Operator):
    """Liga ou desliga a chapa da caixa apontada nos alternadores da vista 3D"""

    bl_idname = "caffmob.armario_v2_hud_alternar"
    bl_label = "Alternar chapa da caixa"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        if not _em_vista(context):
            return False
        raiz = panel.raiz_da_cena(context)
        return raiz is not None and _vazio(raiz.btm_armario)

    def invoke(self, context, event):
        raiz = panel.raiz_da_cena(context)
        if raiz is None:
            return {'PASS_THROUGH'}
        armario = raiz.btm_armario
        campo = campo_no_ponto(armario, context.region.width, event.mouse_region_x, event.mouse_region_y)
        if campo is None:
            return {'PASS_THROUGH'}  # clique fora dos alternadores segue para a cena
        setattr(armario, campo, not getattr(armario, campo))
        if context.area is not None:
            context.area.tag_redraw()
        return {'FINISHED'}

    def execute(self, context):
        return {'CANCELLED'}         # só faz sentido com o mouse: quem chama é a keymap da vista


classes = (BTM_OT_ArmarioV2HudAlternar,)


def _ligar():
    if _handles:
        return
    _handles.append(bpy.types.SpaceView3D.draw_handler_add(_desenhar, (), 'WINDOW', 'POST_PIXEL'))
    wm = getattr(bpy.context, 'window_manager', None)
    keyconfigs = getattr(wm, 'keyconfigs', None)
    kc = getattr(keyconfigs, 'addon', None)
    if kc is None:
        return                       # em segundo plano não há keymap: o desenho continua
    km = kc.keymaps.new(name='3D View', space_type='VIEW_3D')
    kmi = km.keymap_items.new(BTM_OT_ArmarioV2HudAlternar.bl_idname, 'LEFTMOUSE', 'PRESS', any=True, head=True)
    _keymaps.append((km, kmi))


def _desligar():
    for km, kmi in _keymaps:
        try:
            km.keymap_items.remove(kmi)
        except (ReferenceError, RuntimeError):
            pass
    _keymaps.clear()
    for handle in _handles:
        bpy.types.SpaceView3D.draw_handler_remove(handle, 'WINDOW')
    _handles.clear()


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    _ligar()


def unregister():
    _desligar()
    for cls in reversed(classes):
        if cls.is_registered:
            bpy.utils.unregister_class(cls)
