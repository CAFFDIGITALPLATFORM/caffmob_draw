# Cápsula de reprodução (lote 26)

- Commit base: HEAD antes do lote (master)
- Ambiente: Linux 6.8, Blender 5.2.0 LTS (`--background --factory-startup`, ou xvfb quando indicado)
- Testes: blender_bug_5NLX_legacy.py
- Taxa: 2/2 (cópia isolada e projeto) · Classificação: deterministic

## Saída antes da correção

```
blender_bug_5NLX_legacy.py (exit 1):
Erro: Python: Traceback (most recent call last):
FALHA 5NLX: nada criado fica na cena ['BTM_Cabinet', 'BTM_Cabinet.001', 'BTM_Cabinet.001_Controller', 'BTM_Cabinet.001_Door_L', 'BTM_Cabinet.001_Door_R', 'BTM_Cabinet_Controller', 'BTM_Cabinet_Door_L', 'BTM_Cabinet_Door_R']
FALHA 5NLX: ERROR com o nome do armário 8, in failing
OK   5NLX: os herdados continuam 
FALHA NTM3: o basculante de puxar conta uma vez {'DRAWERS': 1, 'SPECIAL': 1}
FALHA HUWF: falha do leitor aparece como perda Balcao C (Frameless) → Módulo  ·  sem perdas
FALHA ORRG: o homônimo de outra pasta entra na lista [('Torre', '/tmp/tmp8avz0s3f/Torre.blend')]
blender_bug_5NLX_legacy: FALHAS: 5NLX: nada criado fica na cena, 5NLX: ERROR com o nome do armário, NTM3: o basculante de puxar conta uma vez, HUWF: falha do leitor aparece como perda, ORRG: o homônimo de outra pasta entra na lista
Traceback (most recent call last):
```
