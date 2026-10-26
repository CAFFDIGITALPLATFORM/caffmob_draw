"""Núcleo da gaveta (072 D-01, D-03, RN-02 a RN-09), sem bpy.

Do espaço livre do vão, do spec da gaveta e da corrediça saem as alturas das frentes e as peças da caixa de cada
gaveta, ou os motivos da recusa. As regras vêm dos guias do titular: desconto lateral pela corrediça, laterais com o
comprimento nominal, contra-frente e traseira = largura da gaveta − 2 laterais, fundo em canal (ou parafusado no
gavetão), fundo recuado e furo na traseira da oculta, só fundo e costas na lateral metálica. Medidas em mm; o
referencial da caixa tem x na largura, y na profundidade (a partir da face de trás da frente) e z na altura.
"""
from dataclasses import asdict, dataclass, field

from . import catalogo

PUXADORES = ('externo', 'cava', 'sem')
FUNDOS = ('canal', 'parafusado')
FOLGA_TRASEIRA = 10.0         # mm entre o fim da corrediça e o fundo do vão
LARGURA_MINIMA = 100.0
ALTURA_MINIMA_DA_CAIXA = 50.0
FRENTE_DA_CAVA = 18.0
RECUO_DO_TOQUE = (3.0, 5.0)


@dataclass
class Espaco:
    largura: float
    altura: float
    profundidade: float


@dataclass
class Gaveta:
    corredica: str = 'telescopica'
    comprimento: float = 0.0          # 0 = o maior que cabe (RN-06)
    frente_espessura: float = 18.0
    puxador: str = 'externo'
    recuo_toque: float = 4.0
    lateral: float = 15.0
    contra_frente: float = 15.0
    fundo: float = 6.0
    fundo_tipo: str = 'canal'
    canal_profundidade: float = 4.0
    canal_da_borda: float = 8.0
    folga_superior: float = 30.0
    folga_inferior: float = 10.0
    modelo: str = ''

    def para_dict(self):
        d = asdict(self)
        d['versao'] = 1
        return d

    @classmethod
    def de_dict(cls, d):
        return cls(**{k: d[k] for k in cls.__dataclass_fields__ if k in (d or {})})


@dataclass
class Caixa:
    largura: float                    # largura externa da gaveta (vão − folga)
    altura: float
    comprimento: float                # comprimento nominal da corrediça
    recuo: float                      # deslocamento em y a partir da frente (toque)
    deslocamento_x: float             # da face esquerda do vão à face esquerda da gaveta
    pecas: list = field(default_factory=list)


def comprimento_que_cabe(profundidade, corredica):
    """Maior comprimento nominal ≤ profundidade livre − folga traseira (RN-06); None se nenhum cabe."""
    cabem = [c for c in corredica.comprimentos if c <= profundidade - FOLGA_TRASEIRA + 1e-6]
    return max(cabem) if cabem else None


def dividir_altura(altura, n, folga):
    """N frentes iguais com a folga entre elas (RN-09)."""
    n = max(int(n), 1)
    cada = (altura - folga * (n - 1)) / n
    return [cada] * n


def motivos(espaco, gaveta, corredica, altura_da_frente=None):
    """Motivos (texto, com as medidas) de a gaveta não caber; lista vazia se cabe (RN-01, RN-06 a RN-08)."""
    erros = []
    if corredica is None:
        return ["Corrediça desconhecida."]
    menor = min(corredica.comprimentos)
    if comprimento_que_cabe(espaco.profundidade, corredica) is None:
        erros.append(f"Profundidade livre de {espaco.profundidade:.0f} mm é menor que a menor corrediça "
                     f"({menor} mm).")
    elif gaveta.comprimento and gaveta.comprimento > espaco.profundidade - FOLGA_TRASEIRA + 1e-6:
        erros.append(f"A corrediça de {gaveta.comprimento:.0f} mm não cabe na profundidade livre de "
                     f"{espaco.profundidade:.0f} mm.")
    largura = espaco.largura - corredica.folga_total
    if largura < LARGURA_MINIMA:
        erros.append(f"Largura livre de {espaco.largura:.0f} mm é pequena para a corrediça "
                     f"(desconto de {corredica.folga_total:.0f} mm).")
    if corredica.lateral_max and corredica.laterais_mdf and gaveta.lateral > corredica.lateral_max + 1e-6:
        erros.append(f"A {corredica.nome.lower()} aceita lateral de até {corredica.lateral_max:.0f} mm; a gaveta tem "
                     f"{gaveta.lateral:.0f} mm. Use laterais de 15 mm.")
    altura = altura_da_frente if altura_da_frente is not None else espaco.altura
    if altura - gaveta.folga_superior - gaveta.folga_inferior < ALTURA_MINIMA_DA_CAIXA:
        erros.append(f"Altura de {altura:.0f} mm é pequena para a caixa da gaveta.")
    if gaveta.puxador == 'cava' and gaveta.frente_espessura < FRENTE_DA_CAVA:
        erros.append(f"Puxador cava exige frente de 18 ou 22 mm; a frente tem {gaveta.frente_espessura:.0f} mm.")
    if corredica.toque and not RECUO_DO_TOQUE[0] <= gaveta.recuo_toque <= RECUO_DO_TOQUE[1]:
        erros.append("A corrediça de toque pede recuo de 3 a 5 mm.")
    return erros


