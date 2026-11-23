# DONE, BUG-20261123-RW3G

Encerrado em 2026-11-23, na ordem do fluxo: causa raiz e change set aplicados, veredito de spec decidido pelo titular, e só então esta trava.

- **resolution_kind:** `fixed`. Closure policy `local-software` satisfeita.
- **Veredito de spec:** `spec-gap`, aprovado pelo titular em 2026-11-23 (opção 1 do menu do `/reversa-debugger-fix`), com adendo aditivo `_reversa_sdd/addenda/bug-BUG-20261123-RW3G-v001.md`. A spec original não foi tocada.
- **Change set:** CHG-001 (`build.py`, filtro `entrada_excluida`), CHG-002 (`tests/test_packaging.py`, reprodução e regressão do zip) e CHG-003 (o adendo). Código e spec registrados juntos na seção Resolution do `bug.md`.
- **Verificação:** `test_entradas_excluidas_do_pacote` e `test_zip_tem_manifesto_na_raiz` verdes; `python build.py` com exit 0 gera zip de 2363 arquivos sem nenhuma entrada iniciada por ponto, sem `__pycache__` e sem `*.pyc`, com `blender_manifest.toml` e `__init__.py` na raiz.

Este bug está encerrado. Nenhum agente deve modificar esta pasta. Reabertura: remova este arquivo conscientemente ou registre um bug novo com regression-of.
