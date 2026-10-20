"""Apresentação Blender da prancheta Studio. Regras e documento ficam em studio/parede_edicao."""
import math
import os
import blf
import bpy
from gpu_extras.batch import batch_for_shader
from mathutils import Vector
from mathutils.geometry import tessellate_polygon
from ..canvas2d import draw
from ..caffmob.geometria import geometria_da_parede, trechos_da_parede, vao_da_abertura
from ..caffmob.v2 import paredes_edicao as pe
from ..data import units
from ..data.i18n import tr
from . import props
from . import studio_painel as sp
from .studio import cota, pontos
from .studio_aberturas import simbolo
from .tokens_studio import TOKENS


def cor(nome, tema='claro'):
    valor = TOKENS['cores'][nome][tema]
    if valor.startswith('#'):
        return tuple(int(valor[k:k + 2], 16) / 255 for k in (1, 3, 5)) + (1,)
    return tuple(float(x) / (255 if k < 3 else 1) for k, x in enumerate(valor[5:-1].split(',')))


def mm(s):
    return tuple(v * 1000 for v in s.cursor) if s.cursor else (0, 0)


def tela(view, q):
    return view.to_screen((q[0] / 1000, q[1] / 1000))


def erro(s):
    s.error = '; '.join(e['mensagem'] for e in s.v2.erros)


def medir(texto):
    # O painel do Studio usa milímetros; a expressão mantém contas e sufixos do addon.
    return units.parse_length(texto, 'MM', allow_zero=False) * 1000


def preencher(sh, ps, tinta):
    triangulos = tessellate_polygon([[Vector((q[0], q[1], 0)) for q in ps]])
    if triangulos:
        sh.bind()
        sh.uniform_float('color', tinta)
        batch_for_shader(sh, 'TRIS', {'pos': [(q.x, q.y) for t in triangulos for q in t]}).draw(sh)


# Fonte e formas do Studio -------------------------------------------------------------------------------------
_FONTES = {}
PASTA_FONTES = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'fontes', 'studio')


def fonte(peso=400):
    """Sora do próprio pacote (OFL), como o Studio serve em /fontes/studio; sem ela, a fonte do Blender."""
    peso = 600 if peso >= 600 else 400
    if peso not in _FONTES:
        caminho = os.path.join(PASTA_FONTES, f'sora-latin-{peso}-normal.woff2')
        fid = blf.load(caminho) if os.path.exists(caminho) else -1
        _FONTES[peso] = (fid, caminho) if fid >= 0 else (0, None)
    return _FONTES[peso][0]


def descarregar_fontes():
    for _, caminho in _FONTES.values():
        if caminho:
            try:
                blf.unload(caminho)
            except Exception:
                pass
    _FONTES.clear()


def escala_ui():
    try:
        e = float(bpy.context.preferences.system.ui_scale)
    except AttributeError:
        return 1.0
    return e if e > 0 else 1.0


def medir_texto(texto, tamanho, peso=400):
    f = fonte(peso)
    blf.size(f, tamanho)
    return blf.dimensions(f, tr(texto))[0]


def escrever(x, y, texto, tinta, tamanho, peso=400, espaco=0.0):
    """Texto já traduzido; `espaco` imita o letter-spacing do CSS (o blf não tem)."""
    f = fonte(peso)
    blf.size(f, tamanho)
    blf.color(f, *tinta)
    if not espaco:
        blf.position(f, x, y, 0)
        blf.draw(f, texto)
        return
    for letra in texto:
        blf.position(f, x, y, 0)
        blf.draw(f, letra)
        x += blf.dimensions(f, letra)[0] + espaco


def largura(texto, tamanho, peso=400):
    f = fonte(peso)
    blf.size(f, tamanho)
    return blf.dimensions(f, texto)[0]


def meio(r, tamanho, peso=400):
    """Linha de base que centra o texto no retângulo."""
    f = fonte(peso)
    blf.size(f, tamanho)
    return r[1] + (r[3] - blf.dimensions(f, 'Ag')[1]) / 2 + 1


def alfa(tinta, a):
    return tuple(tinta[:3]) + (a,)


def contorno(r, raio, passos=4):
    x, y, w, h = r
    raio = max(0.0, min(raio, w / 2, h / 2))
    ps = []
    for cx, cy, a0 in ((x + w - raio, y + raio, -90), (x + w - raio, y + h - raio, 0),
                       (x + raio, y + h - raio, 90), (x + raio, y + raio, 180)):
        for k in range(passos + 1):
            a = math.radians(a0 + 90 * k / passos)
            ps.append((cx + raio * math.cos(a), cy + raio * math.sin(a)))
    return ps


def caixa(sh, r, raio, fundo=None, borda=None):
    ps = contorno(r, raio)
    if fundo:
        preencher(sh, ps, fundo)
    if borda:
        draw.lines(sh, [q for a, b in zip(ps, ps[1:] + ps[:1]) for q in (a, b)], borda)


def anel_de_foco(sh, r, raio, e):
    """`:focus-visible` do Studio: 2 px de --blue, afastado 2 px."""
    f = TOKENS['foco']
    for k in range(int(f['largura_px'] * e)):
        d = (f['afastamento_px'] + k) * e
        caixa(sh, (r[0] - d, r[1] - d, r[2] + 2 * d, r[3] + 2 * d), TOKENS['raios']['campo'] * e + d, borda=cor(f['cor']))


def seta(sh, centro, angulo, comprimento, tinta):
    a = math.radians(angulo)
    ux, uy = math.cos(a), math.sin(a)
    x0, y0 = centro[0] - ux * comprimento / 2, centro[1] - uy * comprimento / 2
    x1, y1 = centro[0] + ux * comprimento / 2, centro[1] + uy * comprimento / 2
    ps = [(x0, y0), (x1, y1)]
    for lado in (1, -1):
        b = a + math.pi + lado * math.radians(35)
        ps += [(x1, y1), (x1 + math.cos(b) * comprimento * 0.4, y1 + math.sin(b) * comprimento * 0.4)]
    draw.lines(sh, ps, tinta)


