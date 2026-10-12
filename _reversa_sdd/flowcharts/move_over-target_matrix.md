# Fluxograma: `MoveOver._target_matrix`, `preview` e `set_gap` (move_over/scene.py)

Posição de A no mundo a partir de `delta` e `rotation` no referencial de B.

```mermaid
flowchart TD
    A[_target_matrix] --> B[local = origin_in_b + delta]
    B --> C{rotation ≠ 0?}
    C -- sim --> D[local = origin_after_rotation local, caixa não girada, rotation: gira a origem em torno do centro da base]
    C -- não --> E
    D --> E[loc = b_frame @ local]
    E --> F[rot = rotação de B]
    F --> G{rotation ≠ 0?}
    G -- sim --> H[rot = rot @ Rz rotation]
    G -- não --> I
    H --> I[LocRotScale loc, rot, a_scale]
    J[preview] --> K{B é parede, ou pai de B tem IS_WALL_BP?}
    K -- sim e A.parent ≠ parede --> L[A.parent = parede; matrix_parent_inverse = Identity]
    K -- não --> M
    L --> M[A.matrix_world = _target_matrix]
    N[restore] --> O[parent, matrix_parent_inverse e matrix_world originais]
```

```mermaid
flowchart TD
    A[set_gap axis value] --> B{axis}
    B -- 0 X --> C{centro de A ≥ centro de B?}
    C -- sim: A à direita --> D[dx = bx1 + value − ax0]
    C -- não: A à esquerda --> E[dx = bx0 − value − ax1]
    B -- 1 profundidade --> F[dy = by0 + value − ay0]
    B -- 2 altura --> G[dz = bz0 + value − az0]
    D --> H[delta += d; preview]
    E --> H
    F --> H
    G --> H
    I[set_world axis value] --> J[atual = b_frame @ xmin ymin zmin de box_a]
    J --> K[alvo = atual com alvo axis = value]
    K --> L[delta += b_frame_inv 3×3 @ alvo − atual; preview]
```

`box_a()` = caixa local de A posta em `origin_in_b + delta` e, com rotação, envolvida por `rotated_box` (caixa
alinhada da planta girada pelo centro da base, Z inalterado). `gaps()` e `world_min()` são só exibição: trocar
Relativa/Absoluta não move nada.
