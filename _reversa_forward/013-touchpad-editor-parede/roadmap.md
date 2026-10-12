# Roadmap: Zoom e navegação por touchpad no editor de parede

> Identificador: `013-touchpad-editor-parede`
> Data: `2026-10-10`
> Requirements: `_reversa_forward/013-touchpad-editor-parede/requirements.md`
> Confidência: 🟢 CONFIRMADO, 🟡 INFERIDO, 🔴 LACUNA

## 1. Resumo da abordagem

A navegação do Editor de Paredes já passa por um ponto só: `BTM_OT_WallEditorModal._handle`
(`caffmob_draw/walls2d/ops_editor.py`, l. 510-523). Esse ponto é tratado antes da caixa de pergunta e das ferramentas.
A feature acrescenta ali os eventos `TRACKPADZOOM` e `TRACKPADPAN`. Como já acontece com a roda, o gesto vale em
qualquer estado e é consumido (`RUNNING_MODAL`), então não vaza para o Editor de Imagem por baixo.

A conta (fator de zoom a partir do delta, retângulo do zoom janela) fica num núcleo puro novo,
`canvas2d/gestures.py`, testável sem Blender. A leitura do delta no `Event` passa por um encaixe em `compat.py`.

O primeiro passo é uma **prova** no Blender 5.2, porque o corpus não documenta como o delta do gesto chega.

A barra superior é desenhada em GPU no mesmo `POST_PIXEL` da planta, como a caixa de pergunta, e tem um botão: a lupa
do zoom janela. O modo zoom janela é estado transitório da sessão, fora do histórico de desfazer. Ele usa
`View2D.fit`, que já existe.

## 2. Princípios aplicados

| Princípio | Como a feature se relaciona | Status |
|-----------|------------------------------|--------|
| I. Simples por fora, milimétrico por dentro | Os gestos funcionam sem configuração. A barra tem um único botão, com dica ao passar o mouse | respeita |
| II. Medir antes de cortar | A ação de prova (D-02) mede a codificação do delta antes do núcleo. A preferência `invert_zoom_wheel` e os tipos de evento são citados do corpus | respeita |
| III. Nada pregado | A sensibilidade da pinça e as medidas da barra viram constantes nomeadas num lugar só (`gestures.py` e `ops_editor.py`). Elas não são regra de negócio, então não vão para preferências | respeita |
| IV. Cada camada na espessura certa | A conta fica em `canvas2d/gestures.py` (puro). O modal só despacha. O desenho fica em `draw_plan` | respeita |
| V. Encaixes padronizados | `compat.trackpad_delta(event)` isola a leitura do delta, e o editor de armário poderá reusá-lo na feature seguinte | respeita |
| VI. Reaproveitar antes de criar | Reaproveita `View2D.zoom`, `View2D.pan`, `View2D.fit`, `canvas2d/draw.button` e `outline` e o tratamento atual da roda | respeita |
| VII. Caixote no esquadro | Teste puro novo, fumaça própria e regressão das fumaças do editor de parede (002, 009). Não registra classe nova | respeita |
| VIII. Fita de borda | Delta zero, retângulo menor que 5 px, Esc no meio do zoom janela e gesto sobre o painel lateral têm comportamento definido | respeita |
| IX. Aproveitamento milimétrico | Eventos de navegação pulam `_update_snap` (índice de inferência), que hoje roda em todo evento | respeita |

## 3. Decisões técnicas

