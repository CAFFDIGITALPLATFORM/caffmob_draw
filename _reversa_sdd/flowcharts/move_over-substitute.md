# Fluxograma: `ops_substitute.substitute` (move_over/ops_substitute.py)

Troca A por um módulo da biblioteca do usuário no mesmo lugar, com a rotação de A e o mesmo canto de referência.

```mermaid
flowchart TD
    A[substitute context a b entry] --> B[library_io.load → root, loaded, warnings]
    B --> C{root é None?}
    C -- sim --> D[Remove os objetos carregados; devolve None, warnings]
    C -- não --> E[root.matrix_world = A; root.parent = A.parent]
    E --> F{A tem pai?}
    F -- sim --> G[root.matrix_parent_inverse = o de A; matrix_world de A reaplicada]
    F -- não --> H
    G --> H[view_layer.update]
    H --> I[frame_inv de B: box_a = _tree_box A; box_b = _local_box B; box_new = _tree_box root]
    I --> J[side = side_of box_a box_b]
    J --> K{side}
    K -- RIGHT --> L[dx = xmin A − xmin novo]
    K -- LEFT --> M[dx = xmax A − xmax novo]
    L --> N[delta = dx, ymin A − ymin novo, zmin A − zmin novo]
    M --> N
    N --> O[root.translation += frame 3×3 @ delta]
    O --> P[Remove A e descendentes, do fundo para a raiz]
    P --> Q[Devolve root, warnings]
    R[BTM_OT_MoveOverSubstitute.execute] --> S{a, b e entry existem?}
    S -- não --> T[WARNING Escolha um módulo; CANCELLED]
    S -- sim --> A
    Q --> U{root?}
    U -- não --> V[WARNING com os avisos; CANCELLED]
    U -- sim --> W[Seleciona e ativa o novo; INFO ou WARNING; FINISHED]
```

`_tree_box` usa as malhas visíveis do grupo (fora `WIRE`/`BOUNDS`); sem nenhuma, a caixa da raiz. O `module` Enum é
preenchido a cada leitura por `library_io.list_modules()` (id = caminho do `.blend`), e `_ITEMS` global mantém as
strings vivas para o Blender.
