# Regression watch — 004-editor-armario-grudar

> Criado por `/reversa-coding` em 2026-10-07 (rodada única, T001–T060).

| ID | Origem (arquivo, seção) | Regra esperada após mudança | Tipo de verificação | Sinal de violação |
|---|---|---|---|---|
| W001 | `caffmob_draw/product_libraries/frameless/operators/ops_placement.py` (posicionamento na parede, frente `y = 0`, trás `y = espessura` com giro de 180°) | O módulo posto na parede continua filho dela e passa a ter vínculo `btm_stick` na face `NEG_Y` (frente) ou `POS_Y` (trás); ao abrir arquivo antigo, o vínculo é criado sem mover o módulo | presença | Spec regenerada descreve o módulo de parede só como filho com Y local fixo, sem o vínculo à face |
| W002 | `_reversa_forward/002-editor-parede-mover-sobre/requirements.md#5` (RF-10) e `caffmob_draw/walls2d/apply.py` (filhos mantêm a posição local) | Mudar a espessura ou o comprimento da parede mantém os elementos filhos encostados na mesma face (≤ 0,1 mm); aberturas continuam recebendo a nova espessura | redação | Spec regenerada diz que só as aberturas acompanham a espessura, ou módulos de trás ficam dentro da parede |
| W003 | `_reversa_forward/003-modulos-agregados-reposicionar/requirements.md#5` (RF-12) | Apagar o pai continua perguntando sobre os agregados; elementos filhos grudados são soltos no mesmo lugar com o aviso "Vínculo perdido" | presença | Spec regenerada não menciona os elementos filhos, ou o item grudado some ou salta ao apagar o hospedeiro |
| W004 | `caffmob_draw/data/properties.py` (`BTM_PG_SceneSettings.collision_global`, "Evitar Sobreposição") | Além do posicionamento, a chave liga e desliga a verificação de colisão de corpo; `btm_plane.collision_override` (Herdar/Ativa/Desativada) passa a valer por item | redação | Spec regenerada diz que `collision_override` não é usado, ou que a chave só afeta o posicionamento |
| W005 | `caffmob_draw/inspection/interference.py` (`TOLERANCE = 0.001`) | A mesma tolerância de 1 mm separa encostar de colidir na colisão de corpo (`collision/rules.py`) | presença | As duas tolerâncias divergem, ou a spec trata encostar como colisão |
| W006 | `caffmob_draw/walls2d/window.py` (janela própria do editor de paredes, 002 T028) | A mecânica da janela 2D é comum (`canvas2d/window.py`) e serve ao Editor de Paredes e ao Editor de Armário, com a mesma API em `walls2d/window.py` | redação | Spec regenerada descreve a janela como exclusiva do editor de paredes, ou o editor de paredes deixa de abrir |
| W007 | `caffmob_draw/walls2d/history.py` (histórico do rascunho, BUG-20261007-ZZUK) | `History` aceita uma função de assinatura; o editor de paredes continua com `plan_signature` e o Ctrl+Z do rascunho igual | presença | Ctrl+Z dentro do editor de paredes deixa de desfazer passo a passo |
| W008 | `_reversa_forward/003-modulos-agregados-reposicionar/roadmap.md` (D-27) e `caffmob_draw/ui/save_feedback.py` | O aviso "Projeto salvo" inclui "N colisões pendentes" ou "Colisões não verificadas desde a última mudança" quando houver verificação; o salvar nunca é bloqueado | presença | Salvar com colisões é bloqueado, ou o aviso diz "sem colisões" com resultado desatualizado |

## Histórico de re-extrações

### Re-extração 2026-10-10 18:26

| ID | Veredito | Observação |
|----|----------|------------|
| W001 | 🟢 verde | preservada em `_reversa_sdd/stick/requirements.md` RN-20 |
| W002 | 🟢 verde | preservada em `_reversa_sdd/stick/requirements.md` RN-11/RN-12 e `walls2d/requirements.md` RN-20 (`Dim Y` = espessura); tolerância 0,1 mm não citada literalmente |
| W003 | 🟢 verde | preservada em `_reversa_sdd/aggregates/requirements.md` RN-29 e `aggregates/design.md` (`_release_stuck_children`) |
| W004 | 🟡 amarelo | chave global preservada (`collision/requirements.md` RN-10), mas RN-11 diz que só `OFF` age e `ON` equivale a `INHERIT`: equivalência parcial com "Herdar/Ativa/Desativada por item"; aguarda julgamento |
| W005 | 🟢 verde | preservada em `_reversa_sdd/collision/requirements.md` RN-01 e `inspection/design.md` (`TOLERANCE` 0,001 m, mesma de `collision/rules.py`) |
| W006 | 🟢 verde | preservada em `_reversa_sdd/canvas2d/requirements.md` (telas 2D dos editores de paredes e armários; RN-14 a RN-16) |
| W007 | 🟢 verde | preservada em `_reversa_sdd/walls2d/requirements.md` RN-11 e `walls2d/design.md` (`history.py`, assinatura injetável) |
| W008 | 🟢 verde | preservada em `_reversa_sdd/collision/requirements.md` RF-12/CA-23 (`_collision_note`); verificação é depois do fato, sem bloqueio |

<!-- Preenchido pelo agente reverso em cada `/reversa` futuro: data, veredito 🟢/🟡/🔴 por item. -->

## Arquivadas

<!-- Itens que deixaram de ser relevantes, com data e motivo. -->

## Observações

Itens sem peso de regressão (origem 🟡/🔴 ou decisão nova desta feature):

- Assentar por `Window.modal_operators`: ímã e verificação de colisão rodam quando nenhum movimento modal está ativo;
  o ímã gruda ao soltar, sem prévia durante o arraste (RF-12 parcial). 🟡
- Face `BOX_SIDE` com `u`/`v` medidos a partir da origem local do hospedeiro; troca para a face oposta quando o item
  vai parar além dela (editor de paredes invertendo a direção). 🟡
- Editor de Armário: edição ao vivo com instantâneos; Cancelar reaplica o inicial; Confirmar é um passo de desfazer
  (confirmado na fumaça T058 nas quatro bibliotecas). Era 🔴 no plano (D-22). 🟡
- Validação do editor: `DIM-001..003`, `GEO-001`, `GEO-002`, `CAT-001`, `LIB-001`; limites por biblioteca vindos do
  RNA das propriedades (`btm_cabinet` tem faixa; face frame e closets usam a geral). 🟡
- Biblioteca frameless: `change_opening_type` de `OPEN` para `DOUBLE_DOORS` deixa uma gaiola em arame `Doors.001`
  sobrando (comportamento anterior à feature; candidato a bug próprio). 🔴
