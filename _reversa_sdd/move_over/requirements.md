# Mover Sobre — Requisitos

🟢 **CONFIRMADO** — contrato extraído de `caffmob_draw/move_over/` em 2026-10-10 (10 arquivos, 1.338 linhas; a árvore de trabalho não tem alterações sem commit nesta pasta, último commit que a tocou: `640b2c2`). Confirmação de código não implica validação visual no Blender. 🟡 identifica inferência (prioridade, intenção); 🔴 identifica lacuna que exige decisão ou teste no Blender.

## Visão Geral

🟢 A unit implementa o "Mover Sobre" (feature 002, bloco 2) ampliado pelo "Reposicionar" (feature 003, nome "Mover Sobre" mantido): com o modo ligado, o usuário arrasta com o botão direito um objeto **A** até uma referência **B** e, numa janela GPU desenhada sobre a viewport com as vistas Superior e Frontal, alinha A a B por cliques em alvos, por distâncias digitadas, por rotação, por passo do teclado, por posições salvas, ou substitui A por outro módulo. Inclui também dois recursos de posicionamento ligados ao mesmo bloco: **Mover na Parede** (arrastar o módulo só no plano da parede) e **Plano de inserção** (uma face escolhida substitui o piso Z = 0 nas inserções). Fontes: `__init__.py`, `ops_drag.py`, `ops_dialog.py`, `ops_move_on_wall.py`, `ops_substitute.py`, `insertion_plane.py`.

## Responsabilidades

- 🟢 Calcular alvos e deslocamentos de alinhamento no referencial de B, sem `bpy` (`align.py`).
- 🟢 Calcular rotação pelo centro da base, passo do teclado e posição relativa salva, sem `bpy` (`reposition.py`).
- 🟢 Levar A e B ao referencial de B, aplicar a prévia em A, restaurar e detectar sobreposição (`scene.py:MoveOver`).
- 🟢 Guardar o estado do modo, as posições salvas na cena e o plano de inserção da sessão (`props.py`).
- 🟢 Ligar/desligar o modo e capturar o arraste do botão direito na viewport (`ops_drag.py`).
- 🟢 Desenhar e operar a janela "Mover Sobre" (`ops_dialog.py`).
- 🟢 Arrastar um módulo só ao longo da sua parede (`ops_move_on_wall.py`).
- 🟢 Substituir A por um módulo da biblioteca do usuário no mesmo canto (`ops_substitute.py`).
- 🟢 Escolher/limpar o plano de inserção (`insertion_plane.py`). O **consumo** do plano é de `hb_snap.py`, fora da unit.
- 🟢 Fora da responsabilidade: classificar objetos (contrato de `selection/classify.py`), primitivas 2D e `View2D` (contrato de `_reversa_sdd/canvas2d/`), cálculo de cotas e deslize na parede (`measure/cotas.py`, `measure/scene_cotas.py`), carregar módulos da biblioteca (`customize/library_io.py`).

## Regras de Negócio

