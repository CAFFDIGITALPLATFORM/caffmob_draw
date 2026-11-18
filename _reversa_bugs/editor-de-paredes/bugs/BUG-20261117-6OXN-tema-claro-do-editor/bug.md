---
schema_version: 1
id: BUG-20261117-6OXN
display_number: 147
title: Editor de parede só no tema escuro, sem opção de fundo branco
status: resolved
phase: delivering
severity: low
priority: P3
created: 2026-11-17
updated: 2026-11-18

origin:
  type: manual-report
  external_ref: null

area: paredes
module: walls2d
feature: 002-editor-parede-mover-sobre
labels: [spec-gap, interface, tema]

visibility: normal
security_suspected: false

reproduction:
  classification: deterministic
  rate: "1/1 (leitura do código: COLORS fixo em ops_editor.py:46-58, herdado por classico_v2:127; sem preferência de tema; plano fix/plan.html aguardando aprovação)"
  suspected_triggers: []

blocking: []

relationships:
  - bug: BUG-20261117-JXDJ
    type: related-to
    state: proposed
    evidence: []

traceability:
  specs: ["_reversa_sdd/walls2d/requirements.md#RF-13"]
  affected_code: ["caffmob_draw/walls2d/ops_editor.py", "caffmob_draw/walls2d/classico_v2.py", "caffmob_draw/walls2d/props.py"]
  root_cause:
    state: confirmed
    hypothesis: "A paleta é uma constante de módulo (`ops_editor.COLORS`) e o fundo é um valor fixo dela; `classico_v2.desenhar` herda a mesma constante. Não existe propriedade de tema, leitura de preferência nem ponto de escolha, então o editor nasce sempre escuro."
    causal_path:
      - "ops_editor.py:46-58 define COLORS com background (0.12, 0.12, 0.13, 1) e todas as cores da planta"
      - "ops_editor.draw_plan pinta a região com COLORS['background'] e usa draw.COLORS para os textos"
      - "classico_v2.desenhar:127 faz C = ed.COLORS, então a cena v2 repete a paleta fixa"
      - "props.py e a sessão não guardam tema, e não há arquivo de preferência do editor"
    evidence:
      - ref: "fix/plan.html"
        observation: "plano com as duas paletas, contraste, persistência e change set"
      - ref: "caffmob_draw/walls2d/cores.py"
        observation: "cores por tipo também fixas, com cinza claro ilegível sobre fundo branco"
    code_refs:
      - file: "caffmob_draw/walls2d/ops_editor.py"
        symbol: "COLORS"
        commit: "8caf911e"
      - file: "caffmob_draw/walls2d/classico_v2.py"
        symbol: "desenhar"
        commit: "8caf911e"
  reproduction_tests: ["tests/test_walls2d_tema.py", "tests/blender_bug_6OXN_tema.py"]
  regression_tests: ["tests/test_walls2d_tema.py", "tests/blender_bug_6OXN_tema.py", "tests/blender_002_smoke.py", "tests/blender_065_walls2d_v2.py", "tests/blender_bug_AKYJ_menu.py", "tests/blender_bug_RP9Q_paineis.py", "tests/test_walls2d_menu_contexto.py", "tests/test_i18n_coverage.py"]

spec_verdict: spec-gap

