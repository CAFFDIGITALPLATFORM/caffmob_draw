<!-- GENERATED, DO NOT EDIT: regenerado por /reversa-debugger-graph em 2026-11-24T06:45:20+00:00 a partir de 8 bugs -->

# Grafo · standards

```mermaid
graph LR
  BUG_20261011_KVDM["#72 A Montagem se perde na ida e volta do .b…"]
  BUG_20261011_ZK42["#73 validate dos padrões aceita NaN e inf"]
  BUG_20261011_3HN6["#74 Documento de padrões malformado quebra o…"]
  BUG_20261011_MTPU["#75 Falha na migração de padrões interrompe…"]
  BUG_20261011_QO2H["#76 A segunda pergunta de Definir ativa repe…"]
  BUG_20261011_64UD["#77 Projeto só com face frame não ativa 'Pad…"]
  BUG_20261011_ZATR["#78 Import com 'replace' desloca a definição…"]
  BUG_20261011_EKM7["#79 Mensagens de validação dos padrões não s…"]
  BUG_20261011_3HN6 -->|related-to| BUG_20261011_KVDM
  BUG_20261011_EKM7 -->|related-to| BUG_20261011_ZK42
```

## Clusters

- `caffmob_draw/standards/io_json.py`: 3 bugs (BUG-20261011-KVDM, BUG-20261011-3HN6, BUG-20261011-ZATR)
- `caffmob_draw/standards/model.py`: 3 bugs (BUG-20261011-KVDM, BUG-20261011-ZK42, BUG-20261011-EKM7)
- `caffmob_draw/operators/ops_standards.py`: 2 bugs (BUG-20261011-3HN6, BUG-20261011-QO2H)
- `caffmob_draw/standards/migration.py`: 2 bugs (BUG-20261011-MTPU, BUG-20261011-64UD)

Leitura: 3 bugs convergem em `caffmob_draw/standards/io_json.py`, o maior ponto de convergência do contexto. Nenhum bug aberto neste contexto: o cluster mostra onde as correções se acumularam.

## Impact score

Heurística de triagem (não substitui priority/severity): causados ×3, bloqueados ×2, regressões ×4, relacionados ×1 (no máximo 3 no total), só arestas supported/confirmed.

| # | ID | score |
|---|---|---|
| 72 | BUG-20261011-KVDM | 1 |
| 73 | BUG-20261011-ZK42 | 1 |
