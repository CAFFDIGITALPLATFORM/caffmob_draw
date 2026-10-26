"""Leitura do projeto `.promob` (071 D-01 a D-04), sem bpy.

Reescrito a partir do leitor do OpenMob (`crates/openmob-formats/src/promob.rs`, do titular, MIT OR Apache-2.0) e
conferido nos projetos do titular. O `.promob` é um ZIP (nomes com `\\`) de XML UTF-8, alguns com BOM:

- `solucao/container*/document*/document*.ambient3d`: ambientes 3D; cada item é um `INFORMACOES` com `TYPE`;
- `solucao/materials/materials.material`: materiais (`COLORBASE`, textura em `MyTextures/`);
- `document*/LinkedFiles/*.obj`: malhas de entidades externas;
- `*.dataclient`: dados do cliente.

O `promob.info` (licença do Promob) nunca é aberto, e catálogos protegidos nunca são decifrados (RN-01).
"""
import io
import posixpath
import re
import zipfile
import zlib
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field

MAX_ENTRADAS = 20000
MAX_TOTAL = 2 * 1024 ** 3
MAX_ENTRADA = 512 * 1024 ** 2
ARQUIVO_DE_LICENCA = 'promob.info'
NEUTRO = (0xE6, 0xE4, 0xDF)       # acabamento do catálogo, que o arquivo não traz (`cin_cor_*`)
PADRAO = (0xBD, 0xB7, 0xAE)


class PromobErro(Exception):
    """Falha de leitura com mensagem para a pessoa."""


@dataclass
class Item:
    tipo: str
    id: str
    nome: str
    camada: str
    visivel: bool
    base: tuple          # PONTOBASE, mm de mundo: canto traseiro-esquerdo-inferior
    rotacao: float       # graus, anti-horário, absoluta (herdada quando falta)
    largura: float
    altura: float
    profundidade: float
    material: str = None          # material próprio (só os filhos diretos)
    material_das_faces: str = None
    pontos: list = field(default_factory=list)       # SHAPE: (x, y, e_ou_a)
    alinhamento: str = ''
    invertido_x: bool = False
    invertido_y: bool = False
    arquivo_3d: str = None        # FILE3D vinculado (LinkedFiles)
    normal: tuple = None          # POSICAOINSERCAO/NORMAL (A, B, C): o eixo da altura do item; None = para cima
    limites: tuple = None         # LIMITS MIN/MAX: a caixa no referencial do item, a partir do ponto base
    limites_base: tuple = None    # LIMITS MINBASE/MAXBASE: a caixa do molde do contorno (o "Painel" vem em 1000 × 1000)
    componentes: list = field(default_factory=list)  # COMPONENTDEFINITION (ID, IDMATERIAL): o item tem corpo próprio
    acabamentos: dict = field(default_factory=dict)  # MODELS: face → acabamento ('ext', 'int', 'fita', 'fita_fro')
    abertura: dict = None         # OPENSERVICE (TYPE, MAX, X, Y, Z, INVERT, CURRENTVALUE): porta, gaveta, correr
    invertido: bool = False       # INVERTED="true": a peça espelhada, que as fórmulas do OPENSERVICE leem como $I$
    rotacao_propria: bool = True  # False: o ângulo veio do pai (a porta aberta guarda o giro só na posição)
    furo: dict = None             # HOLE: {'ativo': PRICK="Y", 'profundidade': DEPTH em mm ou None}; None sem HOLE
    materiais_por_trecho: dict = field(default_factory=dict)
    filhos: list = field(default_factory=list)


@dataclass
class Material:
    id: str
    nome: str
    cor: tuple
    textura: str = None          # entrada do ZIP, já normalizada
    textura_do_sistema: str = None   # %PastaTextures%: biblioteca instalada do Promob, que não vem no arquivo
    escala: tuple = None          # mm (largura, altura) de uma repetição da textura
    transparencia: float = 0.0    # TRANSPARENCY, 0 a 1
    acabamento: str = ''          # FINISHSCHEME (Mirror, ...)


@dataclass
class Ambiente:
    indice: int
    entrada: str
    nome: str
    contagem: int
    raiz: object = None


