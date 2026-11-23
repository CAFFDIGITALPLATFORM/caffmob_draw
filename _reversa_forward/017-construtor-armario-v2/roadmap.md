# Roadmap: Construtor de armário v2 no CAFFMob Draw

> Identificador: `017-construtor-armario-v2`
> Data: `2026-11-19`
> Requirements: `_reversa_forward/017-construtor-armario-v2/requirements.md`
> Especificação que prevalece: `novo_arm_building/CAFF_MOB_Construtor_Armarios_Blender_5_2/caff_construtor_armarios_blender_5_2/`
> Escopo (clarify 2026-11-19): todos os armários, inclusive módulos de biblioteca; superfície na vista 3D; móveis antigos preservados
> Confidência: 🟢 CONFIRMADO, 🟡 INFERIDO, 🔴 LACUNA

## 1. Resumo da abordagem

O motor anexado passa a ser o construtor do pacote, num pacote novo `caffmob_draw/armario_v2/` com núcleo puro e camada Blender separados. O núcleo (`spec`, `chapas`, `conferencia`, `gavetas`, `portas`, `internos`) calcula todas as peças em milímetros sem `bpy`; a camada Blender (`props`, `build`, `panel`, `menu`, `ops`, `anim`, `hud`) grava o contrato no armário, cria malhas, desenha o painel da vista 3D e anima abrir/fechar.

O `cabinet_editor` não é apagado: perde o registro da interface (janela, modal e painéis), mantém a galeria de estruturas registrada — `library_panel/ops_cabinet.py:46-47` chama `caffmob.structure_gallery` sem guarda e a galeria é seletor, não o editor 2D — e continua registrando os dados que o resto do pacote usa (`data_props`, `previews`, `reflow_handler`). Seus núcleos puros — `structure`, `structures_core`, `divisions`, `structure_inputs` — continuam servindo `geometry/mesh_gen.py`, `customize/adapters`, `standards` e `cutting`.

O abridor mantém o `bl_idname` `caffmob.cabinet_editor`, agora abrindo o painel novo: `ui/sidebar_vocab.py`, `ui/object_properties.py`, `ui/context_menu.py`, `target/commands.py` e `library_panel/ops_cabinet.py` continuam funcionando sem edição. Só os dois guardas que citam o modal antigo (`collision/guard.py`, `stick/settle.py`) mudam.

O corte ganha um adaptador que lê o papel gravado em cada malha gerada (`Object.btm_armario_parte`), somado aos adaptadores existentes em `part_extractor.extract_production_parts`.

## 2. Princípios aplicados

`.reversa/principles.md` não existe nesta instalação (nenhum `/reversa-principles` executado). A verificação usa as regras do repositório (`CLAUDE.md`/`AGENTS.md`) como princípios de fato, marcadas 🟡.

| Princípio | Como a feature se relaciona | Status |
|-----------|------------------------------|--------|
| I. Núcleo puro fora do `bpy` 🟡 | `spec`, `chapas`, `conferencia`, `gavetas`, `portas`, `internos` não importam `bpy`; só `build`, `panel`, `ops`, `anim` e `hud` tocam a cena | respeita |
| II. Diferenças de versão só em `compat.py` 🟡 | Import de OBJ, `prop` e desenho usam `compat` quando houver variação; nenhum `mod["Socket_X"]` novo | respeita |
| III. Propriedades lidas por atributo 🟡 | Todo dado novo é `bpy.props` em PropertyGroup; nada é lido por `obj["..."]` | respeita |
| IV. Um passo de desfazer por comando 🟡 | `Gerar`, `Aplicar`, `Cancelar`, `Abrir/Fechar`, `Duplicar` e `Excluir` são operadores com `'UNDO'`; abrir o painel não cria passo | respeita |
| V. `unregister()` desfaz tudo 🟡 | Menu, timer, `draw_handler`, PropertyGroups e a coleção de preview saem no desregistro | respeita |
| VI. Reaproveitar antes de criar 🟡 | Reusa `part_extractor.limit_status`, `cabinet_editor.structure.carcass_lengths`, `standards.api` e o catálogo de i18n | respeita |
| VII. Texto novo em português, catálogo nas duas línguas 🟡 | `tr()`/`N_()` com `pt_BR` e `en_US`; `tests/test_i18n_coverage.py` cobre | respeita |
| VIII. Não editar a cópia espelhada da raiz 🟡 | Toda escrita em `caffmob_draw/` e `tests/` | respeita |
| IX. RF-26 tira o editor de móveis antigos 🟡 | Conflito consciente: o móvel antigo deixa de ser editável pelo editor 2D. É decisão do titular (clarify Q3); o painel avisa e o móvel continua na cena e no corte | conflita (aceito) |

