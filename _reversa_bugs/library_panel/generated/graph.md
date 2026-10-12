<!-- GENERATED, DO NOT EDIT: regenerado por /reversa-debugger-graph em 2026-10-12T04:02:39+00:00 a partir de 4 bugs -->

# Grafo · library_panel

```mermaid
graph LR
  BUG_20261011_3UWR["#85 ':' no nome da categoria grava o módulo…"]
  BUG_20261011_C7IK["#86 categories.json inválido é sobrescrito …"]
  BUG_20261011_2HDG["#87 Valor não numérico quebra o popover da …"]
  BUG_20261011_NCPI["#88 null no JSON da biblioteca vira o texto…"]
```

## Clusters

- `caffmob_draw/library_panel/categories_core.py`: 2 bugs (BUG-20261011-3UWR, BUG-20261011-NCPI)
- `caffmob_draw/library_panel/models_core.py`: 2 bugs (BUG-20261011-2HDG, BUG-20261011-NCPI)

Leitura: 2 bugs convergem em `caffmob_draw/library_panel/categories_core.py`, o maior ponto de convergência do contexto; vale corrigi-los numa mesma passada.

## Impact score

Heurística de triagem (não substitui priority/severity): só arestas supported/confirmed contam.

Todas as relações abertas estão como `proposed`: score 0 para todos.
