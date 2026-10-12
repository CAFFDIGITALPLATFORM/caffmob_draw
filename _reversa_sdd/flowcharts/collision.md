# Fluxograma: módulo `collision`

Verificação de colisão de corpo (feature 004, I2): o item fica onde foi solto; o sistema avisa, destaca e oferece afastar.

```mermaid
flowchart TD
    subgraph Entradas
        OP[caffmob.check_collisions ALL ou SELECTED]
        MV[stick/settle: fim do assentar → scan.check_moved objs]
        PO[caffmob.collision_push_out]
    end
    OP --> EN{scan.enabled: btm_settings.collision_global?}
    EN -- não --> W1[WARNING Colisão desligada]
    EN -- sim --> CA[scan.check_all]
    CA --> FIND[scan.find: collect → rules.conflicts com confirm BVH]
    FIND -- exceção --> ERR[state.error = texto; lista vazia; stale = False]
    FIND -- ok --> ST[_store: items, checked, checked_names, scope; stale.reset]
    MV --> EN2{enabled?}
    EN2 -- sim --> CM[find só dos movidos + children_recursive]
    CM --> MERGE[mantém linhas sem os movidos + novas; stale.rechecked]
    MERGE --> TOAST[save_feedback: X colide com Y]
    PO --> PUSH[translation += push; grudado: só no plano da face; project; check_moved]
    ST --> UI
    MERGE --> UI
    subgraph UI[Saídas]
        PAN[panels.draw_collisions: desligado / erro / nunca / desatualizado / sem colisões / lista]
        OV3[overlay POST_VIEW: arestas da OBB, vermelho ou laranja]
        OV2[overlay POST_PIXEL: Tipo: A × B, sombra]
        SAVE[save_post: N colisões pendentes ou não verificadas]
    end
    DG[depsgraph_update_post stale] --> CH{Object vigiado mudou geometria ou transformação?}
    CH -- sim --> STALE[_changed.add raiz; state.stale = True] --> UI
```

Camadas: `obb` e `rules` são puros (testáveis sem Blender); `scan` traduz a cena em `Item`s e confirma pares finos pela
malha (`BVHTree.overlap`); `props` guarda o resultado em `WindowManager.btm_collision`, nunca no arquivo.
