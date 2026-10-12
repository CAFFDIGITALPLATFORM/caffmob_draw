# Onboarding: testar o zoom por touchpad no editor de parede

> Identificador: `013-touchpad-editor-parede`
> Data: `2026-10-10`

## 1. Preparar

1. `python3 build.py` e instalar `caffmob_draw.zip` (Edit → Preferences → Get Extensions → Install from Disk), ou
   rodar a partir do repositório.
2. Num notebook com touchpad. No Linux, anote se a sessão é Wayland ou X11 (`echo $XDG_SESSION_TYPE`).
3. Crie uma sala de quatro paredes (3.900 × 2.700 mm) e abra o Editor de Paredes ("Editar Paredes…" no botão direito
   de uma parede).

## 2. Roteiro

| # | Faça | Espere |
|---|------|--------|
| 1 | Ponha o cursor sobre um canto e afaste dois dedos | A planta aproxima, e o canto fica sob o cursor |
| 2 | Junte os dois dedos | A planta afasta, e o canto continua sob o cursor |
| 3 | Afaste e junte na mesma medida | Volta ao tamanho de antes |
| 4 | Arraste dois dedos para a direita | A planta anda junto com os dedos; o tamanho não muda |
| 5 | (X11/Windows) Faça a pinça | Zoom do mesmo jeito (chega como Ctrl + roda) |
| 6 | Escolha "Construir Parede", comece um trecho, digite `2.4` e faça a pinça | Zoom muda; `2.4` continua digitado; o trecho continua em curso |
| 7 | Feche o contorno até aparecer "Fechar o contorno?" e faça a pinça | Zoom muda; a pergunta continua aberta |
| 8 | Faça a pinça com o cursor sobre o painel lateral | A planta não muda |
| 9 | Aperte a lupa na barra superior | A lupa fica realçada; ao passar o mouse aparece a dica |
| 10 | Marque um retângulo em volta de um canto e solte | O canto enche a planta, centrado; a lupa volta ao normal; nenhuma parede mudou nem foi selecionada |
| 11 | Aperte a lupa e tecle Esc | O modo desliga; a vista não muda |
| 12 | Aperte a lupa e só clique (retângulo minúsculo) | A vista não muda |
| 13 | Ctrl+Z depois dos passos acima | Não desfaz nenhum zoom (só desenho) |
| 14 | Preferences → Navigation → Zoom → "Invert Zoom Wheel Direction" ligado; gire a roda para cima | A planta afasta; a pinça continua no sentido normal |
| 15 | Com mouse: botão do meio, roda e Home | Iguais a antes |

## 3. Testes automáticos

```bash
python3 -m pytest tests/test_canvas2d_gestures.py tests/test_canvas2d_view.py
blender --background --factory-startup --python-exit-code 1 --python tests/blender_013_touchpad_smoke.py
blender --factory-startup --enable-event-simulate --python tests/blender_013_trackpad_probe.py   # precisa de janela
ruff check caffmob_draw/ && python3 docs/rag/tools/check_api.py
```

## 4. Estado da prova (2026-10-10)

- Simulada (`tests/blender_013_trackpad_probe.py`, Linux Wayland, Blender 5.2.0): o modal recebe `TRACKPADZOOM` e
  `TRACKPADPAN` com o delta em `mouse_x − mouse_prev_x` / `mouse_y − mouse_prev_y`; Ctrl + roda dá zoom de 1,15.
- Sinal da pinça real: convenção do Blender (afastar os dedos = `mouse_prev_x > mouse_x`), **ainda sem confirmação à
  mão** (T010). `PINCH_SENSITIVITY = 1/150` é o valor de partida.
- Ficou sem teste à mão: pinça e arraste reais em macOS, Windows e X11 (passos 1 a 5 do roteiro).

Para a prova à mão, num notebook com touchpad:

```bash
CAFFMOB_PROBE_MANUAL=1 /opt/blender/blender --factory-startup --enable-event-simulate --python tests/blender_013_trackpad_probe.py
```

Afaste os dedos sobre a planta e leia `dxy` no console. Se vier `dx > 0`, troque o sinal em `compat.pinch_delta`; se o
delta por evento for muito maior ou menor que ~10 a 30, ajuste `PINCH_SENSITIVITY`. Esc no editor encerra.

## 5. Se algo der errado

- Zoom no sentido contrário ou arraste invertido: confira o resultado da prova em `investigation.md` §6 e o sinal em
  `compat.trackpad_delta`.
- Pinça sem efeito no Linux X11: confira se o driver manda Ctrl + roda (passo 5). Sem isso, o Blender não recebe a
  pinça.
