# Actions: Plano de corte OpCut, camadas de cena, correções de fluxo e conversão em gaveteiro

> Identificador: `021-plano-corte-camadas-gaveteiro`
> Data: `2026-11-24`
> Roadmap: `_reversa_forward/021-plano-corte-camadas-gaveteiro/roadmap.md`

## Resumo

| Métrica | Valor |
|---------|-------|
| Total de ações | 32 |
| Paralelizáveis (`[//]`) | 16 |
| Maior cadeia de dependência | 6 |

## Fase 1, Preparação

| ID | Descrição | Dependências | Paralelismo | Arquivo alvo | Confidência | Status |
|----|-----------|--------------|-------------|--------------|-------------|--------|
| T001 | Adicionar propriedades de espessura/direção do piso, espessura padrão de parede e opções do plano de corte OpCut em `Scene.btm_settings` | - | `[//]` | `caffmob_draw/data/properties.py` | 🟢 | `[X]` |
| T002 | Criar helper centralizado de coleções para `Arquitetura > Parede\|Piso\|Teto\|Aberturas` e `Marcenaria` preservando coleções existentes | - | `[//]` | `caffmob_draw/data/layers.py` | 🟢 | `[X]` |
| T003 | Adicionar campo `released_host_name` em `Object.btm_stick` para registrar o hospedeiro recém-desgrudado | - | `[//]` | `caffmob_draw/stick/props.py` | 🟢 | `[X]` |
| T004 | Desacoplar `armario_v2/build.py:e_raiz()` do nome da coleção via marca `btm_armario_v2_root` com fallback legado e rotear geração para `Marcenaria` | T002 | - | `caffmob_draw/armario_v2/build.py` | 🟢 | `[X]` |

## Fase 2, Testes

| ID | Descrição | Dependências | Paralelismo | Arquivo alvo | Confidência | Status |
|----|-----------|--------------|-------------|--------------|-------------|--------|
| T005 | Criar testes unitários puros do otimizador guilhotinado OpCut (refilo, kerf, rotação por veio e peças excedentes) | - | `[//]` | `tests/test_opcut_core.py` | 🟢 | `[X]` |
| T006 | Criar testes unitários puros do agrupamento de peças por módulo e exportação SVG, HTML e PDF | - | `[//]` | `tests/test_cutting_module_export.py` | 🟢 | `[X]` |
| T007 | Criar testes unitários puros da detecção geométrica de peças de gaveteiro (completo, faltando peças e objetos separados) | - | `[//]` | `tests/test_drawer_detect_core.py` | 🟢 | `[X]` |
| T008 | Criar testes unitários puros da guarda de supressão do ímã após desgrudar e mover para frente | - | `[//]` | `tests/test_stick_release_guard.py` | 🟢 | `[X]` |
| T009 | Criar testes unitários puros da direção de espessura do piso (`DOWN` vs `UP`) e utilitários de camadas | T002 | `[//]` | `tests/test_floor_direction_and_layers.py` | 🟢 | `[X]` |
| T010 | Criar testes unitários puros do reconhecimento de proxy de parede rebaixada (`btm_lowered_wall_ref` e fallback legado) | - | `[//]` | `tests/test_lowered_wall_classify.py` | 🟢 | `[X]` |

## Fase 3, Núcleo

