---
schema_version: 1
id: BUG-20261117-4MF7
display_number: 151
title: Sem coleção Arquitetura com subcoleção Parede na organização da cena
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
labels: [spec-gap, organizacao, colecoes, camadas]

visibility: normal
security_suspected: false

reproduction:
  classification: deterministic
  rate: "1/1 (leitura do código: nenhuma ocorrência de 'Arquitetura' e nenhuma coleção criada por walls2d; plano fix/plan.html aguardando aprovação)"
  suspected_triggers: []

blocking: []

relationships:
  - bug: BUG-20261117-JXDJ
    type: related-to
    state: proposed
    evidence: []

traceability:
  specs: ["_reversa_sdd/walls2d/requirements.md#RF-08", "_reversa_sdd/walls2d/design.md#Ponte com a cena"]
  affected_code: ["caffmob_draw/walls2d/apply.py", "caffmob_draw/walls2d/scene_v2.py", "caffmob_draw/walls2d/ops_editor.py"]
  root_cause:
    state: confirmed
    hypothesis: "O objeto de parede nasce sempre na raiz da cena: `hb_types.GeoNodeWall.create` delega a `GeoNodeObject.create`, que linka em `bpy.context.scene.collection.objects` (hb_types.py:73). O pacote `walls2d/` não tem nenhuma chamada de coleção, então `apply.py` grava geometria e propriedades mas nunca escolhe onde o objeto mora."
    causal_path:
      - "apply.py apply_plan: parede nova por GeoNodeWall().create('Wall') ou existente por source"
      - "hb_types.GeoNodeWall.create -> GeoNodeObject.create: bpy.data.objects.new + scene.collection.objects.link"
      - "walls2d/ sem new_collection, children.link ou users_collection: nenhuma coleção é criada, procurada ou usada"
      - "resultado: paredes na raiz da cena, fora de qualquer hierarquia de camadas"
    evidence:
      - ref: "fix/plan.html"
        observation: "plano com as cinco evidências de código, change set e riscos"
      - ref: "caffmob_draw/hb_types.py:64-73"
        observation: "GeoNodeObject.create linka todo objeto de geometria em scene.collection"
      - ref: "caffmob_draw/walls2d/apply.py"
        observation: "apply_plan cria e atualiza paredes sem tocar em users_collection"
      - ref: "caffmob_draw/mobi/cena.py:21-26"
        observation: "padrão de coleção própria do addon: reaproveita por nome antes de criar"
    code_refs:
      - file: "caffmob_draw/walls2d/apply.py"
        symbol: "apply_plan"
        commit: "8caf911e"
      - file: "caffmob_draw/hb_types.py"
        symbol: "GeoNodeObject.create"
        commit: "8caf911e"
  reproduction_tests: ["tests/blender_bug_4MF7_colecoes.py#REPRODUÇÃO: coleção Arquitetura e subcoleção Parede"]
  regression_tests: ["tests/blender_bug_4MF7_colecoes.py", "tests/blender_002_smoke.py", "tests/blender_065_walls2d_v2.py"]

spec_verdict: spec-gap

change_set:
  - id: CHG-001
    kind: test
    artifact: "tests/blender_bug_4MF7_colecoes.py"
    purpose: "reprodução (hierarquia inexistente) e regressões de reaproveitamento, migração, isolamento e OK vazio"
    diff: "fix/CHG-001.diff"
  - id: CHG-002
    kind: code
    artifact: "caffmob_draw/walls2d/layers.py"
    purpose: "arquivo novo: ensure (Arquitetura > Parede por caminho) e place (vínculo só nesta cena)"
    diff: "fix/CHG-002.diff"
  - id: CHG-003
    kind: code
    artifact: "caffmob_draw/walls2d/apply.py"
    purpose: "apply_plan garante a coleção uma vez e coloca cada parede criada ou atualizada"
    diff: "fix/CHG-003.diff"
  - id: CHG-004
    kind: specification
    artifact: "_reversa_sdd/addenda/bug-BUG-20261117-4MF7-v001.md"
    purpose: "adendo aditivo (spec-gap) da hierarquia de coleções e dos limites"

