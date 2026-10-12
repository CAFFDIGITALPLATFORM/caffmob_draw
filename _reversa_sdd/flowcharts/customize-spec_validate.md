# Fluxograma: `spec.validate`, `spec.validate_interior`, `spec.shelf_positions` e `manifest.validate` (customize)

Validação pura, sem Blender (RN-01 a RN-06; contrato 1.1.0).

```mermaid
flowchart TD
    A[validate spec] --> B[Para cada Opening]
    B --> C{path vazio?} -- sim --> E1[vão sem caminho]
    C -- não --> D{path repetido?} -- sim --> E2[repetido]
    D -- não --> F{front fora de FRONT_TYPES?} -- sim --> E3[frente desconhecida]
    F -- não --> G{front DRAWERS e drawer_count fora de 1..8?} -- sim --> E4[quantidade de gavetas]
    G -- não --> H{pull_position fora de PULL_POSITIONS?} -- sim --> E5[posição desconhecida]
    H -- não --> I{interior?} -- sim --> VI[validate_interior prefixado pelo vão]
    I -- não --> B
    VI --> B
    B -- fim --> J[Para cada grupo em group_materials: fora de GROUPS → erro]
    J --> K[Para cada material de grupo e de peça: vazio → erro]
    K --> R[lista de erros; vazia = válido]
```

```mermaid
flowchart TD
    A[validate_interior interior inner_height] --> B{shelves 0..20, dividers 0..10, drawers 0..8?}
    B -- não --> E[erros de faixa]
    B -- sim --> C{heights dado?}
    C -- não --> OK[sem erros]
    C -- sim --> D{len heights = shelves?} -- não --> E2[quantidade de alturas não bate]
    D -- sim --> F{crescentes?} -- não --> E3[alturas precisam ser crescentes]
    F -- sim --> G{heights 0 ≤ 0 ou última ≥ inner_height?} -- sim --> E4[altura fora do vão]
    G -- não --> OK
    SP[shelf_positions count H t heights] --> SQ{count ≤ 0?} -- sim --> SZ[lista vazia]
    SQ -- não --> SH{heights?} -- sim --> SD[as digitadas]
    SH -- não --> SG[gap = H − count·t / count+1; posição i = gap·i+1 + t·i]
```

```mermaid
flowchart TD
    A[manifest.validate data] --> B{dict?} -- não --> E0[não é objeto JSON]
    B -- sim --> C{format = caffmob_draw.user-module?} -- não --> E1[formato desconhecido]
    C -- sim --> D{major de schema_version ≤ 1?} -- não --> E2[versão não suportada]
    D -- sim --> F{library em LIBRARIES?} -- não --> E3[biblioteca desconhecida]
    F -- sim --> G{name e root_object não vazios?} -- não --> E4[nome vazio / raiz não informada]
    G -- sim --> H{algum erro até aqui?}
    H -- sim --> R[devolve erros]
    H -- não --> I[spec.validate from_dict spec]
    I --> J[_validate_structure: papel em ROLES, modo em MODES, space ^s\d+ .a|.b *$, orientação, medidas ≥ 0]
    J --> R
```

Leitor 1.0 abre arquivos 1.1.0 (mesmo major) e ignora `structure` e `divisions`; `loads` devolve `(dados, None, erros)`
em vez de levantar exceção.
