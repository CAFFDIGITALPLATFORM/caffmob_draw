"""065 T112: adaptadores finos de cena e tarefas; nenhum operador ou construção."""
import json
from .api_v2_core import ClienteV2, Operacao
from ..data.i18n import N_

PROPRIEDADE = 'caffmob_operacao_v2'
DISCOVERING = N_('Consultando capacidades do MOBI…')
_sessao = {}


class ArmazenamentoCena:
    """Uma propriedade JSON da Scene é serializada pelo Blender no arquivo .blend.

    Inclui o pedido congelado: uma mudança posterior da cena não pode trocar o hash
    de uma operação cujo resultado ainda é desconhecido. Não contém credenciais.
    """
    def __init__(self, scene):
        self.scene = scene

    def ler(self):
        texto = self.scene.get(PROPRIEDADE)
        return Operacao(**json.loads(texto)) if texto else None

    def guardar(self, operacao):
        self.scene[PROPRIEDADE] = json.dumps(operacao.dados(), ensure_ascii=False, allow_nan=False, separators=(',', ':'))

    def confirmar(self, chave):
        atual = self.ler()
        if atual is not None and atual.chave == chave:
            del self.scene[PROPRIEDADE]


def cliente(context, job, sessao=None, v1=None):
    import bpy  # type: ignore
    if sessao is None:
        from ..texture_library import downloads
        if _sessao.get('servidor') != downloads.server_url():
            _sessao.clear()
            _sessao['servidor'] = downloads.server_url()
    return ClienteV2(job.request, ArmazenamentoCena(context.scene), _sessao if sessao is None else sessao,
                     online=lambda: bpy.app.online_access, v1=v1)


def na_conexao(context, mensagem):
    """GET autenticado na conexão; 404 não encerra a sessão v1 nem apaga a cena."""
    import bpy  # type: ignore
    from . import tarefas
    from ..texture_library import downloads
    if not bpy.app.online_access:
        return None
    _sessao.clear()
    base = downloads.server_url()
    _sessao['servidor'] = base
    job = tarefas.Job(context, DISCOVERING)
    def recebido(resultado):
        if base != downloads.server_url():
            _sessao.clear()
        job.finish(mensagem)
        if base == downloads.server_url() and not resultado.mensagem:
            retomar_texturas(context)
            from ..standards import sync_cloud      # 067 onda 7: o login sincroniza o Padrão de Dimensões
            sync_cloud.schedule(0.1)
    cliente(context, job).descobrir(recebido)
    return job


def encerrar_sessao():
    _sessao.clear()


def retomar_texturas(context):
    """Após reconexão, tenta apenas as texturas pendentes da coleção ativa v2."""
    import bpy  # type: ignore
    from . import materiais_v2
    colecoes = [c for c in context.scene.collection.children if c.get('caffmob_schema') == 'caffmob.ambiente/v2']
    if not colecoes:
        return
    def tick():
        for colecao in colecoes:
            try:
                materiais_v2.baixar_pendentes(colecao)
            except (ReferenceError, RuntimeError):
                pass
        return None
    bpy.app.timers.register(tick, first_interval=0.01)
