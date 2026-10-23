"""Janela "Mover Sobre", com a aparência e as funções do "Encostar" do artefato (T026; D-15, RN-05 a RN-11,
RF-28 a RF-33; BUG-20261022-RQR5).

Painel claro desenhado sobre a viewport (`POST_PIXEL`) por um modal, porque o popup do Blender não desenha vistas:
- título "Encostar «A» em «B»" e X para fechar;
- vistas **Frontal** (X × altura) e **Planta baixa** (X × profundidade, o fundo em cima), no referencial de B, com B em
  teal, A original tracejado e A na posição nova em laranja, com alça e a cota do afastamento;
- arrastar o laranja nas vistas move A; com o **ímã** ligado ele puxa para encostar, alinhar ou centralizar
  (`encostar.snap`, 8 px), com guias azuis; Shift solta o ímã enquanto estiver apertado; clicar fora do laranja
  escolhe o lado de B mais perto do clique;
- seis lados (À esquerda, À direita, Em cima, Embaixo, Atrás, Na frente), **Afastamento** em mm (0 a 5000) e os
  alinhamentos dos dois eixos livres do lado; **Grudar** liga A a B pela face do lado (`stick.link`);
- linha de folga e deslocamento; Cancelar (Esc) devolve A à posição original; Encostar (Enter) grava como um passo
  de desfazer, pela pose que o guarda de colisão permite (feature 066, D-08, RF-003), sem aviso.

"Mais opções" guarda o restante do Mover Sobre (feature 003, D-21/D-22): X, profundidade e altura digitáveis, rotação,
passo, posição relativa/absoluta, posições salvas e Substituir. Setas e Page Up/Down movem A pelo passo.

Fora do painel, a navegação da viewport (botão do meio, roda) continua funcionando; os demais cliques são ignorados.
"""

import bpy  # type: ignore

from ..data.i18n import N_, tr
from ..canvas2d import draw
from ..canvas2d.view import View2D
from ..data import units
from ..hb_gpu_draw import point_in_rect
from . import encostar, reposition
from .scene import MoveOver

NAV_EVENTS = {'MIDDLEMOUSE', 'WHEELUPMOUSE', 'WHEELDOWNMOUSE', 'TRACKPADPAN', 'TRACKPADZOOM', 'MOUSEROTATE',
              'NDOF_MOTION'}
FIELD_LABELS = ("X", N_("Profundidade"), N_("Altura"))
ABS_LABELS = ("X", "Y", "Z")
ROTATION, STEP = 3, 4             # campos da segunda linha de "Mais opções"
FIELD_COUNT = 5
GAP = 5                           # campo Afastamento
ARROWS = {'RIGHT_ARROW', 'LEFT_ARROW', 'UP_ARROW', 'DOWN_ARROW', 'PAGE_UP', 'PAGE_DOWN'}
MAX_SAVED_BUTTONS = 4
L = draw.LIGHT
VIEWS = {'front': ('FRONT', 0, 2), 'plan': ('PLAN', 0, 1)}     # vista → (nome, eixo horizontal, eixo vertical)
SNAP_HINT = N_("Arraste o móvel laranja nas vistas. Com o ímã, ele puxa para encostar, alinhar ou centralizar. "
               "Shift solta o ímã momentaneamente.")


def _scale():
    try:
        return bpy.context.preferences.system.ui_scale or 1.0      # 0 no modo background
    except AttributeError:
        return 1.0


def _mm(meters):
    return round(meters * 1000.0)


def _dashed_rect(r):
    corners = [(r[0], r[1]), (r[0] + r[2], r[1]), (r[0] + r[2], r[1] + r[3]), (r[0], r[1] + r[3])]
    return [p for i, c in enumerate(corners) for p in draw.dashed(c, corners[(i + 1) % 4], 5.0, 4.0)]


