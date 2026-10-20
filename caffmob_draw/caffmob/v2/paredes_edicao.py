"""Operações de edição de parede do Studio: porte de shared/studio/paredes.ts (065 T123).

Mesmas regras e códigos de erro do TypeScript. Nenhuma operação muda o documento recebido; toda
operação devolve `dict(ok=True, valor=documento, avisos=[...])` com a cena nova validada inteira
por `validacao.validar_documento`, ou `dict(ok=False, erros=[...])` sem aplicar nada.
Python puro, sem `bpy`. Cálculos de trecho e de face reaproveitam o porte v1 e `paredes.py`.
"""
import math
from ..contrato import arredondar_medida, normalizar_absoluto, normalizar_relativo
from ..geometria import angulos_relativos, folga_de_fechamento, trechos_da_parede
from .contrato import FAMILIAS
from .paredes import comprimento_da_linha
from .validacao import erro, validar_documento

# Lados dos modelos, em sequência de desenho a partir da origem e girados por `angulo`.
LADOS = dict(
    retangulo=(('largura', 0), ('profundidade', 90), ('largura', 180), ('profundidade', 270)),
    L=(('largura', 0), ('profundidade', 90)),
    U=(('largura', 0), ('profundidade', 90), ('largura', 180)),
)


def falha(caminho, codigo, mensagem):
    return dict(ok=False, erros=[erro(caminho, codigo, mensagem)])


def confirmar_edicao(novo, avisos=None):
    erros = validar_documento(novo)
    return dict(ok=False, erros=erros) if erros else dict(ok=True, valor=novo, avisos=list(avisos or []))


def exigir_confirmacao(dependencias, confirmar):
    if not dependencias or confirmar:
        return []
    return [erro(c, 'CONFIRMAR_DEPENDENCIAS', 'A operação afeta esta relação; confirme para continuar.') for c in dependencias]


def ids_do_documento(d):
    ids = {d['id']}
    for f in FAMILIAS:
        ids.update(e['id'] for e in d[f])
    ids.update(s['id'] for p in d['paredes'] for s in p['segmentos'])
    for p in d['pavimentos']:
        ids.add(p['laje']['id'])
        ids.update(r['id'] for r in p['laje']['recortes'])
    ids.update(r['id'] for p in d['pecas_avulsas'] for r in p['recortes'])
    return ids


def gerador_sem_repeticao(d, gerar_id):
    usados = ids_do_documento(d)

    def gerar():
        for _ in range(1000):
            id = gerar_id()
            if id not in usados:
                usados.add(id)
                return id
        raise ValueError('O gerador de UUID repetiu IDs existentes.')
    return gerar


def _finito(v):
    return type(v) in (int, float) and math.isfinite(v)


def _inteiro(v):
    return type(v) is int or (type(v) is float and v.is_integer())


def _graus(dy, dx):
    return math.atan2(dy, dx) * 180 / math.pi


def _localizar(d, segmento_id):
    for i, parede in enumerate(d['paredes']):
        for j, s in enumerate(parede['segmentos']):
            if s['id'] == segmento_id:
                return i, j, parede
    return None


def _com_parede(d, i, parede):
    return {**d, 'paredes': [parede if k == i else p for k, p in enumerate(d['paredes'])]}


def recalcular_angulos(parede):
    """recalcularAngulos de shared/caffmob/polilinha.ts: normaliza absolutos e refaz relativos."""
    relativos = angulos_relativos(parede['segmentos'])
    return {**parede, 'segmentos': [{**s, 'angulo_absoluto': normalizar_absoluto(s['angulo_absoluto']), 'angulo_relativo': r}
                                    for s, r in zip(parede['segmentos'], relativos)]}


def _com_segmentos(parede, segmentos, origem=None):
    return recalcular_angulos({**parede, 'origem': parede['origem'] if origem is None else origem, 'segmentos': segmentos})


def _ponto(p):
    return dict(x=p[0], y=p[1])


