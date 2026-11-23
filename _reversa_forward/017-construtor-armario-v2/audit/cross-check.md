# Cross-check: Construtor de armário v2 no CAFFMob Draw

> Identificador: `017-construtor-armario-v2`
> Data da auditoria: `2026-11-21`
> Artefatos analisados:
> - `_reversa_forward/017-construtor-armario-v2/requirements.md` (24 RN, 26 RF, 26 cenários Gherkin)
> - `_reversa_forward/017-construtor-armario-v2/roadmap.md` (D-01 a D-16)
> - `_reversa_forward/017-construtor-armario-v2/actions.md` (T001 a T034)
> - Apoio: `data-delta.md`, `investigation.md`, `onboarding.md`, `_reversa_sdd/domain.md`, código de `caffmob_draw/`
> Natureza: relatório leitor. Nenhum dos três artefatos foi alterado.

## 1. Resumo

| Severidade | Quantidade |
|------------|------------|
| CRITICAL | 1 |
| HIGH | 2 |
| MEDIUM | 4 |
| LOW | 4 |
| **Total** | **11** |

Um CRITICAL de contrato de produção (peça duplicada no plano de corte), dois HIGH de elo quebrado (operador da galeria e flags de presença ausentes no modelo de dados). Os quatro MEDIUM são divergências de documento e cobertura parcial; os LOW são rastreabilidade.

## 2. Findings

| ID | Severidade | Eixo | Descrição | Onde está |
|----|------------|------|-----------|-----------|
| A001 | CRITICAL | 3, coerência com o legado / 1.2 | `btm_cut_exclude` não protege o caminho BTM: `iter_modules` percorre `scene.objects` sem filtro de visibilidade e `synthetic_records` não consulta a marca. Módulo de biblioteca convertido (face frame, que é módulo `btm_*`) continua emitindo peças sintéticas, duplicando-as no plano de corte ao lado do armário v2 | `roadmap.md` §9 (risco "duplicada no plano de corte", mitigação "`part_sources._visible` e `geometry_records` já respeitam"); `roadmap.md` D-13; `actions.md` T026/T029; código `caffmob_draw/cutting/part_sources.py:87` e `:221` |
| A002 | HIGH | 1.2 / 3.2 | `library_panel/ops_cabinet.py` chama `bpy.ops.caffmob.structure_gallery` sem guarda, e esse operador vive em `cabinet_editor/gallery.py`, que o D-04 tira do registro. O roadmap §5 declara `ops_cabinet.py` "contrato-mantido" sem edição; na prática "Criar armário" da biblioteca perde a galeria e o acesso ao operador não registrado levanta `AttributeError` antes do `.poll()` | `roadmap.md` §1, §5 e D-04; `actions.md` T027 (não prevê `gallery` em `ops_cabinet.py`); código `caffmob_draw/library_panel/ops_cabinet.py:46-47` e `caffmob_draw/cabinet_editor/__init__.py:19-24` |
| A003 | HIGH | 1.1 | RN-01 e RF-01 exigem construtor vazio com "Montar Caixa" ligando laterais, base inferior, base superior e fundo, e o HUD mostra "alternadores da estrutura". O modelo de dados não tem flag de presença por peça: `data-delta.md` §2 só tem `gerado`, e nenhuma ação cria `laterais_ativa`, `base_inf_ativa`, `base_sup_ativa`. Sem isso a janela vazia e o Montar Caixa não são representáveis | `requirements.md` RN-01, RF-01; `roadmap.md` D-05; `data-delta.md` §2; `actions.md` T003, T012, T020, T023, T025 |
| A004 | MEDIUM | 2.1 / 4.4 | O roadmap §5 manda registrar `armario_v2` "depois de `customize` ... e antes de `cutting`", mas não existe `cutting.register()` na cascata do addon: `cutting` é importado no topo, não registrado. O T030 já corrigiu o ponto de inserção para "antes de `cabinet_editor.register()`", ficando divergente do roadmap | `roadmap.md` §5; `actions.md` T030; código `caffmob_draw/__init__.py:9-30` e `:340-360` |
| A005 | MEDIUM | 2.1 / 1.2 | `vaos.py` (núcleo) e `test_017_vaos.py` não existem no delta arquitetural: o roadmap §3 D-01 e §5 enumeram sete núcleos (`spec`, `chapas`, `conferencia`, `gavetas`, `portas`, `internos`, `resumo`) e não atribuem módulo a RN-11 (duplicar) nem RN-12 (inserção múltipla). A ação criou um oitavo arquivo | `roadmap.md` §3 D-01 e §5; `actions.md` T006 e T013 (a divergência já está declarada no Resumo do actions) |
| A006 | MEDIUM | 1.3 | RF-20 e o cenário "Reabrir mantém o armário" não têm ação com verificação. T003 grava os PropertyGroups e T023 lê, mas nenhuma ação exercita salvar → reabrir → painel; a fumaça T033 é headless e não faz ida e volta por arquivo `.blend` | `requirements.md` RF-20, §7; `actions.md` T003, T023, T033; `onboarding.md` §14 (só manual) |
| A007 | MEDIUM | 1.3 | O cenário "Erro bloqueante impede OK" e RN-18 ("erro bloqueante impede OK e Aplicar") não aparecem em nenhuma ação de forma explícita: T023 desabilita Gerar e Aplicar apenas para móvel da construção antiga, e T021 trata contrato ausente e snapshot, não erro de faixa | `requirements.md` RN-18, RF-22, §7; `actions.md` T021, T023 |
| A008 | LOW | 1.2 | D-07 (sem modal; Gerar/Cancelar) e D-15 (um teste puro por regra e uma fumaça) não são citados por nenhuma ação, embora estejam implementados de fato em T021 e no par T005–T011/T033. Rastreabilidade decisão → ação incompleta | `roadmap.md` D-07, D-15; `actions.md` inteiro |
| A009 | LOW | 1.1 | RF-17 (acabamento) não tem decisão própria no roadmap: D-01 a D-16 não cobrem o tema, que aparece só em RN-14 e na ação T020 | `requirements.md` RF-17; `roadmap.md` §3 |
| A010 | LOW | 4.4 | O roadmap §5 e o T029 dizem somar o adaptador "depois das gavetas"; em `extract_production_parts` a ordem é caffmob → BTM → cutpart → geometry → stairs → drawers → **promob**, então "depois das gavetas" tem duas leituras. Sem impacto funcional porque há `parts.sort` no fim | `roadmap.md` §5; `actions.md` T029; código `caffmob_draw/cutting/part_extractor.py:94-110` |
| A011 | LOW | 0, instalação | `.reversa/state.json` e `.reversa/active-requirements.json` não existem nesta instalação. O skill manda abortar sem o segundo; a auditoria foi feita resolvendo a feature pelos artefatos (única com `roadmap.md` e sem `actions.md`) | ausência em `.reversa/` |

