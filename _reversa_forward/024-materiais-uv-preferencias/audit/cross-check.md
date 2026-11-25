# Cross-check: 024-materiais-uv-preferencias

> Data: 2026-11-25 (auditoria do `todo.md` contra o `roadmap.md`, o `requirements.md` e o código real)
> Feature: `_reversa_forward/024-materiais-uv-preferencias`
> Artefatos analisados: [requirements.md](../requirements.md) · [roadmap.md](../roadmap.md) · [todo.md](../todo.md)
> Leitura de código: `caffmob_draw/armario_v2/build.py`, `props.py`, `__init__.py`, `edgeband/build.py`,
> `edgeband/props.py`, `hb_details.py`

## Resumo

| Severidade | Quantidade |
|---|---|
| CRITICAL | 0 |
| HIGH | 0 |
| MEDIUM | 1 |
| LOW | 3 |

Nenhuma ação do `todo.md` foi executada; esta auditoria é leitora e só gravou este relatório.

## Achados e situação

| ID | Severidade | Eixo | Descrição | Situação |
|---|---|---|---|---|
| A001 | MEDIUM | Consistência | `D-06` pede “todas as arestas de cada peça” mas não fixa o mecanismo; no Solid não há como desenhar aresta por peça sem escolher entre contorno global, wireframe ou geometria. A ação T010 fica dependente de uma decisão que o clarify não tomou | **Registrado** — T010 existe e está marcada bloqueada; pergunta 2 em `todo.md#Lacunas`. Não é defeito de cobertura |
| A002 | LOW | Consistência | `roadmap.md` D-05 cita `__init__.py:195` para `cabinet_color`; a linha real é **185** (a 195 é `door_window_color`). `hb_details.py` é citado como 98 na prosa do requirements e 99 no código (`color_type`) | **Corrigido no todo** — T002/T009 citam 185, 304 e 99 conferidos nesta árvore |
| A003 | LOW | Cobertura | “Cursos 3D” não existe em nenhuma string de `caffmob_draw/`; o plano o tratou como “não remover opções existentes”, mas isso é inferência | **Endereçado** — T001 é ação de confirmação na GUI, bloqueante de T009, sem código |
| A004 | LOW | Sanidade | T013 cita `blender_024_*` e T003/T004 citam `test_*_024.py`, arquivos que ainda não existem | **Esperado** — são as provas a criar; nenhum caminho de teste é reaproveitado por engano |

## Fechamento

### A001 — mecanismo de “Textura com linhas”

As três opções reais no Blender 5.2 são: `space.shading.show_object_outline` (contorno de todo objeto na viewport, não
por peça), wireframe por objeto (`show_wire`, mostra arestas e triangulação) ou geometria de contorno por peça (exato,
com custo de cena). O `todo.md` deixa T010 bloqueada e a pergunta escrita para o titular; **não escolhi por conta
própria**. RN-02 fica coberta por ação, mas o critério de pronto não fecha até a resposta.

### A002 — citações de linha

Conferidas no repositório: `cabinet_color` em `caffmob_draw/__init__.py:185`, desenho em `:304`,
`BTM_AddonPreferences` em `:146`; `color_type = 'OBJECT'` em `caffmob_draw/hb_details.py:99`; `_material` em
`build.py:309`, `materiais` em `:328`, `_uv_metros` em `:390-396`, `_material_da_peca` em `:608`; `_write`/`update` em
`edgeband/build.py:18/57`; `use_color` em `edgeband/props.py:44`; `_MODULES` em `armario_v2/__init__.py:30`. O
`todo.md` usa os valores corretos.

### A003 — “Cursos 3D”

`grep -rn "Cursos 3D" caffmob_draw` não encontra nada. A ação T001 resolve por confirmação visual antes de remover
qualquer controle, e mantém `cabinet_color` como propriedade legada — nenhuma opção é apagada sem confirmação.

### A004 — provas ainda inexistentes

Os arquivos de teste citados são entregas de T003/T004/T005/T006/T010/T011. Nenhuma ação reaproveita teste existente
como se já cobrisse a 024; os testes existentes aparecem só como regressão (`blender_017`, `blender_023_fase7`,
`blender_023_desempenho`, `test_i18n_coverage`, `check_api.py`).

## Critério de pronto vs. o que o to-do cobre

| Critério (`roadmap.md` §10) | Ações | Situação |
|---|---|---|
| Armário novo nasce texturizado; material do usuário vence | T004, T005 | coberto |
| Solid com `color_type = 'TEXTURE'`; mesmo material em Preview/render | T008, T005 | coberto |
| UV EXTERNA/INTERNA/FITA + fita com U/V próprios | T003, T006, T007 | coberto |
| “Somente textura” e “Textura com linhas” sem remover opções | T001, T009, T010 | coberto, **T010 bloqueada** (A001) |
| Migração única com aviso e `exibicao_versao` | T002, T011 | coberto |
| i18n e `check_api` | T012, T013 | coberto |
| Suítes verdes exceto ambiente-gated | T013, T014 | coberto |
| Aparência e contorno julgados na GUI | T015 | coberto, **requer sessão gráfica** |

## Itens verificados que passaram

### Cobertura
- RN-01 → T005/T008; RN-02 → T009/T010; RN-03 → T003/T006/T007; RN-04 → T002/T011. Nenhum requisito sem ação.
- As 7 decisões do roadmap têm ação: D-01→T004/T005; D-02→T008; D-03→T003/T007; D-04→T006; D-05→T001/T009;
  D-06→T010; D-07→T002/T011.

### Consistência
- As cinco decisões do clarify aparecem sem contradição: textura runtime (T004/T005), Solid `TEXTURE` (T008), três
  classes de face (T003), fita U/V (T006), `exibicao_armario` + `cabinet_color` legado (T009), migração idempotente
  (T002/T011).
- Nenhuma ação exige edição de produto fora de `caffmob_draw/`; `tests/` é superfície de ensaio já liberada pela
  config (`allowedPaths: tests/*`), e `_reversa_forward/` é a própria pasta do Reversa.

### Coerência com o legado
- `armario_v2` continua dono da geração; a fita continua objeto separado; o plano de corte não é tocado (textura não é
  produção).
- O padrão de `load_post` vem de `armario_v2/anim.py:400`, não de um handler novo inventado.

### Sanidade do actions
- Dependências apontam para IDs existentes; sem ciclo; T002 é a raiz da maior cadeia.
- T006 não compartilha arquivo com nenhuma ação paralela.

## Aviso

Este relatório não alterou `requirements.md`, `roadmap.md`, `todo.md`, `data-delta.md` nem `onboarding.md`. As
correções de citação foram feitas no próprio `todo.md` pelo ciclo `/reversa-to-do`, antes desta auditoria.
