# Cápsula de reprodução (lote 7: molduras)

- Commit base: 83a6863 + lotes 1 a 6 aplicados (master, não commitado)
- Ambiente: Linux 6.8, Blender 5.2.0 LTS, `--background --factory-startup`
- Comando: `/opt/blender/blender --background --factory-startup --python-exit-code 1 --python tests/blender_bug_VHMP_molding.py`
- Exit code: 1 (antes) · Taxa: 2/2 (cópia isolada e projeto) · Classificação: deterministic

```
FALHA VHMP: sweep convertido em malha não aborta a reconstrução TypeError('BlendDataCurves.remove(): ... expected a Curve type, not Mesh')
FALHA XP5E: apagar o 1º armário deixa a moldura
FALHA QT2G: falha no meio mantém as molduras de antes 1 → 1, mesmos: False
FALHA MWN5: sweep descartado não deixa curva órfã 4 → 6
FALHA ARCH: perfil do sweep apagado à mão não acumula 2 perfis, 1 sweeps
```

Sonda extra (#107): pelo Delete nativo ou `bpy.data.objects.remove` do armário-pai, o sweep salta 2,769 m.
