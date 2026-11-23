"""Abrir e fechar animados das gavetas, folhas deslizantes e portas (feature 017, T022; RN-10, D-08, RF-16).

Um alvo por vez, por timer de 16 ms e no máximo 18 quadros (`QUADROS`), como a D-08 fixa. O curso de cada peça já vem
gravado em `btm_armario_parte.curso_mm` e `eixo` por `build.pecas`, então a animação não recalcula medida nenhuma:

- gaveta (`eixo='Y'`) anda `72%` da profundidade para a frente, e as peças da corrediça (`PAPEIS_GAIOLA`) andam
  `50%` do curso da gaveta;
- folha deslizante (`eixo='X'`) corre `80%` da própria largura, com sentidos opostos entre folhas vizinhas;
- porta de abrir (`eixo='GIRO'`) gira `95°` em torno da dobradiça, no sentido do lado escolhido.

O estado fica gravado em `btm_armario.aberto` do armário (o `§2` do `data-delta` não tem estado por peça) e o rótulo
de menu é sempre o da ação oposta ao que a geometria mostra (`rotulo`). O "segundo toque" inverte a animação em curso
a partir do ponto onde ela está, sem deixar passo de desfazer: o passo é empurrado só quando a animação termina.

Cada alvo tem o seu timer guardado no dicionário de módulo `_handles`, removido em todos os caminhos de saída: fim da
animação, alvo apagado no meio do caminho, novo toque no mesmo alvo, `cancelar_tudo()` no `unregister()` e arquivo novo
(`load_post`, porque o timer não é persistente). A matriz de referência é a do estado **fechado**, refeita a cada toque
a partir da posição atual e do progresso `p`, então a animação não acumula erro ao inverter no meio.

Timer conforme o RAG do projeto (seção `bpy.app.timers`): a função devolve o intervalo até o próximo quadro e `None`
quando o timer deve sair.
"""

import math

import bpy  # type: ignore
from bpy.app.handlers import persistent  # type: ignore
from mathutils import Matrix, Vector  # type: ignore

from ..data.i18n import tr
from . import build
from . import portas as portas_mod

INTERVALO = 0.016        # segundos entre quadros (D-08)
QUADROS = 18             # quadros por alvo, no máximo (D-08)
CURSO_GAIOLA = 0.5       # a gaiola da corrediça anda metade do curso da gaveta (RN-10)

PAPEIS_ANIMAVEIS = ('FRENTE_GAVETA', 'SEPARADOR', 'AFASTADOR', 'FOLHA', 'PORTA')
PAPEIS_GAIOLA = ('GAIOLA', 'CORREDICA', 'TRILHO')
SEPARADOR_GAVETA = ' da gaveta '

# Timer em curso de cada alvo (nome do objeto) -> função registrada em `bpy.app.timers`.
_handles = {}
# Estado de cada animação em curso: passo, progresso, destino, raiz e as matrizes fechadas dos objetos.
_animacoes = {}


# Alvo ------------------------------------------------------------------------------------------------------------
def _raiz(obj):
    """Armário v2 dono do objeto: o vazio da coleção, subindo a hierarquia (`build.raiz_de`).

    Testar o grupo `btm_armario` não serve: ele existe em toda peça, e o estado ia para a própria frente da gaveta
    (a fumaça de T033 pegou o `aberto` gravado no lugar errado).
    """
    return build.raiz_de(obj)


def animavel(obj):
    """O objeto é uma peça que abre e fecha: gaveta, folha ou porta com curso gravado."""
    parte = getattr(obj, 'btm_armario_parte', None)
    if parte is None or parte.papel not in PAPEIS_ANIMAVEIS:
        return False
    return float(parte.curso_mm) > 0.0


def alvo_de(context):
    """Peça animável da seleção ativa, ou `None`."""
    obj = getattr(context, 'active_object', None)
    return obj if obj is not None and animavel(obj) else None


