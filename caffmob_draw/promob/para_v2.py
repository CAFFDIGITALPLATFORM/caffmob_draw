"""Do projeto `.promob` lido ao documento do CAFF MOBI v2 e ao complemento local (071 D-05 a D-11, D-30), sem bpy.

- Paredes e aberturas vão para o documento v2 (RN-10): ganham o Editor de Paredes, o painel por seleção e o envio
  ao MOBI.
- Móveis, lajes livres e malhas vinculadas vão para o complemento, que só existe no `.blend` (D-30): o contrato
  do v2 aceita no máximo 300 entidades posicionáveis, e um ambiente do Promob passa disso.
"""
import ast
import dataclasses
import json
import math
import os
import re
import uuid
from datetime import datetime, timezone

from ..caffmob.contrato import normalizar_relativo
from ..caffmob.v2.validacao import validar_documento
from ..texture_library import pbr_core
from . import texturas

PERTO_DA_PAREDE = 60.0          # mm que a porta pode ficar fora da face (RN-04)
SOBREPOSICAO_MINIMA = 50.0
PEITORIL_DE_PORTA = 100.0       # abaixo disso a abertura é porta (D-07)
TRECHO_MINIMO = 50.0            # o contrato v2 recusa trecho menor
IGNORADOS = {'Teto': 'forro', 'LuzSpot': 'luz', 'LuzAmbiente': 'luz'}
PALAVRAS_DE_ABERTURA = ('abert', 'janel', 'portai')
SOBRA_RELATIVA = 20.0           # mm que o ângulo relativo ao pai precisa poupar para valer
AUXILIAR = 10.0                 # mm: folha sem componente até esse tamanho é marcador do Promob (furo, "Sem Puxador")
MOLDURA = 60.0                  # mm: montante da porta com vidro, que o catálogo desenharia e não vem no arquivo
VIDRO = 8.0                     # mm: espessura do vidro desenhado dentro da moldura
VAO_DE_VIDRO = 0.4              # fração da face do pai que um vidro filho ocupa para o pai virar moldura
FORMAS = ('torneira', 'cuba')   # louças e metais do catálogo desenhados com silhueta, não caixa
_CORES_DA_CLASSE = {'vidro': (0xA9, 0xC7, 0xC4), 'espelho': (0xD8, 0xDE, 0xE2), 'metal': (0x9A, 0x9D, 0xA0),
                    'cro': (0xD0, 0xD2, 0xD4), 'alu': (0xB8, 0xBB, 0xBE), 'ino': (0xA9, 0xAC, 0xAE)}


def _id():
    return str(uuid.uuid4())


def _cor_hex(rgb):
    return '#%02x%02x%02x' % tuple(rgb)


# -- referencial do item (071, correção da importação de armários e peças em outras superfícies) ----------------------
#
# Conferido nos projetos do titular:
# - `LIMITS` traz a caixa do item no referencial dele, a partir do ponto base. Nem sempre é x ∈ [0, W], y ∈ [−D, 0],
#   z ∈ [0, H]: peças espelhadas têm x ∈ [−W, 0] e ferragens centradas têm z ∈ [−H/2, H/2];
# - `NORMAL` (A, B, C) é o eixo da altura do item (z local). Com a normal horizontal, a largura parte de −Z e gira pelo
#   ângulo do item em torno da normal; a profundidade é normal × largura. Com a normal para baixo, o item é o espelho
#   do comum (largura e profundidade giradas, altura para baixo). Os OBJ vinculados vêm nesse mesmo referencial;
# - quando a peça tem pai, vale, entre as orientações possíveis, a que a mantém dentro do pai.

def _sub(a, b):
    return tuple(a[k] - b[k] for k in range(3))


def _cruz(a, b):
    return (a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0])


def _escala(a, s):
    return tuple(v * s for v in a)


def _soma(*vs):
    return tuple(sum(v[k] for v in vs) for k in range(3))


def _unit(a):
    n = math.sqrt(sum(v * v for v in a)) or 1.0
    return tuple(v / n for v in a)


def _girar_em(eixo, v, graus):
    """Rodrigues: `v` girado `graus` em torno de `eixo` (unitário)."""
    t = math.radians(graus)
    c, s = math.cos(t), math.sin(t)
    d = sum(eixo[k] * v[k] for k in range(3))
    x = _cruz(eixo, v)
    return tuple(v[k] * c + x[k] * s + eixo[k] * d * (1 - c) for k in range(3))


_EIXOS = ((1, 0, 0), (-1, 0, 0), (0, 1, 0), (0, -1, 0), (0, 0, 1), (0, 0, -1))


def _candidatos(item):
    """Referenciais possíveis (X, Y, Z) do item, o preferido primeiro."""
    if item.normal is None:
        x = (math.cos(math.radians(item.rotacao)), math.sin(math.radians(item.rotacao)), 0.0)
        return [(x, _cruz((0, 0, 1), x), (0.0, 0.0, 1.0))]
    n = _unit(item.normal)
    saida = []
    if abs(n[2]) < 0.9:
        preferidos = [((0, 0, -1), 1, 1)]
    else:
        preferidos = [((1, 0, 0), 1 if n[2] > 0 else -1, 1)]
    for x0, sentido, mao in preferidos + [(e, s, h) for e in _EIXOS for s in (1, -1) for h in (1, -1)]:
        if abs(sum(x0[k] * n[k] for k in range(3))) > 0.5:
            continue
        x0 = _unit(_sub(x0, _escala(n, sum(x0[k] * n[k] for k in range(3)))))
        x = _girar_em(n, x0, sentido * item.rotacao)
        quadro = (x, _escala(_cruz(n, x), mao), n)
        if quadro not in saida:
            saida.append(quadro)
    return saida


def caixa_local(item):
    if item.limites is not None:
        return item.limites
    return (0.0, -item.profundidade, 0.0), (item.largura, 0.0, item.altura)


def cantos(item, quadro):
    (lo, hi), (x, y, z) = caixa_local(item), quadro
    return [_soma(item.base, _escala(x, a), _escala(y, b), _escala(z, c))
            for a in (lo[0], hi[0]) for b in (lo[1], hi[1]) for c in (lo[2], hi[2])]


def envoltoria(pontos):
    return (tuple(min(p[k] for p in pontos) for k in range(3)), tuple(max(p[k] for p in pontos) for k in range(3)))


def referencial(item, caixa_do_pai=None, rotacao_do_pai=None):
    """(X, Y, Z) do item: o preferido, ou o que melhor o mantém dentro da caixa do pai (mm de mundo).

    Algumas peças sem normal (o fundo da cuba esculpida no granito, frentes e trilhos) trazem o ângulo relativo ao
    pai: essa leitura só vale quando reduz à metade, e em mais de 20 mm, o quanto a peça sai do pai.
    """
    opcoes = _candidatos(item)
    if caixa_do_pai is None:
        return opcoes[0]
    plo, phi = caixa_do_pai

    def excesso(q):
        lo, hi = envoltoria(cantos(item, q))
        return sum(max(0.0, plo[k] - lo[k]) + max(0.0, hi[k] - phi[k]) for k in range(3))
    melhor = min(opcoes, key=lambda q: (round(excesso(q), 1), opcoes.index(q)))
    if item.normal is None and rotacao_do_pai:
        t = math.radians(item.rotacao + rotacao_do_pai)
        x = (math.cos(t), math.sin(t), 0.0)
        relativo = (x, _cruz((0, 0, 1), x), (0.0, 0.0, 1.0))
        e0, e1 = excesso(melhor), excesso(relativo)
        if e1 < e0 * 0.5 and e0 - e1 > SOBRA_RELATIVA:
            return relativo
    return melhor


