"""Seletor de objetos sobrepostos da viewport 3D (feature 016, T007 a T011; RN-01 a RN-11, RF-01 a RF-14).

Ctrl + Alt + clique na viewport (ou o item do menu de contexto) abre um painel com os objetos `MESH` empilhados sob o
cursor, do mais próximo ao mais distante. Na lista:
- setas e o mouse movem o foco, que aparece destacado na viewport pela caixa envolvente (RN-04);
- clique na linha, `+`, `-`, `Ctrl+A` e `Ctrl+/` marcam o que entra na seleção (RF-10, RF-12);
- `I` isola o item em foco, escondendo o resto do view layer e devolvendo tudo ao sair (RN-05);
- `Enter` soma à seleção anterior o que está marcado e tira o que foi desmarcado, com o item em foco como ativo
  quando ele está marcado (RF-10, RF-12); `Esc` e o botão direito devolvem seleção, ativo e visibilidade ao estado da
  abertura (RN-03). Nada é gravado na cena (RN-10), por isso `{'INTERNAL'}`.

O raio é por objeto (`Object.ray_cast` na malha avaliada), porque `scene.ray_cast` devolve só o primeiro impacto
(RN-02). O desenho reaproveita `canvas2d/draw.py` no painel (`POST_PIXEL`) e a caixa envolvente em `POST_VIEW`.
"""

import bpy  # type: ignore
import gpu  # type: ignore
from bpy_extras import view3d_utils  # type: ignore
from gpu_extras.batch import batch_for_shader  # type: ignore
from mathutils import Vector  # type: ignore

from .. import compat
from ..canvas2d import draw
from ..data.i18n import N_, tr
from . import overlap_core

FOCUS_COLOR = (1.0, 0.72, 0.1, 1.0)
_EDGES = ((0, 1), (1, 2), (2, 3), (3, 0), (4, 5), (5, 6), (6, 7), (7, 4), (0, 4), (1, 5), (2, 6), (3, 7))
_NAV_EVENTS = {'MIDDLEMOUSE', 'TRACKPADPAN', 'TRACKPADZOOM', 'MOUSEROTATE', 'NDOF_MOTION'}

_addon_keymaps = []
_active = None          # seletor aberto, para o cancelamento externo (D-10)


def hits_along(context, origin, direction):
    """Objetos `MESH` visíveis e selecionáveis que o raio cruza, do mais próximo ao mais distante (D-03).

    O filtro por `MESH` vem antes de qualquer avaliação: `ray_cast` em curva já derrubou o Blender numa sonda.
    """
    depsgraph = context.evaluated_depsgraph_get()
    found = []
    for obj in context.view_layer.objects:
        try:
            if obj.type != 'MESH' or obj.hide_select or not obj.visible_get():
                continue
            evaluated = obj.evaluated_get(depsgraph)
            inverse = evaluated.matrix_world.inverted()
            hit, location, _normal, _index = evaluated.ray_cast(inverse @ origin, inverse.to_3x3() @ direction)
            if hit:
                found.append(((evaluated.matrix_world @ location - origin).length, obj))
        except (ReferenceError, RuntimeError, ValueError):
            continue
    return overlap_core.rank(found)


def snapshot_state(context):
    """Seleção, ativo e visibilidade do view layer na abertura, para devolver tudo no cancelar."""
    selection = [obj for obj in context.view_layer.objects if obj.select_get()]
    return {
        'selection': selection,
        'active': context.view_layer.objects.active,
        'hidden': {obj: obj.hide_get() for obj in context.view_layer.objects},
    }


def apply_selection(context, objects, active=None):
    """Deixa selecionado exatamente `objects`, com `active` como objeto ativo."""
    for obj in context.view_layer.objects:
        obj.select_set(False)
    for obj in objects:
        try:
            obj.select_set(True)
        except (ReferenceError, RuntimeError):
            continue
    context.view_layer.objects.active = active


def restore_state(context, state):
    """Devolve a visibilidade e depois a seleção que existiam na abertura."""
    restore_visibility(context, state['hidden'])
    apply_selection(context, state['selection'], state['active'])


def isolate(context, hidden, focus):
    """Esconde tudo menos `focus`, guardando o estado original de cada objeto (RN-05)."""
    for obj, was_hidden in hidden.items():
        try:
            obj.hide_set(True if obj is not focus else was_hidden)
        except (ReferenceError, RuntimeError):
            continue
    context.view_layer.update()


