---
schema_version: 1
id: BUG-20261014-RWU2
display_number: 143
title: "Modelos prontos aparecem com a mesma miniatura na grade da biblioteca"
status: resolved
phase: delivering
severity: medium
priority: P1
created: 2026-10-14
updated: 2026-10-14

origin:
  type: manual-report
  external_ref: null

area: interface
module: library_panel
feature: unclassified
labels: ["spec-gap"]

change_risk:
  classification: baixa
  reasons: ["só o desenho da célula da grade", "sem dados nem contrato externo", "reversível pelo diff"]

visibility: normal
security_suspected: false

reproduction:
  classification: deterministic
  rate: "1/1"
  suspected_triggers: []

blocking: []

relationships: []

traceability:
  specs: ["_reversa_forward/014-texturas-fabricantes-grade/requirements.md#RN-08", "_reversa_sdd/library_panel/requirements.md#RN-15"]
  affected_code: ["caffmob_draw/library_panel/draw.py", "caffmob_draw/data/library_models.json"]
  root_cause:
    state: confirmed
    hypothesis: "block_entries monta todo modelo pronto com thumb_file vazio, e _draw_block_cell cai no mesmo desenho genérico de módulo; o catálogo de modelos não tem miniatura."
    causal_path:
      - "caffmob_draw/data/library_models.json (sem miniatura por modelo)"
      - "library_panel/draw.py block_entries (thumb_file: \"\")"
      - "library_panel/draw.py _draw_block_cell (desenho genérico)"
    evidence:
      - ref: evidence/origem.md
        observation: "cinco modelos com geometria distinta e a mesma imagem na célula"
      - ref: evidence/reproduction.md
        observation: "10 de 10 pares de miniaturas idênticos pixel a pixel, 3/3 execuções"
    code_refs:
      - {file: caffmob_draw/library_panel/draw.py, symbol: block_entries, commit: 1c9ea2d}
      - {file: caffmob_draw/library_panel/draw.py, symbol: _draw_block_cell, commit: 1c9ea2d}
  reproduction_tests: ["tests/blender_bug_RWU2_model_thumbs.py"]
  regression_tests: ["tests/test_library_model_thumbs.py", "tests/blender_bug_RWU2_model_thumbs.py", "tests/blender_014_library_draw.py", "tests/blender_014_panel_smoke.py", "tests/blender_014_drag_smoke.py", "tests/blender_012_library_ui.py"]

spec_verdict: spec-gap
change_set:
  - id: CHG-001
    kind: test
    artifact: tests/test_library_model_thumbs.py
    purpose: "formas da miniatura por tipo, medidas, portas e prateleiras"
    diff: _reversa_bugs/library_panel/bugs/BUG-20261014-RWU2-modelos-prontos-com-a-mesma-miniatura/fix/CHG-001.diff
  - id: CHG-002
    kind: test
    artifact: tests/blender_bug_RWU2_model_thumbs.py
    purpose: "reprodução pela tela: nenhum par de miniaturas igual"
    diff: _reversa_bugs/library_panel/bugs/BUG-20261014-RWU2-modelos-prontos-com-a-mesma-miniatura/fix/CHG-002.diff
  - id: CHG-003
    kind: code
    artifact: caffmob_draw/library_panel/models_core.py
    purpose: "thumb_shapes: frente do módulo em escala comum"
    diff: _reversa_bugs/library_panel/bugs/BUG-20261014-RWU2-modelos-prontos-com-a-mesma-miniatura/fix/CHG-003.diff
  - id: CHG-004
    kind: code
    artifact: caffmob_draw/library_panel/draw.py
    purpose: "medidas do Padrão de Dimensões nas entradas de modelo e desenho da frente na célula"
    diff: _reversa_bugs/library_panel/bugs/BUG-20261014-RWU2-modelos-prontos-com-a-mesma-miniatura/fix/CHG-004.diff
  - id: CHG-005
    kind: specification
    artifact: _reversa_sdd/addenda/bug-BUG-20261014-RWU2-v001.md
    purpose: "miniatura do modelo pronto especificada pela primeira vez"
    diff: _reversa_sdd/addenda/bug-BUG-20261014-RWU2-v001.md
closure:
  policy: local-software
  satisfied: true
resolution_kind: fixed
---

# Modelos prontos aparecem com a mesma miniatura na grade da biblioteca

## Summary

Na aba Blocos da BIBLIOTECA CAFFMOB maximizada, os modelos prontos (balcão de 1 e 2 portas, aéreo de 1 e 2 portas,
torre) aparecem todos com o mesmo desenho de módulo. Só o nome embaixo diferencia o inferior do aéreo e do alto.

## Expected Behavior

Cada modelo pronto mostra uma miniatura que deixa ver o tipo (inferior, aéreo, alto), a proporção e as portas, como os
módulos salvos mostram a miniatura gerada ao salvar.

A spec não define a miniatura de modelo pronto: a RN-08 da feature 014 fala só da textura (a própria imagem) e do
bloco salvo ("a miniatura que já é gerada ao salvar"), e a RN-15 do legado descreve o popover "sem miniaturas".
Fica aberto para o fix se a miniatura vem de imagens no pacote, de uma renderização ao instalar ou de um desenho
paramétrico por tipo (`spec-gap`).

