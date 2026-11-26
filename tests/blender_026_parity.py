"""Ensaios dirigidos da paridade 026 no Blender, sem GUI e sem `--background`.

    blender --factory-startup --enable-event-simulate --python-exit-code 1 --python tests/blender_026_parity.py

Prova por execução: export JSON/cutlist, vista, tema, Apenas Laterais, medida, duplicata que sobrevive ao Gerar,
menu de contexto e o caminho modal do arraste (press → move → release) por hook, sem depender de screenshot.
"""

import json
import os
import sys
import tempfile
import traceback
from pathlib import Path
from types import SimpleNamespace

import bpy  # type: ignore

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tests"))
sys.path.insert(0, str(ROOT))
import _blender_env  # noqa: F401,E402

from caffmob_draw.armario_v2 import build, ops_window, validar, window  # noqa: E402

FAILURES = []


def check(nome, ok, detalhe=""):
    print(("OK   " if ok else "FALHA ") + nome, detalhe, flush=True)
    if not ok:
        FAILURES.append(nome)


def pecas(root):
    return [filho for filho in root.children if getattr(filho, 'btm_armario_parte', None) is not None]


def selecionar(obj):
    for outro in bpy.context.selected_objects:
        outro.select_set(False)
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj


def run():
    _blender_env.clean_scene()
    scene = bpy.context.scene
    scene.btm_armario_contrato.configurado = True
    root = build.criar_raiz(scene)
    selecionar(root)
    bpy.ops.caffmob.armario_v2_montar_caixa()
    s = window.JanelaSessao()
    s.armario_root = root
    window.iniciar_sessao(s)
    check("Montar Caixa antes da 026", len(pecas(root)) >= 5, len(pecas(root)))

    # Export JSON + cutlist -----------------------------------------------------------------------------------------
    caminho = os.path.join(tempfile.gettempdir(), "caffmob_armario_026.json")
    resultado = bpy.ops.caffmob.armario_v2_window_export_json('EXEC_DEFAULT', filepath=caminho)
    with open(caminho, encoding='utf-8') as arquivo:
        dados = json.load(arquivo)
    check("C02 export JSON grava o arquivo", resultado == {'FINISHED'} and os.path.exists(caminho), str(resultado))
    check("C02 payload tem peças e cutlist", dados.get("schema") == "caffmob.armario.v1"
          and dados.get("pecas") and dados.get("cutlist"), list(dados))
    check("C08 cutlist cobre as peças geradas", sum(g["quantidade"] for g in dados["cutlist"]) == len(dados["pecas"]))
    os.unlink(caminho)

    # Vista / tema --------------------------------------------------------------------------------------------------
    bpy.ops.caffmob.armario_v2_window_vista(vista='LATERAL')
    check("C01 vista lateral", s.vista == 'LATERAL', s.vista)
    bpy.ops.caffmob.armario_v2_window_vista(vista='FRONTAL')
    check("C01 vista frontal", s.vista == 'FRONTAL', s.vista)
    bpy.ops.caffmob.armario_v2_window_tema()
    check("C10 tema alterna para Dark", s.tema == 'DARK', s.tema)
    bpy.ops.caffmob.armario_v2_window_tema()
    check("C10 tema volta para Light", s.tema == 'LIGHT', s.tema)

    # Duplicata manual + Gerar --------------------------------------------------------------------------------------
    alvo = pecas(root)[0]
    window.definir_selecao(s, [{"nome": alvo.name, "vista": "FRONTAL"}])
    antes = len(pecas(root))
    bpy.ops.caffmob.armario_v2_window_duplicar()
    check("C05 duplicar cria a cópia", len(pecas(root)) == antes + 1, f"{antes} -> {len(pecas(root))}")
    check("C05 duplicata fica gravada", any(a.duplicada for a in root.btm_armario.ajustes))
    bpy.ops.caffmob.armario_v2_gerar()
    nomes = {o.name for o in pecas(root)}
    check("C05 Gerar preserva a duplicata", any("(cópia)" in n for n in nomes), sorted(nomes)[:4])

    # Popover de medida ---------------------------------------------------------------------------------------------
    bpy.ops.caffmob.armario_v2_window_medida('EXEC_DEFAULT', medida=800.0, eixo='LARGURA')
    check("C06 medida altera a largura e regenera", abs(root.btm_armario.largura - 800.0) < 1e-6,
          root.btm_armario.largura)

    # Apenas Laterais -----------------------------------------------------------------------------------------------
    bpy.ops.caffmob.armario_v2_window_apenas_laterais(criar=True)
    a = root.btm_armario
    check("C09 Apenas Laterais liga as duas laterais e desliga base/fundo",
          a.lateral_esq_ativa and a.lateral_dir_ativa and not a.base_inf_ativa and not a.base_sup_ativa
          and not a.fundo_ativo)
    check("C09 preview filtra para laterais", s.apenas_laterais is True)
    papeis = {p.btm_armario_parte.papel for p in pecas(root)
              if p.btm_armario_parte.ferragem == 'NENHUMA'}
    check("C09 geração só tem laterais", papeis == {'LATERAL'}, papeis)

    # Menu de contexto ----------------------------------------------------------------------------------------------
    class Layout:
        def __init__(self):
            self.itens = []

        def separator(self):
            pass

        def operator(self, idname, **_kw):
            self.itens.append(idname)
            return SimpleNamespace(acao=None)

    lay = Layout()
    ops_window.BTM_MT_ArmarioV2WindowContext.draw(SimpleNamespace(layout=lay), bpy.context)
    ids = [i for i in lay.itens]
    check("C05 menu desenha duplicar/medida", "caffmob.armario_v2_window_duplicar" in ids
          and "caffmob.armario_v2_window_medida" in ids, ids)

    # Arraste pelo caminho modal ------------------------------------------------------------------------------------
    window.definir_selecao(s, [{"nome": pecas(root)[0].name, "vista": "FRONTAL"}])
    obj = pecas(root)[0]
    s.escala_frontal = 100.0                     # 100 px por mm
    original_ativa = window.janela_ativa
    original_selecionar = window.selecionar_no_ponto
    original_area = window._area_da_sessao
    window.janela_ativa = lambda _ctx, _s: True
    window.selecionar_no_ponto = lambda _ctx, _s, *_a, **_k: {"nome": obj.name, "vista": "FRONTAL"}
    window._area_da_sessao = lambda: (None, None, None)
    try:
        modal = SimpleNamespace(_drag=None)
        ev = SimpleNamespace(type='LEFTMOUSE', value='PRESS', mouse_x=100, mouse_y=100, shift=False, ctrl=False)
        ops_window.BTM_OT_ArmarioV2WindowModal.modal(modal, bpy.context, ev)
        ev = SimpleNamespace(type='MOUSEMOVE', value='NOTHING', mouse_x=120, mouse_y=110)
        ops_window.BTM_OT_ArmarioV2WindowModal.modal(modal, bpy.context, ev)
        moveu = obj.location.x
        ev = SimpleNamespace(type='LEFTMOUSE', value='RELEASE', mouse_x=120, mouse_y=110)
        ops_window.BTM_OT_ArmarioV2WindowModal.modal(modal, bpy.context, ev)
        ajuste = next((x for x in root.btm_armario.ajustes if x.nome == obj.name), None)
        check("C07 modal arrasta a peça", abs(moveu) > 1e-9, moveu)
        check("C07 modal grava dx/dz", ajuste is not None and abs(ajuste.dx) > 1e-9 and abs(ajuste.dz) > 1e-9,
              None if ajuste is None else (ajuste.dx, ajuste.dz))
    finally:
        window.janela_ativa = original_ativa
        window.selecionar_no_ponto = original_selecionar
        window._area_da_sessao = original_area

    # Ferramentas restantes existem e o painel lateral troca ---------------------------------------------------------
    check("C01 abrir/fechar tudo registrado", hasattr(bpy.ops.caffmob, 'armario_v2_window_abrir_tudo'))
    check("C01 painel lateral registrado", hasattr(bpy.ops.caffmob, 'armario_v2_window_painel'))
    check("C03 titlebar tem export/tema", hasattr(bpy.ops.caffmob, 'armario_v2_window_export_json')
          and hasattr(bpy.ops.caffmob, 'armario_v2_window_tema'))
    spec, itens = validar.pecas_da_raiz(root)
    check("C08 lista de peças/cutlist", spec is not None and itens, len(itens))


try:
    run()
except Exception:
    traceback.print_exc()
    FAILURES.append("exceção no roteiro")
finally:
    print(f"blender_026_parity: {'OK' if not FAILURES else 'FALHAS: ' + ', '.join(FAILURES)}", flush=True)
    os._exit(1 if FAILURES else 0)
