# Roadmap: Construtor de armário v2 no CAFFMob Draw

> Identificador: `017-construtor-armario-v2`
> Data: `2026-11-19`
> Requirements: `_reversa_forward/017-construtor-armario-v2/requirements.md`
> Especificação que prevalece: `novo_arm_building/CAFF_MOB_Construtor_Armarios_Blender_5_2/caff_construtor_armarios_blender_5_2/`
> Escopo (clarify 2026-11-19): todos os armários, inclusive módulos de biblioteca; superfície na vista 3D; móveis antigos preservados
> Confidência: 🟢 CONFIRMADO, 🟡 INFERIDO, 🔴 LACUNA

## 1. Resumo da abordagem

O motor anexado passa a ser o construtor do pacote, num pacote novo `caffmob_draw/armario_v2/` com núcleo puro e camada Blender separados. O núcleo (`spec`, `chapas`, `conferencia`, `gavetas`, `portas`, `internos`) calcula todas as peças em milímetros sem `bpy`; a camada Blender (`props`, `build`, `panel`, `menu`, `ops`, `anim`, `hud`) grava o contrato no armário, cria malhas, desenha o painel da vista 3D e anima abrir/fechar.

O `cabinet_editor` não é apagado: perde o registro da interface (janela, modal, painéis, galeria) e continua registrando os dados que o resto do pacote usa (`data_props`, `previews`, `reflow_handler`). Seus núcleos puros — `structure`, `structures_core`, `divisions`, `structure_inputs` — continuam servindo `geometry/mesh_gen.py`, `customize/adapters`, `standards` e `cutting`.

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
| D-04 | `cabinet_editor.register()` fica só com dados: `data_props`, `previews`, `reflow_handler`; a UI sai do registro | `data_props` registra os PropertyGroups que os módulos antigos usam; `mesh_gen`, `customize`, `standards` e `cutting` importam os núcleos puros sem depender do registro | (a) apagar `cabinet_editor` inteiro (quebra `mesh_gen` e o corte); (b) deixar a UI registrada e só escondê-la | 🟢 |
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

## 4. Premissas

Nenhum marcador `[DÚVIDA]` restou no `requirements.md` (clarify de 2026-11-19). As premissas abaixo vêm das lacunas 🟡 da seção 10 do requirements e precisam ser validadas no `/reversa-coding`.

| Premissa | Origem (`requirements.md` seção) | Risco se errada |
|----------|----------------------------------|-----------------|
| Calceiro e sapateira a 480 mm do piso do vão e maleiro a 420 mm abaixo do topo; a faixa editável é `[0, altura do vão − espessura do interno]` | §3, §10 | Peça fora do vão em armário baixo; corrigir a faixa no núcleo, sem tocar nas abas |
| Quando dois internos disputam a mesma altura, vence o inserido por último e o outro sobe um passo mínimo de 50 mm | §10 | Sobreposição de internos no roupeiro; ajustar `internos.py` |
| Mapeamento dos módulos de biblioteca para o spec: medidas do módulo, espessuras do `btm_cabinet`/`btm_structure`, montagem de `assembly`, portas de `door_swing`, divisões de `scene_divisions` | §10 | Módulo importado chega com aba vazia; a ponte fica em `ponte.py`, sem tocar o editor antigo |

## 5. Delta arquitetural

