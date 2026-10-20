"""Painel da parede como o Studio (T128) e seleção múltipla (T133), sem bpy.

Um modelo só (`controles`) alimenta o desenho GPU, os cliques, a tabulação e os testes; o N-panel nativo lê e grava o
mesmo documento. A composição segue `PainelDeParedeStudio.tsx`, `PainelDeParedesEmLoteStudio.tsx` e
`studioArtefato.css` (`.studio-paredes-painel`): medidas e espaçamentos saem de `tokens_studio.py`.
"""
from ..caffmob.v2 import paredes_edicao as pe
from ..data import units
from ..data.i18n import N_
from .studio import pontos
from .tokens_studio import TOKENS

M, E, T = TOKENS['medidas'], TOKENS['espacamento'], TOKENS['tipografia']
PAD = ((135, 90, 45), (180, 'ok', 0), (225, 270, 315))
CONFIRMAR_LOTE = N_('Excluir {} parede(s) selecionada(s)? Aberturas serão removidas e vínculos serão soltos.')
DICA_SELECAO = N_('arraste no vazio para selecionar · botão do meio ou Espaço move a vista')


def numero(texto, zero=False, negativo=False):
    return units.parse_length(texto, 'MM', allow_zero=zero, allow_negative=negativo) * 1000


def formatar(valor):
    return f'{valor:g}' if isinstance(valor, (float, int)) and not isinstance(valor, bool) else str(valor or '')


def dentro(pixel, r):
    return r is not None and r[0] <= pixel[0] <= r[0] + r[2] and r[1] <= pixel[1] <= r[1] + r[3]


