"""065 T121: ida e volta REAL web → Blender → web contra o MOBI de ENSAIO em 127.0.0.1.

Não integra tools/portao.sh. Exige:
- CAFFMOB_BASE=http://127.0.0.1:<porta> (qualquer outro host aborta antes de registrar o addon);
- T121_PREPARO=<json de feature/ensaios/t121-preparo.mts> com o token de ensaio e o ambiente v2 criado pela web;
- BLENDER_USER_RESOURCES dentro da pasta de entrega (a sessão do addon é gravada lá, nunca no perfil do usuário);
- opcionais: CAFFMOB_ADDON (raiz do addon, padrão: pasta-mãe de tests/) e T121_RESULTADO (arquivo JSON de saída).

Comando:
  blender --background --factory-startup --online-mode --python-exit-code 1 --python <este arquivo>

Transporte HTTP real (subprocesso do addon). Só os timers do Blender são bombeados à mão, porque --python bloqueia o
laço de eventos; cada callback roda no thread principal na ordem e no intervalo que pediu. O token nunca é impresso.
"""
import copy
import importlib.util
import json
import os
import sys
import time
import uuid
from pathlib import Path
from urllib.parse import urlsplit
from unittest.mock import patch

import bpy

_aqui = Path(__file__).resolve()
# addon/tests/<este> ou a cópia em feature/ensaios/<este>, ambas dentro da pasta de entrega.
ROOT = Path(os.environ.get('CAFFMOB_ADDON') or (_aqui.parents[1] if (_aqui.parents[1] / 'caffmob_draw').is_dir()
                                                 else _aqui.parents[2] / 'addon')).resolve()
ENTREGA = ROOT.parent
BASE = os.environ.get('CAFFMOB_BASE', '')
assert urlsplit(BASE).scheme == 'http' and urlsplit(BASE).hostname == '127.0.0.1', 'Somente o MOBI de ensaio em 127.0.0.1'
assert bpy.app.online_access, 'Use --online-mode'
USUARIO = Path(os.environ.get('BLENDER_USER_RESOURCES', '/')).resolve()
assert ENTREGA in USUARIO.parents, 'BLENDER_USER_RESOURCES precisa ficar dentro da pasta de entrega'
PREPARO = json.loads(Path(os.environ['T121_PREPARO']).read_text())
RESULTADO = Path(os.environ.get('T121_RESULTADO') or ENTREGA / 'feature/ensaios/t121-resultado.json')
AMBIENTE = PREPARO['ambiente_id']
SCHEMA_V2 = 'caffmob.ambiente/v2'
ENVELOPE = ('version', 'atualizado_em', 'origem')  # só no nível de cima; paredes[].origem é geometria
TOLERANCIA_MM = 0.1

# Timers bombeados à mão (a rede continua real).
_timers = {}


def _registrar(cb, first_interval=0.0, persistent=False):
    _timers[cb] = time.monotonic() + (first_interval or 0.0)


def _desregistrar(cb):
    if cb not in _timers:
        raise ValueError('timer não registrado')
    del _timers[cb]


def bombear():
    agora = time.monotonic()
    for cb, quando in list(_timers.items()):
        if quando <= agora and _timers.get(cb) == quando:
            del _timers[cb]
            intervalo = cb()
            if intervalo is not None and cb not in _timers:
                _timers[cb] = time.monotonic() + intervalo


def esperar(predicado, rotulo, limite=90):
    fim = time.monotonic() + limite
    while not predicado():
        assert time.monotonic() < fim, ('Tempo esgotado: ' + rotulo, estado().situacao,
                                        [getattr(cb, '__qualname__', repr(cb)) for cb in _timers],
                                        {k: v.get('state') for k, v in downloads._queue.items.items()}, len(downloads._requests))
        bombear()
        time.sleep(0.002)


