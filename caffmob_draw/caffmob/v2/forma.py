"""Forma fechada de shared/studio/validacao.ts; não aplica defaults nem coerções."""
import math
import re
from datetime import datetime
from .contrato import (
    MATERIAIS_DE_ABERTURA,
    MODELOS_DE_ABERTURA,
    MODELOS_DE_JANELA,
    MODELOS_DE_PORTA,
)


def numero(minimo=-math.inf, maximo=math.inf, inteiro=False, positivo=False):
    def conferir(v):
        if type(v) not in (float, int):
            return False
        try:
            return math.isfinite(v) and minimo <= v <= maximo and (not inteiro or int(v) == v) and (not positivo or v > 0)
        except OverflowError:
            return False
    conferir.limites = (minimo, maximo, inteiro, positivo)
    return conferir



def enum(*valores):
    return lambda v: type(v) is type(valores[0]) and v in valores


def texto(maximo=160):
    return ('nome', maximo)


def opcional(forma):
    return ("opcional", forma)


def anulavel(forma):
    return ("anulavel", forma)


def lista(forma, minimo=0, maximo=math.inf):
    return ("lista", forma, minimo, maximo)


def uniao(campo, formas):
    return ("uniao", campo, formas)


UUID = lambda v: isinstance(v, str) and re.fullmatch('[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}', v) is not None
N = numero()
P = numero(positivo=True)
NN = numero(0)
I = numero(0, 9007199254740991, inteiro=True)
B = lambda v: type(v) is bool
PONTO2 = dict(x=N, y=N)
PONTO3 = dict(x=N, y=N, z=N)
DIMENSOES = dict(largura=P, profundidade=P, altura=P)
COMUM = dict(
    id=UUID,
    nome=texto(),
    pavimento_id=UUID,
    camada_id=anulavel(UUID),
    visivel=B,
    posicao=PONTO3,
    rotacao_z=N,
)
RB = dict(id=UUID, posicao=PONTO2, escada_id=opcional(UUID))
RECORTE = uniao(
    'forma',
    dict(
        retangular={**RB, 'forma': enum('retangular'), 'largura': P, 'altura': P},
        circular={**RB, 'forma': enum('circular'), 'diametro': P},
    ),
)
LAJE = dict(
    material_id=opcional(UUID),
    id=UUID,
    ativa=B,
    tipo=enum('macica', 'trelicada', 'nervurada', 'steel_deck'),
    espessura=numero(60, 500),
    contrapiso=numero(0, 150),
    beiral=numero(0, 2000),
    contorno=opcional(lista(PONTO2, 3, 400)),
    recortes=lista(RECORTE),
)
SANCA = dict(tipo=enum('fechada', 'aberta', 'invertida'), largura=numero(100, 1500), rebaixo=numero(30, 800), led=B)
FORRO = uniao(
    'tipo',
    {t: dict(tipo=enum(t), material=enum('gesso', 'drywall', 'pvc', 'madeira'), material_id=opcional(UUID), sanca=SANCA if t == 'sanca' else lambda v: v is None) for t in ('nenhum', 'liso', 'sanca')},
)
CONSTRUCAO = dict(
    laterais=enum('PASSANTE', 'SOBRE_A_BASE'),
    tampo=enum('ENTRE_LATERAIS', 'SOBREPOSTO'),
    fundo=dict(modo=enum('CANAL', 'REBAIXADO', 'SOBREPOSTO'), espessura=NN, encaixe=NN),
    rodape=dict(altura=NN, recuo=NN),
    porta=dict(modo=enum('SOBREPOSTA', 'EMBUTIDA'), folga=NN, folga_central=NN, espessura=NN),
    prateleiras=dict(quantidade=I, recuo_frontal=NN, folga_lateral=NN, espessura=NN),
    divisorias=dict(quantidade=I),
    gavetas=dict(quantidade=I, altura_frente=NN),
    travessas=dict(quantidade=I, largura=NN),
    fitas=dict(frente=NN, demais=NN, portas=NN),
)
EDICAO = dict(
    papel=enum(
              'LATERAL_ESQUERDA',
              'LATERAL_DIREITA',
              'BASE',
              'TAMPO',
              'FUNDO',
              'PRATELEIRA',
              'DIVISORIA',
              'PORTA',
              'FRENTE_DE_GAVETA',
              'RODAPE',
              'TRAVESSA',
          ),
    indice=I,
    largura=opcional(P),
    altura=opcional(P),
    espessura=opcional(P),
    veio=opcional(enum('NONE', 'VERTICAL', 'HORIZONTAL')),
    textura_id=opcional(UUID),
)
PARAMETROS = dict(
    tipo=enum('BASE', 'WALL', 'TALL'),
    largura=N,
    altura=N,
    profundidade=N,
    espessura=N,
    material=enum('MDF', 'MDP', 'WOOD'),
    portas=enum('NONE', 'LEFT', 'RIGHT', 'DOUBLE', 'FLIP'),
    construcao=CONSTRUCAO,
    chapas_editadas=lista(EDICAO),
    plano_pai=dict(tipo=enum('FLOOR', 'WALL', 'MODULE'), id=anulavel(UUID)),
    modelo=opcional(
               dict(
                   id=UUID,
                   version=numero(1, 9007199254740991, inteiro=True),
                   escopo=enum('titular', 'pessoal'),
               ),
           ),
)
SEGMENTO = dict(
    id=UUID,
    comprimento=P,
    angulo_absoluto=N,
    angulo_relativo=N,
    espessura=P,
    pe_direito_inicial=P,
    pe_direito_final=P,
    afastamento=NN,
    flecha=N,
    sentido=enum('LEFT', 'RIGHT'),
    tipo=enum('NORMAL', 'DRYWALL', 'GLASS'),
    estado=enum('ativo', 'oculto'),
    material_interno_id=opcional(UUID),
    material_externo_id=opcional(UUID),
)
CONFIGURACAO = dict(perfil=enum('studio/1'), espessuras=dict(caixa=numero(3, 50), porta=numero(3, 50), fundo=numero(2, 30)))


