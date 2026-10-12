<!-- GENERATED, DO NOT EDIT: regenerado por /reversa-debugger-graph em 2026-10-12T03:01:13+00:00 a partir de 8 bugs -->

# Grafo · standards

```mermaid
graph LR
  BUG_20261011_KVDM["#72 A Montagem se perde na ida e volta do .…"]
  BUG_20261011_ZK42["#73 validate dos padrões aceita NaN e inf"]
  BUG_20261011_3HN6["#74 Documento de padrões malformado quebra …"]
  BUG_20261011_MTPU["#75 Falha na migração de padrões interrompe…"]
  BUG_20261011_QO2H["#76 A segunda pergunta de Definir ativa rep…"]
  BUG_20261011_64UD["#77 Projeto só com face frame não ativa 'Pa…"]
  BUG_20261011_ZATR["#78 Import com 'replace' desloca a definiçã…"]
  BUG_20261011_EKM7["#79 Mensagens de validação dos padrões não …"]
  BUG_20261011_3HN6 -->|related-to| BUG_20261011_KVDM
  BUG_20261011_EKM7 -->|related-to| BUG_20261011_ZK42
```

## Clusters

- `caffmob_draw/standards/io_json.py`: 3 bugs (BUG-20261011-KVDM, BUG-20261011-3HN6, BUG-20261011-ZATR)
- `caffmob_draw/standards/model.py`: 3 bugs (BUG-20261011-KVDM, BUG-20261011-ZK42, BUG-20261011-EKM7)
- `caffmob_draw/operators/ops_standards.py`: 2 bugs (BUG-20261011-3HN6, BUG-20261011-QO2H)
- `caffmob_draw/standards/migration.py`: 2 bugs (BUG-20261011-MTPU, BUG-20261011-64UD)

Leitura: 3 bugs convergem em `caffmob_draw/standards/io_json.py`, o maior ponto de convergência do contexto; vale corrigi-los numa mesma passada.

## Impact score

Heurística de triagem (não substitui priority/severity): só arestas supported/confirmed contam.

Todas as relações abertas estão como `proposed`: score 0 para todos.
