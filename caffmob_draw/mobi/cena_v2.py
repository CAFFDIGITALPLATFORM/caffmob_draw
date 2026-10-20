"""065 T114 a T117: documento v2 validado → cena, com troca apenas ao concluir.

Parede do contrato é a fonte da verdade. Não cria parede do Home Builder nem
estado walls2d. Transporte, progresso e cancelamento pertencem à T118.
"""
import math
import bmesh  # type: ignore
import bpy  # type: ignore
from ..caffmob.v2.validacao import validar_documento
from ..caffmob.v2.serializacao import serializar
from ..caffmob.v2.paredes import geometria_da_parede, vao_da_abertura
from ..caffmob.chapas import caixas_das_chapas
from ..geometry import obra_v2 as obra
from ..openings import build, door_core, window_core
from . import cena, materiais_v2

NOME_DA_COLECAO = cena.NOME_DA_COLECAO


def _dados(obj, dado, tipo, pavimento_id):
    obj['caffmob_tipo'] = tipo
    obj['caffmob_id'] = dado['id']
    obj['caffmob_pavimento_id'] = pavimento_id
    obj['caffmob_entidade_v2'] = serializar(dado)
    obj['caffmob_camada_id'] = dado.get('camada_id') or ''
    obj['caffmob_visivel'] = dado.get('visivel', True)


def _material(materiais, id_=None, veio='HORIZONTAL'):
    chave = (id_, veio)
    if chave not in materiais['cache']:
        materiais['cache'][chave] = materiais_v2.criar_material(materiais['dados'].get(id_), veio)
    return materiais['cache'][chave]


def _malha(colecao, nome, malha, materiais, por_face=None, veio='HORIZONTAL'):
    mesh = bpy.data.meshes.new(nome)
    obj = bpy.data.objects.new(nome, mesh)
    colecao.objects.link(obj)
    mesh.from_pydata([tuple(v / 1000 for v in p) for p in malha['vertices']], [], malha['faces'])
    mesh.update()
    uv = mesh.uv_layers.new(name='UVMap')
    indices = {}
    for face, tag, coords in zip(mesh.polygons, malha['materiais'], malha['uvs']):
        mid = por_face.get(tag) if por_face is not None else tag
        material = _material(materiais, mid, veio)
        if material not in indices:
            indices[material] = len(mesh.materials)
            mesh.materials.append(material)
        face.material_index = indices[material]
        for loop, co in zip(face.loop_indices, coords):
            uv.data[loop].uv = co
    return obj


def _lugar(obj, entidade, z):
    obj.location = (entidade['posicao']['x'] / 1000, entidade['posicao']['y'] / 1000,
                    (entidade['posicao']['z'] + z) / 1000)
    obj.rotation_euler.z = math.radians(entidade['rotacao_z'])


def _visibilidade(obj, documento, entidade, categoria):
    obj.hide_viewport = obj.hide_render = not obra.visivel(documento, entidade, categoria)


def _aberturas(documento, parede, colecao, z):
    for s, g in zip(parede['segmentos'], geometria_da_parede(parede)):
        for abertura in (a for a in documento['aberturas'] if a['segmento_id'] == s['id']):
            vao = vao_da_abertura(abertura, s, g)
            root = bpy.data.objects.new('Abertura ' + abertura['id'][:8], None)
            colecao.objects.link(root)
            _dados(root, abertura, 'abertura', parede['pavimento_id'])
            root['caffmob_abertura'] = serializar(abertura)
            root['caffmob_segmento_id'] = s['id']
            root.location = (*[v / 1000 for v in vao['inicio']], (z + s['afastamento'] + abertura['peitoril']) / 1000)
            root.rotation_euler.z = math.atan2(vao['fim'][1] - vao['inicio'][1], vao['fim'][0] - vao['inicio'][0])
            if s['sentido'] == 'RIGHT':
                root.scale.y = -1
            visivel = dict(parede, visivel=parede['visivel'] and s['estado'] != 'oculto')
            _visibilidade(root, documento, visivel, 'paredes')
            width, height, wall = abertura['largura'] / 1000, abertura['altura'] / 1000, s['espessura'] / 1000
            if abertura['tipo'] == 'WINDOW':
                parts = window_core.window_parts(width, height, wall)
            else:
                w, h = door_core.leaf_size(width, height)
                parts = door_core.door_parts(w, h, wall)
            for key, child in build.build(parts, colecao, window=abertura['tipo'] == 'WINDOW').items():
                child.parent = root
                _dados(child, abertura, 'abertura_peca', parede['pavimento_id'])
                child['caffmob_papel'] = str(key)
                _visibilidade(child, documento, visivel, 'paredes')


