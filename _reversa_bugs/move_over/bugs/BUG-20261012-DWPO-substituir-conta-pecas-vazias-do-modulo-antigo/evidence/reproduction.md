# Cápsula de reprodução (lote 34)

- Commit base: HEAD antes do lote (master)
- Ambiente: Linux 6.8, Blender 5.2.0 LTS (`--background --factory-startup`, ou xvfb quando indicado)
- Testes: blender_bug_DWPO_substitute.py
- Taxa: 2/2 (cópia isolada e projeto) · Classificação: deterministic

## Saída antes da correção

```
blender_bug_DWPO_substitute.py (exit 1):
FALHA DWPO: a caixa do balcão não vai até a origem x 0.000 a 5.914
FALHA DWPO: o módulo novo encosta no mesmo canto do antigo antigo -5.000 novo 2.000
blender_bug_DWPO_substitute: FALHAS: DWPO: a caixa do balcão não vai até a origem, DWPO: o módulo novo encosta no mesmo canto do antigo
```