## 3. Decisões técnicas

| ID | Decisão | Justificativa | Alternativas descartadas | Confidência |
|----|---------|----------------|--------------------------|-------------|
| D-01 | Pacote novo `caffmob_draw/armario_v2/`, com núcleo puro e camada Blender separados | O motor anexado já é uma unidade com contrato próprio; separar mantém o cálculo testável fora do Blender e não mistura com os 38 arquivos do `cabinet_editor` | (a) reescrever dentro de `cabinet_editor/`; (b) adaptar as bibliotecas paramétricas para emitir o modelo novo | 🟢 |
| D-02 | O armário guarda o spec em `Object.btm_armario` (`BTM_PG_ArmarioV2`) e cada peça em `Object.btm_armario_parte` | RN-17 exige reabrir com o mesmo estado; RN-24 exige papel gravado na malha | (a) JSON em custom property única; (b) `Text` datablock por armário; (c) só scene-level | 🟢 |
| D-03 | `caffmob.cabinet_editor` passa a abrir o painel novo, mantendo o `bl_idname` | Cinco pontos do pacote chamam esse id (`ui/sidebar_vocab.py:25`, `ui/object_properties.py:433`, `ui/context_menu.py:35`, `target/commands.py:68`, `library_panel/ops_cabinet.py:79`); trocar o id obrigaria a editar todos | (a) id novo `caffmob.armario_v2` + editar os cinco; (b) dois ids convivendo | 🟢 |
| D-04 | `cabinet_editor.register()` fica com `data_props`, `previews`, `reflow_handler` e `gallery`; só janela, modal, painéis e ops saem do registro | `data_props` registra os PropertyGroups que os módulos antigos usam; `mesh_gen`, `customize`, `standards` e `cutting` importam os núcleos puros sem depender do registro; `gallery` fica porque `library_panel/ops_cabinet.py:46` chama `caffmob.structure_gallery` sem guarda e o RF-24 entra por ali (decisão do titular, 2026-11-21) | (a) apagar `cabinet_editor` inteiro (quebra `mesh_gen` e o corte); (b) deixar toda a UI registrada; (c) tirar `gallery` e adaptar `ops_cabinet.py` | 🟢 |
| D-05 | Superfície: painel `BTM_PT_ArmarioV2` na sidebar existente, com as sete abas num `EnumProperty` e sub-abas (Divisões, Gavetas) em segundo `EnumProperty` | RN-22 e o add-on anexo; a sidebar `View3D > CAFFMob Draw` já é o lugar das ferramentas | (a) janela 2D própria; (b) `Popup` por aba; (c) `N`-panel separado | 🟢 |
| D-06 | Menu de contexto em `VIEW3D_MT_object_context_menu` via `_append`/`_remove`, com itens filtrados pelo armário ativo | RN-22 e `mockup_construtor_armarios.html#openContextMenu`; o gancho é o mesmo já usado em `ui/context_menu.py` | (a) `VIEW3D_MT_object`; (b) atalhos só | 🟢 |
| D-07 | Sem modal: `Gerar` reconstrói a partir do spec; `Cancelar` restaura o snapshot JSON gravado na abertura e apaga as peças geradas | RN-18/RF-22 pedem um passo de desfazer por confirmação, não um modal; o painel pode ficar aberto | (a) modal como o editor atual; (b) reconstruir a cada `update` de propriedade | 🟢 |
| D-08 | Abrir/Fechar por timer de 16 ms com no máximo 18 quadros, estado em `btm_armario.aberto` e rótulo oposto | RN-10 e `__init__.py#CAFF_OT_toggle_abrir_fechar` do anexo | (a) `frame_set` com keyframes; (b) driver | 🟢 |
| D-09 | Validação de chapa reusa `part_extractor.limit_status` (comparação do lado maior com o maior limite) | Mesma regra que o plano de corte já aplica; uma implementação só evita divergência entre aviso e corte | (a) reimplementar no núcleo; (b) validar só no corte | 🟢 |
| D-10 | Comprimento das chapas pela montagem reusa `cabinet_editor.structure.carcass_lengths` | Regra lateral/base passante já testada em `tests/test_cabinet_editor_structure.py` | (a) duplicar a conta no `armario_v2`; (b) tabela por montagem | 🟢 |
| D-11 | Contrato de chapas em `Scene.btm_armario_contrato`, semeado do Padrão de Dimensões ativo (`standards.api`), sobrescrevível por `apply_host_contract(...)` | RN-02 pede contrato injetável pelo hospedeiro; o padrão já tem chapa e espessuras por papel | (a) contrato só no armário; (b) arquivo JSON separado | 🟢 |
| D-12 | Corrediça 3D: `caffmob_draw/assets/slides/slide-st48-0200-0.obj` importado uma vez por armário e instanciado por gaveta; alternativa geométrica quando falta | RN-08; `build.py` empacota `caffmob_draw/` inteiro, então o asset viaja no ZIP | (a) geometria procedural sempre; (b) `Asset Library` externa | 🟢 |
| D-13 | Módulo de biblioteca (frameless, face frame, closets) abre o painel com o spec preenchido; `Gerar` cria o armário v2 e o módulo antigo é ocultado e marcado com `btm_cut_exclude` | RN-21 sem apagar o móvel (RN-23) e sem peça duplicada no corte (`part_sources._visible` e `geometry_records` já respeitam as duas marcas) | (a) converter o módulo no lugar; (b) excluir o módulo antigo; (c) deixar os dois visíveis e filtrar no corte | 🟡 |
| D-14 | Armário antigo (sem `btm_armario`) não é convertido: o painel mostra aviso e desabilita `Gerar`/`Aplicar` | RN-23 e precedente `015 RN-22` | (a) converter ao abrir; (b) editor antigo convivendo | 🟢 |
| D-15 | Testes: um puro por regra (`tests/test_017_*.py`) e uma fumaça `tests/blender_017_armario_smoke.py` | Padrão das features 004/006/008/015 | (a) só fumaça; (b) só puros | 🟢 |
| D-16 | `caffmob_draw/blender_manifest.toml` sobe de `1.25.0` para `1.26.0` | Feature nova em pacote versionado; `build.py` recusa empacotar sem os ativos | (a) manter a versão | 🟢 |
| D-17 | O corte deixa de ver módulo convertido filtrando na origem: `part_sources.iter_modules` ignora módulo oculto ou com `btm_cut_exclude` | O caminho sintético (`synthetic_records`) não consulta a marca e deduz peças de `btm_cabinet`, então ocultar só o módulo não basta; filtrar na origem vale também para `modules[]` do JSON v2. Decisão do titular em 2026-11-21 (fechamento do A001) | (a) filtrar em `extract_production_parts`; (b) deletar o módulo antigo da cena, contra RN-23 | 🟢 |
| D-18 | `BTM_PG_ArmarioV2` ganha as flags `lateral_esq_ativa`, `lateral_dir_ativa`, `base_inf_ativa` e `base_sup_ativa`, todas `False`; `fundo_ativo` continua sendo a presença do fundo | RN-01/RF-01 exigem construtor vazio e Montar Caixa ligando as peças; sem as flags o estado vazio não é representável e o HUD não tem alternador. Confirmado pelo titular em 2026-11-21 (fechamento do A003): presença por flag, não por enum, porque as quatro peças são independentes e o `snapshot` precisa restaurar qualquer combinação | (a) enum de montagem rápida, descartado como modelo de dados (pode voltar como atalho de interface que liga várias flags); (b) presença implícita em `espessura = 0`, descartada (confunde ausência com espessura inválida) | 🟢 |
| D-19 | Corrediça 3D em duas camadas: `armario_v2/corredica.py` (puro) calcula em milímetros as três partes do conjunto telescópico (trilho externo preso na lateral do vão, trilho interno preso na caixa da gaveta e as gaiolas a meio curso) e o `build` importa `caffmob_draw/assets/slides/slide-st48-0200-0.obj` uma vez por armário e instancia o conjunto por gaveta; sem o arquivo, as mesmas três partes saem do cálculo de `corredica.py`. As partes levam `papel` vazio, para continuarem fora do plano de chapa (`resumo.lista_de_pecas` e `conferencia.conferir` já tratam papel vazio como ferragem, e `part_sources.armario_v2_records` pula papel vazio), e um campo novo `ferragem` (`TRILHO_EXT`, `TRILHO_INT`, `GAIOLA`) em `BTM_PG_ArmarioParte`, que a animação passa a consultar no lugar de `PAPEIS_GAIOLA` | RN-08 e RF-10 são `Must` e a feature fechou sem a peça na cena (achado A012); `anim.PAPEIS_GAIOLA` existe desde a T022 e não tem peça para animar | (a) gravar `papel` `GAIOLA`/`TRILHO` em `btm_armario_parte` (entraria como chapa no corte, contra o RF-19); (b) só geometria procedural, sem o OBJ (perde o trilho real do anexo); (c) importar o OBJ por gaveta (custo em armário de 10 gavetas) | 🟢 |
| D-20 | A reabertura por arquivo ganha prova em fumaça própria: `tests/blender_017_reabrir_smoke.py` gera um armário com três vãos, quatro gavetas e folha deslizante, salva em `tempdir` com `save_as_mainfile`, reabre com `open_mainfile` e confere abas, medidas, `snapshot` e peças na cena. Nenhuma mudança de desenho: o `Object.btm_armario` de D-02 já é o mecanismo | RN-17 e RF-20 são `Must` e não tinham ação nem prova (achado A013); `PropertyGroup` que não sobrevive ao ciclo só aparece numa ida e volta por arquivo | (a) acrescentar a conferência ao `blender_017_armario_smoke.py` (mistura registro e persistência no mesmo roteiro); (b) conferência manual em janela (não regride) | 🟢 |
| D-21 | A inserção pela interface sai em operadores próprios no `ops.py`, um por peça, com geração no mesmo passo: `caffmob.armario_v2_inserir_divisoria` (eixo, variante e posição opcional), `..._inserir_matriz` (linhas e colunas de 1 a 5), `..._criar_bloco_gavetas` (quantidade, altura do bloco e modelo) e `..._inserir_interno` (tipo). Cada um lê o vão ativo das coleções do armário, chama o núcleo já testado (`vaos.inserir_vertical`, `vaos.inserir_horizontal`, `vaos.matriz`, `gavetas.bloco`, `internos.inserir`), regrava a coleção e, se o armário já foi gerado, chama `ops.gerar_armario` no mesmo `execute`. O vão ativo sai de `panel._vao_ativo` para `ops.vao_ativo`, e o painel delega | RF-07, RF-09 e RF-12 são `Must` e só existiam no núcleo; o painel editava o que já estava gravado e o Duplicar do menu não cria a primeira peça. Operador com `UNDO` dá um passo por clique, o mesmo contrato de Duplicar e Excluir (D-08, RN-18), e reusa funções com teste puro em vez de recalcular no painel | (a) inserir por `update` de propriedade (sem passo de desfazer e gerando a cada tecla); (b) um operador genérico com `EnumProperty` de peça (mais difícil de rotular e de testar); (c) deixar a inserção só no HUD | 🟢 |
| D-22 | Contra-frente e peça de trás passam a ser geradas com presença própria: `contra_frente_ativa` e `peca_tras_ativa` em `BTM_PG_ArmarioV2`, ambas `False`, e as duas peças em `build.pecas` como travessa de 90 mm entre as laterais, com `espessura = espessura_base_superior`, no topo interno: a contra-frente na face da frente e a peça de trás na face de trás. `EM_PE` deixa os 90 mm na altura e a espessura na profundidade; `DEITADA` troca os dois eixos, como o motor anexo (`__init__.py:558-568`) e o mockup (`renderPanel`, travessa de 100 mm no cutlist) | RF-05 é `Must` e o `spec` calculava as duas sem geometria; sem presença o usuário não liga nem desliga. A peça do mockup é uma travessa de 90 mm, não um painel da altura toda: `spec.contra_frente` e `peca_de_tras` passam a devolver `{'comprimento': largura_interna, 'altura': ALTURA_TRAVESSA, 'espessura': espessura_base_superior, 'em_pe': ...}`, e o `test_017_spec.py` acompanha | (a) gerar painel da altura total, que fecha a frente do armário; (b) manter o cálculo e não gerar, contra o RF-05 reescrito no clarify de 2026-11-23 | 🟡 |

