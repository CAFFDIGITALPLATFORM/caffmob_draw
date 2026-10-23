"""Medição do guarda de colisão (feature 066, T077; RNF Desempenho, R3).

Run: blender --background --factory-startup --python-exit-code 1 --python tests/blender_066_guard_bench.py

Cena: 1000 corpos físicos (cubos soltos em grade) e um componente de 100 membros (um Empty com 100 peças). Depois do
aquecimento, 30 movimentos do componente pela cena, parte deles contra obstáculos. Registra:
- o p95 da atualização (o handler do guarda por movimento; meta 33 ms);
- o p95 da confirmação (`guard.clamp`, como no Confirmar do Mover Sobre; meta 500 ms).
A meta é registrada, não reprovada: a segurança vence a meta (RNF). Reprova só se o guarda deixar penetrar.
"""

import math
import statistics
import sys
import time
import traceback
from pathlib import Path

import bpy
from mathutils import Matrix, Vector

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _blender_env as env  # noqa: E402
from caffmob_draw.collision import guard as _guard  # noqa: E402
# Estes cenários movem por código no lugar do G: o guarda só limita G e gizmo (BUG-20261023-TAMR, RF01).
_guard._direct_move_running = lambda: True
from caffmob_draw.collision import guard, obb  # noqa: E402

ctx = bpy.context
FAILURES = []
UPDATE_GOAL, CONFIRM_GOAL = 0.033, 0.5


def check(name, ok, detail=""):
    print(("OK   " if ok else "FALHA ") + name, detail, flush=True)
    if not ok:
        FAILURES.append(name)


def p95(values):
    ordered = sorted(values)
    return ordered[max(0, math.ceil(0.95 * len(ordered)) - 1)]


def build():
    env.clean_scene()
    ctx.scene.btm_settings.block_penetration = False         # montar a cena sem o guarda
    mesh = bpy.data.meshes.new("Cubo")
    import bmesh
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=0.3)
    bm.to_mesh(mesh)
    bm.free()
    for i in range(1000):
        obj = bpy.data.objects.new(f"Corpo{i:04d}", mesh)
        obj.location = ((i % 40) * 0.6, 3.0 + (i // 40) * 0.6, 0.15)
        ctx.scene.collection.objects.link(obj)
    root = bpy.data.objects.new("Componente", None)
    ctx.scene.collection.objects.link(root)
    piece = bpy.data.meshes.new("Peca")
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=0.05)
    bm.to_mesh(piece)
    bm.free()
    for i in range(100):
        obj = bpy.data.objects.new(f"Membro{i:03d}", piece)
        obj.parent = root
        obj.location = ((i % 10) * 0.06, (i // 10) * 0.06, 0.03)
        ctx.scene.collection.objects.link(obj)
    root.location = (0.0, 0.0, 0.0)
    env.settle()
    ctx.scene.btm_settings.block_penetration = True
    guard.seed()
    env.settle()
    return root


def penetrating(root):
    depsgraph = ctx.evaluated_depsgraph_get()
    from caffmob_draw.collision import scan
    mine = [scan.box_of(o, depsgraph) for o in root.children]
    for obj in ctx.scene.objects:
        if obj.name.startswith("Corpo"):
            other = scan.box_of(obj, depsgraph)
            for box in mine:
                hit = obb.overlap(box, other)
                if hit is not None and hit['depth'] > 0.0015:
                    return obj.name
    return None


def bench():
    root = build()
    # Inclui a atualização da cena inteira, também mapa de filhos e depsgraph.
    for step in range(40):                 # 10 de aquecimento + 30 medidos
        root.location = root.location + Vector((0.11, 0.09 if step % 2 else 0.17, 0.0))
        t0 = time.perf_counter()
        ctx.view_layer.update()
        elapsed = time.perf_counter() - t0
        if step >= 10:
            bench.updates.append(elapsed)
    start = root.matrix_world.copy()
    for step in range(40):
        target = Matrix.Translation(start.translation + Vector((0.05 * (step % 30), 4.0, 0.0)))
        t0 = time.perf_counter()
        allowed = guard.clamp(root, start, target)
        elapsed = time.perf_counter() - t0
        if step >= 10:
            bench.confirms.append(elapsed)
        # Fora da medição: valida também a pose devolvida por cada confirmação.
        if guard.overlapping(root, allowed):
            FAILURES.append(f"confirmação {step} penetrou")
    print("CENA: 1000 obstáculos físicos + componente de 100 membros; aquecimento=10, amostras=30")
    hit = penetrating(root)
    check("o guarda não deixou o componente penetrar", hit is None, str(hit))


bench.updates, bench.confirms = [], []
try:
    bench()
except Exception:
    traceback.print_exc()
    FAILURES.append("exceção na medição")
if bench.updates:
    up, conf = p95(bench.updates), p95(bench.confirms)
    print(f"MEDIDA atualização: p95 {up * 1000:.1f} ms (meta {UPDATE_GOAL * 1000:.0f} ms), "
          f"mediana {statistics.median(bench.updates) * 1000:.1f} ms, n={len(bench.updates)}")
    print(f"MEDIDA confirmação: p95 {conf * 1000:.1f} ms (meta {CONFIRM_GOAL * 1000:.0f} ms), "
          f"mediana {statistics.median(bench.confirms) * 1000:.1f} ms, n={len(bench.confirms)}")
    print(f"MEDIDA metas: atualização {'cumprida' if up <= UPDATE_GOAL else 'NÃO cumprida'}, "
          f"confirmação {'cumprida' if conf <= CONFIRM_GOAL else 'NÃO cumprida'}")
print(f"blender_066_guard_bench: {'OK' if not FAILURES else 'FALHAS: ' + ', '.join(FAILURES)}")
sys.exit(1 if FAILURES else 0)
