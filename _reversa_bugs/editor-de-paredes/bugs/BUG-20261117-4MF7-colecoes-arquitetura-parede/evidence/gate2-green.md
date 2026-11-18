# Gate 2 · o teste passa depois do change set

Change set aplicado: `caffmob_draw/walls2d/layers.py` (novo, CHG-002) e o gancho em `apply_plan`
(`caffmob_draw/walls2d/apply.py`, CHG-003).

## Teste do bug

```bash
"/c/Program Files/Blender Foundation/Blender 5.2/blender.exe" --background --factory-startup \
  --python-exit-code 1 --python tests/blender_bug_4MF7_colecoes.py
```

```
blender_bug_4MF7_colecoes: OK
EXIT_TEST=0
```

Cobre: hierarquia criada no OK, paredes dentro de `Arquitetura > Parede`, coleção existente reaproveitada (mesma
coleção, marcador próprio preservado, sem nome duplicado), parede que estava em outra coleção migrada no OK seguinte,
móvel e empty `obj_x` intactos, `read_plan` lendo as mesmas paredes e OK vazio sem coleção órfã.

## Regressões

```bash
B="/c/Program Files/Blender Foundation/Blender 5.2/blender.exe"
for t in blender_002_smoke blender_002_ui_events blender_065_walls2d_v2; do
  "$B" --background --factory-startup --python-exit-code 1 --python "tests/$t.py"
done
```

| Teste | Exit | Saída |
|---|---|---|
| `blender_002_smoke.py` | 0 | `blender_002_smoke: OK` |
| `blender_002_ui_events.py` | 0 | sem saída: o roteiro vive num `bpy.app.timers` e o Blender em `--background` encerra antes do timer. Execução **vazia**, não serve como prova. |
| `blender_065_walls2d_v2.py` | 0 | `OK Parede nova pertence ao pavimento ativo` (entre outras linhas OK) |

## Compatibilidade de API

```bash
py -3 docs/rag/tools/check_api.py
```

```
Scanned 577 files against 24382 Blender 5.2 symbols.
OK: no unknown API references found.
```

## Limitações

- Desfazer depois do OK não foi exercitado: `--background` não empilha passos de operador. A criação da coleção e os
  vínculos acontecem dentro do modal com `bl_options = {'UNDO'}`, então devem voltar no mesmo passo, mas isso pede
  conferência manual com interface.
- O teste não abre o Outliner nem confere a árvore visualmente; valida a estrutura de dados das coleções.
