# Editor de Paredes 2D (walls2d) — Requisitos

🟢 **CONFIRMADO** — contrato extraído de `caffmob_draw/walls2d/` em 2026-10-10, incluindo a árvore de trabalho ainda sem commit da feature 013 (`ops_editor.py`, `props.py`, `compat.py`). 🟢 **Decisão do titular (2026-10-10, questions.md#pergunta-70):** commitar a 013 antes de congelar as specs; enquanto não houver commit, RN-24/RN-25, RF-10/RF-11 e CA-20..CA-23 ficam **pendentes de commit** (DT-07). Confirmação de código não implica validação visual no Blender. 🟡 identifica prioridade ou intenção inferida; 🔴 identifica lacuna de validação. O contrato de vista, gestos, desenho e janela vem de `_reversa_sdd/canvas2d/` e não é redescrito aqui.

## Visão Geral

🟢 Planta 2D vista de cima onde o projetista desenha e edita as paredes do Home Builder 5 (`IS_WALL_BP`) como **rascunho em memória**: nós, trechos, faces interna/externa, direção da espessura, tipo e pés-direitos. Nada muda no 3D até o OK, que grava o rascunho nas paredes, remove as apagadas, refaz esquadrias, piso/teto e aberturas. Fontes: `__init__.py` (docstring), `props.py` (docstring), `apply.py:apply_plan`.

## Responsabilidades

- 🟢 Modelar cadeias de paredes em Python puro: geometria das faces, ângulos, esquadrias, edição e validação (`model.py`).
- 🟢 Ler as paredes da cena para o rascunho e converter paredes da camada nova (`scene_io.py`, `convert.py`).
- 🟢 Manter a sessão única do editor, os campos virtuais do painel e o desfazer próprio do rascunho (`props.py`, `history.py`).
- 🟢 Interpretar eventos da planta: ferramentas, lápis com mira e digitação, perguntas, navegação, barra superior com zoom janela (`ops_editor.py`, `inference.py`, `direction.py`).
- 🟢 Desenhar a planta num handler `POST_PIXEL` do Image Editor e expor painéis na região lateral (`window.py`, `ops_editor.py:draw_plan`, `panels.py`).
- 🟢 Aplicar o rascunho às paredes do Home Builder 5 e sincronizar o pé-direito do projeto (`apply.py`, `heights.py`).
- 🟢 Fora da responsabilidade: conversão mundo↔pixel, fatores de zoom, primitivas GPU e abertura/fechamento da janela (`canvas2d`); criação de `GeoNodeWall`, esquadrias e piso/teto (`hb_types`, `operators/walls.py`); remoção de parede (`operators/ops_wall_extras.py`); portas/janelas reais (`openings/sync.py`).

## Regras de Negócio

| ID | Regra confirmada | Fonte |
|---|---|---|
| RN-01 | 🟢 Os nós de uma cadeia são a **face interna** (medida real). A face externa é a linha deslocada pela espessura `t` para o lado `side` (`LEFT`/`RIGHT` em relação ao sentido dos nós), prolongada nas pontas por `t·tan(meia virada)` (esquadria). Ponta sem vizinho tem meia virada 0. | model.py:Chain.outer_line/miter_angles |
| RN-02 | 🟢 Limites (metros/graus): comprimento 0,01–100; espessura 0,01–2; pé-direito inicial e final 0,5–10; ângulo absoluto 0–360; relativo −180–180. Fora da faixa: `ValueError` traduzido "Valor Inválido: {campo} deve estar entre {lo} e {hi} (recebido: {v})." (com ponto final). Limites inclusivos. _(Revisão 2026-10-10: model.py:36)_ | model.py:LIMITS/validate |
| RN-03 | 🟢 Tipos: `NORMAL`, `DIVISORIA`, `MURETA`. Trocar o tipo aplica os padrões: Divisória espessura 0,10; Mureta altura e altura final 1,10; Normal nenhum. Gravar `height` arrasta `end_height` para o mesmo valor. | model.py:TYPE_DEFAULTS/set_segment_value |
| RN-04 | 🟢 Contorno fechado leva a espessura para fora: `outward_side` = `RIGHT` se anti-horário (área com sinal > 0; aberto: soma das viradas ≥ 0), senão `LEFT`. Fechar pelo lápis sempre aplica; fechar por arraste ou no OK só aplica se nenhum trecho da cadeia tiver `source`. | model.py:is_ccw/outward_side; ops_editor.py:_handle_prompt; apply.py:apply_plan |
| RN-05 | 🟢 Mudar o comprimento na face interna move o nó final na direção atual do trecho. Na face externa, ajuste iterativo (até 12 passos, tolerância 1e−7 m) porque a esquadria muda quando o nó anda; cada passo valida o comprimento interno. | model.py:set_length |
| RN-06 | 🟢 "Bloquear Ângulo" no trecho que **chega** num nó faz esse nó andar só na direção desse trecho (projeção escalar). Vale para arraste, digitação e campos do painel. | model.py:move_node |
| RN-07 | 🟢 Adicionar Vértice divide o trecho no ponto projetado com `t` preso a [0,05; 0,95] (trecho degenerado: 0,5); o novo trecho é cópia rasa sem `source`. | model.py:split |
| RN-08 | 🟢 Remover Vértice exige 2+ trechos na cadeia; ponta de cadeia aberta remove o trecho da ponta; nó interno une os vizinhos (o trecho anterior continua até o nó seguinte). O `source` do trecho descartado **não** vai para `removed_sources`. | model.py:remove_node |
| RN-09 | 🟢 Inverter Sentido inverte nós e trechos e troca `side`, mantendo a parede fisicamente no lugar; fechada, o primeiro nó continua o primeiro. | model.py:invert |
| RN-10 | 🟢 Cadeia aberta fecha automaticamente quando tem 3+ trechos, 4+ nós e o último nó está a ≤ 0,01 m do primeiro (o duplicado sai). Usado na pergunta de arraste e como rede de segurança no OK. | model.py:close_if_touching; apply.py:apply_plan |
| RN-11 | 🟢 A assinatura do rascunho (nós arredondados a 6 casas, `closed`, `side`, campos dos trechos com `source`, `removed_sources`, `converted_sources`) decide "sujo" e passos de desfazer. Desfazer guarda até 100 passos; passo novo descarta o refazer. | model.py:plan_signature; history.py |
| RN-12 | 🟢 Nada vai para o 3D antes do OK. O OK tem duas fases: com itens que não cabem, módulos em trechos apagados ou pé-direito diferente do projeto, a 1ª chamada só preenche avisos (`confirm_pending`); a 2ª aplica. Cancelar/Esc com rascunho sujo pede confirmação. | ops_editor.py:BTM_OT_WallEditorOk/BTM_OT_WallEditorCancel/_handle |
| RN-13 | 🟢 Ordem das travas da mira: ímã do início do lápis (2+ trechos, ≤ 15 px) → vértice (≤ 9 px) → trava ortogonal (±2,5°, fixa um eixo) + alinhamento X/Y com vértices (≤ 8 px na tela, só no eixo não fixado; Shift desliga) → grade magnética (só se nada travou). | ops_editor.py:resolve_point |
| RN-14 | 🟢 Direção do lápis: nasce no primeiro Enter pela direção do mouse (encaixe 0/90/180/270° a ≤ 2,5°), muda só por clique (direção do trecho criado) ou setas; o mouse sozinho nunca a muda; zera ao começar uma cadeia e ao terminar por Esc/botão direito; fechar pelo "Sim" não zera, mas o próximo clique inicial zera _(Revisão 2026-10-10: ops_editor.py:_handle_prompt 862-867 sem reset_direction; _handle_draw:812)_. | direction.py; ops_editor.py:_handle_draw/_append |
| RN-15 | 🟢 Digitação aceita `0123456789,.+-*/() ` e `mMcC` só depois de algum dígito, até 64 caracteres; Enter interpreta na unidade do projeto, rejeita zero; conta mostra prévia ("= 16 mm"/"Valor Inválido"). | ops_editor.py:accept_typing/_typed_length; data/expr.py; data/units.py:parse_length |
| RN-16 | 🟢 Delete ou X remove o trecho selecionado (ferramenta ≠ Construir): em cadeia fechada, abre o contorno começando no nó seguinte ao trecho; em aberta, divide em até duas cadeias, descartando partes sem trecho. `source` do trecho vai para `removed_sources`. | ops_editor.py:remove_segment |
| RN-17 | 🟢 Paredes da cena viram cadeias: começa na parede sem vizinha à esquerda e segue pela direita; laços sem início também entram; fecha com 3+ paredes se o fim da última está a < 0,01 m do início da primeira; `side='LEFT'`. | scene_io.py:read_plan/_chain_from |
| RN-18 | 🟢 Paredes da camada nova selecionadas na abertura: converter (padrão) ou só referência. Convertidas viram cadeias novas (sem `source`) a partir da linha de centro deslocada meia espessura; sem dados ficam como referência tracejada; no OK o objeto original é removido. | ops_editor.py:BTM_OT_WallEditor; scene_io.py:convert_into; convert.py |
| RN-19 | 🟢 O Home Builder 5 põe a espessura à esquerda: no OK, cadeia com `side='RIGHT'` é aplicada invertida. A primeira parede fica solta no primeiro nó; as seguintes presas ao fim da anterior (`COPY_LOCATION`). | apply.py:apply_plan; model.py:hb_order |
| RN-20 | 🟢 Parede cuja rotação muda mais de 90° no OK mantém os filhos (exceto `obj_x`) na mesma matriz de mundo; portas/janelas são re-hospedadas (deslocam −Dim X, rotação zerada, `Swing Inside` e `Is Left` invertidos na folha). Aberturas recebem `Dim Y` = espessura do trecho. | apply.py:apply_plan/_rehost_opening |
| RN-21 | 🟢 Paredes de `removed_sources` não reutilizadas são removidas; seus módulos ficam soltos no lugar, salvo "Remover os módulos junto?". Portas, janelas, cotas, `obj_x` e o proxy de rebaixo (`btm_lowered_proxy`) sempre saem com a parede _(Revisão 2026-10-10: ops_wall_extras.py:18-21 KEEP_WITH_WALL)_. | apply.py:apply_plan/modules_of_removed; ops_wall_extras.KEEP_WITH_WALL |
| RN-22 | 🟢 Mureta (`btm_wall_type`) e meia-parede/parede falsa do legado (`WALL_TYPE` `Half`/`Fake`) não acompanham o pé-direito do projeto; tolerância 1 mm. "Igualar ao pé-direito do projeto" (padrão ligado) grava `height = end_height = pé-direito` no OK nas demais. | heights.py; apply.py:height_mismatches/apply_plan |
| RN-23 | 🟢 Depois de aplicar: esquadrias de todas as paredes, piso/teto existentes refeitos (troca só a malha; salas fechadas emparelhadas com pisos/tetos na ordem dos nomes) e portas/janelas reais sincronizadas. | apply.py:apply_plan/refresh_floors_and_ceilings |
| RN-24 | 🟢 Navegação (013): roda e Ctrl+roda dão zoom ancorado obedecendo `PreferencesInput.invert_zoom_wheel`; pinça (`TRACKPADZOOM`) dá zoom ancorado proporcional ao gesto; `TRACKPADPAN` e botão do meio movem a vista; Home enquadra com margem 0,15. Funciona em qualquer ferramenta e estado (inclusive com pergunta aberta ou lupa ligada); não recalcula a mira (exceto Home, que não está em `NAVIGATION_EVENTS`) e não gera passo de desfazer _(Revisão 2026-10-10: ops_editor.py:44, 592-593)_. | ops_editor.py:_handle/_is_navigation/modal |
| RN-25 | 🟢 Barra superior de `32 px × ui_scale` acima da área útil, com a lupa (zoom janela): 1º clique arma, 2º clique na lupa desarma, Esc cancela só o modo; arrastar um retângulo (≥ 5 px por lado) enquadra com margem 0; clique em outro ponto da barra não chega às ferramentas. Com a lupa ligada, só navegação, Ctrl+Z e a própria lupa agem. | ops_editor.py:_toolbar_rects/handle_zoom_window/_handle |
| RN-26 | 🟢 Ctrl+Z (ou ⌘) desfaz e Ctrl+Shift+Z ou Ctrl+Y refaz **no rascunho**, sem chegar ao desfazer do Blender; sem passo: "Nada para desfazer."/"Nada para refazer.". | ops_editor.py:_handle_undo; props.py:Session.undo/redo |
| RN-27 | 🟢 Um editor por vez: abrir exige janela, Blender não em segundo plano e nenhuma sessão ativa. | ops_editor.py:BTM_OT_WallEditor.poll |
| RN-28 | 🟢 Campos de medida do painel mostram a unidade do projeto sem arredondar; texto sem sufixo vale a unidade do projeto; aceitam mm/cm/m e contas; zero é rejeitado. Erro do modelo vai para `s.error` (painel e planta). | props.py:_text_get/_text_set/_guard |
| RN-29 | 🟢 Mudar o pé-direito do projeto nas Configurações grava `Height`/`End Height` em todas as paredes de altura cheia do arquivo (todas as cenas) e refaz esquadrias e piso/teto da cena atual. | apply.py:sync_project_height; hb_props.py:84 |

## Requisitos Funcionais

🟡 Prioridades inferidas do caminho crítico (abrir → editar → OK), dos consumidores e dos testes existentes; não constituem roadmap aprovado.

| ID | Requisito | Prioridade | Critério de aceite |
|---|---|---|---|
| RF-01 | 🟢 Modelo puro de cadeias: faces, ângulos, esquadrias, validação, edição (RN-01 a RN-10) | Must | CA-01 a CA-04 |
| RF-02 | 🟢 Abrir o editor: ler paredes, converter camada nova, criar sessão, abrir janela, iniciar modal (RN-17, RN-18, RN-27) | Must | CA-05, CA-06 |
| RF-03 | 🟢 Selecionar face/vértice, arrastar vértice com travas, digitar medida (RN-05, RN-06, RN-13, RN-15) | Must | CA-07, CA-08 |
| RF-04 | 🟢 Lápis: clique e Enter com direção travada, setas, fechar contorno (RN-04, RN-13, RN-14) | Must | CA-09, CA-10 |
| RF-05 | 🟢 Ferramentas Inverter, Adicionar/Remover Vértice e Delete (RN-07 a RN-09, RN-16) | Should | CA-11, CA-12 |
| RF-06 | 🟢 Campos do trecho no painel ligados ao rascunho (RN-02, RN-03, RN-28) | Must | CA-13, CA-14 |
| RF-07 | 🟢 Desfazer/refazer do rascunho (RN-11, RN-26) | Should | CA-15, CA-16 |
| RF-08 | 🟢 OK em duas fases e aplicação nas paredes do Home Builder 5 (RN-12, RN-19 a RN-23) | Must | CA-17, CA-18 |
| RF-09 | 🟢 Cancelar com confirmação quando sujo (RN-12) | Must | CA-19 |
| RF-10 | 🟢 Navegação por roda, touchpad, botão do meio e Home (RN-24) | Must | CA-20, CA-21 |
| RF-11 | 🟢 Barra superior com zoom janela (RN-25) | Should | CA-22, CA-23 |
| RF-12 | 🟢 Pé-direito do projeto: avisar/igualar no OK e sincronizar pelas Configurações (RN-22, RN-29) | Should | CA-24 |
| RF-13 | 🟢 Desenho da planta e painéis laterais (Ferramentas, Painel, Grid, Confirmar) | Must | CA-25 |

## Requisitos Não Funcionais

| Tipo | Requisito observado | Evidência | Confiança |
|---|---|---|---|
| Desempenho da mira | Alinhamento X/Y em O(log n) por movimento (duas listas ordenadas + `bisect`); índice refeito só quando a assinatura do rascunho muda | inference.py:Index; ops_editor.py:_index | 🟢 |
| Desempenho da navegação | Eventos de navegação não recalculam a mira (o touchpad manda dezenas de eventos) | ops_editor.py:modal/_is_navigation | 🟢 |
| Memória do desfazer | Até 100 cópias profundas do rascunho (`LIMIT = 100`) | history.py:LIMIT/checkpoint | 🟢 |
| Tolerância de toque | Alvos em pixels de tela, independentes do zoom: vértice 9, linha 7, ímã 15, alinhamento 8 (convertido em metros por `8/scale`) | ops_editor.py:NODE_HIT_PX/LINE_HIT_PX/SNAP_CLOSE_PX/ALIGN_PX | 🟢 |
| Escala de interface | Barra superior escala com `preferences.system.ui_scale` (0 em segundo plano → 1) | ops_editor.py:_ui_scale/toolbar_height | 🟢 |
| Separação do cálculo | `model`, `history`, `inference`, `direction`, `heights`, `convert` rodam sem `bpy` (36 testes puros) | `__init__.py:_modules` (import tardio); tests/test_walls2d_*.py, test_wall_*.py | 🟢 |
| Desfazer do Blender | Aplicação no OK acontece dentro do modal com `bl_options` `UNDO`: um passo de desfazer do Blender | ops_editor.py:BTM_OT_WallEditorModal | 🟡 (efeito depende do Blender empilhar o passo ao terminar o modal com FINISHED) |
| Latência de comandos do painel | OK/Cancelar só põem `request`; o modal aplica no próximo evento, com timer de 0,1 s garantindo eventos | ops_editor.py:TIMER_STEP/modal | 🟢 |

## Critérios de Aceitação

🟢 Cenários derivados das funções atuais. CA-01, CA-03, CA-09 (parte direção) e CA-15 têm equivalentes nos testes puros; CA-02 só em parte (outro valor, mensagem por regex) e CA-04 não tem teste _(Revisão 2026-10-10: tests/test_walls2d_model.py:68-105)_; os demais exigem Blender.

```gherkin
CA-01 — Face externa com esquadria
Dado a sala rectangle(4, 3) (anti-horária, side RIGHT, espessura 0,15)
Quando meço face_length(0, OUTER)
Então obtenho 4,30 m (interna 4,00 + 0,15 em cada canto), e face_length(0, INNER) = 4,00

CA-02 — Valor fora do limite
Dado um trecho selecionado
Quando set_segment_value(i, 'thickness', 2.5)
Então ValueError "Valor Inválido: Espessura deve estar entre 0.01 m e 2 m (recebido: 2.5 m)." e o trecho não muda _(Revisão 2026-10-10: model.py:36)_

CA-03 — Bloquear Ângulo
Dado um trecho i com lock_angle e seu nó final k
Quando move_node(k, ponto fora da reta do trecho)
Então o nó fica na projeção do ponto sobre a reta do trecho i

CA-04 — Remover vértice da única parede
Dado uma cadeia com um único trecho
Quando remove_node(0)
Então ValueError "Uma cadeia precisa de pelo menos um trecho." e a cadeia continua intacta

CA-05 — Abertura normal
Dado uma cena com paredes IS_WALL_BP encadeadas e nenhuma sessão aberta
Quando executo caffmob.wall_editor
Então a sessão é criada com o pé-direito do projeto, new_height recebe esse valor, a janela abre, o primeiro trecho fica selecionado e o modal começa

CA-06 — Sem janela disponível
Dado contexto sem área ou janela e duplicação impossível
Quando executo caffmob.wall_editor
Então o operador reporta ERROR "O Editor de Paredes precisa de uma janela do Blender aberta.", encerra a sessão e devolve CANCELLED

CA-07 — Digitação na face selecionada
Dado SELECT com a face OUTER de um trecho selecionada e unidade do projeto em mm
Quando digito "2*1500" e Enter
Então a face externa passa a medir 3000 mm (ajuste iterativo), s.typed fica vazio e um passo de desfazer é gravado

CA-08 — Digitação no primeiro vértice de cadeia aberta
Dado o nó 0 de uma cadeia aberta selecionado
Quando digito "1000" e Enter
Então s.error = "Valor Inválido: o primeiro vértice de uma parede aberta não tem trecho chegando nele." e nada muda

CA-09 — Lápis com direção travada
Dado DRAW, ponto inicial clicado e mouse a 1° do eixo X
Quando digito "4" com unidade m e Enter
Então o trecho de 4 m é criado na direção 0° (encaixe ortogonal) e a direção fica travada para os próximos Enter

CA-10 — Enter sem direção
Dado DRAW, ponto inicial clicado e cursor exatamente sobre o ponto inicial (sem direção)
Quando digito "4" e Enter
Então s.error = "Mova o mouse na direção da parede ou use as setas do teclado" e nenhum trecho é criado

CA-11 — Fechar contorno pelo lápis
Dado um desenho com 2+ trechos e o cursor a ≤ 15 px do primeiro nó
Quando clico e respondo "Sim"
Então o trecho de fechamento é acrescentado, a cadeia fecha, side = outward_side, o lápis termina e a ferramenta vira SELECT

CA-12 — Delete em cadeia fechada
Dado uma sala fechada de 4 trechos com o trecho 1 selecionado (source "Wall.001")
Quando aperto Delete
Então a cadeia vira aberta com 4 nós e 3 trechos começando no nó 2, e "Wall.001" entra em removed_sources

CA-13 — Campo de texto com unidade
Dado unidade do projeto mm e um trecho selecionado
Quando escrevo "2,5 m" em length_text
Então o comprimento na linha escolhida vira 2,5 m, s.error fica vazio e o painel mostra "2500 mm"

CA-14 — Campo de texto inválido
Dado um trecho selecionado
Quando escrevo "abc" em thickness_text
Então s.error recebe a mensagem de parse_length, o trecho não muda e nenhum passo é gravado

CA-15 — Desfazer no rascunho
Dado dois passos gravados
Quando aperto Ctrl+Z e depois Ctrl+Shift+Z
Então o rascunho volta ao anterior e depois ao último; lápis, digitação e perguntas são limpos

CA-16 — Nada para desfazer
Dado um rascunho recém-aberto
Quando aperto Ctrl+Z
Então s.error = "Nada para desfazer." e o evento não chega ao desfazer do Blender

CA-17 — OK com avisos
Dado um trecho existente encurtado de modo que um módulo filho passa do fim
Quando clico OK pela primeira vez
Então o painel lista "{módulo} não cabe em {parede}", o operador reporta WARNING e nada é aplicado; no 2º OK aplica

CA-18 — OK aplica
Dado um rascunho com um trecho novo, um atualizado e um removido
Quando o OK é aceito
Então report = 1 nova, 1 atualizada, 1 removida; esquadrias, piso/teto e aberturas reais são atualizados e a janela fecha 0,05 s depois

CA-19 — Cancelar sujo
Dado um rascunho alterado desde a abertura
Quando clico Cancelar (ou Esc fora do lápis sem digitação)
Então é pedida confirmação ("Descartar as alterações e fechar o editor?"); só "Descartar"/"Sim" fecha sem alterar as paredes

CA-20 — Pinça durante digitação
Dado DRAW com "2.4" digitado no meio de um trecho
Quando faço pinça sobre a planta
Então a escala muda ancorada no cursor, e typed, o trecho em curso e o histórico ficam iguais

CA-21 — Roda invertida pela preferência
Dado invert_zoom_wheel ligado
Quando giro a roda para cima (com ou sem Ctrl)
Então a escala é dividida por 1,15

CA-22 — Zoom janela
Dado a lupa armada
Quando arrasto um retângulo de 200 × 120 px na planta
Então a vista é centrada no retângulo com fit(bounds, margin=0) (o eixo limitante ocupa toda a área útil) e a lupa desarma

CA-23 — Zoom janela curto ou cancelado
Dado a lupa armada
Quando arrasto 3 px ou aperto Esc
Então a vista não muda, a lupa desarma e o lápis/rascunho não são afetados

CA-24 — Igualar pé-direito
Dado pé-direito do projeto 2,70 m, uma parede Normal de 2,60 m e uma Mureta de 1,10 m
Quando dou OK duas vezes com "Igualar" ligado
Então a Normal passa a 2,70 m (inicial e final) e a Mureta continua 1,10 m

CA-25 — Painel sem seleção
Dado nenhum trecho selecionado
Quando o painel "Painel" é desenhado
Então mostra só "Selecione um trecho na planta."
```

## Prioridade (MoSCoW)

| Requisitos | Classificação | Justificativa |
|---|---|---|
| RF-01, RF-02, RF-03, RF-04, RF-06, RF-08, RF-09, RF-10, RF-13 | 🟡 Must | Caminho crítico abrir → editar → OK; modelo usado também por `geometry/floor_outline.py` e `cabinet_editor/state.py` (histórico) |
| RF-05, RF-07, RF-11, RF-12 | 🟡 Should | Têm alternativa (arrastar/redesenhar, Cancelar, roda/Home, igualar manualmente) |
| `model.rectangle`, `WallPlan.remove_chain_segment_sources` | 🟡 Could | Sem chamador no pacote além dos testes (grep) |

## Rastreabilidade de Código e Verificação

| Arquivo | Símbolos / responsabilidade | Evidência |
|---|---|---|
| caffmob_draw/walls2d/model.py | `Segment`, `Chain`, `WallPlan`, `validate`, `plan_signature`, `rectangle` | 🟢 Código; test_walls2d_model |
| caffmob_draw/walls2d/history.py | `History` | 🟢 Código; test_walls2d_history |
| caffmob_draw/walls2d/inference.py | `Index`, `plan_points` | 🟢 Código; test_wall_inference |
| caffmob_draw/walls2d/direction.py | `initial_direction`, `ARROWS`, `label`, `next_point` | 🟢 Código; test_wall_direction |
| caffmob_draw/walls2d/heights.py | `follows_project_height`, `walls_to_equalize` | 🟢 Código; test_walls2d_heights |
| caffmob_draw/walls2d/convert.py | `chains_from_segments` | 🟢 Código; test_walls2d_convert |
| caffmob_draw/walls2d/scene_io.py | `read_plan`, `convert_into`, `reference_segments`, `is_other_layer_wall` | 🟢 Código; blender_002_smoke |
| caffmob_draw/walls2d/apply.py | `apply_plan`, avisos, `refresh_floors_and_ceilings`, `sync_project_height` | 🟢 Código; blender_002_smoke, blender_bug_TBY3_walls |
| caffmob_draw/walls2d/props.py | `Session`, campos virtuais, `BTM_PG_WallEditorState` | 🟢 Código |
| caffmob_draw/walls2d/ops_editor.py | 5 operadores, `draw_plan`, `resolve_point`, barra superior | 🟢 Código; blender_002_ui_events, blender_009_walls_smoke, blender_013_touchpad_smoke |
| caffmob_draw/walls2d/panels.py | 4 painéis da região lateral | 🟢 Código |
| caffmob_draw/walls2d/window.py | Handler de desenho e embrulhos de `canvas2d.window` | 🟢 Código |

🟢 Executado em 2026-10-10: `PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=tests python3 -m unittest test_wall_direction test_wall_inference test_walls2d_convert test_walls2d_heights test_walls2d_history test_walls2d_model`: **36 testes aprovados**. Os testes `blender_*` não foram executados nesta extração.

## Lacunas e Pré-condições

- 🟢 **Decisão do titular (2026-10-10, questions.md#pergunta-1):** Remover Vértice deve registrar o `source` do trecho eliminado em `removed_sources`, como o Delete (`remove_segment`). 🟢 (código) hoje `remove_node` descarta o `source` e a parede correspondente fica na cena, fora do rascunho (EC-01). Pendência de implementação: DT-01.
- 🟢 **Decisão do titular (2026-10-10, questions.md#pergunta-8):** o "Não" da pergunta de fechamento por arraste deve sobreviver ao OK (a cadeia marcada pula `close_if_touching`). 🟢 (código) hoje a rede de segurança do OK fecha a cadeia mesmo assim (EC-03). Pendência de implementação: DT-02.
- 🟢 **Decisão do titular (2026-10-10, questions.md#pergunta-9):** a barra superior consome só `LEFTMOUSE PRESS`; o `RELEASE` segue quando há arraste de vértice ou retângulo da lupa em curso. 🟢 (código) hoje soltar sobre a barra não termina o arraste (EC-05). Pendência de implementação: DT-03.
- 🟡 Sinal real da pinça por plataforma (herdado de `canvas2d`/`compat.pinch_delta`). Decisão do titular (2026-10-10, questions.md#pergunta-72): validar à mão com `tests/blender_013_trackpad_probe.py` em cada plataforma e registrar em `investigation.md` §6 — decisão: medir/testar (DT-06).
- 🟢 O rascunho só é consistente se os nomes em `source` existirem no OK; nomes ausentes viram paredes novas (`apply.py:apply_plan`, `bpy.data.objects.get` devolve `None`).
