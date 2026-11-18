<!-- GENERATED, DO NOT EDIT: regenerado por /reversa-debugger-graph em 2026-11-18T15:34:10+00:00 a partir de 7 bugs -->

# Grafo · openings

```mermaid
graph LR
  BUG_20261011_A2Z4["#118 Uma exceção em sync para o lote de abert…"]
  BUG_20261011_MMVI["#119 Reconstruir a porta apaga objetos do usu…"]
  BUG_20261011_IDPP["#120 Porta real não acompanha largura e altur…"]
  BUG_20261011_UV6S["#121 Trocar porta simples para dupla não refa…"]
  BUG_20261011_SX4T["#122 _swing pega o filho errado como símbolo…"]
  BUG_20261011_7SNG["#123 Porta inserida em região do lado de trás…"]
  BUG_20261011_D3GC["#124 draw_regions escreve dados durante o des…"]
  BUG_20261011_A2Z4 -->|related-to| BUG_20261011_MMVI
  BUG_20261011_MMVI -.->|related-to| BUG_20261011_A2Z4
  BUG_20261011_UV6S -->|related-to| BUG_20261011_IDPP
```

## Clusters

- `caffmob_draw/openings/sync.py`: 5 bugs (BUG-20261011-A2Z4, BUG-20261011-MMVI, BUG-20261011-IDPP, BUG-20261011-UV6S, BUG-20261011-SX4T)
- `caffmob_draw/openings/region.py`: 2 bugs (BUG-20261011-7SNG, BUG-20261011-D3GC)

Leitura: 5 bugs convergem em `caffmob_draw/openings/sync.py`, o maior ponto de convergência do contexto. Nenhum bug aberto neste contexto: o cluster mostra onde as correções se acumularam.

## Impact score

Heurística de triagem (não substitui priority/severity): causados ×3, bloqueados ×2, regressões ×4, relacionados ×1 (no máximo 3 no total), só arestas supported/confirmed.

| # | ID | score |
|---|---|---|
| 120 | BUG-20261011-IDPP | 1 |
| 119 | BUG-20261011-MMVI | 1 |
