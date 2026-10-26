"""Despacho dos eventos da prancheta, sem bpy; a sessão e a vista são portas de entrada."""
import copy
import math
import time
from ..data import units
from ..caffmob.geometria import geometria_da_parede, vao_da_abertura
from ..caffmob.v2 import paredes_edicao as pe
from .studio import arredondar, snap_ponto, pontos
from .studio_selecao import selecionar_no_retangulo
from .studio_aberturas import projetar


def mm(s):
    return tuple(v * 1000 for v in s.cursor) if s.cursor else (0, 0)


def medir(texto):
    return units.parse_length(texto, 'MM', allow_zero=False) * 1000


def erro(s):
    s.error = '; '.join(e['mensagem'] for e in s.v2.erros)


ESPERA_DA_ARESTA = 0.45


def segurar(op, v, agora=None):
    """Toque ou caneta parados 450 ms: no corpo ligam a seleção múltipla; na aresta, prendem a aresta (G1)."""
    espera = getattr(op, 'studio_espera', None)
    if not espera or (agora if agora is not None else time.monotonic()) - espera['tempo'] < ESPERA_DA_ARESTA:
        return False
    hit = espera['hit']
    if hit['tipo'] == 'trecho':
        v.selecionar_ids([hit['id']], 'somar')
        v.multipla_toque = True
    else:
        v.aresta_presa = True
    op.dragging = espera
    op.studio_espera = None
    return True


