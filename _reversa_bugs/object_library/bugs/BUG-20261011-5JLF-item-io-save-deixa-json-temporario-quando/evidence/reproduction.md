# Cápsula de reprodução (lote 10: temporários)

- Commit base: 83a6863 + lotes 1 a 9 aplicados (master, não commitado)
- Ambiente: Linux 6.8, Blender 5.2.0 LTS, `--background --factory-startup`
- Comando: `/opt/blender/blender --background --factory-startup --python-exit-code 1 --python tests/blender_bug_SWAD_temp_files.py`
- Exit code: 1 (antes) · Taxa: 2/2 · Classificação: deterministic

```
FALHA SWAD: sem .tmp na pasta do marcador ['tmp05zszxz4.tmp']
FALHA 5JLF: sem temporários na pasta ['tmpw8jai4q1.json']
```
