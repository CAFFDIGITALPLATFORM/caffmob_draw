# Padrão de Dimensões (standards) — Requisitos

🟢 **CONFIRMADO** — contrato extraído em 2026-10-10 de `caffmob_draw/standards/` (11 arquivos, sem alterações sem commit na pasta) e dos arquivos que a unit possui fora dela segundo `.reversa/context/modules.json`: `caffmob_draw/data/dimension_schema.py` (esquema), `caffmob_draw/operators/ops_standards.py` (13 operadores) e `caffmob_draw/ui/standards_tree.py` (UIList). Confirmação de código não implica validação no Blender. 🟡 identifica inferência (prioridade, intenção); 🔴 identifica lacuna que depende de validação humana ou de execução no Blender.

## Visão Geral

🟢 A unit é a fonte única das medidas de fábrica dos móveis: medidas externas por linha de produto, material/espessura/limite de chapa/fitas por componente e medidas máximas globais, em definições nomeadas e versionadas guardadas na cena principal do projeto. Oferece o Configurador de Dimensões (rascunho com árvore, busca, validação e lista de pendências), propaga a definição aos módulos CAFFMob por duas perguntas ao usuário, mantém compatibilidade com as bibliotecas herdadas (frameless/closets), migra projetos antigos e troca definições com arquivos `.btmdim.json` e `DIMENSIONEXPORT` do Promob. Fontes: `standards/__init__.py`, `api.py`, `sync.py`, `operators/ops_standards.py`.

## Responsabilidades

- 🟢 Declarar o domínio configurável (870 parâmetros: 5 globais + 5 linhas × 13 externas + 5 linhas × 20 componentes × 8 campos), com padrões BR/US, faixa, unidade, imagem, códigos Promob e destinos legados (`data/dimension_schema.py`).
- 🟢 Persistir definições na cena principal (`Scene.btm_standards`) e garantir as embutidas "Padrão Brasil" e "Padrão EUA (HB5)" somente leitura (`model.py`, `builtin.py`, `api.py:ensure_ready`).
- 🟢 Ler/gravar valores por chave com validação "Valor Inválido" e gestão de definições: ativa, duplicar, renomear, excluir (`api.py`).
- 🟢 Manter o rascunho do Configurador no `WindowManager` (árvore achatada, busca, edição na unidade do usuário, pendências) e gravá-lo na definição com incremento de versão (`api.py:begin_draft/apply_draft`).
- 🟢 Calcular as medidas de um armário CAFFMob novo pela definição ativa (`cabinet_defaults.py:defaults`), consumido por `operators/cabinet_builder.py`, `library_panel/ops_cabinet.py` e `legacy/convert.py`.
- 🟢 Classificar os módulos da cena em segue/difere/não aplicável e aplicar a definição aos escolhidos (`apply_core.py`, `sync.py`, `ops_standards.py:BTM_OT_StandardsApplyScene/ApplyDiffer`).
- 🟢 Sincronizar propriedades de cena das bibliotecas herdadas e, só no modo de suporte (`legacy/gate.legacy_ui`), os gabinetes herdados, preservando medidas editadas à mão (`sync.py`).
- 🟢 Migrar arquivos em `load_post` (M-01, M-02, M-03) e na abertura sem arquivo (`migration.py`).
- 🟢 Importar/exportar `.btmdim.json` e `DIMENSIONEXPORT` com escrita atômica (`io_json.py`, `io_promob.py`).
- 🟢 Carregar imagens de referência do Configurador sob demanda (`previews.py`).
- 🟢 Fora da responsabilidade: a geometria do armário (`data/properties.update_cabinet_geom`, ver `_reversa_sdd/cabinet_editor/`), a classificação de objetos (`_reversa_sdd/selection/`), o gate legado e a conversão (`legacy/`), a lista de corte (`_reversa_sdd/cutting/`; os testes `test_cabinet_hardware` pertencem a cutting).

## Regras de Negócio

