# Reprodução de BUG-20261012-DWPO

- Commit: master em 2026-10-12
- Ambiente: Linux 6.8, Blender 5.2.0 LTS (`/opt/blender/blender`)

Sonda (Blender 5.2.0): `tf.BaseCabinet` "Balcao" em x = 5, `run_calc_fix_until_stable`; caixa em X pelo `_tree_box` do Substituir e pelo `_local_box` do Mover Sobre.

```
PROBE4 tree_box x -5.0 0.914 scene box x [0.0]
```

Malhas da árvore com caixa degenerada: `Sink Apron 0.0 0.0` e `Top 0.0 0.0` (x mínimo e máximo no mundo).
