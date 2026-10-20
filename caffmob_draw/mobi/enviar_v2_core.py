"""065 T119/T120: cena simulável → delta sobre o contrato integral, sem bpy."""
import copy
import json
import math
from datetime import datetime, timezone
from uuid import uuid4
from .api_v2_core import SCHEMA_V1, SCHEMA_V2
from ..caffmob.v2.contrato import FAMILIAS
from ..caffmob.v2.serializacao import DocumentoInvalido
from ..data.i18n import N_, tr

SEM_MALHA = N_('Objeto sem malha; não foi convertido em caixa')
PRESERVADO = N_('Entidade não suportada; contrato preservado integralmente')
TRANSFORMACAO = N_('Transformação não representável no contrato; ajuste o objeto antes de enviar')
IDENTIDADE = N_('Identidade de entidade inválida ou duplicada na cena')
NOVO = N_('Ambiente do Blender')

TIPOS = dict(parede='paredes', abertura='aberturas', modulo='modulos',
             peca_avulsa='pecas_avulsas', primitiva='primitivas', escada='escadas', item_externo='itens_externos')
DERIVADOS = {'abertura_peca', 'modulo_frentes', 'piso', 'laje', 'forro', 'led'}


def schema_da_cena(scene):
    """O documento ativo manda; uma base v2 antiga nunca promove uma cena v1."""
    raw = scene.get('caffmob_ambiente')
    if raw:
        schema = json.loads(raw)['schema']
        if schema not in (SCHEMA_V1, SCHEMA_V2):
            raise ValueError(tr(PRESERVADO))
        return schema
    return SCHEMA_V2


def novo_documento(nome=None, gerar_uuid=lambda: str(uuid4())):
    documento = {f: [] for f in FAMILIAS}
    documento.update(schema=SCHEMA_V2, id=gerar_uuid(), version=1,
        atualizado_em=datetime.now(timezone.utc).isoformat(timespec='milliseconds').replace('+00:00', 'Z'),
        origem='blender', nome=nome or tr(NOVO), unidade='mm', eixos='Z_UP',
        configuracao_geometrica=dict(perfil='studio/1', espessuras=dict(caixa=15, porta=18, fundo=6)))
    documento['pavimentos'] = [dict(id=gerar_uuid(), nome='Térreo', ordem=0, pe_direito=2600,
        laje=dict(id=gerar_uuid(), ativa=False, tipo='macica', espessura=120, contrapiso=0, beiral=0, recortes=[]),
        forro=dict(tipo='nenhum', material='gesso', sanca=None))]
    return documento


def aplicar_delta(destino, original, editado):
    """Não regrava campos intocados nem usa defaults para completar entidades."""
    if isinstance(original, dict) and isinstance(editado, dict) and isinstance(destino, dict):
        for k in original.keys() - editado.keys():
            destino.pop(k, None)
        for k, valor in editado.items():
            if k not in original:
                destino[k] = copy.deepcopy(valor)
            elif valor != original[k]:
                destino[k] = aplicar_delta(destino.get(k), original[k], valor)
        return destino
    return copy.deepcopy(editado)


def _girar(x, y, graus):
    r = math.radians(graus)
    return x * math.cos(r) - y * math.sin(r), x * math.sin(r) + y * math.cos(r)


def transformar(entidade, objeto, elevacao):
    atual, inicial = objeto.get('lugar'), objeto.get('inicial')
    if not atual or not inicial:
        return
    mudou = (any(abs(a-b) > 0.001 for a,b in zip(atual['posicao'], inicial['posicao']))
             or any(abs(a-b) > 0.00001 for a,b in zip(atual['rotacao'], inicial['rotacao']))
             or any(abs(a-b) > 0.000001 for a,b in zip(atual['escala'], inicial['escala'])))
    if not mudou:
        return
    sx, sy, sz = [a/b if b else 0 for a,b in zip(atual['escala'], inicial['escala'])]
    sx, sy, sz = [1 if abs(v-1) <= 0.000001 else v for v in (sx, sy, sz)]
    tipo = objeto['tipo']
    if (objeto.get('cisalhamento') or min(sx, sy, sz) <= 0 or
        any(abs(v) > 0.00001 for v in atual['rotacao'][:2]) or
        tipo == 'abertura' or
        (tipo == 'parede' and abs(sx-sy) > 0.000001) or
        (entidade.get('forma') == 'cilindro' and abs(sx-sy) > 0.000001) or
        (tipo == 'escada' and abs(sx-sy) > 0.000001)):
        raise DocumentoInvalido([dict(caminho='cena.' + objeto['nome'], codigo='TRANSFORMACAO_NAO_SUPORTADA', mensagem=tr(TRANSFORMACAO))])
    angulo = atual['rotacao'][2] - inicial['rotacao'][2]
    if abs(angulo) <= 0.00001:
        angulo = 0
    parede = tipo == 'parede'
    posicao = entidade['origem'] if parede else entidade['posicao']
    # A origem Blender do módulo fica no meio da traseira; as demais também
    # podem ter pivô deslocado. Conjuga o ponto do contrato pelo lugar inicial.
    x, y = _girar(posicao['x']-inicial['posicao'][0], posicao['y']-inicial['posicao'][1], -inicial['rotacao'][2])
    x, y = _girar(x*sx, y*sy, inicial['rotacao'][2]+angulo)
    for eixo, valor in (('x', atual['posicao'][0]+x), ('y', atual['posicao'][1]+y)):
        if abs(valor-posicao[eixo]) > 0.001:
            posicao[eixo] = valor
    if parede:
        # O contrato de parede não tem Z próprio; só seus afastamentos.
        dz = atual['posicao'][2] - inicial['posicao'][2]
        for s in entidade['segmentos']:
            s['angulo_absoluto'] += angulo
            for campo in ('comprimento', 'espessura', 'flecha'):
                s[campo] *= sx
            for campo in ('pe_direito_inicial', 'pe_direito_final'):
                s[campo] *= sz
            s['afastamento'] = s['afastamento']*sz + dz
        return
    z = atual['posicao'][2] + (posicao['z'] + elevacao - inicial['posicao'][2])*sz - elevacao
    if abs(z-posicao['z']) > 0.001:
        posicao['z'] = z
    entidade['rotacao_z'] += angulo
    medidas = entidade.get('parametros') if tipo == 'modulo' else entidade.get('dimensoes')
    if medidas is not None:
        for campo, fator in zip(('largura', 'profundidade', 'altura'), (sx, sy, sz)):
            if abs(fator-1) > 0.000001:
                medidas[campo] *= fator
    elif entidade.get('forma') == 'cilindro':
        entidade['diametro'] *= sx
        entidade['altura'] *= sz
    elif tipo == 'escada':
        entidade['largura'] *= sx
        entidade['altura'] *= sz