def restore_visibility(context, hidden):
    for obj, was_hidden in hidden.items():
        try:
            obj.hide_set(was_hidden)
        except (ReferenceError, RuntimeError):
            continue
    context.view_layer.update()


def cancel_active():
    """Fecha o seletor aberto, se houver, devolvendo o estado da abertura (D-10)."""
    global _active
    selector, _active = _active, None
    if selector is None:
        return
    try:
        selector.cancel(bpy.context)
    except (ReferenceError, RuntimeError, AttributeError):
        pass


def _viewport_region(context):
    """Região WINDOW e `region_3d` da área 3D, mesmo quando a ação vem do popup do menu de contexto (D-08)."""
    area = context.area if context.area is not None and context.area.type == 'VIEW_3D' else None
    window = context.window
    if area is None and window is not None and window.screen is not None:
        area = next((each for each in window.screen.areas if each.type == 'VIEW_3D'), None)
    if area is None:
        return None, None
    region = next((each for each in area.regions if each.type == 'WINDOW'), None)
    space = area.spaces.active
    return region, (space.region_3d if space is not None else None)


def _cursor_point(context, event, region):
    """Ponto do cursor na região da viewport (D-08).

    `Event.mouse_x/mouse_y` são coordenadas da janela, então servem tanto ao atalho quanto ao menu de contexto (onde
    `mouse_region_x/y` vêm relativos ao popup). `Window.mouse_x` não existe mais no Blender 5.2. Fora da região, vale
    o centro dela.
    """
    if event is not None and region is not None:
        point = (event.mouse_x - region.x, event.mouse_y - region.y)
        if 0 <= point[0] <= region.width and 0 <= point[1] <= region.height:
            return point
    if event is not None and region is not None:
        point = (event.mouse_region_x, event.mouse_region_y)
        if 0 <= point[0] <= region.width and 0 <= point[1] <= region.height:
            return point
    if region is None:
        return (0.0, 0.0)
    return (region.width / 2.0, region.height / 2.0)


def _alive(obj):
    """Objeto apagado durante a inspeção devolve `ReferenceError`; ele sai da lista sem fechar o seletor."""
    try:
        obj.name
    except ReferenceError:
        return False
    return True


def _name_of(obj):
    try:
        return obj.name
    except ReferenceError:
        return "?"


