---
schema_version: 1
id: BUG-20261124-7K2M
display_number: 156
title: Contrato v2 não importa em Python 3.10 por causa de NotRequired
status: resolved
phase: delivering
severity: high
priority: P1
created: 2026-11-24
updated: 2026-11-24

origin:
  type: inspection
  external_ref: null

area: plugin
module: data
feature: unclassified
labels: [spec-gap, compatibilidade, python-3.10]
visibility: normal
security_suspected: false

reproduction:
  classification: deterministic
  rate: "29/29 falhas nos testes puros que importam o contrato"
  suspected_triggers: []

blocking: []

relationships: []

traceability:
  specs: []
  affected_code: ["caffmob_draw/caffmob/v2/contrato.py"]
  root_cause:
    state: confirmed
    hypothesis: "`typing.NotRequired` só existe a partir do Python 3.11; o Python do sistema é 3.10 e o import direto derruba qualquer módulo que carregue o contrato."
    causal_path:
      - "tests/test_*.py importam caffmob_draw.caffmob.v2.contrato"
      - "contrato.py: from typing import Literal, NotRequired, TypedDict"
      - "Python 3.10: ImportError: cannot import name 'NotRequired'"
    evidence:
      - ref: "evidence/suite-antes.log"
        observation: "29 falhas com ImportError de NotRequired"
    code_refs:
      - file: "caffmob_draw/caffmob/v2/contrato.py"
        symbol: "import"
        commit: null
  reproduction_tests: ["tests/test_017_corte.py", "tests/test_parte_v2.py"]
  regression_tests: ["tests/test_017_corte.py", "tests/test_parte_v2.py", "tests/test_contrato_v2.py"]

spec_verdict: spec-gap

change_set:
  - id: CHG-001
    kind: code
    artifact: "caffmob_draw/caffmob/v2/contrato.py"
    purpose: "importar NotRequired de typing quando existir e de typing_extensions no Python 3.10"
    diff: "fix/CHG-001.diff"

closure:
  policy: local-software
  satisfied: true
resolution_kind: fixed
---

# Contrato v2 não importa em Python 3.10 por causa de NotRequired

## Summary

O contrato v2 importava `NotRequired` diretamente de `typing`, que só oferece esse símbolo no Python 3.11. No Python 3.10 do sistema, 29 testes puros morriam no import antes de exercitar qualquer comportamento.

## Expected Behavior

O pacote importa e os testes rodam tanto no Python 3.10 do sistema quanto no 3.13 interno do Blender 5.2.

## Actual Behavior

`ImportError: cannot import name 'NotRequired' from 'typing'` em `caffmob_draw/caffmob/v2/contrato.py:2`.

## Steps to Reproduce

1. `python3 tests/test_017_corte.py` com Python 3.10.
2. Observar o ImportError no import do contrato.

## Evidence

- `evidence/suite-antes.log`

## Suspected Area

`caffmob_draw/caffmob/v2/contrato.py`.

## Acceptance Criteria

- [x] Import funciona em Python 3.10 e 3.13.
- [x] Os testes puros que importam o contrato passam.

## Traceability

Sem spec específica para compatibilidade de versão do Python: `spec-gap`. Código afetado e testes no bloco YAML.

## Resolution

Causa confirmada: símbolo ausente no `typing` do Python 3.10. Correção mínima com fallback para `typing_extensions`, que já acompanha o sistema e o Blender. Suíte pura completa: 186 arquivos, 0 falhas.

## Agent Notes

Não trocar o fallback por dependência nova: `typing_extensions` já está disponível nos dois ambientes.
