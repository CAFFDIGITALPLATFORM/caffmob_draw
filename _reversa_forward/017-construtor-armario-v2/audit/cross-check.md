# Cross-check: Construtor de armário v2 no CAFFMob Draw

> Identificador: `017-construtor-armario-v2`
> Data da auditoria: `2026-11-23` (segunda passada; a primeira foi em `2026-11-21`)
> Artefatos analisados:
> - `_reversa_forward/017-construtor-armario-v2/requirements.md` (24 RN, 26 RF, 26 cenários Gherkin)
> - `_reversa_forward/017-construtor-armario-v2/roadmap.md` (D-01 a D-18)
> - `_reversa_forward/017-construtor-armario-v2/actions.md` (T001 a T035, 35 ações, todas `[X]`)
> - Apoio: `data-delta.md`, `_reversa_sdd/domain.md`, `_reversa_sdd/cutting/requirements.md`, código de `caffmob_draw/`, `.reversa/state.json` e `.reversa/active-requirements.json`
> Natureza: relatório leitor. Nenhum dos três artefatos foi alterado.

## 1. Resumo

| Severidade | Quantidade |
|------------|------------|
| CRITICAL | 0 |
| HIGH | 2 |
| MEDIUM | 3 |
| LOW | 4 |
| **Total** | **9** |

Os três achados da primeira passada (A001 a A003) foram fechados de verdade: `btm_cut_exclude` passou a valer na origem do corte (T035), a galeria continua registrada (T027) e as quatro flags de presença existem em `props.py` (T003). O que resta é diferente: a feature está com 35 de 35 ações `[X]`, e o que sobra são **dois requisitos `Must` sem implementação ou sem verificação** (`RF-10`/`RN-08`, a corrediça 3D; e `RF-20`/`RN-17`, reabrir o arquivo), mais divergências de documento.

## 2. Findings

