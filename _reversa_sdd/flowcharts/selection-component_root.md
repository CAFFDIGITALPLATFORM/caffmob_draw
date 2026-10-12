# Fluxograma: `component.component_root` e `delete_plan` (selection/component.py)

Raiz do componente pela precedência D-01 e plano de exclusão em profundidade (D-05).

```mermaid
flowchart TD
    A[component_root obj modes] --> B{obj None?}
    B -- sim --> C[None]
    B -- não --> D[chain = ancestrais de obj]
    D --> E{algum ancestral é vão: IS_ENTRY_DOOR_BP, IS_WINDOW_BP ou btm_kind OPENING?}
    E -- sim --> F[o vão]
    E -- não --> G{obj IS_2D_ANNOTATION?}
    G -- sim --> H[obj: cota solta não sobe]
    G -- não --> I[Para cada ancestral até o primeiro módulo, sem incluí-lo]
    I --> J{grudado btm_stick.is_stuck, ou agregado próprio: is_aggregate e não folha LEAF de grupo FRAME?}
    J -- sim --> K[ele mesmo RN-03]
    J -- não --> I
    I -- módulo ou fim --> L[root library = module_root]
    L --> M{root existe?}
    M -- sim --> N{modes.get library, True?}
    N -- sim --> O[root: módulo inteiro]
    N -- não --> P[obj: modo peça da biblioteca herdada]
    M -- não --> Q{algum ancestral btm_object_item.is_item?}
    Q -- sim --> R[o item]
    Q -- não --> S{free_group?}
    S -- sim --> T[grupo de peças mais alto]
    S -- não --> U[obj: parede, piso, malha solta]
```

```mermaid
flowchart TD
    A[delete_plan targets keep_aggregates] --> B{keep_aggregates?}
    B -- sim --> C[keep = own_aggregates de cada alvo]
    B -- não --> D
    C --> D[Para cada alvo: walk alvo, is_target = True]
    D --> E{já visto?}
    E -- sim --> F[volta]
    E -- não --> G{não é alvo e é grudado ou está em keep?}
    G -- sim --> F
    G -- não --> H[marca visto]
    H --> I{não é alvo, ou deletes_subtree: não é parede, piso nem teto?}
    I -- sim --> J[walk em cada filho, is_target = False]
    I -- não --> K
    J --> K[remove.append node: filhos antes do pai]
    D -- fim --> L[openings = vãos em remove]
    L --> M[DeletePlan remove openings]
```

`own_aggregates(target)`: desce pelos filhos (sem entrar em vãos nem partir de grupo `FRAME`) e recolhe agregados que
são a própria raiz de componente; a folha de porta, janela ou esquadria é peça delas e não entra.
