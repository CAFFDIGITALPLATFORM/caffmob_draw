# Editor de Armário (cabinet_editor) — Requisitos

🟢 **CONFIRMADO** — contrato extraído de `caffmob_draw/cabinet_editor/` (34 arquivos `.py`, 5.443 linhas, 47 miniaturas) em 2026-10-10. A pasta não tem alterações sem commit (`git diff HEAD -- caffmob_draw/cabinet_editor` vazio; último commit `83a6863`). Confirmação de código não implica validação visual no Blender. 🟡 identifica prioridade ou intenção inferida; 🔴 identifica lacuna. Contratos de outras units são citados, não redescritos: janela, vista, primitivas de desenho em `_reversa_sdd/canvas2d/`; histórico `History` em `_reversa_sdd/walls2d/` (design §Núcleo auxiliar); adaptadores por biblioteca, `spec`, `reapply`, `common.call` em `_reversa_sdd/customize/`; `classify`/`editing` em `_reversa_sdd/selection/`; `obb` em `_reversa_sdd/collision/`; `local_box` em `_reversa_sdd/stick/`; grupos `FRAME`/`LEAF` e `make_leaf` em `_reversa_sdd/aggregates/`.

## Visão Geral

🟢 Janela própria com a **vista frontal** (x, z) de um módulo de armário e um painel lateral de 7 abas no modelo do Construtor do Promob (Estrutura, Divisões, Gavetas, Internos, Portas, Deslizantes, Fundos). Diferente do Editor de Paredes, o módulo é editado **ao vivo** na cena: cada botão só enfileira um pedido na sessão e um único operador modal com `UNDO` executa a fila. O rascunho é uma pilha de instantâneos `EditorState` (desfazer/refazer dentro do editor); **OK** fecha mantendo (um passo de desfazer do Blender), **Aplicar** grava um passo sem fechar e vira o novo ponto de retorno, **Cancelar** reaplica o instantâneo de retorno. Fontes: `__init__.py`, `ops_editor.py` (docstring), `state.py`, ADR 0004.

## Responsabilidades

- 🟢 Núcleos puros sem `bpy`: rascunho e assinatura (`state.py`), validação com códigos (`validate.py`), vista frontal e diff (`elevation.py`), componentes externos e caixa do módulo `btm` (`structure.py`), subvãos e divisões (`divisions.py`), catálogo do Construtor (`catalog.py`), geometria de extras, vãos, deslizantes, internos e cotas (`extras.py`, `bays.py`, `slides.py`, `appliances.py`, `position.py`).
- 🟢 Dados gravados no módulo: `Object.btm_structure`, `Object.btm_division`, `Object.btm_extra` (`data_props.py`).
- 🟢 Sessão única em memória e campos do painel `WindowManager.btm_cabinet_editor`, quase todos virtuais (`props.py`).
- 🟢 Ponte com a cena: ler instantâneo, levar o módulo a um instantâneo, 23 ações de edição, caixas das peças para a vista (`bridge.py`).
- 🟢 Peças próprias como filhos diretos da raiz, fora do que as bibliotecas reconstroem: divisões, extras, internos, deslizantes (`scene_divisions.py`, `scene_parts.py`, `scene_extras.py`, `scene_interiors.py`, `scene_slides.py`).
- 🟢 Reposicionar divisões quando o módulo muda fora do editor (`reflow_handler.py`).
- 🟢 Abrir, modal, OK/Cancelar/Fechar/Aplicar e botões que só enfileiram (`ops_editor.py`, `ops_actions.py`); janela e desenho `POST_PIXEL` (`window.py`); miniaturas (`previews.py`); 17 painéis (`panels*.py`).
- 🟢 Fora da responsabilidade: abrir/fechar janela, `View2D`, primitivas GPU (`canvas2d`); reconstrução de cada biblioteca, frentes, interior, remoção de chapas por biblioteca (`customize/adapters/*`); medidas do módulo (`selection/editing`); salvar módulo (`caffmob.module_save`, `customize`); comportamento de folha de correr (`aggregates/leaf`); lista de corte e furação (`cutting`).

## Regras de Negócio

