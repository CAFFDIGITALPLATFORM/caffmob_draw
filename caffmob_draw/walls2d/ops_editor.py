"""Editor de Paredes: desenho da planta, ferramentas e OK/Cancelar (T029; RN-15 a RN-17, RF-01 a RF-09).

- `caffmob.wall_editor`: lê as paredes do ambiente (rascunho), abre a janela do editor e inicia o modal.
- `caffmob.wall_editor_modal`: recebe os eventos da tela 2D:
  - Selecionar/Mover: clicar numa linha seleciona o trecho e a face (interna/externa); arrastar um vértice com prévia,
    trava ortogonal (±2,5°), grade magnética e "Bloquear Ângulo";
  - Construir Parede (lápis): clique no ponto inicial, digite o comprimento e Enter (ou clique), trava ortogonal,
    clique no ponto inicial pergunta se deve fechar;
  - Inverter Sentido, Adicionar Vértice e Remover Vértice por clique; Delete remove o trecho selecionado;
  - botão do meio arrasta a vista, a roda aproxima, Home enquadra tudo.
- Feature 013 (RN-01 a RN-07; D-04 a D-10): pinça no touchpad (`TRACKPADZOOM`) dá zoom ancorado no cursor e o
  arraste com dois dedos (`TRACKPADPAN`) move a vista, em qualquer ferramenta ou estado; a roda e o Ctrl + roda
  obedecem à preferência `PreferencesInput.invert_zoom_wheel`; a conta fica em `canvas2d/gestures.py` e a leitura do
  delta em `compat.trackpad_delta`. Barra superior desenhada em GPU com a lupa com quadrado (zoom janela): marcar um
  retângulo enquadra, Esc cancela só o modo. Navegar não refaz o encaixe da mira nem grava passo de desfazer.
- Feature 009 (RN-01 a RN-07): mira em cruz que trava por alinhamento X/Y com os vértices (8 px na tela; Shift
  desliga), cadeia única de travas (`resolve_point`), medida com conta (`data/expr.py`) e direção travada no lápis:
  o Enter segue a direção atual, que só muda por clique ou pelas setas do teclado.
- `caffmob.wall_editor_ok` / `caffmob.wall_editor_cancel`: o OK aplica o rascunho como um passo de desfazer (avisa antes se
  algum item não couber); Cancelar ou Esc descarta.
"""

import math

import bpy  # type: ignore

from .. import compat
from ..canvas2d import draw, gestures
from ..canvas2d.view import View2D, distance_point_point, distance_point_segment, ortho_snap, snap_to_grid
from ..data import expr, units
from ..data.i18n import N_, tr
from . import direction as dr
from . import cores, inference, medir, menu_contexto as mc, model, props, selecao_classica, tema, window

NODE_HIT_PX = 9
LINE_HIT_PX = 7
SNAP_CLOSE_PX = 15          # ímã do ponto inicial, em pixels de tela (D-33)
CLOSE_TOLERANCE = 0.01      # fim a até 10 mm do início conta como chegar nele (D-34)
ALIGN_PX = 8                # mira: alinhamento X/Y com os vértices a até 8 px na tela (009, RN-02)
TYPING_CHARS = "0123456789,.+-*/() "
UNIT_CHARS = "mMcC"         # sufixo de unidade: só depois de um dígito (009, R-05)
TIMER_STEP = 0.1
TOOLBAR_HEIGHT = 32         # barra superior da planta, em pixels a 100% (013, D-07); escala com `ui_scale`
NAVIGATION_EVENTS = {'TRACKPADZOOM', 'TRACKPADPAN', 'WHEELUPMOUSE', 'WHEELDOWNMOUSE', 'MIDDLEMOUSE'}   # 013, D-06

def _cores():
    """Paleta do tema escolhido no estado do editor (BUG-20261117-6OXN); fora do editor, a escura."""
    try:
        return tema.paleta(_state(bpy.context).tema)
    except AttributeError:
        return tema.ESCURO


def _tema_claro():
    """Se o editor está no tema claro, para as cores por tipo de parede."""
    return _cores() is tema.CLARO


class _PaletaViva:
    """Leitura de cor que segue o tema atual: `COLORS[...]` é o ponto único da paleta no desenho."""

    def __getitem__(self, chave):
        return _cores()[chave]


COLORS = _PaletaViva()      # medição entre dois pontos também usa esta paleta (BUG-20261117-V4I3)


def _state(context):
    return context.window_manager.btm_wall_editor


def _ui_scale():
    try:
        scale = float(bpy.context.preferences.system.ui_scale)
    except AttributeError:
        return 1.0
    return scale if scale > 0 else 1.0        # em segundo plano o Blender devolve 0


def _invert_zoom_wheel(context):
    """Preferência do Blender "inverter o zoom pela roda" (013, D-05; corpus `PreferencesInput.invert_zoom_wheel`)."""
    try:
        return bool(context.preferences.inputs.invert_zoom_wheel)
    except AttributeError:
        return False


def toolbar_height():
    """Altura da barra superior na tela, em pixels."""
    return TOOLBAR_HEIGHT * _ui_scale()


def _region_rect(region, area=None):
    """Retângulo da vista: a região menos o painel lateral e menos a barra superior, para que enquadrar, Home e a lupa
    não deixem paredes atrás da barra (013, D-08)."""
    width = window.visible_width(area, region) if area is not None else float(region.width)
    return (0.0, 0.0, width, max(1.0, float(region.height) - toolbar_height()))


def ensure_view(region, area=None):
    s = props.session()
    rect = _region_rect(region, area)
    if s.view is None:
        s.view = View2D(rect)
        s.view.fit(s.v2.bounds() if s.v2 else s.plan.bounds(), margin=0.15)
    else:
        s.view.rect = rect
    return s.view


# Desenho --------------------------------------------------------------------------------------------------

def vista_em_metros(s):
    """Retângulo da vista no mundo 2D, para a impressão sair com o enquadramento atual (BUG-20261117-744U)."""
    view = s.view
    if view is None:                              # sem janela (ensaios): tudo o que o rascunho tem
        return s.v2.bounds() if s.v2 else s.plan.bounds()
    x, y, w, h = view.rect
    return (view.to_world((x, y)), view.to_world((x + w, y + h)))


