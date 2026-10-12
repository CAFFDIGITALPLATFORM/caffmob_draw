# Cápsula de reprodução (lote 3: editor de paredes)

- Commit base: 83a6863 + lotes 1 e 2 aplicados + mudanças locais da feature 013 (master, não commitado)
- Ambiente: Linux 6.8, Blender 5.2.0 LTS, `--background --factory-startup`
- Comando: `/opt/blender/blender --background --factory-startup --python-exit-code 1 --python tests/blender_bug_TLPN_remove_node.py`
- Exit code: 1 (antes da correção) · Taxa: 2/2 (cópia isolada e projeto) · Classificação: deterministic

```
FALHA TLPN: o trecho eliminado vai para removed_sources []
FALHA TLPN: depois do OK a cena tem uma parede a menos (sem órfã) 4 → 4: ['Wall', 'Wall.001', 'Wall.002', 'Wall.003']
OK   TLPN: a parede do trecho que continua fica Wall.001
OK   TLPN: o rascunho lido de novo bate com a cena
FALHA GKUE: Delete numa cadeia fechada limpa a seleção (0, 1)
```
