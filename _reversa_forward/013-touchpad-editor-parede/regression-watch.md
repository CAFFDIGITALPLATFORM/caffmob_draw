# Regression watch: 013-touchpad-editor-parede

> Gerado por `/reversa-coding` em 2026-10-10. Fonte: `legacy-impact.md` (seção "Modificadas": nenhuma regra 🟢 do
> `_reversa_sdd/domain.md` alterada ou removida).

| ID | Origem (arquivo, seção) | Regra esperada após mudança | Tipo de verificação | Sinal de violação |
|----|--------------------------|------------------------------|---------------------|-------------------|

Nenhum item com peso de regressão nesta rodada.

## Observações

Comportamentos novos ou alterados que não vinham como regra 🟢 do legado:

- **Pinça e arraste com dois dedos na planta** (`walls2d/ops_editor.py#_handle`): `TRACKPADZOOM` dá zoom ancorado no
  cursor e `TRACKPADPAN` move a vista, em qualquer ferramenta e estado, consumidos pelo modal. Uma re-extração que
  volte a ver esses eventos passando direto ao Editor de Imagem é regressão. 🟢
- **Roda obedece a `invert_zoom_wheel`** e Ctrl + roda = roda (`gestures.wheel_factor`). Antes o editor ignorava a
  preferência. 🟢
- **Navegar não refaz o encaixe nem grava passo de desfazer** (`modal._is_navigation`, `history._sign` só do
  rascunho). 🟢
- **Barra superior com a lupa com quadrado** (`_draw_toolbar`, `handle_zoom_window`): marcar um retângulo enquadra;
  Esc ou segundo clique cancela só o modo; lado < 5 px não muda a vista; a vista desconta a barra. 🟢
- **Sinal da pinça** (`compat.pinch_delta`): afastar os dedos = `mouse_prev_x > mouse_x`, convenção do Blender ainda
  sem prova à mão (T010). Se a prova inverter o sinal, só `compat.py` muda. 🟡
- **Sensibilidade** `PINCH_SENSITIVITY = 1/150`: valor de partida, a calibrar na prova à mão. 🟡

## Histórico de re-extrações

### Re-extração 2026-10-10 18:26

| ID | Veredito | Observação |
|----|----------|------------|
| — | — | nenhum watch item na tabela principal; nada a verificar |

## Arquivadas
