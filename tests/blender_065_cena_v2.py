"""065 T114 a T117: ensaio real no Blender 5.2, sem interface nem rede externa."""
import copy
import importlib.util
import json
import sys
from collections import Counter
from pathlib import Path
from unittest.mock import patch
from types import SimpleNamespace
import bpy

ROOT = Path(__file__).resolve().parents[1]
ENTREGA = ROOT.parent
# Como extensão; nenhum wheel/pacote é instalado por este ensaio.
PACKAGE = 'bl_ext.ensaio_065.caffmob_draw'
spec = importlib.util.spec_from_file_location(PACKAGE, ROOT / 'caffmob_draw/__init__.py',
                                            submodule_search_locations=[str(ROOT / 'caffmob_draw')])
addon = importlib.util.module_from_spec(spec)
sys.modules[PACKAGE] = addon
spec.loader.exec_module(addon)
from importlib import import_module
cena = import_module(PACKAGE + '.mobi.cena_v2')
materiais = import_module(PACKAGE + '.mobi.materiais_v2')
obra = import_module(PACKAGE + '.geometry.obra_v2')
validar = import_module(PACKAGE + '.caffmob.v2.validacao').validar_documento
serializar = import_module(PACKAGE + '.caffmob.v2.serializacao').serializar
addon.register()
addon.load_file_post(None)

PASTA = ROOT / 'tests/casos_ouro_v2'
RESULTADO = ENTREGA / 'blender-065-resultado.json'
context = bpy.context
assert not bpy.app.online_access
relatorio = dict(status='erro', blender=bpy.app.version_string, online_access=bpy.app.online_access, verificacoes=[])


def conferir(condicao, descricao):
    assert condicao, descricao
    relatorio['verificacoes'].append(descricao)


def objetos(root):
    return list(root.all_objects)


def cena_guardada():
    return dict(objetos={o.as_pointer(): (o.name, tuple(o.location), o.hide_viewport, o.hide_render,
                    tuple(v.co[:] for v in o.data.vertices) if o.type == 'MESH' else None)
                    for o in context.scene.objects},
                colecoes={c.as_pointer() for c in bpy.data.collections},
                ambiente=context.scene.get('caffmob_ambiente'), versao=context.scene.get('caffmob_versao'))


def componentes(obj):
    vizinhos = {v.index:set() for v in obj.data.vertices}
    for e in obj.data.edges:
        a,b = e.vertices
        vizinhos[a].add(b)
        vizinhos[b].add(a)
    n = 0
    while vizinhos:
        n += 1
        fila = [next(iter(vizinhos))]
        while fila:
            fila += list(vizinhos.pop(fila.pop(), ()))
    return n


def extremos(obj):
    vs = [tuple(v.co[k] * 1000 for k in range(3)) for v in obj.data.vertices]
    return dict(min=[min(p[k] for p in vs) for k in range(3)] if vs else None,
                max=[max(p[k] for p in vs) for k in range(3)] if vs else None)


def verificar_topologia(obj, area_esperada, lacos):
    m = obj.data
    faces = [p for p in m.polygons if p.normal.z > 0.9]
    edges = Counter(tuple(sorted((a, p.vertices[(i + 1) % len(p.vertices)])))
                    for p in faces for i, a in enumerate(p.vertices))
    vizinhos = {}
    for (a, b), n in edges.items():
        if n == 1:
            vizinhos.setdefault(a, set()).add(b)
            vizinhos.setdefault(b, set()).add(a)
    conferir(all(len(v) == 2 for v in vizinhos.values()), 'Tampa sem vértices em T')
    n = 0
    while vizinhos:
        n += 1
        fila = [next(iter(vizinhos))]
        while fila:
            fila += list(vizinhos.pop(fila.pop(), ()))
    conferir(n == lacos, f'Tampa com {lacos} laços de borda')
    area = sum(p.area for p in faces) * 1e6
    conferir(abs(area - area_esperada) < 2, 'Área da tampa exclui os furos')
    todos = Counter(tuple(sorted((a, p.vertices[(i + 1) % len(p.vertices)])))
                    for p in m.polygons for i, a in enumerate(p.vertices))
    conferir(set(todos.values()) == {2}, 'Sólido estanque: duas faces por aresta')
    # Gênero: V − E + F = 2 − 2h para a extrusão com h furos.
    conferir(len(m.vertices) - len(todos) + len(m.polygons) == 2 - 2 * (lacos - 1), 'Euler confirma os furos atravessando a laje')
    return dict(area_mm2=area, lacos_de_borda=n, vertices=len(m.vertices), faces=len(m.polygons))


