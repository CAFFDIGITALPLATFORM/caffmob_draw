# Relatório de Confiança — BlenderToMob (re-extração 2026-10)

> Gerado pelo Reviewer em 2026-10-10. Escopo: as 18 units novas da re-extração (features 001 a 013). Units de 2026-07 e legadas mantêm os relatórios anteriores (`feedback.md`).
> Contagem = ocorrências dos emojis em todos os `.md` da unit (inclui legendas de cabeçalho, igual para antes e depois).

## Resumo Geral

| Nível | Quantidade | Percentual |
|---|---|---|
| 🟢 CONFIRMADO | 4361 | 91.8% |
| 🟡 INFERIDO | 304 | 6.4% |
| 🔴 LACUNA | 85 | 1.8% |
| **Total** | 4750 | 100% |

**Confiança geral:** 95.0% (antes da revisão: 89.5%)

## Por Spec

| Spec | 🟢 | 🟡 | 🔴 | Confiança | Antes | Perguntas |
|---|---|---|---|---|---|---|
| `_reversa_sdd/canvas2d/` | 211 | 11 | 4 | 95.8% | 90.5% | 3 |
| `_reversa_sdd/walls2d/` | 319 | 12 | 2 | 97.6% | 92.2% | 6 |
| `_reversa_sdd/measure/` | 146 | 14 | 4 | 93.3% | 83.9% | 5 |
| `_reversa_sdd/move_over/` | 213 | 14 | 6 | 94.4% | 87.3% | 7 |
| `_reversa_sdd/selection/` | 215 | 15 | 4 | 95.1% | 88.3% | 4 |
| `_reversa_sdd/openings/` | 246 | 20 | 4 | 94.8% | 86.7% | 6 |
| `_reversa_sdd/aggregates/` | 301 | 29 | 3 | 94.7% | 88.5% | 8 |
| `_reversa_sdd/collision/` | 195 | 29 | 5 | 91.5% | 84.4% | 6 |
| `_reversa_sdd/stick/` | 224 | 18 | 4 | 94.7% | 86.0% | 5 |
| `_reversa_sdd/customize/` | 205 | 7 | 3 | 97.0% | 89.5% | 3 |
| `_reversa_sdd/cabinet_editor/` | 227 | 11 | 1 | 97.3% | 92.6% | 9 |
| `_reversa_sdd/standards/` | 341 | 25 | 4 | 95.5% | 92.5% | 7 |
| `_reversa_sdd/legacy/` | 228 | 17 | 4 | 95.0% | 88.9% | 3 |
| `_reversa_sdd/library_panel/` | 245 | 16 | 3 | 95.8% | 92.7% | 4 |
| `_reversa_sdd/object_library/` | 273 | 17 | 4 | 95.7% | 89.8% | 4 |
| `_reversa_sdd/inspection/` | 287 | 17 | 5 | 95.6% | 91.1% | 6 |
| `_reversa_sdd/molding/` | 248 | 20 | 11 | 92.5% | 90.6% | 2 |
| `_reversa_sdd/geometry_free/` | 237 | 12 | 14 | 92.4% | 89.4% | 3 |

## Revisão Cruzada

- Engine externa consultada: nenhuma (plugin Codex indisponível na sessão; `doc_level = detalhado` exigiria). Revisão cruzada feita internamente entre units.
- Notas cruzadas resolvidas: 74 (34 com correção in-place)
- Contradições novas: 8
- `code-spec-matrix`: 0 linhas acrescentadas, 5 corrigidas
- `spec-impact-matrix`: +1 / −0 arestas (grafo de imports via AST)

## Lacunas Pendentes 🔴

As 98 perguntas de `questions.md` foram **respondidas pelo titular em 2026-10-10** ("aceito": recomendações adotadas). 97 aplicadas nas specs; a 97 só afeta artefatos fora de `_reversa_sdd/` (`modules.json`, `_reversa_forward/003` e `004`). 93 tarefas `DT-xx` de implementação foram criadas nos `tasks.md`. Os 🔴 restantes são legendas, títulos e lacunas de teste sem pergunta associada; 97 lacunas de código em `gaps.md` Parte B.

### Decisões críticas (agora tarefas DT)

