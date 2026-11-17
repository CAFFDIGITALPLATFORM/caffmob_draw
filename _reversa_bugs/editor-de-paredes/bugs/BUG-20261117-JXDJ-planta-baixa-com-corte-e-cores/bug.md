---
schema_version: 1
id: BUG-20261117-JXDJ
display_number: 148
title: Sem planta baixa dos objetos da cena com corte superior e cores
status: resolved
phase: delivered
severity: medium
priority: P2
created: 2026-11-17
updated: 2026-11-17

origin:
  type: manual-report
  external_ref: null

area: paredes
module: walls2d
feature: 002-editor-parede-mover-sobre
labels: [spec-gap, planta-baixa, corte, materiais]

visibility: normal
security_suspected: false

reproduction:
  classification: deterministic
  rate: "1/1 (leitura do código e sondagem MCP no Blender 5.2 instalado: nenhum operador de planta no namespace do editor)"
  suspected_triggers: []

blocking: []

relationships: []

traceability:
  specs: ["_reversa_sdd/walls2d/requirements.md#RF-13", "docs/usuario/editor-paredes-e-mover-sobre.md#1. Editor de Paredes (planta 2D)"]
  affected_code: ["caffmob_draw/walls2d/ops_editor.py", "caffmob_draw/walls2d/classico_v2.py", "caffmob_draw/walls2d/scene_io.py", "caffmob_draw/operators/layouts.py", "caffmob_draw/ui/view3d_sidebar.py"]
  root_cause:
    state: supported
    hypothesis: "draw_plan desenha apenas paredes do rascunho e referências tracejadas; não lê objetos da cena, não tem plano de corte, não pinta por material."
    causal_path:
      - "ops_editor.py `draw_plan`: itera apenas s.plan.chains (paredes do rascunho) e s.plan.references (parede da camada nova, tracejado); não acessa scene.objects nem materiais"
      - "ops_editor.py `draw_plan`: pinta todo trecho com COLORS['wall'] (cor única), sem olhar wall_type ou material do objeto"
      - "classico_v2.py `desenhar`: delega para ops_editor.draw_plan quando não é v2; não adiciona objetos da cena"
      - "scene_io.py `reference_segments`: só lê arestas de malha de paredes da camada nova no piso, sem objetos nem corte"
      - "layouts.py `generate_2d_plan` / `create_plan_view`: geram planta fora do editor, não integrada ao modal"
    evidence:
      - ref: evidence/reproduction.md
        observation: "draw_plan desenha fundo, grade, paredes do rascunho e referências; sem objetos, corte ou cor por material"
    code_refs:
      - {file: caffmob_draw/walls2d/ops_editor.py, symbol: draw_plan}
      - {file: caffmob_draw/walls2d/classico_v2.py, symbol: desenhar}
      - {file: caffmob_draw/walls2d/scene_io.py, symbol: reference_segments}
      - {file: caffmob_draw/operators/layouts.py, symbol: generate_2d_plan}
  reproduction_tests: ["tests/blender_bug_JXDJ_plant_baixa.py#REPRODUÇÃO: plant_low toggle existe"]
  regression_tests: ["tests/blender_bug_JXDJ_plant_baixa.py#REGRESSÃO: {walls_drawn} parede(s) no rascunho", "tests/blender_bug_JXDJ_plant_baixa.py#REGRESSÃO: plant_low desligado mantém comportamento atual", "tests/blender_bug_JXDJ_plant_baixa.py#REGRESSÃO: plant_low ligado com cut_height definido"]

spec_verdict: spec-gap