@dataclass
class Camera:
    """Vista salva do Promob (`VIEWPOINT`): observador e alvo em mm de mundo, campo de visão em graus."""
    nome: str
    observador: tuple
    alvo: tuple
    fov: float = 50.0
    corte_anterior: float = 1.0       # ZNEAR (mm)
    corte_posterior: float = 50000.0  # ZFAR (mm)
    perspectiva: bool = True
    largura_ortogonal: float = 0.0    # ORTHOR − ORTHOL (mm)
    atual: bool = False               # a vista dinâmica (a do momento em que o projeto foi salvo)


@dataclass
class Projeto:
    ambiente: Ambiente
    itens: list
    materiais: dict
    cliente: dict
    pasta_do_documento: str
    avisos: list
    entradas: frozenset = frozenset()
    cameras: list = field(default_factory=list)
    camadas_ocultas: frozenset = frozenset()   # camadas desligadas no Promob (LAYERSTATUS `<camada>_Visual` ON="N")
    material_do_piso: str = None   # REGIONS do PisoTeto: o material do piso do ambiente


def _normalizar(nome):
    return nome.replace('\\', '/')


def _insegura(nome):
    n = _normalizar(nome)
    return n.startswith('/') or re.match(r'^[A-Za-z]:', n) is not None or '..' in n.split('/')


def _numero(e, chave, padrao=0.0):
    if e is None:
        return padrao
    valor = e.get(chave)
    if valor is None or not valor.strip():
        return padrao
    try:
        return float(valor.strip().replace(',', '.'))
    except ValueError:
        return padrao


def _texto_numero(e):
    if e is None or e.text is None or not e.text.strip():
        return None
    try:
        return float(e.text.strip().replace(',', '.'))
    except ValueError:
        return None


def _xml(dados, nome):
    if dados.startswith(b'\xef\xbb\xbf'):
        dados = dados[3:]
    cabeca = dados[:4096].upper()
    if b'<!DOCTYPE' in cabeca or b'<!ENTITY' in cabeca:
        raise PromobErro(f'O arquivo tem um XML com declarações não aceitas ({posixpath.basename(nome)}).')
    try:
        return ET.fromstring(dados)
    except ET.ParseError as exc:
        raise PromobErro(f'O arquivo tem um XML ilegível ({posixpath.basename(nome)}).') from exc


