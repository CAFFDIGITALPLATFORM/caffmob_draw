<!-- GENERATED, DO NOT EDIT: regenerado por /reversa-debugger-graph em 2026-10-12T03:56:34+00:00 a partir de 5 bugs -->

# Grafo · molding

```mermaid
graph LR
  BUG_20261011_VHMP["#106 Remover dado que não é Curve aborta a r…"]
  BUG_20261011_XP5E["#107 Apagar o 1º armário da corrida faz o sw…"]
  BUG_20261011_QT2G["#108 Falha no meio de apply_scene_packages d…"]
  BUG_20261011_MWN5["#109 _spawn_sweep deixa dados de curva órfãos"]
  BUG_20261011_ARCH["#110 Perfil oculto acumula quando o sweep é …"]
  BUG_20261011_QT2G -->|related-to| BUG_20261011_VHMP
```

## Clusters

- `caffmob_draw/molding/ops.py`: 5 bugs (BUG-20261011-VHMP, BUG-20261011-XP5E, BUG-20261011-QT2G, BUG-20261011-MWN5, BUG-20261011-ARCH)

Leitura: 5 bugs convergem em `caffmob_draw/molding/ops.py`, o maior ponto de convergência do contexto; vale corrigi-los numa mesma passada.

## Impact score

Heurística de triagem (não substitui priority/severity): só arestas supported/confirmed contam.

Todas as relações abertas estão como `proposed`: score 0 para todos.