change_set:
  - id: CHG-001
    kind: test
    artifact: "tests/test_walls2d_tema.py"
    purpose: "paletas completas, contraste WCAG nos dois temas, variantes por tipo e ida e volta da preferência"
    diff: "fix/CHG-001.diff"
  - id: CHG-002
    kind: test
    artifact: "tests/blender_bug_6OXN_tema.py"
    purpose: "reprodução (sem tema) e regressões: preferência lida ao abrir, toggle no Grid, paleta no desenho"
    diff: "fix/CHG-002.diff"
  - id: CHG-003
    kind: code
    artifact: "caffmob_draw/walls2d/tema.py"
    purpose: "arquivo novo: ESCURO e CLARO, paleta(), arquivo(), ler() e salvar()"
    diff: "fix/CHG-003.diff"
  - id: CHG-004
    kind: code
    artifact: "caffmob_draw/walls2d/cores.py"
    purpose: "variantes escuras por tipo de parede para o fundo branco (cor(tipo, claro=False))"
    diff: "fix/CHG-004.diff"
  - id: CHG-005
    kind: code
    artifact: "caffmob_draw/walls2d/props.py"
    purpose: "enum tema no estado, gravação da preferência no update e aplicar_preferencia() no start"
    diff: "fix/CHG-005.diff"
  - id: CHG-006
    kind: code
    artifact: "caffmob_draw/walls2d/ops_editor.py"
    purpose: "COLORS passa a ler a paleta do tema (ponto único) e os textos da planta usam a paleta"
    diff: "fix/CHG-006.diff"
  - id: CHG-007
    kind: code
    artifact: "caffmob_draw/walls2d/classico_v2.py"
    purpose: "cena v2 segue a mesma paleta e as cores de tipo do tema"
    diff: "fix/CHG-007.diff"
  - id: CHG-008
    kind: code
    artifact: "caffmob_draw/walls2d/panels.py, caffmob_draw/walls2d/painel_ui.py"
    purpose: "caixa Aparência com o toggle, desenhada igual nas duas telas"
    diff: "fix/CHG-008.diff"
  - id: CHG-009
    kind: configuration
    artifact: "caffmob_draw/data/translations/walls2d.json"
    purpose: "sete textos novos em pt_BR e en_US"
    diff: "fix/CHG-009.diff"
  - id: CHG-010
    kind: specification
    artifact: "_reversa_sdd/addenda/bug-BUG-20261117-6OXN-v001.md"
    purpose: "adendo aditivo (spec-gap) do tema, da persistência e do escopo do cromo"

closure:
  policy: local-software
  satisfied: true
resolution_kind: fixed
---
# Editor de parede só no tema escuro, sem opção de fundo branco

## Summary

O titular pede a opção de trocar a cor do editor, que hoje é sempre escuro, para branco.

## Expected Behavior

Pedido do titular (2026-11-17): opção de escolher a cor do editor, que hoje prevalece preto, incluindo branco.

Spec efetiva: `_reversa_sdd/walls2d/requirements.md` RF-13 descreve o desenho da planta e os painéis (Ferramentas,
Painel, Grid, Confirmar) e não trata de tema ou cor de fundo: `spec-gap` provável.

## Actual Behavior

O fundo é um valor fixo da paleta: `draw_plan` pinta a região inteira com `COLORS['background']`
(`caffmob_draw/walls2d/ops_editor.py`) e o caminho v2 faz o mesmo em `classico_v2.desenhar`. Não existe preferência,
toggle na sessão nem no painel Grid para trocar o tema.

As cores das linhas (parede, seleção, grade, referência) também são fixas na paleta: um fundo branco sem revisar o
contraste deixaria rótulos e linhas claras ilegíveis.

## Steps to Reproduce

1. Abrir o Editor de Paredes.
2. Procurar em qualquer painel do editor uma opção de cor de fundo ou tema claro.

Resultado: não existe.

## Evidence

- `../../intake/editor-de-paredes-titulo-e-ferramentas-20261117.webp`: fundo escuro no editor, sem controle de cor.
- Relato bruto: `../../intake/relato-20261117-1430.md` (Problema 4).
- `../../intake/sondagem-mcp-20261117.md`: a sessão `btm_wall_editor` do addon instalado não tem nenhuma propriedade
  com `theme`, `background` ou `color`.

## Suspected Area

`caffmob_draw/walls2d/ops_editor.py` (`COLORS`, `draw_plan`), `classico_v2.py` (desenho da cena v2), `props.py`
(onde caberia a preferência da sessão).

## Acceptance Criteria

- Uma opção no editor alterna entre tema escuro e tema claro (fundo branco).
- Com o tema claro, linhas, rótulos de medida, grade, seleção e mensagens continuam legíveis (contraste conferido nos
  dois temas).
- A escolha sobrevive ao fechar e reabrir o editor, sem gravar dados da cena.

## Traceability

- Specs: `_reversa_sdd/walls2d/requirements.md#RF-13`
- Código suspeito: `caffmob_draw/walls2d/ops_editor.py`, `caffmob_draw/walls2d/classico_v2.py`,
  `caffmob_draw/walls2d/props.py`
- Testes existentes relacionados: `tests/blender_002_ui_events.py`

## Resolution

A preencher pelo `/reversa-debugger-fix`.

**Causa raiz (final):** `confirmed`. A paleta era a constante `ops_editor.COLORS` (fundo `0.12, 0.12, 0.13`) e
`classico_v2.desenhar` fazia `C = ed.COLORS`, então as duas telas herdavam o mesmo valor fixo. Não havia propriedade de
tema, leitura de preferência nem ponto de escolha, e as cores por tipo de parede eram claras demais para um fundo
branco.

