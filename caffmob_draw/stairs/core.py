"""Núcleo da escada de marcenaria (071 D-20, RN-07, RN-08), sem bpy.

Portado do construtor de escadas do OpenMob (`crates/openmob-core/src/stairs.rs`, do titular, MIT OR Apache-2.0):
reta, em L ou em U com patamar. O tamanho é a planta (largura × comprimento) e a altura a vencer; os espelhos seguem
uma altura confortável (cerca de 175 mm) e os pisos dividem o comprimento. Peças: degraus, espelhos (opcionais),
laterais em degraus (opcionais), patamar com base e corrimão. O giro à esquerda espelha a escada em X (o OpenMob só
gira à direita). Medidas em mm.
"""
import math
from dataclasses import asdict, dataclass

TIPOS = ('reta', 'L', 'U')
GIROS = ('direita', 'esquerda')
LIMITES = dict(altura=(300, 6000), largura=(500, 3000), largura_total=(500, 6000), comprimento=(500, 9000),
               degrau=(15, 100), vao=(0, 1000))
ESPELHO_CONFORTAVEL = 175.0
ESPESSURA_DO_ESPELHO = 18.0
ESPESSURA_DA_LATERAL = 30.0
SOBREPOSICAO_DO_DEGRAU = 20.0
BLONDEL_CONFORTAVEL = (600.0, 660.0)
ESPELHO_MAXIMO = 190.0


def _limitar(valor, chave):
    lo, hi = LIMITES[chave]
    return min(max(float(valor), lo), hi)


@dataclass
class Escada:
    tipo: str = 'reta'
    giro: str = 'direita'
    largura: float = 900.0         # do lance
    degrau: float = 40.0           # espessura do degrau
    espelhos: bool = True
    laterais: bool = True
    corrimao: bool = True
    vao: float = 100.0             # entre os lances do U
    x: float = 900.0               # planta: largura total
    y: float = 3990.0              # planta: comprimento
    z: float = 2800.0              # altura a vencer
    material_frente: str = ''
    material_corpo: str = ''

    def normalizada(self):
        e = Escada(**asdict(self))
        e.tipo = e.tipo if e.tipo in TIPOS else 'reta'
        e.giro = e.giro if e.giro in GIROS else 'direita'
        e.largura, e.degrau, e.vao = _limitar(e.largura, 'largura'), _limitar(e.degrau, 'degrau'), _limitar(e.vao, 'vao')
        e.z, e.y = _limitar(e.z, 'altura'), _limitar(e.y, 'comprimento')
        e.x = e.largura if e.tipo == 'reta' else max(_limitar(e.x, 'largura_total'), e.largura)
        return e

    def para_dict(self):
        d = asdict(self)
        d['versao'] = 1
        return d

    @classmethod
    def de_dict(cls, d):
        campos = {k: d[k] for k in cls.__dataclass_fields__ if k in (d or {})}
        return cls(**campos).normalizada()


def _espelhos(altura):
    return max(int(math.floor(altura / ESPELHO_CONFORTAVEL + 0.5)), 2)


def planta_confortavel(e):
    """(largura total, comprimento) com piso confortável (Blondel 630 mm) para a altura (`footprint`)."""
    n = _espelhos(e.z)
    espelho = e.z / n
    piso = min(max(630.0 - 2 * espelho, 220.0), 340.0)
    pisos = n - 1
    w = e.largura
    if e.tipo == 'reta':
        return w, pisos * piso
    t1 = math.ceil(pisos / 2)
    if e.tipo == 'L':
        return w + max(pisos - t1 - 1, 0) * piso, t1 * piso + w
    return 2 * w + e.vao, t1 * piso + w


@dataclass
class Plano:
    espelhos: int
    espelho: float
    piso: float
    blondel: float

    @property
    def confortavel(self):
        return BLONDEL_CONFORTAVEL[0] <= self.blondel <= BLONDEL_CONFORTAVEL[1] and self.espelho <= ESPELHO_MAXIMO


def plano(e):
    """Degraus para o tamanho da escada (`plan`)."""
    n = _espelhos(e.z)
    espelho = e.z / n
    pisos = n - 1
    w = min(e.largura, e.x)
    if e.tipo == 'reta':
        piso = e.y / pisos
    else:
        piso = max((e.y - w) / math.ceil(pisos / 2), 100.0)
    return Plano(n, espelho, piso, 2 * espelho + piso)


def leitura(e):
    p = plano(e)
    return p, f"{p.espelhos} espelhos de {p.espelho:.0f} mm · piso de {p.piso:.0f} mm · Blondel {p.blondel:.0f} mm"


def medidas_sao_confortaveis(e):
    x, y = planta_confortavel(e)
    return abs(x - e.x) <= 0.5 and abs(y - e.y) <= 0.5


