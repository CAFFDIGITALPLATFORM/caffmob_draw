<!-- GENERATED, DO NOT EDIT: regenerado por /reversa-debugger-graph em 2026-11-24T16:57:54+00:00 a partir de 11 bugs -->

# Grafo · plugin-caffmob-draw

```mermaid
graph LR
  BUG_20261006_NO4Q["#1 Interface legada Home Builder aparece sep…"]
  BUG_20261006_QAVK["#2 Nome e identificador do plugin devem ser …"]
  BUG_20261006_SCVF["#3 Cópia antiga do plugin na raiz do reposit…"]
  BUG_20261007_FLZO["#11 Interface metade em português e metade em…"]
  BUG_20261012_RCOU["#139 test_identity falha: btm.door_invert_hand…"]
  BUG_20261012_WBKI["#142 get_user_preferences quebra sem o add-on …"]
  BUG_20261123_56YQ["#154 Arrastar o zip para o Blender 5.2 falha n…"]
  BUG_20261123_RW3G["#155 build.py empacota dotfiles e caches no zi…"]
  BUG_20261124_7K2M["#156 Contrato v2 não importa em Python 3.10 po…"]
  BUG_20261124_7H3K["#161 Ensaios de SHA256SUMS ordenam por Path e …"]
  BUG_20261124_Q2MF["#162 Ensaio do transporte por subprocesso usa …"]
  BUG_20261006_QAVK -->|related-to| BUG_20261006_NO4Q
  BUG_20261006_NO4Q -->|related-to| BUG_20261006_QAVK
  BUG_20261006_SCVF -.->|related-to| BUG_20261006_NO4Q
  BUG_20261006_NO4Q -.->|related-to| BUG_20261006_SCVF
  BUG_20261007_FLZO -.->|related-to| BUG_20261006_QAVK
  BUG_20261006_QAVK -.->|related-to| BUG_20261007_FLZO
  BUG_20261012_RCOU -.->|regression-of| BUG_20261006_NO4Q
  BUG_20261123_56YQ -.->|related-to| BUG_20261006_SCVF
  BUG_20261006_SCVF -.->|related-to| BUG_20261123_56YQ
  BUG_20261123_56YQ -->|related-to| BUG_20261123_RW3G
  BUG_20261123_RW3G -->|related-to| BUG_20261123_56YQ
```

## Clusters

- `build.py`: 3 bugs (BUG-20261006-QAVK, BUG-20261006-SCVF, BUG-20261123-RW3G)
- `blendertomob/__init__.py`: 2 bugs (BUG-20261006-NO4Q, BUG-20261006-QAVK)

## Impact score

Heurística de triagem (não substitui priority/severity): causados ×3, bloqueados ×2, regressões ×4, relacionados ×1 (no máximo 3 no total), só arestas supported/confirmed.

| # | ID | score |
|---|---|---|
| 1 | BUG-20261006-NO4Q | 1 |
| 2 | BUG-20261006-QAVK | 1 |
| 154 | BUG-20261123-56YQ | 1 |
| 155 | BUG-20261123-RW3G | 1 |
| 3 | BUG-20261006-SCVF | 0 |
| 11 | BUG-20261007-FLZO | 0 |
| 139 | BUG-20261012-RCOU | 0 |
| 142 | BUG-20261012-WBKI | 0 |
| 156 | BUG-20261124-7K2M | 0 |
| 161 | BUG-20261124-7H3K | 0 |