| ID | Regra confirmada | Fonte |
|---|---|---|
| RN-01 | 🟢 Comprimentos do esquema e das definições ficam em **mm**; propriedades do Blender recebem metros por `valor / 1000`. Material é texto (ENUM). | `dimension_schema.py` (docstring); `api.py:get_value_m`; `sync.py:write_legacy_targets`; `cabinet_defaults.py:defaults.meters` |
| RN-02 | 🟢 Chave de parâmetro: `GLOBAL.max.<campo>`, `<LINHA>.external.<campo>` ou `<LINHA>.sheets.<COMPONENTE>.<campo>`; linhas COZ, DOR, BAN, SAL, ESC; campos de chapa `material, max_width, max_length, thickness, edge_1..edge_4`. O mesmo prefixo `sheets` vale para componentes da árvore "Componentes" (SAR, ROD, MOL). | `dimension_schema.py:max_key/external_key/sheet_key/_build` |
| RN-03 | 🟢 Padrões por mercado: BR caixa/tampo 15 mm, frente 18, fundo 6, fita 0,4 mm só nos lados `visible_sides_br`; US 19,05 / 19,05 / 6,35 mm e fita 0. Dormitórios sobrescrevem `tall_height`, `tall_depth`, `base_height`, `toe_kick_height`, `toe_kick_setback`. Padrões US são arredondados a 4 casas. | `dimension_schema.py:_THICKNESS/_EXTERNAL_OVERRIDES/_build` |
| RN-04 | 🟢 Validação: ENUM exige pertencer a `enum_items` (sensível a maiúsculas); FLOAT exige `float(value)` possível, não negativo (salvo `negative_allowed`, nunca verdadeiro hoje) e `min ≤ v ≤ max` inclusivo. Mensagem começa por "Valor Inválido:" e o rótulo; faixa, unidade (vírgula decimal) e valor recebido só aparecem na mensagem de fora da faixa (não numérico traz só o valor recebido; negativo, nenhum dos dois) _(Revisão 2026-10-10: executado `validate` com 999, −1, "abc"; dimension_schema.py:validate)_. NaN passa (sem `isfinite`). | `dimension_schema.py:validate/_fmt` |
| RN-05 | 🟢 As definições vivem na cena principal (`hb_project.get_main_scene()`; qualquer exceção ou ausência usa a cena recebida). | `api.py:main_scene/standards` |
| RN-06 | 🟢 Embutidas `builtin-br` ("Padrão Brasil", BR) e `builtin-us` ("Padrão EUA (HB5)", US) são criadas se faltarem e completadas com chaves ausentes (nunca sobrescreve valores existentes). São somente leitura em `set_value`/`apply_draft` e não podem ser excluídas. | `builtin.py:ensure_builtins/fill_from_schema`; `api.py:set_value/remove_definition/apply_draft` |
| RN-07 | 🟢 `ensure_ready` zera `active_index` se ≥ quantidade de definições; `active_definition` limita o índice ao último item e devolve None com coleção vazia. Sem definição, `active_assembly` = `'LATERAL'` e `get_value` = padrão BR do esquema. | `api.py:ensure_ready/active_definition/active_assembly/get_value` |
| RN-08 | 🟢 Duplicar cria UID `uuid4().hex`, nome `"<nome> - cópia"` (ou o dado) tornado único com sufixo ` (n)` a partir de 2, origem USER, versão 1, mercado, montagem, valores e atributos crus copiados, e ativa a cópia. | `api.py:duplicate_definition/unique_name/copy_values` |
| RN-09 | 🟢 Valor ausente na definição vale o padrão do mercado da definição; chave fora do esquema levanta `StandardsError`. `definition_values` devolve todas as 870 chaves mais quaisquer itens extras da coleção. | `api.py:get_definition_value/definition_values` |
| RN-10 | 🟢 `set_values` valida todos os pares antes de gravar o primeiro (sem aplicação parcial por erro de domínio). | `api.py:set_values` |
| RN-11 | 🟢 O rascunho copia a definição ativa (montagem inclusive) e completa chaves ausentes; pendências comparam montagem e cada valor (ENUM por igualdade, FLOAT com tolerância 1e-6 mm). Aplicar exige definição existente e não embutida, renomeia com nome único se o nome mudou, copia o rascunho e só incrementa `version` e `updated_at` se houver pendências. | `api.py:begin_draft/pending_changes/apply_draft` |
| RN-12 | 🟢 Mudar o padrão global (Configurador, Aplicar, Definir ativa) **não** altera módulos CAFFMob: a sincronização roda com `modules=[]` e depois duas perguntas decidem. Sem janela (background/script) as perguntas não abrem. | `ops_standards.py:ask_apply/BTM_OT_StandardsConfigurator.execute/BTM_OT_StandardsSetActive.execute` |
| RN-13 | 🟢 Classificação: módulo não CAFFMob → não aplicável (LEGACY também em `legacy`); CAFFMob com padrão próprio ou com `btm_standard_uid` não vazio diferente do global anterior → difere; demais → segue. Padrão próprio = overrides manuais, montagem diferente da do padrão de origem ou espessura por papel > 0. | `apply_core.py:plan/is_own`; `cabinet_editor/bridge.py:is_own_standard` |
| RN-14 | 🟢 1ª pergunta Sim aplica "segue"; havendo "difere", abre a 2ª pergunta (interativo) ou aplica-os se `apply_differ=True` (EXEC). Cancelar a 1ª não muda módulos; cancelar a 2ª não desfaz a 1ª. | `ops_standards.py:BTM_OT_StandardsApplyScene/ApplyDiffer` |
| RN-15 | 🟢 Aplicar a um módulo CAFFMob: altura/profundidade do tipo e espessuras da linha do módulo, montagem da definição; **largura e posição não mudam**; espessuras explícitas da estrutura zeradas, overrides apagados, `btm_standard_uid` e `btm_line` gravados, geometria refeita uma vez. | `sync.py:apply_to_module` |
| RN-16 | 🟢 Toda sincronização grava os 17 destinos legados (`Scene.hb_frameless`/`hb_closets`, metros, cena principal e cena atual se diferente), marca `btm_line` ausente em gaiolas herdadas (frameless COZ, closet DOR), e marca `btm_settings.cut_plan_stale = True` — inclusive com `modules=[]`. | `sync.py:_apply_definition/write_legacy_targets/_tag_lines` |
| RN-17 | 🟢 Gabinetes herdados só são atualizados com o modo de suporte ligado; medidas marcadas em `btm_overrides` são puladas salvo `include_manual`. | `sync.py:_apply_definition/make_skip/_update_closets` |
| RN-18 | 🟢 Medidas de armário novo: tipo fora de BASE/WALL/TALL vira BASE; sem valores ou linha ausente usa `FALLBACK` com aviso; largura sempre de `FALLBACK` (0,8/0,8/0,6 m); Z só para WALL (`install_height_upper`); espessura por papel via `ROLE_COMPONENT` (TOP/BOTTOM→BAS, LEFT/RIGHT→LAT, BACK→FUN_INF em todos os tipos); `carcass` = espessura LEFT. | `cabinet_defaults.py`; `cabinet_editor/structure.py:ROLE_COMPONENT` |
| RN-19 | 🟢 Medida manual: nome gravado em `btm_overrides` (lista JSON ordenada) na raiz do módulo; escritas durante a sincronização (`is_syncing()`) não viram override nos consumidores closets. | `sync.py:add_override/is_syncing`; `product_libraries/closets/props_closets.py:_starter_prop_updater` |
| RN-20 | 🟢 `.btmdim.json`: `schema` = `caffmob_draw.dimension-standard` (lê também `blendertomob.dimension-standard`), `schema_version` int ≤ 1, `unit` = `mm`; qualquer valor fora do domínio aborta a importação; desconhecidos viram aviso. Importar cria definição nova USER (UID novo, não ativa); conflito de nome renomeia. **Montagem não é serializada.** | `io_json.py` |
| RN-21 | 🟢 `DIMENSIONEXPORT`: raiz obrigatória, ≥ 1 `ATTRIBUTE` com `ID`; todos os atributos preservados na ordem como crus; ID repetido usa o último valor; número aceita vírgula; valor inválido fica cru sem chave; `CAFF_MONTAGEM` define a montagem (LATERAL/BASE, outro → LATERAL com aviso). Importação é mercado BR, origem PROMOB_IMPORT, não ativa. | `io_promob.py:read_dimensionexport/to_definition_data`; `ops_standards.py:BTM_OT_StandardsImportPromob` |
| RN-22 | 🟢 Exportação Promob reescreve os pares crus na ordem; numérico igual (< 1e-6) mantém o texto original, senão 4 casas sem zeros finais e vírgula; sem crus, sintetiza um atributo por código Promob conhecido; `CAFF_MONTAGEM` sempre no fim. | `io_promob.py:build_attributes/_format_number/write_dimensionexport/attributes_from_values` |
| RN-23 | 🟢 Escrita de arquivo é atômica: temporário `.tmp` na pasta de destino + `os.replace`; temporário apagado em qualquer falha. JSON UTF-8 sem BOM, `indent=2`, `ensure_ascii=False`, `\n` final. | `io_json.py:write_document`; `io_promob.py:write_dimensionexport` |
| RN-24 | 🟢 Migração: M-01/M-02 uma vez por arquivo (marca `btm_standards_migrated` na cena principal); M-02 ativa US se houver gaiola frameless/closet, senão BR; M-01 cria "Migrada" (MIGRATED, ativa) com valores explicitamente setados nos grupos obsoletos; M-03 grava o UID ativo em toda raiz de módulo sem `btm_standard_uid` a cada execução. | `migration.py` |
| RN-25 | 🟢 Imagem de referência ausente devolve `icon_id` 0 e é avisada no console uma vez por chave. | `previews.py:icon_id` |

