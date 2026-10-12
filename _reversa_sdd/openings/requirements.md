# Porta e Janela Reais e Região na Parede (openings) — Requisitos

🟢 **CONFIRMADO** — contrato extraído de `caffmob_draw/openings/` em 2026-10-10 (11 arquivos, 1.169 linhas; a árvore de trabalho não tem alterações sem commit nesta pasta, último commit que a tocou: `83a6863`). Confirmação de código não implica validação visual no Blender. 🟡 identifica inferência (prioridade, intenção); 🔴 identifica lacuna que exige decisão ou teste no Blender.

## Visão Geral

🟢 A unit transforma a **caixa** de porta ou janela do Home Builder (`GeoNodeCage` com `IS_ENTRY_DOOR_BP` ou `IS_WINDOW_BP`, que continua sendo o cortador do furo na parede) numa **porta ou janela real**: um gerador paramétrico puro produz as peças (porta de giro com marco, guarnições, folha almofadada e ferragens; janela de correr de alumínio com vidro e peitoril), uma montagem as junta em poucas malhas por papel com materiais compartilhados, e uma sincronização por **assinatura** monta e refaz o conjunto dentro da caixa, transformando as folhas em agregados `LEAF` que abrem (feature 010, RN-01 a RN-04, RN-10; D-07 a D-16). Também oferece "Atualizar portas e janelas" para arquivos antigos, a tecla **I** que inverte a dobradiça (commit `640b2c2`) e a **região marcada** na parede, um retângulo de dois cliques que define o vão exato da próxima porta ou janela (feature 011, RN-10 a RN-12; D-10 a D-12). Fontes: `door_core.py`, `window_core.py`, `region_core.py` (núcleo puro, sem `bpy`), `materials.py`, `build.py`, `sync.py`, `props.py`, `region_props.py` (ponte e estado), `ops.py`, `region.py` (operadores, keymap, desenho) e `__init__.py` (registro).

## Responsabilidades

- 🟢 Gerar as peças da porta (simples, dupla, vão aberto) no referencial da caixa e converter furo ↔ folha (`door_core.door_parts`, `hole_size`, `leaf_size`).
- 🟢 Gerar as peças da janela de correr e o curso das folhas (`window_core.window_parts`, `travel`).
- 🟢 Encaixar uma região marcada numa parede, com motivo de recusa (`region_core.fit`, `REASONS`).
- 🟢 Criar uma vez por arquivo e reaproveitar os 8 materiais (`materials.get`).
- 🟢 Juntar as peças em uma malha por papel (marco, ferragens do marco, folha N, ferragens da folha N) com UV de caixa e chanfro (`build.build`).
- 🟢 Montar e refazer a porta/janela real na caixa só quando a assinatura muda, preservando abertura das folhas e marcação de produção (`sync.sync`).
- 🟢 Registrar `Object.btm_opening_real` (salvo) e `WindowManager.btm_wall_region` (sessão).
- 🟢 Operadores `caffmob.openings_update`, `btm.door_invert_hand` (tecla I), `caffmob.wall_region` (modal de dois cliques) e `caffmob.wall_region_clear` (Esc na vista 3D), com o desenho `POST_PIXEL` da região e o `load_post` que a descarta.
- 🟢 Hospedar o registro de `ui/view_mode` (modos de vista Sólido/Textura e Linhas da feature 010, RF-08), cujo contrato fica na unit `ui`.
- 🟢 Fora da responsabilidade: criar a caixa, posicioná-la, cortar a parede, o modal de inserção e os diálogos de porta/janela (`operators/doors_windows.py`, que chama `sync.sync` por `_sync_opening` e aplica `region_core.fit` em `place_in_region`); abrir e limitar as folhas (`aggregates/leaf.make_leaf`, `aggregates/collision`, `aggregates/apply`); o painel "Aberturas" (`ui/sidebar_build.py`); re-sincronizar no OK do Editor de Paredes (contrato em `_reversa_sdd/walls2d/`, F-12); raiz do componente e medida pela folha (contrato em `_reversa_sdd/selection/`, RN-07, RN-22, RN-23); o encaixe e o snap genéricos do `PlacementMixin` (contrato em `_reversa_sdd/hb_placement/`).

## Regras de Negócio

