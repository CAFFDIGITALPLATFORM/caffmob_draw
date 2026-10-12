# Seleção, Componente e Dimensões (selection) — Requisitos

🟢 **CONFIRMADO** — contrato extraído de `caffmob_draw/selection/` em 2026-10-10 (9 arquivos, 949 linhas; a árvore de trabalho não tem alterações sem commit nesta pasta, último commit que a tocou: `83a6863`). Confirmação de código não implica validação visual no Blender. 🟡 identifica inferência (prioridade, intenção); 🔴 identifica lacuna que exige decisão ou teste no Blender.

## Visão Geral

🟢 A unit responde, para qualquer objeto da cena e de qualquer biblioteca, **"o que é isto?"** (`classify`: tipo, objeto representante, módulo dono e biblioteca; RN-01 e D-09 da feature 002) e **"qual é o componente inteiro?"** (`component_root`: a raiz que deve ser selecionada, movida e apagada junto; feature 011, D-01). Com isso ela mantém a **seleção por componente** (um handler troca peças selecionadas pelas raízes; Alt + clique escolhe só a peça), monta o **plano de exclusão** em profundidade, lê e grava **dimensões por biblioteca** (RN-03 e D-10 da 002), mede o **elemento tocado** para o aviso da viewport e executa o **Redimensionar** da largura com adaptação dos agregados. Fontes: `classify.py` e `component.py` (núcleo puro, sem `bpy`), `editing.py`, `element_size.py`, `resize.py` (ponte com a cena), `component_props.py`, `component_select.py`, `component_pick.py` (propriedades, handlers, operadores e keymap), `__init__.py` (só docstring).

## Responsabilidades

- 🟢 Classificar um objeto em 12 tipos e 5 bibliotecas, com precedência fixa (`classify.classify`).
- 🟢 Achar a raiz de módulo (`module_root`), o grupo de peças de topo (`free_group`) e as raízes do "Mover Sobre" (`movable_root`, `reference_root`).
- 🟢 Achar a raiz do componente pela precedência D-01 (`component.component_root`) e colapsar listas de objetos em raízes (`collapse`).
- 🟢 Planejar a exclusão em profundidade, filhos antes dos pais (`delete_plan`, `own_aggregates`, `deletes_subtree`).
- 🟢 Normalizar a seleção às raízes num `depsgraph_update_post` (`component_select.on_depsgraph_update`), com isenções do Alt + clique.
- 🟢 Registrar o interruptor `Scene.btm_component_select`, o estado de sessão `WindowManager.btm_component_exempt`, os operadores `caffmob.component_pick` e `caffmob.component_click_reset` e os itens de keymap.
- 🟢 Ler e gravar dimensões, peitoril e medidas de parede por biblioteca, com validação de domínio (`editing.py`).
- 🟢 Identificar o elemento tocado e medir largura × altura × profundidade (`element_size.py`).
- 🟢 Mudar a largura do elemento e esticar/reposicionar os agregados na proporção (`resize.py`).
- 🟢 Fora da responsabilidade: apagar os objetos (`aggregates/ops_aggregate.py:delete_components`, que consome `delete_plan`), o diálogo Redimensionar (`ui/ops_resize.py:btm.resize_width`), o aviso de medidas (`overlays/element_toast.py`), os campos do painel (`ui/object_properties.py`), as cotas (contrato em `_reversa_sdd/measure/`), o "Mover Sobre" (contrato em `_reversa_sdd/move_over/`), o clamp dos agregados (`aggregates/limits.py`, `aggregates/apply.py`) e a conversão furo ↔ folha da porta (`operators/doors_windows.py`, `openings/door_core.py`).

## Regras de Negócio

