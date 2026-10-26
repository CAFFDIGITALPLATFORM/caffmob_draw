"""Editor de Paredes clássico sobre a cena v2 do CAFF MOBI.

O projeto que veio do CAFF MOB abre no mesmo editor das paredes do addon: fundo escuro, face interna tracejada, as
ferramentas Selecionar/Mover, Construir Parede, Inverter Sentido e Adicionar/Remover Vértice, a lupa da barra superior
e os painéis nativos. Os campos mostram e aceitam a unidade do projeto, como no clássico.

Por baixo, o documento v2 continua a fonte da verdade: as regras são as de `studio.Prancheta` e de
`caffmob/v2/paredes_edicao` (os casos-ouro do Studio), então arcos, aberturas, materiais por face, trechos ocultos,
elevação e pavimentos vão e voltam sem perda. Este módulo é só a apresentação: desenho, ferramentas e painéis.
"""

import math
from types import SimpleNamespace

import bpy  # type: ignore
from gpu_extras.batch import batch_for_shader  # type: ignore
from mathutils import Vector  # type: ignore
from mathutils.geometry import tessellate_polygon  # type: ignore

from ..caffmob.geometria import geometria_da_parede, vao_da_abertura
from ..caffmob.v2 import paredes_edicao as pe
from ..canvas2d import draw
from ..canvas2d.view import snap_to_grid
from ..data import units
from ..data.i18n import N_, tr
from . import props
from . import studio_painel as sp
from .studio import arredondar, cota, pontos
from .studio_aberturas import simbolo

DICAS = {
    'SELECT': N_("Clique numa parede, porta ou janela; arraste vértices, arestas e aberturas; digite a medida e Enter. "
                 "Arraste no vazio para selecionar; Delete remove."),
    'DRAW': N_("Clique o ponto inicial, digite o comprimento e Enter (setas mudam a direção). Clique no início para "
               "fechar. Esc termina."),
    'INVERT': N_("Clique numa parede para inverter o lado da espessura."),
    'ADD_NODE': N_("Clique num trecho para dividi-lo no ponto clicado."),
    'REMOVE_NODE': N_("Clique num vértice para unir os trechos."),
}
NAVEGACAO = {'WHEELUPMOUSE', 'WHEELDOWNMOUSE', 'MIDDLEMOUSE', 'TRACKPADPAN', 'TRACKPADZOOM', 'TIMER'}


def _ed():
    from . import ops_editor      # o editor importa este módulo sob demanda; aqui, as cores e a barra dele
    return ops_editor


def _v():
    s = props.session()
    return s.v2 if s else None


def _unidade():
    return units.get_scene_length_unit(bpy.context.scene)


def digitado_mm(texto):
    """Medida digitada na planta, na unidade do projeto (como o clássico), em mm; None se vazia ou inválida."""
    if not texto:
        return None
    try:
        return units.parse_length(texto, _unidade(), allow_zero=False) * 1000
    except ValueError:
        return None


def erro(s):
    s.error = '; '.join(e['mensagem'] for e in s.v2.erros)


def tela(view, q):
    return view.to_screen((q[0] / 1000, q[1] / 1000))


def preencher(sh, ps, tinta):
    # `tessellate_polygon` devolve trincas de índices dos pontos, não os pontos.
    triangulos = tessellate_polygon([[Vector((q[0], q[1], 0)) for q in ps]])
    if triangulos:
        sh.bind()
        sh.uniform_float('color', tinta)
        batch_for_shader(sh, 'TRIS', {'pos': [tuple(ps[i][:2]) for t in triangulos for i in t]}).draw(sh)


def _polilinha(view, ps, tracejada=False):
    pares = []
    for a, b in zip(ps, ps[1:]):
        a, b = tela(view, a), tela(view, b)
        pares += draw.dashed(a, b) if tracejada else [a, b]
    return pares


# Desenho ------------------------------------------------------------------------------------------------------