| ID | Regra confirmada | Fonte |
|---|---|---|
| RN-01 | 🟢 A medida da porta é a da **folha**. Furo = (`2·w + CENTER_GAP` na dupla, senão `w`) `+ 2·SIDE` de largura e `h + TOP` de altura, arredondado a 6 casas; `SIDE = MARCO + GAP = 0,049`, `TOP = 0,059`, `CENTER_GAP = 0,003`. 80 × 210 → 0,898 × 2,159; dupla de 2 × 80 → 1,701 × 2,159. `leaf_size` é o inverso exato (dupla: `(furo − 2·SIDE − CENTER_GAP)/2`) | `door_core.py:hole_size/leaf_size` |
| RN-02 | 🟢 Constantes da porta (m): `LEAF_T` 0,040 (folha), `FLOOR_GAP` 0,008 (folga no piso), `MARCO` 0,046, `GAP` 0,003, `HANDLE_Z` 1,02. Ferragens e perfis têm tamanho fixo; só larguras e alturas acompanham a folha. A profundidade do marco é a espessura da parede (`Dim Y`) | `door_core.py` (constantes, `_leaf`, `_frame`) |
| RN-03 | 🟢 Tipos de porta: simples = 1 folha (índice 0) com fechadura e dobradiças no lado `hinge`; dupla = folha 0 em `x0 = 0` com dobradiça à esquerda e fechadura, folha 1 em `x0 = w + CENTER_GAP` com dobradiça à direita, sem fechadura; vão aberto (`OPEN_DOOR`) = só marcos, marco superior e guarnições (sem batentes, vedações, folhas nem ferragens) | `door_core.py:door_parts/_frame` |
| RN-04 | 🟢 Referencial da caixa: x ao longo do furo (0 = borda esquerda), y na espessura (0 a `wall`), z para cima (0 = piso). As peças da porta são geradas centradas em y = 0 e convertidas por `x + SIDE`, `y → wall/2 + y·flip`, com `flip = −1` se `side == 'POS_Y'`, senão `+1`: dobradiças e giro ficam no lado `side` da parede | `door_core.py:door_parts` |
| RN-05 | 🟢 Lado e mão vêm do símbolo 2D (`GeoNodeDoorSwing`, primeiro filho com `IS_2D_ANNOTATION`): `Is Left` verdadeiro → dobradiça à **direita** (`hinge='RIGHT'`, medido no Blender 5.2: põe a dobradiça em x = largura); `Swing Inside` verdadeiro **ou ausente** → `side='NEG_Y'` e `swing_sign='OUT'`, senão `POS_Y`/`IN`. Leitura que falha → `(símbolo, True, True, False)` | `sync.py:_swing/_parts/sync` |
| RN-06 | 🟢 Tipo da caixa (`kind_of`): `IS_WINDOW_BP` → `WINDOW`; senão `btm_opening_real.kind` se ≠ `NONE` (o gravado vence o símbolo); senão sem símbolo → `OPEN_DOOR`; com símbolo `Is Double` → `DOUBLE_DOOR`, senão `DOOR` | `sync.py:kind_of` |
| RN-07 | 🟢 Janela de correr (m): marco `PROFILE` 0,040 com a profundidade da parede; dois trilhos (inferior e superior, 8 mm de altura, 3 mm de espessura) em y = `wall/2 ∓ 0,020`; 2 folhas de largura `(w − 2·PROFILE)/2 + OVERLAP/2` (`OVERLAP` 0,050), perfil `SASH` 0,035 × `SASH_DEPTH` 0,030, de `z = PROFILE + 0,005` a `h − PROFILE − 0,005`, folha 0 no trilho y menor encostada à esquerda, folha 1 no outro trilho encostada à direita; vidro `GLASS_T` 0,004 entrando 6 mm no perfil; puxador concha 16 × 6 × 120 mm no montante externo de cada folha; guarnições de 50 × 12 mm só na face y = `wall`; peitoril de granito `SILL_T` 0,020 saindo `SILL_OUT` 0,030 para os lados e para as duas faces, com pingadeira 6 × 4 mm sob a face y = 0 | `window_core.py:window_parts` |
| RN-08 | 🟢 Curso da folha da janela = `inner − (inner/2 + OVERLAP/2)` com `inner = w − 2·PROFILE`, arredondado a 6 casas (1,20 m → 0,535); folha 0 corre para `POS_X`, folha 1 para `NEG_X`, e o curso é gravado em `btm_aggregate.travel` | `window_core.py:travel`; `sync.py:sync` |
| RN-09 | 🟢 Assinatura = `"{kind}\|{DimX:.5f}\|{DimY:.5f}\|{DimZ:.5f}\|{Is Left}\|{Swing Inside}\|v{MODEL_VERSION}"` (booleanos ou `None` como texto). `sync` não refaz quando, sem `force`, a assinatura é igual à gravada e a montagem existe em `bpy.data.objects`. Posição e rotação da caixa **não** entram (a montagem é filha e acompanha) | `sync.py:signature/sync` |
| RN-10 | 🟢 Ao refazer, a abertura (`open_value > 0`) de cada folha e a marca `production_part` são restauradas pelo nome-base (`nome.split(".")[0]`) das folhas da montagem anterior; só objetos que voltam como grupo `LEAF` recebem `production_part` | `sync.py:_remember/sync` |
| RN-11 | 🟢 Hierarquia montada: caixa → grupo `FRAME` (Empty, "`<caixa>` - montagem") com as malhas Marco e Ferragens do marco → por folha, pivô (Empty criado por `leaf.make_leaf`) → grupo `LEAF` ("`<caixa>` - folha N") com a malha Folha N → malha Ferragens da folha N filha da **malha da folha**. Os Empties são girados para os eixos da caixa sem mover as malhas; as malhas do marco recebem `btm_opening_frame` = nome do grupo `FRAME` (a folha não colide com o próprio marco) | `sync.py:sync/_align/_parent_keep`; `aggregates/collision.py:OPENING_FRAME_PROP` |
| RN-12 | 🟢 Folhas da porta: `leaf.make_leaf(sash, frame, 'SWING', hinge, swing_sign, max_angle=90.0)`; `hinge` = `RIGHT` se `Is Left` (porta simples), `LEFT` para a folha 0 e `RIGHT` para a folha 1 (dupla) | `sync.py:SWING_MAX/sync` |
| RN-13 | 🟢 A caixa continua sendo o furo da parede; após montar ela vira arame (`display_type='WIRE'`, `show_in_front=False`) e fica oculta (`hide_set`) quando `scene.home_builder.show_entry_door_and_window_cages` é falso; filhos `FONT` ou com "Text" no nome são ocultos na viewport; o símbolo 2D permanece | `sync.py:_style_cage`; `hb_props.py:update_show_entry_door_and_window_cages` |
| RN-14 | 🟢 Agrupamento das peças em malhas: `FRAME` e `FRAME_HW` sem índice de folha; peça `LEAF`, ou de material `ALU`/`GLASS`, vai para a malha da folha; o resto (`LEAF_HW` de metal/latão/fenda) vai para "Ferragens da folha N". Resultado: porta simples 4 malhas, dupla 6, vão aberto 1, janela 3 (Marco, Folha 1, Folha 2) | `build.py:group_key/group_name` |
| RN-15 | 🟢 Materiais por chave, reaproveitados pela marca `btm_opening_material` = chave: `WOOD` "Nogueira verniz acetinado", `METAL` "Aço inox escovado", `RUBBER` "Borracha EPDM", `SLOT` "Cavidades das ferragens", `BRASS` "Latão", `ALU` "Alumínio anodizado", `GLASS` "Vidro" (`BLENDED`, alpha 0,25 no `diffuse_color`, IOR 1,52, transmissão 1), `STONE` "Granito cinza"; `WOOD` usa as texturas do pacote (cor e rugosidade) quando os arquivos existem | `materials.py:SPECS/get/_wood_textures` |
| RN-16 | 🟢 "Atualizar portas e janelas" refaz, com `force=True`, só as caixas desatualizadas (`model_version < MODEL_VERSION` ou sem montagem); nunca roda sozinho, a barra lateral só avisa com a contagem | `ops.py:BTM_OT_OpeningsUpdate`; `sync.py:outdated`; `ui/sidebar_build.py:draw` |
| RN-17 | 🟢 Tecla I: com o ativo **selecionado** dentro de uma porta (primeiro ancestral, inclusive, com `IS_ENTRY_DOOR_BP`) que tem símbolo, inverte `Is Left` e refaz a porta; mantém o lado da parede para onde ela abre. Sem porta com símbolo o `poll` falha e o I segue o padrão do Blender | `ops.py:door_of/BTM_OT_DoorInvertHand` |
| RN-18 | 🟢 Encaixe na região: cantos em qualquer ordem são ordenados; `z0` em (−5 mm, 0) vira 0; largura ou altura < `MIN_SIZE` 1 mm → `EMPTY`; `x0 < −TOLERANCE`, `x1 > comprimento + TOLERANCE` ou `z0 < 0` → `OUTSIDE`; `z1 > altura + TOLERANCE` → `TOO_TALL` (`TOLERANCE` 5 mm); porta (qualquer tipo ≠ `WINDOW`) tem `sill = 0` e vai do piso até `z1`; janela usa `sill = z0`; interseção estrita com folga de 1 mm em X e em Z (de `sill` a `z1`) com outra abertura → `OVERLAP`. Aceito → `Fit(True, x0, x1 − x0, z1 − sill, sill, '')`, sem grade nem folga | `region_core.py:fit` |
| RN-19 | 🟢 Marcar região: o primeiro clique só vale sobre um objeto cuja cadeia de pais chega a `IS_WALL_BP`; a face é `BACK` se o ponto atingido tem y local > espessura/2, senão `FRONT`; os cantos são o mouse projetado no plano da face, na grade (`hb_snap.snap_value_to_grid`: 10 mm métrico, 1 polegada imperial; Shift: 1 mm / 1/16") e presos a `[0, Length] × [0, Height]` | `region.py:BTM_OT_WallRegion._wall_hit/_local/modal`; `hb_snap.py:snap_value_to_grid` |
| RN-20 | 🟢 A região é estado de sessão em `WindowManager.btm_wall_region`, guarda o **nome** da parede, e é descartada por: novo `caffmob.wall_region` (já no `invoke`), `caffmob.wall_region_clear`, abrir arquivo (`load_post`), confirmar uma porta/janela na região, ou a parede deixar de existir/perder `IS_WALL_BP` (na próxima leitura por `region_wall`). Cancelar a inserção na região mantém a região | `region_props.py:region_wall/clear`; `region.py`; `operators/doors_windows.py:modal_in_region` |

## Requisitos Funcionais

🟡 Prioridades inferidas das features 010 (`_reversa_forward/010-porta-real-textura-linha/requirements.md` RF-01 a RF-07, RF-13; `roadmap.md` D-07 a D-16) e 011 (`_reversa_forward/011-selecao-por-componente/requirements.md` RF-09, RF-10; `roadmap.md` D-10 a D-12) e do commit `640b2c2` (tecla I); não constituem roadmap aprovado.

| ID | Requisito | Prioridade | Critério de aceite |
|---|---|---|---|
| RF-01 | 🟢 Gerar a porta paramétrica (simples, dupla, vão aberto) pela medida da folha e pela espessura da parede | Must | CA-01, CA-02 |
| RF-02 | 🟢 Converter furo ↔ folha para a inserção, o diálogo e a seleção | Must | CA-01 |
| RF-03 | 🟢 Gerar a janela de correr e o curso das folhas | Must | CA-03 |
| RF-04 | 🟢 Montar a porta/janela real na caixa em poucas malhas, com materiais compartilhados | Must | CA-04, CA-05 |
| RF-05 | 🟢 Refazer só quando a assinatura muda, preservando abertura e produção | Must | CA-06, CA-07 |
| RF-06 | 🟢 Folhas que abrem: giro de 90° na porta, correr até o batente na janela | Must | CA-04 |
| RF-07 | 🟢 Caixa como referência em arame, sem o texto "DOOR"/"WINDOW" | Must | CA-04 |
| RF-08 | 🟢 Atualizar portas e janelas de arquivos antigos, sob comando | Should | CA-08 |
| RF-09 | 🟢 Inverter a mão da porta pela tecla I | Should | CA-09, CA-10 |
| RF-10 | 🟢 Marcar, mostrar e limpar uma região na parede | Must | CA-11, CA-12 |
| RF-11 | 🟢 Encaixar porta/janela na região com medidas exatas ou recusar com motivo | Must | CA-13, CA-14 |

## Requisitos Não Funcionais

| Tipo | Requisito observado | Evidência | Confiança |
|---|---|---|---|
| Testabilidade | `door_core.py`, `window_core.py` e `region_core.py` não importam `bpy` (só `dataclasses`, `collections`, `data.i18n.N_`) e rodam fora do Blender | docstrings; `tests/test_door_core.py`, `test_window_core.py`, `test_wall_region_core.py` | 🟢 |
| Desempenho | Uma porta simples vira 4 malhas + 3 Empties (FRAME, pivô, LEAF) no lugar das 157 peças do gerador original (D-08); a assinatura evita refazer em `check()` de diálogo e no OK do Editor de Paredes. `materials.get` percorre `bpy.data.materials` a cada chamada. Nenhuma meta de tempo medida | `build.py` docstring; `sync.py:sync`; `materials.py:get` | 🟢 (mecanismo) / 🟡 (meta) decisão: medir/testar (DT-06; questions.md#pergunta-78): medir uma vez com 30 portas; abaixo de 1 s no total, não definir meta |
| Robustez | Leitura do símbolo que falha usa padrões; `clear` só remove objetos ainda em `bpy.data.objects` e malhas sem usuários; o consumidor `_sync_opening` engole exceções e imprime "CAFFMob Draw: porta/janela real não montada (…)" mantendo caixa e furo; parede apagada descarta a região sem erro; remoção de keymap engole `ReferenceError`/`RuntimeError` | `sync.py:_swing/clear`; `operators/doors_windows.py:_sync_opening`; `region_props.py:region_wall`; `ops.py`/`region.py:unregister` | 🟢 |
| Ciclo de vida | `register`/`unregister` simétricos: classes, `Object.btm_opening_real`, `WindowManager.btm_wall_region`, `draw_handler_add`/`remove` do desenho da região, `load_post` `@persistent`, itens de keymap; `unregister` em ordem inversa | `__init__.py`, `props.py`, `region_props.py`, `region.py`, `ops.py` | 🟢 |
| Internacionalização | Mensagens com `tr` e motivos com `N_`; 25 chaves em `data/translations/openings.json` (`pt_BR`/`en_US`), cobrindo todas as 11 strings de `tr`/`N_` da unit. Nomes de malhas, materiais e grupos ("Marco", "Folha N", "Nogueira…") e `bl_label` não passam por `tr` | `ops.py`, `region.py`, `region_core.py`, `build.py`, `materials.py` | 🟢 |
| Undo | `caffmob.openings_update` e `btm.door_invert_hand` têm `{'REGISTER', 'UNDO'}`; `caffmob.wall_region` e `caffmob.wall_region_clear` têm só `{'REGISTER'}` (região é estado de sessão, fora do undo) | `ops.py`; `region.py` | 🟢 |
| Persistência | `btm_opening_real` é salvo no `.blend` na caixa; `btm_wall_region` vive no `WindowManager` e é zerada no `load_post` | `props.py`; `region_props.py`; `region.py:on_load_post` | 🟢 |
| Licença dos ativos | Texturas `assets/nogueira_cor.jpg` e `nogueira_rugosidade.jpg` vêm da porta realista do projeto (modelo original) | `materials.py` docstring; `door_core.py` docstring | 🟢 _(Revisão 2026-10-10: tools/build_openings_assets.py:6-8: os JPG são convertidos dos PNG gerados por `docs/porta_realista_080x210/gerar_porta.py`, modelo original do projeto; a licença formal não está escrita no repositório)_ |

## Critérios de Aceitação

🟢 CA-01 a CA-03 e CA-13/CA-14 têm o cálculo coberto por testes puros (`tests/test_door_core.py` 9, `test_window_core.py` 5, `test_wall_region_core.py` 7: **21 testes aprovados** em 2026-10-10) ou verificado nesta extração com o mesmo núcleo. CA-04 a CA-12 dependem do Blender (`tests/blender_010_openings_smoke.py`, `blender_011_region_smoke.py`, `blender_bug_YIMY_openings.py`, `blender_bug_porta_real_abre.py`, `blender_toast_resize_invert.py`; não executados nesta extração).

```gherkin
CA-01 — Furo pela folha (feliz)
Dado uma porta de folha 0,80 × 2,10 m
Quando chamo hole_size(0.8, 2.1) e hole_size(0.8, 2.1, double=True)
Então devolve (0.898, 2.159) e (1.701, 2.159)
E leaf_size(0.898, 2.159) = (0.8, 2.1); leaf_size(1.701, 2.159, double=True) = (0.8, 2.1)

CA-02 — Peças da porta
Dado folha 0,80 × 2,10 numa parede de 0,15
Quando chamo door_parts com hinge LEFT/RIGHT, side NEG_Y/POS_Y, double e open_door
Então a simples tem 143 peças (21 FRAME, 43 FRAME_HW, 24 LEAF, 55 LEAF_HW); a dupla 256 com folhas 0 e 1; o vão aberto 15 peças só FRAME
E a folha tem 40 mm de espessura a 8 mm do piso; o marco tem a espessura da parede; trocar o lado espelha as dobradiças em y
E uma folha de 1,00 m mantém maçaneta e dobradiças do mesmo tamanho que a de 0,80 (falha se distorcer)

CA-03 — Janela
Dado um furo de 1,20 × 1,00 numa parede de 0,15
Quando chamo window_parts e travel(1.2)
Então há 25 peças: marco de 40 mm com a profundidade da parede, trilhos em y = 0,055 e 0,095, 2 folhas com vidro sobrepostas 50 mm, 2 puxadores, guarnições na face y = 0,15 e peitoril saindo 30 mm
E travel = 0,535

CA-04 — Montar a porta real (feliz)
Dado uma caixa IS_ENTRY_DOOR_BP com Dim X 0,898, Dim Y 0,15, Dim Z 2,159 e símbolo Is Left falso, Swing Inside verdadeiro
Quando chamo sync.sync(context, caixa)
Então devolve True; a caixa tem filho "Door - montagem" (FRAME) com as malhas "Door Marco" e "Door Ferragens do marco" e o grupo LEAF "Door - folha 1"
E a folha é LEAF SWING com hinge LEFT, swing_sign OUT, max_angle 90; as malhas do marco têm btm_opening_frame = nome do FRAME
E btm_opening_real tem kind DOOR, assembly = FRAME, model_version 1 e a assinatura; a caixa está em WIRE e o texto "DOOR" oculto

CA-05 — Janela montada
Dado uma caixa IS_WINDOW_BP de 1,20 × 0,15 × 1,00
Quando chamo sync.sync
Então há as malhas Marco, Folha 1 e Folha 2 (puxador e vidro dentro da folha), a folha 0 é SLIDE POS_X e a 1 SLIDE NEG_X, as duas com travel 0,535

CA-06 — Sem mudança não refaz (falha proposital)
Dado a porta do CA-04 já montada
Quando chamo sync.sync de novo sem mudar medidas, símbolo nem versão
Então devolve False e os objetos da montagem são os mesmos
E com force=True a montagem é apagada e refeita

CA-07 — Refazer preserva estado
Dado a porta do CA-04 com a folha aberta a 0,5 e marcada como peça de produção
Quando Dim X muda para 0,998 e chamo sync.sync
Então a folha nova tem 0,90 m de largura, open_value 0,5 e production_part verdadeiro
E a malha e o grupo antigos não existem mais em bpy.data

CA-08 — Atualizar portas e janelas
Dado um arquivo com 3 caixas de porta sem montagem (kind NONE)
Quando a barra lateral é desenhada e o usuário executa caffmob.openings_update
Então o aviso mostra "3 porta(s) ou janela(s) em caixa"; após o operador as 3 têm a porta real nas mesmas posições e o relatório diz "3 porta(s) e janela(s) atualizada(s)"
E num arquivo sem caixas desatualizadas o relatório diz "Todas as portas e janelas já estão atualizadas"

CA-09 — Tecla I (feliz)
Dado a maçaneta de uma porta real selecionada e ativa
Quando aperto I no modo objeto
Então Is Left do símbolo é invertido, a dobradiça muda de lado (hinge RIGHT), o lado de abertura (Swing Inside) é mantido e aparece "Giro da porta invertido"
E se o ativo foi apagado pela remontagem, uma malha da montagem nova (ou a caixa) fica selecionada e ativa

CA-10 — Tecla I sem porta (falha)
Dado um balcão, um vão aberto (sem símbolo) ou uma porta com ativo não selecionado
Quando aperto I
Então btm.door_invert_hand não passa no poll e o I segue o padrão do Blender

CA-11 — Marcar região (feliz)
Dado uma parede de 4,00 × 2,70 × 0,15 e o modo objeto
Quando executo caffmob.wall_region, clico na face frontal em (1,004; 0,3) e no canto oposto em (1,826; 2,118)
Então btm_wall_region fica active, wall = nome da parede, side FRONT, x0 1,00, x1 1,83, z0 0,30, z1 2,12 (grade de 10 mm), e aparece "Região marcada: L × A. Escolha a porta ou a janela" com 0,83 e 1,82 m formatados por units.unit_to_string (unidade do BlenderToMob, vírgula decimal)
E com Shift pressionado os cantos andam de 1 mm; clicar além da ponta prende o canto em Length

CA-12 — Marcar região cancelado ou limpo (falha)
Dado o modal de marcação ativo
Quando aperto Esc ou o botão direito, ou clico fora de qualquer parede no primeiro canto
Então Esc/botão direito cancela sem região; o clique fora não faz nada e o modal continua
E com uma região marcada, Esc na vista 3D (caffmob.wall_region_clear) ou "Limpar região" põe active = False; abrir outro arquivo também

CA-13 — Encaixe na região (feliz)
Dado uma parede de 4,00 × 2,70
Quando chamo fit(1.0, 1.82, 0.3, 2.12, 4, 2.7, 'DOOR') e fit(1, 2.2, 1.1, 2.1, 4, 2.7, 'WINDOW')
Então a porta vai do piso: x 1,0, largura 0,82, altura 2,12, peitoril 0
E a janela tem largura 1,20, altura 1,00, peitoril 1,10

CA-14 — Encaixe recusado (falha)
Dado a mesma parede
Quando a região é um clique só, passa 6 mm da ponta, tem z0 = −6 mm, sobe além de 2,705 ou cruza outra abertura com mais de 1 mm
Então fit devolve ok False com EMPTY, OUTSIDE, OUTSIDE, TOO_TALL ou OVERLAP e o consumidor avisa "<motivo>: a inserção segue presa ao cursor"
E uma vizinha que só encosta (borda com borda) ou fica acima da janela não bloqueia
```

## Prioridade (MoSCoW)

| Requisitos | Classificação | Justificativa |
|---|---|---|
| RF-01 a RF-07 | 🟡 Must | 010 RF-01 a RF-05 e RF-13 são Must: porta e janela têm de parecer reais sem perder o corte |
| RF-10, RF-11 | 🟡 Must | 011 RF-09 e RF-10 são Must |
| RF-08 | 🟡 Should | 010 RF-06 (compatibilidade com arquivos antigos) é Should |
| RF-09 | 🟡 Should | Atalho de conveniência (commit `640b2c2`); os botões "Flip Door Hand"/"Flip Door Swing" de `doors_windows` fazem o mesmo |
| Abertura seguir o lado da face marcada (011 RN-11) | 🟡 Won't (nesta versão) | `place_in_region` ignora `region.side` (EC-07) |
| Alternar porta simples ↔ dupla refazendo a porta real | 🟡 Won't (nesta versão) | `kind_of` prefere o `kind` gravado e `toggle_double_door` não chama `sync` (EC-04) |

## Rastreabilidade de Código e Verificação

| Arquivo | Símbolos / responsabilidade | Evidência |
|---|---|---|
| caffmob_draw/openings/door_core.py | `FRAME`, `FRAME_HW`, `LEAF`, `LEAF_HW`, `WOOD`, `METAL`, `RUBBER`, `SLOT`, `BRASS`, `LEAF_T`, `FLOOR_GAP`, `MARCO`, `GAP`, `SIDE`, `TOP`, `CENTER_GAP`, `HANDLE_Z`, `Part`, `hole_size`, `leaf_size`, `_Builder`, `_leaf`, `_frame`, `door_parts` | 🟢 Código; `tests/test_door_core.py` |
| caffmob_draw/openings/window_core.py | `ALU`, `GLASS`, `STONE`, `PROFILE`, `SASH`, `SASH_DEPTH`, `GLASS_T`, `OVERLAP`, `SILL_T`, `SILL_OUT`, `_box`, `travel`, `window_parts` | 🟢 Código; `tests/test_window_core.py` |
| caffmob_draw/openings/region_core.py | `Fit`, `EMPTY`, `OUTSIDE`, `TOO_TALL`, `OVERLAP`, `MIN_SIZE`, `TOLERANCE`, `REASONS`, `_refuse`, `fit` | 🟢 Código; `tests/test_wall_region_core.py` |
| caffmob_draw/openings/materials.py | `TAG`, `ASSETS`, `SPECS`, `_image`, `_wood_textures`, `get` | 🟢 Código |
| caffmob_draw/openings/build.py | `BEVEL`, `_AXIS`, `group_key`, `group_name`, `_add_part`, `build` | 🟢 Código |
| caffmob_draw/openings/sync.py | `DOOR_FLAG`, `WINDOW_FLAG`, `SWING_MAX`, `is_opening`, `_swing`, `kind_of`, `_dims`, `signature`, `_parts`, `_remember`, `clear`, `_to_world`, `_parent_keep`, `_align`, `_style_cage`, `sync`, `openings`, `outdated` | 🟢 Código; `tests/blender_010_openings_smoke.py`, `blender_bug_YIMY_openings.py` (não executados) |
| caffmob_draw/openings/props.py | `KIND_ITEMS`, `MODEL_VERSION`, `BTM_PG_Opening`, `Object.btm_opening_real` | 🟢 Código |
| caffmob_draw/openings/ops.py | `BTM_OT_OpeningsUpdate` (`caffmob.openings_update`), `door_of`, `BTM_OT_DoorInvertHand` (`btm.door_invert_hand`), keymap I | 🟢 Código; `tests/blender_toast_resize_invert.py` (não executado) |
| caffmob_draw/openings/region_props.py | `SIDE_ITEMS`, `BTM_PG_WallRegion`, `WindowManager.btm_wall_region`, `region_wall`, `clear` | 🟢 Código |
| caffmob_draw/openings/region.py | `_draw_handle`, `_addon_keymaps`, `_live`, `FILL`, `LINE`, `TEXT`, `_face_y`, `_rect_world`, `_draw_rect`, `draw_regions`, `_tag_redraw`, `BTM_OT_WallRegion` (`caffmob.wall_region`), `BTM_OT_WallRegionClear` (`caffmob.wall_region_clear`), `on_load_post`, `register`, `unregister` | 🟢 Código; `tests/blender_011_region_smoke.py` (não executado) |
| caffmob_draw/openings/__init__.py | `_modules` (`props`, `ops`, `ui.view_mode`, `region_props`, `region`), `register`, `unregister` | 🟢 Código |
| caffmob_draw/openings/assets/ | `nogueira_cor.jpg`, `nogueira_rugosidade.jpg` (usados); `previa_porta.png`, `previa_janela.png` (não referenciados pela unit) | 🟢 Arquivos; 🟢 prévias geradas por `tools/render_openings_preview.py` e não lidas por nenhum código do pacote _(Revisão 2026-10-10: grep `previa_` em caffmob_draw/, tests/ e build.py: nenhum uso; _reversa_forward/010…/roadmap.md:98)_ |

🟢 Executado em 2026-10-10: `cd tests && python3 -m unittest test_door_core test_window_core test_wall_region_core` → **21 testes aprovados** (9 + 5 + 7). Não cobrem `materials.py`, `build.py`, `sync.py`, `ops.py`, `region.py` nem `region_props.py`.

## Lacunas e Pré-condições

- 🟢 **Decisão do titular (2026-10-10, questions.md#pergunta-22):** a abertura inserida em região com `side = BACK` abre para o lado dessa face (gravar `Swing Inside` = falso no símbolo ou girar 180° ao inserir), atendendo 011 RN-11 sem mexer no corte. 🟢 (código) hoje `doors_windows.place_in_region` põe a caixa sempre em `y = 0` com rotação zero (EC-07). Pendência de implementação: DT-01.
- 🟢 **Decisão do titular (2026-10-10, questions.md#pergunta-23):** `_swing` filtra por `has_input('Swing Inside')` (ou pelo nome 'Door Swing'), como `room_door_leaf.swing_of`. 🟢 (código) hoje pega o **primeiro** filho com `IS_2D_ANNOTATION` e uma cota antes do símbolo é lida como símbolo (EC-02). Pendência de implementação: DT-02.
- 🟢 **Decisão do titular (2026-10-10, questions.md#pergunta-24):** `toggle_double_door` atualiza `btm_opening_real.kind` e chama `_sync_opening`; a assinatura inclui o kind efetivo. 🟢 (código) hoje não refaz a porta real e `kind_of` manteria o `kind` gravado (EC-04). Pendência de implementação: DT-03.
- 🟢 **Decisão do titular (2026-10-10, questions.md#pergunta-25):** tirar a invalidação do desenho: em `draw_regions` só ignorar a região inválida; zerar `active` em `region_wall` chamado por operadores ou num `depsgraph_update_post`. 🟢 (código) hoje `region_wall` grava `region.active = False` dentro do desenho `POST_PIXEL` (EC-10). Pendência de implementação: DT-04.
- 🟡 Sem meta de desempenho para `sync` (montagem com `bmesh` e várias `view_layer.update()`) — decisão: medir/testar (DT-06; questions.md#pergunta-78).
- 🟢 Pré-condição: `hb_types.GeoNodeObject/GeoNodeCage/GeoNodeWall` (`get_input`/`set_input`), `hb_placement.PlacementMixin` (`init_placement`, `update_snap`, `mouse_pos`, `region`), `hb_placement.draw_header_text/clear_header_text`, `hb_snap.snap_value_to_grid`, `units.unit_to_string`, `data/i18n` (`tr`, `N_`), `aggregates/group.create_group`, `aggregates/leaf.make_leaf`, `aggregates/apply._write`, `aggregates/collision.OPENING_FRAME_PROP`, `inspection/room_door_leaf.remove_leaves`, `PropertyGroup` `btm_aggregate` e `scene.home_builder.show_entry_door_and_window_cages`, com os contratos citados em `design.md` › Dependências.
