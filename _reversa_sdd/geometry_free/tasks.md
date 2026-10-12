# Geometria livre: placa e caixa (geometry_free) — Tarefas de Implementação

🟢 **CONFIRMADO** — sequência para reimplementar `caffmob_draw/geometry_free/` a partir do código de 2026-10-10. IDs RN/RF/CA de `requirements.md`; algoritmos A-xx e fluxos F-xx de `design.md`; casos EC-xx de `edge-cases.md`.

## Pré-requisitos

- [ ] 🟢 `Object.btm_plane` (`data/properties.py:BTM_PG_InsertionPlane`) com o item `'GEOMETRY'` em `object_kind`, registrado antes desta unit.
- [ ] 🟢 `data.dimension_schema.COMPONENTS` (20 itens com `code` e `label_pt`, inclusive `ESP`).
- [ ] 🟢 `data.units` (`parse_length`, `get_scene_length_unit`, `format_length`) e `data.i18n` (`tr`, `N_`) com o catálogo `data/translations/geometry_free.json` (15 chaves).
- [ ] 🟢 `hb_snap` (`main`, `event_is_pass_through`, filtro `HB_CURRENT_DRAW_OBJ` em `best_hit`).
- [ ] 🟢 Sem banco de dados, rede, variáveis de ambiente ou arquivos `.blend` próprios.

## Tarefas

- [ ] T-01, Criar `props.py`: `KINDS`, `PLANES`, `COMPONENT_ITEMS`, `LIMIT_MIN = 0.001`, `LIMIT_MAX = 10.0`, `_length(name, default, description="")` (`DISTANCE`/`LENGTH`, `precision=1`, `update=_update`), `BTM_PG_GeometryProps` com as 10 propriedades e padrões da tabela de `design.md`; `_update` com import tardio de `mesh`; `register` cria `bpy.types.Object.btm_geometry`, `unregister` remove com `hasattr` antes de desregistrar a classe (RN-04, RN-05, RN-06)
  - Origem no legado: `caffmob_draw/geometry_free/props.py`
  - Critério de pronto: registrar/desregistrar duas vezes sem erro; todo objeto expõe `btm_geometry` com `kind='PLACA'`, `plane='XY'`, medidas 0,6/0,4/0,4/0,018, `fabrication=False`, `component='ESP'`, `material='MDF'`; mudar `material` não chama `mesh.update`
  - Confiança: 🟢

- [ ] T-02, Criar `mesh.py` — funções puras `size` (A-01) e `sheets` (A-02), sem tocar o Blender (RN-02, RN-14)
  - Origem no legado: `caffmob_draw/geometry_free/mesh.py:12-39`
  - Critério de pronto: CA-10, CA-16 e as sondas de A-01/A-02 (EC-02, EC-03) reproduzidas
  - Confiança: 🟢

- [ ] T-03, `mesh.py` — `GEOMETRY_FLAG`, `_props`, `update` (A-03: cubo BMesh de lado 1, +0,5 e escala, `to_mesh`, `free`, `data.update`), `create_object(context, kind='PLACA', name=None)` (ordem: malha → objeto → `context.collection.objects.link` → idprop `IS_BTM_GEOMETRY` → `btm_plane.object_kind='GEOMETRY'` → `btm_geometry.kind` → `update`) e `is_geometry` (RN-01, RN-03)
  - Origem no legado: `caffmob_draw/geometry_free/mesh.py:42-76`
  - Critério de pronto: CA-08, CA-09; malha com 8 vértices e menor coordenada (0, 0, 0); `is_geometry` falso para objeto sem `object_kind == 'GEOMETRY'` mesmo com `btm_geometry`
  - Confiança: 🟢

