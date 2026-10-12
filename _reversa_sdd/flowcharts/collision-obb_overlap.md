# Fluxograma: `obb.overlap` (collision)

Teste dos eixos separadores (SAT) entre duas caixas orientadas; devolve a menor sobreposição e o empurrão que a desfaz (D-12, D-19).

```mermaid
flowchart TD
    A[overlap a b] --> B[t = centro B − centro A]
    B --> C[eixos = 3 de A + 3 de B + 9 produtos vetoriais A_i × B_j]
    C --> D[Para cada eixo, índice 0..14]
    D --> E{comprimento < 1e-6?}
    E -- sim --> D
    E -- não --> F[normaliza; dist = t · eixo]
    F --> G[amount = raio A + raio B − abs dist; raio = Σ half_i · abs axes_i · eixo]
    G --> H{amount < −1e-9?}
    H -- sim --> N[return None: eixo separa as caixas]
    H -- não --> I{best vazio ou amount < best − 1e-9?}
    I -- sim --> J[sign = −1 se dist > 0 senão +1; best = amount, eixo × sign × amount, índice]
    I -- não --> D
    J --> D
    D -- fim --> K{best vazio?}
    K -- sim --> N
    K -- não --> R[return depth, push, axis]
```

```mermaid
flowchart LR
    FB[from_box origin axes lo hi] --> M[mid = lo + hi / 2]
    M --> CTR[center = origin + Σ axes_i · mid_i]
    CTR --> HALF[half = abs hi − lo / 2]
    HALF --> OBB[OBB center axes half]
    OBB --> AABB[aabb: ext_k = Σ abs axes_i_k · half_i]
```

`push` aponta de B para fora de A pelo eixo de menor sobreposição: é o deslocamento que "Afastar até encostar" aplica
a `name_a`. `axis` 0–2 = face de A, 3–5 = face de B, 6–14 = aresta × aresta.
