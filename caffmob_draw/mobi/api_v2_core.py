"""065 T112: protocolo e intenções duráveis, sem bpy e sem acesso à rede.

O transporte injetado é tarefas.Job.request. Ele já usa o subprocesso da 063,
que faz as esperas e retentativas; este núcleo nunca duplica essa política.
"""
import copy
from dataclasses import dataclass, asdict
from uuid import uuid4
from urllib.parse import urlencode
from ..data.i18n import N_, tr
from ..caffmob.v2.serializacao import serializar
from ..caffmob.contrato import sem_envelope_do_servidor

ACCEPT = 'application/vnd.caffmob.ambiente+json;version=2, application/vnd.caffmob.ambiente+json;version=1'
BASE = '/api/draw/v2'
SCHEMA_V1 = 'caffmob.ambiente/v1'
SCHEMA_V2 = 'caffmob.ambiente/v2'
RETRY = N_('Tentar novamente')
OFFLINE = N_('Acesso à internet do Blender desligado')
OLD_SERVER = N_('Este servidor aceita somente ambientes v1. O ambiente v2 foi preservado')
DISCOVER = N_('Não foi possível consultar as capacidades do MOBI. Tente novamente')
PENDING = N_('Há um envio pendente. Confirme o recibo antes de iniciar outro envio')
REMOTE = N_('Carregar a versão do MOBI')
LOCAL = N_('Enviar a versão local')
COPY = N_('Salvar como cópia')
BAD_OPERATION = N_('Operação ou revisão-base inválida')
BAD_CHOICE = N_('Escolha de conflito inválida')
INVALID_RECEIPT = N_('O MOBI não confirmou o recibo. A chave do envio foi preservada')


def cabecalho(headers, nome):
    return next((v for k, v in (headers or {}).items() if k.lower() == nome.lower()), None)


@dataclass(frozen=True)
class Operacao:
    chave: str
    ambiente_id: str
    metodo: str
    revisao_base: int | None
    documento: dict

    @classmethod
    def criar(cls, documento, metodo, revisao_base=None, gerar_uuid=lambda: str(uuid4())):
        if metodo not in ('POST', 'PUT') or (metodo == 'PUT' and (type(revisao_base) is not int or revisao_base < 1)):
            raise ValueError(tr(BAD_OPERATION))
        return cls(gerar_uuid(), documento['id'], metodo, revisao_base if metodo == 'PUT' else None, copy.deepcopy(documento))

    def dados(self):
        return asdict(self)

    def mesma_intencao(self, documento, metodo, revisao_base):
        return (self.metodo == metodo and self.ambiente_id == documento['id'] and self.revisao_base == (revisao_base if metodo == 'PUT' else None)
                and serializar(sem_envelope_do_servidor(self.documento)) == serializar(sem_envelope_do_servidor(documento)))

    def pedido(self):
        headers = {'Accept': ACCEPT, 'Content-Type': 'application/json; charset=utf-8', 'Idempotency-Key': self.chave}
        if self.metodo == 'PUT':
            headers['If-Match'] = f'"{self.revisao_base}"'
        path = BASE + '/ambientes' + ('/' + self.ambiente_id if self.metodo == 'PUT' else '')
        return self.metodo, path, copy.deepcopy(self.documento), headers


@dataclass(frozen=True)
class Conflito:
    local: dict
    remota: dict
    versao_atual: int
    escolhas: tuple = ('remota', 'local', 'copia')

    def escolher(self, escolha, gerar_uuid=lambda: str(uuid4())):
        if escolha == 'remota':
            return copy.deepcopy(self.remota)
        if escolha == 'local':
            return Operacao.criar(self.local, 'PUT', self.versao_atual, gerar_uuid)
        if escolha == 'copia':
            documento = copy.deepcopy(self.local)
            documento['id'] = gerar_uuid()
            return Operacao.criar(documento, 'POST', gerar_uuid=gerar_uuid)
        raise ValueError(tr(BAD_CHOICE))

    def rotulos(self):
        return tuple(tr(v) for v in (REMOTE, LOCAL, COPY))


@dataclass
class Resultado:
    status: int | None
    corpo: object
    headers: dict
    mensagem: str = ''
    conflito: Conflito | None = None
    replay: bool = False
    atual: object = None
    status_atual: int | None = None


def confirmar_recibo(operacao, status, corpo):
    return (status == (201 if operacao.metodo == 'POST' else 200) and isinstance(corpo, dict)
            and corpo.get('id') == operacao.ambiente_id and type(corpo.get('version')) is int
            and corpo['version'] == (1 if operacao.metodo == 'POST' else operacao.revisao_base + 1))


