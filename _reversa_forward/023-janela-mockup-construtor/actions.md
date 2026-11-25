# Actions: Janela própria do Construtor de Armários igual ao mockup

> Identificador: `023-janela-mockup-construtor`
> Data: `2026-11-24`
> Roadmap: `_reversa_forward/023-janela-mockup-construtor/roadmap.md`

## Resumo

| Métrica | Valor |
|---------|-------|
| Total de ações | 24 |
| Paralelizáveis (`[//]`) | 8 |
| Maior cadeia de dependência | 13 |

## Fase 1, Preparação

Setup, scaffolding, migrações iniciais, configuração de infraestrutura local.

| ID | Descrição | Dependências | Paralelismo | Arquivo alvo | Confidência | Status |
|----|-----------|--------------|-------------|--------------|-------------|--------|
| T001 | Criar scaffolding do módulo `caffmob_draw/armario_v2/window.py` com registro de janela Image Editor sem imagem via `canvas2d.window.open_window` | - | `[//]` | `caffmob_draw/armario_v2/window.py` | 🟡 | `[X]` |
| T002 | Implementar operador de abertura `caffmob.cabinet_editor_window_open` que lança a janela própria e inicia sessão do editor v2 | T001 | - | `caffmob_draw/armario_v2/ops_window.py` | 🟡 | `[X]` |
| T003 | Registrar a janela própria no `__init__.py` do pacote `armario_v2` (entre `customize` e `cabinet_editor`, conforme adendo 017) | T001, T002 | - | `caffmob_draw/armario_v2/__init__.py` | 🟢 | `[X]` |

## Fase 2, Testes

Testes que precisam existir antes ou logo após o núcleo.

| ID | Descrição | Dependências | Paralelismo | Arquivo alvo | Confidência | Status |
|----|-----------|--------------|-------------|--------------|-------------|--------|
| T004 | Criar teste de abertura/fechamento da janela própria (sessão ativa/inativa; roda no Blender `--background`) | T002 | `[//]` | `tests/blender_023_janela_open.py` | 🟡 | `[X]` |

## Fase 3, Núcleo

Lógica central da feature.

| ID | Descrição | Dependências | Paralelismo | Arquivo alvo | Confidência | Status |
|----|-----------|--------------|-------------|--------------|-------------|--------|
| T005 | Implementar preview dividido (frontal + corte lateral) na janela própria, espelhando o armário v2 | T003 | - | `caffmob_draw/armario_v2/window.py` | 🟡 | `[X]` |
| T006 | Implementar painel lateral de 7 abas (Estrutura, Divisões, Gavetas, Internos, Portas, Deslizantes, Fundos) na janela própria | T005 | - | `caffmob_draw/armario_v2/panel_window.py` | 🟡 | `[X]` |
| T007 | Implementar empty state "Janela de Armário Vazia" com botão Montar Caixa | T006 | - | `caffmob_draw/armario_v2/window.py` | 🟡 | `[X]` |
| T008 | Implementar máquina de estado fila + modal UNDO (OK/Aplicar/Cancelar) na janela própria, reaproveitando F-01 a F-03 | T006 | - | `caffmob_draw/armario_v2/ops_window.py` | 🟢 | `[X]` |

## Fase 4, Integração

Cola com outras partes do sistema, contratos externos, ganchos.

| ID | Descrição | Dependências | Paralelismo | Arquivo alvo | Confidência | Status |
|----|-----------|--------------|-------------|--------------|-------------|--------|
| T009 | Conectar ações de construção (laterais, bases, fundo, prateleiras, divisórias, gavetas, internos, portas, deslizantes) ao armário v2 (`Object.btm_armario`) | T008 | - | `caffmob_draw/armario_v2/ops_window.py` | 🟢 | `[X]` |
| T010 | Travar sessão: bloquear abertura de segunda janela do construtor enquanto uma estiver aberta (poll/reflow_handler) | T008 | - | `caffmob_draw/armario_v2/ops_window.py` | 🟢 | `[X]` |

## Fase 5, Polimento

Logs, telemetria, mensagens de erro, documentação curta.

| ID | Descrição | Dependências | Paralelismo | Arquivo alvo | Confidência | Status |
|----|-----------|--------------|-------------|--------------|-------------|--------|
| T011 | Aplicar paleta, espaçamento e ícones pixel-perfeito do mockup na UI da janela | T010 | `[//]` | `caffmob_draw/armario_v2/panel_window.py` | 🟡 | `[X]` |
| T012 | Revisar cobertura dos RF-01 a RF-07 e gerar `regression-watch.md` | T011 | `[//]` | `_reversa_forward/023-janela-mockup-construtor/regression-watch.md` | 🟢 | `[X]` |

## Fase 6, Correção da auditoria de 2026-11-25

O que a sonda mediu como divergente de D-01/RF-01 e o que foi corrigido. A paridade pixel a pixel não entra aqui:
é decisão do titular (T018).

