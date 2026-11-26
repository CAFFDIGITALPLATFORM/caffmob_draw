# Onboarding — Feature 026 concluída

> **Estado:** CONCLUÍDA em 2026-11-26.
> **Commit local:** `d0c67988` · **Tag:** `v1.35.0` · **Push:** não realizado.
> **Auditoria:** `_reversa_forward/026-paridade-total-construtor-biblioteca/audit/cross-check.md` — 0 CRITICAL,
> 0 HIGH, 0 MEDIUM, 0 LOW.
> **Reversa:** `requirements.md`, `roadmap.md`, `actions.md` (12/12 `[X]`), `data-delta.md`,
> `legacy-impact.md`, `regression-watch.md`, `progress.jsonl` e este onboarding.
> **Feature ativa:** `.reversa/active-requirements.json` aponta para a 026, estágio `done`.

Este arquivo é a memória de contexto para outro agente. Ele não é um pedido para reimplementar a 026: a feature já
foi implementada, provada e commitada. Leia o estado final antes de propor qualquer mudança.

---

## 1. Prompt de retomada (copiar)

```text
Você está retomando o CAFFMob Draw depois da feature 026 (paridade restante do Construtor e padrão da Biblioteca).

Antes de agir:
1. Leia _reversa_forward/026-paridade-total-construtor-biblioteca/onboarding.md inteiro.
2. Confirme `git log -2 --oneline --decorate`: o HEAD deve ser d0c67988, tag v1.35.0.
3. Leia o cross-check da 026; ele está 0/0/0/0.
4. Não reabra a 026 nem a 025 sem um pedido novo e explícito.
5. Não faça push, não commite AGENTS.md, PNGs nem docs/*.tar.gz.
6. Se o pedido for uma função nova do mockup ou da Biblioteca, trate como feature nova (027), com prova executada.
7. Use o RAG em docs/rag/ antes de mexer em bpy/gpu/blf; rode check_api.py depois.

A 026 entregou: toolbar completa, export JSON/cutlist, titlebar, abas horizontais, menu de contexto, popover de
medida, arraste, Apenas Laterais, Light/Dark, categorias do documento, grade 2×3, tema da Biblioteca e alvo de 44 px.
O fluxo 025 (Criar→Aplicar→Escolher/Cursor 3D) permanece intacto.
```

---

## 2. O que está pronto

### 2.1 Construtor

| ID | Entrega | Código principal | Prova |
|----|---------|------------------|-------|
| C01 | Toolbar completa | `panel_window.py`, `ops_window.py` | `blender_026_parity` |
| C02 | Export JSON + cutlist | `ops_window.py`, `parity_core.py` | `blender_026_parity`, `test_armario_026_parity` |
| C03 | Titlebar | `panel_window.py` | `blender_026_parity` + 023 |
| C04 | Sete abas horizontais | `panel_window.py` | `blender_023_fase7` + UI |
| C05 | Menu de contexto | `ops_window.py` (`BTM_MT...Context`) | `blender_026_parity` (draw + duplicata) |
| C06 | Popover de medida | `BTM_OT...Medida` | `blender_026_parity` (`EXEC_DEFAULT`) |
| C07 | Arraste press→move→release | modal + `window.registrar_movimento` | `blender_026_parity` (eventos sintéticos) |
| C08 | Cutlist no painel | `panel_window.py` + `parity_core.cutlist` | `blender_026_parity` |
| C09 | Apenas Laterais | `BTM_OT...ApenasLaterais` + filtro do preview | `blender_026_parity` (`papeis == {'LATERAL'}`) |
| C10 | Light/Dark | `preview.PALETAS/aplicar_tema`; `style.LIGHT/DARK` | `blender_026_parity` + puros |

### 2.2 Biblioteca

| ID | Entrega | Código | Prova |
|----|---------|--------|-------|
| L01 | Armários, Portas, Janelas, Armários autorais | `categories_core.py`, `draw.items` | UI 012 9/9 |
| L02 | Grade 2×3 na aba Blocos | `grid_core.columns(fixed=2)`, `draw._draw_grid` | `test_armario_026_parity`, card 38/38 |
| L03 | Tema Light/Dark | `style.py`, `props.theme`, `ops_click THEME` | puros + UI |
| L04 | Alvo de 44 px | `layout_core._touch`, `style.MIN_TOUCH` | `test_armario_026_parity` |

