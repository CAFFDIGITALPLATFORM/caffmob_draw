# Cápsula de reprodução (lote 22)

- Commit base: HEAD antes do lote (master)
- Ambiente: Linux 6.8, Blender 5.2.0 LTS (`--background --factory-startup`, ou xvfb quando indicado)
- Testes: blender_bug_KX3O_collision.py, test_collision_rules.py
- Taxa: 2/2 (cópia isolada e projeto) · Classificação: deterministic

## Saída antes da correção

```
blender_bug_KX3O_collision.py (exit 1):
FALHA KX3O: Afastar move o selecionado (o segundo do par) primeiro andou 0.200 m
FALHA KX3O: com resultado desatualizado, recusa {'FINISHED'}
FALHA L5ML: grupo solto entra na colisão []
FALHA JUJZ: o painel do agregado edita o próprio agregado [('prop', 'BTM_Cabinet', 'collision_override')]
FALHA 7GRY: check_moved deixa a lista na ordem [('A', 0.2), ('C', 0.3)]
FALHA 7GRY: e limpa o erro antigo 'erro antigo'
FALHA EWKD: peça inteira dentro de outra é colisão []
FALHA ZEN6: as linhas de ocorrência ficam em alerta [('label', 'Colisão entre itens: A × B (200 mm)', False)]
blender_bug_KX3O_collision: FALHAS: KX3O: Afastar move o selecionado (o segundo do par), KX3O: com resultado desatualizado, recusa, L5ML: grupo solto entra na colisão, JUJZ: o painel do agregado edita o próprio agregado, 7GRY: check_moved deixa a lista na ordem, 7GRY: e limpa o erro antigo, EWKD: peça inteira dentro de outra é colisão, ZEN6: as linhas de ocorrência ficam em alerta

test_collision_rules.py (exit 1):
FAILED (failures=1)
```
