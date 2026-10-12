# Inspeção de frentes (inspection) — Requisitos

🟢 **CONFIRMADO** — contrato extraído de `caffmob_draw/inspection/` (12 arquivos + 6 adaptadores em `adapters/`) em 2026-10-10; a pasta não tem alterações sem commit. Confirmação de código não implica validação visual no Blender. 🟡 identifica prioridade ou intenção inferida; 🔴 identifica lacuna de validação. Origem dos requisitos de produto: `_reversa_forward/001-addon-moveis-planejados/requirements.md` (RF-090, RF-091, RN-14 da 001).

## Visão Geral

🟢 A unit abre e fecha portas, basculantes, gavetas e pullouts de **todas** as linhas de produto (frameless, face frame, closets, módulo rápido `btm_cabinet`, portas de ambiente do Home Builder 5 e folhas convertidas da feature 003) com um valor de abertura comum, sem recalcular o módulo durante a pose. Oferece: abrir/fechar em massa por escopo, modo de inspeção por clique com animação, controle giratório/seta no 3D (gizmo), salvar o arquivo com as frentes fechadas sem mudar a vista e verificação sob demanda da interferência do envelope de abertura com outros objetos, com destaque no viewport. Fontes: `__init__.py` (docstring), `fronts.py`, `ops_inspect.py`, `gizmo.py`, `save_guard.py`, `interference.py`, `ops_interference.py`, `overlay.py`.

🟢 Abrir frentes é **inspeção** (RN-14 da 001): os operadores não entram no histórico de desfazer e a abertura não marca o plano de corte como desatualizado (`ops_inspect.py` docstring; `cutting/stale.py:depsgraph_update_post`).

## Responsabilidades

- 🟢 Definir o contrato `Front` (get/apply/commit/hinge_frame/objects/can_sweep/is_valid) e descobrir frentes por adaptador de linha (`fronts.py`; `adapters/*.py`; ADR `_reversa_sdd/adrs/0005-adaptadores-por-biblioteca.md`).
- 🟢 Matemática pura das poses: limites, encaixe, conversões graus↔fração, rotação em aresta, deslizamento (`pivot_math.py`) e folhas da porta de ambiente (`room_door_math.py`).
- 🟢 Criar/atualizar a folha 3D cinza da porta de ambiente na primeira abertura (`room_door_leaf.py`).
- 🟢 Operadores `caffmob.fronts_set_open`, `caffmob.inspect_fronts` (modal), `caffmob.check_front_interference`, `caffmob.interference_goto` (`ops_inspect.py`, `ops_interference.py`).
- 🟢 Gizmo `BTM_GGT_front_open` (`gizmo.py`), handlers de desenho (`overlay.py`) e handlers de salvar (`save_guard.py`).
- 🟢 Estado de sessão `WindowManager.btm_inspection` (`props.py`).
- 🟢 **Não** pertence a esta unit: o painel/HUD que expõe os botões (`ui/panels.py:draw_inspection_box`, `ui/object_properties.py:_draw_open`, `ui/context_menu.py`, `operators/viewport_hud.py:_InspectButton`), a opção `Scene.btm_settings.save_fronts_open` (`data/properties.py`), o recálculo das linhas legadas e a parada na batida das folhas convertidas (`_reversa_sdd/aggregates/`), nem a colisão de corpo (`_reversa_sdd/collision/`).

## Regras de Negócio

