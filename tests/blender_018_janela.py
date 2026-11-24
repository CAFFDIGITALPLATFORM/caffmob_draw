"""Conferência com janela da 018 (T024, T019): o campo "Veio (graus)", o aviso de ângulo e o destaque do conta-gotas.

    blender --factory-startup --enable-event-simulate --python tests/blender_018_janela.py

O `--background` não desenha painel nem roda o `POST_PIXEL` da vista: até aqui o campo, o aviso e a caixa da peça só
tinham sido provados por sonda e por estado. Este ensaio abre a janela de verdade, deixa a barra lateral do addon
desenhar na aba em que ela vive (só a seção Selecionado aberta, no modo Completa) e confere:

A. O painel desenha o campo "Veio (graus)" da chapa do armário v2 com 45° e pede o texto do aviso; com 90° pede o
   campo e não pede o aviso. O desenho é o de verdade, num `UILayout` da janela.
B. O destaque do conta-gotas pinta a caixa e o nome da parte na vista: a contagem de pixels na cor do destaque sai de
   zero (conta-gotas fechado) para centenas (apontando a peça).

As capturas ficam em `smoke_018_janela_veio.png`, `smoke_018_janela_veio_90.png` e `smoke_018_janela_destaque.png`
na raiz (ignoradas pelo git).
"""

import os
import sys
import tempfile
import traceback
from pathlib import Path

import bpy  # type: ignore
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
EVIDENCIAS = ROOT / '_reversa_forward' / '018-textura-uv-veio' / 'evidencias'
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / 'tests'))
import _blender_env as env  # noqa: E402,F401  (caminho + addon registrado)
from caffmob_draw.armario_v2 import build, spec as spec_mod  # noqa: E402
from caffmob_draw.target import snapshot  # noqa: E402
from caffmob_draw.texture_library import pick  # noqa: E402
from caffmob_draw.ui import object_properties, sidebar_props  # noqa: E402
FALHAS = []
VISTOS = []
ANGULOS = []
SECOES = []                                     # (seção, objeto, tipo, detalhe) de cada desenho real
_draw_real = object_properties._draw_grain_angle
_secao_real = object_properties._draw_section
_tr_real = object_properties.tr


def check(nome, ok, detalhe=""):
    print(("OK   " if ok else "FALHA ") + nome, detalhe, flush=True)
    if not ok:
        FALHAS.append(nome)


def _espiao_angulo(layout, obj, grupo):
    ANGULOS.append(round(float(getattr(grupo, 'grain_angle', 0.0) or 0.0), 3))
    return _draw_real(layout, obj, grupo)


def _espiao_secao(layout, context, target, obj, section):
    SECOES.append((section.id, getattr(obj, 'name', None), target.kind, target.detail))
    return _secao_real(layout, context, target, obj, section)


def _espiao_tr(texto, contexto=None):
    VISTOS.append(texto)
    return _tr_real(texto, contexto)


object_properties._draw_grain_angle = _espiao_angulo
object_properties._draw_section = _espiao_secao
object_properties.tr = _espiao_tr


def _captura(win, nome):
    """Janela inteira: a conferência visual é da barra lateral junto com a vista."""
    EVIDENCIAS.mkdir(parents=True, exist_ok=True)
    caminho = os.path.join(EVIDENCIAS, 'smoke_018_janela_' + nome + '.png')
    with bpy.context.temp_override(window=win):
        bpy.ops.screen.screenshot(filepath=caminho)
    return caminho


def _rolar(win, area, vezes=12):
    """Rola a barra lateral até o fim: o campo e o aviso ficam no pé da seção Selecionado."""
    ui = next((r for r in area.regions if r.type == 'UI'), None)
    if ui is None:
        return
    x, y = ui.x + ui.width // 2, ui.y + ui.height // 2
    for _ in range(vezes):
        win.event_simulate('WHEELDOWNMOUSE', 'PRESS', x=x, y=y)
        win.event_simulate('WHEELDOWNMOUSE', 'RELEASE', x=x, y=y)


def _captura_vista(win, area, nome, temporaria=False):
    """Recorte da vista 3D; as capturas de apoio (sem destaque) ficam no temporário e as de prova, em evidencias."""
    pasta = tempfile.gettempdir() if temporaria else str(EVIDENCIAS)
    caminho = os.path.join(pasta, 'smoke_018_janela_' + nome + '.png')
    with bpy.context.temp_override(window=win, area=area):
        bpy.ops.screen.screenshot_area(filepath=caminho)
    return caminho


def _pixels(caminho, retangulo):
    imagem = bpy.data.images.load(caminho)
    largura, altura = imagem.size
    pixels = np.empty(largura * altura * 4, dtype=np.float32)
    imagem.pixels.foreach_get(pixels)
    bpy.data.images.remove(imagem)
    x, y, w, h = retangulo
    return pixels.reshape(altura, largura, 4)[y:y + h, x:x + w, :3]


def _pintados(antes, depois):
    """Pixels que mudaram entre as duas capturas: é o traço do destaque, sem depender da cor da madeira."""
    return int(np.count_nonzero(np.abs(depois - antes).sum(axis=2) > 0.08))