| ID | Regra confirmada | Fonte |
|---|---|---|
| RN-01 | 🟢 Toda mudança dos botões e campos virtuais vira `Session.push(tipo, dados)`; só o modal `caffmob.cabinet_editor_modal` (`UNDO`) altera a cena, em `process`. Botões não têm `UNDO`. Exceções que escrevem direto na cena estão em EC-03. | ops_actions.py (docstring); props.py:_dim_set/_tree_set/_comp_set/_bays_set/_pos_set; ops_editor.py:process |
| RN-02 | 🟢 Um editor por vez: abrir exige `context.window`, nenhuma sessão ativa e objeto ativo pertencente a um módulo com adaptador (`customize.adapters.for_object`); senão `poll` falso ("Selecione um módulo"). Abre sempre na aba Estrutura. | ops_editor.py:BTM_OT_CabinetEditor.poll/module_root/start_session |
| RN-03 | 🟢 Instantâneo `EditorState` = medidas (L, A, P) + `spec` da 003 com `_raw` (campos crus de `btm_custom`) + estrutura + divisões cruas + extras + deslizantes + internos + fundo. Assinatura = JSON ordenado com floats a 6 casas (1 µm); rascunho "sujo" = assinatura atual ≠ de retorno. A montagem (`btm_cabinet.assembly`) **não** entra. | state.py:EditorState/signature/Draft.dirty; bridge.py:read_state |
| RN-04 | 🟢 Cada pedido executado chama `refresh`, que grava um passo no histórico só se a assinatura mudou (`History.checkpoint`, limite 100 de `walls2d/history`). Desfazer/refazer devolve um instantâneo que `bridge.apply_state` reaplica, sem gravar passo. | ops_editor.py:refresh/process; state.py:Draft |
| RN-05 | 🟢 Aplicar exige rascunho sujo e nenhum erro: `bpy.ops.ed.undo_push("Editor de armário: Aplicar")`, o atual vira o instantâneo de retorno, o histórico recomeça, `initial_parts` = peças atuais, `edited` limpo, `applied = True`. | ops_editor.py:_apply_now; state.py:Draft.apply_point; ops_actions.py:BTM_OT_CabinetEditorApply.poll |
| RN-06 | 🟢 OK (`request='ok'`) encerra mantendo a cena e devolve `FINISHED` com "Armário atualizado: {raiz}". Cancelar, janela fechada ou cancelamento do modal pelo Blender reaplicam o instantâneo de retorno (só se sujo) e devolvem `CANCELLED`; raiz apagada encerra com WARNING "O módulo não existe mais; o editor foi fechado" e `CANCELLED`, sem rollback (`rollback` exige `s.root()`) _(Revisão 2026-10-10: ops_editor.py:275-279 rollback só com raiz; modal 379-382)_; janela fechada com alterações mostra o aviso "Editor fechado: alterações descartadas". | ops_editor.py:BTM_OT_CabinetEditorModal.modal/_end/cancel; rollback |
| RN-07 | 🟢 Só mensagem `ERROR` bloqueia OK, Aplicar e "Confirmar" do Fechar; `WARNING`/`INFO` não. | validate.py:Message.blocks; ops_editor.py:BTM_OT_CabinetEditorConfirm.poll/BTM_OT_CabinetEditorClose.execute |
| RN-08 | 🟢 Faixa das medidas: geral largura 0,01–10 m, altura 0,01–10 m, profundidade 0,005–10 m, estreitada campo a campo pela `hard_min`/`hard_max` da propriedade da biblioteca (`face_frame_cabinet`, `hb_closet_starter`, `btm_cabinet`; mínimo nunca < 0). Fora (folga 1e−9) → `DIM-003` (erro) guardado por campo; a medida não é aplicada até um valor válido ou desfazer/refazer. | validate.py:DEFAULT_LIMITS/limits_for/check_dimension; bridge.py:library_limits; ops_editor.py:process |
| RN-09 | 🟢 `GEO-001`: peça (exceto vão e agregado) que passa da largura ou da altura do módulo mais de 1 mm; erro em prateleira/divisória, aviso no resto. A profundidade é livre (puxador). `GEO-002`: pares de prateleiras/divisórias sobrepostos > 1 mm (OBB com eixos identidade) → erro. | validate.py:outside_volume/internal_overlaps |
| RN-10 | 🟢 Ajustes automáticos = `elevation.diff(initial_parts, parts, targets=edited)`: `ADDED`, `REMOVED`, `RESIZED` (tamanho difere > 0,1 mm), `MOVED` (canto mínimo difere > 0,1 mm), ordenados por nome, sem as peças que o usuário editou. | elevation.py:diff; ops_editor.py:refresh |
| RN-11 | 🟢 Componentes externos (`TOP`, `BOTTOM`, `BACK`, `LEFT`, `RIGHT`) removíveis em `KEEP` (só a chapa sai), `EXTEND` (vizinhas avançam; vão cresce) ou `SHRINK` (medida externa diminui; vão igual). Modo que a biblioteca não faz cai em `KEEP` com o motivo como aviso `LIB-001`. Espessura própria 3–60 mm ou 0 (= Configurador); fora → `STR-002` (erro). | structure.py:MODES/allowed_mode/check_thickness; bridge.py:remove_part/edit_part |
| RN-12 | 🟢 O registro em `btm_structure` muda **antes** de chamar o adaptador; registro que voltou ao padrão (não removido, espessura 0, material vazio) é apagado (`_tidy`). Toda mudança de estrutura termina em `scene_divisions.reflow(force=True)`. | bridge.py:remove_part/restore_part/edit_part/_tidy |
| RN-13 | 🟢 Uma divisão corta um subvão-**folha** inteiro: vertical em `.a` (esquerda) e `.b` (direita), horizontal em `.a` (baixo) e `.b` (cima). `offset` = distância da face esquerda/de baixo do subvão até a chapa; permanece quando o vão-raiz muda. Recuos (`front`/`back`, padrão 20 mm) só tiram profundidade. Distanciador (`SPACER`) ocupa a faixa sem dividir: o subvão mantém o caminho, do lado maior. | divisions.py:resolve/_split/place |
| RN-14 | 🟢 `DIV-001`: offset fora de `[50 mm, tamanho − espessura − 50 mm]` (distanciador: `[0, tamanho − espessura]`); `DIV-002`: profundidade da chapa < 50 mm após recuos; `DIV-003`: subvão inexistente ou já cortado (órfã). Todos erro. | divisions.py:MIN_SPACE/MIN_DEPTH/offset_range/validate |
| RN-15 | 🟢 Divisão nova fica no meio (`max(0, (tamanho − t)/2)`); distanciador em offset 0; inserção múltipla de N chapas cria N+1 subvãos iguais `(tamanho − N·t)/(N+1)` em cadeia pelos `.b`. Espessura/material vêm do componente Divisória (`DIV`) do Configurador da linha `btm_line` (padrão `COZ`; closets `DOR`; faltando, MDF e 15 mm), salvo distanciador (espessura própria 15/30 mm) ou sobrescrita na divisão. | divisions.py:add/add_many/middle_offset; scene_divisions.py:configured/line_of; bridge.py:add_division/_raw_entry |
| RN-16 | 🟢 Remover divisão leva as que estão dentro das suas metades. "Sem Divisória" remove a divisória (não distanciador) que criou a folha escolhida; folha-raiz ou sem divisória → aviso "Este vão não tem divisória para remover". | divisions.py:remove/remove_in_space; bridge.py:remove_in_space |
| RN-17 | 🟢 "Distanciador p/ Divisão" exige que a folha escolhida seja filha de uma divisória (não distanciador); senão `ValueError` "Escolha o vão logo à direita (ou acima) de uma divisória"; grava `follow` = uid da divisória. | bridge.py:add_division |
| RN-18 | 🟢 Número de vãos N (1–10) = N−1 divisórias verticais `bay` em cadeia `s0`, `s0.b`, `s0.b.b`… com offset `(L − (N−1)·t)/N`; mudar N mantém as `bay` existentes (posição nova), acrescenta ou remove só as do fim (com o que estiver dentro); aviso "{n} divisória(s) de vão removida(s)". Sem `s0`, nada muda. | bays.py:plan/apply/removed; bridge.py:set_bays |
| RN-19 | 🟢 Cotas da divisória selecionada: `front`/`back` = recuo (0 se desligado), `low` = offset, `high` = tamanho − offset − espessura. Editar `low`/`high` muda o offset; editar `front`/`back` liga o recuo se > 0 (valor 0 desliga e mantém o valor antigo). | position.py:cotas/offset_from_cota; props.py:_pos_set |
| RN-20 | 🟢 Setas ←/→ movem divisória vertical e ↓/↑ horizontal pelo **Passo** (padrão 10 mm, mín. 0,1 mm); o primeiro toque numa divisória diferente da última movida usa o **Passo inicial** se > 0; o resultado fica em `offset_range`. Seta no eixo errado não faz nada. | position.py:step_move; ops_editor.py:_arrow/_ARROWS |
| RN-21 | 🟢 Extras da Estrutura (árvore de 20 nós): Base Superior Recuada (troca o tampo: remove `TOP` em `KEEP` ao ligar, restaura ao desligar), Pés Plásticos (150 mm, 4 posições ligadas por padrão), Rodapés frontal/esquerdo/direito, Rodapés Granito, Fechamentos (50 mm), Vistas e Vistas altas (150 mm). Valor 0 volta ao padrão. Pés e rodapés ficam abaixo da caixa (o módulo não sobe). Cada mudança recria todos os extras. | catalog.py:TREE/DEFAULT_ON; extras.py:layout/DEFAULTS; bridge.py:toggle_extra; scene_extras.py:sync |
| RN-22 | 🟢 Clique na vista: escolhe a **chapa** de menor Y (mais à frente; empate pela menor área) entre as que não são frente nem vão e não cobrem o subvão inteiro sob o clique; sem chapa, limpa a seleção e escolhe o **subvão-folha** de menor área sob o ponto (mantém o anterior se nenhum) e recalcula o vão da biblioteca. Vale em qualquer aba. | ops_editor.py:_handle_click/_boards; elevation.py:hit; divisions.py:space_at |
| RN-23 | 🟢 Inserir é recusado com motivo: Divisões/Gavetas/Internos/Portas sem subvão válido → "Selecione um vão na vista"; Gavetas/Portas sem vão da biblioteca que contenha o centro do subvão → "Este vão não pertence a um vão da biblioteca"; Internos/Deslizantes sem item de catálogo válido → "Escolha um item do catálogo". | ops_actions.py:insert_reason; bridge.py:library_opening |
| RN-24 | 🟢 Portas: frente por `DOOR_FRONTS[(escopo, invertido)]` (Ambas → `DOUBLE_DOORS`; Inteira/Esquerda → `DOOR_LEFT`, invertido `DOOR_RIGHT`; Direita → `DOOR_RIGHT`, invertido `DOOR_LEFT`); região ou escopo `FLIP` → `FLIP_UP`. Depois aplica estilo e puxador se escolhidos. A mesma frente já existente não é refeita. | bridge.py:DOOR_FRONTS/insert_doors/_front_steps/edit('FRONT') |
| RN-25 | 🟢 Gavetas: `DRAWERS` com N (1–8); Gavetões limitam N a 2–4; Blum grava `btm_custom.slide_kind = 'BLUM'` no vão (senão ""); Interna só no frameless, via `set_interior(drawers=N)`. | bridge.py:insert_drawers; props.py:drawer_count |
| RN-26 | 🟢 Internos: o item precisa caber (largura e altura do item + 10 mm de cada lado; profundidade ignorada), senão "{item} precisa de um vão de L × A mm". Painel externo no plano da frente para fora (Y −t a 0), embutido recuado (Y t a 2t), t = 18 mm; recorte centrado (maior largura, soma das alturas; respiro 440 × 30) como modificador `CPM_CUTOUT`; eletros de referência atrás; apoio = prateleira `PRAT` a 1/3 da altura; pistão = caixa 20 × 250 × 20 mm `PISTAO`. Cada inserção recebe `slot` = máximo + 1. | appliances.py:layout; catalog.py:Item.too_small; bridge.py:insert_interior; scene_interiors.py:_build |
| RN-27 | 🟢 Deslizantes: N folhas (2–3) no primeiro vão-raiz, uma por trilho (passo 20 mm, folha 18 mm, sobreposição 30 mm, largura `(L + (N−1)·30)/N`), trilhos de 10 mm em cima e embaixo; invertido põe a folha da direita na frente; estilos com gola/cava/perfil/puxador integrado ganham rasgo 20 mm. Exige profundidade `N·20 + 50 mm`. Folhas viram grupos `LEAF` de correr num grupo `FRAME` "Deslizantes"; folha com curso livre < 10 mm gera aviso "{folha} não corre: esbarra em {contato}". Reinserir troca o conjunto. | slides.py; scene_slides.py:apply; bridge.py:insert_slides |
| RN-28 | 🟢 Fundos: Inteiro/Inteiro Recuado (recuo padrão 20 mm), "Inserir automaticamente"; Inserir grava o modo e devolve o fundo se ele estiver removido. Fora do `btm`, biblioteca sem peça de fundo → "Este armário não tem fundo". | bridge.py:set_back; ops_actions.py:insert_payload |
| RN-29 | 🟢 Ctrl (ou ⌘)+Z desfaz e Ctrl+Shift+Z ou Ctrl+Y refaz **no rascunho**, em qualquer posição do mouse; sem passo: "Nada para desfazer."/"Nada para refazer.". | ops_editor.py:_handle_undo/process |
| RN-30 | 🟢 Fechar (botão ou Esc com o mouse na vista): sem alterações fecha; com alterações abre diálogo Continuar editando (padrão) / Descartar / Confirmar (recusado com erro bloqueante). Cancelar com alterações pede "Descartar as alterações e fechar o editor?". | ops_editor.py:BTM_OT_CabinetEditorClose/BTM_OT_CabinetEditorCancel |
| RN-31 | 🟢 Fora do editor (sem sessão), divisões acompanham o vão: `depsgraph_update_post` (raízes atualizadas com `btm_division_sig`) e `frame_change_post` (todas as raízes com assinatura) chamam `scene_divisions.reflow`, que só trabalha se a assinatura (vãos a 6 casas + divisões cruas + material + espessura) mudou. | reflow_handler.py; scene_divisions.py:reflow/_signature |
| RN-32 | 🟢 Montagem `LATERAL` (laterais do piso ao topo; base e tampo entre elas) ou `BASE` (base na largura toda; laterais em cima), só em módulo CAFFMob (`btm_kind == 'MODULE'` com `btm_cabinet`); "Padrão próprio" quando `standards.apply_core.is_own` (overrides, montagem diferente da origem ou espessura por papel). Na prática o ramo "overrides" não dispara num módulo CAFFMob: os únicos escritores de `btm_overrides` são `selection/editing.py:88-90` (só frameless por Geometry Nodes), `closets/props_closets.py:104` e `frameless/operators/ops_cabinet.py:76`; só a montagem e a espessura por papel tornam o padrão próprio _(Revisão cruzada 2026-10-10: grep `add_override`/`btm_overrides` no pacote)_. | structure.py:layout/carcass_lengths; bridge.py:is_caffmob_module/is_own_standard; panels_structure.py:draw_assembly |

