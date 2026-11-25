"""Fecha a sonda da 023: restaura a área, apaga a cena temporária e reporta o estado final."""

import json
import os

import bpy

resultado = {}
wm = bpy.context.window_manager
resultado["janelas"] = len(wm.windows)

# Encerra a sessão do editor, se ainda existir.
try:
    from caffmob_draw.armario_v2 import window as win_mod
except Exception as erro:  # noqa: BLE001
    win_mod = None
    resultado["import"] = repr(erro)

if win_mod is not None and win_mod.sessao() is not None:
    try:
        with bpy.context.temp_override(window=bpy.context.window):
            bpy.ops.caffmob.armario_v2_window_cancelar()
        resultado["cancelar"] = "ok"
    except Exception as erro:  # noqa: BLE001
        resultado["cancelar"] = repr(erro)
    win_mod.encerrar_sessao()

# Restaura qualquer área que ficou como IMAGE_EDITOR sem imagem (a sonda).
restauradas = 0
for w in wm.windows:
    for a in w.screen.areas:
        if a.type == 'IMAGE_EDITOR' and a.spaces.active.image is None:
            a.type = 'VIEW_3D'
            a.show_menus = True
            a.spaces.active.show_region_header = True
            restauradas += 1
resultado["areas_restauradas"] = restauradas

# Apaga a cena temporária da sonda.
cena = bpy.data.scenes.get("AUDIT_023_JANELA")
if cena is not None:
    removidos = []
    for obj in list(cena.objects):
        removidos.append(obj.name)
        bpy.data.objects.remove(obj, do_unlink=True)
    bpy.data.scenes.remove(cena)
    resultado["cena_temporaria_removida"] = removidos
else:
    resultado["cena_temporaria_removida"] = None

resultado["areas_finais"] = [(w.as_pointer(), [a.type for a in w.screen.areas]) for w in wm.windows]
saida = os.path.join(r"C:\Users\RYZEN\Documents\BlenderToMob3", "_reversa_bugs", "plugin-caffmob-draw",
                     "inspections", "2026-11-25-janela-023")
resultado["capturas"] = sorted(n for n in os.listdir(saida) if n.endswith(".png"))

print("[AUDIT023-CLOSE-INICIO]")
print(json.dumps(resultado, ensure_ascii=False, indent=2))
print("[AUDIT023-CLOSE-FIM]")