| ID | Descrição | Dependências | Paralelismo | Arquivo alvo | Confidência | Status |
|----|-----------|--------------|-------------|--------------|-------------|--------|
| T013 | Abrir a janela por `canvas2d.window.open_window` (janela nova, sem trocar a Vista 3D do usuário) e focar a categoria do construtor | T002 | - | `caffmob_draw/armario_v2/window.py` | 🟢 | `[X]` |
| T014 | Dar entrada de interface ao operador: botão "Abrir Janela" no painel da Vista 3D e na conversão | T013 | `[//]` | `caffmob_draw/armario_v2/panel.py` | 🟢 | `[X]` |
| T015 | Modal dentro da janela nova: seleção por clique no preview, alternadores de Cotas/Portas, aviso ao fechar pelo sistema e gate GEO em OK/Aplicar | T013 | `[//]` | `caffmob_draw/armario_v2/ops_window.py` | 🟢 | `[X]` |
| T016 | Preview: largura visível, deslocamento da vista frontal, ordem de pintura (FUNDO primeiro) e registro dos hits | T013 | - | `caffmob_draw/armario_v2/preview.py` | 🟢 | `[X]` |
| T017 | Núcleos puros de seleção e de GEO-001/GEO-002 com ensaios próprios | T015 | `[//]` | `caffmob_draw/armario_v2/selecao.py`, `validar.py`, `tests/test_janela_023_core.py` | 🟢 | `[X]` |
| T018 | Decidir a paridade visual: réplica pixel a pixel (desenho da janela em GPU) ou paridade funcional com o chrome do Blender | T016 | - | `_reversa_forward/023-janela-mockup-construtor/requirements.md` | 🟢 | `[X]` (decidido: híbrida, D-05) |

## Fase 7, Escopo decidido no clarify de 2026-11-25

| ID | Descrição | Dependências | Paralelismo | Arquivo alvo | Confidência | Status |
|----|-----------|--------------|-------------|--------------|-------------|--------|
| T019 | Fila + modal UNDO: painéis enfileiram, `processar_fila` aplica com um único passo de desfazer; remover chamadas diretas | T015 | - | `caffmob_draw/armario_v2/panel_window.py`, `ops_window.py`, `fila.py` | 🟢 | `[X]` (botão só enfileira; modal processa; ensaio `blender_023_fase7`) |
| T020 | Seleção múltipla (Shift/Ctrl+clique) e ações em lote mover/apagar/espelhar num passo de desfazer, **sobrevivendo ao Gerar** | T015 | - | `caffmob_draw/armario_v2/selecao.py`, `ops_window.py`, `window.py`, `build.py`, `props.py` | 🟢 | `[X]` (lote grava `Armário.ajustes` e o Gerar reaplica; 6 ensaios puros + 17 no Blender, incluindo regerar) |
| T021 | Persistir por cena a última aba e o último tamanho da janela (padrão 1009×831, Estrutura) | T013 | `[//]` | `caffmob_draw/armario_v2/window.py` | 🟢 | `[X]` com limitação: aba restaurada e tamanho **registrado**, mas `Window.width/height` são readonly no Blender 5.2 — não há como aplicar o tamanho |
| T022 | Aplicar paleta, espaçamento e ícones do mockup onde a UI do Blender permitir (sem titlebar/abas horizontais) | T017 | `[//]` | `caffmob_draw/armario_v2/panel_window.py`, `preview.py` | 🟢 | `[X]` (barra de abas 4+3 com aba ativa, barras de título/seleção/lote, espaçamento e ícones; paleta do preview já era do mockup) |
| T023 | Sonda de desempenho: abrir < 2 s e preview < 200 ms por interação, com o armário montado | T022 | - | `tests/blender_023_desempenho.py` | 🟢 | `[X]` (abrir 127,5 ms na sessão gráfica; preview 0,4 ms máx. com 54 peças; sonda `--background` com assert da meta) |
| T024 | Regressão final (pura + Blender) e atualização de onboarding/regression-watch para o escopo novo | T019, T020, T021, T022, T023 | - | `_reversa_forward/023-janela-mockup-construtor/onboarding.md` | 🟢 | `[X]` (pura 1600 com só a falha POSIX/NTFS; 017/021/023 verdes) |

## Notas de execução

<!--
Reservado para /reversa-coding registrar avisos ou observações que surgiram durante a execução.
Não use isso para corrigir ações, edits manuais ficam fora desse arquivo, vão direto no código.
-->

## Histórico de alterações

| Data | Alteração | Autor |
|------|-----------|-------|
| 2026-11-24 | Versão inicial gerada por `/reversa-to-do` | reversa |
| 2026-11-25 | Fase 6 acrescentada pela correção da auditoria; T004 aponta para o ensaio Blender; T018 aberta (decisão do clarify) | reversa |
| 2026-11-25 | T018 fechada (paridade híbrida) e Fase 7 aberta com o escopo decidido no clarify (T019–T024) | reversa |
| 2026-11-25 | Fase 7 executada: T019–T024 `[X]`; T021 com a limitação de plataforma no tamanho da janela | reversa |
| 2026-11-25 | T020 reforçada: edições em lote passam a sobreviver ao Gerar (coleção `ajustes` + reaplicação no `build.gerar`) | reversa |
| 2026-11-25 | T020: pivô do espelho no centro do módulo (porta/ferragem fora do centro); contador e ação "Limpar ajustes manuais" com regeneração | reversa |
| 2026-11-25 | T024: menu de contexto ganhou "Abrir janela do construtor" no armário (antes só peça animável/divisão desenhava itens) | reversa |