def draw_plan(context):
    s = props.session()
    region = context.region
    if s is None or region is None:
        return
    view = ensure_view(region, context.area)
    if s.v2:                              # cena do CAFF MOBI: o mesmo editor, sobre o documento v2
        from . import classico_v2
        classico_v2.desenhar(context, s, view)
        return
    state = _state(context)
    sh = draw.begin()
    draw.rect(sh, (0, 0, region.width, region.height), COLORS['background'])
    xs, ys = view.grid_lines(state.grid_size)
    grid = []
    for x in xs:
        grid += [view.to_screen((x, ys[0] if ys else 0)), view.to_screen((x, ys[-1] if ys else 0))]
    for y in ys:
        grid += [view.to_screen((xs[0] if xs else 0, y)), view.to_screen((xs[-1] if xs else 0, y))]
    draw.lines(sh, grid, COLORS['grid'])

    reference = []                        # paredes da camada nova: só para ver (D-05)
    for a, b in s.plan.references:
        reference += draw.dashed(view.to_screen(a), view.to_screen(b))
    if reference:
        draw.lines(sh, reference, COLORS['reference'])

    selected_chain, selected_index = s.segment()
    for ci, chain in enumerate(s.plan.chains):
        for i in range(chain.segment_count()):
            inner = chain.inner_line(i)
            outer = chain.outer_line(i)
            is_selected = chain is selected_chain and i == selected_index
            in_batch = (ci, i) in s.multi and len(s.multi) > 1          # 067 onda 8 (D-39)
            a0, a1 = view.to_screen(inner[0]), view.to_screen(inner[1])
            b0, b1 = view.to_screen(outer[0]), view.to_screen(outer[1])
            # Face interna tracejada (medida real), externa e pontas contínuas (D-28).
            cor = cores.cor(chain.segments[i].wall_type, claro=_tema_claro())   # cor por tipo (BUG-20261117-AKYJ)
            draw.lines(sh, draw.dashed(a0, a1) + [b0, b1, a0, b0, a1, b1],
                       COLORS['selected'] if in_batch else cor)
            if is_selected:
                line = chain.line(i, s.line)
                a, b = view.to_screen(line[0]), view.to_screen(line[1])
                draw.lines(sh, [a, b, (a[0], a[1] + 1), (b[0], b[1] + 1)], COLORS['selected'])
                _draw_arrow(sh, view, chain, i)
            mid = ((inner[0][0] + inner[1][0]) / 2, (inner[0][1] + inner[1][1]) / 2)
            p = view.to_screen(mid)
            label = draw.length_label(chain.face_length(i, s.line if is_selected else model.INNER))
            draw.text(p[0] + 4, p[1] + 4, label, COLORS['selected'] if is_selected else COLORS['muted'],
                      size=11)
        for k, node in enumerate(chain.nodes):
            q = view.to_screen(node)
            color = COLORS['selected'] if s.selected_node == (ci, k) else COLORS['node']
            draw.rect(sh, (q[0] - 4, q[1] - 4, 8, 8), color)

    # Planta baixa com objetos (BUG-20261117-JXDJ) -------------------------------
    if state.plant_low:
        from . import scene_io
        objs = scene_io.plant_objects(context.scene, state.cut_height)
        for o in objs:
            if not o['points']:
                continue
            pts = [view.to_screen(p) for p in o['points']]
            if len(pts) < 2:
                continue
            color = o['color'] if state.material_color_mode == 'SOLID' else COLORS['wall']
            # Fecha o polígono se não estiver fechado
            if pts[0] != pts[-1]:
                pts = pts + [pts[0]]
            draw.polygon(sh, pts, color)

    if s.drawing is None and s.typed and s.cursor is not None:      # digitação direta (D-27)
        q = view.to_screen(s.cursor)
        draw.text(q[0] + 12, q[1] + 12, tr("Medida: {}▏ {} (Enter aplica, Esc limpa)").format(
            s.typed, s.typed_preview), COLORS['selected'])

    if s.cursor is not None and state.tool in ('DRAW', 'SELECT') and s.prompt not in PROMPTS:
        _draw_crosshair(sh, view, region, s)

    if s.drawing is not None and s.cursor is not None and s.drawing.nodes:
        start = s.drawing.nodes[-1]
        end, kind = s.snap_point or (s.cursor, 'free')
        snapped = kind == 'close'
        locked = kind != 'free'
        typed_length = _typed_length(s)
        if typed_length is not None and s.direction is not None:      # com digitação, a prévia segue a direção (D-06)
            end, locked = dr.next_point(start, s.direction, typed_length), True
        a, b = view.to_screen(start), view.to_screen(end)
        draw.lines(sh, [a, b] if locked else draw.dashed(a, b), COLORS['preview_locked'] if locked
                   else COLORS['preview'])
        if snapped:                                    # ímã: anel no ponto inicial e "Fechar" (D-33)
            ring = [(b[0] + 11 * math.cos(t * math.pi / 8), b[1] + 11 * math.sin(t * math.pi / 8)) for t in range(17)]
            draw.lines(sh, [p for k in range(16) for p in (ring[k], ring[k + 1])], COLORS['selected'])
            draw.text(b[0] + 14, b[1] - 18, "Fechar", COLORS['selected'])
        length = math.hypot(end[0] - start[0], end[1] - start[1])
        text = f"{s.typed}▏ {s.typed_preview}".rstrip() if s.typed else draw.length_label(length)
        draw.text(b[0] + 10, b[1] + 10, tr("Comprimento: {}").format(text), COLORS['preview'])
        if s.direction_locked and s.direction is not None:          # direção atual no último ponto (RN-06)
            _draw_direction(sh, a, s.direction)

    hint = {'SELECT': N_("Clique numa face (interna tracejada / externa) ou num vértice e digite a medida + Enter; "
                         "arraste os vértices. Delete remove o trecho."),
            'DRAW': N_("Clique o ponto inicial, digite o comprimento e Enter. Clique no início para fechar. Esc termina."),
            'INVERT': N_("Clique numa parede para inverter o sentido."),
            'MOVE': N_("Selecione as paredes e arraste para mover; setas trocam a direção, digite a medida e Enter. "
                       "Esc cancela."),
            'MEASURE': N_("Clique o primeiro ponto e o segundo para medir a distância; Esc limpa a medição."),
            'ADD_NODE': N_("Clique num trecho para dividi-lo."),
            'REMOVE_NODE': N_("Clique num vértice para unir os trechos.")}[state.tool]
    if s.move_start is not None and s.cursor is not None:          # leitura do movimento (BUG-20261117-EELF)
        dx, dy = s.move_delta
        q = view.to_screen(s.cursor)
        medida = f"{s.typed}▏" if s.typed else draw.length_label(math.hypot(dx, dy))
        angulo = math.degrees(math.atan2(dy, dx)) % 360.0
        draw.text(q[0] + 14, q[1] + 14, tr("Mover: {}  {:.0f}°  (Esc cancela)").format(medida, angulo),
                  COLORS['preview'])
    draw.text(12, 12, hint, COLORS['muted'])
    if s.error:
        draw.text(12, 32, s.error, COLORS['warning'])
    if s.medir is not None:
        _draw_measure(sh, view, s.medir, s.cursor)      # ferramenta Medir (BUG-20261117-V4I3)
    _draw_toolbar(sh, view, s)
    if s.prompt in PROMPTS:
        _draw_prompt(sh, region, PROMPTS[s.prompt])
    if s.menu is not None:
        _draw_menu(sh, s.menu)                  # caixa de contexto por cima de tudo (BUG-20261117-AKYJ)
    draw.end()


def _draw_measure(sh, view, medicao, cursor=None):
    """Medição entre dois pontos: linha com pontas, medida no meio e a prévia até o cursor (BUG-20261117-V4I3).

    A medida sai com `draw.length_label`, a mesma formatação da planta, na unidade do projeto.
    """
    inicio = medicao['inicio']
    if inicio is None:
        return
    fim = medicao['fim'] or cursor
    if fim is None:
        return
    a, b = view.to_screen(inicio), view.to_screen(fim)
    cor = COLORS['measure']
    pronta = medicao['fim'] is not None
    draw.lines(sh, [a, b] if pronta else draw.dashed(a, b), cor)
    if pronta:                                          # pontas perpendiculares, como uma cota
        dx, dy = b[0] - a[0], b[1] - a[1]
        n = math.hypot(dx, dy) or 1.0
        px, py = -dy / n * 6.0, dx / n * 6.0
        draw.lines(sh, [(a[0] - px, a[1] - py), (a[0] + px, a[1] + py),
                        (b[0] - px, b[1] - py), (b[0] + px, b[1] + py)], cor)
    draw.rect(sh, (a[0] - 3, a[1] - 3, 6, 6), cor)
    metros = math.hypot(fim[0] - inicio[0], fim[1] - inicio[1])
    texto = draw.length_label(metros)
    draw.text((a[0] + b[0]) / 2 - draw.text_width(texto, 11) / 2, (a[1] + b[1]) / 2 + 10, texto, cor, size=11)


def _draw_menu(sh, caixa):
    """Caixa de contexto: fundo, borda e uma linha por controle, com marca do tipo atual (BUG-20261117-AKYJ)."""
    box = (caixa['x'], caixa['y'], caixa['largura'], caixa['altura'])
    draw.rect(sh, box, draw.COLORS['panel'])
    draw.outline(sh, box, draw.COLORS['border'])
    for (chave, r), item in zip(caixa['itens'], caixa.get('linhas', [])):
        tinta = draw.COLORS['text'] if item.get('marcado') or not item.get('cor') else draw.COLORS['muted']
        if item.get('cor'):
            draw.rect(sh, (r[0] + 6, r[1] + 7, 11, 11), item['cor'])
            if item.get('marcado'):
                draw.outline(sh, (r[0] + 4, r[1] + 5, 15, 15), draw.COLORS['text'])
        draw.text(r[0] + (22 if item.get('cor') else 8), r[1] + 6, item['rotulo'], tinta, size=11)
        if item.get('valor'):
            draw.text(r[0] + r[2] - draw.text_width(item['valor'], 11) - 8, r[1] + 6, item['valor'],
                      COLORS['selected'], size=11)


# Barra superior (013, RN-07, D-07) ----------------------------------------------------------------------------

ZOOM_WINDOW_HINT = N_("Zoom janela: marque um retângulo para enquadrar")
MOVE_LABEL = N_("Mover")          # botão da barra superior (BUG-20261117-EELF)
# Nome do editor na barra superior (BUG-20261117-6KBC): a barra do Windows é do Blender e usa o nome do tipo de área.
TITULO = N_("Editor de Paredes CAFF MOB DRAW")


def _toolbar_rects(view):
    """(faixa da barra, botão da lupa, botão Mover) em pixels da região; a barra fica logo acima da vista."""
    top, width, h = view.rect[3], view.rect[2], toolbar_height()
    side = h - 8
    lupa = (8.0, top + 4, side, side)
    mover = (lupa[0] + side + 6, top + 4, 74.0 * _ui_scale(), side)      # BUG-20261117-EELF
    return (0.0, top, width, h), lupa, mover


def _mouse_pixel(view, s):
    return view.to_screen(s.cursor) if s.cursor is not None else None


