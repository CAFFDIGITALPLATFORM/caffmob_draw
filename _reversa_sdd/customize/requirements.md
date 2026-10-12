# Personalizar Módulo e Biblioteca do Usuário (customize) — Requisitos

🟢 **CONFIRMADO** — contrato extraído de `caffmob_draw/customize/` (15 arquivos, 3.028 linhas: 1.432 no pacote e 1.596 em `adapters/`) em 2026-10-10, sem alterações sem commit na pasta (`git status` limpo). Confirmação de código não implica validação visual no Blender. 🟡 marca inferência (prioridade, intenção, efeito de API de biblioteca não executada); 🔴 marca lacuna. IDs RN/RF/D da feature 003 aparecem como "003 RN-xx"/"003 D-xx" (e "006 D-xx", "008 D-xx") para não colidir com os IDs desta unit. Contratos de outras units são citados, não redescritos: raiz e biblioteca do módulo (`classify.module_root`, `module_library`) em `_reversa_sdd/selection/`; agregados (`Object.btm_aggregate`) em `_reversa_sdd/aggregates/`; `PlacementMixin` (raycast, `cancel_placement`) em `_reversa_sdd/hb_placement/`; mecanismos internos das bibliotecas (troca de vão, estilos, puxadores, recálculos) em `_reversa_sdd/frameless/`, `_reversa_sdd/face_frame/`, `_reversa_sdd/closets/`; malha e portas do módulo paramétrico em `_reversa_sdd/geometry/`; barra lateral única (`sidebar_proxy`, `group_scope`) em `_reversa_sdd/ui/`; papéis de peça (`part_roles.classify`) em `_reversa_sdd/cutting/`.

## Visão Geral

🟢 Personalização **por instância** de um módulo já inserido (frente de cada vão, estilo, puxador, material por peça/grupo/frente, divisões internas), gravada em `Object.btm_custom` no vão, na peça ou na raiz, e reaplicada por um **adaptador por biblioteca** (frameless, face frame, closets, `btm` paramétrico) depois de cada reconstrução que a biblioteca fizer. Inclui a **biblioteca de módulos do usuário**: salvar o módulo personalizado como `.blend` + manifesto JSON `caffmob_draw.user-module` 1.1.0 + miniatura, listar, inserir com posicionamento modal, renomear, apagar e abrir a pasta (docstrings de `__init__.py`, `spec.py`, `props.py`, `reapply.py`, `library_io.py`; 003 bloco A; 006 e 008 estendem com estrutura, divisões e fundo recuado).

🟢 Princípio central: um `Spec` descreve **só o que o usuário mudou**; campo vazio = segue a biblioteca (`spec.py` docstring; 003 RN-01, D-01).

## Responsabilidades

- 🟢 Núcleo puro (sem `bpy`) da personalização: `Spec`/`Opening`/`Interior`, validação, serialização, posições de prateleira, grupos de material (`spec.py`).
- 🟢 Núcleo puro do manifesto do módulo salvo: montar, validar, ler, gravar, nome de arquivo seguro, estrutura e divisões em mm (`manifest.py`).
- 🟢 Propriedade persistente `Object.btm_custom` (`BTM_PG_CustomSpec`, `BTM_PG_GroupMaterial`) (`props.py`).
- 🟢 Contrato de adaptador por biblioteca e seleção do adaptador pela biblioteca da raiz (`adapters/__init__.py`), utilidades comuns de material, espessura, remoção por driver, espaços internos e fundo recuado (`adapters/common.py`), quatro adaptadores (`frameless.py`, `face_frame.py`, `closets.py`, `btm.py`).
- 🟢 Gancho pós-reconstrução `after_rebuild` chamado pelas bibliotecas e por `data/properties.update_cabinet_geom`; reaplicação com trava de reentrância (`reapply.py`).
- 🟢 Gravar, listar, inserir, renomear e apagar módulos na pasta do usuário (`library_io.py`).
- 🟢 Seis operadores de personalização `caffmob.customize_*` e cinco da biblioteca `caffmob.module_*` (`ops_customize.py`, `ops_library.py`).
- 🟢 Funções de desenho `draw_customize`/`draw_library` e as classes de painel usadas pela barra lateral única, sem registro próprio (`panels.py`).
- 🟢 Fornecer o contrato de adaptador a 24 arquivos consumidores (editor de armário, conversão legada, substituir, biblioteca de objetos, furação, menus) (`.reversa/context/modules.json` `dependents`).

## Regras de Negócio

