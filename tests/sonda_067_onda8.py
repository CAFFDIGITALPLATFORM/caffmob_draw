"""Sonda em janela real da onda 8 da 067 (T210; D-44). Precisa de janela:

    OUT=/caminho/das/capturas xvfb-run -a -s "-screen 0 1600x1000x24" blender --factory-startup \\
        --enable-event-simulate --python tests/sonda_067_onda8.py

Sobre o ambiente sintético do MOBI (`_mobi_sintetico`), com eventos simulados:
1. a cena importada fica na unidade do projeto, e "Novas paredes" mostra 150 mm;
2. clicar na folha do portão no 3D seleciona o portão inteiro, e o painel reconhece a Porta do MOBI;
3. digitar 3000 na largura grava no documento pelo timer, e um Ctrl+Z na viewport volta a 3500;
4. A no editor de parede seleciona todas as paredes, no projeto do MOBI e no do addon.
Capturas em $OUT (scrot). Sai com 0 se tudo passou.
"""
import json
import os
import subprocess
import sys
import traceback

import bpy

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _blender_env  # noqa: E402,F401
import _fixtures_067 as fx  # noqa: E402
import _mobi_sintetico as ms  # noqa: E402
from bpy_extras import view3d_utils  # noqa: E402
from mathutils import Euler, Vector  # noqa: E402
import math  # noqa: E402

OUT = os.environ.get('OUT', '/tmp')
FALHAS = []


def check(ok, texto, detalhe=''):
    print(('OK   ' if ok else 'FALHA ') + texto + (f' ({detalhe})' if detalhe and not ok else ''), flush=True)
    if not ok:
        FALHAS.append(texto)


def foto(nome):
    subprocess.run(['scrot', '-o', os.path.join(OUT, f'onda8_{nome}.png')], check=False)


def largura():
    return next(a for a in json.loads(bpy.context.scene['caffmob_ambiente'])['aberturas'] if a['id'] == ms.PORTAO)['largura']


def area_3d():
    win = bpy.context.window_manager.windows[0]
    area = next(a for a in win.screen.areas if a.type == 'VIEW_3D')
    region = next(r for r in area.regions if r.type == 'WINDOW')
    return win, area, region


