# Gate 2: verde depois da correção

Comandos (2026-11-18), exit 0 em todos:

```
py -3 tests/test_walls2d_tema.py                       -> Ran 13 tests ... OK
py -3 tests/test_i18n_coverage.py                      -> Ran 3 tests ... OK
py -3 tools/i18n_scan.py walls2d --faltando            -> 378 textos, 247 únicos; sem tradução: 0
blender --background ... tests/blender_bug_6
