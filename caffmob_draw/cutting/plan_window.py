"""Janela própria do plano de corte (027, T009; RF-01).

Abre uma janela do sistema pelo caminho comum dos editores (`canvas2d.window.open_window`) e desenha as chapas do
resultado do otimizador num handler `POST_PIXEL` do Image Editor: chapa, refilo, peças coloridas por módulo, nome e
medidas de cada peça, aproveitamento. O painel lateral traz a navegação entre chapas, o resumo, a lista de peças da
chapa atual e as exportações que já existem (`caffmob.export_cut_plan_json`, `caffmob.export_parts_csv`).

O plano vem do cache da cena (`btm_nesting_json_cache`, escrito por `operators/ops_cutting.calculate`); o operador
`caffmob.cut_plan_window` calcula de novo quando não há cache ou quando o projeto mudou (`cut_plan_stale`). Esta
janela passa a ser o caminho de entrada do plano de corte: o botão da barra lateral abre ela em vez de só calcular.

A geometria e o hit test ficam em `plan_window_core.py` (Python puro, testável sem o Blender).
"""

import bpy  # type: ignore

from ..canvas2d import draw
from ..canvas2d import window as canvas_window
from ..data.i18n import tr
from ..operators import ops_cutting
from . import plan_window_core as core
from .plan_render import module_color

CATEGORIA = "Plano de Corte"
TOPO = 30                       # faixa do cabeçalho desenhado, em pixels
RODAPE = 26                     # faixa do rodapé (aproveitamento e contagem)
PASSO_ZOOM = 1.25
COR = {
    'fundo': (0.09, 0.10, 0.11, 1.0),
    'faixa': (0.13, 0.14, 0.16, 1.0),
    'chapa': (0.17, 0.18, 0.20, 1.0),
    'borda': (0.94, 0.48, 0.16, 1.0),
    'refilo': (1.0, 1.0, 1.0, 0.22),
    'texto': (0.93, 0.93, 0.93, 1.0),
    'mudo': (0.62, 0.63, 0.66, 1.0),
    'hover': (1.0, 0.76, 0.20, 1.0),
    'selecionado': (0.35, 0.85, 1.0, 1.0),
    'contorno': (0.06, 0.06, 0.08, 1.0),
    'erro': (1.0, 0.42, 0.36, 1.0),
}

_session = []


class Sessao:
    """Janela do plano de corte aberta: chapas, chapa atual, vista e seleção."""

    def __init__(self, payload):
        self.window_ptr = 0
        self.area_ptr = 0
        self.restore_area_type = None     # quando a janela ocupa uma área da janela atual
        self.sheets = core.sheets_of(payload)
        self.stats = dict((payload or {}).get('stats') or {})
        self.unplaced = list((payload or {}).get('unplaced') or [])
        self.index = 0
        self.view = None
        self.hover = None                 # peça sob o cursor
        self.selected = None              # peça escolhida no clique ou na lista
        self.hits = []                    # [(retângulo em pixels, peça)] do último desenho

    def sheet(self):
        return self.sheets[self.index] if 0 <= self.index < len(self.sheets) else None


def sessao():
    return _session[0] if _session else None


def _load(context):
    """Lê o cache da cena, calculando o plano quando ele falta ou está desatualizado."""
    payload = ops_cutting.cached_result(context.scene)
    settings = getattr(context.scene, 'btm_settings', None)
    if payload is None or getattr(settings, 'cut_plan_stale', False):
        ops_cutting.calculate(context)
        payload = ops_cutting.cached_result(context.scene)
    return payload


def _message_missing():
    return tr("O Plano de Corte precisa de uma janela do Blender aberta.")


def open_window(context):
    """Abre a janela do plano de corte e devolve a sessão; levanta RuntimeError sem peças ou sem janela."""
    payload = _load(context)
    if not core.sheets_of(payload):
        raise RuntimeError(tr("Nenhuma peça de marcenaria encontrada no projeto."))
    s = Sessao(payload)
    canvas_window.open_window(context, s, _message_missing())
    _session[:] = [s]
    canvas_window.focus_tab(canvas_window.editor_area(context, s)[1], CATEGORIA)
    return s


