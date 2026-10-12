# Cápsula de reprodução (lote 15: gizmo de inspeção)

- Commit base: 83a6863 + lotes 1 a 14 aplicados (master, não commitado)
- Ambiente: Linux 6.8, Blender 5.2.0 LTS, `--background --factory-startup`
- Comando: `/opt/blender/blender --background --factory-startup --python-exit-code 1 --python tests/blender_bug_5EX7_gizmo.py`
- Exit code: 1 (antes) · Taxa: 2/2 · Classificação: deterministic

```
FALHA 5EX7: folha de correr convertida tem curso e o gizmo lê AttributeError("'AggregateLeafFront' object has no attribute 'travel'")
FALHA GBPG: o dial vai até o máximo da folha 90.0°
FALHA PGMI: o valor pendente é gravado na frente de antes 0.0°
```
