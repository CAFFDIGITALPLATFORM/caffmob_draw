"""Preview dividido da janela própria (feature 023, T005/T011; RF-02; feature 026).

Desenha no Image Editor da janela própria: elevação frontal (X × Z) e corte lateral (Y × Z), espelhando o mockup. As
peças saem de `build.pecas` — as mesmas que o Gerar cria —, então o preview mostra o armário de verdade: caixa,
divisórias, prateleiras, gavetas, portas, deslizantes e fundo, cada uma na cor do papel dela. Só o desenho usa
`gpu`/`blf` (import tardio, dentro das funções de render); o núcleo de cálculo é importável sem `bpy`.

O desenho ocupa só a largura visível da região: o painel lateral do Blender fica por cima à direita, e o corte lateral
era desenhado debaixo dele (achado A006 da auditoria). Cada peça desenhada entra em `hits`, que `selecao` usa para o
clique escolher a peça (A005).

As cores seguem o mockup de referência (paleta do Construtor de Armários CAFF MOB).
"""

import bpy  # type: ignore

from ..data.i18n import tr

# Paleta do mockup (conforme mockup_construtor_armarios.html)
COR_BG = (0.925, 0.933, 0.949, 1.0)         # #eceef2
COR_SURFACE = (1.0, 1.0, 1.0, 1.0)          # #ffffff
COR_ACCENT = (0.145, 0.388, 0.922, 1.0)     # #2563eb
COR_WOOD_FILL = (0.847, 0.722, 0.573, 1.0)  # #d8b892
COR_WOOD_STROKE = (0.537, 0.400, 0.263, 1.0)  # #8a6642
COR_WOOD_DARK = (0.722, 0.569, 0.412, 1.0)  # #b89166
COR_FRONT_FILL = (0.906, 0.812, 0.663, 1.0)  # #e7cfa9
COR_BACK_FILL = (0.894, 0.835, 0.765, 1.0)  # #e4d5c3
COR_GRID_LINE = (0.878, 0.898, 0.929, 1.0)  # #e0e5ed
COR_TEXTO = (0.122, 0.149, 0.188, 1.0)      # #1f2630
COR_MUTED = (0.373, 0.420, 0.478, 1.0)      # #5f6b7a
COR_FERRAGEM = (0.612, 0.639, 0.686, 1.0)   # #9ca3af
COR_SELECAO = (0.984, 0.749, 0.141, 1.0)    # #fbbf24

# Cor de cada papel de chapa no preview.
CORES = {
    'LATERAL': COR_WOOD_STROKE,
    'BASE_INF': COR_WOOD_STROKE,
    'BASE_SUP': COR_WOOD_STROKE,
    'DIVISORIA': COR_WOOD_DARK,
    'PRATELEIRA': COR_WOOD_FILL,
    'FUNDO': COR_BACK_FILL,
    'CONTRA_FRENTE': COR_WOOD_DARK,
    'PECA_TRAS': COR_WOOD_DARK,
    'FRENTE_GAVETA': COR_FRONT_FILL,
    'SEPARADOR': COR_WOOD_FILL,
    'AFASTADOR': COR_WOOD_FILL,
    'PORTA': COR_FRONT_FILL,
    'FOLHA': COR_FRONT_FILL,
}

ESPACO_DA_GRADE = 100.0     # linha de grade a cada 100 mm, como no mockup
PAPEIS_PORTA = ('PORTA', 'FOLHA')

# Ordem de pintura: o fundo é a peça mais ao fundo do armário e precisa ser desenhado primeiro; portas e frentes de
# gaveta ficam por cima de tudo. Sem isso o FUNDO cobre a vista inteira (achado da sonda de 2026-11-25).
PRIORIDADE = {'FUNDO': 0, 'PECA_TRAS': 1, 'LATERAL': 2, 'BASE_INF': 2, 'BASE_SUP': 2, 'CONTRA_FRENTE': 3,
              'DIVISORIA': 4, 'PRATELEIRA': 4, 'SEPARADOR': 5, 'AFASTADOR': 5, 'FRENTE_GAVETA': 6,
              'PORTA': 7, 'FOLHA': 7}