## Requisitos Funcionais

🟡 Prioridades inferidas por número de consumidores, posição na cadeia e testes; não constituem roadmap aprovado.

| ID | Requisito | Prioridade | Critério de aceite |
|---|---|---|---|
| RF-01 | 🟢 Esquema declarativo com consulta, filtro, validação e índice Promob | Must | CA-01, CA-02; `test_dimension_schema` |
| RF-02 | 🟢 Modelo persistente, embutidas e definição ativa | Must | CA-03, CA-04 |
| RF-03 | 🟢 Leitura/escrita de valores e gestão (duplicar, renomear, excluir) | Must | CA-05, CA-06 |
| RF-04 | 🟢 Configurador: rascunho, árvore, busca, edição, pendências e aplicar | Must | CA-07, CA-08, CA-09 |
| RF-05 | 🟢 Medidas de armário novo pela definição ativa | Must | CA-10, CA-11; `test_cabinet_defaults` |
| RF-06 | 🟢 Duas perguntas e aplicação seletiva a módulos CAFFMob | Must | CA-12, CA-13, CA-14; `test_standards_apply_core` |
| RF-07 | 🟢 Sincronização das propriedades/gabinetes herdados com preservação de medidas manuais | Should | CA-15 |
| RF-08 | 🟢 Importar/exportar `.btmdim.json` | Should | CA-16, CA-17 |
| RF-09 | 🟢 Importar/exportar `DIMENSIONEXPORT` com reexportação sem perda | Should | CA-18, CA-19; `test_promob_io`, `test_promob_assembly` |
| RF-10 | 🟢 Migração M-01/M-02/M-03 | Should | CA-20, CA-21 |
| RF-11 | 🟢 Relatório da última aplicação/importação | Could | CA-22 |
| RF-12 | 🟢 Imagens de referência do Configurador | Could | CA-23 |

