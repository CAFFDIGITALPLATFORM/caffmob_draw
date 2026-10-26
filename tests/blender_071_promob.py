"""071, onda A (T042; RF-01 a RF-13): importar o `.promob` sintético no Blender.

Run: blender --background --factory-startup --python-exit-code 1 --python tests/blender_071_promob.py

Sem janela, o timer da importação não dispara: o ensaio chama `importar` (que troca para o arquivo novo) e depois
`_montar`, que é o que o timer faria. O desfazer da importação foi provado em janela pelo protótipo T003.
Só o arquivo sintético (RN-02).
"""
import json
import math
import os
import sys
import tempfile
import time
import traceback
from pathlib import Path

import bpy

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _blender_env as env  # noqa: E402,F401
import _promob_sintetico as ps  # noqa: E402
from caffmob_draw import mechanisms  # noqa: E402
from caffmob_draw.cutting import json_exporter, part_extractor  # noqa: E402
from caffmob_draw.promob import complemento, ops  # noqa: E402
from caffmob_draw.selection import component_select  # noqa: E402
from caffmob_draw.target import mobi_fields, snapshot  # noqa: E402
from caffmob_draw.target import resolver as r  # noqa: E402

FAILURES = []
PASTA = tempfile.mkdtemp(prefix='caffmob_071_')


def check(ok, label, detail=""):
    print(("OK   " if ok else "FALHA ") + label + (f" ({detail})" if detail and not ok else ""), flush=True)
    if not ok:
        FAILURES.append(label)


def importar(dados, nome='Cozinha teste.promob', indice=None):
    caminho = ps.gravar(os.path.join(PASTA, nome), dados)
    erro = ops.importar(caminho, indice)
    if erro is None:
        if bpy.app.timers.is_registered(ops._montar):
            bpy.app.timers.unregister(ops._montar)
        ops._montar()
    return erro, caminho


def colecao():
    return next(c for c in bpy.data.collections if c.name.startswith('Promob · '))


def obj(nome):
    return next(o for o in colecao().all_objects if o.name == nome or o.name.startswith(nome + '.'))


def entradas():
    check(hasattr(bpy.types, 'CAFFMOB_FH_promob'), "arrastar .promob para a janela tem FileHandler")
    funcoes = getattr(bpy.types.TOPBAR_MT_file_import.draw, '_draw_funcs', [])
    check(ops.menu_importar in funcoes, "Arquivo › Importar tem o projeto do Promob")


