"""072, onda A (T038; RF-03 a RF-06, RF-09 a RF-12, RF-15): gavetas do construtor no módulo rápido.

Run: blender --background --factory-startup --python-exit-code 1 --python tests/blender_072_gavetas.py

Sem janela, o timer do campo do painel não roda: o ensaio chama a fila dele direto, que é o que o timer faria.
"""
import json
import sys
import traceback
from pathlib import Path

import bpy

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _blender_env as env  # noqa: E402,F401
from caffmob_draw import mechanisms  # noqa: E402
from caffmob_draw.customize.adapters import btm  # noqa: E402
from caffmob_draw.cutting import hardware, json_exporter, part_extractor  # noqa: E402
from caffmob_draw.drawers import core, props, scene  # noqa: E402
from caffmob_draw.geometry import subspace_fronts  # noqa: E402
from caffmob_draw.selection import component_select  # noqa: E402
from caffmob_draw.target import snapshot, view  # noqa: E402

FAILURES = []


def check(ok, label, detail=""):
    print(("OK   " if ok else "FALHA ") + label + (f" ({detail})" if detail and not ok else ""), flush=True)
    if not ok:
        FAILURES.append(label)


def frentes(root, path="module"):
    return sorted((o for o in subspace_fronts.fronts_of(root, path) if o.get('hb_part_role') == 'DRAWER_FRONT'),
                  key=lambda o: o.matrix_world.translation.z)


def peca(front, papel):
    return next(c for c in front.children if json.loads(c.get(scene.PART_PROP) or '{}').get('papel') == papel)


def mm(v):
    return round(v * 1000, 1)


def modulo():
    env.clean_scene()
    assert bpy.ops.caffmob.cabinet_builder(width=0.6, door_swing='LEFT') == {'FINISHED'}
    root = bpy.context.object
    env.settle()
    lo, hi = btm.space_boxes(bpy.context, root)["module"]
    return root, mm(hi[0] - lo[0])


def tres_gavetas(root, largura):
    g = core.Gaveta(corredica='telescopica_soft').para_dict()
    check(btm.set_front(bpy.context, root, root, 'DRAWERS', 3, g) == [], "3 gavetas com telescópica soft")
    fs = frentes(root)
    check(len(fs) == 3 and all(scene.is_drawer(f) for f in fs), "as 3 frentes são gavetas do construtor")
    papeis = sorted(json.loads(c[scene.PART_PROP])['papel'] for c in fs[0].children if c.get(scene.PART_PROP))
    check(papeis == ['contra_frente', 'fundo', 'lateral', 'lateral', 'traseira'], "caixa com 5 peças", str(papeis))
    check(mm(peca(fs[0], 'contra_frente').dimensions.x) == largura - 26 - 30,
          f"contra-frente = vão ({largura}) − 26 − 30", str(mm(peca(fs[0], 'contra_frente').dimensions.x)))
    comp = scene.comprimento(fs[0])
    check(mm(peca(fs[0], 'lateral').dimensions.y) == comp and comp in (300, 350, 400, 450, 500, 550),
          "laterais com o comprimento nominal", str(comp))
    check(abs(fs[0].btm_aggregate.travel - comp / 1000) < 1e-6 and mechanisms.of(fs[0]).kind == mechanisms.DRAWER,
          "a gaveta corre o comprimento da corrediça")
    return fs


def producao(root, n_gavetas, corredica, comprimento):
    partes, _ = part_extractor.extract_production_parts(bpy.context)
    gav = [p for p in partes if p.source == 'DRAWERS']
    check(len(gav) == n_gavetas * 6, "frente e 5 peças por gaveta no plano de corte", str(len(gav)))
    linhas = hardware.collect(bpy.context.scene)
    codigo = f"CORREDICA_{corredica}_{int(comprimento)}"
    check(any(l['code'] == codigo and l['quantity'] == n_gavetas for l in linhas)
          and not any(l['code'] in ('CORREDICA', 'CORREDICA_BLUM') for l in linhas),
          "ferragem por corrediça e comprimento, sem a contagem genérica", str(linhas))
    payload = json_exporter.build_global_payload({}, {}, partes, hardware=linhas)
    check(json_exporter.validate_global_json(payload) == [], "o JSON do plano de corte valida com as gavetas",
          str(json_exporter.validate_global_json(payload)[:3]))
    return partes


def trocar(root, largura, fs):
    antes = fs[0].matrix_world.translation.copy()
    bpy.ops.caffmob.gaveta_corredica(gaveta=fs[0].name, corredica='oculta_soft')
    f0 = frentes(root)[0]
    check(scene.spec(f0).corredica == 'oculta_soft', "troca para oculta com um botão")
    check(mm(peca(f0, 'contra_frente').dimensions.x) == largura - 10 - 30, "a caixa alarga 16 mm",
          str(mm(peca(f0, 'contra_frente').dimensions.x)))
    traseira = json.loads(peca(f0, 'traseira')[scene.PART_PROP])
    check(traseira['furos'] and traseira['furos'][0]['diametro'] == 6, "furo de 6 mm na traseira")
    check((f0.matrix_world.translation - antes).length < 1e-6, "a frente não se mexe")
    item = subspace_fronts.specs(root)["module"]
    check(item['gavetas'][0]['corredica'] == 'oculta_soft' and item['gavetas'][1]['corredica'] == 'telescopica_soft',
          "o pedido do vão grava a troca só da primeira gaveta")
    partes, _ = part_extractor.extract_production_parts(bpy.context)
    furadas = [p for p in partes if p.source == 'DRAWERS' and p.drilling]
    check(len(furadas) == 1, "a traseira da oculta leva o furo no plano de corte", str(len(furadas)))


