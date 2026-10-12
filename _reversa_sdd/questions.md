# Perguntas para Validação — BlenderToMob (re-extração 2026-10)

> Gerado pelo Reviewer em 2026-10-10. 98 perguntas, ordenadas por severidade.
> **Status: todas respondidas em 2026-10-10 — titular aceitou as 98 recomendações.**
> Cada uma traz a **resposta recomendada** pelo Reviewer. Preencha **Resposta** (ou escreva `aceito` para adotar a recomendação) e digite `reversa` quando terminar.

| Severidade | Quantidade |
|---|---|
| Crítico | 5 |
| Moderado | 65 |
| Cosmético | 28 |

---

## Pergunta 1

**Severidade:** Crítico · **Unit:** `walls2d`
**Contexto:** model.py:remove_node 260-271; ops_editor.py:_handle_click 718-726
**Spec afetada:** `_reversa_sdd/walls2d/edge-cases.md`
**Pergunta:** Remover Vértice deve registrar o source do trecho eliminado em removed_sources (como o Delete faz)?
**Impacto:** Hoje a parede de origem fica na cena, fora do rascunho, com a restrição antiga, sobreposta ao trecho que passou a cobrir o vão
**Recomendação do Reviewer:** Sim: acrescentar o source a removed_sources em remove_node (ou no chamador), igual a remove_segment; evita parede órfã no projeto

✅ Respondida

**Resposta:** aceito (recomendação do Reviewer adotada pelo titular em 2026-10-10)

---

## Pergunta 2

**Severidade:** Crítico · **Unit:** `selection`
**Contexto:** caffmob_draw/selection/component.py:own_aggregates; aggregates/ops_aggregate.py:delete_components
**Spec afetada:** `_reversa_sdd/selection/requirements.md`
**Pergunta:** Ao apagar uma parede, os agregados dos módulos filhos dela devem entrar na pergunta 'O objeto tem agregados'?
**Impacto:** Hoje o diálogo aparece e, com 'Apagar também os agregados' desligado, os agregados de um módulo que não foi apagado viram objetos soltos (unconvert)
**Recomendação do Reviewer:** Não: own_aggregates deve parar em raízes de módulo e em alvos que não levam a subárvore (parede, piso, teto), porque esses agregados pertencem a outro componente

✅ Respondida

**Resposta:** aceito (recomendação do Reviewer adotada pelo titular em 2026-10-10)

---

## Pergunta 3

**Severidade:** Crítico · **Unit:** `aggregates`
**Contexto:** caffmob_draw/aggregates/convert.py:can_convert linha 126
**Spec afetada:** `_reversa_sdd/aggregates/requirements.md`
**Pergunta:** O terceiro teste de can_convert deve recusar 'pai descendente do objeto' (como diz a mensagem) em vez de 'objeto descendente do pai' (como o código faz)?
**Impacto:** Hoje um objeto que já é filho do pai (peça de módulo, agregado ou folha que se quer reconverter) é recusado, e um pai que é filho do objeto passa e pode gerar ciclo de parentesco no Blender
**Recomendação do Reviewer:** Sim: trocar para `parent in obj.children_recursive`; é o que a mensagem e a 003 descrevem e evita o ciclo

✅ Respondida

**Resposta:** aceito (recomendação do Reviewer adotada pelo titular em 2026-10-10)

---

## Pergunta 4

**Severidade:** Crítico · **Unit:** `aggregates`
**Contexto:** caffmob_draw/aggregates/ops_aggregate.py:delete_components; selection/component.py:own_aggregates/delete_plan
**Spec afetada:** `_reversa_sdd/aggregates/edge-cases.md`
**Pergunta:** Apagar uma parede (ou piso/teto) deve perguntar pelos agregados dos módulos filhos dela?
**Impacto:** O diálogo aparece; desligado, desconverte agregados de módulos que não são apagados (EC-16, EC-02); ligado, não apaga nada além da parede. Nenhuma resposta faz o que o texto promete
**Recomendação do Reviewer:** Não: own_aggregates deve parar em raízes de módulo e em alvos que não levam a subárvore (mesma decisão da revisão de selection)

✅ Respondida

**Resposta:** aceito (recomendação do Reviewer adotada pelo titular em 2026-10-10)

---

## Pergunta 5

**Severidade:** Crítico · **Unit:** `revisão cruzada`
**Contexto:** Exclusão de parede por X/Delete (plugin ou nativo) × caffmob.wall_remove
**Spec afetada:** `_reversa_sdd/selection/edge-cases.md EC-18`
**Pergunta:** Ao apagar uma parede, portas/janelas, geometrias e cotas filhas devem ir junto, ficar no lugar (como em wall_remove) ou o X/Delete deve delegar para caffmob.wall_remove?
**Impacto:** Hoje filhos não grudados saltam para a posição local e caixas de porta/janela ficam soltas sem parede
**Recomendação do Reviewer:** Fazer o X/Delete numa parede usar ops_wall_extras.remove_wall (mesma regra KEEP_WITH_WALL e matriz de mundo preservada)

✅ Respondida

**Resposta:** aceito (recomendação do Reviewer adotada pelo titular em 2026-10-10)

---

## Pergunta 6

**Severidade:** Moderado · **Unit:** `canvas2d`
**Contexto:** canvas2d/window.py:_close (l. 105-122)
**Spec afetada:** `_reversa_sdd/canvas2d/edge-cases.md`
**Pergunta:** Quando o editor foi aberto numa janela duplicada e, no fechamento, só resta uma janela (ou window_ptr não bate), _close não faz nada e a área fica como Image Editor sem cabeçalho nem menus. Isso é intencional ou a área deveria voltar a VIEW_3D com menus/cabeçalho?
**Impacto:** Usuário pode ficar com uma área 'vazia' sem cabeçalho no layout salvo no .blend
**Recomendação do Reviewer:** Restaurar VIEW_3D com show_menus/show_region_header ligados nesse ramo: evita área órfã e coincide com o fluxograma flowcharts/canvas2d.md §1

✅ Respondida

**Resposta:** aceito (recomendação do Reviewer adotada pelo titular em 2026-10-10)

---

## Pergunta 7

**Severidade:** Moderado · **Unit:** `canvas2d`
**Contexto:** compat.py:pinch_delta; gestures.py:PINCH_SENSITIVITY
**Spec afetada:** `_reversa_sdd/canvas2d/tasks.md`
**Pergunta:** O sinal de pinch_delta (-(dx+dy)) e a sensibilidade 1/150 foram validados em quais plataformas (macOS, Wayland, Windows)?
**Impacto:** Pinça invertida ou lenta/rápida demais numa plataforma não testada
**Recomendação do Reviewer:** Rodar tests/blender_013_touchpad_smoke.py e a prova manual em cada plataforma suportada e registrar em investigation.md §6

✅ Respondida

**Resposta:** aceito (recomendação do Reviewer adotada pelo titular em 2026-10-10)

---

## Pergunta 8

**Severidade:** Moderado · **Unit:** `walls2d`
**Contexto:** ops_editor.py:_answer_no 838-841; apply.py:apply_plan 244
**Spec afetada:** `_reversa_sdd/walls2d/edge-cases.md`
**Pergunta:** O "Não" da pergunta de fechamento por arraste (close_existing) deve sobreviver ao OK?
**Impacto:** A rede de segurança do OK fecha a cadeia mesmo assim e conta em 'closed'
**Recomendação do Reviewer:** Respeitar o Não (marcar a cadeia para pular close_if_touching) ou remover a pergunta; hoje ela não tem efeito

✅ Respondida

**Resposta:** aceito (recomendação do Reviewer adotada pelo titular em 2026-10-10)

---

## Pergunta 9

**Severidade:** Moderado · **Unit:** `walls2d`
**Contexto:** ops_editor.py:handle_zoom_window 261-262
**Spec afetada:** `_reversa_sdd/walls2d/edge-cases.md`
**Pergunta:** Soltar o botão sobre a barra superior deve concluir o arraste de vértice e o retângulo da lupa?
**Impacto:** Hoje o RELEASE é consumido pela barra: o nó continua seguindo o mouse e o retângulo não termina
**Recomendação do Reviewer:** Consumir na barra só LEFTMOUSE PRESS; deixar o RELEASE seguir quando há arraste ou retângulo em curso

✅ Respondida

**Resposta:** aceito (recomendação do Reviewer adotada pelo titular em 2026-10-10)

---

## Pergunta 10

**Severidade:** Moderado · **Unit:** `walls2d`
**Contexto:** ops_editor.py:BTM_OT_WallEditorOk 887-891
**Spec afetada:** `_reversa_sdd/walls2d/tasks.md`
**Pergunta:** confirm_pending deve ser zerado quando o rascunho muda depois do 1º aviso?
**Impacto:** Um OK posterior aplica sem mostrar avisos novos (itens que não cabem, módulos em trechos apagados)
**Recomendação do Reviewer:** Sim: guardar a assinatura do rascunho no aviso e recalcular se mudou

✅ Respondida

**Resposta:** aceito (recomendação do Reviewer adotada pelo titular em 2026-10-10)

---

## Pergunta 11

**Severidade:** Moderado · **Unit:** `walls2d`
**Contexto:** model.py:set_angle_abs/set_angle_rel/_move_end/move_node
**Spec afetada:** `_reversa_sdd/walls2d/edge-cases.md`
**Pergunta:** Com Bloquear Ângulo ligado, os campos de ângulo devem ficar desabilitados (ou ignorar a trava)?
**Impacto:** Hoje o ângulo não muda e o comprimento vira L·cos Δ, chegando a 0 ou invertendo o trecho, sem validação
**Recomendação do Reviewer:** Desabilitar angle_abs/angle_rel no painel quando lock_angle; é a leitura mais coerente da trava

✅ Respondida

**Resposta:** aceito (recomendação do Reviewer adotada pelo titular em 2026-10-10)

---

## Pergunta 12

**Severidade:** Moderado · **Unit:** `measure`
**Contexto:** caffmob_draw/measure/cotas.py:apply
**Spec afetada:** `_reversa_sdd/measure/requirements.md`
**Pergunta:** Aplicar a cota anterior/posterior pode sobrepor o vizinho do lado oposto, e a inferior pode passar do teto (cota superior negativa). Isso deve ser rejeitado com 'Valor Inválido'?
**Impacto:** Hoje o painel aceita posições que colidem ou atravessam o teto sem aviso (EC-01, EC-02)
**Recomendação do Reviewer:** Rejeitar as duas com 'Valor Inválido': segue o padrão de validação já usado em apply e evita colisão silenciosa

✅ Respondida

**Resposta:** aceito (recomendação do Reviewer adotada pelo titular em 2026-10-10)

---

## Pergunta 13

