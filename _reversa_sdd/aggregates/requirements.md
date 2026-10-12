# Agregados, Folhas, Grupos de Peças e Importação (aggregates) — Requisitos

🟢 **CONFIRMADO** — contrato extraído de `caffmob_draw/aggregates/` em 2026-10-10 (26 arquivos, 3.000 linhas; a árvore de trabalho não tem alterações sem commit nesta pasta, último commit que a tocou: `83a6863`). Confirmação de código não implica validação visual no Blender. 🟡 identifica inferência (prioridade, intenção, efeito no Blender); 🔴 identifica lacuna que exige decisão ou teste no Blender.

## Visão Geral

🟢 A unit faz cinco coisas sobre objetos que não são módulos paramétricos: (1) **converte** uma malha (ou um grupo de peças) em **agregado** preso a uma face de um objeto pai, com posição `u`/`v`/`offset` limitada ao contorno do pai, recorte 3D opcional (Perfurar), furo real para o plano de corte e marca de peça de produção (feature 003, RN-07 a RN-13); (2) converte em **folha** que gira ou corre por um pivô, com barra de abertura que para no primeiro contato com a cena (003 RN-11, RN-11a) e, numa **esquadria**, batentes de abrir e de fechar (feature 007, RN-06 a RN-09); (3) cria **grupos de peças** (Empty com membros), sugere esquadria e folhas pelo nome das peças e **instala** a esquadria numa parede HB (007, RN-03 a RN-05); (4) **importa** OBJ, FBX, glTF/GLB e SketchUp (`.skp` pelo OpenSKP) com unidade, eixo e árvore de grupos (007 RN-01; 009 RN-13/RN-14; 010 RN-07 a RN-09; 011 D-09); (5) oferece o **X/Delete** que apaga componentes inteiros perguntando se os agregados vão junto (011 D-05/D-06; 012). Inclui a simulação gráfica da folha na viewport e o painel "Agregados e folhas".

## Responsabilidades

- 🟢 Limites puros do agregado na face do pai (`limits.py`) e posicionamento no Blender, com regravação do valor ajustado (`apply.py`).
- 🟢 Converter e desconverter, guardando pai e matriz originais (`convert.py`).
- 🟢 Recorte 3D por caixa cortadora + `BOOLEAN`, furo real `CPM_CUTOUT` e peça de produção (`perforate.py`, `production.py`).
- 🟢 Folha: pivô, pose fechada, giro/correr, abertura com parada no contato, curso livre e batentes na esquadria (`leaf.py`, `sweep.py`, `slide_limits.py`, `collision.py`).
- 🟢 Grupo de peças, sugestão de grupos pelo nome e "Montar esquadria" (`group_props.py`, `group.py`, `grouping.py`, `ops_group.py`).
- 🟢 Instalar/desinstalar a esquadria numa parede HB (`window_props.py`, `install.py`, `ops_install.py`).
- 🟢 Importar modelo 3D com unidade, eixo e agrupamento; SketchUp em árvore de grupos (`import_units.py`, `ops_import.py`, `skp.py`, `skp_core.py`, `skp_build.py`).
- 🟢 Operadores de converter, mover arrastando, desconverter e apagar com agregados, com o atalho X/Delete (`ops_aggregate.py`).
- 🟢 Simulação gráfica da folha (`overlay.py`) e função de desenho do painel (`panels.py`).
- 🟢 Fora da responsabilidade: decidir **o que** é componente, raiz e subárvore a apagar (`selection/component.py`: `component_root`, `own_aggregates`, `deletes_subtree`, `delete_plan`; contrato em `_reversa_sdd/selection/`, RN-09, RN-10, F-03, F-04, EC-07); montar a porta/janela real que usa `group.create_group`, `leaf.make_leaf` e `collision.OPENING_FRAME_PROP` (contrato em `_reversa_sdd/openings/`, F-05, RN-11, RN-12); grudar itens (`stick/`, que reutiliza `limits.FACES`/`FACE_LABELS`/`face_axes`/`thickness`, mas não `box_for`: a docstring de `limits.box_for` sobre `clamp_to_face=False` no grudar está desatualizada _(Revisão cruzada 2026-10-10: único chamador de `box_for` é aggregates/apply.py:61)_); esticar agregados no Redimensionar (`selection/resize.py`, contrato em `_reversa_sdd/selection/`); listar a peça de produção no plano de corte (`cutting/part_sources.py`); a barra lateral que chama `panels.draw_aggregate` (`ui/object_properties.py`); o adaptador de inspeção das folhas (`inspection/adapters/aggregate_leaf.py`); deslizantes do editor de armário (`cabinet_editor/scene_slides.py`); "Mover Sobre" (contrato em `_reversa_sdd/move_over/`, que usa `group.object_corners`).

## Regras de Negócio