def criar_modelo_de_parede(d, o):
    """`o` como NovoModeloDeParede do TS; `gerar_id` é chamável sem argumentos."""
    lados = LADOS.get(o.get('modelo'))
    if not lados:
        return falha('modelo', 'ESQUEMA', 'Modelo de parede desconhecido.')
    piso = next((p for p in d['pavimentos'] if p['id'] == o.get('pavimento_id')), None)
    if piso is None:
        return falha('pavimento_id', 'REFERENCIA_ORFA', 'Pavimento inexistente.')
    altura = o['pe_direito'] if o.get('pe_direito') is not None else piso['pe_direito']
    gerar_id = gerador_sem_repeticao(d, o['gerar_id'])
    parede = dict(id=gerar_id(), origem=dict(o['origem']), fechada=o['modelo'] == 'retangulo',
                  pavimento_id=o['pavimento_id'], camada_id=None, visivel=True, perfil='studio/1', segmentos=[])
    for medida, angulo in lados:
        parede['segmentos'].append(dict(
            id=gerar_id(), comprimento=o[medida],
            angulo_absoluto=normalizar_absoluto(angulo + (o.get('angulo') or 0)), angulo_relativo=0,
            espessura=o['espessura'] if o.get('espessura') is not None else 150,
            pe_direito_inicial=altura, pe_direito_final=altura, afastamento=0, flecha=0,
            sentido=o.get('sentido') or 'RIGHT', tipo=o.get('tipo') or 'NORMAL', estado='ativo'))
    return confirmar_edicao({**d, 'paredes': [*d['paredes'], recalcular_angulos(parede)]})


def _ou(e, chave, atual):
    return e[chave] if e.get(chave) is not None else atual


def editar_trecho(d, segmento_id, e):
    """`e` como EdicaoDeTrecho: ancora ('inicio'|'fim'), lado_medida ('interna'|'externa'|'eixo') e opcionais."""
    achado = _localizar(d, segmento_id)
    if achado is None:
        return falha('segmento_id', 'REFERENCIA_ORFA', 'Trecho inexistente.')
    i, j, parede = achado
    atual = parede['segmentos'][j]
    angulo = _ou(e, 'angulo', atual['angulo_absoluto'])
    espessura = _ou(e, 'espessura', atual['espessura'])
    comprimento = atual['comprimento'] if e.get('comprimento') is None else comprimento_da_linha(
        parede, j, e['comprimento'], e['lado_medida'], angulo, espessura)
    if not (_finito(comprimento) and comprimento > 0):
        return falha(f'paredes[{i}].segmentos[{j}].comprimento', 'DIMENSAO', 'A medida não deixa comprimento positivo na linha.')
    trechos = trechos_da_parede(parede)
    segmentos = [dict(s) for s in parede['segmentos']]
    segmentos[j] = {**atual, 'comprimento': comprimento, 'angulo_absoluto': normalizar_absoluto(angulo), 'espessura': espessura,
                    **{k: _ou(e, k, atual[k]) for k in ('pe_direito_inicial', 'pe_direito_final', 'flecha', 'afastamento', 'sentido', 'tipo')}}
    origem = parede['origem']
    a = normalizar_absoluto(angulo) * math.pi / 180
    if e.get('ancora') == 'fim':
        # O vértice final fica onde está; o inicial recua pela direção nova.
        fim = trechos[j][1]
        inicio = dict(x=fim[0] - comprimento * math.cos(a), y=fim[1] - comprimento * math.sin(a))
        if j == 0:
            origem = inicio
        else:
            # O trecho anterior se ajusta para chegar ao novo início; o começo dele não se move.
            ini = trechos[j - 1][0]
            dx, dy = inicio['x'] - ini[0], inicio['y'] - ini[1]
            segmentos[j - 1] = {**segmentos[j - 1], 'comprimento': math.hypot(dx, dy), 'angulo_absoluto': normalizar_absoluto(_graus(dy, dx))}
    elif parede['fechada'] and j != len(segmentos) - 1 and len(segmentos) > 1:
        # Como a 061 (mudarComprimento): o último trecho é refeito para a cadeia continuar fechada.
        novos = trechos_da_parede(dict(origem=origem, segmentos=segmentos))
        ultimo = len(segmentos) - 1
        dx, dy = origem['x'] - novos[ultimo][0][0], origem['y'] - novos[ultimo][0][1]
        segmentos[ultimo] = {**segmentos[ultimo], 'comprimento': math.hypot(dx, dy), 'angulo_absoluto': normalizar_absoluto(_graus(dy, dx))}
    return confirmar_edicao(_com_parede(d, i, _com_segmentos(parede, segmentos, origem)))


