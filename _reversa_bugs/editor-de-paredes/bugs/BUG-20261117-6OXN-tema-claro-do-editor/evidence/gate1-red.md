# Gate 1: vermelho antes da correção

Comandos (2026-11-18):

```
py -3 tests/test_walls2d_tema.py
"/c/Program Files/Blender Foundation/Blender 5.2/blender.exe" --background --factory-startup --python-exit-code 1 --python tests/blender_bug_6OXN_tema.py
```

Saída:

```
ImportError: cannot import name 'tema' from 'caffmob_draw.walls2d' (tests/test_walls2d_tema.py:16)
ImportError: cannot import name 'tema' from 'caffmob_draw.walls2d' (tests/blender_bug_6OXN_tema.py:25)
Error: script failed, file: 'tests/blender_bug_6OXN_tema.py', exiting.
```

Exit 1 nos dois. O módulo de tema não existia e o estado do editor não tinha a propriedade `tema`; a primeira asserção do
teste do Blender (`'tema' in state.bl_rna.properties`) é a que falharia com o módulo presente.