def close(context):
    s = sessao()
    if s is None:
        return
    canvas_window.close_later(s.window_ptr, s.area_ptr, s.restore_area_type)
    _session[:] = []


def reload(context):
    """Recalcula o plano e mantém a janela aberta, preservando a chapa atual."""
    s = sessao()
    payload = ops_cutting.cached_result(context.scene)
    if payload is None or getattr(context.scene.btm_settings, 'cut_plan_stale', False) or s is None:
        payload = _load(context)
    if s is None:
        return None
    s.sheets = core.sheets_of(payload)
    s.stats = dict((payload or {}).get('stats') or {})
    s.unplaced = list((payload or {}).get('unplaced') or [])
    s.index = min(s.index, max(0, len(s.sheets) - 1))
    s.hover = s.selected = None
    s.view = None
    return s


def go_to(index):
    s = sessao()
    if s is None or not s.sheets:
        return
    s.index = max(0, min(int(index), len(s.sheets) - 1))
    s.hover = s.selected = None
    s.view = None


def _region_rect(region):
    """Retângulo de desenho entre o cabeçalho e o rodapé."""
    height = max(1.0, region.height - TOPO - RODAPE)
    return (0.0, float(RODAPE), float(region.width), height)


def _ensure_view(region, s):
    """Vista da chapa para a região atual; devolve None quando não há região nem vista ainda."""
    sheet = s.sheet()
    if sheet is None:
        return None
    if region is None:
        return s.view
    if s.view is None or tuple(s.view.rect) != _region_rect(region):
        s.view = core.sheet_view(_region_rect(region), sheet)
    return s.view


def _text_in(ctx, x, y, value, color, size=11):
    """Texto só quando cabe: `ctx` é (pixels disponíveis) e devolve True quando desenhou."""
    if draw.text_width(value, size) > ctx:
        return False
    draw.text(x, y, value, color, size=size)
    return True


def draw_plan(context):
    """Desenho da janela (handler POST_PIXEL do Image Editor)."""
    s = sessao()
    region = context.region
    sheet = s.sheet() if s is not None else None
    if s is None or region is None or sheet is None:
        return
    view = _ensure_view(region, s)
    if view is None:
        return
    sh = draw.begin()
    draw.rect(sh, (0, 0, region.width, region.height), COR['fundo'])

    # Cabeçalho: título da chapa e navegação  <  2/5  >
    draw.rect(sh, (0, region.height - TOPO, region.width, TOPO), COR['faixa'])
    draw.text(12, region.height - TOPO + 9, core.sheet_title(sheet, s.index, len(s.sheets)), COR['texto'], size=12)
    nav = tr("‹  ↑  ↓  →  roda: zoom  ·  arraste: mover  ·  Esc: fechar")
    if draw.text_width(nav, 11) < region.width * 0.45:
        draw.text(region.width - draw.text_width(nav, 11) - 12, region.height - TOPO + 10, nav, COR['mudo'])

    # Chapa e refilo
    (x0, y0), (x1, y1) = core.bounds(sheet)
    a, b = view.to_screen((x0, y0)), view.to_screen((x1, y1))
    body = (min(a[0], b[0]), min(a[1], b[1]), abs(b[0] - a[0]), abs(b[1] - a[1]))
    draw.rect(sh, body, COR['chapa'])
    draw.outline(sh, body, COR['borda'])
    refilos = sheet.get('refilos') or {}
    if refilos:
        lo = view.to_screen((refilos.get('left', 0.0), refilos.get('bottom', 0.0)))
        hi = view.to_screen((x1 - refilos.get('right', 0.0), y1 - refilos.get('top', 0.0)))
        cantos = [(lo[0], lo[1]), (hi[0], lo[1]), (hi[0], hi[1]), (lo[0], hi[1])]
        tracejado = []
        for i in range(4):
            tracejado += draw.dashed(cantos[i], cantos[(i + 1) % 4])
        draw.lines(sh, tracejado, COR['refilo'])

    # Peças: cor por módulo, nome e medidas quando cabem
    s.hits = []
    for part in core.placed(sheet):
        pa, pb = view.to_screen((part['x'], part['y'])), view.to_screen(
            (part['x'] + part['width'], part['y'] + part['height']))
        r = (min(pa[0], pb[0]), min(pa[1], pb[1]), abs(pb[0] - pa[0]), abs(pb[1] - pa[1]))
        s.hits.append((r, part))
        base = module_color(part['module'])
        color = tuple(base[:3]) + (0.55,) if part is s.hover or part is s.selected else base
        draw.rect(sh, r, color)
        draw.outline(sh, r, COR['contorno'])
        if part is s.selected:
            draw.outline(sh, (r[0] - 1, r[1] - 1, r[2] + 2, r[3] + 2), COR['selecionado'])
        elif part is s.hover:
            draw.outline(sh, (r[0] - 1, r[1] - 1, r[2] + 2, r[3] + 2), COR['hover'])
        if r[2] > 34 and r[3] > 16:
            _text_in(r[2] - 6, r[0] + 4, r[1] + r[3] - 14, part['name'], COR['texto'], size=10)
        if r[2] > 34 and r[3] > 30:
            _text_in(r[2] - 6, r[0] + 4, r[1] + 6, core.part_size_label(part), COR['texto'], size=10)

    # Rodapé: aproveitamento e contagem
    draw.rect(sh, (0, 0, region.width, RODAPE), COR['faixa'])
    info = core.summary(sheet)
    rodape = tr("{} peça(s) · aproveitamento {}% · {} m² aproveitados").format(
        info['parts'], f"{info['utilization']:.1f}", f"{info['used_area_m2']:.3f}")
    draw.text(12, 8, rodape, COR['texto'], size=11)
    if s.unplaced:
        aviso = tr("{} peça(s) não couberam na chapa").format(len(s.unplaced))
        draw.text(region.width - draw.text_width(aviso, 11) - 12, 8, aviso, COR['erro'], size=11)
    draw.end()