def dividir_trecho(d, segmento_id, posicao, novo_id):
    """O primeiro pedaço conserva o ID; aberturas do segundo passam ao ID novo."""
    achado = _localizar(d, segmento_id)
    if achado is None:
        return falha('segmento_id', 'REFERENCIA_ORFA', 'Trecho inexistente.')
    i, j, parede = achado
    s = parede['segmentos'][j]
    caminho = f'paredes[{i}].segmentos[{j}]'
    if s['flecha'] != 0:
        return falha(caminho, 'RECURSO_NAO_SUPORTADO', 'Trecho curvo não é dividido nesta fatia; a curva seria perdida.')
    if not (0 < posicao < s['comprimento']):
        return falha(f'{caminho}.comprimento', 'DIMENSAO', 'Divida num ponto interno do trecho.')
    cortadas = [k for k, a in enumerate(d['aberturas'])
                if a['segmento_id'] == segmento_id and a['posicao'] < posicao and a['posicao'] + a['largura'] > posicao]
    if cortadas:
        return dict(ok=False, erros=[erro(f'aberturas[{k}]', 'DEPENDENCIA', 'A divisão cortaria esta abertura.') for k in cortadas])
    fracao = posicao / s['comprimento']
    meio = s['pe_direito_inicial'] + (s['pe_direito_final'] - s['pe_direito_inicial']) * fracao
    # O espalhamento conserva os materiais das duas faces em ambas as metades.
    segmentos = [*parede['segmentos'][:j],
                 {**s, 'comprimento': posicao, 'pe_direito_final': meio},
                 {**s, 'id': novo_id, 'comprimento': s['comprimento'] - posicao, 'pe_direito_inicial': meio},
                 *parede['segmentos'][j + 1:]]
    aberturas = [{**a, 'segmento_id': novo_id, 'posicao': a['posicao'] - posicao}
                 if a['segmento_id'] == segmento_id and a['posicao'] >= posicao else a for a in d['aberturas']]
    return confirmar_edicao({**_com_parede(d, i, _com_segmentos(parede, segmentos)), 'aberturas': aberturas})


def _mudar_estado(d, segmento_id, estado):
    achado = _localizar(d, segmento_id)
    if achado is None:
        return falha('segmento_id', 'REFERENCIA_ORFA', 'Trecho inexistente.')
    i, j, parede = achado
    segmentos = [{**s, 'estado': estado} if k == j else s for k, s in enumerate(parede['segmentos'])]
    return confirmar_edicao(_com_parede(d, i, {**parede, 'segmentos': segmentos}))


def ocultar_trecho(d, segmento_id):
    """Ocultar não apaga: o trecho, suas aberturas e relações continuam no documento."""
    return _mudar_estado(d, segmento_id, 'oculto')


def restaurar_trecho(d, segmento_id):
    return _mudar_estado(d, segmento_id, 'ativo')


def _preso_a(m, segmentos, paredes):
    pai = m['parametros']['plano_pai']
    return pai['tipo'] == 'WALL' and bool(pai['id']) and (pai['id'] in segmentos or pai['id'] in paredes)


def dependencias_dos_trechos(d, segmentos, paredes):
    """Relações que caem junto com os trechos: aberturas, módulos presos à parede e vínculos de segmento."""
    caminhos = [f'aberturas[{k}]' for k, a in enumerate(d['aberturas']) if a['segmento_id'] in segmentos]
    caminhos += [f'modulos[{k}].parametros.plano_pai' for k, m in enumerate(d['modulos']) if _preso_a(m, segmentos, paredes)]
    caminhos += [f'vinculos[{k}]' for k, v in enumerate(d['vinculos'])
                 if v['destino']['tipo'] == 'segmento' and v['destino']['id'] in segmentos]
    return caminhos


def soltar_dependentes(d, segmentos, paredes):
    """Solta os dependentes conservando a posição: o módulo vai ao piso; o vínculo sai."""
    return {**d,
            'aberturas': [a for a in d['aberturas'] if a['segmento_id'] not in segmentos],
            'modulos': [{**m, 'parametros': {**m['parametros'], 'plano_pai': dict(tipo='FLOOR', id=None)}}
                        if _preso_a(m, segmentos, paredes) else m for m in d['modulos']],
            'vinculos': [v for v in d['vinculos'] if not (v['destino']['tipo'] == 'segmento' and v['destino']['id'] in segmentos)]}