class ClienteV2:
    def __init__(self, transporte, armazenamento, sessao, online=lambda: True, v1=None):
        self.transporte, self.armazenamento, self.sessao = transporte, armazenamento, sessao
        self.online, self.v1 = online, v1

    def _pedido(self, metodo, path, corpo=None, headers=None, callback=None):
        if not self.online():
            callback(None, {'erro': 'OFFLINE', 'message': tr(OFFLINE)}, {})
            return None
        return self.transporte(metodo, path, corpo, headers=headers or {'Accept': ACCEPT}, callback=callback)

    def descobrir(self, callback):
        def recebido(status, corpo, headers):
            if status == 404:
                self.sessao['capacidades'] = {'versao_api': 1, 'schemas': [SCHEMA_V1], 'ambientes_v2': False}
            elif status == 200 and isinstance(corpo, dict) and corpo.get('versao_api') == 2 and isinstance(corpo.get('schemas'), list):
                self.sessao['capacidades'] = copy.deepcopy(corpo)
            else:
                callback(Resultado(status, corpo, headers, tr(DISCOVER)))
                return
            callback(Resultado(status, corpo, headers))
        return self._pedido('GET', BASE + '/capacidades', callback=recebido)

    def rota(self, schema):
        caps = self.sessao.get('capacidades')
        if caps is None:
            raise ValueError(tr(DISCOVER))
        if schema not in (SCHEMA_V1, SCHEMA_V2) or schema not in caps.get('schemas', []):
            raise ValueError(tr(OLD_SERVER))
        if caps.get('versao_api') == 1:
            if schema != SCHEMA_V1:
                raise ValueError(tr(OLD_SERVER))
            return '/api/draw/v1'
        if schema == SCHEMA_V2 and not caps.get('ambientes_v2'):
            raise ValueError(tr(OLD_SERVER))
        return BASE

    def listar(self, callback, depois='0'):
        base = self.rota(SCHEMA_V1)
        return self._pedido('GET', base + '/ambientes?' + urlencode({'depois': depois}), callback=callback)

    def ler(self, ambiente_id, callback, schema=SCHEMA_V2):
        # Não há downgrade após 404/5xx. Só a descoberta decide a rota.
        base = self.rota(schema)
        return self._pedido('GET', base + '/ambientes/' + ambiente_id, callback=callback)

    def enviar(self, documento, metodo, revisao_base, callback):
        if not self.online():
            callback(Resultado(None, {}, {}, tr(OFFLINE)))
            return None
        base = self.rota(documento['schema'])
        if base != BASE:
            if self.v1 is None:
                raise ValueError(tr(OLD_SERVER))
            return self.v1(documento, metodo, revisao_base, callback)
        if documento['schema'] == SCHEMA_V2:
            from ..caffmob.v2.validacao import validar_documento
            from ..caffmob.v2.serializacao import DocumentoInvalido
            erros = validar_documento(documento)
            if erros:
                raise DocumentoInvalido(erros)
        operacao = self.armazenamento.ler()
        if operacao is None:
            operacao = Operacao.criar(documento, metodo, revisao_base)
            # O armazenamento confirma a escrita antes de qualquer chamada de transporte.
            self.armazenamento.guardar(operacao)
        elif not operacao.mesma_intencao(documento, metodo, revisao_base):
            raise ValueError(tr(PENDING))
        return self.reenviar(callback)

    def reenviar(self, callback):
        operacao = self.armazenamento.ler()
        if operacao is None:
            raise ValueError(tr(PENDING))
        self.rota(operacao.documento['schema'])
        def recebido(status, corpo, headers):
            resultado = Resultado(status, corpo, headers)
            if confirmar_recibo(operacao, status, corpo):
                self.armazenamento.confirmar(operacao.chave)
                resultado.replay = str(cabecalho(headers, 'Idempotency-Replayed')).lower() == 'true'
                if resultado.replay:
                    # O recibo pode ser antigo: GET é informativo, nunca um novo PUT automático.
                    def atual(s, d, h):
                        resultado.atual, resultado.status_atual = d, s
                        callback(resultado)
                    self._pedido('GET', BASE + '/ambientes/' + operacao.ambiente_id, callback=atual)
                    return
            elif status in (200, 201):
                resultado.mensagem = tr(INVALID_RECEIPT)
            elif status == 409 and isinstance(corpo, dict) and corpo.get('erro') == 'VERSAO_DIVERGENTE':
                if isinstance(corpo.get('documento_atual'), dict) and type(corpo.get('versao_atual')) is int:
                    resultado.conflito = Conflito(copy.deepcopy(operacao.documento), copy.deepcopy(corpo['documento_atual']), corpo['versao_atual'])
            elif status is None or status == 429 or 500 <= status < 600:
                resultado.mensagem = tr(RETRY)
            callback(resultado)
        metodo, path, corpo, headers = operacao.pedido()
        return self._pedido(metodo, path, corpo, headers, recebido)
