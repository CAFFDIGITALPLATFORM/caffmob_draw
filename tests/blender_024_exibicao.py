"""Exibição do armário, diálogo recomendado e fluxo de detalhes (024, T008/T010/T016/T017; RN-01, D-05).

Precisa de janela (a vista 3D e o fluxo de detalhes só existem com tela). No Linux o repositório usa
`xvfb-run -a blender --factory-startup --enable-event-simulate --python tests/blender_024_exibicao.py`; no Windows,
`blender.exe --factory-startup --enable-event-simulate --python tests/blender_024_exibicao.py`.

- a variante aplica `TEXTURE` e o interruptor Linhas em todas as vistas 3D; "Somente textura" desliga as linhas;
- o diálogo recomendado aplica `color_type = 'TEXTURE'` e mantém os demais controles (inclusive "Cursos 3D");
- o fluxo de detalhes (`DetailView.create`) deixa a vista em `SOLID` + `TEXTURE` (T008);
- com `TEXTURE` o aviso da barra lateral não aparece; fora de `OBJECT`/`TEXTURE`, aparece (T017).
"""

import sys
import traceback
from pathlib import Path

import bpy

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _blender_env as env  # noqa: E402,F401
import caffmob_draw  # noqa: E402
from caffmob_draw import hb_details  # noqa: E402
from caffmob_draw.armario_v2 import exibicao  # noqa: E402
from caffmob_draw.ui import view3d_sidebar  # noqa: E402

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

    classe = getattr(caffmob_draw, 'BTM_AddonPreferences', None)
    check("classe de preferências existe", classe is not None)
    prefs = classe.bl_rna.properties if classe is not None else {}
    check("preferência exibicao_armario", prefs.get('exibicao_armario') is not None)
    check("preferência cabinet_color preservada", prefs.get('cabinet_color') is not None)

    operador = next((cls for cls in bpy.types.Operator.__subclasses__()
                     if getattr(cls, 'bl_idname', '') == 'caffmob.set_recommended_settings'), None)
    check("diálogo recomendado registrado", operador is not None)
    if operador is not None:
        props = [prop.identifier for prop in bpy.ops.caffmob.set_recommended_settings.get_rna_type().properties]
        check("controle Cursos 3D preservado", 'turn_off_3d_cursor' in props, str(props))
        check("controle de cor virou textura", 'turn_on_texture_color_type' in props, str(props))
        check("controle antigo removido", 'turn_on_object_color_type' not in props, str(props))
        for space in vistas:
            space.shading.color_type = 'OBJECT'
            space.overlay.show_cursor = True
            space.overlay.show_relationship_lines = True
        resultado = bpy.ops.caffmob.set_recommended_settings('EXEC_DEFAULT')
        check("operador executou", resultado == {'FINISHED'}, str(resultado))
        check("operador aplicou TEXTURE", all(s.shading.color_type == 'TEXTURE' for s in vistas),
              str([s.shading.color_type for s in vistas]))
        check("operador desligou o cursor 3D", all(not s.overlay.show_cursor for s in vistas))
        check("operador desligou linhas de relação", all(not s.overlay.show_relationship_lines for s in vistas))

    # T017: o aviso só aparece quando a cor não é OBJECT nem TEXTURE.
    check("aviso fora de OBJECT/TEXTURE", view3d_sidebar.precisa_aviso('MATERIAL') is True)
    check("sem aviso em OBJECT", view3d_sidebar.precisa_aviso('OBJECT') is False)
    check("sem aviso em TEXTURE", view3d_sidebar.precisa_aviso('TEXTURE') is False)

    # T008: fluxo de detalhes de verdade (cria cena de detalhe e configura a vista).
    cena_original = bpy.context.window.scene
    detalhe = hb_details.DetailView().create("Detalhe 024")
    try:
        check("cena marcada como detalhe", bool(detalhe.get('IS_DETAIL_VIEW')))
        check("detalhe em SOLID + TEXTURE",
              all(s.shading.type == 'SOLID' and s.shading.color_type == 'TEXTURE' for s in spaces()),
              str([(s.shading.type, s.shading.color_type) for s in spaces()]))
    finally:
        bpy.context.window.scene = cena_original
        bpy.data.scenes.remove(detalhe)


if __name__ == '__main__':
    try:
        main()
    except Exception:
        traceback.print_exc()
        FAILURES.append("exceção")
    print(f"\n{len(FAILURES)} falha(s)")
    sys.exit(1 if FAILURES else 0)
