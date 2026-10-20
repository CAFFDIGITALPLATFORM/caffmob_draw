"""065 T118: botão real, transporte falso, timers dirigidos e cena anterior medida."""
import copy
import importlib.util
import json
from pathlib import Path
import sys
from time import perf_counter
from unittest.mock import patch
import bpy

ROOT = Path(__file__).resolve().parents[1]
ENTREGA = ROOT.parent
SCRATCH = ENTREGA / 'scratch'
SCRATCH.mkdir(exist_ok=True)
PACKAGE = 'bl_ext.ensaio_065.caffmob_draw'
spec = importlib.util.spec_from_file_location(PACKAGE, ROOT / 'caffmob_draw/__init__.py',
                                            submodule_search_locations=[str(ROOT / 'caffmob_draw')])
addon = importlib.util.module_from_spec(spec)
sys.modules[PACKAGE] = addon
spec.loader.exec_module(addon)
from importlib import import_module
ops = import_module(PACKAGE + '.mobi.ops_ambientes')
cena = import_module(PACKAGE + '.mobi.cena_v2')
api = import_module(PACKAGE + '.mobi.api_v2')
tarefas = import_module(PACKAGE + '.mobi.tarefas')
materiais = import_module(PACKAGE + '.mobi.materiais_v2')
downloads = import_module(PACKAGE + '.texture_library.downloads')
serializar = import_module(PACKAGE + '.caffmob.v2.serializacao').serializar
addon.register()
addon.load_file_post(None)
bpy.context.preferences.view.language = 'pt_BR'
context = bpy.context
assert not bpy.app.online_access
DOC = json.loads((ROOT / 'tests/casos_ouro_v2/obra/referencia-obra.json').read_text())['entrada']
DOC['version'] = 7
V1 = json.loads((ROOT / 'tests/casos_ouro/paredes/parede-ambiente-l.json').read_text())['entrada']
CAPS = dict(versao_api=2, ambientes_v2=True, schemas=['caffmob.ambiente/v1', 'caffmob.ambiente/v2'])
RESULTADO = ENTREGA / 'blender-065-baixar-resultado.json'
resultado = dict(status='erro', blender=bpy.app.version_string, online_access=bpy.app.online_access,
                 verificacoes=[], passos=[], ticks=[])
queue, pedidos, texturas = [], [], []
baixar_texturas = materiais.baixar_pendentes


def conferir(valor, descricao):
    assert valor, descricao
    resultado['verificacoes'].append(descricao)


def snapshot():
    objects = sorted(context.scene.objects, key=lambda o: o.name)
    vertices = [tuple(v.co) for o in objects if o.type == 'MESH' for v in o.data.vertices]
    return dict(nomes=[o.name for o in objects], contagem=len(objects), vertices=len(vertices),
                soma_vertices=[sum(v[i] for v in vertices) for i in range(3)],
                objetos={o.as_pointer(): (o.name, tuple(o.location), tuple(o.scale), tuple(o.rotation_euler),
                         o.hide_viewport, o.hide_render, tuple(tuple(v.co) for v in o.data.vertices) if o.type=='MESH' else None)
                         for o in objects},
                colecoes={c.as_pointer(): (c.name, tuple(sorted(o.name for o in c.objects))) for c in bpy.data.collections},
                propriedades={k:context.scene[k] for k in context.scene.keys()},
                materiais={m.as_pointer():(m.name,tuple(m.diffuse_color)) for m in bpy.data.materials})


def contagens():
    return {k:len(getattr(bpy.data,k)) for k in cena.Montagem.TIPOS}


def register(callback, **kwargs):
    queue.append(callback)


def tick():
    callback = queue.pop(0)
    start = perf_counter()
    again = callback()
    resultado['ticks'].append((perf_counter()-start)*1000)
    if again is not None:
        queue.append(callback)


def drain():
    for _ in range(1000):
        if not queue:
            return
        tick()
    raise AssertionError('Timer não terminou')


def request(method, path, body=None, headers=None, callback=None, **kwargs):
    pedidos.append(dict(method=method, path=path, headers=headers or {}, callback=callback))
    return dict(rid=len(pedidos))


