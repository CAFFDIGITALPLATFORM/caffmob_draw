"""`.promob` sintético para os testes da 071 (T002; RN-01, RN-02), gerado aqui e nunca lido de um projeto real.

Imita a estrutura conferida nos projetos do titular: ZIP com separador `\\`, XML com BOM, `ALIGNMENT` da parede,
portas e janelas hospedadas pelo `WALL`, módulos com filhos, laje `GEOMETRY` com arco, entidade externa com malha
em `LinkedFiles`, materiais de cor e de textura e um `promob.info` com licença fictícia (que nunca pode ser lido).

Medidas do ambiente principal (mm):
- parede em L, alinhamento Direita (espessura 150 à esquerda), altura 2700: (0,0) → (3000,0) → (3000,2500);
- porta 800 × 2100 no trecho 1, a 1000 mm do início;
- janela 1200 × 1000, peitoril 1000, no trecho 2, a 700 mm do início;
- balcão 600 × 850 × 580 com duas laterais e uma porta.
"""
import io
import struct
import zipfile
import zlib

import _bootstrap  # noqa: F401

BOM = '﻿'
OBJ_GUID = '0f0f0f0f-0000-4000-8000-000000000071'


def _png():
    def bloco(tipo, dados):
        return struct.pack('>I', len(dados)) + tipo + dados + struct.pack('>I', zlib.crc32(tipo + dados) & 0xffffffff)
    cabeca = struct.pack('>IIBBBBB', 2, 2, 8, 2, 0, 0, 0)
    pixels = zlib.compress(b'\x00' + b'\x8b\x5a\x2b' * 2 + b'\x00' + b'\xa0\x70\x40' * 2)
    return b'\x89PNG\r\n\x1a\n' + bloco(b'IHDR', cabeca) + bloco(b'IDAT', pixels) + bloco(b'IEND', b'')


def _item(tipo, id_, base=(0, 0, 0), dim=(0, 0, 0), rot=None, nome=None, camada='Default', material=None,
          filhos=(), extra='', visivel=True, normal=None, limites=None):
    x, y, z = base
    w, h, d = dim
    rotacao = f'<ROTATION>{rot}</ROTATION>' if rot is not None else '<ROTATION />'
    atributos = f'<ATTRIBUTE ID="DESCRIPTION" VALUE="{nome}" />' if nome else ''
    componente = (f'<COMPONENTDEFINITIONCOLLECTION><COMPONENTDEFINITION NAME="c" ID="c" IDMATERIAL="{material}" />'
                  f'</COMPONENTDEFINITIONCOLLECTION>') if material else ''
    colecao = f'<INFORMACOESCOLECAO>{"".join(filhos)}</INFORMACOESCOLECAO>' if filhos else ''
    oculto = '' if visivel else ' VISIBLE="N"'
    vetor = '<NORMAL {} />'.format(' '.join(f'{k}="{v}"' for k, v in zip('ABC', normal) if v)) if normal else ''
    lim = ''
    if limites:
        (a, b, c), (e, f, g) = limites
        lim = f'<LIMITS><MIN X="{a}" Y="{b}" Z="{c}" /><MAX X="{e}" Y="{f}" Z="{g}" /></LIMITS>'
    return (f'<INFORMACOES ID="{id_}" TYPE="{tipo}"{oculto}><POSICAOINSERCAO>{vetor}<PONTOBASE X="{x}" Y="{y}" Z="{z}" />'
            f'{rotacao}</POSICAOINSERCAO><INSERTDIMENSION WIDTH="{w}" HEIGHT="{h}" DEPTH="{d}" />{lim}'
            f'<LAYER DESCRIPTION="{camada}" /><ATTRIBUTES>{atributos}</ATTRIBUTES>{componente}{extra}{colecao}'
            f'</INFORMACOES>')


