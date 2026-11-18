<!-- GENERATED, DO NOT EDIT: regenerado por /reversa-debugger-graph em 2026-11-18T15:34:10+00:00 a partir de 8 bugs -->

# Grafo · stick

```mermaid
graph LR
  BUG_20261011_VVEJ["#51 Checagem de descendente em link.release…"]
  BUG_20261011_XPD2["#52 Vínculo de grudar órfão quando o pai é t…"]
  BUG_20261011_XF4S["#53 Índice de hospedeiros desatualizado ao a…"]
  BUG_20261011_73SM["#54 Item desgrudado de parede é regrudado na…"]
  BUG_20261011_EE4E["#55 Grudar disponível em tipos diferentes co…"]
  BUG_20261011_I3I3["#56 Orientação em relação à face perdida dep…"]
  BUG_20261011_TNY3["#57 Erro silencioso em settle.run descarta o…"]
  BUG_20261011_JKLK["#58 FACE_LABELS sem tradução"]
  BUG_20261011_VVEJ -->|related-to| BUG_20261011_ZKQ7
  BUG_20261011_73SM -.->|related-to| BUG_20261011_XPD2
  BUG_20261011_JKLK -.->|related-to| BUG_20261011_35HE
```

## Clusters

- `caffmob_draw/stick/link.py`: 4 bugs (BUG-20261011-VVEJ, BUG-20261011-XPD2, BUG-20261011-XF4S, BUG-20261011-73SM)
- `caffmob_draw/stick/settle.py`: 2 bugs (BUG-20261011-73SM, BUG-20261011-TNY3)

Leitura: 4 bugs convergem em `caffmob_draw/stick/link.py`, o maior ponto de convergência do contexto. Nenhum bug aberto neste contexto: o cluster mostra onde as correções se acumularam.

## Impact score

Heurística de triagem (não substitui priority/severity): causados ×3, bloqueados ×2, regressões ×4, relacionados ×1 (no máximo 3 no total), só arestas supported/confirmed.

| # | ID | score |
|---|---|---|
