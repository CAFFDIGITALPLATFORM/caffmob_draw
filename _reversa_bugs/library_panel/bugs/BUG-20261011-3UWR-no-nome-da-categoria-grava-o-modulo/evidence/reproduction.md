# Cápsula de reprodução (lote 27)

- Commit base: HEAD antes do lote (master)
- Ambiente: Linux 6.8, Blender 5.2.0 LTS (`--background --factory-startup`, ou xvfb quando indicado)
- Testes: test_library_categories.py, test_library_models.py, blender_bug_C7IK_library_panel.py
- Taxa: 2/2 (cópia isolada e projeto) · Classificação: deterministic

## Saída antes da correção

```
test_library_categories.py (exit 1):
FAILED (failures=2)

test_library_models.py (exit 1):
FAILED (failures=1, errors=1)

blender_bug_C7IK_library_panel.py (exit 1):
OK   C7IK: a categoria nova é criada None
FALHA C7IK: o arquivo inválido fica em categories.json.bak None
FALHA 3UWR: 'Pia: Lavabo' é recusada None
FALHA 3UWR: nenhuma pasta criada 
blender_bug_C7IK_library_panel: FALHAS: C7IK: o arquivo inválido fica em categories.json.bak, 3UWR: 'Pia: Lavabo' é recusada, 3UWR: nenhuma pasta criada
```
