"""
Números, serialização e unidades do contrato (061 RN-03, RN-04).

- Medida arredondada a 0,1 mm e ângulo a 0,001°, com o meio para longe do zero. Nem o round() do
  Python nem o Math.round do JavaScript servem: os dois lados usam esta mesma regra escrita à mão.
- Serialização com chaves em ordem alfabética, sem espaço, e inteiro sem ".0", igual ao
  JSON.stringify do MOBI, para a ida e volta comparar o texto.
- Metros (Blender) × 1000 = milímetros (contrato). Fita de borda já é mm no addon e não converte.
"""

import json
import math
import sys

SCHEMA_AMBIENTE = "caffmob.ambiente/v1"
SCHEMA_MODULO = "caffmob.modulo/v1"
TOLERANCIA_MM = 0.1


def _arredondar_ao_passo(valor, inverso):
    escalado = abs(valor) * inverso
    inteiro = math.floor(escalado + 0.5 + escalado * sys.float_info.epsilon)
    resultado = math.copysign(inteiro, valor) / inverso
    return 0 if resultado == 0 else resultado


def numero(valor):
    """Inteiro quando não tem fração, como o JSON do JavaScript."""
    if isinstance(valor, bool) or not isinstance(valor, (int, float)):
        return valor
    return int(valor) if float(valor).is_integer() else valor


def arredondar_medida(mm):
    return numero(_arredondar_ao_passo(mm, 10))


def arredondar_angulo(graus):
    return numero(_arredondar_ao_passo(graus, 1000))


def normalizar_absoluto(graus):
    valor = arredondar_angulo(((graus % 360) + 360) % 360)
    return 0 if valor >= 360 else valor


def normalizar_relativo(graus):
    valor = ((graus % 360) + 360) % 360
    if valor > 180:
        valor -= 360
    valor = arredondar_angulo(valor)
    return 180 if valor <= -180 else valor


def metros_para_mm(metros):
    return arredondar_medida(metros * 1000)


def mm_para_metros(mm):
    return mm / 1000


def _normalizar_numeros(valor):
    if isinstance(valor, dict):
        return {chave: _normalizar_numeros(item) for chave, item in valor.items()}
    if isinstance(valor, list):
        return [_normalizar_numeros(item) for item in valor]
    return numero(valor)


def serializar(documento):
    """Mesmo texto que o serializar() do núcleo do MOBI."""
    return json.dumps(_normalizar_numeros(documento), sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def ler_documento(texto):
    valor = json.loads(texto)
    if not isinstance(valor, dict):
        raise ValueError("O documento precisa ser um objeto JSON.")
    return valor


def sem_envelope_do_servidor(documento):
    return {chave: valor for chave, valor in documento.items() if chave not in ("version", "atualizado_em", "origem")}


# Campos de medida que o Blender guarda em metros (os mesmos do núcleo do MOBI).
MEDIDAS = {
    "origem": ("x", "y"),
    "segmento": ("comprimento", "espessura", "pe_direito_inicial", "pe_direito_final", "afastamento", "flecha"),
    "abertura": ("posicao", "largura", "altura", "peitoril"),
    "modulo": ("largura", "altura", "profundidade", "espessura"),
    "posicao": ("x", "y", "z"),
    "fundo": ("espessura", "encaixe"),
    "rodape": ("altura", "recuo"),
    "porta": ("folga", "folga_central", "espessura"),
    "prateleiras": ("recuo_frontal", "folga_lateral", "espessura"),
    "gavetas": ("altura_frente",),
    "travessas": ("largura",),
    "edicao": ("largura", "altura", "espessura"),
}


def _campos(objeto, campos, conversao):
    copia = dict(objeto)
    for campo in campos:
        if isinstance(copia.get(campo), (int, float)) and not isinstance(copia.get(campo), bool):
            copia[campo] = conversao(copia[campo])
    return copia


def _modulo(modulo, conversao):
    copia = _campos(modulo, MEDIDAS["modulo"], conversao)
    if isinstance(copia.get("posicao"), dict):
        copia["posicao"] = _campos(copia["posicao"], MEDIDAS["posicao"], conversao)
    if isinstance(copia.get("construcao"), dict):
        construcao = dict(copia["construcao"])
        for bloco in ("fundo", "rodape", "porta", "prateleiras", "gavetas", "travessas"):
            if isinstance(construcao.get(bloco), dict):
                construcao[bloco] = _campos(construcao[bloco], MEDIDAS[bloco], conversao)
        copia["construcao"] = construcao
    if isinstance(copia.get("chapas_editadas"), list):
        copia["chapas_editadas"] = [_campos(edicao, MEDIDAS["edicao"], conversao) for edicao in copia["chapas_editadas"]]
    return copia


def _converter(documento, conversao):
    if documento.get("schema") == SCHEMA_MODULO:
        return _modulo(documento, conversao)
    copia = dict(documento)
    if isinstance(copia.get("paredes"), list):
        copia["paredes"] = [
            {**parede, "origem": _campos(parede["origem"], MEDIDAS["origem"], conversao),
             "segmentos": [_campos(segmento, MEDIDAS["segmento"], conversao) for segmento in parede["segmentos"]]}
            for parede in copia["paredes"]
        ]
    if isinstance(copia.get("aberturas"), list):
        copia["aberturas"] = [_campos(abertura, MEDIDAS["abertura"], conversao) for abertura in copia["aberturas"]]
    if isinstance(copia.get("modulos"), list):
        copia["modulos"] = [_modulo(modulo, conversao) for modulo in copia["modulos"]]
    return copia


def para_metros(documento):
    """Contrato (mm) para as unidades do Blender (m)."""
    return _converter(documento, mm_para_metros)


def de_metros(documento):
    """Blender (m) para o contrato (mm), arredondado a 0,1 mm."""
    return _converter(documento, metros_para_mm)
