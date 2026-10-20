"""065 T119: leitura da cena Blender, sem rede; protocolo fica no cliente v2."""
import copy
import json
import math
from uuid import uuid4
from . import enviar_v2_core as core
from ..geometry.obra_v2 import elevacoes_dos_pavimentos
from ..caffmob.v2.serializacao import serializar

PROPRIEDADES = ('caffmob_entidade_v2', 'caffmob_parede', 'caffmob_abertura', 'caffmob_modulo', 'caffmob_forro')
ESTADO = 'caffmob_estado_cena_v2'


def matriz_mundial(obj):
    # Ocultos por camada podem ficar fora do depsgraph: matrix_world conserva
    # identidade ou o último cache. Os canais locais continuam atualizados.
    if obj.constraints or (obj.parent and obj.parent_type != 'OBJECT'):
        return obj.matrix_world.copy()
    if obj.parent:
        return matriz_mundial(obj.parent) @ obj.matrix_parent_inverse @ obj.matrix_basis
    return obj.matrix_basis.copy()


def lugar(obj):
    loc, rot, escala = matriz_mundial(obj).decompose()
    return dict(posicao=[v*1000 for v in loc], rotacao=[math.degrees(v) for v in rot.to_euler('XYZ')], escala=list(escala))


def registrar_estado(obj):
    """Conserva o lugar e os contratos da malha construída, inclusive após salvar .blend."""
    obj[ESTADO] = serializar(dict(lugar=lugar(obj), propriedades={k: json.loads(obj[k]) for k in PROPRIEDADES if obj.get(k)}))


def _inicial(original, tipo, z, documento):
    if tipo == 'abertura':
        from mathutils import Matrix, Vector
        from ..caffmob.v2.paredes import geometria_da_parede, vao_da_abertura
        for parede in documento['paredes']:
            for segmento, geometria in zip(parede['segmentos'], geometria_da_parede(parede)):
                if segmento['id'] != original['segmento_id']:
                    continue
                vao = vao_da_abertura(original, segmento, geometria)
                ponto = (*[v/1000 for v in vao['inicio']],
                         (z + segmento['afastamento'] + original['peitoril'])/1000)
                r = math.atan2(vao['fim'][1]-vao['inicio'][1], vao['fim'][0]-vao['inicio'][0])
                mundo = Matrix.Translation(Vector(ponto)) @ Matrix.Rotation(r, 4, 'Z')
                if segmento['sentido'] == 'RIGHT':
                    mundo = mundo @ Matrix.Diagonal((1, -1, 1, 1))
                loc, rot, escala = mundo.decompose()
                return dict(posicao=[v*1000 for v in loc], rotacao=[math.degrees(v) for v in rot.to_euler('XYZ')], escala=list(escala))
    posicao = original.get('posicao', dict(x=0, y=0, z=0))
    posicao = [posicao[k] for k in 'xyz'] if isinstance(posicao, dict) else [0, 0, 0]
    rotacao = original.get('rotacao_z', 0)
    if tipo == 'modulo':
        p = original['parametros']
        x, y = core._girar(p['largura']/2, p['profundidade'], rotacao)
        posicao[0] += x
        posicao[1] += y
    posicao[2] += z
    return dict(posicao=posicao, rotacao=[0, 0, rotacao], escala=[1, 1, 1])


def documento_da_cena(context):
    from mathutils import Matrix
    scene = context.scene
    if core.schema_da_cena(scene) != core.SCHEMA_V2:
        raise ValueError(core.SCHEMA_V1)
    raw = scene.get('caffmob_base_v2')
    ativo = scene.get('caffmob_ambiente')
    if raw and ativo and json.loads(raw)['id'] == json.loads(ativo)['id']:
        base = json.loads(raw)
    elif ativo:
        base = json.loads(ativo)
    else:
        base = core.novo_documento(scene.name)
        # Identidade de POST estável mesmo antes da primeira chamada e após cancelar.
        scene['caffmob_ambiente'] = serializar(base)
        for k in ('caffmob_etag_v2', 'caffmob_base_v2', 'caffmob_versao'):
            if k in scene:
                del scene[k]
    elevacoes = elevacoes_dos_pavimentos(base)
    context.view_layer.update()
    depsgraph = context.evaluated_depsgraph_get()
    objetos = []
    for obj in scene.objects:
        tipo = obj.get('caffmob_tipo')
        dado = dict(chave=obj.as_pointer(), pai=obj.parent.as_pointer() if obj.parent else None,
                    nome=obj.name, tipo=tipo, id=obj.get('caffmob_id'), tipo_blender=obj.type)
        if tipo in core.TIPOS and obj.get('caffmob_entidade_v2'):
            original = json.loads(obj['caffmob_entidade_v2'])
            estado = json.loads(obj[ESTADO]) if obj.get(ESTADO) else dict(lugar=_inicial(original, tipo,
                elevacoes.get(obj.get('caffmob_pavimento_id', original.get('pavimento_id')), 0), base), propriedades={})
            fontes = estado['propriedades']
            original = fontes.get('caffmob_entidade_v2', original)
            editada = copy.deepcopy(original)
            for prop in PROPRIEDADES:
                if not obj.get(prop):
                    continue
                atual = json.loads(obj[prop])
                anterior = fontes.get(prop, original)
                if prop == 'caffmob_modulo':
                    # O recipiente v2 mantém campos produtivos que a malha v1 não edita.
                    anterior = fontes.get(prop, {**original.get('parametros', {}),
                        **{k:original[k] for k in ('id', 'nome', 'posicao', 'rotacao_z') if k in original}})
                    parametros = {k:v for k,v in atual.items() if k not in ('id', 'nome', 'posicao', 'rotacao_z')}
                    antigos = {k:v for k,v in anterior.items() if k not in ('id', 'nome', 'posicao', 'rotacao_z')}
                    core.aplicar_delta(editada['parametros'], antigos, parametros)
                    for k in ('nome', 'posicao', 'rotacao_z'):
                        if atual.get(k) != anterior.get(k) and k in atual:
                            editada[k] = atual[k]
                elif prop != 'caffmob_forro':
                    core.aplicar_delta(editada, anterior, atual)
            atual = lugar(obj)
            mundo = matriz_mundial(obj)
            reconstruida = Matrix.LocRotScale(mundo.translation, mundo.to_quaternion(), mundo.to_scale())
            dado.update(original=original, editada=editada, lugar=atual, inicial=estado['lugar'],
                        cisalhamento=any(abs(mundo[i][j]-reconstruida[i][j]) > 1e-6 for i in range(4) for j in range(4)))
            if obj.get('caffmob_ultimo_envio_v2'):
                dado['ultimo_envio'] = json.loads(obj['caffmob_ultimo_envio_v2'])
        elif tipo in core.TIPOS:
            # Nunca converte silenciosamente uma entidade com metadados incompletos.
            dado['tipo'] = 'contrato_ausente'
        elif not tipo:
            if not obj.get('caffmob_externo_id_v2'):
                obj['caffmob_externo_id_v2'] = str(uuid4())
            dado['externo_id'] = obj['caffmob_externo_id_v2']
            dado['pavimento_id'] = obj.get('caffmob_pavimento_id')
            if obj.type == 'MESH':
                avaliado = obj.evaluated_get(depsgraph)
                mundo = matriz_mundial(obj)
                dado['cantos'] = [tuple(v*1000 for v in (mundo @ p.co)) for p in avaliado.data.vertices]
        objetos.append(dado)
    return core.montar_documento(base, objetos, elevacoes)
