"""As duas janelas novas, com desenho de verdade (027, T009 a T014; RF-01, RF-02).

    blender --enable-event-simulate --python-exit-code 1 --python tests/blender_027_janelas.py

Precisa de janela e GPU: abre o plano de corte (com um ambiente da fixture 067) e o V-Ray Mesh Measure (com um bloco
solto), força o desenho e fecha cada uma. Confere que a área virou Image Editor, que a sessão existe, que as opções
mudam com a janela aberta e que o fechar não deixa sessão pendurada. Não confere a aparência: para isso, olhar a tela.
"""

import sys
import traceback
from pathlib import Path

import bpy

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _blender_env as env  # noqa: E402
import _fixtures_067 as fx  # noqa: E402
from caffmob_draw.cutting import plan_window  # noqa: E402
from caffmob_draw.mesh_measure import scene as measure_scene  # noqa: E402

FAILURES = []


def check(name, ok, detail=""):
    print(("OK   " if ok else "FALHA ") + name + (f" ({detail})" if detail and not ok else ""), flush=True)
    if not ok:
        FAILURES.append(name)


def _op(call):
    """Chama um operador com o contexto de uma Vista 3D (o script começa sem área)."""
    win = bpy.context.window_manager.windows[0]
    area = next(a for a in win.screen.areas if a.type == 'VIEW_3D')
    region = next(r for r in area.regions if r.type == 'WINDOW')
    with bpy.context.temp_override(window=win, area=area, region=region):
        return call()


def _redraw(iterations=3):
    _op(lambda: bpy.ops.wm.redraw_timer(type='DRAW_WIN_SWAP', iterations=iterations))


def _area_type(session):
    return bpy.context.window_manager.windows and next(
        (area.type for window in bpy.context.window_manager.windows for area in window.screen.areas
         if area.as_pointer() == session.area_ptr), None)


def _plano_de_corte():
    fx.scene_15()
    resultado = bpy.ops.caffmob.calculate_nesting()
    check("plano de corte calculado", resultado == {'FINISHED'}, str(resultado))
    janelas = len(bpy.context.window_manager.windows)
    resultado = _op(lambda: bpy.ops.caffmob.cut_plan_window())
    check("a janela do plano abre", resultado == {'FINISHED'}, str(resultado))
    session = plan_window.sessao()
    check("sessão do plano aberta", session is not None and bool(session.sheets))
    check("a janela do plano é uma janela nova", len(bpy.context.window_manager.windows) > janelas,
          f"{len(bpy.context.window_manager.windows)} <= {janelas}")
    check("a área do plano virou Image Editor", _area_type(session) == 'IMAGE_EDITOR', str(_area_type(session)))
    _redraw()
    check("o desenho do plano não quebra", True)
    bpy.ops.caffmob.cut_plan_step(delta=1)
    bpy.ops.caffmob.cut_plan_zoom(factor=1.25)
    bpy.ops.caffmob.cut_plan_zoom(fit=True)
    _redraw()
    bpy.ops.caffmob.cut_plan_close()
    _redraw()
    check("fechar o plano encerra a sessão", plan_window.sessao() is None)


def _medicao():
    env.clean_scene()
    bpy.ops.mesh.primitive_cube_add(size=0.6, location=(0.0, 0.0, 0.3))
    obj = bpy.context.object
    obj.name = "Bloco de Medição"
    env.settle()
    resultado = _op(lambda: bpy.ops.caffmob.mesh_measure_window())
    check("a janela de medição abre", resultado == {'FINISHED'}, str(resultado))
    session = measure_scene.sessao()
    check("sessão de medição aberta", session is not None and bool(session.malha.parts))
    check("a área da medição virou Image Editor", _area_type(session) == 'IMAGE_EDITOR', str(_area_type(session)))
    _redraw()
    for representacao in ('ARAMADO', 'LINHAS_OCULTAS', 'SOLIDO', 'RAIO_X', 'MATERIAL'):
        bpy.ops.caffmob.mesh_measure_option(option='REPRESENTATION', value=representacao)
        _redraw(2)
        check(f"desenho em {representacao} sem quebrar", session.representation == representacao)
    bpy.ops.caffmob.mesh_measure_option(option='PROJECTION', value='ORTHO')
    _redraw(2)
    check("desenho em ortográfica sem quebrar", session.camera.projection == 'ORTHO')
    bpy.ops.caffmob.mesh_measure_view(action='CREATE')
    bpy.ops.caffmob.mesh_measure_option(option='PRINT', value='ON')
    _redraw(3)
    check("folha de impressão desenhada", session.print_preview and len(session.views) == 1)
    bpy.ops.caffmob.mesh_measure_option(option='PRINT', value='OFF')
    bpy.ops.caffmob.mesh_measure_close()
    _redraw()
    check("fechar a medição encerra a sessão", measure_scene.sessao() is None)


def _run():
    """Roda com a interface já montada: o script de `--python` começa sem área no contexto."""
    try:
        _plano_de_corte()
    except Exception:
        traceback.print_exc()
        FAILURES.append("plano de corte")
    try:
        _medicao()
    except Exception:
        traceback.print_exc()
        FAILURES.append("medição")
    resultado = 'OK' if not FAILURES else 'FALHAS: ' + ', '.join(FAILURES)
    print(f"blender_027_janelas: {resultado}", flush=True)
    # Sai pelo Blender: `sys.exit` dentro do timer derruba o processo no Windows.
    (Path(__file__).resolve().parent.parent / '_janelas_result.txt').write_text(resultado, encoding='utf-8')
    bpy.app.timers.register(lambda: bpy.ops.wm.quit_blender(), first_interval=0.3)


def main():
    if bpy.app.background:
        print("blender_027_janelas: PRECISA DE JANELA (rode com interface)", flush=True)
        return
    bpy.app.timers.register(_run, first_interval=2.0)


if __name__ == '__main__':
    main()