| Componente | Arquivo de origem no legado | Tipo de mudança | Resumo |
|------------|------------------------------|-----------------|--------|
| `armario_v2` (núcleo) | — (novo) | componente-novo | `spec`, `chapas`, `conferencia`, `gavetas`, `portas`, `internos`, `resumo` em milímetros, sem `bpy` |
| `armario_v2` (cena) | — (novo) | componente-novo | `props`, `build`, `panel`, `menu`, `ops`, `anim`, `hud`, `ponte`, `assets/slides` |
| `cabinet_editor` | `caffmob_draw/cabinet_editor/__init__.py` | componente-extinto (parcial) | `_modules()` perde a UI (`window`, `ops_editor`, `ops_actions`, `panels*`, `gallery`); os núcleos continuam importáveis |
| `cabinet_editor.props` | `caffmob_draw/cabinet_editor/props.py` | contrato-removido | `WindowManager.btm_cabinet_editor` deixa de ser registrado junto com a UI |
| `part_sources` | `caffmob_draw/cutting/part_sources.py` | contrato-novo | `armario_v2_records(scene)` lê `btm_armario_parte` e devolve `PartRecord` com `source="ARMARIO_V2"` |
| `part_extractor` | `caffmob_draw/cutting/part_extractor.py#extract_production_parts` | regra-alterada | soma as peças do adaptador novo depois das gavetas |
| `collision/guard`, `stick/settle` | `caffmob_draw/collision/guard.py:44`, `caffmob_draw/stick/settle.py:21` | regra-alterada | sai `caffmob.cabinet_editor_modal` das listas de modais gerenciados |
| abridor e chamadas | `caffmob_draw/ui/sidebar_vocab.py:25`, `ui/object_properties.py:433`, `ui/context_menu.py:35`, `target/commands.py:68`, `library_panel/ops_cabinet.py:79` | contrato-mantido | Mesmo `bl_idname`, implementação nova |
| `caffmob_draw/__init__.py` | `caffmob_draw/__init__.py:355` e `:441` | regra-alterada | Registra `armario_v2` depois de `customize` (usa `standards`/`adapters`) e antes de `cutting` |
| i18n | `caffmob_draw/data/i18n.py`, `data/translations/*.json` | contrato-alterado | Chaves novas nas duas línguas, nos dois contextos |
| manifesto | `caffmob_draw/blender_manifest.toml` | regra-alterada | Versão `1.26.0` |

## 6. Delta no modelo de dados

Resumo: um PropertyGroup novo no armário (spec completo + estado + snapshot), um por peça (papel, medidas de corte, material, veio, fitas, alvo de animação) e um na cena (contrato de chapas). Os PropertyGroups do editor antigo deixam de existir; nada é migrado.

Detalhe completo em: `_reversa_forward/017-construtor-armario-v2/data-delta.md`

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
| Módulo de biblioteca convertido gera peça duplicada no plano de corte | alto | média | Ocultar o módulo e marcar `btm_cut_exclude`; teste de contagem de peças antes e depois de `Gerar` |
| Timer de abrir/fechar pendurado depois de desregistrar ou de trocar de armário | médio | média | Handle em dicionário de módulo, removido em `unregister`, em `Esc` e ao apagar a coleção |
| Importar o OBJ por gaveta estoura o tempo em armário com 10 gavetas | médio | média | Importar uma vez por armário e duplicar o conjunto; medir com `tests/blender_017_armario_smoke.py` |
| Sem Padrão de Dimensões ativo, o contrato nasce vazio | médio | baixa | Semear pelo `dimension_schema` BR, mesma fallback de `part_extractor._schema_values` |
| Catálogo de i18n incompleto quebra `tests/test_i18n_coverage.py` | médio | alta | Chaves no mesmo commit do texto; o teste roda antes da fumaça |
| `cabinet_editor` sem UI quebra um chamador esquecido | alto | baixa | `code_search` por `btm_cabinet_editor` e `cabinet_editor_modal` antes de remover; `check_api.py` e a fumaça 008 no aceite |

## 10. Critério de pronto

- [ ] Todas as ações do `actions.md` marcadas `[X]`
- [ ] `cross-check.md` (se executado) sem CRITICAL nem HIGH
- [ ] `regression-watch.md` gerado
- [ ] `ruff check caffmob_draw/` limpo
- [ ] `python3 docs/rag/tools/check_api.py` sem `[UNKNOWN in 5.2]`
- [ ] `tests/blender_017_armario_smoke.py` verde e as fumaças 004, 006, 008 e 015 sem regressão
- [ ] `tests/test_i18n_coverage.py` verde com as chaves novas
- [ ] Plano de corte de um armário v2 com gavetas lista as peças com papel e sem a corrediça
- [ ] Re-extração reversa executada e sem regressão vermelha (recomendado, não obrigatório)

## 11. Histórico de alterações

| Data | Alteração | Autor |
|------|-----------|-------|
| 2026-11-19 | Versão inicial gerada por `/reversa-plan` a partir do requirements da 017 já esclarecido | reversa |