def ambiente():
    bpy.ops.mesh.primitive_cube_add()
    bpy.context.active_object.name = 'Do arquivo anterior'
    erro, caminho = importar(ps.promob())
    check(erro is None, "a importação do sintético não dá erro", str(erro))
    cena = bpy.context.scene
    check('Do arquivo anterior' not in bpy.data.objects, "o projeto abre num arquivo novo")
    d = json.loads(cena['caffmob_ambiente'])
    check(len(d['paredes']) == 1 and len(d['aberturas']) == 2, "documento do MOBI com a parede e as duas aberturas")
    paredes = [o for o in cena.objects if o.get('caffmob_tipo') == 'parede']
    aberturas = [o for o in cena.objects if o.get('caffmob_tipo') == 'abertura']
    check(len(paredes) == 1 and len(aberturas) == 2, "a parede e as aberturas estão na cena")
    trechos = json.loads(paredes[0]['caffmob_parede'])['segmentos']
    check([round(s['comprimento']) for s in trechos] == [3000, 2500] and {s['espessura'] for s in trechos} == {150}
          and {s['pe_direito_inicial'] for s in trechos} == {2700}, "medidas da parede iguais às do arquivo")
    check(cena.unit_settings.length_unit == 'MILLIMETERS', "a cena fica em mm")
    balcao = obj('Balcão 600')
    check(balcao.type == 'EMPTY' and len(balcao.children) == 3, "o balcão é um grupo com as três peças")
    porta = obj('Porta')
    check(tuple(round(v, 4) for v in porta.dimensions) == (0.6, 0.018, 0.7), "a porta do balcão tem as medidas",
          str(tuple(porta.dimensions)))
    lateral = obj('Lateral direita')
    check(tuple(round(v, 4) for v in lateral.matrix_world.translation) == (1.085, 0.62, 0.0),
          "a lateral fica no canto frontal do Promob", str(tuple(lateral.matrix_world.translation)))
    check(obj('Oculto').hide_viewport, "item oculto no Promob entra oculto")
    madeira = next(m for m in bpy.data.materials if m.get('btm_promob_material') == 'madeira')
    imagens = [n.image for n in madeira.node_tree.nodes if n.type == 'TEX_IMAGE']
    check(imagens and imagens[0].packed_file is not None, "a textura do arquivo fica embutida")
    check(obj('Piso').type == 'MESH' and len(obj('Piso').data.vertices) > 8, "a laje com arco é uma malha extrudada")
    externa = obj('EntidadeExterna')
    malhas = [o for o in externa.children if o.type == 'MESH']
    from mathutils import Vector
    cantos = [o.matrix_world @ Vector(c) for o in malhas for c in o.bound_box]
    medidas = tuple(round(max(c[k] for c in cantos) - min(c[k] for c in cantos), 4) for k in range(3)) if cantos else ()
    check(medidas == (0.6, 0.4, 0.2), "a malha vinculada entra ajustada à caixa do item", str(medidas))
    check(not any(o.get('caffmob_tipo') for o in colecao().all_objects), "o complemento não leva caffmob_tipo")
    dados = complemento.lido(bpy.context)
    check(dados['arquivo'] == 'Cozinha teste.promob' and len(dados['sha256']) == 64, "a cena guarda de onde veio")
    check(dados['cliente'] == {'NOMECLIENTE': 'Cliente Fictício'} and 'FICTICIO-0000' not in cena['caffmob_promob'],
          "guarda o cliente e nunca a licença")
    check(dados['relatorio']['caixas'] == 5 and dados['relatorio']['aberturas'] == 2, "relatório da importação")
    porta = next(o for o in cena.objects if o.get('caffmob_tipo') == 'abertura'
                 and json.loads(o['caffmob_abertura'])['tipo'] == 'DOOR')
    check(porta.children and not any(c.hide_viewport for c in porta.children) and 'Folha' not in bpy.data.objects,
          "porta de madeira: fica a folha do MOBI")
    return caminho


def painel_da_porta():
    folha = next(o for o in bpy.context.scene.objects if o.get('caffmob_tipo') == 'abertura'
                 and json.loads(o['caffmob_abertura'])['tipo'] == 'DOOR')
    for o in bpy.context.selected_objects:
        o.select_set(False)
    folha.select_set(True)
    bpy.context.view_layer.objects.active = folha
    component_select.forget()
    bpy.context.view_layer.update()
    component_select.normalize(bpy.context, bpy.context.scene)
    alvo = snapshot.ensure(bpy.context)
    check(alvo is not None and alvo.kind == r.OPENING and alvo.library == 'MOBI' and alvo.detail == 'DOOR'
          and alvo.owner_name.endswith('· trecho 1'), "a porta importada aparece no painel da 067",
          str(alvo and (alvo.kind, alvo.library, alvo.owner_name)))


def remontar_preserva_o_complemento():
    antes = len(colecao().all_objects)
    parede = next(o for o in bpy.context.scene.objects if o.get('caffmob_tipo') == 'parede')
    for o in bpy.context.selected_objects:
        o.select_set(False)
    parede.select_set(True)
    bpy.context.view_layer.objects.active = parede
    component_select.forget()
    snapshot.ensure(bpy.context)
    bpy.context.window_manager.btm_mobi.parede_altura = '2800'
    mobi_fields._tick()
    d = json.loads(bpy.context.scene['caffmob_ambiente'])
    check({s['pe_direito_inicial'] for s in d['paredes'][0]['segmentos']} == {2800}, "editar a altura da parede grava")
    check(len(colecao().all_objects) == antes, "a remontagem preserva os móveis importados")
    madeira = next(m for m in bpy.data.materials if m.get('btm_promob_material') == 'madeira')
    check(any(n.type == 'TEX_IMAGE' and n.image for n in madeira.node_tree.nodes), "e as texturas")