- **[walls2d]** Remover Vértice deve registrar o source do trecho eliminado em removed_sources (como o Delete faz)? → decidido: Sim: acrescentar o source a removed_sources em remove_node (ou no chamador), igual a remove_segment; evita parede órfã no projeto
- **[selection]** Ao apagar uma parede, os agregados dos módulos filhos dela devem entrar na pergunta 'O objeto tem agregados'? → decidido: Não: own_aggregates deve parar em raízes de módulo e em alvos que não levam a subárvore (parede, piso, teto), porque esses agregados pertencem a outro componente
- **[aggregates]** O terceiro teste de can_convert deve recusar 'pai descendente do objeto' (como diz a mensagem) em vez de 'objeto descendente do pai' (como o código faz)? → decidido: Sim: trocar para `parent in obj.children_recursive`; é o que a mensagem e a 003 descrevem e evita o ciclo
- **[aggregates]** Apagar uma parede (ou piso/teto) deve perguntar pelos agregados dos módulos filhos dela? → decidido: Não: own_aggregates deve parar em raízes de módulo e em alvos que não levam a subárvore (mesma decisão da revisão de selection)
- **[revisão cruzada]** Ao apagar uma parede, portas/janelas, geometrias e cotas filhas devem ir junto, ficar no lugar (como em wall_remove) ou o X/Delete deve delegar para caffmob.wall_remove? → decidido: Fazer o X/Delete numa parede usar ops_wall_extras.remove_wall (mesma regra KEEP_WITH_WALL e matriz de mundo preservada)

## Recomendações

- [ ] Executar as tarefas `DT-xx` (decisões do titular) começando pelas críticas — via `/reversa-forward` ou `/reversa-debugger`
- [ ] `aggregates` tem 6 perguntas críticas/moderadas — priorizar validação
- [ ] `cabinet_editor` tem 6 perguntas críticas/moderadas — priorizar validação
- [ ] `standards` tem 6 perguntas críticas/moderadas — priorizar validação
- [ ] `walls2d` tem 5 perguntas críticas/moderadas — priorizar validação
- [ ] `move_over` tem 5 perguntas críticas/moderadas — priorizar validação
- [ ] `openings` tem 5 perguntas críticas/moderadas — priorizar validação
- [ ] `collision` tem 5 perguntas críticas/moderadas — priorizar validação
- [ ] `stick` tem 4 perguntas críticas/moderadas — priorizar validação
- [ ] Lacunas de código críticas em `gaps.md` Parte B (1) — candidatas a `/reversa-debugger`
- [ ] Criar units para o código sem spec (`gaps.md` Parte C, 7 grupos)

## Reclassificações por tipo

| De → Para | Quantidade |
|---|---|
| 🔴 → 🟡 | 4 |
| 🔴 → 🟢 | 31 |
| 🟡 → 🔴 | 1 |
| 🟡 → 🟢 | 93 |

## Histórico de Reclassificações