def desenhar_painel(sh, s, view, e):
    """Painel lateral da parede como `.studio-paredes-painel` (T128): cartões, rótulos, cores e medidas do Studio."""
    v = s.v2
    area = getattr(s, 'studio_painel_area', None)
    if not area:
        return
    p = sp.painel_de(v)
    x0, y0, w, h = area
    tp = TOKENS['tipografia']
    corpo, secao = tp['corpo_px'] * e, tp['secao_px'] * e
    raio_campo, raio_botao, raio_peq = TOKENS['raios']['campo'] * e, TOKENS['medidas']['raio_botao'] * e, TOKENS['raios']['pequeno'] * e
    draw.rect(sh, area, cor('paper'))
    draw.lines(sh, [(x0, y0), (x0, y0 + h)], cor('line'))
    itens = p.compor(v, area, medir_texto, e)
    primeiro = True
    for it in itens:
        c, r = it['c'], it['r']
        rotulo = tr(c['rotulo']).format(*c.get('args', ())) if c.get('args') else tr(c['rotulo'])
        if c['tipo'] == 'titulo':
            if not primeiro:
                y = r[1] + r[3] + TOKENS['espacamento']['grupo'] * e / 2
                draw.lines(sh, [(x0 + 1, y), (x0 + w, y)], cor('line-soft'))
            escrever(r[0], r[1] + TOKENS['espacamento']['margem'] * e, rotulo.upper(), cor('orange-ink'), secao, 600,
                     tp['secao_espacamento_px'] * e)
            if c.get('args'):
                n = str(c['args'][0])
                bw = largura(n, secao, 600) + 12 * e
                selo = (x0 + w - TOKENS['espacamento']['painel'] * e - bw, r[1] + TOKENS['espacamento']['margem'] * e - 4 * e, bw, secao + 8 * e)
                caixa(sh, selo, selo[3] / 2, cor('orange'))
                escrever(selo[0] + 6 * e, meio(selo, secao, 600), n, cor('on-orange'), secao, 600)
        elif c['tipo'] in ('campo', 'escolha'):
            caixa_r = it['partes'][0][1]
            escrever(r[0], meio(r, corpo), rotulo, cor('muted'), corpo)
            focado = p.foco == c['id']
            caixa(sh, caixa_r, raio_campo, cor('paper'), cor('line-strong') if p.hover == c['id'] else cor('line'))
            grande = c.get('grande')
            tamanho, peso = (tp['marca_px'] * e, 600) if grande else (corpo, 400)
            if c['tipo'] == 'escolha':
                nomes = dict(c['opcoes'])
                texto = tr(nomes.get(c['valor'], nomes.get('', '')))
                tinta = cor('muted') if not c['valor'] else cor('ink')
                escrever(caixa_r[0] + 8 * e, meio(caixa_r, corpo), texto, tinta, corpo)
                cx, cy = caixa_r[0] + caixa_r[2] - 12 * e, caixa_r[1] + caixa_r[3] / 2
                draw.lines(sh, [(cx - 4 * e, cy + 2 * e), (cx, cy - 2 * e), (cx, cy - 2 * e), (cx + 4 * e, cy + 2 * e)], cor('muted'))
            else:
                texto = p.texto if focado else sp.formatar(c['valor'])
                tinta = cor('ink')
                if not texto and not focado and c.get('placeholder'):
                    texto, tinta = tr(c['placeholder']), cor('muted')
                lw = largura(texto, tamanho, peso)
                tx = caixa_r[0] + caixa_r[2] - 8 * e - lw if grande else caixa_r[0] + 8 * e
                base = meio(caixa_r, tamanho, peso)
                if focado and p.marcado and texto:
                    draw.rect(sh, (tx - 1, caixa_r[1] + 5 * e, lw + 2, caixa_r[3] - 10 * e), cor('orange-tint'))
                escrever(tx, base, texto, tinta, tamanho, peso)
                if focado and not p.marcado:
                    cx = tx + largura(texto[:p.cursor], tamanho, peso)
                    draw.lines(sh, [(cx, caixa_r[1] + 6 * e), (cx, caixa_r[1] + caixa_r[3] - 6 * e)], cor('ink'))
                unidade = c.get('unidade', '')
                escrever(caixa_r[0] + caixa_r[2] + 6 * e, meio(caixa_r, tp['subtitulo_px'] * e), unidade, cor('muted'), tp['subtitulo_px'] * e)
            if focado:
                anel_de_foco(sh, caixa_r, raio_campo, e)
        elif c['tipo'] == 'segmentado':
            fundo = it['partes'][0][1]
            escrever(r[0], fundo[1] + fundo[3] + 5 * e, rotulo, cor('muted'), secao)
            caixa(sh, fundo, raio_botao, cor('cream'))
            nomes = dict(c['opcoes'])
            for valor, rr in it['partes'][1:]:
                ativo = valor == c['valor']
                if ativo:
                    caixa(sh, (rr[0], rr[1] - 1 * e, rr[2], rr[3]), raio_campo, cor('sombra'))
                    caixa(sh, rr, raio_campo, cor('paper'))
                texto = tr(nomes[valor])
                peso = 600 if ativo else 400
                escrever(rr[0] + (rr[2] - largura(texto, corpo, peso)) / 2, meio(rr, corpo, peso), texto,
                         cor('orange-ink') if ativo else cor('ink'), corpo, peso)
        elif c['tipo'] == 'pad':
            escrever(r[0], r[1] + r[3] - secao, rotulo, cor('muted'), secao)
            for angulo, rr in it['partes']:
                if angulo == 'ok':
                    caixa(sh, rr, raio_botao, cor('teal-ink'), cor('teal-ink'))
                    escrever(rr[0] + (rr[2] - largura('OK', corpo, 600)) / 2, meio(rr, corpo, 600), 'OK', cor('paper'), corpo, 600)
                    continue
                ativo = c['valor'] is not None and round(c['valor']) % 360 == angulo
                caixa(sh, rr, raio_botao, cor('orange') if ativo else cor('paper'), cor('orange') if ativo else cor('line'))
                seta(sh, (rr[0] + rr[2] / 2, rr[1] + rr[3] / 2), angulo, 14 * e, cor('on-orange') if ativo else cor('ink'))
        elif c['tipo'] == 'botao':
            fundo, borda, tinta, peso = cor('paper'), cor('line'), cor('ink'), 400
            if c.get('primario'):
                fundo, borda, tinta, peso = cor('orange'), cor('orange'), cor('on-orange'), 600
            elif c.get('ativo'):
                fundo, borda, tinta = cor('orange-tint'), cor('orange'), cor('orange-ink')
            elif c.get('perigo'):
                borda, tinta = alfa(cor('danger'), 0.45), cor('danger')
            if p.hover == c['id'] and not c.get('desabilitado'):
                borda = cor('line-strong') if not c.get('primario') else cor('orange-ink')
            if c.get('desabilitado'):
                fundo, borda, tinta = alfa(fundo, 0.45), alfa(borda, 0.45), alfa(tinta, 0.45)
            caixa(sh, r, raio_peq, fundo, borda)
            escrever(r[0] + (r[2] - largura(rotulo, secao, peso)) / 2, meio(r, secao, peso), rotulo, tinta, secao, peso)
        primeiro = False
    # Cabeçalho e rodapé fixos.
    cab = p.cabecalho
    draw.rect(sh, cab, cor('paper'))
    draw.lines(sh, [(cab[0], cab[1]), (cab[0] + cab[2], cab[1])], cor('line-soft'))
    pad = TOKENS['espacamento']['painel'] * e
    escrever(cab[0] + pad, meio(cab, tp['modal_px'] * e, 600), tr('Editar paredes'), cor('ink'), tp['modal_px'] * e, 600)
    n = len(v.selecionadas)
    if n > 1:
        texto = str(n)
        bw = largura(texto, corpo, 600) + 16 * e
        selo = (cab[0] + cab[2] - pad - bw, cab[1] + (cab[3] - 22 * e) / 2, bw, 22 * e)
        caixa(sh, selo, 11 * e, cor('orange'))
        escrever(selo[0] + 8 * e, meio(selo, corpo, 600), texto, cor('on-orange'), corpo, 600)
    rodape = (x0, y0, w, p.rodape_rects[0][1][1] + p.rodape_rects[0][1][3] + TOKENS['espacamento']['grupo'] * e - y0)
    draw.rect(sh, rodape, cor('paper'))
    draw.lines(sh, [(x0, rodape[1] + rodape[3]), (x0 + w, rodape[1] + rodape[3])], cor('line'))
    for id, rr in p.rodape_rects:
        primario = id == 'aplicar'
        caixa(sh, rr, TOKENS['medidas']['raio_botao'] * e, cor('orange') if primario else cor('paper'),
              cor('orange') if primario else (cor('line-strong') if p.hover == id else cor('line')))
        texto = tr('Aplicar') if primario else tr('Cancelar')
        escrever(rr[0] + (rr[2] - largura(texto, corpo, 600)) / 2, meio(rr, corpo, 600), texto,
                 cor('on-orange') if primario else cor('ink'), corpo, 600)
    erro_texto = p.erro or s.error
    if erro_texto:
        escrever(x0 + pad, rodape[1] + rodape[3] + 6 * e, erro_texto[:60], cor('danger'), tp['subtitulo_px'] * e)
    for valor, nome, rr in p.menu_rects:
        caixa(sh, rr, 0, cor('orange-tint') if p.menu and valor == p.menu.get('valor') else cor('paper'), cor('line'))
        escrever(rr[0] + 8 * e, meio(rr, corpo), tr(nome), cor('ink'), corpo)


