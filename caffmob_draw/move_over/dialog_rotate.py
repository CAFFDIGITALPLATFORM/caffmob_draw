"""Rotação, pivô, navegação e histórico do diálogo Mover Sobre (feature 067, T082 a T085, T111; D-24; RF-120 a RF-127,
RF-129).

Mixin de `ops_dialog.BTM_OT_MoveOverDialog`:
- máquina IDLE / HOVER / TRANSLATE / ROTATE (CONFIRM e CANCEL são o Encostar e o Cancelar): o mouse perto de um
  canto de A numa vista (tolerância `btm_move_over.tolerance_px` × escala da interface, DPI) é HOVER; apertar ali
  começa o ROTATE, com o quadro congelado no mouse-down (pivô, ângulo inicial e estado de A); soltar grava um passo
  no histórico local; Esc volta ao estado do mouse-down;
- prioridade do clique numa vista: campo de ângulo > pivô > alça (girar) > corpo (arrastar) > vazio; Ctrl+clique
  num ponto (cantos e centro) escolhe o pivô e Alt+clique, a âncora;
- ângulo digitável junto de cada vista, com snap de 15° no arraste (Shift: precisão fina) e R para zerar o giro;
- navegação por vista: roda = zoom no mouse, botão do meio = pan, F ou Home = enquadrar; pan e zoom não mexem em A;
- histórico local Ctrl+Z / Ctrl+Shift+Z, separado do Desfazer global (um passo só, no Encostar); Cancelar volta à
  entrada;
- contorno de A pelas arestas reais da malha (até 12 mil; acima, a caixa), lidas uma vez na abertura; o desenho só
  projeta o que está em cache (sem varredura da cena no draw nem no mousemove).
"""

import math

from ..canvas2d import draw
from . import rotation as rot

MAX_EDGES = 12000
VIEW_SIGN = {'plan': 1.0, 'front': -1.0}          # anti-horário na tela = giro positivo no eixo da vista
L = draw.LIGHT