## Requisitos Funcionais

🟡 Prioridades inferidas do caminho crítico (abrir → editar → OK/Cancelar), dos consumidores e dos 70 testes puros; não constituem roadmap aprovado.

| ID | Requisito | Prioridade | Critério de aceite |
|---|---|---|---|
| RF-01 | 🟢 Abrir o editor para o módulo ativo: sessão, rascunho, limites, peças iniciais, subvãos, janela, modal (RN-02) | Must | CA-01, CA-02 |
| RF-02 | 🟢 Rascunho com desfazer/refazer, Aplicar, OK, Cancelar, Fechar e rollback (RN-03 a RN-07, RN-29, RN-30) | Must | CA-03 a CA-08 |
| RF-03 | 🟢 Medidas do módulo validadas pela faixa (RN-08) | Must | CA-09, CA-10 |
| RF-04 | 🟢 Vista frontal: peças, vãos, seleção por clique, zoom pela roda, rótulos e barra "Selecionado" (RN-22) | Must | CA-11, CA-12 |
| RF-05 | 🟢 Validação e mensagens `DIM`/`GEO`/`DIV`/`STR`/`LIB`, Ajustes automáticos (RN-09, RN-10) | Must | CA-13, CA-14 |
| RF-06 | 🟢 Estrutura: remover/restaurar/editar componentes externos (RN-11, RN-12) | Must | CA-15, CA-16 |
| RF-07 | 🟢 Divisões: inserir (vertical, horizontal, múltipla, móvel, fixa, distanciador), editar, remover, Sem Divisória (RN-13 a RN-17) | Must | CA-17 a CA-20 |
| RF-08 | 🟢 Número de vãos (RN-18) | Should | CA-21 |
| RF-09 | 🟢 Posição e Movimentação da divisória selecionada (RN-19, RN-20) | Should | CA-22, CA-23 |
| RF-10 | 🟢 Extras da Estrutura (RN-21) | Should | CA-24 |
| RF-11 | 🟢 Gavetas e Portas no vão da biblioteca do alvo (RN-23 a RN-25) | Should | CA-25, CA-26 |
| RF-12 | 🟢 Internos para eletro (RN-26) | Could | CA-27 |
| RF-13 | 🟢 Deslizantes (RN-27) | Could | CA-28 |
| RF-14 | 🟢 Fundos (RN-28) | Should | CA-29 |
| RF-15 | 🟢 Ações da 003 sobre o vão selecionado: frente, estilo, puxador, material (grupo/frentes), interior da biblioteca; Salvar como módulo | Should | CA-30 |
| RF-16 | 🟢 Divisões acompanham o vão fora do editor (RN-31) | Must | CA-31 |
| RF-17 | 🟢 Montagem e "Padrão próprio" no módulo CAFFMob (RN-32) | Could | CA-32 |

