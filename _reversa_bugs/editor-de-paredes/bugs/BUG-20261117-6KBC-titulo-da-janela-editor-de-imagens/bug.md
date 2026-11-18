---
schema_version: 1
id: BUG-20261117-6KBC
display_number: 144
title: Janela do editor mostra Editor de Imagens em vez de Editor de Paredes CAFF MOB DRAW
status: resolved
phase: delivering
severity: low
priority: P3
created: 2026-11-17
updated: 2026-11-17

origin:
  type: manual-report
  external_ref: null

area: paredes
module: walls2d
feature: 002-editor-parede-mover-sobre
labels: [spec-gap, interface, titulo-da-janela]

visibility: normal
security_suspected: false

reproduction:
  classification: deterministic
  rate: "1/1 (captura do titular e código-fonte do Blender; teste vermelho antes do change set, verde depois)"
  suspected_triggers: []

blocking: []

relationships: []

traceability:
  specs: ["_reversa_sdd/walls2d/requirements.md#RF-02", "_reversa_sdd/walls2d/design.md#Interface", "_reversa_sdd/addenda/bug-BUG-20261117-6KBC-v001.md"]
  affected_code: ["caffmob_draw/walls2d/ops_editor.py", "caffmob_draw/canvas2d/window.py", "caffmob_draw/walls2d/window.py"]
  root_cause:
    state: confirmed
    hypothesis: "O texto não é do add-on: em `wm_window_title_text` (código do Blender) a janela de tela temporária com uma área só recebe `IFACE_(ED_area_name(area))`. Como `canvas2d/window.py:prepare` troca a área para `IMAGE_EDITOR`, o título vira o nome traduzido desse tipo de área, e `bpy.types.Window` em 5.2 não tem `title`: nenhum add-on renomeia a barra do sistema."
    causal_path:
      - "canvas2d/window.py prepare: area.type = 'IMAGE_EDITOR' (necessário para o handler de desenho da planta)"
      - "walls2d/window.py open_editor: screen.area_dupli cria uma tela temporária com uma área só"
      - "wm_window_title_text: janela temporária de área única recebe IFACE_(ED_area_name(area)) = 'Editor de Imagens' em pt_BR"
      - "bpy.types.Window: sem atributo nem método de título (5.2); não há override por add-on"
    evidence:
      - ref: "evidence/reproduction.md"
        observation: "trecho de wm_window_title_text e lista de atributos de bpy.types.Window"
      - ref: "evidence/titulo-editor-de-imagens.webp"
        observation: "captura do titular com a seta sobre 'Editor de Imagens'"
      - ref: "evidence/gate1-red.md"
        observation: "a barra superior não desenhava nome nenhum"
      - ref: "evidence/gate2-green.md"
        observation: "nome desenhado e regressões de janela verdes"
    code_refs:
      - file: "caffmob_draw/walls2d/ops_editor.py"
        symbol: "_draw_toolbar"
        commit: "8caf911e"
      - file: "caffmob_draw/canvas2d/window.py"
        symbol: "prepare"
        commit: "8caf911e"
  reproduction_tests: ["tests/blender_bug_6KBC_titulo.py"]
  regression_tests: ["tests/blender_bug_6KBC_titulo.py", "tests/blender_002_smoke.py", "tests/blender_002_ui_events.py", "tests/blender_007_window_smoke.py"]

spec_verdict: spec-gap

change_set:
  - id: CHG-001
    kind: test
    artifact: "tests/blender_bug_6KBC_titulo.py"
    purpose: "reprodução e regressão: nome na barra, alinhamento e botões preservados"
    diff: "fix/CHG-001.diff"
  - id: CHG-002
    kind: code
    artifact: "caffmob_draw/walls2d/ops_editor.py"
    purpose: "constante TITULO e desenho do nome à direita da barra superior"
    diff: "fix/CHG-002.diff"
  - id: CHG-003
    kind: configuration
    artifact: "caffmob_draw/data/translations/walls2d.json"
    purpose: "nome em pt_BR e en_US"
    diff: "fix/CHG-003.diff"
  - id: CHG-004
    kind: test
    artifact: "tests/blender_002_smoke.py"
    purpose: "stub do modal com _handle_menu (o smoke falhava desde o menu de contexto, #146)"
    diff: "fix/CHG-004.diff"
  - id: CHG-005
    kind: specification
    artifact: "_reversa_sdd/addenda/bug-BUG-20261117-6KBC-v001.md"
    purpose: "adendo aditivo (spec-gap) com a limitação da barra do sistema"
    diff: null

closure:
  policy: local-software
  satisfied: true
resolution_kind: fixed
---
# Janela do editor mostra Editor de Imagens em vez de Editor de Paredes CAFF MOB DRAW

## Summary

A janela do Editor de Paredes aparece com o título do editor de imagens do Blender ("Editor de Imagens"), e não com o
nome do editor. O titular pede "Editor de Paredes CAFF MOB DRAW" (TT 001).

## Expected Behavior

Pedido do titular (2026-11-17): a janela do editor deve se chamar "Editor de Paredes CAFF MOB DRAW".

