# Auditoria — frente do objeto no "Mover Sobre"

**Data:** 2026-11-22 · **Comando:** `/reversa-audit` · **Unit:** `move_over`
**Escopo auditado:** `caffmob_draw/move_over/` (janela Encostar, `scene.py`, `align.py`, `encostar.py`, `rotation.py`,
`dialog_rotate.py`) e as convenções de eixo que ele consome (`selection/classify.py`, `walls2d/apply.py`, `hb_types.py`).
**Método:** leitura de código com `file:line`; **nenhuma execução no Blender nesta rodada** (as afirmações de
comportamento são de código, não de tela).

---

## 1. Resumo executivo

| Severidade | Qtd | Impacto |
|---|---|---|
| ALTA | 3 | A frente exibida e a frente usada para posicionar A não são detectadas: são a convenção "−Y local" aplicada a qualquer objeto |
| MÉDIA | 4 | Não há parede atrás, não há pergunta, não há propriedade persistida; girar a base toca arraste, ímã, cotas e giro |
| BAIXA | 1 | Falta indicador visual de qual lado a janela está chamando de frente |

**Veredito:** o pedido do titular **não está implementado**. O código atual acerta os módulos da biblioteca (que têm a
frente em −Y por construção), mas erra em três casos reais: parede como referência desenhada no sentido inverso,
objeto importado (SketchUp/FBX/grupo solto) e objeto cuja malha não segue a convenção. Não existe hoje nenhum caminho
— nem automático, nem manual — para a janela saber outra frente.

---

## 2. Achados

| ID | Severidade | Achado | Evidência |
|---|---|---|---|
| **A001** | ALTA | As duas vistas são **fixas** nos eixos locais de B: `front = (X, Z)` e `plan = (X, Y)`. A frente é sempre o **−Y local**, por convenção, sem nenhuma verificação. | `ops_dialog.py:43` (`VIEWS`), `scene.py:73` (`b_frame = _frame(self.b)`), `align.py:5` e `encostar.py:5` (docstrings da convenção), `encostar.py:19` (`FRONT: 'NEG_Y'`) |
| **A002** | ALTA | **A parede atrás de B nunca é consultada.** `_wall_of` só devolve `obj.parent` quando é `IS_WALL_BP` e serve **apenas** para reparentar A na prévia; não há varredura de paredes, distância, nem normal. B ser parede só muda a lista de alvos (`WALL_FACE`) e o reparent. | `scene.py:55` (`_wall_of`), `scene.py:260` (`preview`), `ops_dialog.py:82` (`b_is_wall`) |
| **A003** | ALTA | **Não existe propriedade de frente no objeto.** O único `btm_front*` do projeto é `btm_front_hinge` (dobradiça de porta). Logo, um objeto importado ou solto não tem como "ensinar" a frente, e uma escolha manual não sobreviveria à reabertura do arquivo. | `cutting/stale.py:39`, `mechanisms/__init__.py:61`; `move_over/props.py` não tem nenhum campo de frente; `data/properties.py` idem |
| **A004** | MÉDIA | Não há **janela/pergunta de desambiguação** nem operador/painel para escolher a frente. A única janela do bloco é a do Encostar (e o Substituir). | `ops_dialog.py` (campos e chips: lado, afastamento, alinhamento, ímã, grudar — nenhum de frente); `ops_drag.py` |
| **A005** | MÉDIA | A semântica de lados é **eixo Y cru**: `SIDE_AXIS`/`SIDE_FACE` mapeiam "Na frente"/"Atrás" para o índice 1 e `NEG_Y`/`POS_Y`. Girar as vistas sem remapear isso trocaria "Na frente" por "Atrás". | `encostar.py:12-19`, `encostar.py:47`, `align.py:34-62` (`DEPTH`, `WALL_FACE`) |
| **A006** | MÉDIA | **A herda a rotação de B** ao abrir e ao gravar: `_target_matrix` compõe `b_rot @ orientation`. Se a frente de B foi inferida errado, A é **girado** errado, não só desenhado errado. Corrigir apenas o desenho não corrige o resultado. | `scene.py:215-219`, chamado em `preview()` (`scene.py:260`) e `_confirm` (`ops_dialog.py`) |
| **A007** | MÉDIA | Girar a base **não é trocar rótulo**: arraste (`_drag_move` grava `target[h]`/`target[v]` direto em `delta`), ímã (`encostar.snap` por índice de eixo), cota de folga (`_draw_gap` usa `g[h]`/`g[v]`), alças e arestas (`dialog_rotate._project`, `_edge_lines`) e o giro por vista (`rotation.VIEW_AXIS`, `VIEW_SIGN`) usam índices 0/1/2 fixos. | `ops_dialog.py:308-334`, `ops_dialog.py:390-420`, `dialog_rotate.py:25`, `dialog_rotate.py:60-100`, `rotation.py:16` |
| **A008** | BAIXA | Falta **indicador de frente** nas vistas (seta, linha "frente", ou marca no plano). Mesmo com a base certa, o usuário não vê qual lado a janela trata como frente. | `_draw_view` (`ops_dialog.py:385`) desenha título, B, A original tracejada, A e alça — nada de frente |