def _peca(nome, papel, pos, tam, furos=()):
    return dict(nome=nome, papel=papel, pos=tuple(pos), tam=tuple(tam), furos=list(furos))


def caixa(espaco, gaveta, corredica, altura_da_frente):
    """Peças da caixa de uma gaveta (RN-02 a RN-05). Levanta ValueError com os motivos se não cabe."""
    erros = motivos(espaco, gaveta, corredica, altura_da_frente)
    if erros:
        raise ValueError(' '.join(erros))
    comprimento = gaveta.comprimento or comprimento_que_cabe(espaco.profundidade, corredica)
    largura = espaco.largura - corredica.folga_total
    altura = altura_da_frente - gaveta.folga_superior - gaveta.folga_inferior
    recuo = gaveta.recuo_toque if corredica.toque else 0.0
    x0, y0, z0 = 0.0, recuo, gaveta.folga_inferior
    c = Caixa(largura=largura, altura=altura, comprimento=comprimento, recuo=recuo,
              deslocamento_x=corredica.folga_total / 2)
    if corredica.laterais_mdf:
        e = gaveta.lateral
        c.pecas.append(_peca("Lateral da gaveta", 'lateral', (x0, y0, z0), (e, comprimento, altura)))
        c.pecas.append(_peca("Lateral da gaveta", 'lateral', (x0 + largura - e, y0, z0), (e, comprimento, altura)))
    else:
        e = corredica.lateral_fabrica
    interna = largura - 2 * e
    cf = gaveta.contra_frente
    furos = [dict(diametro=corredica.furo_traseira, x=interna / 2, z=corredica.recuo_fundo / 2)] \
        if corredica.furo_traseira else []
    if corredica.laterais_mdf:
        c.pecas.append(_peca("Contra-frente da gaveta", 'contra_frente', (x0 + e, y0, z0), (interna, cf, altura)))
    c.pecas.append(_peca("Traseira da gaveta", 'traseira', (x0 + e, y0 + comprimento - cf, z0), (interna, cf, altura),
                         furos))
    if gaveta.fundo_tipo == 'parafusado' or not corredica.laterais_mdf:
        espessura = gaveta.fundo if corredica.laterais_mdf else max(gaveta.fundo, 16.0)
        z_fundo = z0 + (corredica.recuo_fundo if corredica.tipo == 'oculta' else 0.0)
        c.pecas.append(_peca("Fundo da gaveta", 'fundo', (x0 + e, y0 + (cf if corredica.laterais_mdf else 0.0), z_fundo),
                             (interna, comprimento - (2 * cf if corredica.laterais_mdf else cf), espessura)))
    else:
        p = gaveta.canal_profundidade
        borda = corredica.recuo_fundo if corredica.tipo == 'oculta' else gaveta.canal_da_borda
        c.pecas.append(_peca("Fundo da gaveta", 'fundo', (x0 + e - p, y0 + cf - p, z0 + borda),
                             (interna + 2 * p, comprimento - 2 * cf + 2 * p, gaveta.fundo)))
    return c


def gavetas(espaco, gaveta, corredica, n, folga_entre_frentes):
    """Alturas das frentes e caixas das N gavetas no espaço; levanta ValueError com os motivos."""
    alturas = dividir_altura(espaco.altura, n, folga_entre_frentes)
    return [(h, caixa(espaco, gaveta, corredica, h)) for h in alturas]


def registros(c, uid=''):
    """Peças da caixa para o plano de corte: comprimento ≥ largura ≥ espessura, com os furos."""
    out = []
    for i, p in enumerate(c.pecas):
        espessura, largura, comprimento = sorted(p['tam'])
        out.append(dict(nome=p['nome'], papel=p['papel'], indice=i, comprimento=comprimento, largura=largura,
                        espessura=espessura, furos=p['furos'], uid=f"{uid}/{p['papel']}/{i}"))
    return out


def trocar_corredica(espaco, gaveta, nova, altura_da_frente):
    """Spec novo com a corrediça trocada (RN-07): o comprimento volta ao automático; ValueError se não cabe."""
    novo = Gaveta(**{**asdict(gaveta), 'corredica': nova.id, 'comprimento': 0.0})
    caixa(espaco, novo, nova, altura_da_frente)
    return novo


def corredica_de(gaveta, pasta=None):
    return catalogo.por_id(gaveta.corredica, pasta)
