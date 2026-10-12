# Fluxograma do Módulo: selection

Classificação, seleção por componente, dimensões e Redimensionar (`caffmob_draw/selection/`), nível **Detalhado**.
Re-extração 2026-10 (Fase 2c).

## 1. Normalizador da seleção por componente

```mermaid
flowchart TD
    A[depsgraph_update_post] --> B{_busy?}
    B -- sim --> Z[sai]
    B -- não --> C{Scene.btm_component_select ligado?}
    C -- não --> D[esquece assinatura; sai]
    C -- sim --> E{modo OBJECT, view_layer e window_manager?}
    E -- não --> Z
    E -- sim --> F{modal da extensão ou transform rodando?}
    F -- sim --> Z
    F -- não --> G[assinatura = nomes selecionados + ativo]
    G --> H{igual à última?}
    H -- sim --> Z
    H -- não --> I[_busy = True; normalize]
    I --> J[poda isenções não selecionadas]
    J --> K[modes = cabinet_modes: vazio sem interface herdada]
    K --> L[Para cada selecionado não isento]
    L --> M[root = component_root obj modes]
    M --> N{root ≠ obj e presente na camada?}
    N -- sim --> O[root.select_set True; obj.select_set False]
    N -- não --> L
    O --> L
    L -- fim --> P{ativo não isento e sua raiz selecionada?}
    P -- sim --> Q[ativo = raiz]
    P -- não --> R
    Q --> R[_busy = False; grava assinatura]
```

## 2. Alt + clique e reset

```mermaid
flowchart TD
    A[Alt + clique: caffmob.component_pick] --> B{poll: OBJECT, VIEW_3D, interruptor ligado?}
    B -- não --> C[Alt + clique do Blender]
    B -- sim --> D[exempt = isenções atuais se Shift, senão vazio]
    D --> E[suspended: view3d.select extend deselect_all location]
    E --> F{FINISHED e ativo selecionado?}
    F -- sim --> G[exempt += ativo]
    F -- não --> H
    G --> H[set_exempt; forget]
    I[Clique PRESS sem Alt: caffmob.component_click_reset] --> J{poll: ligado e há isenções?}
    J -- não --> K[segue ao view3d.select]
    J -- sim --> L[set_exempt vazio; forget; PASS_THROUGH]
```

## 3. Dimensões e Redimensionar

```mermaid
flowchart TD
    A[element obj] --> B[classify]
    B -- ANNOTATION ou None --> C[None]
    B -- FRONT / PART --> D[classify da raiz]
    D --> E
    B --> E{MODULE ROOM_DOOR WINDOW GEOMETRY OBSTACLE WALL?}
    E -- sim --> F[Element info.obj]
    E -- não --> G[Element free_group ou obj, rótulo Objeto]
    H[size el] --> I{kind}
    I -- WALL HB --> J[Length Height Thickness]
    I -- GN kinds --> K[editing.get_dimension ×3; porta: furo → folha]
    I -- resto --> L[box_size: caixa × escala]
    M[resize el width] --> N{can_resize e 0,01 ≤ width ≤ 100?}
    N -- não --> O[ValueError]
    N -- sim --> P[Mede pais com agregados: largura local e u v]
    P --> Q[_set_width: escala X, set_dimension, Dim X do vão + sync, set_wall length, btm_geometry.width ou Dim X]
    Q --> R[view_layer.update]
    R --> S[Para cada pai: factor = nova / antiga]
    S --> T{abs factor − 1 < 1e-6?}
    T -- sim --> S
    T -- não --> U[_stretch_aggregate em cada agregado: escala eixo alinhado ao X do pai, size e rest_offset, u v]
    U --> S
    S -- fim --> V[view_layer.update]
```