def _lance(c, saida, primeiro, n, sentido, x0, y0, z0):
    espelho, piso, w, t, lado = c['espelho'], c['piso'], c['w'], c['t'], c['lado']
    for i in range(n):
        k = primeiro + i + 1
        z = z0 + espelho * (i + 1)
        if sentido == 'sobe':
            degrau = ((x0 + lado, y0 + i * piso, z - t), (w - 2 * lado, piso + SOBREPOSICAO_DO_DEGRAU, t))
            frente = ((x0 + lado, y0 + i * piso, z - espelho), (w - 2 * lado, ESPESSURA_DO_ESPELHO, espelho - t))
            coluna = lambda off: ((x0 + off, y0 + i * piso, 0.0), (lado, piso, z))
        elif sentido == 'desce':
            degrau = ((x0 + lado, y0 - (i + 1) * piso - SOBREPOSICAO_DO_DEGRAU, z - t),
                      (w - 2 * lado, piso + SOBREPOSICAO_DO_DEGRAU, t))
            frente = ((x0 + lado, y0 - i * piso - ESPESSURA_DO_ESPELHO, z - espelho),
                      (w - 2 * lado, ESPESSURA_DO_ESPELHO, espelho - t))
            coluna = lambda off: ((x0 + off, y0 - (i + 1) * piso, 0.0), (lado, piso, z))
        else:   # 'direita': sobe ao longo de +x
            degrau = ((x0 + i * piso, y0 + lado, z - t), (piso + SOBREPOSICAO_DO_DEGRAU, w - 2 * lado, t))
            frente = ((x0 + i * piso, y0 + lado, z - espelho), (ESPESSURA_DO_ESPELHO, w - 2 * lado, espelho - t))
            coluna = None
        saida.append(dict(nome=f'Degrau {k}', papel='degrau', material='frente', indice=k, pos=degrau[0], tam=degrau[1]))
        if c['espelhos']:
            saida.append(dict(nome=f'Espelho {k}', papel='espelho', material='corpo', indice=k, pos=frente[0],
                              tam=frente[1]))
        if lado > 0:
            for off in (0.0, w - lado):
                if sentido == 'direita':
                    pos, tam = (x0 + i * piso, y0 + off, 0.0), (piso, lado, z)
                else:
                    pos, tam = coluna(off)
                saida.append(dict(nome='Lateral da escada', papel='lateral', material='corpo', indice=k, pos=pos,
                                  tam=tam))


def pecas(e):
    """Peças da escada (`build`): lista de dicts e o comprimento do corrimão em mm (0 sem corrimão)."""
    e = e.normalizada()
    p = plano(e)
    pisos = p.espelhos - 1
    c = dict(espelho=p.espelho, piso=p.piso, w=min(e.largura, e.x), t=e.degrau,
             lado=ESPESSURA_DA_LATERAL if e.laterais else 0.0, espelhos=e.espelhos)
    w, t, piso, espelho = c['w'], c['t'], c['piso'], c['espelho']
    saida = []
    if e.tipo == 'reta':
        _lance(c, saida, 0, pisos, 'sobe', 0.0, 0.0, 0.0)
        percurso = math.hypot(pisos * piso, e.z)
    else:
        t1 = math.ceil(pisos / 2)
        t2 = pisos - t1 - 1                # o patamar ocupa um degrau
        _lance(c, saida, 0, t1, 'sobe', 0.0, 0.0, 0.0)
        zl = espelho * (t1 + 1)
        ly = t1 * piso
        cheio = 2 * w + e.vao if e.tipo == 'U' else w
        saida.append(dict(nome='Patamar', papel='patamar', material='frente', indice=t1 + 1, pos=(0.0, ly, zl - t),
                          tam=(cheio, w, t)))
        if c['lado'] > 0:
            saida.append(dict(nome='Base do patamar', papel='base_patamar', material='corpo', indice=t1 + 1,
                              pos=(0.0, ly, 0.0), tam=(cheio, w, zl - t)))
        if e.tipo == 'L':
            _lance(c, saida, t1 + 1, t2, 'direita', w, ly, zl)
        else:
            _lance(c, saida, t1 + 1, t2, 'desce', w + e.vao, ly, zl)
        percurso = math.hypot(t1 * piso, zl) + math.hypot(t2 * piso, e.z - zl) + cheio
    saida = [s for s in saida if min(s['tam']) > 0.5]
    if e.giro == 'esquerda':
        for s in saida:
            s['pos'] = (e.x - s['pos'][0] - s['tam'][0], s['pos'][1], s['pos'][2])
    return saida, (percurso if e.corrimao else 0.0)


def registros(saida):
    """Peças para o plano de corte: comprimento ≥ largura ≥ espessura (a menor medida é a espessura)."""
    out = []
    for s in saida:
        espessura, largura, comprimento = sorted(s['tam'])
        out.append(dict(nome=s['nome'], papel=s['papel'], material=s['material'], indice=s['indice'],
                        comprimento=comprimento, largura=largura, espessura=espessura))
    return out
