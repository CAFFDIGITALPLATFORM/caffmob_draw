<!-- GENERATED, DO NOT EDIT: regenerado por /reversa-debugger-graph em 2026-10-12T02:16:58+00:00 a partir de 6 bugs -->

# Grafo · move_over

```mermaid
graph LR
  BUG_20261011_CKVJ["#126 Tab na janela de Mover Sobre vai para o…"]
  BUG_20261011_JMDR["#127 O segundo Confirmar salva sem rever a s…"]
  BUG_20261011_LWF6["#128 Alinhamento e sobreposição usam só a ca…"]
  BUG_20261011_X5OS["#129 O Substituir herda a escala do módulo a…"]
  BUG_20261011_3T7M["#130 Interromper os modais de Mover na Pared…"]
  BUG_20261011_CNTL["#137 Rotação inválida mostra o erro cru do f…"]
  BUG_20261011_3T7M -->|related-to| BUG_20261011_TLCT
  BUG_20261011_JMDR -->|related-to| BUG_20261011_XMZM
```

## Clusters

- `caffmob_draw/move_over/ops_dialog.py`: 3 bugs (BUG-20261011-CKVJ, BUG-20261011-JMDR, BUG-20261011-CNTL)

Leitura: 3 bugs convergem em `caffmob_draw/move_over/ops_dialog.py`, o maior ponto de convergência do contexto; vale corrigi-los numa mesma passada.

## Impact score

Heurística de triagem (não substitui priority/severity): só arestas supported/confirmed contam.

Todas as relações abertas estão como `proposed`: score 0 para todos.