| ID | Regra confirmada | Fonte |
|---|---|---|
| RN-01 | 🟢 Referencial de B, em metros: X = largura, Y = profundidade com a **frente em Y mínimo** (bibliotecas e módulo rápido têm frente em −Y e fundo em Y ≈ 0), Z = altura. O referencial usa posição e rotação de B, **sem escala**; as caixas locais já incluem a escala do objeto. Parede como B tem a face em Y = 0 (caixa de Y = 0 até a espessura). | align.py (docstring); scene.py:_frame/_local_box |
| RN-02 | 🟢 A = `classify.movable_root(obj)` (módulo para frentes e peças; geometria; obstáculo; grupo solto); B = `classify.reference_root(obj)` (o mesmo, mais paredes). A nunca é parede. `None` em qualquer um, ou A == B, levanta `ValueError("Esses objetos não podem ser usados no Mover Sobre.")` (traduzido). | scene.py:MoveOver.__init__; selection/classify.py:movable_root/reference_root |
| RN-03 | 🟢 Ao abrir a janela, A assume a rotação de B (sua escala é mantida e sua origem fica no mesmo ponto do mundo); a rotação pedida pelo usuário é composta por cima, em graus em torno de Z, pelo **centro da base** da caixa de A, que não se move. | scene.py:_target_matrix; reposition.py:origin_after_rotation; ops_dialog.py:invoke |
| RN-04 | 🟢 Alvos: `LEFT` (A encostado à esquerda: `bx0 − ax1`), `RIGHT` (`bx1 − ax0`), `DEPTH f` (frente de A na linha `by0 + f·(by1−by0)`), `HEIGHT f` (base de A em `bz0 + f·(bz1−bz0)`), `STACK` (base de A no topo de B), `WALL_FACE` (fundo de A na face da parede: `by0 − ay1`). Frações `0, 0.30, 0.50, 0.75, 1.0`; 0% = frente/base, 100% = fundo/topo. | align.py:delta_for/FRACTIONS |
| RN-05 | 🟢 Vista Superior: lados de B + 5 linhas de profundidade; com **parede** como B, lados + só a linha `WALL_FACE` (sem frações). Vista Frontal: lados + 5 linhas de altura (também com parede). | align.py:top_view_lines/front_view_lines |
| RN-06 | 🟢 Um clique escolhe no máximo **um alvo por eixo** (eixo `x` = lados; eixo `v` = profundidade/altura/face), o mais próximo em pixels dentro da tolerância inclusiva (padrão 12 px; janela usa `btm_move_over.tolerance_px`). Lado + linha no mesmo clique combinam. Fora de qualquer alvo o clique não faz nada. | align.py:pick; ops_dialog.py:_hits/_apply_click |
| RN-07 | 🟢 Na Frontal, só quando `pick` não achou alvo: clique com X dentro da largura de B na tela e Y acima do topo de B **além** da tolerância (`y > topo + tol`, sem limite superior) = `STACK`. | align.py:pick_stack; ops_dialog.py:_hits |
| RN-08 | 🟢 `combine` soma alvos de eixos diferentes; dentro de um mesmo eixo, o último alvo com deslocamento ≠ 0 vence. `align_to` só soma em `delta` os eixos com passo ≠ 0. | align.py:combine; scene.py:align_to |
| RN-09 | 🟢 Distâncias mostradas (modo relativo): X entre as faces mais próximas (negativo = sobrepostos em X, valor = −menor penetração); profundidade = frente de A − frente de B; altura = base de A − base de B. Digitar X mantém o lado em que o **centro** de A está (empate ⇒ direita). | align.py:gaps; scene.py:set_gap |
| RN-10 | 🟢 Modo absoluto: os campos X/Y/Z mostram o canto mínimo da caixa de A **no referencial de B** levado ao mundo; digitar move A para esse canto ficar no valor pedido. Alternar Relativa/Absoluta é só exibição: nada se move. | scene.py:world_min/set_world; ops_dialog.py:modal (button_mode) |
| RN-11 | 🟢 Digitação: Rotação aceita vírgula e remove `°` (buffer vazio = 0°); X/Profundidade/Altura aceitam negativo e zero; Passo não aceita negativo nem zero; comprimentos via `units.parse_length` na unidade da cena. Caracteres aceitos: `0123456789,.-mc °`. Valor inválido vira aviso no painel e o campo continua em edição. | ops_dialog.py:_commit_typing/modal |
| RN-12 | 🟢 Passo do teclado: → / ← movem ±passo em X, ↑ / ↓ ±passo em profundidade, Page Up / Page Down ±passo em altura. Passo padrão 0,01 m (0,0001–1 m). | reposition.py:step_delta; props.py:BTM_PG_MoveOverState.step |
| RN-13 | 🟢 Posição salva = `{delta, rotation, b_side}`: `b_side` = lado de B em que está o centro de A (empate ⇒ `RIGHT`); `delta.x` = do lado direito `xmin(A) − xmax(B)`, do esquerdo `xmax(A) − xmin(B)`; `delta.y` = frente A − frente B; `delta.z` = base A − base B. Aplicar = primeiro fixa a rotação salva, depois desloca A para repetir o delta no par atual. Persistem em `Scene.btm_saved_positions` (no `.blend`) com nome "Posição N"; a janela mostra só as **4 últimas**; a unit não remove itens. | reposition.py:save_position/apply_position; scene.py:apply_saved; ops_dialog.py:_save_position/_saved_items |
| RN-14 | 🟢 Se B é parede, ou o pai de B tem `IS_WALL_BP`, a prévia faz A **filho dessa parede** (`matrix_parent_inverse = Identity`, posição no mundo mantida). Cancelar devolve pai, inverso e matriz originais. | scene.py:preview/restore/_wall_of |
| RN-15 | 🟢 Confirmar grava como um passo de desfazer (`bl_options` com `UNDO`). Com `scene.btm_settings.collision_global` ligado e ainda sem aviso, se A (na posição alvo) cruza a AABB mundial de algum módulo (tolerância 1e−3 m), o primeiro Confirmar só escreve "Sobrepõe: …" (até 4 nomes) e o segundo grava. Sem `btm_settings`, não verifica. | ops_dialog.py:_confirm; scene.py:overlapping |
| RN-16 | 🟢 Cancelar (botão, Esc ou botão direito) devolve A exatamente ao estado original. Posições salvas durante a sessão **não** são desfeitas. | ops_dialog.py:cancel; scene.py:restore |
| RN-17 | 🟢 Com o modo ligado, o botão direito na viewport nunca abre menu de contexto: sem objeto movível sob o cursor, o clique é consumido. Desligado, o `poll` falha e o evento segue ao Blender. | ops_drag.py:BTM_OT_MoveOverDrag.poll/invoke |
| RN-18 | 🟢 O arraste abre a janela só com deslocamento Manhattan ≥ 5 px **e** referência válida ≠ A sob o cursor no último `MOUSEMOVE`; senão não faz nada. O atalho é registrado em "3D View" e nos 19 mapas de modo da viewport (senão o menu do modo captura o clique antes). | ops_drag.py:modal/register/VIEW3D_MODE_KEYMAPS |
| RN-19 | 🟢 Substituir: o novo módulo herda matriz de mundo e pai de A e encosta no mesmo canto de A em relação a B (lado de B pelo centro: direita ⇒ alinha `xmin`, esquerda ⇒ `xmax`), frente (`ymin`) e base (`zmin`); A e descendentes são apagados. Só a biblioteca de módulos do usuário (`library_io.list_modules`). | ops_substitute.py:substitute |
| RN-20 | 🟢 Mover na Parede: só X local (ou Z com Shift, nunca abaixo de 0); o afastamento (`back_y`) não muda. Em X o destino passa por `cotas.slide`, que para no vizinho da mesma faixa e nas pontas da parede com "Evitar Sobreposição" (`PlacementMixin.avoid_overlap`, ligado por padrão se a propriedade não existir) e, desligado, só limita a `[0, comprimento − largura]`. | ops_move_on_wall.py:_move; measure/cotas.py:slide; hb_placement.py:avoid_overlap |
| RN-21 | 🟢 Plano de inserção da sessão: matriz = `Translation(ponto clicado no mundo) @ normal.to_track_quat('Z','Y')`, achatada linha a linha em 16 floats; vale até "Limpar". O consumidor `hb_snap.py` usa a translação e a coluna Z como plano no lugar do piso, exceto em vista ortográfica lateral. | insertion_plane.py:_plane_matrix/set_plane; hb_snap.py:snap_to_grid |

