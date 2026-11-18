---
schema_version: 1
id: BUG-20261117-RP9Q
display_number: 152
title: Menu lateral de paredes com estilo antigo; quer botão de toggle moderno
status: resolved
phase: delivering
severity: medium
priority: P2
created: 2026-11-17
updated: 2026-11-18

origin:
  type: manual-report
  external_ref: null

area: paredes
module: walls2d
feature: 002-editor-parede-mover-sobre
labels: [ui-design, menu-lateral, toggle, estilo-antigo, ux]

visibility: normal
security_suspected: false

reproduction:
  classification: deterministic
  rate: "1/1 (abertura do editor e leitura de panels.py/classico_v2.py: painel ligado direto no enum com expand=True; plano fix/plan.html aguardando aprovação)"
  suspected_triggers: []

blocking: []

relationships: []

traceability:
  specs: ["_reversa_sdd/walls2d/requirements.md#RF-13", "_reversa_sdd/walls2d/design.md#Interface"]
  affected_code: ["caffmob_draw/walls2d/panels.py", "caffmob_draw/walls2d/classico_v2.py"]
  root_cause:
    state: confirmed
    hypothesis: "Os dois painéis ligam o enum `tool` direto na UI (`prop(..., expand=True)`), sem camada de apresentação: o Blender desenha 7 linhas de largura total, sem grade, sem ícone como botão e sem estado pressionado. Os booleanos usam a caixa de marcar padrão."
    causal_path:
      - "panels.py:48-49 e classico_v2.py:722-723: layout.prop(state, 'tool', expand=True), desenho duplicado nas duas telas"
      - "props.py:389: o enum tool já declara ícone por ferramenta, mas a UI não usa os itens como botões"
      - "magnetic, lock_angle, equalize_height e remove_modules saem como checkbox, sem estado visual de toggle"
    evidence:
      - ref: "fix/plan.html"
        observation: "plano com o desenho proposto, change set e riscos"
      - ref: "caffmob_draw/walls2d/classico_v2.py:708"
        observation: "o editor v2 já usa botão com depress (_acao), então o padrão existe no addon"
    code_refs:
      - file: "caffmob_draw/walls2d/panels.py"
        symbol: "BTM_PT_WallEditorTools.draw"
        commit: "8caf911e"
      - file: "caffmob_draw/walls2d/classico_v2.py"
        symbol: "painel_ferramentas"
        commit: "8caf911e"
  reproduction_tests: ["tests/blender_bug_RP9Q_paineis.py#REPRODUÇÃO: botão por ferramenta com ícone e ativo pressionado"]
  regression_tests: ["tests/blender_bug_RP9Q_paineis.py", "tests/blender_002_smoke.py", "tests/blender_065_walls2d_v2.py"]

spec_verdict: spec-gap

change_set:
  - id: CHG-001
    kind: test
    artifact: "tests/blender_bug_RP9Q_paineis.py"
    purpose: "reprodução (nenhum botão de ferramenta) e regressões de operador, paridade v2, toggles e painéis"
    diff: "fix/CHG-001.diff"
  - id: CHG-002
    kind: code
    artifact: "caffmob_draw/walls2d/painel_ui.py"
    purpose: "arquivo novo: grade de 2 colunas com ícone, rótulo curto e depress no ativo"
    diff: "fix/CHG-002.diff"
  - id: CHG-003
    kind: code
    artifact: "caffmob_draw/walls2d/ops_editor.py"
    purpose: "operador caffmob.wall_editor_tool, que grava state.tool e redesenha"
    diff: "fix/CHG-003.diff"
  - id: CHG-004
    kind: code
    artifact: "caffmob_draw/walls2d/panels.py"
    purpose: "painel Ferramentas com a grade; booleanos com toggle e ícone; Grid em caixas"
    diff: "fix/CHG-004.diff"
  - id: CHG-005
    kind: code
    artifact: "caffmob_draw/walls2d/classico_v2.py"
    purpose: "mesma grade e caixas na cena v2 (fim da duplicação do desenho)"
    diff: "fix/CHG-005.diff"
  - id: CHG-006
    kind: specification
    artifact: "_reversa_sdd/addenda/bug-BUG-20261117-RP9Q-v001.md"
    purpose: "adendo aditivo (spec-gap) da apresentação das ferramentas e do operador"

closure:
  policy: local-software
  satisfied: true
resolution_kind: fixed
---
# Menu lateral de paredes com estilo antigo; quer botão de toggle moderno

## Summary

O titular considera que o menu lateral do Editor de Paredes tem um "estilo antigo" e pede um visual moderno com botões de toggle de verdade (ao invés de controles padrão `layout.prop` do Blender). Além disso, relata que ao tocar em "Mover" e selecionar uma parede ocorre um erro (imagem em anexo no relato).

## Expected Behavior