## 4. Premissas

Nenhum marcador `[DÚVIDA]` restou no `requirements.md` (clarify de 2026-11-19). As premissas abaixo vêm das lacunas 🟡 da seção 10 do requirements e precisam ser validadas no `/reversa-coding`.

| Premissa | Origem (`requirements.md` seção) | Risco se errada |
|----------|----------------------------------|-----------------|
| Calceiro e sapateira a 480 mm do piso do vão e maleiro a 420 mm abaixo do topo; a faixa editável é `[0, altura do vão − espessura do interno]` | §3, §10 | Peça fora do vão em armário baixo; corrigir a faixa no núcleo, sem tocar nas abas |
| Quando dois internos disputam a mesma altura, vence o inserido por último e o outro sobe um passo mínimo de 50 mm | §10 | Sobreposição de internos no roupeiro; ajustar `internos.py` |
| Mapeamento dos módulos de biblioteca para o spec: medidas do módulo, espessuras do `btm_cabinet`/`btm_structure`, montagem de `assembly`, portas de `door_swing`, divisões de `scene_divisions` | §10 | Módulo importado chega com aba vazia; a ponte fica em `ponte.py`, sem tocar o editor antigo |
| A travessa de contra-frente e de trás tem 90 mm de altura de peça (`ALTURA_TRAVESSA`), e o RF-05 continua valendo como troca de eixo da travessa em pé ou deitada; `spec.contra_frente` e `peca_de_tras` mudam de painel da altura total para travessa (D-22) | §4 (RN-04) e §9 (clarify 2026-11-23) | Peça com altura errada no corte; corrigir a constante no núcleo, sem tocar nas abas |
| A inserção pela interface usa o vão da peça escolhida na coleção ativa e, sem escolha, o vão raiz `s0`; num armário sem divisórias é sempre o vão raiz | §9 (clarify 2026-11-23) | Peça inserida no vão errado; corrigir `ops.vao_ativo` |

