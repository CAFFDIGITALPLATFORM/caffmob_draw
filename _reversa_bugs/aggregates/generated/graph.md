<!-- GENERATED, DO NOT EDIT: regenerado por /reversa-debugger-graph em 2026-11-24T06:45:20+00:00 a partir de 11 bugs -->

# Grafo · aggregates

```mermaid
graph LR
  BUG_20261011_DXOV["#14 Apagar parede com 'Apagar também os agre…"]
  BUG_20261011_ZKQ7["#32 Checagem de descendência invertida em ca…"]
  BUG_20261011_3VD7["#33 Geometria livre convertida em agregado s…"]
  BUG_20261011_WOPM["#34 Renomear agregado com furo real deixa fu…"]
  BUG_20261011_NQ2L["#35 Desconverter depois de mover o pai deixa…"]
  BUG_20261011_VPY5["#36 Exclusão de colisão larga demais em folh…"]
  BUG_20261011_I7QE["#37 Folha aberta fica fora do lugar depois d…"]
  BUG_20261011_PON4["#38 Caixa local errada quando o pai é Empty…"]
  BUG_20261011_4OV4["#39 install.install levanta TypeError numa e…"]
  BUG_20261011_MQPR["#40 Ícone do pivô não atualiza quando o movi…"]
  BUG_20261011_5DDZ["#41 Mensagem 'Converta a parede pelo editor…"]
  BUG_20261011_DXOV -->|related-to| BUG_20261011_TUWO
```

## Clusters

- `caffmob_draw/aggregates/convert.py`: 2 bugs (BUG-20261011-ZKQ7, BUG-20261011-NQ2L)
- `caffmob_draw/aggregates/leaf.py`: 2 bugs (BUG-20261011-I7QE, BUG-20261011-MQPR)
- `caffmob_draw/aggregates/ops_aggregate.py`: 2 bugs (BUG-20261011-DXOV, BUG-20261011-5DDZ)

Leitura: 2 bugs convergem em `caffmob_draw/aggregates/convert.py`, o maior ponto de convergência do contexto. Nenhum bug aberto neste contexto: o cluster mostra onde as correções se acumularam.

## Impact score

Heurística de triagem (não substitui priority/severity): causados ×3, bloqueados ×2, regressões ×4, relacionados ×1 (no máximo 3 no total), só arestas supported/confirmed.

| # | ID | score |
|---|---|---|
