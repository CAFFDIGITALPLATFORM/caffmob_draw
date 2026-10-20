"""Prancheta v2: documento em mm, interação e histórico sem Blender.

O documento é a fonte da verdade. Geometria desenhada e alvos de clique são derivados.
Tolerâncias de interação usam pixels visuais, como pranchetaDeParedesStudio.ts.
"""
import copy
import math
import uuid
from ..caffmob.v2 import paredes_edicao as pe
from ..caffmob.geometria import geometria_da_parede, trechos_da_parede, vao_da_abertura
from .studio_selecao import combinar


def arredondar(v, passo):
    # Math.round do JS, inclusive nos meios negativos.
    return math.floor(v / passo + 0.5) * passo


def distancia(p, a, b):
    dx, dy = b[0] - a[0], b[1] - a[1]
    q = dx * dx + dy * dy
    f = max(0, min(1, ((p[0] - a[0]) * dx + (p[1] - a[1]) * dy) / q)) if q else 0
    return math.hypot(p[0] - a[0] - f * dx, p[1] - a[1] - f * dy), f


def pontos(p):
    ts = trechos_da_parede(p)
    return [ts[0][0], *(t[1] for t in (ts[:-1] if p['fechada'] else ts))]


def previa(inicio, cursor, escala, primeiro=None, vizinhos=(), comprimento=None, angulo=None, ortogonal=False):
    dx, dy = cursor[0] - inicio[0], cursor[1] - inicio[1]
    a = angulo if angulo is not None else arredondar(math.degrees(math.atan2(dy, dx)), 90 if ortogonal else 15)
    l = comprimento if comprimento is not None else max(10, arredondar(math.hypot(dx, dy), 10))
    x, y = inicio[0] + l * math.cos(math.radians(a)), inicio[1] + l * math.sin(math.radians(a))
    retorno = 'Snap de 15° e 10 mm'
    if comprimento is not None or angulo is not None:
        retorno = 'Medida e direção'
    elif primeiro is not None and math.dist(cursor, primeiro) <= 16 / escala:
        x, y = primeiro
        retorno = 'Primeiro ponto'
    else:
        vx = next((q for q in vizinhos if abs(q[0] - cursor[0]) < 10 / escala), None)
        vy = next((q for q in vizinhos if abs(q[1] - cursor[1]) < 10 / escala), None)
        if vx is not None:
            x, retorno = vx[0], 'Alinhamento X'
        if vy is not None:
            y, retorno = vy[1], 'Alinhamento X e Z' if vx is not None else 'Alinhamento Z'
    return dict(fim=(x, y), comprimento=math.hypot(x - inicio[0], y - inicio[1]),
                angulo=math.degrees(math.atan2(y - inicio[1], x - inicio[0])) % 360, retorno=retorno)


def snap_ponto(parede, indice, alvo, escala):
    ps = pontos(parede)
    x, y = (arredondar(v, 10) for v in alvo)
    for j in (indice - 1, indice + 1):
        if parede['fechada']:
            j %= len(ps)
        if not 0 <= j < len(ps):
            continue
        q = ps[j]
        if abs(q[0] - x) < 10 / escala:
            x = q[0]
        if abs(q[1] - y) < 10 / escala:
            y = q[1]
    return x, y


def cota(p, i, escala):
    a, b = trechos_da_parede(p)[i]
    ps = pontos(p)
    centro = (sum(q[0] for q in ps) / len(ps), sum(q[1] for q in ps) / len(ps))
    meio = ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2)
    l = math.dist(a, b) or 1
    nx, ny = -(b[1] - a[1]) / l, (b[0] - a[0]) / l
    sinal = -1 if (centro[0] - meio[0]) * nx + (centro[1] - meio[1]) * ny > 0 else 1
    return meio[0] + nx * sinal * 30 / escala, meio[1] + ny * sinal * 30 / escala