## Requisitos Não Funcionais

| Tipo | Requisito observado | Evidência | Confiança |
|---|---|---|---|
| Um passo de desfazer por OK | Toda mudança dentro de um modal com `bl_options` `UNDO`; botões sem `UNDO`; Aplicar empurra passo explícito | ops_editor.py:BTM_OT_CabinetEditorModal; _apply_now | 🟢 código / 🟢 efeito: um Ctrl+Z na cena desfaz o OK inteiro _(Revisão 2026-10-10: `xvfb-run` de blender_004 "um Ctrl+Z na cena volta ao anterior" nas 4 bibliotecas, blender_006 "um Ctrl+Z desfaz o Confirmar inteiro", blender_008 "um Ctrl+Z desfaz o Aplicar inteiro")_ |
| Latência dos botões | Pedidos executados no próximo evento do modal; timer de 0,1 s (`TIMER_STEP`) garante eventos | ops_editor.py:TIMER_STEP/invoke/modal | 🟢 |
| Custo do reflow | `scene_divisions.reflow` sai sem trabalho quando a assinatura gravada na raiz não mudou; handlers ignoram enquanto há sessão e têm trava de reentrada `_running` | scene_divisions.py:reflow; reflow_handler.py | 🟢 |
| Memória do rascunho | Até 100 cópias profundas de `EditorState` (`walls2d.history.LIMIT`) | state.py:Draft; walls2d/history.py | 🟢 |
| Tolerâncias | Assinatura 1 µm; diff 0,1 mm; GEO 1 mm; faixa 1e−9 m; `library_opening` 0,1 mm | state.py; elevation.py; validate.py; bridge.py | 🟢 |
| Separação do cálculo | 11 núcleos rodam sem `bpy` (70 testes puros); `__init__` importa os módulos `bpy` só em `register` | `__init__.py:_modules`; tests/test_cabinet_*.py | 🟢 |
| Robustez dos handlers | `ReferenceError`/`RuntimeError` durante o reflow fora do editor são engolidos (a próxima atualização refaz) | reflow_handler.py:_reflow | 🟢 |
| Acessibilidade do estado | Peças removidas e subvão escolhido têm texto ("removido", rótulo do vão), não só cor | window.py:_draw_006 | 🟢 |