| De | Para | Afirmação | Evidência |
|---|---|---|---|
| 🟡 | 🟢 | `canvas2d` design.md: Usos da paleta COLORS (painel/quadro/alvo) | move_over/ops_dialog.py:179,186,197; walls2d/ops_editor.py:187,189,232 |
| 🟡 | 🟢 | `canvas2d` tasks.md: TT-01 contains com borda exata sem teste | grep contains em tests/test_canvas2d_*.py: zero ocorrências |
| 🟡 | 🟢 | `canvas2d` tasks.md: TT-03 sem teste de zoom com fator <= 0 | tests/test_canvas2d_view.py:22 e test_canvas2d_gestures.py só usam fator 2.0/pinch_factor |
| 🟡 | 🟢 | `canvas2d` tasks.md: TT-06 falta caso perto de 360° | tests/test_canvas2d_view.py:35-44 cobre ~2°, ~3°, ~270° |
| 🟡 | 🟢 | `canvas2d` tasks.md: TT-07 dashed sem teste | nenhum teste importa canvas2d.draw |
| 🟡 | 🟢 | `canvas2d` edge-cases.md: Nota EC-03 limiar de overflow | executado: math.exp(106467/150)=1.79e308; 106468 -> OverflowError |
| 🔴 | 🟢 | `walls2d` edge-cases.md: EC-14 ordem de find_wall_chains | operators/walls.py:find_wall_chains 132-159 (laços fechados primeiro, ordem de scene.objects) |
| 🟡 | 🟢 | `walls2d` edge-cases.md: EC-15 usuário consegue editar o 3D com o modal ativo | ops_editor.py:modal 583-587 (PASS_THROUGH fora da região do editor) |
| 🟡 | 🟢 | `walls2d` edge-cases.md: Nota EC-05 point_in_rect inclusivo | hb_gpu_draw.py:107 |
| 🟡 | 🔴 | `walls2d` edge-cases.md: EC-06 intenção de confirm_pending | intenção de produto; alinhado a tasks.md Lacunas (já 🔴) |
| 🟡 | 🟢 | `walls2d` design.md: Risco: confirm_pending nunca volta a False | ops_editor.py:887-891; props.py:38 |
| 🟡 | 🟢 | `walls2d` design.md: Risco: Direção pelo painel sem passo imediato | props.py:188-197 (_side_set sem _guard) |
| 🟡 | 🟢 | `walls2d` tasks.md: TT-09 sem teste identificado | tests/test_walls2d_model.py:89-94 só cobre move_node com lock_angle |
| 🟡 | 🟢 | `measure` design.md: obstacles() descarta a faixa de altura real do obstáculo | caffmob_draw/measure/scene_cotas.py:ModuleCotas.obstacles; únicos usos em limits/slide (move_over/ops_move_on_wall.py:88, overlays/selection_cotas.py:40) |
| 🟡 | 🟢 (código) / 🟡 (paredes só giram em Z) | `measure` edge-cases.md: EC-09 módulo livre com pai rotacionado/escalado | scene_cotas.py:ModuleCotas.__init__ (matrix_world.translation.z) e apply (location.z += delta) |
| 🟡 | 🟢 | `measure` edge-cases.md: Nota EC-03: btm_cabinet como vizinho depende de get_wall_children_sorted | scene_cotas.py:_dims; hb_placement.py:393 |
| 🟡 | 🟢 | `measure` tasks.md: TT-02 casos sem teste puro | tests/test_cotas.py (6 testes, nenhum desses casos); casos reexecutados em Python puro |
| 🟡 | 🟢 | `move_over` design.md: align.size sem chamador no pacote | grep em caffmob_draw/ e tests/: nenhum uso de align.size |
| 🟡 | 🟢 | `move_over` design.md: original_box_a sem chamador | grep: só definido em caffmob_draw/move_over/scene.py:MoveOver.original_box_a |
| 🟡 | 🟢 | `move_over` design.md: delta_for/combine aceitam wall e o ignoram | caffmob_draw/move_over/align.py:34-62 |
| 🟡 | 🟢 | `move_over` design.md: original_box_a, align.size, absolute_values sem chamador (o último só em teste) | grep; tests/test_reposition.py:33 |
| 🟡 | 🟢 | `move_over` edge-cases.md: EC-06 texto exato da mensagem com buffer vazio | caffmob_draw/data/units.py:113 (_NUMBER_RE exige dígito), :176 (mensagem), data/expr.py:130 has_operator("") falso |
| 🟡 | 🟢 | `move_over` tasks.md: T-14 textos em move_over.json (48 chaves) | caffmob_draw/data/translations/move_over.json: 48 chaves, 2 idiomas cada; rótulos curtos em geral.json e cabinet_editor.json |
| 🟡 | 🟢 | `move_over` tasks.md: TT-03 casos sem teste puro | tests/test_move_over_align.py:68 só cobre gaps separados e overlaps |
| 🟡 | 🟢 | `selection` edge-cases.md: EC-05 forma exata de bl_idname em modal_operators | caffmob_draw/selection/component_select.py:76-82: as duas formas (caffmob.x / CAFFMOB_OT_x, btm.x / BTM_OT_x, TRANSFORM_OT_x) passam no teste em minúsculas |
| 🟡 | 🟢 | `selection` edge-cases.md: EC-10 janelas BTM têm GeoNodeCage? | caffmob_draw/operators/opening_builder.py:360-378 (malha simples + booleano, sem GN nem home_builder.mod_name); caffmob_draw/hb_types.py:301-313 levanta ValueError |
| 🟡 | 🟢 | `selection` edge-cases.md: Nota EC-07/EC-08 (referências às features 011 e 010) | _reversa_forward/011-selecao-por-componente/requirements.md:140; 010-porta-real-textura-linha/requirements.md:47,105 |
| 🟡 | 🟢 | `selection` tasks.md: TT-04 casos puros sem teste | reexecutado com os objetos simulados de tests/test_component_core.py: EC-01 → Janela, EC-02 → AggInGroup, own_aggregates(parede) → [Fruteira], btm_kind sem is_property_set → 'WALL'; nenhum teste dedicado em tests/test_component_*.py |
| 🟡 | 🟢 | `selection` design.md: _modal_running por substring | caffmob_draw/selection/component_select.py:80 |
| 🟡 | 🟢 (mecanismo) / 🟡 (colisão de nomes vinculados) | `selection` design.md: Assinatura por nomes | caffmob_draw/selection/component_select.py:99-101 usa o.name |
| 🟡 | 🟢 | `openings` requirements.md: Origem das texturas de nogueira (RNF Licença dos ativos) | tools/build_openings_assets.py:6-8 (PNG gerados por docs/porta_realista_080x210/gerar_porta.py, modelo original); licença formal não escrita |
| 🟡 | 🟢 | `openings` requirements.md: Uso das prévias previa_porta.png/previa_janela.png | geradas por tools/render_openings_preview.py; grep 'previa_' em caffmob_draw/, tests/, build.py sem uso |
| 🟡 | 🟢 | `openings` tasks.md: TT-04 casos puros sem teste | execução de region_core.fit: x0 −0,004 aceito, z1 2,704 aceito, porta sobre janela → OVERLAP, kind desconhecido → sill 0; tests/test_wall_region_core.py não cobre |
| 🟡 | 🟢 | `openings` design.md: _remember usa nome-base antes do primeiro ponto | caffmob_draw/openings/sync.py:90-92, 160, 192 |
| 🟡 | 🟢 (código) / 🟡 (escala 1 no fluxo normal) | `openings` design.md: _to_world aplica a escala da caixa | caffmob_draw/openings/sync.py:111 |
| 🟡 | 🟢 | `openings` edge-cases.md: Nota EC-02/EC-04/EC-07 (referências às features 010 e 011) | _reversa_forward/010-porta-real-textura-linha/requirements.md:143; 011-selecao-por-componente/requirements.md:122 |
| 🟡 | 🟢 | `aggregates` edge-cases.md: EC-09 efeito visível de renomear agregado perfurado | caffmob_draw/aggregates/perforate.py:_remove_boolean/_remove_cutout (o CPM_CUTOUT antigo fica no pai e segue na usinagem) |
| 🟡 | 🟢 | `aggregates` design.md: Riscos: renomear perde vínculo com modificador e cutout | caffmob_draw/aggregates/perforate.py:_remove_cutout |
| 🟡 | 🟢 | `aggregates` design.md: Riscos: _guard/_last_parent_box/_cache por nome | props.py:_guarded (obj.name, prop); apply.py:on_depsgraph_update (original.name); collision.py:_targets (obj.name) |
| 🟡 | 🟢 | `aggregates` tasks.md: TT-05 casos puros sem teste | reexecutado em Python puro: sweep (EC-05), grouping.leaf_key (EC-19), limits com caixa degenerada (EC-01); skp_core.py:tree linhas 149-152 (EC-18) |
| 🟡 | 🟢 | `collision` requirements.md: Divergência com 004 D-16 (aviso ao soltar só pelo assentar) | caffmob_draw/stick/settle.py:run linhas 60-94; _MAGNET_KINDS = (MODULE, GEOMETRY) |
| 🟡 | 🟢 | `collision` requirements.md: Divergência com 004 D-17 (handlers permanentes) | caffmob_draw/collision/overlay.py:register/unregister; ops_collision.py:BTM_OT_CollisionClear não remove handlers |
| 🟡 | 🟢 | `collision` requirements.md: Divergência com data-dictionary.md (collision_override, ordem RN-13) | _reversa_sdd/data-dictionary.md linhas 36 e 577; scan.py:check_moved |
| 🟡 | 🟢 | `collision` requirements.md: Divergência com state-machines.md | _reversa_sdd/state-machines.md §Colisão de corpo (sem estado de erro nem check_moved) |
| 🟡 | 🟢 (mecanismo) / 🟡 (custo) | `collision` design.md: overlay._draw_3d recalcula box_of a cada redesenho | caffmob_draw/collision/overlay.py:48 |
| 🔴 | 🟢 | `stick` requirements.md: Fumaças 004/005 não executadas (Blender ausente) | /opt/blender/blender 5.2.0 LTS: blender_004_stick_smoke → OK; blender_005_viewport_smoke (xvfb-run) → 11 checagens OK |
| 🟡 | 🟢 | `stick` requirements.md: Divergência 004 D-06 (ímã fora do PlacementMixin) | hb_placement.py sem referência a stick/magnet; settle.run → magnet.try_stick |
| 🟡 | 🟢 | `stick` requirements.md: Divergência 004 D-04(b) (project não restaura spin) | stick/apply.py:project |
| 🟡 | 🟢 | `stick` requirements.md: Divergência 004 RN-10 / regra de wall_side | stick/migrate.py:wall_side; .reversa/context/modules.json:4183 |
| 🟡 | 🟢 | `stick` requirements.md: Divergência com aggregates/design.md (box_for clamp_to_face=False) | grep box_for|clamp_to_face em caffmob_draw/stick/ vazio; aggregates/design.md:29,276 |
| 🟡 | 🟢 | `stick` requirements.md: Divergência com state-machines.md/permissions.md | permissions.md:42; state-machines.md sem stick |
| 🟡 | 🟢 | `stick` requirements.md: stick_migrated gravado e nunca lido | único uso: stick/migrate.py:50 |
| 🟡 | 🟢 | `stick` design.md: _undo_push usa windows[0]; até 8 ray_cast por quadro | settle.py:_undo_push; magnet._MAX_STEPS=8 via magnet_preview._draw_3d |
| 🟡 | 🟢 | `stick` tasks.md: TT-02 limites puros executados manualmente | reexecutado: 1,0°/1,1°, 0,5/0,6 mm, 0,69/0,70, 1,0/1,1 mm, normal nula → PLANE e ValueError('vetor nulo') |
| 🟡 | 🟢 | `stick` edge-cases.md: Nota EC-01/02/03 vêm do índice por nome | invalidate() só em link._record/release, ops_stick.restore, lose_link, on_load_or_undo; fumaça linha 189 |
| 🟡 | 🟢 | `stick` edge-cases.md: Nota: temporizador anota qualquer objeto; colisão só recebe linked e raízes MODULE/GEOMETRY | apply.on_depsgraph_update; settle.run |
| 🔴 | 🟢 | `customize` requirements.md: Fumaça 003 não executada | Blender 5.2.0 LTS → "blender_003_customize_smoke: OK" |
| 🔴 | 🟢 | `customize` requirements.md: EC-01 .blend sem .json → UnboundLocalError | sonda no Blender 5.2: library_io.load:390 levanta com 26 objetos ligados; module_insert → RuntimeError |
| 🔴 | 🟢 | `customize` requirements.md: EC-02 estilos do closets tratados como ausentes | sonda: aviso único 'Estilos ausentes…: NAO_EXISTE, WIDE_SHAKER'; aviso real do closets apagado pelo filtro de prefixo |
| 🔴 | 🟢 | `customize` requirements.md: EC-06 painel só grava door_style | panels.py:53; ops_customize.py:107,114 |
| 🔴 | 🟢 | `customize` tasks.md: TT-03 fumaça não executada | executada → OK |
| 🔴 | 🟢 | `customize` edge-cases.md: Nota: fumaça não executada, nenhum caso reproduzido | fumaça OK; EC-01, EC-02, EC-04 reproduzidos |
| 🟡 | 🟢 | `customize` requirements.md: Divergência com interfaces/user-module-file.md (003) | user-module-file.md:31,38,40,41,54 |
| 🟡 | 🟢 | `customize` requirements.md: Divergência com flowcharts/customize.md | flowcharts/customize.md:14,22 |
| 🟡 | 🟢 | `customize` requirements.md: part_materials comentado como caminho, gravado por obj.name | spec.py:50; adapters/common.py:98 |
| 🟡 | 🟢 | `customize` requirements.md: shelf_positions/is_empty/structure_of/divisions_of só em testes | grep; is_empty sem uso algum |
| 🟡 | 🟢 | `customize` requirements.md: slide_kind não lido pela unit | cabinet_editor/bridge.py:623; cutting/hardware.py:52 |
| 🟡 | 🟢 | `customize` requirements.md: state-machines.md sem seção da unit | grep |
| 🟡 | 🟢 | `customize` design.md: NO_STYLE_REASON não usado | só a definição em adapters/common.py:10 |
| 🟡 | 🟢 | `customize` design.md: after_rebuild devolve avisos que as bibliotecas descartam | 6 chamadas ignoram o retorno (data/properties.py:81 etc.) |
| 🟡 | 🟢 | `customize` design.md: EC-04 perda da personalização com várias gavetas | sonda no Blender 5.2 |
| 🟡 | 🟢 | `customize` design.md: _data_blocks depende de libraries.write levar dependências indiretas | docs/rag/blender-api/corpus/bpy.types.BlendDataLibraries.md#bpy.types.BlendDataLibraries.write |
| 🟡 | 🟢 | `customize` tasks.md: Módulos sem manifesto dependem da correção de EC-01 | sonda no Blender 5.2 |
| 🟡 | 🟢 | `customize` edge-cases.md: EC-01 (inferência: objetos ficam na cena) | sonda: 26 objetos ligados |
| 🟡 | 🟢 | `customize` edge-cases.md: EC-04 (linha e nota) | sonda: vão antigo apagado, vãos novos com btm_custom vazio |
| 🟡 | 🟢 | `cabinet_editor` requirements.md: RNF 'Um passo de desfazer por OK' (efeito no Blender) | xvfb-run blender_004 'um Ctrl+Z na cena volta ao anterior' (4 bibliotecas); blender_006 'um Ctrl+Z desfaz o Confirmar inteiro'; blender_008 'um Ctrl+Z desfaz o Aplicar inteiro' |
| 🔴 | 🟢 | `cabinet_editor` requirements.md: Lacuna 'efeito real do passo de desfazer do Blender (um por OK)' | smokes blender_004/006/008 executados com xvfb-run, código 0 |
| 🟡 | 🟢 | `cabinet_editor` edge-cases.md: Nota EC-11 (touchpad só no editor de paredes) | walls2d/ops_editor.py:649-652 (TRACKPADZOOM/TRACKPADPAN, sem commit); nenhum TRACKPAD em cabinet_editor/ |
| 🟡 | 🟢 | `cabinet_editor` tasks.md: TT-02 smokes no Blender | blender_004 39 OK, blender_006 162 OK, blender_008 70 OK (xvfb-run), blender_012_cabinet_standard_smoke OK (--background), todos código 0 |
| 🟡 | 🟢 | `standards` design.md: Riscos: docstrings divergentes do código | sync.py:170-171 × 263-265; ops_standards.py:177, 211 × 187, 239 (modules=[]); standards/__init__.py:10 |
| 🟡 | 🟢 | `standards` design.md: Riscos: símbolos sem consumidor | grep em caffmob_draw/: só definições; apply_core.targets só em tests/test_standards_apply_core.py:31-33 |
| 🔴 | 🟡 | `standards` edge-cases.md: EC-15 update de tree_index com o mesmo valor | sonda no Blender 5.2.0: 3 atribuições do mesmo valor a IntProperty com update → 3 chamadas; clique na UIList não testado |
| 🔴 | 🟡 | `standards` tasks.md: T-13 'Validar EC-15 no Blender' | mesma sonda |
| 🟡 | 🟢 | `standards` tasks.md: TT-02 'não existe hoje' (teste puro de io_json) | nenhum test_*.py importa io_json; só blender_identity_smoke.py:66-70 |
| 🔴 | 🟢 | `legacy` requirements.md: RNF Desempenho: 50 armários em menos de 5 s (tempo não medido) | tests/blender_012_convert_smoke.py executado no Blender 5.2: 1,05 s |
| 🔴 | 🟢 | `legacy` requirements.md: RNF Desfazer: runtime do UNDO da conversão | tests/blender_012_convert_undo.py com xvfb-run: OK (desfaz e refaz) |
| 🔴 | 🟢 | `legacy` requirements.md: Lacuna: desfazer quando convert_scene levanta no meio do lote | sonda (build_module falha no 2º): módulo parcial 'BTM_Cabinet' fica, originais intactos, 1 Ctrl+Z remove o parcial |
| 🔴 | 🟢 | `legacy` design.md: Riscos: sem rollback, efeito do UNDO não verificado | mesma sonda; legacy/convert.py:138-140 |
| 🔴 | 🟢 | `legacy` edge-cases.md: EC-05 runtime do undo | mesma sonda |
| 🔴 | 🟢 | `legacy` tasks.md: T-10 undo não executado | tests/blender_012_convert_undo.py OK |
| 🔴 | 🟡 | `legacy` tasks.md: TT-06 teste de falha no meio do lote | comportamento conhecido pela sonda; teste ainda não existe |
| 🟡 | 🟢 | `legacy` edge-cases.md: EC-01 adaptador e _other_fronts veem as mesmas gaiolas? | customize/adapters/face_frame.py:45-49 (só folhas) vs legacy/convert.py:66-74 (children_recursive): não veem sempre as mesmas |
| 🟡 | 🟢 | `legacy` edge-cases.md: EC-15 valor real de cabinet_type nos produtos face frame | props_hb_face_frame.py:4540 (default BASE), :8115; types_face_frame.py:8411-8463 (produtos não gravam cabinet_type) |
| 🟡 | 🟢 | `legacy` edge-cases.md: EC-16 regra de renome do Blender 5.2 | sonda: b.name='X' com 'X' ocupado dá 'X.001' |
| 🟡 | 🟢 | `legacy` design.md: Divergências entre o plano da 012 e o código | _reversa_forward/012-biblioteca-caffmob-chapas/roadmap.md D-24/D-29; actions.md:106-107 (T067/T068) |
| 🟡 | 🟢 (face frame) / 🟡 (closets) | `legacy` design.md: NEUTRAL_TAB: efeito nos keymaps | product_libraries/face_frame/dim_edit_overlay.py:_active_mode exige 'FACE FRAME'; nenhum gate de closets por product_tab |
| 🔴 | 🟢 | `library_panel` edge-cases.md: EC-04 categoria com ':' (não reproduzido no Blender) | sonda: create('Pia: Lavabo') + library_io.save gravou em 'Pia_ Lavabo/'; list_modules → categoria 'Pia_ Lavabo'; load() lista 'Pia_ Lavabo' como COZ (customize/library_io.py:34-37, manifest.py:24-27) |
| 🟡 | 🟢 | `library_panel` design.md: Divergências com artefatos anteriores (a)-(c) | state-machines.md:214-226; roadmap 012 D-15 (linha 85); domain.md:349-351; (d) corrigido |
| 🔴 | 🟢 | `object_library` edge-cases.md: EC-10 modal invocado pela barra lateral | sonda xvfb-run com eventos simulados: pela região UI, _follow vê region UI e rv3d None e a raiz não se move; pela WINDOW segue o mouse (ops.py:91-94) |
| 🔴 | 🟢 | `object_library` design.md: Riscos: modal pela barra lateral | mesma sonda |
| 🔴 | 🟢 | `object_library` tasks.md: T-10 confiança do modal pela barra lateral | mesma sonda |
| 🔴 | 🟢 | `object_library` edge-cases.md: EC-08 pai da raiz vai para o .blend | sonda: .blend salvo contém ['Teste pai', 'PaiX', 'Cube'] |
| 🔴 | 🟢 | `object_library` design.md: Riscos: libraries.write leva o pai | mesma sonda |
| 🔴 | 🟢 | `object_library` edge-cases.md: EC-07 fake user dos dados indiretos | sonda: porta embutida inserida com 0/2 malhas e 0 materiais com fake user; users = 0 após remover os objetos |
| 🔴 | 🟢 | `object_library` design.md: Riscos: fake user de malhas/materiais | mesma sonda (texto corrigido: não persistem) |
| 🔴 | 🟢 | `object_library` tasks.md: Lacuna: pai no .blend e fake user (EC-07/EC-08) | sondas acima |
| 🔴 | 🟡 | `object_library` tasks.md: TT-03 teste do modal | comportamento conhecido por sonda; o teste ainda não existe |
| 🟡 | 🟢 | `object_library` edge-cases.md: EC-06 efeito com raiz que tem pai | item_io.py:132-139 (fallback exige parent is None → 'Item corrompido') |
| 🟡 | 🟢 | `object_library` design.md: Manifesto com tipo inesperado derruba a listagem (EC-01) | read_manifest executado: TypeError para features 5, materials 5, size_mm [null,0,0]; store.py:137 |
| 🟡 | 🟢 (código) / 🟡 (efeito) | `object_library` design.md: _finish_items sem referência às strings | ops.py:245-246; retexture.py:41-44 |
| 🟡 | 🟢 | `inspection` requirements.md: RNF Persistência: WindowManager.btm_inspection não vai para o .blend | sonda Blender 5.2 (salvar/abrir): checked_fronts 7→-1, interferences 1→0, default_angle '45'→'90' |
| 🔴 | 🟢 | `inspection` design.md: Riscos: tests/blender_inspection_smoke.py não executado | executado no Blender 5.2.0 LTS: BLENDER_INSPECTION_SMOKE_OK, exit 0 |
| 🟡 | 🟢 | `inspection` edge-cases.md: EC-18 (parte do código; janela de tempo continua 🟡) | gizmo.py:_active_front/_commit_pending |
| 🟡 | 🟢 | `molding` design.md: Riscos: mitras sem limite (EC-05) e cadeia ramificada (EC-06) | sonda Blender 5.2: offset_polyline_right([(0,0),(1,0),(0,0.1)],0.1) → (3.005,-0.1); engine.py:order_chain |
| 🟡 | 🟢 | `molding` design.md: Riscos: moldura não acompanha mudanças (RN-19) | molding/ sem handler de depsgraph; hb_props.py:update_molding_package e ops.py:home_builder_OT_refresh_room_molding são os únicos chamadores |
| 🟡 | 🟢 | `molding` edge-cases.md: EC-01 efeito do pai apagado | sonda Blender 5.2: bpy.ops.object.delete mantém o filho com parent None e matrix_world = location local |
| 🔴 | 🟢 | `molding` edge-cases.md: EC-04 exceção exata e efeito | sonda Blender 5.2: bpy.data.curves.remove(mesh) → TypeError; curve.bevel_object = objeto malha é ignorado (fica None) |
| 🟡 | 🟢 | `molding` edge-cases.md: EC-11 exceção | sonda Blender 5.2: TypeError 'expected a Curve type, not Mesh' |
| 🟡 | 🟢 | `molding` edge-cases.md: EC-12 filho mantido ao apagar o pai | sonda Blender 5.2 com bpy.ops.object.delete |
| 🔴 | 🟢 | `geometry_free` design.md: Riscos: duplicar/espelhar com parent (EC-09) | sonda Blender 5.2: cópia em (1.5,2,0) em vez de (2,0.5,0); espelho em (2.5,0,0) em vez de (2,-0.5,0) |
| 🟡 | 🟢 | `geometry_free` design.md: Riscos: escala do objeto não muda produção (EC-10) | cutting/part_sources.py:geometry_records lê só btm_geometry |
| 🟡 | 🟢 | `geometry_free` design.md: Riscos: _update reconstrói qualquer malha (EC-11) | sonda: malha comum vira cubo de 8 vértices; props.py:_update |
| 🔴 | 🟢 | `geometry_free` tasks.md: Lacuna: posição de duplicar/espelhar com parent e dos filhos ao excluir | sondas no Blender 5.2 (EC-09, EC-14) |
| 🟡 | 🟢 | `geometry_free` edge-cases.md: EC-04 limitação a 10 m na atribuição | sonda: width = 15.0 → 10.0 |
| 🟡 | 🟢 | `geometry_free` edge-cases.md: EC-07 limitação 0,001–10 m | sonda: 15.0 → 10.0; 0.0005 → 0.001 |
| 🔴 | 🟢 | `geometry_free` edge-cases.md: EC-09 posição resultante | sonda Blender 5.2 |
| 🟡 | 🟢 | `geometry_free` edge-cases.md: EC-11 nenhum chamador atual dispara | grep: só selection/resize.py:100 (classify.GEOMETRY), ops_create.py, mesh.create_object |
| 🔴 | 🟢 | `geometry_free` edge-cases.md: EC-14 posição dos filhos | sonda: filho salta de (6,0,0) para (1,0,0), parent None |
| 🔴 | 🟢 | `geometry_free` requirements.md: RNF Testabilidade: smoke sem execução (falta de teste puro segue 🔴) | tests/blender_002_smoke.py executado: 'blender_002_smoke: OK', exit 0 |