## 5. Delta arquitetural

| Componente | Arquivo de origem no legado | Tipo de mudança | Resumo |
|------------|------------------------------|-----------------|--------|
| `armario_v2` (núcleo) | — (novo) | componente-novo | `spec`, `chapas`, `conferencia`, `gavetas`, `portas`, `internos`, `resumo` em milímetros, sem `bpy` |
| `armario_v2` (corrediça) | `novo_arm_building/.../__init__.py#attach_drawer_slide_3d` | componente-novo | `corredica.py` calcula em milímetros o trilho externo, o trilho interno e as gaiolas, e o `build` instancia o OBJ uma vez por armário ou o conjunto de reserva (D-19) |
| `armario_v2` (cena) | — (novo) | componente-novo | `props`, `build`, `panel`, `menu`, `ops`, `anim`, `hud`, `ponte`, `assets/slides` |
| `armario_v2` (inserção) | `caffmob_draw/armario_v2/ops.py` | componente-alterado | quatro operadores de inserção (`inserir_divisoria`, `inserir_matriz`, `criar_bloco_gavetas`, `inserir_interno`) e o `vao_ativo` que o painel passa a ler |
| `armario_v2` (painel) | `caffmob_draw/armario_v2/panel.py` | regra-alterada | botões de inserção no topo das abas Divisões, Gavetas e Internos, com a matriz na sub-aba Múltipla, e `_vao_ativo` delegando para `ops` |
| `armario_v2` (contra-frente) | `caffmob_draw/armario_v2/{spec,build}.py` | regra-alterada | duas flags de presença, travessa de 90 mm emitida em `pecas` e as duas medidas corrigidas no `spec` (D-22) |
| `cabinet_editor` | `caffmob_draw/cabinet_editor/__init__.py` | componente-extinto (parcial) | `_modules()` perde a UI (`window`, `ops_editor`, `ops_actions`, `panels*`) e mantém `gallery`; os núcleos continuam importáveis |
| `cabinet_editor.props` | `caffmob_draw/cabinet_editor/props.py` | contrato-removido | `WindowManager.btm_cabinet_editor` deixa de ser registrado junto com a UI |
| `part_sources` | `caffmob_draw/cutting/part_sources.py` | contrato-novo | `armario_v2_records(scene)` lê `btm_armario_parte` e devolve `PartRecord` com `source="ARMARIO_V2"`; `iter_modules` passa a ignorar módulo oculto ou com `btm_cut_exclude` (D-17) |
| `part_extractor` | `caffmob_draw/cutting/part_extractor.py#extract_production_parts` | regra-alterada | soma as peças do adaptador novo depois das gavetas |
| `collision/guard`, `stick/settle` | `caffmob_draw/collision/guard.py:44`, `caffmob_draw/stick/settle.py:21` | regra-alterada | sai `caffmob.cabinet_editor_modal` das listas de modais gerenciados |
| abridor e chamadas | `caffmob_draw/ui/sidebar_vocab.py:25`, `ui/object_properties.py:433`, `ui/context_menu.py:35`, `target/commands.py:68`, `library_panel/ops_cabinet.py:79` | contrato-mantido | Mesmo `bl_idname`, implementação nova |
| `caffmob_draw/__init__.py` | `caffmob_draw/__init__.py:355` e `:441` | regra-alterada | Registra `armario_v2` depois de `customize` (usa `standards`/`adapters`) e antes de `cutting` |
| i18n | `caffmob_draw/data/i18n.py`, `data/translations/*.json` | contrato-alterado | Chaves novas nas duas línguas, nos dois contextos |
| manifesto | `caffmob_draw/blender_manifest.toml` | regra-alterada | Versão `1.26.0` |

