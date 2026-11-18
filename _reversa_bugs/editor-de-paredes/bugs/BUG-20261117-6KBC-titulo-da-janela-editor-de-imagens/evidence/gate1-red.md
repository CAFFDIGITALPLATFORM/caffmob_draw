# Gate 1 · vermelho

Comando (antes do change set, sem `ops_editor.TITULO`):

```
"/c/Program Files/Blender Foundation/Blender 5.2/blender.exe" --background --factory-startup \
  --python-exit-code 1 --python tests/blender_bug_6KBC_titulo.py
```

Saída (exit 1):

```
    assert hasattr(ops_editor, "TITULO"), "ops_editor sem TITULO: a barra não mostra o nome do editor"
           ~~~~~~~^^^^^^^^^^^^^^^^^^^^^
AssertionError: ops_editor sem TITULO: a barra não mostra o nome do editor
Error: script failed, file: 'tests/blender_bug_6KBC_titulo.py', exiting.
```

A barra superior não tinha nenhuma chamada de desenho com o nome do editor: o teste falha na primeira perna
(a constante) e falharia também na segunda (nenhum texto desenhado).
