<!-- GENERATED, DO NOT EDIT: regenerado por /reversa-debugger-graph em 2026-11-24T06:45:20+00:00 a partir de 7 bugs -->

# Grafo · move_over

```mermaid
graph LR
  BUG_20261011_CKVJ["#126 Tab na janela de Mover Sobre vai para o…"]
  BUG_20261011_JMDR["#127 O segundo Confirmar salva sem rever a so…"]
  BUG_20261011_LWF6["#128 Alinhamento e sobreposição usam só a cai…"]
  BUG_20261011_X5OS["#129 O Substituir herda a escala do módulo an…"]
  BUG_20261011_3T7M["#130 Interromper os modais de Mover na Parede…"]
  BUG_20261011_CNTL["#137 Rotação inválida mostra o erro cru do fl…"]
  BUG_20261012_DWPO["#141 Substituir conta peças vazias do módulo…"]
  BUG_20261011_JMDR -->|related-to| BUG_20261011_XMZM
  BUG_20261011_3T7M -->|related-to| BUG_20261011_TLCT
  BUG_20261012_DWPO -.->|related-to| BUG_20261011_LWF6
```

## Clusters

- `caffmob_draw/move_over/ops_dialog.py`: 3 bugs (BUG-20261011-CKVJ, BUG-20261011-JMDR, BUG-20261011-CNTL)
- `caffmob_draw/move_over/ops_substitute.py`: 2 bugs (BUG-20261011-X5OS, BUG-20261012-DWPO)
- `caffmob_draw/move_over/scene.py`: 2 bugs (BUG-20261011-LWF6, BUG-20261012-DWPO)

Leitura: 3 bugs convergem em `caffmob_draw/move_over/ops_dialog.py`, o maior ponto de convergência do contexto. Nenhum bug aberto neste contexto: o cluster mostra onde as correções se acumularam.

## Impact score

Heurística de triagem (não substitui priority/severity): causados ×3, bloqueados ×2, regressões ×4, relacionados ×1 (no máximo 3 no total), só arestas supported/confirmed.

| # | ID | score |
|---|---|---|
