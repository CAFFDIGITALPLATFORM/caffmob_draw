# Molduras de ambiente por pacote (molding) — Requisitos

🟢 **CONFIRMADO** — contrato extraído de `caffmob_draw/molding/` (5 arquivos, 1.687 linhas) em 2026-10-10; a pasta não tem alterações sem commit. Confirmação de código não implica validação visual no Blender (nenhum teste da unit existe; nada foi executado no Blender nesta extração). 🟡 identifica prioridade ou intenção inferida; 🔴 identifica lacuna de validação.

🟢 **Relação com a unit legada `_reversa_sdd/catalog_molding/`:** aquela unit descreveu o mesmo motor quando ele vivia em `blendertomob/molding/` (fork do Home Builder 5). O código atual é o mesmo, com 4 diferenças, todas em `ops.py`: `bl_idname` `caffmob.refresh_room_molding` (antes `home_builder.`/`blendertomob.`), mensagem do operador traduzida por `data.i18n.tr`, prefixo `CAFFMob Draw molding:` no `print` de erro e `register`/`unregister` que preferem a própria classe quando `cls.is_registered`. Decisões já tomadas lá (Q-02 motor único, Q-03 closets, Q-04 desatualizado, Q-05 preset BR) **não estão implementadas** e continuam valendo como roadmap; esta unit só descreve o comportamento atual.

## Visão Geral

🟢 Moldura de ambiente "em um clique": o usuário escolhe na sala um **pacote** de coroa (crown), de rodapé (base) e de light rail num menu, e o sistema varre o perfil por todos os armários elegíveis da cena: corridas encadeadas por armários de canto e várias paredes, ilhas contornadas, eletrodomésticos de piso pulados, pontas acabadas com retorno até o fundo do armário. Não existe atribuição por armário (`molding/__init__.py` docstring).

🟢 Toda mudança numa das 14 propriedades `molding_*` da sala, ou o botão "Refresh Molding", **apaga todos os sweeps de moldura da cena e reconstrói tudo** (`ops.py:apply_scene_packages`). O resultado é uma curva 2D por (corrida × entrada da pilha do pacote), com perfil (`bevel_object`) oculto como filho, parentada no primeiro armário da corrida.

🟢 Só armários **face frame** e **frameless** (bibliotecas herdadas) recebem moldura; o módulo CAFFMob (`btm_cabinet`), closets e geometria livre não têm adaptador (`adapters.py:collect_targets`).

## Responsabilidades

- 🟢 Coletar alvos por tipo de moldura e por biblioteca, e eletrodomésticos de piso como pontes do rodapé (`adapters.py:collect_targets/collect_bridges`).
- 🟢 Produzir o dicionário de fatos (`FACTS`) por membro: papel, canto em L, rodapé (recuo e montantes), pontas acabadas, datum da coroa; resolver o material de acabamento do estilo (`adapters.py:build_facts/finish_material`).
- 🟢 Geometria agnóstica de biblioteca: medidas do cage, agrupamento por contato, ordenação em cadeia, offsets com meia-esquadria (aberto e fechado), planta do canto em L, percurso frontal (coroa, capa, light rail) e trechos de rodapé com retornos e perímetro de ilha (`engine.py`).
- 🟢 Presets de pacotes como pilhas de perfis, registro de packs externos de perfis, contornos substitutos embutidos, métricas de perfil com cache e criação do objeto-perfil (`packages.py`).
- 🟢 Orquestração: limpar, resolver pilhas e cotas Z, criar sweeps, callback de propriedade e operador `caffmob.refresh_room_molding` (`ops.py`).
- 🟢 **Não** pertence a esta unit: as 14 propriedades `Scene.home_builder.molding_*` e seus callbacks de itens (`hb_props.py:177-221,509-599`, unit `hb_props`/núcleo legado); o desenho da UI (`product_libraries/face_frame/props_hb_face_frame.py:draw_molding_ui`, aba OPTIONS › Molding da biblioteca face frame); a biblioteca de perfis avulsos `HOME_BUILDER_PT_molding_library` e as molduras próprias do frameless/closets (`_reversa_sdd/catalog_molding/questions.md` Q-02); os packs de perfis (instalados à parte, nenhum no repositório).

