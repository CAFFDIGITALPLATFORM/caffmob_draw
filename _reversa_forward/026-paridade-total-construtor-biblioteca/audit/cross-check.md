# Cross-check: Paridade restante do Construtor e padrão completo da Biblioteca

> Data: `2026-11-26`
> Feature: `_reversa_forward/026-paridade-total-construtor-biblioteca`
> Artefatos analisados: [`requirements.md`](../requirements.md) · [`roadmap.md`](../roadmap.md) · [`actions.md`](../actions.md)
> Apoio: [`data-delta.md`](../data-delta.md) · [`legacy-impact.md`](../legacy-impact.md) · [`regression-watch.md`](../regression-watch.md)
> Fontes: `mockup_construtor_armarios.html`; `docs/Caff+Mob+Biblioteca+Mockup.tar.gz`; `docs/Elicitacao+Requisitos+Caff+Mob+Biblioteca.tar.gz`
>
> **Este relatório é só de leitura.** Nenhum dos três artefatos foi alterado por esta auditoria.

## 1. Resumo

| Severidade | Quantidade |
|------------|------------|
| CRITICAL | 0 |
| HIGH | 0 |
| MEDIUM | 0 |
| LOW | 0 |
| **Total** | **0** |

Cada requisito funcional da 026 tem decisão e ação; cada decisão tem ação; cada cenário Gherkin tem prova. A
matriz abaixo liga função → código → teste executado nesta rodada. Não há item marcado como pendente, bloqueado
ou fora de escopo.

## 2. Achados

| ID | Severidade | Eixo | Descrição | Onde está |
|----|------------|------|-----------|-----------|
| — | — | — | Nenhuma inconsistência encontrada | — |

Não há CRITICAL nem HIGH para explicar em §3.

## 3. Matriz de rastreabilidade

### 3.1 Construtor

| ID | Fonte | Função | Código | Prova executada | Resultado |
|----|-------|--------|--------|-----------------|-----------|
| C01 | mockup toolbar | Toolbar completa (montar/limpar, vistas, cotas, portas, abrir/fechar, laterais, tema, painel, plano, export) | `panel_window.py` `BTM_PT...Toolbar`; `ops_window.py` operadores | `blender_026_parity` (vista, tema, laterais, operadores registrados); UI 012 para o painel da Biblioteca | PASSOU |
| C02 | mockup export | Export JSON com spec/peças/cutlist | `ops_window.py` `BTM_OT...ExportJson`; `parity_core.payload` | `blender_026_parity` grava e lê o JSON; `test_armario_026_parity` | PASSOU |
| C03 | mockup titlebar | Titlebar com título, dimensões, contrato/export/tema | `panel_window.py` header | `blender_026_parity` (export/tema registrados); `blender_023_fase7` (memória/painéis) | PASSOU |
| C04 | mockup abas | Sete abas em uma linha horizontal | `panel_window.py` header, `ABAS` | `blender_023_fase7` (troca de aba) + inspeção de código; UI 012 | PASSOU |
| C05 | mockup menu | Menu de contexto Duplicar/Medida/Espelhar/Apagar | `ops_window.py` `BTM_MT...Context`; modal RIGHTMOUSE | `blender_026_parity` chama `draw` e valida os ids; duplicata testada | PASSOU |
| C06 | mockup medida | Popover de medida largura/altura/profundidade | `ops_window.py` `BTM_OT...Medida` | `blender_026_parity('EXEC_DEFAULT', medida=800, eixo=LARGURA)` | PASSOU |
| C07 | mockup arraste | Arraste press→move→release com ajuste dx/dy/dz | `ops_window.py` modal; `window.registrar_movimento` | `blender_026_parity` simula os três eventos; dx/dz > 0 | PASSOU |
| C08 | mockup cutlist | Lista de peças + cutlist exportada | `panel_window.py` `BTM_PT...Pecas`; `parity_core.cutlist` | `blender_026_parity` soma quantidades = peças; puro testa agrupamento | PASSOU |
| C09 | mockup “Apenas Laterais” | Liga laterais, desliga base/fundo, gera só LATERAL | `ops_window.py` `BTM_OT...ApenasLaterais`; `preview.py` filtro | `blender_026_parity` flags + `papeis == {'LATERAL'}` | PASSOU |
| C10 | mockup Light/Dark | Tokens Light/Dark no preview e na Biblioteca | `preview.py` `PALETAS/aplicar_tema`; `library_panel/style.py`; `THEME` | `blender_026_parity` alterna DARK/LIGHT; `test_armario_026_parity` tokens; UI theme | PASSOU |

### 3.2 Biblioteca

