"""Lista as raízes v2 e suas coleções/cenas, para separar resíduo da sonda do trabalho do usuário."""

import json

import bpy

resultado = []
for obj in bpy.data.objects:
    if not obj.get("btm_armario_v2_root"):
        continue
    cenas = [s.name for s in bpy.data.scenes if obj.name in s.objects]
    resultado.append({
        "nome": obj.name,
        "colecoes": [c.name for c in obj.users_collection],
        "usuarios": obj.users,
        "cenas": cenas,
        "filhos": len(obj.children),
        "gerado": bool(obj.btm_armario.gerado) if getattr(obj, "btm_armario", None) else None,
    })
print("[AUDIT023-RESIDUE-INICIO]")
print(json.dumps(resultado, ensure_ascii=False, indent=2))
print("[AUDIT023-RESIDUE-FIM]")