class PainelStudio:
    def __init__(self):
        self.scroll = 0
        self.foco = None
        self.texto = ''
        self.cursor = 0
        self.marcado = False
        self.menu = None
        self.hover = None
        self.mais = False
        self.lote = {}
        self._assinatura = None
        self.largura = 4000
        self.profundidade = 3000
        self.erro = ''
        self.composicao = []
        self.altura_conteudo = 0

    # Lote ------------------------------------------------------------------------------------------------------
    def preparar_lote(self, v):
        """Valores comuns às selecionadas; vazio quando são vários, como o Studio."""
        ss = [s for p in v.paredes() for s in p['segmentos'] if s['id'] in v.selecionadas]
        assinatura = repr((v.selecionadas, ss))
        if assinatura == self._assinatura:
            return
        self._assinatura = assinatura

        def comum(vs):
            return vs[0] if vs and all(x == vs[0] for x in vs) else ''
        self.lote = dict(espessura=comum([s['espessura'] for s in ss]),
                         altura=comum([s[k] for s in ss for k in ('pe_direito_inicial', 'pe_direito_final')]),
                         material_interno_id=comum([s.get('material_interno_id') or '' for s in ss]),
                         material_externo_id=comum([s.get('material_externo_id') or '' for s in ss]),
                         ocultar=False) if ss else {}

    def aplicar_lote(self, v):
        """Campo vazio não muda nada; uma entrada só no histórico (quem chama faz o checkpoint)."""
        self.preparar_lote(v)
        patch = {}
        for chave in ('espessura', 'altura'):
            if formatar(self.lote.get(chave, '')).strip():
                patch[chave] = numero(formatar(self.lote[chave]))
        for chave in ('material_interno_id', 'material_externo_id'):
            if self.lote.get(chave):
                patch[chave] = self.lote[chave]
        if self.lote.get('ocultar'):
            patch['ocultar'] = True
        ok = v.editar_lote(patch)
        if ok:
            self._assinatura = None
        return ok

    # Modelo ----------------------------------------------------------------------------------------------------
    def controles(self, v):
        """Ordem de leitura e tabulação; o GPU, o clique e os testes consomem o mesmo modelo."""
        self.preparar_lote(v)
        cs = []

        def item(tipo, id, rotulo, valor=None, **kwargs):
            cs.append(dict(tipo=tipo, id=id, rotulo=rotulo, valor=valor, **kwargs))

        def campo(id, rotulo, valor, unidade='mm', **kwargs):
            item('campo', id, rotulo, valor, unidade=unidade, **kwargs)

        def botao(id, rotulo, **kwargs):
            item('botao', id, rotulo, **kwargs)

        def titulo(rotulo, *args):
            item('titulo', 'titulo.' + rotulo, rotulo, args=args)

        n = len(v.selecionadas)
        sem = N_('vários') if n > 1 else N_('Sem material')
        materiais = [('', sem)] + [(m['id'], m['nome']) for m in v.documento['materiais']]
        botao('desfazer', N_('Desfazer'))
        botao('refazer', N_('Refazer'))
        botao('enquadrar', N_('Enquadrar'))
        botao('todas', N_('Selecionar todas'), desabilitado=v.desenhando or not v.paredes())
        if v.multipla_toque:
            botao('pronto', N_('Pronto'))
        if n > 1:
            titulo(N_('{} paredes selecionadas'), n)
            campo('lote.espessura', N_('Espessura'), self.lote['espessura'], placeholder=N_('vários'))
            campo('lote.altura', N_('Altura'), self.lote['altura'], placeholder=N_('vários'))
            item('escolha', 'lote.material_interno_id', N_('Face interna'), self.lote['material_interno_id'], opcoes=materiais)
            item('escolha', 'lote.material_externo_id', N_('Face externa'), self.lote['material_externo_id'], opcoes=materiais)
            botao('lote_ocultar', N_('Ocultar selecionadas'), ativo=self.lote['ocultar'])
            botao('lote_aplicar', N_('Aplicar às selecionadas'), primario=True)
            botao('excluir', N_('Excluir selecionadas'), perigo=True)
            return cs
        _, _, t = v.trecho()
        if t and not v.desenhando:
            titulo(N_('Trecho selecionado'))
            if v.ponto:
                p = next(p for p in v.paredes() if p['id'] == v.ponto[0])
                q = pontos(p)[v.ponto[1]]
                campo('ponto.0', N_('Posição X'), q[0], negativo=True, zero=True)
                campo('ponto.1', N_('Posição Y'), q[1], negativo=True, zero=True)
            campo('comprimento', N_('Comprimento'), t['comprimento'], grande=True)
            campo('espessura', N_('Espessura'), t['espessura'])
            campo('angulo', N_('Direção'), t['angulo_absoluto'], '°', zero=True, negativo=True)
            item('pad', 'pad', N_('Direções da parede'), t['angulo_absoluto'])
            item('segmentado', 'lado', N_('Lado da medida'), v.lado,
                 opcoes=[('interna', N_('Interna')), ('externa', N_('Externa')), ('eixo', N_('Pelo eixo'))])
            item('segmentado', 'ancora', N_('Ao mudar a medida, mover'), v.ancora,
                 opcoes=[('inicio', N_('o fim')), ('fim', N_('o início'))])
            item('escolha', 'material_interno_id', N_('Face interna'), t.get('material_interno_id') or '', opcoes=materiais)
            item('escolha', 'material_externo_id', N_('Face externa'), t.get('material_externo_id') or '', opcoes=materiais)
            titulo(N_('Portas e janelas'))
            botao('DOOR', N_('Porta'), desabilitado=t['estado'] == 'oculto')
            botao('WINDOW', N_('Janela'), desabilitado=t['estado'] == 'oculto')
            for a in v.documento['aberturas']:
                if a['segmento_id'] != t['id']:
                    continue
                titulo(N_('Porta') if a['tipo'] == 'DOOR' else N_('Janela'))
                for chave, rotulo in (('posicao', N_('Distância do início')), ('largura', N_('Largura')),
                                      ('altura', N_('Altura')), ('peitoril', N_('Peitoril'))):
                    campo('abertura.' + a['id'] + '.' + chave, rotulo, a[chave], zero=chave in ('posicao', 'peitoril'))
                botao('remover_abertura.' + a['id'], N_('Excluir abertura'), perigo=True)
            titulo(N_('Mais medidas'))
            botao('mais', N_('Esconder') if self.mais else N_('Mostrar'), ativo=self.mais)
            if self.mais:
                for chave, rotulo in (('pe_direito_inicial', N_('Altura inicial')), ('pe_direito_final', N_('Altura final')),
                                      ('flecha', N_('Flecha da curva')), ('afastamento', N_('Elevação relativa'))):
                    campo(chave, rotulo, t[chave], zero=chave in ('flecha', 'afastamento'), negativo=chave == 'flecha')
                item('segmentado', 'sentido', N_('Lado interno'), t['sentido'],
                     opcoes=[('LEFT', N_('Esquerda')), ('RIGHT', N_('Direita'))])
                campo('divisao', N_('Posição da divisão'), v.divisao)
                botao('dividir', N_('Dividir neste ponto'))
                botao('ocultar', N_('Restaurar trecho') if t['estado'] == 'oculto' else N_('Ocultar trecho'))
                botao('espessura_todas', N_('Aplicar espessura a todas'))
            botao('excluir', N_('Excluir ponto') if v.ponto else N_('Excluir parede'), perigo=True)
            if not v.trecho()[0]['fechada']:
                botao('continuar', N_('Continuar'))
            return cs
        titulo(N_('Desenhar paredes'))
        botao('iniciar', N_('Desenhar'), primario=not v.desenhando)
        botao('ortogonal', N_('Ortogonal'), ativo=v.ortogonal)
        campo('padrao', N_('Espessura padrão'), v.espessura)
        if v.desenhando:
            campo('texto', N_('Comprimento'), v.texto, grande=True)
            item('pad', 'pad', N_('Direções da parede'), v.direcao)
            botao('fechar', N_('Fechar'))
            botao('concluir', N_('Concluir'))
        titulo(N_('Modelos'))
        campo('modelo_largura', N_('Largura'), self.largura)
        campo('modelo_profundidade', N_('Profundidade'), self.profundidade)
        for id, rotulo in (('retangulo', N_('Retângulo')), ('L', N_('Canto em L')), ('U', N_('Em U')),
                           ('ambiente_atual', N_('Ambiente atual'))):
            botao(id, rotulo)
        return cs

    # Composição ------------------------------------------------------------------------------------------------
    def compor(self, v, area, medir, e=1.0):
        """Retângulos em pixels da região (y para cima). `medir(texto, tamanho, peso)` devolve a largura.

        Corpo rolável entre o cabeçalho e o rodapé fixos; só entra o que cabe inteiro (o Blender não recorta blf).
        """
        x0, y0, w, h = area
        pad, gap = E['painel'] * e, E['base'] * 1.5 * e
        campo_h, botao_h = (M['botao'] - E['base']) * e, (M['botao'] - E['campo']) * e
        rotulo_w = M['editor_paredes_rotulo'] * e
        cabecalho, rodape = 52 * e, (M['botao'] + 2 * E['grupo']) * e
        largura = w - 2 * pad
        corpo = (y0 + rodape, y0 + h - cabecalho)
        itens, y, linha = [], 0.0, None

        def por(c, altura, **partes):
            itens.append(dict(c=c, y=y, h=altura, **partes))

        for c in self.controles(v):
            if c['tipo'] == 'botao':
                bw = min(largura, medir(c['rotulo'], T['secao_px'] * e, 400) + 2 * E['campo'] * e + 2 * e)
                if linha is None or linha + bw > largura:
                    if linha is not None:
                        y += botao_h + gap
                    linha = 0.0
                itens.append(dict(c=c, y=y, h=botao_h, x=linha, w=bw))
                linha += bw + gap
                continue
            if linha is not None:
                y += botao_h + gap
                linha = None
            if c['tipo'] == 'titulo':
                y += (E['grupo'] + (2 if itens else 0)) * e
                por(c, T['secao_px'] * e + E['margem'] * e)
                y += T['secao_px'] * e + E['margem'] * e
            elif c['tipo'] in ('campo', 'escolha'):
                altura = (TOKENS['toque']['alvo_minimo_px'] * e) if c.get('grande') else campo_h
                por(c, altura)
                y += altura + gap
            elif c['tipo'] == 'segmentado':
                por(c, 18 * e + campo_h)
                y += 18 * e + campo_h + gap
            elif c['tipo'] == 'pad':
                celula = M['editor_paredes_pad_pequeno'] * e
                por(c, 18 * e + 3 * celula + 2 * gap)
                y += 18 * e + 3 * celula + 2 * gap + gap
        if linha is not None:
            y += botao_h + gap
        self.altura_conteudo = y
        self.scroll = max(0.0, min(self.scroll, max(0.0, y - (corpo[1] - corpo[0]))))
        saida = []
        for it in itens:
            c = it['c']
            topo = corpo[1] - it['y'] + self.scroll
            r = (x0 + pad + it.get('x', 0), topo - it['h'], it.get('w', largura), it['h'])
            if r[1] < corpo[0] - 0.5 or r[1] + r[3] > corpo[1] + 0.5:
                continue
            partes = []
            if c['tipo'] in ('campo', 'escolha'):
                caixa = (r[0] + rotulo_w + E['campo'] * e, r[1], r[2] - rotulo_w - E['campo'] * e
                         - (24 * e if c['tipo'] == 'campo' else 0), r[3])
                partes.append(('caixa', caixa))
            elif c['tipo'] == 'segmentado':
                n = len(c['opcoes'])
                base = (r[0], r[1], r[2], campo_h)
                partes.append(('fundo', base))
                iw = (r[2] - E['base'] * e * (n + 1)) / n
                for k, (valor, _) in enumerate(c['opcoes']):
                    partes.append((valor, (r[0] + E['base'] * e + k * (iw + E['base'] * e), r[1] + E['base'] * e,
                                           iw, campo_h - 2 * E['base'] * e)))
            elif c['tipo'] == 'pad':
                celula = M['editor_paredes_pad_pequeno'] * e
                cw = (r[2] - 2 * gap) / 3
                for i, fila in enumerate(PAD):
                    for j, angulo in enumerate(fila):
                        partes.append((angulo, (r[0] + j * (cw + gap), r[1] + (2 - i) * (celula + gap), cw, celula)))
            saida.append(dict(c=c, r=r, partes=partes))
        self.composicao = saida
        self.area = area
        self.cabecalho = (x0, y0 + h - cabecalho, w, cabecalho)
        self.rodape_rects = [(id, (x0 + pad + k * (largura - gap) / 2 + (gap * k), y0 + E['grupo'] * e,
                                   (largura - gap) / 2, M['botao'] * e))
                             for k, id in enumerate(('aplicar', 'cancelar'))]
        self.menu_rects = []
        if self.menu:
            alvo = next((it for it in saida if it['c']['id'] == self.menu['id']), None)
            if alvo:
                caixa = alvo['partes'][0][1]
                for k, (valor, rotulo) in enumerate(alvo['c']['opcoes']):
                    self.menu_rects.append((valor, rotulo, (caixa[0], caixa[1] - (k + 1) * botao_h, caixa[2], botao_h)))
        return saida

    def alvo(self, pixel):
        """(controle, parte) sob o ponteiro: menu aberto, rodapé e corpo, nessa ordem."""
        for valor, _, r in self.menu_rects:
            if dentro(pixel, r):
                return dict(tipo='menu', id=self.menu['id']), valor
        for id, r in getattr(self, 'rodape_rects', []):
            if dentro(pixel, r):
                return dict(tipo='botao', id=id), None
        for it in self.composicao:
            for nome, r in it['partes']:
                if nome not in ('caixa', 'fundo') and dentro(pixel, r):
                    return it['c'], nome
            if dentro(pixel, it['r']):
                return it['c'], None
        return None, None

    # Edição de campos ------------------------------------------------------------------------------------------
    def iniciar_campo(self, c):
        self.foco = c['id']
        self.texto = formatar(c['valor'])
        self.cursor = len(self.texto)
        self.marcado = True
        self.menu = c if c['tipo'] == 'escolha' else None
        self.erro = ''

    def soltar_foco(self, v):
        """Perder o foco grava o campo, como o `onBlur` do Studio; devolve False se o valor foi recusado."""
        if not self.foco:
            return True
        c = next((c for c in self.controles(v) if c['id'] == self.foco), None)
        if c and c['tipo'] == 'campo':
            return self.confirmar_campo(v, c)
        self.foco = self.menu = None
        return True

    def confirmar_campo(self, v, c):
        try:
            id = c['id']
            if id.startswith('lote.'):
                if self.texto.strip():
                    numero(self.texto)          # recusa já na digitação, como "Informe medidas positivas"
                self.lote[id[5:]] = self.texto.strip()
            elif id == 'texto':
                v.texto = self.texto
            else:
                valor = numero(self.texto, c.get('zero', False), c.get('negativo', False))
                if id == 'padrao':
                    v.espessura = valor
                elif id == 'modelo_largura':
                    self.largura = valor
                elif id == 'modelo_profundidade':
                    self.profundidade = valor
                elif id == 'divisao':
                    v.divisao = valor
                elif id.startswith('ponto.'):
                    p = next(p for p in v.paredes() if p['id'] == v.ponto[0])
                    q = list(pontos(p)[v.ponto[1]])
                    q[int(id[-1])] = valor
                    v.tentar(pe.mover_vertice(v.documento, *v.ponto, dict(x=q[0], y=q[1])))
                elif id.startswith('abertura.'):
                    _, aid, chave = id.split('.')
                    v.tentar(pe.editar_abertura(v.documento, aid, {chave: valor}))
                else:
                    v.editar(**{id: valor})
                if v.erros:
                    self.erro = '; '.join(e['mensagem'] for e in v.erros)
                    return False
                v.checkpoint()
            self.foco = self.menu = None
            self.erro = ''
            return True
        except ValueError as exc:
            self.erro = str(exc)
            return False

    def escolher(self, v, c, valor):
        id = c['id']
        if id.startswith('lote.'):
            self.lote[id[5:]] = valor
        elif id in ('lado', 'ancora'):
            setattr(v, id, valor)
        elif id == 'sentido':
            v.editar(sentido=valor)
        else:
            v.tentar(pe.material_da_face(v.documento, v.selecao, 'interna' if id == 'material_interno_id' else 'externa',
                                         valor or None))
        v.checkpoint()
        self.foco = self.menu = None

    def tecla(self, v, event):
        """Teclado do painel: Tab/Shift+Tab percorrem, Enter grava, Esc desiste, setas escolhem nas listas."""
        cs = [c for c in self.controles(v) if c['tipo'] in ('campo', 'escolha')]
        shift = getattr(event, 'shift', False)
        if event.type == 'TAB' and event.value == 'PRESS':
            c = next((c for c in cs if c['id'] == self.foco), None)
            indice = cs.index(c) if c else (-1 if not shift else 0)
            if c and c['tipo'] == 'campo' and not self.confirmar_campo(v, c):
                return True
            cs = [c for c in self.controles(v) if c['tipo'] in ('campo', 'escolha')]
            if cs:
                self.iniciar_campo(cs[(indice + (-1 if shift else 1)) % len(cs)])
            return True
        c = next((c for c in cs if c['id'] == self.foco), None)
        if not c:
            return False
        if event.value != 'PRESS':
            return event.type not in ('MOUSEMOVE', 'LEFTMOUSE', 'MIDDLEMOUSE', 'RIGHTMOUSE', 'TIMER')
        if event.type == 'ESC':
            self.foco = self.menu = None
            self.erro = ''
        elif c['tipo'] == 'escolha':
            if event.type in ('UP_ARROW', 'DOWN_ARROW', 'RET', 'NUMPAD_ENTER'):
                opcoes = [id for id, _ in c['opcoes']]
                atual = opcoes.index(c['valor']) if c['valor'] in opcoes else 0
                if event.type in ('RET', 'NUMPAD_ENTER'):
                    self.escolher(v, c, opcoes[atual])
                else:
                    self.escolher(v, c, opcoes[(atual + (1 if event.type == 'DOWN_ARROW' else -1)) % len(opcoes)])
                    self.iniciar_campo(next(x for x in self.controles(v) if x['id'] == c['id']))
            else:
                return event.type not in ('MOUSEMOVE', 'LEFTMOUSE', 'WHEELUPMOUSE', 'WHEELDOWNMOUSE', 'MIDDLEMOUSE', 'TIMER')
        elif event.type in ('RET', 'NUMPAD_ENTER'):
            self.confirmar_campo(v, c)
        elif event.type == 'A' and getattr(event, 'ctrl', False):
            self.marcado = True
        elif event.type in ('LEFT_ARROW', 'RIGHT_ARROW', 'HOME', 'END'):
            if event.type == 'HOME':
                self.cursor = 0
            elif event.type == 'END':
                self.cursor = len(self.texto)
            else:
                self.cursor = max(0, min(len(self.texto), self.cursor + (-1 if event.type == 'LEFT_ARROW' else 1)))
            self.marcado = False
        elif event.type in ('BACK_SPACE', 'DEL'):
            if self.marcado:
                self.texto, self.cursor = '', 0
            elif event.type == 'BACK_SPACE' and self.cursor:
                self.texto = self.texto[:self.cursor - 1] + self.texto[self.cursor:]
                self.cursor -= 1
            elif event.type == 'DEL':
                self.texto = self.texto[:self.cursor] + self.texto[self.cursor + 1:]
            self.marcado = False
        elif getattr(event, 'unicode', '') and not getattr(event, 'ctrl', False):
            if self.marcado:
                self.texto, self.cursor = '', 0
            self.texto = self.texto[:self.cursor] + event.unicode + self.texto[self.cursor:]
            self.cursor += len(event.unicode)
            self.marcado = False
        else:
            return event.type not in ('MOUSEMOVE', 'LEFTMOUSE', 'WHEELUPMOUSE', 'WHEELDOWNMOUSE', 'MIDDLEMOUSE', 'TIMER')
        return True

    def clicar(self, s, pixel):
        """Clique no painel: foca campo, abre lista, escolhe opção ou executa botão."""
        v = s.v2
        c, parte = self.alvo(pixel)
        if c is None:
            self.soltar_foco(v)
            return True
        if c['tipo'] == 'menu':
            alvo = next(x for x in self.controles(v) if x['id'] == c['id'])
            self.escolher(v, alvo, parte)
            return True
        if c['id'] == self.foco and c['tipo'] == 'campo':
            return True
        if not self.soltar_foco(v):
            return True
        if c['tipo'] in ('campo', 'escolha'):
            self.iniciar_campo(c)
        elif c['tipo'] == 'segmentado' and parte is not None:
            self.escolher(v, c, parte)
        elif c['tipo'] == 'pad' and parte == 'ok':
            executar(s, 'fixar' if v.desenhando else 'confirmar')
        elif c['tipo'] == 'pad' and parte is not None:
            executar(s, 'direcao', parte)
        elif c['tipo'] == 'botao' and not c.get('desabilitado'):
            executar(s, c['id'])
        return True

    def rolar(self, passo):
        self.scroll = max(0.0, self.scroll + passo)


