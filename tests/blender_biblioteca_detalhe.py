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
from mathutils import Vector  # type: ignore

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(Path(__file__).resolve().parent))
import _blender_env  # noqa: E402,F401
from caffmob_draw.library_panel import draw, ops_detail, ops_drag  # noqa: E402

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

    # Filtro de acervo por ambiente segue íntegro (entrega anterior).
    cozinha = {e["name"] for e in draw.grid_entries(STATE)}
    STATE.category = "Banheiro"
    banheiro = {e["name"] for e in draw.grid_entries(STATE)}
    STATE.category = "Cozinha"
    check("filtro por ambiente intacto", "Gabinete de banheiro" in banheiro and not (cozinha & banheiro),
          str(sorted(cozinha & banheiro)))

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

    # Recusa específica da chapa máxima: uma chapa pequena no Padrão faz uma medida válida para o módulo exceder a
    # chapa; a mensagem precisa citar a chapa e nada pode ser criado. O padrão original é restaurado no fim.
    from caffmob_draw.data import dimension_schema as schema
    from caffmob_draw.standards import api as standards_api
    original = standards_api.active_definition(bpy.context.scene)
    temporaria = standards_api.duplicate_definition(bpy.context.scene, original, "Teste chapa do card")
    standards_api.set_values(temporaria, {schema.max_key('sheet_width_max'): 600.0,
                                          schema.max_key('sheet_length_max'): 1000.0})
    STATE.detail_width, STATE.detail_height, STATE.detail_depth = 1200.0, 2700.0, 900.0
    STATE.detail_line, STATE.detail_error = 'DOR', ""
    STATE.detail_thickness = ops_detail.espessura(bpy.context, 'DOR')
    antes = _conta_objetos()
    check("medida acima da chapa é recusada", ops_detail.confirmar(bpy.context) is False)
    check("recusa de chapa mostra mensagem", "chapa" in STATE.detail_error.lower(), STATE.detail_error)
    check("recusa de chapa não cria peça", _conta_objetos() == antes)
    check("card continua aberto após recusa de chapa", STATE.detail_open)
    standards_api.set_active(bpy.context.scene, original)
    standards_api.remove_definition(bpy.context.scene, temporaria)

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
        from caffmob_draw.cabinet_editor import structures_core
        check("estrutura do Editor V2 no módulo",
              bool(cab.structure_id) and structures_core.get(cab.structure_id) is not None, cab.structure_id)

    # Arraste: a soltura usa as medidas e o ambiente definidos no card, sem passar pelo mouse.
    class _Arraste:
        width_mm, height_mm, depth_mm, line = 600.0, 700.0, 450.0, 'SAL'
        entry = dict(ALVO)

        @staticmethod
        def report(*_args, **_kwargs):
            pass

    antes = _conta_objetos()
    resultado = ops_drag.BTM_OT_LibraryDrag._drop_model(_Arraste(), bpy.context, Vector((2.0, 2.0, 0.0)))
    check("arraste insere", 'FINISHED' in resultado)
    check("arraste insere uma peça", _conta_objetos() > antes)
    arrastado = bpy.context.active_object
    if arrastado is not None and hasattr(arrastado, 'btm_cabinet'):
        cab = arrastado.btm_cabinet
        check("arraste usa largura do card", abs(cab.width - 0.6) < 1e-4, str(cab.width))
        check("arraste usa altura do card", abs(cab.height - 0.7) < 1e-4, str(cab.height))
        check("arraste usa profundidade do card", abs(cab.depth - 0.45) < 1e-4, str(cab.depth))
        check("arraste usa ambiente do card", cab.line == 'SAL', cab.line)

    # Preset sem variação: confirma com os valores do catálogo e continua inserindo.
    STATE.tab, STATE.category, STATE.search, STATE.scroll = 'BLOCKS', "Cozinha", "", 0.0
    preset = next((e for e in draw.grid_entries(STATE)
                   if e.get('kind') == 'PRESET' and not e.get('right_width_mm')
                   and e.get('corner_kind') in ('', 'NONE', None)), None)
    check("acervo tem preset sem variação", preset is not None)
    if preset is not None:
        check("preset abre o card", ops_detail.abrir(bpy.context, draw.entry_key(preset)))
        antes = _conta_objetos()
        check("preset confirma com o catálogo", ops_detail.confirmar(bpy.context))
        check("preset insere uma peça", _conta_objetos() > antes)
        preset_obj = bpy.context.active_object
        if preset_obj is not None and hasattr(preset_obj, 'btm_cabinet'):
            cab = preset_obj.btm_cabinet
            check("preset usa a largura do catálogo",
                  abs(cab.width - float(preset["size_mm"][0]) / 1000.0) < 1e-4, str(cab.width))
            check("preset grava o modelo", preset_obj.get('btm_model_id') == preset.get("model"))

    print("RESULTADO", "OK" if not FAILURES else "FALHA", FAILURES, flush=True)
    os._exit(1 if FAILURES else 0)


run_checks()
bpy.app.timers.register(capture_and_confirm, first_interval=2.5)
