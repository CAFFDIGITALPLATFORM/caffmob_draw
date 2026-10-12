# Cápsula de reprodução (lote 14: resultados desatualizados)

- Commit base: 83a6863 + lotes 1 a 13 aplicados (master, não commitado)
- Ambiente: Linux 6.8, Blender 5.2.0 LTS, `--background --factory-startup`
- Comando: `/opt/blender/blender --background --factory-startup --python-exit-code 1 --python tests/blender_bug_TIPN_stale_results.py`
- Exit code: 1 (antes) · Taxa: 2/2 · Classificação: deterministic

```
FALHA TIPN: módulo novo deixa desatualizado
FALHA TIPN: renomear deixa desatualizado
FALHA TIPN: apagar deixa desatualizado
FALHA TIPN: aviso ao soltar sem verificar marca os itens verificados checked=-1 linhas=1
FALHA TIPN: e esse resultado também fica desatualizado
AttributeError: 'BTM_PG_InspectionState' object has no attribute 'stale'   (interferência sem estado desatualizado)
```
