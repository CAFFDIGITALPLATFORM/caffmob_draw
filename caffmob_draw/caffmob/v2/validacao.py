"""Etapas do Studio: forma, contagens, referências e geometria, nesta ordem."""
from collections import Counter
from .contrato import FAMILIAS, POSICIONAVEIS, LIMITES_STUDIO, SCHEMA_STUDIO
from .forma import erros_da_forma
from .serializacao import serializar, conferir_bytes
from ..validacao import validar_ambiente as validar_geometria_v1, validar_medidas_do_modulo


def erro(caminho, codigo, mensagem):
    return dict(caminho=caminho, codigo=codigo, mensagem=mensagem)


def contar_pecas_legadas(m):
    p = m['parametros']
    k = p['construcao']
    return (5 + k['prateleiras']['quantidade'] * (k['divisorias']['quantidade'] + 1)
            + k['divisorias']['quantidade'] + k['travessas']['quantidade']
            + int(k['rodape']['altura'] > 0) + k['gavetas']['quantidade']
            + (2 if p['portas'] == 'DOUBLE' else 0 if p['portas'] == 'NONE' else 1))


def conferir_contagens(d):
    erros = []
    def teto(caminho, n, limite):
        if n > limite or n > 9007199254740991:
            erros.append(erro(caminho, 'LIMITE', f'Quantidade {n}; máximo {limite}.'))
    teto('pavimentos', len(d['pavimentos']), LIMITES_STUDIO['pavimentos'])
    teto('entidades', sum(len(d[f]) for f in POSICIONAVEIS), LIMITES_STUDIO['entidades'])
    vertices = Counter()
    for p in d['paredes']:
        vertices[p['pavimento_id']] += len(p['segmentos']) + int(not p['fechada'])
    for piso, n in vertices.items():
        i = next((i for i, p in enumerate(d['pavimentos']) if p['id'] == piso), -1)
        teto(f'pavimentos[{i}].vertices', n, LIMITES_STUDIO['vertices_por_pavimento'])
    for s, n in Counter(a['segmento_id'] for a in d['aberturas']).items():
        teto(f'segmentos[{s}].aberturas', n, LIMITES_STUDIO['aberturas_por_segmento'])
    for i, p in enumerate(d['pavimentos']):
        teto(f'pavimentos[{i}].laje.recortes', len(p['laje']['recortes']), LIMITES_STUDIO['recortes'])
    for i, p in enumerate(d['pecas_avulsas']):
        teto(f'pecas_avulsas[{i}].recortes', len(p['recortes']), LIMITES_STUDIO['recortes'])
    teto('modulos', len(d['pecas_avulsas']) + sum(contar_pecas_legadas(m) for m in d['modulos']), LIMITES_STUDIO['pecas'])
    return erros


