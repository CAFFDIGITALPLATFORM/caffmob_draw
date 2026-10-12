# Fluxograma do Módulo: canvas2d

Fluxo das telas 2D próprias do add-on (`caffmob_draw/canvas2d/`), no nível de documentação **Detalhado**. Re-extração
2026-10 (Fase 2c).

---

## 1. Ciclo de vida de uma tela 2D

```mermaid
flowchart TD
    A[Operador do editor chama window.open_window] --> B{Área atual é VIEW_3D?}
    B -- sim --> C[screen.area_dupli: janela nova]
    C --> D{Janela nova criada?}
    D -- sim --> E[Área = maior área da janela nova]
    D -- não --> F[Usa a área atual; guarda restore_area_type]
    B -- não --> F
    F --> G{Há área e janela?}
    G -- não --> H[RuntimeError: precisa de janela aberta]
    E --> I[prepare: IMAGE_EDITOR sem imagem, só região lateral]
    G -- sim --> I
    I --> J[Sessão guarda window_ptr e area_ptr]
    J --> K[Modal do editor roda; draw_handler POST_PIXEL desenha com draw.begin/end]
    K --> L[focus_tab por timer até a aba do editor ficar ativa]
    K --> M[OK / Cancelar]
    M --> N[close_later: timer de 50 ms fora do modal]
    N --> O{restore_area_type?}
    O -- sim --> P[Devolve menus, cabeçalho e tipo da área]
    O -- não --> Q{Janela do editor e mais de uma janela?}
    Q -- sim --> R[wm.window_close]
    Q -- não --> T[Nada: área fica como está]
    R -- RuntimeError --> S[area.type = VIEW_3D]
```

_(Revisão cruzada 2026-10-10: canvas2d/window.py:_close — `VIEW_3D` só no `except RuntimeError` de `wm.window_close`; com uma janela só ou outra janela, nada é feito)_

## 2. Eventos do mouse e sobreposição de regiões

```mermaid
flowchart TD
    A[Evento chega ao modal] --> B{over_side_panel?}
    B -- sim --> C[PASS_THROUGH: botões e campos do painel recebem]
    B -- não --> D[pixel = mouse - origem da região]
    D --> E[View2D.to_world: cursor no mundo]
    E --> F[Tratadores do editor]
```

## 3. Desenho de um quadro

```mermaid
flowchart TD
    A[draw.begin: blend ALPHA + shader UNIFORM_COLOR] --> B[rect de fundo]
    B --> C[View2D.grid_lines -> draw.lines]
    C --> D[Entidades: to_screen -> lines / dashed / box / segment]
    D --> E[Textos: draw.text traduz com tr]
    E --> F[Botões: draw.button por estado]
    F --> G[draw.end: blend NONE]
```
