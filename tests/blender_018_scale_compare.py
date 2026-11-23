"""Compara BOX × UV na escala de textura retrato (018).

Textura 300 × 600 mm com 3 × 6 células de 100 × 100 px (célula = 100 × 100 mm). Mede o período em mm no topo e na
lateral da chapa, salvando um render por caso para inspeção. O caminho 'antigo' (BOX) é o que `apply_cached` usava
antes de escolher a projeção pelo alvo; o 'novo' é o UV da chapa.
"""

import json
import os
import sys

import bpy  # type: ignore

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

CELULA_MM = 100.0
COLUNAS, LINHAS = 3, 6


def _imagem(caminho):
    largura, altura = int(COLUNAS * CELULA_MM), int(LINHAS * CELULA_MM)
    img = bpy.data.images.new('grade_300x600', largura, altura, alpha=True)
    pixels = [0.0] * (largura * altura * 4)
    for y in range(altura):
        for x in range(largura):
            base = (y * largura + x) * 4
            pixels[base:base + 4] = (0.9, 0.15, 0.1, 1.0) if (x // 100 + y // 100) % 2 == 0 else (0.92, 0.92, 0.9, 1.0)
    img.pixels = pixels
    img.filepath_raw = caminho
    img.file_format = 'PNG'
    img.save()
    return caminho


def _transicoes(amostras):
    marcas, anterior = [], None
    for indice, valor in enumerate(amostras):
        atual = (valor[0] - valor[1]) > 0.08
        if anterior is not None and atual != anterior:
            marcas.append(indice)
        anterior = atual
    return marcas


def medir(rotulo, caixa_mm, local, rotacao, escala, projecao, textura, saida):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    from caffmob_draw.armario_v2 import build
    from caffmob_draw.object_library import retexture

    obj = bpy.data.objects.new(rotulo, build._malha(rotulo, caixa_mm))
    bpy.context.scene.collection.objects.link(obj)
    obj.data.materials.append(retexture.image_material(textura, 300.0, 600.0, projection=projecao))

    luz = bpy.data.objects.new('sol', bpy.data.lights.new('sol', 'SUN'))
    bpy.context.scene.collection.objects.link(luz)
    luz.rotation_euler = (0.6, 0.2, 0.0)

    cena = bpy.context.scene
    cena.render.engine = 'CYCLES'
    cena.cycles.device = 'CPU'
    cena.cycles.samples = 1
    cena.cycles.use_denoising = False
    cena.render.resolution_x = cena.render.resolution_y = 320
    cena.render.image_settings.file_format = 'PNG'
    dados = bpy.data.cameras.new('cam')
    dados.type = 'ORTHO'
    dados.ortho_scale = escala
    cam = bpy.data.objects.new('cam', dados)
    cena.collection.objects.link(cam)
    cam.location, cam.rotation_euler = local, rotacao
    cena.camera = cam
    cena.render.filepath = os.path.join(ROOT, saida)
    bpy.ops.render.render(write_still=True)

    img = bpy.data.images.load(os.path.join(ROOT, saida))
    largura, altura = img.size
    pixels = list(img.pixels)

    def cor(x, y):
        base = (y * largura + x) * 4
        return pixels[base:base + 3]

    mm_por_px = escala * 1000.0 / largura
    mx = _transicoes([cor(x, altura // 2) for x in range(largura)])
    my = _transicoes([cor(largura // 2, y) for y in range(altura)])
    bpy.data.images.remove(img)
    px = [round((b - a) * mm_por_px, 1) for a, b in zip(mx, mx[1:])]
    py = [round((b - a) * mm_por_px, 1) for a, b in zip(my, my[1:])]
    return {'passo_x_mm': px, 'passo_y_mm': py,
            'celula_x_mm': min(px) if px else None, 'celula_y_mm': min(py) if py else None}


def main():
    textura = _imagem(os.path.join(ROOT, 'probe_018_grade.png'))
    resultado = {}
    for projecao in ('BOX', 'UV'):
        sufixo = projecao.lower()
        resultado['topo_' + sufixo] = medir(
            'topo_' + sufixo, ((0.0, 0.0, 0.0), (600.0, 400.0, 18.0)),
            (0.3, 0.2, 1.0), (0.0, 0.0, 0.0), 0.6, projecao, textura,
            'probe_018_{}_topo.png'.format(sufixo))
        resultado['lateral_' + sufixo] = medir(
            'lateral_' + sufixo, ((0.0, 0.0, 0.0), (18.0, 400.0, 600.0)),
            (1.0, 0.2, 0.3), (1.5707963, 0.0, 1.5707963), 0.6, projecao, textura,
            'probe_018_{}_lateral.png'.format(sufixo))
    resultado['celula_mm'] = CELULA_MM
    print('===PROBE_JSON===')
    print(json.dumps(resultado, ensure_ascii=False, indent=2))
    print('===PROBE_FIM===')
    os.remove(textura)


main()
