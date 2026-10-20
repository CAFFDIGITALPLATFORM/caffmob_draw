"""065 T119/T120: operadores reais, transporte falso, Blender offline."""
import copy
import importlib.util
import json
import math
from pathlib import Path
import sys
from unittest.mock import patch
import bpy
from mathutils import Vector
from importlib import import_module

ROOT = Path(__file__).resolve().parents[1]
ENTREGA = ROOT.parent
SCRATCH = ENTREGA / 'scratch/rodada-18'
SCRATCH.mkdir(parents=True, exist_ok=True)
PACKAGE = 'bl_ext.ensaio_065.caffmob_draw'
spec = importlib.util.spec_from_file_location(PACKAGE, ROOT / 'caffmob_draw/__init__.py',
                                            submodule_search_locations=[str(ROOT / 'caffmob_draw')])
addon = importlib.util.module_from_spec(spec)
sys.modules[PACKAGE] = addon
spec.loader.exec_module(addon)
ops = import_module(PACKAGE + '.mobi.ops_ambientes')
cena = import_module(PACKAGE + '.mobi.cena_v2')
envio = import_module(PACKAGE + '.mobi.enviar_v2')
api = import_module(PACKAGE + '.mobi.api_v2')
tarefas = import_module(PACKAGE + '.mobi.tarefas')
materiais = import_module(PACKAGE + '.mobi.materiais_v2')
downloads = import_module(PACKAGE + '.texture_library.downloads')
validar = import_module(PACKAGE + '.caffmob.v2.validacao').validar_documento
serializar = import_module(PACKAGE + '.caffmob.v2.serializacao').serializar
addon.register()
addon.load_file_post(None)
bpy.context.preferences.view.language = 'pt_BR'
context = bpy.context
DOC = json.loads((ROOT / 'tests/casos_ouro_v2/obra/referencia-obra.json').read_text())['entrada']
DOC['version'] = 7
V1 = json.loads((ROOT / 'tests/casos_ouro/paredes/parede-ambiente-l.json').read_text())['entrada']
CAPS = dict(versao_api=2, ambientes_v2=True, schemas=['caffmob.ambiente/v1', 'caffmob.ambiente/v2'])
resultado = dict(status='erro', blender=bpy.app.version_string, online_access=bpy.app.online_access, verificacoes=[])
pedidos, queue = [], []


def conferir(valor, texto):
    assert valor, texto
    resultado['verificacoes'].append(texto)


def request(method, path, body=None, headers=None, callback=None, **kwargs):
    pedidos.append(dict(method=method, path=path, body=copy.deepcopy(body), headers=copy.deepcopy(headers or {}), callback=callback))
    return dict(rid=len(pedidos))


def cliente(context, job):
    return api.ClienteV2(job.request, api.ArmazenamentoCena(context.scene), api._sessao, online=lambda:True)


def drain():
    for _ in range(1000):
        if not queue: return
        cb = queue.pop(0)
        if cb() is not None: queue.append(cb)
    raise AssertionError('Timer não terminou')


def responder(status, corpo, headers=None):
    pedidos[-1]['callback'](status, copy.deepcopy(corpo), headers or {})
    drain()


def baixar(doc=DOC):
    bpy.ops.caffmob.mobi_baixar_ambiente(ambiente_id=doc['id'], schema=doc['schema'])
    responder(200, doc, {'ETag':'"{}"'.format(doc['version'])})


def enviar():
    bpy.ops.caffmob.mobi_enviar_ambiente()
    return pedidos[-1]


def sucesso(version, status=200, replay=False):
    pedido = pedidos[-1]
    responder(status, dict(id=pedido['body']['id'], version=version, atualizado_em='2026-10-20T12:00:00.000Z'),
              {'ETag':'"{}"'.format(version), 'Idempotency-Replayed':str(replay).lower()})


def cubo(nome, location, scale, parent=None):
    bpy.ops.mesh.primitive_cube_add(size=1)
    obj = context.object
    obj.name = nome
    obj.parent = parent
    obj.location, obj.scale = location, scale
    return obj


def extremos(objetos):
    context.view_layer.update()
    pontos = [o.matrix_world @ v.co for o in objetos for v in o.data.vertices]
    minimo = [min(v[i] for v in pontos)*1000 for i in range(3)]
    maximo = [max(v[i] for v in pontos)*1000 for i in range(3)]
    return minimo, [b-a for a,b in zip(minimo,maximo)]