def remover_trecho(d, segmento_id, confirmar_dependencias=False, nova_parede_id=None):
    """Na ponta, a cadeia encurta; no meio, vira duas (a segunda recebe `nova_parede_id`); fechada, abre."""
    achado = _localizar(d, segmento_id)
    if achado is None:
        return falha('segmento_id', 'REFERENCIA_ORFA', 'Trecho inexistente.')
    i, j, parede = achado
    pendentes = exigir_confirmacao(dependencias_dos_trechos(d, {segmento_id}, set()), confirmar_dependencias)
    if pendentes:
        return dict(ok=False, erros=pendentes)
    base = soltar_dependentes(d, {segmento_id}, set())
    trechos = trechos_da_parede(parede)
    n = len(parede['segmentos'])
    if n == 1:
        dependentes = exigir_confirmacao(dependencias_dos_trechos(d, set(), {parede['id']}), confirmar_dependencias)
        if dependentes:
            return dict(ok=False, erros=dependentes)
        sem_parede = soltar_dependentes(base, set(), {parede['id']})
        return confirmar_edicao({**sem_parede, 'paredes': [p for k, p in enumerate(sem_parede['paredes']) if k != i]})
    segmentos = parede['segmentos']
    if parede['fechada']:
        resto = [*segmentos[j + 1:], *segmentos[:j]]
        return confirmar_edicao(_com_parede(base, i, _com_segmentos({**parede, 'fechada': False}, resto, _ponto(trechos[j][1]))))
    if j == 0:
        return confirmar_edicao(_com_parede(base, i, _com_segmentos(parede, segmentos[1:], _ponto(trechos[0][1]))))
    if j == n - 1:
        return confirmar_edicao(_com_parede(base, i, _com_segmentos(parede, segmentos[:-1])))
    if not nova_parede_id:
        return falha('novaParedeId', 'ESQUEMA', 'Remover trecho do meio divide a cadeia: informe o UUID da nova parede.')
    primeira = _com_segmentos(parede, segmentos[:j])
    segunda = _com_segmentos({**parede, 'id': nova_parede_id}, segmentos[j + 1:], _ponto(trechos[j][1]))
    return confirmar_edicao({**base, 'paredes': [*base['paredes'][:i], primeira, segunda, *base['paredes'][i + 1:]]})


def limpar_paredes(d, pavimento_id, confirmar_dependencias=False):
    """Limpeza explícita das paredes de um pavimento; os outros pavimentos não mudam."""
    if not any(p['id'] == pavimento_id for p in d['pavimentos']):
        return falha('pavimento_id', 'REFERENCIA_ORFA', 'Pavimento inexistente.')
    alvo = [p for p in d['paredes'] if p['pavimento_id'] == pavimento_id]
    segmentos = {s['id'] for p in alvo for s in p['segmentos']}
    paredes = {p['id'] for p in alvo}
    pendentes = exigir_confirmacao(dependencias_dos_trechos(d, segmentos, paredes), confirmar_dependencias)
    if pendentes:
        return dict(ok=False, erros=pendentes)
    base = soltar_dependentes(d, segmentos, paredes)
    avisos = [f'{len(alvo)} cadeia(s) de parede removida(s) do pavimento.'] if alvo else []
    return confirmar_edicao({**base, 'paredes': [p for p in base['paredes'] if p['pavimento_id'] != pavimento_id]}, avisos)


def _folga_na_precisao_do_contrato(parede):
    """Confere também a precisão usada na gravação, sem arredondar outros trechos ou pavimentos."""
    return folga_de_fechamento(_com_segmentos(parede, [{**s, 'comprimento': arredondar_medida(s['comprimento'])} for s in parede['segmentos']]))


def _com_vertices_editados(parede, segmentos, origem, vizinhos=None):
    """Mantém direções exatas; ajusta só os dois vizinhos se a quantização abrir o contorno."""
    novos = segmentos
    if parede['fechada'] and vizinhos and _folga_na_precisao_do_contrato({**parede, 'origem': origem, 'segmentos': segmentos}) > 0.1:
        i, j = vizinhos
        a, b = segmentos[i], segmentos[j]
        angulo_a, angulo_b = normalizar_absoluto(a['angulo_absoluto']), normalizar_absoluto(b['angulo_absoluto'])
        ax, ay = math.cos(angulo_a * math.pi / 180), math.sin(angulo_a * math.pi / 180)
        bx, by = math.cos(angulo_b * math.pi / 180), math.sin(angulo_b * math.pi / 180)
        determinante = ax * by - ay * bx
        dx = a['comprimento'] * math.cos(a['angulo_absoluto'] * math.pi / 180) + b['comprimento'] * math.cos(b['angulo_absoluto'] * math.pi / 180)
        dy = a['comprimento'] * math.sin(a['angulo_absoluto'] * math.pi / 180) + b['comprimento'] * math.sin(b['angulo_absoluto'] * math.pi / 180)
        # Duas direções canônicas e dois comprimentos conservam a soma vetorial dos vizinhos.
        if abs(determinante) > 1e-9:
            comprimento_a = (dx * by - dy * bx) / determinante
            comprimento_b = (ax * dy - ay * dx) / determinante
            if comprimento_a > 0 and comprimento_b > 0:
                novos = [{**s, 'comprimento': comprimento_a, 'angulo_absoluto': angulo_a} if k == i
                         else {**s, 'comprimento': comprimento_b, 'angulo_absoluto': angulo_b} if k == j else s
                         for k, s in enumerate(segmentos)]
    return {**parede, 'origem': origem, 'segmentos': [
        {**s, 'angulo_relativo': normalizar_relativo(s['angulo_absoluto'] - (novos[k - 1]['angulo_absoluto'] if k else 0))}
        for k, s in enumerate(novos)]}