| ID | Regra confirmada | Fonte |
|---|---|---|
| RN-01 | 🟢 Unidade do valor de abertura: articuladas (`DOOR`, `FLIP_UP`, `FLIP_DOWN`) em **graus** em [0, `MAX_ANGLE`=90]; `DRAWER`/`PULLOUT` em **fração** do curso em [0, 1]. Folhas convertidas (`AggregateLeafFront`) usam o próprio `btm_aggregate.max_angle` como teto. | `pivot_math.py:clamp_angle/clamp_fraction`; `fronts.py:Front.clamp/max_value`; `adapters/aggregate_leaf.py:clamp/max_value` |
| RN-02 | 🟢 Frente está "aberta" quando `get() > 0,5` (graus) para articuladas ou `> 0,005` (fração) para gavetas; abaixo disso conta como fechada. | `fronts.py:Front.is_open` |
| RN-03 | 🟢 Valor de "aberta" (`open_value(graus)`): o ângulo pedido limitado para articuladas; **sempre 1,0** para gavetas. | `fronts.py:Front.open_value` |
| RN-04 | 🟢 Abrir/fechar em massa: `CLOSE`→0; `OPEN_45`→45° (gaveta 0,5); `OPEN_90`→90° (gaveta 1,0). Articuladas usam `open_value(graus)`; gavetas usam `graus/90`. O valor é gravado com `commit`. | `ops_inspect.py:BTM_OT_FrontsSetOpen.execute` |
| RN-05 | 🟢 Escopos: `ALL` = todas as frentes da **cena atual**; `ACTIVE_MODULE` = frentes do módulo do objeto ativo (vazio sem ativo ou sem módulo); `SELECTED` = todas as frentes dos módulos que contêm objetos selecionados **mais** as frentes donas de cada selecionado, deduplicadas por `key`. | `ops_inspect.py:scope_fronts` |
| RN-06 | 🟢 Clique no modo de inspeção alterna: aberta → 0; fechada → `open_value(default_angle)` (90 ou 45; gaveta 1,0). Clique durante a animação inverte o alvo a partir da pose interpolada atual. | `ops_inspect.py:BTM_OT_InspectFronts._toggle` |
| RN-07 | 🟢 Animação: duração 0,35 s, curva smoothstep `t²(3−2t)`, timer de 60 Hz; durante a animação só `apply` (pose); ao terminar, `commit` do alvo. | `ops_inspect.py:ANIM_DURATION/TIMER_HZ/_smoothstep/_step` |
| RN-08 | 🟢 Saída do modo (Esc, botão direito, `cancel`, segunda invocação do operador) **conclui** as animações pendentes com `commit` do alvo; não volta ao estado anterior à animação. | `ops_inspect.py:_finish/modal/invoke` |
| RN-09 | 🟢 Gizmo: dial (`GIZMO_GT_dial_3d`) no eixo da dobradiça para articuladas; seta (`GIZMO_GT_arrow_3d`) no sentido do curso para gavetas. Arrastar só aplica pose; com `snap_stops` ligado o valor encaixa em 0°/45°/90° quando a até 5°; senão é limitado a [0, 90]. Ao soltar, o valor é gravado num timer fora do desenho do gizmo. | `gizmo.py`; `pivot_math.py:snap_angle` |
| RN-10 | 🟢 Salvar fechado: em `save_pre`, as frentes abertas de todas as cenas sem `btm_settings.save_fronts_open` são fechadas (`commit(0)`) e lembradas por (cena, `key`, valor); em `save_post` **e** `save_post_fail` são reabertas com `commit(valor)`. | `save_guard.py` |
| RN-11 | 🟢 Envelope de abertura: articuladas amostradas de 0 até `max_value` a cada 15° (último ponto = máximo); gavetas em 0 e 1. Cada par de poses consecutivas vira um casco convexo dos cantos das caixas, encolhido radialmente 1 mm. A pose original é restaurada no fim só com `apply`. | `interference.py:_samples/envelope_hulls/_shrink` |
| RN-12 | 🟢 Alvos da interferência: objetos `MESH`/`CURVE` da cena, visíveis, sem `display_type` `WIRE`/`BOUNDS`, sem `IS_2D_ANNOTATION`, fora do **próprio módulo** da frente e fora dos objetos da própria frente. | `interference.py:_Targets.__init__/check_fronts` |
| RN-13 | 🟢 Ausência de aviso só vale para as frentes efetivamente verificadas: o relatório informa a contagem (`checked_fronts`), que conta apenas frentes válidas, varríveis e com envelope (≥ 2 poses com cantos). | `interference.py:check_fronts`; `ops_interference.py:execute` |
| RN-14 | 🟢 Conversão por linha legada (teto físico): face frame 100° (`swing_percent` = graus/100), closets 110° (`hb_door_open` = graus/110), módulo rápido 90° (`_Controller.location.y` = fração × 0,2 m). | `pivot_math.py:*_MAX_ANGLE`; `adapters/face_frame.py`, `closets.py`, `btm.py` |
| RN-15 | 🟢 Porta de ambiente sem folha conta como fechada; a folha (pivô + malha) só é criada quando a porta abre (> 0); a verificação de interferência não cria folha (`can_sweep` falso). Porta com porta real da feature 010 (`btm_opening_real.assembly`) deixa de ser porta de ambiente (o adaptador `aggregate_leaf` assume). | `adapters/room_doors.py`; `room_door_leaf.py:is_room_door/has_real_door` |
| RN-16 | 🟢 Frameless: só abrem peças `MESH` com tag de frente (`IS_FLIP_UP_DOOR`, `IS_DOOR_FRONT`, `IS_PULLOUT_FRONT`, `IS_DRAWER_FRONT`), modificador `GeoNodeCutpart`, não ocultas (`hide_viewport`), sem `False Front` e dentro de `IS_FRAMELESS_CABINET_CAGE`. Pose em `delta_rotation_euler`/`delta_location`; valor em idprop `btm_open`, apagada ao fechar. | `adapters/frameless.py:_openable/apply/commit` |
| RN-17 | 🟢 Raiz de módulo (`module_root_of`): primeiro ancestral (incluindo o próprio) com `IS_FRAMELESS_CABINET_CAGE`, `IS_FACE_FRAME_CABINET_CAGE`, `IS_CLOSET_STARTER_CAGE`, `IS_ENTRY_DOOR_BP` ou `btm_plane.object_kind == 'MODULE'`. | `fronts.py:module_root_of` |
| RN-18 | 🟢 Folha da porta de ambiente: `Swing Inside` põe a dobradiça em y = `Dim Y` e abre para −Y; sem ele, y = 0 e abre para +Y. Simples: `Is Left` põe a dobradiça em x = largura. Dupla: duas folhas de meia largura com dobradiças em x = 0 e x = largura. Espessura da folha fechada do lado oposto ao giro. | `room_door_math.py:leaves` |

