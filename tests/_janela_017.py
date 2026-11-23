"""Sonda com janela da feature 017: painel, HUD e realce desenhados de verdade na vista 3D.

    xvfb-run -a blender --factory-startup --enable-event-simulate --python tests/_janela_017.py

Não é fumaça de regressão (não confere operador nenhum): é a conferência do que só existe com tela — a aba
`CAFFMob Draw` na barra lateral, os alternadores e o cartão do inspetor do HUD em `POST_PIXEL` e as arestas do realce
da peça escolhida. Salva as capturas em
`_reversa_forward/017-construtor-armario-v2/audit/janela/` e sai com o código do resultado.

O menu de contexto fica de fora: abri-lo exige clique direito na peça sob o cursor e a posição do menu não é estável
para conferência — os itens dele já são provados pela fumaça headless, com a camada falsa de layout.
"""

import os
import sys
import traceback
from pathlib import Path

import bpy
from bpy_extras import view3d_utils

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _blender_env as env  # noqa: E402
from caffmob_draw.armario_v2 import hud, panel  # noqa: E402

SHOTS = Path(__file__).resolve().parents[1] / "_reversa_forward" / "017-construtor-armario-v2" / "audit" / "janela"
FAILURES = []
DRAW_ERRORS = []
_hook = sys.excepthook


def _record(exc_type, exc, tb):
    """Erro dentro de um draw handler não derruba o Blender: fica aqui para a conferência."""
    DRAW_ERRORS.append("".join(traceback.format_exception(exc_type, exc, tb))[-400:])
    _hook(exc_type, exc, tb)


sys.excepthook = _record


def check(name, ok, detail=""):
    print(("OK   " if ok else "FALHA ") + name, detail, flush=True)
    if not ok:
        FAILURES.append(name)


def view3d(ctx):
    win = ctx.window_manager.windows[0]
    area = max((a for a in win.screen.areas if a.type == 'VIEW_3D'), key=lambda a: a.width * a.height)
    region = next(r for r in area.regions if r.type == 'WINDOW')
    return win, area, region


def selecionar(ctx, obj):
    for outro in ctx.view_layer.objects:
        outro.select_set(False)
    ctx.view_layer.objects.active = obj
    if obj is not None:
        obj.select_set(True)


def redraw(ctx):
    for window in ctx.window_manager.windows:
        for area in window.screen.areas:
            area.tag_redraw()


def shot(ctx, nome):
    SHOTS.mkdir(parents=True, exist_ok=True)
    caminho = SHOTS / nome
    win = ctx.window_manager.windows[0]
    with ctx.temp_override(window=win):
        bpy.ops.screen.screenshot(filepath=str(caminho))
    return caminho


def enquadrar(ctx, area, region):
    """Centraliza a vista nos objetos (a inicial é de câmera e pode cortar o armário)."""
    win = ctx.window_manager.windows[0]
    with ctx.temp_override(window=win, area=area, region=region):
        bpy.ops.view3d.view_all()


def cantos_na_vista(ctx, peca, area, region):
    dados = area.spaces.active.region_3d
    with ctx.temp_override(window=ctx.window_manager.windows[0], area=area, region=region, region_data=dados):
        return [view3d_utils.location_3d_to_region_2d(region, dados, canto) for canto in hud._pontos_da_peca(peca)]


class _SondaPainel(bpy.types.Operator):
    """Desenha o painel do armário v2 num popup largo, só para a captura desta sonda"""

    bl_idname = "caffmob.armario_v2_sonda_painel"
    bl_label = "Construtor de Armário v2 (sonda)"

    def draw(self, context):
        panel.draw_painel(self.layout, context)

    def invoke(self, context, _event):
        return context.window_manager.invoke_popup(self, width=480)

    def execute(self, _context):
        return {'CANCELLED'}