PACKAGE = 'bl_ext.ensaio_065_t121.caffmob_draw'
spec = importlib.util.spec_from_file_location(PACKAGE, ROOT / 'caffmob_draw/__init__.py',
                                            submodule_search_locations=[str(ROOT / 'caffmob_draw')])
addon = importlib.util.module_from_spec(spec)
sys.modules[PACKAGE] = addon
spec.loader.exec_module(addon)
from importlib import import_module
api = import_module(PACKAGE + '.mobi.api_v2')
tarefas = import_module(PACKAGE + '.mobi.tarefas')
ops_conta = import_module(PACKAGE + '.mobi.ops_conta')
auth = import_module(PACKAGE + '.texture_library.auth')
catalog = import_module(PACKAGE + '.texture_library.catalog')
downloads = import_module(PACKAGE + '.texture_library.downloads')
validar = import_module(PACKAGE + '.caffmob.v2.validacao').validar_documento

context = bpy.context
resultado = dict(status='erro', blender=bpy.app.version_string, base=BASE, ambiente_id=AMBIENTE,
                 texturas_usadas=PREPARO['texturas'], passos={}, verificacoes=[], diferencas={}, defeitos=[])


def estado():
    return context.window_manager.btm_caffmob


def conferir(valor, texto, passo):
    resultado['passos'].setdefault(passo, [])
    if not valor:
        resultado['passos'][passo].append('FALHOU: ' + texto)
        raise AssertionError(texto + ' | situação: ' + estado().situacao)
    resultado['passos'][passo].append('OK: ' + texto)
    resultado['verificacoes'].append(texto)
    print('  ok -', texto, flush=True)


def ocioso():
    return not estado().ocupado and not tarefas._jobs


def operar(operador, rotulo, **kwargs):
    assert operador(**kwargs) == {'FINISHED'}, rotulo
    esperar(ocioso, rotulo)


def pedido(method, path, body=None, headers=None):
    """Pedido HTTP pelo mesmo transporte autenticado do addon (só para conferir o servidor)."""
    saida = []
    downloads.request(method, path, body, headers=headers, auth=True,
                      callback=lambda s, b, h: saida.append((s, b, h)), response_headers=True)
    esperar(lambda: bool(saida), method + ' ' + path)
    return saida[0]


def ler_servidor():
    status, corpo, headers = pedido('GET', '/api/draw/v2/ambientes/' + AMBIENTE, headers={'Accept': 'application/vnd.caffmob.ambiente+json;version=2'})
    assert status == 200, (status, corpo)
    return corpo, {k.lower(): v for k, v in headers.items()}


def sem_envelope(doc):
    return {k: v for k, v in doc.items() if k not in ENVELOPE}


def comparar(a, b, caminho=''):
    """Diferenças recursivas (chave ausente, tipo, tamanho de lista, valor); número com tolerância de 0,1 mm."""
    difs, maior = [], 0.0
    numero = lambda v: isinstance(v, (int, float)) and not isinstance(v, bool)
    if isinstance(a, dict) and isinstance(b, dict):
        for k in sorted(a.keys() | b.keys()):
            if k not in b:
                difs.append(dict(caminho=caminho + '.' + k, tipo='perdido_no_retorno'))
            elif k not in a:
                difs.append(dict(caminho=caminho + '.' + k, tipo='novo_no_retorno'))
            else:
                d, m = comparar(a[k], b[k], caminho + '.' + k)
                difs += d
                maior = max(maior, m)
    elif isinstance(a, list) and isinstance(b, list):
        if len(a) != len(b):
            difs.append(dict(caminho=caminho, tipo='tamanho', antes=len(a), depois=len(b)))
        for i, (x, y) in enumerate(zip(a, b)):
            d, m = comparar(x, y, caminho + '[' + str(i) + ']')
            difs += d
            maior = max(maior, m)
    elif numero(a) and numero(b):
        maior = abs(a - b)
        if maior > TOLERANCIA_MM:
            difs.append(dict(caminho=caminho, tipo='valor', antes=a, depois=b))
    elif a != b or type(a) is not type(b):
        difs.append(dict(caminho=caminho, tipo='valor', antes=a, depois=b))
    return difs, maior