def _draw_magnifier(sh, r, color):
    """Lupa com quadrado desenhada em linhas: anel, cabo e o quadrado da janela dentro do anel."""
    x, y, w, h = r
    cx, cy, rad = x + w * 0.44, y + h * 0.56, min(w, h) * 0.26
    ring = [(cx + rad * math.cos(t * math.pi / 8), cy + rad * math.sin(t * math.pi / 8)) for t in range(17)]
    pts = [p for k in range(16) for p in (ring[k], ring[k + 1])]
    d = rad * math.cos(math.pi / 4)
    pts += [(cx + d, cy - d), (cx + d + rad * 0.95, cy - d - rad * 0.95)]          # cabo a 45°
    q = rad * 0.5
    pts += [(cx - q, cy - q), (cx + q, cy - q), (cx + q, cy - q), (cx + q, cy + q),
            (cx + q, cy + q), (cx - q, cy + q), (cx - q, cy + q), (cx - q, cy - q)]
    draw.lines(sh, pts, color)


def _draw_toolbar(sh, view, s):
    from ..hb_gpu_draw import point_in_rect
    bar, lupa, mover = _toolbar_rects(view)
    mouse = _mouse_pixel(view, s)
    hot = mouse is not None and point_in_rect(mouse[0], mouse[1], lupa)
    mover_hot = mouse is not None and point_in_rect(mouse[0], mouse[1], mover)
    armed = s.zoom_window is not None
    movendo = _state(bpy.context).tool == 'MOVE'        # BUG-20261117-EELF: o botão acende com a ferramenta ativa
    draw.rect(sh, bar, draw.COLORS['panel'])
    draw.lines(sh, [(bar[0], bar[1]), (bar[0] + bar[2], bar[1])], draw.COLORS['border'])
    draw.rect(sh, lupa, draw.COLORS['button_primary'] if armed else (draw.COLORS['button_hot'] if hot
                                                                     else draw.COLORS['button']))
    draw.outline(sh, lupa, draw.COLORS['border'])
    _draw_magnifier(sh, lupa, draw.COLORS['text'])
    draw.rect(sh, mover, draw.COLORS['button_primary'] if movendo else (draw.COLORS['button_hot'] if mover_hot
                                                                       else draw.COLORS['button']))
    draw.outline(sh, mover, draw.COLORS['border'])
    draw.text(mover[0] + 10, mover[1] + (mover[3] - draw.FONT_SIZE) / 2.0 + 1, MOVE_LABEL,
              draw.COLORS['text'] if movendo else draw.COLORS['muted'])
    titulo = tr(TITULO)                       # o nome do editor, à direita da barra (BUG-20261117-6KBC)
    draw.text(bar[0] + bar[2] - draw.text_width(titulo) - 12,
              bar[1] + (bar[3] - draw.FONT_SIZE) / 2.0 + 1, titulo, draw.COLORS['muted'])
    if hot or armed:                                   # dica ao passar o mouse e enquanto o modo está ligado
        draw.text(mover[0] + mover[2] + 10, bar[1] + (bar[3] - draw.FONT_SIZE) / 2.0 + 1, ZOOM_WINDOW_HINT,
                  draw.COLORS['text'] if armed else draw.COLORS['muted'])
    box = getattr(s, 'selection_box', None)                    # 067 onda 8 (D-39): retângulo de seleção
    if box is not None:
        (x0, y0), (x1, y1) = box
        corners = [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]
        draw.lines(sh, [p for k in range(4) for p in (corners[k], corners[(k + 1) % 4])], COLORS['selected'])
    if isinstance(s.zoom_window, tuple) and s.zoom_box_end is not None:     # retângulo elástico
        (x0, y0), (x1, y1) = s.zoom_window, s.zoom_box_end
        corners = [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]
        pts = []
        for k in range(4):
            pts += draw.dashed(corners[k], corners[(k + 1) % 4])
        draw.lines(sh, pts, COLORS['selected'])


def handle_zoom_window(event, s, view, pixel):
    """Barra superior e lupa com quadrado (013, RN-07, D-10). Devolve True quando consumiu o evento.

    Função de módulo, não método: as fumaças ligam ao modal falso só a lista de métodos que conhecem."""
    from ..hb_gpu_draw import point_in_rect
    bar, lupa, mover = _toolbar_rects(view)
    press = event.value == 'PRESS'
    if event.type == 'LEFTMOUSE' and press and point_in_rect(pixel[0], pixel[1], mover):
        state = _state(bpy.context)
        state.tool = 'SELECT' if state.tool == 'MOVE' else 'MOVE'   # botão Mover (BUG-20261117-EELF)
        return True
    if event.type == 'LEFTMOUSE' and press and point_in_rect(pixel[0], pixel[1], lupa):
        s.zoom_window = None if s.zoom_window is not None else 'ARMED'      # liga; segundo clique cancela
        s.zoom_box_end = None
        return True
    if event.type == 'LEFTMOUSE' and press and point_in_rect(pixel[0], pixel[1], bar):
        return True                                   # clique no resto da barra não chega às ferramentas
    # Soltar sobre a barra segue: conclui o arraste de vértice ou o retângulo da lupa (questions.md, pergunta 9).
    if s.zoom_window is None:
        return False
    if event.type == 'ESC' and press:                 # cancela só o modo: a vista e o desenho ficam como estão
        s.zoom_window, s.zoom_box_end = None, None
        return True
    if event.type == 'LEFTMOUSE' and press:
        s.zoom_window, s.zoom_box_end = pixel, pixel
        return True
    if isinstance(s.zoom_window, tuple):
        if event.type == 'MOUSEMOVE':
            s.zoom_box_end = pixel
            return True
        if event.type == 'LEFTMOUSE' and event.value == 'RELEASE':
            bounds = gestures.zoom_window_bounds(view, s.zoom_window, pixel)
            if bounds is not None:
                view.fit(bounds, margin=0)
            s.zoom_window, s.zoom_box_end = None, None
            return True
    return False


def _draw_crosshair(sh, view, region, s):
    """Mira em cruz (009, RN-01, D-03): linhas finas e neutras; o eixo travado em acento, com guia tracejada até a
    referência e um anel nela."""
    point = (s.snap_point or (s.cursor, 'free'))[0]
    p = view.to_screen(point)
    draw.lines(sh, [(0, p[1]), (region.width, p[1])], COLORS['selected'] if s.lock_y else COLORS['grid_axis'])
    draw.lines(sh, [(p[0], 0), (p[0], view.rect[3])], COLORS['selected'] if s.lock_x else COLORS['grid_axis'])
    for lock in (s.lock_x, s.lock_y):
        if lock is None:
            continue
        q = view.to_screen(lock[1])
        ring = [(q[0] + 7 * math.cos(t * math.pi / 8), q[1] + 7 * math.sin(t * math.pi / 8)) for t in range(17)]
        draw.lines(sh, draw.dashed(p, q) + [r for k in range(16) for r in (ring[k], ring[k + 1])], COLORS['selected'])


def _draw_direction(sh, origin, angle):
    """Seta e texto da direção atual no último ponto do lápis ("→ 0°")."""
    ux, uy = math.cos(angle), math.sin(angle)
    tip = (origin[0] + ux * 26, origin[1] + uy * 26)
    left = (tip[0] - ux * 8 - uy * 5, tip[1] - uy * 8 + ux * 5)
    right = (tip[0] - ux * 8 + uy * 5, tip[1] - uy * 8 - ux * 5)
    draw.lines(sh, [origin, tip, tip, left, tip, right], COLORS['selected'])
    draw.text(tip[0] + 6, tip[1] + 6, dr.label(angle), COLORS['selected'], size=11)


def _typed_length(s):
    """Comprimento da digitação atual em metros, ou None se vazio ou inválido."""
    if not s.typed:
        return None
    try:
        return units.parse_length(s.typed, units.get_scene_length_unit(), allow_zero=False)
    except ValueError:
        return None


def accept_typing(s, char):
    """Acrescenta um caractere à digitação se ele cabe numa medida com conta; devolve se aceitou."""
    if not char:
        return False
    if char in UNIT_CHARS and not any(ch.isdigit() for ch in s.typed):
        return False
    if char not in TYPING_CHARS and char not in UNIT_CHARS:
        return False
    if len(s.typed) >= expr.MAX_LENGTH:
        return False
    s.typed += char
    s.typed_preview = expr.preview(s.typed, units.get_scene_length_unit())
    return True


