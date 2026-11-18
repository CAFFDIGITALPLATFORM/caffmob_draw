# Gate 1 · o teste falha antes do change set

Arquivo: `tests/blender_bug_RP9Q_paineis.py` (novo, CHG-001).

```bash
"/c/Program Files/Blender Foundation/Blender 5.2/blender.exe" --background --factory-startup \
  --python-exit-code 1 --python tests/blender_bug_RP9Q_paineis.py
```

```
Traceback (most recent call last):
  File "tests/blender_bug_RP9Q_paineis.py", line 82, in <module>
    assert len(botoes(r)) == len(FERRAMENTAS), \
AssertionError: REPRODUÇÃO (#152): painel sem botões de ferramenta (0)

Error: script failed, file: 'tests/blender_bug_RP9Q_paineis.py', exiting.
EXIT=1
```

O teste desenha o painel Ferramentas num `UILayout` de mentira, que grava as chamadas de `operator`/`prop` (mesmo
padrão de `tests/blender_065_walls2d_selecao.py`). Antes da correção, nenhum botão `caffmob.wall_editor_tool` é
desenhado, e `magnetic` sai sem `toggle=True`.