## Requisitos Funcionais

🟡 Prioridades inferidas das features 002/003 (`_reversa_forward/002-editor-parede-mover-sobre/requirements.md` §5.4, `003-modulos-agregados-reposicionar/requirements.md` RF-21..RF-28) e dos testes; não constituem roadmap aprovado.

| ID | Requisito | Prioridade | Critério de aceite |
|---|---|---|---|
| RF-01 | 🟢 Ligar/desligar o modo (operador, HUD, painel) sem modal permanente | Must | CA-01 |
| RF-02 | 🟢 Arraste com botão direito de A até B abre a janela; clique simples não abre menu com o modo ligado | Must | CA-02, CA-03 |
| RF-03 | 🟢 Janela com vistas Superior e Frontal só com A (laranja) e B (azul), alvos realçáveis e rótulos de fração | Must | CA-04 |
| RF-04 | 🟢 Alinhar por clique em alvos (lados, profundidade, altura, empilhar, face da parede) com prévia no 3D | Must | CA-04, CA-05 |
| RF-05 | 🟢 Campos digitáveis X/Profundidade/Altura (relativo) ou X/Y/Z (absoluto), Rotação e Passo | Must | CA-06, CA-07 |
| RF-06 | 🟢 Passo do teclado (setas, Page Up/Down) | Should | CA-08 |
| RF-07 | 🟢 Confirmar (um passo de desfazer, aviso de sobreposição) e Cancelar (restaura) | Must | CA-09, CA-10 |
| RF-08 | 🟢 Salvar posição relativa e reaplicar em outro par | Should | CA-11 |
| RF-09 | 🟢 Substituir A por módulo da biblioteca do usuário no mesmo canto | Could | CA-12 |
| RF-10 | 🟢 Mover na Parede (X; Shift = Z) com parada em vizinhos | Should | CA-13 |
| RF-11 | 🟢 Escolher e limpar o plano de inserção da sessão | Should | CA-14 |