def script():
    ctx = bpy.context
    for o in list(ctx.scene.objects):
        bpy.data.objects.remove(o, do_unlink=True)
    _documento, objetos = fx.ambiente_mobi_sintetico()
    bpy.ops.ed.undo_push(message='ambiente')
    win, area, region = area_3d()
    space = area.spaces.active
    space.show_region_ui = True
    win.event_simulate(type='ESC', value='PRESS', x=region.x + 20, y=region.y + 20)     # fecha a tela de abertura
    win.event_simulate(type='ESC', value='RELEASE', x=region.x + 20, y=region.y + 20)
    for o in ctx.selected_objects:
        o.select_set(False)
    # Vista de frente para o portão (trecho 2, em x = 30 m, de frente para -X), a 7 m.
    folha = objetos['folha']
    centro = sum((folha.matrix_world @ Vector(c) for c in folha.bound_box), Vector()) / 8
    rv3d = space.region_3d
    rv3d.view_perspective = 'PERSP'
    rv3d.view_location = centro
    rv3d.view_rotation = Euler((math.radians(80), 0.0, math.radians(90))).to_quaternion()
    rv3d.view_distance = 7.0
    yield 1.0

    # 1. unidade
    cena = ctx.scene
    check(cena.unit_settings.length_unit == 'MILLIMETERS', 'cena importada na unidade do projeto (mm)')

    # 2. clique na folha
    p = view3d_utils.location_3d_to_region_2d(region, space.region_3d, centro)
    x, y = region.x + int(p.x), region.y + int(p.y)
    win.event_simulate(type='MOUSEMOVE', value='NOTHING', x=x, y=y)
    win.event_simulate(type='LEFTMOUSE', value='PRESS', x=x, y=y)
    win.event_simulate(type='LEFTMOUSE', value='RELEASE', x=x, y=y)
    yield 0.5
    win.event_simulate(type='MOUSEMOVE', value='NOTHING', x=x + 40, y=y + 40)    # redesenho: o normalizador roda
    yield 1.5
    raiz = next(o for o in cena.objects if o.get('caffmob_tipo') == 'abertura' and o.get('caffmob_id') == ms.PORTAO)
    check(ctx.view_layer.objects.active is raiz, 'clique na folha seleciona o portão inteiro',
          getattr(ctx.view_layer.objects.active, 'name', None))
    from caffmob_draw.target import snapshot
    alvo = snapshot.ensure(ctx)
    check(alvo is not None and alvo.library == 'MOBI' and alvo.detail == 'DOOR', 'o painel reconhece a Porta do MOBI',
          str(alvo and (alvo.kind, alvo.library)))
    foto('1_portao_selecionado')

    # 3. largura pelo campo + Ctrl+Z
    ctx.window_manager.btm_mobi.largura = '3000'
    yield 1.5
    check(largura() == 3000, 'digitar 3000 grava no documento pelo timer', largura())
    foto('2_largura_3000')
    cx, cy = region.x + region.width // 2, region.y + region.height // 2
    win.event_simulate(type='MOUSEMOVE', value='NOTHING', x=cx, y=cy)
    win.event_simulate(type='Z', value='PRESS', x=cx, y=cy, ctrl=True)
    win.event_simulate(type='Z', value='RELEASE', x=cx, y=cy, ctrl=True)
    yield 1.5
    check(largura() == 3500, 'um Ctrl+Z volta a 3500', largura())

    # 4. A no editor de parede (projeto do MOBI); o desfazer recarregou a cena
    cena = ctx.scene
    parede = next(o for o in cena.objects if o.get('caffmob_tipo') == 'parede')
    ctx.view_layer.objects.active = parede
    with ctx.temp_override(window=win, area=area, region=region):
        bpy.ops.caffmob.wall_editor('INVOKE_DEFAULT')
    yield 2.0
    from caffmob_draw.walls2d import props
    from caffmob_draw.walls2d import window as w2d
    s = props.session()
    ewin, _earea, ereg = w2d.editor_area(ctx)
    ex, ey = ereg.x + ereg.width // 2, ereg.y + ereg.height // 2
    ewin.event_simulate(type='MOUSEMOVE', value='NOTHING', x=ex, y=ey)
    ewin.event_simulate(type='A', value='PRESS', x=ex, y=ey)
    ewin.event_simulate(type='A', value='RELEASE', x=ex, y=ey)
    yield 0.5
    check(len(s.v2.selecionadas) == 4, 'A seleciona as quatro paredes no projeto do MOBI', len(s.v2.selecionadas))
    foto('3_editor_mobi_A')
    # o mesmo editor, com um plano do projeto do addon no lugar do documento do MOBI
    from caffmob_draw.walls2d import model
    s.v2 = None
    s.plan = model.WallPlan([model.rectangle(4.0, 3.0)])
    s.multi, s.selected = [], None
    s.view.fit(s.plan.bounds(), margin=0.15)
    ewin.event_simulate(type='A', value='PRESS', x=ex, y=ey)
    ewin.event_simulate(type='A', value='RELEASE', x=ex, y=ey)
    yield 0.5
    check(len(s.multi) == 4, 'A seleciona as quatro paredes no projeto do addon', len(s.multi))
    s.redraw()
    yield 0.6
    s.redraw()                                      # o painel lateral refaz a altura no redesenho seguinte
    yield 0.6
    foto('4_editor_addon_A')


g = script()


def tick():
    try:
        return next(g)
    except StopIteration:
        pass
    except Exception:
        traceback.print_exc()
        FALHAS.append('exceção')
    print('RESULTADO', 'VERDE' if not FALHAS else 'VERMELHO: ' + ', '.join(FALHAS), flush=True)
    os._exit(1 if FALHAS else 0)


bpy.app.timers.register(tick, first_interval=2.0)