def _deslocado(obj):
    """A peça saiu do lugar: `build.gerar` nasce com a matriz identidade e só a animação a desloca ou gira."""
    local, rotacao, _escala = obj.matrix_world.decompose()
    return local.length > 1e-4 or abs(rotacao.angle) > 1e-4


def estado(obj):
    """`True` quando o alvo está aberto — pela animação em curso ou pela posição em que a peça está."""
    animacao = _animacoes.get(obj.name)
    if animacao is not None:
        return bool(animacao['abrir'])
    return _deslocado(obj)


def rotulo(obj):
    """Texto do menu: sempre a ação oposta ao estado atual (RN-10, RF-16)."""
    return tr("Fechar") if estado(obj) else tr("Abrir")


def _indice_entre_irmaos(obj, papel):
    """Posição do objeto entre as peças irmãs do mesmo papel, na ordem em que `build.gerar` as criou."""
    pai = obj.parent
    if pai is None:
        return 0
    irmaos = [filho for filho in pai.children
              if getattr(filho, 'btm_armario_parte', None) is not None
              and filho.btm_armario_parte.papel == papel]
    return irmaos.index(obj) if obj in irmaos else 0


def _sufixo_da_gaveta(obj):
    """Sufixo do nome que agrupa as peças da mesma gaveta (`" da gaveta 2"`), como `build` as nomeia."""
    if SEPARADOR_GAVETA not in obj.name:
        return None
    return SEPARADOR_GAVETA + obj.name.rsplit(SEPARADOR_GAVETA, 1)[1]


def _grupo(alvo):
    """O alvo e as peças que andam com ele: as da mesma gaveta e o conjunto pendurado embaixo dele.

    A corrediça 3D (T029) entra na animação como irmã da frente, com o nome marcado pelo mesmo sufixo de gaveta: assim
    ela anda `CURSO_GAIOLA` do curso no referencial do armário. Objeto filho da frente anda com ela, sem conta própria.
    """
    grupo = [alvo]
    if getattr(alvo, 'btm_armario_parte', None).papel not in ('FOLHA', 'PORTA'):
        sufixo = _sufixo_da_gaveta(alvo)
        if sufixo is not None and alvo.parent is not None:
            for irmao in alvo.parent.children:
                if irmao is alvo or getattr(irmao, 'btm_armario_parte', None) is None:
                    continue
                if _sufixo_da_gaveta(irmao) == sufixo:
                    grupo.append(irmao)
    grupo.extend(alvo.children)
    return tuple(grupo)


# Deslocamento de cada peça ----------------------------------------------------------------------------------------
def _limites(obj):
    """(x mínimo, x máximo, y mínimo) da peça em coordenadas de mundo, para achar a linha da dobradiça."""
    if obj.type != 'MESH':
        return None
    matriz = obj.matrix_world
    pontos = [matriz @ vertice.co for vertice in obj.data.vertices]
    if not pontos:
        return None
    return min(p.x for p in pontos), max(p.x for p in pontos), min(p.y for p in pontos)


def _lado_da_dobradica(obj, raiz):
    """Lado da dobradiça da folha de porta, conforme o armário (RN-10, alternada alterna por folha)."""
    escolha = raiz.btm_armario.porta_dobradica
    if escolha == portas_mod.ALTERNADA:
        return portas_mod.ESQUERDA if _indice_entre_irmaos(obj, 'PORTA') % 2 == 0 else portas_mod.DIREITA
    return escolha