def _modulo(context, documento, modulo, colecao, z, materiais):
    legado = dict(modulo['parametros'], id=modulo['id'], nome=modulo['nome'],
                  posicao=modulo['posicao'], rotacao_z=modulo['rotacao_z'])
    obj = cena.criar_modulo(context, legado, colecao=colecao)
    obj.location.z += z / 1000
    _dados(obj, modulo, 'modulo', modulo['pavimento_id'])
    obj['caffmob_modulo_v2'] = serializar(modulo)
    _visibilidade(obj, documento, modulo, None)
    obj.data.materials.clear()
    uv = obj.data.uv_layers.active
    # Reusa as caixas e o construtor da 063, trocando somente aparência/UVs. Uma
    # variante por veio evita girar juntas chapas horizontais e verticais.
    frentes_ocultas = []
    for j, b in enumerate(caixas_das_chapas(legado)):
        dado = next((m for m in documento['materiais'] if m['tipo'] == 'textura' and m['textura_id'] == b['textura_id']), None)
        if dado is None and b['textura_id']:
            dado = dict(id=b['textura_id'], nome='Chapa', tipo='textura', textura_id=b['textura_id'])
            materiais['dados'][dado['id']] = dado
        mat = _material(materiais, dado['id'] if dado else None, b['veio'])
        if mat.name not in obj.data.materials:
            obj.data.materials.append(mat)
        indice = obj.data.materials.find(mat.name)
        categoria = ('portas_dormitorio' if legado['tipo'] == 'TALL' else 'portas_cozinha') if b['papel'] in ('PORTA', 'FRENTE_DE_GAVETA') else None
        for face in list(obj.data.polygons)[j * 6:(j + 1) * 6]:
            face.material_index = indice
            # O UV usa a caixa original em mm, com comprimento X, profundidade Y
            # e Z vertical. A escala não depende do tamanho final da chapa.
            for loop in face.loop_indices:
                co = obj.data.vertices[obj.data.loops[loop].vertex_index].co
                x, y, zz = co.x * 1000 + legado['largura'] / 2, co.y * 1000 + legado['profundidade'], co.z * 1000
                uv.data[loop].uv = (x, y) if abs(face.normal.z) > 0.5 else (x if abs(face.normal.y) > 0.5 else y, 1000 - (zz - b['z']))
            if categoria and not obj.hide_viewport and not obra.visivel(documento, modulo, categoria):
                frentes_ocultas.append(face.index)
    if frentes_ocultas:
        # A fonte produtiva continua sendo o contrato do módulo. A cópia oculta
        # conserva as faces das frentes para que esconder a categoria não apague peças.
        mesh = obj.data.copy()
        child = bpy.data.objects.new(modulo['nome'] + ' — frentes ocultas', mesh)
        colecao.objects.link(child)
        child.parent = obj
        _dados(child, modulo, 'modulo_frentes', modulo['pavimento_id'])
        child.hide_viewport = child.hide_render = True
        for alvo, ocultar in ((obj.data, True), (mesh, False)):
            bm = bmesh.new()
            bm.from_mesh(alvo)
            bm.faces.ensure_lookup_table()
            faces = [f for f in bm.faces if (f.index in frentes_ocultas) == ocultar]
            bmesh.ops.delete(bm, geom=faces, context='FACES')
            bm.to_mesh(alvo)
            bm.free()
            alvo.update()
    return obj