def desenhar_selecao(sh, s, view, e):
    """Retângulo da seleção, barra do toque e diálogo de exclusão em lote (T133)."""
    v = s.v2
    r = v.retangulo
    if r and r['moveu'] and not r['toque']:
        a, b = tela(view, r['inicio']), tela(view, r['fim'])
        ret = (min(a[0], b[0]), min(a[1], b[1]), abs(b[0] - a[0]), abs(b[1] - a[1]))
        draw.rect(sh, ret, alfa(cor('orange'), 0.08))
        toca = r['fim_pixel'][0] < r['pixel'][0]
        cantos = [(ret[0], ret[1]), (ret[0] + ret[2], ret[1]), (ret[0] + ret[2], ret[1] + ret[3]), (ret[0], ret[1] + ret[3])]
        for q0, q1 in zip(cantos, cantos[1:] + cantos[:1]):
            draw.lines(sh, draw.dashed(q0, q1, 2, 3) if toca else draw.dashed(q0, q1, 6, 4), cor('orange'))
    corpo = TOKENS['tipografia']['corpo_px'] * e
    barra = sp.barra_toque(v, view.rect, medir_texto, e)
    if barra:
        fundo = barra[0][1]
        caixa(sh, fundo, fundo[3] / 2, cor('paper'), cor('line'))
        texto = tr('{} paredes').format(len(v.selecionadas))
        escrever(fundo[0] + 16 * e, meio(fundo, corpo, 600), texto, cor('ink'), corpo, 600)
        for nome, rr in barra[1:]:
            rotulo = tr('Todas') if nome == 'todas' else tr('Pronto')
            escrever(rr[0] + (rr[2] - largura(rotulo, corpo, 600)) / 2, meio(rr, corpo, 600), rotulo, cor('orange-ink'), corpo, 600)
    if v.confirmacao:
        draw.rect(sh, (0, 0, view.rect[2], view.rect[3]), cor('sombra-forte'))
        d = sp.dialogo(view.rect, e)
        caixa(sh, d['cartao'], TOKENS['raios']['dialogo'] * e, cor('paper'), cor('line'))
        texto = tr(sp.CONFIRMAR_LOTE).format(v.confirmacao['quantidade'])
        linhas, linha = [], ''
        limite = d['cartao'][2] - 2 * TOKENS['espacamento']['secao'] * e
        for palavra in texto.split():
            tentativa = (linha + ' ' + palavra).strip()
            if linha and largura(tentativa, corpo) > limite:
                linhas.append(linha)
                linha = palavra
            else:
                linha = tentativa
        linhas.append(linha)
        y = d['cartao'][1] + d['cartao'][3] - TOKENS['espacamento']['secao'] * e - corpo
        for k, linha in enumerate(linhas[:4]):
            escrever(d['cartao'][0] + TOKENS['espacamento']['secao'] * e, y - k * corpo * 1.5, linha,
                     cor('ink'), corpo, 600 if k == 0 else 400)
        for nome, rotulo, fundo, tinta in (('cancelar', tr('Cancelar'), cor('paper'), cor('ink')),
                                           ('confirmar_exclusao', tr('Excluir'), cor('danger'), cor('on-orange'))):
            rr = d[nome]
            caixa(sh, rr, TOKENS['medidas']['raio_botao'] * e, fundo, cor('line') if nome == 'cancelar' else fundo)
            escrever(rr[0] + (rr[2] - largura(rotulo, corpo, 600)) / 2, meio(rr, corpo, 600), rotulo, tinta, corpo, 600)