change_set:
  - chg: CHG-001
    kind: specification
    artifact: "_reversa_sdd/addenda/bug-BUG-20261117-JXDJ-v001.md"
    purpose: "Adendo de spec aditivo (spec-gap): especifica planta baixa com corte superior e cores por material no Editor de Paredes (RF-13 estendido)"
  - chg: CHG-002
    kind: code
    artifact: "caffmob_draw/walls2d/ops_editor.py"
    purpose: "draw_plan desenha objetos da cena com corte superior e cores por material quando state.plant_low está ligado"
  - chg: CHG-003
    kind: code
    artifact: "caffmob_draw/walls2d/classico_v2.py"
    purpose: "desenhar propaga plant_low ao caminho v2 para as duas telas não divergirem"
  - chg: CHG-004
    kind: code
    artifact: "caffmob_draw/canvas2d/draw.py"
    purpose: "Nova função draw.polygon (triangulação) para preenchimento de objetos na planta"
  - chg: CHG-005
    kind: code
    artifact: "caffmob_draw/walls2d/scene_io.py"
    purpose: "plant_objects(scene, cut_height) lê objetos da cena com materiais para a vista de planta"
  - chg: CHG-006
    kind: code
    artifact: "caffmob_draw/walls2d/props.py"
    purpose: "Propriedades plant_low, cut_height, material_color_mode em BTM_PG_WallEditorState"
  - chg: CHG-007
    kind: code
    artifact: "tests/blender_bug_JXDJ_plant_baixa.py"
    purpose: "Teste de reprodução e regressão para BUG-20261117-JXDJ"

closure:
  policy: local-software
  satisfied: true
resolution_kind: fixed
---
# Sem planta baixa dos objetos da cena com corte superior e cores

## Summary

O editor de paredes só desenha paredes. O titular pede uma vista de topo estilo planta baixa, com corte superior
escolhido por ele e cores 2D dos objetos, em textura sólida ou textura real.

## Expected Behavior

Pedido do titular (2026-11-17): opção de mostrar os objetos da cena na vista de topo, estilo planta baixa, com corte
superior configurável de cima para baixo (o que fica acima do corte não aparece) e cores 2D dos objetos, escolhendo
entre textura sólida e textura real.

Spec efetiva: `_reversa_sdd/walls2d/requirements.md` RF-13 descreve só "desenho da planta e painéis laterais"
(paredes e referências). Nenhum requisito cobre desenhar objetos da cena, plano de corte ou cores por material:
`spec-gap` provável, a confirmar pelo fix.

## Actual Behavior

`draw_plan` (`caffmob_draw/walls2d/ops_editor.py`) desenha o fundo, a grade, as paredes do rascunho e as paredes da
camada nova apenas como referência tracejada (`s.plan.references`). Nenhum objeto da cena entra no desenho e não há
plano de corte nem leitura de material.

Fora do editor existem peças parecidas, mas nenhuma atende ao pedido:
- `caffmob_layouts.generate_2d_plan` (`caffmob_draw/operators/layouts.py:4002`): gera uma **malha** de planta 2D com
  paredes cheias e vãos de portas/janelas. Não tem corte superior, não usa cor de material e não é desenhada dentro do
  editor.
- `caffmob_layouts.create_plan_view` (`operators/layouts.py:327`): cria vista em planta das paredes.
- `move_over/ops_dialog.py`: mostra "PLANTA BAIXA" como vista de alinhamento de um objeto, sem relação com planta do
  ambiente.

## Steps to Reproduce

1. Abrir o Editor de Paredes com um ambiente e móveis na cena.
2. Procurar no painel do editor qualquer opção de mostrar objetos, corte superior ou cor por material.

Resultado: nenhuma dessas opções existe.

## Evidence

- `../../intake/editor-de-paredes-titulo-e-ferramentas-20261117.webp`: captura do editor, sem qualquer controle de
  planta baixa, corte ou cor.
- Relato bruto: `../../intake/relato-20261117-1430.md` (Problema 5).
- `../../intake/relato-20261117-1520.md` e `../../intake/manual-ctb-cores-espessuras-20261117.webp`: padrão CTB do
  titular (verde paredes, amarelo portas e janelas, azul colunas, vermelho piso, ciano textos, magenta detalhe,
  cinza 253 hachura; tracejado para o que fica acima do corte).
- Código lido: `caffmob_draw/walls2d/ops_editor.py` (`draw_plan`), `caffmob_draw/operators/layouts.py`
  (`generate_2d_plan`, `create_plan_view`).
- `../../intake/sondagem-mcp-20261117.md`: dos 223 operadores `caffmob.*` do addon instalado, nenhum desenha planta de
  objetos com corte ou cor; os de planta vivem em `caffmob_layouts.*`, fora do editor.

## Suspected Area

Não há causa raiz a procurar: é funcionalidade inexistente. O trabalho é de desenho novo, não de conserto.