class Pacote:
    """O ZIP aberto em memória, com as entradas seguras indexadas pelo nome normalizado."""

    def __init__(self, origem):
        dados = origem if isinstance(origem, (bytes, bytearray)) else open(origem, 'rb').read()
        try:
            self._zip = zipfile.ZipFile(io.BytesIO(dados))
            infos = self._zip.infolist()
        except (zipfile.BadZipFile, OSError, ValueError) as exc:
            raise PromobErro('O arquivo não é um projeto do Promob válido.') from exc
        if len(infos) > MAX_ENTRADAS:
            raise PromobErro('O arquivo tem entradas demais para um projeto do Promob.')
        if sum(i.file_size for i in infos) > MAX_TOTAL:
            raise PromobErro('O arquivo é grande demais depois de descompactado.')
        self.avisos, self._entradas = [], {}
        for info in infos:
            if info.is_dir():
                continue
            if _insegura(info.filename):
                self.avisos.append(f'Entrada recusada (caminho inválido): {info.filename[:80]}')
                continue
            if info.file_size > MAX_ENTRADA:
                self.avisos.append(f'Entrada grande demais ignorada: {posixpath.basename(_normalizar(info.filename))}')
                continue
            self._entradas[_normalizar(info.filename)] = info
        self._ambientes = None

    def nomes(self):
        return sorted(self._entradas)

    def ler(self, nome):
        """Bytes de uma entrada segura; a licença do Promob nunca (RN-01)."""
        if posixpath.basename(nome).lower() == ARQUIVO_DE_LICENCA:
            raise PromobErro('A licença do Promob não é lida.')
        info = self._entradas.get(nome)
        if info is None:
            return None
        try:
            return self._zip.read(info)
        except (zipfile.BadZipFile, OSError, RuntimeError, EOFError, zlib.error) as exc:
            raise PromobErro('O arquivo está corrompido.') from exc

    def procurar(self, sufixo):
        sufixo = sufixo.lower()
        return next((n for n in self.nomes() if n.lower().endswith(sufixo)), None)

    def ambientes(self):
        if self._ambientes is None:
            chaves = sorted((n for n in self._entradas if n.lower().endswith('.ambient3d')),
                            key=lambda n: [int(t) if t.isdigit() else t for t in re.split(r'(\d+)', n)])
            if not chaves:
                raise PromobErro('O arquivo não tem ambiente 3D.')
            self._ambientes = []
            for i, chave in enumerate(chaves):
                raiz = _xml(self.ler(chave), chave)
                nome = raiz.get('NAME') or f'Ambiente {i + 1}'
                self._ambientes.append(Ambiente(i, chave, nome, sum(1 for _ in raiz.iter('INFORMACOES')), raiz))
        return self._ambientes

    def maior_ambiente(self):
        return max(self.ambientes(), key=lambda a: a.contagem).indice

    def projeto(self, indice=None):
        ambientes = self.ambientes()
        if indice is None:
            indice = self.maior_ambiente()
        if not 0 <= indice < len(ambientes):
            raise PromobErro(f'O ambiente {indice + 1} não existe; o arquivo tem {len(ambientes)}.')
        ambiente = ambientes[indice]
        topo = ambiente.raiz.find('INFORMACOES')
        padrao = _acabamentos(ambiente.raiz.find('MODELMANAGER'), None, 'MODELS//MODEL')
        itens = _filhos(topo, 0.0, padrao) if topo is not None else []
        return Projeto(ambiente=ambiente, itens=itens, materiais=self.materiais(), cliente=self.cliente(),
                       pasta_do_documento=posixpath.dirname(ambiente.entrada), avisos=list(self.avisos),
                       entradas=frozenset(self._entradas), cameras=_cameras(ambiente.raiz),
                       camadas_ocultas=_camadas_ocultas(ambiente.raiz),
                       material_do_piso=_material_das_faces(topo)[0] if topo is not None else None)

    def materiais(self):
        chave = self.procurar('.material')
        if chave is None:
            return {}
        raiz = _xml(self.ler(chave), chave)
        out = {}
        for m in raiz.iter('MATERIAL'):
            mid = m.get('ID')
            if not mid:
                continue
            c = m.find('COLORBASE')
            cor = tuple(int(_numero(c, k)) & 255 for k in 'RGB') if c is not None else (0xC8, 0xC8, 0xC8)
            arquivo = m.find('TEXTUREFILES/TEXTUREFILE')
            if arquivo is None:
                arquivo = m.find('TEXTUREFILE')
            textura = sistema = None
            if arquivo is not None and (arquivo.text or '').strip():
                bruto = _normalizar(arquivo.text.strip())
                marca = re.match(r'^%([^%]+)%/*(.*)$', bruto)
                if marca and marca.group(1).lower() == 'pastamytextures':
                    alvo = 'mytextures/' + marca.group(2).lower()
                    textura = next((n for n in self._entradas if n.lower().endswith(alvo)), None)
                else:
                    sistema = bruto
            ex, ey = _texto_numero(m.find('ESCALETEXTUREX')), _texto_numero(m.find('ESCALETEXTUREY'))
            escala = (ex or 1000.0, ey or ex or 1000.0) if (ex or ey) else None
            transparencia = min(max(_texto_numero(m.find('TRANSPARENCY')) or 0.0, 0.0), 1.0)
            out[mid] = Material(mid, m.get('NAME') or mid, cor, textura, sistema, escala, transparencia,
                                (m.findtext('FINISHSCHEME') or '').strip())
        return out

    def cliente(self):
        chave = self.procurar('.dataclient')
        if chave is None:
            return {}
        raiz = _xml(self.ler(chave), chave)
        return {e.get('NAME'): e.get('VALUE').strip() for e in raiz.iter('FIELD')
                if e.get('NAME') and (e.get('VALUE') or '').strip()}