def capturar(op, context, event, s, view, pixel):
    """Eventos do painel desenhado, do diálogo e da barra de toque, antes da prancheta e da navegação."""
    v = s.v2
    p = sp.painel_de(v)
    e = escala_ui()
    if v.confirmacao:
        d = sp.dialogo(view.rect, e)
        if event.value == 'PRESS' and event.type in {'RET', 'NUMPAD_ENTER'}:
            sp.executar(s, 'confirmar_exclusao')
        elif event.value == 'PRESS' and event.type == 'ESC':
            sp.executar(s, 'cancelar_exclusao')
        elif event.value == 'PRESS' and event.type == 'LEFTMOUSE':
            for nome in ('cancelar', 'confirmar_exclusao'):
                if sp.dentro(pixel, d[nome]):
                    sp.executar(s, 'cancelar_exclusao' if nome == 'cancelar' else nome)
        return event.type not in {'WHEELUPMOUSE', 'WHEELDOWNMOUSE', 'MIDDLEMOUSE', 'TRACKPADPAN', 'TRACKPADZOOM'}
    mouse = {'MOUSEMOVE', 'LEFTMOUSE', 'MIDDLEMOUSE', 'RIGHTMOUSE', 'WHEELUPMOUSE', 'WHEELDOWNMOUSE',
             'TRACKPADPAN', 'TRACKPADZOOM', 'TIMER', 'INBETWEEN_MOUSEMOVE'}
    if p.foco and event.type not in mouse:
        if p.tecla(v, event):
            if v.erros:
                erro(s)
            return True
    if event.type == 'TAB' and event.value == 'PRESS':
        return p.tecla(v, event)
    if event.type == 'LEFTMOUSE' and event.value == 'PRESS':
        for nome, r in sp.barra_toque(v, view.rect, medir_texto, e)[1:]:
            if sp.dentro(pixel, r):
                sp.executar(s, nome)
                return True
    area = getattr(s, 'studio_painel_area', None)
    ocupado = (getattr(op, 'dragging', None) is not None or v.retangulo or getattr(op, 'studio_pan', None) is not None
               or getattr(op, 'studio_espera', None))
    if area and not ocupado and sp.dentro(pixel, area):
        if event.type in {'WHEELUPMOUSE', 'WHEELDOWNMOUSE'}:
            p.rolar((-40 if event.type == 'WHEELUPMOUSE' else 40) * e)
            return True
        p.compor(v, area, medir_texto, e)
        if event.type == 'LEFTMOUSE' and event.value == 'PRESS':
            p.clicar(s, pixel)
            if v.erros:
                erro(s)
            return True
        if event.type == 'MOUSEMOVE':
            c, _ = p.alvo(pixel)
            p.hover = c['id'] if c else None
        return event.type in mouse - {'TIMER', 'MIDDLEMOUSE', 'TRACKPADPAN', 'TRACKPADZOOM'}
    if event.type == 'MOUSEMOVE':
        p.hover = None
    if event.type == 'LEFTMOUSE' and event.value == 'PRESS' and p.foco:
        p.soltar_foco(v)
    return False


