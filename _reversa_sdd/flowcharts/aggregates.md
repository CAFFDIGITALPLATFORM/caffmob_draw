# Fluxograma do Módulo: aggregates

Agregados, folhas, grupos, esquadria e SketchUp (`caffmob_draw/aggregates/`), nível **Detalhado**. Re-extração
2026-10 (Fase 2c).

## 1. Converter, posicionar e desconverter

```mermaid
flowchart TD
    A[caffmob.aggregate_convert: malhas ou grupos + pai ativo] --> B{can_convert?}
    B -- não --> C[WARNING por objeto]
    B -- sim --> D[convert: guarda orig_parent e orig_matrix; parenta mantendo o mundo]
    D --> E[face = nearest_face do centro ou a escolhida]
    E --> F[size, rest_offset, u v offset = params_from_box]
    F --> G[parent_ref, is_aggregate; update_position]
    H[update de face / u / v / offset ou pai muda de tamanho] --> I[update_position]
    I --> J[clamp aos limites da face; grava de volta sem disparar update]
    J --> K[location = box_for.lo − rest_offset]
    K --> L{perforate ou cutter?}
    L -- sim --> M[perforate.sync: cortador + BOOLEAN; CPM_CUTOUT se furo real possível]
    N[caffmob.aggregate_unconvert] --> O[remove recorte e furo real; remove pivô; desmarca produção]
    O --> P[pai e matriz originais; kind AGGREGATE; parent_ref None]
```

## 2. Folha de porta

```mermaid
flowchart TD
    A[caffmob.leaf_convert ou window_assemble ou openings.sync] --> B[make_leaf: btm_leaf_rest, motion, hinge, sentido, ângulo ou curso]
    B --> C{esquadria com folhas irmãs?}
    C -- sim --> D[rest_overlap nas duas folhas]
    C -- não --> E
    D --> E[rebuild_pivot: Empty Eixo filho do pai; folha filha dele; base_point]
    E --> F{SLIDE numa esquadria?}
    F -- sim --> G[measure_free_travel: varre até a esquadria → free_travel, travel]
    F -- não --> H
    G --> H[update_open]
    I[open_value / swing_sign / max_angle / travel mudam] --> H
    H --> J[Tester: caixa da folha encolhida 1 mm; alvos em cache]
    J --> K{esquadria?}
    K -- não --> L[sweep: fechar livre; abrir para no 1º contato com bissecção]
    K -- sim --> M[sweep close: fechar também testa e não passa do batente da outra folha]
    L --> N[apply_fraction; contact_name e contact_kind; open_value ajustado]
    M --> N
```

## 3. Grupos, esquadria e janela na parede

```mermaid
flowchart TD
    A[caffmob.import_model] --> B{extensão}
    B -- .skp --> C[skp.read → skp_build.build: árvore de grupos PLAIN, materiais, texturas empacotadas]
    B -- obj/fbx/gltf --> D[Importador nativo com eixo; escala pela unidade; 2+ malhas → grupo PLAIN]
    D --> E[caffmob.window_assemble: grouping.suggest pelos nomes]
    E --> F[Esquadria FRAME + uma folha LEAF por linha, filha da esquadria]
    F --> G[make_leaf SLIDE com sentido padrão para o próprio lado, ou SWING]
    G --> H[caffmob.window_install: esquadria + parede HB]
    H --> I[GeoNodeCage IS_WINDOW_BP: Dim X/Z da esquadria, Dim Y da parede; filha da parede em x, 0, peitoril]
    I --> J[Esquadria filha da jaula com drivers x = Dim X/2, y = Dim Y/2; cut_wall]
    K[caffmob.window_uninstall] --> L[remove drivers; solta a esquadria; tira o booleano; apaga a jaula]
    M[caffmob.group_dissolve] --> N[desconverte folhas e grupo; ungroup devolve ao pai original]
```

## 4. Apagar com agregados (X / Delete)

```mermaid
flowchart TD
    A[X ou Delete] --> B{poll: descendentes apagáveis, agregados próprios ou grudados?}
    B -- não --> C[Delete do Blender]
    B -- sim --> D{há agregados próprios?}
    D -- sim --> E[Diálogo: apagar também os agregados?]
    D -- não --> F
    E --> F[delete_components]
    F --> G[Solta os grudados e avisa Vínculo perdido]
    G --> H[component.delete_plan]
    H --> I{keep_aggregates?}
    I -- sim --> J[unconvert nos agregados próprios]
    I -- não --> K
    J --> K[Remove o booleano dos vãos na parede]
    K --> L[Apaga cortadores órfãos]
    L --> M[bpy.data.batch_remove dos vivos]
```
