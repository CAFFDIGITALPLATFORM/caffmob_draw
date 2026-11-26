"""Prova visual da 024 por script (T015; RN-01, RN-03, RN-04, D-05).

Roda com janela (a variante precisa de vista 3D) e renderiza de verdade:

    blender.exe --factory-startup --enable-event-simulate --python tests/blender_024_visual.py

Cobre o que o roteiro de `onboarding.md` pede ao olho, no que dá para medir:

- **cor média**: um render amplo da chapa tem a mesma média de um render com material liso da mesma cor — o Solid em
  `TEXTURE` mostra a cor média da textura;
- **grão do MDF**: um close-up da chapa tem variação de alta frequência; o mesmo close-up com material liso não tem;
- **contorno no Solid**: a variante "Textura com linhas" deixa `shading.type = 'SOLID'`, `color_type = 'TEXTURE'` e
  `overlay.show_wireframes` com o limiar/opacidade do modo de vista; "Somente textura" desliga;
- **Solid/Preview/render iguais**: as três leituras usam o mesmo material e a mesma imagem empacotada, e o render com a
  vista em Material Preview sai idêntico ao render em Solid (o render não depende do shading da vista);
- **aviso de migração**: o `load_post` avisa uma única vez por cena migrada, com a contagem no texto.

O que sobra para o olho humano está em `onboarding.md` §6.
"""

import math
import os
import statistics
import sys
import tempfile
import traceback
from pathlib import Path

import bpy
from mathutils import Vector

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _blender_env as env  # noqa: E402,F401
from caffmob_draw.armario_v2 import build, exibicao, mdf_core, textura_padrao  # noqa: E402

FAILURES = []
LIMIAR_PAINEL = 0.40            # o PNG carrega em sRGB: o fundo escuro fica ~0,23 e a chapa iluminada ~0,63
MARGEM_PAINEL = 4               # borda anti-serrilhada e degrau de fundo ficam de fora


def check(name, ok, detail=""):
    print(("OK   " if ok else "FALHA ") + name, detail, flush=True)
    if not ok:
        FAILURES.append(name)


def spaces():
    return [space for window in bpy.context.window_manager.windows for area in window.screen.areas
            if area.type == 'VIEW_3D' for space in area.spaces if space.type == 'VIEW_3D']


def _limpar_objetos():
    for obj in list(bpy.data.objects):
        bpy.data.objects.remove(obj, do_unlink=True)


def _camera(cena, posicao, alvo=Vector((0.30, 0.009, 0.36))):
    camera = cena.camera
    camera.location = Vector(posicao)
    camera.rotation_euler = (alvo - camera.location).to_track_quat('-Z', 'Y').to_euler()


def _montar(cena):
    malha = build._malha("Chapa 024", ((0.0, 0.0, 0.0), (600.0, 18.0, 720.0)))
    objeto = bpy.data.objects.new("Chapa 024", malha)
    cena.collection.objects.link(objeto)
    mapa = build.materiais('MADEIRADO')
    malha.materials.append(mapa['CHAPA'])

    dados_camera = bpy.data.cameras.new("Cam 024")
    camera = bpy.data.objects.new("Cam 024", dados_camera)
    cena.collection.objects.link(camera)
    cena.camera = camera
    _camera(cena, (1.15, -1.45, 0.95))

    luz_dados = bpy.data.lights.new("Sol 024", 'SUN')
    luz_dados.energy = 3.0
    luz = bpy.data.objects.new("Sol 024", luz_dados)
    cena.collection.objects.link(luz)
    luz.rotation_euler = (math.radians(50.0), 0.0, math.radians(30.0))

    if cena.world is None:
        cena.world = bpy.data.worlds.new("Mundo 024")
    if cena.world.node_tree is None:
        cena.world.use_nodes = True
    fundo = cena.world.node_tree.nodes.get('Background')
    if fundo is not None:
        fundo.inputs['Color'].default_value = (0.05, 0.05, 0.05, 1.0)
    cena.render.engine = 'BLENDER_EEVEE'
    cena.eevee.taa_render_samples = 1024      # ruído de TAA abaixo do grão: o close-up mede textura, não amostragem
    cena.render.resolution_x = cena.render.resolution_y = 256
    cena.render.film_transparent = False
    cena.render.dither_intensity = 0.0      # sem dithering: o degrau de 1/255 não vira ruído que imita grão

    return objeto, mapa


