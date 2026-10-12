# Fluxograma: `sweep.sweep`, `leaf.update_open` e `collision.Tester.hit` (aggregates)

Abrir e fechar a folha parando no primeiro contato (RN-11a; esquadria D-10).

```mermaid
flowchart TD
    A[sweep current target hit step tolerance close floor floor_contact] --> B{target ≤ current: fechando?}
    B -- sim --> C{close?}
    C -- não --> D[target, None: fechar é livre]
    C -- sim --> E[stop = max target, floor]
    E --> F{stop ≥ current?}
    F -- sim --> G[current, floor_contact se floor > target]
    F -- não --> H[sweep espelhado de −current a −stop com hit −v]
    H --> I[reached = −reached; contato ou floor_contact]
    B -- não: abrindo --> J[free = current]
    J --> K{free < target?}
    K -- não --> L[target, None]
    K -- sim --> M[probe = min free + step, target; contact = hit probe]
    M --> N{contato?}
    N -- não --> O[free = probe] --> K
    N -- sim --> P[blocked = probe]
    P --> Q{blocked − free > tolerance?}
    Q -- sim --> R[middle; hit middle? blocked = middle : free = middle] --> Q
    Q -- não --> S[free, contact]
```

```mermaid
flowchart TD
    A[update_open obj] --> B{LEAF com pivô?}
    B -- não --> Z[sai]
    B -- sim --> C[target = open_value 0..1; current = fração do pivô]
    C --> D{motion}
    D -- SLIDE --> E[scale = travel; passo 10 mm; tol 1 mm]
    D -- SWING --> F[scale = max_angle; passo 2°; tol 0,25°]
    E --> G[Tester obj]
    F --> G
    G --> H{esquadria?}
    H -- não --> I[sweep current·scale → target·scale]
    H -- sim --> J[floor = _close_floor: batente pela outra folha; sweep close]
    I --> K[apply_fraction reached/scale]
    J --> K
    K --> L[contact_name; se SLIDE abrindo chegou ao free_travel: peça do fim do curso livre]
    L --> M[contact_kind CLOSE/OPEN/NONE; open_value ajustado; redesenha]
```

```mermaid
flowchart TD
    A[Tester.hit fraction] --> B[corners_at: parent_world @ pose_matrix @ matrix_basis @ cantos encolhidos 1 mm]
    B --> C[caixa AABB dos cantos]
    C --> D[candidatos = alvos em cache cuja AABB cruza]
    D --> E{algum?}
    E -- não --> F[None]
    E -- sim --> G[BVH da caixa da folha 6 faces]
    G --> H[Para cada candidato: BVH do alvo sob demanda; overlap?]
    H -- sim --> I[o objeto]
    H -- nenhum --> F
```

Alvos excluídos: a folha, o pivô e descendentes; na esquadria as folhas irmãs e o pai (as peças da esquadria contam);
fora dela a raiz do módulo do pai; arame, bounds, cortadores, anotações, invisíveis, e as peças com `btm_opening_frame`
igual ao pai (marco da porta real).
