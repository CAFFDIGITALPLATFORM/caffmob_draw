# Reprodução de BUG-20261012-PFY2

- Commit: master em 2026-10-12
- Ambiente: Linux 6.8, Blender 5.2.0 LTS (`/opt/blender/blender`)

Sonda (Blender 5.2.0): cubo A de 1 m em (0, 0, 0,5) e cubo B de 1 m em (dx, 0, 0,5); `scan.find(ctx)` e `BVHTree.FromObject(a).overlap(BVHTree.FromObject(b))`.

```
PROBE3 dx 0.5 colisões [('A', 'B', 0.5)] bvh overlap 2
PROBE3 dx 0.8 colisões [] bvh overlap 2
PROBE3 dx 0.9 colisões [] bvh overlap 2
PROBE3 dx 0.95 colisões [] bvh overlap 2
```