def colocacao(item, quadro):
    """Origem (canto da caixa, mm de mundo), eixos (X, Y, Z destro) e medidas positivas da caixa do item."""
    (lo, hi), (x, y, z) = caixa_local(item), quadro
    origem = _soma(item.base, _escala(x, lo[0]), _escala(y, lo[1]), _escala(z, lo[2]))
    medidas = tuple(hi[k] - lo[k] for k in range(3))
    if sum(_cruz(x, y)[k] * z[k] for k in range(3)) < 0:        # espelhado: anda a origem e inverte X
        origem, x = _soma(origem, _escala(x, medidas[0])), _escala(x, -1)
    return origem, (x, y, z), medidas


def _contorno_na_medida(item, contorno):
    """O contorno que vem como molde (o "Painel" desenhado em 1000 × 1000, igual à caixa `MINBASE`/`MAXBASE`) é
    esticado até a medida do item (`LIMITS`), como o Promob faz; o contorno já em milímetros fica como está."""
    if not item.limites_base or not item.limites or len(contorno) < 3:
        return contorno
    (bx0, by0), (bx1, by1) = item.limites_base
    (lx0, ly0, _), (lx1, ly1, _) = item.limites
    xs, ys = [x for x, _ in contorno], [y for _, y in contorno]
    if bx1 - bx0 < 2 or by1 - by0 < 2:
        return contorno
    if abs(min(xs) - bx0) > 1 or abs(max(xs) - bx1) > 1 or abs(min(ys) - by0) > 1 or abs(max(ys) - by1) > 1:
        return contorno
    if abs((lx1 - lx0) - (bx1 - bx0)) < 1 and abs((ly1 - ly0) - (by1 - by0)) < 1:
        return contorno
    sx, sy = (lx1 - lx0) / (bx1 - bx0), (ly1 - ly0) / (by1 - by0)
    return [(lx0 + (x - bx0) * sx, ly0 + (y - by0) * sy) for x, y in contorno]


PEDRAS = ('granito', 'marmore', 'quartz', 'pedra', 'silestone', 'dekton', 'porcelanato')


def _pedra(material):
    return any(p in texturas.fold(material or '') for p in PEDRAS)


def _do_catalogo(item):
    """Objeto cujo desenho só existe no catálogo instalado do Promob: a entidade Catalog3D sem arquivo, os objetos
    das camadas de decoração (cadeira, computador, ar-condicionado) e a persiana da janela."""
    camada = texturas.fold(item.camada)
    if item.tipo == 'ENTIDADEEXTERNA' and not item.arquivo_3d:
        return True
    if 'persiana' in texturas.fold(item.nome):
        return True
    return camada.startswith('decor') and not camada.startswith('decore-abert') or camada == 'catalog3d items'


MARCO = 50.0                    # mm: o batente do marco desenhado em volta do vão
PASSAGENS = ('s/ porta', 'sem porta', 'abertura p/', 'passagem', 'vao livre')


def _passagem(item):
    """Passagem ou abertura sem esquadria (E005): o vão sem folha."""
    nome = texturas.fold(item.nome)
    return any(p in nome for p in PASSAGENS)


def _vao_do_marco(base):
    """O vão dentro do marco: batentes dos lados e em cima; embaixo, o piso."""
    a, b = _eixos_da_face(base['dimensoes'])
    med = base['dimensoes']
    m = min(MARCO, med[a] / 4, med[b] / 4)
    return (m, med[a] - m, 0.0, med[b] - m)


def _girar_z(p, centro, graus):
    t = math.radians(graus)
    c, s = math.cos(t), math.sin(t)
    x, y = p[0] - centro[0], p[1] - centro[1]
    return (centro[0] + c * x - s * y, centro[1] + s * x + c * y, p[2])


def _faixa_z(no):
    zs = [p[2] for p in _cantos_do_no(no)]
    return min(zs), max(zs)


def _frentes_com_as_gavetas(nos):
    """No Promob a frente da gaveta e a caixa dela são irmãs, cada uma com o seu OPENSERVICE: a frente passa a filha
    da caixa da mesma altura, para as duas abrirem juntas."""
    gavetas = [n for n in nos if (n.get('mecanismo') or {}).get('tipo') == 'DRAWER']
    frentes = [n for n in gavetas if n.get('componente') in ('FRENTE_GAVETA', 'POR')]
    caixas = [n for n in gavetas if n not in frentes]
    if not frentes or not caixas:
        return nos
    soltas = []
    for frente in frentes:
        f0, f1 = _faixa_z(frente)
        melhor = max(caixas, key=lambda c: min(f1, _faixa_z(c)[1]) - max(f0, _faixa_z(c)[0]))
        c0, c1 = _faixa_z(melhor)
        if min(f1, c1) - max(f0, c0) > 0:
            frente.pop('mecanismo')
            melhor['filhos'].append(frente)
            soltas.append(frente)
    return [n for n in nos if all(n is not f for f in soltas)]


def _todos(nos):
    for n in nos:
        yield n
        yield from _todos(n['filhos'])


def _eixos_da_face(medidas):
    """Os dois maiores eixos da caixa (a face); o terceiro é a espessura."""
    fina = min(range(3), key=lambda k: medidas[k])
    return tuple(k for k in range(3) if k != fina)


def _cantos_do_no(no):
    o, eixos, d = no['origem'], no['eixos'], no['dimensoes']
    return [_soma(o, _escala(eixos[0], a), _escala(eixos[1], b), _escala(eixos[2], c))
            for a in (0, d[0]) for b in (0, d[1]) for c in (0, d[2])]


def _no_referencial(no, p):
    r = _sub(p, no['origem'])
    return tuple(sum(r[i] * e[i] for i in range(3)) for e in no['eixos'])


def origem_da_caixa(item):
    """Canto da caixa do item em mm de mundo (com `LIMITS` e `NORMAL`)."""
    return colocacao(item, referencial(item))[0]


def classe_do_material(mid, material=None):
    """'vidro', 'espelho', 'metal' ou None. Os materiais do catálogo não vêm no arquivo: vale o padrão do nome
    (`vid_verde`, `vidro_fume`, `espelho_01`, `dec_met_lis_cro`) e, quando o material vem, a transparência dele."""
    base = re.sub(r'\(\d+\)$', '', (mid or '').lower())
    partes = base.split('_')
    if material is not None and material.transparencia > 0:
        return 'vidro'
    if 'espelho' in base or (material is not None and material.acabamento.lower() == 'mirror'):
        return 'espelho'
    if 'vid' in partes or any(p.startswith('vidro') for p in partes):
        return 'vidro'
    if base.startswith('dec_met') or 'met' in partes:
        return 'metal'
    return None


# Peça de chapa pelo nome do Promob → componente do Padrão de Dimensões (`cutting/part_roles`) ou da gaveta (os
# mesmos códigos do adaptador DRAWERS da 072). A ordem importa: as peças da gaveta vêm antes de "lateral" e "fundo".
COMPONENTES_POR_NOME = (
    ('frente de gaveta', 'FRENTE_GAVETA'), ('frente gaveta', 'FRENTE_GAVETA'), ('frente', 'POR'), ('porta', 'POR'),
    ('lateral de gaveta', 'LATERAL_GAVETA'), ('fundo de gaveta', 'FUNDO_GAVETA'),
    ('contra frente', 'CONTRA_FRENTE_GAVETA'), ('posterior de gaveta', 'TRASEIRA_GAVETA'),
    ('traseira de gaveta', 'TRASEIRA_GAVETA'), ('lateral', 'LAT'), ('montante', 'DIV'), ('divis', 'DIV'), ('prateleira', 'PRAT'),
    ('base', 'BAS'), ('tampo', 'TAMP'), ('fundo', 'FUN_INF'), ('rodape', 'ROD'), ('travessa', 'TRA'),
    ('sarrafo', 'SAR'), ('tamponamento', 'TAMPON'), ('painel', 'TAMPON'), ('moldura', 'MOL'),
)


