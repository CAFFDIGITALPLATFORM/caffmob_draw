# Investigation: Seleção por componente e região na parede

> Identificador: `011-selecao-por-componente`
> Data: `2026-10-09`

## 1. O que já existe no código

| Tema | Onde | Achado |
|------|------|--------|
| Observação da seleção | `ui/sidebar_selection.py` (l. 14-49) | `msgbus` em `(LayerObjects, "active")`, refeito no `load_post`; só abre a seção Selecionado, não muda a seleção |
| Handlers `depsgraph_update_post` | `aggregates/collision.py:164`, `aggregates/apply.py:110`, `collision/stale.py:59`, `stick/apply.py:317`, `cabinet_editor/reflow_handler.py:60` | Nenhum mexe na seleção; o novo handler precisa conviver com eles (sair cedo, trava de reentrada) |
| Clique na viewport | `operators/viewport_hud.py` (l. 818-829) | O HUD prende `LEFTMOUSE PRESS` `any=True, head=True`; um clique fora dos widgets passa adiante (`PASS_THROUGH`) |
| Modos de seleção de armários | `frameless_selection_mode` (`props_hb_frameless.py:1348`), `face_frame_selection_mode` e `closet_selection_mode` (com `..._enabled`) | Mostram as caixas e selecionam a caixa do nível escolhido; não sobem a seleção |
| Raízes | `selection/classify.py` (`classify`, `module_root`, `free_group`, `movable_root`) | Já resolvem porta, janela, módulo e grupo; `movable_root` é o que o "Mover sobre" usa |
| Exclusão | `aggregates/ops_aggregate.py` (l. 202-293); `operators/doors_windows.py` (l. 1317-1350); `operators/ops_general.py` (l. 80-215) | Só o `delete_with_aggregates` está em X/Delete. `delete_door_window` apaga só os filhos diretos (defeito) |
| Importação | `aggregates/ops_import.py` (l. 85-115) | Malhas soltas, selecionadas, com aviso "Selecione o pai por último…" |
| Retângulo na parede | `operators/walls.py#draw_wall_cutter` (l. 5516-5700) | Raycast até `IS_WALL_BP`, projeção no plano local Y = 0, retângulo em X/Z locais, prévia por `draw_handler` |
| Inserção de porta | `operators/doors_windows.py#_PlaceWallObjectBase` (l. 694-1055) | Enter só aplica o valor digitado; clique coloca (`cut_wall` + `_sync_opening`); modo D de largura por dois pontos |

## 2. API do Blender 5.2 consultada

- `bpy.ops.view3d.select(*, extend, deselect, toggle, deselect_all, select_passthrough, center, enumerate, object, location)`:
  `docs/rag/blender-api/corpus/bpy.ops.view3d.md#bpy.ops.view3d.select`. O `enumerate` é o Alt + clique padrão do
  Blender (lista os objetos sob o cursor). O D-04 passa na frente dele com o interruptor ligado.
- `bpy.app.handlers.depsgraph_update_post` (aceita `scene` e `depsgraph`):
  `docs/rag/blender-api/corpus/bpy.app.handlers.md#bpy.app.handlers.depsgraph_update_post`. Alterar dados no handler
  pede cuidado (seção "Note on Altering Data"); aqui só se altera a seleção, com trava de reentrada.
- `obj.select_set` em vez de `bpy.ops.object.select_all`: `docs/rag/project/04_armadilhas.md` (operadores são lentos
  e empilham undo).
- `draw_handler_add` `POST_VIEW` e remoção em todos os caminhos de saída: `docs/rag/project/02_padroes_blender_5_2.md`
  (modal + GPU).

## 3. Alternativas avaliadas

| Tema | Alternativa | Veredito |
|------|-------------|----------|
| Onde promover a seleção | Sobrescrever `view3d.select` no keymap | Descartada como mecanismo único: não cobre caixa, laço, lista de objetos e `select_all`. Fica como plano B só do clique-arrasto (D-03) |
| | `msgbus` do objeto ativo | Descartada: a seleção por caixa não troca necessariamente o ativo |
| | `depsgraph_update_post` com assinatura da seleção | **Escolhida** (D-02) |
| Editar uma peça | Duplo clique entra no componente (estilo SketchUp) | Descartada pelo titular (Q2); Alt + clique escolhido |
| Exclusão | Operador novo em X/Delete | Descartada: dois itens `head=True` no mesmo evento não têm ordem garantida; o `delete_with_aggregates` é ampliado |
| Região | Objeto cortador na cena (como `create_wall_cutter`) | Descartada: sujaria o arquivo e o undo; a região é estado de sessão |
| | Reaproveitar um recorte já existente | Descartada pelo titular (Q3) |
| Marca de raiz | Propriedade nova `is_component_root` em todo objeto | Descartada: as marcas atuais (`IS_*_BP`, `btm_group`, `btm_object_item`, tags de módulo) já bastam, e evita migração |

## 4. Padrões do projeto aplicados

- Núcleo puro com objetos simulados (`.get()`, `.parent`) como em `tests/test_classify.py` e `tests/test_grouping.py`.
- Fumaças em fundo por feature (`tests/blender_0NN_*_smoke.py`), padrão da 004 a 010.
- Textos com `tr()` e `N_()` (`data/i18n.py`) e catálogos por área.