- Menu lateral com visual moderno: botões de toggle com feedback visual (ativo/inativo), ícones claros, layout organizado
- Ferramenta Mover funciona sem erro ao selecionar uma parede

## Actual Behavior

- Painel lateral usa controles padrão do Blender (`layout.prop`) com aparência antiga
- Erro ao usar Mover + selecionar parede: `AttributeError: 'WallPlan' object has no attribute 'move_segments'` (já corrigido no BUG-20261117-JXDJ)

## Steps to Reproduce

1. Abrir o Editor de Paredes
2. Observar o menu lateral (Ferramentas, Painel, Grid, Confirmar)
3. Tocar em "Mover" e selecionar uma parede → erro (já corrigido)

## Evidence

- Relatório do usuário com imagem em anexo (Relatório: Erro)
- Código: `caffmob_draw/walls2d/panels.py` e `caffmob_draw/walls2d/classico_v2.py` usam `layout.prop` em todo o painel

## Suspected Area

`caffmob_draw/walls2d/panels.py` (painéis do editor do addon) e `caffmob_draw/walls2d/classico_v2.py` (painéis da cena v2) — ambos desenham a UI com controles padrão do Blender sem estilo moderno de toggle.

## Acceptance Criteria

- Menu lateral com botões de toggle modernos (feedback visual ativo/inativo)
- Ícones e labels claros para cada ferramenta
- Layout organizado e consistente com o restante da UI do addon
- Nenhuma regressão na funcionalidade existente

## Traceability

- Specs: `_reversa_sdd/walls2d/requirements.md#RF-13` (desenho da planta e painéis laterais), `_reversa_sdd/walls2d/design.md#Interface`
- Código suspeito: `caffmob_draw/walls2d/panels.py`, `caffmob_draw/walls2d/classico_v2.py`

## Resolution

**Causa raiz (final):** `confirmed`. Os dois painéis ligavam o enum `tool` direto na UI
(`prop(state, "tool", expand=True)` em `panels.py:48-49` e `classico_v2.py:722-723`), sem camada de apresentação: 7
linhas de largura total, sem grade, sem botão com estado, e booleanos como caixa de marcar.

**Estratégia:** correção direta com o desenho aprovado pelo titular (grade de 2 colunas). Plano em `fix/plan.html`.

**Veredito de spec:** `spec-gap` (RF-13 e a seção Interface descrevem o conteúdo dos painéis, não a apresentação).
Adendo aditivo: `_reversa_sdd/addenda/bug-BUG-20261117-RP9Q-v001.md`.

**resolution_kind:** `fixed`.

### Change set

| CHG | Tipo | Artefato | Propósito | Diff |
|---|---|---|---|---|
| CHG-001 | test | `tests/blender_bug_RP9Q_paineis.py` | reprodução e regressões | `fix/CHG-001.diff` |
| CHG-002 | code | `caffmob_draw/walls2d/painel_ui.py` (novo) | grade de ferramentas com ícone e `depress` | `fix/CHG-002.diff` |
| CHG-003 | code | `caffmob_draw/walls2d/ops_editor.py` | operador `caffmob.wall_editor_tool` | `fix/CHG-003.diff` |
| CHG-004 | code | `caffmob_draw/walls2d/panels.py` | painel Ferramentas, toggles e caixas | `fix/CHG-004.diff` |
| CHG-005 | code | `caffmob_draw/walls2d/classico_v2.py` | mesma grade e caixas na cena v2 | `fix/CHG-005.diff` |
| CHG-006 | specification | `_reversa_sdd/addenda/bug-BUG-20261117-RP9Q-v001.md` | adendo aditivo (`spec-gap`) |  |

### Prova vermelho → verde

- Vermelho (antes do CHG-002..005), exit 1:
  `AssertionError: REPRODUÇÃO (#152): painel sem botões de ferramenta (0)` (`evidence/gate1-red.md`).
- Verde (depois), exit 0: `blender_bug_RP9Q_paineis: OK` (`evidence/gate2-green.md`).
- Regressões: `blender_002_smoke` e `blender_065_walls2d_v2`, exit 0; `test_i18n_coverage` OK;
  `check_api.py` sem referência desconhecida (578 arquivos).

### Riscos e limites

- Risco da mudança: baixa (só apresentação; enum, propriedades e modal intactos; sem dado salvo; sem texto novo).
- O teste valida as chamadas de layout, não o desenho na tela: a conferência visual do painel no Blender com interface
  fica pendente e depende do titular.
- Fora de escopo: campos de medida do painel Painel, listas de Portas e Janelas, ícones novos e qualquer mudança no
  conjunto de ferramentas.

## Agent Notes

- O erro de `move_segments` (WallPlan) já foi corrigido no BUG-20261117-JXDJ; este bug foca no design visual do menu lateral
- É um pedido de UX/design, não um defeito de comportamento: provavelmente `spec-gap` para especificar o estilo moderno
- Consultar `docs/rag/` para diretrizes de UI do addon, se existirem