def recusa(root):
    g = core.Gaveta(corredica='telescopica', lateral=18).para_dict()
    btm.set_front(bpy.context, root, root, 'DRAWERS', 2, g)
    f0 = frentes(root)[0]
    try:
        bpy.ops.caffmob.gaveta_corredica(gaveta=f0.name, corredica='oculta_soft')
        motivo = ''
    except RuntimeError as exc:
        motivo = str(exc)
    check('até 16 mm' in motivo and scene.spec(frentes(root)[0]).corredica == 'telescopica',
          "oculta em gaveta de lateral 18 é recusada com o motivo, sem mudar", motivo)
    raso = btm.set_front(bpy.context, root, root, 'DRAWERS', 2, core.Gaveta(comprimento=800).para_dict())
    check(raso and any('800' in m for m in raso), "comprimento que não cabe é recusado com o motivo", str(raso))


def remontagem(root):
    btm.set_front(bpy.context, root, root, 'DRAWERS', 3, core.Gaveta(corredica='telescopica_soft').para_dict())
    bpy.ops.caffmob.gaveta_corredica(gaveta=frentes(root)[0].name, corredica='oculta_soft')
    boxes = btm.space_boxes(bpy.context, root)
    lo, hi = boxes["module"]
    novo = (lo, (hi[0] + 0.1, hi[1], hi[2]))
    subspace_fronts.rebuild_all(root, {"module": novo})
    fs = frentes(root)
    check(len(fs) == 3 and scene.spec(fs[0]).corredica == 'oculta_soft' and scene.spec(fs[1]).corredica ==
          'telescopica_soft', "refazer o módulo mantém a corrediça de cada gaveta")


def antiga(root):
    btm.set_front(bpy.context, root, root, 'DRAWERS', 2)
    fs = frentes(root)
    caixas = [c for c in fs[0].children if c.get('hb_part_role') == 'CLOSET_DRAWER_BOX']
    check(not scene.is_drawer(fs[0]) and len(caixas) == 1 and caixas[0].get(scene.PART_PROP) is None,
          "pedido sem corrediça segue a caixa de antes (arquivo antigo igual)")
    linhas = hardware.collect(bpy.context.scene)
    check(any(l['code'] == 'CORREDICA' and l['quantity'] == 2 for l in linhas), "a gaveta antiga conta como antes")
    bpy.ops.caffmob.gaveta_corredica(gaveta=fs[0].name, corredica='telescopica')
    f0 = frentes(root)[0]
    check(scene.is_drawer(f0) and len([c for c in f0.children if c.get(scene.PART_PROP)]) == 5,
          "trocar a corrediça converte a gaveta antiga")


def painel(root):
    btm.set_front(bpy.context, root, root, 'DRAWERS', 2, core.Gaveta(corredica='telescopica_soft').para_dict())
    f0 = frentes(root)[0]
    for o in bpy.context.selected_objects:
        o.select_set(False)
    f0.select_set(True)
    bpy.context.view_layer.objects.active = f0
    component_select.forget()
    alvo = snapshot.ensure(bpy.context)
    check(alvo is not None and alvo.detail == 'DRAWER', "a frente da gaveta aparece como gaveta no painel",
          str(alvo and (alvo.kind, alvo.detail)))
    campos = {(f.data, f.prop) for f in view.fields(view.build(alvo, view.COMPLETE))}
    check(('drawer', 'corredica') in campos, "o painel tem a lista de corrediças", str(campos))
    sel = bpy.context.window_manager.btm_drawer_sel
    check(sel.corredica == 'telescopica_soft' and sel.comprimento.endswith('mm'), "mostra a corrediça e o comprimento")
    sel.corredica = 'oculta_toque'
    props._tick()
    check(scene.spec(frentes(root)[0]).corredica == 'oculta_toque', "trocar pela lista do painel troca a corrediça")


try:
    root, largura = modulo()
    print(f"INFO largura livre do vão: {largura} mm", flush=True)
    fs = tres_gavetas(root, largura)
    producao(root, 3, 'TELESCOPICA_SOFT', scene.comprimento(fs[0]))
    trocar(root, largura, fs)
    recusa(root)
    remontagem(root)
    antiga(root)
    painel(root)
except Exception:
    traceback.print_exc()
    FAILURES.append("exceção")
print(f"blender_072_gavetas: {'OK' if not FAILURES else 'FALHAS: ' + ', '.join(FAILURES)}", flush=True)
sys.exit(1 if FAILURES else 0)