def _obra(documento, p, colecao, z, materiais):
    superficies = obra.superficies_do_pavimento(documento, p)
    for tipo in ('piso', 'laje', 'forro'):
        ss = [s for s in superficies if s['tipo'] == tipo or (tipo == 'forro' and s['tipo'] == 'sanca')]
        if not ss:
            continue
        dado = p['laje'] if tipo == 'laje' else p
        mid = p.get('piso_material_id') if tipo == 'piso' else p[tipo].get('material_id')
        if tipo == 'forro' and not mid:
            mid = 'studio/' + p['forro']['material']
        faces = dict(cima=p.get('piso_material_id') if tipo == 'laje' else mid, baixo=mid, lateral=mid)
        m = obra.juntar_malhas(obra.extrudar(s['contorno'], s['furos'], s['z'], s['profundidade']) for s in ss)
        obj = _malha(colecao, tipo.capitalize() + ' ' + p['nome'], m, materiais, faces)
        obj.location.z = z / 1000
        _dados(obj, dado, tipo, p['id'])
        obj['caffmob_chave'] = p['id'] + '/' + tipo
        _visibilidade(obj, documento, dict(p, pavimento_id=p['id']), 'piso' if tipo == 'piso' else 'teto')
        if tipo == 'forro':
            obj['caffmob_forro'] = serializar(p['forro'])
    # LED é uma faixa estreita na borda interna da sanca radial, no rebaixo.
    sanca = next((s for s in superficies if s['tipo'] == 'sanca'), None)
    if sanca and p['forro']['sanca']['led']:
        interno = sanca['furos'][0]
        externo = obra.radial(interno, 5)
        m = obra.extrudar(externo, [interno], sanca['z'] + 15, 2)
        obj = _malha(colecao, 'LED ' + p['nome'], m, materiais, {})
        mat = materiais_v2.criar_material(dict(nome='LED', tipo='cor', cor='#fff1cc', classe_visual='gesso'), emissivo=True)
        obj.data.materials.clear()
        obj.data.materials.append(mat)
        for f in obj.data.polygons:
            f.material_index = 0
        obj.location.z = z / 1000
        _dados(obj, p, 'led', p['id'])
        obj['caffmob_chave'] = p['id'] + '/led'
        _visibilidade(obj, documento, dict(p, pavimento_id=p['id']), 'teto')


def _remover_colecao(colecao, context=None):
    for child in list(colecao.children):
        _remover_colecao(child, context)
    for obj in list(colecao.objects):
        if context is not None and not obj.get('caffmob_tipo'):
            if obj.name not in context.scene.collection.objects:
                context.scene.collection.objects.link(obj)
            colecao.objects.unlink(obj)
        else:
            mesh = obj.data if obj.type == 'MESH' else None
            mats = list(mesh.materials) if mesh is not None else []
            bpy.data.objects.remove(obj, do_unlink=True)
            if mesh is not None and mesh.users == 0:
                bpy.data.meshes.remove(mesh)
            for mat in set(mats):
                if mat is not None and mat.users == 0 and mat.get('caffmob_material'):
                    bpy.data.materials.remove(mat)
    bpy.data.collections.remove(colecao)