def script():
    ctx = bpy.context
    bpy.utils.register_class(_SondaPainel)
    env.clean_scene()
    win, area, region = view3d(ctx)
    win.event_simulate('ESC', 'PRESS', x=10, y=10)          # fecha a tela de boas-vindas
    win.event_simulate('ESC', 'RELEASE', x=10, y=10)
    area.spaces.active.show_region_ui = True
    yield 0.6
    ui = next(r for r in area.regions if r.type == 'UI')
    ui.active_panel_category = "CAFFMob Draw"
    yield 0.4

    with ctx.temp_override(window=win, area=area, region=region):
        resultado = bpy.ops.caffmob.cabinet_editor()
    root = bpy.context.view_layer.objects.active
    check("Abrir cria o armário e o painel entra em cena",
          resultado == {'FINISHED'} and root is not None and panel.BTM_PT_ArmarioV2.poll(ctx), str(resultado))
    enquadrar(ctx, area, region)
    redraw(ctx)
    yield 0.8
    vazio = shot(ctx, "1-armario-vazio.png")
    armario = root.btm_armario
    check("armário vazio mostra os alternadores do HUD",
          bool(hud.botoes_da_estrutura(armario, region.width)) and hud._vazio(armario),
          f"{len(hud.botoes_da_estrutura(armario, region.width))} botão(ões)")

    # Uma gaveta dá uma peça escolhível; gerar monta a caixa e as frentes.
    gaveta = armario.gavetas.add()
    gaveta.vao, gaveta.indice, gaveta.altura, gaveta.modelo = 's0', 0, 700.0, 's_cf_reta'
    with ctx.temp_override(window=win, area=area, region=region):
        gerado = bpy.ops.caffmob.armario_v2_gerar()
    frente = next((filho for filho in root.children if filho.btm_armario_parte.papel == 'FRENTE_GAVETA'), None)
    selecionar(ctx, frente)
    armario.aba = 'GAVETAS'
    enquadrar(ctx, area, region)
    redraw(ctx)
    yield 0.8
    peca = shot(ctx, "2-peca-escolhida.png")

    check("Gerar e escolher a frente deixa a peça no inspetor",
          gerado == {'FINISHED'} and frente is not None and hud._peca(ctx) is frente, str(gerado))
    # Nome, medidas e papel sempre; o aviso `Fora da chapa` é uma quarta linha e só aparece quando a peça passa.
    linhas = hud.linhas_do_inspetor(frente, bpy.context.scene.btm_armario_contrato)
    avisos = [texto for texto, tipo in linhas if tipo == 'warning']
    check("o cartão do inspetor tem o nome, as medidas e o papel (aviso só fora da chapa)",
          linhas[0][0] == frente.name and len(linhas) == 3 + len(avisos),
          str([(texto, tipo) for texto, tipo in linhas]))
    cantos = cantos_na_vista(ctx, frente, area, region)
    check("os oito cantos da peça projetam dentro da vista (o realce desenha)",
          len(cantos) == 8 and all(ponto is not None for ponto in cantos), f"{sum(p is not None for p in cantos)}/8")

    # A barra lateral da vista abre com o painel hospedeiro da 005 por cima; o painel da 017 é desenhado num popup
    # largo para a conferência visual do corpo inteiro (mesmo `draw_painel`, com `layout` de verdade).
    centro = (area.x + area.width // 3, area.y + area.height // 2)
    win.event_simulate('MOUSEMOVE', 'NOTHING', x=centro[0], y=centro[1])
    yield 0.3
    with ctx.temp_override(window=win, area=area, region=region):
        aberto = bpy.ops.caffmob.armario_v2_sonda_painel('INVOKE_DEFAULT')
    yield 0.8
    painel = shot(ctx, "3-painel-em-popup.png")
    check("o painel da 017 desenha o corpo inteiro num popup", aberto == {'RUNNING_MODAL'}, str(aberto))
    win.event_simulate('ESC', 'PRESS', x=10, y=10)
    win.event_simulate('ESC', 'RELEASE', x=10, y=10)
    yield 0.4
    check("painel, HUD e realce desenharam sem erro de Python", not DRAW_ERRORS, "\n".join(DRAW_ERRORS[:3]))
    tamanhos = {caminho.name: caminho.stat().st_size for caminho in (vazio, peca, painel)}
    check("capturas salvas", all(tamanho > 20_000 for tamanho in tamanhos.values()), str(tamanhos))
    bpy.utils.unregister_class(_SondaPainel)
    print(f"capturas em {SHOTS}", flush=True)


_gen = script()


def tick():
    try:
        return next(_gen)
    except StopIteration:
        pass
    except Exception:
        traceback.print_exc()
        FAILURES.append("exceção no roteiro")
    print(f"janela_017: {'OK' if not FAILURES else 'FALHAS: ' + ', '.join(FAILURES)}", flush=True)
    os._exit(1 if FAILURES else 0)


bpy.app.timers.register(tick, first_interval=2.0)
