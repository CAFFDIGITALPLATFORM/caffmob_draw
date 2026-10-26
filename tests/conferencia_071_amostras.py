"""071 (T052; RF-14): conferência local com projetos `.promob` reais do titular. Nunca roda no portão.

    xvfb-run -a blender --factory-startup --python tests/conferencia_071_amostras.py -- SAIDA ARQ1.promob [ARQ2 ...]

Importa cada ambiente de cada arquivo, mede o tempo, confere que os móveis caem dentro das paredes e grava uma
imagem em perspectiva e uma em planta por ambiente em SAIDA. O relatório só tem contagens e medidas: nenhum dado do
cliente é impresso, e os arquivos não são copiados (RN-02).
"""
import json
import math
import os
import sys
import time
import traceback
from pathlib import Path

import bpy
from mathutils import Vector

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _blender_env  # noqa: E402,F401
from caffmob_draw.promob import leitor, ops  # noqa: E402

args = sys.argv[sys.argv.index('--') + 1:]
SAIDA, ARQUIVOS = args[0], args[1:]
os.makedirs(SAIDA, exist_ok=True)
FILA = [(a, i) for a in ARQUIVOS for i in range(len(leitor.abrir(a).ambientes()))]
RESULTADOS = []


def caixa(objs):
    cantos = [o.matrix_world @ Vector(c) for o in objs for c in o.bound_box]
    return (Vector([min(c[k] for c in cantos) for k in range(3)]), Vector([max(c[k] for c in cantos) for k in range(3)])) if cantos else None


def fotografar(nome):
    """Render do viewport (OpenGL) por uma câmera: perspectiva e planta."""
    from mathutils import Euler
    cena = bpy.context.scene
    visiveis = [o for o in cena.objects if o.type == 'MESH' and not o.hide_viewport]
    lo, hi = caixa(visiveis)
    centro, tamanho = (lo + hi) / 2, max(hi - lo)
    cam = bpy.data.objects.get('Conferencia') or bpy.data.objects.new('Conferencia', bpy.data.cameras.new('Conferencia'))
    if cam.name not in cena.collection.objects:
        cena.collection.objects.link(cam)
    cena.camera = cam
    cena.render.resolution_x, cena.render.resolution_y = 1400, 900
    cena.display.shading.color_type = 'MATERIAL'
    cena.display.shading.light = 'STUDIO'
    area = next(a for a in bpy.context.screen.areas if a.type == 'VIEW_3D')
    regiao = next(r for r in area.regions if r.type == 'WINDOW')
    for sufixo in ('perspectiva', 'planta'):
        if sufixo == 'planta':
            cam.data.type, cam.data.ortho_scale = 'ORTHO', max(hi.x - lo.x, (hi.y - lo.y) * 1400 / 900) * 1.08
            cam.rotation_euler = Euler((0, 0, 0))
            cam.location = (centro.x, centro.y, hi.z + 10)
        else:
            cam.data.type, cam.data.lens = 'PERSP', 30
            cam.rotation_euler = Euler((math.radians(38), 0, math.radians(-30)))
            direcao = cam.rotation_euler.to_matrix() @ Vector((0, 0, 1))
            cam.location = centro + direcao * tamanho * 1.3
        cena.render.filepath = os.path.join(SAIDA, f'{nome}_{sufixo}.png')
        with bpy.context.temp_override(area=area, region=regiao):
            bpy.ops.render.opengl(write_still=True, view_context=False)


def conferir(arquivo, indice, duracao):
    cena = bpy.context.scene
    d = json.loads(cena['caffmob_ambiente'])
    dados = json.loads(cena['caffmob_promob'])
    paredes = [o for o in cena.objects if o.get('caffmob_tipo') == 'parede']
    moveis = [o for o in cena.objects if o.get('btm_promob_item') is not None and o.type == 'MESH' and not o.hide_viewport]
    fora = 0
    caixa_paredes = caixa(paredes)
    if caixa_paredes:
        lo, hi = caixa_paredes
        margem = 0.6
        for o in moveis:
            a, b = caixa([o])
            if a.x < lo.x - margem or a.y < lo.y - margem or b.x > hi.x + margem or b.y > hi.y + margem:
                fora += 1
    rel = dados['relatorio']
    linha = dict(arquivo=os.path.basename(arquivo)[:40], ambiente=indice + 1, segundos=round(duracao, 1),
                 paredes=len(d['paredes']), trechos=sum(len(p['segmentos']) for p in d['paredes']),
                 aberturas=len(d['aberturas']), caixas=rel['caixas'], grupos=rel['grupos'], lajes=rel['lajes'],
                 malhas=rel['malhas'], ignorados=len(rel['ignorados']),
                 motivos=sorted({i['motivo'] for i in rel['ignorados']}), avisos=len(rel['avisos']),
                 moveis_fora_das_paredes=fora, objetos=len(moveis))
    RESULTADOS.append(linha)
    print('CONFERENCIA', json.dumps(linha, ensure_ascii=False), flush=True)
    fotografar(f'{len(RESULTADOS):02d}_{Path(arquivo).stem[-12:]}_amb{indice + 1}')


def proximo():
    if not FILA:
        with open(os.path.join(SAIDA, 'relatorio.json'), 'w', encoding='utf-8') as f:
            json.dump(RESULTADOS, f, ensure_ascii=False, indent=1)
        print('FIM', len(RESULTADOS), flush=True)
        os._exit(0)
    arquivo, indice = FILA.pop(0)
    inicio = time.perf_counter()
    try:
        erro = ops.importar(arquivo, indice)
        if erro:
            print('ERRO', os.path.basename(arquivo)[:40], indice + 1, erro, flush=True)
            bpy.app.timers.register(proximo, first_interval=0.5)
            return None
        def depois():
            try:
                conferir(arquivo, indice, time.perf_counter() - inicio)
            except Exception:
                traceback.print_exc()
            bpy.app.timers.register(proximo, first_interval=0.5)
            return None
        bpy.app.timers.register(depois, first_interval=1.0)
    except Exception:
        traceback.print_exc()
        bpy.app.timers.register(proximo, first_interval=0.5)
    return None


bpy.app.timers.register(proximo, first_interval=2.0)
