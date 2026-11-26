"""Prova no Blender do card branco de detalhe do módulo na Biblioteca (2026-11-26).

Roda com janela (não em --background), para o card desenhar:

    blender.exe --factory-startup --enable-event-simulate --python-exit-code 1 --python tests/blender_biblioteca_detalhe.py

Abre a Biblioteca na categoria Cozinha, seleciona um módulo da grade (o mesmo `ops_detail.abrir` que o clique chama),
preenche largura, altura e profundidade diferentes do padrão e troca o ambiente para Dormitório, recusa uma medida
acima do máximo (sem criar peça), confirma a medida válida e confere o objeto resultante (`btm_cabinet`). Salva um PNG
do card aberto em `biblioteca_detalhe.png`, na raiz do projeto, e encerra com código 0 ou 1.
"""

import os
import sys
from pathlib import Path

import bpy  # type: ignore

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(Path(__file__).resolve().parent))
import _blender_env  # noqa: E402,F401
from caffmob_draw.library_panel import draw, ops_detail  # noqa: E402

FAILURES = []
STATE = None
ALVO = {}


def check(name, ok, detail=""):
    print(("OK   " if ok else "FALHA ") + name, detail, flush=True)
    if not ok:
        FAILURES.append(name)


def _conta_objetos():
    return len(bpy.data.objects)


def run_checks():
    global STATE
    try:
        bpy.context.preferences.view.show_splash = False   # sem a abertura cobrindo o card no print
    except Exception:
        pass
    STATE = bpy.context.window_manager.btm_library
    STATE.tab, STATE.category, STATE.search, STATE.scroll = 'BLOCKS', "Cozinha", "", 0.0
    STATE.mode, STATE.pinned, STATE.rect = 'MAX', True, (0.0, 0.0, 0.0, 0.0)

    entries = draw.grid_entries(STATE)
    target = next((e for e in entries if e.get('kind') == 'MODEL'), None)
    check("grade tem módulo", target is not None)
    if target is None:
        return
    ALVO.update(target)

    abriu = ops_detail.abrir(bpy.context, draw.entry_key(target))
    check("clique no módulo abre o card", abriu and STATE.detail_open)
    check("nome no card", STATE.detail_name == target["name"], STATE.detail_name)

    # Pré-preenchido pelo catálogo.
    padrao_w = float(target["size_mm"][0])
    check("largura pré-preenchida", abs(STATE.detail_width - padrao_w) < 1e-4, str(STATE.detail_width))
    check("card começa em Cozinha", STATE.detail_line == 'COZ', STATE.detail_line)

    padrao = (STATE.detail_width, STATE.detail_height, STATE.detail_depth)

    # Recusa acima do padrão de chapa máxima: nada é criado e a mensagem aparece.
    antes = _conta_objetos()
    STATE.detail_depth = 2000.0
    check("medida acima do máximo é recusada", ops_detail.confirmar(bpy.context) is False)
    check("recusa mostra mensagem", bool(STATE.detail_error), STATE.detail_error)
    check("recusa não cria peça", _conta_objetos() == antes)
    check("card continua aberto", STATE.detail_open)

    # Medidas e ambiente diferentes do padrão, dentro dos limites.
    largura = min(1200.0, padrao[0] + 100.0)
    altura = min(2700.0, padrao[1] + 80.0)
    profundidade = max(200.0, padrao[2] - 50.0)
    STATE.detail_width, STATE.detail_height, STATE.detail_depth = largura, altura, profundidade
    STATE.detail_line = 'DOR'
    STATE.detail_thickness = ops_detail.espessura(bpy.context, 'DOR')
    STATE.detail_error = ""
    ALVO.update(width=largura, height=altura, depth=profundidade, line='DOR')
    check("medidas válidas aceitas", ops_detail.validar(bpy.context, STATE)[0])
    draw.tag_redraw(bpy.context)


def capture_and_confirm():
    path = str(ROOT / "biblioteca_detalhe.png")
    try:
        bpy.ops.screen.screenshot(filepath=path)
        check("print do card aberto", os.path.exists(path), path)
    except Exception as exc:                     # a prova de comportamento não depende da imagem
        print("PRINT FALHOU", exc, flush=True)

    antes = _conta_objetos()
    ok = ops_detail.confirmar(bpy.context)
    check("confirmar insere", ok)
    check("card fecha depois de inserir", not STATE.detail_open)
    check("inseriu uma peça", _conta_objetos() > antes)

    obj = bpy.context.active_object
    check("módulo ativo", obj is not None and hasattr(obj, 'btm_cabinet'))
    if obj is not None and hasattr(obj, 'btm_cabinet'):
        cab = obj.btm_cabinet
        check("largura do objeto", abs(cab.width - ALVO["width"] / 1000.0) < 1e-4, str(cab.width))
        check("altura do objeto", abs(cab.height - ALVO["height"] / 1000.0) < 1e-4, str(cab.height))
        check("profundidade do objeto", abs(cab.depth - ALVO["depth"] / 1000.0) < 1e-4, str(cab.depth))
        check("ambiente do objeto", cab.line == 'DOR', cab.line)
        check("modelo gravado no objeto", obj.get('btm_model_id') == ALVO.get("model"), str(obj.get('btm_model_id')))

    print("RESULTADO", "OK" if not FAILURES else "FALHA", FAILURES, flush=True)
    os._exit(1 if FAILURES else 0)


run_checks()
bpy.app.timers.register(capture_and_confirm, first_interval=2.5)
