# Gate 1 · os testes falham antes da correção

Data: 2026-11-17. Testes de reprodução e regressão aplicados sem o change set de código.

```text
$ py -3 tests/test_walls2d_medir.py
Traceback (most recent call last):
  File ".../tests/test_walls2d_medir.py", line 12, in <module>
    from caffmob_draw.walls2d import medir
ImportError: cannot import name 'medir' from 'caffmob_draw.walls2d' (unknown location)
EXIT_PURO=1

$ blender --background --factory-startup --python-exit-code 1 --python tests/blender_bug_V4I3_medir.py
Traceback (most recent call last):
  File ".../tests/blender_bug_V4I3_medir.py", line 21, in <module>
    from caffmob_draw.walls2d import classico_v2, medir, model, ops_editor, props
ImportError: cannot import name 'medir' from 'caffmob_draw.walls2d'
Error: script failed, file: 'tests/blender_bug_V4I3_medir.py', exiting.
EXIT_BLENDER=1
```

Vermelho nas duas pernas: a ferramenta Medir não existia (módulo, estado, enum e captura).