def data(v):
    if not isinstance(v, str) or not re.match(r'^\d{4}-\d\d-\d\dT', v):
        return False
    try:
        # Date.parse também normaliza dias excedentes de meses curtos.
        from datetime import timedelta
        base = datetime.fromisoformat(v[:8] + '01' + v[10:].replace('Z', '+00:00'))
        return 1 <= int(v[8:10]) <= 31 and bool(base + timedelta(days=int(v[8:10]) - 1))
    except (ValueError, OverflowError):
        return False


def matriz(v):
    return isinstance(v, list) and len(v) == 16 and all(N(x) for x in v) and v[12:] == [0, 0, 0, 1]


DOCUMENTO = dict(
    schema=enum('caffmob.ambiente/v2'),
    id=UUID,
    version=numero(1, 9007199254740991, inteiro=True),
    atualizado_em=data,
    origem=enum('web', 'mobile', 'blender'),
    nome=texto(),
    unidade=enum('mm'),
    eixos=enum('Z_UP'),
    configuracao_geometrica=CONFIGURACAO,
    pavimentos=lista(
                   dict(
                       id=UUID,
                       nome=texto(40),
                       ordem=I,
                       pe_direito=numero(1000, 6000),
                       piso_material_id=opcional(UUID),
                       laje=LAJE,
                       forro=FORRO,
                   ),
                   1,
               ),
    paredes=lista(
                dict(
                    id=UUID,
                    origem=PONTO2,
                    fechada=B,
                    pavimento_id=UUID,
                    camada_id=anulavel(UUID),
                    visivel=B,
                    material_id=opcional(UUID),
                    perfil=enum('studio/1', 'caffmob.parede/v1'),
                    segmentos=lista(SEGMENTO, 1),
                ),
            ),
    aberturas=lista(
                  dict(
                      id=UUID,
                      tipo=enum('DOOR', 'WINDOW'),
                      segmento_id=UUID,
                      posicao=NN,
                      largura=P,
                      altura=P,
                      peitoril=NN,
                      modelo=opcional(enum(*MODELOS_DE_ABERTURA)),
                      material=opcional(enum(*MATERIAIS_DE_ABERTURA)),
                  ),
              ),
    modulos=lista({**COMUM, 'perfil_construcao': enum('caffmob.modulo/v1'), 'parametros': PARAMETROS}),
    pecas_avulsas=lista(
                      {
                          **COMUM,
                          'papel': enum(
                              'lateral',
                              'prateleira',
                              'tampo',
                              'fundo',
                              'painel',
                              'porta',
                              'rodape',
                              'livre',
                          ),
                          'dimensoes': DIMENSOES,
                          'espessura': numero(2, 150),
                          'material_id': anulavel(UUID),
                          'veio': enum('NONE', 'VERTICAL', 'HORIZONTAL'),
                          'fitas': dict(topo=NN, base=NN, esquerda=NN, direita=NN),
                          'recortes': lista(RECORTE),
                      },
                  ),
    primitivas=lista(
                   uniao(
                       'forma',
                       {t: {**COMUM, 'forma': enum(t), **(dict(diametro=P, altura=P) if t == 'cilindro' else dict(dimensoes=DIMENSOES)), 'material_id': anulavel(UUID)} for t in ('caixa', 'placa', 'cilindro')},
                   ),
               ),
    escadas=lista(
                {
                    **COMUM,
                    'tipo': enum('reta', 'L', 'U'),
                    'altura': numero(300, 6000),
                    'largura': numero(600, 2000),
                    'espelho_alvo': numero(150, 200),
                    'material': enum('concreto', 'porcelanato', 'madeira'),
                    'laje_id': anulavel(UUID),
                    'furo_id': opcional(UUID),
                },
            ),
    itens_externos=lista(
                       {
                           **COMUM,
                           'forma': enum('caixa'),
                           'dimensoes': DIMENSOES,
                           'origem_tipo': enum('externo_blender'),
                           'transformacao_origem': opcional(('matriz',)),
                       },
                   ),
    materiais=lista(
                  uniao(
                      'tipo',
                      dict(
                          textura=dict(
                                      id=UUID,
                                      nome=texto(),
                                      tipo=enum('textura'),
                                      textura_id=UUID,
                                      escala_mm=opcional(
                                                    dict(
                                                        largura=numero(1, 10000, inteiro=True),
                                                        altura=numero(1, 10000, inteiro=True),
                                                    ),
                                                ),
                                      rotacao=opcional(
                                                  lambda v: type(v) in (int, float) and v in (0, 90, 180, 270),
                                              ),
                                  ),
                          cor=dict(
                                  id=UUID,
                                  nome=texto(),
                                  tipo=enum('cor'),
                                  cor=lambda v: isinstance(v, str) and re.fullmatch('#[0-9a-fA-F]{6}', v) is not None,
                                  classe_visual=enum(
                                                    'mdf',
                                                    'madeira',
                                                    'vidro',
                                                    'metal',
                                                    'concreto',
                                                    'gesso',
                                                    'pvc',
                                                    'porcelanato',
                                                ),
                              ),
                      ),
                  ),
              ),
    camadas=lista(
                dict(
                    id=UUID,
                    nome=texto(80),
                    categoria=enum(
                                  'ambiente',
                                  'cozinhas_inferiores',
                                  'portas_cozinha',
                                  'superiores',
                                  'caixas_dormitorio',
                                  'portas_dormitorio',
                                  'decore',
                                  'geometria',
                                  'paredes',
                                  'piso',
                                  'teto',
                              ),
                    pavimento_id=anulavel(UUID),
                    visivel=B,
                ),
            ),
    vinculos=lista(
                 dict(
                     id=UUID,
                     origem_id=UUID,
                     destino=dict(tipo=enum('modulo', 'segmento', 'piso'), id=UUID),
                     deslocamento_mundial=PONTO3,
                     lado=enum('esquerda', 'direita', 'cima', 'baixo', 'frente', 'atras'),
                     afastamento=numero(0, 5000),
                 ),
             ),
)