## Regras de Negócio

| ID | Regra confirmada | Fonte |
|---|---|---|
| RN-01 | 🟢 Elegibilidade por tipo: `CROWN` e `CAP` → `cabinet_type`/`CABINET_TYPE` em (`UPPER`, `TALL`); `BASE` → (`BASE`, `TALL`, `LAP_DRAWER`); `LIGHT_RAIL` → (`UPPER`,). Face frame: objeto com idprop `IS_FACE_FRAME_CABINET_CAGE` e `obj.face_frame_cabinet.cabinet_type`; frameless: `IS_FRAMELESS_CABINET_CAGE` ou `IS_FRAMELESS_PRODUCT_CAGE` e idprop `CABINET_TYPE`. Ordem: todos os face frame, depois todos os frameless, na ordem de `scene.objects` | `adapters.py:_CROWN_TYPES/_BASE_TYPES/_RAIL_TYPES/collect_targets` |
| RN-02 | 🟢 Pontes do rodapé: objetos com `IS_APPLIANCE` e `matrix_world.translation.z ≤ 0,02` m entram como membros só no tipo `BASE`; papel `APPLIANCE`, rodapé `SKIP`, sem pontas acabadas. Eletrodoméstico suspenso (forno de embutir, micro-ondas sobre o fogão) é ignorado | `adapters.py:collect_bridges/build_facts`; `ops.py:_apply_type` |
| RN-03 | 🟢 Agrupamento: dois membros se tocam quando a cota de alinhamento difere ≤ 0,02 m (`top` = Z da origem + altura para coroa/capa; `bottom` = Z da origem para rodapé e light rail) **e** os AABB XY mundiais dos footprints se sobrepõem com folga de 0,02 m. Componentes conexos por busca em largura; componente sem nenhum alvo (só pontes) é descartado | `engine.py:members_touch/connected_components`; `ops.py:_TYPES/_apply_type` |
| RN-04 | 🟢 Uma corrida = uma componente ordenada em cadeia: começa no primeiro membro com exatamente 1 vizinho (senão no primeiro da componente) e segue o primeiro vizinho não usado; membros não alcançados (ramificação) vão para o fim da cadeia. Componentes de 1 ou 2 membros não são reordenadas | `engine.py:order_chain` |
| RN-05 | 🟢 Sentido do percurso: o lado **direito** do sentido de viagem é sempre o lado de fora. O primeiro membro reto da cadeia é a sonda: se `direita(viagem) · normal_frontal < 0`, a cadeia é invertida e remontada | `engine.py:chain_sweep_points/kick_sweep_segments` |
| RN-06 | 🟢 Ponta da cadeia acabada (`finished_left/right` do lado que é extremidade) recebe **retorno**: o último ponto avança `offset` para fora e é acrescentado o ponto do fundo do armário (canto traseiro do lado) também deslocado `offset` para fora. Ponta não acabada termina rente | `engine.py:chain_sweep_points/_stretch_segments` |
| RN-07 | 🟢 Ponta acabada — face frame: `left/right_finished_end_condition` ≠ `UNFINISHED` (e não vazio/None). Frameless: a ponta é acabada quando o ponto a 0,03 m para fora do meio da lateral **não** cai em nenhum AABB XY de parede (`IS_WALL_BP`) expandido 0,05 m | `adapters.py:build_facts/_frameless_end_finished/_near_wall` |
| RN-08 | 🟢 Rodapé por armário: eletrodoméstico, refrigerador face frame (`CLASS_NAME == 'RefrigeratorCabinet'`) → `SKIP`; recuo ≤ 1e-5 → `FRONT` na face; recuo > 0 → trecho `RECESS` na face recuada, com os montantes que descem ao piso (`extend_*_stile_to_floor` e largura > 1e-5) como trechos `FRONT` que incluem o retorno lateral. Face frame só tem recuo com `toe_kick_type` em {`NOTCH`, `LOOSE`, `FLOATING`}; frameless usa a idprop `Toe Kick Setback` sem montantes | `engine.py:_kick_spans_local`; `adapters.py:_RECESSED_FF_KICKS/build_facts` |
| RN-09 | 🟢 `FRONT` sempre leva rodapé; `RECESS` só com `molding_base_include_recessed`; `SKIP` nunca. Onde um trecho mantido encontra um descartado, o percurso **retorna** até o ponto do trecho descartado adjacente (o rodapé entra até a face do rodapé recuado/eletrodoméstico) | `engine.py:_stretch_segments` |
| RN-10 | 🟢 Ilha: todos os membros da corrida sem `parent`, nenhum de canto, no máximo 2 rotações Z distintas (arredondadas a 2 casas) e, se 2, opostas (diferença ≡ π ± 0,05 rad). Ilha vira perímetro fechado (frente, laterais e fundo, ou duas fileiras costas com costas) sem tratamento de ponta; se todo o perímetro é mantido, um laço cíclico; senão trechos abertos começando no primeiro descartado. Só para rodapé | `engine.py:_island_perimeter_spans/kick_sweep_segments/_stretch_segments` |
| RN-11 | 🟢 Datum Z da coroa (no espaço local do 1º membro): face frame com peça `TOP_RAIL` medida → `altura − largura_do_TOP_RAIL + max(default_top_overlay, 0) + molding_crown_reveal`; senão (frameless, ou face frame sem TOP_RAIL) → `altura` | `ops.py:_crown_datum`; `adapters.py:_top_rail_width/build_facts` |
| RN-12 | 🟢 Z de cada sweep: `CROWN` = datum + dy; `CAP` = `max(altura, topo_da_pilha_de_coroa) + molding_cap_offset + dy` (topo da pilha = datum + max(dy + altura do perfil) das entradas resolvidas; sem pacote de coroa vale a altura); `BASE` e `LIGHT_RAIL` = dy (origem do 1º membro: piso para base, base do aéreo para light rail) | `ops.py:_sweep_z/_crown_stack_top` |
| RN-13 | 🟢 Pilha resolvida em ordem: override de perfil por categoria (`<Categoria>/<override>`), `STACK_OFFSET` → `molding_crown_stack_offset`, `STACK_FRONT` → frente acumulada das entradas anteriores; frente = `max(frente, dx + espessura_do_perfil)` | `ops.py:_resolve_stack` |
| RN-14 | 🟢 Pilha do rodapé: entradas do pacote (vazio com `NONE`) com o perfil `Base Molding/<molding_base_profile>` quando ≠ `DEFAULT`; com `molding_base_shoe`, acrescenta `('Base Molding/Base Shoe', 'base_shoe', 'STACK_FRONT', 0.0)` — o complemento vai na face do rodapé (dx = espessura do rodapé) ou, sem pacote, na face do rodapé do armário (dx = 0) | `ops.py:_base_stack`; `packages.py:BASE_SHOE_REF/BASE_SHOE_FALLBACK` |
| RN-15 | 🟢 Capa de móvel (furniture cap) é um interruptor independente do pacote de coroa: aplica `FURNITURE_CAP_STACK` com tipo `CAP`, alinhamento `top`, alvos de coroa | `ops.py:apply_scene_packages`; `packages.py:FURNITURE_CAP_STACK` |
| RN-16 | 🟢 Perfil: o `.blend` `<pack>/<Categoria>/<Nome>.blend` do primeiro pack registrado que o tenha e contenha objeto com o nome do arquivo; senão o contorno embutido de `fallback_key`; sem nenhum dos dois, a entrada não gera sweep | `packages.py:make_profile_object/_load_library_profile` |
| RN-17 | 🟢 Material do sweep: material de acabamento do estilo do **primeiro** membro da cadeia que resolve um (pontes resolvem `None`); sem nenhum, a curva fica sem material | `ops.py:_spawn_sweep`; `adapters.py:finish_material` |
| RN-18 | 🟢 Cenas com idprop `IS_LAYOUT_VIEW` ou `IS_DETAIL_VIEW`, ou sem `scene.home_builder`, não são tocadas (nem limpas) | `ops.py:apply_scene_packages` |
| RN-19 | 🟢 Reconstrução total e destrutiva: antes de criar, remove todo objeto da cena com `IS_HB_MOLDING_SWEEP` e seu perfil `IS_HB_MOLDING_PROFILE`; edições manuais nos sweeps se perdem. Não há atualização automática quando um armário muda (só ao mexer numa propriedade `molding_*` ou no botão) | `ops.py:clear_scene_molding/apply_scene_packages` |
| RN-20 | 🟢 Unidades internas em metros; defaults e contornos embutidos definidos em polegadas (`units.inch(v) = v · 0,0254`) | `packages.py:_in`; `hb_props.py:536-562` |