Spec efetiva: `_reversa_sdd/walls2d/requirements.md` RF-02 descreve abrir o editor sem dizer nada sobre o título, e o
`design.md#Interface` descreve a barra superior e os painéis sem nome de produto. Nenhum requisito cobria o nome
exibido: `spec-gap`, agora especificado pelo adendo
`_reversa_sdd/addenda/bug-BUG-20261117-6KBC-v001.md`.

## Actual Behavior

A barra da janela do editor mostra "Editor de Imagens" (marcado com seta vermelha na captura do titular), e a barra
desenhada pelo add-on não trazia nome nenhum: só a lupa, o botão Mover e as dicas.

O texto da barra do sistema é o nome traduzido do tipo de área `IMAGE_EDITOR`: `canvas2d/window.py:prepare` faz
`area.type = 'IMAGE_EDITOR'` e o Blender monta o título da janela temporária com `IFACE_(ED_area_name(area))`.

## Steps to Reproduce

1. Abrir o Editor de Paredes (Construir > Editor de Paredes).
2. Olhar o topo da janela nova.

Resultado: "Editor de Imagens".

## Evidence

- `evidence/titulo-editor-de-imagens.webp`: captura do titular, com a seta vermelha sobre o título.
- `evidence/reproduction.md`: trecho de `wm_window_title_text` e a ausência de `title` em `bpy.types.Window` (5.2).
- `evidence/gate1-red.md` e `evidence/gate2-green.md`: vermelho e verde do teste.
- `../../intake/sondagem-mcp-20261117.md`: `pgettext_iface("Image Editor")` devolve "Editor de Imagens" em `pt_BR`.
- Relato bruto: `../../intake/relato-20261117-1430.md` (Problema 1).

## Suspected Area

`caffmob_draw/canvas2d/window.py:prepare` (troca do tipo de área) e `caffmob_draw/walls2d/window.py`
(`EDITOR_CATEGORY`, `open_editor`). A mecânica de janela é compartilhada com o Editor de Armário
(`caffmob_draw/cabinet_editor/window.py`), que não foi tocado.

## Acceptance Criteria

- A janela do Editor de Paredes exibe "Editor de Paredes CAFF MOB DRAW" no lugar de "Editor de Imagens".
  **Atendido com ressalva aprovada:** o nome aparece na barra superior do editor, desenhado pelo add-on. A barra do
  sistema operacional continua "Editor de Imagens", porque o Blender define esse texto e não expõe título por janela à
  API Python (ver `evidence/reproduction.md`); o titular aprovou esse alcance em 2026-11-17.
- O editor de armário não é renomeado por essa mudança sem decisão própria. **Atendido:** a mudança fica em
  `walls2d/ops_editor.py`, que o armário não usa.
- Fechar o editor devolve a área 3D ao estado anterior, como hoje. **Atendido:** `tests/blender_007_window_smoke.py`
  passa.

## Resolution

- **Causa raiz:** `confirmed` — o título é montado pelo Blender a partir do tipo de área, e a API 5.2 não permite
  renomear a janela.
- **Estratégia:** correção direta, risco baixo (acrescenta um texto na barra que o add-on já desenha; nada muda em
  janela, área, painéis ou dados).
- **Veredito de spec:** `spec-gap`, aprovado pelo titular no fechamento; adendo aditivo versionado.
- **resolution_kind:** `fixed`.
- **Closure policy:** `local-software` satisfeita — regressão passando + veredito de spec.

### Change set

| CHG | tipo | artefato | propósito |
|---|---|---|---|
| CHG-001 | test | `tests/blender_bug_6KBC_titulo.py` | reprodução e regressão do nome na barra |
| CHG-002 | code | `caffmob_draw/walls2d/ops_editor.py` | `TITULO` e desenho à direita da barra superior |
| CHG-003 | configuration | `caffmob_draw/data/translations/walls2d.json` | nome em `pt_BR` e `en_US` |
| CHG-004 | test | `tests/blender_002_smoke.py` | stub do modal com `_handle_menu` (smoke quebrado desde o #146) |
| CHG-005 | specification | `_reversa_sdd/addenda/bug-BUG-20261117-6KBC-v001.md` | adendo aditivo (`spec-gap`) |

Diffs em `fix/CHG-001.diff` a `fix/CHG-004.diff`.

### Testes

| momento | comando | resultado |
|---|---|---|
| vermelho | `blender --background --factory-startup --python-exit-code 1 --python tests/blender_bug_6KBC_titulo.py` | exit 1: `ops_editor sem TITULO` |
| verde | mesmo comando | `blender_bug_6KBC_titulo: OK` (exit 0) |
| regressão | `blender_002_smoke`, `blender_002_ui_events`, `blender_007_window_smoke` | exit 0 nos três |
| i18n | `tools/i18n_scan.py walls2d --faltando` e `tests/test_i18n_coverage.py` | 0 textos sem tradução; 3 testes OK |

## Agent Notes

- Severidade e prioridade confirmadas pelo titular (low/P3) no fechamento.
- O smoke `blender_002_smoke` já falhava antes desta correção, por falta de `_handle_menu` no stub do modal (método
  criado no #146); o CHG-004 conserta o stub, sem afrouxar asserção.
- Fora do escopo, se o titular quiser: o resíduo do cabeçalho do Image Editor no topo da área ("Sample Size", linha de
  marcadores) que a captura mostra.