def salvar_e_reabrir():
    destino = os.path.join(PASTA, 'Cozinha teste.blend')
    bpy.ops.file.pack_all()
    bpy.ops.wm.save_as_mainfile(filepath=destino, check_existing=False)
    n = len(colecao().all_objects)
    bpy.ops.wm.read_homefile(use_empty=True)
    bpy.ops.wm.open_mainfile(filepath=destino)
    check(len(colecao().all_objects) == n and 'caffmob_ambiente' in bpy.context.scene and complemento.lido(bpy.context),
          "o .blend reabre com o ambiente, o complemento e a origem")
    imagens = [i for i in bpy.data.images if i.source == 'FILE']
    check(imagens and all(i.packed_file is not None for i in imagens), "com as texturas embutidas")


def arquivo_invalido():
    n = len(bpy.data.objects)
    mapa = {k: v for k, v in ps.entradas().items() if not k.endswith('.ambient3d')}
    erro, caminho = importar(ps.zip_de(mapa), 'sem ambiente.promob')
    check(erro == 'O arquivo não tem ambiente 3D.' and len(bpy.data.objects) == n,
          "sem ambiente: a mensagem e nenhum objeto criado", str(erro))
    try:
        bpy.ops.caffmob.promob_importar(filepath=caminho)
        motivo = ''
    except RuntimeError as exc:
        motivo = str(exc)
    check('não tem ambiente 3D' in motivo, "o operador recusa com a mesma mensagem", motivo)


def desempenho():
    inicio = time.perf_counter()
    erro, _ = importar(ps.promob_grande(300), 'grande.promob')
    duracao = time.perf_counter() - inicio
    print(f"INFO importação de 300 módulos: {duracao:.1f} s", flush=True)
    check(erro is None and duracao <= 10, "300 módulos importam em até 10 s", f"{duracao:.1f} s")


def corpos():
    torneira = ps._item('MODULO', 'Torneira_20', base=(0, 0, 900), dim=(32, 100, 90), rot=0, material='dec_met_lis_cro')
    vidro = ps._item('MODULO', 'pv', base=(2000, 1000, 0), dim=(879, 2025, 76), rot=0, nome='Porta em vidro', extra=(
        '<COMPONENTDEFINITIONCOLLECTION><COMPONENTDEFINITION NAME="P" ID="P" IDMATERIAL="jacaranda" />'
        '<COMPONENTDEFINITION NAME="V" ID="V" IDMATERIAL="vidro_fume" /></COMPONENTDEFINITIONCOLLECTION>'))
    folha = ps._item('MODULO', 'OCL_PORT_01', base=(1002, 4998, 1), dim=(796, 1998, 15), rot=0, nome='Folha de vidro',
                     material='vidro_fume')
    porta = ps._item('MODULO', 'Porta_29', base=(1000, 5000, 0), dim=(800, 2000, 150), rot=0, nome='Porta de Vidro',
                     camada='Decore-Aberturas', material='cin_cor_000', filhos=[folha])
    parede = ps._parede([(0, 5000, 150), (3000, 5000, 150)], 2700, hospedados=[porta], id_='PAREDE2')
    erro, _ = importar(ps.promob([torneira, vidro, parede]), 'corpos.promob')
    t = obj('Torneira_20')
    check(erro is None and t.type == 'MESH' and len(t.data.polygons) > 6
          and tuple(round(v, 3) for v in t.dimensions) <= (0.032, 0.09, 0.1), "a torneira é silhueta, não caixa",
          str(t.dimensions))
    metal = t.data.materials[0].node_tree.nodes['Principled BSDF'].inputs['Metallic'].default_value
    painel = obj('Porta em vidro · vidro')
    m = painel.data.materials[0]
    check(metal == 1.0 and m.diffuse_color[3] < 1.0 and m.node_tree.nodes['Principled BSDF'].inputs['Alpha']
          .default_value < 1.0, "metal metálico e vidro transparente")

    def folhas_genericas():
        cena = bpy.context.scene
        vao = next(o for o in cena.objects if o.get('caffmob_tipo') == 'abertura'
                   and o.get('caffmob_id') == obj('Porta de Vidro').get('btm_promob_abertura'))
        return vao.children
    check(obj('Folha de vidro').type == 'MESH' and folhas_genericas()
          and all(c.hide_viewport for c in folhas_genericas()), "porta de vidro: a folha do Promob entra e a do MOBI sai")
    from caffmob_draw.mobi.cena_v2 import construir_cena
    construir_cena(bpy.context, json.loads(bpy.context.scene['caffmob_ambiente']))
    check(folhas_genericas() and all(c.hide_viewport for c in folhas_genericas()),
          "e segue assim depois de remontar o ambiente")


