# Fluxograma do Módulo: walls2d

Editor de Paredes 2D (`caffmob_draw/walls2d/`), nível **Detalhado**. Re-extração 2026-10 (Fase 2c).

## 1. Ciclo abrir → editar → OK

```mermaid
flowchart TD
    A[caffmob.wall_editor] --> B{Paredes da camada nova selecionadas?}
    B -- sim --> C[Diálogo: converter ou só referência]
    B -- não --> D[scene_io.read_plan: cadeias das paredes IS_WALL_BP]
    C --> D
    D --> E[props.start: Session com pé-direito do projeto]
    E --> F[canvas2d.window.open_window]
    F --> G[caffmob.wall_editor_modal]
    G --> H{Evento}
    H -- navegação --> I[View2D pan/zoom/fit]
    H -- ferramenta --> J[Chain: move_node / split / invert / remove_node / append]
    H -- painel --> K[props: campos virtuais -> model.set_*]
    J --> L[Session.checkpoint se a assinatura mudou]
    K --> L
    H -- OK --> M{Itens que não cabem, módulos em trechos apagados, pé-direito diferente?}
    M -- sim, 1ª vez --> N[Avisos no painel; confirm_pending]
    M -- não ou 2ª vez --> O[request = ok]
    O --> P[apply.apply_plan]
    P --> Q[close_later; props.end]
    H -- Esc / Cancelar --> R{dirty?}
    R -- sim --> S[Pergunta descartar]
    R -- não --> Q
```

## 2. `apply_plan`

```mermaid
flowchart TD
    A[Para cada cadeia] --> B[close_if_touching: fecha contorno aberto com fim no início]
    B --> C{project_height?}
    C -- sim --> D[height = end_height nas paredes de altura cheia]
    C -- não --> E
    D --> E[hb_order: espessura à esquerda]
    E --> F[Para cada trecho]
    F --> G{source existe?}
    G -- sim --> H[GeoNodeWall existente; updated]
    G -- não --> I[GeoNodeWall.create; created]
    H --> J[Guarda matrizes dos filhos; limpa COPY_LOCATION]
    I --> J
    J --> K{Primeiro trecho?}
    K -- sim --> L[location = primeiro nó]
    K -- não --> M[connect_to_wall anterior]
    L --> N[rotation = direção]
    M --> N
    N --> O{Girou > 90°?}
    O -- sim --> P[Filhos voltam à matriz de mundo; aberturas re-hospedadas]
    O -- não --> Q
    P --> Q[Length, Thickness, Height, End Height, btm_wall_type; Dim Y das aberturas]
    Q --> F
    F -- fim --> R[Remove removed_sources e converted_sources]
    R --> S[update_all_wall_miters]
    S --> T[refresh_floors_and_ceilings]
    T --> U[openings.sync nas portas e janelas reais]
```

## 3. Lápis (ferramenta Construir Parede)

```mermaid
flowchart TD
    A[Clique] --> B{drawing?}
    B -- não --> C[Novo Chain com o ponto da mira; direção zerada]
    B -- sim --> D{Ponto no ímã do início?}
    D -- sim --> E[prompt = close]
    D -- não --> F[append: fixa direção do trecho]
    G[Dígitos / operadores / unidade] --> H[typed; preview da conta]
    I[Enter] --> J{typed válido?}
    J -- não --> K[error Valor Inválido]
    J -- sim --> L{direção fixada?}
    L -- não --> M[initial_direction do mouse com trava ortogonal]
    L -- sim --> N[next_point na direção]
    M --> N
    N --> O{Toca o início com 2+ trechos?}
    O -- sim --> P[prompt = close; pending_point]
    O -- não --> F
    Q[Setas] --> R[direção = ARROWS; travada]
    S[Esc / botão direito] --> T[_finish_drawing: descarta cadeia vazia]
```