def _deslocamento_de(obj, raiz):
    """Especificação do movimento do objeto do estado fechado para o aberto, ou `None` se ele não se mexe.

    ('mover', vetor) desloca em metros na direção do vetor; ('girar', pivô, ângulo) gira em torno da vertical no pivô.
    """
    parte = getattr(obj, 'btm_armario_parte', None)
    if parte is None or float(parte.curso_mm) <= 0.0:
        return None
    if parte.eixo == 'GIRO':
        limites = _limites(obj)
        if limites is None:
            return None
        x_min, x_max, y_min = limites
        esquerda = _lado_da_dobradica(obj, raiz) == portas_mod.ESQUERDA
        pivo = Vector((x_min if esquerda else x_max, y_min, 0.0))
        # Sentido da dobradiça igual ao de `portas.portas_de_abrir`: esquerda abre para −95°, direita para +95°.
        sentido = -1.0 if esquerda else 1.0
        return ('girar', pivo, sentido * math.radians(float(parte.curso_mm)))
    curso = float(parte.curso_mm) * build.MM
    if parte.papel in PAPEIS_GAIOLA:
        curso *= CURSO_GAIOLA
    if parte.eixo == 'Y':
        return ('mover', Vector((0.0, -curso, 0.0)))
    if parte.eixo == 'X':
        # Sentidos opostos entre folhas vizinhas, como em `portas.folhas_deslizantes` (índice par para a esquerda).
        sentido = -1.0 if _indice_entre_irmaos(obj, 'FOLHA') % 2 == 0 else 1.0
        return ('mover', Vector((sentido * curso, 0.0, 0.0)))
    return None


def _matriz(especificacao, progresso):
    """Matriz de mundo do movimento no progresso `progresso` (0 fechado, 1 aberto), com suavização nas pontas."""
    p = min(max(progresso, 0.0), 1.0)
    suave = p * p * (3.0 - 2.0 * p)
    if especificacao[0] == 'mover':
        return Matrix.Translation(especificacao[1] * suave)
    pivo, angulo = especificacao[1], especificacao[2]
    return (Matrix.Translation(pivo) @ Matrix.Rotation(angulo * suave, 4, 'Z')
            @ Matrix.Translation(-pivo))


def _progresso_atual(alvo):
    """Progresso da animação do alvo: o do timer em curso, ou 1/0 conforme a peça esteja aberta ou fechada."""
    animacao = _animacoes.get(alvo.name)
    if animacao is not None:
        return animacao['p']
    return 1.0 if _deslocado(alvo) else 0.0


# Timer -----------------------------------------------------------------------------------------------------------
def _descartar(nome):
    """Só esquece a animação — usado de dentro do quadro, quando quem para o timer é o próprio Blender."""
    _animacoes.pop(nome, None)
    _handles.pop(nome, None)


def cancelar(nome):
    """Para e esquece a animação do alvo, desregistrando o timer se ele ainda estiver de pé."""
    funcao = _handles.pop(nome, None)
    _animacoes.pop(nome, None)
    if funcao is not None and bpy.app.timers.is_registered(funcao):
        bpy.app.timers.unregister(funcao)


def cancelar_tudo():
    """Para todas as animações — no `unregister()` e ao carregar outro arquivo."""
    for nome in tuple(_handles):
        cancelar(nome)
    _animacoes.clear()


def _concluir(nome, raiz):
    """Fecha a animação: grava o estado no armário e empurra o único passo de desfazer do toque (RF-16)."""
    animacao = _animacoes.pop(nome, None)
    _handles.pop(nome, None)
    if animacao is None:
        return
    armario = getattr(raiz, 'btm_armario', None)
    if armario is not None:
        armario.aberto = bool(animacao['abrir'])
    bpy.ops.ed.undo_push(message=tr("Abrir") if animacao['abrir'] else tr("Fechar"))


def _quadro(nome):
    """Função do timer do alvo: aplica um quadro e devolve o intervalo até o próximo, ou `None` no fim."""

    def quadro():
        animacao = _animacoes.get(nome)
        if animacao is None:
            _descartar(nome)
            return None
        raiz = bpy.data.objects.get(animacao['raiz'])
        if raiz is None:
            _descartar(nome)
            return None
        animacao['passo'] += 1
        fracao = min(1.0, animacao['passo'] / QUADROS)
        progresso = animacao['p0'] + (animacao['destino'] - animacao['p0']) * fracao
        for nome_objeto, especificacao, fechada in animacao['objetos']:
            objeto = bpy.data.objects.get(nome_objeto)
            if objeto is None:
                _descartar(nome)
                return None
            objeto.matrix_world = _matriz(especificacao, progresso) @ fechada
        animacao['p'] = progresso
        if fracao >= 1.0:
            _concluir(nome, raiz)
            return None
        return INTERVALO

    return quadro