def cliente(context, job):
    # Só o transporte falso enxerga online=True; bpy permanece offline.
    return api.ClienteV2(job.request, api.ArmazenamentoCena(context.scene), api._sessao, online=lambda: True)


def baixar():
    bpy.ops.caffmob.mobi_baixar_ambiente(ambiente_id=DOC['id'], schema=DOC['schema'])
    pedido = pedidos[-1]
    conferir(pedido['method']=='GET' and pedido['path']=='/api/draw/v2/ambientes/'+DOC['id'], 'GET v2 pelo cliente da T112')
    conferir('version=2' in pedido['headers']['Accept'], 'Accept v2 e v1 presente')
    pedido['callback'](200, copy.deepcopy(DOC), {'eTaG':'"7"'})
    return next(iter(tarefas._jobs.values()))


try:
    with patch.object(api, 'cliente', side_effect=cliente), \
         patch.object(downloads, 'request', side_effect=request), \
         patch.object(downloads, 'cancel_request'), \
         patch.object(bpy.app.timers, 'register', side_effect=register), \
         patch.object(bpy.app.timers, 'is_registered', side_effect=lambda c:c in queue), \
         patch.object(bpy.app.timers, 'unregister', side_effect=lambda c:queue.remove(c)), \
         patch.object(materiais, 'baixar_pendentes', side_effect=lambda c:texturas.append((c.name, bool(c.name in context.scene.collection.children)))):
        api._sessao.update(capacidades=CAPS)
        # Lista mista e paginação preservam o schema, inclusive entre páginas.
        bpy.ops.caffmob.mobi_listar_ambientes()
        conferir(pedidos[-1]['path'].startswith('/api/draw/v2/ambientes?'), 'Lista usa v2 com capacidade')
        pedidos[-1]['callback'](200, dict(itens=[dict(id=DOC['id'], nome=DOC['nome'], version=7, schema=DOC['schema'])], proximo='50'), {})
        bpy.ops.caffmob.mobi_listar_ambientes(mais=True)
        conferir(pedidos[-1]['path'].endswith('depois=50'), 'Cursor da segunda página enviado')
        pedidos[-1]['callback'](200, dict(itens=[dict(id=V1['id'], nome=V1['nome'], version=1, schema=V1['schema'])]), {})
        conferir([i.schema for i in context.window_manager.btm_caffmob.ambientes]==[DOC['schema'], V1['schema']], 'Lista mista conserva os schemas')
        # Primeiro download: mede cada passo e o tick inteiro, não só a geometria.
        job = baixar()
        fluxo = job.preparo
        conferir(not texturas, 'Sem textura antes da montagem')
        drain()
        resultado['passos'] += fluxo.medicoes
        assert context.scene.get('caffmob_etag_v2'), context.window_manager.btm_caffmob.situacao
        conferir(context.scene['caffmob_etag_v2']=='"7"' and context.scene['caffmob_versao']==7, 'Revisão ETag guardada na cena')
        conferir(json.loads(context.scene['caffmob_base_v2'])==DOC, 'Documento-base integral guardado na cena')
        conferir(json.loads(context.scene['caffmob_ambiente'])==DOC, 'Documento ativo integral')
        conferir(texturas==[('CAFF MOB', True)], 'Texturas solicitadas depois da troca')
        conferir(not context.window_manager.btm_caffmob.ocupado and not tarefas._jobs, 'Operação termina e libera a barra')
        root = next(c for c in context.scene.collection.children if c.name=='CAFF MOB')
        conferir(len(root.all_objects)==17, 'Referência rica monta 17 objetos')
        pendentes = {m for o in root.all_objects if o.type=='MESH' for m in o.data.materials if m and m.get('caffmob_textura_pendente')}
        with patch.object(downloads, 'request', side_effect=AssertionError('HTTP offline')), \
             patch.object(downloads, 'fetch', side_effect=AssertionError('Imagem offline')):
            baixar_texturas(root)
        conferir(bool(pendentes) and all(m.get('caffmob_textura_pendente') for m in pendentes), 'Offline conserva UUIDs pendentes e cor de reserva sem HTTP')
        api.retomar_texturas(context)
        drain()
        conferir(len(texturas)==2 and texturas[-1][1], 'Reconexão agenda retomada de texturas da coleção ativa')
        # Local dentro da coleção do ambiente também deve sobreviver à substituição.
        mesh = bpy.data.meshes.new('Local Mesh')
        mesh.from_pydata([(0,0,0),(1,0,0),(0,2,0)], [], [(0,1,2)])
        local = bpy.data.objects.new('Objeto local', mesh)
        root.objects.link(local)
        local.parent = next(o for o in root.all_objects if o.get('caffmob_tipo')=='modulo')
        local.location = (1, 2, 3)
        neutral = bpy.data.materials.new('CAFFMOB chapa')
        neutral.diffuse_color = (0.1, 0.2, 0.3, 1)
        local.data.materials.append(neutral)
        context.view_layer.update()
        mundo_local = local.matrix_world.copy()
        before, counts = snapshot(), contagens()
        def resumo(snapshot):
            return {k:snapshot[k] for k in ('nomes','contagem','vertices','soma_vertices')}
        resultado['preservacao'] = {'antes':resumo(before)}
        # Cancela depois de uma parede, com outras paredes/aberturas pendentes.
        job = baixar()
        fluxo = job.preparo
        while not fluxo.medicoes or fluxo.medicoes[-1]['etapa']!='paredes':
            tick()
        conferir(any(c.name.startswith('CAFF MOB preparo') for c in bpy.data.collections), 'Preparo existe no meio das paredes')
        bpy.ops.caffmob.mobi_cancelar()
        drain()
        resultado['passos'] += fluxo.medicoes
        resultado['preservacao']['depois_cancelar_paredes'] = resumo(snapshot())
        conferir(snapshot()==before and contagens()==counts, 'Cancelar durante paredes preserva nomes, contagens, vértices, propriedades e dados')
        conferir(not any(c.name.startswith('CAFF MOB preparo') for c in bpy.data.collections), 'Cancelar apaga todo o preparo')
        # Um erro depois de criar obra parcial também recolhe tudo que foi criado.
        original = cena._obra
        def erro(*args):
            original(*args)
            raise RuntimeError('Erro forçado na obra')
        with patch.object(cena, '_obra', side_effect=erro):
            job = baixar()
            fluxo = job.preparo
            drain()
            resultado['passos'] += fluxo.medicoes
        resultado['preservacao']['depois_erro_obra'] = resumo(snapshot())
        conferir(snapshot()==before and contagens()==counts, 'Erro em obra parcial preserva cena e limpa todos os dados')
        conferir('Erro forçado' in context.window_manager.btm_caffmob.situacao, 'Erro aparece na barra')
        # Cancela em cada intervalo, inclusive depois de texturas e antes do commit.
        job = baixar()
        fluxo = job.preparo
        while fluxo.avancar():
            pass
        total = len(fluxo.medicoes)
        resultado['passos'] += fluxo.medicoes
        job.cancel()
        for limite in range(total + 1):
            job = baixar()
            fluxo = job.preparo
            for _ in range(limite):
                tick()
            bpy.ops.caffmob.mobi_cancelar()
            drain()
            resultado['passos'] += fluxo.medicoes
            conferir(snapshot()==before and contagens()==counts, 'Cancelamento no intervalo ' + str(limite) + ' conserva a cena')
        # Dados locais novos, criados entre ticks, não pertencem ao preparo.
        job = baixar()
        tick()
        entre = bpy.data.objects.new('Local criado entre ticks', None)
        context.scene.collection.objects.link(entre)
        bpy.ops.caffmob.mobi_cancelar()
        drain()
        conferir(entre.name in context.scene.objects, 'Objeto local criado entre ticks sobrevive à limpeza')
        bpy.data.objects.remove(entre, do_unlink=True)
        conferir(snapshot()==before and contagens()==counts, 'Limpeza afeta somente dados criados pelo preparo')
        # Validação ocorre antes de qualquer coleção, com caminhos na interface.
        bpy.ops.caffmob.mobi_baixar_ambiente(ambiente_id=DOC['id'], schema=DOC['schema'])
        bad = copy.deepcopy(DOC)
        bad['pavimentos'][0]['pe_direito'] = -1
        pedidos[-1]['callback'](200, bad, {'ETag':'"7"'})
        conferir('pavimentos[0].pe_direito' in context.window_manager.btm_caffmob.relatorio_v2, 'Relatório por caminho na interface')
        conferir(snapshot()==before and contagens()==counts, 'Documento inválido não toca na cena')
        # Falta de revisão não é sucesso: a base para o envio seguinte seria ambígua.
        bpy.ops.caffmob.mobi_baixar_ambiente(ambiente_id=DOC['id'], schema=DOC['schema'])
        pedidos[-1]['callback'](200, copy.deepcopy(DOC), {})
        conferir(snapshot()==before and contagens()==counts, 'ETag ausente preserva a cena')
        conferir('Revisão' in context.window_manager.btm_caffmob.situacao, 'Erro de revisão aparece na barra')
        # Uma resposta atrasada depois de Cancelar não recria o preparo.
        bpy.ops.caffmob.mobi_baixar_ambiente(ambiente_id=DOC['id'], schema=DOC['schema'])
        atrasado = pedidos[-1]['callback']
        bpy.ops.caffmob.mobi_cancelar()
        atrasado(200, copy.deepcopy(DOC), {'ETag':'"7"'})
        conferir(snapshot()==before and contagens()==counts and not queue, 'Resposta após Cancelar é ignorada')
        # Sucesso seguinte move o local para fora da coleção substituída.
        job = baixar()
        fluxo = job.preparo
        drain()
        resultado['passos'] += fluxo.medicoes
        conferir(local.name in context.scene.objects and len(local.data.vertices)==3, 'Sucesso preserva objeto local da coleção anterior')
        context.view_layer.update()
        conferir(local.parent is None and all(abs(local.matrix_world[i][j]-mundo_local[i][j])<1e-6 for i in range(4) for j in range(4)), 'Local com pai MOBI conserva transformação mundial na troca')
        # Servidor antigo: descoberta 404 permite a lista original v1.
        api._sessao.clear()
        bpy.ops.caffmob.mobi_listar_ambientes()
        conferir(pedidos[-1]['path']=='/api/draw/v2/capacidades', 'Descoberta ao listar após reabrir')
        pedidos[-1]['callback'](404, {}, {})
        conferir(pedidos[-1]['path'].startswith('/api/draw/v1/ambientes?'), '404 de capacidades usa lista v1')
        pedidos[-1]['callback'](200, dict(itens=[dict(id=V1['id'], nome=V1['nome'], version=1)]), {})
        conferir(context.window_manager.btm_caffmob.ambientes[0].schema==V1['schema'], 'Item antigo sem schema é v1')
        # Mesmo com capacidade v2, v1 continua pelo download e preparo da 063.
        api._sessao.update(capacidades=CAPS)
        with patch.object(ops, 'prepare', wraps=ops.prepare) as prepare:
            bpy.ops.caffmob.mobi_baixar_ambiente(ambiente_id=V1['id'])
            conferir(pedidos[-1]['path']=='/api/draw/v1/ambientes/'+V1['id'], 'Download v1 usa rota da 063')
            pedidos[-1]['callback'](200, V1, {})
            drain()
            conferir(prepare.call_count==1, 'Download v1 usa preparo de texturas da 063')
        conferir(json.loads(context.scene['caffmob_ambiente'])==V1, 'Ambiente v1 continua baixando')
        conferir(local.name in context.scene.objects, 'Objeto local sobrevive ao download v1')
    resultado['maior_passo_ms'] = max(p['ms'] for p in resultado['passos'])
    resultado['maior_tick_ms'] = max(resultado['ticks'])
    conferir(resultado['maior_passo_ms']<=200 and resultado['maior_tick_ms']<=200, 'Passos e ticks completos abaixo de 200 ms')
    resultado['status'] = 'ok'
finally:
    RESULTADO.write_text(json.dumps(resultado, ensure_ascii=False, indent=2)+'\n')
    print(json.dumps({k:v for k,v in resultado.items() if k not in ('passos','ticks','verificacoes','preservacao')}, ensure_ascii=False), flush=True)
