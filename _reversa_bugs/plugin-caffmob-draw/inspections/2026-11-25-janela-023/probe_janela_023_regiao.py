"""Coordenadas das regiões da janela nova e teste de seleção com coordenadas locais."""

import json

import bpy

from caffmob_draw.armario_v2 import window as win_mod

s = win_mod.sessao()
resultado = {}
if s is not None:
    for w in bpy.context.window_manager.windows:
        if w.as_pointer() != s.window_ptr:
            continue
        resultado["janela"] = (w.width, w.height, w.x, w.y)
        for a in w.screen.areas:
            if a.as_pointer() != s.area_ptr:
                continue
            resultado["area"] = (a.x, a.y, a.width, a.height)
            resultado["regioes"] = [(r.type, r.x, r.y, r.width, r.height) for r in a.regions]
    hits = getattr(s, "hits", [])
    resultado["hit"] = hits[0] if hits else None
print("[AUDIT023-REGIAO-INICIO]")
print(json.dumps(resultado, ensure_ascii=False, indent=2))
print("[AUDIT023-REGIAO-FIM]")
