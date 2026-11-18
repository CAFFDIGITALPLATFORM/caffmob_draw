<!-- GENERATED, DO NOT EDIT: regenerado por /reversa-debugger-graph em 2026-11-18T15:34:10+00:00 a partir de 9 bugs -->

# Grafo · inspection

```mermaid
graph LR
  BUG_20261011_5EX7["#97 Gizmo quebra numa folha de correr conver…"]
  BUG_20261011_GBPG["#98 Dial do gizmo tem teto fixo de 90°"]
  BUG_20261011_B5JP["#99 Salvar durante a animação grava estado i…"]
  BUG_20261011_PGMI["#100 Valor pendente do gizmo descartado sem c…"]
  BUG_20261011_NWRA["#101 Desligar o addon com a inspeção ativa de…"]
  BUG_20261011_FVQI["#102 Interferência desatualizada sem aviso"]
  BUG_20261011_UURX["#103 depth_test_set('NONE') não é restaurado…"]
  BUG_20261011_6AX3["#104 Contagem errada na mensagem de abrir fre…"]
  BUG_20261011_B54S["#105 default_angle não é usado pelo 'Abrir tu…"]
  BUG_20261011_PGMI -.->|related-to| BUG_20261011_B5JP
  BUG_20261011_FVQI -->|related-to| BUG_20261011_TIPN
```

## Clusters

- `caffmob_draw/inspection/gizmo.py`: 3 bugs (BUG-20261011-5EX7, BUG-20261011-GBPG, BUG-20261011-PGMI)
- `caffmob_draw/inspection/fronts.py`: 2 bugs (BUG-20261011-6AX3, BUG-20261011-B54S)

Leitura: 3 bugs convergem em `caffmob_draw/inspection/gizmo.py`, o maior ponto de convergência do contexto. Nenhum bug aberto neste contexto: o cluster mostra onde as correções se acumularam.

## Impact score

Heurística de triagem (não substitui priority/severity): causados ×3, bloqueados ×2, regressões ×4, relacionados ×1 (no máximo 3 no total), só arestas supported/confirmed.

| # | ID | score |
|---|---|---|
