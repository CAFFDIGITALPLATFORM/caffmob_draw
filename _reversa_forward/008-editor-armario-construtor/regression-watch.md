# Regression watch: 008-editor-armario-construtor

> Gerado por `/reversa-coding` em 2026-10-08. Fonte: `legacy-impact.md` (seção "Modificadas": nenhuma regra 🟢 do
> `_reversa_sdd/domain.md` alterada ou removida).

| ID | Origem (arquivo, seção) | Regra esperada após mudança | Tipo de verificação | Sinal de violação |
|----|--------------------------|------------------------------|---------------------|-------------------|

Nenhum item com peso de regressão nesta rodada.

## Observações

Comportamentos novos ou alterados que não vinham como regra 🟢 do legado:

- **JSON de produção 2.2.0** (`cutting/json_exporter.py`):
  - `hardware[]` ordenado por módulo e código;
  - `parts[].drilling` com `SHELF_PIN_LINE` (37 mm da frente e de trás, passo 32);
  - o leitor aceita 2.0 a 2.2.

  Contrato: `interfaces/cut-plan-json.md`. Substitui o 2.1.0 da 003. 🟢
- **Uid das peças do `btm`** (`cutting/part_sources.synthetic_records`): peças sintéticas e reais numeradas juntas
  por componente, com as sintéticas primeiro. Uma re-extração não deve voltar a aceitar uids repetidos. 🟢
- **Aplicar** (`cabinet_editor/ops_editor._apply_now`): um passo de desfazer na cena, e o estado aplicado vira a
  referência do Cancelar. OK = aplicar e fechar. 🟢
- **Aba Acabamento da 006 removida:** Materiais foi para Estrutura, Interior da biblioteca para Divisões, e frente,
  estilo e puxador para as abas Gavetas e Portas. 🟡
- **Distanciador** (`cabinet_editor/divisions.resolve`): ocupa a faixa sem criar subvãos, e o vão fica com o lado
  maior. 🟡
- **"Inserir automaticamente" (D-11, com desvio):** reafirma o recuo depois de reconstruções, mas não devolve um fundo
  removido pelo projetista (`customize/reapply.after_rebuild`). 🟡
- **Ferragens** (`cutting/hardware.collect`): `btm_hardware` conta 1 cada; cada frente de gaveta conta 1 par de
  corrediça (Blum quando o vão tem `slide_kind` BLUM). O face frame fica fora, uma lacuna herdada. 🟡
- **Furação** (`cutting/drilling.scene_drilling`): a peça vizinha é achada pela caixa no referencial da raiz (folga de
  2 mm). A face TOP/BOTTOM vem da normal +Z local da peça. 🟡

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
