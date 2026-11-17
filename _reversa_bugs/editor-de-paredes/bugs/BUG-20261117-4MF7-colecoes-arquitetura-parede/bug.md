---
schema_version: 1
id: BUG-20261117-4MF7
display_number: 151
title: Sem coleção Arquitetura com subcoleção Parede na organização da cena
status: open
phase: triaging
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
labels: [spec-gap, organizacao, colecoes, camadas]

visibility: normal
security_suspected: false

reproduction:
  classification: deterministic
  rate: "1/1 (leitura do código: nenhuma ocorrência de 'Arquitetura' e nenhuma coleção criada por walls2d)"
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
  root_cause: null
  reproduction_tests: []
  regression_tests: []

spec_verdict: null

change_set: []

closure:
  policy: local-software
  satisfied: false
resolution_kind: null
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

A preencher pelo `/reversa-debugger-fix`.

## Agent Notes

- Severidade e prioridade propostas pelo agente na triagem (medium/P2), a confirmar pelo titular.
- Isto é convenção de projeto, não conserto: entra como adendo de spec antes do código, senão a organização nasce
  incompleta e cada nova função escolhe outra coleção.
- Decidir com o titular se a hierarquia vale só para paredes ou para todo o ambiente (piso, teto, aberturas, móveis),
  porque Promob separa por camadas e o pedido dele cita só Arquitetura > Parede.
- Migrar paredes já existentes é a parte delicada: mover objeto de coleção muda contexto de `bpy.ops` e pode afetar
  bibliotecas linkadas. Testar em cena com paredes antigas antes.