try:
    referencia = json.loads((PASTA / 'referencia-rica.json').read_text())['entrada']
    inicial = cena.construir_cena(context, referencia)
    print('Contagem da referência:', dict(Counter(o.get('caffmob_tipo') for o in inicial.all_objects)), flush=True)
    conferir(len(inicial.all_objects) == 14, 'Referência rica original: 14 objetos, sem inventar contorno do andar')
    relatorio['objetos_referencia_original'] = 14
    doc = json.loads((PASTA / 'obra/referencia-obra.json').read_text())['entrada']
    conferir(not validar(doc), 'Referência de obra válida no contrato fechado')
    original = copy.deepcopy(doc)
    relatorio['objetos_antes'] = 3
    root = cena.construir_cena(context, doc)
    conferir(doc == original, 'Documento de entrada intacto')
    conferir(context.scene['caffmob_ambiente'] == serializar(doc), 'Documento completo guardado sem perda')
    elevacoes = obra.elevacoes_dos_pavimentos(doc)
    pisos = list(root.children)
    conferir([c['caffmob_id'] for c in pisos] == [p['id'] for p in sorted(doc['pavimentos'], key=lambda p:p['ordem'])], 'Coleções na ordem dos pavimentos')
    for p, c in zip(sorted(doc['pavimentos'], key=lambda p:p['ordem']), pisos):
        conferir(c.name == p['nome'] and c['caffmob_nome'] == p['nome'] and c['caffmob_z_mm'] == elevacoes[p['id']], 'Nome e elevação do pavimento ' + p['nome'])
        conferir(all(o['caffmob_pavimento_id'] == p['id'] for o in c.all_objects), 'Entidades na coleção de ' + p['nome'])
    relatorio['pavimentos'] = [dict(nome=c['caffmob_nome'], ordem=c['caffmob_ordem'], z_mm=c['caffmob_z_mm']) for c in pisos]
    contagens = Counter(o['caffmob_tipo'] for o in objetos(root))
    # Contagem explícita da referência rica, incluindo partes da janela e o LED.
    esperado = dict(parede=2, abertura=1, abertura_peca=3, modulo=1, peca_avulsa=1,
                    primitiva=2, item_externo=1, escada=1, piso=2, laje=1, forro=1, led=1)
    conferir(dict(contagens) == esperado, 'Contagem exata por família e peças da abertura')
    ids = {e['id'] for familia in ('pavimentos','paredes','aberturas','modulos','pecas_avulsas',
                                  'primitivas','escadas','itens_externos') for e in doc[familia]}
    ids.update(p['laje']['id'] for p in doc['pavimentos'])
    conferir(all(o.get('caffmob_id') in ids for o in objetos(root)), 'Todo objeto aponta para ID existente do contrato')
    relatorio['contagens'] = dict(contagens)
    relatorio['objetos_ambiente'] = sum(contagens.values())
    relatorio['objetos_depois'] = len(context.scene.objects)
    laje = next(o for o in objetos(root) if o.get('caffmob_tipo') == 'laje')
    relatorio['laje'] = verificar_topologia(laje, 5500000, 2)
    p = doc['pavimentos'][0]
    conferir(all(laje.data.materials[f.material_index]['caffmob_id'] == (p['piso_material_id'] if f.normal.z > 0.9 else p['laje']['material_id'])
                 for f in laje.data.polygons), 'Laje: piso no topo, material da laje embaixo e nas laterais')
    escada = next(o for o in objetos(root) if o.get('caffmob_tipo') == 'escada')
    e = doc['escadas'][0]
    conferir(escada['caffmob_degraus'] == 15 and escada['caffmob_blocos'] == 14, 'Escada L: 15 espelhos e 14 blocos')
    conferir(escada['caffmob_laje_id'] == e['laje_id'] and escada['caffmob_furo_id'] == e['furo_id'], 'IDs da laje e do furo preservados na escada')
    conferir(componentes(escada) == 14, 'Malha da escada contém 14 blocos independentes reais')
    relatorio['degraus'] = escada['caffmob_degraus']
    parede = next(o for o in objetos(root) if o.get('caffmob_id') == doc['paredes'][0]['id'])
    conferir(all(abs(o.location.z * 1000 - elevacoes[o['caffmob_pavimento_id']]) < 0.1
                 for o in objetos(root) if o.get('caffmob_tipo') in ('parede','piso','laje','forro','led')),
             'Geometria acompanha o Z do pavimento em metros')
    conferir(json.loads(parede['caffmob_parede']) == doc['paredes'][0], 'Parede guarda contrato v2 íntegro')
    interno, externo = doc['paredes'][0]['segmentos'][0]['material_interno_id'], doc['paredes'][0]['segmentos'][0]['material_externo_id']
    conferir(parede.data.materials[parede.data.polygons[2].material_index]['caffmob_id'] == externo and
             parede.data.materials[parede.data.polygons[4].material_index]['caffmob_id'] == interno, 'Parede: materiais nas faces externa e interna')
    face_i, face_e = parede.data.polygons[4], parede.data.polygons[2]
    deslocamento = face_i.center - face_e.center
    conferir(face_i.normal.dot(deslocamento) > 0 and face_e.normal.dot(deslocamento) < 0,
             'Face interna aponta para o lado deslocado pelo sentido do trecho')
    conferir(all(not o.get('btm_wall_segments') for o in objetos(root) if o.get('caffmob_tipo') == 'parede'), 'Parede v2 não é convertida para Home Builder ou walls2d')
    conferir(any(m.get('caffmob_textura_pendente') for o in objetos(root) if o.type == 'MESH' for m in o.data.materials), 'Sem rede: UUID pendente e cor de reserva')
    conferir(all(o.hide_render for o in objetos(root) if o.get('caffmob_tipo') == 'modulo'), 'Camada oculta conserva os módulos sem desenhá-los')
    led = next(o for o in objetos(root) if o.get('caffmob_tipo') == 'led')
    conferir(led.data.materials[0].node_tree.nodes.get('Principled BSDF').inputs['Emission Strength'].default_value > 0, 'LED com material emissivo')
    externo_obj = next(o for o in objetos(root) if o.get('caffmob_tipo') == 'item_externo')
    conferir(list(externo_obj['caffmob_transformacao_origem']) == doc['itens_externos'][0]['transformacao_origem'], 'Matriz de procedência preservada')
    conferir(abs(externo_obj.location.x * 1000 - e['posicao']['x']) < 0.1, 'Caixa externa não recebe a matriz de procedência duas vezes')
    antes = cena_guardada()
    quantidade_dados = {k:len(getattr(bpy.data,k)) for k in ('objects','collections','meshes','materials','images')}
    with patch.object(cena, '_obra', side_effect=RuntimeError('Erro deliberado após paredes, aberturas e móveis')):
        try:
            cena.construir_cena(context, doc)
        except RuntimeError:
            pass
        else:
            raise AssertionError('Falha injetada não foi disparada')
    conferir(cena_guardada() == antes, 'Erro no meio da montagem preserva cena e documento anteriores')
    conferir(quantidade_dados == {k:len(getattr(bpy.data,k)) for k in quantidade_dados}, 'Erro remove preparo, malhas e materiais novos')
    # Testa a atualização posterior sem abrir rede: arquivo de imagem criado localmente,
    # catálogo e fila da 062 simulados. O Blender permanece --offline-mode.
    pending = next(m for o in objetos(root) if o.type=='MESH' for m in o.data.materials if m.get('caffmob_textura_pendente'))
    image = bpy.data.images.new('Ensaio de textura', 8, 4)
    (ENTREGA / 'scratch').mkdir(exist_ok=True)
    image.filepath_raw = str(ENTREGA / 'scratch/textura-ensaio.png')
    image.file_format = 'PNG'
    image.save()
    with patch.object(materiais.catalog, 'item', return_value={'id':pending['caffmob_textura_pendente']}), \
         patch.object(materiais.downloads, 'cached', return_value=image.filepath_raw):
        materiais.baixar_pendentes(root)
    conferir(not pending['caffmob_textura_pendente'], 'Textura pendente aplicada depois pelo cache da 062')
    conferir(any(n.type=='TEX_IMAGE' and n.image for n in pending.node_tree.nodes), 'Imagem real no nó do material')
    conferir(list(pending['caffmob_escala_mm']) == [1500,750], 'Escala física conservada ao resolver textura')
    vertical = next(m for o in objetos(root) if o.type == 'MESH' for m in o.data.materials
                    if m.get('caffmob_veio') == 'VERTICAL' and json.loads(m['caffmob_material'])['tipo'] == 'textura')
    giro = next(n for n in vertical.node_tree.nodes if n.bl_idname == 'ShaderNodeVectorRotate')
    conferir(abs(giro.inputs['Angle'].default_value + __import__('math').pi) < 1e-6,
             'Veio vertical soma 90 graus à rotação do catálogo')
    # A retomada após reconexão passa pela mesma metadata/fila assíncrona da 062.
    # Só o sinal online deste módulo é simulado; não existe HTTP neste ensaio.
    pending['caffmob_textura_pendente'] = json.loads(pending['caffmob_material'])['textura_id']
    pedidos, downloads = [], []
    with patch.object(materiais, 'bpy', SimpleNamespace(app=SimpleNamespace(online_access=True), data=bpy.data)), \
         patch.object(materiais.catalog, 'item', return_value=None), \
         patch.object(materiais.catalog, 'remember', side_effect=lambda body: body), \
         patch.object(materiais.downloads, 'request', side_effect=lambda *a,**kw: pedidos.append((a,kw))), \
         patch.object(materiais.downloads, 'fetch', side_effect=lambda tid,callback,**kw: downloads.append(callback)):
        materiais.baixar_pendentes(root)
        conferir(len(pedidos) == 1 and pending['caffmob_baixando'], 'Retomada consulta metadata sem bloquear a montagem')
        pedidos[0][1]['callback'](200, {'id':pending['caffmob_textura_pendente']})
        conferir(len(downloads) == 1 and bool(pending['caffmob_textura_pendente']), 'Imagem fica na fila assíncrona da 062')
        downloads[0](image.filepath_raw, None)
        conferir(not pending['caffmob_textura_pendente'] and not pending['caffmob_baixando'], 'Callback conclui textura pendente após reconexão')
    # Extremos locais medidos nas malhas Blender, contra Three.Float32 do oráculo.
    maior = 0
    for arquivo in sorted((PASTA / 'obra').glob('parede-*.json')):
        c = json.loads(arquivo.read_text())
        root = cena.construir_cena(context, c['entrada'])
        for esperado in c['esperado']:
            obj = next(o for o in objetos(root) if o.get('caffmob_id') == esperado['id'])
            obtido = extremos(obj)
            for k in ('min','max'):
                if esperado[k] is None:
                    conferir(obtido[k] is None, 'Trecho oculto sem malha')
                else:
                    maior = max(maior, *(abs(a-b) for a,b in zip(obtido[k],esperado[k])))
    conferir(maior <= 0.1, 'Extremos de 17 casos de parede dentro de 0,1 mm')
    relatorio['maior_diferenca_mm'] = maior
    # Constrói as demais escadas e sancas de cada tipo no Blender, com os mesmos IDs.
    for tipo in ('reta','L','U'):
        d = copy.deepcopy(doc)
        d['escadas'][0]['tipo'] = tipo
        root = cena.construir_cena(context, d)
        obj = next(o for o in objetos(root) if o.get('caffmob_tipo')=='escada')
        conferir(componentes(obj) == len(obra.calcular_escada(d['escadas'][0])['blocos']), 'Blocos na malha da escada ' + tipo)
        conferir(obj['caffmob_degraus']==obra.calcular_escada(d['escadas'][0])['degraus'], 'Escada real do tipo ' + tipo)
    for tipo in ('fechada','aberta','invertida'):
        d = copy.deepcopy(doc)
        d['pavimentos'][1]['forro']['sanca']['tipo'] = tipo
        root = cena.construir_cena(context, d)
        conferir(any(o.get('caffmob_tipo')=='forro' and len(o.data.vertices)>0 for o in objetos(root)), 'Sanca real do tipo ' + tipo)
    d = copy.deepcopy(doc)
    d['camadas'] = [dict(id='06500000-0000-4000-8000-000000000080', nome='Frentes',
                        categoria='portas_cozinha', pavimento_id=d['pavimentos'][0]['id'], visivel=False)]
    d['modulos'][0]['camada_id'] = None
    root = cena.construir_cena(context, d)
    modulo = next(o for o in objetos(root) if o.get('caffmob_tipo') == 'modulo')
    frentes = next(o for o in objetos(root) if o.get('caffmob_tipo') == 'modulo_frentes')
    conferir(not modulo.hide_render and frentes.hide_render and frentes.parent == modulo,
             'Categoria de portas oculta só frentes e conserva a caixa do módulo')
    # Laje côncava com um círculo e um retângulo: também é estanque em Float32.
    c = json.loads((PASTA / 'obra/laje-concava.json').read_text())
    d = copy.deepcopy(doc)
    d['escadas'] = []
    d['pavimentos'][0]['laje']['contorno'] = c['entrada']['contorno']
    for j,r in enumerate(c['entrada']['recortes']):
        r['id'] = f'06500000-0000-4000-8000-{j+1:012d}'
    d['pavimentos'][0]['laje']['recortes'] = c['entrada']['recortes']
    root = cena.construir_cena(context, d)
    obj = next(o for o in objetos(root) if o.get('caffmob_tipo')=='laje')
    relatorio['laje_concava'] = verificar_topologia(obj, c['area_mm2'], 3)
    # Volta à referência rica e confirma substituição sem duplicar coleção/objetos.
    root = cena.construir_cena(context, doc)
    conferir(Counter(o['caffmob_tipo'] for o in objetos(root))==contagens, 'Reimportação sem duplicar objetos')
    conferir(len([c for c in context.scene.collection.children if c.name==cena.NOME_DA_COLECAO])==1, 'Uma coleção ativa ao concluir')
    relatorio['status'] = 'ok'
finally:
    RESULTADO.write_text(json.dumps(relatorio, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps(relatorio, ensure_ascii=False), flush=True)