def componente_da_peca(nome):
    """Código do componente pelo nome da peça ("Lateral 15mm" → 'LAT'), ou None."""
    limpo = ' '.join(texturas._palavras(nome))
    return next((c for prefixo, c in COMPONENTES_POR_NOME if limpo.startswith(prefixo)), None)


def face_do_componente(componente):
    """Face do modelo que dá o acabamento do componente: 'ext', 'int', 'fita' ou 'fita_fro'."""
    c = componente.upper()
    if c.startswith('FITA'):
        return 'fita_fro' if c.endswith('_FRO') else 'fita'
    return 'int' if 'INTERNO' in c else 'ext'


_ORDEM_DA_FACE = {'ext': 0, 'int': 1, 'fita_fro': 2, 'fita': 3}

# -- chapa para o plano de corte (regra do OpenMob, `openmob-formats/promob.rs` `classify_leaf`, corrigida) ----------
#
# O OpenMob manda ao corte a folha da árvore com espessura até 40 mm, largura a partir de 60 mm e material próprio.
# Corrigido aqui, pelo conferido nos projetos: vale também o item com filhos que tem corpo próprio (a porta com as
# dobradiças); vidro, espelho e metal não são chapa; peça de decoração não é chapa; o papel vem do nome da peça e não
# de um trecho do ID ("gav" punha lateral e fundo de gaveta como frente); o veio do código do Promob segue a peça.
ESPESSURA_MAXIMA_DA_CHAPA = 40.0
LARGURA_MINIMA_DA_CHAPA = 60.0

# -- abertura (OPENSERVICE) ------------------------------------------------------------------------------------------
MECANISMOS = {'Door': 'HINGE', 'Dumping': 'TILT', 'Sliding': 'SLIDE', 'Drawer': 'DRAWER'}
PADRAO_DO_MAXIMO = {'HINGE': 90.0, 'TILT': 90.0, 'SLIDE': 400.0, 'DRAWER': 400.0}
_NOS_PERMITIDOS = (ast.Expression, ast.BinOp, ast.UnaryOp, ast.IfExp, ast.Compare, ast.Constant, ast.Add, ast.Sub,
                   ast.Mult, ast.Div, ast.USub, ast.UAdd, ast.Eq, ast.NotEq, ast.Gt, ast.Lt, ast.GtE, ast.LtE)


def avaliar(formula, item):
    """Valor de uma fórmula do OPENSERVICE (`@($I$?-$WIDTH$:$WIDTH$)`, `$W$-50`, `-$DEPTH$`), ou None.

    Só aritmética, comparação e o `?:` sobre as medidas do item e o `$I$` (espelhada). Macro do catálogo (`#…#`,
    `%…%`) ou variável desconhecida devolve None, e vale o padrão."""
    t = (formula or '').strip()
    if t.startswith('@'):
        t = t[1:].strip()
    if not t or '#' in t or '%' in t:
        return None
    inv = '1' if item.invertido else '0'
    for nome, valor in (('$INVERTED$', inv), ('$I$', inv), ('$WIDTH$', item.largura), ('$W$', item.largura),
                        ('$HEIGHT$', item.altura), ('$H$', item.altura), ('$DEPTH$', item.profundidade),
                        ('$D$', item.profundidade)):
        t = t.replace(nome, f'{float(valor):g}').replace(nome.lower(), f'{float(valor):g}')
    if '$' in t:
        return None
    t = _ternario(t)
    try:
        arvore = ast.parse(t, mode='eval')
    except SyntaxError:
        return None
    if not all(isinstance(n, _NOS_PERMITIDOS) for n in ast.walk(arvore)):
        return None
    try:
        return float(eval(compile(arvore, '<openservice>', 'eval'), {'__builtins__': {}}, {}))
    except (ZeroDivisionError, TypeError, ValueError):
        return None


def _fecha(t, i):
    """Índice do `)` que fecha o `(` em `i`, ou -1."""
    nivel = 0
    for j in range(i, len(t)):
        nivel += {'(': 1, ')': -1}.get(t[j], 0)
        if nivel == 0:
            return j
    return -1


def _ternario(t):
    """`a ? b : c` do Promob → `(b) if (a) else (c)` do Python, respeitando parênteses e `?:` aninhados."""
    t = t.strip()
    while t.startswith('(') and _fecha(t, 0) == len(t) - 1:
        t = t[1:-1].strip()
    nivel, pergunta = 0, None
    for i, ch in enumerate(t):
        nivel += {'(': 1, ')': -1}.get(ch, 0)
        if ch == '?' and nivel == 0:
            pergunta = i
            break
    if pergunta is None:
        return t
    nivel, aninhados = 0, 0
    for j in range(pergunta + 1, len(t)):
        ch = t[j]
        nivel += {'(': 1, ')': -1}.get(ch, 0)
        if nivel == 0 and ch == '?':
            aninhados += 1
        elif nivel == 0 and ch == ':':
            if aninhados == 0:
                return (f'(({_ternario(t[pergunta + 1:j])}) if ({_ternario(t[:pergunta])}) '
                        f'else ({_ternario(t[j + 1:])}))')
            aninhados -= 1
    return t


def _verdadeiro(formula, item):
    t = (formula or '').strip()
    if t.upper() in ('Y', 'S', 'TRUE'):
        return True
    valor = avaliar(t, item) if t else None
    return bool(valor)


def _catalogo_do_addon():
    caminho = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'textures', 'catalog.json')
    try:
        with open(caminho, encoding='utf-8') as f:
            return texturas.itens_do_catalogo(json.load(f))
    except (OSError, ValueError):
        return []


def _pbr_do_addon():
    """Manifesto das texturas PBR do pacote (073), ou None."""
    return pbr_core.carregar(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'pbr'))


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
    saida = re.sub(r'\$[A-Za-z_][^$\s]*\$', '', saida)       # $REFERENCE(...)$: vem do catálogo, que não está no arquivo
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


def _coletar_itens_arvore(item):
    yield item
    for f in getattr(item, 'filhos', ()) or ():
        yield from _coletar_itens_arvore(f)


