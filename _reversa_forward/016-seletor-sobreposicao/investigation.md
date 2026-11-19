# Investigation: Seletor de objetos sobrepostos da viewport 3D

> Identificador: `016-seletor-sobreposicao`
> Data: `2026-11-19`

## 1. O que já existe no código

| Tema | Onde | Achado |
|------|------|--------|
| Raio por objeto | `.cloud-attachments/…ba0ce0c5b.txt#_objects_under_cursor` (anexo) | Percorre o view layer, filtra `MESH`, `visible_get()` e `hide_select`, e faz `evaluated.ray_cast` por objeto, com origem e direção convertidas para o espaço local. Ordena por distância em mundo |
| Painel da lista | Anexo, `VIEW3D_OT_overlap_selector._draw` e `_panel_geometry` | Painel de 390 px, 12 linhas visíveis, 25 px por linha, cabeçalho de 78 e rodapé de 62, preso à região ao lado do cursor |
| Isolamento | Anexo, `_toggle_isolation` | `hide_set` em todos os objetos do view layer, com `original_hidden` guardado e restaurado |
| Seleção preparada | Anexo, `_preview_object` e `_finish` | O anexo usa a seleção viva como pré-visualização; a feature troca isso por destaque (RN-04) |
| Keymap | `selection/component_pick.py#register` | `LEFTMOUSE` / `CLICK`, `alt=True`, `shift` em `(False, True)`, `head=True`, no mapa `3D View` de `keyconfigs.addon`, com poll por `scene.btm_component_select` |
| Menu de contexto | `ui/context_menu.py#draw_context_menu` | `prepend` em `VIEW3D_MT_object_context_menu`; usa `sidebar_vocab.draw_action` e `layout.operator_context` |
| Desenho 2D | `canvas2d/draw.py` | `begin`, `end`, `rect`, `outline`, `text`, `line` sobre `compat.get_builtin_shader` e `hb_gpu_draw`; usado por `move_over/ops_dialog.py` em `POST_PIXEL` |
| Hit test de retângulo | `hb_gpu_draw.point_in_rect` | Usado pelo painel da biblioteca e pelos diálogos; evita reimplementar clique em botão |
| Desenho 3D por objeto | `aggregates/overlay.py#_draw_3d` | `POST_VIEW` com `line_width_set` sobre cantos de `bound_box`; é o modelo do destaque do foco |
| Registro | `caffmob_draw/__init__.py` | `_submodule_names` para hot-reload; as cascatas de `register()` e `unregister()`; os módulos de seleção entram num laço próprio |
| Normalizador de seleção | `selection/component_select.py#on_depsgraph_update` | Troca peças por raízes a cada atualização; por isso a inspeção não pode selecionar (RN-03, RN-04) |
| Traduções | `data/i18n.py`, `data/translations/*.json` | `tr`/`N_`, dois idiomas obrigatórios, um dono por texto; `tests/test_i18n_coverage.py` cobre as áreas entregues |
| Identidade | `tests/test_identity.py` | Todo `bl_idname` começa com `caffmob`; uma aba só na barra lateral |

## 2. API do Blender 5.2 consultada

- `bpy.types.SpaceView3D.draw_handler_add(callback, args, 'WINDOW', 'POST_VIEW' | 'POST_PIXEL')` e
  `draw_handler_remove(handle, 'WINDOW')`: `docs/rag/blender-api/corpus/bpy.types.SpaceView3D.md`. O `POST_PIXEL`
  recebe a região em pixels com origem embaixo à esquerda, como `canvas2d/view.py` já documenta.
- `bpy_extras.view3d_utils.region_2d_to_origin_3d(region, rv3d, coord, clamp=…)` e
  `region_2d_to_vector_3d(region, rv3d, coord)`: `docs/rag/blender-api/corpus/bpy_extras.view3d_utils.md`; é o par
  que o anexo usa para montar o raio.
- `Object.ray_cast` e `Object.evaluated_get(depsgraph)`: o cast é no espaço local do objeto e precisa da matriz
  invertida; `depsgraph` vem de `context.evaluated_depsgraph_get()`.
- `Object.hide_get()` e `Object.hide_set(hide)` com `SpaceView3D.local_view` desligado: `bpy.types.Object.md`.
  Restringir o `hide_set` a objetos do view layer evita `RuntimeError` em objeto de outra cena ou de coleção não
  ligada.
- `Window.mouse_x` e `Window.mouse_y`: coordenadas de janela, usadas só no caminho do menu de contexto (D-08).
- `gpu.state.line_width_set`, `gpu.state.blend_set`: `docs/rag/blender-api/corpus/gpu.state.md`; o projeto já usa
  ambos em `overlays/draw_handlers.py` e `aggregates/overlay.py`.
- `bpy.app.handlers.load_post` não entra: o seletor não sobrevive a abrir outro arquivo, porque é modal.

## 3. Alternativas avaliadas

