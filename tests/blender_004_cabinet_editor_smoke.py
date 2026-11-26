"""Teste de fumaça do Editor de Armário (feature 004), atualizado para o Construtor v2 (021/T027).

O editor 2D antigo saiu do registro em T027; `caffmob.cabinet_editor` hoje é o abridor do armário v2. Este ensaio
mantém o propósito da feature 004 — abrir, montar, alterar e cancelar — no contrato atual, e confirma que o móvel da
construção antiga continua recusado com o motivo, sem criar armário nenhum.

Precisa de janela (não roda em --background), numa instância própria (encerra com o código do resultado):
    blender --factory-startup --enable-event-simulate --python-exit-code 1 --python tests/blender_004_cabinet_editor_smoke.py
"""

import os
import sys
import traceback
from pathlib import Path

import bpy

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _blender_env as env  # noqa: E402
from caffmob_draw import hb_utils  # noqa: E402
from caffmob_draw.armario_v2 import build  # noqa: E402
from caffmob_draw.product_libraries.frameless import types_frameless as tf  # noqa: E402

FAILURES = []


def check(name, ok, detail=""):
    print(("OK   " if ok else "FALHA ") + name, detail, flush=True)
    if not ok:
        FAILURES.append(name)


def raiz():
    """Raiz v2: o EMPTY na coleção do construtor (o PointerProperty `btm_armario` existe em todo objeto)."""
    return next((obj for obj in bpy.data.objects if obj.type == 'EMPTY'
                 and any(colecao.name == build.COLECAO for colecao in obj.users_collection)), None)


def pecas(root):
    return [filho for filho in root.children if getattr(filho, 'btm_armario_parte', None) is not None]


def papeis(root):
    return sorted(getattr(item.btm_armario_parte, 'papel', '') for item in pecas(root))


def selecionar(obj):
    for other in bpy.context.selected_objects:
        other.select_set(False)
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj


def view3d(ctx):
    win = ctx.window_manager.windows[0]
    area = next(a for a in win.screen.areas if a.type == 'VIEW_3D')
    region = next(r for r in area.regions if r.type == 'WINDOW')
    return win, area, region


def abrir(ctx):
    win, area, region = view3d(ctx)
    with ctx.temp_override(window=win, area=area, region=region):
        return bpy.ops.caffmob.cabinet_editor('INVOKE_DEFAULT')


def script():
    ctx = bpy.context
    yield 0.5

    # 1. Móvel da construção antiga: a guarda recusa e não cria raiz v2.
    env.clean_scene()
    legado = tf.BaseCabinet()
    legado.create("Balcao")
    hb_utils.run_calc_fix_until_stable(ctx, legado.obj)
    selecionar(legado.obj)
    win, area, region = view3d(ctx)
    with ctx.temp_override(window=win, area=area, region=region, active_object=legado.obj, object=legado.obj):
        aceita = bpy.ops.caffmob.cabinet_editor.poll()
    check("móvel legado recusado pelo construtor v2", not aceita)
    check("recusa não cria armário v2", raiz() is None)

    # 2. Projeto limpo: abrir cria o armário vazio e semeia o contrato.
    env.clean_scene()
    resultado = abrir(ctx)
    root = raiz()
    check("abrir num projeto limpo cria o armário vazio", resultado == {'FINISHED'} and root is not None,
          str(resultado))
    check("abrir não cria peça", root is not None and not pecas(root))
    check("abrir guarda o instantâneo", bool(root.btm_armario.snapshot) if root is not None else False)
    check("abrir semeia o contrato de chapas", ctx.scene.btm_armario_contrato.configurado)

    # 3. Montar Caixa gera as quatro chapas e o fundo.
    selecionar(root)
    resultado = bpy.ops.caffmob.armario_v2_montar_caixa()
    check("Montar Caixa cria as cinco chapas", resultado == {'FINISHED'} and papeis(root) == [
        'BASE_INF', 'BASE_SUP', 'FUNDO', 'LATERAL', 'LATERAL'], str(papeis(root)))
    check("Montar Caixa marca o armário como gerado", root.btm_armario.gerado)

    # 4. Aplicar fixa o ponto; alterar e Cancelar devolve o estado aplicado, sem perder as chapas.
    resultado = bpy.ops.caffmob.armario_v2_aplicar()
    largura0 = float(root.btm_armario.largura)
    root.btm_armario.largura = largura0 + 100.0
    gerou = bpy.ops.caffmob.armario_v2_gerar()
    check("alterar a largura gera o armário", gerou == {'FINISHED'}
          and abs(float(root.btm_armario.largura) - (largura0 + 100.0)) < 1e-4, str(root.btm_armario.largura))
    resultado = bpy.ops.caffmob.armario_v2_cancelar()
    check("Cancelar volta a largura aplicada", resultado == {'FINISHED'}
          and abs(float(root.btm_armario.largura) - largura0) < 1e-4, str(root.btm_armario.largura))
    check("Cancelar mantém as cinco chapas", len(pecas(root)) >= 5, str(len(pecas(root))))

    print("RESULTADO", "OK" if not FAILURES else "FALHA", FAILURES, flush=True)
    os._exit(1 if FAILURES else 0)


_gen = script()


def tick():
    try:
        return next(_gen)
    except StopIteration:
        pass
    except Exception:
        traceback.print_exc()
        FAILURES.append("exceção no roteiro")
    print(f"blender_004_cabinet_editor_smoke: {'OK' if not FAILURES else 'FALHAS: ' + ', '.join(FAILURES)}",
          flush=True)
    os._exit(1 if FAILURES else 0)


bpy.app.timers.register(tick, first_interval=2.0)