## Requisitos Não Funcionais

| Tipo | Requisito observado | Evidência | Confiança |
|---|---|---|---|
| Testabilidade | `align.py` e `reposition.py` não importam `bpy`; `__init__.py` importa os submódulos com `bpy` tardiamente para os testes puros rodarem | `__init__.py:_modules`; `tests/test_move_over_align.py`, `tests/test_reposition.py` | 🟢 |
| Disponibilidade do salvamento automático | O modo é uma propriedade, não um modal permanente (um modal rodando bloquearia o autosave) | `ops_drag.py` (docstring); `operators/viewport_hud.py:_MoveOverButton` | 🟢 |
| Ciclo de vida | Todo `draw_handler_add` tem `draw_handler_remove` em `_finish`, chamado em todas as saídas e no `cancel()`; itens de keymap removidos no `unregister` | `ops_dialog.py:_finish/cancel`; `ops_drag.py:_finish/unregister` | 🟢 |
| Escala de interface | Geometria da janela multiplicada por `preferences.system.ui_scale` | `ops_dialog.py:_scale/_layout` | 🟢 |
| Desempenho | Nenhum requisito de tempo verificável no código. A feature 002 pedia prévia em até 200 ms e redesenho em até 100 ms, sem medição | `_reversa_forward/002…/requirements.md` (RNF) | 🟡 decisão: medir/testar (DT-06; questions.md#pergunta-76): manter a meta e medi-la uma vez num projeto com ~100 módulos; sem medição, retirar a meta |

## Critérios de Aceitação

🟢 Cenários derivados do código atual; CA-01 a CA-05 e CA-11 têm cálculo coberto por testes puros, os demais dependem do Blender (`tests/blender_003_move_over_smoke.py`, `tests/blender_002_ui_events.py`, não executados nesta extração).

```gherkin
CA-01 — Ligar e desligar o modo
Dado WindowManager.btm_move_over.enabled = False
Quando executo caffmob.move_over_toggle duas vezes
Então enabled fica True e depois False, cada vez com relatório INFO, e as VIEW_3D são redesenhadas
E nenhum modal fica rodando entre as execuções

CA-02 — Arraste abre a janela (feliz)
Dado o modo ligado, um aéreo A e um balcão B na viewport
Quando pressiono o botão direito sobre uma porta de A, arrasto ≥ 5 px e solto sobre B
Então caffmob.move_over_dialog é invocado com a_name = raiz de A e b_name = raiz de B
E durante o arraste há uma linha tracejada do início ao cursor com o rótulo "A → B"

CA-03 — Arraste sem efeito (falha)
Dado o modo ligado
Quando clico com o botão direito no vazio, ou solto sobre A, sobre o vazio, ou após mover menos de 5 px
Então nenhuma janela abre, nenhum objeto muda e o menu de contexto não aparece
E com o modo desligado o mesmo clique abre o menu de contexto do Blender

CA-04 — Alinhar pelo lado e pela frente
Dado B = ((0,−0.55,0),(0.6,0,0.72)) e A = ((1.5,−0.40,1.4),(1.9,−0.05,2.1)) no referencial de B
Quando clico, na Superior, a 3 px do canto direito-frontal de B (tolerância 12 px)
Então os alvos RIGHT e DEPTH 0 são aplicados juntos: xmin(A) = 0.6 e ymin(A) = −0.55

CA-05 — Clique fora da tolerância (falha)
Dado a mesma vista
Quando clico a 13 px do lado direito de B, longe de qualquer linha
Então pick devolve [] e A não se move

CA-06 — Distância digitada
Dado A à direita de B no modo relativo e unidade da cena em mm
Quando clico no campo X, digito "50" e pressiono Enter
Então a face esquerda de A fica 50 mm à direita da face direita de B, e as vistas são reenquadradas

CA-07 — Valor inválido (falha)
Dado o campo Passo em edição
Quando digito "0" ou "-5" e pressiono Enter
Então o painel mostra a mensagem de units.parse_length, o passo não muda e o campo continua em edição

CA-08 — Passo do teclado
Dado passo 0,01 m e nenhum campo em edição
Quando pressiono seta direita e depois Page Down
Então A move +0,01 m em X e −0,01 m em altura no referencial de B

CA-09 — Confirmar com sobreposição
Dado btm_settings.collision_global = True e A sobreposto a outro módulo
Quando pressiono Enter
Então o painel mostra "Sobrepõe: <nomes>. Confirme de novo para gravar mesmo assim." e a janela continua
E ao pressionar Enter de novo a janela fecha com FINISHED e um passo de desfazer

CA-10 — Cancelar
Dado A já movido, girado e reparentado à parede de B na prévia
Quando pressiono Esc, o botão direito ou Cancelar
Então pai, matrix_parent_inverse e matrix_world de A voltam aos originais e o operador devolve CANCELLED

CA-11 — Posição salva em outro par
Dado A à direita de B com 0,15 m de folga e rotação 0
Quando salvo a posição e a aplico a outro par A'/B'
Então xmin(A') − xmax(B') = 0,15 e base(A') − base(B') = base(A) − base(B)
E sem posições salvas não há botões; com mais de 4, só as 4 últimas aparecem

CA-12 — Substituir
Dado A à direita de B e um módulo salvo na biblioteca do usuário
Quando clico em Substituir e escolho o módulo
Então o novo módulo fica com xmin, ymin e zmin iguais aos de A no referencial de B, A some e o novo fica ativo
E se a lista estiver vazia ou o carregamento falhar, o operador avisa e devolve CANCELLED sem apagar A

CA-13 — Mover na Parede
Dado um módulo ativo encostado na frente de uma parede, Evitar Sobreposição ligado e um vizinho à direita
Quando invoco caffmob.move_on_wall e arrasto para a direita além do vizinho
Então o módulo para encostado no vizinho, o afastamento não muda, e Esc devolve a posição original
E se o raio do mouse não cortar o plano da frente, o operador avisa e devolve CANCELLED

CA-14 — Plano de inserção
Dado o menu do objeto
Quando escolho "Usar como plano de inserção" e clico numa face
Então btm_insertion_plane.active = True, source_name = objeto da face e a matriz tem a normal na coluna Z
E clicar fora de qualquer face avisa "Nenhuma face sob o cursor" e devolve CANCELLED; "Limpar" volta ao piso
```

## Prioridade (MoSCoW)

| Requisitos | Classificação | Justificativa |
|---|---|---|
| RF-01 a RF-05, RF-07 | 🟡 Must | Núcleo do fluxo pedido na 002 (RF-26..RF-33) e 003 (RF-21..RF-23, RF-25) |
| RF-06, RF-08, RF-10, RF-11 | 🟡 Should | Marcados Should nas features 002/003 |
| RF-09 | 🟡 Could | Marcado Could na 003 (RF-27) |
| Fechar o modo por Esc (002 RF-26) | 🟢 **Decisão do titular (2026-10-10, questions.md#pergunta-75):** Won't (nesta versão) | Não implementado: Esc só cancela arraste/janela |

## Rastreabilidade de Código e Verificação

| Arquivo | Símbolos / responsabilidade | Evidência |
|---|---|---|
| caffmob_draw/move_over/align.py | Target, delta_for, combine, top/front_view_lines, pick, pick_stack, gaps, overlaps | 🟢 Código; test_move_over_align |
| caffmob_draw/move_over/reposition.py | box_center_base, rotate_point_z, origin_after_rotation, rotated_box, step_delta, absolute_values, side_of, save_position, apply_position | 🟢 Código; test_reposition |
| caffmob_draw/move_over/scene.py | MoveOver (caixas, prévia, restauração, sobreposição) | 🟢 Código; blender_003_move_over_smoke (não executado) |
| caffmob_draw/move_over/props.py | BTM_PG_MoveOverState, BTM_PG_SavedPosition, BTM_PG_InsertionPlane | 🟢 Código |
| caffmob_draw/move_over/ops_drag.py | caffmob.move_over_toggle, caffmob.move_over_drag, keymaps | 🟢 Código; blender_002_ui_events (não executado) |
| caffmob_draw/move_over/ops_dialog.py | caffmob.move_over_dialog | 🟢 Código; validação visual pendente |
| caffmob_draw/move_over/ops_move_on_wall.py | caffmob.move_on_wall | 🟢 Código; blender_002_smoke importa o módulo |
| caffmob_draw/move_over/ops_substitute.py | caffmob.move_over_substitute, substitute | 🟢 Código; blender_003_move_over_smoke |
| caffmob_draw/move_over/insertion_plane.py | caffmob.set_insertion_plane, caffmob.clear_insertion_plane | 🟢 Código; blender_003_move_over_smoke (só `set_plane`) |

🟢 Executado em 2026-10-10: `PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=tests python3 -m unittest test_move_over_align test_reposition -v`: **14 testes aprovados** (8 + 6). Cobrem lados, frações, empilhar, parede, clique e tolerância, folgas/sobreposição, rotação pelo centro da base, caixa girada, passo, valor absoluto, posição salva nos dois lados. Não cobrem `scene.py`, operadores, GPU nem eventos.

## Lacunas e Pré-condições

- 🟡 Prévia e redesenho sem meta de tempo medida (RNF de 002 não verificado) — decisão: medir/testar (DT-06; questions.md#pergunta-76).
- 🟢 **Decisão do titular (2026-10-10, questions.md#pergunta-75):** Esc não desliga o modo e não há realce 3D do alvo durante o arraste (002 RF-26/RF-27 ficam Won't nesta versão); o botão do HUD desliga o modo e o rótulo A → B identifica o alvo. O código já faz isso; a atualização da 002 fica para o ciclo forward (fora de `_reversa_sdd/`).
- 🟢 **Decisão do titular (2026-10-10, questions.md#pergunta-16):** alinhamento e verificação de sobreposição usam a mesma caixa da árvore visível (`_tree_box`) do Substituir. 🟢 (código) hoje as caixas de A e B em `scene.py` usam só a geometria da raiz quando ela não é Empty (`object_corners` → `bound_box` da raiz). Pendência de implementação: DT-02.
- 🟢 Pré-condição: `selection/classify.py`, `aggregates/group.object_corners`, `canvas2d` (`draw`, `View2D`, `distance_point_segment`), `measure/cotas`, `measure/scene_cotas`, `customize/library_io`, `data/units`, `data/i18n` disponíveis com os contratos citados em `design.md` › Dependências.
