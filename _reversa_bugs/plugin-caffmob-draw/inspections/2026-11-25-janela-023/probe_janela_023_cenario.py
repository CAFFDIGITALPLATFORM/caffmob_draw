"""Cenário da 023: abrir a janela nova e montar a caixa pelo painel (mesmo caminho do botão)."""

import json

import bpy

RAIZ = r"C:\Users\RYZEN\Documents\BlenderToMob3"
import os
import sys

if RAIZ not in sys.path:
    sys.path.insert(0, RAIZ)

from caffmob_draw.armario_v2 import window as win_mod  # noqa: E402

resultado = {}
wm = bpy.context.window_manager
janela = bpy.context.window
area3d = next((a for a in janela.screen.areas if a.type == 'VIEW_3D'), None)
resultado["janelas_antes"] = len(wm.windows)
antes = {w.as_pointer() for w in wm.windows}

with bpy.context.temp_override(window=janela, area=area3d):
    resultado["abrir"] = str(bpy.ops.caffmob.armario_v2_window_open())

novas = [w for w in wm.windows if w.as_pointer() not in antes]
resultado["janelas_depois"] = len(wm.windows)
resultado["janelas_novas"] = [w.as_pointer() for w in novas]

s = win_mod.sessao()
resultado["sessao"] = s is not None
if s is not None:
    root = s.armario_root
    resultado["raiz"] = getattr(root, "name", None)
    resultado["ativo"] = getattr(bpy.context.view_layer.objects.active, "name", None)
    resultado["gerado_antes"] = bool(root.btm_armario.gerado)
    with bpy.context.temp_override(window=janela, area=area3d):
        resultado["montar"] = str(bpy.ops.caffmob.armario_v2_montar_caixa())
    resultado["gerado_depois"] = bool(root.btm_armario.gerado)
    resultado["filhos"] = len(root.children)
    resultado["estrutura"] = [bool(root.btm_armario.lateral_esq_ativa), bool(root.btm_armario.lateral_dir_ativa),
                              bool(root.btm_armario.base_inf_ativa), bool(root.btm_armario.base_sup_ativa),
                              bool(root.btm_armario.fundo_ativo)]
    for w in wm.windows:
        for a in w.screen.areas:
            if a.as_pointer() == s.area_ptr:
                a.tag_redraw()

print("[AUDIT023-CENARIO-INICIO]")
print(json.dumps(resultado, ensure_ascii=False, indent=2))
print("[AUDIT023-CENARIO-FIM]")