## Requisitos Funcionais

🟡 Prioridades inferidas da 001 (RF-090 Must, RF-091 Should) e do uso pelos painéis; não constituem roadmap aprovado.

| ID | Requisito | Prioridade | Critério de aceite |
|---|---|---|---|
| RF-01 | 🟢 Descobrir as frentes inspecionáveis de 6 adaptadores e resolver a frente dona de um objeto (o próprio ou filho, como puxador) | Must | CA-01, CA-02 |
| RF-02 | 🟢 Abrir 90°, abrir 45° e fechar por escopo (`caffmob.fronts_set_open`) | Must | CA-03, CA-04 |
| RF-03 | 🟢 Modo de inspeção por clique com animação (`caffmob.inspect_fronts`) | Must | CA-05, CA-06, CA-07 |
| RF-04 | 🟢 Controle de abertura no 3D com encaixe opcional (`BTM_GGT_front_open`) | Should | CA-08, CA-09 |
| RF-05 | 🟢 Salvar com frentes fechadas sem mudar a vista; opção por cena para salvar abertas | Must | CA-10, CA-11 |
| RF-06 | 🟢 Verificar interferência do envelope de abertura sob demanda (`caffmob.check_front_interference`) | Should | CA-12, CA-13 |
| RF-07 | 🟢 Listar, ir até e destacar interferências no viewport (`caffmob.interference_goto`; overlay) | Should | CA-14, CA-15 |
| RF-08 | 🟢 Folha 3D da porta de ambiente criada/atualizada na abertura | Should | CA-16, CA-17 |
| RF-09 | 🟢 Opções de sessão: ângulo do clique (90/45) e encaixe nas paradas | Could | CA-05, CA-08 |

## Requisitos Não Funcionais

