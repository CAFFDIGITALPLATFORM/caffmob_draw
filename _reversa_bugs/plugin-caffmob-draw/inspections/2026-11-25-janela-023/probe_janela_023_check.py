"""Confere que a sonda não deixou resíduo na sessão do Blender."""

import json

import bpy

resultado = {
    "cena_ativa": bpy.context.scene.name,
    "objetos_armario": [o.name for o in bpy.data.objects if o.get("btm_armario_v2_root")],
    "scenes": [s.name for s in bpy.data.scenes],
    "janelas": len(bpy.context.window_manager.windows),
    "areas": [(w.as_pointer(), [a.type for a in w.screen.areas]) for w in bpy.context.window_manager.windows],
}
print("[AUDIT023-CHECK-INICIO]")
print(json.dumps(resultado, ensure_ascii=False, indent=2))
print("[AUDIT023-CHECK-FIM]")
