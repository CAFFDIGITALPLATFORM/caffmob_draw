"""T086: p95 real, 4 paredes, 2 portas, 1 janela e exatamente 1000 peças de revestimento.

Prévia mede a mesma extração e o mesmo layout/recorte usados pelo modal (sem rasterização GPU, em background).
Confirmação muda a espessura de todas as peças, constrói malhas e conclui a avaliação do depsgraph.
"""
import sys
import time
import math
import json
import tempfile
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import bpy
import _cladding_env as a
from caffmob_draw.cladding import ops, ops_adopt, region, sync
from caffmob_draw.collision import guard
from caffmob_draw.operators import doors_windows as dw


def preview(root):
    return len(ops.preview_geometry(root.btm_cladding))


def p95(values):
    return sorted(values)[math.ceil(.95*len(values))-1] * 1000


walls, wall, door, window, first = a.scene()
with guard.suspended():
    second = a.oe.make_cage()
    other = next(w for w in walls if w != wall)
    second.parent, second.location = other, (.5,0,0)
    dw.cut_wall(other, second)
    a.env.settle()
    a.opening_sync.sync(bpy.context, second)
    roots = [first] + [ops_adopt.create(w) for w in walls if w != wall]
    # Os quatro controladores têm a mesma grade densa. Ajustar só o último deixa o total exato.
    for root in roots:
        root.btm_cladding.width_mm = 18
        root.btm_cladding.joint_mm = 3
    for root in roots:
        sync.sync(root)
    a.env.settle()
    # Buscar um total de 1000 por contagem de chaves, sem apagar nem fabricar peças fora do gerador.
    fixed = sum(len(a.pieces(r)) for r in roots[:-1])
    last = roots[-1]
    target = 1000 - fixed
    last.btm_cladding.band = 'PARTIAL'
    last.btm_cladding.band_mm = 1600
    _basis, tris = region.extract(last.btm_cladding)
    outline = region.bounds(tris)
    height_mm = max(y for x,y in outline)-min(y for x,y in outline)
    last.btm_cladding.width_mm = height_mm / (target-.5) - 3
    a.check(len(sync.prepare(last)[3]) == target, 'ajuste paramétrico do total exato')
    sync.sync(last)
    a.env.settle()
    total = sum(len(a.pieces(r)) for r in roots)
    a.check(total == 1000, 'cena com exatamente 1000 peças')
    for _ in range(3):
        for root in roots:
            preview(root)
    previews, confirmations = [], []
    for i in range(30):
        start = time.perf_counter()
        for root in roots:
            preview(root)
        previews.append(time.perf_counter()-start)
        start = time.perf_counter()
        for root in roots:
            root.btm_cladding.thickness_mm = 16 - (i % 2)
            sync.sync(root)
        a.env.settle()
        confirmations.append(time.perf_counter()-start)
        if (i+1) % 5 == 0:
            print('T086 amostras: {}/30'.format(i+1), flush=True)
    result = dict(pieces=total, walls=len(walls), doors=2, windows=1, samples=30,
                  preview_p95_ms=p95(previews), confirmation_p95_ms=p95(confirmations),
                  preview_target_ms=100, confirmation_target_ms=2000,
                  blender=bpy.app.version_string,
                  preview_scope=('quatro controladores; mesma função do modal: extração, layout, recorte '
                                 'e vetores de desenho; sem rasterização GPU'))
    # Artefato temporário, independente da árvore do repositório.
    with tempfile.TemporaryDirectory() as folder:
        Path(folder,'resultado.json').write_text(json.dumps(result,indent=2))
    print('T086 '+json.dumps(result,ensure_ascii=False),flush=True)