## Critérios de Aceitação

🟢 Cenários derivados do código atual. CA-03, CA-13 (GEO-002), CA-17 a CA-21, CA-22 (cálculo), CA-24 (geometria), CA-27 e CA-28 (geometria) têm equivalentes nos testes puros; os demais exigem Blender (smokes `blender_004_cabinet_editor_smoke`, `blender_006_cabinet_editor_tabs_smoke`, `blender_008_construtor_smoke`, `blender_012_cabinet_standard_smoke`, não executados nesta extração).

```gherkin
CA-01 — Abrir
Dado um módulo frameless ativo e nenhuma sessão
Quando executo caffmob.cabinet_editor
Então a sessão é criada com Draft(read_state(raiz)), a aba vira STRUCTURE, uma janela com Image Editor abre e o modal começa com timer de 0,1 s

CA-02 — Abrir sem janela disponível
Dado que window.open_editor levanta RuntimeError
Quando executo caffmob.cabinet_editor
Então a sessão é encerrada, o operador reporta ERROR "O Editor de Armário precisa de uma janela do Blender aberta." e devolve CANCELLED

CA-03 — Desfazer e refazer no rascunho
Dado três pedidos que mudaram o módulo (três passos)
Quando aperto Ctrl+Z duas vezes e Ctrl+Shift+Z uma vez
Então apply_state reaplica o 1º e depois o 2º instantâneo, nenhum passo novo é gravado e o painel reflete o instantâneo

CA-04 — Nada para desfazer
Dado um rascunho recém-aberto
Quando aperto Ctrl+Z
Então s.error = "Nada para desfazer." e a cena não muda

CA-05 — OK
Dado rascunho sujo sem erro
Quando clico OK
Então o modal termina FINISHED, reporta "Armário atualizado: {raiz}", a sessão acaba, os espelhos do painel são limpos e a janela fecha 0,05 s depois

CA-06 — OK bloqueado
Dado uma mensagem DIV-001 (ERROR)
Quando tento OK (ou Aplicar, ou "Confirmar" no Fechar)
Então o poll recusa com "Corrija os erros para confirmar" (Aplicar: "Corrija os erros para aplicar"; Fechar: WARNING e CANCELLED)

CA-07 — Cancelar depois de Aplicar
Dado que mudei a largura para 0,60, apliquei e depois mudei para 0,50
Quando clico Cancelar e confirmo "Descartar"
Então o módulo volta a 0,60 (instantâneo do Aplicar) e o modal devolve CANCELLED

CA-08 — Janela do sistema fechada
Dado rascunho sujo
Quando a janela do editor é fechada pelo sistema
Então o módulo volta ao instantâneo de retorno, aparece "Editor fechado: alterações descartadas" e o modal devolve CANCELLED

CA-09 — Medida válida
Dado faixa de largura 0,01–10 m
Quando escrevo 0,9 no campo Largura
Então o pedido 'dimension' chama selection.editing.set_dimension, grava um passo e o título mostra a nova largura

CA-10 — Medida fora da faixa
Dado faixa de profundidade estreitada pela biblioteca a 0,3–0,8 m
Quando escrevo 1,2 em Profundidade
Então DIM-003 (ERROR) com "valor 1200 mm faixa 300 mm – 800 mm" (unidade mm), a medida não muda, nenhum passo é gravado e o campo fica em alerta

CA-11 — Clique escolhe chapa
Dado uma prateleira e o fundo sob o cursor
Quando clico na vista
Então a prateleira é selecionada (o fundo cobre o subvão inteiro e é excluído) e a barra mostra "Selecionado: {prateleira}"

CA-12 — Clique escolhe vão
Dado área livre ou uma frente sob o cursor
Quando clico
Então selected = None, space = folha de menor área sob o ponto, o vão da biblioteca é recalculado e a barra mostra "Selecionado: Vão 1 › esquerdo"

CA-13 — Sobreposição interna
Dado duas prateleiras que se cruzam 5 mm
Quando o refresh valida
Então há GEO-002 (ERROR) com as duas peças e OK fica bloqueado

CA-14 — Ajustes automáticos
Dado que mudei a largura do módulo
Quando o refresh roda
Então as chapas que mudaram de medida aparecem como "mudou de medida" e as deslocadas como "moveu", exceto as editadas pelo usuário

CA-15 — Remover lateral em SHRINK
Dado módulo btm com lateral esquerda de 18 mm e largura 0,80
Quando removo a lateral esquerda em "Reduzir o armário"
Então btm_structure registra removed/SHRINK antes do adaptador, a largura vira 0,782, as demais chapas não saem do lugar e as divisões são reposicionadas

CA-16 — Modo não suportado
Dado biblioteca que só faz KEEP
Quando peço EXTEND no diálogo
Então o operador recusa com o motivo (WARNING) e nada é enfileirado; pelo bridge o modo cai em KEEP com LIB-001

CA-17 — Divisão vertical no meio
Dado subvão s0 de 0,764 m e espessura 15 mm
Quando insiro divisória vertical
Então offset = 0,3745 m, folhas s0.a e s0.b de 0,3745 m e um objeto "Divisória N" filho da raiz

CA-18 — Divisória perto da borda
Dado uma divisória com offset 30 mm
Quando o refresh valida
Então DIV-001 (ERROR) com a faixa 50 mm – (tamanho − t − 50 mm) e "Deixe pelo menos 50 mm de cada lado"

CA-19 — Inserção múltipla
Dado subvão de 0,90 m, 2 chapas de 15 mm
Quando insiro em modo múltiplo
Então três subvãos de 0,29 m (s0.a, s0.b.a, s0.b.b)

CA-20 — Sem Divisória num vão-raiz
Dado o subvão s0 escolhido
Quando insiro com tipo "Sem Divisória"
Então a mensagem LIB-001 "Este vão não tem divisória para remover" aparece e nada muda

CA-21 — Número de vãos
Dado 3 vãos (2 divisórias bay)
Quando mudo para 2
Então a divisória do fim sai (com o que estava dentro), a outra vai para a posição nova e aparece "1 divisória(s) de vão removida(s)"

CA-22 — Seta com Passo inicial
Dado Passo 10 mm, Passo inicial 50 mm e uma divisória vertical selecionada
Quando aperto → duas vezes com o mouse na vista
Então o offset anda +50 mm e depois +10 mm, sempre dentro de offset_range

CA-23 — Seta sem divisória
Dado nenhuma divisória selecionada
Quando aperto ↑
Então a cena não muda (a mensagem "Selecione uma divisória…" é apagada no mesmo ciclo: EC-01; 🟢 **Decisão do titular (2026-10-10, questions.md#pergunta-85):** a mensagem deve aparecer. Pendência de implementação: DT-08)

CA-24 — Pés plásticos
Dado caixa da carcaça e Pés Plásticos ligados com valor 0
Quando a árvore é sincronizada
Então 4 cilindros de raio 20 mm a 50 mm dos cantos, com 150 mm de altura abaixo da caixa, btm_hardware PE_PLASTICO

CA-25 — Portas invertidas
Dado escopo "Inteira" e "Inserir invertido"
Quando insiro portas num subvão contido num vão da biblioteca
Então a frente DOOR_RIGHT é aplicada no vão da biblioteca; com o mesmo tipo já existente, nada é refeito

CA-26 — Gaveta interna fora do frameless
Dado módulo closets
Quando insiro gaveta Interna
Então LIB-001 "Gaveta interna só existe no frameless" e nada muda

CA-27 — Painel de forno que não cabe
Dado subvão de 500 × 700 mm
Quando insiro "Painel Forno Externo" (595 × 595)
Então LIB-001 "Painel Forno Externo precisa de um vão de 615 × 615 mm" e nada é criado

CA-28 — Deslizantes sem profundidade
Dado vão-raiz de 80 mm de profundidade e 2 folhas
Quando insiro deslizantes
Então nada é criado e aparece "Os trilhos precisam de mais profundidade (profundidade 0.090)"

CA-29 — Fundo recuado
Dado fundo removido
Quando escolho "Inteiro Recuado" e Inserir
Então back_mode = RECESSED, o fundo é restaurado e o adaptador recebe set_back_recess(0,02)

CA-30 — Ação da 003 sem vão
Dado nenhuma peça e nenhum vão da biblioteca escolhidos
Quando clico "Material das frentes do vão…" (ou Frente, Estilo, Puxador, Interior)
Então WARNING "Selecione um vão ou uma frente na vista" e CANCELLED; "Material de um grupo…" funciona sem vão

CA-31 — Reflow fora do editor
Dado um módulo frameless com divisões e o editor fechado
Quando a largura muda por driver e o quadro troca
Então frame_change_post reposiciona as chapas mantendo o offset; uma segunda troca de quadro sem mudança não regrava nada

CA-32 — Montagem
Dado módulo CAFFMob com montagem LATERAL igual à do padrão de origem
Quando mudo para BASE no painel
Então a malha segue a nova montagem e aparece "Padrão próprio: difere do Padrão de Dimensões global"
```