def _seta_do_trecho(sh, view, g, cor_seta):
    """Sentido do trecho selecionado, como o clássico: seta no meio da face interna (a linha desenhada)."""
    a, b = g['trecho']
    meio = tela(view, ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2))
    d = math.atan2(b[1] - a[1], b[0] - a[0])
    ux, uy = math.cos(d), math.sin(d)
    ponta = (meio[0] + ux * 18, meio[1] + uy * 18)
    esq = (ponta[0] - ux * 8 - uy * 5, ponta[1] - uy * 8 + ux * 5)
    dir_ = (ponta[0] - ux * 8 + uy * 5, ponta[1] - uy * 8 - ux * 5)
    draw.lines(sh, [meio, ponta, ponta, esq, ponta, dir_], cor_seta)


def _pergunta(sh, region, linhas):
    ed = _ed()
    box, sim, nao = ed._prompt_rects(region)
    draw.rect(sh, box, draw.COLORS['panel'])
    draw.outline(sh, box, draw.COLORS['border'])
    for k, linha in enumerate(linhas[:2]):
        draw.text(box[0] + 16, box[1] + box[3] - 24 - 18 * k, linha)
    draw.button(sh, sim, "Sim", primary=True)
    draw.button(sh, nao, "Não")


def _texto_da_pergunta(v):
    texto = tr(sp.CONFIRMAR_LOTE).format(v.confirmacao['quantidade'])
    primeira, _, resto = texto.partition('? ')
    return [primeira + ('?' if resto else ''), resto] if resto else [texto]