def estado_da_raiz(raiz):
    """(spec, peças) do armário da raiz; `(None, [])` sem raiz ou sem o grupo do armário."""
    if raiz is None or getattr(raiz, 'btm_armario', None) is None:
        return None, []
    from . import build
    from . import ops

    armario = raiz.btm_armario
    spec = ops.spec_do_armario(raiz)
    pecas = build.pecas(spec, ops.divisoes_do_armario(armario), ops.gavetas_do_armario(armario),
                        ops.internos_do_armario(armario))
    return spec, pecas


def tem_estrutura(spec):
    """Há alguma chapa da caixa ligada (o preview mostra o empty state quando não há)."""
    return bool(spec is not None and (spec.lateral_esq_ativa or spec.lateral_dir_ativa or spec.base_inf_ativa
                                      or spec.base_sup_ativa or spec.fundo_ativo))


def _retangulo(shader, x0, y0, x1, y1, cor):
    """Retângulo preenchido (a ordem dos cantos fecha o TRI_FAN)."""
    from gpu_extras.batch import batch_for_shader  # type: ignore

    coords = [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]
    batch = batch_for_shader(shader, 'TRI_FAN', {"pos": coords})
    shader.uniform_float("color", cor)
    batch.draw(shader)


def _contorno(shader, x0, y0, x1, y1, cor):
    """Contorno de um retângulo."""
    from gpu_extras.batch import batch_for_shader  # type: ignore

    coords = [(x0, y0), (x1, y0), (x1, y1), (x0, y1), (x0, y0)]
    batch = batch_for_shader(shader, 'LINE_STRIP', {"pos": coords})
    shader.uniform_float("color", cor)
    batch.draw(shader)


def _grade(shader, x0, y0, largura, altura, passo):
    """Grade de 100 mm por trás das peças, num lote só (um `draw` por vista)."""
    from gpu_extras.batch import batch_for_shader  # type: ignore

    coords = []
    x = passo
    while x < largura:
        coords.extend([(x0 + x, y0), (x0 + x, y0 + altura)])
        x += passo
    y = passo
    while y < altura:
        coords.extend([(x0, y0 + y), (x0 + largura, y0 + y)])
        y += passo
    if not coords:
        return
    batch = batch_for_shader(shader, 'LINES', {"pos": coords})
    shader.uniform_float("color", COR_GRID_LINE)
    batch.draw(shader)


def _vista(shader, pecas, caixa, eixo, deslocamento, escala, vista, chaves=()):
    """Fundo, grade e peças de uma vista; devolve os retângulos desenhados (para o clique escolher a peça)."""
    x0, y0, largura, altura = caixa
    _retangulo(shader, x0, y0, x0 + largura, y0 + altura, COR_SURFACE)
    _grade(shader, x0, y0, largura, altura, ESPACO_DA_GRADE * escala)
    hits = []
    for peca in pecas:
        (ax0, ay0, az0), (ax1, ay1, az1) = peca['box']
        # O X da peça é centrado no módulo (−largura/2 a +largura/2), então as duas vistas recebem o mesmo
        # deslocamento para caírem dentro do retângulo da vista.
        inicio, fim = (ax0 + deslocamento, ax1 + deslocamento) if eixo == 'x' else (ay0 + deslocamento,
                                                                                 ay1 + deslocamento)
        if fim - inicio <= 0.0 or az1 - az0 <= 0.0:
            continue
        cor = COR_FERRAGEM if peca.get('ferragem') else CORES.get(peca['papel'], COR_WOOD_FILL)
        px0, py0 = x0 + inicio * escala, y0 + az0 * escala
        px1, py1 = x0 + fim * escala, y0 + az1 * escala
        _retangulo(shader, px0, py0, px1, py1, cor)
        escolhida = (peca['nome'], vista) in chaves
        _contorno(shader, px0, py0, px1, py1, COR_SELECAO if escolhida else COR_WOOD_STROKE)
        hits.append({'nome': peca['nome'], 'papel': peca['papel'], 'ferragem': bool(peca.get('ferragem')),
                     'vista': vista, 'rect': (px0, py0, px1, py1)})
    _contorno(shader, x0, y0, x0 + largura, y0 + altura, COR_ACCENT)
    return hits


