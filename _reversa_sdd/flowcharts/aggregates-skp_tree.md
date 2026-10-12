# Fluxograma: `skp_core.tree` e `skp_build.build` (aggregates)

Do SketchUp (OpenSKP) à árvore de grupos de peças no Blender (features 009 e 010).

```mermaid
flowchart TD
    A[tree scene model] --> B[material_names: casa materiais glTF com os do SketchUp pela imagem ou pela cor; Layer_x → x; senão SketchUp padrão]
    B --> C[_nodes: percorre scene_hierarchy; figuras de escala saem e seus caminhos vão para banned]
    C --> D[GroupPlan por nó; root_plan SketchUp]
    D --> E[Para cada primitiva glb]
    E --> F{caminho banido?}
    F -- sim --> E
    F -- não --> G[verts = to_blender x, −z, y]
    G --> H{vários nós no mesmo caminho?}
    H -- sim --> I[nó cuja position_mm está mais perto da caixa da primitiva]
    H -- não --> J[o nó do caminho, ou root_plan]
    I --> K{mesmos vértices já vistos no alvo?}
    J --> K
    K -- sim --> E
    K -- não --> L[MeshPlan: tris, uvs com v invertido, material, textura]
    L --> E
    E -- fim --> M[Monta filhos sob os pais; _prune: contêiner vazio sai, com um filho só colapsa]
    M --> N[root_plan na frente se tiver malha; devolve tops, skipped]
```

```mermaid
flowchart TD
    A[build context model scene] --> B[tree; pasta temporária; caches de imagens e materiais]
    B --> C[_build_node em cada topo]
    C --> D[Filhos primeiro, recursivo]
    D --> E[Para cada MeshPlan: material por assinatura nome|cor|imagem, reaproveitado se já existe]
    E --> F{textura?}
    F -- sim --> G[grava imagem na pasta; load; pack; nó Image Texture → Base Color]
    F -- não --> H
    G --> H[Mesh from_pydata + UV + material; Object na coleção]
    H --> I{malhas?}
    I -- sim --> J[group.create_group PLAIN com o nome da instância]
    I -- não --> K[Empty contêiner com btm_group no centro dos filhos]
    J --> L[Filhos parentados ao grupo mantendo o mundo]
    K --> L
    L --> M[grupos de topo, figuras puladas]
```

`skp.read` levanta `ValueError` com o motivo quando a wheel do OpenSKP falta, o arquivo não existe, não abre ou não tem
geometria; `ops_import._import_skp` apaga o que criou se a montagem falhar.
