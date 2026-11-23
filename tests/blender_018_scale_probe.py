"""Probe da escala de textura retangular na chapa (018): mede células em mm por face.

Textura 600 × 300 mm com 6 × 3 células de 100 × 100 px: cada célula vale 100 × 100 mm. Se o material divide U pela
largura e V pela altura da imagem, as células saem quadradas nas três faces. Cada face é medida numa chapa com área
grande naquela direção, com render ortográfico e leitura do período em mm.
"""

import json
import os
import sys

import bpy  # type: ignore

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

CELULA_MM = 100.0
COLUNAS, LINHAS = 6, 3


def _imagem(caminho):
    largura, altura = int(COLUNAS * CELULA_MM), int(LINHAS * CELULA_MM)
    img = bpy.data.images.new('grade_600x300', largura, altura, alpha=True)
    pixels = [0.0] * (largura * altura * 4)
    for y in range(altura):
        for x in range(largura):
            base = (y * largura + x) * 4
            pixels[base:base + 4] = (0.9, 0.2, 0.1, 1.0) if (x // 100 + y // 100) % 2 == 0 else (0.9, 0.9, 0.9, 1.0)
    img.pixels = pixels
    img.filepath_raw = caminho
    img.file_format = 'PNG'
    img.save()
    return caminho


def _transicoes(amostras):
    """Marcas onde a célula vermelha vira branca (ou vice-versa); compara R−G, que sobrevive à exposição."""
    marcas, anterior = [], None
    for indice, valor in enumerate(amostras):
        atual = (valor[0] - valor[1]) > 0.08
        if anterior is not None and atual != anterior:
            marcas.append(indice)
        anterior = atual
    return marcas


def medir(rotulo, caixa_mm, camera_local, camera_rot, escala, caminho_textura):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    from caffmob_draw.armario_v2 import build
    from caffmob_draw.object_library import retexture

    obj = bpy.data.objects.new(rotulo, build._malha(rotulo, caixa_mm))
    bpy.context.scene.collection.objects.link(obj)
    obj.data.materials.append(retexture.image_material(caminho_textura, 600.0, 300.0, projection='UV'))

    luz = bpy.data.objects.new('sol', bpy.data.lights.new('sol', 'SUN'))
    bpy.context.scene.collection.objects.link(luz)
    luz.rotation_euler = (0.6, 0.2, 0.0)

    cena = bpy.context.scene
    cena.render.engine = 'CYCLES'
    cena.cycles.device = 'CPU'
    cena.cycles.samples = 1
    cena.cycles.use_denoising = False
    cena.render.resolution_x = cena.render.resolution_y = 240
    cena.render.image_settings.file_format = 'PNG'
    dados = bpy.data.cameras.new('cam')
    dados.type = 'ORTHO'
    dados.ortho_scale = escala
    cam = bpy.data.objects.new('cam', dados)
    cena.collection.objects.link(cam)
    cam.location, cam.rotation_euler = camera_local, camera_rot
    cena.camera = cam
    arq = os.path.join(ROOT, 'probe_018_render.png')
    cena.render.filepath = arq
    bpy.ops.render.render(write_still=True)

    img = bpy.data.images.load(arq)
    largura, altura = img.size
    pixels = list(img.pixels)

    def cor(x, y):
        base = (y * largura + x) * 4
        return pixels[base:base + 3]

    mm_por_px = escala * 1000.0 / largura
    marcas_x = _transicoes([cor(x, altura // 2) for x in range(largura)])
    marcas_y = _transicoes([cor(largura // 2, y) for y in range(altura)])
    passos_x = [round((b - a) * mm_por_px, 1) for a, b in zip(marcas_x, marcas_x[1:])]
    passos_y = [round((b - a) * mm_por_px, 1) for a, b in zip(marcas_y, marcas_y[1:])]
    bpy.data.images.remove(img)
    return {'passo_x_mm': passos_x, 'passo_y_mm': passos_y,
            'celula_x_mm': min(passos_x) if passos_x else None,
            'celula_y_mm': min(passos_y) if passos_y else None}


def main():
    caminho = _imagem(os.path.join(ROOT, 'probe_018_grade.png'))
    resultado = {
        'topo': medir('topo', ((0.0, 0.0, 0.0), (600.0, 400.0, 18.0)),
                      (0.3, 0.2, 1.0), (0.0, 0.0, 0.0), 0.6, caminho),
        'lateral': medir('lateral', ((0.0, 0.0, 0.0), (18.0, 400.0, 720.0)),
                         (1.0, 0.2, 0.36), (1.5707963, 0.0, 1.5707963), 0.72, caminho),
        'frente': medir('frente', ((0.0, 0.0, 0.0), (600.0, 18.0, 720.0)),
                        (0.3, -1.0, 0.36), (1.5707963, 0.0, 0.0), 0.72, caminho),
    }
    resultado['celula_mm'] = CELULA_MM
    resultado['ok'] = all(
        item['celula_x_mm'] is not None and item['celula_y_mm'] is not None
        and abs(item['celula_x_mm'] - CELULA_MM) < 5 and abs(item['celula_y_mm'] - CELULA_MM) < 5
        for chave, item in resultado.items() if isinstance(item, dict)
    )
    print('===PROBE_JSON===')
    print(json.dumps(resultado, ensure_ascii=False, indent=2))
    print('===PROBE_FIM===')
    os.remove(caminho)
    os.remove(os.path.join(ROOT, 'probe_018_render.png')) if os.path.exists(os.path.join(ROOT, 'probe_018_render.png')) else None


main()