def desenhar(context, s, view):
    ed = _ed()
    C = ed.COLORS
    v, region = s.v2, context.region
    v.sem_alcas = True                            # o clássico não tem as alças do Studio: o painel faz o mesmo
    state = context.window_manager.btm_wall_editor
    escala = view.scale / 1000
    sh = draw.begin()
    draw.rect(sh, (0, 0, region.width, region.height), C['background'])
    xs, ys = view.grid_lines(state.grid_size)
    grade = []
    for x in xs:
        grade += [view.to_screen((x, ys[0] if ys else 0)), view.to_screen((x, ys[-1] if ys else 0))]
    for y in ys:
        grade += [view.to_screen((xs[0] if xs else 0, y)), view.to_screen((xs[-1] if xs else 0, y))]
    draw.lines(sh, grade, C['grid'])

    referencia = []                       # módulos do pavimento: só para ver
    for contorno in v.referencias():
        for a, b in zip(contorno, contorno[1:]):
            referencia += draw.dashed(tela(view, a), tela(view, b))
    draw.lines(sh, referencia, C['reference'])

    selecionadas = set(v.selecionadas)
    uma = len(selecionadas) == 1
    for p in v.paredes():
        for i, g in enumerate(geometria_da_parede(p)):
            t = p['segmentos'][i]
            oculto = t['estado'] == 'oculto'
            marcada = t['id'] in selecionadas
            tinta = C['selected'] if marcada else (C['reference'] if oculto else C['wall'])
            # A linha desenhada é a face interna, tracejada (medida real); a espessura cresce para fora, com a face
            # externa e as pontas contínuas, como no clássico. Trecho oculto: tudo tracejado.
            pares = _polilinha(view, g['linha'], True) + _polilinha(view, g['face'], oculto)
            pares += [tela(view, g['linha'][0]), tela(view, g['face'][0]),
                      tela(view, g['linha'][-1]), tela(view, g['face'][-1])]
            draw.lines(sh, pares, tinta)
            if marcada and uma and not oculto:
                _seta_do_trecho(sh, view, g, C['selected'])
            q = tela(view, cota(p, i, escala))
            rotulo = draw.length_label(t['comprimento'] / 1000)
            draw.text(q[0] - draw.text_width(rotulo, 11) / 2, q[1] - 4, rotulo,
                      C['selected'] if marcada else draw.COLORS['muted'], size=11)
            for a in v.documento['aberturas']:
                if a['segmento_id'] != t['id'] or oculto:
                    continue
                vao = vao_da_abertura(a, t, g)
                if not vao:
                    continue
                simb = simbolo(a, vao, t['espessura'], t['sentido'])
                tinta_vao = C['selected'] if a['id'] == v.abertura else C['node']
                preencher(sh, [tela(view, q) for q in simb['recorte']], C['background'])
                draw.lines(sh, [tela(view, q) for par in simb['linhas'] for q in par], tinta_vao)
                draw.lines(sh, _polilinha(view, simb['arco'], True), tinta_vao)
        for k, q in enumerate(pontos(p)):
            x, y = tela(view, q)
            draw.rect(sh, (x - 4, y - 4, 8, 8), C['selected'] if v.ponto == (p['id'], k) else C['node'])

    r = v.retangulo
    if r and r['moveu'] and not r['toque']:
        a, b = tela(view, r['inicio']), tela(view, r['fim'])
        cantos = [(a[0], a[1]), (b[0], a[1]), (b[0], b[1]), (a[0], b[1])]
        toca = r['fim_pixel'][0] < r['pixel'][0]          # da direita para a esquerda: pega o que tocar
        pares = []
        for k in range(4):
            pares += draw.dashed(cantos[k], cantos[(k + 1) % 4], *((2, 3) if toca else (6, 4)))
        draw.lines(sh, pares, C['selected'])

    if s.cursor is not None and state.tool == 'DRAW' and not v.confirmacao and s.prompt not in ed.PROMPTS:
        p = view.to_screen(s.cursor)                       # mira em cruz do lápis
        draw.lines(sh, [(0, p[1]), (region.width, p[1]), (p[0], 0), (p[0], view.rect[3])], C['grid_axis'])

    if v.desenhando and v.inicio is not None and s.cursor is not None:
        medida = digitado_mm(v.texto)
        previa = v.previa(tuple(c * 1000 for c in s.cursor), escala, medida)
        a, b = tela(view, v.inicio), tela(view, previa['fim'])
        travada = medida is not None or previa['retorno'] != 'Snap de 15° e 10 mm'
        draw.lines(sh, [a, b] if travada else draw.dashed(a, b), C['preview_locked'] if travada else C['preview'])
        if previa['retorno'] == 'Primeiro ponto':          # ímã do ponto inicial: anel e "Fechar"
            anel = [(b[0] + 11 * math.cos(k * math.pi / 8), b[1] + 11 * math.sin(k * math.pi / 8)) for k in range(17)]
            draw.lines(sh, [q for k in range(16) for q in (anel[k], anel[k + 1])], C['selected'])
            draw.text(b[0] + 14, b[1] - 18, "Fechar", C['selected'])
        texto = f"{v.texto}▏" if v.texto else draw.length_label(previa['comprimento'] / 1000)
        draw.text(b[0] + 10, b[1] + 10, tr("Comprimento: {}").format(texto), C['preview'])
        draw.text(b[0] + 10, b[1] - 6, f"{previa['angulo']:.0f}° · {tr(previa['retorno'])}", draw.COLORS['muted'],
                  size=11)
        if v.direcao_travada:
            ed._draw_direction(sh, a, math.radians(v.direcao))
    elif v.texto and s.cursor is not None:                   # digitação direta no trecho selecionado
        q = view.to_screen(s.cursor)
        draw.text(q[0] + 12, q[1] + 12, tr("Medida: {}▏ (Enter aplica, Esc limpa)").format(v.texto), C['selected'])

    if not v.paredes() and not v.desenhando:
        cx, cy = view.rect[2] / 2, view.rect[3] / 2
        draw.text(cx - 120, cy, "Escolha Construir Parede e clique o ponto inicial", draw.COLORS['muted'])

    draw.text(12, 12, DICAS[state.tool], draw.COLORS['muted'])
    if s.error:
        draw.text(12, 32, s.error, draw.COLORS['warning'])
    ed._draw_toolbar(sh, view, s)
    if s.prompt in ed.PROMPTS:
        ed._draw_prompt(sh, region, ed.PROMPTS[s.prompt])
    elif v.confirmacao:
        _pergunta(sh, region, _texto_da_pergunta(v))
    draw.end()


# Eventos ------------------------------------------------------------------------------------------------------

def _regiao(context, view):
    from . import window
    region = window.editor_area(context)[2]
    if region is None:                            # sem janela (ensaios): a região é a vista mais a barra superior
        region = SimpleNamespace(width=view.rect[2], height=view.rect[3] + _ed().toolbar_height())
    return region