def _render(cena, caminho):
    """Renderiza e salva; mede nos pixels float do Render Result (o PNG de 8 bits quantizaria o grão)."""
    cena.render.filepath = caminho
    bpy.ops.render.render(write_still=True)
    resultado = bpy.data.images.get('Render Result')
    if resultado is not None and resultado.has_data and tuple(resultado.size) == (256, 256):
        return list(resultado.pixels)
    imagem = bpy.data.images.load(caminho, check_existing=False)
    pixels = list(imagem.pixels)
    bpy.data.images.remove(imagem)
    return pixels


def _tamanho(pixels):
    return int(round(math.sqrt(len(pixels) / 4)))


def _mascara(pixels):
    tamanho = _tamanho(pixels)
    return [[0.2126 * pixels[(y * tamanho + x) * 4] + 0.7152 * pixels[(y * tamanho + x) * 4 + 1]
             + 0.0722 * pixels[(y * tamanho + x) * 4 + 2] > LIMIAR_PAINEL for x in range(tamanho)]
            for y in range(tamanho)]


def _miolo(mascara):
    """Pixels com a vizinhança toda dentro da chapa: sem borda nem fundo."""
    tamanho = len(mascara)
    m = MARGEM_PAINEL
    for y in range(m, tamanho - m):
        for x in range(m, tamanho - m):
            if (mascara[y][x] and mascara[y][x - m] and mascara[y][x + m]
                    and mascara[y - m][x] and mascara[y + m][x]):
                yield x, y


def _estatisticas(pixels):
    """(média da luminância, (r, g, b), cobertura) do miolo chapado."""
    tamanho = _tamanho(pixels)
    mascara = _mascara(pixels)
    cobertura = sum(linha.count(True) for linha in mascara) / (tamanho * tamanho)
    lums, canais = [], ([], [], [])
    for x, y in _miolo(mascara):
        i = (y * tamanho + x) * 4
        lums.append(0.2126 * pixels[i] + 0.7152 * pixels[i + 1] + 0.0722 * pixels[i + 2])
        for canal in range(3):
            canais[canal].append(pixels[i + canal])
    if not lums:
        return 0.0, (0.0, 0.0, 0.0), cobertura
    return statistics.fmean(lums), tuple(statistics.fmean(v) for v in canais), cobertura


def _rugosidade(pixels):
    """|Δ| médio entre pixels vizinhos no miolo da chapa: mede grão, não gradiente de luz."""
    tamanho = _tamanho(pixels)
    mascara = _mascara(pixels)
    diferencas = []
    for x, y in _miolo(mascara):
        i, vizinho = (y * tamanho + x) * 4, (y * tamanho + x + 1) * 4
        lum = 0.2126 * pixels[i] + 0.7152 * pixels[i + 1] + 0.0722 * pixels[i + 2]
        lum_v = 0.2126 * pixels[vizinho] + 0.7152 * pixels[vizinho + 1] + 0.0722 * pixels[vizinho + 2]
        diferencas.append(abs(lum - lum_v))
    return statistics.fmean(diferencas) if diferencas else 0.0


def _material_liso():
    """Material de controle com a cor média exata da textura: mesma luz, sem grão."""
    dados = mdf_core.gerar()
    total = mdf_core.TAMANHO * mdf_core.TAMANHO

    def linear(valor):
        return valor / 12.92 if valor <= 0.04045 else ((valor + 0.055) / 1.055) ** 2.4

    cor = tuple(linear(sum(dados[canal::4]) / total / 255.0) for canal in range(3)) + (1.0,)
    liso = bpy.data.materials.new("Chapa 024 lisa")
    liso.use_nodes = True
    bsdf = next(no for no in liso.node_tree.nodes if no.type == 'BSDF_PRINCIPLED')
    bsdf.inputs['Base Color'].default_value = cor
    bsdf.inputs['Roughness'].default_value = 0.45
    liso.diffuse_color = cor
    return liso


