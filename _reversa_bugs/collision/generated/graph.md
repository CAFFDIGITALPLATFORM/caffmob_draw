<!-- GENERATED, DO NOT EDIT: regenerado por /reversa-debugger-graph em 2026-11-18T15:34:10+00:00 a partir de 10 bugs -->

# Grafo · collision

```mermaid
graph LR
  BUG_20261011_SRPV["#42 Tolerância de 1,0 mm instável por arredo…"]
  BUG_20261011_KX3O["#43 Afastar move o item errado e aceita resu…"]
  BUG_20261011_TIPN["#44 Resultado da colisão não fica desatualiz…"]
  BUG_20261011_L5ML["#45 Grupos soltos (SketchUp, biblioteca de o…"]
  BUG_20261011_JUJZ["#46 Override de colisão no painel de agregad…"]
  BUG_20261011_7GRY["#47 check_moved deixa a lista desordenada e…"]
  BUG_20261011_53DV["#48 Colisão falsa entre folha e caixa da por…"]
  BUG_20261011_EWKD["#49 Contenção total em objeto fino pode pass…"]
  BUG_20261011_ZEN6["#50 Só o cabeçalho fica vermelho no painel d…"]
  BUG_20261012_PFY2["#140 Malhas sobrepostas com faces coplanares…"]
  BUG_20261011_53DV -.->|related-to| BUG_20261011_VPY5
  BUG_20261012_PFY2 -.->|related-to| BUG_20261011_EWKD
```

## Clusters

- `caffmob_draw/collision/ops_collision.py`: 3 bugs (BUG-20261011-KX3O, BUG-20261011-TIPN, BUG-20261011-7GRY)
- `caffmob_draw/collision/obb.py`: 2 bugs (BUG-20261011-SRPV, BUG-20261011-EWKD)
- `caffmob_draw/collision/panels.py`: 2 bugs (BUG-20261011-JUJZ, BUG-20261011-ZEN6)
- `caffmob_draw/collision/rules.py`: 2 bugs (BUG-20261011-SRPV, BUG-20261011-53DV)
- `caffmob_draw/collision/scan.py`: 2 bugs (BUG-20261011-L5ML, BUG-20261012-PFY2)

Leitura: 3 bugs convergem em `caffmob_draw/collision/ops_collision.py`, o maior ponto de convergência do contexto. Nenhum bug aberto neste contexto: o cluster mostra onde as correções se acumularam.

## Impact score

Heurística de triagem (não substitui priority/severity): causados ×3, bloqueados ×2, regressões ×4, relacionados ×1 (no máximo 3 no total), só arestas supported/confirmed.

| # | ID | score |
|---|---|---|