class RotateMixin:
    # Estado -----------------------------------------------------------------------------------------------
    def _init_rotate(self, context):
        self.mode = 'IDLE'
        self.hover = None
        self.rotating = None
        self.panning = None
        self.user_view = False
        self.alt = False
        self.ctrl = False
        self.history = [self.mo.state()]
        self.redo_stack = []
        try:
            self._edges_local = _edges_of(self.mo)
        except (AttributeError, ReferenceError, RuntimeError):
            self._edges_local = None                       # sem malha legível: o desenho usa a caixa
        self._edge_cache = {}

    def _push_history(self):
        if not hasattr(self, 'history'):
            return                                     # janela montada por fora (ensaios antigos)
        state = self.mo.state()
        if not self.history or self.history[-1] != state:
            self.history.append(state)
            self.redo_stack = []

    def _undo_local(self):
        if len(self.history) <= 1:
            return False
        self.redo_stack.append(self.history.pop())
        self.mo.set_state(self.history[-1])
        self.side = None
        return True

    def _redo_local(self):
        if not self.redo_stack:
            return False
        state = self.redo_stack.pop()
        self.history.append(state)
        self.mo.set_state(state)
        self.side = None
        return True

    # Geometria das vistas ---------------------------------------------------------------------------------
    def _tolerance(self):
        return float(getattr(self.state, 'tolerance_px', 12)) * self.s

    def _project(self, key, point):
        from .ops_dialog import VIEWS
        _name, h, v = VIEWS[key]
        return getattr(self, 'view_' + key).to_screen((point[h], point[v]))

    def _handles(self, key):
        """Os cantos do retângulo de A na vista (as alças de girar)."""
        from .ops_dialog import VIEWS
        _name, h, v = VIEWS[key]
        r = self._view_rect(getattr(self, 'view_' + key), self.mo.box_a(), h, v)
        return [(r[0], r[1]), (r[0] + r[2], r[1]), (r[0] + r[2], r[1] + r[3]), (r[0], r[1] + r[3])]

    def _points(self, key):
        return {k: self._project(key, self.mo.point_in_b(k)) for k in rot.POINT_KEYS}

    def _near(self, pixel, points):
        tol = self._tolerance()
        best = None
        for name, p in points:
            d = math.hypot(pixel[0] - p[0], pixel[1] - p[1])
            if d <= tol and (best is None or d < best[0]):
                best = (d, name)
        return best[1] if best else None

    def _angle_field_at(self, pixel):
        from ..hb_gpu_draw import point_in_rect
        for key, rect in getattr(self, 'angle_fields', {}).items():
            if point_in_rect(pixel[0], pixel[1], rect):
                return key
        return None

    # Clique numa vista (prioridade: campo > ponto > alça > corpo > vazio) ----------------------------------
    def _pane_click(self, pane, pixel):
        field = self._angle_field_at(pixel)
        if field is not None:
            self.typing, self.buffer = 'ANGLE_' + field, ""
            return True
        if self.ctrl or self.alt:                        # Ctrl+clique: pivô; Alt+clique: âncora
            point = self._near(pixel, list(self._points(pane).items()))
            if point is not None:
                if self.alt:
                    self.mo.set_anchor(point)
                else:
                    self.mo.set_pivot(point)             # escolher o pivô não move nada (RF-121)
                self._push_history()
                return True
        pivot = self._project(pane, self.mo.point_in_b(self.mo.pivot))
        if self._near(pixel, [('PIVOT', pivot)]) is not None and \
                self._near(pixel, list(enumerate(self._handles(pane)))) is None:
            return True                                  # o pivô vem antes da alça e do corpo: não começa gesto
        handle = self._near(pixel, list(enumerate(self._handles(pane))))
        if handle is not None:
            self._rotate_begin(pane, pixel)
            return True
        self.mode = 'TRANSLATE'
        return False                                     # o corpo e o vazio seguem para o arraste de sempre

    # Girar ------------------------------------------------------------------------------------------------
    def _rotate_begin(self, pane, pixel):
        center = self._project(pane, self.mo.point_in_b(self.mo.pivot))
        start = rot.signed_angle(center, pixel)
        self.rotating = {'pane': pane, 'center': center, 'start': start, 'last': start, 'base': self.mo.state(),
                         'value': 0.0}
        self.mode = 'ROTATE'

    def _rotate_move(self, pixel, fine=False):
        r = self.rotating
        angle = rot.unwrap(r['last'], rot.signed_angle(r['center'], pixel, r['last']))
        r['last'] = angle
        value = rot.snap(angle - r['start'], fine=fine)
        if value == r['value']:
            return
        r['value'] = value
        self.mo.set_state(r['base'], preview=False)
        self.mo.rotate(r['pane'], VIEW_SIGN[r['pane']] * value)
        self.side = None

    def _rotate_end(self, cancel=False):
        r, self.rotating = self.rotating, None
        self.mode = 'IDLE'
        if r is None:
            return
        if cancel:
            self.mo.set_state(r['base'])               # Esc: volta exatamente ao mouse-down (RF-123)
            return
        self._push_history()                           # soltar: um passo no histórico local
        self._fit_views()

    def _hover_update(self, pixel):
        if self.rotating or getattr(self, 'drag', None):
            return
        pane = self._pane_at(pixel)
        handle = self._near(pixel, list(enumerate(self._handles(pane)))) if pane else None
        self.hover = (pane, handle) if handle is not None else None
        self.mode = 'HOVER' if self.hover else 'IDLE'

    # Ângulo digitado ----------------------------------------------------------------------------------------
    def _commit_angle(self, view, text):
        from ..data.i18n import tr
        try:
            value = float(text.replace(",", ".").replace("°", "").strip() or "0")
        except ValueError:
            self.warning = tr("Valor Inválido: o ângulo precisa ser um número em graus (recebido: {}).").format(text)
            return False
        self.mo.set_axis_angle(view, value)
        self._push_history()
        return True

    def _reset_orientation(self):
        self.mo.set_orientation(rot.IDENTITY)
        self._push_history()

    # Navegação ----------------------------------------------------------------------------------------------
    def _zoom(self, pane, pixel, factor):
        getattr(self, 'view_' + pane).zoom(factor, pixel)
        self.user_view = True

    def _pan_begin(self, pane, pixel):
        self.panning = (pane, pixel)

    def _pan_move(self, pixel):
        pane, last = self.panning
        getattr(self, 'view_' + pane).pan(pixel[0] - last[0], pixel[1] - last[1])
        self.panning = (pane, pixel)
        self.user_view = True

    def _reset_views(self):
        self.user_view = False
        self._fit_views()

    # Desenho ------------------------------------------------------------------------------------------------
    def _edge_lines(self, key):
        """Arestas reais de A projetadas na vista; em cache pela pose e pela vista (nada é lido da cena aqui)."""
        if not self._edges_local:
            return None
        view = getattr(self, 'view_' + key)
        signature = (self.mo.state(), view.scale, view.center, view.rect)
        cached = self._edge_cache.get(key)
        if cached is not None and cached[0] == signature:
            return cached[1]
        origin, q = self.mo.origin(), self.mo.orientation
        from .ops_dialog import VIEWS
        _name, h, v = VIEWS[key]
        lines = []
        for p0, p1 in self._edges_local:
            a, b = rot.world_point(origin, q, p0), rot.world_point(origin, q, p1)
            lines += [view.to_screen((a[h], a[v])), view.to_screen((b[h], b[v]))]
        self._edge_cache[key] = (signature, lines)
        return lines

    def _draw_rotate_layer(self, sh, key):
        lines = self._edge_lines(key)
        if lines:
            draw.lines(sh, lines, (*L['orange'][:3], 0.55))
        k = 4 * self.s
        hovered = self.hover[1] if self.hover and self.hover[0] == key else None
        for index, (x, y) in enumerate(self._handles(key)):
            color = L['blue'] if index == hovered else L['orange']
            draw.rect(sh, (x - k, y - k, 2 * k, 2 * k), color)
        pivot = self._project(key, self.mo.point_in_b(self.mo.pivot))
        anchor = self._project(key, self.mo.point_in_b(self.mo.anchor))
        origin = self._project(key, self.mo.origin())
        draw.circle(sh, pivot, 6 * self.s, L['blue'], L['paper'])                  # pivô: disco azul
        draw.lines(sh, [(anchor[0] - k, anchor[1]), (anchor[0], anchor[1] + k), (anchor[0] + k, anchor[1]),
                        (anchor[0], anchor[1] - k), (anchor[0] - k, anchor[1])], L['teal_ink'])   # âncora: losango
        draw.lines(sh, [(origin[0] - k, origin[1] - k), (origin[0] + k, origin[1] + k),
                        (origin[0] - k, origin[1] + k), (origin[0] + k, origin[1] - k)], L['muted'])  # origem: x
        rect = getattr(self, 'angle_fields', {}).get(key)
        if rect is not None:
            active = self.typing == 'ANGLE_' + key
            value = rot.angle_about(self.mo.orientation, rot.VIEW_AXIS[key])
            shown = (self.buffer + "▏") if active else f"{value:.1f}°".replace(".", ",")
            self._field(sh, rect, shown, active)


def _edges_of(mo):
    """Arestas (no referencial local de A) das malhas visíveis da árvore de A, lidas uma vez; acima de 12 mil, None
    (o desenho usa a caixa)."""
    import bpy  # type: ignore
    from .scene import _frame
    depsgraph = bpy.context.evaluated_depsgraph_get()
    to_local = _frame(mo.a).inverted()
    edges, stack = [], [mo.a]
    while stack:
        node = stack.pop()
        stack += list(node.children)
        if node.type != 'MESH' or node.hide_get():
            continue
        evaluated = node.evaluated_get(depsgraph)
        mesh = evaluated.data
        if len(edges) + len(mesh.edges) > MAX_EDGES:
            return None
        matrix = to_local @ node.matrix_world
        verts = [tuple(matrix @ v.co) for v in mesh.vertices]
        edges += [(verts[e.vertices[0]], verts[e.vertices[1]]) for e in mesh.edges]
    return edges
