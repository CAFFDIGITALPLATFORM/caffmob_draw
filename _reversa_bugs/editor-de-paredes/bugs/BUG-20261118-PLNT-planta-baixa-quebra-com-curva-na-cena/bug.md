---
schema_version: 1
id: BUG-20261118-PLNT
display_number: 153
title: Planta baixa derruba o desenho do editor com curva, texto ou vazio na cena
status: resolved
phase: delivered
severity: high
priority: P1
created: 2026-11-18
updated: 2026-11-18

origin:
  type: inspection
  external_ref: null

area: paredes
module: walls2d
feature: 002-editor-parede-mover-sobre
labels: [achado-na-entrega-JXDJ, planta-baixa, reproduzido, blender-5.2]

change_risk:
  classification: baixa
  reasons: ["filtro de tipo antes de ler a malha; nenhum dado salvo", "sem contrato externo nem texto novo para traduzir", "reversível em uma linha"]

visibility: normal
security_suspected: false

reproduction:
  classification: deterministic
  rate: "2/2 (cena do titular no Blender 5.2: o primeiro objeto CURVE derruba `plant_objects`)"
  suspected_triggers: ["objeto de tipo CURVE, FONT ou malha vazia na cena com `plant_low` ligado"]

blocking: []

relationships:
  - bug: BUG-20261117-JXDJ
    type: regression-of
    state: confirmed
    evidence:
      - ref: evidence/reproduction.md
        observation: "a função nasceu no change set do JXDJ (CHG-005) e quebra no primeiro objeto que não é malha"

traceability:
  specs: ["_reversa_sdd/walls2d/requirements.md#RF-13", "_reversa_sdd/addenda/bug-BUG-20261118-PLNT-v001.md"]
  affected_code: ["caffmob_draw/walls2d/scene_io.py", "caffmob_draw/walls2d/ops_editor.py", "caffmob_draw/walls2d/classico_v2.py"]
  root_cause:
    state: confirmed
    hypothesis: "`plant_objects` aceita `MESH`, `CURVE` e `FONT` no filtro, mas lê `obj.data.vertices` e `obj.data.edges` sempre: curva, texto e malha vazia não têm vértices, e o `AttributeError` sobe pelo `draw_plan`, derrubando o desenho inteiro do editor."
    causal_path:
      - "scene_io.py `plant_objects`: filtro aceita CURVE e FONT (`obj.type not in ('MESH', 'CURVE', 'FONT')`)"
      - "scene_io.py `plant_objects`: `obj.data.vertices` é lido sem checar tipo nem existência de vértices"
      - "ops_editor.py `draw_plan` e classico_v2.py `desenhar`: chamam `plant_objects` sem proteção dentro do handler de desenho"
      - "o `AttributeError` interrompe o `POST_PIXEL`: com a planta ligada o editor para de desenhar"
    evidence:
      - ref: evidence/reproduction.md
        observation: "AttributeError: 'Curve' object has no attribute 'vertices' na cena do titular (114 curvas, 163 vazios, 3 textos); depois do filtro, 1319 objetos lidos sem erro"
    code_refs:
      - {file: caffmob_draw/walls2d/scene_io.py, symbol: plant_objects}
      - {file: caffmob_draw/walls2d/ops_editor.py, symbol: draw_plan}
      - {file: caffmob_draw/walls2d/classico_v2.py, symbol: desenhar}
  reproduction_tests: ["tests/blender_bug_JXDJ_plant_baixa.py#REGRESSÃO: planta lê a cena com curva, vazio e objeto acima do corte"]
  regression_tests: ["tests/blender_bug_JXDJ_plant_baixa.py#REGRESSÃO: malha abaixo do corte entra na planta", "tests/blender_bug_JXDJ_plant_baixa.py#REGRESSÃO: objeto acima do corte fica fora da planta", "tests/blender_bug_JXDJ_plant_baixa.py#REGRESSÃO: malha da planta tem contorno e cor"]

spec_verdict: spec-desatualizada

change_set:
  - chg: CHG-001
    kind: code
    artifact: "caffmob_draw/walls2d/scene_io.py"
    purpose: "plant_objects lê só malhas com vértices; curva, texto e vazio ficam fora em vez de derrubar o desenho"
    diff: "fix/CHG-001.diff"
  - chg: CHG-002
    kind: test
    artifact: "tests/blender_bug_JXDJ_plant_baixa.py"
    purpose: "teste passa a exercitar plant_objects com curva, vazio e objeto acima do corte"
    diff: "fix/CHG-002.diff"
  - chg: CHG-003
    kind: specification
    artifact: "_reversa_sdd/addenda/bug-BUG-20261118-PLNT-v001.md"
    purpose: "adendo que estreita o item 3 do adendo do JXDJ para malhas da cena"

closure:
  policy: local-software
  satisfied: true
resolution_kind: fixed
---
# Planta baixa derruba o desenho do editor com curva, texto ou vazio na cena

## Summary

Ligada a planta baixa, o editor de paredes para de desenhar quando a cena tem qualquer objeto que não seja malha. Achado
na verificação de entrega do BUG-20261117-JXDJ no Blender 5.2 do titular, com a cena real.

## Expected Behavior

