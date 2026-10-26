"""Do projeto `.promob` lido ao documento do CAFF MOBI v2 e ao complemento local (071 D-05 a D-11, D-30), sem bpy.

- Paredes e aberturas vão para o documento v2 (RN-10): ganham o Editor de Paredes, o painel por seleção e o envio
  ao MOBI.
- Móveis, lajes livres e malhas vinculadas vão para o complemento, que só existe no `.blend` (D-30): o contrato
  do v2 aceita no máximo 300 entidades posicionáveis, e um ambiente do Promob passa disso.
"""
import math
import uuid
from datetime import datetime, timezone

from ..caffmob.contrato import normalizar_relativo
from ..caffmob.v2.validacao import validar_documento

PERTO_DA_PAREDE = 60.0          # mm que a porta pode ficar fora da face (RN-04)
SOBREPOSICAO_MINIMA = 50.0
PEITORIL_DE_PORTA = 100.0       # abaixo disso a abertura é porta (D-07)
TRECHO_MINIMO = 50.0            # o contrato v2 recusa trecho menor
IGNORADOS = {'Teto': 'forro', 'LuzSpot': 'luz', 'LuzAmbiente': 'luz'}
PALAVRAS_DE_ABERTURA = ('abert', 'janel', 'portai')


def _id():
    return str(uuid.uuid4())


def _cor_hex(rgb):
    return '#%02x%02x%02x' % tuple(rgb)


def _girar(x, y, graus):
    r = math.radians(graus)
    return x * math.cos(r) - y * math.sin(r), x * math.sin(r) + y * math.cos(r)


def origem_da_caixa(item):
    """Canto frontal-esquerdo-inferior em mm de mundo: base + R·(0, −D, 0) (RN-03)."""
    dx, dy = _girar(0.0, -item.profundidade, item.rotacao)
    return (item.base[0] + dx, item.base[1] + dy, item.base[2])


def resolver_macros(nome, item):
    medidas = {'W': item.largura, 'H': item.altura, 'D': item.profundidade}
    for letra, valor in medidas.items():
        for m in (letra, letra.lower()):
            nome = nome.replace(f'${m}$', str(int(round(valor))))
    saida, i = nome, 0
    while True:
        a = saida.find('#', i)
        if a < 0:
            break
        b = saida.find('#', a + 1)
        if b < 0 or b == a + 1 or ' ' in saida[a + 1:b]:
            i = a + 1
            continue
        saida = saida[:a] + saida[b + 1:]
    return ' '.join(saida.split())


def contorno_com_arcos(pontos):
    """Pontos (x, y, ângulo do arco até o seguinte) para um contorno de segmentos retos (`tessellate_outline`)."""
    n, out = len(pontos), []
    for i in range(n):
        x0, y0, a = pontos[i]
        x1, y1, _ = pontos[(i + 1) % n]
        out.append((x0, y0))
        if abs(a) < 0.01 or abs(a) >= 360:
            continue
        theta = math.radians(a)
        dx, dy = x1 - x0, y1 - y0
        corda = math.hypot(dx, dy)
        if corda < 1e-4:
            continue
        r = corda / abs(2 * math.sin(theta / 2))
        mx, my = (x0 + x1) / 2, (y0 + y1) / 2
        h = math.sqrt(max(r * r - corda * corda / 4, 0)) * (-1 if abs(theta) > math.pi else 1)
        lx, ly = -dy / corda, dx / corda
        lado = 1 if theta > 0 else -1
        cx, cy = mx + lx * h * lado, my + ly * h * lado
        inicio = math.atan2(y0 - cy, x0 - cx)
        passos = min(max(math.ceil(abs(a) / 10), 2), 64)
        for k in range(1, passos):
            ang = inicio + theta * k / passos
            out.append((cx + r * math.cos(ang), cy + r * math.sin(ang)))
    return out


