"""Gestos de navegação das telas 2D (013; D-01). Python puro, sem `bpy`.

Converte o que chega do touchpad e da roda em fator de zoom e em retângulo de enquadramento para uma
`canvas2d.view.View2D`:
- `pinch_factor`: pinça com dois dedos (`TRACKPADZOOM`). O fator é exponencial no tamanho do gesto, então uma pinça
  de ida seguida da mesma pinça de volta devolve a escala inicial, e a mesma pinça dá o mesmo resultado em qualquer
  escala de partida. Delta zero dá fator 1.
- `wheel_factor`: roda do mouse, com ou sem a preferência "inverter zoom pela roda" do Blender (D-05).
- `zoom_window_bounds`: retângulo marcado na tela para a lupa com quadrado (RN-07); retângulo pequeno demais é `None`.

A leitura do delta no evento do Blender fica em `compat.trackpad_delta` (D-03). A sensibilidade abaixo é a calibrada
na prova D-02 (`_reversa_forward/013-touchpad-editor-parede/investigation.md` §6).
"""

import math

PINCH_SENSITIVITY = 1.0 / 150.0     # fator e por 150 unidades de delta; calibrado na prova D-02
WHEEL_STEP = 1.15                   # passo da roda, como antes da 013
ZOOM_WINDOW_MIN_PX = 5              # lado mínimo do retângulo da lupa (RN-07)


def pinch_factor(delta, sensitivity=PINCH_SENSITIVITY):
    """Fator de zoom de um evento de pinça: `delta` > 0 aproxima, < 0 afasta, 0 não muda nada."""
    return math.exp(float(delta) * sensitivity)


def wheel_factor(up, inverted=False):
    """Fator de um passo da roda: para cima aproxima, a não ser que a preferência de inverter esteja ligada."""
    return WHEEL_STEP if bool(up) != bool(inverted) else 1.0 / WHEEL_STEP


def zoom_window_bounds(view, p0_px, p1_px, min_px=ZOOM_WINDOW_MIN_PX):
    """Bounds do mundo ((xmin, ymin), (xmax, ymax)) do retângulo marcado entre dois pixels, ou `None` quando um dos
    lados tem menos de `min_px` (um clique sem arraste não muda a vista)."""
    if abs(p1_px[0] - p0_px[0]) < min_px or abs(p1_px[1] - p0_px[1]) < min_px:
        return None
    a, b = view.to_world(p0_px), view.to_world(p1_px)
    return ((min(a[0], b[0]), min(a[1], b[1])), (max(a[0], b[0]), max(a[1], b[1])))