def hit_test(region, x, y):
    """Peça sob o ponto da região, usando os retângulos do último desenho."""
    s = sessao()
    if s is None:
        return None
    for rect, part in reversed(s.hits):
        if rect[0] <= x <= rect[0] + rect[2] and rect[1] <= y <= rect[1] + rect[3]:
            return part
    return None


# Operadores ------------------------------------------------------------------------------------------------------

class BTM_OT_CutPlanWindow(bpy.types.Operator):
    """Abre o plano de corte numa janela própria, com as chapas e as peças desenhadas"""
    bl_idname = "caffmob.cut_plan_window"
    bl_label = "Abrir Plano de Corte"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        try:
            open_window(context)
        except RuntimeError as exc:
            self.report({'ERROR'}, str(exc))
            return {'CANCELLED'}
        return {'FINISHED'}


class BTM_OT_CutPlanGo(bpy.types.Operator):
    """Mostra outra chapa do plano na janela"""
    bl_idname = "caffmob.cut_plan_go"
    bl_label = "Ir para a chapa"
    bl_options = {'REGISTER', 'INTERNAL'}

    index: bpy.props.IntProperty(default=0)  # type: ignore

    def execute(self, context):
        go_to(self.index)
        return {'FINISHED'}


class BTM_OT_CutPlanStep(bpy.types.Operator):
    """Passa para a chapa seguinte ou anterior"""
    bl_idname = "caffmob.cut_plan_step"
    bl_label = "Próxima chapa"
    bl_options = {'REGISTER', 'INTERNAL'}

    delta: bpy.props.IntProperty(default=1)  # type: ignore

    def execute(self, context):
        s = sessao()
        if s is None or not s.sheets:
            return {'CANCELLED'}
        go_to(s.index + self.delta)
        return {'FINISHED'}


