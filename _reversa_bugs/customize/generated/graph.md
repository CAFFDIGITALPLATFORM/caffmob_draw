<!-- GENERATED, DO NOT EDIT: regenerado por /reversa-debugger-graph em 2026-11-18T15:34:10+00:00 a partir de 9 bugs -->

# Grafo · customize

```mermaid
graph LR
  BUG_20261011_J2NY["#23 Inserir um .blend sem .json quebra a ins…"]
  BUG_20261011_MRZC["#24 Estilos válidos do closets aparecem como…"]
  BUG_20261011_UJ5Q["#25 Trocar para 2 a 4 gavetas no frameless p…"]
  BUG_20261011_XMUG["#26 Estilo de gaveta não é editável pelo pai…"]
  BUG_20261011_MNX3["#27 Interior com valor não numérico quebra o…"]
  BUG_20261011_OJBL["#28 Gravação da biblioteca própria não é atô…"]
  BUG_20261011_GL62["#29 R na inserção gira só a raiz do módulo"]
  BUG_20261011_ODY2["#30 set_interior inválido devolve FINISHED e…"]
  BUG_20261011_35HE["#31 Textos em português no en_US (customize)"]
  BUG_20261011_MRZC -->|related-to| BUG_20261011_J2NY
  BUG_20261011_35HE -.->|related-to| BUG_20261007_FLZO
```

## Clusters

- `caffmob_draw/customize/library_io.py`: 3 bugs (BUG-20261011-J2NY, BUG-20261011-MRZC, BUG-20261011-OJBL)
- `caffmob_draw/customize/ops_library.py`: 3 bugs (BUG-20261011-J2NY, BUG-20261011-GL62, BUG-20261011-35HE)
- `caffmob_draw/customize/ops_customize.py`: 2 bugs (BUG-20261011-ODY2, BUG-20261011-35HE)
- `caffmob_draw/customize/panels.py`: 2 bugs (BUG-20261011-XMUG, BUG-20261011-MNX3)
- `caffmob_draw/customize/reapply.py`: 2 bugs (BUG-20261011-UJ5Q, BUG-20261011-MNX3)

Leitura: 3 bugs convergem em `caffmob_draw/customize/library_io.py`, o maior ponto de convergência do contexto. Nenhum bug aberto neste contexto: o cluster mostra onde as correções se acumularam.

## Impact score

Heurística de triagem (não substitui priority/severity): causados ×3, bloqueados ×2, regressões ×4, relacionados ×1 (no máximo 3 no total), só arestas supported/confirmed.

| # | ID | score |
|---|---|---|
| 23 | BUG-20261011-J2NY | 1 |