| ID | Decisão | Justificativa | Alternativas descartadas | Confidência |
|----|---------|----------------|--------------------------|-------------|
| D-01 | Núcleo puro `caffmob_draw/canvas2d/gestures.py`, sem `bpy`. Funções: `pinch_factor(delta, sensitivity=PINCH_SENSITIVITY)` = `exp(delta × sensitivity)`; `wheel_factor(up, inverted)` = `1,15` ou `1/1,15`; `zoom_window_bounds(view, p0_px, p1_px, min_px=5)` → bounds do mundo ou `None` | A exponencial dá zoom proporcional ao gesto, simétrico (ida e volta exata, RF-02) e independente da escala de partida. Delta zero dá fator 1 | Fator linear `1 + delta·k`, que não é simétrico e pode zerar a escala; passo fixo de 15%, que contraria a RN-02; conta dentro do modal, que contraria o Princípio IV | 🟢 |
| D-02 | **Prova primeiro** (`tests/blender_013_trackpad_probe.py`, com janela e `--enable-event-simulate`): enviar `TRACKPADZOOM` e `TRACKPADPAN` com `Window.event_simulate` e registrar `mouse_x/y` e `mouse_prev_x/y`. Ela fixa qual eixo leva a pinça, o sinal de "afastar os dedos" e o sinal do arraste. Se a simulação não reproduzir o delta, a prova é refeita à mão num notebook (Wayland) com um `print` temporário. O resultado fica registrado em `investigation.md` | O corpus confirma `Event.mouse_prev_x` e `mouse_prev_y` e os tipos `TRACKPADZOOM`/`TRACKPADPAN`, mas não a codificação do delta (`docs/rag/blender-api/corpus/bpy.types.Event.md#bpy.types.Event.mouse_prev_x`; `.../bpy_types_enum_items/event_type_items.md`) | Supor o sinal pelo código C do Blender sem medir, o que contraria o Princípio II | 🟡 |
| D-03 | Encaixe `compat.trackpad_delta(event)` → `(dx, dy)` = `(mouse_x − mouse_prev_x, mouse_y − mouse_prev_y)`, com o ajuste de eixo e sinal que a prova (D-02) fixar | Diferença de versão ou de plataforma fica em `compat.py` (`CLAUDE.md`, Princípio V) | Ler `mouse_prev_*` direto no modal | 🟡 |
| D-04 | Em `_handle`, junto da roda: `TRACKPADZOOM` → `view.zoom(gestures.pinch_factor(delta_zoom), pixel)`; `TRACKPADPAN` → `view.pan(dx, dy)` com o sinal da prova; retorna `True` (consumido) | Mesmo ponto da roda: vale em todas as ferramentas, na digitação, com a pergunta aberta e no arraste (RN-05). Consumir impede que o gesto chegue ao Editor de Imagem (RN-06). Fora da planta, `_local` já devolve `PASS_THROUGH` | Tratar o gesto em cada ferramenta; deixar o Editor de Imagem tratar o gesto | 🟢 |
| D-05 | A roda passa a ler `context.preferences.inputs.invert_zoom_wheel` e usa `gestures.wheel_factor(up, inverted)`. O Ctrl continua ignorado na roda, então Ctrl + roda = roda (RN-04) | `docs/rag/blender-api/corpus/bpy.types.PreferencesInput.md#bpy.types.PreferencesInput.invert_zoom_wheel`; esclarecimento Q2 | Criar uma preferência própria do add-on, que duplicaria a do Blender | 🟢 |
| D-06 | `modal` pula `_update_snap` quando o evento é de navegação (`TRACKPADZOOM`, `TRACKPADPAN`, `WHEELUPMOUSE`, `WHEELDOWNMOUSE`, `MIDDLEMOUSE` e o `MOUSEMOVE` de um pan com o botão do meio). `s.cursor` continua atualizado | O touchpad manda dezenas de eventos por segundo, e o encaixe consulta o índice de inferência (RNF de desempenho, Princípio IX). `s.checkpoint()` não grava nada, porque compara a assinatura do rascunho (`walls2d/history.py#checkpoint`) | Limitar a taxa por timer, que é mais estado e dá atraso visível | 🟢 |
| D-07 | **Barra superior em GPU**, desenhada em `draw_plan` (`POST_PIXEL`) sobre a planta, na largura visível (`window.visible_width`). Altura `TOOLBAR_HEIGHT = 32 px × ui_scale`. Um botão: a lupa com quadrado, desenhada com o `outline`/`rect` de `canvas2d/draw.py` (círculo, cabo e quadrado em linhas), realçada com o modo ligado ou com o mouse em cima. Ao passar o mouse, aparece a dica "Zoom janela: marque um retângulo para enquadrar" | O cabeçalho do Editor de Imagem foi escondido de propósito (`canvas2d/window.py#prepare`: `show_region_header = False`), e reativá-lo traz View/Image/Open. A planta já tem botões em GPU (pergunta Sim/Não, `canvas2d/draw.button`) | Reativar o cabeçalho do Editor de Imagem (contraria o Princípio I e o `prepare`); uma classe `Header` na região `TOOL_HEADER` (presa à ferramenta ativa do Editor de Imagem, sem precedente no projeto); botão só no painel lateral (o titular pediu barra superior) | 🟡 |
| D-08 | `_region_rect` desconta a altura da barra: a vista da planta ocupa a região menos a barra. Assim Home, "Enquadrar" e o zoom janela não escondem paredes atrás da barra | Sem isso, o enquadrar centraliza parte do desenho atrás da barra | Barra por cima do desenho, sem desconto | 🟡 |
| D-09 | Estado transitório na `Session` (`walls2d/props.py`): `zoom_window` (`None`, `'ARMED'` ou o pixel de início do retângulo) e `zoom_box_end`. Nada vai para `BTM_PG_WallEditorState.tool` nem para o histórico | A ferramenta do painel não muda, então a anterior "volta" sozinha. O desfazer só assina o rascunho (`history._sign(plan)`) | Item novo no enum `tool`, que apareceria na lista do painel e exigiria guardar e restaurar a ferramenta anterior | 🟢 |
| D-10 | Ordem no `modal`/`_handle`: (1) clique na barra; (2) com o modo zoom janela ligado: Esc ou clique na lupa cancela; LEFTMOUSE PRESS na planta inicia o retângulo; MOUSEMOVE atualiza; RELEASE → `gestures.zoom_window_bounds` → `view.fit(bounds, margin=0)` se não for `None`, e depois desliga o modo; (3) navegação (D-04, D-05); (4) pergunta, ferramentas, Esc de descarte, como hoje. Com o modo ligado, nenhum outro clique ou tecla chega às ferramentas, exceto navegação e Ctrl+Z | Garante RN-07: Esc cancela só o modo, não a digitação nem o desenho; o zoom janela não cria, não seleciona e não altera paredes | Tratar o zoom janela como mais uma ferramenta dentro de `_handle_click` | 🟡 |
| D-11 | Textos novos (dica da lupa) entram no catálogo de tradução com pt_BR e en_US | `tests/test_i18n_coverage.py`: área nova entra traduzida | n/a | 🟢 |
| D-12 | Testes: `tests/test_canvas2d_gestures.py` (puro: sentido, proporcionalidade, ida e volta ≤ 0,1%, delta zero, âncora parada ≤ 1 px, retângulo < 5 px, enquadrar centrado ± 2 px); `tests/blender_013_touchpad_smoke.py` (`--background`: chama `modal` com eventos falsos e confere escala, texto digitado, pergunta aberta e passos do desfazer); `tests/blender_013_trackpad_probe.py` (D-02, com janela); regressão das fumaças 002 e 009 do editor de parede | RF-08; Princípio VII | Testar só à mão no notebook | 🟢 |