## Requisitos Não Funcionais

| Tipo | Requisito observado | Evidência | Confiança |
|---|---|---|---|
| Integridade de arquivo | Escrita atômica com limpeza do temporário | `io_json.py:write_document`; `io_promob.py:write_dimensionexport` | 🟢 |
| Separação do cálculo | Esquema, `apply_core`, `cabinet_defaults`, `io_promob` e a parte de documento de `io_json` executam sem `bpy` (testes puros) | `tests/test_dimension_schema.py`, `test_standards_apply_core.py`, `test_cabinet_defaults.py`, `test_promob_io.py` | 🟢 |
| Estabilidade de RNA | Após `CollectionProperty.add()`, referências são buscadas de novo (realocação) | `api.py:duplicate_definition`; `builtin.py:ensure_builtins` | 🟢 |
| Vida das strings de enum | Itens de `EnumProperty` dinâmico mantidos em cache de módulo | `api.py:_ENUM_ITEMS_CACHE`; `ops_standards.py:_definition_items.cache` | 🟢 |
| Ciclo de vida | `unregister` desfaz `register` (classes, ponteiros, coleção de previews, timer) | `standards/__init__.py`; `model.py`; `previews.py`; `migration.py` | 🟢 |
| Desfazer | Operadores que alteram dados têm `{'REGISTER', 'UNDO'}`; exportações só `REGISTER`; relatório `INTERNAL` | `ops_standards.py` | 🟢 |

