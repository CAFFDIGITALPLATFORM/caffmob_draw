"""Catálogo de corrediças (072 D-02, D-10, M-01), sem bpy.

Os seis tipos de fábrica vêm dos guias do titular (`tipos_de_gavetas_e_corredicas.md` §1 e
`guia_tecnico_gaveteiros.md` §4). As corrediças da pessoa ficam num JSON na pasta de usuário da extensão, com id
prefixado por `usuario:` para não colidir com as de fábrica. Medidas em mm.
"""
import json
import os
from dataclasses import asdict, dataclass, field

COMPRIMENTOS = (300, 350, 400, 450, 500, 550)
PREFIXO_USUARIO = 'usuario:'
ARQUIVO = 'corredicas.json'


@dataclass(frozen=True)
class Corredica:
    id: str
    nome: str
    tipo: str                      # telescopica | oculta | metalica
    folga_total: float             # desconto na largura do vão (os dois lados)
    recuo_fundo: float = 0.0       # o fundo sobe em relação à borda inferior das laterais (oculta)
    furo_traseira: float = 0.0     # diâmetro do furo do gancho na traseira (oculta)
    lateral_max: float = 0.0       # espessura máxima da lateral da gaveta; 0 = sem limite
    laterais_mdf: bool = True      # a lateral metálica já é a lateral: a marcenaria faz só fundo e costas
    lateral_fabrica: float = 0.0   # espessura da lateral metálica, descontada do fundo e das costas
    carga: str = ''
    codigo: str = ''               # código de ferragem: CORREDICA_<codigo>_<mm>
    toque: bool = False            # abertura por toque: pede recuo de 3 a 5 mm e dispensa puxador
    comprimentos: tuple = field(default=COMPRIMENTOS)

    def codigo_de_ferragem(self, mm):
        return f"CORREDICA_{self.codigo}_{int(mm)}"

    def nome_de_ferragem(self, mm):
        return f"{self.nome} {int(mm)} mm (par)"


FABRICA = (
    Corredica('telescopica', "Corrediça telescópica", 'telescopica', 26, carga="30–45 kg", codigo='TELESCOPICA'),
    Corredica('telescopica_soft', "Corrediça telescópica soft", 'telescopica', 26, carga="35–45 kg",
              codigo='TELESCOPICA_SOFT'),
    Corredica('telescopica_toque', "Corrediça telescópica toque", 'telescopica', 26, carga="30–45 kg",
              codigo='TELESCOPICA_TOQUE', toque=True),
    Corredica('oculta_soft', "Corrediça oculta soft", 'oculta', 10, recuo_fundo=12, furo_traseira=6, lateral_max=16,
              carga="30–50 kg", codigo='OCULTA_SOFT'),
    Corredica('oculta_toque', "Corrediça oculta toque", 'oculta', 10, recuo_fundo=12, furo_traseira=6,
              lateral_max=16, carga="30–50 kg", codigo='OCULTA_TOQUE', toque=True),
    Corredica('lateral_metalica', "Lateral metálica", 'metalica', 26, laterais_mdf=False, lateral_fabrica=15,
              carga="40–70 kg", codigo='METALICA'),
)


def _de_dict(d):
    campos = {k: d[k] for k in Corredica.__dataclass_fields__ if k in d}
    campos['comprimentos'] = tuple(int(v) for v in campos.get('comprimentos', COMPRIMENTOS))
    return Corredica(**campos)


def ler_usuario(pasta):
    if not pasta:
        return ()
    caminho = os.path.join(pasta, ARQUIVO)
    try:
        with open(caminho, encoding='utf-8') as f:
            dados = json.load(f)
    except (OSError, ValueError):
        return ()
    saida = []
    for d in dados if isinstance(dados, list) else []:
        try:
            c = _de_dict(d)
        except (TypeError, ValueError):
            continue
        if c.id.startswith(PREFIXO_USUARIO):
            saida.append(c)
    return tuple(saida)


def gravar_usuario(pasta, corredicas):
    os.makedirs(pasta, exist_ok=True)
    caminho = os.path.join(pasta, ARQUIVO)
    temporario = caminho + '.tmp'
    with open(temporario, 'w', encoding='utf-8') as f:
        json.dump([asdict(c) for c in corredicas if c.id.startswith(PREFIXO_USUARIO)], f, ensure_ascii=False,
                  indent=1)
    os.replace(temporario, caminho)


def todas(pasta=None):
    return FABRICA + ler_usuario(pasta)


def por_id(cid, pasta=None):
    return next((c for c in todas(pasta) if c.id == cid), None)
