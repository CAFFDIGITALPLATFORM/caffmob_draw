# Fluxograma: módulo `stick`

Grudar itens em faces planas (feature 004, I1) e prévia do ímã (feature 005). Vínculo = pai Blender + `Object.btm_stick`.

```mermaid
flowchart TD
    subgraph Entradas
        G[caffmob.stick_to_face: clique numa face]
        M[caffmob.stick_move: arrasto no plano, Ctrl troca de face]
        R[caffmob.stick_release]
        F[Campos u, v, distance, spin do painel]
        N[G nativo, posicionamento da biblioteca, mover do plugin]
        L[load_post: migrate.run]
        H[Hospedeiro muda de medida ou é apagado]
    end
    G --> ST[link.stick: host_for → can_stick → is_planar → orient → _attach → choose_face → _record → update_position]
    M --> ST
    M --> UV[st.u / st.v = âncora + delta]
    UV --> UP[apply.update_position: shift para u v distance; _check_face; last_world]
    F --> UP
    F --> SP[apply.update_spin: gira pelo centro da pegada]
    R --> REL[link.release: pai anterior, mesma posição no mundo]
    L --> MIG[migrate: módulo raiz filho de parede → link_in_place NEG_Y ou POS_Y]
    N --> DG[depsgraph_update_post: anota em _pending]
    H --> DG2[depsgraph_update_post: caixa mudou → update_position nos grudados; host None → lose_link]
    DG --> TM[timer 0,2 s: espera modal_running terminar]
    TM --> SE[settle.run]
    SE --> P1[grudado → apply.project]
    SE --> P2[módulo novo na parede → link_in_place]
    SE --> P3[módulo ou geometria solto → magnet.try_stick + undo_push Grudar]
    SE --> P4[collision.scan.check_moved]
    subgraph Saídas
        PAN[painel Elemento filho de: host — face; Elementos filhos]
        TOAST[save_feedback: Elemento filho de / Vínculo perdido / Item fora da face]
        PRE[magnet_preview: contorno da face + caixa encostada + Grudar em: nome]
    end
```

`frame.py` é puro: referencial `(origem, U, V, N)` da face no espaço local do hospedeiro, `BOX_SIDE` (acompanha medida)
ou `PLANE` (plano fixo). O item é descrito por `(u, v, distance)` = canto mínimo da pegada no referencial.
