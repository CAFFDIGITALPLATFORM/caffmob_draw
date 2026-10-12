# Cápsula de reprodução (lote 5: uid e espessura na produção)

- Commit base: 83a6863 + lotes 1 a 4 aplicados (master, não commitado)
- Ambiente: Linux 6.8, Blender 5.2.0 LTS, `--background --factory-startup`
- Comando: `/opt/blender/blender --background --factory-startup --python-exit-code 1 --python tests/blender_bug_3VD7_production_uid.py`
- Exit code: 1 (antes) · Taxa: 2/2 (cópia isolada e projeto) · Classificação: deterministic

```
FALHA 3VD7: geometria convertida em agregado sai uma vez ['855caed637c3/ESP/0', '855caed637c3/ESP/0']
FALHA 3VD7: o JSON global valida ['parts[1].uid: duplicado (855caed637c3/ESP/0)']
FALHA SKDL: cópia nativa não repete o uid ['1daf769804e9/ESP/0', '1daf769804e9/ESP/0']
FALHA SKDL: o JSON global valida ['parts[1].uid: duplicado (1daf769804e9/ESP/0)']
FALHA L6YN: a espessura da placa é sempre thickness [('Placa', 0.6, 0.018, 0.01)]
FALHA L6YN: o painel sabe avisar a medida menor que a espessura
```

Achado lateral (fora deste lote): Shift+D num módulo também repete o `btm_uid` (`['890593a1451c', '890593a1451c']`).
