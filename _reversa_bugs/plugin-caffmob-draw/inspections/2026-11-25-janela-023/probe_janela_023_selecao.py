"""Seleção por clique no preview da 023, com captura da janela montada."""

import json
import os

import bpy

RAIZ = r"C:\Users\RYZEN\Documents\BlenderToMob3"
SAIDA = os.path.join(RAIZ, "_reversa_bugs", "plugin-caffmob-draw", "inspections", "2026-11-25-janela-023")
import sys

if RAIZ not in sys.path:
    sys.path.insert(0, RAIZ)

from caffmob_draw.armario_v2 import window as win_mod  # noqa: E402

resultado = {}
s = win_mod.sessao()
resultado["sessao"] = s is not None
alvo = None
if s is not None:
    area = None
    for w in bpy.context.window_manager.windows:
        for a in w.screen.areas:
            if a.as_pointer() == s.area_ptr:
                area, alvo = a, (w, a)
    resultado["hits"] = len(getattr(s, "hits", []))
    resultado["primeiros"] = [h["nome"] for h in getattr(s, "hits", [])[:6]]
    if area is not None and getattr(s, "hits", None):
        region = next((r for r in area.regions if r.type == 'WINDOW'), None)
        frontal = next((h for h in s.hits if h["vista"] == "FRONTAL" and h["papel"] == "LATERAL"), s.hits[0])
        x0, y0, x1, y1 = frontal["rect"]
        mx, my = region.x + (x0 + x1) / 2.0, region.y + (y0 + y1) / 2.0
        escolhida = win_mod.selecionar_no_ponto(bpy.context, s, mx, my)
        resultado["clicou"] = frontal["nome"]
        resultado["selecionado"] = None if escolhida is None else escolhida["nome"]
        resultado["clique"] = (mx, my)
        area.tag_redraw()

if alvo is not None:
    def _capturar():
        w, a = alvo
        try:
            with bpy.context.temp_override(window=w, area=a):
                bpy.ops.screen.screenshot_area(filepath=os.path.join(SAIDA, "04_janela_montada.png"))
            print("[AUDIT023] captura 04")
        except Exception as erro:  # noqa: BLE001
            print("[AUDIT023] captura falhou", repr(erro))

    bpy.app.timers.register(lambda: (_capturar(), None)[1], first_interval=1.0)

print("[AUDIT023-SELECAO-INICIO]")
print(json.dumps(resultado, ensure_ascii=False, indent=2))
print("[AUDIT023-SELECAO-FIM]")
