"""071, onda B (T048; RF-20 a RF-32): editor de escadas de marcenaria no Blender.

Run: blender --background --factory-startup --python-exit-code 1 --python tests/blender_071_escadas.py

Sem janela, o modal de inserção e o timer do campo não rodam: o ensaio chama o `execute` do inserir (na posição do
cursor 3D) e a fila do campo direto, que é o que o timer faria.
"""
import json
import sys
import traceback
from pathlib import Path

import bpy

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _blender_env as env  # noqa: E402,F401
from caffmob_draw.cutting import hardware, part_extractor  # noqa: E402
from caffmob_draw.selection import component_select  # noqa: E402
from caffmob_draw.stairs import props, scene  # noqa: E402
from caffmob_draw.target import snapshot, view  # noqa: E402
from caffmob_draw.target import resolver as r  # noqa: E402

FAILURES = []


def check(ok, label, detail=""):
    print(("OK   " if ok else "FALHA ") + label + (f" ({detail})" if detail and not ok else ""), flush=True)
    if not ok:
        FAILURES.append(label)


def pecas(raiz, papel):
    return [c for c in raiz.children if json.loads(c.get(scene.PART_PROP) or '{}').get('papel') == papel]


def selecionar(obj):
    for o in bpy.context.selected_objects:
        o.select_set(False)
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    component_select.forget()
    bpy.context.view_layer.update()
    component_select.normalize(bpy.context, bpy.context.scene)
    return snapshot.ensure(bpy.context)


def grupo_escadas():
    from caffmob_draw.ui import sidebar_build
    fonte = Path(sidebar_build.__file__).read_text(encoding='utf-8')
    check('stairs_ui.draw(body, context)' in fonte and 'HOME_BUILDER_PT_room_layout_stairs, body' not in fonte,
          "o grupo Escadas mostra o editor novo, sem o painel do Home Builder")
    check(hasattr(bpy.ops.caffmob_stairs, 'place_stairs'), "a escada herdada segue registrada para arquivos antigos")


def inserir_reta():
    env.clean_scene()
    state = bpy.context.window_manager.btm_stairs
    state.inicial()
    state.altura = '2800'
    _, texto = __import__('caffmob_draw.stairs.core', fromlist=['core']).leitura(state.escada())
    check(texto.startswith('16 espelhos de 175 mm'), "2800 mm em reta dá 16 espelhos de 175 mm", texto)
    bpy.ops.caffmob.escada_inserir('EXEC_DEFAULT')
    raiz = bpy.data.objects[state.editando]
    check(scene.is_root(raiz) and not raiz.get('caffmob_tipo'), "a escada nasce como raiz própria, sem caffmob_tipo")
    check((len(pecas(raiz, 'degrau')), len(pecas(raiz, 'espelho')), len(pecas(raiz, 'lateral'))) == (15, 15, 30),
          "15 degraus, 15 espelhos e 30 laterais")
    check(len(pecas(raiz, 'corrimao')) == 1 and pecas(raiz, 'corrimao')[0].hide_viewport, "o corrimão vai oculto")
    return raiz


def aplicar_l_esquerda(raiz):
    state = bpy.context.window_manager.btm_stairs
    state.tipo = 'L'
    state.giro = 'esquerda'
    bpy.ops.caffmob.escada_aplicar()
    bpy.ops.caffmob.escada_aplicar()
    check(len(pecas(raiz, 'patamar')) == 1 and len(pecas(raiz, 'degrau')) == 14,
          "em L: patamar e 14 degraus, sem duplicar ao aplicar duas vezes")
    e = scene.spec(raiz)
    ultimo = max(pecas(raiz, 'degrau'), key=lambda o: json.loads(o[scene.PART_PROP])['indice'])
    check(e.giro == 'esquerda' and ultimo.location.x * 1000 < e.x / 2, "o segundo lance vai para a esquerda")


def plano_de_corte(raiz):
    partes, _ = part_extractor.extract_production_parts(bpy.context)
    da_escada = [p for p in partes if getattr(p, 'source', '') == 'STAIRS']
    check(len(da_escada) == len([c for c in raiz.children if c.type == 'MESH']),
          "cada chapa da escada entra no plano de corte", f"{len(da_escada)}")
    linhas = [l for l in hardware.collect(bpy.context.scene) if l['code'] == 'CORRIMAO']
    check(len(linhas) == 1 and linhas[0]['quantity'] == 1 and linhas[0]['length_m'] > 2.8,
          "o corrimão entra nas ferragens, com os metros", str(linhas))


def painel(raiz):
    degrau = pecas(raiz, 'degrau')[0]
    alvo = selecionar(degrau)
    check(bpy.context.view_layer.objects.active is raiz, "clicar num degrau seleciona a escada")
    check(alvo is not None and alvo.kind == r.OTHER and alvo.detail == 'STAIR', "o painel reconhece a escada",
          str(alvo and (alvo.kind, alvo.detail)))
    modelo = view.build(alvo, view.COMPLETE)
    campos = {(f.data, f.prop) for f in view.fields(modelo)}
    acoes = {a.operator for a in view.actions(modelo)}
    check({('stair', 'tipo'), ('stair', 'altura'), ('stair', 'largura')} <= campos and 'caffmob.escada_editar' in acoes,
          "tipo, altura, largura e \"Abrir no editor de escadas\" no painel", str((campos, acoes)))
    sel = bpy.context.window_manager.btm_stair_sel
    check(sel.altura.replace(' ', '').startswith('2800'), "a altura da escada selecionada aparece", sel.altura)
    sel.altura = '3000'
    props._tick()
    check(abs(scene.spec(raiz).z - 3000) < 0.5, "editar a altura pelo painel regenera a escada")


def remontagem_do_mobi_preserva(raiz):
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import _fixtures_067 as fx
    nome = raiz.name
    fx.ambiente_mobi_sintetico()
    check(bpy.data.objects.get(nome) is not None and scene.is_root(bpy.data.objects[nome]),
          "montar um ambiente do MOBI preserva a escada de marcenaria")


try:
    grupo_escadas()
    raiz = inserir_reta()
    aplicar_l_esquerda(raiz)
    plano_de_corte(raiz)
    painel(raiz)
    remontagem_do_mobi_preserva(raiz)
except Exception:
    traceback.print_exc()
    FAILURES.append("exceção")
print(f"blender_071_escadas: {'OK' if not FAILURES else 'FALHAS: ' + ', '.join(FAILURES)}", flush=True)
sys.exit(1 if FAILURES else 0)