**Severidade:** Moderado · **Unit:** `measure`
**Contexto:** hb_placement.py:get_wall_children_sorted (usado por scene_cotas.obstacles)
**Spec afetada:** `_reversa_sdd/measure/edge-cases.md`
**Pergunta:** Vizinhos sem Geometry Nodes (módulo rápido btm_cabinet, objeto importado) viram obstáculo de largura e altura zero. As cotas devem medir até a lateral real desses vizinhos?
**Impacto:** Cotas e 'Mover na Parede' erradas em projetos que misturam módulos HB e BTM (EC-03)
**Recomendação do Reviewer:** Sim: medir pela largura de btm_cabinet ou pelo bounding box, igual ao que _dims já faz para o próprio módulo

✅ Respondida

**Resposta:** aceito (recomendação do Reviewer adotada pelo titular em 2026-10-10)

---

## Pergunta 14

**Severidade:** Moderado · **Unit:** `measure`
**Contexto:** scene_cotas.py:_wall_of
**Spec afetada:** `_reversa_sdd/measure/design.md`
**Pergunta:** Módulos filhos de paredes da camada nova (BTM, sem IS_WALL_BP) são tratados como livres (só cotas verticais). É intencional?
**Impacto:** Em paredes BTM o painel não mostra anterior/posterior/afastamento nem 'Mover na Parede'
**Recomendação do Reviewer:** Provavelmente transitório até a camada BTM ter contrato de parede; confirmar e registrar

✅ Respondida

**Resposta:** aceito (recomendação do Reviewer adotada pelo titular em 2026-10-10)

---

## Pergunta 15

**Severidade:** Moderado · **Unit:** `move_over`
**Contexto:** caffmob_draw/move_over/ops_dialog.py:316-319 (modal, ramo de digitação, TAB)
**Spec afetada:** `_reversa_sdd/move_over/design.md`
**Pergunta:** Com um campo em edição e um valor válido, Tab grava e volta ao campo X (índice 0) em vez de ir ao próximo campo; com um valor inválido, vai ao próximo campo levando o texto inválido. Qual é o comportamento esperado?
**Impacto:** A navegação por Tab entre Profundidade, Altura, Rotação e Passo não funciona como o texto de ajuda sugere
**Recomendação do Reviewer:** Tab grava e vai sempre ao próximo campo; se a gravação falhar, fica no campo atual com o aviso. Isso segue a convenção de formulário e corrige um provável bug (guardar o índice antes do _commit_typing)

✅ Respondida

**Resposta:** aceito (recomendação do Reviewer adotada pelo titular em 2026-10-10)

---

## Pergunta 16

**Severidade:** Moderado · **Unit:** `move_over`
**Contexto:** caffmob_draw/move_over/scene.py:_local_box/overlapping vs ops_substitute.py:_tree_box
**Spec afetada:** `_reversa_sdd/move_over/requirements.md`
**Pergunta:** As caixas de A e B usadas no alinhamento e na verificação de sobreposição devem incluir a árvore de malhas visíveis (frentes, puxadores), como o Substituir já faz, ou só a geometria da raiz?
**Impacto:** Com raízes que não envolvem frentes e puxadores, o alinhamento e o aviso de sobreposição ignoram as peças que saem da caixa
**Recomendação do Reviewer:** Usar a mesma caixa da árvore visível (_tree_box) nos dois lugares, para que alinhamento, sobreposição e Substituir concordem

✅ Respondida

**Resposta:** aceito (recomendação do Reviewer adotada pelo titular em 2026-10-10)

---

## Pergunta 17

**Severidade:** Moderado · **Unit:** `move_over`
**Contexto:** caffmob_draw/move_over/ops_move_on_wall.py e insertion_plane.py (sem cancel())
**Spec afetada:** `_reversa_sdd/move_over/edge-cases.md`
**Pergunta:** Se o Blender interromper Mover na Parede ou Plano de inserção (abrir arquivo, fechar janela), a posição original e o cabeçalho/cursor devem ser restaurados?
**Impacto:** Pode deixar o módulo fora da posição original sem passo de desfazer, e o cabeçalho ou o cursor EYEDROPPER presos
**Recomendação do Reviewer:** Sim: definir cancel() que restaura a posição e chama _end, como a janela e o arraste já fazem

✅ Respondida

**Resposta:** aceito (recomendação do Reviewer adotada pelo titular em 2026-10-10)

---

## Pergunta 18

**Severidade:** Moderado · **Unit:** `move_over`
**Contexto:** caffmob_draw/move_over/ops_dialog.py:modal (ARROWS) e _confirm
**Spec afetada:** `_reversa_sdd/move_over/edge-cases.md`
**Pergunta:** Depois do aviso de sobreposição, mover A com setas ou Page Up/Down deve zerar o aviso (para o próximo Confirmar verificar de novo)?
**Impacto:** Hoje o segundo Confirmar grava sem reavaliar, mesmo que o passo tenha mudado a sobreposição
**Recomendação do Reviewer:** Sim: zerar warned no passo do teclado, como clique em alvo, digitação e posição salva já fazem

✅ Respondida

**Resposta:** aceito (recomendação do Reviewer adotada pelo titular em 2026-10-10)

---

## Pergunta 19

**Severidade:** Moderado · **Unit:** `move_over`
**Contexto:** caffmob_draw/move_over/ops_substitute.py:substitute
**Spec afetada:** `_reversa_sdd/move_over/edge-cases.md`
**Pergunta:** No Substituir, o novo módulo deve herdar a escala de A (hoje recebe a.matrix_world inteira)?
**Impacto:** Um A escalado gera um módulo novo escalado, com medidas diferentes das da biblioteca
**Recomendação do Reviewer:** Herdar só posição e rotação (LocRotScale sem escala), já que o módulo da biblioteca tem medidas próprias

✅ Respondida

**Resposta:** aceito (recomendação do Reviewer adotada pelo titular em 2026-10-10)

---

## Pergunta 20

**Severidade:** Moderado · **Unit:** `selection`
**Contexto:** caffmob_draw/selection/editing.py:set_dimension (porta/janela HB)
**Spec afetada:** `_reversa_sdd/selection/edge-cases.md`
**Pergunta:** Editar a largura ou a altura de uma porta/janela HB pelo painel deve refazer a porta real (_sync_opening) e mostrar a medida da folha, como o Redimensionar já faz?
**Impacto:** Hoje o painel grava só o furo e mostra o furo, enquanto o aviso e o Redimensionar mostram a folha: dois números para a mesma porta, e a porta real fica desatualizada
**Recomendação do Reviewer:** Sim: o painel deve usar o mesmo caminho do Redimensionar (_leaf_to_hole + _sync_opening), seguindo a feature 010 RN-01/RN-02

✅ Respondida

**Resposta:** aceito (recomendação do Reviewer adotada pelo titular em 2026-10-10)

---

## Pergunta 21

**Severidade:** Moderado · **Unit:** `selection`
**Contexto:** caffmob_draw/selection/resize.py:can_resize/_set_width
**Spec afetada:** `_reversa_sdd/selection/edge-cases.md`
**Pergunta:** Janelas BTM (btm_plane OPENING) devem ser redimensionáveis? Se sim, por qual caminho (btm_opening.width e a malha de corte)?
**Impacto:** Hoje o menu Redimensionar aparece para elas e sempre falha com um erro em inglês ('Object does not have geometry node modifier')
**Recomendação do Reviewer:** Bloquear em can_resize até existir um caminho próprio; é a correção de menor risco

✅ Respondida

**Resposta:** aceito (recomendação do Reviewer adotada pelo titular em 2026-10-10)

---

## Pergunta 22

**Severidade:** Moderado · **Unit:** `openings`
**Contexto:** operators/doors_windows.py:place_in_region (l. 968-969); openings/region.py:_face_y
**Spec afetada:** `_reversa_sdd/openings/requirements.md`
**Pergunta:** A porta ou janela inserida numa região marcada na face de fundo deve abrir para o lado dessa face, como pede 011 RN-11?
**Impacto:** Hoje a caixa entra sempre em y = 0 com rotação zero; o lado guardado (side) só serve para o desenho
**Recomendação do Reviewer:** Sim: com side = BACK, gravar Swing Inside = falso no símbolo (ou girar 180°) ao inserir; atende a 011 RN-11 sem mexer no corte

✅ Respondida

**Resposta:** aceito (recomendação do Reviewer adotada pelo titular em 2026-10-10)

---

## Pergunta 23

**Severidade:** Moderado · **Unit:** `openings`
**Contexto:** openings/sync.py:_swing (l. 33-43); ops.py:door_of
**Spec afetada:** `_reversa_sdd/openings/edge-cases.md`
**Pergunta:** Cotas e textos 2D podem ficar como filhos da caixa da porta na prática? Se sim, _swing deve exigir o input 'Swing Inside', como room_door_leaf.swing_of?
**Impacto:** Uma cota antes do símbolo faz a porta real ignorar mão e lado, transforma um vão aberto em porta e faz a tecla I falhar com erro
**Recomendação do Reviewer:** Filtrar por has_input('Swing Inside') (ou pelo nome 'Door Swing'), como room_door_leaf já faz; custo baixo e remove a ambiguidade

✅ Respondida

**Resposta:** aceito (recomendação do Reviewer adotada pelo titular em 2026-10-10)

---

## Pergunta 24

**Severidade:** Moderado · **Unit:** `openings`
**Contexto:** operators/doors_windows.py:toggle_double_door (l. 1352-1373); openings/sync.py:kind_of/signature
**Spec afetada:** `_reversa_sdd/openings/edge-cases.md`
**Pergunta:** Trocar porta simples ↔ dupla pelo 'Toggle Double Door' deve refazer a porta real?
**Impacto:** Hoje o símbolo 2D desenha dupla e a porta real continua simples; nem um sync posterior corrige, porque kind_of prefere o kind gravado e a assinatura não inclui Is Double
**Recomendação do Reviewer:** Sim: o operador deve atualizar btm_opening_real.kind e chamar _sync_opening (e a assinatura incluir o kind efetivo)

✅ Respondida

**Resposta:** aceito (recomendação do Reviewer adotada pelo titular em 2026-10-10)

---

## Pergunta 25

**Severidade:** Moderado · **Unit:** `openings`
**Contexto:** openings/region_props.py:region_wall (l. 167) chamado por region.py:draw_regions (POST_PIXEL)
**Spec afetada:** `_reversa_sdd/openings/edge-cases.md`
**Pergunta:** Aceita mover a invalidação da região (active = False) para fora do callback de desenho?
**Impacto:** Escrever em WindowManager durante o desenho pode ser bloqueado ou gerar redesenhos extras no Blender 5.2 (não confirmado no RAG)
**Recomendação do Reviewer:** Sim: no desenho só ignorar a região inválida; zerar active em region_wall chamado por operadores ou num depsgraph_update_post

