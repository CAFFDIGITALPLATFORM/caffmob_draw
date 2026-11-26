# Cross-check: Criação direta, posicionamento e galeria clara do armário v2

> Data: `2026-11-26`
> Feature: `_reversa_forward/025-criacao-posicionamento-armario`
> Artefatos analisados: [`requirements.md`](../requirements.md) · [`roadmap.md`](../roadmap.md) · [`actions.md`](../actions.md)
> Apoio: [`data-delta.md`](../data-delta.md) · [`legacy-impact.md`](../legacy-impact.md) · [`regression-watch.md`](../regression-watch.md)
> Mockup: `novo_arm_building/.../mockup_construtor_armarios.html`
> Galeria: `docs/Caff+Mob+Biblioteca+Mockup.tar.gz` e `docs/Elicitacao+Requisitos+Caff+Mob+Biblioteca.tar.gz`
>
> **Este relatório é só de leitura.** Nenhum dos três artefatos foi alterado por esta auditoria.

## 1. Resumo

| Severidade | Quantidade |
|------------|-----------|
| CRITICAL | 0 |
| HIGH | 0 |
| MEDIUM | 0 |
| LOW | 0 |
| **Total** | **0** |

O fluxo pedido está coberto de ponta a ponta: **Criar armário** na Vista 3D, **Aplicar** perguntando
**Escolher/Cursor 3D**, a **caixa de arame** com mouse/setas/clique/Esc, o **Cursor 3D** e a **galeria Light**.
Cada RF tem decisão e ação; cada decisão tem ação; cada cenário Gherkin tem prova ou ação correspondente.

## 2. Achados

| ID | Severidade | Eixo | Descrição | Onde está |
|----|------------|------|-----------|-----------|
| — | — | — | Nenhuma inconsistência encontrada entre requirements, roadmap e actions | — |

Não há CRITICAL nem HIGH para explicar em §3.

## 3. Cobertura

### 3.1 RF → decisão → ação

| RF | Requisito | Decisão | Ação | Prova |
|----|-----------|---------|------|-------|
| RF-01 | Criar armário abre a viewport sem janela nova | D-01 | T007 | `blender_025_place`: `{'FINISHED'}`, 1 janela |
| RF-02 | Aplicar pergunta com dois caminhos | D-02, D-03 | T002, T003, T004, T007 | gancho chamado; popup com os dois operadores |
| RF-03 | Caixa de arame acompanha o mouse | D-04, D-05, D-06 | T001, T002, T007 | 8 vértices, 12 arestas, 0 faces, `WIRE`; mouse no piso |
| RF-04 | Setas cardeais e R | D-07 | T001, T002, T007 | `RIGHT_ARROW` → 90° |
| RF-05 | Clique confirma; Esc/botão direito restauram | D-08 | T002, T007 | clique remove a caixa; Esc restaura loc/rot/hide |
| RF-06 | Cursor 3D posiciona a raiz | D-04, D-09 | T001, T002, T007 | raiz em (1,2, −0,8, 0); peça filha acompanha |
| RF-07 | Sem viewport cai no Cursor 3D | D-09 | T002, T006, T007 | `EXEC_DEFAULT` FINISHED |
| RF-08 | Galeria na paleta Light | D-10 | T008, T009 | tokens + card 38/38 + UI 9/9 |
| RF-09 | Provas, i18n e versão | D-11 | T006, T007, T012, T013 | 7/7, 16/16, 3/3 i18n, 1.34.0 |

### 3.2 Cenários Gherkin

| Cenário | Coberto por |
|---------|-------------|
| Criar armário abre a viewport direto | T007 |
| Aplicar pergunta onde adicionar | T003/T004/T007 |
| Escolher mostra a caixa e acompanha o mouse | T001/T002/T007 |
| Setas mudam a orientação e o clique confirma | T001/T007 |
| Esc cancela e restaura | T002/T007 |
| Cursor 3D posiciona o armário | T001/T007 |
| Aplicar na janela 023 também pergunta | T004 (código) + T007 (gancho do Aplicar do painel) |
| Galeria na paleta clara | T008/T009 + card/UI |

### 3.3 Roadmap → ações

D-01 → T007; D-02 → T003/T004; D-03 → T002; D-04 → T001; D-05 → T001/T002; D-06 → T001/T002;
D-07 → T001/T002; D-08 → T002; D-09 → T002/T006; D-10 → T008/T009; D-11 → T006/T007/T012/T013.
Não há decisão órfã nem ação sem decisão.

## 4. Consistência

- **Termos:** “Escolher na viewport” é o rótulo do popup; “Escolher” é a forma curta no texto. “Cursor 3D” é usado
  igual em requirements, roadmap, actions e UI. “Caixa de arame” é o mesmo objeto em todos os três documentos.
- **Identificadores:** RN-01..RN-09, RF-01..RF-09, D-01..D-11 e T001..T013 existem e são referenciados.
- **Contratos:** não há `interfaces/` novo; `abrir_prompt` é chamada Python local, documentada em D-02/D-03.
- **Dados:** `data-delta.md` diz “nenhum campo persistente novo” e o roadmap §6/requirements RN-03..RN-06 batem:
  loc/rot/hide já existentes; estado do modal é transitório.
- **i18n:** 28 chaves novas foram acrescentadas em `armario_v2.json` e `library.json`; `test_i18n_coverage` 3/3.

