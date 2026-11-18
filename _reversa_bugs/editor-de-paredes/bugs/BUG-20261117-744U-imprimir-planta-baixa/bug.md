---
schema_version: 1
id: BUG-20261117-744U
display_number: 149
title: Sem botão de imprimir a planta baixa
status: resolved
phase: delivered
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
labels: [spec-gap, impressao, exportacao, pdf-vetorial]

visibility: normal
security_suspected: false

reproduction:
  classification: deterministic
  rate: "2/2 (o operador de impressão não existia: leitura do código, sondagem MCP e teste de reprodução vermelho)"
  suspected_triggers: []

blocking: []

relationships:
  - bug: BUG-20261117-JXDJ
    type: blocked-by
    state: confirmed
    evidence:
      - {ref: ../../BUG-20261117-JXDJ-planta-baixa-com-corte-e-cores/DONE.md, observation: "JXDJ entregou a planta com corte e cor em 2026-11-17; a impressão usa plant_objects e a geometria que ele definiu"}

traceability:
  specs: ["_reversa_sdd/walls2d/requirements.md#RF-13", "_reversa_sdd/addenda/bug-BUG-20261117-744U-v001.md"]
  affected_code: ["caffmob_draw/walls2d/impressao.py", "caffmob_draw/walls2d/ops_editor.py", "caffmob_draw/walls2d/panels.py", "caffmob_draw/walls2d/classico_v2.py"]
  root_cause:
    state: confirmed
    hypothesis: "Funcionalidade inexistente: o editor desenha a planta em GPU sobre a tela e nenhum caminho levava essa geometria a um arquivo de impressão. O único PDF do addon (caffmob_layouts.export_all_to_pdf) renderiza câmeras de layout view, não a planta do editor."
    evidence:
      - "ops_editor.py, panels.py e classico_v2.py não têm operador, botão nem atalho de impressão da planta"
      - "operators/layouts.py:804 export_all_to_pdf depende de câmera, cena de layout, compositor e Pillow"
      - "intake/sondagem-mcp-20261117.md: nenhum operador caffmob.* imprime ou exporta a planta do editor"
      - "tests/test_impressao.py#ReproducaoTest/test_operador_de_impressao_existe falhou antes do change set"
  reproduction_tests: ["tests/test_impressao.py#ReproducaoTest", "tests/blender_bug_744U_imprimir.py#REPRODUÇÃO: sem planta o operador recusa"]
  regression_tests: ["tests/test_impressao.py#RegressaoTest", "tests/test_impressao.py#V2Test", "tests/blender_bug_744U_imprimir.py#REGRESSÃO: PDF de uma página com paredes e medidas"]

spec_verdict: spec-gap

change_set:
  - {id: CHG-001, kind: code, artifact: "caffmob_draw/walls2d/impressao.py", purpose: "Gerador de PDF A4 vetorial: coleta os traços do rascunho clássico e da prancheta v2, aberturas, medidas e objetos da planta baixa, com penas e tintas do padrão CTB e escala padrão que cabe na folha"}
  - {id: CHG-002, kind: code, artifact: "caffmob_draw/walls2d/ops_editor.py", purpose: "Operador caffmob.wall_editor_print (seletor de arquivo, enquadramento da vista, sem escrita no rascunho) e o retângulo da vista em metros"}
  - {id: CHG-003, kind: code, artifact: "caffmob_draw/walls2d/panels.py", purpose: "Botão Imprimir no painel Confirmar do editor clássico"}
  - {id: CHG-004, kind: code, artifact: "caffmob_draw/walls2d/classico_v2.py", purpose: "O mesmo botão no painel Confirmar da cena v2"}
  - {id: CHG-005, kind: code, artifact: "caffmob_draw/data/translations/walls2d.json", purpose: "Dez textos de interface novos com pt_BR e en_US"}
  - {id: CHG-006, kind: specification, artifact: "_reversa_sdd/addenda/bug-BUG-20261117-744U-v001.md", purpose: "Adendo aditivo que especifica a impressão da planta baixa pela primeira vez"}
  - {id: CHG-007, kind: code, artifact: "tests/test_impressao.py, tests/blender_bug_744U_imprimir.py", purpose: "Testes de reprodução e de regressão do gerador e do operador"}