| ID | Regra confirmada | Fonte |
|---|---|---|
| RN-01 | 🟢 Precedência do classificador: `None` → `None`; `IS_2D_ANNOTATION` no próprio objeto → `ANNOTATION`/`HB`; se algum ancestral (inclusive) é raiz de módulo: o **primeiro** ancestral abaixo da raiz que é frente → `FRONT` (o puxador filho da porta conta como a porta); objeto = raiz → `MODULE`; senão `PART`. Sem módulo, sobe os ancestrais (inclusive) testando **por nó, nesta ordem**: `IS_ENTRY_DOOR_BP` → `ROOM_DOOR`/HB; `IS_WINDOW_BP` → `WINDOW`/HB; `btm_kind == 'OPENING'` → `WINDOW`/BTM; `'GEOMETRY'` → `GEOMETRY`/BTM; `IS_OBSTACLE` ou `IS_SOFFIT_BP` → `OBSTACLE`/HB; `IS_WALL_BP` → `WALL`/HB; `btm_kind == 'WALL'` → `WALL`/BTM; `IS_FLOOR_BP` ou `btm_kind == 'FLOOR'` → `FLOOR` (HB se `IS_FLOOR_BP`, senão BTM); `IS_CEILING_BP` → `CEILING`/HB. Nada casou → `OTHER` com `obj = root = objeto` e biblioteca `''` | `classify.py:classify` |
| RN-02 | 🟢 Raiz de módulo = primeiro ancestral (inclusive) com `IS_FRAMELESS_CABINET_CAGE` (FRAMELESS), `IS_FACE_FRAME_CABINET_CAGE` ou `IS_FACE_FRAME_PRODUCT_CAGE` (FACE_FRAME), `IS_CLOSET_STARTER_CAGE` (CLOSETS), testados nessa ordem, ou `btm_kind == 'MODULE'` (BTM) | `classify.py:MODULE_TAGS/module_library/module_root` |
| RN-03 | 🟢 Frente = qualquer marca de `FRONT_TAGS` (`IS_DOOR_FRONT`, `IS_DRAWER_FRONT`, `IS_PULLOUT_FRONT`, `IS_FLIP_UP_DOOR`, `IS_CABINET_FRONT`), ou `hb_part_role` ∈ {`DOOR`, `DRAWER_FRONT`, `PULLOUT_FRONT`, `TILT_OUT`, `FRONT_PIVOT`, `CLOSET_DOOR_FRONT`, `CLOSET_DRAWER_FRONT`}, ou nome terminado em `_Door_L`, `_Door_R` ou `_Door_Flip` | `classify.py:_is_front` |
| RN-04 | 🟢 `btm_plane.object_kind` só vale quando foi gravado (`is_property_set('object_kind')`); sem `btm_plane` ou não gravado → `''`. O padrão `WALL` do enum não torna um objeto parede (BUG-20261007-TBY3). Objeto sem `is_property_set` (simulado) usa o valor direto | `classify.py:btm_kind` |
| RN-05 | 🟢 "Mover Sobre": movível = `info.root` para `FRONT`, `PART`, `MODULE`, `GEOMETRY`, `OBSTACLE`; o grupo de peças mais alto (`free_group`) para `OTHER` (ou `None` se não houver); `None` para porta, janela, parede, piso, teto e anotação. Referência = a parede (`info.obj`) para `WALL`, senão o movível | `classify.py:movable_root/reference_root` |
| RN-06 | 🟢 `free_group(obj)` = o ancestral (inclusive) **mais alto** com `btm_group.is_group` verdadeiro, ou `None` | `classify.py:free_group` |
| RN-07 | 🟢 Raiz do componente, a primeira regra que casa: (1) algum ancestral (inclusive) é vão (`IS_ENTRY_DOOR_BP`, `IS_WINDOW_BP` ou `btm_kind == 'OPENING'`) → o vão **mais baixo** da cadeia; (2) objeto com `IS_2D_ANNOTATION` → ele mesmo; (3) subindo do objeto até o primeiro módulo (sem incluí-lo): primeiro nó grudado (`btm_stick.is_stuck`) ou agregado próprio → ele; (4) há módulo → a raiz se `modes.get(library, True)`, senão o próprio objeto; (5) primeiro ancestral com `btm_object_item.is_item`; (6) `free_group`; (7) o próprio objeto. `None` → `None` | `component.py:component_root` |
| RN-08 | 🟢 Agregado próprio = `btm_aggregate.is_aggregate` verdadeiro **e** não ser folha de esquadria (`kind == 'LEAF'` com `parent_ref` sendo grupo `btm_group.is_group` de `kind == 'FRAME'`) | `component.py:_is_own_aggregate/_is_frame_leaf` |
| RN-09 | 🟢 Exclusão em profundidade: cada alvo leva a subárvore inteira, **filhos antes dos pais**, sem repetir; nó não-alvo grudado nunca entra (solto no lugar pelo consumidor); com `keep_aggregates`, os agregados próprios de cada alvo e toda a subárvore deles ficam; alvo parede/piso/teto (classificado como o próprio objeto) sai **sozinho**; `openings` = nós removidos que são vão | `component.py:delete_plan/deletes_subtree` |
| RN-10 | 🟢 `own_aggregates(target)`: desce pelos filhos sem entrar em vãos; agregado próprio que é a própria raiz de componente é recolhido e não se desce nele; alvo vão ou grupo `FRAME` → `[]` | `component.py:own_aggregates` |
| RN-11 | 🟢 Normalizador: não age com a trava `_busy`, com `btm_component_select` desligado (e então esquece a assinatura), sem `view_layer`, fora de `context.mode == 'OBJECT'`, sem `window_manager` ou com modal cujo `bl_idname` (minúsculo) contém `transform` ou `caffmob` ou começa com `btm`; sai cedo se a assinatura (nomes selecionados, nome do ativo) não mudou | `component_select.py:on_depsgraph_update/_modal_running/_signature` |
| RN-12 | 🟢 Promoção: para cada selecionado não isento cuja raiz é outro objeto presente na camada, seleciona a raiz e, **só se ela ficou selecionada**, desseleciona a peça; o ativo não isento passa para a raiz se ela está selecionada | `component_select.py:normalize` |
| RN-13 | 🟢 Modos de módulo: sem a interface herdada (`legacy.gate.legacy_ui()` falso) → `{}` (todo módulo sobe); com ela, `FRAMELESS` sobe só com `frameless_selection_mode == 'Cabinets'`; `FACE_FRAME` com `face_frame_selection_mode_enabled` falso ou modo `'Cabinets'`; `CLOSETS` com `closet_selection_mode_enabled` falso ou modo `'Starters'`; biblioteca ausente do dicionário (e BTM) sobe | `component_select.py:cabinet_modes` |
| RN-14 | 🟢 Isenções: nomes em `WindowManager.btm_component_exempt` separados por `\n`, gravados ordenados; o normalizador poda os que não estão mais selecionados; `load_post` limpa tudo; clique sem modificador (com isenções) limpa tudo e deixa o clique seguir | `component_select.py:exempt_names/set_exempt/normalize/on_load_post`; `component_pick.py:BTM_OT_ComponentClickReset` |
| RN-15 | 🟢 Alt + clique seleciona a peça sob o cursor (`view3d.select`) com o normalizador suspenso e a marca isenta; Alt + Shift + clique soma às isenções atuais; sem Shift, as isenções anteriores são descartadas | `component_pick.py:BTM_OT_ComponentPick.invoke` |
| RN-16 | 🟢 Dimensões editáveis: `MODULE` → largura, altura, profundidade; `ROOM_DOOR`/`WINDOW` **HB** → largura e altura; os demais (geometria, obstáculo, janela BTM, outro) só leitura. `has_dimensions`: `MODULE`, `ROOM_DOOR`, `WINDOW`, `GEOMETRY`, `OBSTACLE` | `editing.py:editable_dimensions/has_dimensions` |
| RN-17 | 🟢 Limites (m, inclusivos): largura e altura 0,01–10; profundidade 0,005–10; comprimento de parede 0,05–100; pé-direito inicial 0,5–10 (`WALL_LIMITS`); pé-direito final 0,5–10; espessura 0,01–2; peitoril 0–5. Fora → `ValueError("Valor Inválido: {rótulo} deve estar entre {lo} e {hi} (recebido: {v}).")` com valores na unidade da cena, sem alterar nada | `editing.py:LIMITS/WALL_LIMITS/_check` |
| RN-18 | 🟢 Onde gravar: face frame → `root.face_frame_cabinet.<campo>`; closets → `root.hb_closet_starter.<campo>`; módulo rápido → `root.btm_cabinet.<campo>`; frameless → input GN `Dim X/Y/Z` + `standards.sync.add_override(root, 'Dim …')` + `hb_utils.run_calc_fix(context, root)`; porta/janela HB → input GN `Dim X` (largura) / `Dim Z` (altura) do vão, sem refazer a porta real | `editing.py:set_dimension` |
| RN-19 | 🟢 Peitoril = `location.z` do vão; porta → `ValueError("Valor Inválido: o peitoril de uma porta é sempre 0.")` | `editing.py:get_sill/set_sill` |
| RN-20 | 🟢 Parede: só `library == 'HB'` é editável (senão `ValueError("Valor Inválido: esta parede não é editável por aqui.")`); campos `length`→`Length`, `height`→`Height`, `end_height`→`End Height`, `thickness`→`Thickness`; gravar `height` grava também `End Height` (RN-18 da 002); toda gravação recalcula as meias-esquadrias de **todas** as paredes (`update_all_wall_miters`) | `editing.py:set_wall` |
| RN-21 | 🟢 Elemento tocado: anotação ou nada → `None`; frente/peça → o módulo; módulo, porta, janela, geometria, obstáculo, parede → `info.obj` com o rótulo do tipo; piso, teto e outro → `free_group(obj)` ou o objeto, rótulo "Objeto" (o `info` guarda o tipo original) | `element_size.py:element` |
| RN-22 | 🟢 Medida do elemento (largura, altura, profundidade): parede HB pelos inputs `Length`, `Height`, `Thickness`; tipos com GN pela `editing.get_dimension`, com a **porta convertida para a folha** (`_hole_to_leaf`); o resto pela caixa local × escala (`box_size`), com profundidade = eixo Y local | `element_size.py:size/box_size` |
| RN-23 | 🟢 Redimensionar: elemento `None`, piso, teto, parede BTM → não; largura 0,01–100 m (`ValueError("Valor Inválido: a largura deve estar entre 0.01 e 100.0 m.")`); elementos sem largura própria (`OTHER`, obstáculo sem `home_builder.mod_name`) são esticados por `scale.x` (o ramo "geometria sem `btm_geometry`" de `_stretched` é inalcançável com o add-on registrado: `Object.btm_geometry` é `PointerProperty` e nunca é `None`; geometria livre grava `btm_geometry.width`, e na placa YZ a largura não aparece na malha — geometry_free EC-04) _(Revisão cruzada 2026-10-10: resize.py:72-73 e :99-100)_; porta grava a largura do **furo** convertida da folha (`_leaf_to_hole`) e refaz a porta real (`_sync_opening`) | `resize.py:can_resize/_stretched/_set_width/resize` |
| RN-24 | 🟢 Agregados no Redimensionar (só elementos com largura própria): cada objeto da subárvore do elemento que tem agregados é medido no X local antes e depois; com fator `nova/antiga` (|fator − 1| ≥ 1e-6), folhas `LEAF` não mudam; agregados em face com normal em Y ou Z são esticados no eixo local alinhado ao X do pai (`scale`, `size[0]`, `rest_offset[0]`); agregados em face lateral (normal X) só são reposicionados; `u`/`v` são multiplicados pelo fator quando o eixo deles é X | `resize.py:resize/_stretch_aggregate` |