- **RN-01** 🟢 Só o que mudou: campos de `btm_custom` e de `Opening` vazios (`""`, `None`, `'DEFAULT'`) significam "como a biblioteca faz"; `Spec.is_empty()` é verdadeiro sem vãos, materiais, puxador geral e agregados (`spec.py:Spec.is_empty`; `props.py` docstring).
- **RN-02** 🟢 Estilos, materiais e puxadores são guardados **por nome** e resolvidos no momento de aplicar; nome ausente no arquivo → aviso ("Material '{}' não existe neste arquivo", "Estilo '{}' não existe neste arquivo", "Puxador '{}' não encontrado") e nada é trocado (`common.py:material`; `frameless.py:_apply_style/_pull_object`; 003 RN-06).
- **RN-03** 🟢 Vãos endereçados por **caminho estável**, nunca pelo nome do objeto. Ordem estável `common.ordered`: chave `(round(x_mundo, 4), −round(z_mundo, 4), nome)`. Caminhos: frameless `bay<i>/opening<j>` (bays filhos diretos da raiz com `IS_FRAMELESS_BAY_CAGE`; vão estável = primeira jaula `IS_FRAMELESS_OPENING_CAGE` encontrada descendo pelos filhos, sem entrar em jaulas aninhadas); face frame `opening<i>` (jaulas folha `TAG_OPENING_CAGE`, sem jaula descendente); closets `opening<i>` (todas as jaulas `TAG_OPENING_CAGE`); `btm` `"module"` (a própria raiz) (`adapters/*.py:openings`).
- **RN-04** 🟢 Onde mora cada pedido: no **vão** `door_style`, `drawer_style`, `pull_model`, `pull_position`, `front_material`, `interior`, `slide_kind`; na **peça** `material`; na **raiz** `group_materials`, `pull_all_fronts` e, com ele, `pull_model` (no `btm`, vão = raiz, então tudo fica na raiz). O vão sobrevive à troca de frente da biblioteca (só os filhos dele são recriados) (`props.py` docstring; `frameless.py` docstring; 003 D-03).
- **RN-05** 🟢 Precedência de material nas bibliotecas de peças: material da **peça** > material das frentes do **vão** (só em frentes sem material próprio) > material do **grupo**. No `btm`: `front_material` do vão > grupo `FRENTES`; o material por peça não é aplicado (`common.py:apply_group_materials`; `frameless.py/face_frame.py/closets.py:reapply`; `btm.py:reapply`).
- **RN-06** 🟢 Puxador: o modelo vale do vão, ou da raiz quando `root.btm_custom.pull_all_fronts`; só é aplicado quando há modelo ou `pull_position != 'DEFAULT'`; `NO_PULL = "__NONE__"` = sem puxador; `""` = puxador do projeto. A posição `SIDE` existe no domínio mas nenhum adaptador a trata (EC-05; 🟢 **Decisão do titular (2026-10-10, questions.md#pergunta-40):** tirar `SIDE` do menu e manter o valor no domínio. Pendência de implementação: DT-01) (`frameless.py:reapply/_apply_pull/_set_pull_position`; `face_frame.py/closets.py:_apply_pull`; `btm.py:reapply`).
- **RN-07** 🟢 Frentes aceitas por biblioteca (`front_types`): frameless e face frame, as 7 de `FRONT_TYPES`; closets `DOOR_LEFT`, `DOOR_RIGHT`, `DOUBLE_DOORS`, `DRAWERS`, `OPEN`; `btm` `DOOR_LEFT`, `DOOR_RIGHT`, `DOUBLE_DOORS`, `FLIP_UP`, `OPEN` (sem gavetas) (`adapters/*.py:front_types`).
- **RN-08** 🟢 Capacidades por seção (`capabilities(root)` → `{seção: None | motivo}`): frameless, face frame e closets suportam `FRONTS`, `PULLS`, `MATERIALS`, `INTERIOR`; `btm` suporta as quatro e acrescenta `STYLES` com o motivo "O módulo paramétrico não tem estilos de porta". Seção com motivo aparece desabilitada com o texto (`adapters/*.py:capabilities`; `panels.py:_section`; 003 RF-01). _(Revisão 2026-10-10: o painel nunca mostra o motivo de `STYLES`: `panels.draw_customize` só esconde o menu Estilo e o laço de seções desabilitadas cobre `FRONTS`, `PULLS`, `INTERIOR` (e `MATERIALS`); "O módulo paramétrico não tem estilos de porta" não aparece na interface)_
- **RN-09** 🟢 Frameless: mais de uma gaveta só num vão cujo pai é o bay ("Mais de uma gaveta só num vão que ocupa o compartimento inteiro"); pilha máxima `MAX_STACKED_DRAWERS = 4` (acima disso aplica 4 e avisa) (`frameless.py:set_front`).
- **RN-10** 🟢 Interior: `shelves` 0–20 (`MAX_SHELVES`), `dividers` 0–10 (`MAX_DIVIDERS`), `drawers` 0–8 (`MAX_DRAWERS`); alturas digitadas (m, face de baixo de cada prateleira a partir da base do vão) em quantidade igual às prateleiras, estritamente crescentes, a primeira > 0 e, com altura interna conhecida, a última < altura interna; sem alturas, vãos livres iguais `gap = (H − n·t)/(n+1)` e posição `gap·(i+1) + t·i` (`spec.py:validate_interior/shelf_positions`; executado: 3 prateleiras, H = 0,72, t = 0,018 → 0,1665 / 0,351 / 0,5355).
- **RN-11** 🟢 Interior por biblioteca: frameless monta gavetas internas, divisórias, alturas digitadas ou prateleiras iguais (nessa precedência); face frame substitui itens de prateleira/gaveta interna, cria **uma** divisória por vez e ignora alturas (avisa); closets só prateleiras (divisórias, gavetas internas e alturas avisam); `btm` só prateleiras (`btm_cabinet.shelves`; divisórias, gavetas e alturas avisam) (`adapters/*.py:set_interior`).
- **RN-12** 🟢 Reaplicação: `after_rebuild(context, obj)` sai sem custo se o módulo não tem personalização nem estrutura (`has_custom`); `reapply` é bloqueado por nome da raiz enquanto roda (`_running`) para não recursar quando o próprio adaptador dispara recálculo; com estrutura (`has_structure`), ainda reafirma remoções/espessuras, fundo recuado com `auto_back` e refaz divisões, extras, interiores e corrediças (`reapply.py`; 003 D-04; 006 D-07, D-10; 008 D-11, D-12).
- **RN-13** 🟢 Grupos de material pela função da peça: frente (`IS_CABINET_FRONT` ou `hb_part_role` `DOOR`/`DRAWER_FRONT`/`PULLOUT_FRONT`, ou componente `POR`) → `FRENTES`; `BACK`, `FUN_INF`, `FUN_SUP`, `FUN_ALT` → `FUNDO`; `PRAT`, `DIV` → `INTERNO`; resto → `CAIXA`. O veio é preservado usando `"<nome> ROTATED"` no `Rail Material` quando existir (`spec.py:group_of_component`; `common.py:part_group/rotated/set_cutpart_material`).
- **RN-14** 🟢 Módulo salvo = três arquivos de mesmo nome base em `extension_path_user(<pacote>, "modules")/<categoria sanitizada>/`: `.blend` (`libraries.write`, `RELATIVE_ALL`, `fake_user=True`), `.json` (manifesto), `.png` (256 px). Nome de arquivo sanitizado por `file_stem` (troca `<>:"/\|?*` e controles por `_`, tira espaços e pontos finais; vazio → `"modulo"`); o nome original fica no manifesto. Categoria vazia → `"Geral"` (`library_io.py:paths_for/save`; `manifest.py:file_stem`; 003 D-10).
- **RN-15** 🟢 Gravação sem resto: `.blend` e `.json` vão para temporários na pasta destino e só então `os.replace`; `OSError`/`RuntimeError` apaga os temporários e devolve a mensagem com a pasta (`library_io.py:save`). _(Revisão 2026-10-10: falha entre os dois `os.replace` (linhas 313-314 de `library_io.py`) deixa o `.blend` novo com o `.json` antigo: o temporário do `.json` é apagado, mas o `.blend` já foi trocado)_
- **RN-16** 🟢 Nome repetido na mesma categoria exige marcar "Substituir o módulo existente"; sem isso o operador cancela e nada é escrito (`ops_library.py:BTM_OT_ModuleSave.execute/draw`; 003 RN-05, D-11).
- **RN-17** 🟢 Manifesto aceito: `format == "caffmob_draw.user-module"`, major de `schema_version` inteiro e ≤ 1 (0.x também passa), `library` em `FRAMELESS`/`FACE_FRAME`/`CLOSETS`/`BTM`, `name` e `root_object` não vazios; só sem esses erros valida `spec` e estrutura/divisões (`manifest.py:validate`; executado).
- **RN-18** 🟢 Inserir: manifesto inválido → aviso e nada inserido; o `.blend` é a fonte da verdade (o `spec` do manifesto é validado e descartado; a reaplicação lê o `btm_custom` gravado nos objetos); estilos de porta ausentes → um aviso geral que substitui os avisos por estilo; divisões ganham `uid` novo e são refluídas (`library_io.py:load/_renew_divisions`; 003 RF-09).
- **RN-19** 🟢 "Limpar personalização do vão" zera `door_style`, `drawer_style`, `pull_model`, `front_material` e `pull_position = 'DEFAULT'`, mas **não** reaplica nem desfaz a geometria: avisa "troque o estilo do projeto para refazer as frentes" (`ops_customize.py:BTM_OT_CustomizeClear`).
- **RN-20** 🟢 Remoção de chapa (006): esconde por **driver** em `hide_viewport`/`hide_render` com a variável `btm_rm` lendo o idprop `btm_removed`, somada ao driver que a biblioteca já tenha (`(expr) or btm_rm`); restaurar remove só driver que é só nosso. Bibliotecas de peças fazem só "Manter tudo", exceto frameless `BOTTOM` + `EXTEND` pelo `Remove Bottom` nativo; `btm` aceita os três modos em todas as chapas (`common.py:set_removed/keep_only_caps`; `frameless.py:structure_caps/remove_part`; `btm.py:structure_caps`; 006 D-07, D-08).
- **RN-21** 🟢 Fundo recuado (008): nas bibliotecas de peças a peça do fundo anda `setback` para −Y da raiz por `delta_location` (que drivers e recálculos não sobrescrevem); no `btm` refaz a malha. Fundo removido pelo projetista continua removido (`common.py:set_back_recess`; `btm.py:set_back_recess`; `reapply.py` docstring; 008 D-11).

## Requisitos Funcionais

| ID | Requisito | Prioridade | Critério de Aceite | Confiança |
|----|-----------|-----------|-------------------|-----------|
| RF-01 | Painel "Personalizar módulo" para o módulo do objeto ativo (raiz, peça, frente ou vão), com uma caixa por vão (frente, estilo, puxador, material das frentes, interior, limpar), Materiais por grupo, material da peça ativa e "Salvar como módulo"; seções sem suporte desabilitadas com o motivo | Must | CA-01, CA-02 | 🟢 |
| RF-02 | Trocar a frente de um vão pela própria biblioteca (porta esquerda/direita/dupla, gavetas 1–8, basculante, painel fixo, vazio), filtrada por `front_types` | Must | CA-03, CA-04, CA-05 | 🟢 |
| RF-03 | Aplicar um estilo de porta (ou de gaveta) só nas frentes de um vão; `""` volta ao estilo do módulo | Must | CA-06, CA-07 | 🟢 |
| RF-04 | Trocar o puxador (modelo, posição, "sem puxador", "do projeto") de um vão ou de todas as frentes do módulo | Must | CA-08, CA-09 | 🟢 |
| RF-05 | Trocar o material das frentes de um vão, de um grupo (`CAIXA`, `FRENTES`, `FUNDO`, `INTERNO`) ou da peça ativa; `""` volta ao da biblioteca | Must | CA-10, CA-11 | 🟢 |
| RF-06 | Editar o interior do vão: prateleiras, divisórias, gavetas internas e alturas digitadas na unidade da cena (`"a; b; c"`) | Must | CA-12, CA-13 | 🟢 |
| RF-07 | Limpar a personalização de estilo/puxador/material de um vão | Could | CA-14 | 🟢 |
| RF-08 | Reaplicar a personalização (e a estrutura 006/008) depois de cada reconstrução da biblioteca, pelo gancho `after_rebuild` | Must | CA-15, CA-16 | 🟢 |
| RF-09 | Salvar o módulo selecionado na biblioteca do usuário com nome, categoria e miniatura opcional; confirmar substituição | Must | CA-17, CA-18, CA-19 | 🟢 |
| RF-10 | Inserir um módulo salvo com posicionamento modal (clique posiciona, `R` gira 90°, Esc/botão direito cancela) ou direto (`place=False`) | Must | CA-20, CA-21, CA-22 | 🟢 |
| RF-11 | Listar por categoria, renomear, apagar (com confirmação) e abrir a pasta dos módulos | Should | CA-23, CA-24 | 🟢 |
| RF-12 | Expor o contrato de adaptador (`openings`, `read`, `set_front`, `set_interior`, `reapply`, `capabilities`, `front_types`, `style_names`, `pull_items` e o contrato opcional de estrutura via `common.call`) a consumidores sem operador | Must | CA-25 | 🟢 |
| RF-13 | Serializar/validar `Spec` e manifesto em Python puro, testável sem Blender | Must | CA-26, CA-27 | 🟢 |

## Requisitos Não Funcionais

| Tipo | Requisito inferido | Evidência no código | Confiança |
|------|--------------------|---------------------|-----------|
| Desempenho | Módulo sem personalização nem estrutura não paga a reaplicação a cada reconstrução | `reapply.py:after_rebuild` (`has_custom` antes de tudo) | 🟢 |
| Robustez | Reentrância bloqueada por nome da raiz (o adaptador dispara recálculos que chamam o gancho de novo) | `reapply.py:_running` | 🟢 |
| Integridade de dados | Gravação atômica do `.blend` e `.json` (temporário + `os.replace`); erro não deixa parciais, exceto falha entre os dois `os.replace` (`.blend` novo + `.json` antigo) | `library_io.py:save` | 🟢 | _(Revisão 2026-10-10: `library_io.py:save` linhas 313-314)_
| Portabilidade | Nomes de arquivo seguros em Windows/Linux; caminhos do `.blend` relativos; abrir pasta por SO (`startfile`/`open`/`xdg-open`) | `manifest.py:file_stem`; `library_io.py:save` (`RELATIVE_ALL`); `ops_library.py:BTM_OT_ModuleOpenFolder` | 🟢 |
| Compatibilidade | Formato versionado (`schema_version` 1.1.0, leitor aceita major ≤ 1; campos 1.1.0 opcionais, 1.0.0 continua válido) | `manifest.py`; `tests/test_module_manifest.py:test_1_0_0_continua_valido` | 🟢 |
| Compatibilidade de API | Inputs de Geometry Nodes só por `compat.try_set_gn_input`/`try_get_gn_input`/`gn_input_data_path`/`try_get_gn_input_by_id` | `common.py`; `frameless.py:_apply_pull`; `library_io.py:_geo_node_refs` | 🟢 |
| Desfazer | Operadores que alteram a cena têm `{'REGISTER', 'UNDO'}`; os de disco não declaram `UNDO` | `ops_customize.py`; `ops_library.py` | 🟢 |
| Testabilidade | `spec` e `manifest` sem `bpy` (import tardio no `__init__`) | `customize/__init__.py:_modules`; 16 testes puros | 🟢 |
| Internacionalização | Textos por `tr`/`N_` (`data/translations/customize.json`), exceto 6 `self.report` com texto literal ("Vão não encontrado…", "Alturas inválidas", "Personalização do vão removida…", "Digite um nome para o módulo", "Módulo não encontrado", "Módulo ou nome inválido"), que ficam em português no en_US | todos os arquivos | 🟢 | _(Revisão 2026-10-10: `ops_customize.py:75,225,247`; `ops_library.py:63,171,195`)_

> Inferido a partir do código. Sem timeouts, threads ou rede.

## Critérios de Aceitação

```gherkin
CA-01 — Painel por biblioteca (RF-01)
Dado um balcão frameless selecionado (raiz, peça ou frente)
Quando o grupo "Personalizar" desenha draw_customize
Então aparece "Módulo: <raiz>", uma caixa "Vão n: <frente>" por caminho de adapter.read (gavetas > 1: "n gavetas") com os botões Frente, Estilo, "Puxador: do projeto", "Material das frentes: do módulo", "Interior: 0 prat., 0 div., 0 gav." e X; a caixa Materiais com os 4 grupos; e "Salvar como módulo"

CA-02 — Painel sem módulo ou com seção sem suporte (RF-01)
Dado um objeto que não pertence a módulo
Quando o painel desenha
Então mostra "Selecione um módulo" e o poll de BTM_PT_CustomizeModule é falso
E num módulo btm o menu Estilo não aparece (capabilities['STYLES'] tem motivo)

CA-03 — Trocar frente (RF-02; fumaça passo 1)
Dado o primeiro vão de um balcão frameless que ocupa o bay inteiro
Quando set_front(..., 'DRAWERS', 3) e depois set_front(..., 'DOOR_RIGHT')
Então devolvem [] e, após o primeiro, os três vãos lidos têm front_type 'DRAWERS'

CA-04 — Frente recusada (RF-02)
Dado um vão de closets
Quando set_front(..., 'FLIP_UP')
Então devolve ["O closets não tem a frente 'Basculante'"] e nada muda
E no frameless, 3 gavetas num vão cujo pai não é o bay devolvem a mensagem de RN-09; 6 gavetas aplicam 4 e avisam "O frameless empilha no máximo 4 gavetas"

CA-05 — Operador de frente
Dado o vão "bay0/opening0"
Quando caffmob.customize_set_front com front='DRAWERS' é invocado
Então abre diálogo com drawer_count (1–8); ao confirmar chama set_front e reapply e reporta "Frente trocada para Gavetas" (ou WARNING com as mensagens unidas por " | ")
E com path inexistente reporta "Vão não encontrado; selecione o módulo de novo" e devolve CANCELLED

CA-06 — Estilo por vão (RF-03; fumaça passos 1, 3, 4)
Dado door_style = "Vidro" num vão frameless
Quando reapply roda
Então as portas do vão têm DOOR_STYLE_NAME "Vidro" e DOOR_STYLE_INDEX = índice atual do estilo; e continuam assim após mudar o estilo do projeto (after_rebuild)

CA-07 — Estilo ausente (RF-03)
Dado door_style = "Inexistente"
Quando reapply roda
Então a frente não muda e a lista de avisos contém "Estilo 'Inexistente' não existe neste arquivo" (closets: "... não existe no closets")

CA-08 — Puxador em todas as frentes (RF-04)
Dado um módulo com 3 vãos
Quando caffmob.customize_set_pull com all_fronts=True, model=X, position='BOTTOM'
Então root.btm_custom.pull_all_fronts = True, root.btm_custom.pull_model = X, todos os vãos com pull_position 'BOTTOM', e reapply usa X em todas as frentes

CA-09 — Sem puxador e puxador ausente (RF-04)
Dado model = NO_PULL num vão
Quando reapply roda
Então no frameless o input Object do GeoNodeHardware fica None; no face frame/closets/btm os objetos de puxador são removidos
E com um arquivo de puxador inexistente o aviso "Puxador '<nome>' não encontrado" é devolvido e os puxadores ficam como estavam

CA-10 — Materiais por grupo e peça (RF-05; fumaça passo 1)
Dado grupo CAIXA = "MDF" e uma lateral com btm_custom.material = "Laca"
Quando reapply roda e depois o estilo do projeto é refeito
Então as peças de caixa ficam com Top/Bottom Surface "MDF", a lateral com "Laca", e o resultado persiste após o recálculo

CA-11 — Material inexistente (RF-05)
Dado front_material = "Nada"
Quando reapply roda
Então nenhum material é trocado e o aviso "Material 'Nada' não existe neste arquivo" aparece uma vez (common.unique)

CA-12 — Interior com alturas (RF-06; fumaça passo 1)
Dado um vão alto frameless
Quando set_interior(Interior(shelves=2, heights=[0.2, 0.45]))
Então devolve [], btm_custom.interior guarda o JSON e o splitter vertical é criado; Interior(drawers=2) cria 2 "Rollout"

CA-13 — Interior inválido (RF-06)
Dado o mesmo vão
Quando set_interior(Interior(shelves=1, heights=[5.0]))
Então devolve ['altura fora do vão'] e nada é gravado
E no operador, alturas que units.parse_length não entende reportam "Alturas inválidas" e CANCELLED

CA-14 — Limpar vão (RF-07)
Dado um vão com estilo, puxador e material
Quando caffmob.customize_clear
Então os quatro textos ficam vazios, pull_position 'DEFAULT', FINISHED, e a geometria não muda até o próximo recálculo

CA-15 — Gancho sem custo (RF-08)
Dado um módulo sem btm_custom preenchido e sem estrutura
Quando a biblioteca chama after_rebuild(context, obj)
Então devolve [] sem chamar o adaptador

CA-16 — Gancho com estrutura (RF-08)
Dado um módulo com btm_structure.components não vazio
Quando after_rebuild roda
Então chama adapter.reapply, depois reaffirm, set_back_recess (se auto_back e RECESSED) e reflow/sync de divisões, extras, interiores e corrediças; uma chamada aninhada durante isso não faz nada

CA-17 — Salvar (RF-09; fumaça passo 2)
Dado o balcão personalizado
Quando caffmob.module_save(module_name="Balcão vidro", category="Balcões", thumbnail=False)
Então FINISHED e list_modules devolve [("Balcão vidro", "Balcões", has_manifest=True)] com .blend e .json em modules/Balcões/

CA-18 — Nome repetido (RF-09)
Dado "Balcão vidro" já salvo em "Balcões"
Quando salvo de novo sem overwrite
Então WARNING "O módulo 'Balcão vidro' já existe; marque "Substituir" para gravar por cima", CANCELLED e nada escrito; com overwrite os arquivos são substituídos

CA-19 — Falha ao gravar (RF-09)
Dado uma pasta sem permissão de escrita
Quando save roda
Então devolve (None, ["Não foi possível gravar o módulo em <pasta>: <erro>"]), nenhum temporário fica, o operador reporta ERROR e CANCELLED
E com nome vazio reporta "Digite um nome para o módulo"

CA-20 — Inserir direto (RF-10; fumaça passo 6)
Dado um arquivo novo e o módulo salvo
Quando caffmob.module_insert(filepath=<blend>, place=False)
Então FINISHED, raiz ativa e selecionada, no lugar salvo, e adapter.read devolve door_style "Vidro" e front_material "Laca branca"

CA-21 — Inserir com posicionamento (RF-10)
Dado a viewport ativa
Quando invoco caffmob.module_insert e movo o mouse
Então a raiz segue o raycast com snap à grade, R soma 90° no Z da raiz, clique esquerdo devolve FINISHED; Esc/botão direito chama cancel_placement e devolve CANCELLED

CA-22 — Inserir falha (RF-10)
Dado um manifesto com format diferente, ou major 2, ou um .blend sem raiz de módulo
Quando insiro
Então reporta "Manifesto inválido: ..." (nada carregado) ou "Nenhum módulo encontrado no arquivo" (objetos carregados são removidos), e CANCELLED
E filepath fora da lista reporta ERROR "Módulo não encontrado: <caminho>"

CA-23 — Renomear (RF-11)
Dado "A" e "B" na mesma categoria
Quando renomeio "A" para "C"
Então os três arquivos passam a C.*, o manifesto tem name "C"; renomear para "B" devolve "Já existe um módulo 'B' nessa categoria" e nada muda

CA-24 — Apagar (RF-11)
Dado um módulo listado
Quando caffmob.module_delete é confirmado
Então .blend, .png e .json somem e reporta "Módulo apagado: <nome>"; filepath desconhecido reporta "Módulo não encontrado"

CA-25 — Contrato para consumidores (RF-12)
Dado um adaptador sem a função opcional 'inner_spaces'
Quando common.call(adapter, 'inner_spaces', context, root)
Então executa default_inner_spaces e devolve {}; remove_part padrão devolve ["Esta biblioteca não tem estrutura editável"]

CA-26 — Spec ida e volta (RF-13; test_customize_spec)
Dado um Spec com vão DOUBLE_DOORS, estilo, puxador, interior com alturas e materiais
Quando to_dict → from_dict
Então o resultado é igual; vão sem interior não grava a chave 'interior'; validate devolve []

CA-27 — Manifesto inválido (RF-13; test_module_manifest)
Dado texto que não é JSON, ou format/library errados, ou schema 2.x
Quando manifest.loads
Então devolve (dados ou None, None, [mensagens]); estrutura com modo 'X', espessura negativa, space 's0.c' ou orientação 'Z' gera as cinco mensagens correspondentes
```

## Prioridade (MoSCoW)

| Requisitos | Classificação | Justificativa |
|---|---|---|
| RF-01, RF-02, RF-03, RF-04, RF-05, RF-06 | 🟡 Must | 003 RF-01..RF-06 (Must); `adapters.*` usados por 6 arquivos do `cabinet_editor` | _(Revisão 2026-10-10: importam `customize`: `bridge`, `ops_actions`, `ops_editor`, `reflow_handler`, `scene_divisions`, `scene_parts`)_
| RF-08 | 🟢 Must | Chamado pelas três bibliotecas de produto e por `data/properties.update_cabinet_geom` (6 chamadas: 5 nas bibliotecas + `update_cabinet_geom`, que é o `update` de 22 propriedades de `btm_cabinet`) | _(Revisão 2026-10-10: `grep after_rebuild`; `grep -c update=update_cabinet_geom data/properties.py` = 22; os "12 pontos" não foram encontrados)_
| RF-09, RF-10 | 🟡 Must | 003 RF-07, RF-09; `library_io` usado por `legacy/groups`, `move_over/ops_substitute`, `library_panel`, `ui/my_modules` |
| RF-12, RF-13 | 🟢 Must | Contrato consumido por 24 arquivos; núcleo com 16 testes |
| RF-11 | 🟡 Should | 003 RF-10; há a pasta como alternativa |
| RF-07 | 🟡 Could | Atalho; não refaz a geometria |

## Rastreabilidade de Código e Verificação

| Arquivo | Símbolos | Evidência |
|---|---|---|
| `caffmob_draw/customize/spec.py` | `SECTIONS`, `FRONT_TYPES`, `PULL_POSITIONS`, `NO_PULL`, `GROUPS`, limites, `Interior`, `Opening`, `Spec`, `to_dict`, `from_dict`, `validate`, `validate_interior`, `shelf_positions`, `group_of_component`, `interior_to_json`, `interior_from_json` | 🟢 Código; `test_customize_spec` |
| `caffmob_draw/customize/manifest.py` | `FORMAT`, `SCHEMA_VERSION`, `SUPPORTED_MAJOR`, `LIBRARIES`, `ROLES`, `MODES`, `ORIENTATIONS`, `file_stem`, `build`, `structure_of`, `divisions_of`, `validate`, `dumps`, `loads` | 🟢 Código; `test_module_manifest` |
| `caffmob_draw/customize/props.py` | `PULL_POSITION_ITEMS`, `GROUP_ITEMS`, `BTM_PG_GroupMaterial`, `BTM_PG_CustomSpec` | 🟢 Código |
| `caffmob_draw/customize/reapply.py` | `DIVISION_SIGNATURE`, `has_structure`, `has_custom`, `reapply`, `after_rebuild` | 🟢 Código; fumaça 003 |
| `caffmob_draw/customize/adapters/__init__.py` | `module_root`, `for_root`, `for_object` | 🟢 Código |
| `caffmob_draw/customize/adapters/common.py` | materiais, `call` + `default_*`, caixas, remoção, espessura, `set_back_recess` | 🟢 Código |
| `caffmob_draw/customize/adapters/{frameless,face_frame,closets,btm}.py` | contrato completo por biblioteca | 🟢 Código; fumaça 003 passos 1, 3, 4, 5 |
| `caffmob_draw/customize/library_io.py` | `modules_root`, `paths_for`, `exists`, `list_modules`, `build_manifest`, `save`, `load`, `delete`, `rename` | 🟢 Código; fumaça 003 passos 2, 6 |
| `caffmob_draw/customize/ops_customize.py` | 6 operadores `caffmob.customize_*` | 🟢 Código |
| `caffmob_draw/customize/ops_library.py` | 5 operadores `caffmob.module_*` | 🟢 Código; fumaça 003 |
| `caffmob_draw/customize/panels.py` | `draw_customize`, `draw_library`, `BTM_PT_CustomizeModule`, `BTM_PT_ModuleLibrary` (não registrados) | 🟢 Código |

🟢 Executado em 2026-10-10: `cd tests && PYTHONDONTWRITEBYTECODE=1 python3 -m unittest test_customize_spec test_module_manifest -v` → **16 testes aprovados** (8 de `spec`, 8 de manifesto). Executados também em Python puro nesta extração: `shelf_positions(3, 0.72, 0.018)`, as quatro mensagens de `validate_interior`, `file_stem` (`'a/b:c?.. '` → `'a_b_c_'`, `'...'` e `'  '` → `'modulo'`), `schema_version` `'2.0.0'`/`'abc'` recusadas e `'0.9'` aceita, `interior_from_json('{"shelves":"x"}')` → `ValueError` (EC-09). 🟢 `tests/blender_003_customize_smoke.py` não foi executado (Blender ausente). _(Revisão 2026-10-10: executada no Blender 5.2.0 LTS (`/opt/blender/blender`) → "blender_003_customize_smoke: OK")_

## Lacunas e Divergências

- 🟢 Inserir um `.blend` sem `.json` quebra com `UnboundLocalError` (`missing` só é definido com manifesto), contra o contrato "inserido sem reaplicar `spec`" e `domain.md` RN-CUSTOMIZE-13 (EC-01). Afeta também `move_over/ops_substitute.substitute`. _(Revisão 2026-10-10: reproduzido no Blender 5.2: `library_io.load` levanta `UnboundLocalError` com 26 objetos já ligados à cena; `caffmob.module_insert` termina em `RuntimeError`)_
- 🟢 Closets: `_missing_styles` não conhece os estilos do closets e trata todos como ausentes; o aviso geral falso também apaga os avisos reais de estilo (EC-02). _(Revisão 2026-10-10: reproduzido no Blender 5.2: roupeiro com `WIDE_SHAKER` (existe) e `NAO_EXISTE` → único aviso "Estilos ausentes neste arquivo (mantida a geometria salva): NAO_EXISTE, WIDE_SHAKER"; o aviso real "Estilo 'NAO_EXISTE' não existe no closets" sumiu)_
- 🟢 A posição de puxador `SIDE` ("Lateral") não tem efeito em nenhum adaptador (EC-05). 🟢 **Decisão do titular (2026-10-10, questions.md#pergunta-40):** tirar `SIDE` de `PULL_POSITION_ITEMS`, mantendo o valor no domínio para manifestos antigos. Pendência de implementação: DT-01.
- 🟢 O painel só grava `door_style`: o menu Estilo não define `kind`, então `drawer_style` não é editável pelo painel (EC-06). _(Revisão 2026-10-10: `panels.py:53` chama `operator_menu_enum(..., "style")` sem `kind`; `ops_customize.py:107,114` (padrão `DOOR`))_
- 🟢 Divergência com `_reversa_forward/003-modulos-agregados-reposicionar/interfaces/user-module-file.md`: o exemplo 1.0.0 usa `heights_mm`, `parts: [{group, material}]` e `styles.cabinet_style`; o código grava `heights` em metros, `part_materials`/`group_materials` como dicionários e só `styles.door_styles` (que inclui estilos de gaveta). O contrato diz "estilo ausente → usa o padrão da biblioteca"; o código mantém a geometria salva e avisa. `aggregates[].parent_path` é o **nome** do pai, não um caminho (EC-15). _(Revisão 2026-10-10: `user-module-file.md` linhas 31, 38, 40, 41 e 54 contra `library_io.build_manifest` e `load`)_
- 🟢 Divergência com `_reversa_sdd/flowcharts/customize.md`: o fluxograma põe "grava o pedido em `btm_custom`" antes de `set_front` e liga `reapply.reapply` → `has_structure`; no código `set_front` não grava `btm_custom` (só `set_interior` grava `interior`) e a reafirmação de estrutura só ocorre em `after_rebuild`, não nos operadores. _(Revisão 2026-10-10: `flowcharts/customize.md` linhas 14 e 22; `ops_customize.BTM_OT_CustomizeSetFront.execute` e `reapply.reapply` sem `has_structure`)_
- 🟢 `spec.py` comenta `part_materials` como "caminho da peça → material"; `common.read_materials` usa `obj.name`. _(Revisão 2026-10-10: `spec.py:50`; `common.py:98`)_
- 🟢 `spec.shelf_positions`, `Spec.is_empty`, `manifest.structure_of` e `manifest.divisions_of` só são usados pelos testes (e `Spec.is_empty` nem por eles: nenhum uso no repositório); a estrutura e as divisões do manifesto não são aplicadas na inserção (viajam no `.blend`). _(Revisão 2026-10-10: `grep` em `caffmob_draw/` e `tests/`: `shelf_positions` só em `test_customize_spec.py:54-59`, `structure_of`/`divisions_of` do manifesto só em `test_module_manifest.py:48-64`, `is_empty()` sem chamada)_
- 🟢 `slide_kind` é campo de `btm_custom`, mas nenhum código desta unit o lê; `has_custom` não o considera (gravado por `cabinet_editor/bridge.py:623` e lido por `cutting/hardware.py:52`, 008). _(Revisão 2026-10-10: `grep slide_kind`)_
- 🟢 `state-machines.md` não tem seção desta unit; o único ciclo de estados é o modal de inserção (ver `design.md`). _(Revisão 2026-10-10: `state-machines.md` não cita customize/personalização)_