## 5. Coerência com o legado

- **D-01** usa o caminho já existente `caffmob.cabinet_editor`/`BTM_OT_ArmarioV2Abrir`; não contradiz a 023, que
  mantém **Abrir Janela** como entrada separada.
- **D-04** move a **raiz** do agregado; é a hierarquia documentada em `build.py` (raiz EMPTY + filhas com
  `matrix_parent_inverse = Identity`), não uma reposição peça a peça.
- **D-02/D-03** preservam o Aplicar como passo de desfazer e só perguntam depois; nenhuma regra 🟢 do legado é
  contrariada.
- **D-10** só troca tokens de aparência; abas, busca, categorias, grade 2×3, seleção e filtros continuam.
- A fronteira da paridade do mockup está declarada em RN-09/§10 e é a decisão **D-05** da 023 (híbrida), cujo
  `cross-check.md` tem 0 HIGH depois da Fase 7.

## 6. Sanidade do actions

- Todas as dependências apontam para IDs existentes: T002→T001; T003/T004→T002; T005→T003/T004; T006→T001/T002;
  T007→T005; T009→T008; T010→T007/T009; T011→T010; T012→T011; T013→T012.
- Paralelismo: T001, T003, T004, T006, T007 e T008 usam `[//]`; os pares T003/T004, T006/T007 e T008/T009 não
  compartilham arquivo alvo.
- Não há ciclo: a cadeia mais longa é T001 → T002 → T003/T004 → T005 → T007 → T010 → T011 → T012 → T013 (9 nós,
  contando as junções), sem retorno.
- Todas as 13 ações estão `[X]`; T013 fecha versão/tag.

## 7. Evidências executadas nesta rodada

| Prova | Resultado |
|-------|-----------|
| `tests/test_placement_025.py` + `tests/test_library_style_025.py` | **7/7** |
| `tests/blender_025_place.py` (janela real) | **16/16** — Criar armário sem janela nova, gancho do Aplicar, Cursor 3D, caixa, mouse, seta, clique e Esc |
| `tests/blender_biblioteca_detalhe.py` | **38/38** |
| `tests/blender_012_library_ui.py` | **9/9** |
| `test_library_detail`, `test_library_environments`, `test_library_grid`, `test_library_layout` | **36/36** |
| Puros amplos (017, 023, 024, 025) | **54/54** |
| `test_i18n_coverage` | **3/3** (28 chaves novas) |
| `tests/blender_017_armario_smoke.py` | **OK** |
| `docs/rag/tools/check_api.py` | **637 arquivos, nenhuma API desconhecida** |
| `ruff check` nos arquivos novos | **limpo** |

A falha de i18n apareceu na primeira passada larga (`28` textos sem tradução, incluindo 16 do fluxo novo e 12 da
Biblioteca) e foi corrigida **antes** desta auditoria; não é um achado aberto.

## 8. Paridade do mockup do Construtor — nota de escopo

Esta auditoria **não** declara paridade visual/funcional integral com o HTML do mockup. A decisão vigente é a
**D-05 da 023 (híbrida)**, registrada no `cross-check.md` da 023 com **0 HIGH** depois da Fase 7. O que a 025 entrega
e prova é o fluxo explicitamente pedido nesta rodada:

- criar armário na viewport;
- Aplicar → Escolher/Cursor 3D;
- prévia em linhas com mouse, setas, clique e cancelamento;
- Cursor 3D;
- galeria na paleta Light do pacote de requisitos.

Continuam **fora da 025** (e são escopo da 023 ou de uma feature nova, se o titular quiser reabrir): toolbar completa
do mockup (views, export JSON, tema, painel lateral, abrir/fechar tudo), menu de contexto da janela 023, popover de
medida, arraste de peças, grade da matriz, “Apenas Laterais”, contrato de chapas na janela 023, cutlist modal e
alternador Light/Dark. A galeria mantém as categorias atuais (Cozinha/Dormitório/etc.); a mudança para
Armários/Portas/Janelas/Armários autorais é conteúdo, não aparência, e não foi pedida nesta rodada.

## 9. Limitações

- O `screen.screenshot` do Blender **não captura popups**. O ensaio prova que o gancho é chamado e que o operador
  retorna `RUNNING_MODAL`; o desenho do popup em si fica para a conferência humana descrita no `onboarding.md`.
- O clique real do mouse no popup e a sensação do arraste da caixa não foram exercitados por um humano nesta rodada;
  o ensaio usa eventos sintéticos.
- O Aplicar da janela 023 foi coberto por leitura de código e pelo gancho do Aplicar do painel; não houve clique
  humano no rodapé da janela 023 nesta rodada.
- A paridade integral do mockup é a decisão híbrida da 023; não é uma promessa desta feature.
- O `ruff` passa nos arquivos novos e nos demais alterados; `library_panel/draw.py` ainda tem um `E731` antigo da 073
  (lambda atribuído), não introduzido por esta feature e não corrigido aqui para não misturar escopos.

## 10. Aviso

Esta auditoria não alterou `requirements.md`, `roadmap.md`, `actions.md`, `data-delta.md`, `legacy-impact.md`,
`regression-watch.md`, `onboarding.md` nem qualquer arquivo de código. A única escrita é este `cross-check.md`.