- [ ] T-04, Criar `ops_create.py` — `BTM_OT_GeometryCreate` (`caffmob.geometry_create`, "Criar Geometria", `{'REGISTER','UNDO'}`, propriedade `kind`), `poll`, `invoke` (F-01.1–4), `DRAW_FLAG`, `MIN_SIZE`, helpers `_ray`, `_hit`, `_on_plane`, `_update_footprint` (A-04), `_update_height` (A-05) (RN-07 a RN-10, RN-13)
  - Origem no legado: `caffmob_draw/geometry_free/ops_create.py:21-86`
  - Critério de pronto: CA-01, CA-02, CA-06; o raycast de `hb_snap` não acerta a própria peça
  - Confiança: 🟢

- [ ] T-05, `ops_create.py` — `modal` (ordem exata da tabela de teclas de `design.md`, `tag_redraw` em todo evento), `_move`, `_advance`, `_typed_value` (F-02), `_header` (textos e formatação de `design.md`), `_finish`, `_cancel` (RN-11, RN-12)
  - Origem no legado: `caffmob_draw/geometry_free/ops_create.py:89-187`
  - Critério de pronto: CA-03, CA-04, CA-05, CA-07; o aviso do `parse_length` aparece como WARNING; a placa termina no 2º clique e a caixa no 3º; EC-05 e EC-06 reproduzem o comportamento descrito (ou são corrigidos de forma consciente, registrando a mudança)
  - Confiança: 🟢

- [ ] T-06, Criar `ops_edit.py` — `_active_geometry`, mixin `_GeometryAction` (`bl_options`, `poll`), `BTM_OT_GeometryDuplicate` (F-03), `BTM_OT_GeometryMirror` (F-04), `BTM_OT_GeometryDelete` (F-05) (RN-16 a RN-19)
  - Origem no legado: `caffmob_draw/geometry_free/ops_edit.py`
  - Critério de pronto: CA-13, CA-14, CA-15, CA-17; cópia sem `btm_uid` e com malha própria (`copy.data is not obj.data`)
  - Confiança: 🟢

- [ ] T-07, Fachada `__init__.py` (`_modules` com import tardio; `register` em `props → ops_create → ops_edit`, `unregister` invertido) e ligação no pacote: `from . import geometry_free`, `geometry_free.register()` depois de `walls2d` e antes de `ui`, `geometry_free.unregister()` depois de `ui.unregister()`, nome na lista de hot-reload
  - Origem no legado: `caffmob_draw/geometry_free/__init__.py`; `caffmob_draw/__init__.py:10,34,295,371`
  - Critério de pronto: `blender --background --factory-startup --python tests/blender_smoke.py` passa; os 4 `bl_idname` existem em `bpy.ops.caffmob` (verificação de `tests/blender_002_smoke.py:185-192`)
  - Confiança: 🟢

- [ ] T-08, Adaptador de produção (consumidor, na unit `cutting`): `geometry_records(scene)` conforme F-06 e RN-15, chamado por `part_extractor`
  - Origem no legado: `caffmob_draw/cutting/part_sources.py:274-307`; `caffmob_draw/cutting/part_extractor.py:106`
  - Critério de pronto: CA-11, CA-12; JSON global válido com as peças `FREE_GEOMETRY` (`json_exporter.validate_global_json` sem erros)
  - Confiança: 🟢

- [ ] T-09, Interface (consumidores): botões "Placa"/"Caixa" na barra lateral (grupo "Geometrias") e no Construtor; painel "Geometria" em `_draw_geometry` (campos por forma e posição, fabricação habilitando componente/matéria-prima/acabamento, linha de ações) (F-07)
  - Origem no legado: `caffmob_draw/ui/sidebar_build.py:118-122`; `caffmob_draw/ui/panels.py:260-261`; `caffmob_draw/ui/object_properties.py:250-276`
  - Critério de pronto: numa placa `XZ` o painel mostra largura, altura e espessura (sem profundidade); numa caixa, as três medidas e a espessura, sem "Posição da Placa"; `tests/blender_005_sidebar_inventory.py` sem diferença do baseline
  - Confiança: 🟢 (código) / 🟡 (desenho não verificado no Blender nesta extração)