## Requisitos Funcionais

🟡 Prioridades inferidas das features 002 (`_reversa_forward/002-editor-parede-mover-sobre/`, RN-01, RN-03, RN-05, D-09, D-10), 011 (`_reversa_forward/011-selecao-por-componente/requirements.md` RF-01 a RF-08, RF-12; `roadmap.md` D-01 a D-08), 012 (D-05) e do commit `640b2c2` (aviso e Redimensionar); não constituem roadmap aprovado.

| ID | Requisito | Prioridade | Critério de aceite |
|---|---|---|---|
| RF-01 | 🟢 Classificar qualquer objeto (tipo, representante, módulo dono, biblioteca) com a precedência RN-01 | Must | CA-01 |
| RF-02 | 🟢 Raízes do "Mover Sobre" (movível e referência) | Must | CA-02 |
| RF-03 | 🟢 Raiz do componente pela precedência D-01, incluindo modo de módulo da biblioteca herdada | Must | CA-03, CA-04 |
| RF-04 | 🟢 Colapsar uma lista de objetos em raízes, sem repetir, na ordem | Should | CA-05 |
| RF-05 | 🟢 Plano de exclusão em profundidade, com grudados preservados e opção de manter agregados | Must | CA-06, CA-07 |
| RF-06 | 🟢 Normalizar a seleção às raízes, venha de clique, caixa, lista ou script | Must | CA-08, CA-09 |
| RF-07 | 🟢 Interruptor "Seleção por componente" salvo no arquivo, ligado por padrão, com dica na barra lateral | Must | CA-10 |
| RF-08 | 🟢 Alt + clique seleciona só a peça; Alt + Shift soma; clique comum volta ao componente | Must | CA-11 |
| RF-09 | 🟢 Ler e gravar largura/altura/profundidade por biblioteca, com validação | Must | CA-12, CA-13 |
| RF-10 | 🟢 Ler e gravar peitoril e medidas de parede HB | Should | CA-14 |
| RF-11 | 🟢 Elemento tocado e medidas para o aviso da viewport e o diálogo Redimensionar | Should | CA-15 |
| RF-12 | 🟢 Redimensionar a largura adaptando os agregados | Should | CA-16, CA-17 |