def casar_abertura_promob(item, porta):
    """(modelo, material) do contrato v2 inferidos do item de abertura do `.promob` (feature 078, RN-06, RF-06)."""
    nos = list(_coletar_itens_arvore(item))
    texto = ' '.join(
        texturas.fold( f'{getattr(n, "nome", "")} {getattr(n, "id", "")}' )
        for n in nos
    )
    mecanismos = {
        (getattr(n, 'abertura', None) or {}).get('TYPE')
        for n in nos
        if getattr(n, 'abertura', None)
    }
    mids = []
    for n in nos:
        if getattr(n, 'material', None):
            mids.append(str(n.material))
        for _c, m in getattr(n, 'componentes', ()) or ():
            if m:
                mids.append(str(m))
        for m in (getattr(n, 'acabamentos', None) or {}).values():
            if m:
                mids.append(str(m))
    mat_texto = texturas.fold(' '.join(mids))
    tudo = f'{texto} {mat_texto}'

    # Material ('madeira' | 'aluminio' | 'blindex')
    if any(k in tudo for k in ('blindex', 'temperad', ' incolor temperad')):
        material = 'blindex'
    elif any(k in tudo for k in ('madeir', 'mad_', 'mogno', 'freijo', 'imbuia', 'carvalho', 'tauari', 'curupixa', 'cedro', 'angelim')):
        material = 'madeira'
    elif any(k in tudo for k in ('alumin', 'alu_', 'dec_met', 'metal', 'inox')):
        material = 'aluminio'
    elif any(k in mat_texto for k in ('vidro', 'vid_')) and not any(k in tudo for k in ('madeir', 'alumin')):
        material = 'blindex'
    else:
        material = 'madeira' if porta else 'aluminio'

    # Modelo (10 de porta | 20 de janela)
    if porta:
        is_slide = 'Sliding' in mecanismos or any(k in texto for k in ('correr', 'trilho', 'embutid'))
        if any(k in texto for k in ('camarao', 'articulad', 'mao amiga', 'mao-amiga')):
            modelo = 'porta_correr_camarao'
        elif is_slide:
            if any(k in texto for k in ('4 folh', '4f', 'quatro folh')):
                modelo = 'porta_correr_4f'
            elif any(k in texto for k in ('2 folh', '2f', 'duas folh', 'dupla')):
                modelo = 'porta_correr_2f'
            elif 'embutid' in texto:
                modelo = 'porta_correr_embutida'
            else:
                modelo = 'porta_correr_aparente'
        else:
            folhas_giro = sum(1 for n in nos[1:] if 'folha' in texturas.fold(getattr(n, 'nome', '')) or (getattr(n, 'abertura', None) or {}).get('TYPE') == 'Door')
            if any(k in texto for k in ('dupla', '2 folh', '2f', 'duas folh')) or folhas_giro >= 2:
                modelo = 'porta_giro_dupla'
            elif 'visor' in texto:
                modelo = 'porta_giro_visor'
            elif 'frisad' in texto:
                modelo = 'porta_giro_frisada'
            elif 'lisa' in texto:
                modelo = 'porta_giro_lisa'
            else:
                modelo = 'porta_giro_almofadada'
    else:
        if 'Dumping' in mecanismos or any(k in texto for k in ('maximar', 'maxim-ar', 'maxim ar', 'bascul', 'pivot')):
            if 'pivot' in texto:
                modelo = 'janela_pivotante'
            elif 'bascul' in texto:
                modelo = 'janela_basculante'
            elif 'fixo' in texto:
                modelo = 'janela_maximar_fixo'
            elif any(k in texto for k in ('2m', '2 mod', '2 folh', '2f', 'dupla', 'duplo')):
                modelo = 'janela_maximar_2m'
            else:
                modelo = 'janela_maximar_1m'
        elif any(k in texto for k in ('quadro fixo', 'janela fixa', 'panoram', 'bay', 'vitro', 'veneziana fixa')):
            if 'veneziana' in texto:
                modelo = 'janela_veneziana_fixa'
            elif 'panoram' in texto:
                modelo = 'janela_panoramica'
            elif 'bay' in texto:
                modelo = 'janela_bay'
            elif any(k in texto for k in ('vitro', 'quadricul')):
                modelo = 'janela_vitro'
            else:
                modelo = 'janela_fixa'
        elif any(k in texto for k in ('abrir', 'giro', 'camarao', 'articulad')) and 'correr' not in texto:
            if any(k in texto for k in ('camarao', 'articulad')):
                modelo = 'janela_abrir_camarao'
            elif 'veneziana' in texto:
                modelo = 'janela_abrir_veneziana'
            elif 'bandeira' in texto:
                modelo = 'janela_abrir_bandeira'
            elif any(k in texto for k in ('1 folh', '1f', 'uma folh')):
                modelo = 'janela_abrir_1f'
            else:
                modelo = 'janela_abrir_2f'
        else:
            if 'veneziana' in texto:
                modelo = 'janela_correr_veneziana'
            elif 'bandeira' in texto:
                modelo = 'janela_correr_bandeira'
            elif any(k in texto for k in ('4 folh', '4f', 'quatro folh')):
                modelo = 'janela_correr_4f'
            elif any(k in texto for k in ('3 folh', '3f', 'tres folh')):
                modelo = 'janela_correr_3f'
            else:
                modelo = 'janela_correr_2f'

    return modelo, material


