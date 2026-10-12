# Fluxograma: `classify.classify` e raízes do Mover Sobre (selection/classify.py)

Precedência RN-01: frente e peça antes do módulo, módulo antes da parede.

```mermaid
flowchart TD
    A[classify obj] --> B{obj None?}
    B -- sim --> C[None]
    B -- não --> D{IS_2D_ANNOTATION?}
    D -- sim --> E[ANNOTATION obj obj HB]
    D -- não --> F[root library = module_root: primeiro ancestral com MODULE_TAGS ou btm_kind MODULE]
    F --> G{root existe?}
    G -- sim --> H[Para cada ancestral abaixo da raiz]
    H --> I{_is_front: FRONT_TAGS, hb_part_role em FRONT_ROLES ou sufixo _Door_L/_R/_Flip?}
    I -- sim --> J[FRONT node root library]
    I -- não --> H
    H -- chegou à raiz --> K{obj is root?}
    K -- sim --> L[MODULE root root library]
    K -- não --> M[PART obj root library]
    G -- não --> N[Para cada ancestral, na ordem]
    N --> O{IS_ENTRY_DOOR_BP}
    O -- sim --> O1[ROOM_DOOR HB]
    O -- não --> P{IS_WINDOW_BP}
    P -- sim --> P1[WINDOW HB]
    P -- não --> Q{btm_kind OPENING}
    Q -- sim --> Q1[WINDOW BTM]
    Q -- não --> R{btm_kind GEOMETRY}
    R -- sim --> R1[GEOMETRY BTM]
    R -- não --> S{IS_OBSTACLE ou IS_SOFFIT_BP}
    S -- sim --> S1[OBSTACLE HB]
    S -- não --> T{IS_WALL_BP}
    T -- sim --> T1[WALL HB]
    T -- não --> U{btm_kind WALL}
    U -- sim --> U1[WALL BTM]
    U -- não --> V{IS_FLOOR_BP ou btm_kind FLOOR}
    V -- sim --> V1[FLOOR HB ou BTM]
    V -- não --> W{IS_CEILING_BP}
    W -- sim --> W1[CEILING HB]
    W -- não --> N
    N -- fim --> X[OTHER obj obj '']
```

`btm_kind(node)` só devolve `btm_plane.object_kind` quando `is_property_set('object_kind')`: o enum tem padrão `WALL`
em todo objeto (BUG-20261007-TBY3).

```mermaid
flowchart TD
    A[movable_root obj] --> B[classify]
    B -- FRONT PART MODULE GEOMETRY OBSTACLE --> C[info.root]
    B -- OTHER --> D[free_group: grupo btm_group mais alto, ou None]
    B -- WALL FLOOR CEILING ANNOTATION ROOM_DOOR WINDOW --> E[None]
    F[reference_root obj] --> G{WALL?}
    G -- sim --> H[a parede]
    G -- não --> A
```
