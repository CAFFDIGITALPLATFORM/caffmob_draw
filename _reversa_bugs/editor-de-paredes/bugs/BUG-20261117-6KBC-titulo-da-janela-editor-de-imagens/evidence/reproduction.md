# Reprodução e diagnóstico · BUG-20261117-6KBC

- **Data:** 2026-11-17
- **Commit base:** `8caf911e`
- **Ambiente:** Windows 11, Blender 5.2.0 LTS (`fbe6228777e7`), interface em pt_BR
- **Classificação:** determinística, 1/1 (captura do titular em `evidence/titulo-editor-de-imagens.webp`)
- **Sem teste automatizado possível:** o texto vive na barra de título do sistema operacional, fora do desenho do
  add-on e fora do alcance da API Python.

## O que se vê

Na captura, a barra de título do Windows mostra "Editor de Imagens" (seta vermelha do titular). É o único ponto da
janela que não é desenhado pelo add-on: o resto da tela vem de `ops_editor.draw_plan` e dos painéis nativos.

## De onde vem o texto

1. `_reversa_bugs/editor-editor…` não desenha título: `caffmob_draw/walls2d/window.py` só abre a janela e
   `caffmob_draw/canvas2d/window.py:prepare` troca `area.type = 'IMAGE_EDITOR'`, esconde cabeçalho e menus.
2. Código-fonte do Blender (`source/blender/windowmanager/intern/wm_window.cc`, função `wm_window_title_text`):

   ```cpp
   if (win->parent || WM_window_is_temp_screen(win)) {
     /* Not a main window. */
     bScreen *screen = WM_window_get_active_screen(win);
     const bool is_single = screen && BLI_listbase_is_single(&screen->areabase);
     ScrArea *area = (screen) ? screen->areabase.first() : nullptr;
     if (is_single && area && area->spacetype != SPACE_EMPTY) {
       win_title.append(StringRef(IFACE_(ED_area_name(area).c_str())));
     }
     else {
       win_title.append(StringRef("Blender"));
     }
   ```

   Ou seja: janela criada por `screen.area_dupli` com uma área só recebe **o nome traduzido do tipo de área**
   (`IFACE_`), não o nome do `Screen`, da `Workspace` ou de um dado do add-on.
3. `bpy.types.Window` em 5.2 não tem atributo nem método de título (atributos: `height`, `width`, `parent`, `scene`,
   `screen`, `workspace`, `x`, `y`, `modal_operators`, `cursor_*`, `screenshot`, `event_simulate`, ...). Conferido em
   `docs/rag/blender-api/corpus/bpy.types.Window.md` e no resultado da sondagem MCP do registro.

## Consequência

Um add-on **não consegue** renomear a barra de título do sistema enquanto a área for do tipo Image Editor. As saídas
possíveis, e só elas:

- Desenhar o nome dentro da área do editor (controle total, mas a barra do sistema continua "Editor de Imagens").
- Trocar o tipo de área: muda o desenho inteiro (a planta é um handler de `SpaceImageEditor`) e nenhum tipo tem o
  rótulo desejado.
- Forçar uma segunda área na tela para o título cair em "Blender": efeito colateral de layout, sem ganho de nome.

Não há caminho sem efeito colateral que ponha "Editor de Paredes CAFF MOB DRAW" na barra do Windows.