def texturas_de_marca():
    lateral = ps._item('MODULO', 'lat', base=(0, 0, 0), dim=(15, 720, 550), rot=0, nome='Lateral 15mm', extra=(
        '<COMPONENTDEFINITIONCOLLECTION><COMPONENTDEFINITION NAME="CORPO_EXTERNO" ID="CORPO_EXTERNO" '
        'IDMATERIAL="cin_cor_000" /></COMPONENTDEFINITIONCOLLECTION>'))
    porta = ps._item('MODULO', 'por', base=(15, -18, 0), dim=(570, 700, 18), rot=0, nome='Porta Reta',
                     material='Dur_Cri_titanio_v')
    balcao = ps._item('MODULO', 'bal', base=(0, 0, 0), dim=(600, 720, 550), rot=0, nome='Balcão', filhos=[lateral, porta],
                      extra='<MODELS><MODEL IDMODEL="m" IDMODELTYPE="t"><MODEL IDMODEL="coz_ass_duratex_ext" '
                            'IDMODELTYPE="coz_dur_des_nogueira_caiena_h" /></MODEL></MODELS>')
    erro, _ = importar(ps.promob([balcao]), 'marcas.promob')
    lat, por = obj('Lateral 15mm'), obj('Porta Reta')
    imagens = [n.image for n in lat.data.materials[0].node_tree.nodes if n.type == 'TEX_IMAGE']
    check(erro is None and imagens and imagens[0] is not None
          and lat.data.materials[0].get('btm_texture_id') == 'duratex/design/nogueira-caiena-design',
          "a cor do modelo vira a chapa Nogueira Caiena da Duratex, com imagem", str(lat.data.materials[0].name))
    check(por.data.materials[0].get('btm_texture_id') == 'duratex/cristallo/titanio-cristallo',
          "o material Dur_Cri_titanio_v vira o Titanio Cristallo")
    check((lat.btm_part.grain, por.btm_part.grain) == ('H', 'V') and 'btm_grain_rot' in por,
          "o veio do Promob fica na peça e gira a imagem", str((lat.btm_part.grain, por.btm_part.grain)))
    check((lat.get('btm_component'), por.get('btm_component')) == ('LAT', 'POR')
          and json.loads(lat['btm_promob_componentes']) == [['CORPO_EXTERNO', 'coz_dur_des_nogueira_caiena_h']],
          "os componentes do Promob ficam na peça")


