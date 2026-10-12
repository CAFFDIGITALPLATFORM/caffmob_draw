# Fluxograma: `Chain.outer_line` e `shifted_nodes` (walls2d/model.py)

Face externa com esquadria e deslocamento da linha de centro.

```mermaid
flowchart TD
    A[outer_line i] --> B[sign = +1 se side LEFT, −1 se RIGHT]
    B --> C[Normal n = sign × (−sin d, cos d); t = espessura]
    C --> D[left, right = miter_angles i: metade da virada com cada vizinho]
    D --> E[s0 = sign·t·tan left; s1 = sign·t·tan right]
    E --> F[Ponta 0 = n0 + n·t + d·s0; Ponta 1 = n1 + n·t + d·s1]
    G[shifted_nodes factor] --> H[Para cada nó: soma normais × espessura × factor dos trechos que chegam e saem]
    H --> I{Dois trechos no nó?}
    I -- sim --> J[escala 1 / (2·cos² θ/2); 0,5 se cos ≈ 0]
    I -- não --> K[Nó + deslocamento]
    J --> K
```

`face_length(i, OUTER)` = interna + as esquadrias nos cantos; `set_length` na face externa itera até 12 vezes porque
mover o nó muda as esquadrias.
