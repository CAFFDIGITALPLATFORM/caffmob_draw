# Actions: Paridade restante do Construtor e padrão completo da Biblioteca

> Identificador: `026-paridade-total-construtor-biblioteca`
> Data: `2026-11-26`
> Roadmap: `_reversa_forward/026-paridade-total-construtor-biblioteca/roadmap.md`

## Resumo

| Métrica | Valor |
|---------|-------|
| Total de ações | 12 |
| Paralelizáveis (`[//]`) | 5 |
| Maior cadeia | 6 |

## Fase 1, Núcleo

| ID | Descrição | Dependências | Paralelismo | Arquivo alvo | Status |
|----|-----------|--------------|-------------|--------------|--------|
| T001 | Sessão: vista, tema, apenas laterais, escalas e helpers `registrar_movimento`/`registrar_duplicata` | - | `[//]` | `caffmob_draw/armario_v2/window.py` | `[X]` |
| T002 | Preview: paletas Light/Dark, cor do papel em tempo de desenho, filtro laterais, vista única e escalas | T001 | - | `caffmob_draw/armario_v2/preview.py` | `[X]` |
| T003 | Núcleo puro de export/cutlist/normalização | - | `[//]` | `caffmob_draw/armario_v2/parity_core.py` | `[X]` |
| T004 | Duplicata persistida no ajuste e recriada no Gerar | T001 | - | `caffmob_draw/armario_v2/props.py`, `build.py` | `[X]` |

## Fase 2, Operadores e UI

| ID | Descrição | Dependências | Paralelismo | Arquivo alvo | Status |
|----|-----------|--------------|-------------|--------------|--------|
| T005 | Operadores de vista, tema, apenas laterais, abrir/fechar tudo, painel, medida, duplicar e export JSON | T001–T004 | - | `caffmob_draw/armario_v2/ops_window.py` | `[X]` |
| T006 | Menu de contexto e caminho modal de botão direito | T005 | - | `caffmob_draw/armario_v2/ops_window.py` | `[X]` |
| T007 | Arraste no modal com limite de 3 px, conversão px→mm e gravação no release | T005 | - | `caffmob_draw/armario_v2/ops_window.py` | `[X]` |
| T008 | Titlebar, abas horizontais, toolbar completa, seleção com Medida/Duplicar, contrato e cutlist/export | T005 | - | `caffmob_draw/armario_v2/panel_window.py` | `[X]` |

## Fase 3, Biblioteca

| ID | Descrição | Dependências | Paralelismo | Arquivo alvo | Status |
|----|-----------|--------------|-------------|--------------|--------|
| T009 | Categorias do documento + “Armários” com todo o acervo + itens da coluna | - | `[//]` | `library_panel/categories_core.py`, `draw.py` | `[X]` |
| T010 | Tema Light/Dark, botão THEME, ícone, estado e alvo de toque 44 px | - | `[//]` | `library_panel/style.py`, `layout_core.py`, `draw.py`, `ops_click.py`, `props.py`, `draw_kit.py` | `[X]` |
| T011 | Grade de Blocos 2 colunas sem alterar a grade de texturas | T009 | - | `library_panel/grid_core.py`, `draw.py`, `ops_click.py` | `[X]` |

## Fase 4, Provas e fechamento

| ID | Descrição | Dependências | Paralelismo | Arquivo alvo | Status |
|----|-----------|--------------|-------------|--------------|--------|
| T012 | Ensaios puros e Blender, regressão, i18n, API, versão/CHANGELOG, artefatos e auditoria | T005–T011 | - | `tests/`, `_reversa_forward/026...`, `blender_manifest.toml`, `CHANGELOG.md` | `[X]` |

## Notas de execução

- T001/T002: `CORES` deixou de ser um dicionário congelado; `_cor_do_papel` lê os tokens atuais.
- T004: `ajustes.duplicada` é um bool; o Gerar copia a peça de origem e desloca 20 mm.
- T007: o arraste usa `escala_frontal`/`escala_lateral` preenchidas pelo preview; clique abaixo de 3 px não move.
- T008: o cabeçalho nativo é o titlebar; as sete abas estão em uma linha.
- T009/T011: atualizados `blender_012_library_ui.py` e `blender_biblioteca_detalhe.py` para as categorias do documento.
- T012: 109 puros + i18n 3/3; 026 23/23; 025 16/16; 023 36/36; 012 9/9; card 38/38; smoke OK; API 638 arquivos.

## Histórico

| Data | Alteração | Autor |
|------|-----------|-------|
| 2026-11-26 | Versão inicial e execução | reversa |