def _draw_arrow(sh, view, chain, i):
    (x0, y0), (x1, y1) = chain.inner_line(i)
    mid = view.to_screen(((x0 + x1) / 2, (y0 + y1) / 2))
    d = chain.direction(i)
    ux, uy = math.cos(d), math.sin(d)
    tip = (mid[0] + ux * 18, mid[1] + uy * 18)
    left = (tip[0] - ux * 8 - uy * 5, tip[1] - uy * 8 + ux * 5)
    right = (tip[0] - ux * 8 + uy * 5, tip[1] - uy * 8 - ux * 5)
    draw.lines(sh, [mid, tip, tip, left, tip, right], COLORS['selected'])


PROMPT_W, PROMPT_H = 380, 90
PROMPTS = {'close': N_("Deseja fechar a parede e finalizar a sua construção?"),
           'close_existing': N_("Deseja fechar a parede? O último ponto chegou ao início."),
           'discard': N_("Descartar as alterações e fechar o editor?")}


def _prompt_rects(region):
    x = (region.width - PROMPT_W) / 2
    y = (region.height - PROMPT_H) / 2
    return (x, y, PROMPT_W, PROMPT_H), (x + 60, y + 12, 100, 26), (x + 200, y + 12, 100, 26)


def _draw_prompt(sh, region, message):
    box, yes, no = _prompt_rects(region)
    draw.rect(sh, box, draw.COLORS['panel'])
    draw.outline(sh, box, draw.COLORS['border'])
    draw.text(box[0] + 16, box[1] + box[3] - 28, message)
    draw.button(sh, yes, "Sim", primary=True)
    draw.button(sh, no, "Não")


# Geometria da interação ----------------------------------------------------------------------------------------

def _index(s):
    """Índice do alinhamento, refeito só quando o plano muda (009, D-01)."""
    signature = model.plan_signature(s.plan)
    if s.inference_index is None or s.inference_signature != signature:
        s.inference_index = inference.Index(inference.plan_points(s.plan))
        s.inference_signature = signature
    return s.inference_index


def resolve_point(context, s, view, cursor, origin=None, shift=False, exclude=()):
    """Ponto travado do cursor, na ordem da RN-03 (009, D-02): ímã do início → vértice → alinhamento X/Y →
    trava ortogonal → grade. A trava ortogonal fixa um eixo e o alinhamento ainda pode fixar o outro (ponto pareado
    numa parede reta). Com Shift, o alinhamento sai da cadeia. Grava as travas da mira em `s.lock_x` e `s.lock_y`.
    Devolve (ponto, tipo da trava: 'close', 'node', 'align', 'ortho', 'grid' ou 'free')."""
    s.lock_x = s.lock_y = None
    pixel = view.to_screen(cursor)
    if s.drawing is not None and close_snap(s, view, pixel):
        return s.drawing.nodes[0], 'close'
    node = hit_node(s, pixel)
    if node is not None and s.plan.chains[node[0]].nodes[node[1]] not in exclude:
        return s.plan.chains[node[0]].nodes[node[1]], 'node'
    point, fixed = tuple(cursor), None
    if origin is not None:
        point, locked = ortho_snap(origin, cursor)
        if locked:
            fixed = 1 if abs(point[1] - origin[1]) < 1e-12 else 0      # eixo que a trava ortogonal fixou
    kind = 'ortho' if fixed is not None else 'free'
    if not shift:
        x, ref_x, y, ref_y = _index(s).query(cursor, ALIGN_PX / view.scale, exclude=exclude)
        point = list(point)
        if x is not None and fixed != 0:
            point[0], s.lock_x, kind = x, (x, ref_x), 'align'
        if y is not None and fixed != 1:
            point[1], s.lock_y, kind = y, (y, ref_y), 'align'
        point = tuple(point)
    if kind == 'free' and _state(context).magnetic:
        point, kind = snap_to_grid(point, _state(context).grid_size), 'grid'
    return point, kind


def hit_node(s, pixel):
    for ci, chain in enumerate(s.plan.chains):
        for k, node in enumerate(chain.nodes):
            if distance_point_point(pixel, s.view.to_screen(node)) <= NODE_HIT_PX:
                return ci, k
    return None


def close_snap(s, view, pixel):
    """O cursor está no ímã do ponto inicial do desenho a lápis (2+ trechos, até 15 px)?"""
    d = s.drawing
    return (d is not None and d.segment_count() >= 2
            and distance_point_point(pixel, view.to_screen(d.nodes[0])) <= SNAP_CLOSE_PX)


def hit_line(s, pixel):
    """(cadeia, trecho, linha) mais próximo do clique."""
    best = None
    for ci, chain in enumerate(s.plan.chains):
        for i in range(chain.segment_count()):
            for line, which in ((chain.inner_line(i), model.INNER), (chain.outer_line(i), model.OUTER)):
                dist = distance_point_segment(pixel, s.view.to_screen(line[0]), s.view.to_screen(line[1]))
                if dist <= LINE_HIT_PX and (best is None or dist < best[0]):
                    best = (dist, ci, i, which)
    return None if best is None else best[1:]


def remove_segment(s, ci, i):
    """Remove o trecho `i` da cadeia `ci` (abre o contorno ou divide a cadeia aberta)."""
    chain = s.plan.chains[ci]
    seg = chain.segments[i]
    if seg.source:
        s.plan.removed_sources.append(seg.source)
    s.selected = None
    n = len(chain.nodes)
    if chain.closed:
        order = [(i + 1 + k) % n for k in range(n)]
        nodes = [chain.nodes[k] for k in order]
        segments = [chain.segments[(i + 1 + k) % n] for k in range(n - 1)]
        s.plan.chains[ci] = model.Chain(nodes, segments, False, chain.side)
        return
    left = model.Chain(chain.nodes[:i + 1], chain.segments[:i], False, chain.side)
    right = model.Chain(chain.nodes[i + 1:], chain.segments[i + 1:], False, chain.side)
    parts = [c for c in (left, right) if c.segment_count() > 0]
    s.plan.chains[ci:ci + 1] = parts   # a primeira parede da direita fica solta no OK (aplicador)


def remove_node(s, ci, k):
    """Remove o nó `k` da cadeia `ci`; a parede do trecho eliminado sai da cena no OK (questions.md, pergunta 1)."""
    seg = s.plan.chains[ci].remove_node(k)
    if seg.source:
        s.plan.removed_sources.append(seg.source)
    s.selected = None


# Operadores -----------------------------------------------------------------------------------------------

class BTM_OT_WallEditor(bpy.types.Operator):
    """Abre o Editor de Paredes: planta 2D para desenhar e editar as paredes do ambiente"""
    bl_idname = "caffmob.wall_editor"
    bl_label = "Editar Paredes…"
    bl_options = {'REGISTER'}

    other_walls: bpy.props.EnumProperty(
        name="Paredes selecionadas de outra camada",
        items=[('CONVERT', "Converter para paredes editáveis",
                "Viram trechos editáveis; no OK, são trocadas por paredes do CAFFMob Draw 5"),
               ('REFERENCE', "Só referência", "Aparecem tracejadas na planta, sem edição")],
        default='CONVERT')  # type: ignore

    @classmethod
    def poll(cls, context):
        return not bpy.app.background and context.window is not None and props.session() is None

    def _other_layer(self, context):
        from . import scene_io, scene_v2
        if scene_v2.documento_da_cena(context) is not None:
            return []
        return [o for o in context.selected_objects if scene_io.is_other_layer_wall(o)]

    def invoke(self, context, event):
        if self._other_layer(context):
            return context.window_manager.invoke_props_dialog(self, title="Paredes de outra camada")
        return self.execute(context)

    def draw(self, context):
        layout = self.layout
        layout.label(text=tr("{} parede(s) selecionada(s) foram feitas com o construtor antigo.").format(
            len(self._other_layer(context))))
        layout.prop(self, "other_walls", expand=True)

    def execute(self, context):
        from . import scene_io, scene_v2
        try:
            v2_session = scene_v2.abrir(context)
        except (ValueError, TypeError) as exc:
            self.report({'ERROR'}, str(exc))
            return {'CANCELLED'}
        if v2_session is not None:
            try:
                win, area, region = window.open_editor(context)
            except RuntimeError as exc:
                props.end()
                self.report({'ERROR'}, str(exc))
                return {'CANCELLED'}
            with context.temp_override(window=win, area=area, region=region):
                bpy.ops.caffmob.wall_editor_modal('INVOKE_DEFAULT')
            return {'FINISHED'}
        plan = scene_io.read_plan(context.scene)
        others = self._other_layer(context)
        if others and self.other_walls == 'CONVERT':
            skipped = scene_io.convert_into(plan, others, context.scene)
            if skipped:
                self.report({'WARNING'}, tr("Sem dados de trechos, ficam como referência: {}").format(", ".join(skipped)))
        session = props.start(plan, context.scene.name)
        from ..measure import scene_cotas
        session.project_height = scene_cotas.ceiling_height(context.scene)
        context.window_manager.btm_wall_editor.new_height = session.project_height   # pé-direito do projeto (D-36)
        settings = getattr(context.scene, 'btm_settings', None)
        if settings is not None and hasattr(context.window_manager.btm_wall_editor, 'new_thickness'):
            context.window_manager.btm_wall_editor.new_thickness = settings.default_wall_thickness
        try:
            win, area, region = window.open_editor(context)
        except RuntimeError as exc:
            props.end()
            self.report({'ERROR'}, str(exc))
            return {'CANCELLED'}
        if plan.chains:
            first = plan.chains[0]
            props.session().selected = (0, 0) if first.segment_count() else None
        with context.temp_override(window=win, area=area, region=region):
            bpy.ops.caffmob.wall_editor_modal('INVOKE_DEFAULT')
        return {'FINISHED'}


