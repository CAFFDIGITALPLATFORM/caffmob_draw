# Reprodução · BUG-20261117-V4I3

- **Data:** 2026-11-17
- **Commit base:** `88c63c7e` (working tree com as correções não commitadas de #145, #146, #148)
- **Ambiente:** Windows 11, Blender 5.2.0 LTS (`fbe6228777e7`), Python 3 do host para os testes puros
- **Classificação:** determinística, 1/1
- **Pedido do titular:** `_reversa_bugs/editor-de-paredes/intake/relato-20261117-1430.md` (Problema 7) — tocar num ponto,
  tocar noutro e ver a distância entre eles.

## Comandos

```text
py -3 tests/test_walls2d_medir.py
"/c/Program Files/Blender Foundation/Blender 5.2/blender.exe" --background --factory-startup \
  --python-exit-code 1 --python tests/blender_bug_V4I3_medir.py
```

## Saída antes da correção

```text
ImportError: cannot import name 'medir' from 'caffmob_draw.walls2d'      (teste puro)
ImportError: cannot import name 'medir' from 'caffmob_draw.walls2d'      (Blender, exit 1)
```

Sem o módulo, nem a ferramenta nem o ímã existem. A lista de ferramentas do editor (`props.py`) tinha apenas `SELECT`,
`DRAW`, `INVERT`, `MOVE`, `ADD_NODE` e `REMOVE_NODE`; o modal despachava só essas, e `classico_v2.tratar` só conhecia
`DRAW`, `SELECT`, `INVERT`, `MOVE`, `ADD_NODE` e `REMOVE_NODE`. Nenhum caminho guardava um primeiro ponto.
