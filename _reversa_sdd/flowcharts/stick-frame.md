# Fluxograma: `frame.choose_face`, `frame.params` / `shift` e `frame.out_of_face` (stick)

Núcleo puro do grudar (D-01, D-02, RN-05, RN-06, RN-08a).

```mermaid
flowchart TD
    A[choose_face host_box point normal] --> B{normal normalizável?}
    B -- não --> P[PLANE, None]
    B -- sim --> C[cos_tol = cos 1°]
    C --> D[Para cada uma das 6 faces]
    D --> E{n · eixo da face ≥ cos_tol?}
    E -- não --> D
    E -- sim --> F[plane = hi ou lo no eixo da face]
    F --> G{abs point eixo − plane ≤ 0,5 mm?}
    G -- sim --> BS[BOX_SIDE, face]
    G -- não --> D
    D -- fim --> P
```

```mermaid
flowchart TD
    A[box_frame host_box face] --> B[n sign ua va = limits.face_axes]
    B --> C[origem = 0 exceto origem n = hi n se sign > 0 senão lo n]
    C --> D[U = eixo ua; V = eixo va; N = eixo n × sign]
    E[plane_frame origin normal up] --> F[n = normal unitária]
    F --> G{abs up · n < 0,999?}
    G -- sim --> H[hint = up]
    G -- não --> I[hint = X]
    H --> J[U = hint − n · hint·n normalizado; V = n × U]
    I --> J
    K[params frame corners] --> L[to_frame de cada canto: u v n = d·U d·V d·N]
    L --> M[footprint = mín e máx em cada eixo]
    M --> N[u v distance = canto mínimo]
    O[shift frame corners u v distance] --> N
    N --> Q[delta = alvo − atual; None mantém]
    Q --> R[deslocamento local = U·du + V·dv + N·dd]
```

```mermaid
flowchart TD
    A[out_of_face frame corners extent] --> B{extent None PLANE?}
    B -- sim --> F[False]
    B -- não --> C[centro da pegada cu cv]
    C --> D{u0 − 1 mm ≤ cu ≤ u1 + 1 mm e v0 − 1 mm ≤ cv ≤ v1 + 1 mm?}
    D -- sim --> F
    D -- não --> T[True: aviso Item fora da face]
    I[is_planar points normal] --> J{todos abs p − p0 · n ≤ 0,5 mm?}
    J -- sim --> PT[True]
    J -- não --> PF[False: A face não é plana]
    CA[contact_axis normal] --> CB{abs n · Z ≥ 0,7?}
    CB -- sim --> BOT[BOTTOM: base do item encosta]
    CB -- não --> BK[BACK: fundo +Y do item encosta]
```

`u`/`v` partem da origem local do hospedeiro, que não se move ao redimensionar: um aéreo grudado atrás da parede
continua encostado quando a espessura muda (`distance` mantido, `box_frame` recalculado).