def construir_cena(context, documento):
    """Retorna a coleção ativa. Erro antes do commit deixa a cena anterior intacta."""
    erros = validar_documento(documento)
    if erros:
        raise ValueError(str(erros))
    antes = {tipo: {x.as_pointer() for x in getattr(bpy.data, tipo)}
             for tipo in ('objects', 'collections', 'meshes', 'materials', 'images')}
    preparo = bpy.data.collections.new('CAFF MOB preparo v2')
    preparo['caffmob_schema'] = documento['schema']
    preparo['caffmob_id'] = documento['id']
    preparo['caffmob_camadas'] = serializar(documento['camadas'])
    elevacoes = obra.elevacoes_dos_pavimentos(documento)
    materiais = dict(dados={m['id']: m for m in documento['materiais']}, cache={})
    for classe, cor in (('concreto', '#b5b5b5'), ('porcelanato', '#eeeeea'), ('madeira', '#b99770'),
                        ('gesso', '#eee9de'), ('drywall', '#eee9de'), ('pvc', '#efefeb')):
        materiais['dados']['studio/' + classe] = dict(nome=classe.capitalize(), tipo='cor', cor=cor,
                                                     classe_visual='gesso' if classe == 'drywall' else classe)
    colecoes = {}
    try:
        for p in sorted(documento['pavimentos'], key=lambda p: p['ordem']):
            colecao = bpy.data.collections.new(p['nome'])
            preparo.children.link(colecao)
            colecao['caffmob_id'] = p['id']
            colecao['caffmob_pavimento'] = serializar(p)
            colecao['caffmob_ordem'] = p['ordem']
            colecao['caffmob_z_mm'] = elevacoes[p['id']]
            colecao['caffmob_nome'] = p['nome']
            colecoes[p['id']] = colecao
        for parede in documento['paredes']:
            colecao, z = colecoes[parede['pavimento_id']], elevacoes[parede['pavimento_id']]
            obj = _malha(colecao, 'Parede ' + parede['id'][:8], obra.malha_da_parede(documento, parede), materiais)
            _dados(obj, parede, 'parede', parede['pavimento_id'])
            obj['caffmob_parede'] = serializar(parede)
            obj['caffmob_aberturas'] = serializar([a for a in documento['aberturas'] if a['segmento_id'] in {s['id'] for s in parede['segmentos']}])
            obj.location.z = z / 1000
            _visibilidade(obj, documento, parede, 'paredes')
            _aberturas(documento, parede, colecao, z)
        for modulo in documento['modulos']:
            _modulo(context, documento, modulo, colecoes[modulo['pavimento_id']], elevacoes[modulo['pavimento_id']], materiais)
        for tipo, familia in (('peca_avulsa', 'pecas_avulsas'), ('primitiva', 'primitivas'), ('item_externo', 'itens_externos'), ('escada', 'escadas')):
            for e in documento[familia]:
                m = obra.malha_da_escada(e) if tipo == 'escada' else obra.malha_da_entidade(e)
                obj = _malha(colecoes[e['pavimento_id']], e['nome'], m, materiais,
                             {k: e.get('material_id', 'studio/' + e['material'] if tipo == 'escada' else None)
                              for k in ('cima', 'baixo', 'lateral')}, e.get('veio', 'HORIZONTAL'))
                _dados(obj, e, tipo, e['pavimento_id'])
                _lugar(obj, e, elevacoes[e['pavimento_id']])
                _visibilidade(obj, documento, e, None)
                if tipo == 'escada':
                    obj['caffmob_degraus'] = obra.calcular_escada(e)['degraus']
                    obj['caffmob_blocos'] = len(obra.calcular_escada(e)['blocos'])
                    obj['caffmob_laje_id'] = e['laje_id'] or ''
                    obj['caffmob_furo_id'] = e.get('furo_id', '')
                if 'transformacao_origem' in e:
                    obj['caffmob_transformacao_origem'] = e['transformacao_origem']
        for p in documento['pavimentos']:
            _obra(documento, p, colecoes[p['id']], elevacoes[p['id']], materiais)
        guardado = serializar(documento)
    except Exception:
        _remover_colecao(preparo)
        for tipo, ids in antes.items():
            for dado in list(getattr(bpy.data, tipo)):
                if dado.as_pointer() not in ids and dado.users == 0:
                    getattr(bpy.data, tipo).remove(dado)
        raise
    # A coleção de preparo ficou fora da árvore da cena até este ponto.
    antiga = next((c for c in context.scene.collection.children if c.name == NOME_DA_COLECAO or c.get('caffmob_schema') == documento['schema']), None)
    context.scene.collection.children.link(preparo)
    context.scene['caffmob_ambiente'] = guardado
    context.scene['caffmob_versao'] = documento.get('version', 0)
    if antiga:
        _remover_colecao(antiga, context)
    preparo.name = NOME_DA_COLECAO
    for p in documento['pavimentos']:
        colecoes[p['id']].name = p['nome']
    context.scene.unit_settings.system = 'METRIC'
    context.scene.unit_settings.scale_length = 1
    context.view_layer.update()
    # Download é posterior ao commit e nunca invalida uma cena montada.
    try:
        materiais_v2.baixar_pendentes(preparo)
    except Exception:
        # Uma fila/cache indisponível não transforma um commit bem-sucedido em erro.
        for material in materiais['cache'].values():
            material['caffmob_baixando'] = False
    return preparo