class Conversao:
    def __init__(self, projeto, novo_id=_id):
        self.projeto, self.novo_id = projeto, novo_id
        self.relatorio = dict(contagem={}, paredes=0, aberturas=0, caixas=0, grupos=0, lajes=0, malhas=0,
                              ignorados=[], avisos=list(projeto.avisos))
        self.materiais_do_documento = {}
        self.materiais_do_complemento = {}
        self.trechos = []            # (parede_dict, segmento_dict, p0, u, sentido, espessura, altura)
        self.paredes = []
        self.aberturas = []
        self.hospedados = []         # itens de abertura hospedados por WALL
        self.moveis = []
        self.lajes = []
        self.malhas = []

    # -- relatório -------------------------------------------------------------------------------------------------
    def _ignorar(self, item, motivo):
        if len(self.relatorio['ignorados']) < 200:
            self.relatorio['ignorados'].append(dict(item=item.nome[:80], tipo=item.tipo, motivo=motivo))

    def _contar(self, item):
        c = self.relatorio['contagem']
        c[item.tipo] = c.get(item.tipo, 0) + 1

    # -- materiais ------------------------------------------------------------------------------------------------
    def _material(self, mid):
        if not mid:
            return None
        m = self.projeto.materiais.get(mid)
        if mid.lower().startswith('cin_cor_'):
            return dict(id=mid, nome='Acabamento do modelo (não resolvido)', cor=_cor_hex((0xE6, 0xE4, 0xDF)),
                        textura=None, escala=None)
        if m is None:
            return dict(id=mid, nome=mid[:80], cor=_cor_hex((0xBD, 0xB7, 0xAE)), textura=None, escala=None)
        return dict(id=mid, nome=m.nome, cor=_cor_hex(m.cor), textura=m.textura, escala=m.escala)

    def _material_do_documento(self, mid):
        dado = self._material(mid)
        if dado is None:
            return None
        if mid not in self.materiais_do_documento:
            self.materiais_do_documento[mid] = dict(id=self.novo_id(), nome=dado['nome'][:160] or 'Material',
                                                   tipo='cor', cor=dado['cor'], classe_visual='gesso')
        return self.materiais_do_documento[mid]['id']

    def _material_do_complemento(self, mid):
        dado = self._material(mid)
        if dado is not None:
            self.materiais_do_complemento.setdefault(mid, dado)
        return mid if dado is not None else None

    # -- paredes (D-06) -------------------------------------------------------------------------------------------
    def _parede(self, item, pavimento_id):
        altura = item.altura
        pontos = []
        for x, y, e in item.pontos:
            if pontos and math.hypot(x - pontos[-1][0], y - pontos[-1][1]) < TRECHO_MINIMO:
                if math.hypot(x - pontos[-1][0], y - pontos[-1][1]) >= 1:
                    self.relatorio['avisos'].append(f'Trecho curto unido ({item.nome[:40]})')
                continue
            pontos.append((x, y, e))
        fechada = len(pontos) > 2 and math.hypot(pontos[0][0] - pontos[-1][0], pontos[0][1] - pontos[-1][1]) < TRECHO_MINIMO
        if fechada:
            pontos.pop()
        if len(pontos) < 2:
            self._ignorar(item, 'parede sem trecho')
            return
        if not 1000 <= altura <= 6000:
            self.relatorio['avisos'].append(f'Altura da parede ajustada para a faixa de 1000 a 6000 mm ({altura:.0f} mm)')
            altura = min(max(altura, 1000), 6000)
        sentido = 'RIGHT' if item.alinhamento.lower() == 'esquerda' else 'LEFT'
        if item.alinhamento and item.alinhamento.lower() not in ('direita', 'esquerda'):
            self.relatorio['avisos'].append(f'Alinhamento de parede "{item.alinhamento}" tratado como Direita')
        parede = dict(id=self.novo_id(), origem=dict(x=pontos[0][0], y=pontos[0][1]), fechada=fechada,
                      pavimento_id=pavimento_id, camada_id=None, visivel=item.visivel, perfil='studio/1', segmentos=[])
        material = self._material_do_documento(item.material_das_faces)
        if material:
            parede['material_id'] = material
        pares = list(zip(pontos, pontos[1:] + ([pontos[0]] if fechada else [])))
        anterior = None
        for (x0, y0, e), (x1, y1, _) in pares:
            comprimento = math.hypot(x1 - x0, y1 - y0)
            angulo = math.degrees(math.atan2(y1 - y0, x1 - x0)) % 360
            espessura = min(max(e or 150.0, 20.0), 1000.0)
            segmento = dict(id=self.novo_id(), comprimento=round(comprimento, 3), angulo_absoluto=round(angulo, 6),
                            angulo_relativo=0 if anterior is None else normalizar_relativo(angulo - anterior),
                            espessura=espessura, pe_direito_inicial=altura, pe_direito_final=altura, afastamento=0,
                            flecha=0, sentido=sentido, tipo='NORMAL', estado='ativo')
            parede['segmentos'].append(segmento)
            u = ((x1 - x0) / comprimento, (y1 - y0) / comprimento)
            self.trechos.append((parede, segmento, (x0, y0), u, sentido, espessura, altura))
            anterior = angulo
        self.paredes.append(parede)
        self.relatorio['paredes'] += 1

    # -- aberturas (RN-04, D-07) ----------------------------------------------------------------------------------
    @staticmethod
    def _e_abertura(item):
        camada = item.camada.lower()
        return any(p in camada for p in PALAVRAS_DE_ABERTURA)

    def _abertura(self, item):
        ox, oy, oz = origem_da_caixa(item)
        cantos = []
        for x in (0.0, item.largura):
            for y in (0.0, item.profundidade):
                dx, dy = _girar(x, y, item.rotacao)
                cantos.append((ox + dx, oy + dy))
        direcao = _girar(1.0, 0.0, item.rotacao)
        melhor = None
        for parede, segmento, p0, u, sentido, espessura, altura in self.trechos:
            if abs(direcao[0] * u[0] + direcao[1] * u[1]) < 0.9:
                continue
            esquerda = (-u[1], u[0])
            lado = 1 if sentido == 'LEFT' else -1
            s = [(cx - p0[0]) * u[0] + (cy - p0[1]) * u[1] for cx, cy in cantos]
            n = [((cx - p0[0]) * esquerda[0] + (cy - p0[1]) * esquerda[1]) * lado for cx, cy in cantos]
            if not (min(n) < espessura + PERTO_DA_PAREDE and max(n) > -PERTO_DA_PAREDE):
                continue
            x0, x1 = max(min(s), 0.0), min(max(s), segmento['comprimento'])
            z0, z1 = max(oz, 0.0), min(oz + item.altura, altura)
            if x1 - x0 > SOBREPOSICAO_MINIMA and z1 - z0 > SOBREPOSICAO_MINIMA and (melhor is None or x1 - x0 > melhor[0]):
                melhor = (x1 - x0, segmento, x0, x1, z0, z1)
        if melhor is None:
            self._ignorar(item, 'abertura sem trecho de parede compatível; entrou como caixa')
            return False
        _, segmento, x0, x1, z0, z1 = melhor
        ocupadas = [a for a in self.aberturas if a['segmento_id'] == segmento['id']]
        if any(x0 < a['posicao'] + a['largura'] and a['posicao'] < x1 for a in ocupadas):
            self._ignorar(item, 'abertura sobreposta a outra no mesmo trecho; entrou como caixa')
            return False
        self.aberturas.append(dict(id=self.novo_id(), tipo='DOOR' if z0 < PEITORIL_DE_PORTA else 'WINDOW',
                                   segmento_id=segmento['id'], posicao=round(x0, 3), largura=round(x1 - x0, 3),
                                   altura=round(z1 - z0, 3), peitoril=round(z0, 3)))
        self.relatorio['aberturas'] += 1
        return True

    # -- móveis, lajes e malhas (complemento, D-11 e D-30) --------------------------------------------------------
    def _no(self, item, visivel_do_pai, cadeia):
        self._contar(item)
        visivel = visivel_do_pai and item.visivel
        if item.tipo in IGNORADOS:
            self._ignorar(item, IGNORADOS[item.tipo])
            return None
        if item.tipo == 'WALL':
            return None             # tratado antes (paredes e hospedados)
        nome = resolver_macros(item.nome, item)[:160] or item.tipo
        base = dict(nome=nome, promob_id=item.id, tipo_promob=item.tipo, camada=item.camada, visivel=visivel,
                    origem=origem_da_caixa(item), rotacao=item.rotacao,
                    dimensoes=(item.largura, item.profundidade, item.altura))
        if item.tipo == 'GEOMETRY' and len(item.pontos) >= 3:
            contorno = contorno_com_arcos(item.pontos)
            if item.invertido_x:
                contorno = [(-x, y) for x, y in contorno]
            if item.invertido_y:
                contorno = [(x, -y) for x, y in contorno]
            if item.altura > 0 and len(contorno) >= 3:
                laje = dict(base, tipo='laje', origem=item.base, contorno=contorno, altura=item.altura,
                            material=self._material_do_complemento(item.material or item.material_das_faces),
                            filhos=[])
                laje['filhos'] = self._nos(item.filhos, visivel, cadeia + [nome])
                self.relatorio['lajes'] += 1
                return laje
        if item.tipo == 'ENTIDADEEXTERNA' and item.arquivo_3d and min(base['dimensoes']) > 0:
            arquivo = item.arquivo_3d.rsplit('/', 1)[-1]
            entrada = f'{self.projeto.pasta_do_documento}/LinkedFiles/{arquivo}'
            if entrada in self.projeto.entradas:
                self.relatorio['malhas'] += 1
                return dict(base, tipo='malha', entrada=entrada,
                            material=self._material_do_complemento(item.material), filhos=[])
            self._ignorar(item, 'malha vinculada ausente; entrou como caixa')
        filhos = self._nos(item.filhos, visivel, cadeia + [nome])
        if item.filhos:
            self.relatorio['grupos'] += 1
            return dict(base, tipo='grupo', filhos=filhos)
        if min(base['dimensoes']) <= 0:
            self._ignorar(item, 'sem dimensões')
            return None
        self.relatorio['caixas'] += 1
        return dict(base, tipo='caixa', material=self._material_do_complemento(item.material), filhos=[])

    def _nos(self, itens, visivel, cadeia):
        return [n for n in (self._no(i, visivel, cadeia) for i in itens) if n is not None]

    # -- tudo -----------------------------------------------------------------------------------------------------
    def _paredes_do(self, itens, pavimento_id, hospedeiros):
        for item in itens:
            if item.tipo == 'WALL':
                self._parede(item, pavimento_id)
                hospedeiros.append(item)
            self._paredes_do(item.filhos, pavimento_id, hospedeiros)

    def converter(self):
        pavimento_id = self.novo_id()
        hospedeiros = []
        self._paredes_do(self.projeto.itens, pavimento_id, hospedeiros)
        ja_aberturas = set()
        for parede in hospedeiros:
            for h in parede.filhos:
                if h.tipo != 'WALL' and self._e_abertura(h):
                    if self._abertura(h):
                        ja_aberturas.add(id(h))
                        self._contar(h)

        def soltos(itens):
            for item in itens:
                if item.tipo == 'WALL':
                    self._contar(item)
                    yield from soltos([h for h in item.filhos if id(h) not in ja_aberturas])
                else:
                    yield item
        self.moveis = self._nos(list(soltos(self.projeto.itens)), True, [])
        altura = max([s['pe_direito_inicial'] for p in self.paredes for s in p['segmentos']] or [2700])
        agora = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%S.') + '000Z'
        documento = dict(
            schema='caffmob.ambiente/v2', id=self.novo_id(), version=1, atualizado_em=agora, origem='blender',
            nome=(self.projeto.ambiente.nome or 'Projeto Promob')[:160], unidade='mm', eixos='Z_UP',
            configuracao_geometrica=dict(perfil='studio/1', espessuras=dict(caixa=15, porta=18, fundo=6)),
            pavimentos=[dict(id=pavimento_id, nome='Térreo', ordem=0, pe_direito=min(max(altura, 1000), 6000),
                             laje=dict(id=self.novo_id(), ativa=False, tipo='macica', espessura=120, contrapiso=30,
                                       beiral=0, recortes=[]),
                             forro=dict(tipo='nenhum', material='gesso', sanca=None))],
            paredes=self.paredes, aberturas=self.aberturas, modulos=[], pecas_avulsas=[], primitivas=[],
            escadas=[], itens_externos=[], materiais=list(self.materiais_do_documento.values()), camadas=[],
            vinculos=[])
        erros = validar_documento(documento)
        if erros:
            # Uma abertura que o contrato recusa não derruba o projeto: sai e entra no relatório.
            for erro in list(erros):
                caminho = erro.get('caminho', '')
                if caminho.startswith('aberturas['):
                    i = int(caminho[len('aberturas['):].split(']')[0])
                    if i < len(documento['aberturas']):
                        documento['aberturas'][i] = None
            if any(a is None for a in documento['aberturas']):
                removidas = sum(a is None for a in documento['aberturas'])
                documento['aberturas'] = [a for a in documento['aberturas'] if a is not None]
                self.relatorio['aberturas'] -= removidas
                self.relatorio['avisos'].append(f'{removidas} abertura(s) recusada(s) pelas regras do editor de paredes')
                erros = validar_documento(documento)
        return dict(documento=documento, erros=erros, relatorio=self.relatorio,
                    complemento=dict(ambiente=self.projeto.ambiente.nome, moveis=self.moveis,
                                     materiais=self.materiais_do_complemento),
                    cliente=dict(self.projeto.cliente))


def converter(projeto, novo_id=_id):
    """Documento v2 válido, complemento, cliente e relatório. `erros` só vem preenchido se nem as paredes passam."""
    return Conversao(projeto, novo_id).converter()