| ID | Fonte | Função | Código | Prova executada | Resultado |
|----|-------|--------|--------|-----------------|-----------|
| L01 | documento, navegação | Categorias Armários/Portas/Janelas/Armários autorais | `categories_core.py` `FIXED/SIDEBAR_FIXED`; `draw.items` | `blender_012_library_ui` 9/9; `test_library_environments` | PASSOU |
| L02 | documento, grade | Seis modelos em 2×3 na aba Blocos | `grid_core.py` `columns(..., fixed=2)`; `draw._draw_grid`; `ops_click.cell_at` | `test_armario_026_parity` (2 colunas); card 38/38 | PASSOU |
| L03 | documento, tema | Light/Dark persistido na sessão, padrão Light | `style.py` `LIGHT/DARK/aplicar_tema`; `props.theme`; `ops_click THEME` | `test_armario_026_parity` troca e volta; UI 012 | PASSOU |
| L04 | documento, toque | Alvo mínimo de 44 px no cabeçalho | `layout_core._touch`; `style.MIN_TOUCH` | `test_armario_026_parity` acerta fora do desenho de 22 px | PASSOU |

### 3.3 Preservação

| ID | Requisito | Código | Prova | Resultado |
|----|-----------|--------|-------|-----------|
| F01 | Fluxo 025 Criar→Aplicar→Escolher/Cursor 3D | `ops_placement.py`, `placement.py` (intocados) | `blender_025_place` 16/16 | PASSOU |
| F02 | Janela 023 fila/modal/lote/memória/GEO | `ops_window.py`, `fila.py`, `window.py` | `blender_023_fase7` 36/36 | PASSOU |
| F03 | Biblioteca UI e card | `draw.py`, `detail_core.py`, `ops_detail.py` | UI 9/9; card 38/38 | PASSOU |
| F04 | i18n, API 5.2 e smoke | catálogos, `check_api.py`, `blender_smoke.py` | i18n 3/3; 638 arquivos sem API desconhecida; smoke OK | PASSOU |

## 4. Cobertura RF → decisão → ação

| RF | Decisão | Ação | Prova |
|----|---------|------|-------|
| RF-01 | D-01 | T005, T008 | C01 |
| RF-02 | D-02 | T003, T005, T008 | C02 |
| RF-03 | D-03 | T008 | C03 |
| RF-04 | D-04 | T008 | C04 |
| RF-05 | D-05, D-06 | T004, T005, T006 | C05 |
| RF-06 | D-07 | T005, T006 | C06 |
| RF-07 | D-08 | T001, T007 | C07 |
| RF-08 | D-09 | T003, T008 | C08 |
| RF-09 | D-10 | T001, T002, T005 | C09 |
| RF-10 | D-11 | T001, T002, T005, T010 | C10, L03 |
| RF-11 | D-12 | T009 | L01 |
| RF-12 | D-12 | T011 | L02 |
| RF-13 | D-11, D-12 | T010 | L03 |
| RF-14 | D-12 | T010 | L04 |
| RF-15 | D-13 | T012 | F01 |
| RF-16 | D-13 | T012 | F02 |
| RF-17 | D-13 | T012 | F03 |
| RF-18 | D-13 | T012 | F04 |

Não há requisito sem decisão nem decisão sem ação.

## 5. Cenários Gherkin

| Cenário | Cobertura |
|---------|-----------|
| Exportar armário e cutlist | C02/C08 + `test_armario_026_parity` |
| Arrastar uma peça | C07 + modal 026 |
| Apenas Laterais | C09 |
| Menu de contexto e medida | C05/C06 |
| Tema e Biblioteca | C10/L03 + teste puro |
| Categorias do documento | L01 + UI 012 |

## 6. Consistência e sanidade

- **Termos:** “Apenas Laterais”, “Medida”, “Exportar JSON”, “Light/Dark” e “Armários autorais” são usados igual nos
  três artefatos e na UI.
- **Identificadores:** RF-01..RF-18, D-01..D-13 e T001..T012 existem e são referenciados.
- **Dependências:** T002/T003/T004→T001; T005→T001–T004; T006/T007→T005; T008→T005; T011→T009; T012→T005–T011.
  Nenhuma aponta para fora da lista.
- **Paralelismo:** T001/T003/T009/T010 não compartilham arquivo; T005–T008 são sequenciais por tocarem o mesmo
  modal/painel.
- **Ciclo:** não há; a maior cadeia é T001→T005→T007→T012 (4 nós) e T009→T011→T012 (3 nós).
- **Legado:** `ajustes.duplicada` tem default falso; o fluxo sem duplicata é idêntico. A remoção das categorias de
  ambiente da navegação é requisito do documento; `LINES`/`LINE_LABELS` continuam no card.
- **Dados:** `data-delta.md` cobre o único campo persistido novo e os campos de sessão.

## 7. Itens verificados que passaram

- Cobertura: 18 RF, 13 decisões e 12 ações ligados sem órfãos.
- Consistência: termos e identificadores conferem; contratos do JSON e do ajuste estão no roadmap.
- Legado: nenhuma regra 🟢 da 023/025 foi contrariada; 025 e 023 passaram 16/16 e 36/36.
- Sanidade: dependências válidas, sem ciclo, sem `[//]` no mesmo arquivo.
- Provas: 026 23/23; puros 109; i18n 3/3; API 638; smoke OK; UI 9/9; card 38/38.
- Nenhuma linha da matriz está pendente, bloqueada ou fora de escopo.