class BTM_OT_MoveOverDialog(bpy.types.Operator):
    """Alinha o objeto arrastado ao objeto de referência pelas vistas frontal e planta baixa"""
    bl_idname = "caffmob.move_over_dialog"
    bl_label = "Mover Sobre"
    bl_options = {'REGISTER', 'UNDO'}

    a_name: bpy.props.StringProperty(options={'HIDDEN', 'SKIP_SAVE'})  # type: ignore
    b_name: bpy.props.StringProperty(options={'HIDDEN', 'SKIP_SAVE'})  # type: ignore

    _handle = None

    @classmethod
    def poll(cls, context):
        return context.area is not None and context.area.type == 'VIEW_3D'

    # Ciclo ------------------------------------------------------------------------------------------------
    def invoke(self, context, event):
        objects = context.scene.objects
        a, b = objects.get(self.a_name), objects.get(self.b_name)
        try:
            self.mo = MoveOver(context, a, b)
        except ValueError as exc:
            self.report({'WARNING'}, str(exc))
            return {'CANCELLED'}
        for obj in context.selected_objects:
            obj.select_set(False)
        self.mo.a.select_set(True)
        self.mo.b.select_set(True)
        context.view_layer.objects.active = self.mo.b          # B vira o ativo (RN-05)
        self.mo.preview()                                       # A assume a rotação de B (RN-08)
        self.state = context.window_manager.btm_move_over
        self.mouse = (event.mouse_region_x, event.mouse_region_y)
        self._init_encostar(context)
        self._layout(context)
        self._fit_views()
        self._handle = bpy.types.SpaceView3D.draw_handler_add(self._draw, (), 'WINDOW', 'POST_PIXEL')
        context.window_manager.modal_handler_add(self)
        context.workspace.status_text_set(
            tr("Encostar  |  Arraste o laranja nas vistas (Shift solta o ímã)  |  Clique perto de um lado  |  "
               "Enter: encostar  |  Esc: cancelar"))
        context.area.tag_redraw()
        return {'RUNNING_MODAL'}

    def _init_encostar(self, context):
        """Estado inicial, como o artefato: o lado em que A já está, afastamento 0 e os alinhamentos do lado."""
        self.mouse = getattr(self, 'mouse', (-1, -1))
        self.typing, self.buffer, self.warning = None, "", ""
        self.more = False
        self.drag, self.guides = None, []
        self.snap_on = self.state.snap_on
        self.glue = self.state.glue
        self.original_box = self.mo.box_a()
        self.original_min = self.original_box[0]
        self.gap = 0.0
        self.side = encostar.initial_side(self.original_box, self.mo.box_b)
        self.align = encostar.default_align(self.side)
        self._apply()

    def _finish(self, context):
        if self._handle is not None:
            bpy.types.SpaceView3D.draw_handler_remove(self._handle, 'WINDOW')
            self._handle = None
        try:
            context.workspace.status_text_set(None)
        except (AttributeError, RuntimeError):
            pass
        if context.area:
            context.area.tag_redraw()

    def cancel(self, context):
        self.mo.restore()
        from ..collision import guard
        guard.accept(self.mo.a, self.mo.original_matrix)     # voltar à origem nunca é bloqueado
        self._finish(context)

    # Regras do Encostar -----------------------------------------------------------------------------------
    def _apply(self):
        """Leva A ao lado escolhido, com o afastamento e os alinhamentos; sem lado (posição livre), não mexe."""
        if self.side is None:
            return
        box_a = self.mo.box_a()
        self.mo.set_min(encostar.target_min(box_a, self.mo.box_b, self.side, self.gap, self.align, box_a[0]))

    def _set_side(self, side):
        self.side = side
        self.align = encostar.default_align(side)
        self.warning = ""
        self._apply()
        self._fit_views()
        self._layout_form()

    def _set_align(self, axis, value):
        self.align[axis] = value
        self._apply()

    def _set_gap_typed(self, text):
        """Afastamento digitado em mm; fora de 0 a 5000 mm fica o valor anterior, com o aviso."""
        try:
            value = float(text.replace(",", ".").replace("mm", "").strip() or "0") / 1000.0
        except ValueError:
            value = -1.0
        if not 0.0 <= value <= encostar.MAX_GAP:
            self.warning = tr("Afastamento entre 0 e 5000 mm")
            return False
        if self.side is None:          # veio de um arraste: a medida vale no lado mais perto, o resto fica
            self.side = encostar.derived_side(self.mo.box_a(), self.mo.box_b)
            self.align = {axis: encostar.KEEP for axis in range(3)}
            self._layout_form()
        self.gap = value
        self.warning = ""
        self._apply()
        return True

    def _shown_side(self):
        return self.side or encostar.derived_side(self.mo.box_a(), self.mo.box_b)

    def _title(self):
        return tr("Encostar “{}” em “{}”").format(self.mo.a.name, self.mo.b.name)

    def _info_text(self):
        def fmt(v):
            return tr("sobrepõe {}").format(_mm(-v)) if v < -0.0005 else str(_mm(max(0.0, v)))
        box = self.mo.box_a()
        gx, gy, gz = encostar.gaps(box, self.mo.box_b)
        dx, dy, dz = (_mm(box[0][i] - self.original_min[i]) for i in range(3))
        return tr("Folga até “{}”: largura {} · altura {} · profundidade {} mm. Deslocamento: X {} · Y {} · Z {} mm"
                  ).format(self.mo.b.name, fmt(gx), fmt(gz), fmt(gy), dx, dy, dz)

    # Geometria do painel ----------------------------------------------------------------------------------
    def _layout(self, context):
        region = context.region
        height_units = 720 if self.more else 610
        s = _scale()
        s *= max(0.6, min(1.0, (region.width - 24) / (840 * s), (region.height - 24) / (height_units * s)))
        self.s = s
        width, height = 840 * s, height_units * s
        x = max(8, (region.width - width) / 2.0)
        y = max(8, (region.height - height) / 2.0)
        origin = getattr(self, 'panel_origin', None)       # arrastada pelo título (BUG-20261023-WWZT)
        if origin is not None:
            x = max(8, min(origin[0], region.width - width - 8))
            y = max(8, min(origin[1] + origin[2] - height, region.height - height - 8))
        pad = 18 * s
        self.panel = (x, y, width, height)
        top = y + height
        self.title_bar = (x, top - 56 * s, width, 56 * s)
        self.title_pos = (x + 22 * s, top - 34 * s)
        self.button_close = (x + width - 50 * s, top - 45 * s, 34 * s, 34 * s)
        pane_w, pane_h = (width - 3 * pad) / 2.0, 250 * s
        pane_y = top - 56 * s - pad - pane_h
        self.pane_front = (x + pad, pane_y, pane_w, pane_h)
        self.pane_plan = (x + 2 * pad + pane_w, pane_y, pane_w, pane_h)
        self.snap_box = (x + pad, pane_y - pad - 18 * s, 18 * s, 18 * s)
        self.form_top = self.snap_box[1] - 14 * s
        self.footer = (x, y, width, 60 * s)
        self.button_ok = (x + width - pad - 112 * s, y + 13 * s, 112 * s, 34 * s)
        self.button_cancel = (self.button_ok[0] - 10 * s - 106 * s, y + 13 * s, 106 * s, 34 * s)
        self.button_more = (x + pad, y + 13 * s, 130 * s, 34 * s)
        self._layout_form()

    def _layout_form(self):
        """Chips de lado, Afastamento, alinhamentos do lado, Grudar e "Mais opções" (depende do lado)."""
        s, (x, _y, width, _h) = self.s, self.panel
        pad, chip_h = 18 * s, 30 * s
        cy = self.form_top - chip_h
        self.side_chips, cx = [], x + pad
        for side in encostar.SIDES:
            w = draw.text_width(encostar.SIDE_LABELS[side], self._font(12)) + 26 * s
            self.side_chips.append((side, (cx, cy, w, chip_h)))
            cx += w + 8 * s
        half = (width - 3 * pad) / 2.0
        label_w = 124 * s
        r1 = cy - 14 * s - 32 * s
        r2 = r1 - 10 * s - 32 * s
        self.gap_field = (x + pad + label_w, r1, half - label_w - 30 * s, 32 * s)
        self.gap_label_pos = (x + pad, r1 + 11 * s)
        axes = [a for a in encostar.ALIGN_ORDER if a in encostar.align_axes(self.side)] if self.side else []
        slots = [(x + 2 * pad + half, r1), (x + pad, r2)]
        self.align_rows, self.align_options = [], []
        for axis, (sx, sy) in zip(axes, slots):
            self.align_rows.append((axis, (sx, sy, half, 32 * s)))
            ox = sx + 112 * s
            for value, label in encostar.ALIGN_OPTIONS[axis]:
                w = draw.text_width(label, self._font(11)) + 14 * s
                self.align_options.append((axis, value, (ox, sy + 2 * s, w, 28 * s)))
                ox += w + 4 * s
        glue_slot = (x + 2 * pad + half, r2) if len(axes) > 1 else (x + pad, r2)
        self.glue_box = (glue_slot[0], glue_slot[1] + 7 * s, 18 * s, 18 * s)
        self.info_pos = (x + pad, r2 - 22 * s)
        self.warning_pos = (x + pad, r2 - 42 * s)
        more_y = r2 - 60 * s - 30 * s
        field_w = (width - 4 * pad) / 3.0
        self.fields = [(x + pad + i * (field_w + pad), more_y, field_w, 30 * s) for i in range(3)]
        row2 = more_y - 8 * s - 30 * s
        self.fields += [(x + pad, row2, field_w, 30 * s), (x + 2 * pad + field_w, row2, field_w, 30 * s)]
        self.button_mode = (x + 3 * pad + 2 * field_w, row2, field_w, 30 * s)
        small = (width - 2 * pad - (MAX_SAVED_BUTTONS + 1) * 8 * s) / (MAX_SAVED_BUTTONS + 2)
        row3 = row2 - 8 * s - 30 * s
        self.button_save = (x + pad, row3, small, 30 * s)
        self.saved_buttons = [(x + pad + (i + 1) * (small + 8 * s), row3, small, 30 * s)
                              for i in range(MAX_SAVED_BUTTONS)]
        self.button_substitute = (x + pad + (MAX_SAVED_BUTTONS + 1) * (small + 8 * s), row3, small, 30 * s)

    def _fit_views(self):
        """Enquadra A original, B e A na posição nova; durante o arraste a escala fica parada (como o artefato)."""
        if getattr(self, 'drag', None):
            return
        boxes = (self.original_box, self.mo.box_a(), self.mo.box_b)
        inset = 14 * self.s
        for key, rect in (('front', self.pane_front), ('plan', self.pane_plan)):
            _name, h, v = VIEWS[key]
            inner = (rect[0] + inset, rect[1] + inset, rect[2] - 2 * inset, rect[3] - 2 * inset - 18 * self.s)
            view = View2D(inner)
            view.fit(((min(b[0][h] for b in boxes), min(b[0][v] for b in boxes)),
                      (max(b[1][h] for b in boxes), max(b[1][v] for b in boxes))), margin=0.3)
            setattr(self, 'view_' + key, view)

    def _view_rect(self, view, box, h, v):
        p0, p1 = view.to_screen((box[0][h], box[0][v])), view.to_screen((box[1][h], box[1][v]))
        return (min(p0[0], p1[0]), min(p0[1], p1[1]), abs(p1[0] - p0[0]), abs(p1[1] - p0[1]))

    def _pane_at(self, pixel):
        for key in ('front', 'plan'):
            if point_in_rect(pixel[0], pixel[1], getattr(self, 'pane_' + key)):
                return key
        return None

    # Arraste nas vistas -----------------------------------------------------------------------------------
    def _drag_begin(self, pane, pixel):
        _name, h, v = VIEWS[pane]
        view = getattr(self, 'view_' + pane)
        r = self._view_rect(view, self.mo.box_a(), h, v)
        grab = 8 * self.s
        if r[0] - grab <= pixel[0] <= r[0] + r[2] + grab and r[1] - grab <= pixel[1] <= r[1] + r[3] + grab:
            self.drag = {'pane': pane, 'p0': pixel, 'n0': self.mo.box_a()[0], 'moved': False}
        else:
            self.drag = {'pane': pane, 'tap': pixel}

    def _drag_move(self, pixel, shift=False):
        d = self.drag
        if not d or 'tap' in d:
            return
        if not d['moved'] and abs(pixel[0] - d['p0'][0]) + abs(pixel[1] - d['p0'][1]) < 3:
            return
        d['moved'] = True
        self.side = None
        _name, h, v = VIEWS[d['pane']]
        view = getattr(self, 'view_' + d['pane'])
        size = encostar.size(self.mo.box_a())
        target = list(d['n0'])
        target[h] = d['n0'][h] + (pixel[0] - d['p0'][0]) / view.scale
        target[v] = d['n0'][v] + (pixel[1] - d['p0'][1]) / view.scale
        self.guides = []
        if self.snap_on and not shift:
            tolerance = encostar.SNAP_PX * self.s / view.scale
            for axis, vertical_line in ((h, True), (v, False)):
                target[axis], guide = encostar.snap(target[axis], axis, size[axis], self.mo.box_b, self.gap,
                                                    tolerance)
                if guide:
                    self.guides.append((d['pane'], vertical_line, guide[0], tr(guide[1]).format(_mm(self.gap))))
        target[h], target[v] = round(target[h], 3), round(target[v], 3)
        self.mo.set_min(tuple(target))

    def _drag_end(self):
        d, self.drag, self.guides = self.drag, None, []
        if not d:
            return
        if 'tap' in d:      # clique fora do laranja: escolhe o lado de B mais perto do clique
            name, h, v = VIEWS[d['pane']]
            r = self._view_rect(getattr(self, 'view_' + d['pane']), self.mo.box_b, h, v)
            dh = (d['tap'][0] - (r[0] + r[2] / 2.0)) / max(1.0, r[2] / 2.0)
            dv = (d['tap'][1] - (r[1] + r[3] / 2.0)) / max(1.0, r[3] / 2.0)
            self._set_side(encostar.side_from_point(name, dh, dv))
            return
        self._fit_views()
        self._layout_form()

    # Desenho ----------------------------------------------------------------------------------------------
    def _font(self, size):
        return max(9, int(size * getattr(self, 's', 1.0)))

    def _checkbox(self, sh, r, on, label):
        draw.rounded_rect(sh, r, 4 * self.s, L['orange'] if on else L['paper'])
        draw.rounded_outline(sh, r, 4 * self.s, L['orange'] if on else L['line_strong'])
        if on:
            x, y, w, h = r
            draw.lines(sh, [(x + w * 0.22, y + h * 0.52), (x + w * 0.42, y + h * 0.3),
                            (x + w * 0.42, y + h * 0.3), (x + w * 0.78, y + h * 0.72)], L['paper'])
        draw.text(r[0] + r[2] + 8 * self.s, r[1] + 4 * self.s, label, L['ink'], size=self._font(12))

    def _button(self, sh, r, label, primary=False):
        hot = point_in_rect(*self.mouse, r)
        fill = (L['orange_ink'] if hot else L['orange']) if primary else (L['cream'] if hot else L['paper'])
        draw.rounded_rect(sh, r, 10 * self.s, fill)
        if not primary:
            draw.rounded_outline(sh, r, 10 * self.s, L['orange'] if hot else L['line_strong'])
        size = self._font(12)
        w = draw.text_width(label, size)
        draw.text(r[0] + (r[2] - w) / 2.0, r[1] + (r[3] - size) / 2.0 + 2 * self.s, label,
                  L['paper'] if primary else L['ink'], size=size)

    def _chip(self, sh, r, label, on, size=12):
        draw.rounded_rect(sh, r, r[3] / 2.0, L['teal_tint'] if on else L['paper'])
        draw.rounded_outline(sh, r, r[3] / 2.0, L['teal'] if on else L['line_strong'], dashed_line=not on)
        fs = self._font(size)
        w = draw.text_width(label, fs)
        draw.text(r[0] + (r[2] - w) / 2.0, r[1] + (r[3] - fs) / 2.0 + 2 * self.s, label,
                  L['teal_ink'] if on else L['muted'], size=fs)

    def _field(self, sh, r, text_value, active):
        draw.rounded_rect(sh, r, 8 * self.s, L['paper'])
        draw.rounded_outline(sh, r, 8 * self.s, L['orange'] if active else L['line_strong'])
        draw.text(r[0] + 10 * self.s, r[1] + (r[3] - self._font(12)) / 2.0 + 2 * self.s, text_value, L['ink'],
                  size=self._font(12))

    def _draw_view(self, sh, key, title):
        rect = getattr(self, 'pane_' + key)
        view = getattr(self, 'view_' + key)
        _name, h, v = VIEWS[key]
        draw.rounded_rect(sh, rect, 14 * self.s, L['paper'])
        draw.rounded_outline(sh, rect, 14 * self.s, L['line'])
        draw.text(rect[0] + 12 * self.s, rect[1] + rect[3] - 22 * self.s, title, L['orange_ink'],
                  size=self._font(11))
        rb = self._view_rect(view, self.mo.box_b, h, v)
        draw.rect(sh, rb, (*L['teal'][:3], 0.12))
        draw.outline(sh, rb, L['teal'])
        draw.lines(sh, _dashed_rect(self._view_rect(view, self.original_box, h, v)), (*L['orange'][:3], 0.45))
        box = self.mo.box_a()
        rn = self._view_rect(view, box, h, v)
        draw.rect(sh, rn, (*L['orange'][:3], 0.32 if self.drag else 0.22))
        draw.outline(sh, rn, L['orange'])
        draw.outline(sh, (rn[0] + 1, rn[1] + 1, rn[2] - 2, rn[3] - 2), L['orange'])
        hx, hy, k = rn[0] + rn[2] / 2.0, rn[1] + rn[3] / 2.0, 6 * self.s
        draw.circle(sh, (hx, hy), 10 * self.s, L['paper'], L['orange'])
        draw.lines(sh, [(hx - k, hy), (hx + k, hy), (hx, hy - k), (hx, hy + k)], L['orange'])
        draw.text(rb[0] + 4 * self.s, rb[1] + rb[3] - 14 * self.s, self.mo.b.name[:28], L['muted'],
                  size=self._font(10))
        for pane, vertical_line, value, label in self.guides:
            if pane != key:
                continue
            x0, y0, w, hh = view.rect
            if vertical_line:
                px = view.to_screen((value, 0.0))[0]
                draw.lines(sh, draw.dashed((px, y0), (px, y0 + hh)), L['blue'])
                draw.pill(sh, px + 40 * self.s, y0 + hh - 6 * self.s, label, L['blue'], L['paper'],
                          size=self._font(10))
            else:
                py = view.to_screen((0.0, value))[1]
                draw.lines(sh, draw.dashed((x0, py), (x0 + w, py)), L['blue'])
                draw.pill(sh, x0 + 44 * self.s, py + 12 * self.s, label, L['blue'], L['paper'], size=self._font(10))
        self._draw_gap(sh, view, box, h, v)

    def _draw_gap(self, sh, view, box, h, v):
        """Cota de proximidade dos dois na vista, como o artefato: no eixo de maior folga não negativa."""
        b = self.mo.box_b
        g = encostar.gaps(box, b)
        gh, gv = g[h], g[v]
        if gh >= -0.0005 and gh >= gv:
            left = box[1][h] <= b[0][h] + 0.0005
            ha, hb = (box[1][h], b[0][h]) if left else (b[1][h], box[0][h])
            mid = (max(box[0][v], b[0][v]) + min(box[1][v], b[1][v])) / 2.0
            p0, p1, value = view.to_screen((ha, mid)), view.to_screen((hb, mid)), gh
        elif gv >= -0.0005:
            below = box[1][v] <= b[0][v] + 0.0005
            va, vb = (box[1][v], b[0][v]) if below else (b[1][v], box[0][v])
            mid = (max(box[0][h], b[0][h]) + min(box[1][h], b[1][h])) / 2.0
            p0, p1, value = view.to_screen((mid, va)), view.to_screen((mid, vb)), gv
        else:
            return
        draw.lines(sh, [p0, p1], L['teal_ink'])
        draw.pill(sh, (p0[0] + p1[0]) / 2.0, (p0[1] + p1[1]) / 2.0, f"{_mm(max(0.0, value))} mm",
                  L['teal_ink'], L['paper'], size=self._font(11))

    def _draw(self):
        sh = draw.begin()
        s = self.s
        x, y, w, h = self.panel
        draw.rounded_rect(sh, (x + 4 * s, y - 8 * s, w, h), 24 * s, L['shadow'])
        draw.rounded_rect(sh, self.panel, 24 * s, L['cream'])
        tb = self.title_bar
        draw.rounded_rect(sh, tb, 24 * s, L['paper'])
        draw.rect(sh, (tb[0], tb[1], tb[2], tb[3] / 2.0), L['paper'])
        draw.lines(sh, [(tb[0], tb[1]), (tb[0] + tb[2], tb[1])], L['line'])
        draw.text(self.title_pos[0], self.title_pos[1], self._title(), L['ink'], size=self._font(15))
        bc = self.button_close
        cx, cy, k = bc[0] + bc[2] / 2, bc[1] + bc[3] / 2, 5 * s
        draw.circle(sh, (cx, cy), bc[2] / 2, L['orange_tint'] if point_in_rect(*self.mouse, bc) else L['cream'])
        draw.lines(sh, [(cx - k, cy - k), (cx + k, cy + k), (cx - k, cy + k), (cx + k, cy - k)], L['ink'])

        self._draw_view(sh, 'front', N_("FRONTAL"))
        self._draw_view(sh, 'plan', N_("PLANTA BAIXA"))

        self._checkbox(sh, self.snap_box, self.snap_on, N_("Ímã (snap) ligado"))
        hint_x = self.snap_box[0] + 34 * s + draw.text_width(N_("Ímã (snap) ligado"), self._font(12)) + 12 * s
        draw.text(hint_x, self.snap_box[1] + 4 * s, SNAP_HINT, L['muted'], size=self._font(10))
        shown = self._shown_side()
        for side, r in self.side_chips:
            self._chip(sh, r, encostar.SIDE_LABELS[side], side == shown)
        if self.side is None:
            last = self.side_chips[-1][1]
            draw.text(last[0] + last[2] + 10 * s, last[1] + 10 * s, N_("Posição livre (arrastada)."), L['muted'],
                      size=self._font(10))
        draw.text(self.gap_label_pos[0], self.gap_label_pos[1], N_("Afastamento"), L['ink'], size=self._font(12))
        gap_value = self.gap if self.side else max(
            0.0, encostar.gaps(self.mo.box_a(), self.mo.box_b)[encostar.SIDE_AXIS[shown]])
        active = self.typing == GAP
        self._field(sh, self.gap_field, (self.buffer + "▏") if active else str(_mm(gap_value)), active)
        draw.hb_gpu_draw.draw_text(draw.FONT, self.gap_field[0] + self.gap_field[2] + 8 * s, self.gap_field[1] + 11 * s,
                                   self._font(11), L['muted'], "mm")      # unidade: o Blender traduziria "mm"
        for axis, r in self.align_rows:
            draw.text(r[0], r[1] + 11 * s, encostar.ALIGN_TITLES[axis], L['ink'], size=self._font(12))
        for axis, value, r in self.align_options:
            self._chip(sh, r, dict(encostar.ALIGN_OPTIONS[axis])[value], self.align.get(axis) == value, size=11)
        self._checkbox(sh, self.glue_box, self.glue, tr("Grudar (move junto com “{}”)").format(self.mo.b.name))
        draw.text(self.info_pos[0], self.info_pos[1], self._info_text(), L['muted'], size=self._font(10))
        if self.warning:
            draw.text(self.warning_pos[0], self.warning_pos[1], self.warning, L['danger'], size=self._font(11))
        if self.more:
            self._draw_more(sh)

        f = self.footer
        draw.rounded_rect(sh, f, 24 * s, L['paper'])
        draw.rect(sh, (f[0], f[1] + f[3] / 2.0, f[2], f[3] / 2.0), L['paper'])
        draw.lines(sh, [(f[0], f[1] + f[3]), (f[0] + f[2], f[1] + f[3])], L['line'])
        self._button(sh, self.button_more, N_("Menos opções") if self.more else N_("Mais opções"))
        self._button(sh, self.button_cancel, N_("Cancelar"))
        self._button(sh, self.button_ok, N_("Encostar"), primary=True)
        draw.end()

    def _draw_more(self, sh):
        relative = self.state.show_relative
        values = self.mo.gaps() if relative else self.mo.world_min()
        labels = FIELD_LABELS if relative else ABS_LABELS
        for i, rect in enumerate(self.fields):
            if i == ROTATION:
                label, shown = N_("Rotação"), f"{self.mo.rotation:.1f}°".replace(".", ",")
            elif i == STEP:
                label, shown = N_("Passo"), draw.length_label(self.state.step)
            else:
                label, shown = labels[i], draw.length_label(values[i])
            active = self.typing == i
            self._field(sh, rect, f"{tr(label)}: {(self.buffer + '▏') if active else shown}", active)
        self._button(sh, self.button_mode, N_("Posição relativa") if relative else N_("Posição absoluta"))
        self._button(sh, self.button_save, N_("Salvar posição"))
        for rect, item in zip(self.saved_buttons, self._saved_items()):
            self._button(sh, rect, item.name)
        self._button(sh, self.button_substitute, N_("Substituir"))

    # Ações ------------------------------------------------------------------------------------------------
    def _saved_items(self):
        return list(bpy.context.scene.btm_saved_positions)[-MAX_SAVED_BUTTONS:]

    def _save_position(self, context):
        saved = self.mo.saved()
        items = context.scene.btm_saved_positions
        item = items.add()
        item.name = tr("Posição {}").format(len(items))
        item.delta, item.rotation, item.b_side = saved['delta'], saved['rotation'], saved['b_side']
        self.warning = tr("{} salva ({} em relação a {}).").format(item.name, self.mo.a.name, self.mo.b.name)

    def _apply_saved(self, item):
        self.mo.apply_saved({'delta': tuple(item.delta), 'rotation': item.rotation, 'b_side': item.b_side})
        self.side = None
        self.warning = tr("{} aplicada.").format(item.name)
        self._fit_views()

    def _commit_typing(self):
        if self.typing == GAP:
            if not self._set_gap_typed(self.buffer):
                return False
            self.typing, self.buffer = None, ""
            self._fit_views()
            return True
        try:
            if self.typing == ROTATION:
                text = self.buffer.replace(",", ".").replace("°", "").strip() or "0"
                try:
                    value = float(text)
                except ValueError:          # sem a mensagem crua do Python, em inglês (EC-08)
                    raise ValueError(tr("Valor Inválido: a rotação precisa ser um número em graus (recebido: {}).")
                                     .format(self.buffer)) from None
            else:
                value = units.parse_length(self.buffer, units.get_scene_length_unit(),
                                           allow_negative=self.typing != STEP, allow_zero=self.typing != STEP)
        except ValueError as exc:
            self.warning = str(exc) if str(exc) else N_("Valor inválido")
            return False
        if self.typing == ROTATION:
            self.mo.set_rotation(value)
            if getattr(self, 'side', None):
                self._apply()
        elif self.typing == STEP:
            self.state.step = value
        elif self.state.show_relative:
            self.mo.set_gap(self.typing, value)
            self.side = None
        else:
            self.mo.set_world(self.typing, value)
            self.side = None
        self.typing, self.buffer = None, ""
        self.warning = ""
        self._fit_views()
        return True

    def _confirm(self, context):
        """Grava a pose pedida. O Encostar é um salto, não um arraste: o destino livre vale mesmo com algo no
        caminho; o destino que atravessaria outro objeto não é gravado, e a janela fica aberta dizendo com quem
        (BUG-20261023-5ATK). O campo em edição é gravado antes; valor inválido mantém a janela (BUG-20261023-AMQ5)."""
        from ..collision import guard
        if self.typing is not None and not self._commit_typing():
            return {'RUNNING_MODAL'}
        a, b = self.mo.a, self.mo.b
        side = self._shown_side()
        gap = max(0.0, encostar.gaps(self.mo.box_a(), self.mo.box_b)[encostar.SIDE_AXIS[side]])
        target = self.mo._target_matrix()
        with guard.suspended():                  # o guarda não corrige a prévia no meio da conferência
            a.matrix_world = target
            context.view_layer.update()
            blocked = guard.penetrates(a, self.mo.original_matrix)
            names = ", ".join(f"“{o.name}”" for o in guard.overlapping(a, target)[:4]) if blocked else ""
        if blocked:
            self.warning = tr("Nessa posição, “{}” atravessaria {}. Mude o lado, o afastamento ou o alinhamento."
                              ).format(a.name, names or tr("outro objeto"))
            return {'RUNNING_MODAL'}
        guard.accept(a, target)
        message = tr("“{}” posicionado {} “{}” (folga {} mm)").format(
            a.name, tr(encostar.SIDE_PHRASES[side]), b.name, _mm(gap))
        if self.glue:
            from ..stick import link
            if link.can_stick(a, b) is None:
                link.link_in_place(a, b, encostar.SIDE_FACE[side])
                message += tr(" e grudado")
        self.state.glue, self.state.snap_on = self.glue, self.snap_on
        self._finish(context)
        self.report({'INFO'}, message)
        return {'FINISHED'}

    def _click(self, context, pixel):
        """Clique com o botão esquerdo dentro do painel; devolve o resultado do modal ou None para seguir."""
        if point_in_rect(*pixel, self.button_ok):
            return self._confirm(context)
        if point_in_rect(*pixel, self.button_cancel) or point_in_rect(*pixel, self.button_close):
            self.cancel(context)
            return {'CANCELLED'}
        if point_in_rect(*pixel, self.button_more):
            self.more = not self.more
            self._layout(context)
            self._fit_views()
            return None
        if point_in_rect(*pixel, (self.snap_box[0], self.snap_box[1], 200 * self.s, self.snap_box[3])):
            self.snap_on = not self.snap_on
            return None
        if point_in_rect(*pixel, (self.glue_box[0], self.glue_box[1], 340 * self.s, self.glue_box[3])):
            self.glue = not self.glue
            return None
        for side, rect in self.side_chips:
            if point_in_rect(*pixel, rect):
                self._set_side(side)
                return None
        for axis, value, rect in self.align_options:
            if point_in_rect(*pixel, rect):
                self._set_align(axis, value)
                return None
        if point_in_rect(*pixel, self.gap_field):
            self.typing, self.buffer = GAP, ""
            return None
        if self.more:
            for i, rect in enumerate(self.fields):
                if point_in_rect(*pixel, rect):
                    self.typing, self.buffer = i, ""
                    return None
            if point_in_rect(*pixel, self.button_mode):
                self.state.show_relative = not self.state.show_relative      # só exibição: nada se move
                return None
            if point_in_rect(*pixel, self.button_save):
                self._save_position(context)
                return None
            for rect, item in zip(self.saved_buttons, self._saved_items()):
                if point_in_rect(*pixel, rect):
                    self._apply_saved(item)
                    return None
            if point_in_rect(*pixel, self.button_substitute):
                return self._substitute(context)
        pane = self._pane_at(pixel)
        if pane:
            self._drag_begin(pane, pixel)
        return None

    def modal(self, context, event):
        context.area.tag_redraw()
        pixel = (event.mouse_region_x, event.mouse_region_y)
        over_panel = point_in_rect(pixel[0], pixel[1], self.panel)
        if event.type in NAV_EVENTS and not over_panel:
            return {'PASS_THROUGH'}
        window_drag = getattr(self, 'window_drag', None)
        if window_drag:                                      # arrastando a janela pelo título (BUG-20261023-WWZT)
            start_origin, start_pixel = window_drag
            if event.type == 'MOUSEMOVE':
                self.panel_origin = (start_origin[0] + pixel[0] - start_pixel[0],
                                     start_origin[1] + pixel[1] - start_pixel[1], start_origin[2])
                self._layout(context)
                self._fit_views()
            elif event.type == 'LEFTMOUSE' and event.value == 'RELEASE':
                self.window_drag = None
            elif event.type in {'ESC', 'RIGHTMOUSE'} and event.value == 'PRESS':
                self.panel_origin, self.window_drag = start_origin, None
                self._layout(context)
                self._fit_views()
            return {'RUNNING_MODAL'}
        if event.type == 'MOUSEMOVE':
            self.mouse = pixel
            if getattr(self, 'drag', None):
                self._drag_move(pixel, shift=event.shift)
            return {'RUNNING_MODAL'}
        if event.type == 'LEFTMOUSE' and event.value == 'RELEASE' and getattr(self, 'drag', None):
            self._drag_end()
            return {'RUNNING_MODAL'}
        if self.typing is not None and event.type == 'LEFTMOUSE' and event.value == 'PRESS':
            # Clique fora do campo grava o que foi digitado e segue para o clique (BUG-20261023-AMQ5); o Encostar
            # faz isso por conta própria, para manter a janela aberta se o valor for inválido.
            if not point_in_rect(*pixel, self.button_ok) and not self._commit_typing():
                return {'RUNNING_MODAL'}
        elif self.typing is not None and event.value == 'PRESS':
            if event.type in {'RET', 'NUMPAD_ENTER'}:
                self._commit_typing()
            elif event.type == 'ESC':
                self.typing, self.buffer = None, ""
            elif event.type == 'TAB':
                # Grava e vai ao próximo campo; valor inválido fica no campo com o aviso (questions.md, pergunta 15).
                current = self.typing
                if self.buffer and not self._commit_typing():
                    return {'RUNNING_MODAL'}
                self.typing, self.buffer = (None if current == GAP else (current + 1) % FIELD_COUNT), ""
            elif event.type == 'BACK_SPACE':
                self.buffer = self.buffer[:-1]
            elif event.unicode and event.unicode in "0123456789,.-mc °":
                self.buffer += event.unicode
            return {'RUNNING_MODAL'}
        if event.type == 'LEFTMOUSE' and event.value == 'PRESS':
            if point_in_rect(*pixel, self.title_bar) and not point_in_rect(*pixel, self.button_close):
                x, y, _w, h = self.panel
                self.window_drag = ((x, y, h), pixel)
                return {'RUNNING_MODAL'}
            if over_panel:
                result = self._click(context, pixel)
                if result is not None:
                    return result
            return {'RUNNING_MODAL'}
        if event.value == 'PRESS':
            if event.type in {'RET', 'NUMPAD_ENTER'}:
                return self._confirm(context)
            if event.type in {'ESC', 'RIGHTMOUSE'}:
                self.cancel(context)
                return {'CANCELLED'}
            if event.type == 'TAB':
                self.typing, self.buffer = GAP, ""
            if event.type in ARROWS:
                delta = reposition.step_delta(event.type, self.state.step)
                if delta is not None:
                    self.mo.nudge(delta)
                    self.side = None
                    self.warning = ""
                    self._fit_views()
        return {'RUNNING_MODAL'}

    def _substitute(self, context):
        """Fecha a janela com a posição atual e abre a escolha do módulo que vai ocupar o lugar de A (D-23)."""
        a_name, b_name = self.mo.a.name, self.mo.b.name
        self._finish(context)
        bpy.ops.caffmob.move_over_substitute('INVOKE_DEFAULT', a_name=a_name, b_name=b_name)
        return {'FINISHED'}


classes = (BTM_OT_MoveOverDialog,)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