def corte_aberturas_e_cameras():
    from caffmob_draw.aggregates import leaf
    from caffmob_draw.promob import cameras
    def abre(tipo, **a):
        return '<OPENSERVICE TYPE="{}" {} />'.format(tipo, ' '.join(f'{k}="{v}"' for k, v in a.items()))
    porta = ps._item('MODULO', 'porta', base=(0, 0, 0), dim=(400, 700, 18), rot=0, nome='Porta Reta',
                     camada='PORTAS', material='Dur_Cri_titanio_v', extra=abre('Door', MAX='110', X='@($I$?-$WIDTH$:$WIDTH$)',
                                                              Y='-$DEPTH$', CURRENTVALUE='0'))
    caixa = ps._item('MODULO', 'gav', base=(1400, 0, 0), dim=(400, 150, 450), rot=0, nome='Gaveta Externa',
                     extra=abre('Drawer', MAX='400', CURRENTVALUE='100'), filhos=[
                         ps._item('MODULO', 'lg', base=(1400, 0, 0), dim=(15, 120, 400), rot=0,
                                  nome='Lateral de Gaveta 400', material='mas_carvalho_mel_h')])
    frente = ps._item('MODULO', 'fg', base=(1400, 18, 0), dim=(400, 160, 18), rot=0, nome='Frente Gaveta',
                      material='mas_carvalho_mel_h', extra=abre('Drawer', MAX='400', CURRENTVALUE='100'))
    lateral = ps._item('MODULO', 'lat', base=(-15, 0, 0), dim=(15, 700, 550), rot=0, nome='Lateral 15mm',
                       material='Dur_Cri_titanio_v')
    balcao = ps._item('MODULO', 'bal', base=(-15, 0, 0), dim=(1815, 700, 550), rot=0, nome='Balcão',
                      filhos=[porta, caixa, frente, lateral])
    vistas = ('<VIEWPOINTCOLLECTION><VIEWPOINT ID="CAM 0001" NAME="CAM 0001" ZNEAR="50" ZFAR="50000" PERSPECTIVA="Y">'
              '<FOV>51.9</FOV><PTTARGET X="400" Y="300" Z="400" /><PTOBSERVER X="400" Y="-3000" Z="1600" />'
              '</VIEWPOINT></VIEWPOINTCOLLECTION><VIEWPOINT ID="V" NAME="V" ZNEAR="1" ZFAR="50000" PERSPECTIVA="Y">'
              '<FOV>51.9</FOV><PTTARGET X="1552" Y="3270" Z="-328" /><PTOBSERVER X="2042" Y="5251" Z="565.5" />'
              '</VIEWPOINT><LAYERSTATUSMANAGER><LAYERSTATUSCOLLECTION><LAYERSTATUS LAYER="PORTAS_Visual" ON="N" />'
              '</LAYERSTATUSCOLLECTION></LAYERSTATUSMANAGER>')
    principal = ps.ambiente_principal([balcao]).replace('<AMBIENT3D NAME="Cozinha teste">',
                                                        '<AMBIENT3D NAME="Cozinha teste">' + vistas)
    erro, _ = importar(ps.zip_de(ps.entradas(principal=principal)), 'aberturas.promob')
    p, g, f = obj('Porta Reta'), obj('Gaveta Externa'), obj('Frente Gaveta')
    check(erro is None and mechanisms.of(p).kind == mechanisms.HINGE and p.btm_aggregate.hinge == 'RIGHT'
          and abs(p.btm_aggregate.max_angle - 110) < 1e-6, "a porta do Promob abre pela dobradiça da direita, até 110°",
          str(p.btm_aggregate.hinge))
    check(mechanisms.of(g).kind == mechanisms.DRAWER and abs(leaf.current_fraction(g) - 0.25) < 1e-6
          and f.parent == g, "a gaveta entra aberta como no projeto (100 de 400 mm), com a frente junto")
    antes = f.matrix_world.translation.copy()
    mechanisms.of(g).set_fraction(1.0)
    bpy.context.view_layer.update()
    andou = (f.matrix_world.translation - antes)
    check(abs(andou.y + 0.3) < 1e-3 and abs(andou.x) < 1e-6, "abrir a gaveta leva a frente 300 mm para fora",
          str(tuple(andou)))
    camada = p.users_collection[0]
    check(camada.name == 'Camada · PORTAS' and camada.hide_viewport and not g.users_collection[0].hide_viewport,
          "a camada desligada no Promob entra oculta, numa coleção que o olho liga", camada.name)
    camada.hide_viewport = False                  # ligar a camada, como no Promob, antes de abrir a porta
    bpy.context.view_layer.update()
    q0 = p.matrix_world.to_quaternion()
    mechanisms.of(p).set_fraction(1.0)
    bpy.context.view_layer.update()
    giro = math.degrees(q0.rotation_difference(p.matrix_world.to_quaternion()).angle)
    check(abs(giro - 110) < 0.5, "abrir a porta gira 110°", f"{giro:.1f}")
    mechanisms.of(p).set_fraction(0.0)
    partes, _ = part_extractor.extract_production_parts(bpy.context)
    promob = sorted((p.name, p.component, p.grain_direction) for p in partes if p.source == 'PROMOB'
                    and p.module_ref == 'Balcão')
    check(promob == [('Frente Gaveta', 'FRENTE_GAVETA', 'VERTICAL'), ('Lateral 15mm', 'LAT', 'VERTICAL'),
                     ('Lateral de Gaveta 400', 'LATERAL_GAVETA', 'VERTICAL'), ('Porta Reta', 'POR', 'VERTICAL')],
          "as chapas do Promob estão no plano de corte, com papel e veio", str(promob))
    payload = json_exporter.build_global_payload({}, {}, partes)
    check(json_exporter.validate_global_json(payload) == [], "o JSON do plano de corte valida com as chapas do Promob",
          str(json_exporter.validate_global_json(payload)[:3]))
    cams = cameras.todas(bpy.context.scene)
    alvo = cameras.alvo_de(bpy.context.scene.camera)
    check([c.name for c in cams] == ['CAM 0001', 'Vista dinâmica'] and bpy.context.scene.camera.name == 'Vista dinâmica'
          and abs(alvo.location.z + 0.328) < 1e-6 and abs(cams[0].data.clip_start - 0.05) < 1e-6,
          "as câmeras do Promob entram, e a vista dinâmica é a ativa", str([c.name for c in cams]))
    estado = bpy.context.window_manager.btm_cameras
    estado.indice = 0
    estado.altura_do_alvo = 1.0
    check(abs(cameras.alvo_de(cams[0]).location.z - 1.0) < 1e-6 and bpy.context.scene.camera == cams[0],
          "escolher na lista olha pela câmera, e a altura do alvo reaponta")
    bpy.ops.caffmob.camera_nova()
    n = len(cameras.todas(bpy.context.scene))
    bpy.ops.caffmob.camera_remover()
    check(n == 3 and len(cameras.todas(bpy.context.scene)) == 2, "nova câmera da vista e remover")


