<!-- GENERATED, DO NOT EDIT: regenerado por /reversa-debugger-graph em 2026-11-18T15:34:10+00:00 a partir de 6 bugs -->

# Grafo · plugin-caffmob-draw

```mermaid
graph LR
  BUG_20261006_NO4Q["#1 Interface legada Home Builder aparece se…"]
  BUG_20261006_QAVK["#2 Nome e identificador do plugin devem ser…"]
  BUG_20261006_SCVF["#3 Cópia antiga do plugin na raiz do reposi…"]
  BUG_20261007_FLZO["#11 Interface metade em português e metade e…"]
  BUG_20261012_RCOU["#139 test_identity falha: btm.door_invert_han…"]
  BUG_20261012_WBKI["#142 get_user_preferences quebra sem o add-on…"]
  BUG_20261006_QAVK -->|related-to| BUG_20261006_NO4Q
  BUG_20261006_SCVF -.->|related-to| BUG_20261006_NO4Q
  BUG_20261007_FLZO -.->|related-to| BUG_20261006_QAVK
  BUG_20261012_RCOU -.->|regression-of| BUG_20261006_NO4Q
```

## Clusters

- `blendertomob/__init__.py`: 2 bugs (BUG-20261006-NO4Q, BUG-20261006-QAVK)
- `build.py`: 2 bugs (BUG-20261006-QAVK, BUG-20261006-SCVF)

Leitura: 2 bugs convergem em `blendertomob/__init__.py`, o maior ponto de convergência do contexto. Nenhum bug aberto neste contexto: o cluster mostra onde as correções se acumularam.

## Impact score

Heurística de triagem (não substitui priority/severity): causados ×3, bloqueados ×2, regressões ×4, relacionados ×1 (no máximo 3 no total), só arestas supported/confirmed.

| # | ID | score |
|---|---|---|
| 1 | BUG-20261006-NO4Q | 1 |
