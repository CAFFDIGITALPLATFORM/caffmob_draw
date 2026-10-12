# Investigation: Zoom e navegação por touchpad no editor de parede

> Identificador: `013-touchpad-editor-parede`
> Data: `2026-10-10`

## 1. O que o código faz hoje

- `caffmob_draw/walls2d/ops_editor.py#BTM_OT_WallEditorModal.modal` (l. 441-477):
  1. trata timer e Ctrl+Z;
  2. resolve a região e o pixel (`_local`); sobre o painel lateral ou fora da planta, `PASS_THROUGH`;
  3. atualiza `s.cursor` e o encaixe (`_update_snap`) em **todo** evento;
  4. chama `_handle`; o que não é tratado volta como `PASS_THROUGH`.
- `_handle` (l. 510-553) trata a navegação antes de tudo: `MIDDLEMOUSE` (pan), `WHEELUPMOUSE`/`WHEELDOWNMOUSE` (zoom
  de 1,15, ancorado, sem olhar Ctrl nem preferência) e `HOME` (enquadrar). Só depois vêm a pergunta, as ferramentas e
  o Esc.
- `TRACKPADZOOM`/`TRACKPADPAN` não são tratados, então voltam como `PASS_THROUGH` para o Editor de Imagem, onde a
  planta é desenhada (`walls2d/window.py#register`, `SpaceImageEditor.draw_handler_add`). O Editor de Imagem usa o
  gesto no próprio zoom, que não aparece, porque não há imagem.
- `canvas2d/window.py#prepare` esconde o cabeçalho, os menus, a barra de ferramentas e o cabeçalho de ferramenta do
  Editor de Imagem. A planta não tem barra superior.
- `View2D` (`canvas2d/view.py`) já tem `zoom(factor, anchor)`, `pan(dx, dy)` e `fit(bounds, margin)`. O piso de escala é
  `1e-6`.
- `Session.checkpoint` só grava passo se a assinatura do rascunho mudar (`walls2d/history.py#checkpoint`), então
  navegar não gera passo de desfazer.

## 2. API do Blender 5.2 (corpus)

| Símbolo | Uso | Fonte |
|---------|-----|-------|
| `TRACKPADPAN`, `TRACKPADZOOM` | Tipos de evento "Mouse/Trackpad Pan/Zoom" | `docs/rag/blender-api/corpus/bpy_types_enum_items/event_type_items.md` |
| `Event.mouse_x`, `mouse_y`, `mouse_prev_x`, `mouse_prev_y` | Posição atual e anterior; base do delta | `docs/rag/blender-api/corpus/bpy.types.Event.md#bpy.types.Event.mouse_prev_x` |
| `Event.ctrl` | Ctrl + roda | `docs/rag/blender-api/corpus/bpy.types.Event.md#bpy.types.Event.ctrl` |
| `PreferencesInput.invert_zoom_wheel` | Inverter o zoom da roda | `docs/rag/blender-api/corpus/bpy.types.PreferencesInput.md#bpy.types.PreferencesInput.invert_zoom_wheel` |
| `Window.event_simulate` | Prova e teste com eventos simulados (já usado em `tests/blender_002_ui_events.py`) | `docs/rag/blender-api/corpus/bpy.types.Window.md` |

**Lacuna do corpus:** ele não diz como o delta do gesto é codificado (eixo da pinça, sinal, unidade). Pelo
comportamento conhecido do Blender, o delta vai em `posição − posição anterior`, mas isso é 🟡 até a prova (D-02).

## 3. Plataformas

| Sistema | Pinça | Arraste com dois dedos |
|---------|-------|------------------------|
| macOS | `TRACKPADZOOM` | `TRACKPADPAN` |
| Linux Wayland | `TRACKPADZOOM` (gestos de ponteiro do compositor) 🟡 | `TRACKPADPAN` 🟡 |
| Linux X11 | Em geral Ctrl + roda (o driver converte) 🟡 | Em geral roda vertical/horizontal 🟡 |
| Windows (touchpad de precisão) | Em geral Ctrl + roda 🟡 | `TRACKPADPAN` ou roda, conforme o driver 🟡 |

Consequência: Ctrl + roda (RN-04) é o caminho principal fora do macOS e do Wayland, e já funciona hoje.

## 4. Alternativas avaliadas

### Fator de zoom da pinça
- **Exponencial** `exp(delta × k)` (escolhida): simétrica (`f(d)·f(−d) = 1`), nunca zera a escala, proporcional ao
  gesto e independente da escala de partida.
- Linear `1 + delta × k`: não é simétrica e pode dar fator ≤ 0 com delta grande.
- Passo fixo de 15% por evento: dá degraus e velocidade presa à taxa de eventos do driver.