def _parede(pontos, altura, hospedados=(), alinhamento='Direita', id_='PAREDE'):
    forma = ''.join(f'<POINT2DGP X="{x}" Y="{y}" NAME="" E="{e}" />' for x, y, e in pontos)
    extra = (f'<REGIONS><REGION ID="PAREDE_FACE_INFERIOR"><MATERIAL ID="reboco" /></REGION></REGIONS>'
             f'<GEOMETRY INVERTEDX="N" INVERTEDY="N"><PROFILE><POINT2DGM NAME="" /><POINT2DGM Y="1" NAME="" />'
             f'</PROFILE><SHAPE ALIGNMENT="{alinhamento}">{forma}</SHAPE></GEOMETRY>')
    return _item('WALL', id_, dim=(5000, altura, 5000), camada='Parede', extra=extra, filhos=hospedados)


def _ambiente(itens, nome=None):
    raiz = _item('PisoTeto', 'PISOTETO', filhos=itens)
    atributo = f' NAME="{nome}"' if nome else ''
    return f'{BOM}<?xml version="1.0" encoding="utf-8"?><AMBIENT3D{atributo}>{raiz}</AMBIENT3D>'


def ambiente_principal(extras=()):
    porta = _item('MODULO', 'Porta_04', base=(1000, 150, 0), dim=(800, 2100, 150), nome='Porta Externa',
                  camada='Decore-Aberturas',
                  filhos=[_item('MODULO', 'Folha', base=(1000, 120, 0), dim=(796, 2096, 35), nome='Folha')])
    janela = _item('MODULO', 'Janela_07', base=(2850, 700, 1000), dim=(1200, 1000, 150), rot=90, nome='Janela',
                   camada='Decore-Aberturas')
    revestimento = _item('MODULO', 'Revest', base=(200, 160, 900), dim=(500, 600, 10), nome='Revestimento',
                         camada='Decore', material='reboco')
    parede = _parede([(0, 0, 150), (3000, 0, 150), (3000, 2500, 150)], 2700, [porta, janela, revestimento])
    balcao = _item('MODULO', 'bal_600', base=(500, 1200, 0), dim=(600, 850, 580), nome='Balcão $W$ #COR#',
                   camada='Cozinhas-Inferiores', filhos=[
                       _item('MODULO', 'lat_esq', base=(500, 1200, 0), dim=(15, 850, 580), nome='Lateral esquerda',
                             material='cin_cor_000'),
                       _item('MODULO', 'lat_dir', base=(1085, 1200, 0), dim=(15, 850, 580), nome='Lateral direita',
                             material='cin_cor_000'),
                       _item('MODULO', 'porta_bal', base=(500, 620, 0), dim=(600, 700, 18), nome='Porta',
                             material='madeira'),
                   ])
    laje = _item('GEOMETRY', 'Piso', dim=(3000, 20, 2500), nome='Piso', material='reboco', extra=(
        '<GEOMETRY INVERTEDX="N" INVERTEDY="N"><PROFILE><POINT2DGM NAME="" /><POINT2DGM Y="1" NAME="" /></PROFILE>'
        '<SHAPE><POINT2DG NAME="" /><POINT2DG X="2000" NAME="" A="90" /><POINT2DG X="3000" Y="1000" NAME="" />'
        '<POINT2DG Y="1000" NAME="" /></SHAPE></GEOMETRY>'))
    externa = _item('ENTIDADEEXTERNA', 'EntidadeExterna', base=(1500, 1800, 850), dim=(600, 200, 400),
                    material='reboco', extra=f'<FILE3D NAME="%LinkedFilesFolder%\\{OBJ_GUID}.obj" LINKEDFILE="Y" />')
    oculto = _item('MODULO', 'oculto', base=(100, 100, 0), dim=(100, 100, 100), nome='Oculto', visivel=False)
    sem_medida = _item('MODULO', 'zero', base=(0, 0, 0), dim=(0, 0, 0), nome='Sem medida')
    luz = _item('LuzSpot', 'luz', dim=(10, 10, 10))
    teto = _item('Teto', 'teto', dim=(3000, 10, 2500))
    return _ambiente([parede, balcao, laje, externa, oculto, sem_medida, luz, teto, *extras], nome='Cozinha teste')


def ambiente_pequeno():
    parede = _parede([(0, 0, 120), (2000, 0, 120), (2000, 2000, 120), (0, 2000, 120), (0, 0, 120)], 2600,
                     alinhamento='Esquerda', id_='PAREDE2')
    return _ambiente([parede, _item('MODULO', 'aereo', base=(100, 100, 1500), dim=(800, 700, 350), nome='Aéreo')])


