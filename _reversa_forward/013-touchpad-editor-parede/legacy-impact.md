# Legacy impact: 013-touchpad-editor-parede

> Gerado por `/reversa-coding` em 2026-10-10.
> Feature: zoom por pinça e arraste com dois dedos no Editor de Paredes, roda obedecendo à preferência "inverter
> zoom", barra superior com a lupa com quadrado (zoom janela).
> Âncora: `_reversa_sdd/architecture.md`, `_reversa_sdd/domain.md`, `_reversa_sdd/wall_editor/`; princípios
> `.reversa/principles.md`.

## Arquivos afetados

| Arquivo afetado | Componente | Tipo | Severidade | Justificativa |
|-----------------|------------|------|------------|---------------|
| `caffmob_draw/canvas2d/gestures.py` (novo) | Núcleo das telas 2D (`canvas2d`, feature 002) | componente-novo | LOW | Fator da pinça (exponencial), fator da roda com inversão, retângulo do zoom janela; Python puro |
| `caffmob_draw/compat.py` | Compatibilidade (`architecture.md`, camada de API) | regra-nova | LOW | `trackpad_delta(event)` e `pinch_delta(event)`: leitura do delta do gesto num lugar só |
| `caffmob_draw/walls2d/ops_editor.py` | Editor de Paredes 2D (`BTM_OT_WallEditorModal`, `draw_plan`) | regra-alterada | MEDIUM | `_handle` trata `TRACKPADZOOM`/`TRACKPADPAN`; a roda lê `invert_zoom_wheel`; `modal` pula o encaixe em eventos de navegação; barra superior e lupa em GPU; `handle_zoom_window`; a vista desconta a barra; a mira para na barra |
| `caffmob_draw/walls2d/props.py` | Sessão do Editor de Paredes | delta-de-dados | LOW | Campos transitórios `zoom_window` e `zoom_box_end` (memória, fora do histórico) |
| `caffmob_draw/data/translations/walls2d.json` | Catálogo de tradução | delta-de-dados | LOW | Dica da lupa em pt_BR e en_US |
| `tests/test_canvas2d_gestures.py`, `tests/blender_013_touchpad_smoke.py`, `tests/blender_013_trackpad_probe.py` (novos) | Testes | componente-novo | LOW | Teste puro, fumaça em segundo plano e prova com janela |

Nenhum arquivo do legado Home Builder (`operators/walls.py`, `hb_*.py`) foi tocado. Nenhum `bpy.props`, `.blend` ou
arquivo do usuário mudou. Nenhum contrato externo.

## Diff conceitual por componente

**Editor de Paredes 2D (`walls2d/ops_editor.py`).** A navegação continua tratada num ponto só, antes da caixa de
pergunta e das ferramentas, e ganhou dois eventos: a pinça (`TRACKPADZOOM`) vira `view.zoom(pinch_factor(delta),
cursor)` e o arraste com dois dedos (`TRACKPADPAN`) vira `view.pan(dx, dy)`. Os dois são consumidos
(`RUNNING_MODAL`), então não chegam ao Editor de Imagem por baixo da planta. A roda deixa de ter o 1,15 literal e passa
por `wheel_factor(up, invert_zoom_wheel)`; o Ctrl continua ignorado, logo Ctrl + roda = roda. `modal` não refaz o
encaixe da mira em evento de navegação. A planta ganhou uma barra superior desenhada em GPU (32 px × `ui_scale`) com um
botão, a lupa com quadrado: ligado, o próximo clique e arraste marcam um retângulo que `view.fit(bounds, margin=0)`
enquadra; Esc ou segundo clique cancelam só o modo; retângulo com lado < 5 px não muda a vista; com o modo ligado,
só navegação e Ctrl+Z chegam ao resto. O retângulo da vista desconta a barra, então Home e "Enquadrar" não deixam
paredes atrás dela.

**Sessão (`walls2d/props.py`).** Dois campos transitórios que a assinatura do histórico não lê: navegar e usar a lupa
não geram passo de desfazer.

**Núcleo 2D (`canvas2d/gestures.py`).** Conta pura e testada fora do Blender. A pinça é exponencial no delta: ida e
volta devolvem a escala, e o mesmo gesto dá o mesmo fator em qualquer escala.

**Compatibilidade (`compat.py`).** O delta do gesto vem em `mouse_x − mouse_prev_x` e `mouse_y − mouse_prev_y`
(confirmado pela prova D-02). O sinal de "afastar os dedos" segue a convenção do Blender e é o único ponto que a prova
à mão (T010) pode mudar.

## Preservadas

Regras 🟢 do `_reversa_sdd/domain.md` que continuam intactas:

- **R-01** (piso depende de parede), **R-02** (piso conformal) e **R-03** (sentido RIGHT/LEFT define o lado da
  espessura): a feature não toca paredes, piso nem o sentido; o rascunho do editor não muda com os gestos.
- **R-04 a R-08** (aberturas presas ao segmento, movimento constrangido, limites, transição entre segmentos, peitoril
  fixo): sem alteração; o editor de paredes não edita aberturas (002 RN-13).
- **R-09 e R-10** (plano de corte): fora do escopo.
- Regras do próprio Editor de Paredes (002): **RN-16**, edição em rascunho e nada muda no 3D até OK, preservada e
  reforçada: navegar e a lupa não entram no histórico; **RF-02**, navegação da planta, ampliada com os gestos e o zoom
  janela que ela já pedia.

## Modificadas

Nenhuma regra 🟢 do `_reversa_sdd/domain.md` foi alterada ou removida.

Comportamento alterado, sem regra 🟢 de origem: a roda do editor de paredes passa a obedecer à preferência do Blender
"inverter o zoom pela roda" (antes ignorava). Registrado em `regression-watch.md` como observação.