def _indice_invalido(parede, indice):
    n = len(parede['segmentos'])
    return not _inteiro(indice) or indice < 0 or indice > n - (1 if parede['fechada'] else 0)


def mover_vertice(d, parede_id, indice_do_vertice, ponto):
    """Move um canto sem transladar os demais; o último canto de uma cadeia fechada é o primeiro."""
    i = next((k for k, p in enumerate(d['paredes']) if p['id'] == parede_id), -1)
    if i < 0:
        return falha('parede_id', 'REFERENCIA_ORFA', 'Parede inexistente.')
    parede = d['paredes'][i]
    n = len(parede['segmentos'])
    if _indice_invalido(parede, indice_do_vertice):
        return falha(f'paredes[{i}].vertices', 'ESQUEMA', 'Selecione um ponto existente da parede.')
    indice = int(indice_do_vertice)
    if not _finito(ponto.get('x')) or not _finito(ponto.get('y')):
        return falha(f'paredes[{i}].vertices[{indice}]', 'DIMENSAO', 'Informe coordenadas finitas em milímetros.')
    trechos = trechos_da_parede(parede)
    pontos = [parede['origem'], *(_ponto(t[1]) for t in trechos)]
    pontos[indice] = dict(ponto)
    if parede['fechada'] and indice == 0:
        pontos[n] = dict(ponto)
    segmentos = []
    for k, s in enumerate(parede['segmentos']):
        if k != indice and k + 1 != indice and not (parede['fechada'] and indice == 0 and k == n - 1):
            segmentos.append(s)
            continue
        dx, dy = pontos[k + 1]['x'] - pontos[k]['x'], pontos[k + 1]['y'] - pontos[k]['y']
        segmentos.append({**s, 'comprimento': math.hypot(dx, dy), 'angulo_absoluto': (_graus(dy, dx) + 360) % 360})
    nova = _com_vertices_editados(parede, segmentos, pontos[0], ((indice - 1 + n) % n, indice) if parede['fechada'] else None)
    if nova['fechada'] and _folga_na_precisao_do_contrato(nova) > 0.1:
        return falha(f'paredes[{i}].fechada', 'PAREDE_ABERTA', 'As coordenadas não conservam o fechamento na precisão do contrato.')
    return confirmar_edicao(_com_parede(d, i, nova))


def fundir_trechos(d, parede_id, indice_do_vertice):
    """Excluir um canto une os vizinhos pela corda; na ponta aberta, remove apenas o trecho da ponta."""
    i = next((k for k, p in enumerate(d['paredes']) if p['id'] == parede_id), -1)
    if i < 0:
        return falha('parede_id', 'REFERENCIA_ORFA', 'Parede inexistente.')
    parede = d['paredes'][i]
    n = len(parede['segmentos'])
    if _indice_invalido(parede, indice_do_vertice):
        return falha(f'paredes[{i}].vertices', 'ESQUEMA', 'Selecione um ponto existente da parede.')
    indice = int(indice_do_vertice)
    if not parede['fechada'] and indice in (0, n):
        return remover_trecho(d, parede['segmentos'][0 if indice == 0 else n - 1]['id'])
    if parede['fechada'] and n <= 3:
        return falha(f'paredes[{i}].vertices', 'DIMENSAO', 'Um contorno fechado precisa de ao menos 3 pontos.')
    anterior, seguinte = (indice - 1 + n) % n, indice
    a, b = parede['segmentos'][anterior], parede['segmentos'][seguinte]
    if a['flecha'] != 0 or b['flecha'] != 0:
        return falha(f"paredes[{i}].segmentos[{anterior if a['flecha'] != 0 else seguinte}].flecha", 'RECURSO_NAO_SUPORTADO',
                     'Não é possível excluir o ponto entre trechos curvos; a curva seria perdida.')
    trechos = trechos_da_parede(parede)
    inicio, fim = trechos[anterior][0], trechos[seguinte][1]
    unido = {**a, 'comprimento': math.hypot(fim[0] - inicio[0], fim[1] - inicio[1]),
             'angulo_absoluto': (_graus(fim[1] - inicio[1], fim[0] - inicio[0]) + 360) % 360}
    # Ao excluir a origem fechada, a nova cadeia começa no antigo segundo ponto e termina na união.
    segmentos = [unido if k == anterior else s for k, s in enumerate(parede['segmentos']) if k != seguinte]
    origem = _ponto(fim) if indice == 0 else parede['origem']
    nova = _com_vertices_editados(parede, segmentos, origem)
    if nova['fechada'] and _folga_na_precisao_do_contrato(nova) > 0.1:
        return falha(f'paredes[{i}].fechada', 'PAREDE_ABERTA', 'A união não conserva o fechamento na precisão do contrato.')
    return confirmar_edicao({
        **_com_parede(d, i, nova),
        'aberturas': [{**o, 'segmento_id': a['id'], 'posicao': o['posicao'] + a['comprimento']} if o['segmento_id'] == b['id'] else o
                      for o in d['aberturas']],
        'modulos': [{**m, 'parametros': {**m['parametros'], 'plano_pai': {**m['parametros']['plano_pai'], 'id': a['id']}}}
                    if m['parametros']['plano_pai']['tipo'] == 'WALL' and m['parametros']['plano_pai']['id'] == b['id'] else m
                    for m in d['modulos']],
        'vinculos': [{**v, 'destino': {**v['destino'], 'id': a['id']}}
                     if v['destino']['tipo'] == 'segmento' and v['destino']['id'] == b['id'] else v for v in d['vinculos']],
    })