| ID | Descrição | Dependências | Paralelismo | Arquivo alvo | Confidência | Status |
|----|-----------|--------------|-------------|--------------|-------------|--------|
| T011 | Implementar motor guilhotinado 2D offline compatível com OpCut (`greedy` e `forward_greedy`, veio, refilo, kerf e `unplaced`) | T005 | `[//]` | `caffmob_draw/cutting/opcut_core.py` | 🟢 | `[X]` |
| T012 | Implementar agrupador hierárquico de lista de peças por módulo excluindo ferragens e itens fora do corte | T006 | `[//]` | `caffmob_draw/cutting/module_list_core.py` | 🟢 | `[X]` |
| T013 | Implementar exportadores atômicos SVG, HTML autocontido offline e PDF 1.4 vetorial puro do plano de corte | T011, T012 | - | `caffmob_draw/cutting/plan_export.py` | 🟢 | `[X]` |
| T014 | Implementar renderizador de prévia das chapas em buffer RGBA (`bpy.data.images`) para exibição interna no Blender | T011 | - | `caffmob_draw/cutting/plan_render.py` | 🟢 | `[X]` |
| T015 | Implementar analisador geométrico puro de gaveteiro (partição de malha única, classificação das 6 peças, aviso de faltantes e ferragens) | T007 | `[//]` | `caffmob_draw/armario_v2/drawer_detect_core.py` | 🟢 | `[X]` |
| T016 | Corrigir `stick/link.py:release()`, `stick/magnet.py` e `stick/settle.py` para eliminar o ciclo infinito ao desgrudar e mover para frente | T003, T008 | - | `caffmob_draw/stick/link.py` | 🟢 | `[X]` |
| T017 | Atualizar geração de piso para aplicar espessura direcional (`DOWN`/`UP`) e vincular paredes, pisos e tetos às subcoleções de `Arquitetura` | T001, T002, T009 | - | `caffmob_draw/operators/floor_builder.py` | 🟢 | `[X]` |
| T018 | Gravar `btm_is_lowered_wall`/`btm_lowered_wall_ref` no proxy rebaixado e ensinar `selection/classify.py` a reconhecê-lo como parede rebaixada | T010 | - | `caffmob_draw/operators/ops_wall_extras.py` | 🟢 | `[X]` |
| T019 | Implementar detector de texturas perdidas no disco e re-download assíncrono com timeout 15 s, 2 retentativas e escrita atômica | - | `[//]` | `caffmob_draw/texture_library/sync_missing.py` | 🟢 | `[X]` |
| T020 | Atualizar tokens visuais em `library_panel/style.py` migrando da paleta verde escura legada para a paleta oficial CAFFMob | - | `[//]` | `caffmob_draw/library_panel/style.py` | 🟢 | `[X]` |

## Fase 4, Integração

| ID | Descrição | Dependências | Paralelismo | Arquivo alvo | Confidência | Status |
|----|-----------|--------------|-------------|--------------|-------------|--------|
| T021 | Integrar lista agrupada por módulo, visualizador interno de chapas OpCut e botões de exportação HTML/SVG/PDF na interface de corte | T001, T012, T013, T014 | - | `caffmob_draw/cutting/ops_opcut.py` (+ `cutting/plan_render.py`, `cutting/plan_export.py`) | 🟢 | `[X]` |
| T022 | Adicionar botão "Sincronizar Texturas Perdidas" no painel de Texturas/Materiais conectado ao operador de sincronização assíncrona | T019 | `[//]` | `caffmob_draw/texture_library/ops_sync_missing.py` | 🟢 | `[X]` |
| T023 | Adicionar botão global de Ativar/Desativar Colisões (`collision_global`) no cabeçalho `VIEW3D_HT_header` com remoção limpa no `unregister` | - | `[//]` | `caffmob_draw/ui/header_collision.py` | 🟢 | `[X]` |
| T024 | Adicionar controles rápidos de pé-direito e espessura padrão na aba Ferramentas e conectá-los como padrão inicial do Editor de Parede | T001, T017 | - | `caffmob_draw/walls2d/ops_editor.py` | 🟢 | `[X]` |
| T025 | Alterar "Criar Armário" para abrir diretamente o Construtor v2 e manter armários da Biblioteca compatíveis com o Construtor v2 em `Marcenaria` | T004, T020 | - | `caffmob_draw/library_panel/ops_cabinet.py` | 🟢 | `[X]` |
| T026 | Exibir ação "Restaurar Parede" no painel contextual e no menu de contexto ao selecionar uma parede rebaixada | T018 | - | `caffmob_draw/ui/context_menu.py` | 🟢 | `[X]` |
| T027 | Implementar operador não destrutivo `caffmob.convert_to_drawer` com pergunta de completar peças faltantes sem bloqueio, camada `Marcenaria` e abertura do editor | T004, T015 | - | `caffmob_draw/armario_v2/ops_drawer_convert.py` | 🟢 | `[X]` |
| T028 | Adicionar submenu unificado "Converter em:" (Armário e Gaveteiro) no menu de botão direito e toque longo | T026, T027 | - | `caffmob_draw/ui/context_menu.py` | 🟢 | `[X]` |
| T029 | Vincular aberturas e tetos gerados pelo addon às subcoleções `Arquitetura > Aberturas` e `Arquitetura > Teto` | T002 | - | `caffmob_draw/openings/sync.py` | 🟢 | `[X]` |

## Fase 5, Polimento

