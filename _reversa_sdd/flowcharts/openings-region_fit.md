# Fluxograma: `region_core.fit` (openings/region_core.py)

Encaixe da porta ou janela na região marcada (D-11, RN-11, RN-12).

```mermaid
flowchart TD
    A[fit x0 x1 z0 z1 wall_length wall_height kind others] --> B[Ordena: x0 ≤ x1, z0 ≤ z1]
    B --> C{−5 mm < z0 < 0?}
    C -- sim --> D[z0 = 0]
    C -- não --> E
    D --> E{largura ou altura < 1 mm?}
    E -- sim --> F[EMPTY]
    E -- não --> G{x0 < −5 mm, x1 > comprimento + 5 mm ou z0 < 0?}
    G -- sim --> H[OUTSIDE]
    G -- não --> I{z1 > altura da parede + 5 mm?}
    I -- sim --> J[TOO_TALL]
    I -- não --> K{kind WINDOW?}
    K -- sim --> L[sill = z0]
    K -- não --> M[sill = 0: porta vai do piso]
    L --> N[Para cada outra abertura ox0 ox1 oz0 oz1]
    M --> N
    N --> O{cruza em X e em Z com folga de 1 mm?}
    O -- sim --> P[OVERLAP]
    O -- não --> N
    N -- fim --> Q[Fit ok, x0, x1 − x0, z1 − sill, sill]
```

Largura e altura são exatamente as da região. Encostar (borda a borda) ou ficar acima de outra abertura não bloqueia.
