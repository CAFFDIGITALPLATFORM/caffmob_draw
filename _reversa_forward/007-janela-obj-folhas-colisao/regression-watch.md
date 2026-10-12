# Regression watch: 007-janela-obj-folhas-colisao

> Gerado por `/reversa-coding` em 2026-10-08. Fonte: `legacy-impact.md` (seção "Modificadas": nenhuma regra 🟢 do
> `_reversa_sdd/domain.md` alterada ou removida).

| ID | Origem (arquivo, seção) | Regra esperada após mudança | Tipo de verificação | Sinal de violação |
|----|--------------------------|------------------------------|---------------------|-------------------|

Nenhum item com peso de regressão nesta rodada.

## Observações

Comportamentos novos ou alterados que não vinham como regra 🟢 do legado:

- 003 RN-11a ("fechar continua livre") vale só fora de esquadria. Com pai = grupo FRAME, fechar para na pose do
  arquivo, no montante da outra folha (`aggregates/slide_limits.close_stop`) ou no contato. 🟡
- Importação: unidade Automática (mais de 50 unidades = mm) e eixo vertical Z por padrão
  (`aggregates/ops_import.py`). 🟡
- Grupo de peças (Empty `btm_group`) como folha ou agregado; "Montar esquadria" por prefixo de nome. 🟡
- Janela importada instalada como jaula `IS_WINDOW_BP`, com a esquadria centrada por driver (`aggregates/install.py`). 🟡

## Histórico de re-extrações

### Re-extração 2026-10-10 18:26

| ID | Veredito | Observação |
|----|----------|------------|
| — | — | nenhum watch item na tabela principal; nada a verificar |

| Data | Resultado | Observação |
|------|-----------|------------|

## Arquivadas

| ID | Arquivada em | Motivo |
|----|--------------|--------|
