<!-- GENERATED, DO NOT EDIT: regenerado por /reversa-debugger-graph em 2026-11-17T19:42:35+00:00 a partir de 15 bugs -->

# Grafo · editor-de-paredes

```mermaid
graph LR
  BUG_20261006_KFAR["#4 Erro ao salvar no Windows com o editor d…"]
  BUG_20261007_A2G7["#6 Ajustar Piso ignora as paredes do editor…"]
  BUG_20261007_YIMY["#7 Porta e janela inseridas viram bloco lis…"]
  BUG_20261007_ZZUK["#8 Ctrl+Z não desfaz dentro do editor de pa…"]
  BUG_20261007_VQ72["#9 Trecho selecionado não mostra a medida n…"]
  BUG_20261007_TBY3["#10 Todo objeto é tratado como parede (objec…"]
  BUG_20261117_6KBC["#144 Janela do editor mostra Editor de Imagen…"]
  BUG_20261117_AKYJ["#145 Falta menu de contexto na parede com tog…"]
  BUG_20261117_EELF["#146 Sem ferramenta Mover inline para desloca…"]
  BUG_20261117_6OXN["#147 Editor de parede só no tema escuro, sem…"]
  BUG_20261117_JXDJ["#148 Sem planta baixa dos objetos da cena com…"]
  BUG_20261117_744U["#149 Sem botão de imprimir a planta baixa"]
  BUG_20261117_V4I3["#150 Sem ferramenta de medir entre dois ponto…"]
  BUG_20261117_4MF7["#151 Sem coleção Arquitetura com subcoleção P…"]
  BUG_20261117_RP9Q["#152 Menu lateral de paredes com estilo antig…"]
  BUG_20261006_KFAR -->|caused-by| BUG_20261006_SCVF
  BUG_20261007_A2G7 -.->|related-to| BUG_20261007_YIMY
  BUG_20261007_ZZUK -.->|related-to| BUG_20261007_VQ72
  BUG_20261007_TBY3 -->|related-to| BUG_20261007_A2G7
  BUG_20261117_AKYJ -.->|related-to| BUG_20261117_EELF
  BUG_20261117_6OXN -.->|related-to| BUG_20261117_JXDJ
  BUG_20261117_744U -.->|blocked-by| BUG_20261117_JXDJ
  BUG_20261117_V4I3 -->|related-to| BUG_20261117_EELF
  BUG_20261117_4MF7 -.->|related-to| BUG_20261117_JXDJ
```

## Clusters

- `caffmob_draw/walls2d/ops_editor.py`: 9 bugs (BUG-20261007-ZZUK, BUG-20261007-VQ72, BUG-20261117-AKYJ, BUG-20261117-EELF, BUG-20261117-6OXN, BUG-20261117-JXDJ, BUG-20261117-744U, BUG-20261117-V4I3, BUG-20261117-4MF7)
- `caffmob_draw/walls2d/classico_v2.py`: 6 bugs (BUG-20261117-AKYJ, BUG-20261117-EELF, BUG-20261117-6OXN, BUG-20261117-JXDJ, BUG-20261117-V4I3, BUG-20261117-RP9Q)
- `caffmob_draw/walls2d/props.py`: 6 bugs (BUG-20261007-ZZUK, BUG-20261007-VQ72, BUG-20261117-AKYJ, BUG-20261117-EELF, BUG-20261117-6OXN, BUG-20261117-V4I3)
- `caffmob_draw/walls2d/panels.py`: 5 bugs (BUG-20261007-VQ72, BUG-20261117-AKYJ, BUG-20261117-EELF, BUG-20261117-V4I3, BUG-20261117-RP9Q)
- `caffmob_draw/walls2d/apply.py`: 3 bugs (BUG-20261007-A2G7, BUG-20261007-YIMY, BUG-20261117-4MF7)
- `caffmob_draw/walls2d/model.py`: 3 bugs (BUG-20261007-YIMY, BUG-20261007-ZZUK, BUG-20261117-EELF)
- `caffmob_draw/data/properties.py`: 2 bugs (BUG-20261007-A2G7, BUG-20261007-TBY3)
- `caffmob_draw/operators/layouts.py`: 2 bugs (BUG-20261117-JXDJ, BUG-20261117-744U)
- `caffmob_draw/ui/view3d_sidebar.py`: 2 bugs (BUG-20261117-JXDJ, BUG-20261117-744U)
- `caffmob_draw/walls2d/scene_io.py`: 2 bugs (BUG-20261007-TBY3, BUG-20261117-JXDJ)
- `caffmob_draw/walls2d/window.py`: 2 bugs (BUG-20261007-VQ72, BUG-20261117-6KBC)

Leitura: 9 bugs convergem em `caffmob_draw/walls2d/ops_editor.py`, o maior ponto de convergência do contexto. Dos 5 abertos, 3 apontam para esse arquivo.

## Impact score

Heurística de triagem (não substitui priority/severity): só arestas supported/confirmed contam.

| # | ID | score |
|---|---|---|
| 6 | BUG-20261007-A2G7 | 1 |
| 10 | BUG-20261007-TBY3 | 1 |
| 146 | BUG-20261117-EELF | 1 |
| 150 | BUG-20261117-V4I3 | 1 |
