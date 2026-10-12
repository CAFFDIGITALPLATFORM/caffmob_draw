# Fluxograma: `link.stick`, `link.oriented_matrix` e `magnet.find` (stick)

Grudar numa face (D-03, D-05, RN-05) e ímã (D-06, RN-10a).

```mermaid
flowchart TD
    A[stick item hit_obj point normal polygon center rotate] --> B[host = host_for hit_obj: raiz classificada ou o próprio]
    B --> C{can_stick: sem item, sem host, host é o item ou filho, item é agregado?}
    C -- motivo --> X[ValueError motivo]
    C -- ok --> D{polygon dado e não is_planar no espaço do host?}
    D -- sim --> X2[ValueError A face não é plana]
    D -- não --> E{rotate?}
    E -- sim --> F[orient: oriented_matrix]
    E -- não --> G
    F --> G[_attach: orig_parent na 1ª vez; parent = host; inversa = I; basis = host⁻¹ · world]
    G --> H[p n = ponto e normal no espaço do host]
    H --> I[choose_face host_box p n]
    I -- BOX_SIDE --> J[fr = box_frame; plane = IDENTITY]
    I -- PLANE --> K[fr = plane_frame p n; plane = frame_to_matrix]
    J --> L[u v = params fr item_corners]
    K --> L
    L --> M{center?}
    M -- sim --> N[u v = ponto clicado − metade da pegada]
    M -- não --> O
    N --> O[_record: host kind face plane u v distance 0 spin 0 is_stuck; invalidate]
    O --> P[update_position: encosta] --> Q[host, face]
```

```mermaid
flowchart TD
    A[oriented_matrix world normal] --> B[n unitária; loc rot scale = decompose]
    B --> C{contact_axis n}
    C -- BACK face de pé --> D[y = −n; z = Z mundo projetado no plano, ou Z atual; x = y × z]
    C -- BOTTOM face deitada --> E[z = n ou −n apontando para cima; y = Y atual projetado, ou X × z; x = y × z]
    D --> F[basis = colunas x y z]
    E --> F
    F --> G[LocRotScale loc basis scale]
```

```mermaid
flowchart TD
    A[find item distance] --> B[origem = centro do fundo +Y da caixa local no mundo; dir = +Y do item]
    B --> C[start = origem − dir · 1 mm; até 8 passos]
    C --> D[scene.ray_cast start dir distance + 2 mm]
    D --> E{acertou?}
    E -- não --> N[None]
    E -- sim --> F{próprio item, filho, cortador ou anotação?}
    F -- sim --> G[start = acerto + 0,1 mm] --> D
    F -- não --> H{além da distância ou normal · dir > −0,7?}
    H -- sim --> N
    H -- não --> I{host_for é piso ou teto?}
    I -- sim --> N
    I -- não --> R[obj, ponto, normal, vértices do polígono]
```

`try_stick` chama `stick(center=False, rotate=True)`: o item gira para a face e encosta onde o raio bateu.
`preview_pose` reproduz a mesma orientação e o mesmo encosto só em cantos, sem tocar no objeto (prévia da 005).
