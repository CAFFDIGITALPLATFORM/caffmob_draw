# Cotas de Módulo (measure) — Tarefas de Implementação

🟢 **CONFIRMADO** — sequência para reimplementar `caffmob_draw/measure/` a partir do código de 2026-10-10. IDs RN/RF/CA de `requirements.md`; fluxos F-xx de `design.md`; casos EC-xx de `edge-cases.md`.

## Pré-requisitos

- [ ] 🟢 `data/i18n.py` com `tr(msgid)` (devolve o texto fora do Blender) e `N_(msgid)`.
- [ ] 🟢 `selection/classify.py:classify` com `MODULE`, `PART`, `FRONT` e `Classified.root`.
- [ ] 🟢 `hb_types.GeoNodeObject(obj).get_input` (`Dim X/Y/Z`) e `hb_types.GeoNodeWall(obj).get_input` (`Length`, `Thickness`, `Height`), levantando `ValueError` em falha.
- [ ] 🟢 `hb_placement.PlacementMixin.get_wall_children_sorted(wall, exclude_obj, object_z_start, object_height)` conforme `_reversa_sdd/hb_placement/requirements.md` RN-12 e `design.md` › Contrato consumido.
- [ ] 🟢 `hb_project.get_main_scene()` e `Scene.home_builder.ceiling_height`.

## Tarefas

- [ ] T-01, Criar `cotas.py` puro: `Cotas`, `Placement`, `FIELDS`, `LABELS` (com `N_`), `_vertical_overlap` estrito e `limits` (F-01, RN-03)
  - Origem no legado: `caffmob_draw/measure/cotas.py:Cotas/Placement/FIELDS/LABELS/_vertical_overlap/limits`
  - Critério de pronto: CA-06; o módulo importa sem `bpy`; obstáculo que cruza em X é ignorado; encostar em X conta e em Z não (EC-04, EC-05)
  - Confiança: 🟢

- [ ] T-02, Implementar `compute` (RN-02) e `compute_free` (laterais e afastamento `None`)
  - Origem no legado: `caffmob_draw/measure/cotas.py:compute/compute_free`
  - Critério de pronto: CA-01; `compute_free` devolve `superior = ceiling − (z0 + height)`
  - Confiança: 🟢

- [ ] T-03, Implementar `apply` na ordem de F-02 (negativo primeiro; mensagens "Valor Inválido…" traduzidas com `tr` e rótulo de `LABELS`; campo desconhecido com mensagem não traduzida) (RN-04, RN-05)
  - Origem no legado: `caffmob_draw/measure/cotas.py:apply`
  - Critério de pronto: CA-02, CA-03, CA-04; dimensões nunca mudam; tolerância `1e-9` na ponta direita da parede; sem validação de vizinho oposto nem de teto (EC-01, EC-02, comportamento atual)
  - Confiança: 🟢

- [ ] T-04, Implementar `slide(placement, obstacles, wall_length, target_x0, avoid=True)` (RN-12)
  - Origem no legado: `caffmob_draw/measure/cotas.py:slide`
  - Critério de pronto: CA-07; módulo mais largo que a parede fica em `x0 = 0` (EC-14)
  - Confiança: 🟢

- [ ] T-05, Criar `scene_cotas.py`: `_dims` (RN-09), `_wall_of` (`IS_WALL_BP`), `_wall_thickness` (falha → 0,0), `_on_front_side` (RN-07, 0,01 rad e meia espessura)
  - Origem no legado: `caffmob_draw/measure/scene_cotas.py:_dims/_wall_of/_wall_thickness/_on_front_side`
  - Critério de pronto: módulo Frameless lê `Dim X/Y/Z`; módulo rápido lê `btm_cabinet`; módulo girado 180° atrás da parede não é `on_wall`
  - Confiança: 🟢

- [ ] T-06, Implementar `ceiling_height(scene, wall=None)` (F-04, RN-08) com import tardio de `hb_project`
  - Origem no legado: `caffmob_draw/measure/scene_cotas.py:ceiling_height`
  - Critério de pronto: CA-08; ordem cena principal → `Height` da parede → 2,6
  - Confiança: 🟢

- [ ] T-07, Implementar `ModuleCotas` (F-03, `obstacles` com RN-10, `compute`, `apply` com F-05) e `for_object` (F-07, RN-13)
  - Origem no legado: `caffmob_draw/measure/scene_cotas.py:ModuleCotas/for_object`
  - Critério de pronto: CA-05, CA-09; `apply` inválido não escreve `location`; na parede grava `(x0, back_y, z0)`; livre soma só o Δz; anotações e snap lines não são obstáculos
  - Confiança: 🟢

- [ ] T-08, Criar `__init__.py` só com a docstring (sem `register`)
  - Origem no legado: `caffmob_draw/measure/__init__.py`
  - Critério de pronto: `from caffmob_draw.measure import cotas` funciona fora do Blender; nada a registrar em `caffmob_draw/__init__.py`
  - Confiança: 🟢

