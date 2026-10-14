"""
Gera os casos-ouro de peças do contrato caffmob.modulo/v1 a partir do extrator real do addon.

Feature 061 do CAFF MOBI (T008). Roda em Python puro, sem Blender: o pacote `cutting` não importa
`bpy`, então o `extract_parts_from_scene` recebe uma cena simulada com um módulo por caso.

O addon guarda em metros; o contrato, em milímetros arredondados a 0,1 mm com o meio para longe do
zero (a mesma regra de `shared/caffmob/numeros.ts` do MOBI, não o `round()` do Python).

`name` e `material` ficam fora do esperado: o extrator escreve rótulos fixos ("MDF Branco TX"), e o
contrato define esses dois campos pelo nome do módulo e pelo material escolhido (RN-13).

Uso: python3 tests/gerar_casos_ouro_pecas.py <pasta-de-saida>
"""

import json
import math
import sys
import uuid
from pathlib import Path
from types import SimpleNamespace

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "blendertomob"))

from cutting.part_extractor import extract_parts_from_scene  # noqa: E402

NAMESPACE = uuid.UUID("6f0b1c2e-0610-4d72-9c1a-caff0b0d0061")

TIPOS = {
    "BASE": (800, 700, 550),
    "WALL": (800, 700, 350),
    "TALL": (600, 2100, 550),
}
PORTAS = ["NONE", "LEFT", "RIGHT", "DOUBLE", "FLIP"]
ESPESSURA = 15

CONSTRUCAO_DE_FABRICA = {
    "laterais": "PASSANTE",
    "tampo": "ENTRE_LATERAIS",
    "fundo": {"modo": "CANAL", "espessura": 6, "encaixe": 8},
    "rodape": {"altura": 0, "recuo": 0},
    "porta": {"modo": "SOBREPOSTA", "folga": 2, "folga_central": 2, "espessura": 18},
    "prateleiras": {"quantidade": 1, "recuo_frontal": 20, "folga_lateral": 1, "espessura": 15},
    "divisorias": {"quantidade": 0},
    "gavetas": {"quantidade": 0, "altura_frente": 180},
    "travessas": {"quantidade": 0, "largura": 80},
    "fitas": {"frente": 1, "demais": 0.45, "portas": 1},
}


def arredondar_medida(mm):
    escalado = abs(mm) * 10
    inteiro = math.floor(escalado + 0.5 + escalado * sys.float_info.epsilon)
    valor = math.copysign(inteiro, mm) / 10
    return 0 if valor == 0 else valor


def numero(valor):
    """Inteiro quando não tem fração, para o JSON ficar igual ao do TypeScript."""
    return int(valor) if float(valor).is_integer() else valor


def cena_com(modulo_id, largura, altura, profundidade, portas):
    cab = SimpleNamespace(
        width=largura / 1000, height=altura / 1000, depth=profundidade / 1000,
        thickness=ESPESSURA / 1000, door_swing=portas,
    )
    obj = SimpleNamespace(type="MESH", name=modulo_id, btm_plane=SimpleNamespace(object_kind="MODULE"), btm_cabinet=cab)
    return SimpleNamespace(scene=SimpleNamespace(btm_settings=SimpleNamespace(dimension_settings=None), objects=[obj]))


def caso(tipo, portas):
    largura, altura, profundidade = TIPOS[tipo]
    nome = f"pecas-addon-{tipo.lower()}-{portas.lower()}"
    modulo_id = str(uuid.uuid5(NAMESPACE, nome))
    pecas = []
    for parte in extract_parts_from_scene(cena_com(modulo_id, largura, altura, profundidade, portas)):
        bruto = parte.to_dict()
        pecas.append({
            "id": bruto["id"],
            "width": numero(arredondar_medida(bruto["width"])),
            "height": numero(arredondar_medida(bruto["height"])),
            "quantity": bruto["quantity"],
            "thickness": numero(arredondar_medida(bruto["thickness"])),
            "grain_direction": bruto["grain_direction"],
            "module_ref": bruto["module_ref"],
            "edges": {lado: numero(valor) for lado, valor in bruto["edges"].items()},
        })
    return {
        "caso": nome,
        "descricao": f"Módulo {tipo} {largura} × {altura} × {profundidade} × {ESPESSURA}, portas {portas}, padrão de fábrica. "
                     "Gerado pelo cutting/part_extractor.py do addon (caffmob_draw@4b87c21); name e material ficam fora (RN-13).",
        "tipo": "modulo",
        "origem": "addon",
        "revisadoPor": None,
        "revisadoEm": None,
        "entrada": {
            "schema": "caffmob.modulo/v1", "id": modulo_id, "version": 1,
            "atualizado_em": "2026-10-14T00:00:00.000Z", "origem": "blender",
            "nome": f"Módulo {tipo} {portas}", "tipo": tipo,
            "largura": largura, "altura": altura, "profundidade": profundidade, "espessura": ESPESSURA,
            "material": "MDF", "portas": portas,
            "construcao": CONSTRUCAO_DE_FABRICA, "chapas_editadas": [],
        },
        "esperado": {"pecas": pecas},
    }


def principal():
    saida = Path(sys.argv[1] if len(sys.argv) > 1 else "casos-ouro-pecas")
    saida.mkdir(parents=True, exist_ok=True)
    for tipo in TIPOS:
        for portas in PORTAS:
            dados = caso(tipo, portas)
            (saida / f"{dados['caso']}.json").write_text(json.dumps(dados, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            print(dados["caso"], len(dados["esperado"]["pecas"]), "peças")


if __name__ == "__main__":
    principal()