def foto():
    """Estado inteiro da cena: nomes, transformações, vértices, coleções, propriedades e materiais."""
    objetos = sorted(context.scene.objects, key=lambda o: o.name)
    return dict(
        objetos={o.as_pointer(): (o.name, tuple(o.location), tuple(o.scale), tuple(o.rotation_euler), o.hide_viewport,
                 o.hide_render, o.parent.name if o.parent else None,
                 tuple(tuple(v.co) for v in o.data.vertices) if o.type == 'MESH' else None,
                 tuple(sorted((k, str(o[k])) for k in o.keys()))) for o in objetos},
        colecoes={c.as_pointer(): (c.name, tuple(sorted(o.name for o in c.objects)), tuple(sorted(x.name for x in c.children)))
                  for c in bpy.data.collections},
        propriedades={k: str(context.scene[k]) for k in context.scene.keys() if k != api.PROPRIEDADE},
        materiais={m.as_pointer(): (m.name, tuple(m.diffuse_color)) for m in bpy.data.materials},
        contagens={k: len(getattr(bpy.data, k)) for k in ('objects', 'meshes', 'materials', 'collections', 'images', 'curves')})


def resumo(f):
    return dict(objetos=len(f['objetos']), colecoes=len(f['colecoes']), contagens=f['contagens'])


def texturas_quietas():
    # Nenhum timer além dos periódicos (a fila de texturas começa num timer depois da troca),
    # nenhum pedido em voo, nenhuma imagem na fila e nenhum material marcado como baixando.
    mats = [m for m in bpy.data.materials if m.get('caffmob_material')]
    fila = [i for i in list(downloads._queue.items) if downloads.state(i) in ('PENDING', 'ACTIVE')]
    periodicos = ('_tick', '_remote_tick')  # laço do transporte e timer da biblioteca, sempre registrados
    return (not [cb for cb in _timers if getattr(cb, '__name__', '') not in periodicos] and not downloads._requests and not fila
            and not any(m.get('caffmob_baixando') for m in mats))


def tipos_na_cena():
    contagem = {}
    for o in context.scene.objects:
        t = o.get('caffmob_tipo')
        if t:
            contagem[t] = contagem.get(t, 0) + 1
    return contagem


def colecao_ativa():
    return next(c for c in context.scene.collection.children if c.get('caffmob_schema') == SCHEMA_V2)


