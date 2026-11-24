# Cross-Check Audit: Frente do objeto no Mover Sobre

> Identificador: `022-mover-sobre-frente`
> Data: `2026-11-24`
> Artefatos analisados:
> - `_reversa_forward/022-mover-sobre-frente/requirements.md`
> - `_reversa_forward/022-mover-sobre-frente/roadmap.md`
> - `_reversa_forward/022-mover-sobre-frente/actions.md`
>
> **Nenhum dos três artefatos foi alterado por esta rodada.**

## Resumo

| Severidade | Quantidade |
|------------|------------|
| CRITICAL | 0 |
| HIGH | 0 |
| MEDIUM | 2 |
| LOW | 2 |

## Findings

| ID | Severidade | Eixo | Descrição | Onde está |
|----|------------|------|-----------|-----------|
| A001 | MEDIUM | Cobertura | O RNF de desempenho ("decisão em menos de 5 ms para 200 paredes") não tem ação, decisão nem ensaio correspondente; o orçamento de tempo só é citado no roadmap §8 como risco | `requirements.md` §6 × `actions.md` |
| A002 | MEDIUM | Sanidade do actions | T005 e T007 editam o mesmo arquivo (`ops_dialog.py`) na mesma fase; T007 está marcada `[//]` e só depende de T004, então pode ser iniciada em paralelo com T005 e colidir no arquivo | `actions.md` T005/T007 |
| A003 | LOW | Cobertura | As cinco lacunas `[DÚVIDA]` (D1–D5) estão abertas, como esperado antes do `/reversa-clarify`; o roadmap já fixa 100 mm e 45° como premissa, então a resposta do titular pode mudar `GAP_MAX`/`DISAGREE_MAX` e o texto de RN-01 | `requirements.md` §9 × `roadmap.md` §4 |
| A004 | LOW | Terminologia | RN-06 usa "lado de onde A chegou" e `RF-06` fala em "direção de onde A chegou"; o roadmap não define como essa direção é medida (arraste da sessão ou posição de A no momento da abertura) | `requirements.md` RN-06/RF-06, `roadmap.md` §3 |

## Itens verificados e aprovados

### Eixo 1 — Cobertura
- Todo RN (01–08) tem pelo menos um RF correspondente: RN-01→RF-01, RN-02→RF-02, RN-03→RF-03, RN-04→RF-04,
  RN-05→RF-05, RN-06→RF-06, RN-07→RF-07, RN-08→RF-08.
- Todo RF tem decisão no roadmap: RF-01/02→D-01+D-03, RF-03→D-02, RF-04→D-02+D-05 (remapeamento), RF-05→D-04,
  RF-06→D-01, RF-07→D-05, RF-08→D-05 (i18n no fechamento).
- Toda decisão tem ação: D-01→T001/T002, D-02→T004/T005, D-03→T008, D-04→T008/T009, D-05→T007.
- Os cenários Gherkin (módulo sem parede, importado com pergunta e persistência, parede sem pergunta, conflito com
  cancelamento, "Na frente" com base girada) estão cobertos por T002, T005, T006 e T012.

### Eixo 2 — Consistência
- Termos estáveis entre os três documentos: "frente", `btm_front_yaw`, `view_frame`, "parede atrás", "eixo do objeto".
- Todos os IDs citados (`RN-01`–`RN-08`, `RF-01`–`RF-08`, `D-01`–`D-05`, `T001`–`T012`) existem onde são definidos.
- `A002` da auditoria da 021 e `A009` da 017 são citados com o mesmo nome no cabeçalho do requirements.

### Eixo 3 — Coerência com o legado
- A decisão da 017 (`requirements.md:420`, `btm_front_yaw` válida para todo o add-on) é respeitada por RN-02 e D-03.
- RN-03 preserva o comportamento atual com `yaw = 0`, o que mantém `RN-STICK-*` e as posições salvas do Mover Sobre.
- Nenhuma regra 🟢 de `_reversa_sdd/domain.md` é contrariada; o bloco só orienta a janela, não regrava geometria.

### Eixo 4 — Sanidade do actions
- Dependências apontam só para IDs existentes; grafo acíclico (maior cadeia T001→T003→T005→T012, 5 nós contando T009).
- Nenhuma dupla de ações `[//]` compartilha arquivo alvo; A002 é o caso de uma `[//]` concorrendo com uma sequencial.

## Próximo passo sugerido

Sem CRITICAL nem HIGH: seguir para `/reversa-clarify` fechando D1–D5 (limite de proximidade, tolerância de desacordo,
forma da pergunta, alcance da propriedade e o caso B = parede sem arraste). A resposta de D3 decide entre D-04 e o menu
rápido; a de D1/D2 ajusta apenas as constantes do núcleo puro.
