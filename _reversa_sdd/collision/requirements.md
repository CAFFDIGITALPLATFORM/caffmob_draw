# Colisão de Corpo (collision) — Requisitos

🟢 **CONFIRMADO** — contrato extraído de `caffmob_draw/collision/` em 2026-10-10 (sem alterações sem commit na pasta). Confirmação de código não implica validação visual no Blender. 🟡 marca inferência (prioridade, intenção, semântica de API não executada); 🔴 marca lacuna. IDs RN/RF da feature 004 aparecem como "004 RN-xx"/"004 RF-xx" para não colidir com os IDs desta unit. Contratos de outras units são citados, não redescritos: classificação e raízes em `_reversa_sdd/selection/`, caixa local e vínculo do grudar em `caffmob_draw/stick/apply.py` (sem spec própria), aviso de sobreposição do "Mover Sobre" em `_reversa_sdd/move_over/` (RN-15), contato da folha de porta em `_reversa_sdd/aggregates/` (`aggregates/collision.py`, outro mecanismo).

## Visão Geral

🟢 Verificação "depois do fato" de colisão de corpo entre itens (módulos, geometrias, eletrodomésticos, agregados, portas/janelas de ambiente, malhas soltas) e deles com paredes, obstáculos, piso e teto. O item fica onde foi solto: o sistema lista, destaca na viewport, avisa ao soltar e oferece "Afastar até encostar"; nunca bloqueia movimento nem salvamento (`scan.py`, `ops_collision.py`, docstring de `__init__.py`).

🟢 Não confundir com `aggregates/collision.py` (contato da folha de porta por BVH), com `hb_placement.avoid_overlap` (bloqueio no arraste herdado) nem com o aviso do "Mover Sobre" (`move_over/ops_dialog.py:_confirm`); os três apenas compartilham a chave global `btm_settings.collision_global`.

## Responsabilidades

- 🟢 Representar cada item como caixa orientada no mundo e medir a sobreposição de dois itens pelo teste dos eixos separadores, devolvendo profundidade e o deslocamento mínimo que a desfaz (`obb.py:overlap`).
- 🟢 Gerar pares candidatos, aplicar exclusões, descartar contato, classificar, escolher o item móvel do par e ordenar de forma estável (`rules.py`).
- 🟢 Traduzir os objetos da cena em itens, com tipo, raiz, vínculos e exceção por item; confirmar pela malha real os pares que envolvem objetos "finos" (`scan.py:collect/_kind_of/_links/_confirm`).
- 🟢 Guardar o resultado na sessão (`WindowManager.btm_collision`), nunca no `.blend` (`props.py`).
- 🟢 Marcar o resultado como desatualizado quando um item vigiado muda (`stale.py`).
- 🟢 Reverificar só o que se moveu ao fim do assentar do grudar e avisar "X colide com Y" sem mover nada (`scan.py:check_moved`, chamado por `stick/settle.py:_check_collisions`).
- 🟢 Oferecer operadores Verificar / Ir para / Limpar / Afastar até encostar (`ops_collision.py`), destaque na viewport (`overlay.py`) e as funções de desenho dos painéis consumidas pela barra lateral única (`panels.py`).
- 🟢 Fora do escopo: impedir sobreposição durante o arraste (`hb_placement`), folha de porta (`aggregates`), interferência de frentes (`inspection/interference.py`), aviso ao salvar (lê este estado em `ui/save_feedback.py:_collision_note`).

## Regras de Negócio