## 3. Detalhe dos CRITICAL e HIGH

### A001, peça duplicada no plano de corte (CRITICAL)

O D-13 resolve a conversão de módulo de biblioteca por ocultação do módulo antigo mais `btm_cut_exclude`, e o roadmap §9 justifica que `part_sources._visible` e `geometry_records` "já respeitam as duas marcas". Isso é verdade só para as peças filhas lidas pelo caminho CUTPART: `_cutpart_found` filtra `_visible(obj)` e `getattr(obj, 'btm_cut_exclude', False)` por filho. Não vale para o caminho BTM: `iter_modules` (`part_sources.py:87`) varre `scene.objects` sem checar ocultação nem exclusão, e `synthetic_records` (`:221`) deduz laterais, bases, prateleira e portas de `btm_cabinet`/`dimensions` sem nunca consultar a marca. Como face frame é módulo `btm_*` (o próprio `requirements.md` §2 cita `btm_cabinet`/`btm_structure` como origem dos parâmetros), o cenário de A001 é o caminho normal do RF-24, não uma borda.

Impacto: o plano de corte lista duas vezes as peças do mesmo móvel, com medidas diferentes (sintéticas do módulo antigo e reais do armário v2). É exatamente o dado que vai para a produção e o risco que o §9 diz ter mitigado, o que o torna pior: a mitigação declarada impede que alguém procure o defeito. Contraria a regra 🟢 de `_reversa_sdd/cutting/requirements.md#Origem das peças` (objeto marcado como excluído não entra).

Direção da correção (não executada aqui): decidir onde o filtro vive — provavelmente em `iter_modules` (ignorar módulo oculto ou com `btm_cut_exclude`) e um teste puro que conte as peças antes e depois de `Gerar` a partir de módulo, como o §9 já pede. O `actions.md` precisa de uma ação com esse alvo; hoje o T029 só acrescenta o adaptador novo. Skill sugerido para o humano: `/reversa-clarify` no escopo do corte, ou edição manual do roadmap §9 e do T029.

