# Fluxograma: `bridge.read_state`, `apply_state` e `_apply_structure` (cabinet_editor)

Levar o módulo a um instantâneo do rascunho (desfazer/refazer, Cancelar, janela fechada). Muda só o que difere.

```mermaid
flowchart TD
    A[apply_state context root target] --> B[current = read_state root]
    B --> C[para L, A, P: diferença > 1e-7 → editing.set_dimension]
    C --> D{adaptador?} -- não --> R0[return avisos]
    D -- sim --> E[para cada vão de target.spec com objeto e estado atual]
    E --> F{frente ou n gavetas mudou?} -- sim --> G[adapter.set_front; relê os vãos]
    F -- não --> H
    G --> H{interior pedido e diferente?} -- sim --> I[adapter.set_interior]
    H -- não --> E
    I --> E
    E -- fim --> J[_raw: grava os campos crus de btm_custom por vão; pull_model e pull_all_fronts da raiz; material por grupo; material por peça]
    J --> K[reapply.reapply: estilo, puxador, materiais pela biblioteca]
    K --> L[_apply_structure current.structure → target.structure]
    L --> M{backs mudou?} -- sim --> N[set_back: modo, recuo, automático]
    M -- não --> O
    N --> O{divisões cruas mudaram?}
    O -- sim --> P[scene_divisions.apply target.divisions]
    O -- não --> Q[scene_divisions.reflow force]
    P & Q --> S{extras mudaram?} -- sim --> T[btm_structure.extras_from_dict]
    S -- não --> U
    T --> U[scene_extras.sync] --> V[scene_interiors.apply target.interiors]
    V --> W{slides sem opens mudaram ou target tem slides?} -- sim --> Y[scene_slides.apply target.slides]
    W -- não --> R
    Y --> R[return avisos]
```

```mermaid
flowchart TD
    A[_apply_structure current target] --> B[para cada papel TOP, BOTTOM, BACK, LEFT, RIGHT]
    B --> C{RoleState igual?} -- sim --> B
    C -- não --> D{estava removido e agora não, ou modo diferente?}
    D -- sim --> E[restore_part: desfaz com o modo usado; _tidy; reflow]
    D -- não --> F
    E --> F{espessura ou material mudou?} -- sim --> G[edit_part: thickness, material; reaffirm; _tidy; reflow]
    F -- não --> H
    G --> H{alvo removido e não estava no mesmo modo?} -- sim --> I[remove_part: caps; allowed_mode; grava; adapter.remove_part; reflow]
    H -- não --> B
    I --> B
```

```mermaid
flowchart TD
    R[read_state root] --> R1[info = classify; adaptador]
    R1 --> R2[dims = editing.get_dimension width, height, depth]
    R2 --> R3[spec = spec.to_dict adapter.read + _raw]
    R3 --> R4[structure = btm_structure.to_dict]
    R4 --> R5[divisions = scene_divisions.read: btm_division de cada chapa, por nome]
    R5 --> R6[extras = extras_dict; slides = scene_slides.state_of com opens; interiors = entries; backs = backs_dict]
    R6 --> R7[EditorState]
```

A ordem dentro de `_apply_structure` segue a regra da 006: o registro em `btm_structure` muda antes de chamar o
adaptador, porque o recálculo das bibliotecas reafirma o que está gravado. A montagem (012) não está no instantâneo
(ver code-analysis §14.16).
