# Fluxograma do Módulo: openings

Porta e janela reais na parede (`caffmob_draw/openings/`), nível **Detalhado**. Re-extração 2026-10 (Fase 2c).

## 1. Da caixa à porta real

```mermaid
flowchart TD
    A[Caixa IS_ENTRY_DOOR_BP ou IS_WINDOW_BP colocada por doors_windows] --> B[sync.sync context cage]
    B --> C{is_opening?}
    C -- não --> D[False]
    C -- sim --> E[signature = kind, Dim X Y Z, Is Left, Swing Inside, versão]
    E --> F{igual à gravada e montagem viva, sem force?}
    F -- sim --> D
    F -- não --> G[_remember: abertura das folhas e peças de produção]
    G --> H[clear: apaga montagem anterior; remove folha cinza da 005]
    H --> I[_parts: window_parts ou leaf_size + door_parts]
    I --> J[build.build: uma malha por papel, materiais, UV, chanfro]
    J --> K[Nomes com o da caixa; _to_world]
    K --> L[Grupo FRAME: marco + ferragens do marco; OPENING_FRAME_PROP; _align; filho da caixa]
    L --> M[Por folha: grupo LEAF com a malha; ferragens filhas da folha; _align; filho do FRAME]
    M --> N{kind}
    N -- WINDOW --> O[leaf.make_leaf SLIDE: folha 0 → +X, folha 1 → −X; travel]
    N -- porta --> P[leaf.make_leaf SWING: hinge pela dobradiça, sign pelo Swing Inside, 90°]
    O --> Q[Restaura open_value e production_part]
    P --> Q
    Q --> R[btm_opening_real: kind, assembly, signature, model_version]
    R --> S[_style_cage: caixa WIRE, texto oculto]
    S --> T[True]
```

## 2. Atualizar e tecla I

```mermaid
flowchart TD
    A[sidebar_build: outdated não vazio] --> B[Aviso + botão caffmob.openings_update]
    B --> C[Para cada caixa com model_version antiga ou sem montagem: sync force]
    D[Tecla I em Object Mode] --> E{ativo selecionado dentro de porta com símbolo?}
    E -- não --> F[Evento passa ao Blender]
    E -- sim --> G[Is Left invertido no GeoNodeDoorSwing]
    G --> H[sync.sync: assinatura mudou → refaz]
    H --> I{ativo sumiu?}
    I -- sim --> J[Seleciona a primeira malha nova ou a caixa]
    I -- não --> K[INFO Giro da porta invertido]
```

## 3. Região marcada na parede (feature 011)

```mermaid
flowchart TD
    A[caffmob.wall_region] --> B[Limpa prévia e região; modal; cabeçalho]
    B --> C{Evento}
    C -- botão do meio / roda --> D[PASS_THROUGH]
    C -- Esc / botão direito --> E[Cancela: prévia limpa]
    C -- 1º clique --> F[ray_cast até IS_WALL_BP]
    F --> G[side = BACK se y local > espessura/2]
    G --> H[_local: ponto no plano da face, grade 10 mm ou 1 mm com Shift, preso à parede]
    H --> I[_live a = b = canto]
    C -- movimento com a --> J[_live b = _local]
    C -- 2º clique --> K[btm_wall_region: wall, side, x0<x1, z0<z1, active]
    K --> L[INFO Região marcada L × A. Escolha a porta ou a janela]
    L --> M[doors_windows: region_core.fit → caixa exata na região; confirmar limpa a região]
    N[draw_regions POST_PIXEL] --> O{prévia viva?}
    O -- sim --> P[Retângulo da prévia]
    O -- não --> Q{região ativa e parede existe?}
    Q -- sim --> R[Retângulo + texto L × A]
    S[Esc na vista 3D ou Limpar região] --> T[active = False]
```
