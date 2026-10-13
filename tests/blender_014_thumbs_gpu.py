"""Miniaturas da grade na GPU (feature 014, T027; D-05).

Precisa de janela (contexto de GPU):
    xvfb-run -a blender --factory-startup --python tests/blender_014_thumbs_gpu.py

- 40 miniaturas reais do catálogo (`caffmob_draw/textures/thumbs/`) viram `GPUTexture` sem criar `Image` em
  `bpy.data`;
- cada chamada de `process()` respeita o orçamento (para no orçamento depois da primeira conversão), e o timer
  esvazia a fila sozinho, sem o teste chamar `process()`;
- a mesma chave não entra duas vezes na fila; arquivo inexistente vira falha, sem exceção;
- `free()` limpa tudo.
"""

import json
import os
import sys
import time
import traceback
from pathlib import Path

import bpy

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tests"))
import _blender_env  # noqa: E402,F401

from caffmob_draw.library_panel import thumbs_gpu  # noqa: E402

FAILURES = []


def check(name, ok, detail=""):
    print(("OK   " if ok else "FALHA ") + name, detail, flush=True)
    if not ok:
        FAILURES.append(name)


def script():
    textures = ROOT / "caffmob_draw" / "textures"
    catalog = json.load(open(textures / "catalog.json", encoding="utf-8"))
    items = [i for m in catalog["manufacturers"] for c in m["collections"] for i in c["items"]][:40]
    images_before = len(bpy.data.images)
    for item in items:
        thumbs_gpu.texture(item["id"], str(textures / item["thumb"]))
    thumbs_gpu.texture(items[0]["id"], str(textures / items[0]["thumb"]))       # repetida: não duplica
    check("fila sem duplicar", thumbs_gpu.pending() == 40, str(thumbs_gpu.pending()))
    s = time.perf_counter()
    thumbs_gpu.process()
    worst = time.perf_counter() - s
    calls, t0 = 1, time.perf_counter()
    while thumbs_gpu.pending() and calls < 400:           # o timer do módulo converte o resto
        calls += 1
        yield 0.02
    total = time.perf_counter() - t0 + worst
    ready = sum(1 for i in items if thumbs_gpu.texture(i["id"], "") is not None)
    check("40 miniaturas prontas", ready == 40, f"{ready} em {calls} chamadas, {total:.2f} s")
    check("nenhuma Image em bpy.data", len(bpy.data.images) == images_before)
    check("uma chamada fica perto do orçamento (uma conversão no máximo além dele)", worst < 0.04,
          f"{worst * 1000:.1f} ms")
    print("TEMPO_POR_MINIATURA_MS", round(total * 1000 / 40, 2), flush=True)
    thumbs_gpu.texture("nao/existe", "/nao/existe.png")
    for _ in range(20):
        yield 0.02
    check("arquivo inexistente vira falha, sem exceção", thumbs_gpu.failed("nao/existe"))
    thumbs_gpu.free()
    check("free limpa", thumbs_gpu.pending() == 0 and thumbs_gpu.texture(items[0]["id"], "") is None)
    thumbs_gpu.free()


_gen = script()


def tick():
    try:
        return next(_gen)
    except StopIteration:
        pass
    except Exception:
        traceback.print_exc()
        FAILURES.append("exceção no roteiro")
    print(f"blender_014_thumbs_gpu: {'OK' if not FAILURES else 'FALHAS: ' + ', '.join(FAILURES)}", flush=True)
    os._exit(1 if FAILURES else 0)


bpy.app.timers.register(tick, first_interval=1.0)
