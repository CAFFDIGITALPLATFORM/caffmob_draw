# Gate 2 · o teste passa depois do change set

Change set: `walls2d/painel_ui.py` (novo, CHG-002), operador em `ops_editor.py` (CHG-003), painéis em `panels.py`
(CHG-004) e na cena v2 em `classico_v2.py` (CHG-005).

## Teste do bug

```
blender_bug_RP9Q_paineis: OK
EXIT_TEST=0
```

Cobre: 7 botões `caffmob.wall_editor_tool` na ordem do enum, com os rótulos curtos, o ícone de cada item e
`depress` só no ativo; `magnetic` com `toggle=True` e ícone; operador gravando `state.tool` e recusando valor
inválido; a mesma grade no painel da cena v2; e os painéis Confirmar (OK/Cancelar), Painel (campos do trecho) e Grid
(tamanho, magnético, padrões de nova parede) intactos.

## Regressões e verificações

| Verificação | Exit | Saída |
|---|---|---|
| `tests/blender_002_smoke.py` | 0 | `blender_002_smoke: OK` |
| `tests/blender_065_walls2d_v2.py` | 0 | `OK Parede nova pertence ao pavimento ativo` |
| `tests/test_i18n_coverage.py` | 0 | `Ran 3 tests ... OK` |
| `py -3 docs/rag/tools/check_api.py` | 0 | `OK: no unknown API references found` (578 arquivos) |

## Limitações

- O teste valida as chamadas de layout, não o desenho na tela. A conferência visual do painel no Blender com
  interface (tamanho dos botões, truncamento de rótulo, tema) fica para o titular.
- `blender_002_ui_events` continua sem servir como prova em `--background`: o roteiro roda em `bpy.app.timers` e o
  Blender encerra antes do timer.