### A002, o operador da galeria desaparece com a interface (HIGH)

`library_panel/ops_cabinet.py:46` faz `bpy.ops.caffmob.structure_gallery.poll()` dentro de `invoke`, sem `try/except`, e `:47` invoca o operador. Esse operador é `bl_idname = "caffmob.structure_gallery"`, registrado por `cabinet_editor/gallery.py:250`, que está na lista de módulos que o D-04 remove de `_modules()` (`cabinet_editor/__init__.py:19-24`). O roadmap §1 lista `gallery` entre o que sai do registro e, três seções depois, §5 declara `library_panel/ops_cabinet.py:79` "contrato-mantido, sem edição". As duas afirmações não podem valer juntas.

Impacto: o botão "Criar armário" da biblioteca é o caminho pelo qual o módulo nasce na feature 015 (T036), e é justamente o ponto de entrada do RF-24 (módulos de biblioteca no motor novo). Acesso a operador não registrado não devolve `poll()` falso de forma silenciosa: levanta `AttributeError` na obtenção do atributo. Mesmo que devolvesse falso, o fluxo cairia no diálogo antigo e a galeria de estruturas sumiria sem aviso — perda de função não declarada em nenhum requisito.

Direção da correção: escolher entre manter `gallery` registrado (é UI, mas é o único caminho de criação de módulo por estrutura) ou adaptar `ops_cabinet.py` com guarda e um substituto. Isso muda o escopo do T027 e a linha correspondente do §5. Skill sugerido: `/reversa-clarify`.

### A003, o modelo não representa "construtor vazio" (HIGH)

RN-01 é a regra de abertura da feature: nada marcado, nenhuma peça, estado "janela de armário vazia", com Montar Caixa e Limpar. RF-01 detalha que Montar Caixa "liga laterais, base inferior, base superior e fundo". O painel também teria alternadores da estrutura no HUD (T025). O `data-delta.md` §2 descreve o `BTM_PG_ArmarioV2` campo a campo e não traz nenhuma flag de presença de peça estrutural; o único estado é `gerado` (booleano) e `aberto`. Com esse contrato, "Montar Caixa" não tem o que ligar: ou as peças existem desde que o spec existe, ou não existem nunca.

Impacto: é a primeira coisa que o projetista vê (`onboarding.md` §2 e §4) e o primeiro critério de aceite do RF-01. Descobrir no T023 que o campo não existe força mexer no `props.py`, no `spec.py`, no `build.py` e no `data-delta.md` no meio da integração.

Direção da correção: acrescentar as flags de presença ao §2 do `data-delta.md` e uma ação que as crie antes do `build` (o T012 é o lugar natural, junto das faixas). Skill sugerido: `/reversa-clarify`.

## 4. Verificados e aprovados

### Eixo 1, cobertura

- RF-01 a RF-26 têm pelo menos um destino nas ações: os 26 aparecem citados ou são cobertos pelas regras que os originam, com as três exceções acima (A003, A006, A007).
- D-01 a D-16 têm ação correspondente: D-01/D-02 em T003–T004, D-03 em T021, D-04 em T027, D-05 em T023, D-06 em T024, D-08 em T022, D-09 em T015, D-10 em T012, D-11 em T014, D-12 em T001, D-13 em T026, D-14 em T023, D-16 em T031. D-07 e D-15 são cobertos de fato, só não citados (A008).
- 26 cenários Gherkin: 24 com ação que os exercita (testes puros T005–T011 ou fumaça T033); 2 com cobertura parcial (A006, A007).
- RN-16, RN-19 e RN-24 (o corte ler o papel gravado) têm três pontos independentes: papel em T020, adaptador em T029, lista em T019.

### Eixo 2, consistência

- Terminologia estável nos três documentos: `btm_armario`, `btm_armario_parte`, `btm_armario_contrato`, `papel`, `vão`, `bloquear_chapa`, `Gerar`/`Aplicar`/`Cancelar`, `deslizante`, `folha`, `afastador`, `separador`.
- Todos os identificadores citados existem: RN-01 a RN-24 e RF-01 a RF-26 conferem nos requisitos; D-01 a D-16 conferem no roadmap. Nenhum identificador fantasma.
- O roadmap §7 declara que não há contrato externo novo e não há `interfaces/`; o corte continua no JSON v2 existente. A declaração confere com `actions.md` (nenhuma ação de formato externo).
- `data-delta.md` e `props.py` previsto em T003 batem campo a campo, com a exceção A003.

