# Cápsula de reprodução (lote 20)

- Commit base: HEAD antes do lote (master)
- Ambiente: Linux 6.8, Blender 5.2.0 LTS (`--background --factory-startup`, ou xvfb quando indicado)
- Testes: blender_bug_UJ5Q_customize.py
- Taxa: 2/2 (cópia isolada e projeto) · Classificação: deterministic

## Saída antes da correção

```
blender_bug_UJ5Q_customize.py (exit 1):
FALHA UJ5Q: os vãos novos herdam material e puxador [] [('', ''), ('', ''), ('', '')]
OK   UJ5Q: o interior não passa para as gavetas 
FALHA XMUG: o painel oferece o estilo de gaveta [None, None, None]
FALHA MNX3: interior com valor não numérico é ignorado ValueError("invalid literal for int() with base 10: 'x'")
FALHA GL62: R gira também os outros objetos e o offset rot=0° pos=(2.0, 0.0, 0.0)
FALHA ODY2: interior inválido devolve CANCELLED {'FINISHED'}
blender_bug_UJ5Q_customize: FALHAS: UJ5Q: os vãos novos herdam material e puxador, XMUG: o painel oferece o estilo de gaveta, MNX3: interior com valor não numérico é ignorado, GL62: R gira também os outros objetos e o offset, ODY2: interior inválido devolve CANCELLED
```
