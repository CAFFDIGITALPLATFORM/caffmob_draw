# Fluxograma: `scan.collect`, `scan.check_moved` e `stale.on_depsgraph_update` (collision)

Tradução da cena em itens (D-13), aviso ao soltar (D-16, RF-23) e marcador "desatualizado" (D-15, RN-14).

```mermaid
flowchart TD
    A[collect scene depsgraph] --> B[Para cada objeto da cena]
    B --> C{_skip: cortador, anotação, cota, obj_x, oculto?}
    C -- sim --> B
    C -- não --> D[_kind_of]
    D --> D1{malha com btm_wall_segments?} -- sim --> W[WALL, fino]
    D1 -- não --> D2{btm_aggregate.is_aggregate?} -- sim --> AG[ITEM, raiz vazia, fino]
    D2 -- não --> D3{IS_APPLIANCE?} -- sim --> AP[ITEM]
    D3 -- não --> D4[classify.classify]
    D4 --> D5{info.obj é o próprio objeto?}
    D5 -- não --> B
    D5 -- sim --> D6{kind}
    D6 -- MODULE, GEOMETRY --> IT[ITEM]
    D6 -- ROOM_DOOR, WINDOW --> ITF[ITEM, fino]
    D6 -- WALL, OBSTACLE --> SF[WALL ou OBSTACLE, fino]
    D6 -- FLOOR, CEILING --> FC[FLOOR ou CEILING]
    D6 -- OTHER malha solta sem pai, não WIRE/BOUNDS --> ITF
    D6 -- outros --> B
    W --> E
    AG --> E
    AP --> E
    IT --> E
    ITF --> E
    SF --> E
    FC --> E[Item: box_of, _links pai do agregado, hospedeiro, parede da abertura; _override]
    E --> F[_Entry item obj fine ou kind em WALL/OBSTACLE]
    F --> B
```

```mermaid
flowchart TD
    A[check_moved objs] --> B{enabled?}
    B -- não --> Z[return vazio]
    B -- sim --> C[names = vivos + children_recursive]
    C --> D[find context names]
    D -- exceção --> Z
    D -- ok --> E[keep = linhas que não envolvem names]
    E --> F[items = keep + novas]
    F --> G[stale.rechecked names]
    G --> H{há ocorrências?}
    H -- sim --> I[save_feedback.show movido colide com outro]
    H -- não --> J
    I --> J[redraw VIEW_3D e PROPERTIES]
```

```mermaid
flowchart TD
    A[on_depsgraph_update] --> B{btm_collision existe e checked ≥ 0?}
    B -- não --> Z[return]
    B -- sim --> C[names = checked_names ∪ nomes das linhas]
    C --> D[Para cada update com geometria ou transformação de Object]
    D --> E[_checked_root: sobe pelos pais até achar nome vigiado]
    E -- achou --> F[_changed.add raiz]
    F --> D
    D -- fim --> G{_changed e não stale?}
    G -- sim --> H[state.stale = True]
```

`_confirm` só consulta a malha quando um dos dois é fino; o BVH do objeto vem de `to_mesh` avaliado no mundo, com recuo
para as seis faces da OBB. `rechecked` tira os movidos de `_changed`: se nada mais mudou, o resultado volta a estar em dia.