def capturar(op, context, event, s, view, pixel):
    """Perguntas abertas (descartar, excluir em lote) antes da navegação; devolve True quando consumiu o evento."""
    v = s.v2
    ed = _ed()
    if s.prompt != 'discard' and not v.confirmacao:
        return False
    region = _regiao(context, view)
    if event.type in NAVEGACAO or event.type in {'MOUSEMOVE', 'INBETWEEN_MOUSEMOVE'}:
        return event.type not in NAVEGACAO
    if event.value != 'PRESS':
        return True
    from ..hb_gpu_draw import point_in_rect
    _box, sim, nao = ed._prompt_rects(region)
    confirma = event.type in {'RET', 'NUMPAD_ENTER'} or (event.type == 'LEFTMOUSE' and point_in_rect(*pixel, sim))
    recusa = event.type == 'ESC' or (event.type == 'LEFTMOUSE' and point_in_rect(*pixel, nao))
    if s.prompt == 'discard':
        if confirma:
            s.prompt, s.request = None, 'cancel'
        elif recusa:
            s.prompt = None
    elif confirma:
        v.confirmar_exclusao()
        erro(s)
    elif recusa:
        v.confirmacao = None
    return True


def _inverter(v, hit):
    """Inverter Sentido: troca o lado da espessura de toda a parede clicada (a cadeia do clássico)."""
    id = hit.get('segmento', hit.get('id'))
    if hit['tipo'] == 'ponto':
        id = next(p for p in v.paredes() if p['id'] == hit['parede'])['segmentos'][0]['id']
    parede = next(p for p in v.paredes() if any(t['id'] == id for t in p['segmentos']))
    novo = 'RIGHT' if parede['segmentos'][0]['sentido'] == 'LEFT' else 'LEFT'
    documento = v.documento
    for t in parede['segmentos']:
        r = pe.editar_trecho(documento, t['id'], dict(ancora=v.ancora, lado_medida=v.lado, sentido=novo))
        if not r['ok']:
            return v.tentar(r)
        documento = r['valor']
    v.selecionar_ids([id])
    return v.tentar(dict(ok=True, valor=documento))


def _ferramenta(v, tool, hit):
    if hit is None:
        return
    if tool == 'INVERT' and hit['tipo'] in {'trecho', 'cota', 'ponto', 'abertura'}:
        _inverter(v, hit)
    elif tool == 'ADD_NODE' and hit['tipo'] in {'trecho', 'cota'}:
        v.selecionar(hit)
        v.divisao = v.trecho()[2]['comprimento'] * hit['fracao']
        v.dividir()
    elif tool == 'REMOVE_NODE' and hit['tipo'] == 'ponto':
        v.selecionar(hit)
        v.excluir()


def tratar(op, context, event, s, view, pixel):
    """Ferramentas do clássico antes do despacho do Studio (seleção, arraste, lápis em andamento e digitação)."""
    from . import studio_ui
    v = s.v2
    v.sem_alcas = True
    state = context.window_manager.btm_wall_editor
    if state.magnetic and s.cursor is not None:
        s.cursor = snap_to_grid(s.cursor, state.grid_size)
    alvo = tuple(c * 1000 for c in s.cursor) if s.cursor else (0, 0)
    press = event.value == 'PRESS'
    if event.type == 'ESC' and press and v.texto:
        v.texto = ''                              # Esc primeiro limpa a digitação, como o clássico
        return True
    ocupado = v.confirmacao or v.retangulo or op.dragging is not None or v.desenhando or v.selecao or v.ponto
    if event.type == 'ESC' and press and not ocupado:
        if s.dirty():
            s.prompt = 'discard'                  # pergunta antes de descartar (o Studio fechava direto)
        else:
            s.request = 'cancel'
        return True
    if event.type in {'RET', 'NUMPAD_ENTER'} and press and v.texto:
        medida = digitado_mm(v.texto)
        if medida is None:
            try:
                units.parse_length(v.texto, _unidade(), allow_zero=False)
            except ValueError as exc:
                s.error = str(exc)
            return True
        v.texto = repr(round(medida, 6))          # o despacho do Studio lê mm
    espaco = getattr(op, 'studio_espaco', False)
    if event.type == 'LEFTMOUSE' and press and not v.desenhando and not espaco:
        escala = view.scale / 1000
        if state.tool == 'DRAW' or (state.tool == 'SELECT' and not v.paredes()):
            v.iniciar(tuple(arredondar(c, 10) for c in alvo))          # o lápis começa onde se clica
            state.tool = 'DRAW'
            s.error = ''
            return True
        if state.tool in {'INVERT', 'ADD_NODE', 'REMOVE_NODE'}:
            s.error = ''
            _ferramenta(v, state.tool, v.hit(alvo, escala))
            erro(s)
            return True
    if state.tool in {'INVERT', 'ADD_NODE', 'REMOVE_NODE'} and event.type == 'LEFTMOUSE':
        return True
    desenhava = v.desenhando
    resultado = studio_ui.tratar(op, context, event, s, view, pixel)
    if desenhava and not v.desenhando:
        state.tool = 'SELECT'                     # parede concluída: volta a selecionar, como ao fechar no clássico
    return resultado


