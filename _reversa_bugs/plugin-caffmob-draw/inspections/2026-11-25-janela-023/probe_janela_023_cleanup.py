"""Remove a raiz vazia que a sonda criou (a de maior sufixo), com as guardas que provam que é resíduo."""

import json

import bpy

nome = "Armário v2.002"
resultado = {}
obj = bpy.data.objects.get(nome)
motivo = None
if obj is None:
    motivo = "não existe"
elif not obj.get("btm_armario_v2_root"):
    motivo = "não é raiz v2"
elif obj.children:
    motivo = "tem filhos"
elif getattr(obj, "btm_armario", None) is None or obj.btm_armario.gerado:
    motivo = "está gerado"

if motivo is None:
    bpy.data.objects.remove(obj, do_unlink=True)
    resultado["removido"] = nome
else:
    resultado["nao_removido"] = f"{nome}: {motivo}"

resultado["raizes_restantes"] = [o.name for o in bpy.data.objects if o.get("btm_armario_v2_root")]
print("[AUDIT023-CLEANUP-INICIO]")
print(json.dumps(resultado, ensure_ascii=False, indent=2))
print("[AUDIT023-CLEANUP-FIM]")