## Critérios de Aceitação

🟢 Derivados do código e dos testes. CA-12 a CA-15, CA-20 e CA-22/23 dependem do Blender e não foram executados nesta extração. _(Revisão 2026-10-10: `blender_012_apply_smoke.py` executado no Blender 5.2.0 em `--background`, código 0, 10 OK: plano 4 seguem/1 difere, OBJ e frameless não aplicáveis, "Não" não muda nada, Sim+Não muda os 4, Sim+Sim os 5, BAN recebe chapas de BAN, M-03 grava a origem; cobre CA-12 pelo caminho EXEC e a parte M-03 de CA-20)_

```gherkin
CA-01 — Esquema completo
Dado o módulo dimension_schema importado sem bpy
Quando conto PARAMS, COMPONENTS e PROMOB_INDEX
Então obtenho 870 parâmetros, 20 componentes, 1042 códigos Promob e 17 parâmetros com legacy_targets

CA-02 — Valor inválido
Dado o parâmetro COZ.sheets.LAT.thickness (3 a 60 mm)
Quando valido 999, -1, "abc" ou o material "mdf"
Então recebo (False, "Valor Inválido: …") com o rótulo; só 999 traz a faixa "3 e 60 mm" e "recebido: 999 mm"; −1 traz "não aceita valor negativo."; "abc" traz "precisa ser numérico (recebido: abc)."; "mdf" lista os materiais; 18 é aceito _(Revisão 2026-10-10: executado em Python puro)_

CA-03 — Projeto novo
Dado uma cena principal sem definições e sem gaiolas herdadas
Quando migration.run é executado
Então existem "Padrão Brasil" (índice 0) e "Padrão EUA (HB5)" (índice 1), a ativa é a BR e a cena recebe btm_standards_migrated = 1

CA-04 — Embutida protegida
Dado a definição ativa "Padrão Brasil"
Quando chamo set_value, apply_draft ou remove_definition sobre ela
Então StandardsError é levantado e nada muda; Rename e Delete têm poll falso

CA-05 — Duplicar
Dado "Padrão Brasil" e já existindo "Padrão Brasil - cópia"
Quando duplico a embutida
Então nasce "Padrão Brasil - cópia (2)", USER, versão 1, com os mesmos valores e montagem, e ela passa a ser a ativa

CA-06 — Gravação em lote inválida
Dado uma definição USER e o lote {espessura válida, largura máxima fora da faixa}
Quando chamo set_values
Então StandardsError lista o erro e nenhum dos dois valores é gravado

CA-07 — Editar no Configurador
Dado o Configurador aberto numa definição USER, unidade da cena em cm
Quando seleciono a espessura da lateral e digito "1,8"
Então o rascunho guarda 18.0 mm, draft.error fica vazio e a pendência mostra antes → depois

CA-08 — Medida fora da faixa no Configurador
Dado o mesmo parâmetro selecionado
Quando digito "99 cm"
Então draft.error recebe a mensagem "Valor Inválido" e o rascunho mantém o último valor válido

CA-09 — Aplicar rascunho
Dado um rascunho com 2 valores alterados e montagem trocada para BASE
Quando apply_draft(scene, draft, modules=[]) é executado
Então a definição recebe os valores e a montagem, version += 1, updated_at muda e report['changes'] tem 3 itens; sem alterações a versão fica igual

CA-10 — Medidas do armário pelo padrão
Dado os valores do fixture ME MOVEIS e linha COZ
Quando chamo defaults(values, 'COZ', 'WALL')
Então height/depth/z = upper_mid_height/upper_depth/install_height_upper em metros e warning é None

CA-11 — Sem padrão
Dado values None ou linha 'XYZ'
Quando chamo defaults
Então recebo FALLBACK do tipo, espessuras 0,018 (fundo 0,006) e um aviso traduzido

CA-12 — Duas perguntas (Sim, Sim)
Dado módulos CAFFMob A (uid anterior), B (sem uid), C (padrão próprio) e um frameless herdado
Quando defino outra definição ativa e respondo Sim às duas perguntas
Então A e B são atualizados na 1ª, C na 2ª, o herdado é contado como não aplicável e sugere conversão

CA-13 — Primeira pergunta cancelada
Dado o mesmo cenário
Quando cancelo a 1ª pergunta
Então nenhum módulo CAFFMob muda, mas os destinos legados de cena já foram gravados e cut_plan_stale = True

CA-14 — Aplicação mantém largura
Dado um balcão CAFFMob de 0,9 m de largura, linha DOR
Quando aplico uma definição com DOR.external.base_height = 800
Então altura = 0,8 m, largura continua 0,9 m, btm_overrides é apagado e btm_standard_uid = uid da definição

CA-15 — Medida manual preservada no legado
Dado modo de suporte ligado e um starter de closet com "depth" em btm_overrides
Quando a definição é aplicada sem include_manual
Então "depth" não muda, aparece em skipped_manual, e as demais medidas do starter são atualizadas

CA-16 — Ida e volta JSON
Dado uma definição USER exportada para .btmdim.json
Quando importo o arquivo
Então nasce uma definição USER com UID novo, mesmos valores, nome único e não ativa; a montagem volta como LATERAL

CA-17 — JSON recusado
Dado um arquivo com schema estranho, schema_version 2, unit "cm" ou espessura 999
Quando importo
Então StandardFileError é mostrado e nenhuma definição é criada

CA-18 — Ida e volta Promob
Dado o fixture de 692 atributos
Quando leio e reexporto sem alterações
Então o arquivo de saída tem os mesmos 692 pares (ID, VALUE) e o nome "ME MOVEIS - COZ. ESCR."

CA-19 — XML inválido
Dado XML malformado, raiz <OUTRA/> ou nenhum ATTRIBUTE
Quando leio
Então PromobFormatError com mensagem em português

CA-20 — Migração de projeto herdado
Dado um arquivo sem definições com uma gaiola frameless e btm_settings.config_lateral.thickness setado em 0,018 m
Quando o arquivo é aberto
Então M-02 ativa "Padrão EUA (HB5)", M-01 cria "Migrada" (MIGRATED, ativa) com COZ.sheets.LAT.thickness = 18 e M-03 carimba o uid em raízes sem uid

CA-21 — Migração repetida
Dado um arquivo já marcado com btm_standards_migrated
Quando é reaberto
Então M-01/M-02 não rodam; só M-03 pode marcar raízes novas

CA-22 — Relatório
Dado uma importação Promob concluída com janela
Quando o operador termina
Então caffmob.standards_report abre com total, reconhecidos, não reconhecidos, inválidos e duplicados

CA-23 — Imagem ausente
Dado image_key sem PNG em assets/dimension_refs
Quando icon_id é chamado duas vezes
Então devolve 0 nas duas e imprime o aviso só na primeira
```

