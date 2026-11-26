"""Janela V-Ray Mesh Measure (027, T010 a T014; RF-02).

    blender --background --factory-startup --python-exit-code 1 --python tests/blender_027_medicao_malha.py

- a malha de dois blocos soltos é lida como duas partes, com as medidas de cada uma;
- a câmera projeta dentro do retângulo, em perspectiva e em ortográfica, e enquadra a caixa;
- unidades absoluta/arredondada em mm/cm/m, snap nas extremidades do objeto e das partes e medidas manuais;
- as cinco representações projetam os triângulos (sem GPU: só a parte de projeção e ordenação);
- a folha de impressão distribui as views com badge, tamanho e proporção;
- os operadores da janela mudam as opções na sessão, e `unregister()` não deixa handler sobrando.
"""

import sys
import traceback
from pathlib import Path

import bpy

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _blender_env as env  # noqa: E402,F401
from caffmob_draw.mesh_measure import camera as camera_mod  # noqa: E402
from caffmob_draw.mesh_measure import core, draw, scene, window  # noqa: E402

FAILURES = []
RECT = (0.0, 0.0, 900.0, 600.0)

FACES = [(0, 1, 3, 2), (4, 6, 7, 5), (0, 4, 5, 1), (2, 3, 7, 6), (0, 2, 6, 4), (1, 5, 7, 3)]


def check(name, ok, detail=""):
    print(("OK   " if ok else "FALHA ") + name + (f" ({detail})" if detail and not ok else ""), flush=True)
    if not ok:
        FAILURES.append(name)


def _corners(lo, hi):
    return [(x, y, z) for x in (lo[0], hi[0]) for y in (lo[1], hi[1]) for z in (lo[2], hi[2])]


def _two_blocks():
    """Uma malha com dois blocos soltos: 600×400×18 mm e 300×300×300 mm."""
    a = ((0.0, 0.0, 0.0), (0.6, 0.4, 0.018))
    b = ((0.8, 0.0, 0.0), (1.1, 0.3, 0.3))
    verts = _corners(*a) + _corners(*b)
    faces = [tuple(i for i in f) for f in FACES] + [tuple(i + 8 for i in f) for f in FACES]
    mesh = bpy.data.meshes.new("DoisBlocos")
    mesh.from_pydata(verts, [], faces)
    mesh.update()
    material = bpy.data.materials.new("MDF Teste")
    material.diffuse_color = (0.42, 0.24, 0.12, 1.0)
    mesh.materials.append(material)
    obj = bpy.data.objects.new("DoisBlocos", mesh)
    bpy.context.scene.collection.objects.link(obj)
    return obj


