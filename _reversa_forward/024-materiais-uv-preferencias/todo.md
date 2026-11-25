# Actions: Materiais, UV por face e preferências de exibição do armário

> Identificador: `024-materiais-uv-preferencias`
> Data: `2026-11-25` (2ª rodada: `/reversa-to-do` revisado pelo `/reversa-audit`)
> Roadmap: `_reversa_forward/024-materiais-uv-preferencias/roadmap.md`
> Nenhuma ação abaixo foi executada: este é o artefato do `/reversa-to-do`, sem código de produto.
> Base das cinco decisões fechadas no clarify: textura padrão gerada em runtime, Solid com `TEXTURE`,
> UV por face EXTERNA/INTERNA/FITA, fita com UV próprio, `cabinet_color` como legado + `exibicao_armario`,
> migração idempotente por `exibicao_versao`.

## Resumo

| Métrica | Valor |
|---------|-------|
| Total de ações | 17 |
| Paralelizáveis (`[//]`) | 4 (T002, T003, T004, T006) |
| Bloqueadas pelo titular | 2 (T001, T009) |
| Maior cadeia de dependência | 7 (T004 → T005 → T008 → T016 → T012 → T013 → T014) |

**Caminhos e linhas conferidos nesta árvore** (não de memória), por `grep -n` em 2026-11-25:

| Símbolo | Arquivo:linha |
|---------|---------------|
| `space.shading.type = 'SOLID'` / `color_type = 'OBJECT'` | `caffmob_draw/hb_details.py:98` / `:99` |
| `_material` / `materiais` / `_uv_metros` / `_malha` / `_material_da_peca` | `caffmob_draw/armario_v2/build.py:309` / `:328` / `:390` (chamada em `:431`) / `:412` / `:608`; atribuição de material `:649-659` |
| `_write` / `solid_material` / `apply_material` / `update` | `caffmob_draw/edgeband/build.py:18` / `:32` / `:47` / `:57` |
| `use_color` / `length` | `caffmob_draw/edgeband/props.py:44` / `:41` |
| `class BTM_PG_ArmarioV2` / `gerado` | `caffmob_draw/armario_v2/props.py:197` / `:267` |
| `_MODULES` | `caffmob_draw/armario_v2/__init__.py:30` |
| `class BTM_AddonPreferences` / `cabinet_color` / `layout.prop(self, "cabinet_color")` | `caffmob_draw/__init__.py:146` / `:185` / `:304` |
| `cabinet_color` **lido** por `obj.color` | `caffmob_draw/product_libraries/frameless/operators/ops_placement.py:40` |
| `set_recommended_settings` / `turn_off_3d_cursor` / `turn_on_object_color_type` / texto REQUIRED | `caffmob_draw/ops.py:30` / `:54` / `:39` / `:110` |
| Aviso "Object Color Type is not enabled!" | `caffmob_draw/ui/view3d_sidebar.py:38-46` |
| `Scene.btm_view_mode` / `btm_view_lines` / `apply` / `settings` | `caffmob_draw/ui/view_mode.py:51/54/26`; `caffmob_draw/ui/view_mode_core.py:24` |
| Controle Sólido·Textura + Linhas na barra lateral | `caffmob_draw/ui/sidebar_build.py:23-33` (`draw_view_mode`) |
| `LAYER_UV` | `caffmob_draw/texture_library/uv_core.py:24` |
| `load_post` de referência (`@persistent`) | `caffmob_draw/armario_v2/anim.py:362`, `:400-407` |
| Catálogos de tradução dos rótulos novos | `caffmob_draw/data/translations/armario_v2.json`, `ops.json`, `ui.json` |

## Fase 1, Confirmação e propriedades

| ID | Descrição | Dep | Par. | Arquivo-alvo | Prova | Status |
|----|-----------|-----|------|--------------|-------|--------|
| T001 | **“Cursos 3D” confirmado pelo titular (2026-11-25): é o checkbox “Turn Off 3D Cursor”** (`turn_off_3d_cursor`, `caffmob_draw/ops.py:54`), do diálogo `caffmob.set_recommended_settings` (`ops.py:30-110`). Decisão: **preservar intacto** — nenhuma linha desse controle muda. A conferência na GUI deixou de ser bloqueio e virou asserção de teste na T016 | - | - | `caffmob_draw/ops.py` | `tests/blender_024_exibicao.py` (T016) afirma que `turn_off_3d_cursor` continua existindo e que só o controle de cor mudou | `[x]` **respondida em 2026-11-25** |
| T002 | Acrescentar em `BTM_PG_ArmarioV2` (`props.py:197`, junto de `gerado` em `:267`) `exibicao_versao` (Int, default 0) e `exibicao` (Enum `TEXTURA_SO`/`TEXTURA_LINHAS`, default fixo `TEXTURA_SO` — `bpy.props` não herda default de preferência; a preferência é aplicada na geração/migração) | - | `[//]` | `caffmob_draw/armario_v2/props.py` | `tests/blender_024_exibicao.py` (novo): criar raiz e ler/gravar os dois campos; `python docs/rag/tools/check_api.py` sem `[UNKNOWN in 5.2]` | `[ ]` |

