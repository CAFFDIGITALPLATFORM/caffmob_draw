# Fluxograma: `rules.conflicts` (collision)

Pares candidatos, exclusões (RN-12), encostar não é colisão (RN-11) e ordem estável (RN-13).

```mermaid
flowchart TD
    A[conflicts items confirm only] --> B[candidate_pairs]
    B --> C[AABB de cada item; ordena por x_min e nome]
    C --> D[Para A em ordem; para B seguinte]
    D --> E{x_min B > x_max A + TOLERANCE?}
    E -- sim --> D
    E -- não --> F{only dado e nenhum dos dois em only?}
    F -- sim --> D
    F -- não --> G{excluded A B ou AABBs não se tocam com margem?}
    G -- sim --> D
    G -- não --> H[par candidato]
    H --> I[evaluate A B: obb.overlap]
    I --> J{None ou depth ≤ 1 mm?}
    J -- sim --> D
    J -- não --> K{A estático e B não, ou iguais e nome B < nome A?}
    K -- sim --> L[troca A e B; push = −push]
    K -- não --> M
    L --> M[kind: parede ou obstáculo → WALL; piso ou teto → FLOOR_CEILING; senão ITEM]
    M --> N{confirm dado e confirm A B falso?}
    N -- sim --> D
    N -- não --> O[Conflict kind A B depth push location = média dos centros]
    O --> D
    D -- fim --> P[sort: ordem do tipo, −depth arredondado 6 casas, nome A, nome B]
```

```mermaid
flowchart TD
    X[excluded a b] --> X1{ambos estáticos?}
    X1 -- sim --> T[True]
    X1 -- não --> X2{override OFF em um dos dois?}
    X2 -- sim --> T
    X2 -- não --> X3{mesmo group = root ou name?}
    X3 -- sim --> T
    X3 -- não --> X4{nome ou group de um está em linked do outro?}
    X4 -- sim --> T
    X4 -- não --> F[False]
```

A varredura em X evita o produto cartesiano: cada A só compara com os B cuja faixa em X ainda alcança a dele. Um par
gera uma única ocorrência; `name_a` é sempre o item que pode ser movido.