## Requisitos Funcionais

🟡 Prioridades inferidas do uso (a unit atende só bibliotecas herdadas, ocultas por padrão desde a feature 012 — ADR 0006) e de `catalog_molding`; não constituem roadmap aprovado.

| ID | Requisito | Prioridade | Critério de aceite |
|---|---|---|---|
| RF-01 | 🟢 Aplicar coroa por pacote (`SIMPLE`, `STACKED`, `SPACER`) em aéreos e torres | Should | CA-01, CA-02, CA-03 |
| RF-02 | 🟢 Aplicar rodapé por pacote (`SIMPLE`) com recuos, montantes, pontes e retornos | Should | CA-04, CA-05, CA-06 |
| RF-03 | 🟢 Aplicar light rail por pacote (`SIMPLE`) sob os aéreos | Could | CA-07 |
| RF-04 | 🟢 Capa de móvel independente sobre a pilha de coroa, com offset | Could | CA-08 |
| RF-05 | 🟢 Complemento de rodapé (base shoe) independente do pacote | Could | CA-09 |
| RF-06 | 🟢 Encadear corridas por armários de canto em L ou diagonal e contornar ilhas | Should | CA-10, CA-11 |
| RF-07 | 🟢 Trocar perfil por categoria a partir de packs externos registrados, com contorno substituto quando não há pack | Could | CA-12, CA-13 |
| RF-08 | 🟢 Reconstruir sob demanda (`caffmob.refresh_room_molding`) e a cada mudança de propriedade | Should | CA-14, CA-15 |
| RF-09 | 🟢 Moldura com o material de acabamento do estilo do armário | Could | CA-01 |