excluir_ponto = fundir_trechos


def aplicar_espessura_a_todas(d, pavimento_id, espessura):
    """Espessura padrão aplicada exclusivamente às paredes do pavimento informado."""
    if not _finito(espessura) or espessura <= 0:
        return falha('espessura', 'DIMENSAO', 'Informe uma espessura positiva em milímetros.')
    if not any(p['id'] == pavimento_id for p in d['pavimentos']):
        return falha('pavimento_id', 'REFERENCIA_ORFA', 'Pavimento inexistente.')
    return confirmar_edicao({**d, 'paredes': [
        {**p, 'segmentos': [{**s, 'espessura': espessura} for s in p['segmentos']]} if p['pavimento_id'] == pavimento_id else p
        for p in d['paredes']]})


def fixar_vertice(d, parede_id, ponto, novo_id, pavimento_id, espessura=150, origem=None, fechar=False):
    """Lápis do Studio: acrescenta uma corda; fechar usa exatamente o primeiro ponto."""
    parede = next((p for p in d['paredes'] if p['id'] == parede_id), None)
    if parede is None:
        piso = next((p for p in d['pavimentos'] if p['id'] == pavimento_id), None)
        if piso is None:
            return falha('pavimento_id', 'REFERENCIA_ORFA', 'Pavimento inexistente.')
        parede = dict(id=parede_id, origem=dict(origem), fechada=False, pavimento_id=pavimento_id,
                      camada_id=None, visivel=True, perfil='studio/1', segmentos=[])
        inicio = (origem['x'], origem['y'])
        altura = piso['pe_direito']
    else:
        if parede['fechada']:
            return falha('parede_id', 'ESQUEMA', 'Conclua o desenho antes de começar outra parede.')
        inicio = trechos_da_parede(parede)[-1][1]
        altura = parede['segmentos'][-1]['pe_direito_final']
    fim = parede['origem'] if fechar else ponto
    dx, dy = fim['x'] - inicio[0], fim['y'] - inicio[1]
    s = dict(id=novo_id, comprimento=math.hypot(dx, dy), angulo_absoluto=_graus(dy, dx), angulo_relativo=0,
             espessura=espessura, pe_direito_inicial=altura, pe_direito_final=altura, afastamento=0,
             flecha=0, sentido='RIGHT', tipo='NORMAL', estado='ativo')
    nova = recalcular_angulos({**parede, 'fechada': fechar, 'segmentos': [*parede['segmentos'], s]})
    return confirmar_edicao({**d, 'paredes': [nova if p['id'] == parede_id else p for p in d['paredes']]
                            if any(p['id'] == parede_id for p in d['paredes']) else [*d['paredes'], nova]})


def mover_aresta(d, parede_id, indice, delta):
    """Desloca as duas pontas em uma edição atômica; mantém os demais vértices."""
    i = next((k for k, p in enumerate(d['paredes']) if p['id'] == parede_id), -1)
    if i < 0:
        return falha('parede_id', 'REFERENCIA_ORFA', 'Parede inexistente.')
    p = d['paredes'][i]
    if type(indice) is not int or not 0 <= indice < len(p['segmentos']):
        return falha('indice', 'ESQUEMA', 'Selecione um trecho existente.')
    if not all(_finito(delta.get(k)) for k in ('x', 'y')):
        return falha('delta', 'DIMENSAO', 'Informe coordenadas finitas em milímetros.')
    ts = trechos_da_parede(p)
    pontos = [ts[0][0], *(t[1] for t in ts)]
    n = len(p['segmentos'])
    for k in (indice, indice + 1):
        pontos[k] = (pontos[k][0] + delta['x'], pontos[k][1] + delta['y'])
    if p['fechada']:
        if indice == 0:
            pontos[n] = pontos[0]
        elif indice == n - 1:
            pontos[0] = pontos[n]
    segmentos = [{**s, 'comprimento': math.dist(pontos[k], pontos[k + 1]),
                  'angulo_absoluto': _graus(pontos[k + 1][1] - pontos[k][1], pontos[k + 1][0] - pontos[k][0])}
                 for k, s in enumerate(p['segmentos'])]
    return confirmar_edicao(_com_parede(d, i, recalcular_angulos({**p, 'origem': _ponto(pontos[0]), 'segmentos': segmentos})))