def desenhar(context, s, view):
    v = s.v2
    escala = view.scale / 1000
    sh = draw.begin()
    draw.rect(sh, (0, 0, context.region.width, context.region.height), cor('paper'))
    for passo, nome in ((0.1, 'paredes-grade-fina'), (1, 'paredes-grade-metro')):
        xs, ys = view.grid_lines(passo)
        linhas = []
        for x in xs:
            linhas += [view.to_screen((x, view.to_world((0, 0))[1])), view.to_screen((x, view.to_world((0, view.rect[3]))[1]))]
        for y in ys:
            linhas += [view.to_screen((view.to_world((0, 0))[0], y)), view.to_screen((view.to_world((view.rect[2], 0))[0], y))]
        draw.lines(sh, linhas, cor(nome))
    for contorno in v.referencias():
        for a, b in zip(contorno, contorno[1:]):
            draw.lines(sh, draw.dashed(tela(view, a), tela(view, b)), cor('line-strong'))
    selecionadas = set(v.selecionadas)
    for p in v.paredes():
        for i, g in enumerate(geometria_da_parede(p)):
            t = p['segmentos'][i]
            marcada = t['id'] in selecionadas
            tinta = cor('orange') if marcada else cor('ink')
            if t['estado'] == 'oculto':
                tinta = cor('eye-off')
            if t['estado'] != 'oculto':
                preencher(sh, [tela(view, q) for q in g['linha'] + list(reversed(g['face']))], cor('orange-tint') if marcada else cor('cafe'))
            for linha in (g['linha'], g['face']):
                for a, b in zip(linha, linha[1:]):
                    a, b = tela(view, a), tela(view, b)
                    draw.lines(sh, draw.dashed(a, b) if t['estado'] == 'oculto' else [a, b], tinta)
            draw.lines(sh, [tela(view, g['linha'][0]), tela(view, g['face'][0]),
                            tela(view, g['linha'][-1]), tela(view, g['face'][-1])], tinta)
            q = tela(view, cota(p, i, escala))
            label = f"{t['comprimento']:.0f} mm"
            draw.text(q[0] - draw.text_width(label, 11) / 2, q[1] - 4, label, tinta, size=11)
            for a in v.documento['aberturas']:
                if a['segmento_id'] != t['id'] or t['estado'] == 'oculto':
                    continue
                vao = vao_da_abertura(a, t, g)
                if not vao:
                    continue
                simbolos = simbolo(a, vao, t['espessura'], t['sentido'])
                tinta_vao = cor('orange') if a['id'] == v.abertura else cor('teal')
                preencher(sh, [tela(view, q) for q in simbolos['recorte']], cor('paper'))
                draw.lines(sh, [tela(view, q) for par in simbolos['linhas'] for q in par], tinta_vao)
                for x, y in zip(simbolos['arco'], simbolos['arco'][1:]):
                    draw.lines(sh, draw.dashed(tela(view, x), tela(view, y), 3, 3), tinta_vao)
        for k, q in enumerate(pontos(p)):
            x, y = tela(view, q)
            tinta = cor('orange') if v.ponto == (p['id'], k) else cor('teal')
            draw.rect(sh, (x - 4, y - 4, 8, 8), tinta)
    if not v.desenhando:
        for nome, q in v.alcas(escala).items():
            x, y = tela(view, q)
            tinta = cor('orange')
            draw.rect(sh, (x - 9, y - 9, 18, 18), cor('paper'))
            draw.outline(sh, (x - 9, y - 9, 18, 18), tinta)
            if nome == 'dividir':
                draw.lines(sh, [(x - 5, y), (x + 5, y), (x, y - 5), (x, y + 5)], tinta)
            else:
                sinal = -1 if v.ancora == 'inicio' else 1
                draw.lines(sh, [(x - sinal * 5, y), (x + sinal * 5, y),
                                (x + sinal * 5, y), (x, y + 4),
                                (x + sinal * 5, y), (x, y - 4)], tinta)
    if not v.paredes() and not v.desenhando:
        cx, cy = view.rect[2] / 2, view.rect[3] / 2
        draw.lines(sh, [(cx - 17, cy), (cx + 17, cy), (cx, cy - 17), (cx, cy + 17)], cor('orange'))
        draw.text(cx - 110, cy - 46, 'Clique para começar a desenhar', cor('ink'))
        draw.text(cx - 140, cy - 68, 'Ou escolha um modelo no painel da parede', cor('muted'))
    if v.desenhando:
        try:
            comprimento = medir(v.texto) if v.texto else None
            previa = v.previa(mm(s), escala, comprimento)
            a, b = tela(view, v.inicio), tela(view, previa['fim'])
            angulo = math.radians(previa['angulo'])
            normal = (math.sin(angulo) * v.espessura, -math.cos(angulo) * v.espessura)
            aa = tela(view, (v.inicio[0] + normal[0], v.inicio[1] + normal[1]))
            bb = tela(view, (previa['fim'][0] + normal[0], previa['fim'][1] + normal[1]))
            preencher(sh, [a, b, bb, aa], cor('orange-tint'))
            draw.lines(sh, draw.dashed(a, b) + [aa, bb, a, aa, b, bb], cor('orange'))
            draw.rect(sh, (b[0] - 5, b[1] - 5, 10, 10), cor('teal'))
            label = f"{previa['comprimento']:.0f} mm · {previa['angulo']:.0f}°"
            draw.text(b[0] + 12, b[1] + 18, label, cor('orange-ink'))
            draw.text(b[0] + 12, b[1], previa['retorno'], cor('teal-ink'), size=11)
            if v.texto:
                draw.text(b[0] + 12, b[1] - 18, tr('{} | Enter confirma').format(v.texto), cor('ink'))
        except ValueError as exc:
            draw.text(14, 52, str(exc), cor('danger'))
    total = sum(t['comprimento'] for p in v.paredes() for t in p['segmentos']) / 1000
    fechadas = sum(p['fechada'] for p in v.paredes())
    draw.text(14, 14, tr('{} parede(s) · {:.2f} m de parede · {} contorno(s) fechado(s) · Clique seleciona; dois cliques dividem; arraste pontos ou arestas').format(len(v.paredes()), total, fechadas), cor('muted'), size=11)
    if v.texto and not v.desenhando:
        draw.text(14, 54, tr('Comprimento: {} mm | Enter confirma').format(v.texto), cor('orange-ink'))
    if s.error:
        draw.text(14, 34, s.error, cor('danger'))
    e = escala_ui()
    if not v.desenhando and v.paredes():
        draw.text(14 * e, view.rect[3] - 24 * e, sp.DICA_SELECAO, cor('muted'), size=TOKENS['tipografia']['subtitulo_px'] * e)
    desenhar_selecao(sh, s, view, e)
    desenhar_painel(sh, s, view, e)
    draw.end()


def tratar(op, context, event, s, view, pixel):
    from .studio_interacao import tratar as despachar
    desenhando = s.v2.desenhando
    try:
        resultado = despachar(op, event, s, view, pixel)
    except ValueError as exc:
        s.error = str(exc)
        return True
    if desenhando and not s.v2.desenhando and s.v2.paredes():
        view.fit(s.v2.bounds(), margin=0.15)
    elif s.v2.desenhando and s.v2.inicio:
        x, y = tela(view, s.v2.inicio)
        if (x < 40 or y < 40 or x > view.rect[2] - 40 or y > view.rect[3] - 40) and s.v2.paredes():
            view.fit(s.v2.bounds(), margin=0.15)
    if event.type == 'LEFTMOUSE' and s.v2.abertura:
        a = next((a for a in s.v2.documento['aberturas'] if a['id'] == s.v2.abertura), None)
        if a:
            campos = context.window_manager.btm_wall_studio
            for k in ('posicao', 'largura', 'altura', 'peitoril'):
                setattr(campos, 'abertura_' + k, a[k])
    return resultado

