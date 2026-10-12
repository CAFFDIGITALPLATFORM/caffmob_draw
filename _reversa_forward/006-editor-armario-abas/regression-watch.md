# Regression watch: 006-editor-armario-abas

> Gerado por `/reversa-coding` em 2026-10-08. Fonte: `legacy-impact.md` (seção "Modificadas": nenhuma regra 🟢 do
> `_reversa_sdd/domain.md` alterada ou removida).

| ID | Origem (arquivo, seção) | Regra esperada após mudança | Tipo de verificação | Sinal de violação |
|----|--------------------------|------------------------------|---------------------|-------------------|

Nenhum item com peso de regressão nesta rodada.

## Observações

Comportamentos novos ou alterados que **não** vinham como regra 🟢 do legado. Não contam como regressão, mas a próxima
extração deve encontrá-los:

- O módulo `btm` gera só as chapas presentes (`has_*`), com espessura por chapa; Reduzir o armário = Estender as
  vizinhas + medida externa menor e raiz deslocada (`cabinet_editor/structure.py`). 🟡
- A lista de peças do `btm` deixa de ser fixa: tira as chapas removidas e soma as divisões filhas
  (`cutting/part_sources.synthetic_records`). 🟡
- Material da chapa sobrescrito no armário (`btm_raw_material`) vence o material do Configurador no plano de corte
  (`cutting/part_extractor.record_to_part`). 🟡
- Divisão: chapa de vão inteiro no subvão escolhido, recuos na frente e atrás, subvão mínimo de 50 mm, material e
  espessura da Divisória do Configurador (`cabinet_editor/divisions.py`, `scene_divisions.py`). 🟡
- O face frame continua fora do plano de corte (lacuna herdada, `cutting/part_sources.iter_modules`). 🔴

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
