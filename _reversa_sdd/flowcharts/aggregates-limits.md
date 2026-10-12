# Fluxograma: `limits.clamp`, `box_for` e `apply.update_position` (aggregates)

Agregado preso a uma face do pai (RN-08, RN-09).

```mermaid
flowchart TD
    A[face_axes face] --> B[n = eixo da última letra; sign = +1 POS / −1 NEG; u v = os outros dois eixos]
    C[limits parent_box agg_size face] --> D[u ∈ 0 .. max 0, ps u − size u]
    D --> E[v ∈ 0 .. max 0, ps v − size v]
    E --> F[offset ∈ −ps n .. ∞]
    G[clamp] --> H[fit de u, v e offset nos intervalos]
    I[box_for parent_box agg_size face u v offset clamp_to_face] --> J{clamp_to_face?}
    J -- sim --> G
    J -- não --> K
    G --> K[lo u = lo_p u + u; lo v = lo_p v + v]
    K --> L{sign > 0?}
    L -- sim --> M[lo n = hi_p n + offset]
    L -- não --> N[lo n = lo_p n − offset − size n]
    M --> O[hi = lo + size]
    N --> O
```

```mermaid
flowchart TD
    A[update_position obj] --> B{is_aggregate, kind ≠ LEAF, parent_ref = parent Blender?}
    B -- não --> C[None]
    B -- sim --> D[box_p = local_box do pai avaliado]
    D --> E[u v offset = clamp]
    E --> F[Para cada campo que mudou > 1e-9: _write sem update]
    F --> G[lo = box_for.lo; target = lo − rest_offset]
    G --> H{location difere > 1e-9?}
    H -- sim --> I[location = target]
    H -- não --> J
    I --> J{sync_cut e perforate ou cutter?}
    J -- sim --> K[perforate.sync]
    J -- não --> L[devolve u v offset]
    K --> L
    M[depsgraph_update_post] --> N{_busy?}
    N -- não --> O[Para cada update de geometria de Object com agregados]
    O --> P{local_box igual à última vista?}
    P -- não --> Q[guarda; update_position em cada agregado]
```

`sunk_box` = interseção entre a caixa do pai e a do agregado (None se não afunda); `sunk_depth` mede no eixo da face.
O ramo `clamp_to_face=False` não tem chamador: a docstring de `box_for` diz que o grudar (feature 004) o usa, mas `stick/` não chama `box_for` (só `FACES`, `FACE_LABELS`, `face_axes`, `thickness`) _(Revisão cruzada 2026-10-10: único chamador é aggregates/apply.py:61)_.