**Estratégia:** correção direta aprovada pelo titular em 2026-11-18, em `fix/plan.html`: duas paletas completas num
módulo novo, escolhidas por uma propriedade do estado do editor e guardadas como preferência do usuário. A decisão de
escopo foi só a planta; barra superior e painéis nativos seguem o tema do Blender, e o seletor fica no painel Grid.

**Veredito de spec:** `spec-gap` (RF-13 descreve o desenho da planta e os painéis, mas não tema nem cor de fundo).
Recomendado com as evidências abaixo; decisão do titular registrada na conversa de 2026-11-18.

**resolution_kind:** `fixed`.

### Change set

| CHG | Tipo | Artefato | Propósito | Diff |
|---|---|---|---|---|
| CHG-001 | test | `tests/test_walls2d_tema.py` | paletas, contraste e preferência | `fix/CHG-001.diff` |
| CHG-002 | test | `tests/blender_bug_6OXN_tema.py` | reprodução e regressões no Blender | `fix/CHG-002.diff` |
| CHG-003 | code | `caffmob_draw/walls2d/tema.py` (novo) | duas paletas e a preferência | `fix/CHG-003.diff` |
| CHG-004 | code | `caffmob_draw/walls2d/cores.py` | variantes escuras por tipo | `fix/CHG-004.diff` |
| CHG-005 | code | `caffmob_draw/walls2d/props.py` | enum do tema e leitura ao abrir | `fix/CHG-005.diff` |
| CHG-006 | code | `caffmob_draw/walls2d/ops_editor.py` | ponto único da paleta no desenho | `fix/CHG-006.diff` |
| CHG-007 | code | `caffmob_draw/walls2d/classico_v2.py` | cena v2 com a mesma paleta | `fix/CHG-007.diff` |
| CHG-008 | code | `caffmob_draw/walls2d/panels.py`, `painel_ui.py` | caixa Aparência nas duas telas | `fix/CHG-008.diff` |
| CHG-009 | configuration | `caffmob_draw/data/translations/walls2d.json` | sete textos novos | `fix/CHG-009.diff` |
| CHG-010 | specification | `_reversa_sdd/addenda/bug-BUG-20261117-6OXN-v001.md` | adendo aditivo (`spec-gap`) |  |

### Prova vermelho → verde

- Vermelho (antes do CHG-003), exit 1: `tests/test_walls2d_tema.py` parou em
  `ImportError: cannot import name 'tema'` e `tests/blender_bug_6OXN_tema.py` no mesmo import: o editor não tinha módulo
  de tema nem propriedade no estado (`evidence/gate1-red.md`).
- Verde (depois), exit 0: `13 testes OK` no puro e `OK BUG-20261117-6OXN` no Blender, incluindo
  `OK preferência: grava, reabre e aplica o tema salvo` (`evidence/gate2-green.md`).
- Regressões, todas exit 0: `blender_002_smoke`, `blender_065_walls2d_v2`, `blender_bug_AKYJ_menu`,
  `blender_bug_RP9Q_paineis`, `test_i18n_coverage` e `i18n_scan walls2d --faltando` (0 sem tradução).
- `py -3 docs/rag/tools/check_api.py`: sem referência desconhecida na API 5.2.

### Riscos e limites

- Risco da mudança: média (desenho das duas telas e preferência em arquivo), sem dado de cena e reversível voltando
  ao escuro.
- O desenho não foi conferido em pixels: em `--background` não há GPU; o teste prova a paleta escolhida, o contraste
  por luminância e o painel. A conferência visual dos dois temas fica com o titular.
- `ruff` não está instalado no interpretador do ambiente (`No module named ruff`); o config ignora `E501` e várias
  linhas acima de 120 já existiam no projeto.
- Os diffs CHG-005 a CHG-009 são contra o commit `8caf911e` e carregam também as mudanças não commitadas de #151 e
  #152 nos mesmos arquivos.

## Agent Notes

- Severidade e prioridade propostas pelo agente nesta triagem (low/P3), a confirmar pelo titular.
- Não basta trocar o fundo: a paleta inteira precisa de dois conjuntos coerentes, senão o tema claro nasce ilegível.
  O ponto de mudança tem de ser único, compartilhado por `ops_editor` e `classico_v2`.
- Guardar a preferência pelo caminho de preferências já usado pelo add-on (`bpy.utils.extension_path_user` para
  arquivos do usuário), e não em propriedades da cena.
