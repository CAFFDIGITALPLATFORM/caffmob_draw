# Reprodução de BUG-20261012-RCOU

- Commit: master em 2026-10-12
- Ambiente: Linux 6.8, Blender 5.2.0 LTS (`/opt/blender/blender`)

`cd tests && python3 -m unittest test_identity`:

```
FAIL: test_operadores_com_prefixo_caffmob (test_identity.IdentidadeTest)
AssertionError: Lists differ: ['caffmob_draw/openings/ops.py: btm.door_i[58 chars]dth'] != []
- ['caffmob_draw/openings/ops.py: btm.door_invert_hand',
-  'caffmob_draw/ui/ops_resize.py: btm.resize_width']
Ran 5 tests in 4.301s
FAILED (failures=1)
```