def _v():
    s = props.session()
    return s.v2 if s else None


def campo(chave, padrao=0):
    def get(_):
        v = _v()
        t = v.trecho()[2] if v else None
        return float(t.get(chave, padrao)) if t else float(padrao)
    def set_(_, valor):
        v = _v()
        if v and v.selecao:
            v.editar(**{('angulo' if chave == 'angulo_absoluto' else chave): valor})
            v.checkpoint()
            erro(props.session())
            props.session().redraw()
    return bpy.props.FloatProperty(name={'angulo_absoluto':'Direção (°)', 'flecha':'Arco (mm)',
        'comprimento':'Comprimento (mm)', 'espessura':'Espessura (mm)', 'pe_direito_inicial':'Altura inicial (mm)',
        'pe_direito_final':'Altura final (mm)', 'afastamento':'Afastamento (mm)'}[chave], get=get, set=set_, precision=1)


def medida_texto_get(_):
    return _v().texto if _v() else ''


def medida_texto_set(_, valor):
    if _v():
        _v().texto = valor


def material_itens(_, context):
    v = _v()
    return [('nenhum', 'Sem material', '')] + [(m['id'], m['nome'], '') for m in v.documento['materiais']] if v else []


def material_campo(face):
    chave = 'material_' + face + '_id'
    def get(_):
        v = _v()
        t = v.trecho()[2] if v else None
        ids = [x[0] for x in material_itens(None, None)]
        valor = t.get(chave) if t else None
        return ids.index(valor) if valor in ids else 0
    def set_(_, valor):
        v = _v()
        ids = [x[0] for x in material_itens(None, None)]
        v.tentar(pe.material_da_face(v.documento, v.selecao, 'interna' if face == 'interno' else 'externa',
                                    None if valor == 0 else ids[valor]))
        v.checkpoint()
        erro(props.session())
    return bpy.props.EnumProperty(name='Face interna' if face == 'interno' else 'Face externa', items=material_itens, get=get, set=set_)


def ponto_campo(eixo):
    def get(_):
        v = _v()
        if not v or not v.ponto:
            return 0.0
        p = next(p for p in v.paredes() if p['id'] == v.ponto[0])
        return float(pontos(p)[v.ponto[1]][eixo])
    def set_(_, valor):
        v = _v()
        if not v or not v.ponto:
            return
        p = next(p for p in v.paredes() if p['id'] == v.ponto[0])
        q = list(pontos(p)[v.ponto[1]])
        q[eixo] = valor
        v.tentar(pe.mover_vertice(v.documento, *v.ponto, dict(x=q[0], y=q[1])))
        v.checkpoint()
        erro(props.session())
        props.session().redraw()
    return bpy.props.FloatProperty(name='Posição X (mm)' if eixo == 0 else 'Posição Y (mm)', get=get, set=set_, precision=1)


def padrao_get(_):
    return float(_v().espessura) if _v() else 150.0


def padrao_set(_, valor):
    if _v():
        _v().espessura = valor


def divisao_get(_):
    return float(_v().divisao) if _v() else 0.0


def divisao_set(_, valor):
    if _v():
        _v().divisao = valor


def material_itens_lote(_, context):
    v = _v()
    return [('nenhum', 'vários', '')] + [(m['id'], m['nome'], '') for m in v.documento['materiais']] if v else []


def _lote():
    v = _v()
    if not v:
        return None, None
    p = sp.painel_de(v)
    p.preparar_lote(v)
    return v, p


def lote_texto(chave):
    def get(_):
        _v2, p = _lote()
        return sp.formatar(p.lote.get(chave, '')) if p else ''
    def set_(_, valor):
        v, p = _lote()
        if not p:
            return
        try:
            if valor.strip():
                sp.numero(valor)
            p.lote[chave] = valor.strip()
            props.session().error = ''
        except ValueError as exc:
            props.session().error = str(exc)
    return bpy.props.StringProperty(name='Espessura (mm)' if chave == 'espessura' else 'Altura (mm)', get=get, set=set_)


def lote_material(face):
    chave = 'material_' + face + '_id'
    def get(_):
        _v2, p = _lote()
        ids = [x[0] for x in material_itens_lote(None, None)]
        return ids.index(p.lote.get(chave)) if p and p.lote.get(chave) in ids else 0
    def set_(_, valor):
        _v2, p = _lote()
        if p:
            ids = [x[0] for x in material_itens_lote(None, None)]
            p.lote[chave] = '' if valor == 0 else ids[valor]
    return bpy.props.EnumProperty(name='Face interna' if face == 'interno' else 'Face externa', items=material_itens_lote,
                                  get=get, set=set_)


def lote_ocultar_get(_):
    _v2, p = _lote()
    return bool(p and p.lote.get('ocultar'))


def lote_ocultar_set(_, valor):
    _v2, p = _lote()
    if p:
        p.lote['ocultar'] = bool(valor)


class CamposStudio(bpy.types.PropertyGroup):
    lote_espessura: lote_texto('espessura')
    lote_altura: lote_texto('altura')
    lote_material_interno: lote_material('interno')
    lote_material_externo: lote_material('externo')
    lote_ocultar: bpy.props.BoolProperty(name='Ocultar selecionadas', get=lote_ocultar_get, set=lote_ocultar_set)
    ponto_x: ponto_campo(0)
    ponto_y: ponto_campo(1)
    padrao: bpy.props.FloatProperty(name='Espessura padrão (mm)', min=1, get=padrao_get, set=padrao_set)
    divisao: bpy.props.FloatProperty(name='Posição da divisão (mm)', get=divisao_get, set=divisao_set)
    comprimento: campo('comprimento')
    espessura: campo('espessura')
    angulo: campo('angulo_absoluto')
    arco: campo('flecha')
    altura: campo('pe_direito_inicial')
    altura_final: campo('pe_direito_final')
    afastamento: campo('afastamento')
    texto: bpy.props.StringProperty(name='Medida (mm)', get=medida_texto_get, set=medida_texto_set)
    modelo_largura: bpy.props.FloatProperty(name='Largura (mm)', default=4000, min=10)
    modelo_profundidade: bpy.props.FloatProperty(name='Profundidade (mm)', default=3000, min=10)
    abertura_posicao: bpy.props.FloatProperty(name='Posição (mm)', default=0)
    abertura_largura: bpy.props.FloatProperty(name='Largura (mm)', default=800, min=1)
    abertura_altura: bpy.props.FloatProperty(name='Altura (mm)', default=2100, min=1)
    abertura_peitoril: bpy.props.FloatProperty(name='Peitoril (mm)', default=0, min=0)
    material_interno: material_campo('interno')
    material_externo: material_campo('externo')