✅ Respondida

**Resposta:** aceito (recomendação do Reviewer adotada pelo titular em 2026-10-10)

---

## Pergunta 26

**Severidade:** Moderado · **Unit:** `openings`
**Contexto:** openings/sync.py:clear (l. 96-106)
**Spec afetada:** `_reversa_sdd/openings/edge-cases.md`
**Pergunta:** Objetos do usuário postos como filhos do marco ou da folha devem sobreviver quando a porta real é refeita?
**Impacto:** Hoje clear apaga children_recursive da montagem inteira: um objeto do usuário pendurado nela some sem aviso a cada mudança de medida
**Recomendação do Reviewer:** Sim: apagar só objetos criados pela montagem (marcados, ex. com btm_opening_frame ou uma marca própria) e reparentar os demais para a caixa

✅ Respondida

**Resposta:** aceito (recomendação do Reviewer adotada pelo titular em 2026-10-10)

---

## Pergunta 27

**Severidade:** Moderado · **Unit:** `aggregates`
**Contexto:** caffmob_draw/aggregates/convert.py:unconvert
**Spec afetada:** `_reversa_sdd/aggregates/edge-cases.md`
**Pergunta:** Desconverter (e o Delete com 'Apagar também os agregados' desligado) deve deixar o objeto onde está agora, em vez de voltar à matriz da época da conversão?
**Impacto:** Agregado de um pai que foi movido 'salta' de volta para a posição antiga, contrariando 'os agregados ficam soltos na mesma posição' (EC-02)
**Recomendação do Reviewer:** Manter a posição atual (matriz de mundo corrente), devolvendo só o pai original; é o que a opção do Delete promete

✅ Respondida

**Resposta:** aceito (recomendação do Reviewer adotada pelo titular em 2026-10-10)

---

## Pergunta 28

**Severidade:** Moderado · **Unit:** `aggregates`
**Contexto:** caffmob_draw/aggregates/apply.py:local_box
**Spec afetada:** `_reversa_sdd/aggregates/edge-cases.md`
**Pergunta:** Agregado com pai Empty (grupo, esquadria, raiz de FBX) deve usar a caixa da união das peças (group.object_corners)?
**Impacto:** Hoje usa o bound_box do Empty (−1 em tudo segundo a API): u/v presos em 0 e posição degenerada (EC-01)
**Recomendação do Reviewer:** Sim, usar a união das malhas como move_over e selection já fazem; confirmar antes o valor do bound_box de Empty no 5.2 com um teste de fumaça

✅ Respondida

**Resposta:** aceito (recomendação do Reviewer adotada pelo titular em 2026-10-10)

---

## Pergunta 29

**Severidade:** Moderado · **Unit:** `aggregates`
**Contexto:** caffmob_draw/aggregates/collision.py:_excluded
**Spec afetada:** `_reversa_sdd/aggregates/edge-cases.md`
**Pergunta:** Folha cujo pai não pertence a módulo (ex.: parede) deve excluir do contato só o pai, e não toda a subárvore dele?
**Impacto:** Com o pai = parede, nenhum módulo ou porta filho da parede conta como obstáculo (EC-07)
**Recomendação do Reviewer:** Excluir só o pai e a própria folha quando module_root_of(pai) é None

✅ Respondida

**Resposta:** aceito (recomendação do Reviewer adotada pelo titular em 2026-10-10)

---

## Pergunta 30

**Severidade:** Moderado · **Unit:** `aggregates`
**Contexto:** caffmob_draw/aggregates/leaf.py:update_open; sweep.py
**Spec afetada:** `_reversa_sdd/aggregates/requirements.md`
**Pergunta:** Mudar sentido/ângulo/curso com a folha aberta deve passar pela varredura, e a varredura deve refinar obstáculos finos (passo menor ou teste de volume varrido)?
**Impacto:** A folha atravessa objetos ao trocar o sentido (EC-06) e pode atravessar obstáculos finos entre amostras (EC-05)
**Recomendação do Reviewer:** Ao mudar swing_sign/max_angle/travel, fechar (fração 0) e reabrir pela varredura; manter o passo atual até haver caso real de obstáculo fino

✅ Respondida

**Resposta:** aceito (recomendação do Reviewer adotada pelo titular em 2026-10-10)

---

## Pergunta 31

**Severidade:** Moderado · **Unit:** `collision`
**Contexto:** caffmob_draw/collision/rules.py:TOLERANCE/evaluate
**Spec afetada:** `_reversa_sdd/collision/requirements.md`
**Pergunta:** Encostar com sobreposição de exatamente 1 mm deve contar como colisão? Se não, a comparação deve ter folga numérica (depth <= TOLERANCE + 1e-9)?
**Impacto:** Hoje o mesmo encosto de 1 mm é ou não colisão conforme o arredondamento das coordenadas (resultado instável para medidas redondas em mm)
**Recomendação do Reviewer:** Usar depth <= TOLERANCE + 1e-9: torna 1,0 mm estável como 'encostar', que é a intenção de 004 RN-11

✅ Respondida

**Resposta:** aceito (recomendação do Reviewer adotada pelo titular em 2026-10-10)

---

## Pergunta 32

**Severidade:** Moderado · **Unit:** `collision`
**Contexto:** caffmob_draw/collision/ops_collision.py:BTM_OT_CollisionPushOut
**Spec afetada:** `_reversa_sdd/collision/requirements.md`
**Pergunta:** 'Afastar até encostar' deve ter prévia e mover o item selecionado (004 RF-26), ou manter o movimento direto de name_a?
**Impacto:** Em ITEM×ITEM move o de nome menor, que pode não ser o que o usuário escolheu; com resultado desatualizado usa o push antigo (EC-06)
**Recomendação do Reviewer:** Mover o selecionado quando ele for um dos dois (invertendo o push) e recusar com resultado desatualizado; prévia só se houver pedido

✅ Respondida

**Resposta:** aceito (recomendação do Reviewer adotada pelo titular em 2026-10-10)

---

## Pergunta 33

**Severidade:** Moderado · **Unit:** `collision`
**Contexto:** caffmob_draw/collision/scan.py:_confirm
**Spec afetada:** `_reversa_sdd/collision/edge-cases.md`
**Pergunta:** A confirmação pela malha deve tratar item totalmente contido num objeto fino (teste de ponto dentro da malha)?
**Impacto:** Item embutido na espessura de uma parede sem cruzar faces pode sumir da lista e o painel dizer 'Sem colisões' (EC-01), contrariando 004 RN-14
**Recomendação do Reviewer:** Sim: quando BVH não acusa e o SAT acusa, testar o centro do item contra a malha fina (ray-cast de paridade); validar antes no Blender

✅ Respondida

**Resposta:** aceito (recomendação do Reviewer adotada pelo titular em 2026-10-10)

---

## Pergunta 34

**Severidade:** Moderado · **Unit:** `collision`
**Contexto:** caffmob_draw/collision/stale.py:on_depsgraph_update; scan.py:check_moved
**Spec afetada:** `_reversa_sdd/collision/edge-cases.md`
**Pergunta:** Objetos novos, apagados ou renomeados após a verificação devem deixar o resultado desatualizado, e check_moved sem verificação prévia deve marcar checked?
**Impacto:** Painel pode seguir 'Sem colisões em N item(ns).' com módulo novo colidindo (EC-03, EC-07) e linhas de check_moved nunca ficam desatualizadas (EC-04)
**Recomendação do Reviewer:** Marcar stale para qualquer objeto que _kind_of aceitaria e não está em checked_names; é barato e fecha a garantia de RN-12

✅ Respondida

**Resposta:** aceito (recomendação do Reviewer adotada pelo titular em 2026-10-10)

---

## Pergunta 35

**Severidade:** Moderado · **Unit:** `collision`
**Contexto:** caffmob_draw/collision/scan.py:_kind_of; panels.py:BTM_PT_ItemCollision
**Spec afetada:** `_reversa_sdd/collision/edge-cases.md`
**Pergunta:** Grupos soltos (SketchUp, biblioteca de objetos) devem entrar na colisão, e o painel do item deve editar o override do agregado em vez do da raiz do módulo?
**Impacto:** Grupos importados nunca aparecem na colisão (EC-15); desligar a colisão de um agregado pelo painel desliga o módulo inteiro (EC-16)
**Recomendação do Reviewer:** Incluir a raiz de free_group como ITEM fino; no painel, usar o próprio objeto ativo quando ele é agregado

✅ Respondida

**Resposta:** aceito (recomendação do Reviewer adotada pelo titular em 2026-10-10)

---

## Pergunta 36

**Severidade:** Moderado · **Unit:** `stick`
**Contexto:** stick/apply.py:on_depsgraph_update + linked (docstring linhas 9-10)
**Spec afetada:** `_reversa_sdd/stick/edge-cases.md`
**Pergunta:** Trocar o pai de um item grudado fora do plugin (Ctrl+P/Alt+P) deve desfazer o vínculo com aviso "Vínculo perdido", como promete a docstring de apply.py? Hoje o vínculo fica órfão: o painel continua dizendo "Elemento filho de", os campos não movem nada e o hospedeiro antigo ainda lista o item.
**Impacto:** Estado inconsistente visível no painel e na lista "Elementos filhos"; a colisão continua ignorando o par item × hospedeiro antigo (collision/scan._links lê btm_stick.host).
**Recomendação do Reviewer:** Sim: no handler, tratar is_stuck com host presente e parent != host como vínculo perdido (lose_link). Fica coerente com a docstring e não exige UI nova.

✅ Respondida

**Resposta:** aceito (recomendação do Reviewer adotada pelo titular em 2026-10-10)

---

## Pergunta 37

**Severidade:** Moderado · **Unit:** `stick`
**Contexto:** stick/apply.py:index/invalidate (EC-01, EC-03)
**Spec afetada:** `_reversa_sdd/stick/edge-cases.md`
**Pergunta:** Quando o hospedeiro é apagado pelo Outliner ou renomeado, o vínculo deve ser atualizado na hora? Hoje o índice por nome só é refeito depois de grudar, desgrudar, abrir ou desfazer, então o item fica com is_stuck sem hospedeiro, ou deixa de acompanhar a medida do hospedeiro renomeado.
**Impacto:** "Vínculo perdido" atrasado; o item pode saltar de lugar ao perder o pai; mudar a medida do hospedeiro renomeado não reposiciona os grudados.
**Recomendação do Reviewer:** Sim: no handler, invalidar o índice quando algum update traz um objeto com btm_stick, ou guardar o hospedeiro pela referência (PointerProperty) em vez do nome. É barato e elimina EC-01/EC-03.

✅ Respondida

**Resposta:** aceito (recomendação do Reviewer adotada pelo titular em 2026-10-10)

---

## Pergunta 38

