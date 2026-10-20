"""065 T118: decisões e passos canceláveis, sem bpy nem transporte próprio."""
from time import perf_counter
from .api_v2_core import SCHEMA_V1, SCHEMA_V2, cabecalho
from ..data.i18n import N_, tr

ETAPAS = {
    'pavimentos': N_('Montando pavimentos…'),
    'paredes': N_('Montando paredes…'),
    'obra': N_('Montando obra…'),
    'moveis': N_('Montando móveis…'),
    'texturas': N_('Solicitando texturas…'),
}
ROTULOS = {SCHEMA_V1: N_('v 1'), SCHEMA_V2: N_('v 2')}
REVISAO_INVALIDA = N_('Revisão do ambiente inválida. A cena foi preservada')
ERRO_POR_CAMINHO = N_('{}: {} ({})')


def lista_v2(capacidades):
    return bool(capacidades and capacidades.get('ambientes_v2') is True)


def schema_do_item(itens, ambiente_id, informado=SCHEMA_V1):
    return next((i.schema for i in itens if i.id == ambiente_id), informado)


def rotulo(schema):
    return tr(ROTULOS.get(schema, schema))


def revisao(documento, headers):
    etag = cabecalho(headers, 'ETag')
    version = documento.get('version')
    if type(version) is not int or version < 1 or etag != '"{}"'.format(version):
        raise ValueError(tr(REVISAO_INVALIDA))
    return etag


def relatorio(erros):
    return '\n'.join(tr(ERRO_POR_CAMINHO).format(e['caminho'], tr(e['mensagem']), e['codigo']) for e in erros)


class Preparo:
    """Um passo por chamada; erro e Cancelar descartam o preparo uma única vez.

    A troca é externa e só pode ocorrer depois de pronto. Isso deixa Cancelar
    disponível também entre a última entidade e a aplicação do resultado.
    """
    def __init__(self, montagem, progresso=lambda etapa, valor: None, relogio=perf_counter):
        self.montagem, self.progresso, self.relogio = montagem, progresso, relogio
        self.passos = iter(montagem.passos())
        self.cancelado, self.pronto = False, False
        self.medicoes = []

    def avancar(self):
        if self.cancelado or self.pronto:
            return False
        inicio = self.relogio()
        etapa = None
        try:
            etapa, passo = next(self.passos)
            self.progresso(etapa, (list(ETAPAS).index(etapa) + 1) / (len(ETAPAS) + 1))
            passo()
        except StopIteration:
            self.pronto = True
            return False
        except Exception:
            self.cancelar()
            raise
        finally:
            if etapa is not None:
                self.medicoes.append(dict(etapa=etapa, ms=(self.relogio() - inicio) * 1000))
        return True

    def cancelar(self):
        if not self.cancelado:
            self.cancelado = True
            self.passos.close()
            self.montagem.cancelar()
