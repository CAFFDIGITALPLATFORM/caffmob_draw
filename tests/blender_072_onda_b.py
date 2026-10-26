"""072, onda B (T058; RF-01, RF-02, RF-07, RF-08, RF-11, RF-14): espaço livre, gaveteiro, armário autoral e modelos.

Run: blender --background --factory-startup --python-exit-code 1 --python tests/blender_072_onda_b.py
"""
import json
import sys
import traceback
from pathlib import Path

import bpy
from mathutils import Vector

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _authored_env as authored_env  # noqa: E402
import _blender_env as env  # noqa: E402
from caffmob_draw.aggregates import ops_authored  # noqa: E402
from caffmob_draw.customize.adapters import btm  # noqa: E402
from caffmob_draw.drawers import build, core, espaco, inserir, modelos, scene  # noqa: E402

FAILURES = []


def check(ok, label, detail=""):
    print(("OK   " if ok else "FALHA ") + label + (f" ({detail})" if detail and not ok else ""), flush=True)
    if not ok:
        FAILURES.append(label)


def gavetas_de(raiz):
    return [o for o in raiz.children_recursive if scene.is_drawer(o)]


def lista_de_vaos_e_modelo():
    env.clean_scene()
    assert bpy.ops.caffmob.cabinet_builder(width=0.6, door_swing='NONE') == {'FINISHED'}
    raiz = bpy.context.object
    env.settle()
    vaos = espaco.vaos_do_modulo(bpy.context, raiz)
    check(len(vaos) == 1 and vaos[0]['caminho'] == 'module' and vaos[0]['largura'] > 500,
          "a lista mostra o vão do módulo com as medidas", str(vaos))
    b = bpy.context.window_manager.btm_drawer_builder
    b.modelo, b.quantidade = 'secreta', 2
    bpy.ops.caffmob.gaveta_inserir(alvo=json.dumps(vaos[0]))
    gs = gavetas_de(raiz)
    check(len(gs) == 2 and all(scene.spec(g).corredica == 'oculta_toque' and scene.spec(g).puxador == 'sem'
                               for g in gs), "o modelo Gaveta secreta entra com oculta toque e sem puxador")
    return raiz


def espaco_pelo_raio(raiz):
    lo, hi = btm.space_boxes(bpy.context, raiz)["module"]
    centro = raiz.matrix_world @ Vector(((lo[0] + hi[0]) / 2, (lo[1] + hi[1]) / 2, (lo[2] + hi[2]) / 2))
    direcao = Vector((0, 1, 0))
    alvo = espaco.no_ponto(bpy.context, raiz, centro + direcao * 0.05, direcao)
    check(alvo is not None and alvo['tipo'] == 'BTM' and alvo['caminho'] == 'module' and alvo['ocupado'],
          "o ponto clicado no vão acha o vão do módulo (ocupado pelas gavetas)", str(alvo))


def gaveteiro_volante():
    env.clean_scene()
    b = bpy.context.window_manager.btm_drawer_builder
    b.modelo, b.corredica, b.quantidade = 'NENHUM', 'telescopica_soft', 3
    b.largura, b.altura, b.profundidade, b.metodo, b.tipo = 450, 600, 500, 'BASE', 'volante'
    check(bpy.ops.caffmob.gaveteiro_criar() == {'FINISHED'}, "o gaveteiro volante é criado")
    raiz = bpy.context.view_layer.objects.active
    cab = raiz.btm_cabinet
    check(cab.assembly == 'BASE' and abs(cab.thickness_top - 0.025) < 1e-6, "base passante com tampo de 25 mm")
    lo, hi = btm.space_boxes(bpy.context, raiz)["module"]
    check(abs((hi[2] - lo[2]) * 1000 - (600 - 18 - 25)) < 0.6, "vão de 557 mm de altura (600 − 18 − 25)",
          str(round((hi[2] - lo[2]) * 1000, 1)))
    check(raiz.btm_structure.extras_dict().get('CASTERS', {}).get('enabled'), "com rodízios")
    check(len(gavetas_de(raiz)) == 3, "com as 3 gavetas", str(len(gavetas_de(raiz))))


def armario(profundidade=0.56):
    env.clean_scene()
    raiz = bpy.data.objects.new('Armário', None)
    bpy.context.collection.objects.link(raiz)
    t, p = 0.018, profundidade
    pecas = [('Lateral E', (t, p, 2.0), (t / 2, p / 2, 1.0)), ('Lateral D', (t, p, 2.0), (.6 - t / 2, p / 2, 1.0)),
             ('Base', (.6 - 2 * t, p - .006, t), (.3, (p - .006) / 2, t / 2)),
             ('Tampo', (.6 - 2 * t, p - .006, t), (.3, (p - .006) / 2, 2 - t / 2)),
             ('Fundo', (.6 - 2 * t, .006, 2.0), (.3, p - .003, 1.0)),
             ('Prateleira', (.6 - 2 * t, p - .02, t), (.3, (p - .02) / 2, .7 + t / 2))]
    objs = [authored_env.cube(n, s, l, raiz) for n, s, l in pecas]
    env.settle()
    ops_authored.adopt(raiz, [raiz] + objs, 'NEG_Y')
    return raiz


def armario_autoral():
    raiz = armario()
    alvo = espaco.no_ponto(bpy.context, raiz.children[0], raiz.matrix_world @ Vector((0.3, 0.3, 0.3)),
                           Vector((0, 1, 0)))
    check(alvo is not None and alvo['tipo'] == 'AUTHORED' and alvo['altura'] == 682.0, "espaço livre no armário autoral",
          str(alvo and (alvo['tipo'], alvo['altura'])))
    b = bpy.context.window_manager.btm_drawer_builder
    b.modelo, b.corredica, b.quantidade = 'interna', 'telescopica', 2
    check(bpy.ops.caffmob.gaveta_inserir(alvo=json.dumps(alvo)) == {'FINISHED'} and len(gavetas_de(raiz)) == 2,
          "gaveta interna no armário autoral")
    f0 = gavetas_de(raiz)[0]
    for o in bpy.context.selected_objects:
        o.select_set(False)
    f0.select_set(True)
    bpy.context.view_layer.objects.active = f0
    b.nome_do_modelo = "Interna Hettich"
    bpy.ops.caffmob.gaveta_salvar_modelo()
    salvo = modelos.por_id('usuario:interna_hettich', build.pasta_do_usuario())
    check(salvo is not None and salvo.gaveta['corredica'] == 'telescopica', "salvar a gaveta como modelo e reler")


def nicho_raso():
    raiz = armario(profundidade=0.29)
    alvo = espaco.espaco_livre_do_autoral(raiz, (0.3, 0.1, 0.3))
    motivos = inserir.inserir(bpy.context, alvo, 1, core.Gaveta())
    check(motivos and 'menor que a menor corrediça (300 mm)' in motivos[0], "nicho raso recusado com o motivo",
          str(motivos))
    check(not gavetas_de(raiz), "nada é inserido no nicho raso")


try:
    raiz = lista_de_vaos_e_modelo()
    espaco_pelo_raio(raiz)
    gaveteiro_volante()
    armario_autoral()
    nicho_raso()
except Exception:
    traceback.print_exc()
    FAILURES.append("exceção")
print(f"blender_072_onda_b: {'OK' if not FAILURES else 'FALHAS: ' + ', '.join(FAILURES)}", flush=True)
sys.exit(1 if FAILURES else 0)