class BTM_OT_WallEditorModal(bpy.types.Operator):
    """Interação da planta do Editor de Paredes"""
    bl_idname = "caffmob.wall_editor_modal"
    bl_label = "Editor de Paredes"
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    _timer = None

    def invoke(self, context, event):
        if props.session() is None:
            return {'CANCELLED'}
        self.dragging = None
        self.panning = None
        self.box = None                   # 067 onda 8 (D-39): retângulo de seleção (início, somar, seleção de antes)
        self.tab_ready = False
        self._timer = context.window_manager.event_timer_add(TIMER_STEP, window=context.window)
        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}

    def _end(self, context, apply_changes):
        s = props.session()
        report = None
        if s is not None and apply_changes and s.v2:
            from . import scene_v2
            scene_v2.aplicar(context, s)
            report = dict(created=[], updated=[p['id'] for p in s.v2.documento['paredes']], removed=[])
        elif s is not None and apply_changes:
            from . import apply
            report = apply.apply_plan(context, s.plan, remove_modules=s.remove_modules,
                                      project_height=s.project_height if s.equalize_height else None)
        if self._timer is not None:
            context.window_manager.event_timer_remove(self._timer)
            self._timer = None
        if s is not None:
            # Fecha a janela depois que o modal terminar (não fechar a janela onde o modal está rodando).
            window.close_later(s.window_ptr, s.area_ptr, s.restore_area_type)
            props.end()
        return report

    def cancel(self, context):
        self._end(context, False)

    def _local(self, context, event):
        _win, area, region = window.editor_area(context)
        if region is None:
            return None, None
        if self.dragging is None and self.panning is None and window.over_side_panel(area, event.mouse_x,
                                                                                     event.mouse_y):
            return None, None             # painel lateral: os botões e campos recebem o evento
        return region, (event.mouse_x - region.x, event.mouse_y - region.y)

    def modal(self, context, event):
        s = props.session()
        if s is None:
            self._end(context, False)
            return {'CANCELLED'}
        if s.request == 'ok':
            try:
                report = self._end(context, True)
            except Exception as exc:
                s.request, s.error = None, str(exc)
                self.report({'ERROR'}, s.error)
                s.redraw()
                return {'RUNNING_MODAL'}
            closed = tr(", {} sala(s) fechada(s) no OK").format(report['closed']) if report.get('closed') else ""
            self.report({'INFO'}, tr("Paredes aplicadas: {} nova(s), {} atualizada(s), {} removida(s){}.").format(
                len(report['created']), len(report['updated']), len(report['removed']), closed))
            if report.get('opening_errors'):
                self.report({'WARNING'}, tr("Não foi possível montar a porta ou janela real de: {}").format(
                    ", ".join(report['opening_errors'])))
            return {'FINISHED'}
        if s.request == 'cancel':
            self._end(context, False)
            return {'CANCELLED'}
        if event.type == 'TIMER':
            if not self.tab_ready:
                _win, area, _region = window.editor_area(context)
                self.tab_ready = window.focus_editor_tab(area)
            if s.v2 and getattr(self, 'studio_espera', None):
                from .studio_interacao import segurar      # 065 T133: segurar 450 ms no toque ou na caneta
                if segurar(self, s.v2):
                    s.redraw()
            return {'PASS_THROUGH'}
        if self._handle_undo(event, s):
            return {'RUNNING_MODAL'}          # Ctrl+Z fica com o rascunho: não vai para o desfazer do 3D
        region, pixel = self._local(context, event)
        if region is None:
            return {'PASS_THROUGH'}
        inside = 0 <= pixel[0] <= region.width and 0 <= pixel[1] <= region.height
        if not inside and self.dragging is None and self.panning is None:
            return {'PASS_THROUGH'}       # painéis laterais e cabeçalho
        _win, area, _region = window.editor_area(context)
        view = ensure_view(region, area)
        s.cursor = view.to_world(pixel)
        self.shift = event.shift
        if not self._is_navigation(event):
            self._update_snap(context, s, view)   # navegar não refaz o encaixe: o touchpad manda dezenas de eventos
        handled = self._handle(context, event, s, view, pixel)
        if handled and self.dragging is None and s.move_start is None:
            s.checkpoint()                    # um passo por ação concluída; o arraste e o movimento gravam ao soltar
        s.redraw()
        return {'RUNNING_MODAL'} if handled else {'PASS_THROUGH'}

    # Caixa de contexto da parede (BUG-20261117-AKYJ) --------------------------------------------------------
    def _handle_menu(self, state, event, s, view, pixel):
        """Caixa aberta: clique executa, Esc e um segundo botão direito fecham; fechada, o botão direito abre."""
        if s.menu is None:
            if not mc.abre_menu(state.tool, event.type, event.value):
                return False
            return self._open_menu(s, view, pixel)
        if event.value == 'PRESS' and event.type in {'ESC', 'RIGHTMOUSE'}:
            s.menu = None
            return True
        if event.type == 'LEFTMOUSE' and event.value == 'PRESS':
            chave = mc.alvo(s.menu, pixel)
            s.error = ""
            if chave is None:
                s.menu = None                     # clique fora fecha sem alterar nada
            else:
                self._menu_action(s, chave)
            return True
        return True                    # com a caixa aberta nada mais passa: nem navegação, nem lápis

    def _open_menu(self, s, view, pixel):
        """Abre a caixa no clique sobre a parede; no vazio o botão direito não abre (e segue sem efeito)."""
        if s.v2:
            from . import classico_v2
            return classico_v2.abrir_menu(s, view, pixel)
        line = hit_line(s, pixel)
        if line is None:
            return False
        ci, i, which = line
        if (ci, i) not in (s.multi or []):
            s.multi, s.selected = [(ci, i)], (ci, i)      # o clique na parede também a ativa
        else:
            s.selected = (ci, i)
        s.line = which
        s.menu = dict(pixel=pixel, regiao=tuple(view.rect))
        self._refresh_menu(s)
        return True

    def _refresh_menu(self, s):
        """Refaz as linhas da caixa com os valores de agora, no mesmo ponto do clique."""
        if s.menu is None:
            return
        caixa = mc.layout(s.menu['pixel'], mc.itens(s.line, *props.estado_da_caixa(s)), s.menu['regiao'])
        caixa['pixel'], caixa['regiao'] = s.menu['pixel'], s.menu['regiao']
        s.menu = caixa

    def _menu_action(self, s, chave):
        if s.v2:
            from . import classico_v2
            classico_v2.menu_acao(s, chave)
        elif chave == mc.LINHA:
            s.line = model.INNER if s.line == model.OUTER else model.OUTER
        elif chave == mc.DIRECAO:
            props.aplicar_direcao(s, 'LEFT' if props.estado_da_caixa(s)[0] == 'RIGHT' else 'RIGHT')
        elif chave == mc.INVERTER:
            props.inverter_ativas(s)
        else:
            tipo = mc.tipo_da_chave(chave)
            if tipo:
                props.aplicar_tipo(s, tipo)
        self._refresh_menu(s)

    def _is_navigation(self, event):
        """Evento que só move a vista (013, D-06): pinça, arraste com dois dedos, roda, botão do meio e o arraste dele."""
        return event.type in NAVIGATION_EVENTS or (event.type == 'MOUSEMOVE' and self.panning is not None)

    def _update_snap(self, context, s, view):
        """Ponto travado da mira para o desenho e para o próximo clique (009, D-02)."""
        if s.v2:
            return
        state = _state(context)
        origin, exclude = None, ()
        if self.dragging is not None:
            ci, k = self.dragging
            chain = s.plan.chains[ci]
            prev = k - 1 if k > 0 else (len(chain.nodes) - 1 if chain.closed else None)
            origin = chain.nodes[prev] if prev is not None else None
            exclude = (chain.nodes[k],)
        elif state.tool == 'DRAW' and s.drawing is not None and s.drawing.nodes:
            origin = s.drawing.nodes[-1]
        if state.tool in ('DRAW', 'SELECT'):
            s.snap_point = resolve_point(context, s, view, s.cursor, origin, getattr(self, 'shift', False), exclude)
        else:
            s.snap_point, s.lock_x, s.lock_y = None, None, None

    def _handle_undo(self, event, s):
        """Ctrl+Z desfaz e Ctrl+Shift+Z / Ctrl+Y refaz no rascunho (BUG-20261007-ZZUK)."""
        if event.value != 'PRESS' or event.type not in {'Z', 'Y'} or not (event.ctrl or event.oskey):
            return False
        redo = event.type == 'Y' or event.shift
        self.dragging = None
        if not (s.redo() if redo else s.undo()):
            s.error = N_("Nada para refazer.") if redo else N_("Nada para desfazer.")
        else:
            s.error = ""
        s.redraw()
        return True

    # Eventos ------------------------------------------------------------------------------------------------
    def _handle(self, context, event, s, view, pixel):
        state = _state(context)
        if s.v2:
            from . import classico_v2         # perguntas abertas (descartar, excluir em lote) antes da navegação
            if classico_v2.capturar(self, context, event, s, view, pixel):
                return True
        if self._handle_menu(state, event, s, view, pixel):
            return True
        if handle_zoom_window(event, s, view, pixel):
            return True
        if event.type == 'MIDDLEMOUSE':
            self.panning = pixel if event.value == 'PRESS' else None
            return True
        if event.type == 'MOUSEMOVE' and self.panning is not None:
            view.pan(pixel[0] - self.panning[0], pixel[1] - self.panning[1])
            self.panning = pixel
            return True
        if event.type in {'WHEELUPMOUSE', 'WHEELDOWNMOUSE'}:        # roda e Ctrl + roda (013, RN-04, D-05)
            view.zoom(gestures.wheel_factor(event.type == 'WHEELUPMOUSE', _invert_zoom_wheel(context)), pixel)
            return True
        if event.type == 'TRACKPADZOOM':                              # pinça no touchpad (013, RN-01, D-04)
            view.zoom(gestures.pinch_factor(compat.pinch_delta(event)), pixel)
            return True
        if event.type == 'TRACKPADPAN':                               # arraste com dois dedos (013, RN-03)
            view.pan(*compat.trackpad_delta(event))
            return True
        if event.type == 'HOME' and event.value == 'PRESS':
            view.fit(s.v2.bounds() if s.v2 else s.plan.bounds(), margin=0.15)
            return True
        if s.zoom_window is not None:
            return True                       # com a lupa ligada, só navegação e Ctrl+Z passam (D-10)
        if s.v2:
            from . import classico_v2
            return classico_v2.tratar(self, context, event, s, view, pixel)
        if s.prompt in PROMPTS:
            return self._handle_prompt(context, event, s, pixel)
        if state.tool == 'DRAW':
            return self._handle_draw(context, event, s, view, pixel)
        if state.tool == 'MOVE':
            return self._handle_move(context, event, s, view, pixel)      # BUG-20261117-EELF
        if state.tool == 'MEASURE':
            return self._handle_measure(context, event, s, view, pixel)   # BUG-20261117-V4I3
        if event.type == 'ESC' and event.value == 'PRESS':
            if s.typed:
                s.typed = ""                      # Esc primeiro limpa a digitação
            elif s.dirty():
                s.prompt = 'discard'              # pergunta antes de descartar (D-30)
            else:
                s.request = 'cancel'
            return True
        if state.tool == 'SELECT' and event.type == 'A' and event.value == 'PRESS' and not s.typed:
            # 067 onda 8 (D-39, RF-162): A seleciona todos os trechos do plano; Alt+A limpa.
            s.multi = [] if getattr(event, 'alt', False) else selecao_classica.todos(s.plan)
            s.selected = s.multi[-1] if s.multi else None
            s.selected_node = None
            return True
        if state.tool == 'SELECT' and self._handle_typing(event, s):
            return True
        if event.type in {'DEL', 'X'} and event.value == 'PRESS' and s.selected is not None:
            if s.lote():
                s.error = N_("Apague um trecho por vez.")      # walls2d RN-16: Del apaga um trecho
                return True
            remove_segment(s, *s.selected)
            return True
        if event.type == 'LEFTMOUSE':
            return self._handle_click(context, event, s, view, pixel, state.tool)
        if event.type == 'MOUSEMOVE' and getattr(self, 'box', None) is not None:
            s.selection_box = (self.box[0], pixel)
            return True
        if event.type == 'MOUSEMOVE' and self.dragging is not None:
            ci, k = self.dragging
            chain = s.plan.chains[ci]
            point = (s.snap_point or (s.cursor, 'free'))[0]      # cadeia de travas da mira (009, D-02)
            if (not chain.closed and k == len(chain.nodes) - 1 and chain.segment_count() >= 3
                    and distance_point_point(pixel, view.to_screen(chain.nodes[0])) <= SNAP_CLOSE_PX):
                point = chain.nodes[0]                       # ímã também no arraste (D-33)
            chain.move_node(k, point)
            return True
        return False

    # Ferramenta Mover (BUG-20261117-EELF) -------------------------------------------------------------------
    def _begin_move(self, s, pixel):
        """Cópia dos nós das paredes ativas (regra de 2026-11-17: a vizinha estica). Deslocar a partir da cópia evita
        acumular erro e permite devolver tudo com Esc."""
        selecao, nos = [], {}
        candidatos = list(s.multi) if len(s.multi) > 1 else ([s.selected] if s.selected is not None else [])
        for ci, si in candidatos:
            if not 0 <= ci < len(s.plan.chains):
                continue
            chain = s.plan.chains[ci]
            if not 0 <= si < chain.segment_count():
                continue
            selecao.append((ci, si))
            for k in (si, (si + 1) % len(chain.nodes)):
                nos[(ci, k)] = chain.nodes[k]
        if not nos:
            return False
        s.move_origin, s.move_start, s.move_selection, s.move_delta = pixel, nos, selecao, (0.0, 0.0)
        return True

    def _apply_move(self, s, dx, dy):
        """Repõe a cópia e desloca: o desenho acompanha o ponteiro sem o erro de somar deltas sucessivos."""
        for (ci, k), (x, y) in s.move_start.items():
            s.plan.chains[ci].nodes[k] = (x, y)
        s.plan.move_segments(s.move_selection, dx, dy)
        s.move_delta = (dx, dy)

    def _restore_move(self, s):
        for (ci, k), (x, y) in s.move_start.items():
            s.plan.chains[ci].nodes[k] = (x, y)

    def _end_move(self, s):
        s.move_origin, s.move_start, s.move_selection, s.move_delta = None, None, [], (0.0, 0.0)

    def _handle_move(self, context, event, s, view, pixel):
        """Mover as paredes ativas: arraste, setas de 90° e medida digitada. Esc devolve o rascunho de onde estava."""
        if event.type == 'ESC' and event.value == 'PRESS':
            if s.move_start is None:
                return False                      # sem movimento: o Esc segue o caminho normal
            self._restore_move(s)
            self._end_move(s)
            s.typed, s.typed_preview, s.error = "", "", ""
            return True
        if event.type == 'LEFTMOUSE' and event.value == 'PRESS':
            if s.move_start is not None:
                return True
            if not self._begin_move(s, pixel):
                s.error = N_("Selecione uma ou mais paredes para mover.")
                return True
            s.error = ""
            return True
        if event.type == 'LEFTMOUSE' and event.value == 'RELEASE':
            if s.move_start is None:
                return True
            self._end_move(s)                     # já aplicado; o modal grava um passo de desfazer
            s.typed, s.typed_preview = "", ""
            return True
        if event.type == 'MOUSEMOVE' and s.move_start is not None:
            atual, origem = view.to_world(pixel), view.to_world(s.move_origin)
            dx, dy = atual[0] - origem[0], atual[1] - origem[1]
            if getattr(event, 'shift', False):                # Shift trava no eixo dominante
                if abs(dx) >= abs(dy):
                    dy = 0.0
                else:
                    dx = 0.0
            self._apply_move(s, dx, dy)
            return True
        angulo = dr.arrow_direction(event.type)
        if angulo is not None and event.value == 'PRESS' and s.move_start is not None:
            distancia = math.hypot(*s.move_delta)
            self._apply_move(s, math.cos(angulo) * distancia, math.sin(angulo) * distancia)
            return True
        if accept_typing(s, event.unicode):
            return True
        if event.type == 'BACK_SPACE' and s.typed:
            s.typed = s.typed[:-1]
            s.typed_preview = expr.preview(s.typed, units.get_scene_length_unit())
            return True
        if event.type in {'RET', 'NUMPAD_ENTER'} and s.typed:
            try:
                valor = units.parse_length(s.typed, units.get_scene_length_unit(), allow_zero=False)
            except ValueError as exc:
                s.error, s.typed, s.typed_preview = str(exc), "", ""
                return True
            if s.move_start is None and not self._begin_move(s, pixel):
                s.error = N_("Selecione uma ou mais paredes para mover.")
                s.typed = ""
                return True
            dx, dy = s.move_delta
            direcao = math.atan2(dy, dx) if (dx or dy) else 0.0     # sem arraste, a medida anda para a direita
            self._apply_move(s, math.cos(direcao) * valor, math.sin(direcao) * valor)
            s.typed, s.typed_preview = "", ""
            self._end_move(s)                    # medida digitada conclui o movimento
            return True
        return False

    # Ferramenta Medir (BUG-20261117-V4I3) -------------------------------------------------------------------
    def _handle_measure(self, context, event, s, view, pixel):
        """Dois cliques medem a distância entre eles; o ímã é o dos vértices. Esc (ou o botão direito) limpa.

        Só leitura: o rascunho e o desfazer ficam como estavam.
        """
        if event.type in {'ESC', 'RIGHTMOUSE'} and event.value == 'PRESS':
            if s.medir is None:
                return False
            s.medir, s.error = medir.limpar(s.medir), ""
            return True
        if event.type != 'LEFTMOUSE' or event.value != 'PRESS':
            return event.type in {'MOUSEMOVE', 'INBETWEEN_MOUSEMOVE'}
        candidatos = [node for chain in s.plan.chains for node in chain.nodes]
        ponto, _tipo = medir.snap(view.to_world(pixel), candidatos, view.to_screen)
        s.medir = medir.clicar(s.medir, ponto)
        return True

    def _finish_box(self, s, view, pixel):
        """Solta o retângulo de seleção (D-39): soma com Shift; sem arrastar, um clique no vazio limpa."""
        start, add, before = self.box
        self.box, s.selection_box = None, None
        if distance_point_point(start, pixel) < 4:
            found = []
        else:
            found = selecao_classica.no_retangulo(s.plan, view.to_world(start), view.to_world(pixel))
        s.multi = list(dict.fromkeys([*before, *found])) if add else found
        s.selected = s.multi[-1] if s.multi else None

    def _handle_click(self, context, event, s, view, pixel, tool):
        if event.value == 'RELEASE' and getattr(self, 'box', None) is not None:
            self._finish_box(s, view, pixel)
            return True
        if event.value == 'RELEASE':
            dragged, self.dragging = self.dragging, None
            if dragged is not None:
                ci, k = dragged
                chain = s.plan.chains[ci]
                if (not chain.closed and k == len(chain.nodes) - 1 and chain.segment_count() >= 3
                        and chain.touches_start(chain.nodes[-1], CLOSE_TOLERANCE)):
                    s.prompt, s.prompt_chain = 'close_existing', ci       # arraste até o início (D-34)
            return True
        if event.value != 'PRESS':
            return False
        s.error = ""
        if tool == 'SELECT':
            s.typed = ""
            node = hit_node(s, pixel)
            if node is not None:
                self.dragging = node
                s.selected_node, s.selected, s.multi = node, None, []
                return True
            s.selected_node = None
            line = hit_line(s, pixel)
            if line is not None:
                ci, i, which = line
                if getattr(event, 'shift', False):                # 067 onda 8 (D-39): soma ou tira o trecho
                    base = s.multi or ([s.selected] if s.selected is not None else [])
                    s.multi = selecao_classica.alternar(base, (ci, i))
                    s.selected = (ci, i) if (ci, i) in s.multi else (s.multi[-1] if s.multi else None)
                else:
                    s.multi = [(ci, i)]
                    s.selected = (ci, i)
                s.line = which
            else:
                self.box = (pixel, getattr(event, 'shift', False), list(s.multi))  # retângulo a partir do vazio (D-39)
                s.selection_box = (pixel, pixel)
            return True
        if tool == 'REMOVE_NODE':
            node = hit_node(s, pixel)
            if node is not None:
                try:
                    remove_node(s, *node)
                except ValueError as exc:
                    s.error = str(exc)
                s.selected = None
            return True
        line = hit_line(s, pixel)
        if line is None:
            return True
        ci, i, _which = line
        chain = s.plan.chains[ci]
        if tool == 'ADD_NODE':
            chain.split(i, s.cursor)
        elif tool == 'INVERT':
            chain.invert()
        s.selected = None
        return True

    def _handle_typing(self, event, s):
        """Digitação direta da medida na face ou no vértice selecionado (D-27, RF-39)."""
        if event.value != 'PRESS' or (s.selected is None and s.selected_node is None):
            return False
        if accept_typing(s, event.unicode):                 # conta na medida (009, D-07)
            return True
        if event.type == 'BACK_SPACE' and s.typed:
            s.typed = s.typed[:-1]
            s.typed_preview = expr.preview(s.typed, units.get_scene_length_unit())
            return True
        if event.type in {'RET', 'NUMPAD_ENTER'} and s.typed:
            s.typed_preview = ""
            try:
                value = units.parse_length(s.typed, units.get_scene_length_unit(), allow_zero=False)
                if s.selected_node is not None:
                    ci, k = s.selected_node
                    chain = s.plan.chains[ci]
                    i = k - 1 if k > 0 else (chain.segment_count() - 1 if chain.closed else None)
                    if i is None:
                        raise ValueError(tr("Valor Inválido: o primeiro vértice de uma parede aberta não tem "
                                            "trecho chegando nele."))
                    chain.set_length(i, value, model.INNER)
                else:
                    chain, i = s.segment()
                    chain.set_length(i, value, s.line)
                s.error = ""
            except ValueError as exc:
                s.error = str(exc)
            s.typed = ""
            return True
        return False

    def _handle_draw(self, context, event, s, view, pixel):
        state = _state(context)
        if event.value != 'PRESS':
            return event.type == 'MOUSEMOVE'
        if event.type in {'ESC', 'RIGHTMOUSE'}:
            self._finish_drawing(s)
            return True
        if event.type == 'BACK_SPACE':
            s.typed = s.typed[:-1]
            s.typed_preview = expr.preview(s.typed, units.get_scene_length_unit())
            return True
        if s.drawing is not None and dr.arrow_direction(event.type) is not None:
            s.direction, s.direction_locked = dr.arrow_direction(event.type), True     # setas (RN-06)
            return True
        if accept_typing(s, event.unicode):
            return True
        if event.type in {'RET', 'NUMPAD_ENTER'} and s.drawing is not None and s.typed:
            try:
                length = units.parse_length(s.typed, units.get_scene_length_unit(), allow_zero=False)
            except ValueError as exc:
                s.error, s.typed, s.typed_preview = str(exc), "", ""
                return True
            start = s.drawing.nodes[-1]
            if not s.direction_locked:                      # primeiro trecho: direção do mouse (RN-05)
                s.direction = dr.initial_direction(start, s.cursor)
                if s.direction is None:
                    s.error = tr("Mova o mouse na direção da parede ou use as setas do teclado")
                    return True
                s.direction_locked = True
            target = dr.next_point(start, s.direction, length)       # o mouse não conta (RN-05)
            if s.drawing.segment_count() >= 2 and s.drawing.touches_start(target, CLOSE_TOLERANCE):
                s.typed, s.prompt = "", 'close'           # chegou ao início pelo teclado: pergunta (D-34)
                s.pending_point = target                  # "Não" mantém o trecho digitado
                return True
            self._append(s, state, target)
            return True
        if event.type != 'LEFTMOUSE':
            return False
        origin = s.drawing.nodes[-1] if s.drawing is not None and s.drawing.nodes else None
        point, kind = resolve_point(context, s, view, view.to_world(pixel), origin, getattr(self, 'shift', False))
        if s.drawing is None:
            s.reset_direction()
            s.drawing = model.Chain([point], [], False, state.new_direction)
            s.plan.chains.append(s.drawing)
            return True
        if kind == 'close':
            s.prompt = 'close'
            return True
        if point == s.drawing.nodes[-1]:
            return True
        self._append(s, state, point)          # o clique fixa a direção deste trecho (RN-06)
        return True

    def _append(self, s, state, point):
        start = s.drawing.nodes[-1]
        s.direction, s.direction_locked = dr.segment_direction(start, point), True
        s.typed_preview = ""
        s.drawing.nodes.append((float(point[0]), float(point[1])))
        s.drawing.segments.append(model.Segment(thickness=state.new_thickness, height=state.new_height))
        s.typed = ""

    def _finish_drawing(self, s):
        if s.drawing is not None and s.drawing.segment_count() == 0:
            s.plan.chains.remove(s.drawing)
        s.drawing, s.typed = None, ""
        s.reset_direction()

    def _answer_no(self, context, s):
        if s.prompt == 'close' and getattr(s, 'pending_point', None) is not None and s.drawing is not None:
            self._append(s, _state(context), s.pending_point)
            s.drawing.keep_open = True
        if s.prompt == 'close_existing' and s.prompt_chain is not None and s.prompt_chain < len(s.plan.chains):
            s.plan.chains[s.prompt_chain].keep_open = True
        s.prompt, s.pending_point = None, None

    def _handle_prompt(self, context, event, s, pixel):
        if event.type == 'ESC' and event.value == 'PRESS':
            self._answer_no(context, s)           # Esc fecha a pergunta (= Não)
            return True
        if event.type != 'LEFTMOUSE' or event.value != 'PRESS':
            return event.type != 'MOUSEMOVE'
        _win, _area, region = window.editor_area(context)
        _box, yes, no = _prompt_rects(region)
        from ..hb_gpu_draw import point_in_rect
        if point_in_rect(pixel[0], pixel[1], yes):
            if s.prompt == 'discard':
                s.prompt, s.request = None, 'cancel'
                return True
            if s.prompt == 'close_existing':
                chain = s.plan.chains[s.prompt_chain]
                if chain.close_if_touching(CLOSE_TOLERANCE) and not any(sg.source for sg in chain.segments):
                    chain.side = chain.outward_side()
                s.prompt = None
                return True
            s.pending_point = None
            self._append(s, _state(context), s.drawing.nodes[0])
            s.drawing.close()
            s.drawing.side = s.drawing.outward_side()     # sala fechada: espessura para fora (D-25)
            s.drawing, s.prompt = None, None
            _state(context).tool = 'SELECT'
        elif point_in_rect(pixel[0], pixel[1], no):
            self._answer_no(context, s)
        return True


