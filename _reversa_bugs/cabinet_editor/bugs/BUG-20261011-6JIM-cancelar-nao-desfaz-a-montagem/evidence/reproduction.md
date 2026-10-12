# Cápsula de reprodução (lote 12: fila do editor de armário)

- Commit base: 83a6863 + lotes 1 a 11 aplicados (master, não commitado)
- Ambiente: Linux 6.8, Blender 5.2.0 LTS, `--background --factory-startup`
- Comando: `/opt/blender/blender --background --factory-startup --python-exit-code 1 --python tests/blender_bug_6JIM_cabinet_queue.py`
- Exit code: 1 (antes) · Taxa: 2/2 · Classificação: deterministic

```
FALHA 6JIM: o painel não grava a Montagem direto [('prop', 'assembly')]
FALHA 6JIM: Cancelar desfaz a Montagem LATERAL → BASE → BASE
FALHA N2D4: o OK roda a fila antes de fechar largura 0.600 → 0.600
FALHA N2D4: o Cancelar descarta a fila [('dimension', ('width', 0.7))]
FALHA E33D: o erro da ação continua visível ''
```