closure:
  policy: local-software
  satisfied: true
resolution_kind: fixed
---
# Sem coleção Arquitetura com subcoleção Parede na organização da cena

## Summary

O titular pede organização por camadas: uma coleção Arquitetura e as paredes dentro de Arquitetura > Parede. Hoje o
editor de paredes não cria nem procura coleção nenhuma, e as paredes caem na coleção ativa do momento.

## Expected Behavior

Pedido do titular (2026-11-17): "dentro de camadas, deve ter camada de Arquitetura (coleção), e a parede está dentro da
coleção de Arquitetura > Parede" (registrado em `../../intake/relato-20261117-1520.md`).

Spec efetiva: `_reversa_sdd/walls2d/requirements.md` RF-08 trata de OK em duas fases e da aplicação nas paredes do Home
Builder 5; `_reversa_sdd/walls2d/design.md` (seção "Ponte com a cena") descreve a leitura e a aplicação do rascunho,
sem dizer em que coleção os objetos nascem. Nenhum requisito cobre hierarquia de coleções: `spec-gap` provável.

## Actual Behavior

Nenhuma linha de `caffmob_draw/walls2d/` cria, procura ou move coleções: as buscas por `bpy.data.collections`,
`users_collection`, `collection_objects` e `new_collection` na pasta não retornam nada. O pacote inteiro também não tem
nenhuma ocorrência da palavra "Arquitetura".

Existem coleções próprias do addon em outras partes (`mobi/cena.py`, `mobi/cena_v2.py`, `legacy/groups.py` com
"CAFFMob conversão", `promob/cameras.py`, `promob/complemento.py` com "Camada · ..."), o que mostra que há padrão a
seguir, mas não essa hierarquia, e o editor de paredes não participa dela.

Resultado: no OK do editor, cada parede é criada e linkada na coleção ativa, então a organização depende de onde o
usuário estava e se perde a separação entre arquitetura e o resto do mobiliário.

## Steps to Reproduce

1. Abrir o Editor de Paredes, desenhar uma sala e clicar em OK.
2. Olhar o Outliner.

Resultado: não existe coleção Arquitetura nem subcoleção Parede; as paredes ficam soltas na coleção em uso.

## Evidence

- `../../intake/relato-20261117-1520.md` (item "camadas (coleções)").
- Código lido: `caffmob_draw/walls2d/apply.py`, `caffmob_draw/walls2d/scene_v2.py`, `caffmob_draw/walls2d/ops_editor.py`;
  busca por coleções em `caffmob_draw/walls2d/` sem resultados.
- `../../intake/sondagem-mcp-20261117.md`: o addon instalado está no ar para conferir o Outliner na correção.

## Suspected Area

`caffmob_draw/walls2d/apply.py` (criação das paredes no OK) e `scene_v2.py` (montagem do documento v2). A decisão de
onde linkar objeto novo precisa de um ponto único, senão cada chamada escolhe uma coleção.

## Acceptance Criteria

- Aplicar o rascunho no OK garante a coleção `Arquitetura` na cena, com a subcoleção `Parede` dentro dela.
- As paredes criadas ou atualizadas pelo editor ficam em `Arquitetura > Parede`, inclusive as que já existiam soltas.
- Se o usuário já tiver uma coleção com esse nome, ela é reaproveitada, sem duplicar nem renomear.
- Móveis, aberturas e outros objetos do addon não são movidos para essa coleção por engano.
- A organização respeita o desfazer do Blender: um Ctrl+Z no OK não deixa coleção vazia órfã.

## Traceability

