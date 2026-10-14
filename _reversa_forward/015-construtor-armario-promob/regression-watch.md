# Regression watch: 015-construtor-armario-promob

> O que precisa continuar verdadeiro nas próximas extrações (`/reversa`). Gerado por `/reversa-coding` em 2026-10-14.

| ID | Origem (arquivo, seção) | Regra esperada após mudança | Tipo de verificação | Sinal de violação |
|----|-------------------------|-----------------------------|---------------------|-------------------|
| W001 | `_reversa_sdd/domain.md#cabinet_editor` (RN-CABINET_EDITOR-12) | N vãos: largura igual por padrão; largura digitada de um vão vale e os livres dividem o resto; o último vão é sempre calculado | redação | A re-extração descreve vãos sempre iguais, ou aceita digitar o último vão |
| W002 | `_reversa_sdd/domain.md#cabinet_editor` (RN-CABINET_EDITOR-15) | Sem estrutura, pés e rodapés abaixo da caixa; com estrutura, o rodapé fica dentro da altura total e levanta a caixa | redação | Regra única para os dois casos, ou altura total maior que a informada num "Armário" |
| W003 | `_reversa_sdd/domain.md#standards` (RN-STANDARDS-12) | Fundo FUN_INF em todos os tipos só nos módulos sem estrutura; com estrutura, FUN_INF/FUN_SUP/FUN_ALT pelo grupo | redação | Fundo de aéreo com estrutura sai como FUN_INF |
| W004 | `_reversa_sdd/domain.md#standards` (RN-STANDARDS-20) | O XML reexporta o `raw` e acrescenta no fim `CAFF_MONTAGEM`, `CAFF_GRUPO_*`, `CAFF_SARRAFO_*`, `CAFF_RECUO_PRAT_*` e `CAFF_CABIDEIRO_*`, sem duplicar na ida e volta | presença | Atributo `CAFF_*` duplicado ou perdido numa ida e volta |
| W005 | `_reversa_sdd/domain.md#library_panel` (RN-LIBRARY_PANEL-03) | Modelo pronto nasce com a estrutura de caixa dele ou a equivalente pela linha e pelo tipo | presença | Modelo inserido sem `structure_id` |
| W006 | `_reversa_forward/008-editor-armario-construtor/interfaces/cut-plan-json.md` | JSON de produção 2.3.0, com `modules[].structure_id` (null sem estrutura); leitores 2.x aceitam | presença | `schema_version` diferente de 2.3.0 sem novo contrato, ou `structure_id` ausente |
| W007 | `_reversa_sdd/domain.md#1.2 Entidades de Produção (Plano de Corte)` + RN-22 da 015 | Módulo sem `structure_id` gera exatamente os registros de antes da 015 (`tests/fixtures/cut_legacy_015.json`) | ausência | Mudança de nome, medida ou uid em módulo antigo sem o projetista abrir o editor ou reaplicar o padrão |
| W008 | `_reversa_sdd/domain.md#cabinet_editor` (RN-CABINET_EDITOR-01) | Cancelar devolve o módulo ao instantâneo inicial, inclusive estrutura de caixa e chapas presentes | presença | Cancelar num módulo antigo deixa `structure_id` preenchido ou a Base Superior ausente |

## Observações

Itens 🟡 sem peso de regressão, para conferir quando houver evidência melhor (Promob instalado ou decisão do titular):
- peças do Superior, Gaveteiro e Torre p/ Eletros (inferidas do nome, da biblioteca e do Configurador);
- fundos ENCAIXADO e REBAIXADO iguais; c/ Reb, Não Divide o Fundo e Montante só gravados;
- largura do sarrafo 100, rodapé 100/50, recuo da móvel 20, tubo 70 (padrões editáveis, Q5);
- gaveta "Interna p/ trilho" sem a de baixo mais alta; sapateira sem inclinação.

## Histórico de re-extrações

> Nenhuma re-extração registrada ainda.

## Arquivadas

> Nenhum item arquivado.