class Conversao:
    def __init__(self, projeto, novo_id=_id, catalogo=None, pbr=None):
        self.projeto, self.novo_id = projeto, novo_id
        self.catalogo = _catalogo_do_addon() if catalogo is None else catalogo
        self.pbr = (_pbr_do_addon() if catalogo is None else None) if pbr is None else pbr   # 073 (D-10)
        self.texturas_pbr = dict(com_textura=0, aproximadas=[], em_cor=0, _vistos=set())
        self._movel = 0              # > 0 dentro de uma peça que abre: o que está dentro corre junto
        self.parede_do_wall = {}     # id(item WALL) → id da parede do v2 (o hospedeiro dos itens dele)
        self.aberturas_sem_folha = []   # vãos sem a folha genérica do editor de paredes (E003, E005)
        self._sem_furo = set()       # id(item) de abertura recusada: grupo com as peças, sem o furo (E002, E004)
        self._camada_oculta = None   # camada desligada herdada do pai (vale para os agregados)
        self.relatorio = dict(contagem={}, paredes=0, aberturas=0, caixas=0, grupos=0, lajes=0, malhas=0,
                              auxiliares=0, chapas=0, moveis_que_abrem=0, do_catalogo=0, ignorados=[], avisos=list(projeto.avisos))
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
        classe = classe_do_material(mid, m)
        if classe is None:
            entrada, veio = texturas.resolver(mid, self.catalogo, m.textura_do_sistema if m is not None else None)
            if entrada is not None and not (m is not None and m.textura):
                marca = entrada['id'].split('/', 1)[0]
                return dict(id=mid, nome=f"{entrada['name']} ({marca.capitalize()})"[:80],
                            cor=_cor_hex(m.cor if m is not None else (0xC8, 0xB8, 0xA0)), textura=None,
                            escala=None, classe=None, transparencia=0.0, textura_catalogo=entrada['id'],
                            tamanho=tuple(entrada.get('size-mm') or (600.0, 600.0)), veio=veio)
            pbr = self._pbr(mid, m)
            if pbr is not None:
                return pbr
            cor = texturas.cor_por_nome(mid) if m is None else None
            if cor is not None:
                return dict(id=mid, nome=mid[:80], cor=_cor_hex(cor), textura=None, escala=None, classe=None,
                            transparencia=0.0)
        if mid.lower().startswith('cin_cor_') and m is None:
            return dict(id=mid, nome='Acabamento do modelo (não resolvido)', cor=_cor_hex((0xE6, 0xE4, 0xDF)),
                        textura=None, escala=None, classe=None, transparencia=0.0)
        if classe == 'metal' and (pbr := self._pbr(mid, m)) is not None:
            return pbr
        if m is None:
            partes = re.sub(r'\(\d+\)$', '', mid.lower()).split('_')
            tom = next((p for p in partes if p in ('cro', 'alu', 'ino')), None) if classe == 'metal' else None
            cor = _CORES_DA_CLASSE.get(tom or classe, (0xBD, 0xB7, 0xAE))
            return dict(id=mid, nome=mid[:80], cor=_cor_hex(cor), textura=None, escala=None, classe=classe,
                        transparencia=0.6 if classe == 'vidro' else 0.0)
        return dict(id=mid, nome=m.nome, cor=_cor_hex(m.cor), textura=m.textura, escala=m.escala, classe=classe,
                    transparencia=m.transparencia if classe == 'vidro' and m.transparencia > 0 else
                    (0.6 if classe == 'vidro' else 0.0))

    def _relatorio_de_texturas(self):
        """RF-10: acabamentos com textura (chapa do catálogo ou PBR do pacote), quantos aproximados e quantos em cor."""
        mids = set(self.materiais_do_documento) | set(self.materiais_do_complemento)
        dados = [self._material(mid) for mid in sorted(mids)]
        com = sum(1 for d in dados if d and (d.get('textura_catalogo') or d.get('textura')))
        aproximadas = list(self.texturas_pbr['aproximadas'])
        self.relatorio['texturas'] = dict(com_textura=com, aproximadas=aproximadas, em_cor=len(mids) - com)
        for a in aproximadas:
            self.relatorio['avisos'].append(f"Textura aproximada: {a['material']} → {a['textura']}")

    def _pbr(self, mid, m):
        """Textura PBR do pacote pelo nome (RN-04, RN-05, Q4): só sem textura própria do projeto; guarda o nome
        original do Promob e conta para o relatório (RF-10)."""
        if not self.pbr or (m is not None and m.textura):
            return None
        t, aproximada = pbr_core.casar(mid, self.pbr)
        if t is None:
            return None
        if aproximada and mid not in self.texturas_pbr['_vistos']:
            self.texturas_pbr['aproximadas'].append(dict(material=mid[:80], textura=t['slug']))
        self.texturas_pbr['_vistos'].add(mid)
        cor = texturas.cor_por_nome(mid) or (0xC8, 0xB8, 0xA0)
        tamanho = t['tamanho_mm']
        return dict(id=mid, nome=mid[:80], cor=_cor_hex(m.cor if m is not None else cor), textura=None, escala=None,
                    classe=None, transparencia=0.0, textura_catalogo=t['uuid'], pbr=True, aproximada=aproximada,
                    tamanho=(float(tamanho['largura']), float(tamanho['altura'])))

    def _material_do_documento(self, mid):
        dado = self._material(mid)
        if dado is None:
            return None
        if mid not in self.materiais_do_documento:
            if dado.get('pbr'):                    # 073 (RN-06): textura do pacote, com o tamanho real do manifesto
                largura, altura = dado['tamanho']
                self.materiais_do_documento[mid] = dict(
                    id=self.novo_id(), nome=dado['nome'][:160] or 'Material', tipo='textura',
                    textura_id=dado['textura_catalogo'], escala_mm=dict(largura=int(largura), altura=int(altura)))
            else:
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
        pontos, originais = [], []           # originais: índice no arquivo de cada ponto mantido (INDICEFORMA)
        for i, (x, y, e) in enumerate(item.pontos):
            if pontos and math.hypot(x - pontos[-1][0], y - pontos[-1][1]) < TRECHO_MINIMO:
                if math.hypot(x - pontos[-1][0], y - pontos[-1][1]) >= 1:
                    self.relatorio['avisos'].append(f'Trecho curto unido ({item.nome[:40]})')
                continue
            pontos.append((x, y, e))
            originais.append(i)
        fechada = len(pontos) > 2 and math.hypot(pontos[0][0] - pontos[-1][0], pontos[0][1] - pontos[-1][1]) < TRECHO_MINIMO
        if fechada:
            pontos.pop()
            originais.pop()
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
            # Face de um trecho só (REGIONS PAREDE_FACE_PERFIL_..._INDICEFORMA_n): de 0 a n-1, a face do percurso, que
            # no addon é a externa; de n+1 a 2n, a face do outro lado da espessura, em ordem inversa.
            n, k = len(item.pontos) - 1, originais[len(parede['segmentos'])]
            for chave, indice in (('material_externo_id', k), ('material_interno_id', 2 * n - k)):
                proprio = item.materiais_por_trecho.get(indice)
                if proprio and proprio != item.material_das_faces and (m := self._material_do_documento(proprio)):
                    segmento[chave] = m
            parede['segmentos'].append(segmento)
            u = ((x1 - x0) / comprimento, (y1 - y0) / comprimento)
            self.trechos.append((parede, segmento, (x0, y0), u, sentido, espessura, altura))
            anterior = angulo
        self.paredes.append(parede)
        self.parede_do_wall[id(item)] = parede['id']
        self.relatorio['paredes'] += 1

    # -- aberturas (RN-04, D-07; emendas E001 a E005) --------------------------------------------------------------
    @staticmethod
    def _e_abertura(item):
        """Fura a parede o item que o Promob marca com `HOLE PRICK="Y"`, em qualquer camada (E001). Sem furo ativo, vale
        o nome da camada, como antes (arquivos sem `HOLE`)."""
        if item.furo and item.furo['ativo']:
            return True
        camada = item.camada.lower()
        return any(p in camada for p in PALAVRAS_DE_ABERTURA)

    def _pedacos(self, item, trechos):
        """Pedaços do vão nos trechos compatíveis: (parede, segmento, p0, u, x0, x1, z0, z1)."""
        quadro = referencial(item)
        pontos = cantos(item, quadro)
        oz = min(p[2] for p in pontos)
        topo = max(p[2] for p in pontos)
        cantos_xy = [(p[0], p[1]) for p in pontos]
        direcao = quadro[0][:2]
        out = []
        for parede, segmento, p0, u, sentido, espessura, altura in trechos:
            if abs(direcao[0] * u[0] + direcao[1] * u[1]) < 0.9:
                continue
            esquerda = (-u[1], u[0])
            lado = 1 if sentido == 'LEFT' else -1
            s = [(cx - p0[0]) * u[0] + (cy - p0[1]) * u[1] for cx, cy in cantos_xy]
            n = [((cx - p0[0]) * esquerda[0] + (cy - p0[1]) * esquerda[1]) * lado for cx, cy in cantos_xy]
            if not (min(n) < espessura + PERTO_DA_PAREDE and max(n) > -PERTO_DA_PAREDE):
                continue
            x0, x1 = max(min(s), 0.0), min(max(s), segmento['comprimento'])
            z0, z1 = max(oz, 0.0), min(topo, altura)
            if x1 - x0 > 1.0 and z1 - z0 > SOBREPOSICAO_MINIMA:
                out.append((parede, segmento, p0, u, x0, x1, z0, z1))
        return out

    def _abertura(self, item, hospedeiro=None):
        """Vão(s) do v2 para o item: os ids; None sem trecho compatível; [] se sobrepuser outro vão (E004).

        O trecho é procurado primeiro nas paredes do `WALL` que hospeda o item (E001). A abertura que passa da divisão
        entre trechos colineares da mesma parede fura todos eles, um vão por trecho (E003)."""
        da_parede = [t for t in self.trechos if t[0]['id'] == self.parede_do_wall.get(id(hospedeiro))]
        pedacos = self._pedacos(item, da_parede) or self._pedacos(item, self.trechos)
        principais = [p for p in pedacos if p[5] - p[4] > SOBREPOSICAO_MINIMA]
        if not principais:
            self._ignorar(item, 'abertura sem trecho de parede compatível; entrou como caixa')
            return None
        parede, segmento, p0, u, x0, x1, z0, z1 = max(principais, key=lambda p: p[5] - p[4])
        juntos = [p for p in pedacos if p[0] is parede and abs(p[3][0] * u[0] + p[3][1] * u[1]) > 0.9999
                  and abs((p[2][0] - p0[0]) * -u[1] + (p[2][1] - p0[1]) * u[0]) < 1.0]
        for _p, seg, _p0, _u, a0, a1, _z0, _z1 in juntos:
            if any(a0 < a['posicao'] + a['largura'] and a['posicao'] < a1
                   for a in self.aberturas if a['segmento_id'] == seg['id']):
                self._ignorar(item, 'abertura sobreposta a outra no mesmo trecho; entrou com as peças, sem o furo')
                return []
        porta = z0 < PEITORIL_DE_PORTA      # E002: a porta vai ao piso; o contrato pede peitoril 0 na porta
        modelo, material = casar_abertura_promob(item, porta)
        ids = []
        for _p, seg, _p0, _u, a0, a1, _z0, _z1 in sorted(juntos, key=lambda p: -(p[5] - p[4])):
            ids.append(self.novo_id())
            self.aberturas.append(dict(id=ids[-1], tipo='DOOR' if porta else 'WINDOW', segmento_id=seg['id'],
                                       posicao=round(a0, 3), largura=round(a1 - a0, 3),
                                       altura=round(z1 if porta else z1 - z0, 3), peitoril=0 if porta else round(z0, 3),
                                       modelo=modelo, material=material))
        self.relatorio['aberturas'] += 1
        self.aberturas_sem_folha.extend(ids[1:])      # o pedaço que passa para o trecho vizinho não ganha outra folha
        return ids

    # -- móveis, lajes e malhas (complemento, D-11 e D-30) --------------------------------------------------------
    def _base(self, item, visivel, caixa_do_pai=None, rotacao_do_pai=None):
        nome = resolver_macros(item.nome, item)[:160] or item.tipo
        quadro = referencial(item, caixa_do_pai, rotacao_do_pai)
        origem, eixos, medidas = colocacao(item, quadro)
        base = dict(nome=nome, promob_id=item.id, tipo_promob=item.tipo, camada=item.camada, visivel=visivel,
                    origem=origem, eixos=eixos, rotacao=item.rotacao, dimensoes=medidas)
        return base, quadro, envoltoria(cantos(item, quadro))

    def _no(self, item, visivel_do_pai, cadeia, caixa_do_pai=None, rotacao_do_pai=None):
        self._contar(item)
        # A dobradiça fica dentro do móvel com a porta fechada, e o copo dela não cabe no pai de 2 mm: entra oculta.
        visivel = visivel_do_pai and item.visivel and 'dob' not in item.id.lower().split('_')
        if item.tipo in IGNORADOS:
            self._ignorar(item, IGNORADOS[item.tipo])
            return None
        if item.tipo == 'WALL':
            return None             # tratado antes (paredes e hospedados)
        item, fechamento = self._pose_aberta(item, caixa_do_pai)
        base, quadro, caixa_mundo = self._base(item, visivel, caixa_do_pai, rotacao_do_pai)
        # Camada desligada no Promob vale para o item e os agregados dele (APLICATIONTYPE "AplicarNaEntidadeEAgregados"):
        # a subárvore entra na camada desligada, e o olho dela liga tudo junto.
        if self._camada_oculta:
            base['camada'] = self._camada_oculta
        oculta_aqui = not self._camada_oculta and item.camada in self.projeto.camadas_ocultas
        if oculta_aqui:
            self._camada_oculta = item.camada
        try:
            return self._no_com_base(item, visivel, cadeia, quadro, base, caixa_mundo, fechamento)
        finally:
            if oculta_aqui:
                self._camada_oculta = None

    def _no_com_base(self, item, visivel, cadeia, quadro, base, caixa_mundo, fechamento):
        nome = base['nome']
        if item.tipo == 'GEOMETRY' and len(item.pontos) >= 3:
            contorno = _contorno_na_medida(item, contorno_com_arcos(item.pontos))
            if item.invertido_x:
                contorno = [(-x, y) for x, y in contorno]
            if item.invertido_y:
                contorno = [(x, -y) for x, y in contorno]
            if item.altura > 0 and len(contorno) >= 3:
                material = item.material or item.material_das_faces
                laje = dict(base, tipo='laje', origem=item.base, eixos=quadro, contorno=contorno, altura=item.altura,
                            material=self._material_do_complemento(material), filhos=[])
                componente = componente_da_peca(nome)
                if componente:
                    laje['componente'] = componente
                chapa = self._chapa(item, laje, material, cadeia) if not _pedra(material) else None
                if chapa is not None:
                    laje['chapa'] = chapa           # o painel ripado e o tampo de MDF vão ao plano de corte
                    self.relatorio['chapas'] += 1
                laje['filhos'] = self._nos(item.filhos, visivel, cadeia + [nome], caixa_mundo, item.rotacao)
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
        mecanismo = self._mecanismo(item, quadro, visivel) if self._movel == 0 else None
        self._movel += 1 if mecanismo else 0
        try:
            filhos = self._nos(item.filhos, visivel, cadeia + [nome], caixa_mundo, item.rotacao)
        finally:
            self._movel -= 1 if mecanismo else 0
        no = self._no_do_corpo(item, base, filhos, cadeia)
        # Abre a folha de verdade: a chapa (porta, frente), o grupo (gaveta, porta de alumínio) ou o vidro. A ferragem
        # com OPENSERVICE (braços do basculante, copo da dobradiça) fica fixa.
        if no is not None and mecanismo and (no['tipo'] == 'grupo' or no.get('chapa')
                                              or self._classe(no.get('material')) in ('vidro', 'espelho')):
            no['mecanismo'] = dict(mecanismo, fechar=fechamento) if fechamento else mecanismo
        return no

    def _no_do_corpo(self, item, base, filhos, cadeia):
        if id(item) in self._sem_furo:
            return self._abertura_sem_furo(item, base, filhos)
        # Item com componente tem corpo próprio (a porta, a torneira, a dobradiça), mesmo com filhos; sem componente,
        # é montagem (o balcão, a caixa) e o corpo são os filhos.
        if (item.filhos and not item.componentes) or min(base['dimensoes']) <= 0:
            if item.filhos:
                self.relatorio['grupos'] += 1
                return dict(base, tipo='grupo', filhos=filhos)
            self._ignorar(item, 'sem dimensões')
            return None
        if not item.filhos and not item.componentes and max(base['dimensoes']) <= AUXILIAR:
            self.relatorio['auxiliares'] += 1
            return None
        return self._corpo(item, base, filhos, cadeia)

    def _classe(self, mid):
        return classe_do_material(mid, self.projeto.materiais.get(mid)) if mid else None

    def _acabamento(self, item, componente, mid):
        """O material do componente; o `cin_cor_000` ("cor do modelo") vira o acabamento da face no modelo."""
        if re.sub(r'\(\d+\)$', '', (mid or '').lower()) != 'cin_cor_000' or not item.acabamentos:
            return mid
        face = face_do_componente(componente)
        reserva = {'ext': 'int', 'int': 'ext', 'fita_fro': 'fita', 'fita': 'int'}[face]
        return item.acabamentos.get(face) or item.acabamentos.get(reserva) or mid

    def _materiais_dos_componentes(self, item):
        """[(componente, material resolvido)], da face externa para a fita."""
        pares = [(c, self._acabamento(item, c, m)) for c, m in item.componentes if m]
        return sorted(pares, key=lambda p: _ORDEM_DA_FACE[face_do_componente(p[0])])

    def _pose_aberta(self, item, caixa_do_pai):
        """O Promob grava a peça na posição em que está (CURRENTVALUE): a gaveta deslocada, a porta girada. Devolve
        o item com o ângulo da pose aberta e como fechá-lo (mm e graus de mundo), ou (item, None).

        A porta aberta sem ROTATION própria herda o ângulo do pai, mas o ponto base já é o da porta girada: o ângulo
        real é o herdado ± a abertura, e vale o sinal que, fechando, encosta a porta no móvel."""
        dado = item.abertura or {}
        tipo = MECANISMOS.get(dado.get('TYPE'))
        atual = (avaliar(dado.get('CURRENTVALUE'), item) or 0.0) if tipo else 0.0
        if not tipo or atual <= 0 or caixa_do_pai is None:
            return item, None
        if tipo in ('DRAWER', 'SLIDE'):
            q = referencial(item, caixa_do_pai)
            eixo = q[1] if tipo == 'DRAWER' else q[0]
            sinal = 1.0 if tipo == 'DRAWER' else (1.0 if _verdadeiro(dado.get('INVERT'), item) else -1.0)
            return item, dict(translacao=_escala(eixo, sinal * atual))   # volta para dentro (+Y) ou para o lado
        if tipo != 'HINGE':
            return item, None
        plo, phi = (tuple(v - 40 for v in caixa_do_pai[0]), tuple(v + 40 for v in caixa_do_pai[1]))
        melhor = None
        aberturas = (-1.0, 1.0) if not item.rotacao_propria else (0.0,)
        for s1 in aberturas:
            candidato = dataclasses.replace(item, rotacao=item.rotacao + s1 * atual) if s1 else item
            q = referencial(candidato, caixa_do_pai)
            px, py = (avaliar(dado.get(k), candidato) or 0.0 for k in ('X', 'Y'))
            centro = _soma(candidato.base, _escala(q[0], px), _escala(q[1], py))
            for s2 in ((-s1,) if s1 else (-1.0, 1.0)):
                angulo = s2 * atual
                fechados = [_girar_z(p, centro, angulo) for p in cantos(candidato, q)]
                lo, hi = envoltoria(fechados)
                fora = sum(max(0.0, plo[k] - lo[k]) + max(0.0, hi[k] - phi[k]) for k in range(3))
                if melhor is None or fora < melhor[0]:
                    melhor = (fora, candidato, dict(centro=centro, angulo=angulo))
        return melhor[1], melhor[2]

    def _mecanismo(self, item, quadro, visivel):
        """Porta, basculante, correr ou gaveta pelo OPENSERVICE: o eixo (mm de mundo), o curso e o estado salvo."""
        dado = item.abertura or {}
        tipo = MECANISMOS.get(dado.get('TYPE'))
        if tipo is None or not visivel:
            return None
        maximo = avaliar(dado.get('MAX'), item) or PADRAO_DO_MAXIMO[tipo]
        if maximo <= 0:
            return None
        atual = avaliar(dado.get('CURRENTVALUE'), item) or 0.0
        out = dict(tipo=tipo, maximo=round(maximo, 3), abertura=round(max(0.0, min(1.0, atual / maximo)), 4))
        x, y, z = quadro
        if tipo in ('HINGE', 'TILT'):
            px, py, pz = (avaliar(dado.get(k), item) for k in ('X', 'Y', 'Z'))
            if px is None and py is None and pz is None:
                return None
            out['eixo'] = _soma(item.base, _escala(x, px or 0.0), _escala(y, py or 0.0), _escala(z, pz or 0.0))
        elif tipo == 'SLIDE':
            out['sentido'] = _escala(x, -1.0 if _verdadeiro(dado.get('INVERT'), item) else 1.0)
        else:
            out['sentido'] = _escala(y, -1.0)                 # a gaveta sai pela frente (−Y do item)
        return out

    def _chapa(self, item, base, material, cadeia):
        """A peça para o plano de corte (regra do OpenMob corrigida), ou None."""
        med = base['dimensoes']
        ordem = sorted(range(3), key=lambda k: med[k])
        fina, meio, longo = ordem
        if not material or med[fina] > ESPESSURA_MAXIMA_DA_CHAPA or med[meio] < LARGURA_MINIMA_DA_CHAPA:
            return None
        if item.camada.lower().startswith('decore') or self._classe(material):
            return None
        dado = self._material(material) or {}
        veio = 'NONE'
        if dado.get('veio'):
            eixos = base['eixos']
            if dado['veio'] == 'V':     # o veio "vertical" do Promob: o eixo da face mais em pé (ou a profundidade)
                eixo = max((meio, longo), key=lambda k: (round(abs(eixos[k][2]), 3), k == 1))
            else:                       # "horizontal": o eixo da face mais deitado (a largura, se empatar)
                eixo = min((meio, longo), key=lambda k: (round(abs(eixos[k][2]), 3), k != 0))
            veio = 'VERTICAL' if eixo == longo else 'HORIZONTAL'
        return dict(nome=base['nome'], modulo=(cadeia[0] if cadeia else base['nome'])[:160],
                    componente=base.get('componente') or 'UNCLASSIFIED', comprimento=round(med[longo], 1),
                    largura=round(med[meio], 1), espessura=round(med[fina], 1),
                    material=(dado.get('nome') or material)[:80], veio=veio)

    def _corpo(self, item, base, filhos, cadeia=()):
        pares = self._materiais_dos_componentes(item)
        vidros = [m for _, m in pares if self._classe(m) in ('vidro', 'espelho')]
        outros = [m for _, m in pares if m not in vidros]
        material = outros[0] if outros else item.material
        base = dict(base, componentes=[[c, m] for c, m in pares])
        componente = componente_da_peca(base['nome'])
        if componente and outros:
            base['componente'] = componente
        vao = self._vao_de_vidro(base, filhos)
        if vao is not None:
            # Porta de alumínio com painel de vidro filho: o corpo é a moldura em volta do painel.
            self.relatorio['grupos'] += 1
            return dict(base, tipo='grupo', filhos=self._moldura(base, vao, material) + filhos)
        if vidros and outros:
            # Porta com vidro no mesmo item (madeira e vidro): moldura do material da porta e o vidro dentro.
            a, b = _eixos_da_face(base['dimensoes'])
            m = min(MOLDURA, base['dimensoes'][a] / 4, base['dimensoes'][b] / 4)
            vao = (m, base['dimensoes'][a] - m, m, base['dimensoes'][b] - m)
            self.relatorio['grupos'] += 1
            return dict(base, tipo='grupo', filhos=self._moldura(base, vao, material) +
                        [self._vidro(base, vao, vidros[0])] + filhos)
        self.relatorio['caixas'] += 1
        no = dict(base, tipo='caixa', material=self._material_do_complemento(vidros[0] if vidros and not outros
                                                                             else material), filhos=filhos)
        forma = next((f for f in FORMAS if f in base['nome'].lower()), None)
        if forma:
            no['forma'] = forma
        chapa = self._chapa(item, base, material, cadeia) if not forma else None
        if chapa is not None:
            no['chapa'] = chapa
            self.relatorio['chapas'] += 1
        elif not forma and _do_catalogo(item):
            no['catalogo'] = True           # o modelo 3D fica no catálogo do Promob: marcador em arame, não caixa
            self.relatorio['do_catalogo'] += 1
        return no

    def _vao_de_vidro(self, base, filhos):
        """Retângulo (a0, a1, b0, b1) da face do item que um vidro filho ocupa, ou None."""
        a, b = _eixos_da_face(base['dimensoes'])
        med = base['dimensoes']
        for f in filhos:
            if f['tipo'] != 'caixa' or self._classe(f.get('material')) not in ('vidro', 'espelho'):
                continue
            locais = [_no_referencial(base, p) for p in _cantos_do_no(f)]
            a0, a1 = max(min(p[a] for p in locais), 0.0), min(max(p[a] for p in locais), med[a])
            b0, b1 = max(min(p[b] for p in locais), 0.0), min(max(p[b] for p in locais), med[b])
            if a1 > a0 and b1 > b0 and (a1 - a0) * (b1 - b0) >= VAO_DE_VIDRO * med[a] * med[b]:
                return a0, a1, b0, b1
        return None

    def _sub_caixa(self, base, nome, desloc, dims, material):
        origem = _soma(base['origem'], *(_escala(base['eixos'][k], desloc[k]) for k in range(3)))
        return dict(base, nome=nome, tipo='caixa', origem=origem, dimensoes=tuple(dims),
                    material=self._material_do_complemento(material), filhos=[])

    def _moldura(self, base, vao, material):
        """Quatro réguas em volta do vão, com toda a espessura do item."""
        a, b = _eixos_da_face(base['dimensoes'])
        med = base['dimensoes']
        a0, a1, b0, b1 = vao
        out = []
        for x0, x1, y0, y1 in ((0, med[a], 0, b0), (0, med[a], b1, med[b]), (0, a0, b0, b1), (a1, med[a], b0, b1)):
            if x1 - x0 > 0.5 and y1 - y0 > 0.5:
                desloc, dims = [0.0, 0.0, 0.0], list(med)
                desloc[a], desloc[b], dims[a], dims[b] = x0, y0, x1 - x0, y1 - y0
                out.append(self._sub_caixa(base, base['nome'] + ' · moldura', desloc, dims, material))
        self.relatorio['caixas'] += len(out)
        return out

    def _vidro(self, base, vao, material):
        a, b = _eixos_da_face(base['dimensoes'])
        fina = 3 - a - b
        med = base['dimensoes']
        espessura = min(VIDRO, med[fina])
        desloc, dims = [0.0, 0.0, 0.0], list(med)
        desloc[a], desloc[b], desloc[fina] = vao[0], vao[2], (med[fina] - espessura) / 2
        dims[a], dims[b], dims[fina] = vao[1] - vao[0], vao[3] - vao[2], espessura
        self.relatorio['caixas'] += 1
        return self._sub_caixa(base, base['nome'] + ' · vidro', desloc, dims, material)

    def _folhas_da_abertura(self, item, abertura_id):
        """Porta ou janela de vidro que virou vão do v2: as folhas, o marco e a maçaneta vão ao complemento, e a
        folha genérica do editor de paredes sai. Sem vidro, fica a folha do MOBI, que desenha melhor a porta de
        madeira do que a caixa cinza de um modelo que o catálogo não manda."""
        base, _quadro, caixa_mundo = self._base(item, item.visivel)
        contagem = dict(self.relatorio)
        filhos = self._nos(item.filhos, item.visivel, [base['nome']], caixa_mundo, item.rotacao)
        if not any(self._classe(n.get('material')) in ('vidro', 'espelho') for n in _todos(filhos)):
            for chave in ('caixas', 'grupos', 'auxiliares'):
                self.relatorio[chave] = contagem[chave]
            return None
        self.relatorio['grupos'] += 1
        return dict(base, tipo='grupo', filhos=filhos, abertura=abertura_id)

    def _documento(self, pavimento_id, aberturas):
        return dict(
            schema='caffmob.ambiente/v2', id='validacao', version=1, atualizado_em='2026-01-01T00:00:00.000Z',
            origem='blender', nome='validacao', unidade='mm', eixos='Z_UP',
            configuracao_geometrica=dict(perfil='studio/1', espessuras=dict(caixa=15, porta=18, fundo=6)),
            pavimentos=[dict(id=pavimento_id, nome='Térreo', ordem=0, pe_direito=6000,
                             laje=dict(id='laje', ativa=False, tipo='macica', espessura=120, contrapiso=30, beiral=0,
                                       recortes=[]), forro=dict(tipo='nenhum', material='gesso', sanca=None))],
            paredes=self.paredes, aberturas=aberturas, modulos=[], pecas_avulsas=[], primitivas=[], escadas=[],
            itens_externos=[], materiais=list(self.materiais_do_documento.values()), camadas=[], vinculos=[])

    def _podar_aberturas(self, convertidos, pavimento_id):
        """Valida os vãos antes de montar os móveis (E002): o item cujo vão o editor de paredes recusa volta ao
        complemento com as peças dela, em vez de sumir."""
        while True:
            erros = validar_documento(self._documento(pavimento_id, self.aberturas))
            ruins = set()
            for erro in erros:
                caminho = erro.get('caminho', '')
                if caminho.startswith('aberturas['):
                    i = int(caminho[len('aberturas['):].split(']')[0])
                    if i < len(self.aberturas):
                        ruins.add(self.aberturas[i]['id'])
            if not ruins:
                return convertidos
            fora = [(h, ids) for h, ids in convertidos if ruins & set(ids)]
            for h, ids in fora:
                self.aberturas = [a for a in self.aberturas if a['id'] not in ids]
                self.relatorio['aberturas'] -= 1
                self._sem_furo.add(id(h))
                self._ignorar(h, 'abertura recusada pelas regras do editor de paredes; entrou com as peças, sem o furo')
            self.relatorio['avisos'].append(f'{len(fora)} abertura(s) recusada(s) pelas regras do editor de paredes; '
                                            'entraram com as peças, sem o furo')
            convertidos = [(h, ids) for h, ids in convertidos if not ruins & set(ids)]
            if not fora:
                return convertidos

    def _visual_da_abertura(self, item, ids):
        """O que o Promob desenha no vão: a janela de malha OBJ (E001), as folhas de vidro (3ª auditoria) ou, numa
        passagem, só o marco (E005). Nesses casos a folha genérica do editor de paredes sai."""
        if item.tipo == 'ENTIDADEEXTERNA' and item.arquivo_3d:
            no = self._no(item, item.visivel, [])
            if no is not None:
                return dict(no, abertura=ids[0])
        if _passagem(item):
            self.aberturas_sem_folha.extend(ids[:1])
            base, _quadro, _caixa = self._base(item, item.visivel)
            molduras = self._moldura(base, _vao_do_marco(base), item.material) if item.componentes else []
            self.relatorio['grupos'] += 1
            return dict(base, tipo='grupo', filhos=molduras, abertura=ids[0])
        return self._folhas_da_abertura(item, ids[0])

    def _abertura_sem_furo(self, item, base, filhos):
        """Abertura que o editor de paredes não comporta (E002, E004): as peças dela e o marco em moldura, sem
        tapar o lugar com uma caixa."""
        molduras = self._moldura(base, _vao_do_marco(base), item.material) if item.componentes else []
        self.relatorio['grupos'] += 1
        return dict(base, tipo='grupo', filhos=molduras + filhos)

    def _nos(self, itens, visivel, cadeia, caixa_do_pai=None, rotacao_do_pai=None):
        nos = [n for n in (self._no(i, visivel, cadeia, caixa_do_pai, rotacao_do_pai) for i in itens) if n is not None]
        return _frentes_com_as_gavetas(nos)

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
        convertidos = []             # (item, ids dos vãos)
        for parede in hospedeiros:
            for h in parede.filhos:
                if h.tipo != 'WALL' and self._e_abertura(h):
                    ids = self._abertura(h, parede)
                    if ids:
                        convertidos.append((h, ids))
                    elif ids is not None:
                        self._sem_furo.add(id(h))       # E004: entra com as peças, sem o furo
        convertidos = self._podar_aberturas(convertidos, pavimento_id)
        ja_aberturas = {id(h) for h, _ in convertidos}
        for h, _ in convertidos:
            self._contar(h)

        def soltos(itens):
            for item in itens:
                if item.tipo == 'WALL':
                    self._contar(item)
                    yield from soltos([h for h in item.filhos if id(h) not in ja_aberturas])
                else:
                    yield item
        self.moveis = self._nos(list(soltos(self.projeto.itens)), True, [])
        self.moveis += [n for n in (self._visual_da_abertura(h, ids) for h, ids in convertidos) if n is not None]
        self.relatorio['moveis_que_abrem'] = sum(1 for n in _todos(self.moveis) if n.get('mecanismo'))
        self.relatorio['cameras'] = len(self.projeto.cameras)
        self._relatorio_de_texturas()
        altura = max([s['pe_direito_inicial'] for p in self.paredes for s in p['segmentos']] or [2700])
        agora = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%S.') + '000Z'
        documento = dict(
            schema='caffmob.ambiente/v2', id=self.novo_id(), version=1, atualizado_em=agora, origem='blender',
            nome=(self.projeto.ambiente.nome or 'Projeto Promob')[:160], unidade='mm', eixos='Z_UP',
            configuracao_geometrica=dict(perfil='studio/1', espessuras=dict(caixa=15, porta=18, fundo=6)),
            pavimentos=[dict(id=pavimento_id, nome='Térreo', ordem=0, pe_direito=min(max(altura, 1000), 6000),
                             **({'piso_material_id': piso} if (piso := self._material_do_documento(
                                 self.projeto.material_do_piso)) else {}),
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
                                     cameras=[dict(vars(c)) for c in self.projeto.cameras],
                                     camadas_ocultas=sorted(self.projeto.camadas_ocultas),
                                     aberturas_sem_folha=[a for a in self.aberturas_sem_folha
                                                          if any(b['id'] == a for b in documento['aberturas'])],
                                     materiais=self.materiais_do_complemento),
                    cliente=dict(self.projeto.cliente))


def converter(projeto, novo_id=_id, catalogo=None, pbr=None):
    """Documento v2 válido, complemento, cliente e relatório. `erros` só vem preenchido se nem as paredes passam.

    `catalogo`: entradas do catálogo de texturas (padrão: o do pacote do addon); `pbr`: manifesto das texturas PBR
    (padrão: o do pacote, quando o catálogo também é o do pacote)."""
    return Conversao(projeto, novo_id, catalogo, pbr).converter()
