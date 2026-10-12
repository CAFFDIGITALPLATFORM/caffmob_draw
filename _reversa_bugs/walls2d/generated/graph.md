<!-- GENERATED, DO NOT EDIT: regenerado por /reversa-debugger-graph em 2026-10-12T02:45:55+00:00 a partir de 8 bugs -->

# Grafo · walls2d

```mermaid
graph LR
  BUG_20261011_TLPN["#15 Remover Vértice deixa a parede antiga ó…"]
  BUG_20261011_GKUE["#16 Delete numa cadeia fechada não limpa a …"]
  BUG_20261011_YAVM["#17 Troca de Direção pelo painel se perde n…"]
  BUG_20261011_LT3C["#18 O 'Não' da pergunta de fechar a sala nã…"]
  BUG_20261011_624G["#19 Soltar o mouse na barra da lupa trava o…"]
  BUG_20261011_XMZM["#20 O segundo OK aplica sem rever os avisos…"]
  BUG_20261011_PJJU["#21 Ângulo editável com a trava de ângulo l…"]
  BUG_20261011_Z2BL["#22 Pé-direito gravado nas paredes sem vali…"]
  BUG_20261011_JMDR -->|related-to| BUG_20261011_XMZM
  BUG_20261011_GKUE -->|related-to| BUG_20261011_TLPN
  BUG_20261011_YAVM -.->|related-to| BUG_20261007_ZZUK
```

## Clusters

- `caffmob_draw/walls2d/ops_editor.py`: 5 bugs (BUG-20261011-TLPN, BUG-20261011-GKUE, BUG-20261011-LT3C, BUG-20261011-624G, BUG-20261011-XMZM)
- `caffmob_draw/walls2d/props.py`: 2 bugs (BUG-20261011-YAVM, BUG-20261011-XMZM)
- `caffmob_draw/walls2d/apply.py`: 2 bugs (BUG-20261011-LT3C, BUG-20261011-Z2BL)

Leitura: 5 bugs convergem em `caffmob_draw/walls2d/ops_editor.py`, o maior ponto de convergência do contexto; vale corrigi-los numa mesma passada.

## Impact score

Heurística de triagem (não substitui priority/severity): só arestas supported/confirmed contam.

Todas as relações abertas estão como `proposed`: score 0 para todos.
