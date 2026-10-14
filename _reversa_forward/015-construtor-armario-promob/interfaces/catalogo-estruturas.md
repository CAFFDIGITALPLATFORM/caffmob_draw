# Contrato: catálogo de estruturas de caixa (`cabinet_structures.json`) 1

> Feature: `015-construtor-armario-promob` · Decisões D-01, D-06, D-16 · Leitor: `caffmob_draw/cabinet_editor/structures_core.py`
> Arquivo: `caffmob_draw/data/cabinet_structures.json` (versionado no pacote). Unidade: mm.

## Forma

```json
{
  "schema-version": 1,
  "environments": [
    {"id": "COZ", "label_pt": "Cozinhas", "label_en": "Kitchens", "line": "COZ"},
    {"id": "DOR", "label_pt": "Dormitórios", "label_en": "Bedrooms", "line": "DOR"}
  ],
  "structures": [
    {
      "id": "coz_inferior_divisoria",
      "environment": "COZ",
      "group": "INFERIOR",
      "label_pt": "Inferior c/ Divisória",
      "label_en": "Base w/ Divider",
      "assembly": "LATERAL",
      "sides_to_floor": false,
      "bays": 1,
      "size_mm": {"width": 500, "height": null, "depth": null},
      "components": {
        "LEFT": true, "RIGHT": true, "DIVIDERS": true, "BOTTOM": true, "TOP": false,
        "STRETCHER_FRONT": true, "STRETCHER_BACK": true, "STRETCHER_FULL": false, "TOP_LINEAR": false,
        "TOE_KICK": false, "FEET": false, "KICK_GRANITE": false, "CLOSURE": false, "VIEWS": false
      },
      "division_variants": ["CORTA_SAR", "C_REB"],
      "order": 10
    }
  ],
  "legacy_map": [
    {"line": "COZ", "cabinet_type": "BASE", "structure": "coz_inferior_divisoria"},
    {"line": "COZ", "cabinet_type": "WALL", "structure": "coz_superior_divisoria"},
    {"line": "COZ", "cabinet_type": "TALL", "structure": "coz_torre_eletros"},
    {"line": "DOR", "cabinet_type": "TALL", "structure": "dor_armario"},
    {"line": "*", "cabinet_type": "BASE", "structure": "coz_inferior_divisoria"},
    {"line": "*", "cabinet_type": "WALL", "structure": "coz_superior_divisoria"},
    {"line": "*", "cabinet_type": "TALL", "structure": "coz_torre_eletros"}
  ]
}
```

| Campo | Tipo | Regra |
|---|---|---|
| `id` | texto `[a-z0-9_]+`, único | Gravado em `btm_cabinet.structure_id`; não pode mudar depois de publicado |
| `environment` | id de `environments` | Aba da galeria e filtro dos catálogos das abas |
| `group` | `INFERIOR` \| `SUPERIOR` \| `DESPENSEIRO` | Escolhe o `cabinet_type` (BASE, WALL, TALL), as medidas externas e o `group_assembly` do padrão |
| `label_pt`, `label_en` | texto | Nome na galeria e no cabeçalho "Tipo: …" |
| `assembly` | `LATERAL` \| `BASE` | Padrão quando o Padrão de Dimensões não tem `group_assembly` |
| `sides_to_floor` | booleano | Variantes "até Piso" (RN-06) |
| `bays` | inteiro 1 a 10 | Número de vãos inicial |
| `size_mm` | `width`, `height`, `depth` em mm ou `null` | `null` = vem do Padrão de Dimensões pela linha e pelo grupo |
| `components` | mapa papel → booleano | Estado inicial da árvore. Papéis válidos: `LEFT`, `RIGHT`, `DIVIDERS`, `BOTTOM`, `TOP`, `BACK`, `STRETCHER_FRONT`, `STRETCHER_BACK`, `STRETCHER_FULL`, `TOP_LINEAR`, `TOE_KICK`, `FEET`, `CASTERS`, `KICK_GRANITE`, `CLOSURE`, `VIEWS`, `VIEWS_TALL`, `BASE_TOP_RECESSED` |
| `division_variants` | lista | Variantes extras do catálogo de Divisões: `CORTA_SAR`, `C_REB`, `MONTANTE`, `INVISIBLE`, `CORREDICA`, `ARAMADA`, `NAO_DIVIDE_FUNDO` |
| `order` | inteiro | Ordem na aba da galeria |
| `legacy_map` | lista | (linha, tipo) → estrutura para a migração (RN-22); `"*"` = qualquer linha; vale a primeira entrada que casa |

## Validação e erros

O leitor devolve `(estruturas válidas, avisos)` e nunca levanta exceção (princípio VIII):
- `schema-version` diferente de 1: catálogo inteiro recusado, aviso "Catálogo de estruturas em versão desconhecida".
  Nesse caso a galeria mostra o estado vazio com o aviso, e os módulos seguem a construção antiga.
- Estrutura com `id` repetido, `environment` ou `group` desconhecido, papel desconhecido em `components` ou medida
  não numérica: só essa estrutura é pulada, com o aviso "Estrutura <id>: <motivo>" (RF-02, cenário "Estrutura
  inválida no catálogo").
- `legacy_map` apontando para estrutura inexistente: a entrada é pulada com aviso.

## Modelos

Em `data/library_models.json` (012), cada modelo aceita `"structure_id": "<id>"`. Ausente: vale o `legacy_map` com a
linha da categoria e o `cabinet_type` do modelo. Id desconhecido: o modelo é pulado com aviso, como os outros erros de
`models_core.parse`.

## Idempotência

Leitura pura, sem efeito colateral; o resultado é guardado em cache até recarregar o add-on.

## Timeouts

n/a (arquivo local do pacote).
