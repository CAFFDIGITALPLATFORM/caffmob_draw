"""Testa `screen.area_dupli` sob `temp_override` no Blender aberto (MCP)."""

import json

import bpy

resultado = {}
wm = bpy.context.window_manager
janela = bpy.context.window
area3d = next((a for a in janela.screen.areas if a.type == 'VIEW_3D'), None)
resultado["janelas_antes"] = len(wm.windows)
resultado["area_3d"] = None if area3d is None else (area3d.width, area3d.height)
antes = {w.as_pointer() for w in wm.windows}

if area3d is not None:
    try:
        with bpy.context.temp_override(window=janela, area=area3d):
            bpy.ops.screen.area_dupli('INVOKE_DEFAULT')
        resultado["operador"] = "ok"
    except Exception as erro:  # noqa: BLE001
        resultado["operador"] = repr(erro)

resultado["janelas_depois"] = len(wm.windows)
novas = [w for w in wm.windows if w.as_pointer() not in antes]
resultado["novas"] = [(w.as_pointer(), [(a.type, a.width, a.height) for a in w.screen.areas]) for w in novas]

# fecha só a janela que a sonda criou
for w in novas:
    try:
        with bpy.context.temp_override(window=w):
            bpy.ops.wm.window_close()
        resultado.setdefault("fechadas", []).append(w.as_pointer())
    except Exception as erro:  # noqa: BLE001
        resultado.setdefault("falha_fechar", []).append(repr(erro))

resultado["janelas_final"] = len(bpy.context.window_manager.windows)
print("[AUDIT023-DUPLI-INICIO]")
print(json.dumps(resultado, ensure_ascii=False, indent=2))
print("[AUDIT023-DUPLI-FIM]")