def material_da_face(d, segmento_id, face, material_id):
    achado = _localizar(d, segmento_id)
    if achado is None:
        return falha('segmento_id', 'REFERENCIA_ORFA', 'Trecho inexistente.')
    if face not in ('interna', 'externa'):
        return falha('face', 'ESQUEMA', 'Selecione a face interna ou externa.')
    i, j, p = achado
    segmentos = [{**s, 'material_' + ('interno' if face == 'interna' else 'externo') + '_id': material_id} if k == j else s for k, s in enumerate(p['segmentos'])]
    return confirmar_edicao(_com_parede(d, i, {**p, 'segmentos': segmentos}))


def inserir_abertura(d, abertura):
    achado = _localizar(d, abertura['segmento_id'])
    caminho = f"aberturas[{len(d['aberturas'])}].segmento_id"
    if achado is None:
        return falha(caminho, 'REFERENCIA_ORFA', 'Trecho inexistente.')
    _, j, p = achado
    if p['segmentos'][j]['estado'] == 'oculto':
        return falha(caminho, 'TRECHO_OCULTO', 'Restaure o trecho antes de abrir vão nele.')
    return confirmar_edicao({**d, 'aberturas': [*d['aberturas'], dict(abertura)]})


def editar_abertura(d, abertura_id, patch):
    if not any(a['id'] == abertura_id for a in d['aberturas']):
        return falha('aberturas', 'REFERENCIA_ORFA', 'Abertura inexistente.')
    if patch.get('segmento_id') and _localizar(d, patch['segmento_id']) is None:
        k = next(k for k, a in enumerate(d['aberturas']) if a['id'] == abertura_id)
        return falha(f'aberturas[{k}].segmento_id', 'REFERENCIA_ORFA', 'Trecho inexistente.')
    return confirmar_edicao({**d, 'aberturas': [{**a, **patch, 'id': abertura_id} if a['id'] == abertura_id else a
                                               for a in d['aberturas']]})


def remover_abertura(d, abertura_id):
    if not any(a['id'] == abertura_id for a in d['aberturas']):
        return falha('aberturas', 'REFERENCIA_ORFA', 'Abertura inexistente.')
    return confirmar_edicao({**d, 'aberturas': [a for a in d['aberturas'] if a['id'] != abertura_id]})


def criar_modelo_da_prancheta(d, o):
    """Orientação visual usada por EditorDeParedesStudio.modelo para L e U."""
    r = criar_modelo_de_parede(d, o)
    if not r['ok'] or o['modelo'] == 'retangulo':
        return r
    novo = r['valor']
    p = novo['paredes'][-1]
    segmentos = [{**s, 'comprimento': o['largura'] if k == 1 else o['profundidade'],
                  'angulo_absoluto': 270 if k == 0 else 0 if k == 1 else 90,
                  'angulo_relativo': -90 if k == 0 else 90} for k, s in enumerate(p['segmentos'])]
    return confirmar_edicao({**novo, 'paredes': [*novo['paredes'][:-1],
        {**p, 'origem': dict(x=o['origem']['x'], y=o['origem']['y'] + o['profundidade']), 'segmentos': segmentos}]})


def ambiente_atual_na_prancheta(d, original, pavimento_id, gerar_id, espessura=150):
    """Ambiente atual do Studio: repõe paredes originais ou usa o contorno da laje."""
    atuais = [p for p in original['paredes'] if p['pavimento_id'] == pavimento_id]
    if atuais:
        return confirmar_edicao({**d, 'paredes': [p for p in d['paredes'] if p['pavimento_id'] != pavimento_id] + atuais})
    piso = next(p for p in original['pavimentos'] if p['id'] == pavimento_id)
    contorno = piso['laje']['contorno']
    if len(contorno) < 3:
        return criar_modelo_da_prancheta(d, dict(modelo='retangulo', largura=4000, profundidade=3000,
            origem=dict(x=0, y=0), pavimento_id=pavimento_id, gerar_id=gerar_id, espessura=espessura))
    novo, pid, inicio = d, gerar_id(), contorno[0]
    for k, q in enumerate([*contorno[1:], contorno[0]]):
        r = fixar_vertice(novo, pid, q, gerar_id(), pavimento_id, espessura, inicio, k == len(contorno) - 1)
        if not r['ok']:
            return r
        novo = r['valor']
    return confirmar_edicao(novo)


