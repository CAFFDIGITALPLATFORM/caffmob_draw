# Legacy impact: 012-biblioteca-caffmob-chapas

> Gerado por `/reversa-coding` em 2026-10-09.
> Feature: Biblioteca CAFFMob flutuante, só armários CAFFMob, armários por chapas no padrão global (lateral ou base
> passante), aplicar o padrão com duas perguntas, conversão de armários e grupos antigos.
> Âncora: `_reversa_sdd/architecture.md`, `_reversa_sdd/domain.md`; princípios `.reversa/principles.md` (I a XI).

## Arquivos afetados

| Arquivo afetado | Componente | Tipo | Severidade | Justificativa |
|-----------------|------------|------|------------|---------------|
| `caffmob_draw/legacy/` (`gate.py`, `__init__.py`, `convert_core.py`, `convert.py`, `groups_core.py`, `groups.py`, `ops.py`) (novos) | Bibliotecas herdadas | componente-novo | HIGH | Porta única que tira frameless, face frame, closets e molduras da interface; conversão de armários e grupos salvos; `load_post` que neutraliza `product_tab` e avisa |
| `caffmob_draw/library_panel/` (`props.py`, `categories_core.py`, `categories.py`, `models_core.py`, `layout_core.py`, `draw.py`, `ops_click.py`, `popover.py`, `ops_categories.py`, `ops_cabinet.py`, `__init__.py`) (novos) | Interface (`architecture.md#1`) | componente-novo | HIGH | Painel BIBLIOTECA CAFFMOB sempre desenhado; keymap de clique, hover e Esc no "3D View" |
| `caffmob_draw/data/library_models.json` (novo) | Dados do pacote | delta-de-dados | LOW | Catálogo dos 5 modelos prontos |
| `caffmob_draw/__init__.py` | Registro e preferências | regra-alterada | MEDIUM | Preferência `show_legacy_libraries` (Avançado); registro de `legacy` e `library_panel` |
| `caffmob_draw/standards/model.py`, `api.py` | Padrão de Dimensões | delta-de-dados | MEDIUM | `assembly` na definição e no rascunho; `active_assembly`; `apply_draft(modules=...)` |
| `caffmob_draw/standards/sync.py` | Padrão de Dimensões | regra-alterada | HIGH | Aplicar o padrão atualiza os módulos CAFFMob (por linha); os herdados só no modo de suporte; `scene_modules`/`plan_for` |
| `caffmob_draw/standards/apply_core.py`, `cabinet_defaults.py` (novos) | Padrão de Dimensões | componente-novo | MEDIUM | Decisão das duas perguntas; medidas e chapas do armário pelo padrão |
| `caffmob_draw/standards/io_promob.py` | Contrato Promob | delta-de-contrato-externo | MEDIUM | `CAFF_MONTAGEM` gravado no fim e lido fora dos atributos crus |
| `caffmob_draw/standards/migration.py` | Padrão de Dimensões | delta-de-dados | LOW | M-03: `btm_standard_uid` nas raízes de módulo |
| `caffmob_draw/operators/ops_standards.py` | Configurador | regra-alterada | HIGH | As duas perguntas (`standards_apply_scene`, `standards_apply_differ`); "Incluir medidas manuais" sai; campo Montagem; Promob com montagem |
| `caffmob_draw/data/properties.py` | Módulo CAFFMob | delta-de-dados | MEDIUM | `btm_cabinet.assembly` e `line`; `suspended_geometry` |
| `caffmob_draw/operators/cabinet_builder.py` | Módulo CAFFMob | regra-alterada | HIGH | Medidas, chapas, linha, montagem e Z do padrão; `build_module`; os 0,8/0,7/0,55 viram fallback |
| `caffmob_draw/cabinet_editor/structure.py` | Estrutura do armário | regra-alterada | MEDIUM | `layout(..., assembly)` e `carcass_lengths` |
| `caffmob_draw/geometry/mesh_gen.py` | Geração da malha | regra-alterada | LOW | Repassa a montagem |
| `caffmob_draw/cutting/part_sources.py` | Lista de corte | regra-alterada | MEDIUM | Comprimento das chapas pela montagem |
| `caffmob_draw/cabinet_editor/bridge.py`, `panels_structure.py` | Editor de armário | regra-alterada | MEDIUM | Campo Montagem; "Padrão próprio" (`is_own_standard`) |
| `caffmob_draw/ui/sidebar_insert.py`, `my_modules.py`, `view3d_sidebar.py`, `context_menu.py`, `menus.py`, `sidebar_project.py`, `sidebar_selected.py`, `sidebar_build.py` | Barra lateral | regra-alterada | HIGH | Interface herdada pela porta; aviso do painel; Padrão de origem e montagem em Selecionado; caixa de conversão |
| `caffmob_draw/operators/viewport_hud.py` | HUD | regra-alterada | MEDIUM | Modos herdados pela porta; `room_ui_visible` para os botões gerais |
| `caffmob_draw/selection/component_select.py` | Seleção por componente (011) | regra-alterada | LOW | Sem modos herdados com a porta fechada: todo módulo sobe |
| `caffmob_draw/data/translations/library.json` (novo) | i18n | regra-alterada | LOW | 108 textos novos |
| `tests/blender_005_sidebar_inventory.py`, `tests/fixtures/sidebar_retired_012.json` | Testes | regra-alterada | LOW | Operadores herdados aposentados declarados |
| `tests/blender_011_component_smoke.py`, `tests/blender_increment1_smoke.py` | Testes | regra-alterada | LOW | Ajustados ao comportamento novo (ver T041 nas notas) |