class Prancheta:
    def __init__(self, documento, pavimento_id=None, parede_id=None, gerar_id=None):
        self.documento = copy.deepcopy(documento)
        self.original = copy.deepcopy(documento)
        self.pavimento_id = pavimento_id or min(documento['pavimentos'], key=lambda p: p['ordem'])['id']
        self.gerar_id = gerar_id or (lambda: str(uuid.uuid4()))
        self.selecao = None
        self._selecionadas = []
        self.multipla_toque = False
        self.aresta_presa = False
        self.retangulo = None
        self.confirmacao = None
        self.anuncio = ''
        self.ponto = None
        self.abertura = None
        self.divisao = 0
        self.ancora = 'inicio'
        self.lado = 'interna'
        self.espessura = 150
        self.ortogonal = False
        self.inicio = None
        self.primeiro = None
        self.desenhando = False
        self.parede_desenho = None
        self.direcao = 0
        self.direcao_travada = False
        self.texto = ''
        self.erros = []
        self._historico = [copy.deepcopy(documento)]
        self._indice = 0
        p = next((p for p in self.paredes() if p['id'] == parede_id), None)
        if p and p['segmentos']:
            self.selecao = p['segmentos'][0]['id']

    def paredes(self):
        return [p for p in self.documento['paredes'] if p['pavimento_id'] == self.pavimento_id]

    @property
    def selecionadas(self):
        existentes = {s['id'] for p in self.paredes() for s in p['segmentos']}
        # Compatibilidade com a seleção simples usada pelos campos e pelo caminho v2 anterior.
        if self.selecao not in self._selecionadas:
            return [self.selecao] if self.selecao in existentes else []
        return [id for id in self._selecionadas if id in existentes]

    def selecionar_ids(self, ids, modo='substituir'):
        existentes = {s['id'] for p in self.paredes() for s in p['segmentos']}
        self._selecionadas = [id for id in combinar(self.selecionadas, ids, modo) if id in existentes]
        self.selecao = self._selecionadas[0] if self._selecionadas else None
        self.ponto = self.abertura = None
        self.confirmacao = None
        if not self._selecionadas:
            self.multipla_toque = False
        self.anuncio = f'{len(self._selecionadas)} paredes selecionadas'

    def selecionar_todas(self):
        self.selecionar_ids([s['id'] for p in self.paredes() for s in p['segmentos']])

    def editar_lote(self, patch):
        return self.tentar(pe.editar_paredes_em_lote(self.documento, self.pavimento_id, self.selecionadas, patch))

    def pedir_exclusao(self):
        if len(self.selecionadas) > 1:
            self.confirmacao = dict(ids=self.selecionadas[:], quantidade=len(self.selecionadas))
            return False
        return self.excluir()

    def confirmar_exclusao(self):
        if not self.confirmacao:
            return False
        ids = self.confirmacao['ids']
        if self.tentar(pe.excluir_paredes_em_lote(self.documento, self.pavimento_id, ids,
                                                self.gerar_id, confirmar_dependencias=True)):
            self.selecionar_ids([])
            return True
        return False

    def trecho(self):
        for p in self.paredes():
            for i, s in enumerate(p['segmentos']):
                if s['id'] == self.selecao:
                    return p, i, s
        return None, None, None

    def tentar(self, resultado):
        self.erros = resultado.get('erros', [])
        if not resultado['ok']:
            return False
        self.documento = copy.deepcopy(resultado['valor'])
        return True

    def checkpoint(self):
        if self.documento == self._historico[self._indice]:
            return False
        self._historico[self._indice + 1:] = [copy.deepcopy(self.documento)]
        self._indice += 1
        return True

    def historico(self, passo):
        alvo = self._indice + passo
        if not 0 <= alvo < len(self._historico):
            return False
        self._indice = alvo
        self.documento = copy.deepcopy(self._historico[alvo])
        self.confirmacao = self.retangulo = None
        self.concluir()
        self.ponto = self.abertura = None
        self.erros = []
        if self.trecho()[0] is None:
            self.selecao = None
        self.selecionar_ids(self.selecionadas)
        return True

    def referencias(self):
        referencias = []
        camadas = {c['id']: c['visivel'] for c in self.documento['camadas']}
        for m in self.documento['modulos']:
            if m['pavimento_id'] != self.pavimento_id or not m['visivel'] or not camadas.get(m['camada_id'], True):
                continue
            a = math.radians(m['rotacao_z'])
            w, h = m['parametros']['largura'], m['parametros']['profundidade']
            referencias.append([(m['posicao']['x'] + x * math.cos(a) - y * math.sin(a),
                                 m['posicao']['y'] + x * math.sin(a) + y * math.cos(a))
                                for x, y in ((0, 0), (w, 0), (w, h), (0, h), (0, 0))])
        return referencias

    def bounds(self):
        ps = [q for p in self.paredes() for g in geometria_da_parede(p) for q in g['linha'] + g['face']]
        if not ps:
            return ((-3, -3), (3, 3))
        return ((min(q[0] for q in ps) / 1000, min(q[1] for q in ps) / 1000),
                (max(q[0] for q in ps) / 1000, max(q[1] for q in ps) / 1000))

    def alcas(self, escala):
        p, i, s = self.trecho()
        if p is None or len(self.selecionadas) > 1:
            return {}
        a, b = trechos_da_parede(p)[i]
        l = math.dist(a, b) or 1
        ux, uy = (b[0] - a[0]) / l, (b[1] - a[1]) / l
        centro = ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2)
        return {nome: (centro[0] + ux * dx / escala - uy * 24 / escala,
                       centro[1] + uy * dx / escala + ux * 24 / escala)
                for nome, dx in (('ancora', -16), ('dividir', 16))}

    def hit(self, alvo, escala):
        tol = 12 / escala
        if not self.desenhando:
            for nome, q in self.alcas(escala).items():
                if math.dist(alvo, q) <= 8 / escala:
                    return dict(tipo=nome, id=self.selecao)
        # Aberturas antes de pontos e trechos, como o Studio.
        for p in self.paredes():
            for i, g in enumerate(geometria_da_parede(p)):
                s = p['segmentos'][i]
                for a in self.documento['aberturas']:
                    if a['segmento_id'] != s['id']:
                        continue
                    vao = vao_da_abertura(a, s, g)
                    if vao and distancia(alvo, vao['inicio'], vao['fim'])[0] < tol + s['espessura'] / 2:
                        return dict(tipo='abertura', id=a['id'], segmento=s['id'])
        for p in self.paredes():
            for k, q in enumerate(pontos(p)):
                if math.dist(q, alvo) <= tol:
                    return dict(tipo='ponto', parede=p['id'], indice=k)
        for p in self.paredes():
            for i, s in enumerate(p['segmentos']):
                if math.dist(alvo, cota(p, i, escala)) <= tol:
                    return dict(tipo='cota', id=s['id'], fracao=0.5)
        for p in self.paredes():
            for i, g in enumerate(geometria_da_parede(p)):
                s = p['segmentos'][i]
                if any(distancia(alvo, a, b)[0] <= tol + s['espessura'] for a, b in zip(g['linha'], g['linha'][1:])):
                    return dict(tipo='trecho', id=s['id'], fracao=distancia(alvo, *trechos_da_parede(p)[i])[1])
        return None

    def selecionar(self, hit):
        self.erros = []
        self.ponto = self.abertura = None
        if hit is None:
            self.selecionar_ids([])
        elif hit['tipo'] == 'ponto':
            self.ponto = (hit['parede'], hit['indice'])
            p = next(p for p in self.paredes() if p['id'] == hit['parede'])
            self.selecao = p['segmentos'][min(hit['indice'], len(p['segmentos']) - 1)]['id']
            self._selecionadas = [self.selecao]
        else:
            self.selecao = hit.get('segmento', hit['id'])
            self._selecionadas = [self.selecao]
            if hit['tipo'] == 'abertura':
                self.abertura = hit['id']
            else:
                self.divisao = self.trecho()[2]['comprimento'] * hit['fracao']

    def editar(self, **patch):
        return self.tentar(pe.editar_trecho(self.documento, self.selecao,
                           dict(ancora=self.ancora, lado_medida=self.lado, **patch)))

    def iniciar(self, origem=(0, 0)):
        self.concluir()
        self.desenhando = True
        self.inicio = self.primeiro = tuple(origem)
        self.selecao = self.ponto = self.abertura = None
        self._selecionadas = []
        self.multipla_toque = False

    def continuar(self):
        p, _, _ = self.trecho()
        if p is None or p['fechada']:
            return False
        self.desenhando = True
        self.ponto = self.abertura = None
        self.direcao = p['segmentos'][-1]['angulo_absoluto']
        self.parede_desenho = p['id']
        self.inicio = trechos_da_parede(p)[-1][1]
        self.primeiro = (p['origem']['x'], p['origem']['y'])
        return True

    def previa(self, cursor, escala, comprimento=None):
        if not self.desenhando:
            return None
        return previa(self.inicio, cursor, escala, self.primeiro,
                      [q for p in self.paredes() for q in pontos(p)], comprimento,
                      self.direcao if comprimento is not None or self.direcao_travada else None, self.ortogonal)

    def fixar(self, ponto, fechar=False):
        if not self.desenhando:
            self.iniciar(ponto)
            return True
        atual = next((p for p in self.paredes() if p['id'] == self.parede_desenho), None)
        if atual and len(atual['segmentos']) >= 2 and math.dist(ponto, self.primeiro) <= 0.1:
            fechar = True
        pid = self.parede_desenho or self.gerar_id()
        r = pe.fixar_vertice(self.documento, pid, dict(x=ponto[0], y=ponto[1]), self.gerar_id(),
                            self.pavimento_id, self.espessura, dict(x=self.inicio[0], y=self.inicio[1]), fechar)
        if not self.tentar(r):
            return False
        self.parede_desenho = pid
        self.inicio = ponto
        self.selecao = next(p for p in self.paredes() if p['id'] == pid)['segmentos'][-1]['id']
        self.texto = ''
        self.direcao_travada = False
        self.checkpoint()
        if fechar:
            self.concluir()
        return True

    def fechar(self):
        return self.fixar(self.primeiro, True) if self.desenhando and self.parede_desenho else False

    def concluir(self):
        self.desenhando = False
        self.inicio = self.primeiro = self.parede_desenho = None
        self.texto = ''
        self.direcao_travada = False

    def modelo(self, modelo, largura=4000, profundidade=3000):
        r = pe.criar_modelo_da_prancheta(self.documento, dict(modelo=modelo, largura=largura,
            profundidade=profundidade, origem=dict(x=0, y=0), pavimento_id=self.pavimento_id, gerar_id=self.gerar_id, espessura=self.espessura))
        if self.tentar(r):
            self.concluir()
            self.ponto = self.abertura = None
            self.selecao = self.documento['paredes'][-1]['segmentos'][0]['id']
            self.checkpoint()
            return True
        return False

    def dividir(self):
        p, i, _ = self.trecho()
        if self.tentar(pe.dividir_trecho(self.documento, self.selecao, self.divisao, self.gerar_id())):
            self.ponto = (p['id'], i + 1)
            return True
        return False

    def excluir(self, confirmar=False):
        if self.abertura:
            r = pe.remover_abertura(self.documento, self.abertura)
        elif self.ponto:
            r = pe.excluir_ponto(self.documento, *self.ponto)
        else:
            r = pe.remover_trecho(self.documento, self.selecao, confirmar_dependencias=confirmar,
                                 nova_parede_id=self.gerar_id())
        if not self.tentar(r):
            return False
        self.ponto = self.abertura = None
        if self.trecho()[0] is None:
            self.selecao = None
        return True

    def abertura_nova(self, tipo):
        _, _, s = self.trecho()
        if s is None:
            return False
        janela = tipo == 'WINDOW'
        largura = 1200 if janela else 800
        a = dict(id=self.gerar_id(), segmento_id=s['id'], tipo=tipo, largura=largura,
                 posicao=(s['comprimento'] - largura) / 2, altura=1000 if janela else 2100, peitoril=1100 if janela else 0)
        if not self.tentar(pe.inserir_abertura(self.documento, a)):
            return False
        self.abertura = a['id']
        return True