- [ ] T-09, Integrar os consumidores: campos virtuais e caixa "Cotas" do painel (`ui/object_properties.py`: `BTM_PG_SelectionEdit` com 5 `FloatProperty` `DISTANCE`/`LENGTH`/`precision=1` e `_guard` → `btm_selection_error`), overlay `POST_PIXEL` (`overlays/selection_cotas.py`, F-06, com remoção no `unregister`), `caffmob.move_on_wall` (`move_over/ops_move_on_wall.py`) e pé-direito do Editor de Paredes (`walls2d/ops_editor.py`)
  - Origem no legado: arquivos citados (fora da unit); contrato em `design.md` › Superfície exposta pelos consumidores
  - Critério de pronto: módulo na parede mostra 5 campos e o botão "Mover na Parede"; módulo livre mostra o aviso e 2 campos; com `show_dimensions` desligado nada é desenhado; abrir o Editor de Paredes usa o pé-direito do projeto
  - Confiança: 🟢

- [ ] T-10, Registrar textos: `data/translations/measure.json` (4 mensagens "Valor Inválido…"), rótulos em `geral.json` (`Afastamento da parede`, `Cota anterior/posterior/inferior/superior`, `Cotas`), aviso de módulo livre em `ui.json`
  - Origem no legado: `caffmob_draw/data/translations/measure.json`, `geral.json`, `ui.json`
  - Critério de pronto: interface em inglês sem texto em português nas cotas (`tests/test_i18n_coverage.py` passa)
  - Confiança: 🟢

## Tarefas de Teste

- [ ] TT-01, Núcleo puro: cálculo com janela alta fora da faixa, anterior 75 mm, outras cotas, inválidos, módulo livre, deslizar — `tests/test_cotas.py` (6 testes) 🟢
- [ ] TT-02, Casos ainda sem teste puro: obstáculo que cruza em X, encostar em X/Z, campo desconhecido, módulo mais largo que a parede, `posterior` que sobrepõe o vizinho oposto, `inferior` acima do teto (EC-01, EC-02, EC-04, EC-05, EC-07, EC-14) — 🟢 sem teste identificado (comportamento verificado manualmente nesta extração) _(Revisão 2026-10-10: `tests/test_cotas.py` só tem os 6 testes de TT-01; casos reexecutados em Python puro e conferidos)_
- [ ] TT-03, Camada de cena: `for_object` de um balcão filho de parede (`on_wall`) e deslize até o vizinho sem afastar da parede — `tests/blender_002_smoke.py` §6 🟢 (existe; não executado nesta extração)
- [ ] TT-04, `ceiling_height` com e sem `home_builder.ceiling_height`, `ModuleCotas.apply` livre e na parede, vizinho sem `mod_name` (EC-03, EC-09) — 🔴 sem teste identificado

Comando dos testes puros 🟢: `PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=tests python3 -m unittest test_cotas -v` (6 testes, aprovados em 2026-10-10). Testes Blender: `blender --background --factory-startup --python-exit-code 1 --python tests/blender_002_smoke.py`.

## Tarefas de Migração de Dados

- 🟢 Nenhuma: a unit não tem dados persistentes próprios (só escreve `location` dos módulos).

## Ordem Sugerida

1. 🟢 T-01 → T-02 → T-03 → T-04: núcleo puro (TT-01, TT-02).
2. 🟢 T-05 → T-06 → T-07 → T-08: ponte com a cena (depende dos pré-requisitos).
3. 🟢 T-09 → T-10, validando com TT-03 e TT-04 no Blender.

## Lacunas Pendentes (🔴)

- 🟢 **Decisão do titular (2026-10-10, questions.md#pergunta-12):** `apply` rejeita com "Valor Inválido" (EC-01, EC-02). Pendência de implementação: DT-01.
- 🟢 **Decisão do titular (2026-10-10, questions.md#pergunta-13):** medir pela largura de `btm_cabinet` ou bounding box (EC-03). Pendência de implementação: DT-02.
- 🟢 **Decisão do titular (2026-10-10, questions.md#pergunta-73):** geometrias sem cotas nesta versão (Won't); o código já faz isso.
- 🟡 Medir o custo do recálculo por redesenho e por campo do painel — decisão: medir/testar (DT-03; questions.md#pergunta-74).

## Tarefas por decisão do titular (2026-10-10)

- [ ] DT-01 Em `cotas.apply`, rejeitar com "Valor Inválido" a cota `anterior`/`posterior` que sobrepõe o vizinho do lado oposto e a `inferior` que deixa a cota superior negativa (decisão questions.md#pergunta-12)
- [ ] DT-02 Fazer os obstáculos de vizinhos sem `home_builder.mod_name` usarem a largura de `btm_cabinet` ou o bounding box (como `_dims`), em vez de largura/altura zero (decisão questions.md#pergunta-13)
- [ ] DT-03 Medir o recálculo das cotas (overlay por redesenho e painel por campo) numa parede com ~30 módulos; só criar cache se passar de alguns ms (decisão questions.md#pergunta-74)
