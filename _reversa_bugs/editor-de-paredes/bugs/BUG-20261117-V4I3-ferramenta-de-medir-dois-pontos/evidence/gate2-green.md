# Gate 2 · os testes passam depois da correção

Data: 2026-11-17. Change set CHG-001 a CHG-008 aplicado.

```text
$ py -3 tests/test_walls2d_medir.py
Ran 9 tests in 0.001s
OK
MEDIR_PURO=0

$ blender --background --factory-startup --python-exit-code 1 --python tests/blender_bug_V4I3_medir.py
blender_bug_V4I3_medir: OK
MEDIR_BLENDER=0

$ py -3 tools/i18n_scan.py walls2d --faltando
354 textos, 239 únicos; sem tradução: 0; dinâmicos: 0
I18N_FALTANDO=0

$ py -3 tests/test_i18n_coverage.py
Ran 3 tests in 3.976s
OK
I18N_COVERAGE=0
```

Regressões (todas verdes):

```text
test_walls2d_model: OK          test_walls2d_convert: OK
test_walls2d_history: OK        test_walls2d_heights: OK
test_walls2d_selecao: OK        test_walls2d_studio: OK (exit 0)
test_walls2d_move: OK           test_walls2d_menu_contexto: OK
blender_bug_AKYJ_menu: OK (exit 0)
blender_002_ui_events: OK (exit 0)
REGRESSAO_PURA=0
```

O `test_i18n_coverage` estava vermelho antes por 10 rótulos da planta baixa (#148) ausentes do catálogo; as entradas
entraram no CHG-008 e o check passou a verde.