**Severidade:** Moderado · **Unit:** `stick`
**Contexto:** stick/link.py:link_in_place/release; settle.run; migrate.run (EC-04)
**Spec afetada:** `_reversa_sdd/stick/requirements.md`
**Pergunta:** "Desgrudar" um módulo que está na parede deve ser durável? Hoje ele volta a ser vinculado no próximo assentar com pose nova ou na próxima abertura do arquivo (stick_migrated é gravado e nunca lido).
**Impacto:** O comando Desgrudar parece não funcionar para módulos de parede; o usuário não tem como manter um módulo na parede sem acompanhar a espessura.
**Recomendação do Reviewer:** Tornar durável: gravar uma marca (ex. btm_stick.opt_out) no release de item cujo orig_parent é parede e respeitá-la em settle.run/migrate.run. Consultar stick_migrated não basta, porque o assentar também vincula.

✅ Respondida

**Resposta:** aceito (recomendação do Reviewer adotada pelo titular em 2026-10-10)

---

## Pergunta 39

**Severidade:** Moderado · **Unit:** `stick`
**Contexto:** stick/ops_stick.py:item_of/BTM_OT_StickToFace.poll; panels.py:poll (EC-18)
**Spec afetada:** `_reversa_sdd/stick/edge-cases.md`
**Pergunta:** O comando Grudar deve aceitar parede, piso, teto, cota e objetos não-item como item? O poll e o painel aceitam qualquer objeto ativo (uma parede pode virar filha de outro objeto); só o menu de contexto restringe aos tipos de item.
**Impacto:** Uma parede grudada em outro objeto passa a herdar transformações dele, o que pode bagunçar a planta.
**Recomendação do Reviewer:** Não: alinhar poll e painel ao filtro _ITEM_KINDS do menu de contexto (MODULE, FRONT, PART, GEOMETRY, OBSTACLE e malha OTHER).

✅ Respondida

**Resposta:** aceito (recomendação do Reviewer adotada pelo titular em 2026-10-10)

---

## Pergunta 40