def executar(s, acao, valor=None):
    """Ações do painel desenhado e da barra de toque, sem bpy. O N-panel usa as mesmas regras."""
    v = s.v2
    p = painel_de(v)
    v.erros = []
    s.error = ''
    if acao == 'iniciar':
        v.iniciar()
    elif acao in ('retangulo', 'L', 'U'):
        v.modelo(acao, p.largura, p.profundidade)
    elif acao == 'ambiente_atual':
        v.tentar(pe.ambiente_atual_na_prancheta(v.documento, v.original, v.pavimento_id, v.gerar_id, v.espessura))
        v.concluir()
    elif acao == 'fixar' and v.desenhando:
        comprimento = numero(v.texto or '1000')
        escala = s.view.scale / 1000 if getattr(s, 'view', None) else 0.1
        cursor = tuple(q * 1000 for q in s.cursor) if s.cursor else (0, 0)
        v.fixar(v.previa(cursor, escala, comprimento)['fim'])
    elif acao == 'confirmar':
        if v.texto and v.selecao:
            v.editar(comprimento=numero(v.texto))
            v.texto = ''
    elif acao == 'direcao':
        if v.desenhando:
            v.direcao, v.direcao_travada = valor, True
        elif v.selecao:
            v.editar(angulo=valor)
    elif acao == 'fechar':
        v.fechar()
    elif acao == 'concluir':
        v.concluir()
    elif acao == 'continuar':
        v.continuar()
    elif acao == 'ortogonal':
        v.ortogonal = not v.ortogonal
    elif acao == 'dividir':
        v.dividir()
    elif acao == 'excluir':
        if v.abertura and len(v.selecionadas) <= 1:
            v.excluir()
        else:
            v.pedir_exclusao()
    elif acao == 'confirmar_exclusao':
        v.confirmar_exclusao()
    elif acao == 'cancelar_exclusao':
        v.confirmacao = None
    elif acao == 'ocultar':
        _, _, t = v.trecho()
        v.tentar((pe.restaurar_trecho if t['estado'] == 'oculto' else pe.ocultar_trecho)(v.documento, v.selecao))
    elif acao == 'espessura_todas':
        v.tentar(pe.aplicar_espessura_a_todas(v.documento, v.pavimento_id, v.espessura))
    elif acao in ('DOOR', 'WINDOW'):
        v.abertura_nova(acao)
    elif acao.startswith('remover_abertura.'):
        v.tentar(pe.remover_abertura(v.documento, acao.split('.', 1)[1]))
        v.abertura = None
    elif acao == 'mais':
        p.mais = not p.mais
    elif acao == 'todas':
        if not v.desenhando:
            v.selecionar_todas()
    elif acao == 'pronto':
        v.multipla_toque = False
    elif acao == 'alternar':
        v.selecionar_ids([valor], 'alternar')
    elif acao == 'lote_ocultar':
        p.preparar_lote(v)
        p.lote['ocultar'] = not p.lote.get('ocultar')
    elif acao == 'lote_aplicar':
        p.aplicar_lote(v)
    elif acao == 'desfazer':
        s.undo()
    elif acao == 'refazer':
        s.redo()
    elif acao == 'enquadrar':
        if getattr(s, 'view', None):
            s.view.fit(v.bounds(), margin=0.15)
    elif acao == 'aplicar':
        s.request = 'ok'
    elif acao == 'cancelar':
        s.request = 'cancel'
    if v.erros:
        s.error = '; '.join(e['mensagem'] for e in v.erros)
    if acao in ('retangulo', 'L', 'U', 'ambiente_atual', 'concluir') and getattr(s, 'view', None) and v.paredes():
        s.view.fit(v.bounds(), margin=0.15)
    v.checkpoint()
    return True