class BTM_OT_WallEditorOk(bpy.types.Operator):
    """Aplica as paredes desenhadas ao ambiente"""
    bl_idname = "caffmob.wall_editor_ok"
    bl_label = "OK"
    bl_options = {'REGISTER', 'INTERNAL'}

    def execute(self, context):
        s = props.session()
        if s is None:
            return {'CANCELLED'}
        if s.v2:
            s.request = 'ok'
            return {'FINISHED'}
        from . import apply
        missing = apply.items_that_do_not_fit(s.plan)
        modules = apply.modules_of_removed(s.plan)
        mismatched = apply.height_mismatches(s.plan, s.project_height)
        if s.equalize_height:
            try:
                model.validate('height', s.project_height)
            except ValueError as exc:
                s.error = str(exc)
                self.report({'ERROR'}, s.error)
                return {'CANCELLED'}
        signature = (model.plan_signature(s.plan), s.project_height, s.equalize_height)
        if s.confirm_pending and s.confirm_signature != signature:
            s.confirm_pending = False     # o rascunho mudou depois do 1º aviso: os avisos são refeitos (DT-04)
        if (missing or modules or mismatched) and not s.confirm_pending:
            s.warnings = [tr("{} não cabe em {}").format(item, wall) for wall, item in missing]
            s.removed_modules = [tr("{} (em {})").format(item, wall) for wall, item in modules]
            s.height_mismatches = mismatched
            s.confirm_pending, s.confirm_signature = True, signature
            self.report({'WARNING'}, "Confira os avisos no painel e clique OK de novo para aplicar.")
            return {'CANCELLED'}
        s.request = 'ok'
        return {'FINISHED'}