def conferir_lote(d, piso, ids):
    existentes = {s['id'] for p in d['paredes'] if p['pavimento_id'] == piso for s in p['segmentos']}
    return any(p['id'] == piso for p in d['pavimentos']) and bool(ids) and all(id in existentes for id in ids)


def _falha_lote():
    return falha('selecao', 'REFERENCIA_ORFA', 'Selecione paredes existentes do pavimento atual.')


def editar_paredes_em_lote(d, piso, ids, e):
    """IDs de trechos, como no Studio; opcionais ausentes conservam os valores existentes."""
    if not conferir_lote(d, piso, ids):
        return _falha_lote()
    escolhidas = set(ids)
    patch = {k: e[k] for k in ('espessura', 'material_interno_id', 'material_externo_id') if k in e}
    if 'altura' in e:
        patch.update(pe_direito_inicial=e['altura'], pe_direito_final=e['altura'])
    if 'ocultar' in e:
        patch['estado'] = 'oculto' if e['ocultar'] else 'ativo'
    return confirmar_edicao({**d, 'paredes': [
        {**p, 'segmentos': [{**s, **patch} if s['id'] in escolhidas else s for s in p['segmentos']]}
        if p['pavimento_id'] == piso else p for p in d['paredes']]})


def excluir_paredes_em_lote(d, piso, ids, gerar_id, confirmar_dependencias=False):
    """Remove o lote de uma vez, abre contornos e conserva as origens dos grupos restantes."""
    if not conferir_lote(d, piso, ids):
        return _falha_lote()
    removidos = set(ids)
    inteiras = {p['id'] for p in d['paredes'] if all(s['id'] in removidos for s in p['segmentos'])}
    pendentes = exigir_confirmacao(dependencias_dos_trechos(d, removidos, inteiras), confirmar_dependencias)
    if pendentes:
        return dict(ok=False, erros=pendentes)
    base = soltar_dependentes(d, removidos, inteiras)
    gerar = gerador_sem_repeticao(d, gerar_id)
    paredes = []
    for p in base['paredes']:
        if not any(s['id'] in removidos for s in p['segmentos']):
            paredes.append(p)
            continue
        ts = trechos_da_parede(p)
        n = len(ts)
        primeiro = (next(j for j, s in enumerate(p['segmentos']) if s['id'] in removidos) + 1) % n if p['fechada'] else 0
        grupos, grupo = [], None
        for k in range(n):
            j = (primeiro + k) % n
            s = p['segmentos'][j]
            if s['id'] in removidos:
                grupo = None
                continue
            if grupo is None:
                grupo = dict(origem=_ponto(ts[j][0]), segmentos=[])
                grupos.append(grupo)
            grupo['segmentos'].append(s)
        paredes.extend(_com_segmentos({**p, 'id': gerar() if k else p['id'], 'fechada': False},
                                      g['segmentos'], g['origem']) for k, g in enumerate(grupos))
    return confirmar_edicao({**base, 'paredes': paredes})


def mover_paredes_em_lote(d, piso, ids, delta):
    """Cada junta se move uma vez; pontas coincidentes de outras cadeias do piso acompanham."""
    if not conferir_lote(d, piso, ids):
        return _falha_lote()
    if not all(_finito(delta.get(k)) for k in ('x', 'y')):
        return falha('deslocamento', 'DIMENSAO', 'Informe um deslocamento finito.')
    escolhidas = set(ids)
    juntas = [q for p in d['paredes'] if p['pavimento_id'] == piso
              for j, t in enumerate(trechos_da_parede(p)) if p['segmentos'][j]['id'] in escolhidas for q in t]
    paredes = []
    for p in d['paredes']:
        if p['pavimento_id'] != piso or not p['segmentos']:
            paredes.append(p)
            continue
        ts = trechos_da_parede(p)
        originais = [ts[0][0], *(t[1] for t in ts)]
        mover = [any(math.dist(a, q) < 0.1 for a in juntas) for q in originais]
        if not any(mover):
            paredes.append(p)
            continue
        ps = [(q[0] + delta['x'], q[1] + delta['y']) if m else q for q, m in zip(originais, mover)]
        segmentos = [{**s, 'comprimento': math.dist(ps[k], ps[k + 1]),
                      'angulo_absoluto': normalizar_absoluto(_graus(ps[k + 1][1] - ps[k][1], ps[k + 1][0] - ps[k][0]))}
                     if mover[k] or mover[k + 1] else s for k, s in enumerate(p['segmentos'])]
        paredes.append(_com_vertices_editados(p, segmentos, _ponto(ps[0])))
    return confirmar_edicao({**d, 'paredes': paredes})