closure:
  policy: local-software
  satisfied: true
resolution_kind: fixed
---
# Sem botão de imprimir a planta baixa

## Summary

O titular pede um botão para imprimir a planta baixa. O editor de paredes não tinha nenhum botão de impressão ou
exportação da vista: o painel Confirmar só tinha OK e Cancelar.

## Expected Behavior

Pedido do titular (2026-11-17): botão de imprimir a planta baixa a partir do editor.

Spec efetiva: `_reversa_sdd/walls2d/requirements.md` RF-13 cobre o desenho da planta e os painéis laterais
(Ferramentas, Painel, Grid, Confirmar) e não menciona impressão nem exportação. O veredito é `spec-gap`; o comportamento
passa a ser especificado pelo adendo
[`_reversa_sdd/addenda/bug-BUG-20261117-744U-v001.md`](../../../../_reversa_sdd/addenda/bug-BUG-20261117-744U-v001.md).

## Actual Behavior

Antes do change set: nenhum botão, operador nem atalho de impressão no editor. O que existia, fora dele,
`caffmob_layouts.export_all_to_pdf` (`caffmob_draw/operators/layouts.py:804`, botão em
`caffmob_draw/ui/view3d_sidebar.py:923`), renderiza as *layout views* com câmera, compositor e Pillow; não conhece a
planta desenhada no Image Editor.

## Steps to Reproduce

1. Abrir o Editor de Paredes.
2. Procurar no painel, na barra superior e no menu de contexto qualquer ação de imprimir ou exportar a planta.

Resultado (antes): não existe. O teste de reprodução (`tests/test_impressao.py#ReproducaoTest`) falhava com
"BUG-20261117-744U: nenhum operador imprime a planta do editor".

## Evidence

- Relato bruto: `../../intake/relato-20261117-1430.md` (Problema 6).
- `../../intake/relato-20261117-1520.md` e `../../intake/manual-ctb-cores-espessuras-20261117.webp`: penas do padrão CTB
  (paredes 0,35 a 0,50 mm; estrutura 0,60 a 0,70 mm; muretas 0,15 a 0,20 mm; acima do corte 0,10 a 0,15 mm).
- `../../intake/sondagem-mcp-20261117.md`: nenhum operador `caffmob.*` de imprimir ou exportar a planta.
- Plano e diffs: `fix/plan.html`, `fix/CHG-001.diff` a `fix/CHG-007b-testes-blender.diff`.
- Cena real do titular no Blender 5.2 (2.272 objetos, 1.625 na planta): PDF de 2.295.479 bytes, geração em 0,24 s,
  escala 1:75 (a leitura da cena por `plant_objects` levou 13,2 s).

## Suspected Area

Funcionalidade inexistente. Dependia da planta baixa do BUG-20261117-JXDJ, que foi entregue e é usada pela impressão.

## Acceptance Criteria

- [x] O editor tem uma ação de imprimir a planta baixa (botão Imprimir no painel Confirmar, clássico e v2).
- [x] O conteúdo é o que a tela mostra: paredes com face interna tracejada, aberturas, medidas e objetos da planta baixa.
- [x] A saída respeita a unidade do projeto (medidas nos trechos) e o enquadramento atual da vista.
- [x] Cancelar o seletor não altera o rascunho nem a cena; imprimir não grava passo de desfazer.

## Traceability

- Specs: `_reversa_sdd/walls2d/requirements.md#RF-13`; adendo `_reversa_sdd/addenda/bug-BUG-20261117-744U-v001.md`.
- Código: `caffmob_draw/walls2d/impressao.py`, `ops_editor.py` (`BTM_OT_WallEditorPrint`, `vista_em_metros`),
  `panels.py`, `classico_v2.py`, `data/translations/walls2d.json`.
- Testes: `tests/test_impressao.py`, `tests/blender_bug_744U_imprimir.py`.

## Resolution