class BTM_OT_WallEditorCancel(bpy.types.Operator):
    """Fecha o editor sem alterar as paredes"""
    bl_idname = "caffmob.wall_editor_cancel"
    bl_label = "Cancelar"
    bl_options = {'REGISTER', 'INTERNAL'}

    def invoke(self, context, event):
        s = props.session()
        if s is not None and s.dirty():               # D-30: confirmação antes de descartar
            return context.window_manager.invoke_confirm(
                self, event, title="Descartar alterações", message="Descartar as alterações e fechar o editor?",
                confirm_text="Descartar", icon='WARNING')
        return self.execute(context)

    def execute(self, context):
        s = props.session()
        if s is not None:
            s.request = 'cancel'
        return {'FINISHED'}


class BTM_OT_WallEditorTool(bpy.types.Operator):
    bl_idname = "caffmob.wall_editor_tool"
    bl_label = "Ferramenta"
    bl_options = {'REGISTER', 'INTERNAL'}

    tool: bpy.props.EnumProperty(
        name="Ferramenta",
        items=[('SELECT', "Selecionar/Mover", "Selecionar trechos e arrastar vértices"),
               ('DRAW', "Construir Parede", "Desenhar paredes a lápis"),
               ('INVERT', "Inverter Sentido", "Inverter o sentido da parede clicada"),
               ('MOVE', "Mover", "Deslocar as paredes ativas em qualquer direção (BUG-20261117-EELF)"),
               ('MEASURE', "Medir", "Clique dois pontos para ver a distância entre eles"),
               ('ADD_NODE', "Adicionar Vértice", "Dividir o trecho no ponto clicado"),
               ('REMOVE_NODE', "Remover Vértice", "Unir os trechos do vértice clicado")])  # type: ignore

    def execute(self, context):
        _state(context).tool = self.tool
        s = props.session()
        if s is not None:
            s.redraw()
        return {'FINISHED'}


