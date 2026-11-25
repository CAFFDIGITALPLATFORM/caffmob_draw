"""Fecha só as janelas criadas pela sonda (uma única área IMAGE_EDITOR sem imagem)."""

import json

import bpy

principal = bpy.context.window.as_pointer()
fechadas, erros = [], []
for w in list(bpy.context.window_manager.windows):
    if w.as_pointer() == principal:
        continue
    areas = list(w.screen.areas)
    if len(areas) == 1 and areas[0].type == 'IMAGE_EDITOR' and areas[0].spaces.active.image is None:
        try:
            with bpy.context.temp_override(window=w, area=areas[0]):
                bpy.ops.wm.window_close()
            fechadas.append(w.as_pointer())
        except Exception as erro:  # noqa: BLE001
            erros.append({"janela": w.as_pointer(), "erro": repr(erro)})

print("[AUDIT023-LIMPAR-INICIO]")
print(json.dumps({"fechadas": fechadas, "erros": erros,
                  "janelas": len(bpy.context.window_manager.windows)}, ensure_ascii=False, indent=2))
print("[AUDIT023-LIMPAR-FIM]")
