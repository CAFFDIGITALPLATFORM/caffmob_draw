# Reprodução de BUG-20261012-YUDY

- Commit: master em 2026-10-12
- Ambiente: Linux 6.8, Blender 5.2.0 LTS (`/opt/blender/blender`)

Sonda (Blender 5.2.0, `--background --factory-startup`): `caffmob.cabinet_builder` (balcão 600), `iter_modules`, seleção só do módulo, `bpy.ops.object.duplicate()`, `iter_modules` de novo.

```
PROBE1 uids dd2893129ba3 dd2893129ba3 ['dd2893129ba3', 'dd2893129ba3']
```