def caminhos_diferentes(a,b,caminho=''):
    if isinstance(a,dict) and isinstance(b,dict):
        return [p for k in a.keys()|b.keys() for p in
                ([caminho+'.'+k] if k not in a or k not in b else caminhos_diferentes(a[k],b[k],caminho+'.'+k))]
    if isinstance(a,list) and isinstance(b,list) and len(a)==len(b):
        return [p for i,(x,y) in enumerate(zip(a,b)) for p in caminhos_diferentes(x,y,caminho+'['+str(i)+']')]
    return [] if a==b else [caminho]


try:
    with patch.object(api,'cliente',side_effect=cliente), \
         patch.object(downloads,'request',side_effect=request), \
         patch.object(downloads,'cancel_request'), \
         patch.object(bpy.app.timers,'register',side_effect=lambda cb,**kw:queue.append(cb)), \
         patch.object(bpy.app.timers,'is_registered',side_effect=lambda cb:cb in queue), \
         patch.object(bpy.app.timers,'unregister',side_effect=lambda cb:queue.remove(cb)), \
         patch.object(materiais,'baixar_pendentes'):
        conferir(not bpy.app.online_access,'Blender permanece offline; somente transporte falso')
        for obj in list(context.scene.objects): bpy.data.objects.remove(obj,do_unlink=True)
        api._sessao.update(capacidades=CAPS)
        baixar()
        conferir(json.loads(context.scene['caffmob_base_v2'])==DOC,'Download real guarda referência rica integral')
        sem_edicao,avisos=envio.documento_da_cena(context)
        conferir(sem_edicao==DOC and not avisos,'Cena intacta devolve todos os campos sem ruído float32')
        estados = {o.name:o.get(envio.ESTADO) for o in context.scene.objects}
        for obj in context.scene.objects:
            if obj.get(envio.ESTADO): del obj[envio.ESTADO]
        sem_edicao,avisos=envio.documento_da_cena(context)
        conferir(sem_edicao==DOC and not avisos,'Cena anterior da T118 sem snapshots continua reconhecida pelo contrato e ID')
        for obj in context.scene.objects:
            if estados[obj.name]: obj[envio.ESTADO]=estados[obj.name]
        modulo=next(o for o in context.scene.objects if o.get('caffmob_tipo')=='modulo')
        parede=next(o for o in context.scene.objects if o.get('caffmob_tipo')=='parede')
        original_x=modulo.location.x
        modulo.location.x+=0.123456
        dado=json.loads(parede['caffmob_parede'])
        dado['segmentos'][0]['espessura']=175
        parede['caffmob_parede']=serializar(dado)
        local=cubo('Cubo local',(4.12,-1.83,0.719),(0.333,0.744,1.283))
        local.rotation_euler=(0.21,0.43,0.67)
        pai=bpy.data.objects.new('Pai local',None)
        context.scene.collection.objects.link(pai)
        pai.location=(1.23,2.34,0.67)
        pai.rotation_euler=(0.12,-0.34,0.56)
        pai.scale=(1.2,0.9,1.3)
        filho1=cubo('Filho local 1',(-0.4,0.2,0.5),(0.2,0.3,0.4),pai)
        filho2=cubo('Filho local 2',(0.8,-0.6,1.2),(0.4,0.5,0.6),pai)
        filho2.rotation_euler=(0.7,0.3,0.4)
        esperados={local.name:extremos([local]),pai.name:extremos([filho1,filho2])}
        p=enviar()
        conferir(p['method']=='PUT' and p['headers']['If-Match']=='"7"','Cena baixada envia PUT v2 com If-Match guardado')
        conferir('/api/draw/v2/' in p['path'] and bool(p['headers']['Idempotency-Key']),'Escrita usa rota v2 e chave durável')
        documento=p['body']
        conferir(validar(documento)==[],'Documento enviado passa pela validação v2')
        conferir(len(documento['itens_externos'])==len(DOC['itens_externos'])+2,'Cubo e pai com dois filhos geram só dois itens externos')
        erros=[]
        for item in documento['itens_externos'][-2:]:
            minimo,tamanho=esperados[item['nome']]
            erros += [abs(item['posicao'][k]-v) for k,v in zip('xyz',minimo)]
            erros += [abs(item['dimensoes'][k]-v) for k,v in zip(('largura','profundidade','altura'),tamanho)]
        resultado['erro_maximo_mm']=max(erros)
        conferir(max(erros)<=0.1,'Caixas mundiais respeitam 0,1 mm, incluindo rotação, escala e parentesco')
        comparavel=copy.deepcopy(documento)
        comparavel['itens_externos']=comparavel['itens_externos'][:-2]
        diferencas=caminhos_diferentes(DOC,comparavel)
        resultado['campos_alterados']=diferencas
        conferir(set(diferencas)=={'.modulos[0].posicao.x','.paredes[0].segmentos[0].espessura'},'Comparação campo a campo: só posição X do módulo e espessura da parede mudaram')
        chave=p['headers']['Idempotency-Key']
        sucesso(8)
        conferir(context.scene['caffmob_etag_v2']=='"8"' and context.scene['caffmob_versao']==8,'Sucesso atualiza ETag e versão')
        conferir(not context.scene.get(api.PROPRIEDADE),'Sucesso confirmado remove operação pendente')
        atual,avisos=envio.documento_da_cena(context)
        conferir(atual==json.loads(context.scene['caffmob_base_v2']),'Montagem após sucesso não repete deslocamento nem duplica externos')
        modulo.location.x=original_x
        p=enviar()
        conferir(abs(p['body']['modulos'][0]['posicao']['x']-DOC['modulos'][0]['posicao']['x'])<0.001,'Voltar à posição original depois de enviar produz nova edição')
        conferir(p['headers']['Idempotency-Key']!=chave,'Nova intenção recebe chave nova')
        sucesso(9)
        # Parâmetros legados no recipiente v2 são editáveis sem substituir o restante.
        legado=json.loads(modulo['caffmob_modulo'])
        legado['construcao']['prateleiras']['quantidade']=3
        modulo['caffmob_modulo']=serializar(legado)
        modulo.scale=(1.1,1.2,1.3)
        p=enviar()
        conferir(p['body']['modulos'][0]['parametros']['construcao']['prateleiras']['quantidade']==3,'Parâmetro editado do addon chega ao recipiente v2')
        conferir(abs(p['body']['modulos'][0]['parametros']['largura']-880)<0.001,'Escala do módulo altera dimensão editável em mm')
        conferir(p['body']['modulos'][0]['parametros']['chapas_editadas']==DOC['modulos'][0]['parametros']['chapas_editadas'],'Chapas, textura e veio são preservados ao editar módulo')
        sucesso(10)
        # Erro local bloqueia o transporte e mostra o caminho.
        errado=copy.deepcopy(dado)
        errado['segmentos'][0]['espessura']=-1
        parede['caffmob_parede']=serializar(errado)
        antes=len(pedidos)
        enviar()
        conferir(len(pedidos)==antes and 'paredes[0].segmentos[0].espessura' in context.window_manager.btm_caffmob.relatorio_v2,'Inválido mostra caminho e não envia')
        parede['caffmob_parede']=serializar(dado)
        # Perfil não reconhecido e objeto sem malha geram relatório sem redução.
        camera=bpy.data.objects.new('Sem malha',bpy.data.cameras.new('Sem malha'))
        context.scene.collection.objects.link(camera)
        universal=json.loads(modulo['caffmob_entidade_v2'])
        universal['perfil_construcao']='outro/2'
        modulo['caffmob_entidade_v2']=serializar(universal)
        montado,avisos=envio.documento_da_cena(context)
        conferir({a['codigo'] for a in avisos}=={'PRESERVADO','SEM_MALHA'},'Relatório cobre objeto sem malha e perfil desconhecido preservado')
        universal['perfil_construcao']='caffmob.modulo/v1'
        modulo['caffmob_entidade_v2']=serializar(universal)
        bpy.data.objects.remove(camera,do_unlink=True)
        # Três escolhas reais do operador, cada uma em um conflito próprio.
        enum=bpy.ops.caffmob.mobi_resolver_conflito_v2.get_rna_type().properties['escolha'].enum_items
        conferir([i.identifier for i in enum]==['remota','local','copia'],'Operador oferece exatamente as três escolhas do 409')
        for escolha in ('local','copia','remota'):
            p=enviar()
            antiga=p['headers']['Idempotency-Key']
            remota=copy.deepcopy(p['body'])
            revisao=int(context.scene['caffmob_etag_v2'].strip('"'))+1
            remota.update(version=revisao,nome='Revisão remota')
            responder(409,dict(erro='VERSAO_DIVERGENTE',versao_atual=revisao,documento_atual=remota))
            conflito=json.loads(context.scene['caffmob_conflito_v2'])
            conferir(conflito['local']==p['body'] and conflito['remota']==remota,'409 guarda as duas versões para '+escolha)
            bpy.ops.caffmob.mobi_resolver_conflito_v2(escolha=escolha)
            drain()
            if escolha=='remota':
                conferir(json.loads(context.scene['caffmob_base_v2'])==remota,'Carregar remota troca cena/base sem escrever no Studio')
                conferir(not context.scene.get(api.PROPRIEDADE) and not context.scene.get('caffmob_conflito_v2'),'Escolha remota limpa pendência só depois de concluir a montagem')
            else:
                novo=pedidos[-1]
                conferir(novo['headers']['Idempotency-Key']!=antiga,'Escolha '+escolha+' usa chave nova')
                if escolha=='local':
                    conferir(novo['method']=='PUT' and novo['headers']['If-Match']=='"{}"'.format(revisao),'Enviar local usa revisão atual')
                    sucesso(revisao+1)
                else:
                    conferir(novo['method']=='POST' and novo['body']['id']!=p['body']['id'],'Cópia recebe POST e UUID novo')
                    sucesso(1,201)
        # Perda de resposta: pedido sobrevive ao .blend e congela o conteúdo.
        p=enviar()
        responder(None,dict(erro='REDE'))
        pendente=context.scene[api.PROPRIEDADE]
        arquivo=SCRATCH/'operacao-pendente.blend'
        bpy.ops.wm.save_as_mainfile(filepath=str(arquivo))
        bpy.ops.wm.open_mainfile(filepath=str(arquivo))
        conferir(context.scene.get(api.PROPRIEDADE)==pendente,'Operação durável sobrevive a salvar e reabrir .blend real')
        modulo=next(o for o in context.scene.objects if o.get('caffmob_tipo')=='modulo')
        modulo.location.y+=0.15
        r=enviar()
        conferir((r['method'],r['path'],r['body'],r['headers'])==(p['method'],p['path'],p['body'],p['headers']),'Reenvio após resposta perdida conserva chave, corpo e If-Match apesar de edição posterior')
        recibo=int(r['headers']['If-Match'].strip('"'))+1
        sucesso(recibo,replay=True)
        conferir(pedidos[-1]['method']=='GET','Recibo repetido consulta revisão atual sem PUT automático')
        atual=copy.deepcopy(r['body'])
        atual['version']=recibo+3
        responder(200,atual,{'ETag':'"{}"'.format(atual['version'])})
        conferir(context.scene['caffmob_versao']==recibo and not context.scene.get(api.PROPRIEDADE),'Replay confirma só a revisão do recibo e não sobrescreve revisão atual')
        conferir('outra revisão' in context.window_manager.btm_caffmob.situacao,'Replay mais antigo informa que Studio já avançou')
        # A 063 continua usando seu caminho mesmo com base v2 antiga e capacidades v2.
        bpy.ops.caffmob.mobi_baixar_ambiente(ambiente_id=V1['id'],schema=V1['schema'])
        conferir(pedidos[-1]['path']=='/api/draw/v1/ambientes/'+V1['id'],'Cena v1 baixa pela v1')
        responder(200,V1)
        p=enviar()
        conferir('/api/draw/v1/ambientes' in p['path'] and 'Idempotency-Key' not in p['headers'],'Cena v1 envia pela 063, sem entrar no protocolo v2')
        responder(200,dict(version=2))
        # Cena nova, sem documento: POST direto e UUID/chave estáveis na perda.
        for obj in list(context.scene.objects): bpy.data.objects.remove(obj,do_unlink=True)
        for k in list(context.scene.keys()):
            if k.startswith('caffmob_'): del context.scene[k]
        cubo('Nova cena',(1,2,3),(0.2,0.3,0.4))
        antes=len(pedidos)
        p=enviar()
        conferir(len(pedidos)==antes+1 and p['method']=='POST' and p['path']=='/api/draw/v2/ambientes','Cena nova cria com POST sem download prévio')
        conferir(validar(p['body'])==[],'Documento novo é v2 válido')
        responder(None,{})
        r=enviar()
        conferir(r['body']['id']==p['body']['id'] and r['headers']==p['headers'],'POST perdido reutiliza UUID do ambiente e chave da operação')
        sucesso(1,201)
        # Descoberta 404 não autoriza enviar v2 para v1.
        api._sessao.clear()
        antes=len(pedidos)
        enviar()
        conferir(pedidos[-1]['path']=='/api/draw/v2/capacidades','Envio consulta capacidades após reabrir sessão')
        responder(404,{})
        conferir(len(pedidos)==antes+1 and 'somente ambientes v1' in context.window_manager.btm_caffmob.situacao,'Servidor sem v2 recusa cena rica com mensagem clara e sem fallback de escrita')
        conferir(not bpy.app.online_access,'Nenhuma etapa ativou rede do Blender')
    resultado['status']='ok'
finally:
    (ENTREGA/'blender-065-enviar-resultado.json').write_text(json.dumps(resultado,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(resultado,ensure_ascii=False),flush=True)