| Tipo | Requisito observado | Evidência | Confiança |
|---|---|---|---|
| Histórico de desfazer | Todos os 4 operadores usam `bl_options = {'REGISTER'}` sem `UNDO` (contraria a regra geral do repositório, por decisão RN-14 da 001) | `ops_inspect.py`, `ops_interference.py` | 🟢 |
| Plano de corte | Abrir não marca `cut_plan_stale`: o handler de stale ignora rodadas com o modo de inspeção ativo, peças de frente e a rodada seguinte a `stale.skip_next_update()` (face frame) | `cutting/stale.py:depsgraph_update_post/_is_front_part`; `adapters/face_frame.py:commit`; `tests/blender_inspection_smoke.py:94` | 🟢 |
| Custo da verificação | Só roda por comando; pré-filtro AABB antes de BVH; BVH e malha avaliada de cada alvo construídos sob demanda e cacheados por ponteiro numa checagem; amostra de vértices para contenção com passo `max(1, n//2000)`; até 32 pontos para o local do choque | `interference.py:_Targets/check_fronts` | 🟢 |
| Fluidez da animação | Timer de 60 Hz e 0,35 s por animação; redesenho só da área corrente | `ops_inspect.py` | 🟢 |
| Testabilidade | `pivot_math.py` e `room_door_math.py` sem `bpy` nem `mathutils`; `__init__._modules` importa tardiamente para os testes não carregarem `bpy` | `__init__.py:_modules`; `tests/test_inspection_math.py`, `tests/test_room_door_math.py` | 🟢 |
| Persistência | Estado da inspeção e resultados ficam no `WindowManager` (sessão) | `props.py` docstring | 🟢 _(Revisão 2026-10-10: sonda no Blender 5.2 em background — `checked_fronts=7`, 1 interferência e `default_angle='45'` voltam a `-1`, 0 e `'90'` depois de salvar e abrir o `.blend`)_ |
| Ciclo de vida | `register`/`unregister` simétricos para classes, `WindowManager.btm_inspection`, 2 draw handlers, 3 handlers de app e o timer do gizmo; exceção: sessão modal ativa não é encerrada no `unregister` (EC-04) | `__init__.py`, `overlay.py`, `save_guard.py`, `gizmo.py`, `ops_inspect.py:unregister` | 🟢 |

## Critérios de Aceitação

🟢 Cenários derivados do código atual e de `tests/blender_inspection_smoke.py`. Valores numéricos de CA-18 executados nos testes puros. _(Revisão 2026-10-10: o smoke foi executado no Blender 5.2.0 LTS e passou (`BLENDER_INSPECTION_SMOKE_OK`), cobrindo CA-01 (sem `room_doors`/`aggregate_leaf`), CA-03, CA-10 e CA-12 com `checked_fronts` = 7; CA-05 a CA-09 e CA-14 a CA-17 continuam sem teste)_