### Eixo 3, coerência com o legado

- RN-CABINET_EDITOR-01 (🟢 um passo de desfazer por confirmação; Cancelar reaplica o instantâneo) é preservada por D-07/T021, com o instantâneo em `snapshot` JSON em vez da sessão em memória.
- RN-CABINET_EDITOR-02 (🟢 erro impede OK e Aplicar) é preservada em intenção; a ação explícita falta (A007).
- RN-CABINET_EDITOR-11 (🟢 divisões, extras, internos e deslizantes como filhos diretos da raiz) confere com a raiz vazia de T020.
- RN-CABINET_EDITOR-12 (🟢 vãos em cadeia `s0`, `s0.b`…) confere com o caminho de vão de T006/T013.
- Componentes citados no roadmap existem no código: `cabinet_editor.structure.carcass_lengths`, `part_extractor.limit_status` (`:23`), `part_extractor.extract_production_parts` (`:94`), `part_sources.PartRecord`, `part_sources._visible` (`:123`), `standards.api`, `data/i18n.py`, `ui/context_menu.py`.
- Conflito consciente e arbitrado, não reportado como defect: RN-22 e RF-26 tiram o móvel antigo da edição, contra o comportamento 🟢 do editor 2D. A decisão do titular está registrada no `requirements.md` §9 (sessão 2026-11-19) e o roadmap §2 a marca "conflita (aceito)". O RF-26 preserva os móveis existentes na cena e no corte.

### Eixo 4, sanidade do actions

- 34 IDs únicos e sequenciais, `T001` a `T034`, nenhum reciclado; todos os `Status` em `[ ]`.
- Toda dependência aponta para ID existente; nenhuma aponta para si mesma; todas apontam para ID menor, portanto não há ciclo.
- As 21 ações `[//]` não compartilham arquivo alvo entre si dentro da mesma onda: os sete testes (T005–T011) são arquivos distintos, os seis núcleos (T013–T019) idem, e os itens avulsos (T001, T002, T024, T025, T028, T029, T031) também.
- Nenhuma ação de configuração de IDE, lint avulso ou abertura de PR. T034 é verificação de critério de pronto, no padrão das features 004/006/008/016.
- Toda ação cabe num turno: nenhuma passa de cinco subpontos, de três arquivos não relacionados ou de encadeamento "e também/depois".

## 5. Observações de contexto

- A ausência de `.reversa/state.json` (A011) é de instalação, não de conteúdo: os caminhos usados foram `_reversa_forward/` e `_reversa_sdd/`, que existem.
- O `_reversa_sdd/` não foi auditado nesta passada; a comparação com o legado se limitou às regras 🟢 de `domain.md` e de `cutting/requirements.md` citadas pelos artefatos da 017.

## 6. Fechamento (2026-11-21)

| ID | Estado | Como foi fechado |
|----|--------|------------------|
| A001 | ✅ fechado | Ação **T035** criada: filtrar módulo oculto ou com `btm_cut_exclude` em `part_sources.iter_modules`, com `tests/test_017_corte.py` contando as peças antes e depois de `Gerar` a partir de módulo. Roadmap §9 corrigido e D-17 acrescentado. |
| A002 | ✅ fechado | Decisão do titular: `gallery` **permanece registrado** em `cabinet_editor._modules()`; `library_panel/ops_cabinet.py` não é editado. T027 e roadmap §1/§5 ajustados. |
| A003 | ✅ fechado | Decisão do titular: **quatro flags de presença mais `fundo_ativo`**, não um enum de montagem rápida. `data-delta.md` §2 já traz `lateral_esq_ativa`, `lateral_dir_ativa`, `base_inf_ativa` e `base_sup_ativa` (padrão `False`); D-18 passou de 🟡 a 🟢 e T003 as cria. |

Motivo de A003 ficar por flags: as peças estruturais são independentes umas das outras (RN-01 e RF-01 pedem alternadores por peça no HUD e um `snapshot` que restaure qualquer combinação). Um enum de montagem rápida só representaria presets fechados — quatro peças já dão quinze combinações não vazias, e a combinação escolhida pelo projetista teria de ser convertida de volta para flags ao salvar. O enum pode ser acrescentado depois como *atalho de interface* que liga várias flags de uma vez, sem mudar o modelo de dados.

A007 e A006 continuam abertos: nenhuma ação exercita salvar → reabrir → painel e nenhuma trata erro de faixa bloqueando OK/Aplicar de forma explícita.
