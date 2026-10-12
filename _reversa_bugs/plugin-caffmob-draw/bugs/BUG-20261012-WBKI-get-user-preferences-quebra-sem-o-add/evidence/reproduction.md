# Cápsula de reprodução (lote 36)

- Commit base: HEAD antes do lote (master)
- Ambiente: Linux 6.8, Blender 5.2.0 LTS (`--background --factory-startup`, ou xvfb quando indicado)
- Testes: blender_bug_WBKI_preferences.py
- Taxa: 2/2 (cópia isolada e projeto) · Classificação: deterministic

## Saída antes da correção

```
blender_bug_WBKI_preferences.py (exit 1):
OK   o pacote não está em preferences.addons (cenário do teste) 
FALHA WBKI: a cor dos armários vem do padrão KeyError('bpy_prop_collection[key]: key "caffmob_draw" not found')
FALHA WBKI: o destaque do armário funciona sem o add-on habilitado KeyError('bpy_prop_collection[key]: key "caffmob_draw" not found')
blender_bug_WBKI_preferences: FALHAS: WBKI: a cor dos armários vem do padrão, WBKI: o destaque do armário funciona sem o add-on habilitado
```