# Campos na unidade do projeto ---------------------------------------------------------------------------------

def _redesenhar(s):
    erro(s)
    s.redraw()


def _medida(nome, ler, gravar, negativa=False, zero=False):
    """Campo de texto como o do clássico: mostra e aceita a unidade do projeto (sem sufixo, vale a dela)."""
    def get(_self):
        valor = ler()
        return '' if valor is None else units.format_length(valor / 1000, unit=_unidade())

    def set_(_self, texto):
        s = props.session()
        if s is None or ler() is None:
            return
        try:
            mm = units.parse_length(texto, _unidade(), allow_negative=negativa, allow_zero=zero) * 1000
        except ValueError as exc:
            s.error = str(exc)
            s.redraw()
            return
        s.error = ''
        gravar(mm)
        s.v2.checkpoint()
        _redesenhar(s)
    return bpy.props.StringProperty(name=nome, get=get, set=set_)


def _trecho():
    v = _v()
    return v.trecho()[2] if v else None


def _do_trecho(chave):
    def ler():
        t = _trecho()
        return t[chave] if t else None

    def gravar(valor):
        _v().editar(**{chave: valor})
    return ler, gravar


def _abertura():
    v = _v()
    return next((a for a in v.documento['aberturas'] if a['id'] == v.abertura), None) if v and v.abertura else None


def _da_abertura(chave):
    def ler():
        a = _abertura()
        return a[chave] if a else None

    def gravar(valor):
        v = _v()
        v.tentar(pe.editar_abertura(v.documento, v.abertura, {chave: valor}))
    return ler, gravar


def _do_ponto(eixo):
    def ler():
        v = _v()
        if not v or not v.ponto:
            return None
        p = next(p for p in v.paredes() if p['id'] == v.ponto[0])
        return pontos(p)[v.ponto[1]][eixo]

    def gravar(valor):
        v = _v()
        p = next(p for p in v.paredes() if p['id'] == v.ponto[0])
        q = list(pontos(p)[v.ponto[1]])
        q[eixo] = valor
        v.tentar(pe.mover_vertice(v.documento, *v.ponto, dict(x=q[0], y=q[1])))
    return ler, gravar


def _do_documento(ler_v, gravar_v):
    def ler():
        v = _v()
        return ler_v(v) if v else None

    def gravar(valor):
        gravar_v(_v(), valor)
    return ler, gravar


def _campos_do_studio(chave):
    """Modelos: os campos do Studio em mm, mostrados na unidade do projeto."""
    def ler():
        return getattr(bpy.context.window_manager.btm_wall_studio, chave) if _v() else None

    def gravar(valor):
        setattr(bpy.context.window_manager.btm_wall_studio, chave, valor)
    return ler, gravar


def _angulo_get(_self):
    t = _trecho()
    return math.radians(t['angulo_absoluto']) if t else 0.0


def _angulo_set(_self, valor):
    v = _v()
    if v and v.selecao:
        v.editar(angulo=round(math.degrees(valor), 6))
        v.checkpoint()
        _redesenhar(props.session())


def _enum_do_trecho(chave, itens):
    def get(_self):
        t = _trecho()
        valores = [i[0] for i in itens]
        return valores.index(t[chave]) if t and t[chave] in valores else 0

    def set_(_self, indice):
        v = _v()
        if v and v.selecao:
            v.editar(**{chave: itens[indice][0]})
            v.checkpoint()
            _redesenhar(props.session())
    return get, set_


