---
schema_version: 1
id: BUG-20261124-Q2MF
display_number: 162
title: Ensaio do transporte por subprocesso usa select num pipe e quebra no Windows
status: resolved
phase: closed
severity: medium
priority: P2
created: 2026-11-24
updated: 2026-11-24

origin:
  type: ci-failure
  external_ref: null

area: plugin
module: data
feature: 021-plano-corte-camadas-gaveteiro
labels: [portabilidade, suite-pura, downloads, spec-gap]
visibility: normal
security_suspected: false

reproduction:
  classification: deterministic
  rate: "1/1"
  suspected_triggers: ["rodar a suíte pura no Windows"]

blocking: []

relationships: []

traceability:
  specs:
    - "_reversa_sdd/architecture.md#Re-extração 2026-10-10 — arquitetura atual"
  affected_code:
    - tests/test_download_core_mobi.py
  root_cause:
    state: confirmed
    hypothesis: "O ensaio espera a primeira linha do worker com `select.select([proc.stdout], ...)`. No Windows
      `select` aceita apenas soquetes e levanta OSError 10038 para um pipe."
    causal_path:
      - "subprocess.Popen(stdout=PIPE) cria um pipe, não um soquete"
      - "select.select no Windows só trata winsock"
      - "o ensaio morre antes de avaliar a resposta do worker"
    evidence:
      - ref: "../../../cabinet_editor/inspections/2026-11-24-debugger/report.md"
        observation: "OSError: [WinError 10038] Foi tentada uma operação em algum item que não é um soquete"
    code_refs:
      - file: tests/test_download_core_mobi.py
        symbol: Protocolo.test_subprocesso_transporta_formulario_headers_e_etag
        commit: null
  reproduction_tests:
    - "cd tests && python -m unittest test_download_core_mobi"
  regression_tests:
    - "cd tests && python -m unittest test_download_core_mobi"

spec_verdict: spec-gap

change_set:
  - id: CHG-001
    kind: test
    artifact: tests/test_download_core_mobi.py
    purpose: "esperar a resposta do worker numa thread leitora com join(5) em vez de select num pipe"
    diff: fix/CHG-001.diff

closure:
  policy: local-software
  satisfied: true
resolution_kind: fixed
---

# Ensaio do transporte por subprocesso usa select num pipe e quebra no Windows

## Summary

O ensaio do transporte por subprocesso (`download_core`) usava `select.select` para esperar a primeira linha do
worker. No Windows `select` só funciona com soquetes, então o ensaio levantava `OSError 10038` antes de ler a
resposta. O produto não estava envolvido: a falha era do próprio ensaio.

## Expected Behavior

A espera pela resposta do worker funciona em qualquer plataforma, com limite de tempo, e as asserções de status,
ETag, `If-Match` e corpo do formulário continuam sendo avaliadas.

## Actual Behavior

No Windows, `select.select([proc.stdout], [], [], 5)` levantava `OSError: [WinError 10038]` porque `proc.stdout`
é um pipe, não um soquete. A resposta do worker nunca era lida nem avaliada.

## Steps to Reproduce

1. Rodar a suíte pura no Windows.
2. Executar `python -m unittest test_download_core_mobi`.
3. Observar o `OSError 10038` na espera pela primeira linha do subprocesso.

## Evidence

- `../../../cabinet_editor/inspections/2026-11-24-debugger/report.md`, seção "Defeitos reais encontrados".
- A revisão da thread leitora de `caffmob_draw/texture_library/downloads.py` está no mesmo relatório: a thread
  `_pump` só enfileira linhas sob lock, o timer `_tick` drena no thread principal, `eof` é conferido por processo e
  `shutdown()` limpa fila, buffer e callback. Nenhum defeito de produto foi encontrado.

## Suspected Area

O ensaio do protocolo JSON do worker de download, que esperava a resposta com `select`.

## Acceptance Criteria

- [x] A espera funciona no Windows e no Linux, com timeout de 5 s.
- [x] As asserções de status, ETag, `If-Match` e corpo do formulário seguem idênticas.
- [x] O ensaio passa na suíte pura.

## Traceability

`spec-gap`: não existe spec do ensaio em si. O comportamento esperado é o contrato do worker de `download_core`,
coberto pelo próprio ensaio. Código afetado e testes no bloco YAML.

## Resolution

Causa confirmada: `select` não trata pipes no Windows. A correção troca a espera por uma thread leitora que faz
`proc.stdout.readline()` e um `join(5)`; se a thread não devolver nada em 5 s, o ensaio falha com mensagem própria.
As asserções de status, ETag, `If-Match` e corpo permanecem as mesmas.

## Agent Notes

Não voltar a usar `select` em `proc.stdout`: o caminho do Windows é o que motivou o bug. A thread é daemon para não
segurar o processo de ensaio se o worker não responder.
