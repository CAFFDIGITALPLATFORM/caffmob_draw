<!-- GENERATED, DO NOT EDIT: regenerado por /reversa-debugger-graph em 2026-10-12T03:56:34+00:00 a partir de 5 bugs -->

# Grafo · legacy

```mermaid
graph LR
  BUG_20261011_5NLX["#80 Falha no meio do lote de conversão deix…"]
  BUG_20261011_NTM3["#81 Dupla contagem de frentes no face frame"]
  BUG_20261011_HUWF["#82 Relatório diz 'sem perdas' quando as fr…"]
  BUG_20261011_ORRG["#83 Grupo homônimo em outra pasta descartad…"]
  BUG_20261011_SWAD["#84 write_marker deixa .tmp para trás quand…"]
  BUG_20261011_SWAD -.->|related-to| BUG_20261011_OJBL
  BUG_20261011_5JLF -->|related-to| BUG_20261011_SWAD
```

## Clusters

- `caffmob_draw/legacy/convert.py`: 2 bugs (BUG-20261011-5NLX, BUG-20261011-HUWF)
- `caffmob_draw/legacy/convert_core.py`: 2 bugs (BUG-20261011-NTM3, BUG-20261011-HUWF)

Leitura: 2 bugs convergem em `caffmob_draw/legacy/convert.py`, o maior ponto de convergência do contexto; vale corrigi-los numa mesma passada.

## Impact score

Heurística de triagem (não substitui priority/severity): só arestas supported/confirmed contam.

Todas as relações abertas estão como `proposed`: score 0 para todos.