## Prioridade (MoSCoW)

| Requisitos | Classificação | Justificativa |
|---|---|---|
| RF-01, RF-02, RF-03 | 🟡 Must | Lidos por cabinet_builder, cabinet_editor, cutting, library_panel, legacy/convert e UI |
| RF-04, RF-05, RF-06 | 🟡 Must | Caminho do usuário para mudar medidas e criar armários; testes puros dedicados |
| RF-07 | 🟡 Should | Só tem efeito sobre gabinetes no modo de suporte; destinos de cena mantêm arquivos antigos coerentes |
| RF-08, RF-09 | 🟡 Should | Interoperabilidade; há alternativa (editar no Configurador) |
| RF-10 | 🟡 Should | Necessário para arquivos antigos; idempotente |
| RF-11, RF-12 | 🟡 Could | Apoio visual |
| `draft.include_manual`, `sync.affected_modules`, `apply_core.targets` | 🟡 Won't (sem consumidor) | Campo nunca lido pela UI; `affected_modules` e `targets` não têm chamador no pacote (só testes para `targets`) |

## Rastreabilidade de Código e Verificação

| Arquivo | Símbolos / responsabilidade | Evidência |
|---|---|---|
| `caffmob_draw/data/dimension_schema.py` | `LINES`, `COMPONENTS`, `Param`, `PARAMS`, `validate`, `PROMOB_INDEX`, `parse_promob_id` | 🟢 Código; `test_dimension_schema` |
| `caffmob_draw/standards/model.py` | 6 PropertyGroups, `ASSEMBLY_ITEMS`, ponteiros `Scene.btm_standards`/`WindowManager.btm_standards_draft` | 🟢 Código |
| `caffmob_draw/standards/builtin.py` | `BUILTINS`, `fill_from_schema`, `ensure_builtins`, `now_iso` | 🟢 Código |
| `caffmob_draw/standards/api.py` | definições, valores, rascunho, árvore, callbacks | 🟢 Código |
| `caffmob_draw/standards/apply_core.py` | `ModuleInfo`, `Plan`, `is_own`, `plan`, `targets` | 🟢 Código; `test_standards_apply_core` |
| `caffmob_draw/standards/cabinet_defaults.py` | `Defaults`, `FALLBACK`, `EXTERNAL`, `defaults` | 🟢 Código; `test_cabinet_defaults` |
| `caffmob_draw/standards/sync.py` | overrides, destinos legados, `scene_modules`, `apply_to_module`, `apply_definition` | 🟢 Código; smoke `blender_012_apply_smoke.py` executado na revisão de 2026-10-10 (código 0) |
| `caffmob_draw/standards/io_json.py` | formato `.btmdim.json` | 🟢 Código; sem teste puro dedicado |
| `caffmob_draw/standards/io_promob.py` | `DIMENSIONEXPORT` | 🟢 Código; `test_promob_io`, `test_promob_assembly` |
| `caffmob_draw/standards/migration.py` | M-01/M-02/M-03, timer | 🟢 Código |
| `caffmob_draw/standards/previews.py` | `icon_id`, coleção de previews | 🟢 Código |
| `caffmob_draw/operators/ops_standards.py` | 13 operadores `caffmob.standards_*`, `ask_apply`, relatório | 🟢 Código |
| `caffmob_draw/ui/standards_tree.py` | `BTM_UL_StandardsTree` | 🟢 Código |