---

## 3. Como a frente é decidida hoje (cadeia completa)

1. `BTM_OT_MoveOverDialog.invoke` cria `MoveOver(context, a, b)` e **torna B o objeto ativo**
   (`context.view_layer.objects.active = self.mo.b`).
2. `MoveOver.__init__` monta `b_frame = _frame(b)` — **posição e rotação de B, sem escala** — e calcula `box_b` e
   `a_local_box` nesse referencial (`scene.py:73-78`, `scene.py:49`).
3. `VIEWS` lê `(0, 2)` para a Frontal e `(0, 1)` para a Planta: **X de B na horizontal**, Z ou Y na vertical
   (`ops_dialog.py:43`). Tudo o mais — enquadramento, arraste, ímã, cota, alças — projeta nesses mesmos índices.
4. A convenção "frente = −Y local" está escrita nas docstrings e vale para **módulos da biblioteca** e para o módulo
   rápido (`align.py:5`, `scene.py:5`). Ela é verdadeira porque essas bibliotecas nascem assim.
5. Com B = **parede**, a convenção é "face da frente em Y = 0, módulos do lado −Y" (`scene.py:5-6`) — verdadeira para
   parede desenhada com a espessura à esquerda do sentido (`walls2d/apply.py:123`), que é o que o Editor de Paredes
   grava ao aplicar o rascunho.
6. Quando a convenção não vale, **nada no código percebe**: a janela mostra a lateral do objeto como se fosse a frente,
   e `_target_matrix` gira A para essa base errada.

### Onde a convenção quebra na prática

| Caso | Por que quebra | Consequência na janela |
|---|---|---|
| B = parede isolada desenhada no sentido oposto (ou legado/importada) | a "frente" da parede é geométrica, não inferível da matriz: os dois lados são válidos | "Na frente"/"Atrás" ficam trocados; a Frontal mostra o corte da parede, não o lado da sala |
| B = objeto importado (SketchUp, FBX) ou grupo solto | os eixos locais vêm do arquivo, não da convenção | a vista Frontal pode mostrar o fundo; a Planta aparece espelhada/girada |
| B = módulo com malha fora da convenção (peça autoral, geometria livre convertida) | a caixa local não tem a frente em Y mínimo | idem, e A herda a rotação errada |
| B = módulo encostado numa parede | a parede **daria** a frente de graça; hoje ela é ignorada | perde-se a única evidência geométrica disponível |

---

## 4. Comportamento pedido (traduzido em requisitos)

