<!-- GENERATED, DO NOT EDIT: regenerado por /reversa-debugger-graph em 2026-10-12T02:01:54+00:00 a partir de 8 bugs -->

# Grafo · object_library

```mermaid
graph LR
  BUG_20261011_W2DP["#89 Objeto inserido pela barra lateral não …"]
  BUG_20261011_KKHH["#90 Manifesto com tipo inesperado derruba a…"]
  BUG_20261011_QZSO["#91 O pai da raiz é salvo junto no .blend d…"]
  BUG_20261011_JKZJ["#92 Texturas próprias não são empacotadas a…"]
  BUG_20261011_QP4R["#93 Malhas e materiais inseridos somem ao r…"]
  BUG_20261011_JDYP["#94 cancel() da inserção não remove os obje…"]
  BUG_20261011_5JLF["#95 item_io.save deixa .json temporário qua…"]
  BUG_20261011_EVT6["#96 item_id com quebra de linha final é ace…"]
  BUG_20261011_5JLF -->|related-to| BUG_20261011_SWAD
  BUG_20261011_JDYP -->|related-to| BUG_20261011_TLCT
```

## Clusters

- `caffmob_draw/object_library/item_io.py`: 4 bugs (BUG-20261011-QZSO, BUG-20261011-JKZJ, BUG-20261011-QP4R, BUG-20261011-5JLF)
- `caffmob_draw/object_library/ops.py`: 3 bugs (BUG-20261011-W2DP, BUG-20261011-QP4R, BUG-20261011-JDYP)

Leitura: 4 bugs convergem em `caffmob_draw/object_library/item_io.py`, o maior ponto de convergência do contexto; vale corrigi-los numa mesma passada.

## Impact score

Heurística de triagem (não substitui priority/severity): só arestas supported/confirmed contam.

Todas as relações abertas estão como `proposed`: score 0 para todos.