### Barra superior
- **GPU no `POST_PIXEL`** (escolhida): mesmo caminho da pergunta Sim/Não e do diálogo do "Mover Sobre"
  (`canvas2d/draw.button`). Controle total do que aparece.
- Cabeçalho do Editor de Imagem: traz View/Image/Open, que o `prepare` esconde de propósito.
- Classe `Header` na região `TOOL_HEADER`: presa à ferramenta ativa do Editor de Imagem, sem precedente no projeto e
  difícil de testar.
- Ícones nativos do Blender (`ZOOM_SELECTED`, `ZOOM_ALL`) não têm desenho público no GPU. A lupa é desenhada com
  linhas.

### Estado do zoom janela
- **Campo transitório na `Session`** (escolhido): a ferramenta do painel não muda e fica fora do desfazer.
- Item no enum `tool`: apareceria na lista do painel e exigiria guardar e restaurar a ferramenta anterior.

## 5. Padrões do projeto aplicáveis

- `docs/rag/project/02_padroes_blender_5_2.md`: modal + GPU (`draw_handler_add` POST_PIXEL já registrado pelo
  editor; nada novo a registrar).
- `docs/rag/project/04_armadilhas.md`: o modal não guarda referência a `bpy` entre eventos; o estado novo fica na
  `Session` (Python puro).
- Precedente de teste com eventos simulados: `tests/blender_002_ui_events.py`, `tests/blender_011_drag_probe.py`.

## 6. Resultado da prova D-02

Rodada em 2026-10-10 com `/opt/blender/blender 5.2.0 LTS --factory-startup --enable-event-simulate --python
tests/blender_013_trackpad_probe.py`, numa sessão Linux Wayland, com o Editor de Paredes aberto de verdade.

| Gesto simulado | Evento recebido pelo modal | `mouse_x/y` | `mouse_prev_x/y` | `(dx, dy)` | Escala antes → depois |
|----------------|----------------------------|-------------|------------------|------------|-----------------------|
| zoom x+40 | `TRACKPADZOOM`, value `NOTHING` | (488, 294) | (448, 294) | (40, 0) | 105,0 → 105,0 |
| zoom x−40 | `TRACKPADZOOM` | (408, 294) | (448, 294) | (−40, 0) | 105,0 → 105,0 |
| zoom y+40 | `TRACKPADZOOM` | (448, 334) | (448, 294) | (0, 40) | 105,0 → 105,0 |
| pan x+60 | `TRACKPADPAN`, value `NOTHING` | (508, 294) | (448, 294) | (60, 0) | 105,0 → 105,0 |
| pan y+60 | `TRACKPADPAN` | (448, 354) | (448, 294) | (0, 60) | 105,0 → 105,0 |
| roda para cima | `WHEELUPMOUSE`, `PRESS` | (448, 294) | (448, 294) | (0, 0) | 105,0 → 120,75 |
| Ctrl + roda para cima | `WHEELUPMOUSE`, `PRESS`, `ctrl=True` | (448, 294) | (448, 294) | (0, 0) | 120,75 → 138,86 |

**Fixado pela prova (🟢):**
- O modal recebe `TRACKPADZOOM` e `TRACKPADPAN` com `value = 'NOTHING'`; nenhum dos dois era tratado (escala igual).
- O delta do gesto vem no próprio evento: `(mouse_x − mouse_prev_x, mouse_y − mouse_prev_y)`, em pixels. É isso que
  `compat.trackpad_delta` lê.
- Ctrl + roda já dá zoom de 1,15 (RN-04 confirmada no código atual).

**Convenção adotada para o sinal (🟡, da fonte do Blender, `wm_event_system`, gesto Magnify):** o delta da pinça vem
no eixo X (macOS e Wayland), negado, de modo que **afastar os dedos = `mouse_prev_x > mouse_x`**. `compat.pinch_delta`
devolve `−(dx + dy)`: positivo aproxima. Somar os dois eixos cobre uma plataforma que use o Y.

**Unidade e sensibilidade:** a simulação não diz o tamanho típico do delta de uma pinça real. `PINCH_SENSITIVITY =
1/150` (fator *e* ≈ 2,7 por 150 px de delta acumulado) é o valor de partida.

**Pendência para a prova à mão (T010):** num notebook com touchpad, rodar
`CAFFMOB_PROBE_MANUAL=1 /opt/blender/blender --factory-startup --enable-event-simulate --python
tests/blender_013_trackpad_probe.py`, afastar os dedos sobre a planta e ler no console o sinal de `dxy` e a ordem de
grandeza por evento. Se afastar der `dx > 0`, troca-se o sinal em `compat.pinch_delta`; se o delta por evento for
muito maior ou menor que ~10 a 30, ajusta-se `PINCH_SENSITIVITY`.
