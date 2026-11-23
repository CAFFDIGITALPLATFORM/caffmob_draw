"""Menu de contexto das peças do armário v2 (feature 017, T024; RN-10, RN-11, RN-22, D-06, RF-25).

Um gancho só em `VIEW3D_MT_object_context_menu`, por `_append`/`_remove` como o resto do pacote, com os itens filtrados
pelo armário da seleção: o objeto ativo sobe a hierarquia até quem tem `btm_armario` e, sem armário, o menu não desenha
nada.

- **Abrir/Fechar** na gaveta, na folha deslizante e na porta, com o rótulo da ação oposta ao estado (`anim.rotulo`,
  RN-10). O operador é o de `anim`, então o menu só decide o texto e o ícone.
- **Duplicar** e **Excluir** só em divisória e prateleira (RN-11). A peça de cena não guarda o `uid` da divisão que a
  gerou: a ligação é feita pelo índice do `uid` da peça na lista de `build.pecas`, contando quantas peças de divisão
  vieram antes dela — as divisões e prateleiras entram antes dos internos, então a contagem para na coleção de
  divisórias. Peça de interno cai em `posicao >= len(divisoes)` e fica sem os dois itens.
- Duplicar usa `vaos.duplicar` (meio do maior vão livre, mínimo de 80 mm de cada lado) e Excluir usa `vaos.remover`;
  as duas regravam a coleção com `ops.gravar_divisoes` e refazem as peças quando o armário já estava gerado. Se a
  geração recusar, a coleção volta ao que era.

O menu não aparece em móvel da construção antiga: sem `btm_armario` na hierarquia, nenhum item é desenhado (RN-23).
"""

import bpy  # type: ignore

from ..data.i18n import tr
from . import anim
from . import build
from . import ops
from . import vaos as vaos_mod

PAPEIS_DIVISAO = ('DIVISORIA', 'PRATELEIRA')


def _raiz(obj):
    """Armário v2 dono do objeto (o vazio da coleção, `build.raiz_de`)."""
    return build.raiz_de(obj)


def _peca(context):
    obj = getattr(context, 'active_object', None)
    if obj is None or getattr(obj, 'btm_armario_parte', None) is None:
        return None
    return obj


def _alvo(context):
    """(armário, peça) da seleção; `(None, None)` quando não há peça do armário v2 sob a seleção."""
    peca = _peca(context)
    if peca is None:
        return None, None
    return _raiz(peca), peca


def divisao_da_peca(raiz, obj):
    """(divisão, posição na coleção) da peça escolhida, ou `(None, None)` para interno e outros papéis."""
    parte = getattr(obj, 'btm_armario_parte', None)
    if parte is None or parte.papel not in PAPEIS_DIVISAO:
        return None, None
    try:
        indice = int(str(parte.uid).rsplit('/', 1)[-1])
    except (TypeError, ValueError):
        return None, None
    armario = raiz.btm_armario
    itens = build.pecas(ops.spec_do_armario(raiz), ops.divisoes_do_armario(armario),
                        ops.gavetas_do_armario(armario), ops.internos_do_armario(armario))
    if not 0 <= indice < len(itens) or itens[indice]['papel'] not in PAPEIS_DIVISAO:
        return None, None
    posicao = sum(1 for item in itens[:indice] if item['papel'] in PAPEIS_DIVISAO)
    divisoes = ops.divisoes_do_armario(armario)
    if posicao >= len(divisoes):
        return None, None          # prateleira de interno: entra depois das divisões
    return divisoes[posicao], posicao


def _alvo_de_divisao(context):
    """(armário, divisão, posição) quando a seleção é divisória ou prateleira do armário."""
    raiz, peca = _alvo(context)
    if raiz is None:
        return None, None, None
    divisao, posicao = divisao_da_peca(raiz, peca)
    return raiz, divisao, posicao


def _regerar(raiz, context, anteriores, avisos_do_operador, acao):
    """Refaz as peças depois de mexer na coleção; se a geração recusar, devolve a coleção anterior."""
    if not raiz.btm_armario.gerado:
        return True
    gerou, avisos = ops.gerar_armario(raiz, context)
    for aviso in avisos:
        avisos_do_operador(aviso)
    if gerou:
        return True
    ops.gravar_divisoes(raiz.btm_armario, anteriores)
    acao.report({'WARNING'}, tr("A geração recusou a mudança: a divisória voltou ao que era"))
    return False


class BTM_OT_ArmarioV2Duplicar(bpy.types.Operator):
    """Duplica a divisória ou a prateleira no maior vão livre disponível"""

    bl_idname = "caffmob.armario_v2_duplicar"
    bl_label = "Duplicar"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return _alvo_de_divisao(context)[1] is not None

    def execute(self, context):
        raiz, divisao, _posicao = _alvo_de_divisao(context)
        if raiz is None or divisao is None:
            return {'CANCELLED'}
        anteriores = ops.divisoes_do_armario(raiz.btm_armario)
        divisoes, nova, motivo = vaos_mod.duplicar(anteriores, divisao.uid, ops.spec_do_armario(raiz))
        if nova is None:
            self.report({'WARNING'}, motivo)
            return {'CANCELLED'}
        ops.gravar_divisoes(raiz.btm_armario, divisoes)
        if not _regerar(raiz, context, anteriores, lambda aviso: self.report({'WARNING'}, aviso), self):
            return {'CANCELLED'}
        return {'FINISHED'}


class BTM_OT_ArmarioV2Excluir(bpy.types.Operator):
    """Exclui a divisória ou a prateleira escolhida do armário"""

    bl_idname = "caffmob.armario_v2_excluir"
    bl_label = "Excluir"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return _alvo_de_divisao(context)[1] is not None

    def execute(self, context):
        raiz, divisao, _posicao = _alvo_de_divisao(context)
        if raiz is None or divisao is None:
            return {'CANCELLED'}
        anteriores = ops.divisoes_do_armario(raiz.btm_armario)
        ops.gravar_divisoes(raiz.btm_armario, vaos_mod.remover(anteriores, divisao.uid))
        if not _regerar(raiz, context, anteriores, lambda aviso: self.report({'WARNING'}, aviso), self):
            return {'CANCELLED'}
        return {'FINISHED'}


def desenhar_menu(layout, context):
    """Itens do menu de contexto para a peça sob a seleção; sem armário v2, nada é desenhado."""
    raiz, peca = _alvo(context)
    if raiz is None or peca is None:
        return
    if anim.animavel(peca):
        aberto = anim.estado(peca)
        layout.separator()
        layout.operator("caffmob.armario_v2_alternar", text=anim.rotulo(peca),
                        icon='TRIA_DOWN' if aberto else 'TRIA_RIGHT')
    if divisao_da_peca(raiz, peca)[0] is not None:
        layout.separator()
        layout.operator("caffmob.armario_v2_duplicar", text=tr("Duplicar"), icon='DUPLICATE')
        layout.operator("caffmob.armario_v2_excluir", text=tr("Excluir"), icon='X')


def _menu(self, context):
    desenhar_menu(self.layout, context)


classes = (BTM_OT_ArmarioV2Duplicar, BTM_OT_ArmarioV2Excluir)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.VIEW3D_MT_object_context_menu.append(_menu)


def unregister():
    bpy.types.VIEW3D_MT_object_context_menu.remove(_menu)
    for cls in reversed(classes):
        if cls.is_registered:
            bpy.utils.unregister_class(cls)
