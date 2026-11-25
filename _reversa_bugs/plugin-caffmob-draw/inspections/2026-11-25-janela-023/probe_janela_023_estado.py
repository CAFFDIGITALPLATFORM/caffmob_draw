"""Estado da janela 023 depois dos timers (aba focada, hits do preview)."""

import json

import bpy

from caffmob_draw.armario_v2 import window as win_mod

s = win_mod.sessao()
resultado = {"sessao": s is not None, "janelas": len(bpy.context.window_manager.windows)}
if s is not None:
    area = None
    for w in bpy.context.window_manager.windows:
        for a in w.screen.areas:
            if a.as_pointer() == s.area_ptr:
                area = a
    ui = next((r for r in area.regions if r.type == 'UI'), None) if area is not None else None
    resultado.update({
        "area": None if area is None else area.type,
        "aba_ativa": getattr(ui, "active_panel_category", None),
        "hits": len(getattr(s, "hits", [])),
        "hits_exemplo": [h["nome"] for h in getattr(s, "hits", [])[:5]],
        "raiz": getattr(s.armario_root, "name", None),
        "selecionado": None if not s.selecionado else s.selecionado.get("nome"),
    })
print("[AUDIT023-ESTADO-INICIO]")
print(json.dumps(resultado, ensure_ascii=False, indent=2))
print("[AUDIT023-ESTADO-FIM]")
