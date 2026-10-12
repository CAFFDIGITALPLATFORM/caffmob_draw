# Fluxograma do Módulo: move_over

"Mover Sobre" (`caffmob_draw/move_over/`), nível **Detalhado**. Re-extração 2026-10 (Fase 2c).

## 1. Modo, arraste e janela

```mermaid
flowchart TD
    A[caffmob.move_over_toggle] --> B[WindowManager.btm_move_over.enabled invertido]
    C[Botão direito PRESS na VIEW_3D] --> D{poll: modo ligado?}
    D -- não --> E[Evento segue ao menu de contexto do Blender]
    D -- sim --> F[raycast → classify.movable_root]
    F -- None --> G[FINISHED: clique consumido, sem menu RN-10]
    F -- A --> H[Modal de arraste: linha tracejada + rótulo]
    H --> I{MOUSEMOVE}
    I --> J[raycast → classify.reference_root ≠ A → B candidato]
    H --> K{RELEASE}
    K -- moveu ≥ 5 px e B --> L[caffmob.move_over_dialog a_name b_name]
    K -- senão --> M[FINISHED sem efeito]
    H --> N[Esc → CANCELLED]
    L --> O[MoveOver context A B]
    O -- ValueError --> P[WARNING; CANCELLED]
    O --> Q[Seleciona A e B; B ativo RN-05; preview: A com a rotação de B RN-08]
    Q --> R[Layout + fit das vistas + draw_handler POST_PIXEL + modal]
    R --> S{Evento}
    S -- NAV fora do painel --> T[PASS_THROUGH]
    S -- MOUSEMOVE --> U[hot = alvos sob o cursor]
    S -- clique em alvo ou empilhar --> V[align_to → preview; fit]
    S -- campo / Tab / dígitos / Enter --> W[_commit_typing: set_rotation, step, set_gap ou set_world]
    S -- setas / PgUp PgDn --> X[step_delta → nudge]
    S -- Salvar posição --> Y[Scene.btm_saved_positions.add saved]
    S -- posição salva --> Z[apply_saved]
    S -- Relativa/Absoluta --> AA[show_relative invertido: só exibição]
    S -- Substituir --> AB[_finish; caffmob.move_over_substitute INVOKE]
    S -- Confirmar / Enter --> AC{collision_global e ainda não avisado?}
    AC -- sim e overlapping --> AD[Aviso Sobrepõe; warned = True; permanece]
    AC -- não ou 2ª vez --> AE[FINISHED: passo de desfazer]
    S -- Esc / botão direito / Cancelar --> AF[restore → CANCELLED]
```

## 2. Mover na Parede (`caffmob.move_on_wall`)

```mermaid
flowchart TD
    A[poll: VIEW_3D, OBJECT, ativo com scene_cotas on_wall] --> B[invoke: guarda location; grab = _wall_point]
    B -- None --> C[WARNING: não projetou; CANCELLED]
    B --> D[start = placement; modal; cabeçalho Anterior Posterior Inferior]
    D --> E{Evento}
    E -- botão do meio / roda --> F[PASS_THROUGH]
    E -- Esc / botão direito --> G[location original; CANCELLED]
    E -- clique esquerdo / Enter --> H[FINISHED: passo de desfazer]
    E -- MOUSEMOVE --> I[point = raio do mouse ∩ plano da frente do módulo, no referencial da parede]
    I --> J{Shift?}
    J -- sim --> K[z0 = max 0, z0 inicial + Δz]
    J -- não --> L[alvo x0 = x0 inicial + Δx → cotas.slide com avoid_overlap]
    K --> M[location = x0, back_y, z0; placement atualizado; cabeçalho]
    L --> M
```

## 3. Plano de inserção

```mermaid
flowchart TD
    A[Menu do objeto › Usar como plano de inserção] --> B[invoke: modal, cursor EYEDROPPER]
    B --> C{Evento}
    C -- clique esquerdo --> D[scene.ray_cast]
    D -- sem acerto --> E[WARNING; CANCELLED]
    D -- acerto --> F[matrix = Translation local @ to_track_quat Z Y da normal; source_name; active = True]
    C -- Esc / botão direito --> G[CANCELLED]
    C -- botão do meio / roda --> H[PASS_THROUGH]
    F --> I[hb_snap: plano do piso substituído pela translação e coluna Z da matriz RN-17]
    J[Limpar plano de inserção] --> K[active = False → piso Z = 0]
```
