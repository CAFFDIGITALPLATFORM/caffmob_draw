"""Onda 8 da 067 (T185; RF-160 a RF-166, D-37 a D-45): unidade única, várias paredes e parede e porta do MOBI.

Run: blender --background --factory-startup --python-exit-code 1 --python tests/blender_067_onda8.py

Cobre os quatro cenários da sessão 2026-10-25 do requirements (pé-direito na unidade do projeto; espessura de várias
paredes de uma vez; portão do MOBI no painel; largura maior que a parede) e os critérios dos RF-160 a RF-166, sobre o
ambiente sintético `_mobi_sintetico` (nunca um documento de produção). Sem janela, o timer do campo não roda: o
ensaio chama a fila do `mobi_fields` direto, que é o que o timer faria.
"""

import json
import sys
import time
import traceback
from pathlib import Path

import bpy

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _blender_env as env  # noqa: E402,F401
import _fixtures_067 as fx  # noqa: E402
import _mobi_sintetico as ms  # noqa: E402
from caffmob_draw.selection import classify, component_select  # noqa: E402
from caffmob_draw.target import mobi_fields, snapshot, view  # noqa: E402
from caffmob_draw.target import resolver as r  # noqa: E402
from caffmob_draw.walls2d import model, props, selecao_classica  # noqa: E402

FAILURES = []


def check(ok, label, detail=""):
    print(("OK   " if ok else "FALHA ") + label + (f" ({detail})" if detail and not ok else ""), flush=True)
    if not ok:
        FAILURES.append(label)


def documento():
    return json.loads(bpy.context.scene['caffmob_ambiente'])


def abertura(d, id_):
    return next(a for a in d['aberturas'] if a['id'] == id_)


def objeto(tipo, id_=None):
    return next(o for o in bpy.context.scene.objects
                if o.get('caffmob_tipo') == tipo and (id_ is None or o.get('caffmob_id') == id_))


def selecionar(obj):
    for o in bpy.context.selected_objects:
        o.select_set(False)
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    component_select.forget()
    bpy.context.view_layer.update()
    component_select.normalize(bpy.context, bpy.context.scene)
    return snapshot.ensure(bpy.context)


def unidade():
    cena = bpy.context.scene
    check(cena.btm_settings.btm_unit == 'MILLIMETERS' and cena.unit_settings.length_unit == 'MILLIMETERS',
          "importar do MOBI deixa a cena na unidade do projeto (mm)", cena.unit_settings.length_unit)
    cena.btm_settings.btm_unit = 'METERS'
    check(cena.unit_settings.length_unit == 'METERS', "trocar a unidade do projeto troca a da cena")
    bpy.ops.caffmob.change_units(unit_system='METRIC', length_unit='CENTIMETERS')
    check(cena.btm_settings.btm_unit == 'CENTIMETERS' and cena.unit_settings.length_unit == 'CENTIMETERS',
          "o menu de unidades grava a unidade do projeto")
    cena.btm_settings.btm_unit = 'MILLIMETERS'
    state = bpy.context.window_manager.btm_wall_editor
    texto = bpy.utils.units.to_string('METRIC', 'LENGTH', state.new_thickness)
    check(cena.unit_settings.length_unit == 'MILLIMETERS', "\"Novas paredes\" usa a unidade da cena alinhada", texto)


def lote():
    plano = model.WallPlan([model.rectangle(4.0, 3.0, thickness=0.14, height=2.6)])
    plano.chains[0].segments[2].thickness = 0.19
    s = props.start(plano, bpy.context.scene.name)
    try:
        state = bpy.context.window_manager.btm_wall_editor
        s.multi = selecao_classica.todos(s.plan)
        s.selected = s.multi[-1]
        check(len(s.multi) == 4, "A seleciona todas as paredes do plano")
        check(state.thickness_text == '' and props.multiplos(s, 'thickness'),
              "espessuras diferentes mostram Múltiplos", state.thickness_text)
        state.thickness_text = '150'
        check({round(sg.thickness, 6) for sg in s.plan.chains[0].segments} == {0.15}, "digitar 150 muda as quatro")
        check(s.undo() and {round(sg.thickness, 6) for sg in s.plan.chains[0].segments} == {0.14, 0.19},
              "um desfazer volta as quatro")
        check(not props.campo_de_um_trecho_editavel(s, 'length'), "comprimento fica cinza em seleção múltipla")
        s.multi = [s.multi[0]]
        check(props.campo_de_um_trecho_editavel(s, 'length'), "com um trecho, o comprimento volta")
    finally:
        props.end()