## 4. Premissas

| Premissa | Origem (`requirements.md` seção) | Risco se errada |
|----------|----------------------------------|-----------------|
| O delta da pinça e do arraste chega em `mouse_x − mouse_prev_x` e `mouse_y − mouse_prev_y`, num eixo e sinal que a prova fixa | §6, RNF de compatibilidade | Médio: só muda `compat.trackpad_delta` e a constante de sensibilidade. A prova vem antes do núcleo |
| No Linux, o Blender só gera `TRACKPADZOOM` no Wayland. No X11, a pinça chega como Ctrl + roda, que já é coberto (RN-04) | §1, RN-04 | Baixo: os dois caminhos estão cobertos |
| "Lupa com quadrado" é zoom janela (marcar um retângulo e enquadrá-lo) | §9, sessão 2026-10-10 | Médio: se for "enquadrar tudo", RN-07 e D-09/D-10 encolhem para um botão que chama `caffmob.wall_editor_fit` |

Nenhum `[DÚVIDA]` aberto no requirements.

## 5. Delta arquitetural

| Componente | Arquivo de origem no legado | Tipo de mudança | Resumo |
|------------|------------------------------|-----------------|--------|
| Núcleo de gestos (puro) | `caffmob_draw/canvas2d/gestures.py` (novo) | componente-novo | Fator da pinça, fator da roda com inversão, retângulo do zoom janela |
| Compatibilidade | `caffmob_draw/compat.py` | contrato-novo | `trackpad_delta(event)` |
| Modal do Editor de Paredes | `caffmob_draw/walls2d/ops_editor.py#BTM_OT_WallEditorModal` | regra-alterada | Despacha `TRACKPADZOOM`/`TRACKPADPAN`, roda com inversão, barra e modo zoom janela; pula o encaixe em eventos de navegação |
| Desenho da planta | `caffmob_draw/walls2d/ops_editor.py#draw_plan`, `_region_rect` | regra-alterada | Desenha a barra, a lupa, a dica e o retângulo elástico; a vista desconta a barra |
| Sessão do editor | `caffmob_draw/walls2d/props.py#Session` | regra-alterada | Campos transitórios `zoom_window` e `zoom_box_end` |
| Catálogo de tradução | `caffmob_draw/data/translations/` | regra-alterada | Dica da lupa em pt_BR e en_US |

