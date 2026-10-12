<!-- GENERATED, DO NOT EDIT: regenerado por /reversa-debugger-graph em 2026-10-12T02:39:10+00:00 a partir de 9 bugs -->

# Grafo · collision

```mermaid
graph LR
  BUG_20261011_SRPV["#42 Tolerância de 1,0 mm instável por arred…"]
  BUG_20261011_KX3O["#43 Afastar move o item errado e aceita res…"]
  BUG_20261011_TIPN["#44 Resultado da colisão não fica desatuali…"]
  BUG_20261011_L5ML["#45 Grupos soltos (SketchUp, biblioteca de …"]
  BUG_20261011_JUJZ["#46 Override de colisão no painel de agrega…"]
  BUG_20261011_7GRY["#47 check_moved deixa a lista desordenada e…"]
  BUG_20261011_53DV["#48 Colisão falsa entre folha e caixa da po…"]
  BUG_20261011_EWKD["#49 Contenção total em objeto fino pode pas…"]
  BUG_20261011_ZEN6["#50 Só o cabeçalho fica vermelho no painel …"]
  BUG_20261011_53DV -.->|related-to| BUG_20261011_VPY5
  BUG_20261011_FVQI -->|related-to| BUG_20261011_TIPN
```

## Clusters

- `caffmob_draw/collision/ops_collision.py`: 3 bugs (BUG-20261011-KX3O, BUG-20261011-TIPN, BUG-20261011-7GRY)
- `caffmob_draw/collision/rules.py`: 2 bugs (BUG-20261011-SRPV, BUG-20261011-53DV)
- `caffmob_draw/collision/obb.py`: 2 bugs (BUG-20261011-SRPV, BUG-20261011-EWKD)
- `caffmob_draw/collision/panels.py`: 2 bugs (BUG-20261011-JUJZ, BUG-20261011-ZEN6)

Leitura: 3 bugs convergem em `caffmob_draw/collision/ops_collision.py`, o maior ponto de convergência do contexto; vale corrigi-los numa mesma passada.

## Impact score

Heurística de triagem (não substitui priority/severity): só arestas supported/confirmed contam.

Todas as relações abertas estão como `proposed`: score 0 para todos.