## Requisitos Não Funcionais

| Tipo | Requisito observado | Evidência | Confiança |
|---|---|---|---|
| Testabilidade | `classify.py` e `component.py` não importam `bpy` (só `collections`, `data.i18n.N_` e o próprio `classify`); usam só `.get()`, `.parent`, `.children` e atributos, e rodam com objetos simulados | docstrings; `tests/test_classify.py`, `test_component_core.py`, `test_component_delete.py` | 🟢 |
| Desempenho | O normalizador sai cedo comparando a assinatura da seleção (conjunto de nomes + ativo) a cada `depsgraph_update_post`; montar a assinatura percorre a seleção inteira a cada atualização. Nenhuma meta medida | `component_select.py:on_depsgraph_update` | 🟢 (mecanismo) / 🟡 (meta) decisão: medir/testar (DT-04; questions.md#pergunta-77): medir uma vez com ~500 objetos selecionados; abaixo de 5 ms por atualização, não definir meta |
| Robustez | Objeto apagado na seleção de um contexto sobrescrito (`ReferenceError`) é descartado; `select_set` inválido (`RuntimeError`) é ignorado; remoção de keymap engole `ReferenceError`/`RuntimeError`; leitura GN falha em `get_dimension` cai para `obj.dimensions` | `component_select.py:_selected/normalize`; `component_pick.py:unregister`; `editing.py:get_dimension` | 🟢 |
| Ciclo de vida | `register`/`unregister` idempotentes; handlers `@persistent`; `unregister` remove handlers, itens de keymap, classes e as duas propriedades | `component_select.py`, `component_pick.py`, `component_props.py` | 🟢 |
| Internacionalização | Rótulos com `N_` e mensagens com `tr`; chaves em `data/translations/selection.json` (23 chaves `pt_BR`/`en_US`). Exceções: o nome/descrição de `btm_component_select` e os `bl_label` não passam por `tr` (traduzidos pelo Blender, se houver) e mensagens do `hb_types` em inglês podem vazar (EC-10) | `classify.py`, `editing.py`, `resize.py`, `component_props.py` | 🟢 |
| Undo | `caffmob.component_pick` tem `{'REGISTER', 'UNDO'}`; `caffmob.component_click_reset` é `INTERNAL` e sem undo; o normalizador age em handler (sem passo de undo próprio) | `component_pick.py`; `component_select.py` | 🟢 |

## Critérios de Aceitação

🟢 CA-01 a CA-07 têm cálculo coberto por testes puros (`tests/test_classify.py`, `test_component_core.py`, `test_component_delete.py`, 12 testes aprovados em 2026-10-10) ou verificado nesta extração com os mesmos objetos simulados. CA-08 a CA-17 dependem do Blender (`tests/blender_011_component_smoke.py`, `blender_toast_resize_invert.py`, `blender_bug_TBY3_walls.py`, `blender_012_legacy_gate_smoke.py`; não executados nesta extração).

```gherkin
CA-01 — Classificar (feliz e falha)
Dado um balcão IS_FRAMELESS_CABINET_CAGE filho de uma parede IS_WALL_BP, com uma porta IS_DOOR_FRONT e um puxador filho dela
Quando classifico o puxador, a porta, o balcão e a parede
Então FRONT(obj=porta, root=balcão, FRAMELESS), FRONT(porta), MODULE(balcão), WALL(parede, HB)
E uma malha sem marcas cujo btm_plane.object_kind não foi gravado é OTHER com biblioteca '' (não WALL)
E classify(None) devolve None

CA-02 — Raízes do Mover Sobre
Dado uma dobradiça dentro do grupo SketchUp "Porta SKP" (grupo de topo), a maçaneta de um vão de porta e a parede
Quando chamo movable_root e reference_root
Então movable_root(dobradiça) = "Porta SKP"; movable_root(maçaneta) = None (porta não se move pelo Mover Sobre)
E reference_root(parede) = parede; movable_root(parede) = None

CA-03 — Raiz do componente (feliz)
Dado a porta real: vão → marco FRAME → pivô → folha LEAF (parent_ref = marco) → maçaneta, e o símbolo 2D filho do vão
Quando chamo component_root na maçaneta, na folha e no símbolo
Então devolve o vão nos três casos
E a fruteira (agregado) do balcão devolve a fruteira; o vaso grudado devolve o vaso; a cota filha do balcão devolve a cota

CA-04 — Modo peça da biblioteca herdada
Dado o puxador da porta do balcão FRAMELESS
Quando chamo component_root com modes = {'FRAMELESS': False}
Então devolve o próprio puxador
E com modes = {} ou {'FRAMELESS': True} devolve o balcão; o módulo rápido (BTM) sobe sempre

CA-05 — Colapsar
Dado [pé da cadeira (item da biblioteca), a cadeira, maçaneta, vidro da janela, malha solta]
Quando chamo collapse
Então [cadeira, porta, janela, malha solta], sem repetir e na ordem

CA-06 — Plano de exclusão (feliz)
Dado o vão de porta do CA-03
Quando chamo delete_plan([vão])
Então remove = {vão, marco, pivô, folha, maçaneta, símbolo} com a maçaneta antes da folha, a folha antes do marco e o vão por último
E openings = [vão]; delete_plan([vão, folha, maçaneta]) tem 6 itens sem repetição

CA-07 — Exclusão com grudados, agregados e parede (falha de propagação proposital)
Dado o balcão com fruteira (agregado com peça) e vaso grudado, filho da parede
Quando chamo delete_plan([balcão]) e delete_plan([balcão], keep_aggregates=True)
Então o primeiro remove a fruteira e a peça dela, e nenhum dos dois remove o vaso
E o segundo não remove a fruteira nem a peça dela, mas remove o puxador
E delete_plan([parede]).remove = [parede] (porta e balcão ficam)

CA-08 — Normalizar clique numa peça (feliz)
Dado o interruptor ligado, modo objeto e nenhum modal rodando
Quando o usuário clica na maçaneta de uma porta real
Então após o depsgraph_update_post a maçaneta está desselecionada, o vão está selecionado e é o ativo

CA-09 — Normalizador inativo (falha)
Dado o interruptor desligado, ou o modo de edição, ou um transform/caffmob/btm modal rodando
Quando a seleção muda para uma peça
Então a peça continua selecionada; religar o interruptor promove a seleção atual na próxima atualização (forget)

CA-10 — Interruptor
Dado um arquivo novo ou um arquivo antigo sem a propriedade
Quando leio Scene.btm_component_select
Então é True; draw_toggle mostra "Seleção por componente" com CHECKBOX_HLT e a dica "Ligada: Alt + clique seleciona uma peça"
E desligado mostra CHECKBOX_DEHLT e "Desligada: clique seleciona a peça"

CA-11 — Alt + clique
Dado o interruptor ligado
Quando Alt + clique na almofada de uma porta, depois Alt + Shift + clique em outra peça
Então as duas peças ficam selecionadas e isentas (btm_component_exempt com os dois nomes ordenados)
E um clique sem modificador limpa as isenções antes do view3d.select; com o interruptor desligado o Alt + clique é o do Blender

CA-12 — Gravar dimensão (feliz)
Dado um módulo FACE_FRAME, um CLOSETS, um BTM e um FRAMELESS
Quando set_dimension(context, info, 'width', 0.9)
Então gravam face_frame_cabinet.width, hb_closet_starter.width, btm_cabinet.width e o input Dim X (com override "Dim X" e run_calc_fix), respectivamente

CA-13 — Dimensão inválida (falha)
Dado um módulo qualquer
Quando set_dimension com width = 0.005, ou com depth em um obstáculo
Então ValueError "Valor Inválido: Largura deve estar entre … e … (recebido: …)" / "Valor Inválido: Profundidade não é editável para este objeto."
E nada é gravado

CA-14 — Peitoril e parede
Dado uma janela HB e uma parede HB
Quando set_sill(janela, 1.1) e set_wall(parede, 'height', 2.7)
Então janela.location.z = 1.1; Height = End Height = 2.7 e as meias-esquadrias são recalculadas
E set_sill numa porta, set_wall numa parede BTM e set_wall 'height' = 0.3 levantam "Valor Inválido…"

CA-15 — Elemento tocado
Dado uma porta HB de vão com folha 0,80 × 2,10 m, uma frente de um balcão e um grupo SketchUp
Quando chamo element e size
Então a porta mede a folha (0,80 × 2,10), a frente devolve o balcão com o rótulo "Módulo", o grupo devolve o grupo de topo com "Objeto" e medida da caixa × escala
E uma cota devolve None

CA-16 — Redimensionar (feliz)
Dado um balcão de 0,60 m com um agregado numa face frontal (normal Y) e outro na face lateral (normal X)
Quando resize(context, el, 0.90)
Então a largura do balcão vira 0,90; o agregado frontal é esticado ×1,5 no eixo alinhado ao X do pai e o u dele (eixo X) ×1,5
E o lateral só é reposicionado (escala e size inalterados)

CA-17 — Redimensionar inválido (falha)
Dado um piso, uma parede BTM, ou uma largura de 0,005 m ou 150 m
Quando chamo resize
Então ValueError "Valor Inválido: este elemento não pode ser redimensionado por aqui." / "…a largura deve estar entre 0.01 e 100.0 m."
E nada muda; o operador btm.resize_width reporta o erro e devolve CANCELLED
```

## Prioridade (MoSCoW)

| Requisitos | Classificação | Justificativa |
|---|---|---|
| RF-01, RF-02 | 🟡 Must | Base de 33 consumidores (cotas, Mover Sobre, grudar, colisão, editor de armário, painel) |
| RF-03, RF-05 a RF-08 | 🟡 Must | 011 RF-01, RF-03, RF-05 a RF-08, RF-12 são Must |
| RF-09 | 🟡 Must | 002 RN-03/D-10: campos de dimensão do painel e do editor de armário |
| RF-04 | 🟡 Should | 011 RF-02 é Should |
| RF-10, RF-11, RF-12 | 🟡 Should | Edição pelo painel e Redimensionar (commit 640b2c2) são caminhos alternativos aos editores |
| Refazer a porta real ao editar a largura pelo painel | 🟡 Won't (nesta versão) | `set_dimension` não chama `_sync_opening` (EC-08) |

## Rastreabilidade de Código e Verificação

| Arquivo | Símbolos / responsabilidade | Evidência |
|---|---|---|
| caffmob_draw/selection/classify.py | `Classified`, `KINDS`, `KIND_LABELS`, `LIBRARY_LABELS`, `MODULE_TAGS`, `FRONT_TAGS`, `FRONT_ROLES`, `BTM_FRONT_SUFFIXES`, `btm_kind`, `_btm_kind`, `module_library`, `_is_front`, `_ancestors`, `module_root`, `classify`, `free_group`, `movable_root`, `reference_root` | 🟢 Código; `tests/test_classify.py` |
| caffmob_draw/selection/component.py | `DeletePlan`, `is_opening_root`, `_is_stuck`, `_is_frame_leaf`, `_is_own_aggregate`, `_is_item`, `component_root`, `collapse`, `own_aggregates`, `_is_frame_group`, `deletes_subtree`, `delete_plan` | 🟢 Código; `tests/test_component_core.py`, `test_component_delete.py` |
| caffmob_draw/selection/component_select.py | `_busy`, `_last`, `forget`, `suspended`, `cabinet_modes`, `exempt_names`, `set_exempt`, `_modal_running`, `_selected`, `_signature`, `normalize`, `on_depsgraph_update`, `on_load_post`, `register`, `unregister` | 🟢 Código; `tests/blender_011_component_smoke.py` (não executado) |
| caffmob_draw/selection/component_pick.py | `BTM_OT_ComponentPick` (`caffmob.component_pick`), `BTM_OT_ComponentClickReset` (`caffmob.component_click_reset`), `_enabled`, keymap | 🟢 Código |
| caffmob_draw/selection/component_props.py | `Scene.btm_component_select`, `WindowManager.btm_component_exempt`, `_on_toggle`, `draw_toggle` | 🟢 Código |
| caffmob_draw/selection/editing.py | `DIM_FIELDS`, `DIM_LABELS`, `GN_DIM`, `WALL_FIELDS`, `LIMITS`, `WALL_LIMITS`, `_check`, `has_dimensions`, `editable_dimensions`, `get_dimension`, `set_dimension`, `get_sill`, `set_sill`, `get_wall`, `set_wall` | 🟢 Código |
| caffmob_draw/selection/element_size.py | `Element`, `_GN_KINDS`, `element`, `_door_kind`, `box_size`, `size` | 🟢 Código; `tests/blender_toast_resize_invert.py` (não executado) |
| caffmob_draw/selection/resize.py | `MIN_WIDTH`, `MAX_WIDTH`, `can_resize`, `_parents_with_aggregates`, `_width_x`, `_stretch_aggregate`, `_stretched`, `_set_width`, `resize` | 🟢 Código; `tests/blender_toast_resize_invert.py` (não executado) |
| caffmob_draw/selection/__init__.py | Só docstring `"Pacote selection (feature 002)."` | 🟢 Código |

🟢 Executado em 2026-10-10: `PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=tests python3 -m unittest test_classify test_component_core test_component_delete`: **12 testes aprovados** (2 + 5 + 5). Não cobrem `component_select.py`, `component_pick.py`, `editing.py`, `element_size.py` nem `resize.py`.

## Lacunas e Pré-condições

- 🟢 **Decisão do titular (2026-10-10, questions.md#pergunta-20):** o painel usa o mesmo caminho do Redimensionar (`_leaf_to_hole` + `_sync_opening`) e mostra a medida da folha (010 RN-01/RN-02); idem questions.md#pergunta-69 (`set_dimension` chama `doors_windows._sync_opening` para ROOM_DOOR/WINDOW). 🟢 (código) hoje grava só o furo (`Dim X`/`Dim Z`), não refaz a porta real e mostra o furo (EC-08). Pendência de implementação: DT-02.
- 🟢 **Decisão do titular (2026-10-10, questions.md#pergunta-2):** `own_aggregates` para em raízes de módulo e em alvos que não levam a subárvore (parede, piso, teto): agregados de módulos filhos não entram na pergunta. 🟢 (código) hoje `own_aggregates(parede)` desce nos módulos filhos e, com "Apagar também os agregados" desligado, desconverte agregados de módulos não apagados (EC-07). Pendência de implementação: DT-01.
- 🟢 **Decisão do titular (2026-10-10, questions.md#pergunta-21):** bloquear janela BTM em `can_resize` até existir caminho próprio. 🟢 (código) hoje passa em `can_resize` e `_set_width` falha com `GeoNodeCage.set_input('Dim X')` (EC-10). Pendência de implementação: DT-03.
- 🟡 Sem meta de desempenho para o normalizador em cenas com muitas peças selecionadas — decisão: medir/testar (DT-04; questions.md#pergunta-77).
- 🟢 Pré-condição: `data/i18n.py` (`N_`, `tr`), `data/units.py` (`get_scene_length_unit`, `format_length`), `hb_types.GeoNodeObject/GeoNodeWall/GeoNodeCage`, `standards/sync.add_override`, `hb_utils.run_calc_fix`, `operators/walls.update_all_wall_miters`, `operators/doors_windows` (`_hole_to_leaf`, `_leaf_to_hole`, `_sync_opening`), `openings/sync.kind_of`, `aggregates/group.object_corners`, `aggregates/apply` (`local_box`, `aggregates_of`, `_write`, `update_position`), `aggregates/limits.face_axes` e `legacy/gate.legacy_ui`, com os contratos citados em `design.md` › Dependências.