```gherkin
CA-01 — Descoberta em todas as linhas
Dado uma cena com um módulo frameless (porta e gaveta), um face frame, um closets e um btm_cabinet com portas
Quando fronts.iter_fronts(scene) é chamado
Então há ao menos uma Front de DOOR por linha e uma DRAWER frameless, na ordem frameless, face_frame, closets, btm, room_doors, aggregate_leaf

CA-02 — Objeto que não é frente
Dado uma prateleira de um vão de face frame (sem papel de frente nem pivô no caminho até o vão)
Quando fronts.front_for_object(prateleira, scene) é chamado
Então devolve None; e front_for_object(None, scene) também devolve None

CA-03 — Abrir tudo
Dado o projeto do CA-01 com todas as frentes fechadas
Quando caffmob.fronts_set_open(scope='ALL', mode='OPEN_90') executa
Então devolve FINISHED, toda DOOR lê 90, a gaveta frameless lê 1,0, swing_percent do face frame = 0,9, hb_door_open do closets = 90/110, _Controller.location.y = 0,2, e o plano de corte não fica desatualizado

CA-04 — Escopo sem frentes
Dado nada selecionado e scope='SELECTED' (ou objeto ativo fora de qualquer módulo e scope='ACTIVE_MODULE')
Quando caffmob.fronts_set_open executa
Então reporta WARNING "Nenhuma porta, basculante ou gaveta encontrada." e devolve CANCELLED

CA-05 — Clique abre com animação
Dado o modo caffmob.inspect_fronts ativo numa VIEW_3D e default_angle='45'
Quando clico (LEFTMOUSE PRESS) sobre o puxador de uma porta fechada
Então a porta anima 0,35 s até 45° (apply a cada TIMER) e no fim grava 45 com commit; o evento é consumido (RUNNING_MODAL)

CA-06 — Clique fora de frente
Dado o modo de inspeção ativo
Quando clico no vazio, numa parede ou num widget do HUD/pílula do overlay do closets
Então o evento passa adiante (PASS_THROUGH) e nada abre

CA-07 — Saída conclui a animação
Dado uma porta no meio da animação de abertura
Quando aperto Esc (ou botão direito, ou clico de novo no botão do modo)
Então a porta é gravada no alvo (aberta), os timers são removidos, btm_inspection.active = False e o texto de status é limpo; o operador devolve CANCELLED (Esc/direito) ou FINISHED (segunda invocação)

CA-08 — Encaixe do controle giratório
Dado uma porta ativa e selecionada, snap_stops = True
Quando arrasto o dial até 43°
Então a pose vai a 45° (apply) e, ao soltar, um timer grava 45 (commit)

CA-09 — Gizmo sem frente
Dado o objeto ativo não selecionado, ou um objeto que não pertence a nenhuma frente
Quando a viewport redesenha
Então o grupo de gizmos não aparece (poll falso); se hinge_frame falhar com ReferenceError/AttributeError/ValueError, dial e seta ficam ocultos

CA-10 — Salvar fechado, vista aberta
Dado frentes abertas a 90° e save_fronts_open = False
Quando o arquivo é salvo
Então o .blend gravado tem todas as frentes fechadas e, depois do salvamento (ou de falha dele), a tela volta a mostrar as frentes abertas

CA-11 — Salvar aberto por escolha
Dado frentes abertas e Scene.btm_settings.save_fronts_open = True
Quando o arquivo é salvo
Então nenhuma frente daquela cena é fechada nem reaberta

CA-12 — Interferência detectada
Dado um cubo de 0,1 m à frente da porta do módulo "Balcao" (dentro do arco de abertura) e todas as frentes fechadas
Quando caffmob.check_front_interference(scope='ALL') executa
Então btm_inspection.interferences contém (module_name='Balcao', hit_name='Obstaculo'), checked_fronts ≥ 5, todas as frentes voltam a ler 0 e é reportado WARNING "N interferência(s) em M frente(s) verificada(s)."

CA-13 — Nada a verificar
Dado um escopo sem frentes, ou só portas de ambiente sem folha criada
Quando caffmob.check_front_interference executa
Então checked_fronts = 0, a lista fica vazia e é reportado WARNING "Nenhuma frente foi verificada: não há portas ou gavetas no escopo." (o operador devolve FINISHED)

CA-14 — Ir até a interferência
Dado uma interferência registrada no índice 0
Quando caffmob.interference_goto(index=0) executa
Então a seleção vira a frente e o objeto atingido (se existirem e estiverem visíveis), a frente vira o objeto ativo e view_location de toda VIEW_3D da tela vai para o ponto do choque

CA-15 — Índice inválido
Dado 2 interferências registradas
Quando caffmob.interference_goto(index=5) executa
Então devolve CANCELLED sem mudar seleção nem vista

CA-16 — Porta de ambiente abre pela primeira vez
Dado uma porta IS_ENTRY_DOOR_BP com símbolo GeoNodeDoorSwing e sem pivôs
Quando a Front da porta recebe commit(90)
Então são criados, como filhos, um Empty "<porta>_Pivo_<L|R>" (btm_room_door_pivot) e uma malha "<porta>_Folha_<L|R>" (btm_room_door_leaf) filha do pivô; o pivô gira rot_sign·90° em Z e a porta recebe btm_open = 90.0

CA-17 — Porta de ambiente fechada sem folha
Dado a mesma porta sem pivôs
Quando apply(0) é chamado (por fechar tudo ou salvar)
Então nada é criado e get() continua 0

CA-18 — Matemática das poses (puro)
Dado pivot_math e room_door_math
Quando chamo snap_angle(43) / snap_angle(52) / snap_angle(120) e leaves(0.9, 0.15, 2.1, is_left=False, is_double=True, swing_inside=True, 0.035)
Então obtenho 45 / 52 / 90 e duas folhas 'L' (x=0, dx=1) e 'R' (x=0,9, dx=−1) de comprimento 0,45 com hinge_y = 0,15
```