| ID | Severidade | Eixo | Descrição | Onde está |
|----|------------|------|-----------|-----------|
| A012 | HIGH | 1.1 / 1.3 | `RN-08` e `RF-10` (`Must`) exigem a corrediça telescópica 3D na cena, com trilho externo, trilho interno e gaiolas, e um conjunto geométrico equivalente quando falta o OBJ. **Nada disso existe no motor**: nenhuma ação do plano instancia o modelo, `caffmob_draw/armario_v2/` não tem um único import de OBJ (`import_scene.obj`/`wm.obj_import` só aparece em `promob/complemento.py`) e `GAIOLA`/`CORREDICA`/`TRILHO` em `armario_v2/` só existem como papel de animação e como item de enum. O T033 registra o limite nas próprias notas ("o OBJ da corrediça continua não instanciado pelo motor") e mesmo assim o T020 e a feature fecham | `requirements.md` RN-08, RF-10 e cenário "Corrediça 3D ausente do pacote"; `roadmap.md` D-12; `actions.md` T001, T020, T022, T033 (Notas de execução, 2026-11-22) |
| A013 | HIGH | 1.3 | `RN-17` e `RF-20` (`Must`) exigem que os parâmetros fiquem gravados no armário e que salvar, fechar, reabrir e abrir o construtor devolva o mesmo estado. O mecanismo existe (`BTM_PG_ArmarioV2` em `Object.btm_armario`, D-02), mas não há **ação nem teste** que o exercite: as 35 ações não citam `RF-20` nem `RN-17`, e `tests/blender_017_armario_smoke.py` não tem uma linha de `save_as_mainfile` ou `open_mainfile`. Era o A006 (MEDIUM no plano); com a feature fechada, requisito `Must` sem nenhuma prova sobe para HIGH | `requirements.md` RN-17, RF-20 e cenário "Reabrir mantém o armário"; `actions.md` T003, T023, T033; código `tests/blender_017_armario_smoke.py` |
| A014 | MEDIUM | 1.1 | `RN-18` e `RF-22` dizem que "erro bloqueante impede OK e Aplicar" e o critério de aceite pede o botão desabilitado. No código, `spec.validate` só roda dentro de `ops.Gerar` (recusa no clique, com `report`), e o painel desabilita `Gerar` apenas por `chapas.pode_gerar`. Uma largura fora de faixa deixa o botão habilitado e o erro só aparece depois do clique. Era o A007, permanece aberto | `requirements.md` RN-18, RF-22, cenário "Erro bloqueante impede OK"; `caffmob_draw/armario_v2/panel.py:105` e `:324`; `caffmob_draw/armario_v2/ops.py:262` |
| A015 | MEDIUM | 2.1 | Os documentos divergem sobre a mesma decisão do titular: o `requirements.md` §9 diz que o A003 ficou **sem resposta** ("Não houve resposta do titular nesta sessão; a derivação está registrada como premissa 🟡 em D-18") e o §10 repete que faltava confirmar no T003, mas o `roadmap.md` D-18 está 🟢 e afirma "Confirmado pelo titular em 2026-11-21 (fechamento do A003)", e o fechamento registrado na primeira passada também diz decisão do titular. Um dos dois está errado sobre um fato verificável | `requirements.md` §9 (sessão 2026-11-21) e §10; `roadmap.md` D-18; histórico do `requirements.md` §11 |
| A016 | MEDIUM | 4.1 | O Resumo do `actions.md` declara "Maior cadeia de dependência: 10 (T005 → T012 → T013 → T020 → T021 → T023 → T027 → T030 → T033 → T034)". A cadeia real tem **11** elos e passa por T014 e T015: T005 → T012 → T014 → T015 → T020 → T021 → T023 → T027 → T030 → T033 → T034. O `T013` citado não é ancestral do `T020` (`T020` depende de `T012`, `T013`, `T015`, `T016`, `T017`, `T018`, `T003`) | `actions.md` §Resumo |
| A017 | LOW | 1.1 | Cinco requisitos não são citados por nenhuma ação, embora estejam cobertos de fato pelas regras que os originam: `RF-05` (montagem/orientações, via `RN-04` em T005/T012), `RF-06` (espessura por papel, via `RN-05`), `RF-07` e `RF-08` (divisões e duplicar, via `RN-12`/`RN-11` em T006/T013), `RF-15` (fundo, via `RN-15`). `RN-17` é o único RN sem citação, e esse é o A013 | `requirements.md` §5; `actions.md` inteiro |
| A018 | LOW | 1.2 | `D-07` (sem modal) e `D-15` (um teste puro por regra e uma fumaça) continuam sem citação em ação alguma, apesar de implementados em T021 e no par T005–T011/T033. Rastreabilidade decisão → ação incompleta, sem efeito funcional. Era o A008 | `roadmap.md` D-07, D-15; `actions.md` inteiro |
| A019 | LOW | 0 / 2.1 | O critério de pronto do `roadmap.md` §10 está com os nove itens desmarcados, inclusive "Todas as ações do `actions.md` marcadas `[X]`", que hoje é verdade (35 de 35). E o item "`ruff check caffmob_draw/` limpo" é contradito pela decisão 1 registrada na T034 (21 erros preexistentes, de propósito não corrigidos nesta feature) | `roadmap.md` §10; `actions.md` T034, Notas de execução |
| A020 | LOW | 0 / instalação | `.reversa/active-requirements.json` continua em `current-stage: plan` com `stages-completed: [requirements, clarify]`, enquanto o `actions.md` está 35 de 35 `[X]` e o `roadmap.md` §10 fala em critério de pronto. O estado da feature não reflete o estágio real | `.reversa/active-requirements.json` |

## 3. Detalhe dos HIGH

### A012, a corrediça 3D nunca é criada (HIGH)

O `RN-08` é explícito: com corrediça 3D ligada, cada gaveta recebe o conjunto importado do arquivo de modelo, com trilho externo preso na lateral do armário, trilho interno preso na gaveta e gaiolas a meio curso, e **sem o arquivo** entra o conjunto geométrico equivalente com as mesmas três partes marcadas. O `RF-10` é `Must` e repete a regra no critério de aceite ("cada gaveta recebe duas corrediças").

O que existe hoje no pacote: o arquivo `caffmob_draw/assets/slides/slide-st48-0200-0.obj` copiado em T001, o campo `corredica_3d` em `gavetas.py` e em `ops.py`, o item de enum e o papel `GAIOLA`/`CORREDICA`/`TRILHO` que a animação consulta em `anim.py:39`. O que não existe: o import do OBJ, a instanciação por gaveta e o conjunto geométrico de reserva. Nenhum arquivo de `armario_v2/` importa OBJ (o único import de OBJ do pacote está em `promob/complemento.py`), e a fumaça da 017 não tem uma conferência sobre a corrediça.

Impacto: é uma peça de ferragem que o projetista promete ao cliente e que não aparece no projeto. A gaveta abre e fecha (a animação foi provada com 72% de curso), mas o trilho que deveria acompanhá-la não está na cena. Como a feature já está fechada com 35 de 35 ações, o defeito não tem dono no plano: o T020 fecha sem a corrediça e o T033 declara o limite nas notas em vez de abrir ação. E o critério de pronto do `roadmap.md` §10 não inclui "a corrediça aparece na cena", então ele não pega isso.