class BTM_OT_OverlapSelect(bpy.types.Operator):
    """Escolhe entre os objetos sobrepostos sob o cursor, com lista, isolamento e confirmação"""
    bl_idname = "caffmob.overlap_select"
    bl_label = "Selecionar entre sobrepostos"
    bl_options = {'INTERNAL'}

    @classmethod
    def poll(cls, context):
        # Só a área 3D e o modo objeto: dentro do popup do menu de contexto a região não é a da viewport, e o
        # `invoke` resolve a região WINDOW da área por conta própria (D-08).
        return context.area is not None and context.area.type == 'VIEW_3D' and context.mode == 'OBJECT'

    def invoke(self, context, event):
        region, rv3d = _viewport_region(context)
        if region is None or rv3d is None:
            return {'CANCELLED'}
        cancel_active()
        self.anchor = self.mouse = _cursor_point(context, event, region)
        origin = view3d_utils.region_2d_to_origin_3d(region, rv3d, self.mouse)
        direction = view3d_utils.region_2d_to_vector_3d(region, rv3d, self.mouse)
        hits = hits_along(context, origin, direction)
        if not hits:
            self.report({'INFO'}, "Nenhum objeto elegível sob o cursor")
            return {'CANCELLED'}
        self.picker = overlap_core.Picker(hits)
        self.picker.staged = {obj for obj in hits if obj.select_get()}   # o que já estava selecionado vem marcado
        self.state = snapshot_state(context)
        self.isolated = False
        self._handles = [
            bpy.types.SpaceView3D.draw_handler_add(self._draw_focus, (), 'WINDOW', 'POST_VIEW'),
            bpy.types.SpaceView3D.draw_handler_add(self._draw_panel, (), 'WINDOW', 'POST_PIXEL'),
        ]
        global _active
        _active = self
        context.window_manager.modal_handler_add(self)
        if context.area is not None:
            context.area.tag_redraw()
        return {'RUNNING_MODAL'}

    # Ciclo de vida ---------------------------------------------------------------------------------------
    def _shutdown(self, context):
        global _active
        for handle in getattr(self, '_handles', []):
            try:
                bpy.types.SpaceView3D.draw_handler_remove(handle, 'WINDOW')
            except (ReferenceError, RuntimeError):
                pass
        self._handles = []
        if getattr(self, 'isolated', False):
            restore_visibility(context, self.state['hidden'])
            self.isolated = False
        if _active is self:
            _active = None
        if context.area is not None:
            context.area.tag_redraw()

    def cancel(self, context):
        """`Esc` e o botão direito: seleção, ativo e visibilidade exatamente como na abertura (RN-03)."""
        restore_state(context, self.state)
        self._shutdown(context)

    def _confirm(self, context):
        """`Enter`: a seleção de fora da lista continua, a de dentro vira o que está marcado (RF-10, RF-12)."""
        staged = [obj for obj in self.picker.hits if obj in self.picker.staged and _alive(obj)]
        original = [obj for obj in self.state['selection'] if _alive(obj)]
        selection, active = overlap_core.confirm_selection(self.picker.hits, staged, original,
                                                           self.state['active'], self.picker.focused)
        if self.isolated:
            restore_visibility(context, self.state['hidden'])
            self.isolated = False
        apply_selection(context, selection, active)
        self._shutdown(context)
        return {'FINISHED'}

    # Isolamento ------------------------------------------------------------------------------------------
    def _set_isolation(self, context, on):
        if on:
            isolate(context, self.state['hidden'], self.picker.focused)
        else:
            restore_visibility(context, self.state['hidden'])
        self.isolated = on
        if context.area is not None:
            context.area.tag_redraw()

    def _follow_focus(self, context):
        if self.isolated:
            isolate(context, self.state['hidden'], self.picker.focused)

    # Eventos ---------------------------------------------------------------------------------------------
    def _rect(self, context):
        """O painel fica preso ao ponto da abertura, não ao mouse: senão ele foge da linha que se quer clicar."""
        region = context.region
        return overlap_core.panel_rect(self.anchor, (region.width, region.height), len(self.picker.hits))

    def _sync_focus(self, context):
        index = overlap_core.row_at(self.mouse, self._rect(context), self.picker.scroll, len(self.picker.hits))
        if index is None or index == self.picker.focus:
            return
        self.picker.focus = index
        self._follow_focus(context)

    def _click(self, context):
        kind, index = overlap_core.action_at(self.mouse, self._rect(context), self.picker.scroll,
                                             len(self.picker.hits))
        if kind == overlap_core.ROW:
            self.picker.toggle(index)

    def modal(self, context, event):
        if context.region is None or context.area is None:
            self._shutdown(context)
            return {'CANCELLED'}
        context.area.tag_redraw()
        if event.type == 'MOUSEMOVE':
            self.mouse = (event.mouse_region_x, event.mouse_region_y)
            self._sync_focus(context)
            return {'RUNNING_MODAL'}
        if event.type in _NAV_EVENTS:
            return {'PASS_THROUGH'}
        if event.value != 'PRESS':
            return {'RUNNING_MODAL'}
        if event.type in {'ESC', 'RIGHTMOUSE'}:
            self.cancel(context)
            return {'CANCELLED'}
        if event.type in {'RET', 'NUMPAD_ENTER'}:
            return self._confirm(context)
        if event.type in {'UP_ARROW', 'DOWN_ARROW'}:
            self.picker.move(-1 if event.type == 'UP_ARROW' else 1)
            self._follow_focus(context)
            return {'RUNNING_MODAL'}
        if event.type in {'WHEELUPMOUSE', 'WHEELDOWNMOUSE'}:
            self.picker.scroll_by(-1 if event.type == 'WHEELUPMOUSE' else 1)
            return {'RUNNING_MODAL'}
        if event.type == 'I':
            self._set_isolation(context, not self.isolated)
            return {'RUNNING_MODAL'}
        if event.type in {'PLUS', 'EQUAL', 'NUMPAD_PLUS'}:
            self.picker.add(self.picker.focus)
            return {'RUNNING_MODAL'}
        if event.type in {'MINUS', 'NUMPAD_MINUS'}:
            self.picker.remove(self.picker.focus)
            return {'RUNNING_MODAL'}
        ctrl = bool(getattr(event, 'ctrl', False) or getattr(event, 'oskey', False))
        if ctrl and event.type == 'A':
            self.picker.mark_all()
            return {'RUNNING_MODAL'}
        if ctrl and event.type == 'SLASH':
            self.picker.invert()
            return {'RUNNING_MODAL'}
        if event.type == 'LEFTMOUSE':
            self._click(context)
        return {'RUNNING_MODAL'}

    # Desenho ---------------------------------------------------------------------------------------------
    def _draw_panel(self):
        region = bpy.context.region
        if region is None or not getattr(self, 'picker', None) or not self.picker.hits:
            return
        picker = self.picker
        rect = overlap_core.panel_rect(self.anchor, (region.width, region.height), len(picker.hits))
        rows = overlap_core.rows_rect(rect)
        left, bottom = rect[0] + 12, rect[1]
        top = rect[1] + rect[3]
        sh = draw.begin()
        draw.rect(sh, rect, draw.COLORS['panel'])
        draw.outline(sh, rect, draw.COLORS['border'])
        draw.text(left, top - 26, N_("Objetos sobrepostos"), draw.COLORS['text'], size=14)
        draw.text(left, top - 46, tr("{} no ponto").format(len(picker.hits)), draw.COLORS['muted'], size=11)
        draw.text(left, top - 64, N_("Isolamento: ligado") if self.isolated else N_("Isolamento: desligado"),
                  draw.COLORS['moving'] if self.isolated else draw.COLORS['muted'], size=11)
        for row_index, obj in enumerate(picker.visible()):
            index = picker.scroll + row_index
            y = rows[1] + rows[3] - (row_index + 1) * overlap_core.ROW_H
            row = (rows[0], y, rows[2], overlap_core.ROW_H)
            if index == picker.focus:
                draw.rect(sh, row, draw.COLORS['button_hot'])
            box = (row[0] + 8, y + 7, 11, 11)
            if obj in picker.staged:
                draw.rect(sh, box, draw.COLORS['moving'])
            draw.outline(sh, box, draw.COLORS['border'])
            draw.text(row[0] + 28, y + 7, _name_of(obj), draw.COLORS['text'], size=12)
        draw.lines(sh, [(rect[0], bottom + overlap_core.FOOTER), (rect[0] + rect[2], bottom + overlap_core.FOOTER)],
                   draw.COLORS['border'])
        draw.text(left, bottom + 42, N_("Enter aplica  ·  Esc restaura  ·  I isola"), draw.COLORS['muted'], size=10)
        draw.text(left, bottom + 24, N_("Ctrl+A marca tudo  ·  Ctrl+/ inverte  ·  roda rola a lista"),
                  draw.COLORS['muted'], size=10)
        draw.text(left, bottom + 6, N_("Ctrl + Alt + clique abre o seletor"), draw.COLORS['muted'], size=10)
        draw.end()

    def _draw_focus(self):
        obj = getattr(self, 'picker', None) and self.picker.focused
        if obj is None:
            return
        try:
            corners = [obj.matrix_world @ Vector(corner) for corner in obj.bound_box]
        except (ReferenceError, RuntimeError, TypeError):
            return
        coords = [corners[index] for edge in _EDGES for index in edge]
        shader = compat.get_builtin_shader('UNIFORM_COLOR')
        gpu.state.depth_test_set('NONE')
        gpu.state.blend_set('ALPHA')
        gpu.state.line_width_set(2.0)
        batch = batch_for_shader(shader, 'LINES', {'pos': coords})
        shader.bind()
        shader.uniform_float('color', FOCUS_COLOR)
        batch.draw(shader)
        gpu.state.line_width_set(1.0)
        gpu.state.blend_set('NONE')
        gpu.state.depth_test_set('LESS_EQUAL')


classes = (BTM_OT_OverlapSelect,)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    wm = bpy.context.window_manager
    kc = wm.keyconfigs.addon if wm else None
    if kc is None:
        return
    km = kc.keymaps.new(name='3D View', space_type='VIEW_3D')
    kmi = km.keymap_items.new(BTM_OT_OverlapSelect.bl_idname, 'LEFTMOUSE', 'CLICK', ctrl=True, alt=True, head=True)
    _addon_keymaps.append((km, kmi))


def unregister():
    cancel_active()
    for km, kmi in _addon_keymaps:
        try:
            km.keymap_items.remove(kmi)
        except (ReferenceError, RuntimeError):
            pass
    _addon_keymaps.clear()
    for cls in reversed(classes):
        if cls.is_registered:
            bpy.utils.unregister_class(cls)