| Tema | Alternativa | Veredito |
|------|-------------|----------|
| Detecção | `scene.ray_cast` | Descartada: devolve só o primeiro impacto, e a feature existe para os de trás (RN-02) |
| | Varrer `depsgraph.object_instances` | Descartada por Q2: instâncias de Geometry Nodes ficam Won't nesta versão |
| | `view3d.select(enumerate=True)` | Descartada: a lista do Blender não tem marcação, isolamento nem confirmação; e o item do componente já passa na frente desse combo |
| Pré-visualização | Selecionar o objeto em foco, como o anexo | Descartada: o normalizador de `component_select.py` reagiria a cada `MOUSEMOVE` e a seleção do usuário mudaria (RN-03/RN-04) |
| | Destaque por malha branca avaliada | Descartada: exigiria batch novo por troca de foco, com custo e descarte de memória |
| | Caixa envolvente em `POST_VIEW` | **Escolhida** (D-04): sem `to_mesh`, sem tocar na seleção |
| Isolamento | `view3d.localview` | Descartada (Q3): isola o que está selecionado e reenquadra a vista |
| | `hide_viewport` | Descartada: é outro interruptor e o usuário não o reconhece como temporário |
| | `hide_set` com mapa guardado | **Escolhida** (D-06) |
| Atalho | `Alt + Shift + clique` do anexo | Descartada: é o "somar à seleção" de `caffmob.component_pick` |
| | Tecla sem mouse (`Ctrl + Alt + O`) | Descartada: menos descoberta que o clique, e o menu cobre quem não decora |
| | `Ctrl + Alt + botão esquerdo` + item de menu | **Escolhida** (D-07), por Q1 e pela sonda que mostrou os oito combos de `LEFTMOUSE` ocupados |
| Onde mora o código | Módulo em `overlays/` | Descartada: `overlays` desenha informação permanente; o seletor é interação de seleção de sessão |
| | Pacote novo `overlap/` na raiz | Descartada: a feature usa `classify` e convive com o normalizador de `selection/`; um pacote novo para dois arquivos não se paga |
| | `selection/overlap_core.py` + `selection/overlap_select.py` | **Escolhida** (D-01, D-02) |
| Registro | Registrar dentro de `selection/__init__.py` | Descartada: o pacote é só docstring hoje, e as cascatas do add-on já chamam módulo por módulo |

## 4. Sondas feitas no Blender 5.2 (2026-11-19)

| Sonda | Resultado |
|-------|-----------|
| Keymap do mapa `3D View` com janela aberta | 116 itens; os oito combos de `LEFTMOUSE` são `view3d.select`, o que confirma a necessidade de `head=True` |
| Keymap em `--background` | O mapa vem com 0 itens de `LEFTMOUSE`; sonda de keymap exige janela |
| `ray_cast` em curva (`CURVE`) e texto (`FONT`) | Devolve falso e o `ev.type` não é `MESH`; numa cena mista, uma chamada em curva derrubou o Blender com `EXCEPTION_ACCESS_VIOLATION` (exit 11) uma vez, não reproduzida isoladamente |
| Malha com Geometry Nodes que instancia cubos | Geometria avaliada com `vertices=0` e `faces=0`; o `ray_cast` devolve falso, porque as instâncias não fazem parte da malha do objeto |
| `view3d.localview` | Isola o que está selecionado e reenquadra a vista, o que contraria RN-03/RN-04 |

## 4.1 Medição do raio por objeto (T001, 2026-11-19)

Sonda `probe_rays.py` (nesta pasta), em `--background --factory-startup`: 2.000 malhas com a mesma malha em cubos de
0,2 m empilhados na frente do raio, câmera sintética com origem em `(0, -6, 1.6)` e alvo em `(0, 0, 1.2)`.

| Métrica | Valor |
|---------|-------|
| Candidatos por passada (`MESH`, visível, selecionável) | 2.001 |
| Objetos com impacto no raio | 287 |
| Passadas medidas (s) | 0,014 / 0,015 / 0,015 / 0,018 / 0,019 |
| Mediana | 0,015 s |
| Pior caso | 0,019 s |

Conclusão: o algoritmo de D-03 cabe folgado no limite de 1 s do RNF de desempenho, então **não entra poda** por caixa
envolvente nem cache: o filtro `MESH` + `visible_get()` + `hide_select` antes do `ray_cast` basta.

## 5. Padrões do projeto aplicados

- Núcleo puro com objetos simulados (`.get()`, `.parent`, atributos simples), como `tests/test_classify.py`.
- Fumaça em fundo por feature (`tests/blender_0NN_*_smoke.py`), padrão das features 004 a 015.
- Texto com `tr()`/`N_()`, catálogo por área, e `tests/test_i18n_coverage.py` barrando texto novo sem tradução.
- Modal com `draw_handler_add` guardado na instância e removido em todos os caminhos, como `move_over/ops_dialog.py`
  e `openings/region.py`.
- Operador com prefixo `caffmob.` e `bl_options` coerente com o que ele muda (`{'INTERNAL'}` quando não muda dado).
