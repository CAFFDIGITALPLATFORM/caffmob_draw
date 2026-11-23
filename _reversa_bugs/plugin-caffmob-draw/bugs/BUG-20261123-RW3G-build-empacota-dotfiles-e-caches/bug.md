---
schema_version: 1
id: BUG-20261123-RW3G
display_number: 155
title: "build.py empacota dotfiles e caches no zip (sai .impeccable/hook.cache.json)"
status: resolved
phase: delivering
severity: low
priority: P3
created: 2026-11-23
updated: 2026-11-23
express: true

origin:
  type: manual-report
  external_ref: null

area: plugin
module: hb_core
feature: unclassified
labels: ["empacotamento", "higiene-do-pacote", "expresso"]

change_risk:
  classification: baixa
  reasons: ["muda só o filtro do os.walk do empacotador", "nenhum arquivo lido pelo add-on é excluído", "o teste de empacotamento já roda o build num diretório temporário"]

visibility: normal
security_suspected: false

reproduction:
  classification: deterministic
  rate: "1/1"
  suspected_triggers: []

blocking: []

relationships:
  - bug: BUG-20261123-56YQ
    type: related-to
    state: confirmed
    evidence:
      - ref: ../../BUG-20261123-56YQ-instalar-zip-falha-no-lock-do-repositorio/evidence/reproduction.md
        observation: "o vazamento foi notado na conferência do pacote feita para aquele bug"

traceability:
  specs: ["_reversa_sdd/deployment.md"]
  affected_code: ["build.py", "tests/test_packaging.py"]
  root_cause:
    state: confirmed
    hypothesis: "O empacotador monta o zip com os.walk e um zipfile próprio: tirava só __pycache__ e o catalog/ da raiz (feature 005, D-16), então todo dotfile e todo cache de ferramenta que exista dentro de caffmob_draw/ viaja no pacote. O paths_exclude_pattern do manifesto não é consultado por este script."
    causal_path:
      - "build.py, build_zip: os.walk(source_dir) sem filtro de dotfile"
      - "caffmob_draw/.impeccable/hook.cache.json (cache de ferramenta de agente) entra no arcname"
      - "zipfile.write grava .impeccable/hook.cache.json no pacote"
    evidence:
      - ref: evidence/reproduction.md
        observation: "listagem do zip conferido no BUG-20261123-56YQ com .impeccable/hook.cache.json"
    code_refs:
      - {file: build.py, symbol: build_zip, commit: null}
  reproduction_tests: ["tests/test_packaging.py::EmpacotamentoTest::test_entradas_excluidas_do_pacote"]
  regression_tests: ["tests/test_packaging.py::EmpacotamentoTest::test_entradas_excluidas_do_pacote", "tests/test_packaging.py::EmpacotamentoTest::test_zip_tem_manifesto_na_raiz"]

spec_verdict: spec-gap

change_set:
  - id: CHG-001
    kind: code
    artifact: build.py
    purpose: "filtro de entradas do zip: dotfiles, dot-dirs, __pycache__, *.pyc (mantendo o catalog/ só na raiz)"
    diff: fix/CHG-001.diff
  - id: CHG-002
    kind: test
    artifact: tests/test_packaging.py
    purpose: "regressão: o zip não leva dotfile nem cache, e segue com manifesto e __init__.py na raiz"
    diff: fix/CHG-002.diff
  - id: CHG-003
    kind: specification
    artifact: _reversa_sdd/addenda/bug-BUG-20261123-RW3G-v001.md
    purpose: "adendo aditivo (spec-gap) que especifica o que entra e o que não entra no zip"
    diff: ../../../../_reversa_sdd/addenda/bug-BUG-20261123-RW3G-v001.md
closure:
  policy: local-software
  satisfied: true
resolution_kind: fixed
---

# build.py empacota dotfiles e caches no zip (sai .impeccable/hook.cache.json)

## Summary

O `build.py` empacota `caffmob_draw/` inteiro com `os.walk` e só exclui `__pycache__` e o `catalog/` da raiz. Toda pasta ou arquivo de ferramenta que comece com ponto entra no pacote: o zip gerado levava `.impeccable/hook.cache.json`, e o pacote tem quatro pastas `.impeccable/` (raiz do pacote, `product_libraries/closets`, `product_libraries/common` e `product_libraries/face_frame`).

## Expected Behavior

O pacote leva apenas o que o add-on usa: código, dados, `wheels/`, `assets/` e os `.blend`. Dotfiles, dot-dirs e caches (`.impeccable/`, `__pycache__/`, `*.pyc`) ficam fora. O manifesto e o `__init__.py` continuam na raiz do zip.

Spec efetiva: `_reversa_sdd/deployment.md`. O que pode ir no pacote nunca foi especificado além da exclusão do `catalog/`, então o veredito é `spec-gap`.