def _iniciar(alvo, abrir, progresso_inicial):
    """Monta o estado e registra o timer do alvo; `False` quando não há peça com movimento."""
    raiz = _raiz(alvo)
    if raiz is None:
        return False
    # No segundo toque, o movimento é o mesmo do timer que está saindo: o pivô da porta já não é o da peça fechada,
    # então reaproveitar a especificação é o que mantém a inversão no meio do caminho sem desvio.
    anterior = _animacoes.get(alvo.name) or {}
    anteriores = {nome: espec for nome, espec, _fechada in anterior.get('objetos', ())}
    cancelar(alvo.name)
    objetos = []
    for objeto in _grupo(alvo):
        especificacao = anteriores.get(objeto.name) or _deslocamento_de(objeto, raiz)
        if especificacao is None:
            continue
        fechada = _matriz(especificacao, progresso_inicial).inverted() @ objeto.matrix_world.copy()
        objetos.append((objeto.name, especificacao, fechada))
    if not objetos:
        return False
    _animacoes[alvo.name] = {
        'passo': 0,
        'abrir': bool(abrir),
        'p0': progresso_inicial,
        'p': progresso_inicial,
        'destino': 1.0 if abrir else 0.0,
        'raiz': raiz.name,
        'objetos': objetos,
    }
    funcao = _quadro(alvo.name)
    _handles[alvo.name] = funcao
    bpy.app.timers.register(funcao, first_interval=0.0)
    return True


def alternar(alvo):
    """Inverte o estado do alvo e começa a animação; devolve o estado de destino, ou `None` se não for animável."""
    if not animavel(alvo):
        return None
    progresso = _progresso_atual(alvo)
    abrir = not estado(alvo)
    if not _iniciar(alvo, abrir, progresso):
        return None
    return abrir


@persistent
def _ao_carregar(_arquivo):
    """Arquivo novo: os timers não persistentes morreram, então o dicionário de módulo some junto."""
    cancelar_tudo()


# Operador --------------------------------------------------------------------------------------------------------
class BTM_OT_ArmarioV2Alternar(bpy.types.Operator):
    """Abre ou fecha a gaveta, a folha deslizante ou a porta selecionada do armário v2"""

    bl_idname = "caffmob.armario_v2_alternar"
    bl_label = "Abrir / Fechar"
    # O operador só agenda o timer; o passo de desfazer é empurrado no último quadro (RF-16), por isso não é `UNDO`:
    # um `UNDO` aqui gravaria um passo vazio e o segundo toque no meio da animação deixaria dois passos.
    bl_options = {'REGISTER'}

    @classmethod
    def poll(cls, context):
        if alvo_de(context) is None:
            cls.poll_message_set(tr("Selecione uma gaveta, folha ou porta do armário v2"))
            return False
        return True

    def execute(self, context):
        alvo = alvo_de(context)
        if alvo is None:
            return {'CANCELLED'}
        if alternar(alvo) is None:
            return {'CANCELLED'}
        return {'FINISHED'}


classes = (BTM_OT_ArmarioV2Alternar,)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    if _ao_carregar not in bpy.app.handlers.load_post:
        bpy.app.handlers.load_post.append(_ao_carregar)


def unregister():
    cancelar_tudo()
    if _ao_carregar in bpy.app.handlers.load_post:
        bpy.app.handlers.load_post.remove(_ao_carregar)
    for cls in reversed(classes):
        if cls.is_registered:
            bpy.utils.unregister_class(cls)
