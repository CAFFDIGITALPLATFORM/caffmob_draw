# Cross-check: 012-biblioteca-caffmob-chapas

> Data: `2026-10-09`
> Gerado por `/reversa-audit` (somente leitura: nenhum artefato da feature foi alterado).
> Artefatos analisados:
> - [`requirements.md`](../requirements.md) (com as sessões de esclarecimento 1 a 3)
> - [`roadmap.md`](../roadmap.md) (versão 2)
> - [`actions.md`](../actions.md) (versão 2)
> - apoio: [`data-delta.md`](../data-delta.md), [`interfaces/promob-dimensionexport.md`](../interfaces/promob-dimensionexport.md),
>   `_reversa_sdd/domain.md`, `_reversa_sdd/architecture.md`, `.reversa/principles.md`

## Resumo

| Severidade | Quantidade |
|------------|-----------:|
| CRITICAL | 0 |
| HIGH | 1 |
| MEDIUM | 4 |
| LOW | 2 |

## Achados

| ID | Severidade | Eixo | Descrição | Onde está |
|----|------------|------|-----------|-----------|
| A001 | HIGH | Cobertura | Os requisitos pedem o **balcão gaveteiro** entre os modelos prontos, e o critério de aceite conta **6 modelos**. O roadmap tira o gaveteiro (o módulo CAFFMob não tem gavetas), e o actions cria **5 modelos**. Um requisito Must fica sem cobertura até o titular confirmar | `requirements.md` RN-15, RF-02, RF-15; `roadmap.md` D-16, P1; `actions.md` T057 |
| A002 | MEDIUM | Cobertura | A RN-12 tira as bibliotecas herdadas de **toda** a interface. A biblioteca de molduras (`HOME_BUILDER_PT_molding_library`, `ui/view3d_sidebar.py` l. 1106-1175, com `caffmob_frameless.add_molding_profile` e `add_solid_lumber`) e a lista de pacotes de moldura do ambiente (dentro da interface do face frame, `props_hb_face_frame.py` l. 7674) não aparecem na nota D-02 nem em nenhuma ação. Ficam visíveis, ou somem sem querer junto com a interface do face frame | `requirements.md` RN-12; `roadmap.md` D-02; `actions.md` (ausente) |
| A003 | MEDIUM | Cobertura | "Meus módulos" perde as origens FRAMELESS e FACE_FRAME (T049), que são os grupos salvos pelo usuário nessas bibliotecas ("Grupos frameless", "Grupos face frame", `ui/my_modules.py` l. 15-16). A RN-13 só converte armários **da cena**: os grupos salvos ficam inacessíveis, sem conversão e sem aviso | `requirements.md` RN-11, RN-13; `roadmap.md` D-02, D-23; `actions.md` T049 |
| A004 | MEDIUM | Sanidade do actions | A T062 confere o Ctrl+Z da conversão com `ed.undo` numa fumaça **em segundo plano**. O projeto só prova o desfazer com janela e eventos simulados (`tests/blender_bug_ZZUK_undo.py`), e a 011 registrou o undo como frágil fora da interface. O critério do RF-14 ("Ctrl+Z volta os 5 originais") pode ficar sem prova real | `requirements.md` RF-14; `actions.md` T062 |
| A005 | MEDIUM | Consistência | O roadmap chama o valor neutro de `product_tab` de `FRAMELESS` (D-04, "o neutro de fábrica"), mas a RN-12 tira o frameless da interface. O valor não é neutro: é o de uma biblioteca herdada. Deixar isso explicado evita que a remoção do código (RN-14) apague o item do enum e quebre arquivos antigos | `roadmap.md` D-04; `data-delta.md` §2; `actions.md` T054 |
| A006 | LOW | Consistência | O `requirements.md` ainda cita 694 atributos no histórico (sessão 3, "694 → 692"); os demais pontos já dizem 692 | `requirements.md` §11 |
| A007 | LOW | Sanidade do actions | O ID T045 ficou sem uso na versão 2 (de T044 pula para T046). Não é reciclagem, mas o resumo é o único lugar que avisa | `actions.md` Resumo |

## Impacto e direção dos achados HIGH

**A001, gaveteiro.** Se o código seguir o actions, a Cozinha sai sem gaveteiro, e o RF-02 e o RF-15 reprovam pelo
próprio critério ("6 modelos"). Se seguir os requisitos, não há como montar gavetas no módulo CAFFMob
(`customize/adapters/btm.py`, l. 15-17 e 51-55). A decisão é do titular:
- confirmar a P1 (gavetas numa feature própria) e ajustar a RN-15, o RF-02 e o RF-15 por `/reversa-clarify` ou edição
  manual;
- ou pedir gavetas no módulo CAFFMob nesta feature, o que pede `/reversa-plan` de novo (decisões e ações novas no I2).

## Itens verificados que passaram

**Cobertura**
- Os 15 RF e as 15 RN aparecem no roadmap, pelo número ou pelas faixas da tabela de incrementos (RF-01 a RF-04,
  RF-05 a RF-07, RF-08 a RF-10…).
- As 27 decisões (D-01 a D-27) têm ação no actions.
- Os 16 cenários Gherkin têm ação:
  - painel e HUD → T020 a T023 e T040;
  - categorias e nome repetido → T025 e T040;
  - Criar armário e Cancelar → T027 e T038;
  - armário no padrão e base passante → T038;
  - aplicar, não aplicar, segunda pergunta e item importado → T039;
  - bibliotecas fora da interface → T056;
  - converter e não converter → T062;
  - modelo pronto na categoria → T024 e T039.

**Consistência**
- Nenhum ID fantasma: todo RN e RF citado no roadmap e no actions existe no requirements; todo D citado no actions
  existe no roadmap.
- O contrato `interfaces/promob-dimensionexport.md` aparece no roadmap (§7, D-27) e nas ações T009 e T016; a contagem
  certa (692) está no contrato, no roadmap e no actions.
- O tipo do armário é `cabinet_type` nos três documentos da versão 2 (o `kind` da versão 1 só aparece como
  alternativa descartada).

**Coerência com o legado**
- Nenhuma decisão contradiz regra 🟢 do `_reversa_sdd/domain.md`. Paredes, aberturas (R-04 a R-08) e plano de corte
  (R-09, R-10) não são tocados; a lista de corte só muda pela montagem do módulo CAFFMob.
- A construção brasileira padrão (001, RN-03, laterais passantes) continua o padrão.
- Os componentes citados existem no código:
  - `standards/` (sync, api, io_promob, migration);
  - `cabinet_editor/structure.py`, `bridge.py` e `panels_structure.py`;
  - `cutting/part_sources.py`;
  - `customize/adapters`;
  - `selection/classify.py` e `component_select.py`;
  - `operators/viewport_hud.py`.
- Os princípios I a XI estão avaliados no roadmap §2, sem conflito.

**Sanidade do actions**
- 60 ações ativas; todas as dependências apontam para IDs existentes; nenhum ciclo.
- Maior cadeia: 9 (T008 → T015 → T020 → T021 → T022 → T023 → T024 → T037 → T041), igual ao resumo.
- Nenhum par de ações `[//]` divide arquivo alvo.
- As ações removidas (T030, T035) estão registradas com o motivo, e os IDs não foram reciclados.