class BTM_OT_CutPlanZoom(bpy.types.Operator):
    """Aproxima, afasta ou reenquadra a chapa na janela"""
    bl_idname = "caffmob.cut_plan_zoom"
    bl_label = "Zoom do plano de corte"
    bl_options = {'REGISTER', 'INTERNAL'}

    factor: bpy.props.FloatProperty(default=1.0)  # type: ignore
    fit: bpy.props.BoolProperty(default=False)  # type: ignore

    def execute(self, context):
        s = sessao()
        if s is None or context.area is None:
            return {'CANCELLED'}
        if self.fit:
            s.view = None
            return {'FINISHED'}
        view = _ensure_view(context.region, s)
        if view is None:
            return {'CANCELLED'}
        view.zoom(self.factor)
        return {'FINISHED'}


class BTM_OT_CutPlanSelect(bpy.types.Operator):
    """Seleciona uma peça da chapa pelo identificador"""
    bl_idname = "caffmob.cut_plan_select"
    bl_label = "Selecionar peça do plano"
    bl_options = {'REGISTER', 'INTERNAL'}

    part_id: bpy.props.StringProperty(default="")  # type: ignore

    def execute(self, context):
        s = sessao()
        sheet = s.sheet() if s is not None else None
        if sheet is None:
            return {'CANCELLED'}
        for part in core.placed(sheet):
            if part['part_id'] == self.part_id:
                s.selected = part
                return {'FINISHED'}
        s.selected = None
        return {'CANCELLED'}


class BTM_OT_CutPlanReload(bpy.types.Operator):
    """Recalcula o plano de corte com o projeto atual e atualiza a janela"""
    bl_idname = "caffmob.cut_plan_reload"
    bl_label = "Recalcular plano de corte"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        s = reload(context)
        if s is None:
            self.report({'ERROR'}, tr("A janela do plano de corte não está aberta."))
            return {'CANCELLED'}
        if not s.sheets:
            self.report({'WARNING'}, tr("Nenhuma peça de marcenaria encontrada no projeto."))
            return {'CANCELLED'}
        if s.unplaced:
            self.report({'WARNING'}, tr("{} peça(s) não couberam na chapa.").format(len(s.unplaced)))
        return {'FINISHED'}


class BTM_OT_CutPlanClose(bpy.types.Operator):
    """Fecha a janela do plano de corte"""
    bl_idname = "caffmob.cut_plan_close"
    bl_label = "Fechar plano de corte"
    bl_options = {'REGISTER', 'INTERNAL'}

    def execute(self, context):
        close(context)
        return {'FINISHED'}


class BTM_OT_CutPlanModal(bpy.types.Operator):
    """Navegação da janela do plano de corte: roda dá zoom, arraste move, clique escolhe a peça, Esc fecha"""
    bl_idname = "caffmob.cut_plan_modal"
    bl_label = "Plano de Corte"
    bl_options = {'REGISTER', 'INTERNAL'}

    _drag = None

    def invoke(self, context, event):
        s = sessao()
        if s is None or not canvas_window.is_editor_area(context, s):
            return {'CANCELLED'}
        self._drag = None
        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}

    def modal(self, context, event):
        s = sessao()
        if s is None or not canvas_window.window_alive(context, s):
            return {'CANCELLED'}
        area = context.area
        if event.type == 'ESC':
            close(context)
            return {'CANCELLED'}
        if event.type == 'MOUSEMOVE':
            if self._drag is not None:
                dx, dy = event.mouse_region_x - self._drag[0], event.mouse_region_y - self._drag[1]
                if abs(dx) + abs(dy) >= 1:
                    view = _ensure_view(context.region, s)
                    if view is not None:
                        view.pan(dx, dy)
                    self._drag = (event.mouse_region_x, event.mouse_region_y)
                    area.tag_redraw()
                return {'RUNNING_MODAL'}
            part = hit_test(context.region, event.mouse_region_x, event.mouse_region_y)
            if part is not s.hover:
                s.hover = part
                area.tag_redraw()
            return {'PASS_THROUGH'}
        if event.type in {'WHEELUPMOUSE', 'WHEELDOWNMOUSE'}:
            view = _ensure_view(context.region, s)
            if view is not None:
                factor = PASSO_ZOOM if event.type == 'WHEELUPMOUSE' else 1.0 / PASSO_ZOOM
                view.zoom(factor, (event.mouse_region_x, event.mouse_region_y))
            area.tag_redraw()
            return {'RUNNING_MODAL'}
        if event.type == 'MIDDLEMOUSE':
            if event.value == 'PRESS':
                self._drag = (event.mouse_region_x, event.mouse_region_y)
            else:
                self._drag = None
            return {'RUNNING_MODAL'}
        if event.type == 'LEFTMOUSE' and event.value == 'PRESS':
            s.selected = hit_test(context.region, event.mouse_region_x, event.mouse_region_y)
            area.tag_redraw()
            return {'RUNNING_MODAL'}
        if event.type in {'HOME', 'F'}:
            s.view = None
            area.tag_redraw()
            return {'RUNNING_MODAL'}
        if event.type in {'DOWN_ARROW', 'LEFT_ARROW', 'UP_ARROW', 'RIGHT_ARROW'}:
            step = -1 if event.type in {'DOWN_ARROW', 'LEFT_ARROW'} else 1
            go_to(s.index + step)
            area.tag_redraw()
            return {'RUNNING_MODAL'}
        return {'PASS_THROUGH'}