| ID | Regra | Fonte | Confiança |
|---|---|---|---|
| RN-01 | Encostar não é colisão: ocorrência só quando a profundidade SAT é **estritamente maior** que `TOLERANCE = 0.001` m (1,1 mm conta — executado; 1,0 mm "exato" fica no limite do ponto flutuante e conta ou não conforme o arredondamento das coordenadas: borda em 0,999 m dá profundidade 0,0010000000000000009 e **conta**, borda em 0,599 m dá 0,0009999999999998899 e não conta) _(Revisão 2026-10-10: texto corrigido de "1,0 mm exato não conta"; reexecutado com obb.overlap/rules.conflicts)_ | `rules.py:TOLERANCE/evaluate` | 🟢 (código) / 🟢 **Decisão do titular (2026-10-10, questions.md#pergunta-31):** comparar com folga numérica, `depth <= TOLERANCE + 1e-9` → sem ocorrência: 1,0 mm fica estável como "encostar" (004 RN-11). Pendência de implementação: DT-01 |
| RN-02 | Par excluído (004 RN-12), nesta ordem: ambos estáticos (`WALL`, `OBSTACLE`, `FLOOR`, `CEILING`); qualquer `override == 'OFF'`; mesmo `group` (`root or name`); nome ou grupo de um em `linked` do outro | `rules.py:excluded` | 🟢 |
| RN-03 | `linked` de um item = pai do agregado (`btm_aggregate.parent_ref`) e a raiz dele; hospedeiro do grudado (`btm_stick.is_stuck` e `host`) e a raiz dele; para porta de entrada/janela (`IS_ENTRY_DOOR_BP`, `IS_WINDOW_BP` ou `classify.WINDOW`) cujo **pai direto** é parede (`IS_WALL_BP` ou `btm_wall_segments`), o nome dessa parede | `scan.py:_links/_root_name` | 🟢 |
| RN-04 | Classificação da ocorrência: parede ou obstáculo no par → `WALL` ("Penetração em parede"); senão piso ou teto → `FLOOR_CEILING` ("Piso ou teto"); senão `ITEM` ("Colisão entre itens") | `rules.py:conflict_kind`; `props.py:KIND_ITEMS` | 🟢 |
| RN-05 | Um par gera uma ocorrência. `name_a` é o item que pode ser movido: o estático vai para `b`; entre dois do mesmo tipo (estático ou não) fica em `a` o de **nome menor**; `push` é o deslocamento de `a` (invertido quando o par é trocado) | `rules.py:evaluate` | 🟢 |
| RN-06 | Ordem (004 RN-13): `WALL` (0) → `ITEM` (1) → `FLOOR_CEILING` (2); dentro do tipo, profundidade decrescente arredondada a 6 casas; empate por `name_a`, depois `name_b`. Mesma cena → mesma lista, independentemente da ordem de entrada (teste) | `rules.py:_ORDER/sort_key/conflicts`; `tests/test_collision_rules.py` | 🟢 |
| RN-07 | Entram como itens: malha com `btm_wall_segments` (parede); agregado; `IS_APPLIANCE`; raiz de `MODULE`/`GEOMETRY`; raiz de `ROOM_DOOR`/`WINDOW`; `WALL`/`OBSTACLE`/`FLOOR`/`CEILING`; `OTHER` apenas se `MESH`, sem pai e `display_type` fora de `WIRE`/`BOUNDS`. Peças e frentes nunca entram sozinhas (só quando `classify(obj).obj is obj`) | `scan.py:_kind_of` | 🟢 |
| RN-08 | Ficam de fora objetos com qualquer idprop verdadeira entre `IS_CUTTING_OBJ`, `IS_2D_ANNOTATION`, `IS_DIMENSION`, `obj_x`, e objetos com `hide_viewport` ou `not visible_get()` (`RuntimeError` também exclui) | `scan.py:_SKIP_TAGS/_skip` | 🟢 |
| RN-09 | Par em que ao menos um lado é "fino" (parede, obstáculo, agregado, porta/janela de ambiente, malha solta) só vira ocorrência se as BVHs das malhas avaliadas no mundo se sobrepõem; isso respeita o vão de porta/janela na parede (004 D-13). Sem malha utilizável, a BVH usa as 6 faces da OBB | `scan.py:_FINE_KINDS/_kind_of/_Meshes/_confirm` | 🟢 |
| RN-10 | Chave global `scene.btm_settings.collision_global` ("Evitar Sobreposição", padrão ligado; ausente = ligada) desligada: nem a verificação manual nem o aviso ao soltar rodam; painel mostra "Colisão desligada (Evitar Sobreposição)" | `scan.py:enabled/check_moved`; `ops_collision.py:BTM_OT_CheckCollisions.execute`; `panels.py:draw_collisions`; `data/properties.py:740` | 🟢 |
| RN-11 | Exceção por item `Object.btm_plane.collision_override` (`INHERIT`/`ON`/`OFF`): só `OFF` tem efeito (tira o item de todos os pares); `ON` se comporta como `INHERIT` e não vence a chave global desligada | `scan.py:_override`; `rules.py:excluded`; `data/properties.py:240` | 🟢 |
| RN-12 | A interface nunca diz "sem colisões" com erro ou com resultado desatualizado; falha de cálculo da verificação manual vira `state.error` visível (004 RN-14, RF-25) | `scan.py:check_all`; `panels.py:draw_collisions` | 🟢 |
| RN-13 | Resultado desatualizado quando um objeto cuja cadeia de pais alcança um nome vigiado (`checked_names` ∪ nomes das linhas) tem atualização de geometria ou transformação no depsgraph; reverificar os movidos os tira da conta e, sem outras mudanças, o resultado volta a estar em dia | `stale.py:on_depsgraph_update/rechecked` | 🟢 |
| RN-14 | Ao fim do assentar do grudar, refaz só os pares que envolvem os objetos movidos e seus `children_recursive`, preserva as demais linhas, avisa "<movido> colide com <outro>" na barra de status para cada ocorrência e **não move** nada (004 RF-23, D-16) | `scan.py:check_moved`; `stick/settle.py:run/_check_collisions` | 🟢 |
| RN-15 | "Afastar até encostar" move `name_a` por `push`; item grudado ao hospedeiro (`stick/apply.linked`) só anda no plano da face (componente normal removida) e, se o resto for < 1e‑6 m, recusa com aviso. É um passo de desfazer, sem prévia | `ops_collision.py:BTM_OT_CollisionPushOut` | 🟢 |
| RN-16 | O resultado vive só na sessão (`WindowManager`), não é salvo no arquivo; `checked = −1` significa "nunca verificado" | `props.py` | 🟢 |
| RN-17 | 🟡 004 RF-26 pede "com prévia" e "move o item selecionado"; o código aplica direto e move `name_a` (para `ITEM`×`ITEM`, o de nome menor), sem olhar a seleção | `ops_collision.py:BTM_OT_CollisionPushOut.execute`; `_reversa_forward/004-editor-armario-grudar/requirements.md` RF-26 | 🟢 (código) / 🟢 **Decisão do titular (2026-10-10, questions.md#pergunta-32):** mover o selecionado quando ele for um dos dois (invertendo o `push`) e recusar com resultado desatualizado; prévia só se houver pedido. Pendência de implementação: DT-02 |

## Requisitos Funcionais

🟡 Prioridades herdadas da 004 (RF-20 a RF-27) e ajustadas pelo uso atual; não constituem roadmap aprovado.

| ID | Requisito | Prioridade | Critério de aceite | Confiança |
|---|---|---|---|---|
| RF-01 | Verificar colisões na cena inteira (`ALL`) ou só nos pares que envolvem as raízes selecionadas (`SELECTED`) | Must | CA-01, CA-02, CA-03 | 🟢 |
| RF-02 | Núcleo puro OBB + regras (RN-01 a RN-06), testável sem Blender | Must | CA-04, CA-05, CA-06 | 🟢 |
| RF-03 | Coleta da cena e confirmação pela malha (RN-07 a RN-09) | Must | CA-07, CA-08 | 🟢 |
| RF-04 | Painel com estados desligado / erro / nunca verificado / desatualizado / sem colisões / lista; até 12 linhas com "Ir para" e "Afastar" | Must | CA-09, CA-10 | 🟢 |
| RF-05 | "Ir para": seleciona os dois itens visíveis e enquadra todas as `VIEW_3D` da janela | Must | CA-11, CA-12 | 🟢 |
| RF-06 | Resultado desatualizado e reverificação parcial (RN-13, RN-14) | Must | CA-13, CA-14 | 🟢 |
| RF-07 | Aviso ao soltar via assentar do grudar (RN-14) | Must | CA-15, CA-16 | 🟢 |
| RF-08 | Destaque na viewport: contorno da OBB e rótulo "Tipo: A × B" (vermelho; laranja e "(desatualizado)" quando stale) | Should | CA-17 | 🟢 |
| RF-09 | Exceção por item e chave global (RN-10, RN-11), com campo "Colisão" no grupo do item da barra lateral | Should | CA-18, CA-19 | 🟢 |
| RF-10 | Limpar resultado (lista, `checked`, `checked_names`, `stale`, `error`) | Should | CA-20 | 🟢 |
| RF-11 | Afastar até encostar (RN-15) | Could | CA-21, CA-22 | 🟢 |
| RF-12 | Expor o estado para o aviso ao salvar (`_collision_note`, 004 RF-27) | Should | CA-23 | 🟢 |

## Requisitos Não Funcionais

| Tipo | Requisito observado | Evidência | Confiança |
|---|---|---|---|
| Desempenho | Verificação de 200 caixas + 1 extra em ≤ 2,0 s, 4 ocorrências | `tests/blender_004_collision_smoke.py` (passo 9; não executado nesta extração — sem Blender no ambiente) | 🟢 (asserção existe) / 🟡 (medição) |
| Desempenho | Pré-filtro: varredura ordenada por `x_min` com corte `x_min(B) > x_max(A) + TOLERANCE`, depois AABB com margem `TOLERANCE`; SAT só nos candidatos; BVH só nos pares finos, construída sob demanda e reaproveitada por objeto (`as_pointer`) dentro de uma chamada | `rules.py:candidate_pairs`; `scan.py:_Meshes` | 🟢 |
| Determinismo | Ordem total por `sort_key`; entradas em ordem diferente geram a mesma lista | `rules.py:sort_key`; `tests/test_collision_rules.py:test_uma_ocorrencia_por_par_e_ordem_estavel` | 🟢 |
| Separação | `obb.py` e `rules.py` não importam `bpy`; `__init__._modules` importa os demais tarde para os testes puros | `__init__.py:_modules` | 🟢 |
| Robustez | Falha na verificação manual vira erro visível; no aviso ao soltar, falha é silenciosa (`[]`) | `scan.py:check_all/check_moved` | 🟢 |
| Ciclo de vida | Handlers `depsgraph_update_post` (`@persistent`) e dois `draw_handler` registrados uma vez e removidos no `unregister`; `WindowManager.btm_collision` removido no `unregister` | `stale.py:register/unregister`; `overlay.py:register/unregister`; `props.py:unregister` | 🟢 |
| Custo de desenho | Overlay limitado a 30 linhas (≤ 60 objetos, `box_of` recalculado a cada redesenho); painel a 12; painel do item a 5 | `overlay.py:MAX_ROWS`; `panels.py:MAX_ROWS/BTM_PT_ItemCollision.draw` | 🟢 |

## Critérios de Aceitação

🟢 CA-04 a CA-06 são cobertos por `tests/test_collision_rules.py` (6 testes aprovados nesta extração) ou executados em Python puro; CA com cena correspondem a `tests/blender_004_collision_smoke.py` quando indicado (não executado aqui).

```gherkin
CA-01 — Penetração em parede (fumaça, passo 1)
Dado uma parede GN de 4,0 × 0,15 × 2,6 m e um balcão 20 mm dentro dela, colisão global ligada
Quando executo caffmob.check_collisions com scope ALL
Então a lista tem uma linha (WALL, "Balcao", "Parede", 0,02 m), o report é WARNING "1 colisão(ões) em M item(ns)" e o resultado não está desatualizado

CA-02 — Chave global desligada (fumaça, passo 8)
Dado btm_settings.collision_global = False
Quando executo caffmob.check_collisions ou scan.check_moved([balcão])
Então o operador devolve CANCELLED com WARNING "Colisão desligada (Evitar Sobreposição)" e check_moved devolve []

CA-03 — Escopo selecionado sem seleção
Dado nenhum objeto selecionado
Quando executo caffmob.check_collisions com scope SELECTED
Então recebo WARNING "Selecione um item", CANCELLED, e o estado não muda

CA-04 — Encostar não é colisão
Dado dois balcões cuja sobreposição em X é 0,5 mm (ou 1,0 mm cuja profundidade calculada não passe de 0,001; ver RN-01 _(Revisão 2026-10-10: texto corrigido, 1,0 mm depende do arredondamento)_)
Quando rules.conflicts avalia os itens
Então não há ocorrência; com 1,1 mm há uma ocorrência ITEM

CA-05 — Pares excluídos
Dado agregado ligado à parede, porta ligada à parede, rodapé com override OFF, duas peças com mesma raiz, parede × piso
Quando rules.conflicts avalia
Então a lista é vazia

CA-06 — Ordem e unicidade
Dado itens que geram uma penetração em parede, uma colisão entre itens e uma com o teto
Quando avalio a lista e a lista invertida
Então as duas saídas são iguais e na ordem WALL (C × Parede), ITEM (A × B), FLOOR_CEILING (D × Teto)

CA-07 — Confirmação pela malha
Dado um par cujas caixas se sobrepõem e confirm que devolve False
Quando rules.conflicts avalia com esse confirm
Então o par é descartado; com only={'C'} só os pares com C aparecem

CA-08 — Porta no vão e agregado afundado (fumaça, passo 5)
Dado uma porta (IS_ENTRY_DOOR_BP) filha da parede e um agregado afundado 5 mm no pai
Quando verifico a cena
Então nem (Porta, Parede) nem o agregado aparecem na lista

CA-09 — Estados do painel
Dado estado nunca verificado (checked = −1, lista vazia)
Quando draw_collisions desenha
Então mostra "Ainda não verificado." e não mostra "Sem colisões"

CA-10 — Erro nunca vira "sem colisões"
Dado que find levanta exceção durante check_all
Quando o painel é desenhado
Então mostra a caixa de alerta "Não foi possível calcular a colisão: <erro>", a lista está vazia e o operador reporta ERROR e CANCELLED

CA-11 — Ir para (fumaça, passo 2)
Dado a ocorrência 0 (Balcao × Parede) com os dois visíveis
Quando executo caffmob.collision_goto(index=0)
Então FINISHED, a seleção é exatamente {Balcao, Parede}, Balcao fica ativo e state.index = 0

CA-12 — Ir para inválido
Dado index fora da lista, ou os dois objetos apagados/ocultos
Quando executo caffmob.collision_goto
Então CANCELLED; no segundo caso com WARNING "Os itens da colisão não estão visíveis"

CA-13 — Desatualizado (fumaça, passo 6)
Dado um resultado com 1 ocorrência e stale falso
Quando movo o balcão verificado 10 mm em Z
Então state.stale fica verdadeiro, o painel mostra "Desatualizado, verifique de novo" e _collision_note devolve "Colisões não verificadas desde a última mudança"

CA-14 — Reverificar o movido
Dado o resultado desatualizado apenas pelo balcão
Quando chamo scan.check_moved([balcão])
Então as linhas do balcão são refeitas, as demais preservadas, e stale volta a falso

CA-15 — Aviso ao soltar (fumaça, passo 7)
Dado um balcão que, ao fim do assentar, sobrepõe "Vizinho"
Quando stick/settle.run chama check_moved
Então a barra de status mostra "Balcao colide com Vizinho" e o balcão continua onde foi solto

CA-16 — Falha no aviso ao soltar
Dado que find levanta exceção dentro de check_moved
Quando o assentar termina
Então check_moved devolve [] sem aviso, sem mudar state.error nem a lista

CA-17 — Destaque
Dado ocorrências na lista e stale falso
Quando a viewport redesenha
Então as 12 arestas da OBB de cada item visível envolvido aparecem em (1, 0,25, 0,2, 1) com largura 2,5, e o rótulo "<Tipo>: A × B" fica a +10 px do ponto; com stale, cor (1, 0,65, 0,2, 0,8) e sufixo "(desatualizado)"

CA-18 — Colisão desativada no item (fumaça, passo 4)
Dado o par Balcao × Vizinho colidindo
Quando Vizinho.btm_plane.collision_override = 'OFF' e verifico
Então a lista fica vazia

CA-19 — Override ON não vence a chave global
Dado collision_override = 'ON' num item e collision_global = False
Quando executo a verificação
Então nada roda (CANCELLED), como em CA-02

CA-20 — Limpar
Dado um resultado com linhas, stale e erro
Quando executo caffmob.collision_clear
Então items vazio, checked = −1, checked_names = "", stale = False, error = "" e o painel volta a "Ainda não verificado."

CA-21 — Afastar até encostar (fumaça, passo 2)
Dado Balcao 20 mm dentro da parede (push = (0, −0,02, 0))
Quando executo caffmob.collision_push_out(index=0)
Então FINISHED, o balcão fica em Y = 0 (± 1e−4), report INFO "Balcao afastado 20.0 mm" e uma nova verificação não acha ocorrências

CA-22 — Item grudado empurrado só pela normal
Dado name_a grudado ao hospedeiro e push paralelo à normal da face
Quando executo caffmob.collision_push_out
Então CANCELLED com WARNING "O item grudado não pode sair da face; mova o outro item" e nada se move

CA-23 — Aviso ao salvar (fumaça, passo 6)
Dado resultado em dia com 1 ocorrência
Quando ui/save_feedback._collision_note é chamado
Então devolve "1 colisões pendentes"; com checked = −1 devolve ""
```

## Prioridade (MoSCoW)

| Requisitos | Classificação | Justificativa |
|---|---|---|
| RF-01, RF-02, RF-03, RF-04, RF-05, RF-06, RF-07 | 🟡 Must | 004 RF-20, RF-21, RF-23, RF-25; núcleo reaproveitado por `cabinet_editor/validate.py` (GEO-002) |
| RF-08, RF-09, RF-10, RF-12 | 🟡 Should | 004 RF-22, RF-24, RF-27; há alternativa (lista do painel) |
| RF-11 | 🟡 Could | 004 RF-26: "o usuário resolve movendo" |

## Rastreabilidade de Código e Verificação

| Arquivo | Símbolos | Evidência |
|---|---|---|
| `caffmob_draw/collision/obb.py` | `OBB`, `from_box`, `overlap`, `aabb_overlap` | 🟢 Código; `test_collision_rules` |
| `caffmob_draw/collision/rules.py` | `Item`, `Conflict`, `excluded`, `conflict_kind`, `candidate_pairs`, `evaluate`, `sort_key`, `conflicts` | 🟢 Código; `test_collision_rules` |
| `caffmob_draw/collision/props.py` | `KIND_ITEMS`, `BTM_PG_Collision`, `BTM_PG_CollisionState` | 🟢 Código |
| `caffmob_draw/collision/scan.py` | `box_of`, `_kind_of`, `_links`, `collect`, `_Meshes`, `_confirm`, `enabled`, `find`, `_store`, `selected_names`, `check_all`, `check_moved`, `_redraw` | 🟢 Código; fumaça 004 |
| `caffmob_draw/collision/stale.py` | `reset`, `rechecked`, `on_depsgraph_update` | 🟢 Código; fumaça 004 |
| `caffmob_draw/collision/ops_collision.py` | 4 operadores `caffmob.*` | 🟢 Código; fumaça 004 |
| `caffmob_draw/collision/overlay.py` | `_draw_3d`, `_draw_2d` | 🟢 Código; validação visual pendente |
| `caffmob_draw/collision/panels.py` | `draw_collisions`, `BTM_PT_Collisions`, `BTM_PT_ItemCollision` (não registrados) | 🟢 Código; `tests/test_layout_probe.py` só usa o operador |
| `caffmob_draw/stick/settle.py` | `run` → `_check_collisions` → `scan.check_moved` | 🟢 Consumidor |
| `caffmob_draw/ui/sidebar_check.py`, `ui/object_properties.py`, `ui/save_feedback.py`, `ui/sidebar_vocab.py` | painel, painel do item, `_collision_note`, `CHECK_ITEM` | 🟢 Consumidores |
| `caffmob_draw/cabinet_editor/validate.py` | reusa `obb.from_box`/`obb.overlap` (GEO-002) | 🟢 Consumidor |

🟢 Executado em 2026-10-10: `cd tests && PYTHONDONTWRITEBYTECODE=1 python3 -m unittest test_collision_rules -v` → **6 testes aprovados** (encostados, penetração 20 mm, pares excluídos, caixa girada 45°, ordem estável, confirmação/only). 🔴 `tests/blender_004_collision_smoke.py` não foi executado (Blender ausente no ambiente).

## Lacunas e Divergências

- 🟢 **Decisão do titular (2026-10-10, questions.md#pergunta-32):** RN-17: "Afastar" move o selecionado quando ele é um dos dois e recusa com resultado desatualizado; sem prévia (004 RF-26 só se houver pedido). Pendência de implementação: DT-02.
- 🟢 Item totalmente dentro de um objeto fino (sem cruzar superfícies) some na confirmação BVH (edge-cases EC-01). 🟢 **Decisão do titular (2026-10-10, questions.md#pergunta-33):** quando a BVH não acusa e o SAT acusa, testar o centro do item contra a malha fina (ray-cast de paridade), validando antes no Blender. Pendência de implementação: DT-03.
- 🟢 Objetos novos na cena depois da verificação não deixam o resultado desatualizado (EC-03); contraria a garantia de RN-12 na prática. 🟢 **Decisão do titular (2026-10-10, questions.md#pergunta-34):** marcar `stale` para qualquer objeto que `_kind_of` aceitaria e não está em `checked_names`. Pendência de implementação: DT-04.
- 🟢 _(Revisão 2026-10-10: 🟡→🟢; stick/settle.py:run linhas 60-94 e `_MAGNET_KINDS = (MODULE, GEOMETRY)`)_ Divergência com 004 D-16: o aviso ao soltar não é chamado no fim de cada movimento do plugin; ele vem do assentar do grudar (`stick/settle.run`), que cobre o G nativo, mas só para itens grudados e raízes `MODULE`/`GEOMETRY` (agregados, eletrodomésticos, obstáculos e aberturas soltos não disparam).
- 🟢 _(Revisão 2026-10-10: 🟡→🟢; overlay.py:register/unregister; collision_clear não remove handlers)_ Divergência com 004 D-17: os handlers de desenho ficam registrados o tempo todo e só retornam cedo sem ocorrências (não são ligados/desligados ao limpar).
- 🟢 _(Revisão 2026-10-10: 🟡→🟢; data-dictionary.md linhas 36 e 577 conferidas)_ Divergência com `data-dictionary.md` (§ `btm_plane.collision_override`): ali "liga ou desliga ignorando a configuração global"; no código só `OFF` age e a chave global desligada vence tudo (RN-11). Também §10.6 diz "Ocorrências em ordem RN-13", mas `check_moved` acrescenta as novas linhas ao fim sem reordenar (EC-05).
- 🟢 _(Revisão 2026-10-10: 🟡→🟢; state-machines.md §Colisão de corpo só tem SemResultado/Atual/Desatualizado)_ Divergência com `state-machines.md` (Colisão de corpo): falta o estado de erro e o caminho `check_moved` sem verificação prévia (EC-04); a volta Desatualizado → Atual também ocorre por `check_moved` quando `_changed` esvazia. _(Revisão cruzada 2026-10-10: state-machines.md › Colisão de corpo corrigido com Avulso, Erro e a volta por `check_moved`)_