## Fase 2, Núcleos puros (sem `bpy`)

| ID | Descrição | Dep | Par. | Arquivo-alvo | Prova | Status |
|----|-----------|-----|------|--------------|-------|--------|
| T003 | Criar `armario_v2/face_uv_core.py`: classificar cada face em `EXTERNA`, `INTERNA` ou `FITA` a partir da normal, do centro da caixa e do sinal do espelho, e devolver o retângulo UV em metros no referencial da peça; reusar `texture_library/uv_core.LAYER_UV` (`:24`) em vez de repetir o nome do layer | T002 | `[//]` | `caffmob_draw/armario_v2/face_uv_core.py` | `tests/test_face_uv_024.py` (novo): caixa 600×720×18, face normal +Y = EXTERNA e oposta = INTERNA; peça espelhada mantém o canto; importável sem `bpy` | `[ ]` |
| T004 | Criar `armario_v2/mdf_core.py`: gerador **puro e determinístico** dos bytes RGBA da textura MDF claro (512×512, semente fixa, grão fino), sem `bpy` e sem rede | - | `[//]` | `caffmob_draw/armario_v2/mdf_core.py` | `tests/test_mdf_core_024.py` (novo): dois chamados produzem o mesmo `bytes`; tamanho = 512×512×4; variação dentro da faixa clara | `[ ]` |
| T005 | Levar o resultado de `mdf_core` para `bpy.data.images` **empacotada** (`pack()`), num módulo de cena `armario_v2/textura_padrao.py`, e usá-lo em `build.py:_material` (`:309`), que alimenta `materiais` (`:328`): `ShaderNodeTexImage` + `Mapping` em 1/tamanho em metros. Preservar `_material_da_peca` (`:608`) e a atribuição por peça (`:649-659`): peça com material escolhido continua vencendo | T003, T004 | - | `caffmob_draw/armario_v2/textura_padrao.py`, `caffmob_draw/armario_v2/build.py` | `tests/blender_024_textura.py` (novo): material da chapa tem nó `TEX_IMAGE` com `image.packed_file`; peça com material do usuário continua com o dele após `caffmob.armario_v2_gerar` | `[ ]` |
| T006 | Dar UV próprio à faixa de fita em `edgeband/build.py:_write` (`:18`, geometria criada em `:19-27`) e `update` (`:57`): layer `UVMap`, **U = comprimento da faixa em metros**, **V = largura da fita em metros**, a partir de `core.band_box` (`edgeband/core.py:193`); `solid_material` (`:32`) e `apply_material` (`:47`) continuam valendo quando `use_color` (`edgeband/props.py:44`) | - | `[//]` | `caffmob_draw/edgeband/build.py` | `tests/blender_024_uv.py` (novo): faixa gerada tem `UVMap`; Umax−Umin ≈ comprimento, Vmax−Vmin ≈ largura | `[ ]` |
| T007 | Fazer `build.py:_uv_metros` (`:390`, chamado por `_malha` em `:431`) delegar o retângulo a `face_uv_core`, mantendo o layer `UVMap` e a unidade metro; nenhuma mudança de geometria | T003 | - | `caffmob_draw/armario_v2/build.py` | `tests/blender_024_uv.py`: faces externa/interna de uma chapa não compartilham o mesmo retângulo; `tests/blender_017_armario_smoke.py` continua OK | `[ ]` |

## Fase 3, Exibição e preferências