with patch.object(bpy.app.timers, 'register', side_effect=_registrar), \
     patch.object(bpy.app.timers, 'is_registered', side_effect=lambda cb: cb in _timers), \
     patch.object(bpy.app.timers, 'unregister', side_effect=_desregistrar):
    addon.register()
    addon.load_file_post(None)
    context.preferences.view.language = 'pt_BR'
    try:
        # ------------------------------------------------------------------ 1. conectar e conferir a referência da web
        passo = '1_conectar_e_referencia_web'
        # A cena de fábrica (Cube, Camera, Light) viraria item externo legítimo no envio; o ensaio parte de cena vazia.
        resultado['cena_de_fabrica_removida'] = sorted(o.name for o in context.scene.objects)
        for obj in list(context.scene.objects):
            bpy.data.objects.remove(obj, do_unlink=True)
        conferir(Path(auth.session_path()).resolve().is_relative_to(ENTREGA), 'Sessão do addon fica dentro da pasta de entrega', passo)
        tokens = dict(PREPARO['token'])
        auth._save(tokens)  # mesmo armazenamento que o login RFC 8628 grava (sessao.json, 0600)
        del tokens
        conferir(auth.signed_in() and oct(os.stat(auth.session_path()).st_mode & 0o777) == '0o600', 'Sessão gravada no armazenamento do addon com modo 600', passo)
        job = api.na_conexao(context, ops_conta.connected_text())  # o mesmo passo que o Conectar faz ao concluir
        esperar(ocioso, 'descoberta na conexão')
        caps = api._sessao.get('capacidades') or {}
        conferir(caps.get('versao_api') == 2 and caps.get('ambientes_v2') is True and SCHEMA_V2 in caps.get('schemas', []),
                 'Conexão descobre capacidades v2 reais', passo)
        original, h = ler_servidor()
        resultado['original'] = original
        conferir(h.get('etag') == '"1"' and original['version'] == 1 and original['origem'] == 'web',
                 'Ambiente criado pela web (criarAmbiente, origem web) na revisão 1', passo)
        conferir(validar(original) == [], 'Documento de referência passa na validação v2 do addon', passo)
        p0, p1 = original['pavimentos']
        conferir(any(s['flecha'] for par in original['paredes'] for s in par['segmentos']), 'Tem arco (flecha ≠ 0)', passo)
        conferir(len(original['pavimentos']) == 2, 'Tem 2 pavimentos', passo)
        furo = p0['laje']['recortes'][0]
        conferir(p0['laje']['ativa'] and furo['escada_id'] == original['escadas'][0]['id']
                 and original['escadas'][0]['furo_id'] == furo['id'], 'Laje com furo ligado à escada (nos dois sentidos)', passo)
        conferir(p1['forro']['tipo'] == 'sanca' and p1['forro']['sanca'], 'Forro com sanca', passo)
        conferir(all(original[k] for k in ('modulos', 'pecas_avulsas', 'primitivas', 'itens_externos', 'materiais', 'aberturas', 'vinculos', 'camadas')),
                 'Módulos, peças, primitivas, externos, materiais, aberturas, vínculos e camadas presentes', passo)
        ids_tex = {t['id'] for t in PREPARO['texturas']}
        usados = {m.get('textura_id') for m in original['materiais']} | {c.get('textura_id') for c in original['modulos'][0]['parametros']['chapas_editadas']}
        conferir(ids_tex <= usados, 'Texturas do catálogo de ensaio usadas no material e na chapa editada', passo)

        # ------------------------------------------------------------------ 2. listar e baixar
        passo = '2_listar_e_baixar'
        operar(bpy.ops.caffmob.mobi_listar_ambientes, 'listar')
        paginas = 1
        while AMBIENTE not in {i.id for i in estado().ambientes} and estado().proximo_ambiente and paginas < 40:
            operar(bpy.ops.caffmob.mobi_listar_ambientes, 'listar mais', mais=True)
            paginas += 1
        item = next((i for i in estado().ambientes if i.id == AMBIENTE), None)
        conferir(item is not None and item.schema == SCHEMA_V2 and item.version == 1,
                 'Lista mostra o ambiente como v2 revisão 1 (' + str(paginas) + ' página(s), ' + str(len(estado().ambientes)) + ' itens)', passo)
        resultado['lista'] = dict(paginas=paginas, itens=len(estado().ambientes),
                                  schemas=sorted({i.schema for i in estado().ambientes}))
        inicio = time.monotonic()
        operar(bpy.ops.caffmob.mobi_baixar_ambiente, 'baixar', ambiente_id=AMBIENTE, schema=item.schema)
        resultado['baixar_ms'] = round((time.monotonic() - inicio) * 1000)
        conferir(context.scene.get('caffmob_etag_v2') == '"1"' and context.scene.get('caffmob_versao') == 1,
                 'Baixar pelo operador real guarda ETag "1" e versão 1', passo)
        conferir(json.loads(context.scene['caffmob_base_v2']) == original and json.loads(context.scene['caffmob_ambiente']) == original,
                 'Documento-base e ativo na cena são idênticos ao GET do servidor', passo)
        raiz = colecao_ativa()
        tipos = tipos_na_cena()
        resultado['cena_montada'] = dict(colecao=raiz.name, objetos=len(raiz.all_objects), tipos=tipos)
        esperado = dict(parede=2, abertura=1, modulo=1, peca_avulsa=1, primitiva=2, escada=1, item_externo=1)
        conferir(all(tipos.get(k, 0) >= v for k, v in esperado.items()), 'Cena montada com paredes, abertura, módulo, peça, primitivas, escada e externo: ' + json.dumps(tipos), passo)
        conferir(tipos.get('laje', 0) >= 1 and tipos.get('forro', 0) >= 1, 'Cena montada com laje e forro derivados', passo)
        esperar(texturas_quietas, 'texturas', limite=60)
        mats = [m for o in raiz.all_objects if o.type == 'MESH' for m in o.data.materials if m and m.get('caffmob_material')]
        com_imagem = sorted({m.name for m in mats if m.node_tree and any(n.type == 'TEX_IMAGE' and n.image for n in m.node_tree.nodes)})
        pendentes = sorted({m.get('caffmob_textura_pendente') for m in mats if m.get('caffmob_textura_pendente')})
        resultado['texturas_na_cena'] = dict(materiais=len(set(mats)), com_imagem=com_imagem, pendentes=pendentes)
        conferir(bool(mats), 'Materiais do documento aplicados à cena (' + str(len(set(mats))) + ')', passo)
        conferir(len(com_imagem) >= 2 and not pendentes, 'Imagens das 2 texturas do catálogo baixadas e ligadas aos materiais: ' + ', '.join(com_imagem), passo)
        # Diagnóstico das imagens: metadados e arquivo de trabalho de cada textura usada, pelo mesmo transporte.
        diag = []
        for t in PREPARO['texturas']:
            st, corpo, _ = pedido('GET', '/api/draw/v1/texturas/' + t['id'])
            item_cat = catalog.item(t['id'])
            obtido = []
            if item_cat:
                downloads.fetch(t['id'], lambda caminho, erro: obtido.append((caminho, erro)), entry=item_cat)
                esperar(lambda: bool(obtido), 'imagem ' + t['id'], limite=60)
            diag.append(dict(id=t['id'], metadados=st, campos=sorted(corpo) if isinstance(corpo, dict) else None,
                             no_catalogo_local=bool(item_cat), estado_fila=downloads.state(t['id']),
                             imagem=dict(baixada=bool(obtido and obtido[0][0]), erro=obtido[0][1] if obtido else None)))
        resultado['texturas_na_cena']['diagnostico'] = diag

        # ------------------------------------------------------------------ 3. enviar sem editar
        passo = '3_enviar_sem_editar'
        operar(bpy.ops.caffmob.mobi_enviar_ambiente, 'enviar sem edição')
        conferir(context.scene.get('caffmob_versao') == 2 and context.scene.get('caffmob_etag_v2') == '"2"' and not context.scene.get(api.PROPRIEDADE),
                 'Servidor gravou a revisão 2 e a cena confirmou a operação', passo)
        volta, h = ler_servidor()
        conferir(volta['version'] == 2 and volta['origem'] == 'blender' and h.get('etag') == '"2"', 'GET v2 devolve revisão 2, origem blender', passo)
        difs, maior = comparar(sem_envelope(original), sem_envelope(volta))
        resultado['diferencas']['sem_edicao'] = dict(lista=difs, maior_mm=maior)
        conferir(not difs, 'Ida e volta sem edição: nenhum campo perdido nem alterado (maior diferença ' + repr(maior) + ' mm)', passo)

        # ------------------------------------------------------------------ 4. editar e enviar
        passo = '4_editar_e_enviar'
        modulo = next(o for o in context.scene.objects if o.get('caffmob_tipo') == 'modulo')
        modulo.location.x += 0.1
        bpy.ops.mesh.primitive_cube_add(size=1, location=(5.0, 1.0, 0.25), scale=(0.4123, 0.3, 0.5))
        cubo = context.object
        cubo.name = 'Cubo local T121'
        context.view_layer.update()
        cantos = [cubo.matrix_world @ v.co for v in cubo.data.vertices]
        min_mm = [min(c[i] for c in cantos) * 1000 for i in range(3)]
        tam_mm = [(max(c[i] for c in cantos) - min(c[i] for c in cantos)) * 1000 for i in range(3)]
        operar(bpy.ops.caffmob.mobi_enviar_ambiente, 'enviar edição')
        conferir(context.scene.get('caffmob_versao') == 3, 'Servidor gravou a revisão 3', passo)
        editado, _ = ler_servidor()
        dx = editado['modulos'][0]['posicao']['x'] - volta['modulos'][0]['posicao']['x']
        erro_mod = abs(dx - 100)
        conferir(erro_mod <= TOLERANCIA_MM, 'Módulo deslocado 100 mm no servidor (Δx = ' + repr(dx) + ' mm)', passo)
        novos = [i for i in editado['itens_externos'] if i['id'] not in {x['id'] for x in volta['itens_externos']}]
        conferir(len(novos) == 1 and novos[0]['nome'] == cubo.name and novos[0]['forma'] == 'caixa', 'Um item externo novo, caixa, com o nome do cubo', passo)
        externo = novos[0]
        erros = [abs(externo['posicao'][k] - v) for k, v in zip('xyz', min_mm)] + \
                [abs(externo['dimensoes'][k] - v) for k, v in zip(('largura', 'profundidade', 'altura'), tam_mm)]
        resultado['externo'] = dict(servidor=externo, esperado=dict(minimo_mm=min_mm, tamanho_mm=tam_mm), erro_max_mm=max(erros))
        conferir(max(erros) <= TOLERANCIA_MM, 'Volume do externo ≤ 0,1 mm (erro ' + repr(max(erros)) + ' mm)', passo)
        comparavel = copy.deepcopy(editado)
        comparavel['itens_externos'] = [i for i in comparavel['itens_externos'] if i['id'] != externo['id']]
        difs, maior_e = comparar(sem_envelope(volta), sem_envelope(comparavel))
        resultado['diferencas']['com_edicao'] = dict(lista=difs, maior_mm_fora_das_edicoes=max(
            [0.0] + [abs(d['depois'] - d['antes']) for d in difs if d['tipo'] == 'valor' and isinstance(d.get('antes'), (int, float))
                     and d['caminho'] != '.modulos[0].posicao.x']))
        conferir({d['caminho'] for d in difs} == {'.modulos[0].posicao.x'}, 'Fora o externo novo, só modulos[0].posicao.x mudou', passo)
        resultado['erro_modulo_mm'] = erro_mod

        # ------------------------------------------------------------------ 5. cancelar e erro preservam a cena
        passo = '5_cancelar_e_erro'
        esperar(texturas_quietas, 'texturas antes da foto', limite=60)
        antes = foto()
        resultado['preservacao'] = dict(antes=resumo(antes))
        # 5a. Cancelar antes da resposta HTTP chegar.
        assert bpy.ops.caffmob.mobi_baixar_ambiente(ambiente_id=AMBIENTE, schema=SCHEMA_V2) == {'FINISHED'}
        bpy.ops.caffmob.mobi_cancelar()
        fim = time.monotonic() + 2
        while time.monotonic() < fim:  # resposta atrasada chega e deve ser ignorada
            bombear()
            time.sleep(0.005)
        conferir(foto() == antes and ocioso(), 'Cancelar com o GET em voo preserva a cena (resposta atrasada ignorada)', passo)
        # 5b. Cancelar no meio da montagem, depois das paredes.
        assert bpy.ops.caffmob.mobi_baixar_ambiente(ambiente_id=AMBIENTE, schema=SCHEMA_V2) == {'FINISHED'}
        job = next(iter(tarefas._jobs.values()))
        esperar(lambda: job.preparo is not None and any(m['etapa'] == 'paredes' for m in job.preparo.medicoes), 'montagem até paredes')
        etapas_feitas = [m['etapa'] for m in job.preparo.medicoes]
        conferir(any(c.name.startswith('CAFF MOB preparo') for c in bpy.data.collections), 'Preparo parcial existe no meio do download (' + ','.join(etapas_feitas) + ')', passo)
        bpy.ops.caffmob.mobi_cancelar()
        for _ in range(200):
            bombear()
            time.sleep(0.002)
        depois = foto()
        resultado['preservacao']['depois_cancelar'] = resumo(depois)
        conferir(depois == antes and ocioso(), 'Cancelar no meio do download preserva objetos, vértices, coleções, propriedades e materiais', passo)
        conferir(not any(c.name.startswith('CAFF MOB preparo') for c in bpy.data.collections), 'Cancelar apaga o preparo inteiro', passo)
        conferir('cancelada' in estado().situacao.lower(), 'Barra informa o cancelamento: ' + estado().situacao, passo)
        # 5c. Erro do servidor: 404 de ambiente inexistente.
        inexistente = str(uuid.uuid4())
        operar(bpy.ops.caffmob.mobi_baixar_ambiente, 'baixar inexistente', ambiente_id=inexistente, schema=SCHEMA_V2)
        resultado['erro_404_situacao'] = estado().situacao
        depois = foto()
        resultado['preservacao']['depois_404'] = resumo(depois)
        conferir(depois == antes, '404 de ambiente inexistente preserva a cena', passo)
        status, corpo, _ = pedido('GET', '/api/draw/v2/ambientes/' + inexistente)
        conferir(status == 404 and corpo.get('erro') == 'NAO_ENCONTRADO', 'Servidor devolveu 404 NAO_ENCONTRADO de verdade', passo)
        conferir(bool(estado().situacao) and estado().situacao != tarefas.tr(tarefas.DONE), 'Erro aparece na barra: ' + estado().situacao, passo)
        final, _ = ler_servidor()
        conferir(final['version'] == 3, 'Nenhuma revisão extra no servidor depois de cancelar e do erro', passo)

        resultado['maior_diferenca_mm'] = max(resultado['diferencas']['sem_edicao']['maior_mm'],
                                              resultado['diferencas']['com_edicao']['maior_mm_fora_das_edicoes'],
                                              resultado['externo']['erro_max_mm'], resultado['erro_modulo_mm'])
        resultado['campos_perdidos'] = [d['caminho'] for k in ('sem_edicao', 'com_edicao')
                                        for d in resultado['diferencas'][k]['lista'] if d['tipo'] in ('perdido_no_retorno', 'tamanho')]
        resultado['status'] = 'ok'
    except Exception as exc:
        resultado['falha'] = repr(exc)
        raise
    finally:
        try:
            # Revoga o aparelho de ensaio e apaga a sessão local, mesmo com falha.
            if auth.signed_in():
                tarefas.cancel_all()
                bpy.ops.caffmob.mobi_desconectar()
                esperar(lambda: not downloads._requests, 'revogação', limite=30)
                resultado['limpeza'] = dict(sessao_local_apagada=not Path(auth.session_path()).exists(), situacao=estado().situacao)
        finally:
            RESULTADO.parent.mkdir(parents=True, exist_ok=True)
            RESULTADO.write_text(json.dumps(resultado, ensure_ascii=False, indent=2) + '\n')
            print(json.dumps({k: resultado.get(k) for k in ('status', 'maior_diferenca_mm', 'campos_perdidos', 'falha')}, ensure_ascii=False), flush=True)
            addon.unregister()
print('BLENDER_065_T121_OK', flush=True)