## 6. Delta no modelo de dados

Resumo: um PropertyGroup novo no armário (spec completo + estado + snapshot), um por peça (papel, medidas de corte, material, veio, fitas, alvo de animação) e um na cena (contrato de chapas). Os PropertyGroups do editor antigo deixam de existir; nada é migrado.

Detalhe completo em: `_reversa_forward/017-construtor-armario-v2/data-delta.md`

O clarify de 2026-11-23 acrescenta duas flags de presença no armário (`contra_frente_ativa`, `peca_tras_ativa`) e nenhuma estrutura nova: a inserção grava nas coleções que já existem (`divisoes`, `gavetas`, `internos`).

## 7. Delta de contratos externos

A feature não cria nem altera contrato externo: não há HTTP, fila, gRPC, GraphQL ou formato de arquivo exportado novo. O JSON v2 do corte continua o mesmo (`cutting/json_exporter.py`), apenas passa a receber mais peças. Por isso não há `interfaces/`.

| Contrato | Tipo | Arquivo de detalhe |
|----------|------|--------------------|
| — (nenhum alterado) | — | — |

## 8. Plano de migração

1. **Nenhuma conversão de dados.** Arquivo salvo com módulos antigos abre igual: as peças continuam na cena e no corte, o painel avisa que a edição exige recriar (RN-23, RF-26).
2. **Módulos de biblioteca.** Quem inserir um módulo frameless/face frame/closets cai no painel novo com o spec preenchido; `Gerar` oculta o módulo antigo e o marca com `btm_cut_exclude`, reversível em `Recriar do módulo` (D-13).
3. **Blocos órfãos.** `WindowManager.btm_cabinet_editor` deixa de ser registrado; um arquivo salvo com esse bloco o perde sem erro na próxima gravação.
4. **Rollback.** Reinstalar `1.25.0` devolve o editor antigo; nenhum dado é convertido em disco, então o móvel antigo volta a ser editável.

