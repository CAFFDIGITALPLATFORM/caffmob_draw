# Cápsula de reprodução (lote 33)

- Commit base: HEAD antes do lote (master)
- Ambiente: Linux 6.8, Blender 5.2.0 LTS (`--background --factory-startup`, ou xvfb quando indicado)
- Testes: blender_bug_PFY2_collision.py
- Taxa: 2/2 (cópia isolada e projeto) · Classificação: deterministic

## Saída antes da correção

```
blender_bug_PFY2_collision.py (exit 1):
OK   PFY2: sobreposição de 0.50 m com faces coplanares é colisão [('A', 'B')]
FALHA PFY2: sobreposição de 0.20 m com faces coplanares é colisão []
FALHA PFY2: sobreposição de 0.10 m com faces coplanares é colisão []
FALHA PFY2: sobreposição de 0.05 m com faces coplanares é colisão []
OK   PFY2: a 0.0 m (encostado ou afastado) não é colisão []
OK   PFY2: a 0.5 m (encostado ou afastado) não é colisão []
blender_bug_PFY2_collision: FALHAS: PFY2: sobreposição de 0.20 m com faces coplanares é colisão, PFY2: sobreposição de 0.10 m com faces coplanares é colisão, PFY2: sobreposição de 0.05 m com faces coplanares é colisão
```
