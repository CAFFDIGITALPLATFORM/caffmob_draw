# Gate 2 · verde

Depois do change set (CHG-002 e CHG-003):

```
blender --background --factory-startup --python-exit-code 1 --python tests/blender_bug_6KBC_titulo.py
blender_bug_6KBC_titulo: OK          (exit 0)
```

Regressões, mesma execução em sequência:

| teste | exit | observação |
|---|---|---|
| `tests/blender_002_smoke.py` | 0 | precisa do stub `_handle_menu` (CHG-004); falhava antes da correção por falta do método no `SimpleNamespace`, não por causa do título |
| `tests/blender_002_ui_events.py` | 0 | eventos da barra superior e do modal |
| `tests/blender_007_window_smoke.py` | 0 | abrir/fechar a janela do editor e devolver a área 3D |

Tradução e cobertura:

```
py -3 tools/i18n_scan.py walls2d --faltando   -> 355 textos, 240 únicos; sem tradução: 0; dinâmicos: 0
py -3 tests/test_i18n_coverage.py             -> Ran 3 tests ... OK (exit 0)
```

O aviso `ValueError: The "package" does not name an extension` no smoke vem do caminho de dados do usuário em
`--background` (pré-existente, não interrompe o teste).
