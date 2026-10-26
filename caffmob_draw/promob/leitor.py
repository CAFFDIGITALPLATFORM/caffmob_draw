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


@dataclass
class Ambiente:
    indice: int
    entrada: str
    nome: str
    contagem: int
    raiz: object = None


@dataclass
class Projeto:
    ambiente: Ambiente
    itens: list
    materiais: dict
    cliente: dict
    pasta_do_documento: str
    avisos: list
    entradas: frozenset = frozenset()


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
        itens = _filhos(topo, 0.0) if topo is not None else []
        return Projeto(ambiente=ambiente, itens=itens, materiais=self.materiais(), cliente=self.cliente(),
                       pasta_do_documento=posixpath.dirname(ambiente.entrada), avisos=list(self.avisos),
                       entradas=frozenset(self._entradas))

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
            out[mid] = Material(mid, m.get('NAME') or mid, cor, textura, sistema, escala)
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


def _item(info, rotacao_do_pai):
    pos = info.find('POSICAOINSERCAO')
    base = pos.find('PONTOBASE') if pos is not None else None
    rotacao = _texto_numero(pos.find('ROTATION')) if pos is not None else None
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
        and arquivo.get('NAME') else None)
    item.filhos = _filhos(info, rotacao)
    return item


def _filhos(info, rotacao):
    colecao = info.find('INFORMACOESCOLECAO')
    if colecao is None:
        return []
    return [_item(c, rotacao) for c in colecao.findall('INFORMACOES')]


def abrir(origem):
    return Pacote(origem)
