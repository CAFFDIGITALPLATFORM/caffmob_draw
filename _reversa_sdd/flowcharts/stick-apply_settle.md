# Fluxograma: `apply.on_depsgraph_update`, `_settle_timer` e `settle.run` (stick)

Manter o item na face sem brigar com o arraste do usuário (D-04, D-06, D-16, RF-12, RF-13, RF-19, RF-23).

```mermaid
flowchart TD
    A[on_depsgraph_update] --> B{_busy?}
    B -- sim --> Z[return]
    B -- não --> C[idx = index hospedeiro → grudados]
    C --> D[Para cada update de Object]
    D --> E{geometria e nome em idx?}
    E -- sim --> F{host_box ≠ _last_box?}
    F -- sim --> G[guarda; update_position em cada grudado]
    E -- não --> H
    F -- não --> H
    G --> H{transformação e fora do período quieto?}
    H -- sim --> I[_pending.add nome]
    H -- não --> D
    I --> D
    D -- fim --> J[Para grudados com host None: lose_link]
    J --> K{_pending e timer não registrado?}
    K -- sim --> L[timers.register _settle_timer 0,2 s]
    K -- não --> Z
```

```mermaid
flowchart TD
    A[_settle_timer] --> B{modal_running: transform.*, _MOVE_IDS ou PlacementMixin?}
    B -- sim --> W[repete em 0,2 s]
    B -- não --> C[names = _pending; limpa; _busy]
    C --> D[settle.run names]
    D --> E[Para cada nome vivo]
    E --> F{returned_to_rest: mesma pose de _settled?}
    F -- sim --> E
    F -- não --> G{apply.linked?}
    G -- sim --> H[apply.project: flip se atravessou; u v da pose solta; update_position] --> MR[moved_roots]
    G -- não --> I{is_stuck com vínculo quebrado?}
    I -- sim --> E
    I -- não --> J{classify: MODULE ou GEOMETRY e raiz?}
    J -- não --> E
    J -- sim --> K{migrate.wall_of: pai é parede?}
    K -- sim --> L[link_in_place na face wall_side] --> MR
    K -- não --> M{magnet.try_stick grudou?}
    M -- sim --> N[stuck_now] --> MR
    M -- não --> MR
    MR --> E
    E -- fim --> O[_settled nome = pose]
    O --> P{stuck_now?}
    P -- sim --> Q[toast Elemento filho de: …; ed.undo_push Grudar]
    P -- não --> R
    Q --> R{moved_roots?}
    R -- sim --> S[collision.scan.check_moved]
    S --> T[return None: timer encerra]
    R -- não --> T
```

```mermaid
flowchart TD
    A[_flip_if_across item] --> B{face_kind BOX_SIDE?}
    B -- não --> F[False]
    B -- sim --> C[d = distance pela face atual; thickness = espessura no eixo]
    C --> D{d ≥ −thickness − 1 mm?}
    D -- sim --> F
    D -- não --> E[d_other = distance pela face oposta]
    E --> G{d_other < −1 mm?}
    G -- sim --> F
    G -- não --> H[face = oposta; distance = d_other; True]
```

`on_load_or_undo` (`load_post`, `undo_post`, `redo_post`) abre um período quieto de 0,6 s em que transformações não
contam como gesto, e limpa índice, `_last_box` e pendentes.