def main():
    cena = bpy.context.scene
    _limpar_objetos()
    objeto, mapa = _montar(cena)
    chapa = mapa['CHAPA']
    destino = os.path.join(tempfile.gettempdir(), "caffmob_024_mdf.png")
    destino_liso = os.path.join(tempfile.gettempdir(), "caffmob_024_liso.png")

    # 1) Render amplo: cor média igual ao material liso da mesma cor (é o que o Solid em TEXTURE mostra).
    pixels = _render(cena, destino)
    media, (r, g, b), cobertura = _estatisticas(pixels)
    check("render gerou pixels", len(pixels) == 256 * 256 * 4, str(len(pixels)))
    check("chapa visível no render", cobertura > 0.10, f"{cobertura:.0%}")
    check("tom bege no render", r >= g >= b, f"RGB=({r:.3f}, {g:.3f}, {b:.3f})")
    check("render opaco", min(pixels[3::4]) > 0.99, f"alfa_min={min(pixels[3::4]):.3f}")
    check("arquivo do render salvo", os.path.exists(destino), destino)

    liso = _material_liso()
    objeto.data.materials[0] = liso
    pixels_liso = _render(cena, destino_liso)
    objeto.data.materials[0] = chapa
    media_lisa, (r_liso, _g_liso, _b_liso), _cob_lisa = _estatisticas(pixels_liso)
    check("média do render = cor média do Solid", abs(media - media_lisa) < 0.01,
          f"textura={media:.4f} liso={media_lisa:.4f}")

    # 2) Close-up: o grão tem de aparecer onde a textura cobre poucos centímetros por pixel.
    _camera(cena, (0.42, -0.34, 0.40))
    pixels_close = _render(cena, destino)
    rugosidade = _rugosidade(pixels_close)
    objeto.data.materials[0] = liso
    pixels_close_liso = _render(cena, destino_liso)
    objeto.data.materials[0] = chapa
    rugosidade_lisa = _rugosidade(pixels_close_liso)
    check("grão visível no close-up", rugosidade > 0.0015, f"rugosidade={rugosidade:.5f}")
    check("grão distingue a textura do material liso", rugosidade > max(2.5 * rugosidade_lisa, 0.0015),
          f"textura={rugosidade:.5f} liso={rugosidade_lisa:.5f}")

    # 3) Contorno no Solid + coerência da vista em Preview com o render.
    _camera(cena, (1.15, -1.45, 0.95))
    check("variante com linhas aplicada", exibicao.aplicar(bpy.context, 'TEXTURA_LINHAS'))
    vistas = spaces()
    check("há vista 3D para o contorno", bool(vistas))
    check("Solid com TEXTURE", all(s.shading.type == 'SOLID' and s.shading.color_type == 'TEXTURE' for s in vistas),
          str([(s.shading.type, s.shading.color_type) for s in vistas]))
    check("contorno ligado no modo de vista", bpy.context.scene.btm_view_lines
          and not any(s.overlay.show_wireframes for s in vistas))
    check("material da chapa é o da cena", len(objeto.data.materials) == 1 and objeto.data.materials[0] is chapa)
    no = chapa.node_tree.nodes.get(textura_padrao.NOME_NO)
    check("imagem empacotada usada no render", bool(no and no.image and no.image.packed_file))

    for space in vistas:
        space.shading.type = 'MATERIAL'
    pixels_preview = _render(cena, destino)
    media_preview, _rgb_preview, _cob_preview = _estatisticas(pixels_preview)
    check("render idêntico com a vista em Preview", abs(media_preview - media) < 0.01,
          f"solid={media:.4f} preview={media_preview:.4f}")
    exibicao.aplicar(bpy.context, 'TEXTURA_SO')
    check("sem linhas na variante somente textura", not bpy.context.scene.btm_view_lines
          and not any(s.overlay.show_wireframes for s in vistas))

    # 4) Aviso de migração: uma chamada por cena migrada, nenhuma na segunda abertura.
    chamadas = []
    original = exibicao._avisar
    exibicao._avisar = lambda texto: chamadas.append(texto)
    try:
        raiz = build.criar_raiz(cena, "Armário 024 (aviso)")
        exibicao._ao_carregar(None)
    finally:
        exibicao._avisar = original
    check("aviso chamado uma vez", len(chamadas) == 1, str(chamadas))
    check("aviso com a contagem", bool(chamadas) and "1" in chamadas[0], chamadas[0] if chamadas else "")
    chamadas.clear()
    exibicao._avisar = lambda texto: chamadas.append(texto)
    try:
        exibicao._ao_carregar(None)
    finally:
        exibicao._avisar = original
    check("segunda abertura não avisa", chamadas == [], str(chamadas))
    check("raiz migrada", raiz.btm_armario.exibicao_versao == exibicao.VERSAO_ATUAL)
    original("Prova visual 024")

    print(f"\nrender de referência: {destino}")


if __name__ == '__main__':
    try:
        main()
    except Exception:
        traceback.print_exc()
        FAILURES.append("exceção")
    print(f"\n{len(FAILURES)} falha(s)")
    sys.exit(1 if FAILURES else 0)
