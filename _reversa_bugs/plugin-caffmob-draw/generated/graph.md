<!-- GENERATED, DO NOT EDIT: regenerado por /reversa-debugger-graph em 2026-11-24T06:45:20+00:00 a partir de 9 bugs -->

# Grafo · plugin-caffmob-draw

```mermaid
graph LR
  BUG_20261006_NO4Q["#1 Interface legada Home Builder aparece se…"]
  BUG_20261006_QAVK["#2 Nome e identificador do plugin devem ser…"]
  BUG_20261006_SCVF["#3 Cópia antiga do plugin na raiz do reposi…"]
  BUG_20261007_FLZO["#11 Interface metade em português e metade e…"]
  BUG_20261012_RCOU["#139 test_identity falha: btm.door_invert_han…"]
  BUG_20261012_WBKI["#142 get_user_preferences quebra sem o add-on…"]
  BUG_20261123_56YQ["#154 Arrastar o zip para o Blender 5.2 falha…"]
  BUG_20261123_RW3G["#155 build.py empacota dotfiles e caches no z…"]
  BUG_20261124_7K2M["#156 Contrato v2 não importa em Python 3.10 p…"]
  BUG_20261006_QAVK -->|related-to| BUG_20261006_NO4Q
  BUG_20261006_SCVF -.->|related-to| BUG_20261006_NO4Q
  BUG_20261007_FLZO -.->|related-to| BUG_20261006_QAVK
  BUG_20261012_RCOU -.->|regression-of| BUG_20261006_NO4Q
  BUG_20261123_56YQ -.->|related-to| BUG_20261006_SCVF
  BUG_20261123_56YQ -->|related-to| BUG_20261123_RW3G
  BUG_20261123_RW3G -->|related-to| BUG_20261123_56YQ
```

## Clusters

- `build.py`: 3 bugs (BUG-20261006-QAVK, BUG-20261006-SCVF, BUG-20261123-RW3G)
- `blendertomob/__init__.py`: 2 bugs (BUG-20261006-NO4Q, BUG-20261006-QAVK)

Leitura: 3 bugs convergem em `build.py`, o maior ponto de convergência do contexto. Dos 1 abertos, 0 apontam para esse arquivo.

## Impact score

Heurística de triagem (não substitui priority/severity): causados ×3, bloqueados ×2, regressões ×4, relacionados ×1 (no máximo 3 no total), só arestas supported/confirmed.

| # | ID | score |
|---|---|---|
| 1 | BUG-20261006-NO4Q | 1 |
| 154 | BUG-20261123-56YQ | 1 |
| 155 | BUG-20261123-RW3G | 1 |