## Acceptance Criteria

- Uma opção no editor troca entre "só paredes" e "planta baixa com objetos".
- Um campo de corte superior (altura, na unidade do projeto) define onde a cena é cortada; objetos ou partes acima do
  corte não aparecem na planta.
- Objetos aparecem em 2D com preenchimento por material, alternando entre cor sólida e textura real.
- Navegação, zoom e a edição de paredes continuam funcionando com a planta baixa ligada.

## Traceability

- Specs: `_reversa_sdd/walls2d/requirements.md#RF-13`; `docs/usuario/editor-paredes-e-mover-sobre.md#1. Editor de
  Paredes (planta 2D)`
- Código suspeito: `caffmob_draw/walls2d/ops_editor.py`, `caffmob_draw/walls2d/classico_v2.py`,
  `caffmob_draw/walls2d/scene_io.py`, `caffmob_draw/operators/layouts.py`, `caffmob_draw/ui/view3d_sidebar.py`
- Testes existentes relacionados: `tests/blender_002_ui_events.py`, `tests/blender_002_smoke.py`

## Resolution

**Root cause:** `draw_plan` (`caffmob_draw/walls2d/ops_editor.py`) desenha apenas paredes do rascunho e referências tracejadas; nunca lê objetos da cena, não tem plano de corte, não pinta por material. Estado epistemológico: `supported` (evidência em `evidence/reproduction.md`).

**Veredito de spec:** `spec-gap` — não havia requisito para planta baixa com corte e cores por material. Adendo criado em `_reversa_sdd/addenda/bug-BUG-20261117-JXDJ-v001.md` (aditivo, não altera spec original).

**Change set (7 itens):**
| CHG | Tipo | Artefato | Propósito |
|-----|------|----------|-----------|
| CHG-001 | specification | `_reversa_sdd/addenda/bug-BUG-20261117-JXDJ-v001.md` | Adendo de spec (spec-gap): planta baixa com corte superior e cores por material |
| CHG-002 | code | `caffmob_draw/walls2d/ops_editor.py` | `draw_plan` desenha objetos da cena com corte e cor por material quando `plant_low` ligado |
| CHG-003 | code | `caffmob_draw/walls2d/classico_v2.py` | `desenhar` propaga `plant_low` ao caminho v2 |
| CHG-004 | code | `caffmob_draw/canvas2d/draw.py` | Nova função `draw.polygon` (triangulação) para preenchimento de objetos |
| CHG-005 | code | `caffmob_draw/walls2d/scene_io.py` | `plant_objects(scene, cut_height)` lê objetos da cena com materiais |
| CHG-006 | code | `caffmob_draw/walls2d/props.py` | Propriedades `plant_low`, `cut_height`, `material_color_mode` em `BTM_PG_WallEditorState` |
| CHG-007 | code | `tests/blender_bug_JXDJ_plant_baixa.py` | Teste de reprodução + regressão |

**Testes (vermelho→verde):**
- Reprodução: `plant_low` toggle, `cut_height`, `material_color_mode` existem após o fix (verde com as mudanças aplicadas)
- Regressão: toggle desligado → desenho de paredes inalterado; toggle ligado → objetos aparecem com corte e cor por material

**Closure policy:** `local-software` — regressão passando + veredito de spec = fechado. `resolution_kind: fixed`, causa `confirmed` (estado epistemológico `supported`), regressão e veredito presentes.


## Agent Notes

- Severidade e prioridade propostas pelo agente nesta triagem (medium/P2), a confirmar pelo titular.
- É pedido de funcionalidade, não defeito de comportamento existente: o fix deve começar por um adendo de spec
  (`spec-gap`), não por mudança de código.
- Antes de codar, consultar `docs/rag/` para o desenho 2D (`gpu`, `blf`) e para leitura de material/textura; o alvo é
  Blender 5.2.
- Custo: desenhar centenas de objetos com textura real a cada `POST_PIXEL` pesa. Considerar cache por mudança de cena
  e um limite de objetos, para não transformar o editor numa tela travada.
- Caminho mais barato: reaproveitar a ideia de `generate_2d_plan` (malha achatada) só como fonte de geometria, mantendo
  o desenho no handler existente.