# Painéis da janela ------------------------------------------------------------------------------------------------

class BTM_PT_CutPlanHeader(bpy.types.Panel):
    """Cabeçalho da janela: chapa atual, navegação, zoom e fechar."""
    bl_idname = "BTM_PT_CutPlanHeader"
    bl_label = "▦ Plano de Corte"
    bl_space_type = 'IMAGE_EDITOR'
    bl_region_type = 'UI'
    bl_category = CATEGORIA

    def draw(self, context):
        layout = self.layout
        s = sessao()
        if s is None or not s.sheets:
            layout.label(text=tr("Nenhuma chapa no plano."), icon='INFO')
            return
        sheet = s.sheet()
        col = layout.column(align=True)
        col.label(text=core.sheet_title(sheet, s.index, len(s.sheets)), icon='MESH_PLANE')
        nav = col.row(align=True)
        nav.operator("caffmob.cut_plan_step", text="", icon='TRIA_LEFT').delta = -1
        nav.label(text=tr("{} de {}").format(s.index + 1, len(s.sheets)))
        nav.operator("caffmob.cut_plan_step", text="", icon='TRIA_RIGHT').delta = 1
        zoom = col.row(align=True)
        zoom.operator("caffmob.cut_plan_zoom", text="", icon='ZOOM_IN').factor = PASSO_ZOOM
        zoom.operator("caffmob.cut_plan_zoom", text="", icon='ZOOM_OUT').factor = 1.0 / PASSO_ZOOM
        op = zoom.operator("caffmob.cut_plan_zoom", text="Enquadrar", icon='FULLSCREEN_ENTER')
        op.fit = True
        col.operator("caffmob.cut_plan_close", text="Fechar", icon='CANCEL')


class BTM_PT_CutPlanSummary(bpy.types.Panel):
    """Resumo do plano e aviso das peças que não couberam."""
    bl_idname = "BTM_PT_CutPlanSummary"
    bl_label = "Resumo"
    bl_space_type = 'IMAGE_EDITOR'
    bl_region_type = 'UI'
    bl_category = CATEGORIA
    bl_parent_id = "BTM_PT_CutPlanHeader"

    def draw(self, context):
        layout = self.layout
        s = sessao()
        if s is None:
            return
        stats = s.stats
        col = layout.column(align=True)
        col.label(text=tr("Chapas: {}").format(stats.get('sheets_count', len(s.sheets))))
        col.label(text=tr("Peças posicionadas: {}").format(stats.get('total_placed_parts', 0)))
        col.label(text=tr("Aproveitamento: {}%").format(f"{float(stats.get('utilization_percentage', 0.0)):.2f}"))
        col.label(text=tr("Sobra: {} m²").format(f"{float(stats.get('waste_area_m2', 0.0)):.3f}"))
        if s.unplaced:
            aviso = layout.box()
            aviso.alert = True
            aviso.label(text=tr("{} peça(s) não couberam na chapa:").format(len(s.unplaced)), icon='ERROR')
            for item in s.unplaced[:6]:
                aviso.label(text=tr("{} › {}").format(item.get('name', ''), item.get('reason', '')))
        layout.operator("caffmob.cut_plan_reload", text="Recalcular plano", icon='FILE_REFRESH')
        row = layout.row(align=True)
        row.operator("caffmob.export_cut_plan_json", text="JSON", icon='EXPORT')
        row.operator("caffmob.export_parts_csv", text="CSV", icon='SPREADSHEET')