## Prioridade (MoSCoW)

| Requisitos | Classificação | Justificativa |
|---|---|---|
| RF-01 a RF-07, RF-16 | 🟡 Must | Caminho crítico; `structure.layout`/`carcass_lengths` e `divisions` são consumidos por `geometry/mesh_gen`, `customize/adapters/btm` e `cutting/part_sources` |
| RF-08 a RF-11, RF-14, RF-15 | 🟡 Should | Têm alternativa (divisões manuais, customização pelo painel 3D da 003) |
| RF-12, RF-13, RF-17 | 🟡 Could | Abas de uso pontual; deslizantes com geometria simplificada (docstring de `slides.py`) |
| `validate.parse_dimension` (`DIM-001`/`DIM-002`), `validate.unsupported` (`CAT-001`), `structure.unsupported_mode` (`STR-001`), `appliances.support_offset`, lista `components`/`component_index` | 🟡 Won't | Sem chamador no pacote (grep); só testes ou nenhum desenho |

## Rastreabilidade de Código e Verificação

| Arquivo | Símbolos / responsabilidade | Evidência |
|---|---|---|
| state.py | `EditorState`, `signature`, `Draft` | 🟢 Código; test_cabinet_editor_state (4) |
| validate.py | `Message`, `limits_for`, `check_dimension`, `outside_volume`, `internal_overlaps`, `sort_messages` | 🟢 Código; test_cabinet_editor_validate (5) |
| elevation.py | `Part`, `kind_from_role`, `draw_order`, `hit`, `bounds`, `diff` | 🟢 Código; test_cabinet_editor_elevation (4) |
| structure.py | `RoleState`, `allowed_mode`, `check_thickness`, `layout`, `carcass_lengths`, `shrink_change` | 🟢 Código; test_cabinet_editor_structure (10) |
| divisions.py | `Box`, `Division`, `resolve`, `add`, `add_many`, `remove`, `remove_in_space`, `offset_range`, `validate`, `space_at`, `space_tokens` | 🟢 Código; test_cabinet_editor_divisions (16) |
| catalog.py, extras.py, bays.py, slides.py, appliances.py, position.py | Catálogo e geometria da 008 | 🟢 Código; test_cabinet_catalog (7), test_cabinet_extras (6), test_cabinet_bays (5), test_cabinet_slides (5), test_cabinet_appliances (5), test_cabinet_position (3) |
| data_props.py | `BTM_PG_Structure`, `BTM_PG_Division`, `BTM_PG_Extra` | 🟢 Código; blender_006, blender_008 |
| props.py | `Session`, campos virtuais, `BTM_PG_CabinetEditorState` | 🟢 Código |
| bridge.py | `read_state`, `apply_state`, `edit` e 23 ações, `parts`, estrutura, divisões, 008 | 🟢 Código; blender_004/006/008/012 |
| scene_*.py, reflow_handler.py | Peças próprias na cena e handlers | 🟢 Código; blender_006, blender_008 |
| ops_editor.py, ops_actions.py, window.py, panels*.py, previews.py | 18 operadores, desenho, 17 painéis | 🟢 Código; blender_004, blender_008 |