class AcaoStudio(bpy.types.Operator):
    bl_idname = 'caffmob.wall_studio_action'
    bl_label = 'Editar parede'
    bl_options = {'INTERNAL'}
    acao: bpy.props.StringProperty()
    valor: bpy.props.FloatProperty()
    alvo: bpy.props.StringProperty()

    def execute(self, context):
        s = props.session()
        if not s or not s.v2:
            return {'CANCELLED'}
        v, campos = s.v2, context.window_manager.btm_wall_studio
        try:
            if self.acao == 'iniciar':
                v.iniciar()
            elif self.acao in ('retangulo', 'L', 'U'):
                v.modelo(self.acao, campos.modelo_largura, campos.modelo_profundidade)
            elif self.acao == 'ambiente_atual':
                v.tentar(pe.ambiente_atual_na_prancheta(v.documento, v.original, v.pavimento_id, v.gerar_id, v.espessura))
                v.concluir()
            elif self.acao == 'fixar':
                p = v.previa(mm(s), s.view.scale / 1000 if s.view else 0.1, medir(v.texto or '1000'))
                v.fixar(p['fim'])
            elif self.acao == 'confirmar' and v.texto and v.selecao:
                v.editar(comprimento=medir(v.texto))
                v.texto = ''
            elif self.acao == 'fechar':
                v.fechar()
            elif self.acao == 'concluir':
                v.concluir()
            elif self.acao == 'continuar':
                v.continuar()
            elif self.acao == 'direcao':
                if v.desenhando:
                    v.direcao, v.direcao_travada = self.valor, True
                elif v.selecao:
                    v.editar(angulo=self.valor)
            elif self.acao == 'ortogonal':
                v.ortogonal = not v.ortogonal
            elif self.acao == 'dividir':
                v.dividir()
            elif self.acao == 'excluir' and len(v.selecionadas) > 1:
                v.pedir_exclusao()
            elif self.acao in ('excluir', 'confirmar_excluir'):
                v.excluir(self.acao == 'confirmar_excluir')
            elif self.acao in ('todas', 'pronto', 'lote_aplicar', 'confirmar_exclusao', 'cancelar_exclusao', 'alternar'):
                sp.executar(s, self.acao, self.alvo or None)
            elif self.acao == 'ocultar':
                _, _, t = v.trecho()
                v.tentar((pe.restaurar_trecho if t['estado'] == 'oculto' else pe.ocultar_trecho)(v.documento, v.selecao))
            elif self.acao in ('inicio', 'fim'):
                v.ancora = self.acao
            elif self.acao in ('interna', 'externa', 'eixo'):
                v.lado = self.acao
            elif self.acao == 'espessura':
                v.tentar(pe.aplicar_espessura_a_todas(v.documento, v.pavimento_id, v.espessura))
            elif self.acao in ('DOOR', 'WINDOW'):
                if v.abertura_nova(self.acao):
                    a = next(a for a in v.documento['aberturas'] if a['id'] == v.abertura)
                    for k in ('posicao', 'largura', 'altura', 'peitoril'):
                        setattr(campos, 'abertura_' + k, a[k])
            elif self.acao == 'editar_abertura':
                v.tentar(pe.editar_abertura(v.documento, v.abertura,
                    {k: getattr(campos, 'abertura_' + k) for k in ('posicao', 'largura', 'altura', 'peitoril')}))
            elif self.acao == 'desfazer':
                s.undo()
            elif self.acao == 'refazer':
                s.redo()
            erro(s)
            if self.acao in ('retangulo', 'L', 'U', 'ambiente_atual', 'concluir') and s.view and v.paredes():
                s.view.fit(v.bounds(), margin=0.15)
            v.checkpoint()
        except ValueError as exc:
            s.error = str(exc)
        s.redraw()
        return {'FINISHED'}


def botao(layout, texto, acao, valor=0, depress=False, icon='NONE', alvo=''):
    op = layout.operator('caffmob.wall_studio_action', text=tr(texto), depress=depress, icon=icon)
    op.acao, op.valor, op.alvo = acao, valor, alvo


def campo_texto(layout, dono, nome, dica):
    """Campo de texto com a dica "vários" quando o Blender aceita `placeholder` (5.x)."""
    try:
        layout.prop(dono, nome, placeholder=dica)
    except TypeError:
        layout.prop(dono, nome)


def painel_lote(layout, context, s):
    """Alternativa nativa do painel "N paredes" (T133): os mesmos campos e a mesma regra de "vários"."""
    v = s.v2
    c = context.window_manager.btm_wall_studio
    n = len(v.selecionadas)
    layout.label(text=tr('{} paredes selecionadas').format(n), icon='STICKY_UVS_LOC')
    campo_texto(layout, c, 'lote_espessura', tr('vários'))
    campo_texto(layout, c, 'lote_altura', tr('vários'))
    layout.prop(c, 'lote_material_interno')
    layout.prop(c, 'lote_material_externo')
    layout.prop(c, 'lote_ocultar')
    botao(layout, 'Aplicar às selecionadas', 'lote_aplicar', icon='CHECKMARK')
    botao(layout, 'Excluir selecionadas', 'excluir', icon='TRASH')


