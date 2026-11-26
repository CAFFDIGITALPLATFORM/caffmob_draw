"""Prova visual do painel do Construtor de Armários v2 (021, T033/A004).

Roda com janela real e salva um PNG do painel lateral na categoria CAFFMob Draw:

    blender.exe --factory-startup --python-exit-code 1 --python tests/blender_021_panel_visual.py

Cria o armário vazio pelo operador `caffmob.cabinet_editor`, monta a caixa, seleciona a raiz, abre a barra lateral
e deixa a aba Estrutura ativa. O PNG fica em `_reversa_forward/021-plano-corte-camadas-gaveteiro/audit/painel-021.png`.
"""

import os
import sys
from pathlib import Path

import bpy  # type: ignore

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(Path(__file__).resolve().parent))
import _blender_env  # noqa: E402,F401

SAIDA = ROOT / "_reversa_forward/021-plano-corte-camadas-gaveteiro/audit/painel-021.png"


def _raiz():
    return next((obj for obj in bpy.data.objects if getattr(obj, 'btm_armario', None) is not None), None)


def _area_3d():
    window = bpy.context.window_manager.windows[0]
    return window, next(area for area in window.screen.areas if area.type == 'VIEW_3D')


def preparar():
    try:
        bpy.context.preferences.view.show_splash = False
    except Exception:
        pass
    root = _raiz()
    if root is not None:
        for other in bpy.context.selected_objects:
            other.select_set(False)
        root.select_set(True)
        bpy.context.view_layer.objects.active = root
        root.btm_armario.aba = 'ESTRUTURA'
    window, area = _area_3d()
    area.spaces.active.show_region_ui = True
    area.tag_redraw()
    ui = next(region for region in area.regions if region.type == 'UI')
    print("REGIAO", window.width, window.height, ui.x, ui.y, ui.width, ui.height, flush=True)
    # Fecha a splash do Blender e clica na aba CAFFMob Draw. `Region.active_panel_category` é somente leitura neste
    # build, então a aba é escolhida pelo mesmo clique que o usuário daria, na faixa vertical à esquerda do painel.
    window.event_simulate(type='ESC', value='PRESS')
    bpy.app.timers.register(clicar_aba, first_interval=0.8)


def clicar_aba():
    window, area = _area_3d()
    ui = next(region for region in area.regions if region.type == 'UI')
    x = ui.x + ui.width - 7
    y = 130  # centro da aba CAFFMob Draw, em coordenadas de tela (origem no topo)
    print("CLIQUE", x, y, flush=True)
    window.event_simulate(type='MOUSEMOVE', value='NOTHING', x=x, y=y)
    window.event_simulate(type='LEFTMOUSE', value='PRESS', x=x, y=y)
    window.event_simulate(type='LEFTMOUSE', value='RELEASE', x=x, y=y)
    # O painel do armário v2 fica no fim da categoria, depois dos painéis antigos: rola a barra lateral até ele.
    window.event_simulate(type='MOUSEMOVE', value='NOTHING', x=1100, y=500)
    for _ in range(14):
        window.event_simulate(type='WHEELDOWNMOUSE', value='PRESS', x=1100, y=500)
    bpy.app.timers.register(capturar, first_interval=2.0)


def capturar():
    try:
        bpy.ops.screen.screenshot(filepath=str(SAIDA))
        print("PRINT", SAIDA, SAIDA.exists(), flush=True)
    except Exception as exc:
        print("PRINT FALHOU", exc, flush=True)
        os._exit(1)
    os._exit(0)


resultado = bpy.ops.caffmob.cabinet_editor()
root = _raiz()
print("ABRIR", resultado, root is not None, flush=True)
if root is None:
    os._exit(1)
for other in bpy.context.selected_objects:
    other.select_set(False)
root.select_set(True)
bpy.context.view_layer.objects.active = root
print("MONTAR", bpy.ops.caffmob.armario_v2_montar_caixa(), flush=True)
bpy.app.timers.register(preparar, first_interval=1.0)