| ID | Requisito | Origem no pedido |
|---|---|---|
| RF-F01 | A frente é decidida **primeiro pela parede atrás** de B: a normal da parede que aponta para o lado de B define a frente; a distância B–parede decide se ela vale (perto vale, longe não vale). | "a parede que está atrás dele… perto ou longe da parede" |
| RF-F02 | **Sem parede**, a frente é o **eixo do objeto** (a convenção local, hoje −Y). | "caso não tenha parede, considerar o eixo" |
| RF-F03 | Em **dúvida** (sem parede e sem convenção confiável, ou parede e eixo em desacordo), abrir uma **janela perguntando a frente**; a resposta é **guardada como propriedade do objeto** e usada sempre. | "se houver dúvidas, mostrar uma janela perguntando a frente… guardar como propriedade" |
| RF-F04 | A frente exibida é **sempre coerente com o eixo do objeto** depois de decidida — nunca um lado arbitrário — e a parede tem precedência na decisão inicial. | "sempre mostrar como frente ao eixo que aquele objeto está, considerando primeiro a parede" |
| RF-F05 | A janela mostra **Frontal e Planta (topo)** com a frente **embaixo/indicada**, ambas na base decidida. | "visão frontal, topo (planta) dentro da janela mover sobre" |
| RF-F06 | A escolha manual vale para o objeto em **todas** as sessões e sobrevive a salvar/reabrir. | "para considerar sempre aquelas a frente do objeto" |
| RF-F07 | Cancelar a pergunta não muda nada nem grava propriedade. | implícito (padrão do add-on) |

---

## 5. Proposta de correção (não implementada nesta rodada)

### 5.1 Núcleo puro novo — `caffmob_draw/move_over/frente.py` (sem `bpy`)

| Símbolo | Papel |
|---|---|
| `yaw_of(normal_xy)` | ângulo (graus) de uma normal 2D, normalizado |
| `wall_candidates(obj, walls)` | paredes candidatas atrás de B: sobreposição em planta, face mais próxima, distância assinada |
| `decide(matrix_b, box_b, walls, stored_yaw, module_like)` | devolve `(yaw, origem, ambíguo)`; `origem ∈ {PROPRIEDADE, PAREDE, EIXO}` |
| `EM_GAP_MAX` | limite de "perto" (proposta: 0,10 m entre o fundo de B e a face da parede) |
| `EM_DESACORDO` | tolerância de desacordo parede × eixo (proposta: 45°) |

Regras de `decide`, nesta ordem:

1. `stored_yaw` existe → `PROPRIEDADE` (a escolha do usuário vence sempre).
2. Parede atrás, em planta e a até `EM_GAP_MAX` do fundo de B → `PAREDE`, frente = normal da parede **apontando para
   B**. Fora do limite (longe) → ignora a parede.
3. Sem parede ou parede longe: `module_like` (resultado de `classify.module_library`) → `EIXO` (comportamento de hoje,
   `yaw = 0`).
4. Sem parede e **não** `module_like` (importado, grupo solto, geometria) → `ambíguo = True` → perguntar.
5. Parede e eixo em desacordo acima de `EM_DESACORDO` → `ambíguo = True` → perguntar (sem gravar nada até responder).
6. Caso especial **B = parede**: a frente é o lado em que A chegou pelo arraste (direção parede → A, em planta). Se A
   estiver sobre a parede, perguntar.

### 5.2 Referencial das vistas

`view_frame = b_frame @ Rz(yaw)` e `box_b`/`a_local_box` calculados nesse referencial. Com `yaw = 0` o resultado é
**idêntico** ao de hoje — é isso que mantém posições salvas (RN-13), campos absolutos e testes existentes válidos.

Para não reescrever dado salvo, `delta` continua no referencial de B; a conversão para a vista fica em dois helpers
(`to_view`/`from_view`) usados no arraste, no ímã e na cota. Os lados (`encostar.SIDE_AXIS`) passam a ser lidos **na
base da vista**, com a tabela de remapeamento; "Na frente" continua significando o lado da frente **do objeto**.

### 5.3 Propriedade persistida

`obj['btm_front_yaw']` (float, graus, gravado no `.blend` como idprop) + leitura no `decide`. Alternativa: campo em
`data/properties.py`; ver pergunta 100. O bloco **não** regrava geometria nem matriz: só orienta a janela.