MATERIAIS = (f'{BOM}<?xml version="1.0" encoding="utf-8"?><MATERIALS><FOLDER><MATERIALCOLLECTION>'
             '<MATERIAL ID="reboco" NAME="Reboco"><COLORBASE R="232" G="226" B="214" /></MATERIAL>'
             '<MATERIAL ID="madeira" NAME="Madeira clara"><COLORBASE R="10" G="10" B="10" />'
             '<TEXTUREFILES><TEXTUREFILE>%PastaMyTextures%\\madeira.png</TEXTUREFILE></TEXTUREFILES>'
             '<ESCALETEXTUREX>800</ESCALETEXTUREX><ESCALETEXTUREY>400</ESCALETEXTUREY></MATERIAL>'
             '<MATERIAL ID="marmore" NAME="Mármore"><COLORBASE R="200" G="200" B="200" />'
             '<TEXTUREFILES><TEXTUREFILE>%PastaTextures%\\Fabrica\\marmore.jpg</TEXTUREFILE></TEXTUREFILES></MATERIAL>'
             '</MATERIALCOLLECTION></FOLDER></MATERIALS>')
CLIENTE = (f'{BOM}<?xml version="1.0" encoding="utf-8"?><DATACLIENT><FIELDS>'
           '<FIELD NAME="NOMECLIENTE" DESCRIPTION="Nome" VALUE="Cliente Fictício" />'
           '<FIELD NAME="EMAIL" DESCRIPTION="E-mail" VALUE="" /></FIELDS></DATACLIENT>')
LICENCA = 'SERIAL=FICTICIO-0000-0000;PRODUTO=TESTE'
OBJ = 'o caixa\nv 0 0 0\nv 1 0 0\nv 1 1 0\nv 0 1 0\nv 0 0 1\nv 1 0 1\nv 1 1 1\nv 0 1 1\n' \
      'f 1 2 3 4\nf 5 8 7 6\nf 1 5 6 2\nf 2 6 7 3\nf 3 7 8 4\nf 4 8 5 1\n'


def entradas(principal=None, extras=()):
    return {
        'promob.info': LICENCA,
        'sugestao.jpg': b'\xff\xd8\xff\xd9',
        'solucao\\solucao.container': f'{BOM}<CONTAINER />',
        'solucao\\document1\\document1.dataclient': CLIENTE,
        'solucao\\container1\\container1.container': f'{BOM}<CONTAINER />',
        'solucao\\container1\\document1\\document1.ambient3d': principal or ambiente_principal(extras),
        'solucao\\container1\\document1\\LinkedFiles\\' + OBJ_GUID + '.obj': OBJ,
        'solucao\\container1\\document2\\document2.ambient3d': ambiente_pequeno(),
        'solucao\\materials\\materials.material': MATERIAIS,
        'solucao\\materials\\MyTextures\\madeira.png': _png(),
    }


def zip_de(mapa):
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, 'w', zipfile.ZIP_DEFLATED) as z:
        for nome, dados in mapa.items():
            z.writestr(nome, dados.encode('utf-8') if isinstance(dados, str) else dados)
    return buf.getvalue()


def promob(extras=()):
    """Bytes do `.promob` sintético completo."""
    return zip_de(entradas(extras=extras))


def promob_grande(n=300):
    """Ambiente com `n` módulos soltos de três peças, para medir o tempo (RNF de desempenho)."""
    modulos = [_item('MODULO', f'm{i}', base=(i % 20 * 700, i // 20 * 700, 0), dim=(600, 720, 560), nome=f'Módulo {i}',
                     filhos=[_item('MODULO', f'm{i}l', base=(i % 20 * 700, i // 20 * 700, 0), dim=(15, 720, 560),
                                   material='reboco')]) for i in range(n)]
    return zip_de(entradas(extras=modulos))


def gravar(caminho, dados=None):
    with open(caminho, 'wb') as f:
        f.write(dados if dados is not None else promob())
    return caminho
