# Fluxograma: `cotas.limits`, `cotas.apply` e `cotas.slide` (measure/cotas.py)

Limites laterais por obstáculos na mesma faixa de altura e a cota digitada que move o módulo (RN-04, RF-34).

```mermaid
flowchart TD
    A[limits placement obstacles wall_length] --> B[left = 0; right = wall_length]
    B --> C[Para cada obstáculo ox0 ox1 oz0 oz1]
    C --> D{z0 < oz1 e oz0 < z1? sobreposição estrita}
    D -- não --> C
    D -- sim --> E{ox1 ≤ x0 + 1e-9?}
    E -- sim --> F[left = max left, ox1]
    E -- não --> G{ox0 ≥ x1 − 1e-9?}
    G -- sim --> H[right = min right, ox0]
    G -- não --> C
    F --> C
    H --> C
    C -- fim --> I[left, right]
```

```mermaid
flowchart TD
    A[apply field value] --> B{value < 0?}
    B -- sim --> C[ValueError não pode ser negativa]
    B -- não --> D{field}
    D -- afastamento --> E[back_y = −value]
    D -- inferior --> F[z0 = value]
    D -- superior --> G[z0 = ceiling − value − height]
    G --> H{z0 < 0?}
    H -- sim --> I[ValueError maior que o espaço até o piso]
    H -- não --> J[Placement nova]
    D -- anterior / posterior --> K[left right = limits]
    K --> L{anterior?}
    L -- sim --> M[x0 = left + value]
    L -- não --> N[x0 = right − value − width]
    M --> O{x0 < 0 ou x0 + width > wall_length + 1e-9?}
    N --> O
    O -- sim --> P[ValueError tira o módulo da parede]
    O -- não --> J
    D -- outro --> Q[ValueError Cota desconhecida]
    E --> J
    F --> J
```

```mermaid
flowchart TD
    A[slide placement obstacles wall_length target_x0 avoid] --> B{avoid?}
    B -- não --> C[x0 = clamp target, 0, max 0, wall_length − width]
    B -- sim --> D[left right = limits]
    D --> E[x0 = clamp target, left, max left, right − width]
```

As dimensões (`width`, `height`) nunca mudam: a cota só desloca `x0`, `z0` ou `back_y`. Obstáculos que cruzam o
módulo em X são ignorados pelos limites (o módulo já está sobreposto; nada o bloqueia).