| ID | Descrição | Dep | Par. | Arquivo-alvo | Prova | Status |
|----|-----------|-----|------|--------------|-------|--------|
| T008 | Trocar `space.shading.color_type = 'OBJECT'` por `'TEXTURE'` em `hb_details.py:99`, mantendo `shading.type = 'SOLID'` (`:98`); nenhum outro fluxo é tocado — `hb_utils.set_layout_shading` (`:384`), `hb_layouts` (render 2D) e `catalog/render_thumbnails.py:154` **ficam como estão** | T005 | - | `caffmob_draw/hb_details.py` | `tests/blender_024_exibicao.py`: após o fluxo de detalhes, `space.shading.color_type == 'TEXTURE'` num `VIEW_3D` de teste | `[ ]` |
| T016 | **Diálogo de preferências recomendadas** (`ops.py:30-110`): `turn_on_object_color_type` (`:39`) deixa de ser “REQUIRED”/`'OBJECT'` e passa a aplicar `'TEXTURE'` (rótulo em `:110`); `turn_off_3d_cursor` (`:54`, o “Cursos 3D” da T001), `show_wireframes`, `turn_off_relationship_lines`, `change_studio_lighting` e `use_vertex_snapping` ficam **intactos** | T001, T008 | - | `caffmob_draw/ops.py` | `tests/blender_024_exibicao.py`: executar o operador com defaults e ler `shading.color_type == 'TEXTURE'`; `git diff` mostra que só as linhas do controle de cor mudaram | `[ ]` |
| T017 | **Aviso da barra lateral**: `ui/view3d_sidebar.py:38-46` acusa “Object Color Type is not enabled!” quando `color_type != 'OBJECT'`; com o Solid em `TEXTURE` o aviso passaria a acusar erro sempre. A condição passa a aceitar `TEXTURE` (e o texto/rótulo acompanham) | T008 | - | `caffmob_draw/ui/view3d_sidebar.py` | `tests/blender_024_exibicao.py`: com `color_type = 'TEXTURE'` o bloco de erro não é desenhado (contagem de `layout.label`/flag) | `[ ]` |
| T009 | **Preferência de exibição**: criar `exibicao_armario` (Enum `TEXTURA_SO`/`TEXTURA_LINHAS`, default `TEXTURA_SO`) em `BTM_AddonPreferences` (`__init__.py:146`, junto de `cabinet_color` em `:185`) e desenhá-lo; **manter** `cabinet_color` e a linha `layout.prop(self, "cabinet_color")` (`:304`) — esse valor é lido em `ops_placement.py:40` como `obj.color` dos armários das bibliotecas herdadas, não é a opção “Cor por objeto”. Nenhuma outra preferência é removida (`show_legacy_libraries`, `panel_mode`, `stick_magnet`, `mobi_url`, cores de parede/porta/anotação) | T001 | - | `caffmob_draw/__init__.py` | `tests/blender_024_prefs.py` (novo): enum com exatamente 2 itens; `cabinet_color` e o `layout.prop` continuam; demais preferências intactas | `[ ]` (dois níveis: preferência + `Scene.btm_view_mode`) |
| T010 | **Aplicar a variante sem criar mecanismo novo**: `armario_v2/exibicao.py` mapeia `exibicao_armario`/`btm_armario.exibicao` para o modo de vista já existente — `TEXTURA_SO` → `TEXTURE` + linhas desligadas, `TEXTURA_LINHAS` → `TEXTURE` + linhas ligadas — chamando `ui/view_mode_core.settings` (`:24`) e `ui/view_mode.apply` (`:26`), que já gravam `color_type`/`show_wireframes`/limiar em todas as vistas e reaplicam no `load_post`. Nada de `show_object_outline` nem objeto wireframe por peça | T005, T009 | - | `caffmob_draw/armario_v2/exibicao.py` | `tests/blender_024_exibicao.py`: alternar a variante muda `overlay.show_wireframes` sem trocar material; `tests/test_view_mode.py` continua OK | `[ ]` (linhas globais confirmadas em 2026-11-25) |
| T011 | Migração idempotente: handler `load_post` no módulo `exibicao.py` (padrão de `armario_v2/anim.py:362`, `:400-407`, com `@persistent` e remoção no `unregister`) que percorre raízes de `Marcenaria` com `exibicao_versao == 0`, aplica a textura padrão só nas peças sem material, grava `1` e avisa **uma vez**; registrar o módulo em `_MODULES` (`armario_v2/__init__.py:30`) e removê-lo no `unregister` | T002, T005 | - | `caffmob_draw/armario_v2/exibicao.py`, `caffmob_draw/armario_v2/__init__.py` | `tests/blender_024_migracao.py` (novo): primeira passada migra e conta 1 aviso; segunda passada não altera nada; após `unregister()` o handler não está em `bpy.app.handlers.load_post` | `[ ]` |

## Fase 4, Fechamento