**Severidade:** Moderado · **Unit:** `customize`
**Contexto:** customize/adapters/*:_apply_pull/_set_pull_position; props.PULL_POSITION_ITEMS 'SIDE' (EC-05)
**Spec afetada:** `_reversa_sdd/customize/requirements.md`
**Pergunta:** O que a posição de puxador "Lateral" (SIDE) deve fazer? Nenhum adaptador a trata (no btm cai no meio da altura), mas ela aparece no menu.
**Impacto:** O usuário escolhe "Lateral" e nada muda (ou fica igual a Meio no btm).
**Recomendação do Reviewer:** Se não houver regra de produto definida, tirar SIDE de PULL_POSITION_ITEMS (manter só o valor no domínio para manifestos antigos); se houver, definir a distância da borda da dobradiça por biblioteca.

✅ Respondida

**Resposta:** aceito (recomendação do Reviewer adotada pelo titular em 2026-10-10)

---

## Pergunta 41

**Severidade:** Moderado · **Unit:** `customize`
**Contexto:** customize/adapters/frameless.py:set_front (change_bay_opening, EC-04)
**Spec afetada:** `_reversa_sdd/customize/edge-cases.md`
**Pergunta:** Ao trocar um vão para 2 a 4 gavetas no frameless, a personalização do vão antigo (material das frentes, estilo, puxador, interior) deve passar para os vãos novos? Hoje ela se perde (confirmado no Blender 5.2).
**Impacto:** O usuário perde material/estilo/puxador escolhidos ao dividir em gavetas e precisa refazer em cada vão novo.
**Recomendação do Reviewer:** Copiar btm_custom do vão antigo para cada vão novo (exceto interior), porque é o que o usuário espera de "trocar só a frente".

✅ Respondida

**Resposta:** aceito (recomendação do Reviewer adotada pelo titular em 2026-10-10)

---

## Pergunta 42

**Severidade:** Moderado · **Unit:** `cabinet_editor`
**Contexto:** panels_structure.py:draw_assembly; panels_backs.py; bridge.py:read_state/set_assembly
**Spec afetada:** `_reversa_sdd/cabinet_editor/edge-cases.md`
**Pergunta:** A Montagem (LATERAL/BASE) mudada no painel do editor deve entrar no rascunho (Ctrl+Z, Cancelar e Aplicar) como as outras edições? Hoje ela é gravada direto em btm_cabinet.assembly, fora da fila, não faz parte do EditorState e Cancelar não a desfaz; SET_ASSEMBLY existe na ponte mas ninguém o enfileira.
**Impacto:** Cancelar o editor deixa o módulo com a montagem nova: altera o projeto do usuário sem passo de desfazer próprio do editor.
**Recomendação do Reviewer:** Enfileirar SET_ASSEMBLY e incluir assembly no EditorState: a infraestrutura já existe e mantém a promessa do Cancelar.

✅ Respondida

**Resposta:** aceito (recomendação do Reviewer adotada pelo titular em 2026-10-10)

---

## Pergunta 43

**Severidade:** Moderado · **Unit:** `cabinet_editor`
**Contexto:** ops_editor.py:BTM_OT_CabinetEditorModal.modal (linhas 390-397)
**Spec afetada:** `_reversa_sdd/cabinet_editor/edge-cases.md`
**Pergunta:** Com pedidos na fila, OK e Cancelar devem executar a fila antes de encerrar? Hoje `request` é testado antes de `process` e os pedidos pendentes são descartados (EC-02).
**Impacto:** Um valor digitado e confirmado com OK no mesmo ciclo do modal não entra no módulo.
**Recomendação do Reviewer:** Rodar `process` antes de tratar `request == 'ok'` (e descartar no 'cancel'): custo baixo, elimina perda silenciosa.

✅ Respondida

**Resposta:** aceito (recomendação do Reviewer adotada pelo titular em 2026-10-10)

---

## Pergunta 44

**Severidade:** Moderado · **Unit:** `cabinet_editor`
**Contexto:** bays.py:apply; divisions.py:resolve/validate
**Spec afetada:** `_reversa_sdd/cabinet_editor/edge-cases.md`
**Pergunta:** Mudar o Número de vãos quando já existe uma divisória comum em s0 deve ser recusado com aviso, reorganizar as divisões ou continuar gerando DIV-003 (EC-07)?
**Impacto:** O usuário fica com OK e Aplicar bloqueados por uma divisória órfã criada pelo próprio editor.
**Recomendação do Reviewer:** Recusar com mensagem clara quando s0 já está cortado por divisória não bay: mais simples e previsível.

✅ Respondida

**Resposta:** aceito (recomendação do Reviewer adotada pelo titular em 2026-10-10)

---

## Pergunta 45

**Severidade:** Moderado · **Unit:** `cabinet_editor`
**Contexto:** scene_slides.py:apply/missing_depth
**Spec afetada:** `_reversa_sdd/cabinet_editor/edge-cases.md`
**Pergunta:** Os deslizantes devem ocupar sempre o primeiro vão-raiz inteiro (hoje) ou o subvão escolhido / todos os vãos (EC-08)?
**Impacto:** Em armário com 2+ vãos as folhas atravessam as divisórias de vão e o curso livre tende a BLOCKED.
**Recomendação do Reviewer:** Usar o vão da biblioteca do subvão escolhido, como Portas e Gavetas, ou recusar em armário com bays.

✅ Respondida

**Resposta:** aceito (recomendação do Reviewer adotada pelo titular em 2026-10-10)

---

## Pergunta 46

**Severidade:** Moderado · **Unit:** `cabinet_editor`
**Contexto:** ops_actions.py:_division_payload; catalog.py:ITEMS (DIV_NO_RECESS/DIV_RECESS)
**Spec afetada:** `_reversa_sdd/cabinet_editor/edge-cases.md`
**Pergunta:** Os itens 'Interna s/ Recuo — Tras 15mm' e 'c/ Recuo — Tras 15mm' devem aplicar o recuo de trás de 15 mm do catálogo? Hoje só o recuo da frente vem do item; o de trás vem do campo 'Recuo atrás' (desligado por padrão).
**Impacto:** A chapa sai sem o recuo de trás que o rótulo promete; muda a lista de corte.
**Recomendação do Reviewer:** Aplicar back = 15 mm com use_back = True pelo item, como já é feito com a frente.

✅ Respondida

**Resposta:** aceito (recomendação do Reviewer adotada pelo titular em 2026-10-10)

---

## Pergunta 47

**Severidade:** Moderado · **Unit:** `cabinet_editor`
**Contexto:** appliances.py:layout (laço `for code in reversed(codes)`)
**Spec afetada:** `_reversa_sdd/cabinet_editor/design.md`
**Pergunta:** No painel Forno/Micro o forno deve ficar embaixo (comentário do código) ou o micro embaixo (o que o código faz hoje)?
**Impacto:** Posição dos eletros de referência atrás do painel; o recorte é o mesmo, mas a montagem mostrada fica invertida em relação ao comentário.
**Recomendação do Reviewer:** Forno embaixo (convenção de torre quente e o próprio comentário): trocar `reversed(codes)` por `codes` na ordem de baixo para cima.

✅ Respondida

**Resposta:** aceito (recomendação do Reviewer adotada pelo titular em 2026-10-10)

---

## Pergunta 48

**Severidade:** Moderado · **Unit:** `standards`
**Contexto:** io_json.py:values_to_document/import_definition
**Spec afetada:** `_reversa_sdd/standards/requirements.md`
**Pergunta:** A Montagem (LATERAL/BASE) deve ser gravada e lida no .btmdim.json? Hoje não é: uma definição 'Base passante' exportada volta como LATERAL, enquanto o XML do Promob a preserva em CAFF_MONTAGEM.
**Impacto:** Ida e volta pelo formato próprio perde a montagem e muda os módulos a que a definição for aplicada.
**Recomendação do Reviewer:** Incluir 'assembly' no documento (opcional na leitura, LATERAL como padrão) sem subir schema_version: compatível com arquivos antigos.

✅ Respondida

**Resposta:** aceito (recomendação do Reviewer adotada pelo titular em 2026-10-10)

---

## Pergunta 49

**Severidade:** Moderado · **Unit:** `standards`
**Contexto:** dimension_schema.py:validate
**Spec afetada:** `_reversa_sdd/standards/edge-cases.md`
**Pergunta:** Valores não finitos (NaN, inf) devem ser recusados como 'Valor Inválido'? Hoje NaN passa e inf só falha pela faixa.
**Impacto:** NaN vindo de JSON ou script chega a definition_values, defaults e à geometria sem guarda.
**Recomendação do Reviewer:** Recusar com math.isfinite em validate: uma linha, sem efeito nos valores válidos.

✅ Respondida

**Resposta:** aceito (recomendação do Reviewer adotada pelo titular em 2026-10-10)

---

## Pergunta 50

**Severidade:** Moderado · **Unit:** `standards`
**Contexto:** ops_standards.py:BTM_OT_StandardsSetActive.execute → ApplyScene → ApplyDiffer; apply_core.plan
**Spec afetada:** `_reversa_sdd/standards/edge-cases.md`
**Pergunta:** Depois de 'Definir ativa' com Sim na 1ª pergunta, os módulos que acabaram de ser atualizados podem reaparecer na lista 'difere' da 2ª pergunta (EC-01)? Isso é aceito ou a 2ª pergunta deve excluí-los?
**Impacto:** A 2ª pergunta mostra módulos já atualizados e Sim refaz a geometria deles.
**Recomendação do Reviewer:** Excluir da 2ª pergunta os nomes já aplicados na 1ª (passar a lista ou recalcular o plano com o uid novo).

✅ Respondida

**Resposta:** aceito (recomendação do Reviewer adotada pelo titular em 2026-10-10)

---

## Pergunta 51

**Severidade:** Moderado · **Unit:** `standards`
**Contexto:** ops_standards.py:BTM_OT_StandardsConfigurator.invoke/execute; BTM_OT_StandardsDuplicate.execute
**Spec afetada:** `_reversa_sdd/standards/edge-cases.md`
**Pergunta:** No Configurador aberto numa embutida, depois de 'Duplicar para editar', o botão rotulado 'Fechar' deve aplicar as edições na cópia (hoje aplica) ou só fechar (EC-07)?
**Impacto:** Um botão chamado 'Fechar' grava valores e dispara as perguntas de aplicação.
**Recomendação do Reviewer:** Manter a gravação na cópia (o usuário pediu para editar) e ajustar o rótulo ao reabrir; confirmar no Blender se o diálogo continua aberto após duplicar.

✅ Respondida

**Resposta:** aceito (recomendação do Reviewer adotada pelo titular em 2026-10-10)

---

## Pergunta 52

**Severidade:** Moderado · **Unit:** `standards`
**Contexto:** migration.py:_has_legacy_cabinets/migrate_scene
**Spec afetada:** `_reversa_sdd/standards/edge-cases.md`
**Pergunta:** M-02 deve ativar 'Padrão EUA (HB5)' também em projetos herdados só com gabinetes face frame? Hoje só frameless/closets contam (EC-13).
**Impacto:** Projeto face frame antigo passa a ter o padrão BR como ativo e o M-03 carimba o uid BR nas raízes.
**Recomendação do Reviewer:** Incluir a tag de face frame em _has_legacy_cabinets, se a intenção de M-02 é não mudar medidas de projetos do Home Builder.

✅ Respondida

**Resposta:** aceito (recomendação do Reviewer adotada pelo titular em 2026-10-10)

---

## Pergunta 53

**Severidade:** Moderado · **Unit:** `standards`
**Contexto:** io_promob.py:write_dimensionexport (ID extra CAFF_MONTAGEM)
**Spec afetada:** `_reversa_sdd/standards/requirements.md`
**Pergunta:** O XML exportado com o atributo extra CAFF_MONTAGEM abre sem erro no Promob? A docstring afirma que o Promob ignora IDs desconhecidos, mas não houve teste.
**Impacto:** Se o Promob recusar o arquivo, a exportação deixa de servir para interoperabilidade.
**Recomendação do Reviewer:** Testar uma vez no Promob; se recusar, exportar CAFF_MONTAGEM só sob opção.

✅ Respondida

**Resposta:** aceito (recomendação do Reviewer adotada pelo titular em 2026-10-10)

---

## Pergunta 54

**Severidade:** Moderado · **Unit:** `legacy`
**Contexto:** legacy/convert.py:convert_scene (138-140); legacy/ops.py:BTM_OT_LegacyConvert.execute
**Spec afetada:** `_reversa_sdd/legacy/edge-cases.md`
**Pergunta:** Quando a construção de um armário falha no meio do lote, o lote deve ter rollback (apagar os módulos já criados e avisar), ou basta o comportamento atual (traceback, módulo parcial 'BTM_Cabinet' ao lado dos originais, que o Ctrl+Z remove)?
**Impacto:** Hoje o usuário vê um erro Python e um módulo órfão sem nome útil; se não desfizer, o projeto fica com peças duplicadas.
**Recomendação do Reviewer:** Rollback com try/except no operador: remover os módulos criados, reportar ERROR com o nome do armário e devolver CANCELLED. É barato e evita depender do usuário lembrar do Ctrl+Z.

✅ Respondida

**Resposta:** aceito (recomendação do Reviewer adotada pelo titular em 2026-10-10)

---

## Pergunta 55

**Severidade:** Moderado · **Unit:** `legacy`
**Contexto:** legacy/convert_core.py:translate; legacy/convert.py:_other_fronts
**Spec afetada:** `_reversa_sdd/legacy/edge-cases.md`
**Pergunta:** Duas regras de contagem divergem do plano da 012: (a) portas somam entre aberturas (2 portas em vãos diferentes = DOUBLE sem perda), quando o D-24 dizia 'a maior abertura manda, as outras são perda'; (b) no face frame, PULLOUT/TILT_OUT/INSET_PANEL em gaiola folha são contados duas vezes (Gavetas/Painéis + Frentes especiais). Qual é a regra pretendida?
**Impacto:** O relatório de perdas pode subestimar (portas) ou duplicar (face frame) o que se perdeu; o usuário decide se refaz o armário com base nele.
**Recomendação do Reviewer:** Manter a soma de portas (o módulo CAFFMob só tem uma frente e DOUBLE é a melhor aproximação) e eliminar a dupla contagem no face frame, ignorando em _other_fronts as gaiolas folha já lidas pelo adaptador.

✅ Respondida

**Resposta:** aceito (recomendação do Reviewer adotada pelo titular em 2026-10-10)

---

## Pergunta 56

**Severidade:** Moderado · **Unit:** `legacy`
**Contexto:** legacy/convert.py:_build (padrão ativo); legacy/convert_core.py:LOSS_LABELS
**Spec afetada:** `_reversa_sdd/legacy/requirements.md`
**Pergunta:** O relatório deve declarar como perda a troca de chapas, espessuras e montagem pelas do padrão ativo, a redistribuição das prateleiras e as frentes não lidas quando o adaptador falha (hoje sai 'sem perdas')?
**Impacto:** Um armário convertido pode sair com corte de chapas diferente do original e o relatório dizer 'sem perdas', o que afeta orçamento e produção.
**Recomendação do Reviewer:** Sim para a falha do adaptador (uma linha 'frentes não lidas'), porque esconde perda real; para o padrão ativo, uma nota geral no topo do relatório basta.

✅ Respondida

**Resposta:** aceito (recomendação do Reviewer adotada pelo titular em 2026-10-10)

---

## Pergunta 57

**Severidade:** Moderado · **Unit:** `library_panel`
**Contexto:** library_panel/categories.py:create; customize/library_io.py:paths_for (manifest.file_stem)
**Spec afetada:** `_reversa_sdd/library_panel/edge-cases.md`
**Pergunta:** Uma categoria com caractere que o nome de arquivo troca (ex. 'Pia: Lavabo') grava os módulos em 'Pia_ Lavabo/', eles não aparecem na categoria e surge uma categoria nova 'Pia_ Lavabo' (COZ). A validação do nome deve recusar esses caracteres, ou a pasta da categoria deve usar o mesmo nome saneado?
**Impacto:** Confirmado por sonda: o usuário salva um módulo e não o encontra na categoria, e ganha uma categoria duplicada na linha errada.
**Recomendação do Reviewer:** Recusar na validate_name os mesmos caracteres de manifest.file_stem (e ponto final). É uma linha, evita o problema também no Windows, onde a pasta nem seria criada.

✅ Respondida

**Resposta:** aceito (recomendação do Reviewer adotada pelo titular em 2026-10-10)

---

## Pergunta 58

**Severidade:** Moderado · **Unit:** `library_panel`
**Contexto:** library_panel/categories.py:load/create/set_line/save
**Spec afetada:** `_reversa_sdd/library_panel/edge-cases.md`
**Pergunta:** Com categories.json corrompido, criar categoria ou trocar linha sobrescreve o arquivo e as categorias do usuário perdem a linha (as sem pasta somem). Os avisos de leitura também não aparecem em lugar nenhum. Devemos guardar uma cópia do arquivo corrompido antes de regravar e mostrar o aviso no painel?
**Impacto:** Perda silenciosa da configuração de categorias do usuário.
**Recomendação do Reviewer:** Antes de save, se a última leitura teve aviso de arquivo inválido, renomear para categories.json.bak e mostrar o aviso uma vez (save_feedback). Barato e protege o dado do usuário.

✅ Respondida

**Resposta:** aceito (recomendação do Reviewer adotada pelo titular em 2026-10-10)

---

## Pergunta 59

**Severidade:** Moderado · **Unit:** `object_library`
**Contexto:** object_library/ops.py:BTM_OT_ObjectInsert._follow (91-94)
**Spec afetada:** `_reversa_sdd/object_library/edge-cases.md`
**Pergunta:** Inserir pelo botão da barra lateral (o caminho normal da UI) não faz o objeto acompanhar o mouse: o modal recebe a região UI sem RegionView3D. Corrigimos fazendo _follow usar a região WINDOW da área sob o mouse?
**Impacto:** Confirmado por sonda: o usuário clica no objeto da biblioteca e ele fica parado no cursor 3D; a promessa de 'mova para posicionar' do cabeçalho não acontece.
**Recomendação do Reviewer:** Sim: em _follow, achar a região WINDOW da área (e converter event.mouse_x/y para coordenadas dela) quando context.region_data for None. Correção pequena e localizada; acrescentar o caso ao teste do modal (TT-03).

✅ Respondida

**Resposta:** aceito (recomendação do Reviewer adotada pelo titular em 2026-10-10)

---

## Pergunta 60

**Severidade:** Moderado · **Unit:** `object_library`
**Contexto:** object_library/retexture.py:image_material; item_io.py:save (RELATIVE_ALL)
**Spec afetada:** `_reversa_sdd/object_library/edge-cases.md`
**Pergunta:** A textura de imagem própria usa coordenadas de objeto (a escala do objeto muda o tamanho aparente) e a imagem não é empacotada no .blend do item (caminho relativo). Deve-se empacotar a imagem ao salvar o item e compensar a escala?
**Impacto:** Mover ou apagar a imagem original quebra a textura dos itens salvos; objetos com escala ≠ 1 mostram a textura fora da escala real prometida.
**Recomendação do Reviewer:** Empacotar a imagem ao salvar na biblioteca (image.pack()), porque o item deve ser portátil; a escala pode ficar como está, com aplicar escala antes como recomendação.

✅ Respondida

**Resposta:** aceito (recomendação do Reviewer adotada pelo titular em 2026-10-10)

---

## Pergunta 61

**Severidade:** Moderado · **Unit:** `inspection`
**Contexto:** gizmo.py:_arrow_get/_arrow_set; adapters/aggregate_leaf.py
**Spec afetada:** `_reversa_sdd/inspection/edge-cases.md`
**Pergunta:** Folha convertida de correr (SLIDE) ativa: o gizmo chama front.travel(), que não existe em AggregateLeafFront (AttributeError a cada redesenho). A seta deve aparecer com o curso real da folha ou ficar escondida para folhas de correr?
**Impacto:** Erro repetido no console e seta quebrada ao selecionar uma folha de correr convertida (feature 003); hoje sem teste (TT-04).
**Recomendação do Reviewer:** Implementar travel() em AggregateLeafFront com o curso de correr da folha (aggregates/leaf.py) e, por segurança, um travel() na base Front devolvendo 0 com a seta oculta quando 0: mantém o contrato uniforme entre adaptadores.

✅ Respondida

**Resposta:** aceito (recomendação do Reviewer adotada pelo titular em 2026-10-10)

---

## Pergunta 62

**Severidade:** Moderado · **Unit:** `inspection`
**Contexto:** fronts.py:open_value; gizmo.py:_snap; pivot_math.py:snap_angle
**Spec afetada:** `_reversa_sdd/inspection/edge-cases.md`
**Pergunta:** Folhas convertidas com max_angle > 90° (ex. 110°): clique, 'Abrir 90°' e o dial param em 90°; só a varredura de interferência vai até 110°. O dial (e o clique) devem chegar ao max_angle da folha?
**Impacto:** Usuário não consegue abrir pela inspeção até o máximo configurado; a interferência verifica um arco maior do que o usuário consegue ver.
**Recomendação do Reviewer:** Manter 'Abrir 90°' em 90° (o nome promete isso), mas limitar o dial por front.max_value em vez do teto fixo de 90: coerente com a varredura e com o max_angle da 003.

✅ Respondida

**Resposta:** aceito (recomendação do Reviewer adotada pelo titular em 2026-10-10)

---

## Pergunta 63

**Severidade:** Moderado · **Unit:** `inspection`
**Contexto:** save_guard.py:close_for_save; adapters/frameless.py:get; ops_inspect.py:modal
**Spec afetada:** `_reversa_sdd/inspection/edge-cases.md`
**Pergunta:** Salvar (Ctrl+S) no meio de uma animação ou com pending do gizmo grava a pose intermediária (delta_*) porque get() ainda lê btm_open antigo; e um objeto compartilhado entre cenas com save_fronts_open diferente é salvo fechado. O salvar fechado deve concluir/zerar animações pendentes antes de fechar e respeitar a opção por objeto?
**Impacto:** Arquivo salvo com frente frameless meio aberta (RN-14 da 001 diz que o arquivo é salvo fechado).
**Recomendação do Reviewer:** Em save_pre, concluir os tweens do _active e o pending do gizmo (commit do alvo) antes de close_for_save; para cenas compartilhadas, aceitar o comportamento atual (fecha) por ser o lado seguro.

✅ Respondida

**Resposta:** aceito (recomendação do Reviewer adotada pelo titular em 2026-10-10)

---

## Pergunta 64

**Severidade:** Moderado · **Unit:** `molding`
**Contexto:** packages.py:_PROFILE_OUTLINES; ops.py:_spawn_sweep; engine.py:chain_sweep_points
**Spec afetada:** `_reversa_sdd/molding/tasks.md`
**Pergunta:** Validação visual no Blender 5.2: o perfil embutido (X negativo = para dentro) aparece do lado certo do bevel, os retornos nas pontas acabadas e as meias-esquadrias saem corretos? Inclui corridas só de cantos (EC-07, sentido não normalizado) e pai com escala/inclinação (EC-08).
**Impacto:** Se o lado do bevel estiver invertido, toda moldura nasce dentro do armário; sem validação não há referência para reimplementar.
**Recomendação do Reviewer:** Rodar um smoke visual com 3 aéreos face frame, um canto em L e uma ilha (TT-03) e conferir com captura de tela; o código está coerente (direita do percurso = fora), então a expectativa é o lado correto, salvo EC-07/EC-08.

✅ Respondida

**Resposta:** aceito (recomendação do Reviewer adotada pelo titular em 2026-10-10)

---

## Pergunta 65

**Severidade:** Moderado · **Unit:** `geometry_free`
**Contexto:** ops_edit.py:BTM_OT_GeometryDuplicate/BTM_OT_GeometryMirror/BTM_OT_GeometryDelete
**Spec afetada:** `_reversa_sdd/geometry_free/edge-cases.md`
**Pergunta:** Com parent, duplicar e espelhar mandam a peça para outro lugar (EC-09) e excluir faz os filhos (agregados, cotas) saltarem para a origem do mundo (EC-14). Qual o comportamento desejado: duplicar/espelhar no X local relativo ao pai e, ao excluir, apagar os filhos ou mantê-los na posição mundial?
**Impacto:** Geometria presa a parede/grupo é duplicada/espelhada fora do lugar; agregados presos a uma placa excluída saltam de posição.
**Recomendação do Reviewer:** Duplicar/espelhar calculando no espaço do pai (copy.matrix_world = obj.matrix_world @ Translation((x,0,0)); espelho idem) e, ao excluir, manter os filhos na posição mundial (gravar matrix_world antes de remover): preserva o que o usuário vê.

✅ Respondida

**Resposta:** aceito (recomendação do Reviewer adotada pelo titular em 2026-10-10)

---

## Pergunta 66

**Severidade:** Moderado · **Unit:** `geometry_free`
**Contexto:** mesh.py:sheets
**Spec afetada:** `_reversa_sdd/geometry_free/edge-cases.md`
**Pergunta:** Placa com uma medida do plano menor que a espessura (ex. 600 × 10 mm com espessura 18 mm) é exportada com 10 mm de espessura e 18 mm de largura, sem aviso (EC-02); caixa com espessura ≥ metade gera chapas de 1 mm (EC-03). Deve haver aviso ou recusa na produção?
**Impacto:** Peças com espessura errada no plano de corte e no JSON global.
**Recomendação do Reviewer:** Na placa, exportar sempre thickness como espessura (as outras duas medidas como comprimento × largura) e avisar quando alguma for menor que thickness; na caixa, avisar quando 2t ≥ largura ou altura.

✅ Respondida

**Resposta:** aceito (recomendação do Reviewer adotada pelo titular em 2026-10-10)

---

## Pergunta 67

**Severidade:** Moderado · **Unit:** `revisão cruzada`
**Contexto:** Peça de produção de agregado que também é geometria livre
**Spec afetada:** `_reversa_sdd/aggregates/edge-cases.md EC-23`
**Pergunta:** Geometria livre convertida em agregado deve sair na produção como geometria (chapas) ou como agregado (uma placa)?
**Impacto:** Hoje sai duas vezes com o mesmo uid e o JSON global fica inválido
**Recomendação do Reviewer:** No laço de agregados de geometry_records, pular objetos com btm_geometry.is_geometry

✅ Respondida

**Resposta:** aceito (recomendação do Reviewer adotada pelo titular em 2026-10-10)

---

## Pergunta 68

**Severidade:** Moderado · **Unit:** `revisão cruzada`
**Contexto:** Folha LEAF de porta/janela real ou esquadria na colisão de corpo
**Spec afetada:** `_reversa_sdd/collision/edge-cases.md EC-22`
**Pergunta:** Folhas devem ser ligadas à caixa (IS_WINDOW_BP/IS_ENTRY_DOOR_BP) e à parede hospedeira em _links?
**Impacto:** Possível 'Colisão entre itens' ou 'Penetração em parede' falsa com folha aberta ou espessa
**Recomendação do Reviewer:** Rodar sonda no Blender com porta real aberta a 90° e janela instalada; se reproduzir, ligar a folha à raiz da abertura

✅ Respondida

**Resposta:** aceito (recomendação do Reviewer adotada pelo titular em 2026-10-10)

---

## Pergunta 69

**Severidade:** Moderado · **Unit:** `revisão cruzada`
**Contexto:** Porta real após editar Dim X/Z pelo painel
**Spec afetada:** `_reversa_sdd/openings/edge-cases.md EC-21; selection EC-08`
**Pergunta:** set_dimension de porta/janela deve chamar _sync_opening como o Redimensionar?
**Impacto:** Porta real fica com medidas antigas até 'Atualizar portas e janelas'
**Recomendação do Reviewer:** Chamar doors_windows._sync_opening em editing.set_dimension para ROOM_DOOR/WINDOW

✅ Respondida

**Resposta:** aceito (recomendação do Reviewer adotada pelo titular em 2026-10-10)

---

## Pergunta 70

**Severidade:** Moderado · **Unit:** `revisão cruzada`
**Contexto:** Feature 013 (touchpad no editor de paredes) sem commit
**Spec afetada:** `_reversa_sdd/walls2d/ e _reversa_sdd/canvas2d/ (RN-24/RN-25, CA-20..23, T-18/T-19, gestures.py)`
**Pergunta:** A 013 será commitada ou descartada?
**Impacto:** Se descartada, partes de walls2d/canvas2d e as linhas de compat.trackpad_delta/pinch_delta deixam de valer
**Recomendação do Reviewer:** Commitar a 013 antes de congelar as specs ou marcar esses itens como 'pendente de commit'

✅ Respondida

**Resposta:** aceito (recomendação do Reviewer adotada pelo titular em 2026-10-10)

---

## Pergunta 71

**Severidade:** Cosmético · **Unit:** `canvas2d`
**Contexto:** canvas2d/window.py:open_window/_close (fallback)
**Spec afetada:** `_reversa_sdd/canvas2d/edge-cases.md`
**Pergunta:** No fallback (editor ocupando a área atual), a área deve voltar exatamente ao estado anterior (menus, cabeçalho, região N, barras, imagem) ou basta restaurar o tipo e ligar menus/cabeçalho como hoje?
**Impacto:** Preferências visuais da área do usuário são perdidas após usar o editor
**Recomendação do Reviewer:** Guardar um snapshot mínimo (show_menus, show_region_header, show_region_ui) em open_window e restaurá-lo; custo baixo e sem efeito na janela duplicada

✅ Respondida

**Resposta:** aceito (recomendação do Reviewer adotada pelo titular em 2026-10-10)

---

## Pergunta 72

**Severidade:** Cosmético · **Unit:** `walls2d`
**Contexto:** compat.py:pinch_delta 199-207
**Spec afetada:** `_reversa_sdd/walls2d/requirements.md`
**Pergunta:** O sinal da pinça foi validado em todas as plataformas-alvo (macOS, Wayland, X11/Windows)?
**Impacto:** Pinça invertida numa plataforma
**Recomendação do Reviewer:** Validar à mão com tests/blender_013_trackpad_probe.py em cada plataforma e registrar em investigation.md §6

✅ Respondida

**Resposta:** aceito (recomendação do Reviewer adotada pelo titular em 2026-10-10)

---

## Pergunta 73

**Severidade:** Cosmético · **Unit:** `measure`
**Contexto:** scene_cotas.py:for_object
**Spec afetada:** `_reversa_sdd/measure/requirements.md`
**Pergunta:** A feature 002 RF-18 pede cotas para 'módulos e geometrias'; for_object só aceita MODULE/PART/FRONT. Geometrias devem ter cotas?
**Impacto:** Geometrias não mostram o grupo Cotas no painel nem no overlay
**Recomendação do Reviewer:** Confirmar se fica como Won't nesta versão; se sim, atualizar o RF-18 da 002

✅ Respondida

**Resposta:** aceito (recomendação do Reviewer adotada pelo titular em 2026-10-10)

---

## Pergunta 74

**Severidade:** Cosmético · **Unit:** `measure`
**Contexto:** overlays/selection_cotas.py:_specs; ui/object_properties.py:_cota_getter
**Spec afetada:** `_reversa_sdd/measure/requirements.md`
**Pergunta:** Há meta de desempenho para o recálculo das cotas (ModuleCotas recriado e filhos da parede relistados a cada redesenho e por campo do painel)?
**Impacto:** Sem meta não há como decidir se precisa de cache
**Recomendação do Reviewer:** Medir com uma parede de ~30 módulos; só otimizar se o redesenho passar de alguns ms

✅ Respondida

**Resposta:** aceito (recomendação do Reviewer adotada pelo titular em 2026-10-10)

---

## Pergunta 75

**Severidade:** Cosmético · **Unit:** `move_over`
**Contexto:** caffmob_draw/move_over/ops_drag.py (modal) — feature 002 RF-26/RF-27
**Spec afetada:** `_reversa_sdd/move_over/requirements.md`
**Pergunta:** Esc deve desligar o modo Mover Sobre, e o objeto sob o cursor deve ser realçado no 3D durante o arraste, como a feature 002 pedia?
**Impacto:** Hoje Esc só cancela o arraste/janela e o realce é só a cor da linha e o nome
**Recomendação do Reviewer:** Manter como está (Won't nesta versão) e atualizar a 002; o botão do HUD já desliga o modo e o rótulo A → B já identifica o alvo

✅ Respondida

**Resposta:** aceito (recomendação do Reviewer adotada pelo titular em 2026-10-10)

---

## Pergunta 76

**Severidade:** Cosmético · **Unit:** `move_over`
**Contexto:** move_over (prévia e redesenho)
**Spec afetada:** `_reversa_sdd/move_over/requirements.md`
**Pergunta:** Vale manter a meta da feature 002 (prévia em até 200 ms e redesenho em até 100 ms) e medi-la?
**Impacto:** Sem meta medida, não dá para detectar regressão de desempenho
**Recomendação do Reviewer:** Manter a meta e medir uma vez num projeto com cerca de 100 módulos; sem isso, retirar a meta

✅ Respondida

**Resposta:** aceito (recomendação do Reviewer adotada pelo titular em 2026-10-10)

---

## Pergunta 77

**Severidade:** Cosmético · **Unit:** `selection`
**Contexto:** caffmob_draw/selection/component_select.py:on_depsgraph_update
**Spec afetada:** `_reversa_sdd/selection/requirements.md`
**Pergunta:** Há meta de desempenho para o normalizador com seleções grandes (centenas de peças)?
**Impacto:** A assinatura percorre a seleção inteira a cada depsgraph_update_post
**Recomendação do Reviewer:** Medir uma vez com cerca de 500 objetos selecionados; abaixo de 5 ms por atualização, não definir meta

✅ Respondida

**Resposta:** aceito (recomendação do Reviewer adotada pelo titular em 2026-10-10)

---

## Pergunta 78

**Severidade:** Cosmético · **Unit:** `openings`
**Contexto:** openings/sync.py:sync
**Spec afetada:** `_reversa_sdd/openings/requirements.md`
**Pergunta:** Há meta de tempo para sync (bmesh + várias view_layer.update) em projetos com muitas portas?
**Impacto:** Atualizar portas e janelas e o OK do Editor de Paredes refazem várias montagens em sequência
**Recomendação do Reviewer:** Medir uma vez com 30 portas; sem regressão perceptível (menos de 1 s no total), não definir meta

✅ Respondida

**Resposta:** aceito (recomendação do Reviewer adotada pelo titular em 2026-10-10)

---

## Pergunta 79

**Severidade:** Cosmético · **Unit:** `aggregates`
**Contexto:** caffmob_draw/aggregates/install.py:uninstall; window_props.py
**Spec afetada:** `_reversa_sdd/aggregates/requirements.md`
**Pergunta:** Desinstalar deve usar frame_matrix e o pai anterior para devolver a esquadria ao lugar de antes, como diz a docstring de window_props?
**Impacto:** Hoje a esquadria fica sem pai, dentro da parede, no vão (EC-14); frame_matrix é gravado e nunca lido
**Recomendação do Reviewer:** Manter o comportamento atual (soltar no lugar) e corrigir a docstring; menos risco e é o que o operador anuncia ('fica solta no mesmo lugar')

✅ Respondida

**Resposta:** aceito (recomendação do Reviewer adotada pelo titular em 2026-10-10)

---

## Pergunta 80

**Severidade:** Cosmético · **Unit:** `aggregates`
**Contexto:** caffmob_draw/aggregates/ops_aggregate.py:BTM_OT_AggregateMove
**Spec afetada:** `_reversa_sdd/aggregates/requirements.md`
**Pergunta:** Há meta de desempenho para varredura, measure_free_travel e recorte durante o arraste (a 003 pedia recorte só ao soltar)?
**Impacto:** Cada MOUSEMOVE refaz o cortador e o booleano EXACT (EC-11); em cenas grandes pode travar
**Recomendação do Reviewer:** Medir uma vez numa cena típica; se passar de ~30 ms por movimento, recortar só ao soltar

✅ Respondida

**Resposta:** aceito (recomendação do Reviewer adotada pelo titular em 2026-10-10)

---

## Pergunta 81

**Severidade:** Cosmético · **Unit:** `collision`
**Contexto:** caffmob_draw/collision/scan.py:check_moved
**Spec afetada:** `_reversa_sdd/collision/edge-cases.md`
**Pergunta:** check_moved deve reordenar a lista inteira pela ordem RN-06 e limpar error após sucesso?
**Impacto:** Penetração em parede nova fica atrás de colisões antigas (EC-05) e o erro antigo esconde a lista (EC-10)
**Recomendação do Reviewer:** Sim para as duas: ordenar por sort_key ao regravar e limpar error quando find termina sem exceção

✅ Respondida

**Resposta:** aceito (recomendação do Reviewer adotada pelo titular em 2026-10-10)

---

## Pergunta 82

**Severidade:** Cosmético · **Unit:** `stick`
**Contexto:** stick/apply.py:project/_translate_local (EC-07, EC-08)
**Spec afetada:** `_reversa_sdd/stick/tasks.md`
**Pergunta:** Depois de um giro livre (R) num item grudado, o assentar deve restaurar a orientação em relação à face (004 D-04b)? E num hospedeiro com escala de objeto diferente de 1, os campos u/v/Distância devem ser em metros do mundo?
**Impacto:** Item inclinado continua grudado com a pegada inclinada; digitar 10 mm num hospedeiro com escala 2 afasta 20 mm.
**Recomendação do Reviewer:** Restaurar a orientação no project (reaplicar oriented_matrix + spin) e converter os campos pela escala do hospedeiro; hoje bibliotecas aplicam escala 1, então a segunda parte pode ficar como aviso documentado.

✅ Respondida

**Resposta:** aceito (recomendação do Reviewer adotada pelo titular em 2026-10-10)

---

## Pergunta 83

**Severidade:** Cosmético · **Unit:** `customize`
**Contexto:** customize/ops_customize.py:BTM_OT_CustomizeSetMaterial (target PART); adapters/btm.py:reapply (EC-07)
**Spec afetada:** `_reversa_sdd/customize/edge-cases.md`
**Pergunta:** Material por peça num módulo btm (malha única) ou em malha sem GeoNodeCutpart deve ser aplicado, ou o botão "Peça …" deve sumir nesses casos? Hoje grava, reporta sucesso e nada muda.
**Impacto:** Feedback falso de sucesso; has_custom fica verdadeiro e o gancho perde o atalho sem custo.
**Recomendação do Reviewer:** Esconder/desabilitar o botão de peça quando a biblioteca é BTM ou a peça não é cutpart, com motivo em texto.

✅ Respondida

**Resposta:** aceito (recomendação do Reviewer adotada pelo titular em 2026-10-10)

---

## Pergunta 84

**Severidade:** Cosmético · **Unit:** `cabinet_editor`
**Contexto:** bridge.py:insert_doors/DOOR_FRONTS; props.py:DOOR_REGION_ITEMS
**Spec afetada:** `_reversa_sdd/cabinet_editor/edge-cases.md`
**Pergunta:** A Região da aba Portas (Inferior, Superior, Alta) deve mudar algo além de Basculante? Hoje só FLIP tem efeito (EC-13).
**Impacto:** Opção da interface sem efeito.
**Recomendação do Reviewer:** Se não houver regra de produto, esconder as três regiões sem efeito ou documentar que são só rótulo.

✅ Respondida

**Resposta:** aceito (recomendação do Reviewer adotada pelo titular em 2026-10-10)

---

## Pergunta 85

**Severidade:** Cosmético · **Unit:** `cabinet_editor`
**Contexto:** ops_editor.py:_arrow/process
**Spec afetada:** `_reversa_sdd/cabinet_editor/edge-cases.md`
**Pergunta:** A mensagem 'Selecione uma divisória na vista para mover com as setas' deve aparecer? Hoje process limpa s.error logo depois (EC-01).
**Impacto:** Seta sem seleção não dá retorno ao usuário.
**Recomendação do Reviewer:** Preservar s.error quando a ação o definiu (limpar só antes de executar o pedido).

✅ Respondida

**Resposta:** aceito (recomendação do Reviewer adotada pelo titular em 2026-10-10)

---

## Pergunta 86

**Severidade:** Cosmético · **Unit:** `cabinet_editor`
**Contexto:** bridge.py:apply_state; scene_extras.sync; scene_interiors.apply; scene_slides.apply
**Spec afetada:** `_reversa_sdd/cabinet_editor/requirements.md`
**Pergunta:** É aceitável que cada Ctrl+Z/Ctrl+Y do editor apague e recrie internos, extras e deslizantes (nomes .001 e custo) mesmo sem mudança neles (EC-12)? Há meta de tempo para o desfazer no editor?
**Impacto:** Nomes de objetos podem mudar entre passos; custo cresce com o número de peças.
**Recomendação do Reviewer:** Recriar só quando a parte correspondente do instantâneo difere (como já se faz com divisões).

✅ Respondida

**Resposta:** aceito (recomendação do Reviewer adotada pelo titular em 2026-10-10)

---

## Pergunta 87

**Severidade:** Cosmético · **Unit:** `standards`
**Contexto:** ops_standards.py: Configurador/Aplicar/Definir ativa → ApplyScene → ApplyDiffer (três operadores com UNDO)
**Spec afetada:** `_reversa_sdd/standards/requirements.md`
**Pergunta:** Qual o comportamento esperado de Ctrl+Z depois da sequência Configurador → 1ª pergunta → 2ª pergunta: um passo para tudo ou um por operador? Não foi verificado no Blender.
**Impacto:** O usuário pode precisar de vários Ctrl+Z ou desfazer mais do que esperava.
**Recomendação do Reviewer:** Aceitar um passo por operador (comportamento natural do Blender) e registrar num smoke com janela.

✅ Respondida

**Resposta:** aceito (recomendação do Reviewer adotada pelo titular em 2026-10-10)

---

## Pergunta 88

**Severidade:** Cosmético · **Unit:** `library_panel`
**Contexto:** library_panel/layout_core.py:panel_layout
**Spec afetada:** `_reversa_sdd/library_panel/edge-cases.md`
**Pergunta:** A coluna não tem rolagem nem limite: com muitas categorias, as últimas (inclusive 'Criar categoria') saem da área visível. Há um número máximo de categorias esperado, ou a coluna deve rolar/quebrar?
**Impacto:** Itens inalcançáveis com o painel aberto.
**Recomendação do Reviewer:** Limitar a coluna à altura visível e, acima disso, agrupar as categorias do usuário num item 'Mais…' que abre um popover; evita implementar rolagem em GPU.

✅ Respondida

**Resposta:** aceito (recomendação do Reviewer adotada pelo titular em 2026-10-10)

---

## Pergunta 89

**Severidade:** Cosmético · **Unit:** `library_panel`
**Contexto:** library_panel/props.py, draw.py:_mouse, popover.py:_open; ops_click.register (head=True)
**Spec afetada:** `_reversa_sdd/library_panel/requirements.md`
**Pergunta:** Com duas viewports ou duas janelas, o estado aberto é único (abre em todas) e o hover guarda uma região só; e a ordem efetiva do keymap frente ao HUD e à seleção por componente não foi testada com o HUD ligado. Esse comportamento é aceitável?
**Impacto:** Painel aberto em viewports onde o usuário não clicou; possível clique capturado pelo HUD antes do painel.
**Recomendação do Reviewer:** Aceitar por ora (uso típico é uma viewport) e acrescentar à fumaça de UI um caso com o HUD ligado para fixar a ordem do keymap.

✅ Respondida

**Resposta:** aceito (recomendação do Reviewer adotada pelo titular em 2026-10-10)

---

## Pergunta 90

**Severidade:** Cosmético · **Unit:** `object_library`
**Contexto:** object_library/ops.py:_follow; collision/scan.py:_kind_of
**Spec afetada:** `_reversa_sdd/object_library/edge-cases.md`
**Pergunta:** A inserção de objetos não tem encaixe (snapping) nem colisão, e a raiz Empty e as malhas filhas dos itens ficam fora da verificação de colisão. Isso é intencional?
**Impacto:** Portas, mesas e eletros podem ser postos atravessando módulos e paredes sem aviso.
**Recomendação do Reviewer:** Manter sem snapping por ora, mas incluir os itens de topo na verificação de colisão, que já existe e é barata de estender.

✅ Respondida

**Resposta:** aceito (recomendação do Reviewer adotada pelo titular em 2026-10-10)

---

## Pergunta 91

**Severidade:** Cosmético · **Unit:** `object_library`
**Contexto:** object_library/ops.py:BTM_OT_ObjectInsert.cancel
**Spec afetada:** `_reversa_sdd/object_library/edge-cases.md`
**Pergunta:** Quando o modal é cancelado de fora (fechar a janela, abrir outro arquivo), os objetos carregados ficam na cena. Devem ser removidos como no Esc?
**Impacto:** Objeto meio inserido pode ficar no projeto sem o usuário perceber.
**Recomendação do Reviewer:** Remover em cancel() os objetos de _loaded que ainda existirem, igual ao Esc.

✅ Respondida

**Resposta:** aceito (recomendação do Reviewer adotada pelo titular em 2026-10-10)

---

## Pergunta 92

**Severidade:** Cosmético · **Unit:** `inspection`
**Contexto:** ops_inspect.py:unregister
**Spec afetada:** `_reversa_sdd/inspection/edge-cases.md`
**Pergunta:** Ao desativar a extensão com o modo de inspeção rodando, o unregister só zera _active: timers, modal handler e o registro no HUD ficam vivos. Deve encerrar a sessão (chamar _finish)?
**Impacto:** Possíveis timers órfãos e referência pendurada no HUD após desativar/recarregar a extensão.
**Recomendação do Reviewer:** Sim: chamar _active._finish(bpy.context) dentro de try no unregister, como pede a regra do repositório de remover todo handler em todos os caminhos de saída.

✅ Respondida

**Resposta:** aceito (recomendação do Reviewer adotada pelo titular em 2026-10-10)

---

## Pergunta 93

**Severidade:** Cosmético · **Unit:** `inspection`
**Contexto:** ops_interference.py; overlay.py; props.py
**Spec afetada:** `_reversa_sdd/inspection/tasks.md`
**Pergunta:** Os resultados de interferência ficam no WindowManager sem invalidação: mover ou apagar objetos mantém a cruz e o rótulo no ponto antigo. Devem ser invalidados ao editar, como na colisão de corpo?
**Impacto:** Indicação visual desatualizada pode levar o usuário a corrigir um problema que já não existe (ou ignorar um novo).
**Recomendação do Reviewer:** Limpar a lista (ou marcar 'desatualizado' no painel) num depsgraph_update_post quando um objeto MESH/CURVE muda transformação, reaproveitando o padrão de collision/; custo baixo e sem nova verificação automática.

✅ Respondida

**Resposta:** aceito (recomendação do Reviewer adotada pelo titular em 2026-10-10)

---

## Pergunta 94

**Severidade:** Cosmético · **Unit:** `inspection`
**Contexto:** adapters/room_doors.py:apply; ops_inspect.py (bl_options sem UNDO)
**Spec afetada:** `_reversa_sdd/inspection/edge-cases.md`
**Pergunta:** A primeira abertura de uma porta de ambiente cria pivô e folha por um operador sem UNDO; o Ctrl+Z seguinte pode ou não removê-los. É aceitável, ou a criação da folha deve entrar no histórico?
**Impacto:** Objetos de folha podem aparecer/sumir de forma imprevisível no desfazer.
**Recomendação do Reviewer:** Aceitar (decisão RN-14 da 001: abrir não entra no desfazer) e validar no Blender que o undo não deixa pivô sem folha; se deixar, chamar ensure_leaves de forma idempotente já resolve na próxima abertura.

✅ Respondida

**Resposta:** aceito (recomendação do Reviewer adotada pelo titular em 2026-10-10)

---

## Pergunta 95

**Severidade:** Cosmético · **Unit:** `molding`
**Contexto:** hb_props.py:536-562 (update=update_molding_package); ops.py:apply_scene_packages
**Spec afetada:** `_reversa_sdd/molding/edge-cases.md`
**Pergunta:** Arrastar Reveal/Stack Offset/Cap Offset apaga e recria todas as molduras a cada passo do arraste. Isso é aceitável ou a reconstrução deve ser adiada (debounce) para o fim do arraste?
**Impacto:** Travamento perceptível em cenas grandes ou com packs externos (carregamento de .blend na 1ª métrica).
**Recomendação do Reviewer:** Aceitar enquanto as linhas herdadas estão atrás da porta legado (ADR 0006); se o uso crescer, agendar a reconstrução com bpy.app.timers (ex. 0,2 s) cancelando a anterior.

✅ Respondida

**Resposta:** aceito (recomendação do Reviewer adotada pelo titular em 2026-10-10)

---

## Pergunta 96

**Severidade:** Cosmético · **Unit:** `geometry_free`
**Contexto:** ops_create.py (modal); props.py:material/finish
**Spec afetada:** `_reversa_sdd/geometry_free/requirements.md`
**Pergunta:** A feature 002 pedia digitar a espessura durante a criação (RF-11) e material/acabamento por face (RF-12); o código não faz nenhum dos dois (espessura vem de 0,018 m; um único material em texto). Isso continua sendo requisito ou o comportamento atual foi aceito?
**Impacto:** Divergência entre a spec de produto 002 e o código; reimplementação não sabe qual seguir.
**Recomendação do Reviewer:** Aceitar o comportamento atual e registrar na 002 como Won't: a espessura é editável no painel logo depois e material por face não entra na produção (só uma matéria-prima por peça).

✅ Respondida

**Resposta:** aceito (recomendação do Reviewer adotada pelo titular em 2026-10-10)

---

## Pergunta 97

**Severidade:** Cosmético · **Unit:** `revisão cruzada`
**Contexto:** Artefatos fora do escopo de escrita desta revisão
**Spec afetada:** `.reversa/context/modules.json:4183; _reversa_forward/003…/interfaces/user-module-file.md; _reversa_forward/004…/actions.md T052/T053`
**Pergunta:** Atualizar esses artefatos (stick wall_side com espessura 0 ⇒ POS_Y; manifesto 1.1.0 real; collision.check_item inexistente)?
**Impacto:** Leitores das features antigas recebem contratos errados
**Recomendação do Reviewer:** Corrigir no próximo ciclo do Writer/forward ou marcar como históricos

✅ Respondida

**Resposta:** aceito (recomendação do Reviewer adotada pelo titular em 2026-10-10)

---

## Pergunta 98

**Severidade:** Cosmético · **Unit:** `revisão cruzada`
**Contexto:** Pacote catalog/ não importado
**Spec afetada:** `_reversa_sdd/catalog_molding/`
**Pergunta:** catalog/ é código morto a remover ou será religado?
**Impacto:** Spec viva de código que não roda
**Recomendação do Reviewer:** Marcar catalog_molding como histórica por inteiro se catalog/ não voltar

✅ Respondida

**Resposta:** aceito (recomendação do Reviewer adotada pelo titular em 2026-10-10)

---