## Actual Behavior

`.impeccable/hook.cache.json` dentro de `caffmob_draw.zip` (2367 arquivos, conferido no BUG-20261123-56YQ).

## Steps to Reproduce

1. `python build.py`
2. `python -c "import zipfile; print([n for n in zipfile.ZipFile('caffmob_draw.zip').namelist() if n.startswith('.') or '__pycache__' in n])"`

Antes da correção a lista traz `.impeccable/hook.cache.json`.

## Evidence

- `evidence/reproduction.md`: antes e depois da correção, com a lista de entradas excluídas.
- Relato: `../../intake/relato-20261123-1110.md`.
- Origem do achado: `../BUG-20261123-56YQ-instalar-zip-falha-no-lock-do-repositorio/evidence/reproduction.md`, seção 4.

## Suspected Area

- `build.py`, função `build_zip`
- `tests/test_packaging.py`

## Acceptance Criteria

- `python build.py` gera o zip sem nenhum caminho com componente iniciado por ponto e sem `__pycache__` ou `*.pyc`.
- O zip continua com `blender_manifest.toml` e `__init__.py` na raiz, e o build continua saindo com exit 0.
- O teste de regressão falha antes da correção e passa depois.

## Traceability

- Specs: `_reversa_sdd/deployment.md`
- Código afetado: `build.py`, `tests/test_packaging.py`
- Causa raiz: confirmada (filtro do `os.walk` não olhava dotfiles nem caches)
- Relações propostas: `related-to` BUG-20261123-56YQ (confirmada: o achado nasceu da conferência daquele bug)

## Resolution

- **Causa raiz (confirmed):** `build.py#build_zip` monta o zip com `os.walk` e `zipfile` próprios e só tirava `__pycache__` e o `catalog/` da raiz. Todo dotfile e dot-dir que existisse dentro de `caffmob_draw/` viajava no pacote; `.impeccable/hook.cache.json` era um deles, em quatro cópias.
- **Veredito de spec:** `spec-gap` **aprovado pelo titular em 2026-11-23** (opção 1 do menu). Adendo aditivo `_reversa_sdd/addenda/bug-BUG-20261123-RW3G-v001.md` especifica o que entra e o que não entra no zip; a spec original não foi tocada.
- **resolution_kind:** fixed. **Closure policy:** `local-software`, satisfeita (regressão passando + veredito).

| CHG | tipo | artefato | propósito | diff |
|---|---|---|---|---|
| CHG-001 | code | `build.py` | `entrada_excluida(nome, rel_dir)` e `EXCLUIDOS_NA_RAIZ`: dotfiles, dot-dirs, `__pycache__`, `*.pyc`/`*.pyo` e o `catalog/` só na raiz | `fix/CHG-001.diff` |
| CHG-002 | test | `tests/test_packaging.py` | reprodução do filtro e regressão no zip gerado (sem dotfile, sem cache, manifesto e `__init__.py` na raiz) | `fix/CHG-002.diff` |
| CHG-003 | specification | `_reversa_sdd/addenda/bug-BUG-20261123-RW3G-v001.md` | adendo aditivo (`spec-gap`) com o conteúdo permitido no zip | `bug-BUG-20261123-RW3G-v001.md` |

**Vermelho (antes):** zip com 2367 arquivos, incluindo `.impeccable/hook.cache.json`; o filtro vivia dentro do `os.walk` e não existia como função testável.

**Verde (depois):**

- `python build.py` → exit 0, *Successfully created 'caffmob_draw.zip'!*, **2363 arquivos** (exatamente os quatro caches a menos), 167,8 MB.
- Zip conferido: `entradas com ponto: []`, `pyc/pyo: []`, `impeccable: []`, `manifesto raiz: True`, `__init__.py raiz: True`, 12 wheels, 113 `.blend` e `assets/slides/slide-st48-0200-0.obj`.
- `test_entradas_excluidas_do_pacote` → OK; `test_zip_tem_manifesto_na_raiz` → OK (25,3 s, roda o build numa cópia temporária).

- **Reprodução:** `tests/test_packaging.py::EmpacotamentoTest::test_entradas_excluidas_do_pacote`. **Regressão:** o mesmo teste mais `test_zip_tem_manifesto_na_raiz`.

## Agent Notes

- Rota expressa: severidade `low` e prioridade `P3` propostas pelo agente, junto com o plano curto no chat.
- Fora de escopo: tamanho do zip (167,8 MB por causa dos `.blend`, que são necessários) e o manifesto em `novo_arm_building/` que faz `test_raiz_nao_e_extensao` falhar desde antes desta feature.
- `module: hb_core` reaproveitado dos bugs de instalação/empacotamento; o `taxonomy.yaml` não tem termo de empacotamento.