- Specs: `_reversa_sdd/walls2d/requirements.md#RF-08`, `_reversa_sdd/walls2d/design.md#Ponte com a cena`
- Código suspeito: `caffmob_draw/walls2d/apply.py`, `caffmob_draw/walls2d/scene_v2.py`,
  `caffmob_draw/walls2d/ops_editor.py`
- Testes existentes relacionados: `tests/blender_002_smoke.py`, `tests/blender_bug_A2G7_floor.py`

## Resolution

**Causa raiz (final):** `confirmed`. `hb_types.GeoNodeWall.create` delega a `GeoNodeObject.create`, que linka todo
objeto de geometria em `bpy.context.scene.collection.objects` (`hb_types.py:73`). `caffmob_draw/walls2d/` não tinha
nenhuma chamada de coleção, então o OK gravava geometria e propriedades mas nunca escolhia onde a parede morava.

**Estratégia:** correção direta, escopo restrito às paredes (decisão do titular em 2026-11-18). Plano aprovado em
`fix/plan.html`.

**Veredito de spec:** `spec-gap` (RF-08 e a seção "Ponte com a cena" não tratavam de coleções). Adendo aditivo
aprovado: `_reversa_sdd/addenda/bug-BUG-20261117-4MF7-v001.md`.

**resolution_kind:** `fixed`.

### Change set

| CHG | Tipo | Artefato | Propósito | Diff |
|---|---|---|---|---|
| CHG-001 | test | `tests/blender_bug_4MF7_colecoes.py` | reprodução e regressões | `fix/CHG-001.diff` |
| CHG-002 | code | `caffmob_draw/walls2d/layers.py` (novo) | `ensure` e `place`: hierarquia e vínculo só nesta cena | `fix/CHG-002.diff` |
| CHG-003 | code | `caffmob_draw/walls2d/apply.py` | gancho único em `apply_plan`, coleção criada sob demanda | `fix/CHG-003.diff` |
| CHG-004 | specification | `_reversa_sdd/addenda/bug-BUG-20261117-4MF7-v001.md` | adendo aditivo (`spec-gap`) |  |

### Prova vermelho → verde

- Vermelho (antes do CHG-002/003), exit 1:
  `AssertionError: REPRODUÇÃO (#151): o OK não criou a coleção Arquitetura` (`evidence/gate1-red.md`).
- Verde (depois), exit 0: `blender_bug_4MF7_colecoes: OK` (`evidence/gate2-green.md`).
- Regressões: `blender_002_smoke` (exit 0, `OK`) e `blender_065_walls2d_v2` (exit 0, linha `OK Parede nova pertence ao
  pavimento ativo`). `blender_002_ui_events` sai com 0 mas não serve como prova: o roteiro roda num
  `bpy.app.timers` e o Blender em `--background` encerra antes do timer.
- `py -3 docs/rag/tools/check_api.py`: 577 arquivos, nenhuma referência desconhecida na API 5.2.

### Riscos e limites

- Risco da mudança: baixa (sem dado salvo, sem contrato externo, um ponto de mudança, reversível pelo desfazer do
  modal).
- Desfazer depois do OK não foi exercitado em `--background`; fica para conferência manual com interface.
- Fora de escopo: cena v2 (mantém as coleções por pavimento), piso/teto/aberturas/móveis e o empty `obj_x`, que
  continuam na coleção de origem.

## Agent Notes

- Severidade e prioridade propostas pelo agente na triagem (medium/P2), a confirmar pelo titular.
- Isto é convenção de projeto, não conserto: entra como adendo de spec antes do código, senão a organização nasce
  incompleta e cada nova função escolhe outra coleção.
- Decidir com o titular se a hierarquia vale só para paredes ou para todo o ambiente (piso, teto, aberturas, móveis),
  porque Promob separa por camadas e o pedido dele cita só Arquitetura > Parede.
- Migrar paredes já existentes é a parte delicada: mover objeto de coleção muda contexto de `bpy.ops` e pode afetar
  bibliotecas linkadas. Testar em cena com paredes antigas antes.