def main():
    env.clean_scene()
    obj = _two_blocks()
    bpy.context.view_layer.update()

    # T010: detecção da malha ---------------------------------------------------------------
    bpy.context.view_layer.objects.active = obj
    for item in bpy.context.scene.objects:
        item.select_set(item is obj)
    check("a malha ativa é a escolhida", scene.selected_mesh(bpy.context) is obj)
    malha = scene.snapshot(obj)
    check("duas partes soltas", len(malha.parts) == 2, str(len(malha.parts)))
    check("triângulos lidos", malha.triangle_count() == 24, str(malha.triangle_count()))
    medidas = sorted(part.size_mm for part in malha.parts)
    check("medidas do bloco menor", medidas[0] == (300.0, 300.0, 300.0), str(medidas[0]))
    check("medidas do bloco maior", medidas[1] == (600.0, 400.0, 18.0), str(medidas[1]))
    check("parte tem nome e cor", all(part.name and part.color for part in malha.parts))
    check("partes soltas por arestas", core.connected_parts(4, [(0, 1)]) == [[0, 1], [2], [3]])

    # T012: câmera -------------------------------------------------------------------------
    cam = camera_mod.Camera()
    cam.fit(malha.bounds, RECT)
    pontos = cam.project_all(malha.vertices, RECT)
    dentro = all(p is not None and -1 <= p[0] <= RECT[2] + 1 and -1 <= p[1] <= RECT[3] + 1 for p in pontos)
    check("enquadrar cabe no retângulo", dentro, str([p for p in pontos if p][:2]))
    centro = cam.project(core.center(*malha.bounds), RECT)
    check("o centro do alvo cai no centro da tela",
          abs(centro[0] - RECT[2] / 2) < 2 and abs(centro[1] - RECT[3] / 2) < 2, str(centro))
    yaw = cam.yaw
    cam.orbit(10.0, 5.0)
    check("orbitar gira a câmera", abs((cam.yaw - yaw - 10.0) % 360.0) < 1e-9, str(cam.yaw))
    check("orbitar limita a inclinação", (cam.orbit(0.0, 500.0) or cam.pitch) <= camera_mod.PITCH_LIMIT, str(cam.pitch))
    distancia = cam.distance
    cam.zoom(2.0)
    check("aproximar reduz a distância", cam.distance < distancia, f"{cam.distance} !< {distancia}")
    alvo = cam.target
    cam.pan(40.0, 0.0, RECT)
    check("mover desloca o alvo", cam.target != alvo)
    cam.projection = 'ORTHO'
    ortho = cam.project_all(malha.vertices, RECT)
    check("ortográfica projeta todos os vértices", all(p is not None for p in ortho))
    check("perspectiva e ortográfica diferem", ortho[0][0] != cam.copy(projection='PERSP').project(malha.vertices[0], RECT)[0])

    # T011: partes, camadas e medidas -------------------------------------------------------
    session = scene.keep(scene.Sessao(malha))
    check("sessão começa em sólido", session.representation == 'SOLIDO')
    check("todas as partes visíveis", len(session.visible_parts()) == 2)
    session.toggle_part(1)
    check("esconder uma parte", len(session.visible_parts()) == 1)
    session.toggle_part(1)
    rotulos = session.part_labels()
    check("medidas por parte", len(rotulos) == 2 and rotulos[0][1].count('×') == 2, str(rotulos[:1]))
    cor = malha.parts[0].color
    malha.parts[0].cycle_color()
    check("cor sólida troca por parte", malha.parts[0].color != cor)

    # T014: unidades, snap e medidas manuais ------------------------------------------------
    check("mm absoluto", core.format_mm(600.0, 'MM') == "600 mm", core.format_mm(600.0, 'MM'))
    check("mm arredondado", core.format_mm(600.4, 'MM', rounded=True) == "600 mm", core.format_mm(600.4, 'MM', rounded=True))
    check("cm", core.format_mm(600.0, 'CM') == "60 cm", core.format_mm(600.0, 'CM'))
    check("m", core.format_mm(600.0, 'M') == "0,6 m", core.format_mm(600.0, 'M'))
    check("arredondado em cm", core.format_mm(604.0, 'CM', rounded=True) == "60,4 cm", core.format_mm(604.0, 'CM', rounded=True))

    check("sem snap o ponto fica como está", core.snap((0.1, 0.1, 0.1), [], 0.02) == ((0.1, 0.1, 0.1), False))
    cantos_objeto = core.snap_candidates(malha.bounds, malha.parts_bounds(), 'OBJETO')
    check("snap no objeto tem oito cantos", len(cantos_objeto) == 8, str(len(cantos_objeto)))
    cantos_ambos = core.snap_candidates(malha.bounds, malha.parts_bounds(), 'AMBOS')
    check("snap em ambos soma objeto e partes", len(cantos_ambos) == 24, str(len(cantos_ambos)))
    ponto, encaixou = core.snap((0.001, 0.001, 0.002), cantos_ambos, 0.02)
    check("snap acha o canto próximo", encaixou and ponto[0] == 0.0, f"{ponto} {encaixou}")
    check("snap fora do limite não encaixa", core.snap((0.15, 0.15, 0.15), cantos_ambos, 0.01)[1] is False)
    session.snap_mode = 'AMBOS'
    check("a sessão aplica o snap configurado", session.snap((0.001, 0.001, 0.002))[1])
    session.snap_mode = 'OFF'
    check("snap desligado não encaixa", session.snap((0.001, 0.001, 0.002))[1] is False)

    item = session.add_measure((0.0, 0.0, 0.0), (0.6, 0.0, 0.0))
    check("medida manual com 600 mm", abs(item['distance_mm'] - 600.0) < 1e-6, str(item['distance_mm']))
    check("rótulo da medida", "600 mm" in item['label'], item['label'])
    check("medida pendente consumida", session.pending is None)
    session.pending = (0.0, 0.0, 0.0)
    session.clear_measures()
    check("limpar medidas zera tudo", not session.medidas and session.pending is None)

    # T013: representações ------------------------------------------------------------------
    tri_persp = draw._triangles(session, session.camera, RECT)
    check("projeção devolve os triângulos visíveis", len(tri_persp) == 24, str(len(tri_persp)))
    check("triângulos ordenados do longe para o perto",
          all(tri_persp[i][1] >= tri_persp[i + 1][1] for i in range(len(tri_persp) - 1)))
    frente = draw._front_facing(tri_persp, session.camera)
    check("faces da frente são menos que o total", 0 < len(frente) <= len(tri_persp), str(len(frente)))
    cor = draw._shade((0.5, 0.5, 0.5, 1.0), (0.0, 0.0, 1.0))
    check("sombreado escurece a face", cor[0] <= 0.5)
    session.toggle_part(0)
    check("parte escondida sai do desenho", len(draw._triangles(session, session.camera, RECT)) < len(tri_persp))
    session.toggle_part(0)
    for representacao in core.REPRESENTATIONS:
        session.representation = representacao
        check(f"representação {representacao} listada", representacao in core.REPRESENTATIONS)
    session.representation = 'SOLIDO'

    # T014: impressão -----------------------------------------------------------------------
    layout = core.print_layout('A3_PAISAGEM', [{'name': 'V1'}, {'name': 'V2'}, {'name': 'V3'}])
    check("folha A3 paisagem", layout['sheet_mm'] == (420.0, 297.0), str(layout['sheet_mm']))
    check("três views na folha", len(layout['views']) == 3)
    dentro_folha = all(0 <= r['rect_mm'][0] and 0 <= r['rect_mm'][1]
                       and r['rect_mm'][0] + r['rect_mm'][2] <= 420.0
                       and r['rect_mm'][1] + r['rect_mm'][3] <= 297.0 for r in layout['views'])
    check("views dentro da folha", dentro_folha, str([r['rect_mm'] for r in layout['views']]))
    caixas = [r['rect_mm'] for r in layout['views']]
    sobrepoe = any(
        not (a[0] + a[2] <= b[0] or b[0] + b[2] <= a[0] or a[1] + a[3] <= b[1] or b[1] + b[3] <= a[1])
        for i, a in enumerate(caixas) for b in caixas[i + 1:])
    check("views não se sobrepõem", not sobrepoe, str(caixas))
    quadrada = core.print_layout('A3_PAISAGEM', [{'name': 'V1', 'proportion': '1:1'}])['views'][0]['rect_mm']
    check("proporção 1:1 deixa a view quadrada", abs(quadrada[2] - quadrada[3]) < 1e-6, str(quadrada))
    menor = core.print_layout('A3_PAISAGEM', [{'name': 'V1', 'size_pct': 50}])['views'][0]['rect_mm']
    check("tamanho 50% reduz a view", menor[2] < quadrada[2], f"{menor} !< {quadrada}")

    view = session.create_view()
    check("criar view com badge", view['name'] == 'V1', view['name'])
    yaw = session.camera.yaw
    session.camera.orbit(15.0, 0.0)
    check("a view guarda a câmera de quando foi criada",
          abs(session.view_camera(view).yaw - yaw) < 1e-9, str(session.view_camera(view).yaw))

    # Operadores da janela ------------------------------------------------------------------
    check("malha medida na sessão", window.open_window is not None and session.malha is malha)
    bpy.ops.caffmob.mesh_measure_option(option='REPRESENTATION', value='RAIO_X')
    check("opção: representação", session.representation == 'RAIO_X', session.representation)
    bpy.ops.caffmob.mesh_measure_option(option='PROJECTION', value='ORTHO')
    check("opção: projeção", session.camera.projection == 'ORTHO', session.camera.projection)
    bpy.ops.caffmob.mesh_measure_option(option='UNIT', value='CM')
    check("opção: unidade", session.unit == 'CM', session.unit)
    bpy.ops.caffmob.mesh_measure_option(option='ROUNDING', value='ROUNDED')
    check("opção: arredondada", session.rounded is True)
    bpy.ops.caffmob.mesh_measure_option(option='SNAP', value='PARTES', number=50.0)
    check("opção: snap e limite", session.snap_mode == 'PARTES' and session.snap_threshold_mm == 50.0,
          f"{session.snap_mode} {session.snap_threshold_mm}")
    bpy.ops.caffmob.mesh_measure_option(option='SHEET', value='A4_RETRATO')
    check("opção: folha", session.sheet == 'A4_RETRATO', session.sheet)
    bpy.ops.caffmob.mesh_measure_option(option='PRINT', value='ON')
    check("opção: impressão ligada", session.print_preview is True)
    bpy.ops.caffmob.mesh_measure_option(option='PRINT', value='OFF')
    check("opção: impressão desligada", session.print_preview is False)
    bpy.ops.caffmob.mesh_measure_option(option='LABELS')
    check("opção: medidas na tela alternam", session.mostrar_medidas is False)
    bpy.ops.caffmob.mesh_measure_option(option='LABELS')

    bpy.ops.caffmob.mesh_measure_part(action='TOGGLE', index=1)
    check("parte escondida pelo operador", malha.parts[1].visible is False)
    bpy.ops.caffmob.mesh_measure_part(action='TOGGLE', index=1)
    bpy.ops.caffmob.mesh_measure_part(action='SELECT', index=1)
    check("parte escolhida pelo operador", session.selected is malha.parts[1])

    bpy.ops.caffmob.mesh_measure_view(action='CREATE')
    check("operador cria view", len(session.views) == 2, str(len(session.views)))
    bpy.ops.caffmob.mesh_measure_view(action='SIZE', index=1, delta=-10.0)
    check("operador muda o tamanho", session.views[1]['size_pct'] == 90.0, str(session.views[1]['size_pct']))
    bpy.ops.caffmob.mesh_measure_view(action='PROPORTION', index=1, value='4:3')
    check("operador muda a proporção", session.views[1]['proportion'] == '4:3')
    bpy.ops.caffmob.mesh_measure_view(action='REMOVE', index=1)
    check("operador remove a view", len(session.views) == 1)

    session.add_measure((0.0, 0.0, 0.0), (0.0, 0.3, 0.0))
    bpy.ops.caffmob.mesh_measure_clear()
    check("operador limpa as medidas", not session.medidas)
    bpy.ops.caffmob.mesh_measure_fit()
    check("operador reenquadra", session.fitted is False)
    check("reler mantém a malha", window.reload(bpy.context) is session and session.malha is not None)
    check("desenho sem área não quebra", draw.draw_window(bpy.context) is None)

    # Registro ------------------------------------------------------------------------------
    check("operador da janela registrado", hasattr(bpy.types, "CAFFMOB_OT_mesh_measure_window"))
    check("conta-gotas registrado", hasattr(bpy.types, "CAFFMOB_OT_mesh_measure_eyedropper"))
    check("painel da Vista 3D registrado", hasattr(bpy.types, "BTM_PT_MeshMeasure3D"))
    check("handler de desenho registrado", bool(window._draw_handle))
    window.unregister()
    check("unregister remove o handler", not window._draw_handle)
    check("unregister remove os painéis", not hasattr(bpy.types, "BTM_PT_MeshMeasureHeader"))
    window.register()
    check("register devolve o handler", bool(window._draw_handle))


if __name__ == '__main__':
    try:
        main()
    except Exception:
        traceback.print_exc()
        FAILURES.append("exceção")
    print(f"blender_027_medicao_malha: {'OK' if not FAILURES else 'FALHAS: ' + ', '.join(FAILURES)}", flush=True)
    sys.exit(1 if FAILURES else 0)