## Diff conceitual por componente

**Biblioteca e interface.** Antes, a biblioteca era a seção Inserir da barra lateral, com o seletor das três
bibliotecas e as galerias delas. Agora:
- a biblioteca é o painel BIBLIOTECA CAFFMOB, no topo da viewport, com Criar armário, categorias com linha do padrão
  e Criar categoria;
- as categorias abrem os modelos prontos CAFFMob e os módulos do usuário;
- frameless, face frame, closets e a biblioteca de molduras só aparecem com a preferência de suporte.

**Módulo CAFFMob.** Antes, o módulo rápido nascia com medidas fixas e só a espessura da lateral do padrão. Agora:
- nasce com as medidas externas da linha e do tipo, as chapas por papel e a montagem do padrão;
- a montagem (lateral ou base passante) muda a malha e a lista de corte;
- o editor e Selecionado mostram a montagem e a marca de padrão próprio.

**Padrão de Dimensões.** Antes, trocar ou editar o padrão atualizava na hora os módulos frameless e closets, com uma
confirmação e "Incluir medidas manuais". Agora:
- grava e ativa, e as duas perguntas decidem o que muda;
- só os módulos CAFFMob mudam, cada um na sua linha;
- o padrão guarda a montagem e a exporta para o Promob em `CAFF_MONTAGEM`.

**Conversão.** Nova:
- armários herdados viram módulos CAFFMob na mesma caixa, com relatório de perdas e uma etapa de desfazer;
- grupos salvos viram módulos da biblioteca do usuário em Geral.

## Preservadas

Regras 🟢 de `_reversa_sdd/domain.md` que continuam intactas:
- **R-01, R-02, R-03** (paredes e piso): não tocadas.
- **R-04 a R-08** (aberturas): não tocadas.
- **R-09, R-10** (plano de corte): o algoritmo não muda. A lista de peças do módulo CAFFMob só muda pela montagem do
  armário.
- A construção brasileira padrão da 001 (RN-03, laterais passantes) continua o padrão (`assembly = LATERAL`).

## Modificadas

Nenhuma regra 🟢 do `_reversa_sdd/domain.md` foi alterada ou removida. As mudanças estão em regras de features
anteriores e nas regras novas da 012 (RN-01 a RN-16):
- o comportamento de "aplicar o padrão" da 001 (D-16a, RN-23 "Incluir medidas manuais") virou as duas perguntas;
- a seção Inserir da 005 perdeu as galerias;
- os modos de seleção herdados deixaram de influenciar a seleção por componente da 011.