## Actual Behavior

`block_entries` monta toda entrada `MODEL` com `thumb_file: ""`, e `_draw_block_cell` desenha o mesmo contorno de
módulo com duas portas para todas.

## Steps to Reproduce

1. Abrir a BIBLIOTECA CAFFMOB, clicar em "Cozinha" (abre o retângulo maximizado na aba Blocos).
2. Olhar as células "Balcão 1 porta", "Balcão 2 portas", "Aéreo 1 porta", "Aéreo 2 portas" e "Torre".
3. Observado: a mesma imagem nas cinco células. Esperado: imagens diferentes por modelo.

## Evidence

- `evidence/origem.md`: relato, achado A016 da auditoria da 014 e a medição da geometria no Blender 5.2.
- Relato bruto: `../../intake/relato-20261014-0900.md`, problema 1.

## Suspected Area

- `caffmob_draw/library_panel/draw.py` (`block_entries`, `_draw_block_cell`)
- `caffmob_draw/data/library_models.json` (catálogo sem campo de miniatura)

## Acceptance Criteria

- Os cinco modelos prontos mostram miniaturas distintas, que deixam ver o tipo (inferior, aéreo, alto) e o número de
  portas.
- Um modelo novo no catálogo sem miniatura continua aparecendo (com o desenho genérico), sem erro.
- Um teste de reprodução falha antes da correção e passa depois; o teste de regressão fica em `tests/`.

## Traceability

- Specs: `_reversa_forward/014-texturas-fabricantes-grade/requirements.md#RN-08`, `_reversa_sdd/library_panel/requirements.md#RN-15`
- Código afetado: `caffmob_draw/library_panel/draw.py`, `caffmob_draw/data/library_models.json`
- Causa raiz: confirmada e corrigida (`evidence/reproduction.md`): o catálogo não tem miniatura e `block_entries` monta toda entrada `MODEL` sem imagem, caindo no desenho genérico.
- Relações propostas:
- nenhuma com bugs registrados; ligado ao achado A016 da auditoria da 014 (não é bug registrado)

## Resolution

- **Causa raiz (confirmed):** o catálogo de modelos não tem miniatura; `block_entries` montava toda entrada `MODEL` com
  `thumb_file: ""` e `_draw_block_cell` desenhava o mesmo contorno genérico (`evidence/reproduction.md`: 10/10 pares
  iguais, 3/3 execuções).
- **Estratégia (escolha do titular):** desenho da frente por modelo, com as medidas do Padrão de Dimensões em escala
  comum; plano em `fix/plan.html`, aprovado em 2026-10-14.
- **Veredito de spec (aprovado por Leonardo Lima em 2026-10-14, aprovação geral):** `spec-gap`; adendo aditivo
  `_reversa_sdd/addenda/bug-BUG-20261014-RWU2-v001.md`.
- **resolution_kind:** fixed

| CHG | tipo | artefato | propósito | diff |
|---|---|---|---|---|
| CHG-001 | test | `tests/test_library_model_thumbs.py` | formas por tipo, medidas, portas e prateleiras | `fix/CHG-001.diff` |
| CHG-002 | test | `tests/blender_bug_RWU2_model_thumbs.py` | reprodução pela tela | `fix/CHG-002.diff` |
| CHG-003 | code | `caffmob_draw/library_panel/models_core.py` | `thumb_shapes` | `fix/CHG-003.diff` |
| CHG-004 | code | `caffmob_draw/library_panel/draw.py` | medidas do padrão e `_draw_model_front` | `fix/CHG-004.diff` |
| CHG-005 | specification | `_reversa_sdd/addenda/bug-BUG-20261014-RWU2-v001.md` | miniatura do modelo pronto | adendo |

**Vermelho (antes):** `test_library_model_thumbs`: 8 erros (`thumb_shapes` não existe);
`blender_bug_RWU2_model_thumbs`: "nenhum par de miniaturas igual" FALHA com 10 pares iguais.

**Verde (depois):** `test_library_model_thumbs` OK (8); `blender_bug_RWU2_model_thumbs` OK (0 pares iguais, nenhuma
vazia, sem exceção); regressão `test_library_models`, `test_library_grid`, `test_library_max_layout`,
`test_library_layout`, `test_i18n_coverage`, `blender_014_library_draw`, `blender_014_panel_smoke`,
`blender_014_drag_smoke`, `blender_012_library_ui`, `blender_009_library_smoke` OK; `ruff` limpo; `check_api.py` OK.
Captura conferida a olho: balcão no piso com rodapé, aéreo no alto, torre na altura toda, portas e puxadores.

## Agent Notes

- O titular escolheu medium/P1 em 2026-10-14.
- O titular descartou as leituras "mesma construção" (balcão e aéreo com a mesma caixa, sem rodapé ou travessas
  próprios) e "poucos modelos". A construção por tipo, no estilo do Promob, entra na feature do construtor de armário
  (`/reversa-requirements`), pedida no mesmo relato.
- `feature: unclassified`: a feature 014 ainda não está na taxonomia.
- A spec da miniatura do modelo pronto não existe (`spec-gap`); o veredito fica com o fix.
- Não corrigir neste registro: a correção é do `/reversa-debugger-fix` com os gates do `control_mode: gated`.
