# Cápsula de reprodução (lote 11: editor de paredes)

- Commit base: 83a6863 + lotes 1 a 10 aplicados + mudanças locais da 013 (master, não commitado)
- Ambiente: Linux 6.8, Blender 5.2.0 LTS, `--background --factory-startup`
- Comando: `/opt/blender/blender --background --factory-startup --python-exit-code 1 --python tests/blender_bug_YAVM_wall_editor.py`
- Exit code: 1 (antes) · Taxa: 2/2 · Classificação: deterministic

```
FALHA YAVM: Ctrl+Z desfaz a troca de Direção depois da troca=LEFT desfez=False agora=LEFT
FALHA LT3C: o 'Não' de fechar a sala sobrevive ao OK fechadas=1 paredes=4
FALHA 624G: soltar na barra conclui a lupa zoom_window=(100.0, 100.0) escala 100.0 → 100.0
FALHA 624G: soltar na barra durante o arraste de vértice chega ao editor
FALHA XMZM: o 2º OK refaz os avisos se o rascunho mudou 1º={'CANCELLED'} 2º={'FINISHED'}
FALHA PJJU: com a trava, os ângulos ficam desabilitados {... 'angle_abs': True, 'angle_rel': True ...}
FALHA Z2BL: pé-direito de 12 m é recusado recusou=False paredes com 12 m=[4 paredes]
```