def conferir_referencias(d):
    erros, ids = [], set()
    def registrar(id, caminho):
        if id in ids:
            erros.append(erro(caminho, 'ID_DUPLICADO', 'O UUID precisa ser único no documento.'))
        ids.add(id)
    registrar(d['id'], 'id')
    for f in FAMILIAS:
        for i, v in enumerate(d[f]):
            registrar(v['id'], f'{f}[{i}].id')
    for i, p in enumerate(d['paredes']):
        for j, s in enumerate(p['segmentos']):
            registrar(s['id'], f'paredes[{i}].segmentos[{j}].id')
    for i, p in enumerate(d['pavimentos']):
        registrar(p['laje']['id'], f'pavimentos[{i}].laje.id')
        for j, r in enumerate(p['laje']['recortes']):
            registrar(r['id'], f'pavimentos[{i}].laje.recortes[{j}].id')
    for i, p in enumerate(d['pecas_avulsas']):
        for j, r in enumerate(p['recortes']):
            registrar(r['id'], f'pecas_avulsas[{i}].recortes[{j}].id')
    pisos = {p['id'] for p in d['pavimentos']}
    materiais = {p['id'] for p in d['materiais']}
    camadas = {p['id'] for p in d['camadas']}
    modulos = {p['id'] for p in d['modulos']}
    segmentos = {s['id'] for p in d['paredes'] for s in p['segmentos']}
    paredes = {p['id'] for p in d['paredes']}
    escadas = {e['id']: e for e in d['escadas']}
    lajes = {p['laje']['id']: p['laje'] for p in d['pavimentos']}
    def ref(id, alvos, caminho):
        if id is not None and id not in alvos:
            erros.append(erro(caminho, 'REFERENCIA_ORFA', 'A referência não existe na família esperada.'))
    for f in POSICIONAVEIS:
        for i, e in enumerate(d[f]):
            ref(e['pavimento_id'], pisos, f'{f}[{i}].pavimento_id')
            ref(e['camada_id'], camadas, f'{f}[{i}].camada_id')
            ref(e.get('material_id'), materiais, f'{f}[{i}].material_id')
    for i, p in enumerate(d['paredes']):
        for j, s in enumerate(p['segmentos']):
            for k in ('material_interno_id', 'material_externo_id'):
                ref(s.get(k), materiais, f'paredes[{i}].segmentos[{j}].{k}')
    for i, c in enumerate(d['camadas']):
        ref(c['pavimento_id'], pisos, f'camadas[{i}].pavimento_id')
    for i, p in enumerate(d['pavimentos']):
        ref(p.get('piso_material_id'), materiais, f'pavimentos[{i}].piso_material_id')
        ref(p['laje'].get('material_id'), materiais, f'pavimentos[{i}].laje.material_id')
        ref(p['forro'].get('material_id'), materiais, f'pavimentos[{i}].forro.material_id')
        if p['ordem'] != i:
            erros.append(erro(f'pavimentos[{i}].ordem', 'ORDEM', 'A ordem deve ser contínua desde zero.'))
        for j, r in enumerate(p['laje']['recortes']):
            if r.get('escada_id'):
                caminho = f'pavimentos[{i}].laje.recortes[{j}].escada_id'
                ref(r['escada_id'], escadas, caminho)
                e = escadas.get(r['escada_id'])
                if e and (e['laje_id'] != p['laje']['id'] or e.get('furo_id') != r['id']):
                    erros.append(erro(caminho, 'REFERENCIA_ORFA', 'A escada precisa apontar para esta laje e recorte.'))
    for i, p in enumerate(d['pecas_avulsas']):
        for j, r in enumerate(p['recortes']):
            if r.get('escada_id'):
                erros.append(erro(f'pecas_avulsas[{i}].recortes[{j}].escada_id', 'REFERENCIA_ORFA', 'Escada referencia recorte de laje, não de peça.'))
    for i, a in enumerate(d['aberturas']):
        ref(a['segmento_id'], segmentos, f'aberturas[{i}].segmento_id')
    for i, e in enumerate(d['escadas']):
        ref(e['laje_id'], lajes, f'escadas[{i}].laje_id')
        if e.get('furo_id') and not any(r['id'] == e['furo_id'] for r in lajes.get(e['laje_id'], {}).get('recortes', [])):
            erros.append(erro(f'escadas[{i}].furo_id', 'REFERENCIA_ORFA', 'O furo precisa pertencer à laje referenciada.'))
    grafo = {}
    def ligar(a, b):
        grafo.setdefault(a, []).append(b)
    for i, m in enumerate(d['modulos']):
        p = m['parametros']['plano_pai']
        caminho = f'modulos[{i}].parametros.plano_pai.id'
        if p['tipo'] in ('MODULE', 'WALL'):
            if not p['id']:
                erros.append(erro(caminho, 'REFERENCIA_ORFA', 'Módulo pai obrigatório.' if p['tipo'] == 'MODULE' else 'Parede pai obrigatória.'))
            ref(p['id'], modulos if p['tipo'] == 'MODULE' else segmentos | paredes, caminho)
            if p['id'] and p['tipo'] == 'MODULE':
                ligar(m['id'], p['id'])
        else:
            ref(p['id'], pisos, caminho)
    origens = set()
    for i, v in enumerate(d['vinculos']):
        ref(v['origem_id'], modulos, f'vinculos[{i}].origem_id')
        ref(v['destino']['id'], {'modulo': modulos, 'segmento': segmentos, 'piso': pisos}[v['destino']['tipo']], f'vinculos[{i}].destino.id')
        if v['origem_id'] in origens:
            erros.append(erro(f'vinculos[{i}].origem_id', 'VINCULO_DUPLICADO', 'Uma origem só pode ter um vínculo explícito.'))
        origens.add(v['origem_id'])
        ligar(v['origem_id'], v['destino']['id'])
    cor = {}
    for inicio in grafo:
        if cor.get(inicio):
            continue
        pilha = [(inicio, False)]
        while pilha:
            id, saindo = pilha.pop()
            if saindo:
                cor[id] = 2
                continue
            if cor.get(id) == 1:
                return erros + [erro('vinculos', 'CICLO', 'Relações não podem formar ciclo.')]
            if cor.get(id) == 2:
                continue
            cor[id] = 1
            pilha.append((id, True))
            pilha.extend((alvo, False) for alvo in grafo.get(id, []))
    return erros