🟢 Executado em 2026-10-10: `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest test_cabinet_appliances test_cabinet_bays test_cabinet_catalog test_cabinet_editor_divisions test_cabinet_editor_elevation test_cabinet_editor_state test_cabinet_editor_structure test_cabinet_editor_validate test_cabinet_extras test_cabinet_position test_cabinet_slides` (de dentro de `tests/`): **70 testes aprovados**. Os testes `blender_*` não foram executados. _(Revisão 2026-10-10: os 70 testes puros repassaram; blender_004 (39 OK), blender_006 (162 OK) e blender_008 (70 OK) executados com `xvfb-run -a /opt/blender/blender --factory-startup --enable-event-simulate --python <teste>` e blender_012_cabinet_standard_smoke com `--background`, todos com código 0)_

## Lacunas e Pré-condições

- 🟢 A montagem (`btm_cabinet.assembly`) e os campos do fundo `auto_back`/`back_setback` são editados direto pelo painel, fora da fila; a montagem não entra no instantâneo, então Cancelar e Ctrl+Z não a revertem (EC-03). 🟢 **Decisão do titular (2026-10-10, questions.md#pergunta-42):** enfileirar `SET_ASSEMBLY` e incluir `assembly` no `EditorState`. Pendência de implementação: DT-01.
- 🟢 O passo de desfazer do Blender é um por OK (e um por Aplicar): validado no Blender 5.2 _(Revisão 2026-10-10: smokes blender_004/006/008 executados com `xvfb-run -a … --enable-event-simulate`, código 0)_.
- 🟢 `apply_state` reconstrói internos, extras e (quando há) deslizantes a cada desfazer/refazer apagando e recriando objetos; nomes e aberturas dependem da recriação (EC-12), não validado no Blender. 🟢 **Decisão do titular (2026-10-10, questions.md#pergunta-86):** recriar só quando a parte do instantâneo difere. Pendência de implementação: DT-09.
- 🟢 O catálogo diz "Tras 15mm" nas divisórias com/sem recuo, mas o recuo de trás do item nunca é usado (EC-06). 🟢 **Decisão do titular (2026-10-10, questions.md#pergunta-46):** aplicar `back = 15 mm`, `use_back = True` pelo item. Pendência de implementação: DT-05.
- 🟢 Pré-condição: o módulo precisa ter adaptador (`customize.adapters.for_object`); sem vãos-raiz (`inner_spaces` vazio) não há subvãos, divisões nem deslizantes.