### 5.4 Interface

- Botão **"Frente"** na janela (linha dos chips) mostrando a origem da decisão (`Parede`, `Eixo`, `Manual`) e abrindo a
  pergunta; a mesma pergunta no menu de contexto do objeto (`caffmob.move_over_front`).
- Pergunta: quatro setas em planta (frente, fundo, esquerda, direita) com o objeto desenhado; Esc cancela sem gravar.
- Frontal e Planta ganham uma **seta "frente"** e o rótulo da origem (A008/RF-F05).

### 5.5 Arquivos tocados (estimativa)

`ops_dialog.py` (~60 linhas: base das vistas, arraste, cota, botão), `scene.py` (~15: `view_frame`, conversões),
`frente.py` (novo, ~120), `ops_front.py` (novo operador, ~60), `move_over/__init__.py` (registro),
`data/translations/move_over.json` (textos novos). Nenhuma mudança em `align.py`/`encostar.py` se a conversão ficar na
borda da vista.

---

## 6. Impacto e riscos

| Risco | Detalhe | Mitigação |
|---|---|---|
| Regressão em arraste/ímã | a base girada muda o significado dos índices `h`/`v` | conversão só na borda; teste puro da conversão ida-e-volta; `yaw = 0` coberto por toda a suíte atual |
| Posições salvas (RN-13) | `delta` é relativo ao referencial de B | manter `delta` em B e converter na vista; teste com posição salva antes/depois |
| Rotação de A (A006) | `_target_matrix` compõe `b_rot` | trocar por `view_frame` de forma explícita; teste com B girado 90° e 180° |
| Parede "perto" mal calibrada | 0,10 m pode ser pouco para módulo afastado da parede | limite em propriedade de cena/preferência, ou distância medida pela face traseira do módulo (pergunta 99) |
| Duas paredes opostas | canto/península: duas candidatas válidas | `ambíguo` → pergunta, nunca escolha silenciosa |
| Propriedade em objeto que muda de lugar | a frente guardada continua valendo após girar o objeto (é local) | documentar que o yaw é **local** ao objeto |
| Objetos importados com escala negativa | `_frame` descarta escala; espelhamento não é tratado | fora do escopo; registrar como lacuna se aparecer em teste |

---

## 7. Plano de verificação (quando implementar)

1. **Puros** (`tests/test_move_over_frente.py`, ~8 casos): yaw de normal; parede atrás dentro/fora do limite; sem
   parede + módulo → eixo; sem parede + importado → ambíguo; desacordo > 45° → ambíguo; propriedade vence; parede
   oposta (perto de duas) → ambíguo; `yaw = 0` devolve a base de hoje.
2. **Blender, headless** (`tests/blender_018_frente_smoke.py`): parede girada 90°/180° com módulo filho → a vista
   Frontal mostra a frente do módulo (largura × altura) e o chip "Na frente" põe A do lado da sala; grupo importado
   (Empty + malha) → o diálogo abre a pergunta; escolher e gravar → reabrir a janela já vem decidido; Esc não grava.
3. **Regressão**: `tests/test_move_over_align.py`, `tests/test_reposition.py`, `tests/blender_067_onda6_mover.py`,
   `tests/blender_bug_RQR5_janela_encostar.py`, `tests/blender_bug_skp_mover_sobre.py`.

---

## 8. Decisões abertas

- **Pergunta 99** — precedência e limite de "perto"; e, com B = parede, se a frente é o lado onde A foi solto.
- **Pergunta 100** — onde guardar a escolha (idprop × `bpy.props`) e se ela vale só para o Mover Sobre ou para todo o
  add-on (cotas, moldura, inserção).

---

## 9. O que esta auditoria não fez

- Não alterou código, propriedades, testes nem configuração.
- Não executou o Blender: nenhum comportamento de tela foi observado; os achados são de leitura de código.
- Não mediu desempenho da varredura de paredes que a proposta exige.
