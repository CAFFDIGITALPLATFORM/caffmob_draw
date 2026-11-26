# Actions: Criação direta, posicionamento e galeria clara do armário v2

> Identificador: `025-criacao-posicionamento-armario`
> Data: `2026-11-26`
> Roadmap: `_reversa_forward/025-criacao-posicionamento-armario/roadmap.md`

## Resumo

| Métrica | Valor |
|---------|-------|
| Total de ações | 13 |
| Paralelizáveis (`[//]`) | 7 |
| Maior cadeia de dependência | 8 |

## Fase 1, Núcleo do posicionamento

| ID | Descrição | Dependências | Paralelismo | Arquivo alvo | Confidência | Status |
|----|-----------|--------------|-------------|--------------|-------------|--------|
| T001 | Criar `placement.py`: orientações cardeais, caixa de arame (8 vértices/12 arestas/0 faces), raycast no piso, posicionar/orientar/no cursor, ocultar/restaurar | - | `[//]` | `caffmob_draw/armario_v2/placement.py` | 🟢 | `[X]` |
| T002 | Criar `ops_placement.py`: aviso Escolher/Cursor 3D, operador do cursor, operador modal de escolha com setas, clique, Esc e fallback | T001 | - | `caffmob_draw/armario_v2/ops_placement.py` | 🟢 | `[X]` |
| T003 | Chamar `abrir_prompt` depois do snapshot no Aplicar do painel da Vista 3D | T002 | `[//]` | `caffmob_draw/armario_v2/ops.py` | 🟢 | `[X]` |
| T004 | Chamar `abrir_prompt` depois do snapshot no Aplicar da janela 023 | T002 | `[//]` | `caffmob_draw/armario_v2/ops_window.py` | 🟢 | `[X]` |
| T005 | Registrar `ops_placement` em `_MODULES` do pacote | T003, T004 | - | `caffmob_draw/armario_v2/__init__.py` | 🟢 | `[X]` |

## Fase 2, Provas do fluxo

| ID | Descrição | Dependências | Paralelismo | Arquivo alvo | Confidência | Status |
|----|-----------|--------------|-------------|--------------|-------------|--------|
| T006 | Teste puro das setas, da caixa e do fallback sem viewport | T001, T002 | `[//]` | `tests/test_placement_025.py` | 🟢 | `[X]` |
| T007 | Ensaio de janela real: Criar armário sem janela nova, gancho do Aplicar, Cursor 3D, caixa, mouse, seta, clique e Esc | T005 | `[//]` | `tests/blender_025_place.py` | 🟢 | `[X]` |

## Fase 3, Galeria

| ID | Descrição | Dependências | Paralelismo | Arquivo alvo | Confidência | Status |
|----|-----------|--------------|-------------|--------------|-------------|--------|
| T008 | Aplicar os tokens Light do mockup da Biblioteca (janela, sidebar, card, tinta, primário, teal) | - | `[//]` | `caffmob_draw/library_panel/style.py`, `draw.py`, `detail_core.py` | 🟢 | `[X]` |
| T009 | Teste puro dos tokens e da legibilidade do card | T008 | - | `tests/test_library_style_025.py` | 🟢 | `[X]` |

## Fase 4, Fechamento

| ID | Descrição | Dependências | Paralelismo | Arquivo alvo | Confidência | Status |
|----|-----------|--------------|-------------|--------------|-------------|--------|
| T010 | Escrever requirements/roadmap/actions/data-delta/legacy-impact/regression-watch/onboarding e apontar `.reversa/active-requirements.json` para 025 | T007, T009 | - | `_reversa_forward/025-criacao-posicionamento-armario/` | 🟢 | `[X]` |
| T011 | Rodar `/reversa-audit` leitor e gravar `audit/cross-check.md` (sem alterar os três artefatos) | T010 | - | `_reversa_forward/025-criacao-posicionamento-armario/audit/cross-check.md` | 🟢 | `[X]` |
| T012 | Regressão: card 38/38, UI 012 9/9, smoke 017, puros 36, puros amplos 54, i18n 3/3 e `check_api.py` | T011 | - | `tests/` | 🟢 | `[X]` |
| T013 | Bump 1.34.0, CHANGELOG e tag anotada local `v1.34.0` (sem push) | T012 | - | `caffmob_draw/blender_manifest.toml`, `CHANGELOG.md` | 🟢 | `[X]` |

## Notas de execução

- T001/T002: a caixa usa `display_type='WIRE'` e `hide_render`; o armário real é ocultado por `hide_set` e restaurado
  no cancelamento e na confirmação.
- T002/D-03: `abrir_prompt` foi adiado para um timer de 0,05 s porque o popup aberto dentro do `execute` do Aplicar
  não sobrevivia ao operador. O ensaio de janela prova o gancho; o print do Blender não captura o popup.
- T007: 16/16 checagens OK na janela real do Blender 5.2; T006: 7/7; T009: incluído no mesmo comando puro.
- T012: card 38/38, UI 012 9/9, puros 36, puros amplos 54, i18n 3/3 (28 chaves novas nos catálogos `armario_v2.json`/`library.json`), smoke 017 e `check_api.py` (637 arquivos) reexecutados nesta rodada.
- T013: versão 1.34.0 e tag local; sem push, conforme a política da rodada.

## Histórico de alterações

| Data | Alteração | Autor |
|------|-----------|-------|
| 2026-11-26 | Versão inicial e execução do fluxo | reversa |
