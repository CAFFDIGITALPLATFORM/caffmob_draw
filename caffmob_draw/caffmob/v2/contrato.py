"""Tipos de transporte e limites do contrato fechado shared/studio/tipos.ts."""
from typing import Literal, NotRequired, TypedDict

SCHEMA_AMBIENTE = SCHEMA_STUDIO = "caffmob.ambiente/v2"
SCHEMA_CONFIGURACAO_STUDIO = "caffmob.studio-config/v1"
TOLERANCIA_MM = 0.1
LIMITES_STUDIO = dict(bytes=1048576, entidades=300, pavimentos=13,
                      vertices_por_pavimento=400, aberturas_por_segmento=20,
                      recortes=30, pecas=20000)
FAMILIAS = ("pavimentos", "paredes", "aberturas", "modulos", "pecas_avulsas",
            "primitivas", "escadas", "itens_externos", "materiais", "camadas", "vinculos")
POSICIONAVEIS = ("paredes", "modulos", "pecas_avulsas", "primitivas", "escadas", "itens_externos")

MODELOS_DE_PORTA_GIRO = (
    "porta_giro_lisa",
    "porta_giro_almofadada",
    "porta_giro_frisada",
    "porta_giro_visor",
    "porta_giro_dupla",
)
MODELOS_DE_PORTA_CORRER = (
    "porta_correr_aparente",
    "porta_correr_embutida",
    "porta_correr_2f",
    "porta_correr_4f",
    "porta_correr_camarao",
)
MODELOS_DE_PORTA = MODELOS_DE_PORTA_GIRO + MODELOS_DE_PORTA_CORRER

MODELOS_DE_JANELA_CORRER = (
    "janela_correr_2f",
    "janela_correr_3f",
    "janela_correr_4f",
    "janela_correr_veneziana",
    "janela_correr_bandeira",
)
MODELOS_DE_JANELA_ABRIR = (
    "janela_abrir_1f",
    "janela_abrir_2f",
    "janela_abrir_bandeira",
    "janela_abrir_veneziana",
    "janela_abrir_camarao",
)
MODELOS_DE_JANELA_BASCULANTE = (
    "janela_maximar_1m",
    "janela_maximar_2m",
    "janela_maximar_fixo",
    "janela_basculante",
    "janela_pivotante",
)
MODELOS_DE_JANELA_FIXA = (
    "janela_fixa",
    "janela_panoramica",
    "janela_bay",
    "janela_veneziana_fixa",
    "janela_vitro",
)
MODELOS_DE_JANELA = (
    MODELOS_DE_JANELA_CORRER
    + MODELOS_DE_JANELA_ABRIR
    + MODELOS_DE_JANELA_BASCULANTE
    + MODELOS_DE_JANELA_FIXA
)
MODELOS_DE_ABERTURA = MODELOS_DE_PORTA + MODELOS_DE_JANELA
MATERIAIS_DE_ABERTURA = ("madeira", "aluminio", "blindex")
PADRAO_ABERTURA = {
    "DOOR": {"modelo": "porta_giro_almofadada", "material": "madeira"},
    "WINDOW": {"modelo": "janela_correr_2f", "material": "aluminio"},
}


class ErroStudio(TypedDict):
    caminho: str
    codigo: str
    mensagem: str


class Ponto2(TypedDict):
    x: float
    y: float


class Ponto3(Ponto2):
    z: float


class SegmentoStudio(TypedDict):
    id: str
    comprimento: float
    angulo_absoluto: float
    angulo_relativo: float
    espessura: float
    pe_direito_inicial: float
    pe_direito_final: float
    afastamento: float
    flecha: float
    sentido: Literal["LEFT", "RIGHT"]
    tipo: Literal["NORMAL", "DRYWALL", "GLASS"]
    estado: Literal["ativo", "oculto"]
    material_interno_id: NotRequired[str]
    material_externo_id: NotRequired[str]


class ParedeStudio(TypedDict):
    id: str
    origem: Ponto2
    fechada: bool
    pavimento_id: str
    camada_id: str | None
    visivel: bool
    perfil: Literal["studio/1", "caffmob.parede/v1"]
    segmentos: list[SegmentoStudio]
    material_id: NotRequired[str]


class AmbienteStudio(TypedDict):
    schema: Literal["caffmob.ambiente/v2"]
    id: str
    version: int
    atualizado_em: str
    origem: Literal["web", "mobile", "blender"]
    nome: str
    unidade: Literal["mm"]
    eixos: Literal["Z_UP"]
    configuracao_geometrica: dict
    pavimentos: list[dict]
    paredes: list[ParedeStudio]
    aberturas: list[dict]
    modulos: list[dict]
    pecas_avulsas: list[dict]
    primitivas: list[dict]
    escadas: list[dict]
    itens_externos: list[dict]
    materiais: list[dict]
    camadas: list[dict]
    vinculos: list[dict]
