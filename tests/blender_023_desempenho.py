"""Sonda de desempenho da janela da 023 (T023; NFR: abrir < 2 s, preview < 200 ms por interação).

Mede, sem GUI e sem `gpu`, o caminho que o desenho percorre a cada interação: spec → peças → ordenação por prioridade
→ retângulos de hit das duas vistas. É o custo de modelo do preview; o custo de GPU do desenho só se mede numa sessão
gráfica, e isso é declarado como não verificado aqui.

    blender --background --factory-startup --python-exit-code 1 --python tests/blender_023_desempenho.py
"""

import sys
import time
from pathlib import Path

import bpy  # type: ignore

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tests"))
sys.path.insert(0, str(ROOT))
import _blender_env  # noqa: F401,E402  (registra o add-on)

from caffmob_draw.armario_v2 import build, ops, preview  # noqa: E402

LIMITE_PREVIEW = 0.200     # s (NFR decidida em 2026-11-25)
REPETICOES = 30


def cena_com_armario():
    for obj in list(bpy.data.objects):
        bpy.data.objects.remove(obj, do_unlink=True)
    scene = bpy.context.scene
    scene.btm_armario_contrato.configurado = True
    root = build.criar_raiz(scene)
    bpy.context.view_layer.objects.active = root
    root.select_set(True)
    bpy.ops.caffmob.armario_v2_montar_caixa()
    armario = root.btm_armario
    armario.largura, armario.altura, armario.profundidade = 1200.0, 2400.0, 600.0

    def com_raiz_ativa(operador):
        bpy.context.view_layer.objects.active = root
        root.select_set(True)
        operador()

    for _ in range(4):
        com_raiz_ativa(bpy.ops.caffmob.armario_v2_inserir_prateleira)
    com_raiz_ativa(bpy.ops.caffmob.armario_v2_criar_bloco_gavetas)
    com_raiz_ativa(bpy.ops.caffmob.armario_v2_inserir_interno)
    return root


def medir_preview(root):
    """Uma passada do modelo do preview: peças, ordem de pintura e retângulos das duas vistas."""
    inicio = time.perf_counter()
    spec, itens = preview.estado_da_raiz(root)
    itens = sorted(itens, key=lambda p: preview.PRIORIDADE.get(p['papel'], 9))
    hits = 0
    for eixo, deslocamento, extensao in (('x', spec.largura / 2.0, spec.largura),
                                         ('y', spec.profundidade, spec.profundidade)):
        escala = 500.0 / max(1.0, extensao)
        for peca in itens:
            (ax0, ay0, az0), (ax1, ay1, az1) = peca['box']
            inicio_p, fim_p = (ax0 + deslocamento, ax1 + deslocamento) if eixo == 'x' else (ay0 + deslocamento,
                                                                                          ay1 + deslocamento)
            if fim_p - inicio_p <= 0.0 or az1 - az0 <= 0.0:
                continue
            _ = (inicio_p * escala, az0 * escala, fim_p * escala, az1 * escala)
            hits += 1
    return time.perf_counter() - inicio, len(itens), hits


root = cena_com_armario()
_gastou, total, hits = medir_preview(root)
print(f"peças no preview: {total} ({hits} retângulos nas duas vistas)", flush=True)

tempos = []
for _ in range(REPETICOES):
    gasto, _total, _hits = medir_preview(root)
    tempos.append(gasto)
maior, media = max(tempos), sum(tempos) / len(tempos)
print(f"preview: maior {maior * 1000:.1f} ms, média {media * 1000:.1f} ms em {REPETICOES} passadas", flush=True)

inicio = time.perf_counter()
spec = ops.spec_do_armario(root)
build.pecas(spec, ops.divisoes_do_armario(root.btm_armario), ops.gavetas_do_armario(root.btm_armario),
            ops.internos_do_armario(root.btm_armario))
montagem = time.perf_counter() - inicio
print(f"modelo completo das peças: {montagem * 1000:.1f} ms", flush=True)

for obj in list(bpy.data.objects):
    bpy.data.objects.remove(obj, do_unlink=True)

assert total >= 15, f"armário de ensaio pequeno demais: {total} peças"
assert maior < LIMITE_PREVIEW, f"preview acima da meta: {maior * 1000:.1f} ms > {LIMITE_PREVIEW * 1000:.0f} ms"
print(f"blender_023_desempenho: OK (meta {LIMITE_PREVIEW * 1000:.0f} ms)", flush=True)