class BTM_OT_WallEditorFit(bpy.types.Operator):
    """Enquadra todas as paredes na planta"""
    bl_idname = "caffmob.wall_editor_fit"
    bl_label = "Enquadrar Tudo"
    bl_options = {'REGISTER', 'INTERNAL'}

    def execute(self, context):
        s = props.session()
        if s is not None and s.view is not None:
            s.view.fit(s.v2.bounds() if s.v2 else s.plan.bounds(), margin=0.15)
            s.redraw()
        return {'FINISHED'}


class BTM_OT_WallEditorPrint(bpy.types.Operator):
    """Imprime a planta baixa do editor"""
    bl_idname = "caffmob.wall_editor_print"
    bl_label = "Imprimir Planta Baixa"
    bl_description = "Salva a planta baixa da vista num PDF A4 pronto para impressão"
    bl_options = {'REGISTER'}

    filepath: bpy.props.StringProperty(
        name="Arquivo",
        description="Caminho do PDF da planta baixa",
        subtype='FILE_PATH',
        default="//planta-baixa.pdf"
    )  # type: ignore

    filter_glob: bpy.props.StringProperty(
        default="*.pdf",
        options={'HIDDEN'}
    )  # type: ignore

    def invoke(self, context, event):
        if props.session() is None:
            self.report({'WARNING'}, tr("Abra o editor de paredes para imprimir a planta."))
            return {'CANCELLED'}
        base = bpy.path.basename(bpy.data.filepath).rsplit('.', 1)[0] if bpy.data.filepath else "projeto"
        self.filepath = f"//{base}_planta-baixa.pdf"
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

    def execute(self, context):
        s = props.session()
        if s is None:
            self.report({'WARNING'}, tr("Abra o editor de paredes para imprimir a planta."))
            return {'CANCELLED'}
        from . import impressao
        state = _state(context)
        unidade = units.get_scene_length_unit(context.scene)
        tracos = impressao.coletar_v2(s.v2, unidade) if s.v2 else impressao.coletar_plano(s.plan, unidade)
        if state.plant_low:                      # os objetos da planta baixa entram como hachura (BUG-20261117-JXDJ)
            from . import scene_io
            objetos = scene_io.plant_objects(context.scene, state.cut_height)
            tracos += impressao.tracos_da_planta(objetos, state.material_color_mode == 'SOLID')
        caixa = vista_em_metros(s)
        if not tracos or impressao.limites(tracos) is None:
            self.report({'WARNING'}, tr("Não há planta para imprimir."))
            return {'CANCELLED'}
        dados, denominador = impressao.pagina_pdf(tracos, caixa, tr("Planta baixa"), unidade)
        caminho = bpy.path.abspath(self.filepath)
        if not caminho.lower().endswith('.pdf'):
            caminho += '.pdf'
        try:
            with open(caminho, 'wb') as arquivo:
                arquivo.write(dados)
        except OSError as exc:
            self.report({'ERROR'}, tr("Não foi possível salvar o PDF: {}").format(exc))
            return {'CANCELLED'}
        escala = tr("1:{}").format(denominador) if denominador else tr("ajustada à folha")
        self.report({'INFO'}, tr("Planta baixa salva em {} ({})").format(caminho, escala))
        return {'FINISHED'}


classes = (BTM_OT_WallEditor, BTM_OT_WallEditorModal, BTM_OT_WallEditorOk, BTM_OT_WallEditorCancel,
           BTM_OT_WallEditorTool, BTM_OT_WallEditorFit, BTM_OT_WallEditorPrint)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
