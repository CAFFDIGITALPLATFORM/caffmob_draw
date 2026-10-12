<!-- GENERATED, DO NOT EDIT: regenerado por /reversa-debugger-graph em 2026-10-12T02:46:19+00:00 a partir de 6 bugs -->

# Grafo · editor-de-paredes

```mermaid
graph LR
  BUG_20261006_KFAR["#4 Erro ao salvar no Windows com o editor …"]
  BUG_20261007_A2G7["#6 Ajustar Piso ignora as paredes do edito…"]
  BUG_20261007_YIMY["#7 Porta e janela inseridas viram bloco li…"]
  BUG_20261007_ZZUK["#8 Ctrl+Z não desfaz dentro do editor de p…"]
  BUG_20261007_VQ72["#9 Trecho selecionado não mostra a medida …"]
  BUG_20261007_TBY3["#10 Todo objeto é tratado como parede (obje…"]
  BUG_20261006_KFAR -.->|caused-by| BUG_20261006_SCVF
  BUG_20261007_A2G7 -.->|related-to| BUG_20261007_YIMY
  BUG_20261007_TBY3 -->|related-to| BUG_20261007_A2G7
  BUG_20261007_ZZUK -.->|related-to| BUG_20261007_VQ72
  BUG_20261011_YAVM -.->|related-to| BUG_20261007_ZZUK
```

## Clusters

- `caffmob_draw/data/properties.py`: 2 bugs (BUG-20261007-A2G7, BUG-20261007-TBY3)
- `caffmob_draw/walls2d/apply.py`: 2 bugs (BUG-20261007-A2G7, BUG-20261007-YIMY)
- `caffmob_draw/walls2d/model.py`: 2 bugs (BUG-20261007-YIMY, BUG-20261007-ZZUK)
- `caffmob_draw/walls2d/ops_editor.py`: 2 bugs (BUG-20261007-ZZUK, BUG-20261007-VQ72)
- `caffmob_draw/walls2d/props.py`: 2 bugs (BUG-20261007-ZZUK, BUG-20261007-VQ72)

Leitura: 2 bugs convergem em `caffmob_draw/data/properties.py`, o maior ponto de convergência do contexto; vale corrigi-los numa mesma passada.

## Impact score

Heurística de triagem (não substitui priority/severity): só arestas supported/confirmed contam.

Todas as relações abertas estão como `proposed`: score 0 para todos.