class BTM_PT_CutPlanSheets(bpy.types.Panel):
    """Chapas do plano, com material, espessura e aproveitamento."""
    bl_idname = "BTM_PT_CutPlanSheets"
    bl_label = "Chapas"
    bl_space_type = 'IMAGE_EDITOR'
    bl_region_type = 'UI'
    bl_category = CATEGORIA
    bl_parent_id = "BTM_PT_CutPlanHeader"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        s = sessao()
        if s is None:
            return
        col = layout.column(align=True)
        for i, sheet in enumerate(s.sheets):
            row = col.row(align=True)
            row.operator("caffmob.cut_plan_go", text=core.sheet_title(sheet, i, len(s.sheets)),
                         emboss=(i == s.index), depress=(i == s.index)).index = i
            row.label(text=f"{core.utilization(sheet):.1f}%")


class BTM_PT_CutPlanParts(bpy.types.Panel):
    """Peças da chapa atual; o clique escolhe a peça no desenho."""
    bl_idname = "BTM_PT_CutPlanParts"
    bl_label = "Peças da chapa"
    bl_space_type = 'IMAGE_EDITOR'
    bl_region_type = 'UI'
    bl_category = CATEGORIA
    bl_parent_id = "BTM_PT_CutPlanHeader"

    def draw(self, context):
        layout = self.layout
        s = sessao()
        sheet = s.sheet() if s is not None else None
        if sheet is None:
            return
        parts = core.placed(sheet)
        layout.label(text=tr("{} peça(s)").format(len(parts)))
        if s.selected is not None:
            box = layout.box()
            box.label(text=core.part_title(s.selected), icon='OBJECT_DATA')
            box.label(text=core.part_size_label(s.selected), icon='DRIVER_DISTANCE')
            edges = [name for name, on in (s.selected.get('edges') or {}).items() if on]
            if edges:
                box.label(text=tr("Fita: {}").format(", ".join(edges)))
        col = layout.column(align=True)
        for part in parts[:24]:
            row = col.row(align=True)
            row.operator("caffmob.cut_plan_select", text=f"{part['name']} · {core.part_size_label(part)}",
                         depress=(part is s.selected)).part_id = part['part_id']
        if len(parts) > 24:
            layout.label(text=tr("… e mais {}").format(len(parts) - 24))


classes = (
    BTM_OT_CutPlanWindow,
    BTM_OT_CutPlanGo,
    BTM_OT_CutPlanStep,
    BTM_OT_CutPlanZoom,
    BTM_OT_CutPlanSelect,
    BTM_OT_CutPlanReload,
    BTM_OT_CutPlanClose,
    BTM_OT_CutPlanModal,
    BTM_PT_CutPlanHeader,
    BTM_PT_CutPlanSummary,
    BTM_PT_CutPlanSheets,
    BTM_PT_CutPlanParts,
)

_draw_handle = []


def _draw():
    if canvas_window.is_editor_area(bpy.context, sessao()):
        draw_plan(bpy.context)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    if not _draw_handle:
        _draw_handle.append(bpy.types.SpaceImageEditor.draw_handler_add(_draw, (), 'WINDOW', 'POST_PIXEL'))


def unregister():
    while _draw_handle:
        bpy.types.SpaceImageEditor.draw_handler_remove(_draw_handle.pop(), 'WINDOW')
    for cls in reversed(classes):
        if cls.is_registered:
            bpy.utils.unregister_class(cls)
