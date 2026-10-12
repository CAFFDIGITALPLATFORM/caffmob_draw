# Grudar em Superfície (stick) — Requisitos

🟢 **CONFIRMADO** — contrato extraído de `caffmob_draw/stick/` (11 arquivos, 1.486 linhas) em 2026-10-10, sem alterações sem commit na pasta (`git status` limpo). Confirmação de código não implica validação visual no Blender. 🟡 marca inferência (prioridade, intenção, semântica de API não executada); 🔴 marca lacuna. IDs RN/RF/D da feature 004 aparecem como "004 RN-xx"/"004 D-xx" (e "005 D-xx") para não colidir com os IDs desta unit. Contratos de outras units são citados, não redescritos: classificação e raízes (`classify`, `movable_root`, `free_group`) e raiz de componente/plano de exclusão em `_reversa_sdd/selection/`; eixos das faces (`aggregates/limits.face_axes/thickness/FACES/FACE_LABELS`), conversão em agregado e apagar com agregados em `_reversa_sdd/aggregates/` (RN-05, RN-29); colisão ao soltar em `_reversa_sdd/collision/` (RN-03, RN-14, RN-15); "Mover Sobre" (modais esperados pelo assentar) em `_reversa_sdd/move_over/`; barra lateral única e `save_feedback.show` em `_reversa_sdd/ui/`.

## Visão Geral

🟢 Grudar um item (módulo, geometria, malha qualquer) numa face plana de outro objeto (parede, painel, módulo, geometria). O vínculo é "parentesco Blender + `Object.btm_stick`": o item vira filho do hospedeiro com inversa identidade e a propriedade guarda face, posição no plano (`u`, `v`), distância e giro. O item acompanha o hospedeiro ao mover, girar e mudar de medida; movido livremente, volta ao plano da face; o ímã gruda automaticamente ao soltar perto de uma face; módulos já postos na parede viram "elementos filhos" dela (docstrings de `__init__.py`, `apply.py`, `link.py`, `settle.py`, `migrate.py`).

🟢 Vocabulário da interface: "Elemento filho de: <hospedeiro> — <face>" e "Elementos filhos", sem a palavra "pai", para não confundir com o agregado da 003 (`link.py:face_label`; `panels.py`; 004 D-11).

## Responsabilidades

- 🟢 Núcleo puro do referencial da face `(origem, U, V, N)`, da posição `(u, v, distance)`, do teste "fora da face", da planicidade e da escolha `BOX_SIDE`/`PLANE` (`frame.py`, sem `bpy`).
- 🟢 Persistir o vínculo em `Object.btm_stick` (salvo no `.blend`) com `update` que reposiciona o item (`props.py`).
- 🟢 Grudar, gravar vínculo sem mover e desgrudar (`link.py:stick/link_in_place/release`).
- 🟢 Manter o item na face: reposicionar quando a caixa do hospedeiro muda, projetar de volta ao plano depois de movimento livre, trocar para a face oposta quando o item atravessou o hospedeiro, perder o vínculo quando o hospedeiro some, avisar item fora da face (`apply.py`).
- 🟢 Adiar o tratamento pós-movimento até nenhum modal de movimento estar ativo (temporizador de assentar) e, ao assentar, acionar ímã, vínculo com a parede e a reverificação de colisão (`apply.py:_settle_timer`; `settle.py:run`).
- 🟢 Ímã de face plana e prévia do ímã durante o arraste (`magnet.py`, `magnet_preview.py`).
- 🟢 Migração dos módulos que já são filhos de parede ao abrir o arquivo (`migrate.py:run`, chamado por `caffmob_draw/__init__.py:load_file_post`).
- 🟢 Operadores Grudar / Desgrudar / Mover no plano e o painel "Elemento filho" (`ops_stick.py`, `panels.py`).
- 🟢 Servir de API para outras units: `apply.local_box`, `item_corners`, `linked`, `face_of`, `project`, `stuck_items`; `link.release`; `ops_stick.item_of` (consumidores em `design.md`).
- 🟢 Fora do escopo: decidir a raiz do componente e o plano de exclusão (`selection/component.py`), soltar grudados ao apagar pelo operador (`aggregates/ops_aggregate.py:_release_stuck_children`), recusar converter grudado em agregado (`aggregates/convert.py:can_convert`), verificar colisão (`collision/scan.py`), preferências do ímã (declaradas em `caffmob_draw/__init__.py:BTM_AddonPreferences`).

## Regras de Negócio