| ID | Descrição | Dep | Par. | Arquivo-alvo | Prova | Status |
|----|-----------|-----|------|--------------|-------|--------|
| T012 | **i18n bilíngue** de todos os rótulos novos/alterados: “Textura”, “Somente textura”, “Textura com linhas” e o aviso de migração em `data/translations/armario_v2.json`; o rótulo do controle em `ops.json` (`:218-224`, hoje “Turn On Object Color Type”/“- REQUIRED”) e o aviso em `ui.json` (`:778`). `pt_BR` **e** `en_US` preenchidos, sem texto montado por f-string | T008, T016, T017, T009, T010, T011 | - | `caffmob_draw/data/translations/armario_v2.json`, `ops.json`, `ui.json` | `cd tests && python -m unittest test_i18n_coverage` (comando conferido nesta árvore: 3 testes OK); o teste reprova texto novo sem as duas línguas | `[ ]` |
| T013 | Atualizar `onboarding.md` com o resultado real dos passos 1–4 e rodar a bateria | T005, T006, T007, T008, T009, T010, T011, T012, T016, T017 | - | `_reversa_forward/024-materiais-uv-preferencias/onboarding.md` | `tests/test_face_uv_024`, `test_mdf_core_024`, `blender_024_*`, `blender_017_armario_smoke`, `blender_023_fase7`, `blender_023_desempenho`, suíte pura (`python -m unittest` em `tests/`), `docs/rag/tools/check_api.py` | `[ ]` |
| T014 | **Offline e UNDO**: rodar os ensaios da 024 com `CAFFMOB_BASE` vazio e sem `--online-mode`, confirmando zero chamada de rede; conferir que o handler novo tem remoção no `unregister` (T011) e que nenhum operador novo declara `UPDATE`/`UNDO` sem desfazer o que criou | T013 | - | `tests/` | `CAFFMOB_BASE= blender --background --factory-startup --python-exit-code 1 --python tests/blender_024_*.py` sem acesso de rede; `grep -n "bl_options"` nos arquivos tocados; `grep -n "load_post" caffmob_draw/armario_v2/exibicao.py` com append **e** remove | `[ ]` |
| T015 | Verificação visual em sessão gráfica: grão do MDF, Solid/Preview/render iguais, contorno da variante “com linhas”, aviso de migração, e o diálogo de preferências recomendadas sem o “REQUIRED” de cor de objeto | T013 | - | `_reversa_forward/024-materiais-uv-preferencias/onboarding.md` §5 | Checklist preenchido na GUI | `[ ]` **requer GUI** |

## Ordem recomendada

1. **T001** (GUI, bloqueia T009/T016) e **T002, T003, T004, T006** em paralelo — T002/T003/T004/T006 não compartilham arquivo.
2. **T005** fecha a textura padrão (T003 + T004); **T007** fecha o UV da chapa (T003).
3. **T008 → T016/T017**: o Solid passa a `TEXTURE` antes de o diálogo e o aviso deixarem de exigir `OBJECT`; nessa ordem, nenhum estado intermediário acusa erro ao usuário.
4. **T009** depois de T001; **T010** depois de T005 + T009 (reusa `view_mode`, sem mecanismo novo).
5. **T011** fecha a migração; **T012** traduz os rótulos que T008/T016/T017/T009/T010/T011 criaram.
6. **T013 → T014** medem e provam offline/UNDO; **T015** valida na GUI.

## Lacunas

**Nenhuma.** As quatro perguntas abertas pelo `/reversa-audit` foram respondidas pelo titular em
2026-11-25 e estão integradas em `requirements.md` §6 (sessão 2) e no roadmap (D-05, D-06 e D-08):

1. Cursos 3D = “Turn Off 3D Cursor” (`turn_off_3d_cursor`, `ops.py:54`) — preservar intacto.
2. `color_type` global — paredes, portas e armários herdados mostram a cor média do material no Solid.
3. “Textura com linhas” reusa o interruptor Linhas existente (`overlay.show_wireframes`).
4. Dois níveis: `exibicao_armario` (padrão de fábrica) + `Scene.btm_view_mode` (estado do arquivo).

> A pergunta “asset PNG vs. textura em runtime” também segue fechada (decisão 1 do clarify). Nada impede o
> `/reversa-coding`; nenhuma pergunta foi reaberta.

## Notas de execução

> Reservado para `/reversa-coding`. Nada executado nesta rodada: só documentação de reversa foi escrita.

## Histórico de alterações

| Data | Alteração | Autor |
|------|-----------|-------|
| 2026-11-25 | Versão inicial do `/reversa-to-do` (15 ações) | reversa |
| 2026-11-25 | 2ª rodada: to-do revisado pelo `/reversa-audit` — T009 corrigida (o “Cor por objeto” real é o diálogo de `ops.py`, não `cabinet_color`), T010 passou a reusar `ui/view_mode_core`, criadas T016 (diálogo recomendado) e T017 (aviso da barra lateral), T012 ampliada para `ops.json`/`ui.json`, lacuna do asset removida (decisão já fechada). 17 ações | reversa |
| 2026-11-25 | 3ª rodada: `/reversa-clarify` (2ª sessão) — três das quatro perguntas respondidas (Cursos 3D = `turn_off_3d_cursor`; `color_type` global; linhas globais). T001 fechada; resta 1 pergunta (preferência vs. `Scene.btm_view_mode`). Nenhum código tocado | reversa |
| 2026-11-25 | 4ª rodada: 4ª resposta do clarify integrada (dois níveis: `exibicao_armario` + `Scene.btm_view_mode`); T009 desbloqueada e §Lacunas zerada. Nenhum código tocado | reversa |
