"""Sonda de auditoria da feature 023 depois da correção (janela nova x mockup).

Roda dentro do Blender aberto (MCP, 127.0.0.1:9877) e NÃO usa cena temporária: o operador abre a janela a partir de uma
área VIEW_3D real, como o botão do painel faz. O fechamento e a limpeza ficam em `probe_janela_023_close.py`.
"""

import json
import os

import bpy

RAIZ = r"C:\Users\RYZEN\Documents\BlenderToMob3"
SAIDA = os.path.join(RAIZ, "_reversa_bugs", "plugin-caffmob-draw", "inspections",
                     "2026-11-25-janela-023")
os.makedirs(SAIDA, exist_ok=True)

if RAIZ not in os.sys.path:
    os.sys.path.insert(0, RAIZ)

resultado = {}
wm = bpy.context.window_manager
janela = bpy.context.window
area3d = next((a for a in janela.screen.areas if a.type == 'VIEW_3D'), None)

resultado["janelas_antes"] = len(wm.windows)
resultado["raizes_antes"] = [o.name for o in bpy.data.objects if o.get("btm_armario_v2_root")]
resultado["area_3d"] = None if area3d is None else (area3d.as_pointer(), area3d.type, area3d.width, area3d.height)
resultado["operador_registrado"] = hasattr(bpy.ops.caffmob, "armario_v2_window_open")

retorno = None
if area3d is not None:
    try:
        with bpy.context.temp_override(window=janela, area=area3d):
            retorno = bpy.ops.caffmob.armario_v2_window_open()
        resultado["retorno_operador"] = str(retorno)
    except Exception as erro:  # noqa: BLE001
        resultado["erro_operador"] = repr(erro)

resultado["janelas_depois"] = len(wm.windows)
resultado["areas_depois"] = [(w.as_pointer(), [(a.as_pointer(), a.type, a.width, a.height) for a in w.screen.areas])
                             for w in wm.windows]

from caffmob_draw.armario_v2 import window as win_mod  # noqa: E402

s = win_mod.sessao()
resultado["sessao"] = None if s is None else {
    "aberto": s.aberto,
    "area_ptr": s.area_ptr,
    "window_ptr": s.window_ptr,
    "restore_area_type": s.restore_area_type,
    "tem_draw_handler": s.draw_handler is not None,
    "raiz": getattr(s.armario_root, "name", None),
    "mostrar_cotas": s.mostrar_cotas,
    "mostrar_portas": s.mostrar_portas,
}
if s is not None:
    resultado["raiz_criada"] = getattr(s.armario_root, "name", None)

alvo = None
if s is not None:
    for w in wm.windows:
        if w.as_pointer() != s.window_ptr:
            continue
        for a in w.screen.areas:
            if a.as_pointer() == s.area_ptr:
                alvo = (w, a)
                break
if alvo is not None:
    ui = next((r for r in alvo[1].regions if r.type == 'UI'), None)
    resultado["aba_ativa"] = getattr(ui, "active_panel_category", None)
    resultado["ui_visivel"] = None if ui is None else (ui.width, ui.height)
    resultado["area_alvo"] = (alvo[1].type, alvo[1].width, alvo[1].height)


def _capturar(nome):
    w, a = alvo
    caminho = os.path.join(SAIDA, nome)
    try:
        with bpy.context.temp_override(window=w, area=a):
            bpy.ops.screen.screenshot_area(filepath=caminho)
        print("[AUDIT023] captura", caminho)
    except Exception as erro:  # noqa: BLE001
        print("[AUDIT023] captura falhou", nome, repr(erro))


if alvo is not None:
    bpy.app.timers.register(lambda: (_capturar("01_janela_aberta.png"), None)[1], first_interval=1.2)
    bpy.app.timers.register(lambda: (_capturar("02_janela_aberta_redesenho.png"), None)[1], first_interval=2.6)

print("[AUDIT023-INICIO]")
print(json.dumps(resultado, ensure_ascii=False, indent=2))
print("[AUDIT023-FIM]")