def _enum_da_prancheta(atributo, itens):
    def get(_self):
        v = _v()
        valores = [i[0] for i in itens]
        return valores.index(getattr(v, atributo)) if v and getattr(v, atributo) in valores else 0

    def set_(_self, indice):
        v = _v()
        if v:
            setattr(v, atributo, itens[indice][0])
    return get, set_


def _materiais(_self, _context):
    v = _v()
    return [('nenhum', tr('Sem material'), '')] + [(m['id'], m['nome'], '') for m in v.documento['materiais']] if v else []


def _material(face):
    chave = 'material_' + face + '_id'

    def get(_self):
        t = _trecho()
        ids = [x[0] for x in _materiais(None, None)]
        return ids.index(t.get(chave)) if t and t.get(chave) in ids else 0

    def set_(_self, indice):
        v = _v()
        if not v or not v.selecao:
            return
        ids = [x[0] for x in _materiais(None, None)]
        v.tentar(pe.material_da_face(v.documento, v.selecao, 'interna' if face == 'interno' else 'externa',
                                    None if indice == 0 else ids[indice]))
        v.checkpoint()
        _redesenhar(props.session())
    return bpy.props.EnumProperty(name=N_('Face interna') if face == 'interno' else N_('Face externa'),
                                  items=_materiais, get=get, set=set_)


LADOS = [('interna', N_("Interna"), N_("Medida pela face interna (tracejada)")),
         ('externa', N_("Externa"), N_("Medida pela face externa")),
         ('eixo', N_("Eixo"), N_("Medida pelo eixo da parede"))]
ANCORAS = [('inicio', N_("O fim"), N_("Ao mudar o comprimento, o fim do trecho se move")),
           ('fim', N_("O início"), N_("Ao mudar o comprimento, o início do trecho se move"))]
SENTIDOS = [('LEFT', N_("Esquerda"), N_("A espessura cresce para a esquerda da linha desenhada")),
            ('RIGHT', N_("Direita"), N_("A espessura cresce para a direita da linha desenhada"))]
TIPOS = [('NORMAL', N_("Normal"), ""), ('DIVISORIA', N_("Divisória"), ""), ('MURETA', N_("Mureta"), "")]


class BTM_PG_WallClassicV2(bpy.types.PropertyGroup):
    """Campos virtuais do editor clássico sobre a cena v2 (leem e gravam o documento da sessão)."""
    linha: bpy.props.EnumProperty(name=N_("Linha"), items=LADOS, get=_enum_da_prancheta('lado', LADOS)[0],
                                  set=_enum_da_prancheta('lado', LADOS)[1])  # type: ignore
    ancora: bpy.props.EnumProperty(name=N_("Ao mudar a medida, mover"), items=ANCORAS,
                                   get=_enum_da_prancheta('ancora', ANCORAS)[0],
                                   set=_enum_da_prancheta('ancora', ANCORAS)[1])  # type: ignore
    comprimento: _medida(N_("Comprimento"), *_do_trecho('comprimento'))  # type: ignore
    angulo: bpy.props.FloatProperty(name=N_("Ângulo Absoluto"), subtype='ANGLE', unit='ROTATION', precision=2,
                                    get=_angulo_get, set=_angulo_set)  # type: ignore
    flecha: _medida(N_("Flecha do Arco"), *_do_trecho('flecha'), negativa=True, zero=True)  # type: ignore
    espessura: _medida(N_("Espessura"), *_do_trecho('espessura'))  # type: ignore
    altura: _medida(N_("Pé-direito Inicial"), *_do_trecho('pe_direito_inicial'))  # type: ignore
    altura_final: _medida(N_("Pé-direito Final"), *_do_trecho('pe_direito_final'))  # type: ignore
    afastamento: _medida(N_("Elevação"), *_do_trecho('afastamento'), negativa=True, zero=True)  # type: ignore
    sentido: bpy.props.EnumProperty(name=N_("Direção"), items=SENTIDOS, get=_enum_do_trecho('sentido', SENTIDOS)[0],
                                    set=_enum_do_trecho('sentido', SENTIDOS)[1])  # type: ignore
    tipo: bpy.props.EnumProperty(name=N_("Tipo de Parede"), items=TIPOS, get=_enum_do_trecho('tipo', TIPOS)[0],
                                 set=_enum_do_trecho('tipo', TIPOS)[1])  # type: ignore
    material_interno: _material('interno')  # type: ignore
    material_externo: _material('externo')  # type: ignore
    ponto_x: _medida(N_("Posição X"), *_do_ponto(0), negativa=True, zero=True)  # type: ignore
    ponto_y: _medida(N_("Posição Y"), *_do_ponto(1), negativa=True, zero=True)  # type: ignore
    divisao: _medida(N_("Posição da divisão"), *_do_documento(lambda v: v.divisao if v.selecao else None,
                                                             lambda v, x: setattr(v, 'divisao', x)))  # type: ignore
    abertura_posicao: _medida(N_("Distância do início"), *_da_abertura('posicao'), zero=True)  # type: ignore
    abertura_largura: _medida(N_("Largura"), *_da_abertura('largura'))  # type: ignore
    abertura_altura: _medida(N_("Altura"), *_da_abertura('altura'))  # type: ignore
    abertura_peitoril: _medida(N_("Peitoril"), *_da_abertura('peitoril'), zero=True)  # type: ignore
    nova_espessura: _medida(N_("Espessura"), *_do_documento(lambda v: v.espessura,
                                                           lambda v, x: setattr(v, 'espessura', x)))  # type: ignore
    modelo_largura: _medida(N_("Largura"), *_campos_do_studio('modelo_largura'))  # type: ignore
    modelo_profundidade: _medida(N_("Profundidade"), *_campos_do_studio('modelo_profundidade'))  # type: ignore