## Tarefas de Teste

- [ ] TT-01, Testes puros de `size` e `sheets` (CA-10, CA-16, EC-02, EC-03; após DT-03/DT-04, questions.md#pergunta-66) — 🟢 viáveis hoje por extração AST (como na sonda desta extração) ou movendo as funções puras para um módulo sem `bmesh`/`bpy`
- [ ] TT-02, Smoke Blender de geometria: espessura sem mover a face de apoio, 7 peças `FREE_GEOMETRY`, JSON válido, duplicar/espelhar/excluir sem parent (CA-08, CA-11, CA-13 a CA-15) — 🟢 existe em `tests/blender_002_smoke.py:194-224` _(Revisão 2026-10-10: executado no Blender 5.2.0 LTS, OK)_
- [ ] TT-03, Smoke Blender do modal com eventos simulados: clique, arraste negativo, digitação, Esc (CA-01 a CA-07, EC-05, EC-06) — 🔴 inexistente
- [ ] TT-04, Smoke Blender com parent e escala: duplicar/espelhar uma geometria filha de um Empty girado e escalado (EC-09, EC-10) — 🟡 inexistente; cobre DT-01 (questions.md#pergunta-65)
- [ ] TT-05, Smoke Blender de identidade: Shift+D nativo numa geometria extraída e contagem de uids repetidos na lista de peças (EC-12) — 🔴 inexistente

## Ordem Sugerida

1. T-01, T-02, TT-01 (dados e funções puras).
2. T-03 (malha), T-07 (registro mínimo).
3. T-04, T-05 (criação), TT-03.
4. T-06 (edição), T-08 (produção), TT-02.
5. T-09 (interface), TT-04, TT-05.

## Lacunas Pendentes (🔴)

- 🔴 Saída externa do modal sem `cancel()` (EC-01).
- 🟢 Posição resultante de duplicar/espelhar com `parent` (EC-09) e dos filhos ao excluir (EC-14): medidas por sonda, ambas erradas em relação à intenção (ver `edge-cases.md`). 🟢 **Decisão do titular (2026-10-10, questions.md#pergunta-65):** duplicar/espelhar calculam no espaço do pai (`copy.matrix_world = obj.matrix_world @ Matrix.Translation((x, 0, 0))`; espelho idem), preservando o que o usuário vê (DT-01). 🟢 **Decisão do titular (2026-10-10, questions.md#pergunta-65):** ao excluir, os filhos mantêm a posição mundial (gravar `matrix_world` antes de remover) (DT-02). _(Revisão 2026-10-10: sonda no Blender 5.2)_
- 🔴 Origem deslocada após digitar medidas com arraste negativo (EC-06) não validada visualmente.
- 🔴 Nenhum teste puro da unit. _(Revisão 2026-10-10: smoke existente executado e aprovado)_

## Tarefas por decisão do titular (2026-10-10)

- [ ] DT-01 Em `BTM_OT_GeometryDuplicate` e `BTM_OT_GeometryMirror`, calcular no espaço do pai: `copy.matrix_world = obj.matrix_world @ Matrix.Translation((x, 0, 0))` (espelho idem) (decisão questions.md#pergunta-65)
- [ ] DT-02 Em `BTM_OT_GeometryDelete`, gravar a `matrix_world` dos filhos antes de remover o objeto e reaplicá-la, mantendo a posição mundial (decisão questions.md#pergunta-65)
- [ ] DT-03 Em `mesh.sheets`, exportar a placa sempre com `thickness` como espessura (as outras duas medidas como comprimento × largura) e avisar quando alguma medida for menor que `thickness` (decisão questions.md#pergunta-66)
- [ ] DT-04 Avisar na produção quando a caixa tiver 2 × espessura ≥ largura ou altura (decisão questions.md#pergunta-66)
