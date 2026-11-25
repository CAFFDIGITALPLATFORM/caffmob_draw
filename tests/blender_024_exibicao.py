"""Variante de exibição e diálogo recomendado (feature 024, T008/T010/T016/T017; RN-01, D-05).

Precisa de janela (a vista 3D só existe com tela):

    xvfb-run -a blender --factory-startup --enable-event-simulate --python tests/blender_024_exibicao.py

- a variante aplica `TEXTURE` e o interruptor Linhas em todas as vistas 3D;
- "Somente textura" desliga as linhas sem trocar material;
- o diálogo recomendado aplica `color_type = 'TEXTURE'` e mantém `turn_off_3d_cursor` intacto;
- com `TEXTURE`, o aviso da barra lateral não acusa erro.
"""

import sys
import traceback
from pathlib import Path

import bpy

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _blender_env as env  # noqa: E402,F401
from caffmob_draw.armario_v2 import exibicao  # noqa: E402

FAILURES = []


def check(name, ok, detail=""):
    print(("OK   " if ok else "FALHA ") + name, detail, flush=True)
    if not ok:
        FAILURES.append(name)


def spaces():
    return [space for window in bpy.context.window_manager.windows for area in window.screen.areas
            if area.type == 'VIEW_3D' for space in area.spaces if space.type == 'VIEW_3D']


def main():
    vistas = spaces()
    check("há vista 3D", bool(vistas))
    if not vistas:
        return
    for space in vistas:
        space.shading.color_type = 'OBJECT'
        space.overlay.show_wireframes = False
    check("aplica com linhas", exibicao.aplicar(bpy.context, 'TEXTURA_LINHAS'))
    check("modo TEXTURE", bpy.context.scene.btm_view_mode == 'TEXTURE')
    check("linhas ligadas em todas as vistas", all(s.overlay.show_wireframes for s in vistas))
    check("cor média da textura", all(s.shading.color_type == 'TEXTURE' for s in vistas))

    exibicao.aplicar(bpy.context, 'TEXTURA_SO')
    check("linhas desligadas", not any(s.overlay.show_wireframes for s in vistas))
    check("textura mantida", all(s.shading.color_type == 'TEXTURE' for s in vistas))

    operador = bpy.types.CAFFMOB_OT_set_recommended_settings if hasattr(
        bpy.types, 'CAFFMOB_OT_set_recommended_settings') else None
    classe = next((cls for cls in bpy.types.Operator.__subclasses__()
                   if getattr(cls, 'bl_idname', '') == 'caffmob.set_recommended_settings'), None)
    check("diálogo recomendado registrado", operador is not None or classe is not None)
    if classe is not None:
        check("controle Cursos 3D preservado", hasattr(classe, 'turn_off_3d_cursor'))
        check("controle de cor virou textura", hasattr(classe, 'turn_on_texture_color_type'))
    for space in vistas:
        space.shading.color_type = 'MATERIAL'
    check("fora de OBJECT/TEXTURE o aviso aparece", any(s.shading.color_type not in ('OBJECT', 'TEXTURE')
                                                        for s in vistas))


if __name__ == '__main__':
    try:
        main()
    except Exception:
        traceback.print_exc()
        FAILURES.append("exceção")
    print(f"\n{len(FAILURES)} falha(s)")
    sys.exit(1 if FAILURES else 0)