## 9. Riscos e mitigações

| Risco | Impacto | Probabilidade | Mitigação |
|-------|---------|---------------|-----------|
| Móvel antigo perde a edição (RF-26) e o projetista não entende por quê | alto | média | Aviso no cabeçalho do painel, em português e inglês, dizendo o que fazer; `legacy-impact.md` no `/reversa-coding` |
| Módulo de biblioteca convertido gera peça duplicada no plano de corte | alto | média | Ocultar o módulo, marcar `btm_cut_exclude` e filtrar em `iter_modules` — o caminho sintético não consulta a marca (`part_sources.py:87` e `:221`), então a marca sozinha não protege; teste de contagem antes e depois de `Gerar` (D-17, T035) |
| Timer de abrir/fechar pendurado depois de desregistrar ou de trocar de armário | médio | média | Handle em dicionário de módulo, removido em `unregister`, em `Esc` e ao apagar a coleção |
| Importar o OBJ por gaveta estoura o tempo em armário com 10 gavetas | médio | média | Importar uma vez por armário e duplicar o conjunto (T037); a fumaça conta as instâncias por gaveta e as três marcas de `ferragem` (T039) |
| A corrediça entra no plano de chapa como se fosse MDF | alto | baixa | `papel` vazio e `ferragem` preenchido (D-19); `resumo`, `conferencia` e `part_sources.armario_v2_records` já descartam papel vazio, e `tests/test_017_corredica.py` mais `tests/test_017_corte.py` fecham a contagem (T038, T039) |
| Sem Padrão de Dimensões ativo, o contrato nasce vazio | médio | baixa | Semear pelo `dimension_schema` BR, mesma fallback de `part_extractor._schema_values` |
| Catálogo de i18n incompleto quebra `tests/test_i18n_coverage.py` | médio | alta | Chaves no mesmo commit do texto; o teste roda antes da fumaça |
| `cabinet_editor` sem UI quebra um chamador esquecido | alto | baixa | `code_search` por `btm_cabinet_editor` e `cabinet_editor_modal` antes de remover; `check_api.py` e a fumaça 008 no aceite |
| Inserir pelo painel regenerar o armário inteiro a cada clique | médio | média | `gerar_armario` só roda quando o armário já foi gerado e o NFR de 0,5 s cobre 4 vãos, 20 divisões e 10 gavetas; medir na fumaça e, se passar, segurar a geração no Aplicar |
| Vão inválido ou peça que não cabe deixar coleção pela metade | alto | média | O núcleo levanta `ValueError` antes de qualquer escrita; o operador captura, reporta aviso e só regrava a coleção depois do sucesso |
| Mudar a travessa para 90 mm quebrar o contrato do `spec` fechado em T012 | médio | alta | A mudança é decisão D-22 com premissa registrada no §4; `test_017_spec.py` muda no mesmo passo e o `resumo`/corte passam a listar 90 mm |