### 2.3 Preservado

- 025: Criar armário na viewport, Aplicar com Escolher/Cursor 3D, caixa de arame, setas, clique, Esc e Cursor 3D.
- 023: fila/modal, seleção múltipla, lote, memória por cena, GEO-001/GEO-002.
- Biblioteca: card de detalhe, inserção por clique/arraste, recusa de chapa.
- i18n, API 5.2 e smoke.

---

## 3. Provas (resultado desta rodada)

| Comando | Resultado |
|---------|-----------|
| `tests/blender_026_parity.py` | **23/23 OK** |
| `tests/blender_025_place.py` | **16/16 OK** |
| `tests/blender_023_fase7.py` | **36/36 OK** |
| `tests/blender_012_library_ui.py` | **9/9 OK** |
| `tests/blender_biblioteca_detalhe.py` | **38/38 OK** |
| Puros amplos (build, corte, janela, UV, MDF, view, placement, library, 026) | **109 OK** |
| `test_i18n_coverage` | **3/3 OK** (36 chaves novas em `armario_v2.json`) |
| `docs/rag/tools/check_api.py` | **638 arquivos**, nenhuma API desconhecida |
| `tests/blender_smoke.py` | `BLENDER_SMOKE_OK` |
| Ruff dos arquivos novos/tocados da 026 | limpo |

Comandos:

```bash
BL="/c/Program Files/Blender Foundation/Blender 5.2/blender.exe"
"$BL" --factory-startup --enable-event-simulate --python-exit-code 1 --python tests/blender_026_parity.py
"$BL" --factory-startup --enable-event-simulate --python-exit-code 1 --python tests/blender_025_place.py
"$BL" --background --factory-startup --python-exit-code 1 --python tests/blender_023_fase7.py
"$BL" --factory-startup --enable-event-simulate --python-exit-code 1 --python tests/blender_012_library_ui.py
"$BL" --factory-startup --enable-event-simulate --python-exit-code 1 --python tests/blender_biblioteca_detalhe.py

cd tests
PYTHONIOENCODING=utf-8 python -m unittest test_armario_026_parity test_i18n_coverage
cd ..
PYTHONIOENCODING=utf-8 python docs/rag/tools/check_api.py
```

---

## 4. Limites de verificação (não transformar em “passou”)

1. **Sem inspeção visual humana** das telas nesta rodada. O tema é provado por tokens e pelo caminho de desenho.
2. O **popover de medida** foi executado por `EXEC_DEFAULT`; o diálogo nativo não é capturado por screenshot.
3. O **menu de contexto** foi provado pelo `draw`; o clique direito real não foi automatizado.
4. O **arraste** foi provado por eventos sintéticos no modal, não por mouse humano.
5. `blender_023_janela_open.py` imprimiu `OK`, mas o processo não encerrou sozinho e foi interrompido pelo timeout
   de 180 s. Não conte como execução limpa.
6. O **chrome nativo do Blender** segue o tema do Blender; o alternador Light/Dark repinta as áreas desenhadas pelo
   add-on (preview e Biblioteca). Não prometa repintar menus/painéis nativos.
7. O **full ruff** ainda tem 7 achados pré-existentes de outras features. Não os atribua à 026:
   `drawer_detect_core` F401, `panel.py` F841, `panel_window.py` F401 de `ops`, `preview.py` F401 de `bpy`,
   `draw.py` E731 da 073, `models_core.py` F841, `ops_replace.py` F401.

---

## 5. Arquitetura que o próximo agente precisa conhecer

### 5.1 Construtor

- `window.py`: `JanelaSessao` com `vista` (`SPLIT/FRONTAL/LATERAL`), `tema` (`LIGHT/DARK`), `apenas_laterais`,
  `escala_frontal`, `escala_lateral`, `deslocamento_frontal`; `registrar_movimento`, `registrar_duplicata`.