## Requisitos Não Funcionais

| Tipo | Requisito observado | Evidência | Confiança |
|---|---|---|---|
| Desfazer | Operador com `bl_options = {'UNDO'}` (sem `REGISTER`); a reconstrução via callback de propriedade entra no passo de desfazer da própria edição da propriedade | `ops.py:home_builder_OT_refresh_room_molding`; `hb_props.py:update_molding_package` | 🟢 (operador) / 🟡 (callback depende do undo de propriedade do Blender) |
| Custo | Reconstrução síncrona da cena inteira a cada mudança de qualquer das 14 propriedades, inclusive a cada passo de arraste dos campos float; agrupamento O(n²) em pares por tipo; perímetro e retornos lineares no nº de membros | `hb_props.py:509-599` (`update=update_molding_package`); `engine.py:connected_components/order_chain` | 🟢 🟢 **Decisão do titular (2026-10-10, questions.md#pergunta-95):** aceita a reconstrução a cada passo do arraste enquanto as linhas herdadas estão atrás da porta legado (ADR 0006); se o uso crescer, agendar a reconstrução com `bpy.app.timers` (ex. 0,2 s) cancelando a anterior (EC-17) |
| Cache | Métricas de perfil (topo, espessura) por `profile_ref`; itens de enum por categoria; ambos limpos só ao registrar/desregistrar um pack. Cada sweep carrega seu próprio objeto-perfil (sem compartilhamento) | `packages.py:_profile_height_cache/_category_enum_cache/make_profile_object` | 🟢 |
| Robustez | O callback captura **qualquer** exceção e só imprime `CAFFMob Draw molding: apply failed: <ex>` no console; o operador não captura (exceção vira erro do Blender). Sem rollback: falha no meio deixa a cena parcialmente limpa/reconstruída | `ops.py:on_package_changed/home_builder_OT_refresh_room_molding.execute` | 🟢 |
| Ciclo de vida | Uma classe registrada; `register` desregistra antes uma versão já registrada e engole exceções; `unregister` engole exceções. Sem handlers, timers ou propriedades próprias | `ops.py:register/unregister`; `__init__.py` | 🟢 |
| Testabilidade | Nenhum teste da unit; `engine.py` depende de `mathutils` e `hb_types` (não roda fora do Blender). As funções de offset foram sondadas nesta extração com um `Vector` substituto (ver `edge-cases.md` EC-05) | `tests/` (sem `molding`); `engine.py` imports | 🟢 / 🔴 (sem regressão automatizada) |
| Internacionalização | Mensagem do operador e rótulos de pacote em `data/translations/molding.json` (17 chaves); rótulos de pacote passam crus ao `EnumProperty` (tradução depende do mecanismo do catálogo) | `ops.py:execute`; `packages.py:CROWN_PACKAGES…` | 🟢 / 🟡 |

## Critérios de Aceitação

🟢 Cenários derivados do código atual; não há teste da unit. Valores numéricos de CA-16 conferidos por sonda das funções puras de offset. _(Revisão 2026-10-10: sonda no Blender 5.2.0 LTS confirmou CA-03 (dx 0,01905 e dy 0,0889), CA-06 (só `btm_cabinet` → 0 e `FINISHED`), CA-09 (shoe dx 0 sem pacote e 0,015875 com SIMPLE), CA-13 (`profile_enum_items` = só `DEFAULT`), CA-14 (1 sweep e 1 perfil após 2 refreshes, 0 curvas órfãs), CA-15 (`IS_LAYOUT_VIEW` → 0, nada apagado) e CA-16; e, com 2 balcões frameless, 1 sweep BASE com 1 spline aberta, pai = 1º da cadeia, perfil `Molding_Profile_base_simple` oculto)_

```gherkin
CA-01 — Coroa simples numa parede (feliz)
Dado três aéreos face frame UPPER encostados numa parede, topos no mesmo Z, ponta esquerda UNFINISHED e direita FINISHED, TOP_RAIL de 0,0381 m e default_top_overlay 0,0127 m
Quando molding_crown_package muda para 'SIMPLE'
Então surge 1 objeto "MoldingSweep" (curva 2D, bevel_mode 'OBJECT', perfil "Molding_Profile_crown_simple" oculto como filho), parentado no 1º aéreo da cadeia, com location.z = altura − 0,0381 + 0,0127 + 0,015875, um spline BEZIER aberto pela frente dos três com retorno até o fundo só na ponta direita, IS_HB_MOLDING_SWEEP = True, HB_MOLDING_TYPE = 'CROWN', HB_MOLDING_MEMBERS = nomes separados por vírgula, e o material de acabamento do estilo do 1º aéreo

CA-02 — Topos desalinhados (falha de agrupamento)
Dado dois aéreos lado a lado com topos 0,025 m diferentes
Quando a coroa SIMPLE é aplicada
Então nascem 2 sweeps independentes (|Δtopo| > 0,02 m), cada um com as próprias pontas

CA-03 — Coroa empilhada
Dado um aéreo frameless e molding_crown_package = 'STACKED' sem pack instalado
Quando a coroa é aplicada
Então nascem 2 sweeps: espaçador flat_stock em z = altura e coroa crown_simple em z = altura + molding_crown_stack_offset (0,0889 m padrão), com dx = 0,01905 m (espessura do flat_stock: 0,75")

CA-04 — Rodapé atravessa lava-louças (feliz)
Dado dois balcões BASE com rodapé rente e um eletrodoméstico IS_APPLIANCE no piso entre eles, encostados
Quando molding_base_package = 'SIMPLE'
Então os três formam 1 corrida; o vão do eletrodoméstico é SKIP; saem 2 trechos abertos no mesmo sweep (2 splines), cada um terminando no ponto inicial/final do trecho SKIP (coincide com o canto do balcão quando as frentes estão alinhadas; senão vira um retorno até a frente do eletrodoméstico)

CA-05 — Rodapé recuado sem/ com opção
Dado um balcão face frame com toe_kick_type 'NOTCH', toe_kick_setback 0,075 m, sem montantes ao piso, entre dois balcões de rodapé rente
Quando o rodapé é aplicado com molding_base_include_recessed = False
Então o trecho do balcão recuado é descartado e os vizinhos retornam até a face recuada; com a opção True, o percurso entra e sai do recuo num único trecho contínuo

CA-06 — Nenhum alvo (falha)
Dado uma cena só com módulos CAFFMob (btm_cabinet) ou closets
Quando qualquer pacote é escolhido ou o botão é clicado
Então nenhum sweep é criado e o operador reporta INFO "Rebuilt 0 molding run(s)" (traduzido)

CA-07 — Light rail
Dado aéreos UPPER com bases no mesmo Z
Quando molding_light_rail_package = 'SIMPLE'
Então 1 sweep LIGHT_RAIL por corrida, com location.z = 0 no 1º aéreo e perfil light_rail_simple pendurado para baixo (Y negativo do contorno)

CA-08 — Capa de móvel sobre a coroa
Dado aéreos frameless, coroa SIMPLE e molding_crown_furniture_cap = True, cap_offset = 0
Quando a capa é aplicada
Então o sweep CAP fica em z = altura + 0,0762 (topo do crown_simple: 3"); com coroa NONE fica em z = altura; cap_offset negativo baixa a capa abaixo desse valor

CA-09 — Base shoe sem pacote
Dado molding_base_package = 'NONE' e molding_base_shoe = True
Quando a reconstrução roda
Então nasce só o sweep do complemento (base_shoe) na face do rodapé do armário (dx = 0); com pacote SIMPLE o complemento usa dx = 0,015875 m (espessura do base_simple: 0,625")

CA-10 — Canto em L
Dado dois balcões em paredes perpendiculares unidos por um armário de canto face frame (corner_type ≠ 'NONE', left_depth/right_depth)
Quando o rodapé (ou a coroa) é aplicado
Então 1 sweep contínuo passa pelos dois braços do canto com meia-esquadria nas quinas (notch em 2 faces, ou 1 face se DIAGONAL)

CA-11 — Ilha costas com costas
Dado quatro balcões sem parent em duas fileiras com rotações Z de 0 e π, rodapé rente
Quando o rodapé é aplicado
Então o sweep tem 1 spline cíclico contornando o perímetro (frente A, lateral, frente B, lateral) sem pontas

CA-12 — Override de perfil com pack
Dado um pack registrado por register_profile_path(<pasta>) contendo "Crown Molding/Ogee.blend" com objeto curva "Ogee"
Quando molding_crown_profile = 'Ogee' com coroa SIMPLE
Então o perfil do sweep é o objeto anexado "Ogee" (2D, sem bevel, fill NONE, escala 1, oculto, IS_HB_MOLDING_PROFILE)

CA-13 — Pack sem o perfil (falha suave)
Dado nenhum pack registrado
Quando qualquer pacote é aplicado
Então os menus de perfil só listam 'DEFAULT' (e a UI os oculta) e os sweeps usam os contornos embutidos

CA-14 — Idempotência
Dado molduras já aplicadas
Quando caffmob.refresh_room_molding executa duas vezes
Então o nº de objetos MoldingSweep e Molding_Profile na cena é o mesmo após cada execução

CA-15 — Cena de layout (falha)
Dado uma cena com IS_LAYOUT_VIEW
Quando o botão é clicado nela
Então nada é apagado nem criado e o relatório é "Rebuilt 0 molding run(s)"

CA-16 — Offset com meia-esquadria (puro)
Dado offset_polyline_right
Quando chamo com [(0,0),(1,0),(1,1)] e 0,1; com [(0,0),(1,0),(2,0)] e 0,1
Então obtenho [(0,−0,1),(1,1,−0,1),(1,1,1)] e [(0,−0,1),(1,−0,1),(2,−0,1)]; e offset_polygon_right([(0,0),(0,1),(1,1),(1,0)], 0,1) devolve [(0,1,0,1),(0,1,0,9),(0,9,0,9),(0,9,0,1)]
```

## Prioridade (MoSCoW)

| Requisito | MoSCoW | Justificativa |
|---|---|---|
| RF-01, RF-02, RF-06, RF-08 | Should | 🟡 Acabamento essencial de cozinha nas linhas herdadas, mas essas linhas estão atrás da porta legado (ADR 0006) |
| RF-03, RF-04, RF-05, RF-07, RF-09 | Could | 🟡 Variações sobre os pacotes básicos |
| Moldura para módulos CAFFMob/closets | Won't (no código atual) | 🟢 Sem adaptador; decidido como desejado em `catalog_molding` Q-03, não implementado |
| Marcar molduras desatualizadas quando um armário muda | Won't (no código atual) | 🟢 Decisão Q-04 de `catalog_molding` sem implementação |
| Perfis BR (rodapé MDF, sanca, perfil de LED) | Won't (no código atual) | 🟢 Presets só em polegadas, perfis americanos (Q-05 de `catalog_molding`) |

## Rastreabilidade de Código

| Arquivo | Função / Classe | Cobertura |
|---|---|---|
| `caffmob_draw/molding/__init__.py` | `register`, `unregister` (só `ops`) | 🟢 |
| `caffmob_draw/molding/adapters.py` | `_CROWN_TYPES`, `_BASE_TYPES`, `_RAIL_TYPES`, `_face_frame_roots`, `_frameless_roots`, `collect_targets`, `collect_bridges`, `_RECESSED_FF_KICKS`, `_top_rail_width`, `_wall_bounds`, `_near_wall`, `_frameless_end_finished`, `finish_material`, `build_facts` | 🟢 |
| `caffmob_draw/molding/engine.py` | `cage_dims`, `_xy`, `footprint_xy`, `top_z`, `bottom_z`, `front_normal_xy`, `members_touch`, `connected_components`, `order_chain`, `offset_polyline_right`, `offset_polygon_right`, `corner_plan_data`, `_assemble_front_raw`, `chain_sweep_points`, `_kick_spans_local`, `_assemble_kick_spans`, `_stretch_segments`, `_island_perimeter_spans`, `kick_sweep_segments` | 🟢 (offsets sondados) |
| `caffmob_draw/molding/packages.py` | `register_profile_path`, `unregister_profile_path`, `profile_paths`, `profile_enum_items`, `CROWN_PACKAGES`, `FURNITURE_CAP_STACK`, `BASE_PACKAGES`, `BASE_SHOE_REF`, `BASE_SHOE_FALLBACK`, `LIGHT_RAIL_PACKAGES`, `PACKAGES`, `package_stack`, `stack_has_adjustable_offset`, `stack_uses_category`, `enum_items`, `_PROFILE_OUTLINES`, `_finish_profile`, `_load_library_profile`, `_curve_metrics`, `_profile_metrics`, `profile_top_height`, `profile_front_depth`, `make_profile_object` | 🟢 |
| `caffmob_draw/molding/ops.py` | `MOLDING_TAG`, `MOLDING_TYPE`, `MOLDING_MEMBERS`, `_TYPES`, `clear_scene_molding`, `_resolve_stack`, `_crown_datum`, `_crown_stack_top`, `_sweep_z`, `_spawn_sweep`, `_apply_type`, `_base_stack`, `apply_scene_packages`, `on_package_changed`, `home_builder_OT_refresh_room_molding`, `register`, `unregister` | 🟢 |
| `caffmob_draw/hb_props.py` (consumidor) | `update_molding_package`, `_molding_*_items`, 14 props `molding_*` em `Home_Builder_Scene_Props` | 🟢 |
| `caffmob_draw/product_libraries/face_frame/props_hb_face_frame.py` (consumidor) | `draw_molding_ui` | 🟢 |
