"""Mede a abertura real da janela da 023 na sessão gráfica (T023) sem deixar resíduo.

Abre pelo operador, cronometra até a área nova existir, lê a aba ativa e cancela; no fim confere janelas e raízes.
"""

import json
import os
import time

import bpy

RAIZ = r"C:\Users\RYZEN\Documents\BlenderToMob3"
if RAIZ not in os.sys.path:
    os.sys.path.insert(0, RAIZ)

window = next((mod for nome, mod in os.sys.modules.items()
               if nome.startswith('bl_ext.') and nome.endswith('.armario_v2.window')), None)
if window is None:
    from caffmob_draw.armario_v2 import window  # noqa: E402

antes = {
    "janelas": len(bpy.context.window_manager.windows),
    "raizes": sorted(o.name for o in bpy.data.objects if o.get("btm_armario_v2_root")),
}
raiz = bpy.data.objects.get("Armário v2")
resultado = {"antes": antes, "raiz": raiz.name if raiz else None}
if raiz is not None:
    bpy.context.view_layer.objects.active = raiz
    raiz.select_set(True)

if window.sessao() is not None:                 # sobra de uma execução interrompida
    try:
        bpy.ops.caffmob.armario_v2_window_cancelar()
    except RuntimeError:
        window.encerrar_sessao()
    time.sleep(0.4)

area3d = next((a for a in bpy.context.window.screen.areas if a.type == 'VIEW_3D'), None)
inicio = time.perf_counter()
with bpy.context.temp_override(window=bpy.context.window, area=area3d):
    saida = sorted(bpy.ops.caffmob.armario_v2_window_open())
fim = time.perf_counter()
resultado["open"] = saida
resultado["abertura_ms"] = round((fim - inicio) * 1000.0, 1)

s = window.sessao()
resultado["sessao"] = s is not None
if s is not None:
    resultado["aba"] = s.aba
    resultado["janelas_durante"] = len(bpy.context.window_manager.windows)
    resultado["memoria"] = window.ler_memoria(bpy.context.scene)
    bpy.ops.caffmob.armario_v2_window_cancelar()

time.sleep(0.6)
resultado["janelas_depois"] = len(bpy.context.window_manager.windows)
resultado["raizes_depois"] = sorted(o.name for o in bpy.data.objects if o.get("btm_armario_v2_root"))
resultado["filhos_raiz"] = len(raiz.children) if raiz is not None else None
resultado["gerado"] = bool(raiz.btm_armario.gerado) if raiz is not None else None
resultado["abertura_ok"] = resultado["abertura_ms"] < 2000.0

print("[AUDIT023-DESEMPENHO-INICIO]")
print(json.dumps(resultado, ensure_ascii=False, indent=2))
print("[AUDIT023-DESEMPENHO-FIM]")
