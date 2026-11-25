"""Fecha janelas extras do ensaio e reporta o erro do `wm.window_close` quando houver."""

import json

import bpy

resultado = {"janelas_antes": len(bpy.context.window_manager.windows)}
principal = bpy.context.window
extras = [w for w in bpy.context.window_manager.windows if w.as_pointer() != principal.as_pointer()]
resultado["extras"] = [w.as_pointer() for w in extras]
resultado["tipos"] = {str(w.as_pointer()): [a.type for a in w.screen.areas] for w in extras}

erros = []
for w in extras:
    try:
        with bpy.context.temp_override(window=w, area=w.screen.areas[0]):
            bpy.ops.wm.window_close()
    except Exception as erro:  # noqa: BLE001
        erros.append({"janela": w.as_pointer(), "erro": repr(erro)})
resultado["erros"] = erros
resultado["janelas_depois"] = len(bpy.context.window_manager.windows)
print("[AUDIT023-WINCLOSE-INICIO]")
print(json.dumps(resultado, ensure_ascii=False, indent=2))
print("[AUDIT023-WINCLOSE-FIM]")