def tratar(op, event, s, view, pixel):
    v = s.v2
    escala = view.scale / 1000
    alvo = mm(s)
    ctrl = getattr(event, 'ctrl', False)
    shift = getattr(event, 'shift', False)
    toque = getattr(event, 'is_tablet', False) or getattr(event, 'is_touch', False)
    if event.type == 'SPACE' and (event.value != 'PRESS' or not v.texto):
        op.studio_espaco = event.value == 'PRESS'
        return True
    if event.type in {'MIDDLEMOUSE', 'RIGHTMOUSE'} or (event.type == 'LEFTMOUSE' and getattr(op, 'studio_espaco', False)):
        op.studio_pan = pixel if event.value == 'PRESS' else None
        return True
    if event.type == 'MOUSEMOVE' and getattr(op, 'studio_pan', None) is not None:
        view.pan(pixel[0] - op.studio_pan[0], pixel[1] - op.studio_pan[1])
        op.studio_pan = pixel
        return True
    espera = getattr(op, 'studio_espera', None)
    if event.type == 'TIMER':
        return segurar(op, v)
    if event.type == 'ESC' and event.value == 'PRESS':
        op.studio_espera = None
        if v.confirmacao:
            v.confirmacao = None
            return True
        if v.retangulo:
            v.retangulo = None
            return True
        if op.dragging is not None:
            v.documento = copy.deepcopy(op.dragging['base'])
            op.dragging = None
            return True
        if v.desenhando:
            v.concluir()
        elif v.selecao or v.ponto:
            v.selecionar_ids([])
        else:
            s.request = 'cancel'
        return True
    if event.type == 'A' and event.value == 'PRESS' and not v.desenhando:
        # 067 onda 8 (D-39): as mesmas teclas do projeto do addon; Alt+A limpa.
        if getattr(event, 'alt', False):
            v.selecionar_ids([])
        else:
            v.selecionar_todas()
        return True
    if event.type in {'DEL', 'X', 'BACK_SPACE'} and event.value == 'PRESS' and v.selecao and not v.texto:
        v.pedir_exclusao()
        erro(s)
        return True
    if event.value == 'PRESS' and event.type == 'BACK_SPACE':
        v.texto = v.texto[:-1]
        return True
    if event.value == 'PRESS' and not ctrl and event.unicode and event.unicode in '0123456789,.+-*/() mMcC':
        v.texto += event.unicode
        return True
    setas = {'RIGHT_ARROW': 0, 'UP_ARROW': 90, 'LEFT_ARROW': 180, 'DOWN_ARROW': 270}
    if event.value == 'PRESS' and v.desenhando and event.type in setas:
        v.direcao, v.direcao_travada = setas[event.type], True
        return True
    if event.value == 'PRESS' and event.type in {'RET', 'NUMPAD_ENTER'}:
        try:
            if v.desenhando:
                if v.texto:
                    p = v.previa(alvo, escala, medir(v.texto))
                    v.fixar(p['fim'])
                else:
                    v.concluir()
            elif v.texto and v.selecao:
                v.editar(comprimento=medir(v.texto))
                v.texto = ''
            erro(s)
        except ValueError as exc:
            s.error = str(exc)
        return True
    if event.type == 'MOUSEMOVE' and v.desenhando and not v.texto and not v.direcao_travada:
        v.direcao = v.previa(alvo, escala)['angulo']
    if event.type == 'LEFTMOUSE' and event.value in {'PRESS', 'DOUBLE_CLICK'}:
        if v.desenhando:
            if event.value == 'DOUBLE_CLICK' and math.dist(alvo, v.inicio) < 12 / escala:
                v.concluir()
                return True
            previa = v.previa(alvo, escala, medir(v.texto) if v.texto else None)
            v.fixar(previa['fim'], previa['retorno'] == 'Primeiro ponto' and bool(v.parede_desenho))
            erro(s)
            return True
        if not v.paredes():
            v.iniciar()
            return True
        hit = v.hit(alvo, escala)
        if hit and hit['tipo'] == 'ancora':
            v.ancora = 'fim' if v.ancora == 'inicio' else 'inicio'
            return True
        if hit and hit['tipo'] == 'dividir':
            v.dividir()
            erro(s)
            return True
        if not hit:
            v.retangulo = dict(inicio=alvo, fim=alvo, pixel=pixel, fim_pixel=pixel,
                               somar=shift, base=v.selecionadas[:], moveu=False, toque=toque)
            return True
        ids_antes = v.selecionadas[:]
        id = hit.get('segmento', hit.get('id'))
        if hit['tipo'] == 'ponto':
            p = next(p for p in v.paredes() if p['id'] == hit['parede'])
            ligados = [s['id'] for k, s in enumerate(p['segmentos'])
                       if k == hit['indice'] or (k + 1) % len(pontos(p)) == hit['indice']]
            id = next((id for id in ligados if id in ids_antes), ligados[0])
        if shift or ctrl or (toque and v.multipla_toque):
            v.selecionar_ids([id], 'alternar')
            op.dragging = None
            if toque and v.multipla_toque and id in v.selecionadas:
                op.studio_espera = dict(hit=hit, inicio=alvo, pixel=pixel, base=copy.deepcopy(v.documento), moveu=False, tempo=time.monotonic())
            return True
        conjunto = len(ids_antes) > 1 and id in ids_antes and hit['tipo'] in {'trecho', 'ponto'}
        if not conjunto:
            v.selecionar(hit)
        if hit['tipo'] == 'trecho':
            p = next(p for p in v.paredes() if any(s['id'] == id for s in p['segmentos']))
            t = next(s for s in p['segmentos'] if s['id'] == id)
            v.divisao = t['comprimento'] * hit['fracao']
        agora = time.monotonic()
        anterior = getattr(op, 'studio_clique', None)
        duplo = event.value == 'DOUBLE_CLICK' or (anterior and agora - anterior[0] < 0.35
                and math.dist(pixel, anterior[1]) < 8 and hit == anterior[2])
        op.studio_clique = (agora, pixel, hit)
        if hit and hit['tipo'] == 'trecho' and duplo and not conjunto and not toque:
            op.dragging = None
            v.dividir()
            erro(s)
        elif hit and hit['tipo'] in {'ponto', 'trecho', 'abertura'}:
            arraste = dict(hit=hit, inicio=alvo, pixel=pixel, base=copy.deepcopy(v.documento), moveu=False)
            if toque and hit['tipo'] in {'ponto', 'trecho'}:
                arraste['tempo'] = time.monotonic()
                op.studio_espera = arraste
                op.dragging = None
            else:
                op.dragging = arraste
        return True
    if event.type == 'MOUSEMOVE' and v.retangulo:
        r = v.retangulo
        if r['toque']:
            view.pan(pixel[0] - r['fim_pixel'][0], pixel[1] - r['fim_pixel'][1])
        r['fim'], r['fim_pixel'] = alvo, pixel
        r['moveu'] = r['moveu'] or math.dist(pixel, r['pixel']) > 4
        return True
    if event.type == 'MOUSEMOVE' and espera:
        if math.dist(pixel, espera['pixel']) > 4:
            op.studio_espera = None
        return True
    if event.type == 'MOUSEMOVE' and op.dragging is not None:
        arraste = op.dragging
        if math.dist(pixel, arraste['pixel']) < 8 and not arraste['moveu']:
            return True
        arraste['moveu'] = True
        hit, base = arraste['hit'], arraste['base']
        if len(v.selecionadas) > 1 and hit['tipo'] in {'ponto', 'trecho'}:
            delta = [arredondar(alvo[k] - arraste['inicio'][k], 10) for k in (0, 1)]
            if hit['tipo'] == 'ponto':
                p = next(p for p in base['paredes'] if p['id'] == hit['parede'])
                q = pontos(p)[hit['indice']]
                snapped = snap_ponto(p, hit['indice'], (q[0] + delta[0], q[1] + delta[1]), escala)
                delta = [snapped[k] - q[k] for k in (0, 1)]
            r = pe.mover_paredes_em_lote(base, v.pavimento_id, v.selecionadas, dict(x=delta[0], y=delta[1]))
        elif hit['tipo'] == 'ponto':
            p = next(p for p in base['paredes'] if p['id'] == hit['parede'])
            x, y = snap_ponto(p, hit['indice'], alvo, escala)
            r = pe.mover_vertice(base, hit['parede'], hit['indice'], dict(x=x, y=y))
        elif hit['tipo'] == 'trecho':
            p, i, _ = v.trecho()
            r = pe.mover_aresta(base, p['id'], i, dict(x=alvo[0] - arraste['inicio'][0], y=alvo[1] - arraste['inicio'][1]))
        else:
            a = next(a for a in base['aberturas'] if a['id'] == hit['id'])
            p, i, t = v.trecho()
            g = geometria_da_parede(p)[i]
            pos = arredondar(a['posicao'] + projetar(g, alvo) - projetar(g, arraste['inicio']), 10)
            vao = vao_da_abertura(a, t, g)
            r = pe.editar_abertura(base, a['id'], dict(posicao=max(0, min(vao['faixa'][1], pos))))
        v.documento = copy.deepcopy(base)
        v.tentar(r)
        erro(s)
        return True
    if event.type == 'LEFTMOUSE' and event.value == 'RELEASE':
        op.studio_espera = None
        v.aresta_presa = False
        if v.retangulo:
            r = v.retangulo
            if not r['toque'] and r['moveu']:
                ids = selecionar_no_retangulo(v.documento, v.pavimento_id, r['inicio'], r['fim'], r['fim_pixel'][0] < r['pixel'][0])
                v.selecionar_ids(r['base'] if r['somar'] else [])
                v.selecionar_ids(ids, 'somar')
            elif not r['moveu'] and not r['somar']:
                v.selecionar_ids([])
            v.retangulo = None
        op.dragging = None
        return True
    return event.type == 'MOUSEMOVE'