class BTM_OT_WallClassicOpening(bpy.types.Operator):
    """Seleciona a porta ou janela do trecho para editar as medidas dela"""
    bl_idname = 'caffmob.wall_classic_opening'
    bl_label = 'Selecionar abertura'
    bl_options = {'INTERNAL'}
    abertura: bpy.props.StringProperty()  # type: ignore

    def execute(self, context):
        v = _v()
        if v is None:
            return {'CANCELLED'}
        v.abertura = self.abertura or None
        props.session().redraw()
        return {'FINISHED'}


# Painéis nativos ----------------------------------------------------------------------------------------------

def _acao(layout, texto, acao, icon='NONE', depress=False, alvo=''):
    from .studio_ui import botao
    botao(layout, texto, acao, icon=icon, depress=depress, alvo=alvo)


def _com_split(layout):
    layout.use_property_split = True
    layout.use_property_decorate = False
    return layout


def painel_ferramentas(layout, context, s):
    v = s.v2
    state = context.window_manager.btm_wall_editor
    col = layout.column(align=True)
    col.prop(state, "tool", expand=True)
    row = layout.row(align=True)
    _acao(row, N_('Ortogonal'), 'ortogonal', icon='SNAP_PERPENDICULAR', depress=v.ortogonal)
    row = row.row(align=True)
    row.enabled = not v.desenhando and bool(v.paredes())
    _acao(row, N_('Selecionar todas'), 'todas', icon='SELECT_SET')
    layout.operator("caffmob.wall_editor_fit", icon='ZOOM_ALL')
    if v.desenhando:
        row = layout.row(align=True)
        _acao(row, N_('Fechar'), 'fechar')
        _acao(row, N_('Concluir'), 'concluir')


def painel_trecho(layout, context, s):
    v = s.v2
    c = context.window_manager.btm_wall_classic
    p, _i, t = v.trecho()
    if len(v.selecionadas) > 1:
        from .studio_ui import painel_lote
        painel_lote(layout, context, s)
        return
    if t is None:
        layout.label(text="Selecione um trecho na planta.", icon='INFO')
        return
    _com_split(layout)
    if v.ponto:
        layout.prop(c, "ponto_x")
        layout.prop(c, "ponto_y")
        layout.separator()
    layout.prop(c, "linha")
    layout.prop(c, "comprimento")
    layout.prop(c, "angulo")
    layout.prop(c, "flecha")
    layout.prop(c, "espessura")
    layout.prop(c, "altura")
    layout.prop(c, "altura_final")
    layout.prop(c, "afastamento")
    layout.prop(c, "sentido", expand=True)
    layout.prop(c, "ancora", expand=True)
    layout.prop(c, "tipo")
    layout.prop(c, "material_interno")
    layout.prop(c, "material_externo")
    layout.separator()
    layout.prop(c, "divisao")
    col = layout.column(align=True)
    _acao(col, N_('Dividir neste ponto'), 'dividir', icon='ADD')
    _acao(col, N_('Restaurar trecho') if t['estado'] == 'oculto' else N_('Ocultar trecho'), 'ocultar',
          icon='HIDE_OFF' if t['estado'] == 'oculto' else 'HIDE_ON')
    if not p['fechada'] and not v.desenhando:
        _acao(col, N_('Continuar parede'), 'continuar', icon='GREASEPENCIL')
    _acao(col, N_('Aplicar espessura a todas'), 'espessura')
    if not v.abertura:                            # com a abertura marcada, "Excluir" fica no painel dela
        _acao(col, N_('Excluir vértice') if v.ponto else N_('Excluir trecho'), 'excluir', icon='TRASH')


