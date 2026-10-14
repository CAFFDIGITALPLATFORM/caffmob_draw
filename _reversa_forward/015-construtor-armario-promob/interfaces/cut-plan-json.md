# Contrato: JSON de produção (`caffmob_draw.project`) 2.3.0

> Feature: `015-construtor-armario-promob` · Decisões D-02, D-03, D-09, D-14 · Arquivo: `caffmob_draw/cutting/json_exporter.py`
> Contrato anterior: `_reversa_forward/008-editor-armario-construtor/interfaces/cut-plan-json.md` (2.2.0)

## Mudança

Versão `2.2.0` → **`2.3.0`** (menor, compatível).

1. **`modules[].structure_id`** (string ou null): a estrutura de caixa do módulo CAFF MOBI. `null` = construção antiga
   ou módulo de outra biblioteca.

```json
"modules": [
  {"uid": "a1b2", "name": "Inferior c/ Divisória 800", "line": "COZ", "structure_id": "coz_inferior_divisoria"}
]
```

2. **`parts[]` com nomes de papel novos.** Só nos módulos com `structure_id`:

| `name` | `component` | Observação |
|---|---|---|
| `Sarrafo frontal`, `Sarrafo traseiro` | `SAR` | Comprimento = vão interno; largura = `stretcher_width` do padrão |
| `Sarrafo inteiro` | `SAR` | Profundidade toda |
| `Tampo linear` | `TAMP` | Profundidade + `top_overhang` |
| `Rodapé frontal` | `ROD` | Altura = `toe_kick_height`; recuo = `toe_kick_setback` |
| `Travessa traseira` | `TRA` | Fundo TRAVESSAS: duas peças |
| `Fundo` | `FUN_INF`, `FUN_SUP` ou `FUN_ALT` | Pelo grupo da estrutura (antes: sempre `FUN_INF`) |
| `Calceiro`, `Sapateira` | `ESP` | Internos de dormitório de chapa |

Uma estrutura sem Base Superior não exporta `Base superior`. A prateleira e a divisória `INVISIBLE` (e `DIVISION_ONLY`)
não geram peça.

3. **`hardware[].code`** ganha `TUBO_CABIDEIRO`, `CALCEIRO_ARAMADO`, `PORTA_CINTOS` e `RODIZIO`.

## Compatibilidade

- `SCHEMA_VERSION = "2.3.0"`, `SUPPORTED_MAJOR = 2`. O leitor aceita de 2.0 a 2.3.
- `structure_id` ausente = `null`. Leitores 2.0 a 2.2 ignoram o campo novo; os nomes de peça são texto livre.
- Módulos sem `structure_id`: as mesmas peças, nomes e uids da 2.2. Isso é verificado em teste de regressão.

## Erros

- `structure_id` gravado no módulo mas ausente do catálogo instalado: o módulo é exportado com a construção antiga,
  `structure_id` com o valor gravado e `limit_status` = `"STRUCTURE_UNKNOWN"`.
- Peça com dimensão ≤ 0, por exemplo um sarrafo num vão menor que 50 mm: não é exportada e entra em `limit_status`
  como `"PART_DEGENERATE"`, com o nome da peça.

## Idempotência

A ordem das peças de um módulo segue a ordem dos papéis em `carcass_parts`: laterais, bases, sarrafos, tampo,
rodapé, fundo, travessas, prateleiras e frentes. Exportar duas vezes o mesmo projeto gera o mesmo arquivo.

## Timeouts

n/a (escrita local, atômica: temporário + `os.replace`, como na 2.2).
