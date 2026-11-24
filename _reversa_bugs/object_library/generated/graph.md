<!-- GENERATED, DO NOT EDIT: regenerado por /reversa-debugger-graph em 2026-11-24T06:45:20+00:00 a partir de 8 bugs -->

# Grafo · object_library

```mermaid
graph LR
  BUG_20261011_W2DP["#89 Objeto inserido pela barra lateral não s…"]
  BUG_20261011_KKHH["#90 Manifesto com tipo inesperado derruba a…"]
  BUG_20261011_QZSO["#91 O pai da raiz é salvo junto no .blend do…"]
  BUG_20261011_JKZJ["#92 Texturas próprias não são empacotadas ao…"]
  BUG_20261011_QP4R["#93 Malhas e materiais inseridos somem ao re…"]
  BUG_20261011_JDYP["#94 cancel() da inserção não remove os objet…"]
  BUG_20261011_5JLF["#95 item_io.save deixa .json temporário quan…"]
  BUG_20261011_EVT6["#96 item_id com quebra de linha final é acei…"]
  BUG_20261011_JDYP -->|related-to| BUG_20261011_TLCT
  BUG_20261011_5JLF -->|related-to| BUG_20261011_SWAD
```

## Clusters

- `caffmob_draw/object_library/item_io.py`: 4 bugs (BUG-20261011-QZSO, BUG-20261011-JKZJ, BUG-20261011-QP4R, BUG-20261011-5JLF)
- `caffmob_draw/object_library/ops.py`: 3 bugs (BUG-20261011-W2DP, BUG-20261011-QP4R, BUG-20261011-JDYP)

Leitura: 4 bugs convergem em `caffmob_draw/object_library/item_io.py`, o maior ponto de convergência do contexto. Nenhum bug aberto neste contexto: o cluster mostra onde as correções se acumularam.

## Impact score

Heurística de triagem (não substitui priority/severity): causados ×3, bloqueados ×2, regressões ×4, relacionados ×1 (no máximo 3 no total), só arestas supported/confirmed.

| # | ID | score |
|---|---|---|