def _descricao(info):
    for a in info.findall('ATTRIBUTES/ATTRIBUTE'):
        if (a.get('ID') or '').upper() == 'DESCRIPTION' and (a.get('VALUE') or '').strip():
            return a.get('VALUE').strip()
    return info.get('ID') or info.get('TYPE') or 'Item'


def _material_das_faces(info):
    contagem, por_trecho = {}, {}
    for r in info.findall('REGIONS/*'):
        m = r.find('MATERIAL')
        mid = m.get('ID') if m is not None else None
        if not mid:
            continue
        contagem[mid] = contagem.get(mid, 0) + 1
        achado = re.search(r'INDICEFORMA_(\d+)', r.get('ID') or '')
        if achado:
            por_trecho.setdefault(int(achado.group(1)), mid)
    comum = max(contagem, key=contagem.get) if contagem else None
    return comum, por_trecho


_FACE_DO_MODELO = re.compile(r'_ass_.*?_(ext|int|fita_fro|fita)$', re.IGNORECASE)


def _acabamentos(info, do_pai, caminho='MODELS//MODEL'):
    """Acabamento de cada face pelo modelo do item (`dor_ass_cores_ext` → `dor_branco`), herdando o do pai.

    É o que o Promob põe no lugar do `cin_cor_000` ("cor do modelo") dos componentes. O `MODELMANAGER` do ambiente dá
    o padrão de quem não traz modelo."""
    out = dict(do_pai or {})
    if info is None:
        return out
    for m in info.findall(caminho):
        face = _FACE_DO_MODELO.search(m.get('IDMODEL') or '')
        if face and m.get('IDMODELTYPE') and m.find('MODEL') is None:
            out[face.group(1).lower()] = m.get('IDMODELTYPE')
    return out


def _furo(info):
    """O furo que o item faz no hospedeiro (`HOLE`): ativo só com `PRICK="Y"` (o `DEPTH` sozinho não fura)."""
    h = info.find('HOLE')
    if h is None:
        return None
    profundidade = _numero(h, 'DEPTH', 0.0)
    return dict(ativo=(h.get('PRICK') or '').upper() == 'Y', profundidade=profundidade if profundidade > 0 else None)


def _ponto(e):
    return (_numero(e, 'X'), _numero(e, 'Y'), _numero(e, 'Z'))


def _camera(v, atual=False):
    obs, alvo = v.find('PTOBSERVER'), v.find('PTTARGET')
    if obs is None or alvo is None:
        return None
    return Camera(nome=(v.get('NAME') or v.get('ID') or 'Vista').strip()[:63], observador=_ponto(obs), alvo=_ponto(alvo),
                  fov=_texto_numero(v.find('FOV')) or 50.0, corte_anterior=_numero(v, 'ZNEAR', 1.0) or 1.0,
                  corte_posterior=_numero(v, 'ZFAR', 50000.0) or 50000.0, perspectiva=v.get('PERSPECTIVA') != 'N',
                  largura_ortogonal=abs(_numero(v, 'ORTHOR') - _numero(v, 'ORTHOL')), atual=atual)


def _camadas_ocultas(raiz):
    """Camadas desligadas no momento em que o projeto foi salvo (o Promob guarda o estado da vista por camada)."""
    out = set()
    for s in raiz.findall('LAYERSTATUSMANAGER//LAYERSTATUS'):
        nome = s.get('LAYER') or ''
        if s.get('ON') == 'N' and nome.endswith('_Visual'):
            out.add(nome[:-len('_Visual')])
    return frozenset(out)


def _cameras(raiz):
    """As vistas salvas (`VIEWPOINTCOLLECTION`) e, por último, a vista dinâmica (`VIEWPOINT` do ambiente)."""
    out = [c for c in (_camera(v) for v in raiz.findall('VIEWPOINTCOLLECTION/VIEWPOINT')) if c is not None]
    atual = raiz.find('VIEWPOINT')
    if atual is not None:
        c = _camera(atual, atual=True)
        if c is not None:
            out.append(c)
    return out