**Causa raiz:** funcionalidade inexistente. A planta é desenhada direto na GPU (`draw_plan` / `classico_v2.desenhar`) e
nenhum caminho levava essa geometria a um arquivo de impressão; o PDF do addon só cobre cenas de layout com câmera.
Estado epistemológico: `confirmed`.

**Veredito de spec:** `spec-gap`, com adendo aditivo
`_reversa_sdd/addenda/bug-BUG-20261117-744U-v001.md`. A spec original não foi editada.

**Resolution kind:** `fixed`. **Closure policy:** `local-software`, satisfeita (regressão passando + veredito).

| CHG | tipo | artefato | propósito |
|---|---|---|---|
| CHG-001 | code | `caffmob_draw/walls2d/impressao.py` (novo) | PDF A4 vetorial: traços do rascunho clássico e da prancheta v2, aberturas, medidas, objetos, penas CTB e escala padrão que cabe |
| CHG-002 | code | `caffmob_draw/walls2d/ops_editor.py` | Operador `caffmob.wall_editor_print` e `vista_em_metros` |
| CHG-003 | code | `caffmob_draw/walls2d/panels.py` | Botão Imprimir no Confirmar (clássico) |
| CHG-004 | code | `caffmob_draw/walls2d/classico_v2.py` | Botão Imprimir no Confirmar (cena v2) |
| CHG-005 | code | `caffmob_draw/data/translations/walls2d.json` | Traduções dos dez textos novos |
| CHG-006 | specification | `_reversa_sdd/addenda/bug-BUG-20261117-744U-v001.md` | Adendo aditivo (`spec-gap`) |
| CHG-007 | code | `tests/test_impressao.py`, `tests/blender_bug_744U_imprimir.py` | Reprodução e regressão |

Diffs: `fix/CHG-001.diff`, `fix/CHG-002.diff`, `fix/CHG-003.diff`, `fix/CHG-004.diff`, `fix/CHG-005.diff`,
`fix/CHG-007a-testes.diff`, `fix/CHG-007b-testes-blender.diff`.

**Prova vermelho → verde:**

- Vermelho: `test_operador_de_impressao_existe` falhou antes do operador
  (`AssertionError: 'caffmob.wall_editor_print' not found ...`) e `test_modulo_de_impressao_existe` falhava com o
  módulo ausente.
- O teste v2 também pegou um defeito real do próprio change set: `coletar_v2` tratava a geometria em mm como metros
  (caixa de 4.300 m, escala 0). Corrigido com `_em_metros` e coberto por
  `V2Test#test_planta_v2_gera_pdf_com_medidas`.
- Verde: `py -3 -m unittest test_impressao test_i18n_coverage` → `Ran 16 tests ... OK`;
  `py -3 docs/rag/tools/check_api.py` → `OK: no unknown API references found`;
  `blender --background --factory-startup --python-exit-code 1 --python tests/blender_bug_744U_imprimir.py` → 7
  checagens OK, `EXIT=0`.

## Agent Notes

- Severidade e prioridade da triagem (low/P3) mantidas: é funcionalidade que faltava, sem perda de dados.
- O bloqueio `blocked-by` do BUG-20261117-JXDJ caiu: aquele bug foi entregue e a impressão consome
  `scene_io.plant_objects` e a geometria que ele definiu.
- Fica fora da correção: diálogo de impressão do sistema, carimbo, moldura de prancha, várias folhas, escolha de
  escala/folha pelo usuário, hachura por padrão de material e curvas/texto na planta (adendo do PLNT).
- Observação de desempenho medida na cena real: gerar o PDF leva 0,24 s, mas `plant_objects` leva 13,2 s porque varre
  2.272 objetos. A impressão paga esse custo uma vez por clique; o desenho na tela já o paga hoje (entregado no JXDJ),
  não é regressão deste change set.
- `ruff` não está instalado nesta máquina: a checagem foi `py_compile` nos arquivos tocados, `check_api.py` e o teste de
  cobertura de tradução (0 textos sem tradução).
- Nada foi commitado: o conjunto segue no working tree.