def furos():
    from caffmob_draw.mobi.cena_v2 import construir_cena
    marco = ps._item('MODULO', 'marco', base=(1000, 5150, 0), dim=(810, 2403, 150), rot=0,
                     nome='Marco Interno s/ Porta', camada='Decore-Aberturas', material='cin_cor_000',
                     extra='<HOLE PRICK="Y" DEPTH="150" />')
    parede = ps._parede([(0, 5000, 150), (3000, 5000, 150)], 2700, [marco], id_='PAREDE3')
    erro, _ = importar(ps.promob([parede]), 'passagem.promob')

    def folhas():
        doc = json.loads(bpy.context.scene['caffmob_ambiente'])
        aid = next(a['id'] for a in doc['aberturas'] if a['largura'] == 810)
        vao = next(o for o in bpy.context.scene.objects if o.get('caffmob_tipo') == 'abertura' and o.get('caffmob_id') == aid)
        return vao.children
    check(erro is None and folhas() and all(c.hide_viewport for c in folhas()),
          "passagem: o vão abre sem a folha genérica (E005)")
    construir_cena(bpy.context, json.loads(bpy.context.scene['caffmob_ambiente']))
    check(folhas() and all(c.hide_viewport for c in folhas()), "e segue sem folha depois de remontar")


try:
    entradas()
    ambiente()
    painel_da_porta()
    remontar_preserva_o_complemento()
    salvar_e_reabrir()
    arquivo_invalido()
    desempenho()
    corpos()
    texturas_de_marca()
    corte_aberturas_e_cameras()
    furos()
except Exception:
    traceback.print_exc()
    FAILURES.append("exceção")
print(f"blender_071_promob: {'OK' if not FAILURES else 'FALHAS: ' + ', '.join(FAILURES)}", flush=True)
sys.exit(1 if FAILURES else 0)