## 10. Critério de pronto

- [x] T036 a T040 concluídas (corrediça 3D e reabertura por arquivo, achados A012 e A013)
- [x] Inserção pela interface nas três abas, com um passo de desfazer por clique (RF-07, RF-09, RF-12, D-21; T046 a T051)
- [x] Contra-frente e peça de trás na cena com presença, nas duas orientações, e presentes no corte com 90 mm (RF-05, D-22; T041 a T044)
- [x] `regression-watch.md` gerado
- [x] `ruff check` nos caminhos da feature (decisão 1 da T034), limpo em `caffmob_draw/armario_v2/`, `tests/blender_017_armario_smoke.py` e `tests/test_017_*.py`; os 21 erros do pacote inteiro ficam como dívida separada, fora do portão desta feature
- [x] `python3 docs/rag/tools/check_api.py` sem `[UNKNOWN in 5.2]` (599 arquivos, T034)
- [x] `tests/blender_017_armario_smoke.py` verde com 48 conferências, e as demais fumaças resolvidas: 004 colisão e 004 assentar verdes, 015 reescrita enxuta verde, 006 e 008 aposentadas em `tests/retired/` (T034)
- [x] `tests/test_i18n_coverage.py` verde com as chaves novas (`armario_v2.json` com 136 entradas, T032)
- [x] Plano de corte de um armário v2 com gavetas lista as peças com papel e sem a corrediça (T029, T035 e `tests/test_017_corte.py`)
- [x] A corrediça aparece na cena em cada gaveta, com o OBJ e com o conjunto de reserva, e continua fora do plano de chapa (RN-08, T037 e T039)
- [x] Salvar, fechar, reabrir o arquivo e abrir o construtor devolve o mesmo armário, com as peças na cena (RN-17, T040)
- [ ] Re-extração reversa executada e sem regressão vermelha (recomendado, não obrigatório)

## 11. Histórico de alterações

| Data | Alteração | Autor |
|------|-----------|-------|
| 2026-11-19 | Versão inicial gerada por `/reversa-plan` a partir do requirements da 017 já esclarecido | reversa |
| 2026-11-21 | Fechamento do cross-check A001–A003: D-04 mantém `gallery`, D-17 (filtro em `iter_modules`) e D-18 (flags de presença) acrescentados, risco de duplicação no §9 corrigido | reversa |
| 2026-11-23 | Segunda auditoria (A012 e A013): D-19 (corrediça 3D em `corredica.py` mais o OBJ no `build`) e D-20 (fumaça de reabertura por arquivo) acrescentados, componente `armario_v2` (corrediça) no §5, dois riscos no §9 e critério de pronto do §10 refletindo o estado real | reversa |
| 2026-11-23 | Clarify da auditoria de mockup e frente: D-21 (inserção por operadores com geração no mesmo passo) e D-22 (contra-frente e peça de trás geradas como travessa de 90 mm com presença), §4 com duas premissas, §5 com três componentes e §9 com três riscos | reversa |
