# Cápsula de reprodução (lote 32)

- Commit base: HEAD antes do lote (master)
- Ambiente: Linux 6.8, Blender 5.2.0 LTS (`--background --factory-startup`, ou xvfb quando indicado)
- Testes: blender_bug_YUDY_module_uid.py
- Taxa: 2/2 (cópia isolada e projeto) · Classificação: deterministic

## Saída antes da correção

```
blender_bug_YUDY_module_uid.py (exit 1):
FALHA YUDY: os dois módulos têm uids diferentes {'BTM_Cabinet': '29985d6043e2', 'BTM_Cabinet.001': '29985d6043e2'}
FALHA YUDY: o original mantém o uid 29985d6043e2 → {'BTM_Cabinet': '29985d6043e2', 'BTM_Cabinet.001': '29985d6043e2'}
FALHA YUDY: nenhuma peça repete uid 14 peças, 7 uids
blender_bug_YUDY_module_uid: FALHAS: YUDY: os dois módulos têm uids diferentes, YUDY: o original mantém o uid, YUDY: nenhuma peça repete uid
```