| ID | Regra | Fonte | Confiança |
|---|---|---|---|
| RN-01 | Face plana (004 RN-05): quando o polígono acertado é conhecido, todos os vértices (no espaço do hospedeiro) a ≤ `PLANAR_TOLERANCE = 0.0005` m do plano que passa pelo **primeiro** vértice com a normal acertada; lista vazia ou normal nula = não plana → `ValueError("A face não é plana")`. Sem polígono (`polygon_world` vazio/`None`), não testa | `frame.py:is_planar`; `link.py:stick` | 🟢 |
| RN-02 | Tipo da face (004 D-02): percorrendo `FACES` na ordem `POS_X, NEG_X, POS_Y, NEG_Y, POS_Z, NEG_Z`, a primeira face cujo eixo tem `n·eixo ≥ cos(1°)` (`ANGLE_TOLERANCE_DEG = 1.0`) e cujo plano dista ≤ `SIDE_TOLERANCE = 0.0005` m do ponto é `BOX_SIDE`; senão `PLANE` (normal nula também `PLANE`). Executado: 1,0° → `BOX_SIDE`, 1,1° → `PLANE`; 0,5 mm fora → `BOX_SIDE`, 0,6 mm → `PLANE` | `frame.py:choose_face` | 🟢 |
| RN-03 | `BOX_SIDE` acompanha mudança de medida do hospedeiro (o plano é recalculado da caixa local avaliada); `PLANE` é fixo no referencial local do hospedeiro (acompanha mover/girar, não medida) e grava a matriz em `btm_stick.plane` | `frame.py` docstring, `frame_for`; `link.py:stick` | 🟢 |
| RN-04 | Hospedeiro = `classify(obj).root` quando o tipo não é `OTHER` nem `ANNOTATION` e a raiz existe (peça/frente → módulo; parede → ela mesma); senão o próprio objeto clicado | `link.py:host_for` | 🟢 |
| RN-05 | Recusas, nesta ordem: sem item ("Selecione o item a grudar"); sem hospedeiro ("Clique numa face plana de outro objeto"); hospedeiro é o item ou descendente dele ("O item não pode ser grudado nele mesmo nem num filho dele"); item agregado (`btm_aggregate.is_aggregate`: "O item é um agregado: desconverta antes de grudar") | `link.py:can_stick` | 🟢 |
| RN-06 | Orientação ao grudar: `|n·Z| ≥ 0.7` → face deitada (`BOTTOM`: Z do item = ±n apontando para cima); senão face de pé (`BACK`: Y do item = −n, ou seja, o fundo +Y local encosta; Z = Z do mundo projetado no plano). Posição e escala são preservadas. Executado: 0,69 → `BACK`, 0,70 → `BOTTOM` | `frame.py:contact_axis`; `link.py:oriented_matrix/orient` | 🟢 |
| RN-07 | Vínculo (004 D-03): `item.parent = host`, `matrix_parent_inverse = I`, `matrix_basis = host⁻¹·mundo` (sem salto no mundo). `orig_parent` só é gravado na **primeira** vez (item ainda não grudado). Gravados: `host`, `face_kind`, `face` (`'NEG_Y'` em `PLANE`), `plane`, `u`, `v`, `distance = 0`, `spin = 0`, `applied_spin = 0`, `out_of_face = False`, `is_stuck = True` | `link.py:_attach/_record/stick` | 🟢 |
| RN-08 | Posição na face: `(u, v, distance)` = canto mínimo da pegada do item no referencial da face. Em `BOX_SIDE` a origem é a origem local do hospedeiro com só a coordenada normal levada ao lado (U, V são eixos locais crescentes), então `u`/`v` não mudam quando o hospedeiro é redimensionado (004 RN-08a). `distance` 0 = encostado; negativo = entra no hospedeiro. Sem limite de contorno | `frame.py:box_frame/params/footprint` | 🟢 |
| RN-09 | Comando Grudar centra a pegada no ponto clicado (`center=True`: `u = hu − largura/2`, `v = hv − altura/2`); o ímã mantém `u`/`v` da posição atual depois de girar (`center=False`). Nos dois casos `distance = 0` e `update_position` encosta | `link.py:stick`; `magnet.py:try_stick`; `ops_stick.py:BTM_OT_StickToFace.modal` | 🟢 |
| RN-10 | Item grudado só anda no plano (004 RN-06, RF-13): depois de movimento livre (G nativo, campos), ao assentar, `u`/`v` passam a ser os da posição solta e `distance` é restaurada. Só translação é corrigida; giro livre (R) não é desfeito (EC-08) | `apply.py:project/update_position`; `settle.py:run` | 🟢 |
| RN-11 | Acompanhar a medida (004 RN-07, D-04): quando o depsgraph traz atualização de **geometria** de um hospedeiro presente no índice e a caixa local avaliada difere da última vista (`_last_box`), cada item grudado nele é levado de novo a `u`/`v`/`distance`. Mover/girar o hospedeiro é coberto pelo parentesco | `apply.py:on_depsgraph_update/update_position` | 🟢 |
| RN-12 | Troca para a face oposta (só `BOX_SIDE`): se a distância pela face atual é `< −espessura − OUT_TOLERANCE` (item atravessou o hospedeiro, ex. editor de paredes inverteu a parede) e pela oposta é `≥ −OUT_TOLERANCE`, o vínculo passa para `_OPPOSITE[face]` com `distance` = a distância pela oposta; senão nada | `apply.py:_flip_if_across` | 🟢 |
| RN-13 | Fora da face (004 RN-08a): centro da pegada fora do retângulo do lado (`face_extent`) com folga `OUT_TOLERANCE = 0.001` m → `out_of_face = True` e aviso "Item fora da face: {item}" na barra de status **só na transição**; o item fica onde está e mantém o vínculo. `PLANE` nunca fica fora. Executado: centro a 1,0 mm além da borda → dentro; 1,1 mm → fora | `frame.py:out_of_face`; `apply.py:_check_face` | 🟢 |
| RN-14 | Vínculo perdido (004 RN-08): item com `is_stuck` e `host` `None` (hospedeiro apagado) → se o item ficou sem pai e `last_world` não é identidade, volta a `last_world`; `is_stuck`, `host`, `out_of_face` zerados; aviso "Vínculo perdido: {item}". `orig_parent` não é zerado | `apply.py:lose_link/on_depsgraph_update` | 🟢 |
| RN-15 | Desgrudar (004 RN-09): só age se `is_stuck`; pai volta a ser `orig_parent` (se existe e não é o próprio item), senão nenhum; posição no mundo mantida; `is_stuck`, `host`, `orig_parent`, `out_of_face` zerados. `u`/`v`/`distance`/`spin` ficam com o último valor | `link.py:release` | 🟢 |
| RN-16 | Assentar (004 D-04, D-16): transformações só são anotadas fora do período quieto de `QUIET_SECONDS = 0.6` s após abrir/desfazer/refazer; o tratamento roda `SETTLE_SECONDS = 0.2` s depois e é adiado enquanto houver modal de movimento ativo: `bl_idname` `transform.*`, um dos 7 de `_MOVE_IDS` ou instância de `hb_placement.PlacementMixin` | `apply.py:on_depsgraph_update/_settle_timer/modal_running/on_load_or_undo`; `settle.py:is_move_operator/_MOVE_IDS` | 🟢 |
| RN-17 | Pose de repouso: objeto cuja matriz de mundo (arredondada a 6 casas) é igual à da última vez que foi assentado é ignorado (Esc no G, desfazer): cancelar o arraste não gruda | `settle.py:returned_to_rest/_world_key/run` | 🟢 |
| RN-18 | Ordem por objeto no assentar: (1) vinculado → `project`; (2) `is_stuck` sem vínculo válido → ignora; (3) só raiz `MODULE`/`GEOMETRY` continua; (4) pai é parede (`IS_WALL_BP`) → `link_in_place` no lado `wall_side`; (5) senão ímã. Todos os casos (1), (4), (5) entram na reverificação de colisão; os grudados pelo ímã geram aviso "Elemento filho de: …" e **um** passo de desfazer "Grudar" | `settle.py:run/_undo_push/_check_collisions` | 🟢 |
| RN-19 | Ímã (004 RN-10a, D-06): ligado e distância vêm das preferências `stick_magnet` (padrão `True`) e `stick_magnet_distance` (padrão 0,05 m, 0,001–0,5 m); sem preferências (testes) → `(True, 0.05)`. Raio do centro da face +Y da caixa local do item, na direção +Y do item; aceita a primeira face de outro objeto a ≤ distância, de frente para o fundo (`normal·dir ≤ −0.7`), cujo hospedeiro não é piso nem teto; gruda com `center=False, rotate=True`; recusa (`ValueError`) vira "não grudou" | `magnet.py:preferences/find/try_stick`; `caffmob_draw/__init__.py:198-208` | 🟢 |
| RN-20 | Vínculo com a parede (004 RN-10, D-08): módulo raiz filho de parede (`parent` com `IS_WALL_BP`) sem vínculo ganha vínculo `BOX_SIDE` sem mover: `NEG_Y` (frente) se o giro Z mod 2π está a < 0,01 rad de 0 **e** `location.y < espessura/2`; senão `POS_Y` (trás). `distance` guarda o recuo atual. Ao abrir o arquivo (todos os módulos raiz da cena) e ao soltar um módulo/geometria na parede (assentar) | `migrate.py:wall_of/wall_side/run`; `link.py:link_in_place`; `settle.py:run` | 🟢 |
| RN-21 | `link_in_place` grava `orig_parent = host` (a parede), mesmo quando o pai já era ela; logo "Desgrudar" um módulo da parede o deixa filho da parede e ele volta a ser vinculado no próximo assentar com pose nova ou no próximo abrir (EC-04) | `link.py:link_in_place/release`; `migrate.py:run` | 🟢 (código) / 🟢 **Decisão do titular (2026-10-10, questions.md#pergunta-38):** "Desgrudar" passa a ser durável com marca gravada no `release` (ex. `btm_stick.opt_out`) e respeitada em `settle.run`/`migrate.run`. Pendência de implementação: DT-03 |
| RN-22 | Rótulo da face: `PLANE` → "plano"; hospedeiro parede (`classify.WALL`) com `NEG_Y`/`POS_Y` → "frente"/"trás"; demais → `tr(limits.FACE_LABELS[face])` (ex. "Direita (+X)"). Formato "<nome do hospedeiro> — <lado>" | `link.py:face_label` | 🟢 |
| RN-23 | Mover no plano: interseção do raio do mouse com o plano da face deslocado por `distance`; `u`/`v` = início + (ponto − âncora); com Ctrl, ímã ligado e o cursor sobre a face de **outro** hospedeiro, regruda lá (`center=True`) e reancora; Esc/botão direito restaura pai, inversa, matriz de mundo e os 13 campos de `btm_stick` | `ops_stick.py:BTM_OT_StickMove/snapshot/restore/_STICK_FIELDS` | 🟢 |
| RN-24 | Prévia do ímã (005 D-15): só desenho, durante modal de movimento, com ímã ligado, para item não grudado e não filho de parede; mostra o contorno do polígono acertado, a caixa do item girada e encostada, e "Grudar em: {hospedeiro}"; nada no objeto muda | `magnet_preview.py:compute/_draw_3d/_draw_2d`; `magnet.py:preview_pose` | 🟢 |
| RN-25 | Edição pelos campos: `u`, `v`, `distance` chamam `update_position`; `spin` chama `update_spin` (gira pelo centro da pegada em torno da normal pelo delta `spin − applied_spin`); gravações internas usam `apply.write`, que marca `(nome, campo)` em `props._guard` e não dispara `update`; item sem vínculo válido não se move | `props.py:_guarded/_guard`; `apply.py:write/update_position/update_spin` | 🟢 |
| RN-26 | Interações com outras units: grudado não pode ser convertido em agregado (`aggregates` RN-05); apagar pelo operador solta os grudados no lugar com "Vínculo perdido" (`aggregates` RN-29); grudado é raiz de componente e nunca entra no plano de exclusão (`selection` RN-07, RN-09); par grudado × hospedeiro não colide e "Afastar" só anda no plano (`collision` RN-03, RN-15) | consumidores citados | 🟢 |

## Requisitos Funcionais

🟡 Prioridades herdadas da 004 (RF-11 a RF-19), da 005 (RF-14/RF-15) e ajustadas pelo uso atual; não constituem roadmap aprovado.

| ID | Requisito | Prioridade | Critério de aceite | Confiança |
|---|---|---|---|---|
| RF-01 | Núcleo puro do referencial (RN-01 a RN-03, RN-06, RN-08, RN-13), testável sem Blender | Must | CA-01, CA-02, CA-03 | 🟢 |
| RF-02 | Comando "Grudar" (`caffmob.stick_to_face`): clique numa face plana de outro objeto (RN-04 a RN-09) | Must | CA-04, CA-05, CA-06 | 🟢 |
| RF-03 | Vínculo salvo no arquivo e restaurado ao reabrir (004 RF-18) | Must | CA-07 | 🟢 |
| RF-04 | Acompanhar o hospedeiro em mover, girar e mudar medida (RN-11, RN-12) | Must | CA-08, CA-09 | 🟢 |
| RF-05 | Projeção ao plano depois de movimento livre (RN-10, RN-16, RN-17) | Must | CA-10, CA-11 | 🟢 |
| RF-06 | Perda de vínculo e item fora da face com aviso em texto (RN-13, RN-14) | Must | CA-12, CA-13, CA-14 | 🟢 |
| RF-07 | "Desgrudar" (`caffmob.stick_release`) mantendo a posição (RN-15) | Must | CA-15 | 🟢 |
| RF-08 | Painel "Elemento filho" no item e lista "Elementos filhos" no hospedeiro, em texto (RN-22; 004 RF-17) | Must | CA-16 | 🟢 |
| RF-09 | API para consumidores (`local_box`, `item_corners`, `linked`, `face_of`, `project`, `stuck_items`, `release`, `item_of`) | Must | CA-17 | 🟢 |
| RF-10 | Gatilho da reverificação de colisão ao fim do assentar (`collision` RF-07) | Must | CA-18 | 🟢 |
| RF-11 | "Mover no plano" (`caffmob.stick_move`) com troca de face por Ctrl e cancelamento (RN-23) | Should | CA-19, CA-20 | 🟢 |
| RF-12 | Campos `u`, `v`, `distance`, `spin` editáveis (RN-25) | Should | CA-21 | 🟢 |
| RF-13 | Ímã ao soltar, com preferências (RN-19) | Should | CA-22, CA-23 | 🟢 |
| RF-14 | Migração e vínculo de módulo novo na parede (RN-20, RN-21; 004 RF-19) | Should | CA-24, CA-25 | 🟢 |
| RF-15 | Prévia do ímã durante o arraste (RN-24; 005 RF-14/RF-15) | Could | CA-26 | 🟢 |

## Requisitos Não Funcionais

| Tipo | Requisito observado | Evidência | Confiança |
|---|---|---|---|
| Desempenho | Handler barato: só reage a geometria de nomes do índice e compara com o cache `_last_box`; transformações só anotam o nome; o trabalho pesado vai para um temporizador único (0,2 s) que espera o fim do arraste | `apply.py:on_depsgraph_update/_settle_timer` | 🟢 |
| Desempenho | Índice hospedeiro → itens reconstruído sob demanda (varre `bpy.data.objects`) só depois de `invalidate()` (grudar, desgrudar, perder vínculo, abrir/desfazer/refazer) | `apply.py:index/invalidate` | 🟢 |
| Desempenho | Prévia do ímã recalcula `magnet.find` (até 8 `scene.ray_cast`) a cada redesenho durante o arraste | `magnet_preview.py:_draw_3d` | 🟢 (código) / 🟡 (custo não medido) |
| Precisão | Dez mudanças de espessura seguidas não acumulam erro (posição final a 1e‑9 m) | `tests/test_stick_frame.py:test_dez_mudancas_de_espessura_sem_erro_acumulado` (aprovado) | 🟢 |
| Separação | `frame.py` não importa `bpy` (só `math` e `aggregates.limits`); `__init__._modules` importa os demais tarde | `frame.py`; `__init__.py:_modules` | 🟢 |
| Reentrância | `_busy` impede o handler de reagir às mudanças que ele mesmo faz e às do temporizador; `props._guard` impede `update` recursivo | `apply.py:_busy/write`; `props.py:_guarded` | 🟢 |
| Robustez | Handler e temporizador engolem `ReferenceError` (objeto apagado); `modal_running` tolera `AttributeError`; prévia engole `ReferenceError`/`RuntimeError`/`ValueError` | `apply.py`; `magnet_preview.py:compute` | 🟢 |
| Desfazer | Operadores que alteram dados têm `UNDO`; o ímã (sem operador) empurra um passo "Grudar"; desfazer abre o período quieto para o retorno de pose não contar como gesto | `ops_stick.py`; `settle.py:_undo_push`; `apply.py:on_load_or_undo` | 🟢 |
| Ciclo de vida | 4 handlers de aplicação (`depsgraph_update_post`, `load_post`, `undo_post`, `redo_post`, `@persistent`) e 2 `draw_handler` registrados sem duplicar e removidos no `unregister`, que também cancela o temporizador e limpa o estado; `Object.btm_stick` removido antes das classes | `apply.py:register/unregister`; `magnet_preview.py:register/unregister`; `props.py:unregister` | 🟢 |
| Usabilidade | Estado sempre em texto ("Elemento filho de", "Item fora da face", "Vínculo perdido"), não só por cor | `panels.py` docstring; `apply.py:_warn` | 🟢 |

## Critérios de Aceitação

🟢 CA-01 a CA-03 são cobertos por `tests/test_stick_frame.py` (8 testes aprovados nesta extração) ou executados em Python puro; os marcados "fumaça" correspondem a passos de `tests/blender_004_stick_smoke.py` ou `tests/blender_005_viewport_smoke.py` (não executados aqui — Blender ausente no ambiente). _(Revisão 2026-10-10: ambas executadas com `/opt/blender/blender` 5.2.0 LTS: `blender_004_stick_smoke` → OK; `blender_005_viewport_smoke` via `xvfb-run` → 11 checagens OK)_

```gherkin
CA-01 — Ida e volta nas seis faces (puro)
Dado um painel (0..0,6 × 0..0,018 × 0..2,0) e um item qualquer
Quando, para cada face, desloco o item por frame.shift(frame, cantos, u+0,05, v−0,02, 0)
Então frame.params devolve (u+0,05, v−0,02, 0) com 9 casas

CA-02 — Escolha do tipo de face (puro; executado)
Dado a parede ((0; 0; 0), (4; 0,15; 2,6)) _(Revisão 2026-10-10: separadores corrigidos; a caixa é (4, 0.15, 2.6) m)_
Quando choose_face recebe ponto (2, 0, 1) e normal (0, −1, 0)
Então devolve (BOX_SIDE, NEG_Y); com normal a 1,1° do eixo, ou ponto a 0,6 mm do lado, ou ponto (2, 0,07, 1) dentro da parede, devolve (PLANE, None)

CA-03 — Face não plana e fora da face (puro)
Dado um polígono com um vértice a 2 mm do plano
Quando is_planar avalia com normal (0, 0, 1)
Então devolve False; a 0,4 mm devolve True; lista vazia devolve False
E um nicho cujo centro sai do retângulo de um painel encurtado dá out_of_face True; com extent None, False

CA-04 — Grudar num painel (fumaça, passo 3)
Dado um painel de 18 mm e um nicho solto
Quando chamo link.stick(nicho, painel, ponto na face +X, normal (1, 0, 0))
Então devolve (painel, 'POS_X'), nicho.parent é o painel, a distância medida é 0 (± 1e‑6) e face_label contém "Painel"

CA-05 — Grudar falha: face não plana ou alvo inválido
Dado o operador caffmob.stick_to_face em modal
Quando clico numa face cujo polígono não é plano, no próprio item ou num filho dele, ou o item é agregado
Então o operador reporta WARNING com o motivo de RN-01/RN-05, limpa a barra de status e devolve CANCELLED; nada muda

CA-06 — Grudar sem face sob o cursor
Dado o operador caffmob.stick_to_face em modal
Quando clico onde o raio não acerta nada (fora o próprio item, cortadores e anotações)
Então reporta WARNING "Nenhuma face sob o cursor" e continua em RUNNING_MODAL

CA-07 — Vínculo sobrevive a reabrir (fumaça, passo 10)
Dado o aéreo grudado na face POS_Y da parede e o arquivo salvo
Quando reabro e mudo a espessura para 0,22 m
Então btm_stick.is_stuck, host = Parede e face = 'POS_Y' persistem e o fundo do aéreo fica em Y = 0,22 (± 1e‑4)

CA-08 — Espessura muda (fumaça, passo 2; puro)
Dado balcão em NEG_Y e aéreo em POS_Y de uma parede de 0,15 m
Quando a espessura vai para 0,20 m e depois por 0,10/0,12/0,18/0,25/0,15
Então o aéreo continua encostado (fundo em Y = espessura ± 1e‑4) e o balcão não se move (± 1e‑6)

CA-09 — Item do outro lado do hospedeiro (fumaça, passo 2b)
Dado o aéreo em POS_Y
Quando ele é levado para Y = −profundidade − 1 mm (além da espessura) e assenta
Então a face vira 'NEG_Y' e o aéreo não é puxado através da parede; de volta a Y = 0,15, a face volta a 'POS_Y'

CA-10 — Movimento livre volta ao plano (fumaça, passo 4)
Dado o nicho grudado na face +X do painel
Quando o desloco 5 cm para fora e 10 cm para cima (local) e o assentar roda
Então a distância volta a 0 (± 1e‑6) e u/v passam a refletir a posição solta

CA-11 — Assentar espera o arraste e ignora a volta à pose
Dado um G nativo (transform.*) em andamento sobre um item grudado
Quando o temporizador dispara
Então ele se reagenda em 0,2 s sem tratar nada; ao cancelar o G (pose igual à de _settled), settle.run ignora o objeto e não gruda nem verifica colisão

CA-12 — Fora da face (fumaça, passo 6)
Dado um balcão grudado numa placa
Quando a placa encolhe e o centro da pegada sai do retângulo da face
Então out_of_face = True, is_stuck continua True, o balcão não se move (± 1e‑6) e a barra de status mostra "Item fora da face: Livre"

CA-13 — Apagar o hospedeiro pelo operador (fumaça, passo 7)
Dado o balcão grudado na placa
Quando executo caffmob.delete_with_aggregates com a placa selecionada
Então a placa some, o balcão fica sem vínculo, sem pai e no mesmo lugar (± 1e‑6)

CA-14 — Apagar o hospedeiro direto (fumaça, passo 8)
Dado uma caixa grudada em "Outro"
Quando removo "Outro" com bpy.data.objects.remove, chamo apply.invalidate() e o depsgraph atualiza
Então is_stuck = False e a caixa fica no mesmo lugar do mundo (restaurada de last_world)

CA-15 — Desgrudar (fumaça, passo 9)
Dado o nicho grudado no painel
Quando chamo link.release(nicho) e depois movo o painel 1 m em X
Então release devolve True, nicho.parent é None, o nicho não se move (± 1e‑6) nem acompanha o painel
E release num item não grudado devolve False

CA-16 — Painel em texto
Dado o aéreo grudado na face POS_Y de "Parede"
Quando o grupo "Posição e vínculo" desenha BTM_PT_Stick
Então aparece "Elemento filho de: Parede — trás", os campos Posição U/V, Distância, Giro e os botões "Mover no plano"/"Desgrudar"; selecionando a parede, aparece "Elementos filhos: 1" com "Aereo — trás"; num item solto aparece só "Grudar"

CA-17 — API de caixa para consumidores
Dado um módulo cuja raiz não tem geometria própria
Quando collision/scan.box_of ou cabinet_editor/bridge.root_box chama apply.local_box
Então recebe a caixa da união dos filhos (sem cortadores, anotações e obj_x), ou a origem se não houver nenhum

CA-18 — Colisão ao soltar (collision CA-15/CA-16)
Dado um balcão que, ao fim do assentar, sobrepõe outro item
Quando settle.run termina com o balcão em moved_roots
Então collision.scan.check_moved([balcão]) é chamado; se collision não importar (ImportError), nada acontece

CA-19 — Mover no plano
Dado um item grudado e a vista enxergando a face
Quando arrasto com caffmob.stick_move e clico com o botão esquerdo
Então u/v seguem o cursor no plano a cada MOUSEMOVE, distance não muda e o operador devolve FINISHED; com Esc ou botão direito, pai, inversa, matriz e os 13 campos voltam ao snapshot e devolve CANCELLED

CA-20 — Mover no plano com a vista paralela à face
Dado a vista de modo que o raio do mouse não intersecta o plano da face
Quando invoco caffmob.stick_move
Então reporta WARNING "Gire a vista para enxergar a face" e devolve CANCELLED

CA-21 — Campos de posição (004 RF-13)
Dado o aéreo grudado com distance 0
Quando digito Distância = 10 mm no painel
Então o aéreo se afasta 10 mm pela normal da face; num item com vínculo quebrado o campo não move nada

CA-22 — Ímã (fumaça, passo 5)
Dado um balcão solto com o fundo a 30 mm da face −Y de uma placa
Quando assenta com o ímã desligado, ou com distância 20 mm
Então não gruda; com o ímã padrão de 50 mm gruda, host = placa, distance 0 (± 1e‑4), barra de status "Elemento filho de: Placa — Frente (−Y)" e um passo de desfazer "Grudar"

CA-23 — Ímã recusa piso, teto e face de costas
Dado um item cujo raio do fundo acerta primeiro um piso/teto, ou uma face com normal·dir > −0,7
Quando o assentar roda
Então magnet.find devolve None e o item não gruda (mas entra na reverificação de colisão)

CA-24 — Migração (fumaça, passo 1)
Dado balcão filho da parede em Y = 0 sem giro e aéreo em Y = 0,15 girado 180°
Quando migrate.run(scene) roda
Então devolve 2, balcão em NEG_Y, aéreo em POS_Y, distâncias ≈ 0, face_label do aéreo termina em "trás" e btm_settings.stick_migrated = True; a segunda chamada devolve 0

CA-25 — Módulo novo na parede ao soltar
Dado um módulo raiz posto como filho da parede por uma biblioteca, sem vínculo
Quando o assentar o trata
Então link_in_place grava o vínculo no lado de wall_side sem mover o módulo e o ímã não é tentado

CA-26 — Prévia do ímã (fumaça 005)
Dado um aéreo arrastado por G a menos de 50 mm de uma placa, ímã ligado
Quando a viewport redesenha
Então magnet_preview.compute devolve (hospedeiro, ponto, polígono, 8 cantos) e aparecem contorno, caixa e "Grudar em: <hospedeiro>"; ao cancelar, nada gruda; com o ímã desligado ou longe da placa, compute devolve None
```

## Prioridade (MoSCoW)

| Requisitos | Classificação | Justificativa |
|---|---|---|
| RF-01 a RF-10 | 🟡 Must | 004 RF-11, RF-13 a RF-18; `apply.local_box`/`linked`/`project` sustentam `collision`, `cabinet_editor`, `aggregates`, `selection` |
| RF-11 a RF-14 | 🟡 Should | 004 RF-12, RF-19; há alternativa (G nativo + assentar; comando Grudar) |
| RF-15 | 🟡 Could | 005: só visual, o vínculo é gravado ao soltar de qualquer forma |

## Rastreabilidade de Código e Verificação

| Arquivo | Símbolos | Evidência |
|---|---|---|
| `caffmob_draw/stick/frame.py` | `BOX_SIDE`, `PLANE`, tolerâncias, `box_frame`, `plane_frame`, `frame_to_matrix`, `matrix_to_frame`, `frame_for`, `to_frame`, `from_frame`, `footprint`, `params`, `shift`, `face_extent`, `out_of_face`, `is_planar`, `choose_face`, `contact_axis` | 🟢 Código; `test_stick_frame` |
| `caffmob_draw/stick/props.py` | `_guard`, `FACE_ITEMS`, `KIND_ITEMS`, `IDENTITY`, `_guarded`, `BTM_PG_Stick` | 🟢 Código |
| `caffmob_draw/stick/apply.py` | caixas, `write`, `linked`, `update_position`, `project`, `_flip_if_across`, `update_spin`, `lose_link`, índice, handlers, temporizador | 🟢 Código; fumaça 004 |
| `caffmob_draw/stick/link.py` | `host_for`, `can_stick`, `oriented_matrix`, `orient`, `stick`, `link_in_place`, `release`, `face_label` | 🟢 Código; fumaça 004 |
| `caffmob_draw/stick/settle.py` | `_MOVE_IDS`, `is_move_operator`, `_undo_push`, `_settled`, `returned_to_rest`, `run`, `_check_collisions` | 🟢 Código; fumaça 004/005 |
| `caffmob_draw/stick/magnet.py` | `DEFAULT_DISTANCE`, `_MAX_STEPS`, `_FACING`, `preferences`, `find`, `_polygon`, `preview_pose`, `try_stick` | 🟢 Código; fumaça 004/005 |
| `caffmob_draw/stick/magnet_preview.py` | `compute`, `_moving_item`, `_draw_3d`, `_draw_2d` | 🟢 Código; fumaça 005; validação visual pendente |
| `caffmob_draw/stick/migrate.py` | `wall_of`, `wall_side`, `run` | 🟢 Código; fumaça 004 |
| `caffmob_draw/stick/ops_stick.py` | `item_of`, `scene_hit`, `snapshot`, `restore`, 3 operadores `caffmob.stick_*` | 🟢 Código |
| `caffmob_draw/stick/panels.py` | `BTM_PT_Stick` (não registrado) | 🟢 Código |

🟢 Executado em 2026-10-10: `cd tests && PYTHONDONTWRITEBYTECODE=1 python3 -m unittest test_stick_frame -v` → **8 testes aprovados** (ida e volta nas seis faces, aéreo de trás com parede mais grossa, dez mudanças sem erro acumulado, frente = `NEG_Y`, plano inclinado, fora da face, face plana, escolha do tipo de face). Executados também em Python puro: limites de 1° e 0,5 mm de `choose_face`, limite 0,7 de `contact_axis`, folga de 1 mm de `out_of_face`, `plane_frame` com normal Z (U = X). 🟢 `tests/blender_004_stick_smoke.py` e `tests/blender_005_viewport_smoke.py` não foram executados (Blender ausente). _(Revisão 2026-10-10: executados na revisão no Blender 5.2.0 LTS: 004 → "OK blender_004_stick_smoke" (10 passos); 005 com `xvfb-run` → "blender_005_viewport_smoke: OK", incluindo prévia a 30 mm, sem prévia a 80 mm e Esc sem grudar)_

## Lacunas e Divergências

- 🟢 Pai trocado pelo usuário (Ctrl+P/Alt+P) não faz perder o vínculo: a docstring de `apply.py` promete, mas só `host is None` dispara `lose_link` (EC-02). 🟢 **Decisão do titular (2026-10-10, questions.md#pergunta-36):** `parent != host` com `host` presente dispara `lose_link`. Pendência de implementação: DT-01.
- 🟢 Hospedeiro apagado fora do operador só perde o vínculo depois de algo invalidar o índice; a fumaça chama `apply.invalidate()` à mão (EC-01). 🟢 **Decisão do titular (2026-10-10, questions.md#pergunta-37):** o handler invalida o índice quando um update traz objeto com `btm_stick` (ou hospedeiro por `PointerProperty`). Pendência de implementação: DT-02.
- 🟢 `Desgrudar` um módulo filho de parede não é durável: o assentar ou a próxima abertura o vinculam de novo (RN-21, EC-04). 🟢 **Decisão do titular (2026-10-10, questions.md#pergunta-38):** tornar durável (marca no `release`). Pendência de implementação: DT-03.
- 🟢 Grudar está disponível para qualquer objeto ativo, inclusive parede, piso e teto, pelo painel e pelo poll (EC-18); o menu de contexto restringe aos tipos de item. 🟢 **Decisão do titular (2026-10-10, questions.md#pergunta-39):** alinhar poll e painel a `_ITEM_KINDS`. Pendência de implementação: DT-04.
- 🟢 Divergência com 004 D-06: o ímã não age dentro de `PlacementMixin.update_snap`; atua só depois do movimento (assentar) e a prévia é só desenho (005 D-15). _(Revisão 2026-10-10: `hb_placement.py` não referencia `stick`/`magnet`; ímã só em `settle.run` → `magnet.try_stick`)_
- 🟢 Divergência com 004 D-04(b): `project` restaura `distance`, mas não `spin`/orientação (EC-08). _(Revisão 2026-10-10: `apply.py:project` só grava `u`/`v` e chama `update_position` (translação))_
- 🟢 Divergência com 004 RN-10 ("Y local = 0 ou = espessura"): a regra usada é a das cotas (giro ≈ 0 e Y < espessura/2), e com falha na leitura da espessura um módulo em Y = 0 vira `POS_Y` (EC-05). `.reversa/context/modules.json` (nota) diz o contrário ("todo módulo com rotação ≈ 0 vira frente"). _(Revisão 2026-10-10: `migrate.py:wall_side`; nota em `.reversa/context/modules.json:4183`)_
- 🟢 Divergência com `_reversa_sdd/aggregates/design.md` (linhas 29 e 276): diz que `stick/` usa `limits.box_for(..., clamp_to_face=False)`; o código de `stick/` só usa `FACES`, `FACE_LABELS`, `face_axes` e `thickness`. _(Revisão cruzada 2026-10-10: aggregates/design.md, aggregates/requirements.md e flowcharts/aggregates-limits.md corrigidos)_ _(Revisão 2026-10-10: `grep box_for|clamp_to_face` em `caffmob_draw/stick/` vazio; as duas linhas do design de aggregates ainda trazem a afirmação)_
- 🟢 Divergência com `state-machines.md`: não há máquina de estados do vínculo do grudar (ver `design.md`); `permissions.md` diz "sem armazenamento próprio principal", mas `btm_stick` é salvo no `.blend`. _(Revisão 2026-10-10: `state-machines.md` não cita stick/vínculo; `permissions.md:42` traz "Sem armazenamento próprio principal")_ _(Revisão cruzada 2026-10-10: `state-machines.md` ganhou "Vínculo do grudar" e `permissions.md` passou a citar `Object.btm_stick` salvo no `.blend`)_
- 🟢 `btm_settings.stick_migrated` é gravado e nunca lido; a migração varre a cena a cada abertura (idempotente por `is_stuck`). _(Revisão 2026-10-10: único uso fora da declaração é a escrita em `migrate.py:50`)_