JS_TRIM = '\t\n\v\f\r \u00a0\u1680\u2000\u2001\u2002\u2003\u2004\u2005\u2006\u2007\u2008\u2009\u200a\u2028\u2029\u202f\u205f\u3000\ufeff'
MISSING = object()


def erros_da_forma(valor, forma=DOCUMENTO, caminho=''):
    erros = []
    def erro(p, desconhecido=False):
        erros.append(dict(caminho=p or 'documento', codigo='CAMPO_DESCONHECIDO' if desconhecido else 'ESQUEMA', mensagem='Campo não declarado no contrato desta fatia.' if desconhecido else 'Valor fora do formato, enumeração ou faixa permitida.'))
    def conferir(v, f, p):
        if isinstance(f, dict):
            if not isinstance(v, dict):
                erro(p)
                return
            for k, s in f.items():
                conferir(v.get(k, MISSING), s, f'{p}.{k}' if p else k)
            for k in v:
                if k not in f:
                    erro(f'{p}.{k}' if p else k, True)
        elif isinstance(f, tuple):
            t = f[0]
            if t == 'opcional':
                if v is not MISSING:
                    conferir(v, f[1], p)
            elif t == 'anulavel':
                if v is not None:
                    conferir(v, f[1], p)
            elif t == 'lista':
                if not isinstance(v, list):
                    erro(p)
                    return
                for i, x in enumerate(v):
                    conferir(x, f[1], f'{p}[{i}]')
                if not f[2] <= len(v) <= f[3]:
                    erro(p)
            elif t == 'nome':
                if not isinstance(v, str):
                    erro(p)
                else:
                    tamanho = len(v.encode('utf-16-le', errors='surrogatepass')) // 2
                    if tamanho < 1 or tamanho > f[1]:
                        erro(p)
                    if not v.strip(JS_TRIM):
                        erro(p)
            elif t == 'matriz':
                # Zod: erros individuais de tipo, depois comprimento e refine.
                conferir(v, lista(N, 16, 16), p)
                if isinstance(v, list) and all(N(x) for x in v) and v[12:16] != [0, 0, 0, 1]:
                    erro(p)
            elif not isinstance(v, dict):
                erro(p)
            else:
                escolha = v.get(f[1])
                if not isinstance(escolha, str) or escolha not in f[2]:
                    erro(f'{p}.{f[1]}' if p else f[1])
                else:
                    conferir(v, f[2][escolha], p)
        elif hasattr(f, 'limites'):
            minimo, maximo, inteiro, positivo = f.limites
            if not N(v) or (inteiro and int(v) != v):
                erro(p)
            else:
                if inteiro and abs(v) > 9007199254740991:
                    erro(p)
                if v < minimo or v > maximo or (positivo and v <= 0):
                    erro(p)
        elif not f(v):
            erro(p)
    conferir(valor, forma, caminho)
    if forma is DOCUMENTO and isinstance(valor, dict) and isinstance(valor.get('aberturas'), list):
        for i, a in enumerate(valor['aberturas']):
            if isinstance(a, dict) and 'modelo' in a and a.get('tipo') in ('DOOR', 'WINDOW') and a['modelo'] in MODELOS_DE_ABERTURA:
                permitidos = MODELOS_DE_PORTA if a['tipo'] == 'DOOR' else MODELOS_DE_JANELA
                if a['modelo'] not in permitidos:
                    erro(f'aberturas[{i}].modelo')
    return erros