Fica para outra feature: o editor de armário (`caffmob_draw/cabinet_editor/ops_editor.py`, l. 435-438) também só dá
zoom pela roda. Ele pode reusar `gestures.py` e `compat.trackpad_delta` (RF-09).

## 6. Delta no modelo de dados

- Resumo das mudanças: nada persistido. Dois campos transitórios na `Session` (memória, morrem ao fechar o editor) e a
  leitura de uma preferência existente do Blender.
- Detalhe completo em: `_reversa_forward/013-touchpad-editor-parede/data-delta.md`

## 7. Delta de contratos externos

n/a: nenhum contrato externo (HTTP, fila, arquivo). O único encaixe novo é interno: `compat.trackpad_delta(event)`.

## 8. Plano de migração

n/a: nada persistido muda, e nenhum arquivo `.blend` precisa de migração.

## 9. Riscos e mitigações

| Risco | Impacto | Probabilidade | Mitigação |
|-------|---------|---------------|-----------|
| `Window.event_simulate` não reproduz o delta do gesto | médio | médio | Prova manual num notebook (D-02); a fumaça usa eventos falsos chamando `modal` direto |
| Sensibilidade da pinça diferente entre macOS, Wayland e Windows (unidades do delta) | médio | médio | Constante `PINCH_SENSITIVITY` num lugar só, calibrada na prova; o teste puro garante sentido e simetria, não a velocidade |
| A barra rouba cliques de quem desenha perto da borda de cima | baixo | médio | A vista desconta a barra (D-08), e a barra é baixa (32 px) |
| O zoom janela intercepta Esc e esconde a pergunta de descarte | médio | baixo | Ordem fixa (D-10) e cenário Gherkin "Cancelar o zoom janela"; Esc fora do modo segue igual |
| Eventos de touchpad chegam com o mouse sobre o painel lateral | baixo | baixo | `_local` já devolve `PASS_THROUGH` sobre o painel (RN-06) |

## 10. Critério de pronto

- [ ] Todas as ações do `actions.md` marcadas `[X]`
- [ ] Prova D-02 registrada em `investigation.md` (eixo, sinal, unidade)
- [ ] `tests/test_canvas2d_gestures.py` e `tests/test_canvas2d_view.py` passam
- [ ] `tests/blender_013_touchpad_smoke.py` e as fumaças 002 e 009 do editor de parede passam
- [ ] `ruff check caffmob_draw/` e `python3 docs/rag/tools/check_api.py` sem erro; `tests/test_i18n_coverage.py` passa
- [ ] Teste à mão num notebook com touchpad (`onboarding.md`)
- [ ] `cross-check.md` (se executado) sem CRITICAL nem HIGH
- [ ] `regression-watch.md` gerado

## 11. Histórico de alterações

| Data | Alteração | Autor |
|------|-----------|-------|
| 2026-10-10 | Versão inicial gerada por `/reversa-plan` | reversa |
