# Sondagem do addon instalado via MCP (2026-11-17)

> Blender 5.2.0 LTS, locale `pt_BR`, addon `bl_ext.mobi_caff_digital.caffmob_draw` habilitado, servidor MCP em
> 127.0.0.1:9877. Sondagem somente leitura: nenhuma alteração de cena, nenhum operador modal aberto.
> Cliente usado: `.blender-mcp/_mcp.py`.

## 1. Origem do texto do título (BUG-20261117-6KBC)

```
bpy.app.version_string ................. "5.2.0 LTS"
bpy.app.translations.locale ............ "pt_BR"
pgettext_iface("Image Editor", "*") .... "Editor de Imagens"
Area.bl_rna...enum_items["IMAGE_EDITOR"].name ... "UV/Image Editor"
```

Conclusão: o texto "Editor de Imagens" da barra da janela é a tradução pt_BR do nome de exibição do tipo de área
`IMAGE_EDITOR`, para o qual `canvas2d/window.py:prepare` troca a área. Não vem do addon. `window.title` não existe
(`hasattr(w, "title")` → `False`).

## 2. Ferramentas e modelos registrados (BUG-145, 146, 147, 150)

```
sessão btm_wall_editor.tool ....... ["SELECT", "DRAW", "INVERT", "ADD_NODE", "REMOVE_NODE"]
sessão btm_wall_editor.line ....... ["INNER", "OUTER"]
tipo de parede (wall_type) ........ ["NORMAL", "DIVISORIA", "MURETA"]
propriedades com theme/background/color ... []  (nenhuma)
paineis do editor ................. BTM_PT_wall_editor_confirm, _grid, _openings, _segment, _tools
```

Conclusões:
- Não existe ferramenta de mover parede nem de medir: a lista de ferramentas termina em REMOVE_NODE. Sustenta
  BUG-20261117-EELF e BUG-20261117-V4I3.
- Não existe nenhuma propriedade de tema, fundo ou cor na sessão. Sustenta BUG-20261117-6OXN.
- **Divergência de vocabulário a resolver com o titular**: o "Tipo de Parede" do addon é `NORMAL`, `DIVISORIA`,
  `MURETA`, e não "externo/interno". "Externo/interno" no editor é outra coisa: a **Linha** (`INNER`/`OUTER`) e a
  **Direção** (lado para onde a espessura cresce, esquerda/direita). O pedido de toggle "TIPO DE PAREDE (EXTERNO,
  INTERNO)" portanto aponta para Linha/Direção, não para o campo Tipo de Parede.

## 3. Operadores do addon (BUG-148, 149)

Da lista de 223 operadores `caffmob.*`, os que tocam o editor de paredes são `wall_editor`, `wall_editor_modal`,
`wall_editor_ok`, `wall_editor_cancel`, `wall_editor_fit` e `wall_studio_action`. Não há operador de imprimir, exportar
planta ou menu de contexto do editor. `export_cut_plan_json` é plano de corte de peças, não planta baixa.
As operações de planta do addon vivem noutro namespace (`caffmob_layouts.generate_2d_plan`, `create_plan_view`,
`export_all_to_pdf`), fora do editor.

## 4. Estado no momento da sondagem

Uma janela (`Layout`) com PROPERTIES, OUTLINER, DOPESHEET_EDITOR e VIEW_3D. Nenhuma área `IMAGE_EDITOR` aberta, então o
editor de paredes não estava aberto durante a sondagem.