O adendo do JXDJ (`_reversa_sdd/addenda/bug-BUG-20261117-JXDJ-v001.md`) manda os objetos da cena aparecerem em 2D com
preenchimento, corte superior e cores por material, com navegação e edição de paredes funcionando junto. Objeto sem
malha não deveria derrubar o desenho: no máximo ficar de fora.

## Actual Behavior

`scene_io.plant_objects` (`caffmob_draw/walls2d/scene_io.py`) inclui `CURVE` e `FONT` no filtro de tipos e em seguida lê
`obj.data.vertices` e `obj.data.edges` de todo objeto. Curva, texto e malha vazia não têm vértices:

```
File "caffmob_draw\walls2d\scene_io.py", line 156, in plant_objects
    base_z = min((obj.matrix_world @ v.co).z for v in obj.data.vertices) if obj.data.vertices else 0.0
AttributeError: 'Curve' object has no attribute 'vertices'
```

A exceção sobe por `draw_plan` (`ops_editor.py`) e por `desenhar` (`classico_v2.py`), que chamam a função sem proteção
dentro do handler de desenho: com o toggle ligado, o editor inteiro para de desenhar, não só a planta.

## Steps to Reproduce

1. Abrir uma cena com curva, texto ou vazio junto das malhas (a cena do titular tem 114 curvas, 163 vazios e 3 textos).
2. Abrir o Editor de Paredes e ligar "Planta Baixa com Objetos".
3. Ler o console: `AttributeError: 'Curve' object has no attribute 'vertices'` a cada desenho.

## Evidence

- `evidence/reproduction.md`: cena real, composição por tipo, traceback, e a leitura de 1319 objetos depois do fix.
- `fix/CHG-001.diff`, `fix/CHG-002.diff`.

## Suspected Area

`scene_io.plant_objects` (filtro de tipos e leitura de malha) e os dois pontos que a chamam no desenho.

## Acceptance Criteria

- Com `plant_low` ligado, cena com curva, texto, vazio e malha vazia não levanta exceção.
- Malha abaixo do corte continua aparecendo, com contorno no piso e cor do material.
- Objeto acima do corte continua fora da planta.

## Traceability

- Specs: `_reversa_sdd/walls2d/requirements.md#RF-13`; `_reversa_sdd/addenda/bug-BUG-20261118-PLNT-v001.md`
- Código: `caffmob_draw/walls2d/scene_io.py` (`plant_objects`), `caffmob_draw/walls2d/ops_editor.py` (`draw_plan`),
  `caffmob_draw/walls2d/classico_v2.py` (`desenhar`)
- Teste: `tests/blender_bug_JXDJ_plant_baixa.py`
- Relação: `regression-of` BUG-20261117-JXDJ (travado por `DONE.md`)

## Resolution

**Causa raiz:** `plant_objects` filtrava `MESH`, `CURVE` e `FONT`, mas lia `obj.data.vertices` e `obj.data.edges` de
todo objeto sem checar tipo nem existência de vértices. Estado epistemológico: `confirmed` (traceback na cena real e
teste que reproduz o caso).

**Veredito de spec:** `spec-desatualizada` — o item 3 do adendo do JXDJ diz "objetos aparecem em 2D"; o comportamento
correto nesta rodada é só malhas, e o adendo novo (`bug-BUG-20261118-PLNT-v001.md`) registra isso sem editar o anterior.

**Change set (3 itens):**

| CHG | Tipo | Artefato | Propósito |
|-----|------|----------|-----------|
| CHG-001 | code | `caffmob_draw/walls2d/scene_io.py` | `plant_objects` lê só malhas com vértices |
| CHG-002 | test | `tests/blender_bug_JXDJ_plant_baixa.py` | teste exercita curva, vazio e objeto acima do corte |
| CHG-003 | specification | `_reversa_sdd/addenda/bug-BUG-20261118-PLNT-v001.md` | adendo que estreita o escopo para malhas |

**Testes (vermelho→verde):**

- Vermelho: no Blender 5.2 com a cena do titular, `plant_objects` levantou `AttributeError: 'Curve' object has no
  attribute 'vertices'` (traceback em `evidence/reproduction.md` e no console do addon).
- Verde: `blender --background --factory-startup --python-exit-code 1 --python tests/blender_bug_JXDJ_plant_baixa.py`
  → 10 checagens OK, `EXIT=0`, incluindo "planta lê a cena com curva, vazio e objeto acima do corte".
- Verde no Blender do titular: addon atualizado para 1.25.0 e `plant_objects` devolveu 1319 objetos sem erro.

**Closure policy:** `local-software` — regressão passando + veredito de spec = fechado. `resolution_kind: fixed`.

## Agent Notes

- Severidade e prioridade propostas pelo agente nesta rodada (high/P1), a confirmar pelo titular: a falha derruba o
  desenho do editor inteiro, mas só com o toggle da planta ligada.
- Curvas, texto e vazios ficam fora da planta por ora: `to_mesh()` por objeto a cada `POST_PIXEL` custaria caro numa
  cena de 1681 objetos. Se o titular quiser esses objetos na planta, o caminho é cache por mudança de cena.
- O teste do JXDJ só checava a existência das propriedades; agora exercita a leitura da cena. Vale o mesmo cuidado nos
  próximos testes de feature: encostar no caminho de desenho, não só no estado.
