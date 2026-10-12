# Fluxograma: `View2D.zoom` e `gestures` (canvas2d)

Zoom ancorado e os três caminhos que o alimentam (roda, pinça, zoom janela). Re-extração 2026-10.

```mermaid
flowchart TD
    A{Origem} -- roda --> B[wheel_factor up, invert_zoom_wheel]
    A -- TRACKPADZOOM --> C[compat.pinch_delta: -(dx+dy)]
    C --> D[pinch_factor = exp delta/150]
    A -- lupa com quadrado --> E[zoom_window_bounds view p0 p1]
    E --> F{Lado >= 5 px?}
    F -- não --> G[Nada muda]
    F -- sim --> H[View2D.fit bounds margin 0]
    B --> I[View2D.zoom factor anchor]
    D --> I
    I --> J[before = to_world anchor]
    J --> K[scale = max 1e-6, scale * factor]
    K --> L[after = to_world anchor]
    L --> M[center += before - after]
    H --> N[scale = min w/w_mundo, h/h_mundo; center = centro dos bounds]
```

Propriedades garantidas (testes `tests/test_canvas2d_view.py`, `tests/test_canvas2d_gestures.py`):
- o ponto sob a âncora não se move (erro ≤ 1 px);
- `pinch_factor(d) · pinch_factor(−d) = 1` (ida e volta exatas);
- `pinch_factor(0) = 1`.
