<!-- GENERATED, DO NOT EDIT: regenerado por /reversa-debugger-graph em 2026-10-12T02:13:03+00:00 a partir de 8 bugs -->

# Grafo · stick

```mermaid
graph LR
  BUG_20261011_VVEJ["#51 Checagem de descendente em link.release…"]
  BUG_20261011_XPD2["#52 Vínculo de grudar órfão quando o pai é …"]
  BUG_20261011_XF4S["#53 Índice de hospedeiros desatualizado ao …"]
  BUG_20261011_73SM["#54 Item desgrudado de parede é regrudado n…"]
  BUG_20261011_EE4E["#55 Grudar disponível em tipos diferentes c…"]
  BUG_20261011_I3I3["#56 Orientação em relação à face perdida de…"]
  BUG_20261011_TNY3["#57 Erro silencioso em settle.run descarta …"]
  BUG_20261011_JKLK["#58 FACE_LABELS sem tradução"]
  BUG_20261011_DLHX -->|related-to| BUG_20261011_JKLK
  BUG_20261011_73SM -.->|related-to| BUG_20261011_XPD2
  BUG_20261011_JKLK -.->|related-to| BUG_20261011_35HE
  BUG_20261011_VVEJ -->|related-to| BUG_20261011_ZKQ7
```

## Clusters

- `caffmob_draw/stick/link.py`: 4 bugs (BUG-20261011-VVEJ, BUG-20261011-XPD2, BUG-20261011-XF4S, BUG-20261011-73SM)
- `caffmob_draw/stick/settle.py`: 2 bugs (BUG-20261011-73SM, BUG-20261011-TNY3)

Leitura: 4 bugs convergem em `caffmob_draw/stick/link.py`, o maior ponto de convergência do contexto; vale corrigi-los numa mesma passada.

## Impact score

Heurística de triagem (não substitui priority/severity): só arestas supported/confirmed contam.

Todas as relações abertas estão como `proposed`: score 0 para todos.
