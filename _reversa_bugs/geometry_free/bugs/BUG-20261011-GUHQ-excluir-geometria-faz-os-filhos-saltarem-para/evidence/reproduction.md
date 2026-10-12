# Cápsula de reprodução (lote 8: geometria livre com pai e filhos)

- Commit base: 83a6863 + lotes 1 a 7 aplicados (master, não commitado)
- Ambiente: Linux 6.8, Blender 5.2.0 LTS, `--background --factory-startup`
- Comando: `/opt/blender/blender --background --factory-startup --python-exit-code 1 --python tests/blender_bug_ELOZ_geometry_parent.py`
- Exit code: 1 (antes) · Taxa: 2/2 (cópia isolada e projeto) · Classificação: deterministic

```
FALHA ELOZ: duplicar com pai girado põe a cópia ao lado (1.5, 2.0, 0.0)
FALHA ELOZ: espelhar com pai girado passa para o outro lado (2.5, 0.0, 0.0)
FALHA GUHQ: excluir mantém o filho onde estava (6.0, 0.0, 0.0) → (1.0, 0.0, 0.0)
```