def _rotulo(texto, x, y, cor, tamanho=12):
    """Texto de 2D na posição pedida."""
    import blf  # type: ignore

    blf.size(0, tamanho)                 # blf.size(fontid, size) — sem argumento dpi (5.2)
    blf.position(0, x, y, 0.0)
    blf.color(0, *cor[:3], 1.0)
    blf.draw(0, texto)


def desenhar_preview(region, raiz, area=None, sessao=None):
    """Desenha o preview dividido (frontal + corte lateral) na região WINDOW da área."""
    if region is None or region.width <= 0 or region.height <= 0:
        return
    try:
        import gpu  # type: ignore
    except ImportError:
        return
    spec, pecas = estado_da_raiz(raiz)
    if spec is None:
        return

    if sessao is not None and not sessao.mostrar_portas:
        pecas = [p for p in pecas if p['papel'] not in PAPEIS_PORTA]
    pecas = sorted(pecas, key=lambda p: PRIORIDADE.get(p['papel'], 9))

    shader = gpu.shader.from_builtin('UNIFORM_COLOR')
    largura_area, altura_area = float(region.width), float(region.height)
    if area is not None:
        from ..canvas2d import window as canvas_window
        largura_area = canvas_window.visible_width(area, region)

    # Fundo do viewport, como o `.viewport-frame` do mockup.
    _retangulo(shader, 0.0, 0.0, float(region.width), altura_area, COR_BG)

    margem = 18.0
    meio = (largura_area - 3.0 * margem) / 2.0
    if meio <= 0.0:
        return
    util_altura = altura_area - 2.0 * margem
    selecionados = getattr(sessao, 'selecionados', ()) or ()
    chaves = {(item.get('nome'), item.get('vista')) for item in selecionados}
    if not chaves:
        unico = getattr(sessao, 'selecionado', None)
        chaves = {(unico.get('nome'), unico.get('vista'))} if unico else set()

    # ---- Elevação frontal (X × Z): o X da peça entra centrado na largura ----
    escala_f = min(meio / max(1.0, spec.largura), util_altura / max(1.0, spec.altura))
    largura_f, altura_f = spec.largura * escala_f, spec.altura * escala_f
    ox_f, oy_f = margem, altura_area - margem - altura_f
    hits = _vista(shader, pecas, (ox_f, oy_f, largura_f, altura_f), 'x', spec.largura / 2.0, escala_f,
                  'FRONTAL', chaves)
    _rotulo(tr("Frontal"), ox_f, oy_f + altura_f + 5.0, COR_ACCENT, 12)

    # ---- Corte lateral (Y × Z): Y da frente (−profundidade) para trás (0), a frente à esquerda ----
    escala_l = min(meio / max(1.0, spec.profundidade), util_altura / max(1.0, spec.altura))
    largura_l, altura_l = spec.profundidade * escala_l, spec.altura * escala_l
    ox_l, oy_l = largura_area - margem - largura_l, altura_area - margem - altura_l
    hits += _vista(shader, pecas, (ox_l, oy_l, largura_l, altura_l), 'y', spec.profundidade, escala_l,
                   'LATERAL', chaves)
    _rotulo(tr("Corte Lateral"), ox_l, oy_l + altura_l + 5.0, COR_ACCENT, 12)

    if sessao is not None:
        sessao.hits = hits
        if sessao.mostrar_cotas:
            _rotulo(tr("{} × {} mm").format(f"{spec.largura:g}", f"{spec.altura:g}"), ox_f, oy_f - 14.0,
                    COR_MUTED, 11)
            _rotulo(tr("{} mm").format(f"{spec.profundidade:g}"), ox_l, oy_l - 14.0, COR_MUTED, 11)

    # Empty state do mockup: nenhuma chapa da caixa ligada.
    if not tem_estrutura(spec):
        _rotulo(tr("Janela de Armário Vazia — ative as chapas na aba Estrutura"), ox_f + 8.0,
                oy_f + altura_f / 2.0, COR_MUTED, 12)