- `preview.py`: `PALETAS`, `aplicar_tema`, `_cor_do_papel` (lê tokens em tempo de desenho), filtro de portas e
  laterais, vista única/dupla, hits e escalas.
- `props.py`: `BTM_PG_ArmarioAjuste.duplicada` (bool, default `False`).
- `build.py`: depois de gerar as peças, recria uma cópia para cada ajuste com `duplicada=True`.
- `ops_window.py`: operadores `..._vista`, `..._tema`, `..._apenas_laterais`, `..._abrir_tudo`, `..._painel`,
  `..._medida`, `..._duplicar`, `..._export_json`; `BTM_MT...Context`; modal com RIGHTMOUSE, MOUSEMOVE e release.
- `panel_window.py`: header (titlebar + abas em linha), toolbar, seleção com Medida/Duplicar, contrato, lista de
  peças com export, rodapé.
- `parity_core.py`: núcleo puro de export/cutlist; schema `caffmob.armario.v1`.

### 5.2 Biblioteca

- `categories_core.py`: `FIXED` (Armários, Armários autorais), `OPENING_CATEGORIES` (Portas, Janelas) e
  `SIDEBAR_FIXED` na ordem do documento; `LINES`/`LINE_LABELS` continuam sendo os ambientes do card.
- `draw.py`: `items()` usa `sidebar_categories()`; “Armários” mostra todo o acervo; Portas/Janelas usam aberturas;
  grade de Blocos com `fixed=2`.
- `grid_core.py`: `columns(width, scale, fixed=0)`, `content_height(..., fixed=0)`,
  `visible_cells(..., fixed=0)`.
- `style.py`: `LIGHT`, `DARK`, `aplicar_tema`, `MIN_TOUCH=44`.
- `props.py`: `btm_library.theme` (`LIGHT`/`DARK`).
- `ops_click.py`: `THEME` alterna o tema; `GRID` usa `fixed=2` em Blocos.
- `layout_core.py`: `BUTTON_KEYS` inclui `THEME`; `_touch` dá o alvo de 44 px.
- `draw_kit.py`: ícone `THEME`.

---

## 6. Regras para o próximo agente

1. **Não reabra a 026** para “melhorar” sem pedido; ela está fechada e auditada.
2. **Não altere** `requirements.md`, `roadmap.md`, `actions.md`, `data-delta.md`, `legacy-impact.md`,
   `regression-watch.md` nem este onboarding durante uma auditoria. O `reversa-audit` só grava
   `audit/cross-check.md`.
3. **Não faça push** sem autorização explícita.
4. **Não commite** `AGENTS.md`, `biblioteca_detalhe.png`, `prompt_025.png`, `docs/Caff+Mob+Biblioteca+Mockup.tar.gz`
   nem `docs/Elicitacao+Requisitos+Caff+Mob+Biblioteca.tar.gz`.
5. **Não use `git add .`**; o `AGENTS.md` tem symlink problemático e o diff global pode falhar.
6. **Consulte o RAG** antes de usar `bpy`, `gpu`, `blf`, `mathutils` ou `bpy_extras`; `check_api.py` é obrigatório.
7. **Toda função nova** precisa de código + prova executada; impossibilidade técnica é bloqueio explícito, não
   “fora de escopo”.
8. Se o pedido for o próximo passo do mockup ou da Biblioteca, crie uma **feature 027** com o ciclo Reversa completo.

---

## 7. Onde está o estado final

| Artefato | Caminho |
|----------|---------|
| Requisitos | `_reversa_forward/026-paridade-total-construtor-biblioteca/requirements.md` |
| Roadmap | `.../roadmap.md` |
| Ações 12/12 | `.../actions.md` |
| Data delta | `.../data-delta.md` |
| Impacto no legado | `.../legacy-impact.md` |
| Regressão | `.../regression-watch.md` |
| Progresso | `.../progress.jsonl` |
| Auditoria 0/0/0/0 | `.../audit/cross-check.md` |
| Feature ativa | `.reversa/active-requirements.json` |
| Commit/tag | `d0c67988` / `v1.35.0` (local, sem push) |

Se outro agente só puder ler um arquivo, leia este; se puder ler dois, leia também o `audit/cross-check.md`.
