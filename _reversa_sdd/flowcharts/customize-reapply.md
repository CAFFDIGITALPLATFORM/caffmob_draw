# Fluxograma: `reapply.after_rebuild`, `frameless.reapply` e `common.set_cutpart_material` (customize)

Gancho pós-reconstrução (D-03, D-04): a biblioteca recria frentes e materiais; o adaptador relê `btm_custom` e reaplica.

```mermaid
flowchart TD
    A[after_rebuild context obj] --> B[root = adapters.module_root obj]
    B --> C{root e btm_custom e has_custom?}
    C -- não --> Z[return vazio]
    C -- sim --> D[reapply: adapter.reapply com trava _running]
    D --> E{has_structure root?}
    E -- não --> R[return mensagens]
    E -- sim --> F[reaffirm: remoções, espessuras, material bruto]
    F --> G{auto_back e back_mode RECESSED?} -- sim --> H[set_back_recess back_setback]
    G -- não --> I
    H --> I[scene_divisions.reflow; scene_extras.sync; scene_interiors.reflow; scene_slides.reflow]
    I --> R
    HC[has_custom] --> H1{has_structure?} -- sim --> T[True]
    H1 -- não --> H2{raiz: group_materials ou pull_all_fronts?} -- sim --> T
    H2 -- não --> H3{algum btm_custom na raiz ou descendentes com estilo, puxador, posição ≠ DEFAULT, material ou interior?}
    H3 -- sim --> T
    H3 -- não --> FF[False]
```

```mermaid
flowchart TD
    A[frameless.reapply context root] --> B[apply_group_materials: peça vence grupo; part_group por part_roles]
    B --> C[Para cada vão bay i / opening j]
    C --> D[model = pull_model da raiz se pull_all_fronts senão do vão; mat = front_material por nome]
    D --> E[Para cada frente IS_CABINET_FRONT do vão]
    E --> F{estilo porta/gaveta gravado?} -- sim --> G[_apply_style: door_styles.find nome → assign_style_to_front; DOOR_STYLE_INDEX/NAME]
    F -- não --> H
    G --> H{model ou posição ≠ DEFAULT?} -- sim --> I[_apply_pull: GeoNodeHardware Object; NO_PULL → None; idprops de posição]
    H -- não --> J
    I --> J{mat e peça sem material próprio?} -- sim --> K[set_cutpart_material]
    J -- não --> E
    K --> E
    E -- fim --> L{interior pedido e jaula com Shelf Quantity?} -- sim --> M[Shelf Quantity = shelves]
    L -- não --> C
    M --> C
    C -- fim --> N[run_calc_fix] --> O[avisos únicos]
```

```mermaid
flowchart TD
    A[set_cutpart_material obj mat] --> B{mat None?} -- sim --> F[False]
    B -- não --> C{modificador GeoNodeCutpart?}
    C -- não --> D{malha?} -- não --> F
    D -- sim --> E[todos os slots = mat] --> T[True]
    C -- sim --> G[Top Surface e Bottom Surface = mat via compat]
    G --> H{modificador desligado e malha com slots? porta 5 peças} -- sim --> I[slots = mat]
    H -- não --> J
    I --> J[outros modificadores de nós: Material, Stile Material, Panel Material = mat; Rail Material = variante ROTATED]
    J --> T
```

`_running` evita reentrância quando a reaplicação dispara novo recálculo da biblioteca, que chamaria `after_rebuild`
de novo. Estilo por nome resolve o índice só no momento de aplicar (RN-06): remover um estilo não desloca os demais.
