<!-- GENERATED, DO NOT EDIT: regenerado por /reversa-debugger-graph em 2026-10-12T03:59:30+00:00 a partir de 11 bugs -->

# Grafo · aggregates

```mermaid
graph LR
  BUG_20261011_DXOV["#14 Apagar parede com 'Apagar também os agr…"]
  BUG_20261011_ZKQ7["#32 Checagem de descendência invertida em c…"]
  BUG_20261011_3VD7["#33 Geometria livre convertida em agregado …"]
  BUG_20261011_WOPM["#34 Renomear agregado com furo real deixa f…"]
  BUG_20261011_NQ2L["#35 Desconverter depois de mover o pai deix…"]
  BUG_20261011_VPY5["#36 Exclusão de colisão larga demais em fol…"]
  BUG_20261011_I7QE["#37 Folha aberta fica fora do lugar depois …"]
  BUG_20261011_PON4["#38 Caixa local errada quando o pai é Empty…"]
  BUG_20261011_4OV4["#39 install.install levanta TypeError numa …"]
  BUG_20261011_MQPR["#40 Ícone do pivô não atualiza quando o mov…"]
  BUG_20261011_5DDZ["#41 Mensagem 'Converta a parede pelo editor…"]
  BUG_20261011_DXOV -->|related-to| BUG_20261011_TUWO
  BUG_20261011_53DV -.->|related-to| BUG_20261011_VPY5
  BUG_20261011_SKDL -->|related-to| BUG_20261011_3VD7
  BUG_20261011_VVEJ -->|related-to| BUG_20261011_ZKQ7
```

## Clusters

- `caffmob_draw/aggregates/ops_aggregate.py`: 2 bugs (BUG-20261011-DXOV, BUG-20261011-5DDZ)
- `caffmob_draw/aggregates/convert.py`: 2 bugs (BUG-20261011-ZKQ7, BUG-20261011-NQ2L)
- `caffmob_draw/aggregates/leaf.py`: 2 bugs (BUG-20261011-I7QE, BUG-20261011-MQPR)

Leitura: 2 bugs convergem em `caffmob_draw/aggregates/ops_aggregate.py`, o maior ponto de convergência do contexto; vale corrigi-los numa mesma passada.

## Impact score

Heurística de triagem (não substitui priority/severity): só arestas supported/confirmed contam.

Todas as relações abertas estão como `proposed`: score 0 para todos.