def painel_de(v):
    if not hasattr(v, 'painel_studio'):
        v.painel_studio = PainelStudio()
    return v.painel_studio


def largura_painel(largura, escala=1):
    return min(M['editor_paredes_painel'] * escala, largura * 0.48)


def barra_toque(v, area, medir, e=1.0):
    """Barra "N paredes · Todas · Pronto" no topo da prancheta enquanto a seleção múltipla do toque está ligada."""
    if not v.multipla_toque:
        return []
    x0, y0, w, h = area
    alto = TOKENS['toque']['alvo_minimo_px'] * e
    bw = [medir(t, T['corpo_px'] * e, 600) + 2 * E['grupo'] * e for t in ('Todas', 'Pronto')]
    total = 140 * e + sum(bw)
    x = x0 + (w - total) / 2
    y = y0 + h - alto - E['grupo'] * e
    return [('barra', (x, y, total, alto)),
            ('todas', (x + 140 * e, y, bw[0], alto)),
            ('pronto', (x + 140 * e + bw[0], y, bw[1], alto))]


def dialogo(area, e=1.0):
    """Cartão de confirmação da exclusão em lote: (cartão, cancelar, excluir)."""
    x0, y0, w, h = area
    cw, ch = min(420 * e, w - 32 * e), 150 * e
    x, y = x0 + (w - cw) / 2, y0 + (h - ch) / 2
    bw, bh = 120 * e, M['botao'] * e
    return dict(cartao=(x, y, cw, ch),
                cancelar=(x + cw - 2 * bw - 2 * E['grupo'] * e, y + E['painel'] * e, bw, bh),
                confirmar_exclusao=(x + cw - bw - E['painel'] * e, y + E['painel'] * e, bw, bh))