def script():
    ctx = bpy.context
    win = ctx.window_manager.windows[0]
    area = next(a for a in win.screen.areas if a.type == 'VIEW_3D')
    region = next(r for r in area.regions if r.type == 'WINDOW')
    try:                                                    # fecha a tela de abertura
        win.event_simulate('ESC', 'PRESS', x=region.x + 10, y=region.y + 10)
        win.event_simulate('ESC', 'RELEASE', x=region.x + 10, y=region.y + 10)
    except (RuntimeError, ValueError):
        pass
    env.clean_scene()
    spec = spec_mod.Spec(lateral_esq_ativa=True, lateral_dir_ativa=True, base_inf_ativa=True, porta_ativa=True)
    pecas = build.gerar(build.criar_raiz(ctx.scene), spec)
    porta = next(o for o in pecas if o.btm_armario_parte.papel == 'PORTA')
    for obj in ctx.scene.objects:
        obj.select_set(False)
    porta.select_set(True)
    ctx.view_layer.objects.active = porta
    area.spaces.active.show_region_ui = True
    st = ctx.window_manager.btm_sidebar
    for secao in ('build', 'insert', 'selected', 'check', 'project'):
        setattr(st, f'open_{secao}', secao == 'selected')
    for grupo, _aberto in sidebar_props.GROUPS:      # só os grupos da chapa abertos: o campo cabe na tela
        nome = f'open_group_{grupo}'
        if hasattr(st, nome):
            setattr(st, nome, grupo == 'sel_finish')        # só Acabamentos: o campo e o aviso cabem na tela
    # O addon só tem preferências quando está instalado; aqui vale o modo em que os campos todos aparecem.
    object_properties.panel_mode = lambda _context: 'COMPLETE'

    # A. campo e aviso, a 45° e a 90°
    porta.btm_armario_parte.grain_angle = 45.0
    for _ in range(4):
        snapshot.ensure(ctx)
        area.tag_redraw()
        yield 0.35
    VISTOS.clear()
    ANGULOS.clear()
    area.tag_redraw()
    yield 0.5
    vistos_45, angulos_45 = list(VISTOS), list(ANGULOS)
    _rolar(win, area)
    yield 0.4
    _captura(win, 'veio')

    porta.btm_armario_parte.grain_angle = 90.0
    for _ in range(3):
        snapshot.ensure(ctx)
        area.tag_redraw()
        yield 0.35
    VISTOS.clear()
    ANGULOS.clear()
    area.tag_redraw()
    yield 0.5
    vistos_90, angulos_90 = list(VISTOS), list(ANGULOS)
    yield 0.4
    _captura(win, 'veio_90')                          # a seção encurtou uma linha: o campo continua à vista

    rotulo = _tr_real("Veio (graus)")
    aviso = _tr_real("Ângulo do veio não é múltiplo de 90")
    check("A: campo desenhado com 45°", bool(angulos_45) and set(angulos_45) == {45.0} and rotulo in vistos_45,
          str(angulos_45))
    check("A: aviso pedido com 45°", aviso in vistos_45)
    check("A: campo desenhado com 90° e sem aviso",
          bool(angulos_90) and set(angulos_90) == {90.0} and rotulo in vistos_90 and aviso not in vistos_90,
          str(angulos_90))

    # B. destaque do conta-gotas
    with ctx.temp_override(window=win, area=area, region=region):
        bpy.ops.view3d.view_selected()
    area.tag_redraw()
    yield 0.5
    recorte = (region.x - area.x, region.y - area.y, region.width, region.height)
    antes = _pixels(_captura_vista(win, area, 'sem_destaque', temporaria=True), recorte)
    area.tag_redraw()
    yield 0.4
    parado = _pintados(antes, _pixels(_captura_vista(win, area, 'ainda_sem_destaque', temporaria=True), recorte))
    pick.iniciar(ctx, [porta])
    pick.apontar(porta)
    for _ in range(3):
        area.tag_redraw()
        yield 0.4
    pintados = _pintados(antes, _pixels(_captura_vista(win, area, 'destaque'), recorte))
    parte = pick.rotulo()
    pick.encerrar(ctx)
    check("B: a vista parada não muda entre duas capturas", parado == 0, str(parado))
    check("B: apontando a porta a caixa é pintada na vista", pintados >= 100, str(pintados))
    check("B: a parte apontada é a Porta", parte == "Porta", parte)
    print('seções desenhadas: %s' % [secao[0] for secao in SECOES[-4:]], flush=True)


_gen = script()


def tick():
    try:
        return next(_gen)
    except StopIteration:
        pass
    except Exception:
        traceback.print_exc()
        FALHAS.append("exceção no roteiro")
    print(f"blender_018_janela: {'OK' if not FALHAS else 'FALHAS: ' + ', '.join(FALHAS)}", flush=True)
    os._exit(1 if FALHAS else 0)


bpy.app.timers.register(tick, first_interval=2.0)
