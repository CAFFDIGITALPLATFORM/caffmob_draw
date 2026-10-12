<!-- GENERATED, DO NOT EDIT: regenerado por /reversa-debugger-graph em 2026-10-12T02:45:55+00:00 a partir de 4 bugs -->

# Grafo · plugin-caffmob-draw

```mermaid
graph LR
  BUG_20261006_NO4Q["#1 Interface legada Home Builder aparece s…"]
  BUG_20261006_QAVK["#2 Nome e identificador do plugin devem se…"]
  BUG_20261006_SCVF["#3 Cópia antiga do plugin na raiz do repos…"]
  BUG_20261007_FLZO["#11 Interface metade em português e metade …"]
  BUG_20261011_35HE -.->|related-to| BUG_20261007_FLZO
  BUG_20261006_KFAR -.->|caused-by| BUG_20261006_SCVF
  BUG_20261006_QAVK -->|related-to| BUG_20261006_NO4Q
  BUG_20261006_SCVF -.->|related-to| BUG_20261006_NO4Q
  BUG_20261007_FLZO -.->|related-to| BUG_20261006_QAVK
```

## Clusters

- `blendertomob/__init__.py`: 2 bugs (BUG-20261006-NO4Q, BUG-20261006-QAVK)
- `build.py`: 2 bugs (BUG-20261006-QAVK, BUG-20261006-SCVF)

Leitura: 2 bugs convergem em `blendertomob/__init__.py`, o maior ponto de convergência do contexto; vale corrigi-los numa mesma passada.

## Impact score

Heurística de triagem (não substitui priority/severity): só arestas supported/confirmed contam.

Todas as relações abertas estão como `proposed`: score 0 para todos.
