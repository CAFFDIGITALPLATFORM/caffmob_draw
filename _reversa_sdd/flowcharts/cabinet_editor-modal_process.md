# Fluxograma: `BTM_OT_CabinetEditorModal.modal`, `process` e `refresh` (cabinet_editor)

Ciclo do editor (D‑21, D‑22, D‑04, D‑06, D‑16): o modal é o único que muda a cena; o rascunho guarda instantâneos.

```mermaid
flowchart TD
    A[modal context event] --> B{sessão?} -- não --> X1[_end sem manter → CANCELLED]
    B -- sim --> C{raiz existe?} -- não --> X2[_end rollback + aviso 'O módulo não existe mais' → CANCELLED]
    C -- sim --> D{janela viva?} -- não --> X3[_end rollback; se havia alteração: toast 'alterações descartadas' → CANCELLED]
    D -- sim --> E{request}
    E -- ok --> OK[_end mantendo → 'Armário atualizado' → FINISHED]
    E -- cancel --> X4[_end rollback → CANCELLED]
    E -- nenhum --> F[process: fila tem pedido?]
    F -- sim, mudou --> RM[RUNNING_MODAL]
    F -- não --> G{evento}
    G -- TIMER --> T[foca a aba do editor uma vez → PASS_THROUGH]
    G -- Ctrl/Cmd Z, Y --> U[push undo / redo]
    G -- setas fora do painel --> AR[push arrow eixo, sentido]
    G -- roda --> Z[View2D.zoom 1,15 no cursor]
    G -- clique esquerdo na vista --> H[x, z = view.to_world]
    H --> I[_boards: chapas que não são frente nem vão e não cobrem o subvão inteiro sob o clique]
    I --> J{elevation.hit?}
    J -- chapa --> K[selected = chapa]
    J -- nada --> L[selected = None; space = divisions.space_at; vão da biblioteca do alvo]
    G -- Esc --> CL[caffmob.cabinet_editor_close]
    G -- outro --> PT[PASS_THROUGH]
```

```mermaid
flowchart TD
    P[process] --> Q{fila vazia?} -- sim --> R[return mudou?]
    Q -- não --> T{tipo}
    T -- dimension --> D1[check_dimension na faixa] --> D2{erro?}
    D2 -- sim --> D3[dim_messages campo; refresh sem checkpoint]
    D2 -- não --> D4[bridge.set_dimension; refresh com checkpoint]
    T -- edit --> E1[edited += targets; msgs = bridge.edit ação payload] --> E2[refresh com LIB-001]
    T -- apply --> A1{erro bloqueante ou rascunho limpo?} -- não --> A2[ed.undo_push 'Aplicar'; apply_point; initial_parts = parts; edited limpo; applied]
    T -- arrow --> W1{divisória selecionada e eixo da orientação?} -- sim --> W2[position.step_move: Passo inicial no primeiro toque] --> W3[edit EDIT_DIVISION offset; refresh; reflow force]
    W1 -- sem seleção --> W4[s.error 'Selecione uma divisória']
    T -- undo/redo --> H1[draft.undo/redo] --> H2{instantâneo?}
    H2 -- não --> H3[s.error 'Nada para desfazer/refazer']
    H2 -- sim --> H4[dim_messages limpo; refresh com apply_state alvo, sem checkpoint; current = alvo]
    D3 & D4 & E2 & A2 & W3 & H4 --> Q
```

```mermaid
flowchart TD
    RF[refresh library_messages, checkpoint] --> P1[parts = bridge.parts: bound box avaliada de cada filho visível + chapas do btm]
    P1 --> P2{selecionado sumiu?} -- sim --> P3[selected = None]
    P2 -- não --> P4
    P3 --> P4[current = read_state] --> P5{checkpoint?}
    P5 -- sim --> P6[draft.checkpoint: só grava se a assinatura mudou]
    P5 -- não --> P7[draft.current = current]
    P6 & P7 --> P8[adjustments = elevation.diff initial_parts × parts sem edited]
    P8 --> P9[mensagens: DIM guardadas + GEO-001 outside_volume + GEO-002 internal_overlaps]
    P9 --> P10[_divisions_refresh: subvãos no referencial da vista, rótulos, DIV-*, STR-002, peças removidas, vão da biblioteca]
    P10 --> P11[+ LIB-001 por aviso da biblioteca] --> P12[_sync_ui: espelhos no WindowManager] --> P13[redraw]
```

Por que a fila: um botão com `UNDO` criaria um passo de desfazer por clique; dentro do modal, o Blender só registra
o passo quando o modal termina com `FINISHED` (OK). Aplicar empurra um passo explícito (`ed.undo_push`) sem fechar.