## Prioridade (MoSCoW)

| Requisito | MoSCoW | Justificativa |
|---|---|---|
| RF-01, RF-02, RF-03, RF-05 | Must | 🟡 RF-090 da 001 é Must; base de todos os demais |
| RF-04 gizmo | Should | 🟡 Alternativa: clique e abrir em massa |
| RF-06, RF-07 interferência | Should | 🟡 RF-091 da 001 é Should |
| RF-08 folha de ambiente | Should | 🟡 Necessária só para portas de ambiente sem porta real (010) |
| RF-09 opções | Could | 🟡 Padrões (90°, encaixe ligado) já atendem |
| Invalidação automática dos resultados de interferência | Won't (no código atual) | 🟢 Não existe; a colisão de corpo tem (`_reversa_sdd/collision/`) |
| Desfazer a abertura | Won't | 🟢 Decisão RN-14 da 001 |

## Rastreabilidade de Código

| Arquivo | Função / Classe | Cobertura |
|---|---|---|
| `caffmob_draw/inspection/__init__.py` | `_modules`, `register`, `unregister` | 🟢 |
| `caffmob_draw/inspection/props.py` | `BTM_PG_Interference`, `BTM_PG_InspectionState` | 🟢 |
| `caffmob_draw/inspection/pivot_math.py` | constantes, `clamp_*`, `snap_angle`, conversões, vetores, `axis_angle_matrix`, `matrix_to_euler_xyz`, `swing_sign`, `edge_rotation`, `slide`, `frame_from_extents`, `side_hinge`, `top_hinge`, `bottom_hinge`, `pose_for` | 🟢 (10 testes puros) |
| `caffmob_draw/inspection/room_door_math.py` | `Leaf`, `leaves`, `leaf_corners`, `open_tip` | 🟢 (5 testes puros) |
| `caffmob_draw/inspection/room_door_leaf.py` | `swing_of`, `has_real_door`, `is_room_door`, `remove_leaves`, `pivots_of`, `leaf_specs`, `ensure_leaves` | 🟢 |
| `caffmob_draw/inspection/fronts.py` | `Front`, `iter_fronts`, `fronts_of`, `front_for_object`, `module_root_of` | 🟢 |
| `caffmob_draw/inspection/adapters/*.py` | `FramelessFront`, `FaceFrameFront`, `ClosetFront`, `BtmFront`, `RoomDoorFront`, `AggregateLeafFront`, `find_fronts`, `front_for_object` | 🟢 |
| `caffmob_draw/inspection/ops_inspect.py` | `scope_fronts`, `BTM_OT_FrontsSetOpen`, `BTM_OT_InspectFronts`, `inspection_running` | 🟢 |
| `caffmob_draw/inspection/gizmo.py` | `BTM_GGT_front_open`, `_commit_pending` | 🟢 |
| `caffmob_draw/inspection/save_guard.py` | `close_for_save`, `reopen_after_save`, `save_pre`, `save_post` | 🟢 |
| `caffmob_draw/inspection/interference.py` | `envelope_hulls`, `_hull_bmesh`, `_Targets`, `check_fronts`, `store_results` | 🟢 |
| `caffmob_draw/inspection/ops_interference.py` | `BTM_OT_CheckFrontInterference`, `BTM_OT_InterferenceGoto` | 🟢 |
| `caffmob_draw/inspection/overlay.py` | `_draw_3d`, `_draw_2d`, `register`, `unregister` | 🟢 |