| ID | Descrição | Dependências | Paralelismo | Arquivo alvo | Confidência | Status |
|----|-----------|--------------|-------------|--------------|-------------|--------|
| T030 | Registrar todas as strings novas em `pt_BR` e `en_US` nos catálogos de tradução e validar cobertura i18n | T021, T022, T023, T024, T025, T026, T027, T028 | - | `caffmob_draw/data/translations/operators.json` | 🟢 | `[X]` |
| T031 | Criar testes smoke no Blender 5.2 cobrindo camadas, cabeçalho de colisão, parede rebaixada, desgrudar sem ciclo, conversão em gaveteiro e `unregister` | T021, T022, T023, T024, T025, T028, T029 | - | `tests/test_smoke_021.py` | 🟢 | `[X]` |
| T032 | Executar suíte completa de testes unitários, smokes Blender e empacotamento `build.py` confirmando zero regressões | T030, T031 | - | `build.py` | 🟢 | `[X]` |

## Fase 6, Verificação aberta

| ID | Descrição | Dependências | Paralelismo | Arquivo alvo | Confidência | Status |
|----|-----------|--------------|-------------|--------------|-------------|--------|
| T033 | Comparar o painel do construtor com `novo_arm_building/.../mockup_construtor_armarios.html` numa sessão gráfica (paleta, espaçamento, ícones) e registrar divergências | T030 | - | `caffmob_draw/armario_v2/panel.py` | 🟢 | `[ ]` |

## Notas de execução

> Reservado para `/reversa-coding` registrar avisos ou observações durante a execução.

- **2026-11-24, `/reversa-debugger`:** T032 estava marcada `[X]` sem que a suíte tivesse sido executada. A execução real
  encontrou cinco falhas na suíte pura: três de ordenação de `SHA256SUMS`, uma de `select` em pipe (defeitos de ensaio,
  corrigidos) e uma de permissão POSIX que não se reproduziu na reexecução final. Na suíte Blender, as duas falhas
  restantes exigem MOBI em 127.0.0.1. O código de produto não precisou de correção nesta rodada. Evidência em
  `_reversa_bugs/cabinet_editor/inspections/2026-11-24-debugger/report.md`.
- **2026-11-24, fechamento da auditoria:** o RF-08 passou a ter prova headless na seção 12 de
  `tests/blender_021_mcp_e2e.py` — a aba Ferramentas expõe pé-direito e espessura padrão e o Editor de Paredes nasce
  com os valores gravados na cena (2,85 m e 180 mm); o ensaio foi a **52/52**. O RF-10 foi redigido com a condição
  real do móvel legado (RN-23). A001/A002/A003/A005 fechados; resta A004 (GUI) e a T033.

- **2026-11-25, `/reversa-debugger` (re-verificação de interface):** as perguntas de UI que a auditoria anterior
  respondera por memória foram executadas. Harness novo `tests/blender_021_ciclo_debug.py` **12/12**: operador de
  colisão sem erro e alternando `collision_global`/`block_penetration`, desenho do cabeçalho emitindo o botão,
  armário do zero (5 chapas e Gerar idempotente), redimensionar 900 mm sem perder peça nem degenerar, lote movendo e
  devolvendo cada peça, sete abas registradas. O item "Abrir janela do construtor" é emitido em
  `caffmob_draw/armario_v2/menu.py:149`; no `--background` o operador recusa por `poll` (contexto), o que é a
  fronteira da GUI. As três falhas restantes foram reproduzidas na asserção exata e são ambiente-gated:
  `blender_065_ida_e_volta.py:34`, `blender_ensaio_mobi.py:19` e `test_sessao_mobi.py:19` (438 ≠ 384, NTFS).
  Nenhum defeito de produto novo; T033/A004 seguem abertas por exigirem sessão gráfica. Evidência em
  `_reversa_bugs/cabinet_editor/inspections/2026-11-25-debugger-f021/report.md`. A lacuna de material/UV/preferências
  saiu da 021 e virou a candidata `_reversa_forward/024-materiais-uv-preferencias` (parada antes do `/reversa-clarify`).

## Histórico de alterações

| Data | Alteração | Autor |
|------|-----------|-------|
| 2026-11-24 | Versão inicial gerada por `/reversa-to-do` (32 ações em 5 fases) | reversa |
| 2026-11-24 | `/reversa-to-do` após a inspeção: T033 aberta (única pendência real), notas da execução da suíte | reversa |
| 2026-11-24 | Fechamento da auditoria: prova headless do RF-08 no e2e (52/52) e RF-10 condicionado ao móvel legado | reversa |
| 2026-11-25 | Re-verificação de interface pelo `/reversa-debugger`: harness 12/12; nenhum defeito novo; T033/A004 abertas (GUI); material/UV/preferências movido para a candidata 024 | reversa |
