# Cápsula de reprodução (lote 28)

- Commit base: HEAD antes do lote (master)
- Ambiente: Linux 6.8, Blender 5.2.0 LTS (`--background --factory-startup`, ou xvfb quando indicado)
- Testes: test_object_library.py, blender_bug_QZSO_object_library.py, blender_bug_W2DP_object_insert.py
- Taxa: 2/2 (cópia isolada e projeto) · Classificação: deterministic

## Saída antes da correção

```
test_object_library.py (exit 1):
FAILED (failures=1, errors=1)

blender_bug_QZSO_object_library.py (exit 1):
OK   item gravado []
FALHA QZSO: o pai não vai para o .blend ['Peça com pai', 'PaiX', 'Cube']
OK   QZSO: a raiz continua filha do pai na cena 
FALHA JKZJ: a textura própria chega empacotada [('madeira_qzso.001', False)]
blender_bug_QZSO_object_library: FALHAS: QZSO: o pai não vai para o .blend, JKZJ: a textura própria chega empacotada

blender_bug_W2DP_object_insert.py (exit 1):
OK   modal aberto pela barra lateral {'RUNNING_MODAL'}
FALHA W2DP: o objeto segue o mouse (0.0, 0.0, 0.0)
blender_bug_W2DP_object_insert: FALHAS: W2DP: o objeto segue o mouse
```