def lista_do_pavimento(layout, v):
    """Lista textual do pavimento, com as selecionadas marcadas (o leitor de tela do Studio)."""
    box = layout.box()
    box.label(text=tr('Paredes do pavimento'))
    selecionadas = set(v.selecionadas)
    for i, p in enumerate(v.paredes(), 1):
        for j, t in enumerate(p['segmentos'], 1):
            texto = tr('Parede {} · trecho {} · {} mm').format(i, j, round(t['comprimento']))
            botao(box, texto, 'alternar', depress=t['id'] in selecionadas,
                  icon='CHECKBOX_HLT' if t['id'] in selecionadas else 'CHECKBOX_DEHLT', alvo=t['id'])


def painel(layout, context, s):
    v = s.v2
    c = context.window_manager.btm_wall_studio
    layout.label(text='Parede · Studio')
    row = layout.row(align=True)
    botao(row, 'Desfazer', 'desfazer', icon='LOOP_BACK')
    botao(row, 'Refazer', 'refazer', icon='LOOP_FORWARDS')
    layout.operator('caffmob.wall_editor_fit', text='Enquadrar', icon='ZOOM_ALL')
    row = layout.row(align=True)
    botao(row, 'Desenhar', 'iniciar', icon='ADD')
    botao(row, 'Ortogonal', 'ortogonal', depress=v.ortogonal)
    layout.prop(c, 'padrao')
    layout.prop(c, 'modelo_largura')
    layout.prop(c, 'modelo_profundidade')
    row = layout.row(align=True)
    for acao, texto in (('retangulo', 'Retângulo'), ('L', 'Canto em L'), ('U', 'Em U')):
        botao(row, texto, acao)
    botao(layout, 'Ambiente atual', 'ambiente_atual')
    if v.desenhando:
        layout.prop(c, 'texto')
        botao(layout, 'Adicionar trecho', 'fixar')
        row = layout.row(align=True)
        botao(row, 'Fechar', 'fechar')
        botao(row, 'Concluir', 'concluir')
    row = layout.row(align=True)
    row.enabled = not v.desenhando and bool(v.paredes())
    botao(row, 'Selecionar todas', 'todas', icon='SELECT_SET')
    if v.multipla_toque:
        botao(row, 'Pronto', 'pronto')
    if v.anuncio and len(v.selecionadas) < 2:
        layout.label(text=tr('{} paredes selecionadas').format(len(v.selecionadas)))
    if v.confirmacao:
        box = layout.box()
        box.alert = True
        box.label(text=tr(sp.CONFIRMAR_LOTE).format(v.confirmacao['quantidade']), icon='ERROR')
        row = box.row(align=True)
        botao(row, 'Excluir', 'confirmar_exclusao', icon='TRASH')
        botao(row, 'Cancelar', 'cancelar_exclusao')
    p, i, t = v.trecho()
    if len(v.selecionadas) > 1:
        layout.separator()
        painel_lote(layout, context, s)
        t = None
    if t:
        layout.separator()
        layout.label(text='Trecho selecionado')
        if v.ponto:
            layout.prop(c, 'ponto_x')
            layout.prop(c, 'ponto_y')
        for chave in ('comprimento', 'angulo', 'arco', 'espessura', 'altura', 'altura_final', 'afastamento'):
            layout.prop(c, chave)
        row = layout.row(align=True)
        for lado in ('interna', 'externa', 'eixo'):
            botao(row, lado.capitalize(), lado, depress=v.lado == lado)
        row = layout.row(align=True)
        for ancora in ('inicio', 'fim'):
            botao(row, 'Âncora: ' + ('início' if ancora == 'inicio' else 'fim'), ancora, depress=v.ancora == ancora)
        layout.prop(c, 'material_interno')
        layout.prop(c, 'material_externo')
        botao(layout, 'Aplicar espessura a todas', 'espessura')
        layout.prop(c, 'divisao')
        botao(layout, 'Dividir neste ponto', 'dividir')
        botao(layout, 'Restaurar trecho' if t['estado'] == 'oculto' else 'Ocultar trecho', 'ocultar')
        botao(layout, 'Excluir ponto' if v.ponto else 'Excluir trecho', 'excluir', icon='TRASH')
        if not p['fechada'] and not v.desenhando:
            botao(layout, 'Continuar', 'continuar')
        layout.separator()
        layout.label(text='Portas e janelas')
        row = layout.row(align=True)
        botao(row, 'Porta', 'DOOR')
        botao(row, 'Janela', 'WINDOW')
        if v.abertura:
            for chave in ('posicao', 'largura', 'altura', 'peitoril'):
                layout.prop(c, 'abertura_' + chave)
            botao(layout, 'Atualizar abertura', 'editar_abertura')
            botao(layout, 'Excluir abertura', 'excluir')
    if v.desenhando or t:
        layout.label(text='Direção (°)')
        for linha in ((135, 90, 45), (180, None, 0), (225, 270, 315)):
            row = layout.row(align=True)
            row.scale_y = TOKENS['medidas']['editor_paredes_pad_pequeno'] / 20
            for a in linha:
                if a is None:
                    botao(row, 'OK', 'fixar' if v.desenhando else 'confirmar')
                else:
                    botao(row, str(a) + '°', 'direcao', a)
    if v.paredes():
        lista_do_pavimento(layout, v)
    layout.separator()
    layout.label(text=tr('{} parede(s) · {} trecho(s)').format(len(v.paredes()), sum(len(p['segmentos']) for p in v.paredes())))
    if s.error:
        layout.label(text=s.error, icon='ERROR')
        if not v.ponto and v.erros and all(e['codigo'] == 'CONFIRMAR_DEPENDENCIAS' for e in v.erros):
            botao(layout, 'Confirmar exclusão e dependentes', 'confirmar_excluir', icon='TRASH')
    row = layout.row(align=True)
    row.operator('caffmob.wall_editor_ok', text='Aplicar', icon='CHECKMARK')
    row.operator('caffmob.wall_editor_cancel', text='Cancelar', icon='CANCEL')


classes = (CamposStudio, AcaoStudio)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.WindowManager.btm_wall_studio = bpy.props.PointerProperty(type=CamposStudio)


def unregister():
    descarregar_fontes()
    del bpy.types.WindowManager.btm_wall_studio
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
