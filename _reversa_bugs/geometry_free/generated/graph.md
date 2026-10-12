<!-- GENERATED, DO NOT EDIT: regenerado por /reversa-debugger-graph em 2026-10-12T02:21:02+00:00 a partir de 7 bugs -->

# Grafo · geometry_free

```mermaid
graph LR
  BUG_20261011_GUHQ["#112 Excluir geometria faz os filhos saltare…"]
  BUG_20261011_SKDL["#113 Shift+D nativo copia btm_uid"]
  BUG_20261011_L6YN["#116 Placa exportada com espessura errada"]
  BUG_20261011_ELOZ["#111 Duplicar ou espelhar geometria com pai …"]
  BUG_20261011_TLCT["#114 Interromper o modal de criar geometria …"]
  BUG_20261011_NOAU["#115 Medida digitada com arraste negativo de…"]
  BUG_20261011_DLHX["#117 Rótulos e nomes de chapas da geometria …"]
  BUG_20261011_DLHX -->|related-to| BUG_20261011_JKLK
  BUG_20261011_GUHQ -->|related-to| BUG_20261011_ELOZ
  BUG_20261011_GUHQ -->|related-to| BUG_20261011_7DHT
  BUG_20261011_SKDL -->|related-to| BUG_20261011_3VD7
  BUG_20261011_3T7M -->|related-to| BUG_20261011_TLCT
  BUG_20261011_JDYP -->|related-to| BUG_20261011_TLCT
```

## Clusters

- `caffmob_draw/geometry_free/ops_edit.py`: 2 bugs (BUG-20261011-GUHQ, BUG-20261011-ELOZ)
- `caffmob_draw/geometry_free/props.py`: 2 bugs (BUG-20261011-SKDL, BUG-20261011-DLHX)
- `caffmob_draw/geometry_free/mesh.py`: 2 bugs (BUG-20261011-L6YN, BUG-20261011-DLHX)
- `caffmob_draw/geometry_free/ops_create.py`: 2 bugs (BUG-20261011-TLCT, BUG-20261011-NOAU)

Leitura: 2 bugs convergem em `caffmob_draw/geometry_free/ops_edit.py`, o maior ponto de convergência do contexto; vale corrigi-los numa mesma passada.

## Impact score

Heurística de triagem (não substitui priority/severity): só arestas supported/confirmed contam.

Todas as relações abertas estão como `proposed`: score 0 para todos.