Direção da correção (não executada aqui): abrir ação nova para instanciar o OBJ em `build.py` (uma importação por armário, instâncias por gaveta, como o D-12 descreve) mais a alternativa geométrica, e acrescentar à fumaça uma conferência de que cada gaveta tem trilho externo, trilho interno e gaiola, com e sem o arquivo. Skill sugerido para o humano: `/reversa-plan` (ação nova) ou `/reversa-clarify` se a decisão for adiar o `RN-08` e rebaixar o requisito.

### A013, reabrir o arquivo nunca foi provado (HIGH)

`RN-17` e `RF-20` são o motivo de o spec viver em `Object.btm_armario` (D-02): gerar, salvar, fechar, reabrir e abrir o construtor devolvendo as mesmas medidas, divisões, gavetas, portas e fundo, com as peças na cena. O desenho está certo, propriedades de `PropertyGroup` viajam no `.blend` e a abertura grava `snapshot`, mas **nenhuma ação e nenhuma fumaça fazem a ida e volta por arquivo**: o `blender_017_armario_smoke.py` não chama `save_as_mainfile` nem `open_mainfile` (outras fumaças do repositório chamam, a da 017 não).

Impacto: é o requisito que sustenta a decisão de modelo de dados inteira, e o único caminho que o exercita hoje é manual, numa janela. Um `PointerProperty` mal declarado, um `EnumProperty` que reescreve o valor ao carregar ou um `snapshot` que não sobrevive ao ciclo passariam por todos os 48 testes puros e pela fumaça atual sem aparecer. A feature estava com o A006 aberto desde 2026-11-21 e o plano fechou assim mesmo.

Direção da correção: uma ação de verificação, sem tocar no desenho: gravar, salvar em `tempdir`, reabrir com `bpy.ops.wm.open_mainfile`, conferir abas, medidas e peças. Skill sugerido para o humano: `/reversa-plan`.

## 4. Verificados e aprovados

### Eixo 1, cobertura

- `RF-01` a `RF-26`: 19 aparecem citados nas ações e, dos 7 restantes, 5 têm cobertura real por outra via (A017). Só `RF-20` (A013) não tem cobertura nem citação, e `RF-10` (A012) tem citação mas não implementação.
- `RN-01` a `RN-24`: 23 citados; `RN-17` é o único ausente (A013). `RN-08` é citado e não implementado (A012).
- `D-01` a `D-18`: 16 citados em ação; `D-07` e `D-15` são cobertos de fato (A018). `D-17` aparece em T035 e `D-18` em T003, fechando os achados da primeira passada.
- 26 cenários Gherkin: 24 com teste puro ou conferência de fumaça que os exercita; "Reabrir mantém o armário" sem prova (A013) e "Corrediça 3D ausente do pacote" sem implementação (A012).
- Os três achados da primeira passada estão fechados com prova: A001 em T035 e `tests/test_017_corte.py` (6 casos) mais a fumaça (7 → 0 peças); A002 em T027 (galeria registrada, `ops_cabinet.py` intocado); A003 em T003 e D-18 (quatro flags, `False` por padrão, confirmadas pela fumaça do HUD).

### Eixo 2, consistência

- Terminologia estável: `btm_armario`, `btm_armario_parte`, `btm_armario_contrato`, `papel`, `vão`, `bloquear_chapa`, `Gerar`/`Aplicar`/`Cancelar`, `deslizante`, `folha`, `afastador`, `separador`, `Montar Caixa` aparecem com o mesmo nome nos três documentos.
- Identificadores citados existem: `RF-01` a `RF-26` e `RN-01` a `RN-24` conferem no `requirements.md`; `D-01` a `D-18` conferem no `roadmap.md`; `T001` a `T035` conferem no `actions.md`. Nenhum identificador fantasma.
- O `RN-27` citado no `requirements.md` §2 é do `_reversa_sdd/cabinet_editor/requirements.md`, não deste documento, e está identificado como tal.
- Contratos: o `roadmap.md` §7 declara que não há contrato externo novo e o `actions.md` confere (o JSON de corte é o mesmo, com `ARMARIO_V2` acrescentado a `json_exporter.SOURCES` em T029).
- `data-delta.md` e o código batem: nove espessuras no armário, oito no contrato, com a diferença da `espessura_folha` registrada nas notas de T003 e T004.

### Eixo 3, coerência com o legado

