<!-- GENERATED, DO NOT EDIT: regenerado por /reversa-debugger-graph em 2026-10-12T03:01:13+00:00 a partir de 13 bugs -->

# Grafo · cabinet_editor

```mermaid
graph LR
  BUG_20261011_6JIM["#59 Cancelar não desfaz a Montagem"]
  BUG_20261011_N2D4["#60 OK e Cancelar ignoram a fila pendente d…"]
  BUG_20261011_TRMB["#61 Sem rollback do editor de armário se a …"]
  BUG_20261011_5R7U["#62 Mudar o Número de vãos com s0 cortado p…"]
  BUG_20261011_FHQN["#63 Deslizantes usam o vão errado num armár…"]
  BUG_20261011_HF2J["#64 Recuo traseiro de 15 mm ignorado nas di…"]
  BUG_20261011_HVYM["#65 Forno e micro empilhados na ordem errada"]
  BUG_20261011_HR3U["#66 Item de catálogo aceito em qualquer aba…"]
  BUG_20261011_TFC7["#67 Eletro mais profundo que o vão não gera…"]
  BUG_20261011_E33D["#68 Erro da ação do editor de armário apaga…"]
  BUG_20261011_HLV6["#69 apply_state recria internos, extras e d…"]
  BUG_20261011_FGTR["#70 Mensagem enganosa de trilhos quando não…"]
  BUG_20261011_FYXD["#71 'Sem Divisória' num subvão de bay remov…"]
  BUG_20261011_6JIM -.->|related-to| BUG_20261011_N2D4
  BUG_20261011_N2D4 -->|related-to| BUG_20261011_6JIM
```

## Clusters

- `caffmob_draw/cabinet_editor/ops_editor.py`: 4 bugs (BUG-20261011-6JIM, BUG-20261011-N2D4, BUG-20261011-TRMB, BUG-20261011-E33D)
- `caffmob_draw/cabinet_editor/divisions.py`: 3 bugs (BUG-20261011-5R7U, BUG-20261011-HF2J, BUG-20261011-FYXD)
- `caffmob_draw/cabinet_editor/bays.py`: 2 bugs (BUG-20261011-5R7U, BUG-20261011-FYXD)
- `caffmob_draw/cabinet_editor/slides.py`: 2 bugs (BUG-20261011-FHQN, BUG-20261011-FGTR)
- `caffmob_draw/cabinet_editor/catalog.py`: 2 bugs (BUG-20261011-HF2J, BUG-20261011-HR3U)
- `caffmob_draw/cabinet_editor/appliances.py`: 2 bugs (BUG-20261011-HVYM, BUG-20261011-TFC7)
- `caffmob_draw/cabinet_editor/validate.py`: 2 bugs (BUG-20261011-HR3U, BUG-20261011-TFC7)

Leitura: 4 bugs convergem em `caffmob_draw/cabinet_editor/ops_editor.py`, o maior ponto de convergência do contexto; vale corrigi-los numa mesma passada.

## Impact score

Heurística de triagem (não substitui priority/severity): só arestas supported/confirmed contam.

Todas as relações abertas estão como `proposed`: score 0 para todos.
