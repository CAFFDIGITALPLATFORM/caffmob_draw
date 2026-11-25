"""Desfaz o que as sondas da 023 deixaram na cena: peças geradas no armário reusado e raízes vazias criadas por elas."""

import json

import bpy

from caffmob_draw.armario_v2 import build

resultado = {"antes": [], "removidas": [], "limpas": []}
for obj in bpy.data.objects:
    if obj.get("btm_armario_v2_root"):
        resultado["antes"].append({"nome": obj.name, "filhos": len(obj.children),
                                   "gerado": bool(obj.btm_armario.gerado)})

# Raízes vazias criadas pelas sondas (sem filhos e nunca geradas).
for nome in ("Armário v2.002", "Armário v2.003"):
    obj = bpy.data.objects.get(nome)
    if obj is None or not obj.get("btm_armario_v2_root"):
        continue
    if obj.children or obj.btm_armario.gerado:
        resultado.setdefault("recusadas", []).append(nome)
        continue
    bpy.data.objects.remove(obj, do_unlink=True)
    resultado["removidas"].append(nome)

# O armário reusado pela sonda: só as peças com btm_armario_parte, e volta gerado=False.
base = bpy.data.objects.get("Armário v2")
if base is not None and base.get("btm_armario_v2_root"):
    if all(getattr(filho, "btm_armario_parte", None) is not None for filho in base.children):
        build.limpar(base)
        base.btm_armario.gerado = False
        resultado["limpas"].append(base.name)
    else:
        resultado.setdefault("recusadas", []).append(base.name + " (filho estranho)")

resultado["depois"] = [{"nome": o.name, "filhos": len(o.children), "gerado": bool(o.btm_armario.gerado)}
                       for o in bpy.data.objects if o.get("btm_armario_v2_root")]
print("[AUDIT023-RESTAURA-INICIO]")
print(json.dumps(resultado, ensure_ascii=False, indent=2))
print("[AUDIT023-RESTAURA-FIM]")
