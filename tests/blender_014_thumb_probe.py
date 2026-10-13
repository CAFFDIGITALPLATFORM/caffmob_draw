"""Prova D-05 (feature 014, T001): miniatura na GPU sem criar `Image` em `bpy.data`.

Precisa de janela (não roda em --background):
    xvfb-run -a blender --factory-startup --python tests/blender_014_thumb_probe.py

Gera 40 PNGs de 256 px e mede dois caminhos:
- A (escolhido no plano): `bpy.utils.previews.load(..., 'IMAGE')` → `ImagePreview.image_pixels_float` →
  `gpu.types.GPUTexture(size, data=Buffer)`, desenhado com o shader `IMAGE` num handler POST_PIXEL;
- B (reserva): `bpy.data.images.load` → `gpu.texture.from_image`.
Imprime, por caminho: pixels vazios no primeiro acesso, quantos redesenhos até ficarem prontos, tempo por
miniatura e `bpy.data.images` antes e depois. Sai com 0 se o caminho A desenhar as 40 miniaturas.
"""

import os
import tempfile
import time
import traceback

import bpy
import bpy.utils.previews
import gpu
from gpu_extras.batch import batch_for_shader

N, SIZE = 40, 256
REPORT = {}


def make_pngs():
    folder = tempfile.mkdtemp()
    for i in range(N):
        img = bpy.data.images.new(f"probe_{i}", SIZE, SIZE)
        img.pixels[:] = [((i * 37) % 255) / 255.0, 0.4, 0.2, 1.0] * (SIZE * SIZE)
        path = os.path.join(folder, f"t{i}.png")
        img.filepath_raw, img.file_format = path, 'PNG'
        img.save()
        bpy.data.images.remove(img)
    return [os.path.join(folder, f"t{i}.png") for i in range(N)]


def preview_texture(preview):
    """GPUTexture a partir dos pixels do preview, ou None se ainda não carregaram."""
    w, h = preview.image_size
    if not w or not h:
        return None
    pixels = preview.image_pixels_float[:]
    if not pixels or not any(pixels):
        return None
    buffer = gpu.types.Buffer('FLOAT', w * h * 4, pixels)
    return gpu.types.GPUTexture((w, h), format='RGBA8', data=buffer)


def script():
    win = bpy.context.window_manager.windows[0]
    area = next(a for a in win.screen.areas if a.type == 'VIEW_3D')
    paths = make_pngs()
    images_before = len(bpy.data.images)

    # Caminho A: previews → GPUTexture
    coll = bpy.utils.previews.new()
    t0 = time.perf_counter()
    previews = [coll.load(f"p{i}", p, 'IMAGE') for i, p in enumerate(paths)]
    first_empty = sum(1 for p in previews if not p.image_size[0] or not any(p.image_pixels_float[:16]))
    textures, frames = {}, 0
    shader = gpu.shader.from_builtin('IMAGE')

    def draw():
        for i, tex in list(textures.items())[:N]:
            x, y = 10 + (i % 10) * 34, 10 + (i // 10) * 34
            batch = batch_for_shader(shader, 'TRI_FAN', {"pos": ((x, y), (x + 32, y), (x + 32, y + 32), (x, y + 32)),
                                                         "texCoord": ((0, 0), (1, 0), (1, 1), (0, 1))})
            shader.bind()
            shader.uniform_sampler("image", tex)
            batch.draw(shader)

    handle = bpy.types.SpaceView3D.draw_handler_add(draw, (), 'WINDOW', 'POST_PIXEL')
    try:
        while len(textures) < N and frames < 200:
            for i, preview in enumerate(previews):
                if i not in textures:
                    tex = preview_texture(preview)
                    if tex is not None:
                        textures[i] = tex
            area.tag_redraw()
            frames += 1
            yield 0.02
        elapsed_a = time.perf_counter() - t0
        REPORT['A'] = {"prontas": len(textures), "vazias_no_1o_acesso": first_empty, "redesenhos": frames,
                       "ms_por_miniatura": round(elapsed_a * 1000 / N, 2), "tamanho": tuple(previews[0].image_size),
                       "images_em_bpy_data": len(bpy.data.images) - images_before}
        yield 0.3
    finally:
        bpy.types.SpaceView3D.draw_handler_remove(handle, 'WINDOW')
        bpy.utils.previews.remove(coll)

    # Caminho B: bpy.data.images → gpu.texture.from_image
    t0 = time.perf_counter()
    loaded = [bpy.data.images.load(p, check_existing=False) for p in paths]
    textures_b = [gpu.texture.from_image(img) for img in loaded]
    elapsed_b = time.perf_counter() - t0
    REPORT['B'] = {"prontas": sum(1 for t in textures_b if t is not None), "ms_por_miniatura": round(elapsed_b * 1000 / N, 2),
                   "images_em_bpy_data": len(bpy.data.images) - images_before}
    for img in loaded:
        bpy.data.images.remove(img)


_gen = script()


def tick():
    try:
        return next(_gen)
    except StopIteration:
        pass
    except Exception:
        traceback.print_exc()
        REPORT['erro'] = True
    print("PROVA_D05", REPORT, flush=True)
    ok = REPORT.get('A', {}).get('prontas') == N and not REPORT.get('erro')
    os._exit(0 if ok else 1)


bpy.app.timers.register(tick, first_interval=2.0)