def montar_documento(base, objetos, elevacoes=None):
    """Snapshots têm chave/pai, contrato original/editado, lugar e cantos mundiais em mm."""
    documento, avisos = copy.deepcopy(base), []
    elevacoes = elevacoes or {}
    indice = {e['id']: (familia, e) for familia in FAMILIAS for e in documento[familia]}
    vistos = set()
    for obj in objetos:
        tipo = obj.get('tipo')
        if not tipo or tipo in DERIVADOS:
            continue
        entidade_id = obj.get('id')
        if tipo not in TIPOS:
            avisos.append(dict(caminho='cena.'+obj['nome'], codigo='PRESERVADO', mensagem=tr(PRESERVADO)))
            continue
        if entidade_id in vistos or entidade_id not in indice or indice[entidade_id][0] != TIPOS[tipo]:
            raise DocumentoInvalido([dict(caminho='cena.'+obj['nome'], codigo='IDENTIDADE_INVALIDA', mensagem=tr(IDENTIDADE))])
        vistos.add(entidade_id)
        original = obj['original']
        editada = copy.deepcopy(obj.get('editada', original))
        if editada.get('id') != entidade_id:
            raise DocumentoInvalido([dict(caminho='cena.'+obj['nome'], codigo='IDENTIDADE_INVALIDA', mensagem=tr(IDENTIDADE))])
        perfil = editada.get('perfil_construcao', editada.get('perfil'))
        if perfil and perfil not in ('caffmob.modulo/v1', 'studio/1', 'caffmob.parede/v1'):
            avisos.append(dict(caminho='cena.'+obj['nome'], codigo='PRESERVADO', mensagem=tr(PRESERVADO)))
            continue
        transformar(editada, obj, elevacoes.get(editada.get('pavimento_id'), 0))
        aplicar_delta(indice[entidade_id][1], obj.get('ultimo_envio', original), editada)
    locais = {o['chave']: o for o in objetos if not o.get('tipo')}
    grupos = {}
    for obj in locais.values():
        raiz, caminho = obj, set()
        while raiz.get('pai') in locais and raiz['chave'] not in caminho:
            caminho.add(raiz['chave'])
            raiz = locais[raiz['pai']]
        grupos.setdefault(raiz['chave'], []).append(obj)
    for chave, grupo in grupos.items():
        raiz = locais[chave]
        cantos = [p for obj in grupo for p in obj.get('cantos', [])]
        for obj in grupo:
            if not obj.get('cantos') and obj.get('tipo_blender') != 'EMPTY':
                avisos.append(dict(caminho='cena.'+obj['nome'], codigo='SEM_MALHA', mensagem=tr(SEM_MALHA)))
        if not cantos:
            if all(o.get('tipo_blender') == 'EMPTY' for o in grupo):
                avisos.append(dict(caminho='cena.'+raiz['nome'], codigo='SEM_MALHA', mensagem=tr(SEM_MALHA)))
            continue
        minimo = [min(p[i] for p in cantos) for i in range(3)]
        tamanho = [max(p[i] for p in cantos)-minimo[i] for i in range(3)]
        pavimento = raiz.get('pavimento_id') or documento['pavimentos'][0]['id']
        minimo[2] -= elevacoes.get(pavimento, 0)
        item = dict(id=raiz['externo_id'], nome=raiz['nome'][:160], pavimento_id=pavimento,
                    camada_id=None, visivel=True, posicao=dict(zip('xyz', minimo)), rotacao_z=0,
                    forma='caixa', origem_tipo='externo_blender',
                    dimensoes=dict(zip(('largura', 'profundidade', 'altura'), tamanho)))
        existente = indice.get(item['id'])
        if existente:
            existente[1].update(item)
        else:
            documento['itens_externos'].append(item)
    return documento, avisos
