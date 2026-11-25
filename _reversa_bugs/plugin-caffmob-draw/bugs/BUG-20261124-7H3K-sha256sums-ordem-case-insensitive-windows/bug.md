---
schema_version: 1
id: BUG-20261124-7H3K
display_number: 161
title: Ensaios de SHA256SUMS ordenam por Path e divergem no Windows
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
labels: [portabilidade, suite-pura, spec-gap]
visibility: normal
security_suspected: false

reproduction:
  classification: deterministic
  rate: "1/1"
  suspected_triggers: ["executar a suíte pura no Windows"]

blocking: []

relationships: []

traceability:
  specs:
    - "_reversa_forward/021-plano-corte-camadas-gaveteiro/roadmap.md#10. Critério de pronto"
  affected_code:
    - tests/test_contrato_v2.py
    - tests/test_obra_v2.py
    - tests/test_paredes_edicao_v2.py
  root_cause:
    state: confirmed
    hypothesis: "Os três ensaios montam as linhas do SHA256SUMS com `sorted(PASTA.glob('*.json'))`. A comparação
      de `PurePath` usa a forma normalizada para maiúsculas no Windows, então `parede-L.json` ordena depois de
      `parede-aberturas-arco.json`, ao contrário da ordem ordinal usada pelo gerador do arquivo."
    causal_path:
      - "sorted(Path) usa _str_normcase (casefold no Windows)"
      - "SHA256SUMS foi gerado em ordem ordinal (byte a byte)"
      - "16 de 82 linhas divergem do arquivo gravado"
    evidence:
      - ref: "../../../cabinet_editor/inspections/2026-11-24-debugger/report.md"
        observation: "16 linhas divergentes de 82; o arquivo gravado e o calculado têm o mesmo tamanho, sem CRLF"
    code_refs:
      - file: tests/test_contrato_v2.py
        symbol: ContratoV2.test_somas_e_inventario
        commit: null
      - file: tests/test_obra_v2.py
        symbol: ObraV2.test_inventario_e_hashes
        commit: null
      - file: tests/test_paredes_edicao_v2.py
        symbol: ParedesEdicaoV2.test_somas_e_fontes
        commit: null
  reproduction_tests:
    - "cd tests && python -m unittest test_contrato_v2 test_obra_v2 test_paredes_edicao_v2"
  regression_tests:
    - "cd tests && python -m unittest test_contrato_v2 test_obra_v2 test_paredes_edicao_v2"

spec_verdict: spec-gap

change_set:
  - id: CHG-001
    kind: test
    artifact: tests/test_contrato_v2.py
    purpose: "ordenar por p.name (ordinal) em vez de Path (case-insensitive no Windows)"
    diff: fix/CHG-001.diff
  - id: CHG-002
    kind: test
    artifact: tests/test_obra_v2.py
    purpose: "mesma ordenação ordinal no ensaio de inventário de obra"
    diff: fix/CHG-001.diff
  - id: CHG-003
    kind: test
    artifact: tests/test_paredes_edicao_v2.py
    purpose: "mesma ordenação ordinal no ensaio de somas e fontes das paredes"
    diff: fix/CHG-001.diff

closure:
  policy: local-software
  satisfied: true
resolution_kind: fixed
---

# Ensaios de SHA256SUMS ordenam por Path e divergem no Windows

## Summary

A suíte pura da 021 era relatada como "187/187", mas o número contava arquivos de ensaio. Na execução real de
`unittest discover` (1582 ensaios), os três ensaios que recalculam o `SHA256SUMS` falharam no Windows porque
ordenavam os caminhos com `sorted(Path)`.

## Expected Behavior

A comparação usa a mesma ordem ordinal do gerador do `SHA256SUMS`, em qualquer sistema operacional.

## Actual Behavior

No Linux os três ensaios passavam. No Windows, `parede-L.json` ordenava depois de `parede-aberturas-arco.json`
e 16 das 82 linhas divergiam do arquivo gravado. O conteúdo dos arquivos estava correto: o deslocamento era
somente de ordem, não de fim de linha.

## Steps to Reproduce

1. Abrir o projeto no Windows.
2. Rodar `cd tests && python -m unittest test_contrato_v2 test_obra_v2 test_paredes_edicao_v2`.
3. Observar a divergência entre as linhas calculadas e o `SHA256SUMS` gravado.

## Evidence

- `../../../cabinet_editor/inspections/2026-11-24-debugger/report.md`, seção "Defeitos reais encontrados".
- Comparação byte a byte registrada no relatório: mesmo tamanho, 16 linhas fora de ordem.

## Suspected Area

Os três ensaios de inventário que recalculam o `SHA256SUMS` a partir de `Path.glob('*.json')`.

## Acceptance Criteria

- [x] A comparação usa a mesma ordem ordinal do gerador, em qualquer sistema operacional.
- [x] Nenhuma asserção de conteúdo foi afrouxada.
- [x] Os três ensaios passam na suíte pura.

## Traceability

`spec-gap`: não existe spec do ensaio em si. O comportamento esperado vem do contrato do catálogo, que exige
`SHA256SUMS` em ordem ordinal. Código afetado e testes no bloco YAML.

## Resolution

Causa confirmada: `PurePath` usa a forma normalizada para maiúsculas no Windows no momento da comparação. A
correção é explicitar a chave de ordenação com `key=lambda p: p.name` em `test_contrato_v2.py`,
`test_obra_v2.py` e `test_paredes_edicao_v2.py`. As asserções de igualdade e de contagem permanecem intactas.

## Agent Notes

Não trocar a chave por `str(p)`: o gerador usa o nome do arquivo, não o caminho completo.