MENSAGENS_V1 = {
    'ABERTURA_MAIOR_QUE_SEGMENTO': 'A abertura é maior que a parede em que está.',
    'ABERTURA_FORA_DO_SEGMENTO': 'A abertura passa do fim da parede.',
    'PEITORIL_FORA': 'O peitoril está fora da faixa: porta tem peitoril 0, e a janela precisa caber no pé-direito.',
    'FLECHA_FORA': 'A flecha precisa ser no máximo metade do comprimento e deixar a espessura caber na curva.',
    'SEGMENTO_INEXISTENTE': 'A abertura aponta para uma parede que não existe.',
    'PAREDE_ABERTA': 'A parede está marcada como fechada, mas o último vértice não volta ao primeiro.',
}


def conferir_geometria(d):
    from .recortes import conferir_recortes
    erros = []
    for i, p in enumerate(d['paredes']):
        if p['perfil'] == 'studio/1':
            for j, s in enumerate(p['segmentos']):
                for campo, minimo, maximo in (('comprimento', 50, 50000), ('espessura', 20, 1000), ('pe_direito_inicial', 1000, 6000), ('pe_direito_final', 1000, 6000)):
                    if not minimo <= s[campo] <= maximo:
                        erros.append(erro(f'paredes[{i}].segmentos[{j}].{campo}', 'DIMENSAO', f'Faixa permitida: {minimo}..{maximo} mm.'))
    if erros:
        return erros
    for e in validar_geometria_v1(dict(paredes=d['paredes'], aberturas=d['aberturas'], modulos=[])):
        erros.append({**e, 'mensagem': MENSAGENS_V1[e['codigo']]})
    for i, m in enumerate(d['modulos']):
        for e in validar_medidas_do_modulo(m['parametros']):
            erros.append(erro(f"modulos[{i}].parametros.{e['caminho']}", e['codigo'], f"O campo {e['caminho']} está fora dos limites do módulo."))
    anteriores = {}
    for i, a in enumerate(d['aberturas']):
        outras = anteriores.setdefault(a['segmento_id'], [])
        if any(a['posicao'] < b['posicao'] + b['largura'] and b['posicao'] < a['posicao'] + a['largura'] for b in outras):
            erros.append(erro(f'aberturas[{i}]', 'SOBREPOSICAO', 'Aberturas do mesmo segmento não podem se sobrepor.'))
        outras.append(a)
    for i, p in enumerate(d['pavimentos']):
        erros.extend(conferir_recortes(p['laje'].get('contorno'), p['laje']['recortes'], f'pavimentos[{i}].laje'))
    for i, p in enumerate(d['pecas_avulsas']):
        w, h = p['dimensoes']['largura'], p['dimensoes']['altura']
        erros.extend(conferir_recortes([dict(x=0, y=0), dict(x=w, y=0), dict(x=w, y=h), dict(x=0, y=h)], p['recortes'], f'pecas_avulsas[{i}]'))
    return erros


def validar_documento(entrada):
    if not isinstance(entrada, dict):
        return [erro('documento', 'ESQUEMA', 'Informe um objeto de documento.')]
    try:
        bytes_erros = conferir_bytes(serializar(entrada))
        if bytes_erros:
            return bytes_erros
    except (ValueError, TypeError, RecursionError, OverflowError):
        # Não finitos são recusados pela forma; JSON.stringify os mede como null.
        import json
        try:
            texto = json.dumps(entrada, ensure_ascii=False, separators=(',', ':'))
            bytes_erros = conferir_bytes(texto)
            if bytes_erros:
                return bytes_erros
        except (ValueError, TypeError, RecursionError, OverflowError):
            return [erro('documento', 'ESQUEMA', 'O documento precisa ser JSON sem ciclos.')]
    if entrada.get('schema') != SCHEMA_STUDIO:
        return [erro('schema', 'ESQUEMA', 'Esquema não suportado.')]
    suporte = []
    if isinstance(entrada.get('modulos'), list):
        for i, m in enumerate(entrada['modulos']):
            if isinstance(m, dict) and m.get('perfil_construcao') != 'caffmob.modulo/v1':
                valor = m.get('perfil_construcao', 'undefined')
                suporte.append(erro(f'modulos[{i}].perfil_construcao', 'RECURSO_NAO_SUPORTADO', f'O recurso {valor} não é suportado nesta fatia; o documento inteiro foi recusado.'))
    forma = erros_da_forma(entrada)
    if suporte or forma:
        return suporte + forma
    return conferir_contagens(entrada) or conferir_referencias(entrada) or conferir_geometria(entrada)


validar_ambiente = validar_documento
validar_documento_studio = validar_documento