def portao():
    d0 = documento()
    folha = next(o for o in objeto('abertura', ms.PORTAO).children if o.type == 'MESH')
    target = selecionar(folha)
    raiz = objeto('abertura', ms.PORTAO)
    check(bpy.context.view_layer.objects.active is raiz, "clicar na folha seleciona o portão inteiro")
    check(target is not None and target.kind == r.OPENING and target.library == 'MOBI' and target.detail == 'DOOR',
          "o painel reconhece o portão como Porta do MOBI", str(target and (target.kind, target.library)))
    check(target.owner_name.endswith('· trecho 2'), "o cabeçalho diz em <parede> · trecho 2", target.owner_name)
    modelo = view.build(target, view.COMPLETE)
    campos = {(f.data, f.prop) for f in view.fields(modelo)}
    check({('mobi', 'largura'), ('mobi', 'altura'), ('mobi', 'peitoril'), ('mobi', 'posicao')} <= campos,
          "largura, altura, peitoril e distância do início no painel", str(campos))
    check(not any(p in ('scale', 'location', 'rotation_euler') for _d, p in campos),
          "o painel não oferece escala nem posição", str(campos))
    wm = bpy.context.window_manager
    check(wm.btm_mobi.largura.replace(' ', '').startswith('3500'), "a largura mostra 3500 mm", wm.btm_mobi.largura)
    wm.btm_mobi.largura = '3000'
    inicio = time.perf_counter()
    mobi_fields._tick()
    duracao = time.perf_counter() - inicio
    print(f"INFO edição pelo painel: {duracao * 1000:.0f} ms", flush=True)
    d = documento()
    check(abertura(d, ms.PORTAO)['largura'] == 3000, "digitar 3000 grava 3000 no documento")
    raiz = objeto('abertura', ms.PORTAO)
    check(json.loads(raiz['caffmob_abertura'])['largura'] == 3000 and all(
        tuple(round(v, 6) for v in o.scale) == (1.0, 1.0, 1.0) for o in raiz.children),
        "o 3D remonta com o vão de 3,0 m, sem escala nas peças")
    check(bpy.context.view_layer.objects.active is raiz, "a porta continua selecionada depois de remontar")
    check(classify.move_over_denial(next(o for o in raiz.children if o.type == 'MESH')) is not None,
          "a porta do MOBI não se move no Mover Sobre")
    check(abertura(d0, ms.JANELA) == abertura(d, ms.JANELA), "a outra abertura não muda")
    return d


def largura_demais():
    antes = documento()
    selecionar(objeto('abertura', ms.PORTAO))
    try:
        resultado = bpy.ops.caffmob.mobi_editar_entidade(tipo='abertura', entidade_id=ms.PORTAO, campo='largura',
                                                         valor_mm=12000, original=bpy.context.scene['caffmob_ambiente'])
        motivo = ''
    except RuntimeError as exc:                         # o relatório de erro vira exceção quando chamado do Python
        resultado, motivo = {'CANCELLED'}, str(exc)
    check(resultado == {'CANCELLED'} and documento() == antes and 'maior que a parede' in motivo,
          "largura de 12000 mm é recusada com o motivo e nada muda", motivo)
    bpy.context.window_manager.btm_mobi.largura = '12000'
    mobi_fields._tick()
    check(documento() == antes and 'maior que a parede' in bpy.context.window_manager.btm_target.error,
          "pelo campo, a recusa mostra o motivo", bpy.context.window_manager.btm_target.error)


def parede():
    alvo = selecionar(objeto('parede'))
    check(alvo.kind == r.WALL and alvo.library == 'MOBI', "a parede do MOBI aparece como Parede")
    modelo = view.build(alvo, view.COMPLETE)
    linhas = [tuple(i.args) for s in modelo.sections for i in s.items if getattr(i, 'text', '') == "Trecho {}: {}"]
    check(('2', 'mobi.mm.10000') in linhas and len(linhas) == 4, "a linha do trecho 2 mostra 10000 mm", str(linhas))
    from caffmob_draw.ui import object_properties as op
    check(op._note_args(bpy.context, alvo, None, ('mobi.mm.10000',))[0].replace(' ', '').startswith('10000'),
          "a medida do trecho sai na unidade do projeto")
    campos = {(f.data, f.prop) for f in view.fields(modelo)}
    check({('mobi', 'parede_altura'), ('mobi', 'parede_espessura')} <= campos and not any(
        p in ('scale', 'location', 'rotation_euler') for _d, p in campos),
        "altura e espessura da parede, sem posição nem escala", str(campos))
    acoes = {a.operator for a in view.actions(modelo)}
    check('caffmob.wall_editor' in acoes and 'caffmob.mobi_selecionar_abertura' in acoes,
          "\"Abrir no editor de parede\" e as aberturas clicáveis", str(acoes))
    wm = bpy.context.window_manager
    wm.btm_mobi.parede_altura = '2800'
    mobi_fields._tick()
    trechos = documento()['paredes'][0]['segmentos']
    check({(s['pe_direito_inicial'], s['pe_direito_final']) for s in trechos} == {(2800, 2800)},
          "mudar a altura grava os quatro trechos")


def editar_segmento():
    from caffmob_draw.ui import sidebar_project
    check(not sidebar_project.editar_segmento_visivel(bpy.context), "\"Editar segmento\" some com documento v2")


def tempo_com_modulo():
    """R15 (T209): a edição pelo painel remonta a cena inteira, como o OK do editor de parede. Mede com um módulo na
    cena; acima de 1 s a remontagem parcial vira ação nova (registro, não falha)."""
    fx.ambiente_mobi_sintetico(com_modulo=True)
    selecionar(objeto('abertura', ms.PORTAO))
    tempos = []
    for largura in (3100, 3200, 3300):
        bpy.context.window_manager.btm_mobi.largura = str(largura)
        inicio = time.perf_counter()
        mobi_fields._tick()
        tempos.append((time.perf_counter() - inicio) * 1000)
    print(f"INFO R15 edição com módulo: {', '.join(f'{t:.0f}' for t in tempos)} ms", flush=True)
    check(abertura(documento(), ms.PORTAO)['largura'] == 3300, "três edições seguidas com módulo na cena")


try:
    fx.ambiente_mobi_sintetico()
    unidade()
    lote()
    portao()
    largura_demais()
    parede()
    editar_segmento()
    tempo_com_modulo()
except Exception:
    traceback.print_exc()
    FAILURES.append("exceção")
print(f"blender_067_onda8: {'OK' if not FAILURES else 'FALHAS: ' + ', '.join(FAILURES)}", flush=True)
sys.exit(1 if FAILURES else 0)