| ID | Regra confirmada | Fonte |
|---|---|---|
| RN-01 | 🟢 Referencial: tudo no espaço **local do pai**, caixas `(lo, hi)` alinhadas aos eixos dele. `FACES = ('POS_X', 'NEG_X', 'POS_Y', 'NEG_Y', 'POS_Z', 'NEG_Z')`, rótulos "Direita (+X)", "Esquerda (−X)", "Fundo (+Y)", "Frente (−Y)", "Topo (+Z)", "Base (−Z)". `face_axes(face)` = (eixo normal pela última letra, sinal +1 `POS`/−1 `NEG`, os outros dois eixos em ordem crescente como `u`, `v`). `u`, `v` = distância do canto mínimo do pai ao canto mínimo do agregado nesses eixos; `offset` = distância da face do pai à face do agregado voltada para ela (> 0 afasta, < 0 afunda) | `limits.py:FACES/FACE_LABELS/face_axes` |
| RN-02 | 🟢 Limites: `u ∈ [0, max(0, ps[u] − size[u])]`, `v` idem, `offset ∈ [−ps[n], +∞)` (afunda no máximo a espessura do pai no eixo normal). Agregado maior que a face fica preso em 0. `clamp` aplica `max(lo, valor)` e depois `min(hi, …)` | `limits.py:limits/clamp` |
| RN-03 | 🟢 Caixa a partir dos parâmetros: `lo[u] = lo_p[u] + u`, `lo[v] = lo_p[v] + v`, `lo[n] = hi_p[n] + offset` (face `POS`) ou `lo_p[n] − offset − size[n]` (face `NEG`), `hi = lo + size`; por padrão passa antes pelo `clamp` (`clamp_to_face=True`). `params_from_box` é o inverso sem clamp. `nearest_face` escolhe a face cujo plano está mais perto do centro do agregado; empate fica com a primeira na ordem de `FACES` | `limits.py:box_for/params_from_box/nearest_face` |
| RN-04 | 🟢 A posição é sempre recalculada de `u`/`v`/`offset`: `update_position` só age em agregado `AGGREGATE` cujo `parent_ref` é o pai Blender; grava de volta (sem disparar `update`) os valores ajustados que diferem mais de 1e‑9 e põe `location = box_for.lo − rest_offset`; depois sincroniza o recorte se `perforate` ou há cortador. O handler de depsgraph reposiciona os agregados de um pai **só** quando a caixa avaliada do pai mudou desde a última vista | `apply.py:update_position/on_depsgraph_update` |
| RN-05 | 🟢 Converter exige, nesta ordem: objeto de malha ou grupo de peças ("Selecione um objeto de malha para converter"); pai ("Selecione também o elemento pai (por último, como ativo)"); pai diferente do objeto e objeto que **não** seja descendente do pai ("O pai não pode ser o próprio objeto nem um filho dele"; o código testa `obj in parent.children_recursive`, o inverso da mensagem: objeto que já é filho/neto do pai é recusado e pai descendente do objeto passa) _(Revisão 2026-10-10: texto corrigido de "fora dos descendentes dele"; convert.py:can_convert linha 126; docs/rag/blender-api/corpus/bpy.types.Object.md#bpy.types.Object.children_recursive)_ (🟢 **Decisão do titular (2026-10-10, questions.md#pergunta-3):** testar `parent in obj.children_recursive`, como diz a mensagem, para evitar ciclo de parentesco. Pendência de implementação: DT-01); objeto não grudado ("O objeto está grudado numa face: desgrude antes"); pai que não seja folha `LEAF` ("Uma folha de porta não pode receber agregados") | `convert.py:can_convert` |
| RN-06 | 🟢 Converter: na primeira conversão guarda `orig_parent` e `orig_matrix` (mundo); vira filho Blender do pai mantendo o mundo (`matrix_parent_inverse` identidade); `face` = a escolhida ou `nearest_face` do centro da caixa do agregado no pai; `size` = medidas dessa caixa; `rest_offset = box.lo − location`; `u`/`v`/`offset` por `params_from_box`; então `update_position` (pode puxar o objeto para dentro do contorno) | `convert.py:convert` |
| RN-07 | 🟢 Desconverter: desliga e remove recorte e furo real; folha → `remove_pivot`; desmarca produção; devolve `orig_parent` e a matriz de mundo **da época da conversão** (não a atual); `is_aggregate = False`, `kind = 'AGGREGATE'`, `parent_ref = None` | `convert.py:unconvert` |
| RN-08 | 🟢 Perfurar: se o agregado afunda (interseção com a caixa do pai com as três medidas > 1e‑9), cria um cortador "`<agregado> - Recorte`" (caixa do volume afundado, 1 mm além da face de entrada e, se atravessa, da oposta), filho do pai, `IS_CUTTING_OBJ`, arame, oculto e fora do render, e um modificador `BOOLEAN` "Agregado (furo): `<agregado>`" `DIFFERENCE`/`EXACT` no pai, acrescentado ao fim da pilha. A malha do pai nunca é alterada; desligar ou deixar de afundar remove modificador, cortador e malha órfã | `perforate.py:sync/_sync_boolean/_expanded/_remove_boolean` |
| RN-09 | 🟢 Furo real: só com o pai tendo um modificador de nós `GeoNodeCutpart` ("O pai não é uma peça do plano de corte") e face `POS_Z`/`NEG_Z` ("O furo real só vale quando o agregado entra pela face da chapa (topo ou base da peça)"). Cria/atualiza um `CPM_CUTOUT` "Agregado: `<agregado>`" (`machining.AGGREGATE_PREFIX`) com `X`/`End X`, `Y`/`End Y` do volume afundado (Y espelhado se `Mirror Y`), `Route Depth = min(afundamento em Z, Thickness)` e `Flip Z = (face == NEG_Z) != Mirror Z` | `perforate.py:real_hole_reason/_sync_cutout` |
| RN-10 | 🟢 Peça de produção: `production_part` liga `btm_geometry.fabrication` (se o objeto tem `btm_geometry`); `sheet(obj)` devolve `(nome, maior, média, menor)` das medidas `size` em módulo, só para agregado marcado | `production.py:sync/sheet` |
| RN-11 | 🟢 Folha: um Empty pivô "`<folha> - Eixo`" (`SINGLE_ARROW` no giro, `PLAIN_AXES` no correr, tamanho 0,1) filho do pai; a folha é filha do pivô. A pose fechada no espaço do pai fica em `obj['btm_leaf_rest']` (16 floats); o pivô guarda `btm_leaf` (nome da folha), `btm_leaf_base` (ponto do eixo) e `btm_open_fraction`. Abrir só move o pivô; a malha nunca é alterada | `leaf.py:make_leaf/rebuild_pivot/apply_fraction` |
| RN-12 | 🟢 Eixo e sentido: `base_point` sobre a caixa fechada da folha no pai: correr → `lo`; `LEFT` → `(lo.x, lo.y, lo.z)`; `RIGHT` → `(hi.x, lo.y, lo.z)`; `TOP` → `(lo.x, lo.y, hi.z)`; `BOTTOM` → `lo`. Ângulo = `OUT_SIGN[hinge] × (+1 OUT, −1 IN) × fração × max_angle` com `OUT_SIGN = {LEFT: −1, RIGHT: +1, TOP: −1, BOTTOM: +1}`, em torno de Z (`LEFT`/`RIGHT`) ou X (`TOP`/`BOTTOM`): `OUT` sempre leva a borda livre para **−Y do pai** (a frente dos módulos). Correr: `base + (±1, 0, 0) × travel × fração` | `leaf.py:OUT_SIGN/base_point/swing_angle/pose_matrix` |
| RN-13 | 🟢 `open_value` é a fração 0 a 1 (graus = fração × `max_angle`; metros = fração × `travel`). Abrir varre em passos de 2° (tolerância 0,25°) no giro ou 10 mm (tolerância 1 mm) no correr; no primeiro passo com contato refina por bissecção e para no último valor livre; a barra é regravada com a fração alcançada e `contact_name`/`contact_kind` (`OPEN`, `CLOSE`, `NONE`) registram o contato | `sweep.py:sweep`; `leaf.py:update_open` |
| RN-14 | 🟢 Fechar: fora de uma esquadria é livre (não testa contato). Numa esquadria (pai = grupo `FRAME`) fechar também testa contato e não passa do batente `floor` = maior `close_stop(sinal do próprio sentido, deslocamento da folha irmã)` = `max(0, sinal × deslocamento)`; parar no batente cita a folha irmã como contato | `sweep.py:sweep(close=True)`; `leaf.py:_close_floor`; `slide_limits.py:close_stop` |
| RN-15 | 🟢 Folha de correr numa esquadria: sentido padrão para o próprio lado (centro da folha à esquerda do centro da esquadria → `NEG_X`, senão `POS_X`); ao criar o pivô mede o **curso livre** varrendo até a largura da esquadria e grava `free_travel` e `travel = max(livre, 1 mm)`, com a peça do fim do curso em `obj['btm_free_contact']`; `travel` acima de `free_travel + 1e‑6` é regravado em `free_travel`; o painel avisa "Pouco curso para este lado: inverta o sentido" quando `free_travel < 10 %` da largura da folha | `leaf.py:default_slide_dir/measure_free_travel/low_travel`; `props.py:_travel`; `slide_limits.py` |
| RN-16 | 🟢 Ao converter uma folha numa esquadria que já tem folhas, a sobreposição dos montantes no arquivo (`max(0, min(a1, b1) − max(a0, b0))` em X) é gravada em `rest_overlap` nas duas folhas | `leaf.py:make_leaf`; `slide_limits.py:rest_overlap` |
| RN-17 | 🟢 Contato: a folha numa pose é a caixa dela (8 cantos; de um grupo, a união das peças) com cada canto puxado `SHRINK` 1 mm em direção ao centro. Alvos: malhas da cena visíveis, fora `WIRE`/`BOUNDS`, `IS_CUTTING_OBJ`, `IS_2D_ANNOTATION` e peças com `btm_opening_frame` igual ao nome do pai. Excluídos: a folha, o pivô e descendentes; numa esquadria também as folhas irmãs (com pivôs e peças) e o próprio grupo `FRAME` (as peças da esquadria **contam**); fora dela, a raiz do módulo do pai (`fronts.module_root_of(pai)` ou o próprio pai) com **todos** os descendentes e o pai. Pré-filtro por AABB e confirmação por `BVHTree.overlap` | `collision.py:_excluded/_targets/Tester` |
| RN-18 | 🟢 Atualizações de propriedade passam por uma guarda `(nome do objeto, propriedade)`: o `update` não roda de novo enquanto a mesma propriedade do mesmo objeto está sendo aplicada, e `apply._write` grava sem disparar o `update` | `props.py:_guarded/_guard`; `apply.py:_write` |
| RN-19 | 🟢 Grupo de peças: Empty `CUBE` 0,05 com `btm_group.is_group = True` e `kind` (`PLAIN` "Grupo", `FRAME` "Esquadria", `LEAF` "Folha"), no centro em XY e no `z` mínimo da caixa de mundo das **malhas**; ligado às coleções da primeira malha (ou à da cena); se todas as malhas têm o mesmo pai não nulo, o grupo vira filho dele; cada malha vira filha do grupo sem mudar de lugar, com `orig_parent` e `orig_matrix` guardados em `members`. Desfazer devolve cada peça viva ao `orig_parent` na posição de mundo **atual** e apaga o Empty. Consequência para quem salva o grupo num `.blend` (object_library EC-08, confirmado por sonda): malhas com pai comum geram um grupo filho desse pai, e o pai vai junto para o arquivo do item _(Revisão cruzada 2026-10-10: group.py:67-73)_ | `group.py:create_group/ungroup`; `group_props.py` |
| RN-20 | 🟢 Sugestão de grupos: tira o sufixo `.NNN`; nomes cujo primeiro token (separado por `_`) é `folha`/`leaf`/`sash` (sem diferenciar maiúsculas) e com 2+ tokens formam a folha `token0_token1`; o resto vai para "Esquadria". Saída: folhas ordenadas pelo nome do grupo, esquadria por último (só se houver) | `grouping.py:leaf_key/suggest` |
| RN-21 | 🟢 Montar esquadria: linhas sugeridas (papel `FRAME` para a esquadria, `SLIDE` para as folhas; o usuário pode escolher `SWING` ou `IGNORE`); grupos `PLAIN` de importação selecionados são desfeitos antes; cria o grupo `FRAME` com as peças das linhas `FRAME` e, por linha `SLIDE`/`SWING`, um grupo `LEAF` filho da esquadria convertido com `make_leaf` (correr: depois corrige o sentido para o próprio lado, o que refaz o pivô e mede o curso; giro: padrões `LEFT`, `OUT`, 90°). Sem esquadria → "Escolha ao menos um grupo como esquadria" | `ops_group.py:BTM_OT_WindowAssemble` |
| RN-22 | 🟢 Instalar só com esquadria não instalada e parede HB (`IS_WALL_BP`; senão "Converta a parede pelo editor de paredes antes de instalar", mensagem que o operador nunca mostra porque `_selection` só reconhece como parede objetos com `IS_WALL_BP` _(Revisão 2026-10-10: ops_install.py:_selection)_): jaula `GeoNodeCage` "Window" com `IS_WINDOW_BP`, arame, `Dim X`/`Dim Z` = largura/altura da caixa da esquadria, `Dim Y` = `Thickness` da parede, filha da parede em `(x, 0, peitoril)` sem rotação, com `x` = centro da esquadria em X da parede − largura/2 preso a `[0, Length − largura]` (0 se a janela é mais larga que a parede); peitoril padrão 1,0 m. A esquadria vira filha da jaula, sem rotação, em `z = −lo.z`, com drivers `x = Dim X/2` e `y = Dim Y/2`; o vão é cortado por `doors_windows.cut_wall` | `install.py:can_install/install`; `ops_install.py` |
| RN-23 | 🟢 Desinstalar: remove os drivers de `location[0]` e `[1]` da esquadria, solta-a **sem pai** na posição de mundo atual, remove da parede todo `BOOLEAN` cujo objeto é a jaula, apaga os outros filhos da jaula e a jaula | `install.py:uninstall` |
| RN-24 | 🟢 Importar: extensões `.obj` (`wm.obj_import`), `.fbx` (`import_scene.fbx`), `.glb`/`.gltf` (`import_scene.gltf`) e `.skp` (OpenSKP). Eixo vertical `Z` → frente `Y`; `Y` → frente `NEGATIVE_Z` (OBJ) ou `-Z` (FBX); glTF sem eixo. Unidade: `MM` 0,001, `CM` 0,01, `M` 1, `IN` 0,0254; `AUTO` = mm se a maior medida do modelo em escala 1 passa de 50 unidades, senão m; glTF em `AUTO` não é escalado ("m"). A escala é aplicada às raízes importadas e, nas malhas com dados de um só usuário, passada para a malha (escala do objeto volta a 1) | `ops_import.py:_kwargs/_apply_unit`; `import_units.py` |
| RN-25 | 🟢 O arquivo importado com 2+ malhas vira um componente: uma raiz única que não é malha (Empty do FBX/glTF) é marcada como grupo `PLAIN`; senão, com 2+ raízes de malha, um grupo `PLAIN` novo com o nome do arquivo; com menos, nada é agrupado e as malhas ficam selecionadas | `ops_import.py:_group_import/execute` |
| RN-26 | 🟢 SketchUp: posições do glTF em metros, `(x, y, z) → (x, −z, y)`; `v` da UV invertido; um grupo `PLAIN` por instância seguindo `scene_hierarchy` (filhos primeiro, parentados ao grupo do pai sem mudar de lugar); figuras de escala (regex de "2D Woman/Man/Person/Figure/People" e nomes próprios do SketchUp) saem com os descendentes e são contadas; instâncias repetidas (mesmo caminho) recebem a primitiva cuja caixa está mais perto da `position_mm` delas; primitivas com o mesmo conjunto de vértices (6 casas) no mesmo grupo são descartadas (verso emitido à parte); contêiner sem malha some e, com um filho só, colapsa nele; geometria sem nó vai para um grupo "SketchUp" na frente | `skp_core.py:to_blender/_nodes/tree/_prune`; `skp_build.py:_build_node` |
| RN-27 | 🟢 Materiais do SketchUp: nome do SketchUp casado pela imagem (texturizado) ou pela cor RGB 0–255 (liso); `Layer_x` vira `x`; sem correspondência "SketchUp padrão". Reaproveitados entre importações pela assinatura `nome|r,g,b,a (3 casas)|arquivo da imagem` (`btm_skp_material`, `btm_skp_key`); texturas gravadas numa pasta temporária com nome seguro `skp_<índice>_<nome>.<ext>` e empacotadas no `.blend` | `skp_core.py:material_names/texture_filename`; `skp_build.py:_material/_image` |
| RN-28 | 🟢 Um `.skp` que não abre (sem a wheel do OpenSKP, arquivo inexistente, erro do formato, sem geometria) não cria nada e o relatório diz "Não foi possível ler o SketchUp: {motivo}. Salve numa versão recente do SketchUp ou exporte em glTF, OBJ ou FBX."; falha durante a montagem apaga os **objetos** criados e reporta o mesmo texto | `skp.py:available/read`; `ops_import.py:_import_skp`; `skp_core.py:failure_message` |
| RN-29 | 🟢 X/Delete no modo objeto age quando algum selecionado tem descendentes e é apagável em subárvore, tem agregados próprios ou itens grudados; só pergunta ("O objeto tem agregados", "Apagar também os agregados", padrão ligado) se há agregados próprios; senão apaga direto. Apagar: solta os grudados no lugar com aviso "Vínculo perdido: {item}", planeja com `component.delete_plan`, desconverte os agregados mantidos, tira da parede o `BOOLEAN` de cada vão apagado, apaga cortadores órfãos e remove tudo em lote (`bpy.data.batch_remove`). O comentário do `poll` ("parede, piso e teto seguem no Delete do Blender") é impreciso: parede, piso ou teto com módulo filho que tem agregado (ou com item grudado) passa no `poll` por `_children_aggregates`/`_stuck_children` e cai no operador do plugin (ver EC-16) _(Revisão cruzada 2026-10-10: ops_aggregate.py:212-218 poll; component.own_aggregates desce nos filhos da parede)_ | `ops_aggregate.py:BTM_OT_DeleteWithAggregates/delete_components/_release_stuck_children` |
| RN-30 | 🟢 Simulação gráfica: com uma folha convertida ativa (a folha, o pivô ou uma peça dentro do grupo-folha) e pivô vivo, desenha sem teste de profundidade o caminho do canto mais distante do eixo em 24 passos, o eixo (giro, com o comprimento da folha) ou o trilho (correr), a caixa atual (vermelha e mais grossa se há contato) e a caixa da peça de contato, mais o texto "Folha bateu em {}" (abrindo) ou "Folha encostou em {}" (fechando) | `overlay.py:_active_leaf/_draw_3d/_draw_2d` |
| RN-31 | 🟢 Desfazer grupo: a partir do ativo (ou da folha apontada por um pivô) sobe até o primeiro grupo; desconverte todos os grupos internos e o próprio grupo que forem agregados e desfaz cada um (internos primeiro) | `ops_group.py:_active_group/BTM_OT_GroupDissolve` |

## Requisitos Funcionais

🟡 Prioridades inferidas das features 003 (`_reversa_forward/003-modulos-agregados-reposicionar/requirements.md` RF-11 a RF-19), 007 (`007-janela-obj-folhas-colisao/requirements.md` RF-01 a RF-09), 009 (SketchUp), 010 (árvore do SketchUp), 011 (componente na importação e Delete, D-05, D-06, D-09) e 012 (exclusão em lote); não constituem roadmap aprovado.

| ID | Requisito | Prioridade | Critério de aceite |
|---|---|---|---|
| RF-01 | 🟢 Converter malhas ou grupos selecionados em agregados do ativo, na face mais próxima ou escolhida | Must | CA-01, CA-02 |
| RF-02 | 🟢 Posicionar por `u`/`v`/`offset` com limite no contorno e na espessura, mostrando mínimo e máximo | Must | CA-03, CA-04 |
| RF-03 | 🟢 Reposicionar os agregados quando o pai muda de tamanho | Must | CA-05 |
| RF-04 | 🟢 Mover o agregado arrastando no plano da face, com cancelamento | Should | CA-06 |
| RF-05 | 🟢 Perfurar o pai no volume afundado (só 3D) e, opcionalmente, furo real para o plano de corte | Must | CA-07, CA-08 |
| RF-06 | 🟢 Marcar o agregado como peça de produção | Should | CA-09 |
| RF-07 | 🟢 Desconverter devolvendo o objeto como era | Must | CA-10 |
| RF-08 | 🟢 Converter em folha de giro ou de correr com barra de abertura que para no contato | Must | CA-11, CA-12 |
| RF-09 | 🟢 Folha de correr na esquadria: sentido para o próprio lado, curso livre como teto, batente de fechar pela outra folha, aviso de pouco curso | Must | CA-13, CA-14 |
| RF-10 | 🟢 Simulação gráfica da folha na viewport | Must | CA-15 |
| RF-11 | 🟢 Criar e desfazer grupo de peças | Must | CA-16 |
| RF-12 | 🟢 Montar esquadria com sugestão pelo nome das peças | Should | CA-17 |
| RF-13 | 🟢 Instalar e desinstalar a esquadria numa parede HB | Should | CA-18 |
| RF-14 | 🟢 Importar OBJ/FBX/glTF com unidade e eixo, como um componente | Must | CA-19, CA-20 |
| RF-15 | 🟢 Importar SketchUp em árvore de grupos com materiais e texturas | Must | CA-21, CA-22 |
| RF-16 | 🟢 X/Delete apagando a subárvore e perguntando pelos agregados | Must | CA-23, CA-24 |
| RF-17 | 🟢 Painel "Agregados e folhas" com os campos do agregado ou da folha | Should | CA-25 |

## Requisitos Não Funcionais

| Tipo | Requisito observado | Evidência | Confiança |
|---|---|---|---|
| Testabilidade | `limits.py`, `sweep.py`, `slide_limits.py`, `grouping.py`, `import_units.py` e `skp_core.py` não importam `bpy` (só `re`, `dataclasses`, `data.i18n`); o `__init__` importa os módulos `bpy` de forma tardia para os testes carregarem os núcleos | docstrings; `__init__.py:_modules`; 7 arquivos de teste puros | 🟢 |
| Desempenho | Alvos de contato em cache por folha, BVH do alvo construída sob demanda e só para candidatos que passam no pré-filtro AABB; cache descartado por qualquer mudança de objeto fora das folhas/pivôs | `collision.py:_targets/_bvh/on_depsgraph_update` | 🟢 |
| Desempenho | Reposicionar só quando a caixa do pai muda (`_last_parent_box`); a malha do cortador só é refeita quando a chave `btm_box` (6 casas) muda, o que evita laço com o depsgraph | `apply.py:on_depsgraph_update`; `perforate.py:_sync_boolean` | 🟢 |
| Desempenho | Exclusão em lote com `bpy.data.batch_remove` ("um a um custava segundos com centenas de peças", feature 012). Nenhuma meta de tempo medida | `ops_aggregate.py:delete_components` | 🟢 (mecanismo) / 🟡 (meta) decisão: medir (DT-06; questions.md#pergunta-80) |
| Robustez | Handler de posição com trava `_busy` contra reentrada e `ReferenceError` engolido; pivô inexistente tratado (`pivot_of` → `None`); keymap removido engolindo `ReferenceError`/`RuntimeError`; leitura de `.skp` com a wheel ausente não quebra o resto do plugin | `apply.py`; `leaf.py:pivot_of`; `ops_aggregate.py:unregister`; `skp.py:available` | 🟢 |
| Segurança | Nome da textura do SketchUp reduzido ao nome do arquivo e a `[A-Za-z0-9_-]` (sem pastas) antes de gravar na pasta temporária | `skp_core.py:texture_filename` | 🟢 |
| Ciclo de vida | `register`/`unregister` simétricos: 3 `PointerProperty` em `bpy.types.Object` (`btm_aggregate`, `btm_group`, `btm_window`), 2 handlers `depsgraph_update_post` `@persistent` (`apply`, `collision`), 2 `draw_handler_add` (`overlay`), 2 itens de keymap (X e Delete); `unregister` na ordem inversa | `__init__.py`, `props.py`, `group_props.py`, `window_props.py`, `apply.py`, `collision.py`, `overlay.py`, `ops_aggregate.py` | 🟢 |
| Undo | Todos os operadores que alteram dados têm `{'REGISTER', 'UNDO'}`; `caffmob.aggregate_move` tem também `BLOCKING` | `ops_aggregate.py`, `ops_group.py`, `ops_install.py`, `ops_import.py` | 🟢 |
| Internacionalização | Mensagens com `tr`/`N_` e chaves em `data/translations/aggregates.json` (as 43 strings literais de `tr`/`N_` da unit têm chave). Passam sem `tr`: o relatório "Gire a vista para enxergar a face do pai", o título do diálogo "O objeto tem agregados", os rótulos do painel "Selecione a malha e, por último, o elemento pai." e "Pivô ausente; desconverta e converta de novo" (chave existe; a tradução depende da tradução automática de rótulos do Blender, 🟡) e o "{mín} a {máx}" do painel | `ops_aggregate.py`, `panels.py`, `aggregates.json` | 🟢 |
| Dependências opcionais | `openskp` (+ `defusedxml`, `mapbox_earcut`, `shapely`) como wheels da extensão, importado só ao ler `.skp` | `skp.py` docstring; `blender_manifest.toml` | 🟢 |

## Critérios de Aceitação

🟢 Os cálculos de CA-03, CA-04, CA-11 (varredura), CA-13, CA-14 (batentes), CA-17 (sugestão), CA-19 (unidade) e CA-21 (árvore do SketchUp) são cobertos por testes puros (`tests/test_aggregate_limits.py` 6, `test_leaf_sweep.py` 8, `test_slide_limits.py` 5, `test_grouping.py` 4, `test_import_units.py` 2, `test_skp_core.py` 5, `test_skp_tree.py` 5: **35 testes aprovados** em 2026-10-10). Os demais dependem do Blender (`tests/blender_003_aggregates_smoke.py`, `blender_007_window_smoke.py`, `blender_009_skp_smoke.py`, `blender_010_skp_tree_smoke.py`, `blender_004_collision_smoke.py`, `blender_011_component_smoke.py`, `blender_012_apply_smoke.py`, `blender_bug_skp_mover_sobre.py`; não executados nesta extração).

```gherkin
CA-01 — Converter em agregado (feliz)
Dado um painel de 600 × 18 × 700 mm ativo e uma fruteira selecionada encostada na frente dele
Quando executo caffmob.aggregate_convert com face AUTO
Então a fruteira vira filha do painel, btm_aggregate.is_aggregate é verdadeiro, face = NEG_Y
E o relatório INFO diz "Agregado(s) de <painel>: <fruteira> (Frente (−Y))" e a fruteira fica ativa e única selecionada

CA-02 — Converter recusado (falha)
Dado um objeto grudado (btm_stick.is_stuck) e um pai ativo
Quando executo caffmob.aggregate_convert
Então reporta WARNING "<objeto>: O objeto está grudado numa face: desgrude antes" e devolve CANCELLED
E com o pai sendo uma folha LEAF a mensagem é "Uma folha de porta não pode receber agregados"

CA-03 — Limite no contorno (feliz)
Dado um pai de 600 × 18 × 700 mm e um agregado de 200 × 50 × 100 mm na face NEG_Y
Quando gravo u = −1 e v = 5
Então u fica 0, v fica 0,6 (700 − 100 mm) e os campos mostram os valores ajustados

CA-04 — Afundar além da espessura (falha)
Dado o mesmo agregado
Quando gravo offset = −0,030
Então offset fica −0,018 (a espessura do pai) e o agregado não atravessa além da face oposta

CA-05 — Pai muda de tamanho (feliz)
Dado um agregado com u no máximo de um pai de 600 mm
Quando o pai passa a 400 mm de largura
Então o handler de depsgraph reposiciona o agregado com u ajustado ao novo máximo
E se a caixa avaliada do pai não mudou nenhum agregado é reposicionado

CA-06 — Mover arrastando (feliz e cancelamento)
Dado um agregado ativo na vista 3D
Quando executo caffmob.aggregate_move e arrasto além da borda
Então u/v param no limite; clique esquerdo confirma; Esc ou botão direito volta a (u, v) do início
E se o plano da face não é atingido pelo raio do mouse reporta WARNING "Gire a vista para enxergar a face do pai" e CANCELLED

CA-07 — Perfurar (feliz)
Dado um agregado com offset −0,010 num painel de 18 mm
Quando ligo perforate
Então existe "<agregado> - Recorte" filho do painel, oculto, e o modificador BOOLEAN "Agregado (furo): <agregado>" DIFFERENCE EXACT no painel
E com offset ≥ 0 (não afunda) o modificador e o cortador são removidos

CA-08 — Furo real indisponível (falha)
Dado um agregado perfurado na face NEG_Y de uma peça GeoNodeCutpart
Quando olho o painel
Então "Furo real no plano de corte" fica desabilitado com o motivo "O furo real só vale quando o agregado entra pela face da chapa (topo ou base da peça)"
E na face POS_Z, com real_hole, o pai recebe CPM_CUTOUT "Agregado: <agregado>" com Route Depth = min(afundamento, Thickness)

CA-09 — Peça de produção (feliz e falha)
Dado um agregado de 300 × 20 × 500 mm com btm_geometry
Quando ligo production_part
Então btm_geometry.fabrication é verdadeiro e production.sheet devolve (nome, 0,5, 0,3, 0,02)
E para um objeto não convertido ou sem a marca sheet devolve None

CA-10 — Desconverter (feliz)
Dado um agregado perfurado, com produção, convertido quando estava em P
Quando executo caffmob.aggregate_unconvert
Então o modificador e o cortador somem, production_part é falso, o objeto volta ao pai original na matriz P
E o relatório diz "1 objeto(s) desconvertido(s)"; sem agregados selecionados o poll falha

CA-11 — Folha de giro para no contato (feliz)
Dado uma folha de giro LEFT, OUT, máximo 90°, com uma parede a 40° no caminho
Quando ponho open_value = 1
Então a folha para no último ângulo livre (resolução 0,25°), open_value fica ≈ 40/90 e contact_name é a parede, contact_kind OPEN
E o painel mostra "Folha bateu em <parede>"

CA-12 — Fechar fora da esquadria (feliz) e pivô ausente (falha)
Dado a mesma folha aberta com algo entre ela e a posição fechada
Quando ponho open_value = 0
Então ela fecha sem testar contato (fração 0)
E se o pivô foi apagado update_open não faz nada e o painel mostra "Pivô ausente; desconverta e converta de novo"

CA-13 — Curso livre na esquadria (feliz)
Dado uma esquadria com duas folhas de correr montadas por caffmob.window_assemble
Quando a folha da esquerda é criada
Então slide_dir = NEG_X, free_travel = distância até o batente, travel = max(free_travel, 0,001)
E digitar travel maior que free_travel regrava free_travel

CA-14 — Batente de fechar pela outra folha (falha de passagem)
Dado a folha A (sentido +1) e a folha B deslocada +0,30 m da posição do arquivo
Quando fecho A até 0
Então A para em 0,30 m de abertura, contact_kind CLOSE e contact_name = B
E com B na posição do arquivo A volta até 0 sem contato

CA-15 — Simulação gráfica (feliz e falha)
Dado uma folha convertida ativa (ou seu pivô, ou uma peça do grupo-folha)
Quando a vista 3D redesenha
Então aparecem o caminho em 24 passos, o eixo ou trilho e a caixa atual (vermelha se há contato) com o texto do contato
E com um objeto que não é folha (ou folha sem pivô) nada é desenhado

CA-16 — Grupo de peças (feliz e falha)
Dado 15 malhas Folha_Esquerda_* selecionadas
Quando executo caffmob.group_create
Então o nome sugerido é "Folha_Esquerda", as malhas viram filhas de um Empty sem mudar de lugar e o grupo fica ativo
E sem malhas soltas selecionadas o poll falha com "Selecione as peças do grupo"; caffmob.group_dissolve devolve as peças soltas no lugar atual

CA-17 — Montar esquadria (feliz e falha)
Dado as 46 peças do OBJ janela_preta_1400mm (Folha_Esquerda_* 15, Folha_Direita_* 15, outras 16)
Quando executo caffmob.window_assemble sem mudar a sugestão
Então surgem a esquadria FRAME com 16 peças e 2 folhas LEAF de correr filhas dela; relatório "<nome>: esquadria com 16 peça(s) e 2 folha(s)"
E se nenhuma linha é FRAME reporta WARNING "Escolha ao menos um grupo como esquadria" e CANCELLED

CA-18 — Instalar na parede (feliz e falha)
Dado a esquadria e uma parede HB de 150 mm selecionadas
Quando executo caffmob.window_install com peitoril 1,0 m
Então surge a jaula "Window" IS_WINDOW_BP filha da parede com Dim X/Z da esquadria e Dim Y = 0,15, o vão cortado e a esquadria centrada por drivers
E com uma parede sem IS_WALL_BP o poll falha com "Selecione também a parede" (a parede não é reconhecida; "Converta a parede pelo editor de paredes antes de instalar" é inalcançável pelo operador) _(Revisão 2026-10-10: texto corrigido; ops_install.py:_selection, install.py:can_install)_; caffmob.window_uninstall solta a esquadria no lugar e fecha o vão

CA-19 — Unidade automática (feliz)
Dado um OBJ cuja maior medida em escala 1 é 1400
Quando importo com unidade AUTO e eixo Z
Então a escala 0,001 vai para as raízes e para as malhas (escala do objeto 1) e o relatório cita "unidade: mm"

CA-20 — Formato não suportado (falha)
Dado um arquivo ".3ds"
Quando executo caffmob.import_model
Então reporta ERROR "Formato não suportado: .3ds (use OBJ, FBX, glTF, GLB ou SKP)" e CANCELLED
E um importador nativo que levanta RuntimeError gera "O Blender não conseguiu importar <arquivo>: <erro>"

CA-21 — SketchUp em árvore (feliz)
Dado um .skp com um armário que contém duas portas iguais e uma figura "2D Woman"
Quando importo
Então surge um grupo do armário com os grupos das portas como filhos, cada porta com a própria geometria, sem a figura
E o relatório diz "SketchUp importado: {n} grupo(s) de peças de <arquivo>; 1 figura(s) de escala ignorada(s)"

CA-22 — SketchUp que não abre (falha)
Dado um .skp corrompido ou a wheel do OpenSKP ausente
Quando importo
Então nenhum objeto é criado e o ERROR diz "Não foi possível ler o SketchUp: <motivo>. Salve numa versão recente do SketchUp ou exporte em glTF, OBJ ou FBX."

CA-23 — Apagar com agregados (feliz)
Dado um balcão selecionado com uma fruteira agregada
Quando pressiono X
Então abre "O objeto tem agregados" com "1 agregado(s) presos aos objetos selecionados." e a opção ligada
E confirmando, balcão, fruteira e cortadores saem em lote; desligando a opção a fruteira é desconvertida e fica

CA-24 — X sem nada da unit (falha do poll)
Dado uma malha solta sem filhos, sem agregados e sem grudados
Quando pressiono X
Então o poll falha e o Delete padrão do Blender age

CA-25 — Painel (feliz e falha)
Dado um agregado AGGREGATE ativo
Quando abro "Agregados e folhas"
Então vejo pai, face, u/v com "mín a máx", offset com "mín.", Mover agregado, Perfurar, Furo real, Peça de produção e Desconverter
E sem agregado ativo vejo "Selecione a malha e, por último, o elemento pai."
```

## Prioridade (MoSCoW)

| Requisitos | Classificação | Justificativa |
|---|---|---|
| RF-01, RF-02, RF-03, RF-05, RF-07, RF-08 | 🟡 Must | 003 RF-12 a RF-16 e RF-18 são Must; `leaf`/`group`/`collision` são usados por `openings`, `cabinet_editor` e `inspection` |
| RF-09, RF-10, RF-11 | 🟡 Must | 007 RF-04, RF-06 a RF-09 e 003 RF-17 são Must; o caminho crítico da janela importada |
| RF-14, RF-15, RF-16 | 🟡 Must | Importação é a entrada de todo modelo externo (inclusive `object_library` chama `caffmob.import_model`); X/Delete é o atalho de exclusão de todo componente (011 D-05/D-06) |
| RF-04, RF-06, RF-12, RF-13, RF-17 | 🟡 Should | Há alternativa (campos, conversão manual, "Mover Sobre") ou 003/007 os marcam Should |
| Recalcular o recorte só ao soltar o arraste (003, NFR de desempenho) | 🟡 Won't (nesta versão) | O código sincroniza o booleano a cada movimento do arraste (EC-11); decisão: medir (DT-06; questions.md#pergunta-80): acima de ~30 ms por movimento, recortar só ao soltar |
| Devolver a esquadria desinstalada à posição de antes de instalar (`frame_matrix`) | 🟢 **Decisão do titular (2026-10-10, questions.md#pergunta-79):** Won't | `frame_matrix` é gravado e nunca lido (EC-14); manter soltar no lugar e corrigir a docstring de `window_props.py`. Pendência de implementação: DT-07 |

## Rastreabilidade de Código e Verificação

| Arquivo | Símbolos / responsabilidade | Evidência |
|---|---|---|
| caffmob_draw/aggregates/limits.py | `FACES`, `FACE_LABELS`, `_AXIS`, `face_axes`, `size`, `thickness`, `nearest_face`, `limits`, `clamp`, `box_for`, `params_from_box`, `sunk_box`, `sunk_depth` | 🟢 Código; `tests/test_aggregate_limits.py` |
| caffmob_draw/aggregates/sweep.py | `SWING_STEP`, `SWING_TOLERANCE`, `SLIDE_STEP`, `SLIDE_TOLERANCE`, `sweep` | 🟢 Código; `tests/test_leaf_sweep.py` |
| caffmob_draw/aggregates/slide_limits.py | `LOW_TRAVEL_RATIO`, `default_direction`, `sign`, `low_travel`, `rest_overlap`, `close_stop` | 🟢 Código; `tests/test_slide_limits.py` |
| caffmob_draw/aggregates/grouping.py | `LEAF_WORDS`, `FRAME_NAME`, `_SUFFIX`, `_clean`, `leaf_key`, `suggest` | 🟢 Código; `tests/test_grouping.py` |
| caffmob_draw/aggregates/import_units.py | `SCALE`, `AUTO_LIMIT`, `suggest`, `scale_for` | 🟢 Código; `tests/test_import_units.py` |
| caffmob_draw/aggregates/skp_core.py | `DEFAULT_MATERIAL`, `_EXT`, `MeshPlan`, `GroupPlan`, `_FIGURE`, `is_scale_figure`, `clean_material_name`, `to_blender`, `material_names`, `_nodes`, `tree`, `_prune`, `walk`, `plan`, `texture_filename`, `failure_message` | 🟢 Código; `tests/test_skp_core.py`, `test_skp_tree.py` |
| caffmob_draw/aggregates/props.py | `_guard`, `FACE_ITEMS`, `KIND_ITEMS`, `MOTION_ITEMS`, `HINGE_ITEMS`, `SWING_ITEMS`, `SLIDE_ITEMS`, `_guarded`, `_position`, `_perforate`, `_production`, `_open`, `_travel`, `_leaf_setup`, `BTM_PG_Aggregate`, `Object.btm_aggregate` | 🟢 Código |
| caffmob_draw/aggregates/group_props.py, window_props.py | `BTM_PG_GroupMember`, `BTM_PG_Group` (`Object.btm_group`); `BTM_PG_WindowInstall` (`Object.btm_window`) | 🟢 Código |
| caffmob_draw/aggregates/apply.py | `local_box`, `box_in_parent`, `parent_box`, `current_box`, `_write`, `update_position`, `aggregates_of`, `_busy`, `_last_parent_box`, `on_depsgraph_update` | 🟢 Código; `tests/blender_003_aggregates_smoke.py` (não executado) |
| caffmob_draw/aggregates/convert.py | `can_convert`, `convert`, `unconvert` | 🟢 Código |
| caffmob_draw/aggregates/perforate.py, production.py | `BOOL_PREFIX`, `CUTTER_SUFFIX`, `EPSILON`, `_cutpart_mod`, `real_hole_reason`, `_box_mesh`, `_expanded`, `_remove_boolean`, `_remove_cutout`, `_sync_boolean`, `_sync_cutout`, `sync`; `production.sync`, `sheet` | 🟢 Código |
| caffmob_draw/aggregates/leaf.py | `PIVOT_SUFFIX`, `REST_KEY`, `FREE_CONTACT_KEY`, `OPEN_KEY`, `OUT_SIGN`, `rest_matrix`, `local_corners`, `leaf_box`, `frame_of`, `sibling_leaves`, `frame_span`, `displacement`, `base_point`, `swing_angle`, `pose_matrix`, `pivot_of`, `apply_fraction`, `current_fraction`, `rebuild_pivot`, `default_slide_dir`, `measure_free_travel`, `low_travel`, `make_leaf`, `remove_pivot`, `update_open`, `_close_floor` | 🟢 Código; `tests/blender_003_aggregates_smoke.py`, `blender_007_window_smoke.py` (não executados) |
| caffmob_draw/aggregates/collision.py | `SHRINK`, `OPENING_FRAME_PROP`, `_SKIP_DISPLAY`, `_BOX_FACES`, `_cache`, `_own`, `invalidate`, `_excluded`, `_targets`, `_bvh`, `Tester`, `on_depsgraph_update` | 🟢 Código |
| caffmob_draw/aggregates/group.py | `is_group`, `members`, `object_corners`, `world_box`, `group_box`, `create_group`, `ungroup`, `box_corners` | 🟢 Código |
| caffmob_draw/aggregates/install.py, ops_install.py | `WINDOW_FLAG`, `WALL_FLAG`, `DEFAULT_SILL`, `NOT_HB_WALL`, `is_frame`, `frame_of`, `cage_of`, `can_install`, `install`, `uninstall`; `caffmob.window_install`, `caffmob.window_uninstall` | 🟢 Código; `tests/blender_007_window_smoke.py` (não executado) |
| caffmob_draw/aggregates/ops_group.py | `ROLE_ITEMS`, `caffmob.group_create`, `caffmob.group_dissolve`, `BTM_PG_AssembleRow`, `caffmob.window_assemble` | 🟢 Código |
| caffmob_draw/aggregates/ops_import.py, skp.py, skp_build.py | `caffmob.import_model`, `UNIT_ITEMS`, `UP_ITEMS`, `FORMATS`, `_group_import`; `skp.available`, `skp.read`; `SKP_TAG`, `KEY_PROP`, `_image`, `_material`, `_mesh_object`, `_empty_group`, `_build_node`, `build` | 🟢 Código; `tests/blender_009_skp_smoke.py`, `blender_010_skp_tree_smoke.py` (não executados) |
| caffmob_draw/aggregates/ops_aggregate.py | `caffmob.aggregate_convert`, `caffmob.leaf_convert`, `caffmob.aggregate_unconvert`, `caffmob.aggregate_move`, `caffmob.delete_with_aggregates`, `delete_components`, keymap X/Delete | 🟢 Código; `tests/blender_011_component_smoke.py`, `blender_012_apply_smoke.py` (não executados) |
| caffmob_draw/aggregates/overlay.py, panels.py | Cores, `ARC_STEPS`, `_draw_3d`, `_draw_2d`; `draw_aggregate`, `BTM_PT_Aggregate` (não registrado) | 🟢 Código |
| caffmob_draw/aggregates/__init__.py | `_modules`, `register`, `unregister` | 🟢 Código |

🟢 Executado em 2026-10-10: `cd tests && python3 -m unittest test_aggregate_limits test_leaf_sweep test_slide_limits test_grouping test_import_units test_skp_core test_skp_tree` → **35 testes aprovados** (6 + 8 + 5 + 4 + 2 + 5 + 5). Não cobrem nenhum módulo com `bpy`.

## Lacunas e Pré-condições

- 🟢 Pai de agregado `AGGREGATE` sem geometria (grupo de peças/Empty, inclusive uma esquadria): `apply.local_box` usa o `bound_box` do Empty (a API documenta −1 em todos os valores quando não há caixa), não a união das peças (EC-01). 🟢 **Decisão do titular (2026-10-10, questions.md#pergunta-28):** usar a união das malhas, após confirmar o `bound_box` de Empty no 5.2 em teste de fumaça. Pendência de implementação: DT-03.
- 🟢 Desconverter (inclusive pelo X/Delete com "Apagar também os agregados" desligado) devolve o objeto à matriz da **época da conversão**: se o pai foi movido depois, o agregado "salta" de volta (EC-02), contrariando a descrição "os agregados ficam soltos na mesma posição". 🟢 **Decisão do titular (2026-10-10, questions.md#pergunta-27):** manter a matriz de mundo corrente e devolver só o pai original. Pendência de implementação: DT-02.
- 🟢 Folha cujo pai não pertence a módulo (ex.: uma parede) exclui do contato **toda** a subárvore desse pai (EC-07). 🟢 **Decisão do titular (2026-10-10, questions.md#pergunta-29):** excluir só o pai e a própria folha. Pendência de implementação: DT-04.
- 🟢 Obstáculo mais fino que um passo da varredura (2° ou 10 mm) pode ser atravessado (EC-05). 🟢 **Decisão do titular (2026-10-10, questions.md#pergunta-30):** manter o passo atual até haver caso real de obstáculo fino.
- 🟢 Mudar `swing_sign` ou `max_angle` com a folha aberta reposiciona sem teste de contato (EC-06). 🟢 **Decisão do titular (2026-10-10, questions.md#pergunta-30):** fechar (fração 0) e reabrir pela varredura. Pendência de implementação: DT-05.
- 🟡 Sem meta de desempenho para a varredura (até 45 testes de BVH por abertura de 90°, mais a bissecção) nem para `measure_free_travel` em cenas grandes; decisão: medir (DT-06; questions.md#pergunta-80).
- 🟢 Pré-condição: `hb_types.GeoNodeCage` (`create`, `set_input`, `var_input`), `GeoNodeWall.get_input`, `GeoNodeObject.driver_location`, `GeoNodeCutpart.add_part_modifier('CPM_CUTOUT', nome)`; `compat.try_get_gn_input/try_set_gn_input`; `cutting/machining.AGGREGATE_PREFIX = "Agregado: "`; `inspection/fronts.module_root_of`; `operators/doors_windows.cut_wall`; `selection/component` (`own_aggregates`, `deletes_subtree`, `delete_plan`); `stick/apply.stuck_items`, `stick/link.release`, `btm_stick`; `ui/save_feedback.show`; `data/i18n` (`tr`, `N_`), `data/units.format_value`; `btm_geometry` (unit `geometry_free`), com os contratos citados em `design.md` › Dependências.
