<!-- GENERATED, DO NOT EDIT: regenerado por /reversa-debugger-graph em 2026-10-12T02:54:38+00:00 a partir de 3 bugs -->

# Grafo · selection

```mermaid
graph LR
  BUG_20261011_7DHT["#12 X/Delete numa parede faz os filhos não …"]
  BUG_20261011_TUWO["#13 Apagar parede sem 'Apagar também os agr…"]
  BUG_20261011_CHWX["#125 Redimensionar janela BTM sempre falha c…"]
  BUG_20261011_DXOV -->|related-to| BUG_20261011_TUWO
  BUG_20261011_GUHQ -->|related-to| BUG_20261011_7DHT
  BUG_20261011_7DHT -->|related-to| BUG_20261011_TUWO
```

## Clusters

- `caffmob_draw/selection/component.py`: 2 bugs (BUG-20261011-7DHT, BUG-20261011-TUWO)
- `caffmob_draw/aggregates/ops_aggregate.py`: 2 bugs (BUG-20261011-7DHT, BUG-20261011-TUWO)

Leitura: 2 bugs convergem em `caffmob_draw/selection/component.py`, o maior ponto de convergência do contexto; vale corrigi-los numa mesma passada.

## Impact score

Heurística de triagem (não substitui priority/severity): só arestas supported/confirmed contam.

Todas as relações abertas estão como `proposed`: score 0 para todos.