def _item(info, rotacao_do_pai, acabamentos_do_pai=None):
    pos = info.find('POSICAOINSERCAO')
    base = pos.find('PONTOBASE') if pos is not None else None
    rotacao = _texto_numero(pos.find('ROTATION')) if pos is not None else None
    propria = rotacao is not None
    rotacao = rotacao_do_pai if rotacao is None else rotacao
    dim = info.find('INSERTDIMENSION')
    componente = info.find('COMPONENTDEFINITIONCOLLECTION/COMPONENTDEFINITION')
    geometria = info.find('GEOMETRY')
    forma = geometria.find('SHAPE') if geometria is not None else None
    pontos = []
    if forma is not None:
        for p in forma:
            if p.tag.startswith('POINT2D'):
                # Parede: E é a espessura (150 quando falta); laje: A é o ângulo do arco até o ponto seguinte.
                extra = _numero(p, 'E', 150.0) if p.tag == 'POINT2DGP' else _numero(p, 'A')
                pontos.append((_numero(p, 'X'), _numero(p, 'Y'), extra))
    arquivo = info.find('FILE3D')
    camada = info.find('LAYER')
    normal = pos.find('NORMAL') if pos is not None else None
    vetor = (_numero(normal, 'A'), _numero(normal, 'B'), _numero(normal, 'C')) if normal is not None else None
    if vetor is not None and (sum(v * v for v in vetor) < 1e-9 or vetor == (0.0, 0.0, 1.0)):
        vetor = None
    mn, mx = info.find('LIMITS/MIN'), info.find('LIMITS/MAX')
    limites = None
    if mn is not None and mx is not None:
        lo = (_numero(mn, 'X'), _numero(mn, 'Y'), _numero(mn, 'Z'))
        hi = (_numero(mx, 'X'), _numero(mx, 'Y'), _numero(mx, 'Z'))
        if all(hi[k] - lo[k] > 1e-6 for k in range(3)):
            limites = (lo, hi)
    bmn, bmx = info.find('LIMITS/MINBASE'), info.find('LIMITS/MAXBASE')
    limites_base = None
    if bmn is not None and bmx is not None:
        limites_base = ((_numero(bmn, 'X'), _numero(bmn, 'Y')), (_numero(bmx, 'X'), _numero(bmx, 'Y')))
    comum, por_trecho = _material_das_faces(info)
    item = Item(
        tipo=info.get('TYPE') or '', id=info.get('ID') or '', nome=_descricao(info),
        camada=(camada.get('DESCRIPTION') or '') if camada is not None else '',
        visivel=info.get('VISIBLE') != 'N',
        base=(_numero(base, 'X'), _numero(base, 'Y'), _numero(base, 'Z')), rotacao=rotacao,
        largura=_numero(dim, 'WIDTH'), altura=_numero(dim, 'HEIGHT'), profundidade=_numero(dim, 'DEPTH'),
        material=componente.get('IDMATERIAL') if componente is not None else None,
        material_das_faces=comum, materiais_por_trecho=por_trecho, pontos=pontos,
        alinhamento=(forma.get('ALIGNMENT') or '') if forma is not None else '',
        invertido_x=geometria is not None and geometria.get('INVERTEDX') == 'Y',
        invertido_y=geometria is not None and geometria.get('INVERTEDY') == 'Y',
        arquivo_3d=_normalizar(arquivo.get('NAME')) if arquivo is not None and arquivo.get('LINKEDFILE') == 'Y'
        and arquivo.get('NAME') else None, normal=vetor, limites=limites,
        componentes=[(c.get('ID') or '', c.get('IDMATERIAL') or '')
                     for c in info.findall('COMPONENTDEFINITIONCOLLECTION/COMPONENTDEFINITION')],
        acabamentos=_acabamentos(info, acabamentos_do_pai),
        abertura=dict(info.find('OPENSERVICE').attrib) if info.find('OPENSERVICE') is not None else None,
        invertido=(info.get('INVERTED') or '').lower() == 'true', rotacao_propria=propria, furo=_furo(info),
        limites_base=limites_base)
    item.filhos = _filhos(info, rotacao, item.acabamentos)
    return item


def _filhos(info, rotacao, acabamentos=None):
    colecao = info.find('INFORMACOESCOLECAO')
    if colecao is None:
        return []
    return [_item(c, rotacao, acabamentos) for c in colecao.findall('INFORMACOES')]


def abrir(origem):
    return Pacote(origem)