def painel_aberturas(layout, context, s):
    v = s.v2
    c = context.window_manager.btm_wall_classic
    _p, _i, t = v.trecho()
    if t is None or len(v.selecionadas) > 1:
        layout.label(text="Selecione um trecho na planta.", icon='INFO')
        return
    row = layout.row(align=True)
    row.enabled = t['estado'] != 'oculto'
    _acao(row, N_('Porta'), 'DOOR', icon='ADD')
    _acao(row, N_('Janela'), 'WINDOW', icon='ADD')
    do_trecho = [a for a in v.documento['aberturas'] if a['segmento_id'] == t['id']]
    if not do_trecho:
        layout.label(text="Nenhuma porta ou janela neste trecho.")
        return
    col = layout.column(align=True)
    for k, a in enumerate(do_trecho, 1):
        nome = tr('Porta {}') if a['tipo'] == 'DOOR' else tr('Janela {}')
        op = col.operator('caffmob.wall_classic_opening', text=nome.format(k) + ' · ' + draw.length_label(a['largura'] / 1000),
                          depress=a['id'] == v.abertura, icon='MOD_BOOLEAN')
        op.abertura = a['id']
    if _abertura() is not None and _abertura()['segmento_id'] == t['id']:
        box = _com_split(layout.box())
        box.prop(c, "abertura_posicao")
        box.prop(c, "abertura_largura")
        box.prop(c, "abertura_altura")
        box.prop(c, "abertura_peitoril")
        _acao(box, N_('Excluir abertura'), 'excluir', icon='TRASH')


def painel_grade(layout, context, s):
    state = context.window_manager.btm_wall_editor
    c = context.window_manager.btm_wall_classic
    _com_split(layout)
    layout.prop(state, "grid_size")
    layout.prop(state, "magnetic")
    layout.separator()
    layout.label(text="Novas paredes")
    layout.prop(c, "nova_espessura")
    layout.separator()
    layout.label(text="Modelos")
    layout.prop(c, "modelo_largura")
    layout.prop(c, "modelo_profundidade")
    row = layout.row(align=True)
    for acao, texto in (('retangulo', N_('Retângulo')), ('L', N_('Canto em L')), ('U', N_('Em U'))):
        _acao(row, texto, acao)
    _acao(layout, N_('Ambiente atual'), 'ambiente_atual')


def painel_confirmar(layout, context, s):
    v = s.v2
    if s.error:
        layout.label(text=s.error, icon='ERROR')
        if not v.ponto and v.erros and all(e['codigo'] == 'CONFIRMAR_DEPENDENCIAS' for e in v.erros):
            _acao(layout, N_('Confirmar exclusão e dependentes'), 'confirmar_excluir', icon='TRASH')
    total = sum(t['comprimento'] for p in v.paredes() for t in p['segmentos']) / 1000
    layout.label(text=tr("{} parede(s) · {} de parede").format(len(v.paredes()), draw.length_label(total)))
    row = layout.row(align=True)
    row.scale_y = 1.4
    row.operator("caffmob.wall_editor_ok", text="OK", icon='CHECKMARK')
    row.operator("caffmob.wall_editor_cancel", text="Cancelar", icon='CANCEL')


classes = (BTM_PG_WallClassicV2, BTM_OT_WallClassicOpening)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.WindowManager.btm_wall_classic = bpy.props.PointerProperty(type=BTM_PG_WallClassicV2)


def unregister():
    del bpy.types.WindowManager.btm_wall_classic
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