- RN-CABINET_EDITOR-01 (🟢 um passo de desfazer por confirmação) preservada: `Gerar`/`Aplicar`/`Cancelar` com `UNDO`, `Cancelar` reaplicando o `snapshot` (T021), provado na fumaça.
- RN-CABINET_EDITOR-11 (🟢 divisões, extras e internos como filhos diretos da raiz) preservada pela raiz vazia de `build.criar_raiz` e por `build.e_raiz` (T033, defeito 4 corrigido).
- RN-CABINET_EDITOR-12 (🟢 vãos em cadeia `s0`, `s0.b`, `s0.a`) preservada em `vaos.arvore` e provada em `test_017_vaos.py`, inclusive depois da correção de colisão de caminhos de 2026-11-22.
- Regra 🟢 de `_reversa_sdd/cutting/requirements.md#Origem das peças` (objeto marcado como excluído não entra) agora vale na origem, em `iter_modules` (T035).
- Componentes citados existem: `cabinet_editor.structure.carcass_lengths`, `part_extractor.extract_production_parts`, `part_sources.PartRecord`, `part_sources._visible`, `standards.api`, `data/i18n.py`, `json_exporter.SOURCES`.
- Conflito consciente e arbitrado, não reportado como defeito: RN-22 e RF-26 tiram o móvel antigo do editor 2D, contra o comportamento 🟢 do legado. A decisão está no `requirements.md` §9 e o `roadmap.md` §2 a marca "conflita (aceito)"; as fumaças 006 e 008 foram aposentadas com README em `tests/retired/`.

### Eixo 4, sanidade do actions

- 35 IDs únicos e sequenciais, `T001` a `T035`, nenhum reciclado, nenhum duplicado; todas as 35 em `[X]`.
- Toda dependência aponta para ID existente e para ID menor: nenhuma quebrada, nenhuma autorreferência, **nenhum ciclo** (verificado por percurso completo do grafo).
- As 21 ações `[//]` não compartilham arquivo alvo entre si: os sete testes (T005–T011), os seis núcleos paralelos (T013–T019, menos T012 e T018 que são sequenciais por dependência), e os avulsos (T001, T002, T024, T028, T029, T031) apontam cada um para um arquivo distinto. `part_sources.py` aparece em T029 (`[//]`) e T035 (sequencial, dependente de T029), sem violação.
- Distribuição por fase: preparação 4 (T001–T004), testes 7 (T005–T011), núcleo 8 (T012–T019), integração 13 (T020–T031 e T035), polimento 3 (T032–T034). Soma 35, confere com o Resumo.
- Nenhuma ação de configuração de IDE, lint avulso ou abertura de PR.

## 5. Observações de contexto

- A primeira passada desta auditoria (2026-11-21) teve 1 CRITICAL e 2 HIGH, todos fechados por decisão do titular e registrados no histórico do `requirements.md` §11 e do `actions.md`. Este relatório substitui aquele, como o skill manda.
- O que mudou entre as duas passadas: T035 (achado A001) foi criado e executado, D-17 e D-18 entraram no roadmap, e as 35 ações foram fechadas. A cobertura de teste cresceu de 34 para 48 casos puros mais a fumaça no Blender 5.2 com 48 conferências.
- `_reversa_sdd/` não foi auditado nesta passada; a comparação com o legado se limitou às regras 🟢 de `domain.md` e de `cutting/requirements.md` citadas pelos artefatos da 017.
- O `audit/janela/` guarda três capturas da conferência em janela de 2026-11-22 (`1-armario-vazio.png`, `2-peca-escolhida.png`, `3-painel-em-popup.png`). Elas provam desenho, não regra: nenhum dos dois HIGH depende delas.

## 6. Próximo passo sugerido

Há dois HIGH abertos, nenhum deles corrigível por este relatório:

1. A012 e A013 pedem **ação nova** no `actions.md` (a corrediça 3D e a ida e volta por arquivo). Isso é `/reversa-plan`, ou `/reversa-to-do` se a decisão do titular for só acrescentar as ações ao plano existente.
2. A014, A015, A016, A019 e A020 são correções de documento: `requirements.md` §9/§10 contra o D-18, o Resumo do `actions.md`, o §10 do roadmap e o `active-requirements.json`. Isso é edição manual ou `/reversa-clarify`, nunca este skill.
3. A012 tem uma decisão de produto embutida: implementar o `RN-08` agora ou rebaixá-lo no `requirements.md` e fechar a feature sem a corrediça 3D. Só o titular decide.

Estado: nenhum dos três artefatos foi alterado por esta auditoria.