🟢 Executado em 2026-10-10, de dentro de `tests/`: `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest test_standards_apply_core test_dimension_schema test_promob_io test_cabinet_defaults test_promob_assembly` → **35 testes aprovados** (3 + 14 + 12 + 3 + 3). `test_cabinet_hardware` (5 testes, também aprovados) importa só `cutting/` e pertence à unit cutting. Contagens de CA-01 e do fixture (692 atributos, 335 ocorrências mapeadas, 357 não reconhecidas, 294 chaves distintas, 195 de família conhecida sem equivalente) foram executadas nesta sessão. Os smokes `tests/blender_012_apply_smoke.py` e `blender_012_cabinet_standard_smoke.py` exigem Blender e não foram rodados. _(Revisão 2026-10-10: os 35 testes puros repassaram; os dois smokes rodaram no Blender 5.2.0 em `--background` com código 0)_

## Lacunas e Pré-condições

- 🟡 Comportamento real do undo do Blender ao encadear Configurador → 1ª pergunta → 2ª pergunta (três operadores com UNDO) não foi verificado; decisão: testar (DT-07; questions.md#pergunta-87): aceitar um passo por operador (comportamento natural do Blender) e registrar num smoke com janela.
- 🟡 Interoperabilidade real com o Promob (abrir no Promob o XML exportado, inclusive com o ID extra `CAFF_MONTAGEM`) não foi verificada; a docstring afirma que o Promob ignora IDs desconhecidos. Decisão: testar (DT-06; questions.md#pergunta-53): abrir uma vez no Promob; se recusar, exportar `CAFF_MONTAGEM` só sob opção.
- 🟢 Montagem não serializada no JSON (`io_json.values_to_document`). 🟢 **Decisão do titular (2026-10-10, questions.md#pergunta-48):** incluir `assembly` (opcional na leitura, `LATERAL` como padrão), sem subir `schema_version`. Pendência de implementação: DT-01.
- 🟡 Equivalência física `ALT_ARM`/`PROF_ARM` → altura/profundidade de roupeiro DOR é declarada inferida no próprio esquema.
- 🟢 Pré-condição: `hb_project.get_main_scene`, `selection.classify`, `legacy.gate`, `cabinet_editor.bridge/structure`, `data.properties`, `data.units`, `data.i18n` e as bibliotecas frameless/closets disponíveis (ver `design.md` › Dependências).
