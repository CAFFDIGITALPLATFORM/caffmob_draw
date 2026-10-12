# Fluxograma: módulo `cabinet_editor`

Editor de Armário em janela própria (feature 004), com as abas da 006 e o Construtor da 008 (7 abas), mais a montagem
da 012. Os botões só enfileiram pedidos; um único modal com `UNDO` muda a cena (D‑21, D‑22).

```mermaid
flowchart TD
    subgraph Entradas
        OPEN[caffmob.cabinet_editor: barra lateral, menu, inserir da biblioteca]
        BTN[Botões e campos virtuais do painel: edit, insert, part_*, division_*, tree_*, comp_*, bays, pos_*]
        KEY[Teclado e mouse na vista: clique, roda, setas, Ctrl+Z, Esc]
        EXT[Fora do editor: depsgraph_update_post e frame_change_post]
    end
    OPEN --> SS[start_session: Draft com read_state; limites; peças iniciais; subvãos]
    SS --> WIN[window.open_editor: janela nova com Image Editor; aba Estrutura]
    WIN --> MOD[cabinet_editor_modal: timer 0,1 s]
    BTN --> Q[(Session.requests)]
    KEY --> MOD
    MOD --> Q
    Q --> PR[process: um pedido por vez, ValueError/RuntimeError → s.error]
    PR --> BR[bridge: set_dimension / edit ação / apply_state instantâneo]
    BR --> LIB[adaptadores da customize: set_front, set_interior, reapply, remove_part…]
    BR --> SC[scene_divisions / scene_extras / scene_interiors / scene_slides: objetos filhos da raiz]
    BR --> RF[refresh: peças, checkpoint do rascunho, diff, mensagens, subvãos, espelhos do painel]
    RF --> DRAW[window.draw_editor POST_PIXEL: vista frontal, vãos, seleção, barra Selecionado]
    MOD --> END{request}
    END -- ok --> FIN[FINISHED: um passo de desfazer; janela fechada depois]
    END -- cancel / janela fechada / raiz apagada --> RB[rollback: apply_state do instantâneo inicial → CANCELLED]
    PR -- apply --> AP[ed.undo_push + apply_point: o atual vira a referência do Cancelar]
    EXT --> RH{sessão aberta?} -- não --> RFL[scene_divisions.reflow pela assinatura btm_division_sig]
    subgraph Saídas
        S1[Módulo alterado: medidas, frentes, estrutura, divisões, extras, internos, deslizantes, fundo]
        S2[Painel: Mensagens DIM/GEO/CAT/STR/DIV/LIB, Ajustes automáticos, estado do rascunho]
    end
    FIN --> S1
    RF --> S2
```

Núcleos puros sem `bpy` (testados fora do Blender): `state`, `validate`, `elevation`, `structure`, `divisions`,
`catalog`, `extras`, `bays`, `slides`, `appliances`, `position`. Fluxogramas por função:
[`cabinet_editor-modal_process.md`](cabinet_editor-modal_process.md),
[`cabinet_editor-apply_state.md`](cabinet_editor-apply_state.md),
[`cabinet_editor-divisions_resolve.md`](cabinet_editor-divisions_resolve.md),
[`cabinet_editor-layouts.md`](cabinet_editor-layouts.md).
