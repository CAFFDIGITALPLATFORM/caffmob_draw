"""Clique, hover, rolagem e Esc do painel BIBLIOTECA CAFFMOB (feature 012, T021; feature 014, T030; D-13, D-30).

Itens de keymap em "3D View" na frente (`head=True`), como o HUD: cada evento chama um operador curto, que trata o
clique quando ele cai no painel e devolve `PASS_THROUGH` fora dele (sem modal permanente, o salvamento automático
continua).

- MIN e OPEN (012): o rótulo abre e fecha a coluna; o botão de maximizar abre o retângulo (feature 014).
- MAX (feature 014, RN-09): botões fechar, minimizar e fixar; arrastar o cabeçalho move e arrastar a borda
  redimensiona (o clique vira um modal curto até soltar o botão); a roda rola a grade; abas, fabricantes e coleções
  filtram; a célula seleciona e, arrastada, entra no arraste (T032). Fixo, um clique fora segue para a cena sem
  fechar; solto, fecha como hoje. Esc fecha o retângulo solto.
- O retângulo gravado em `btm_library.rect` passa por `grid_core.clamp_rect` com as áreas ocupadas do HUD (T029).
"""

import bpy  # type: ignore

from ..hb_gpu_draw import get_visible_window_bounds
from . import categories, draw, grid_core, layout_core

_addon_keymaps = []
DRAG_THRESHOLD = 6.0                      # px × escala para a célula virar arraste (D-07)
WHEEL_STEP = 60.0                         # px × escala por passo da roda


def _in_viewport(context):
    return (context.area is not None and context.area.type == 'VIEW_3D' and context.region is not None
            and context.region.type == 'WINDOW' and hasattr(context.window_manager, 'btm_library'))


def _hit(context, event):
    lay = draw.layout(context, context.area, context.region)
    return lay, layout_core.hit(lay, event.mouse_region_x, event.mouse_region_y, maximize_scale=draw._scale(context))


def _hit_max(context, event):
    lay = draw.max_layout(context, context.area)
    return lay, layout_core.hit_max(lay, event.mouse_region_x, event.mouse_region_y, draw._scale(context))


def covers(context, event):
    """O mouse está sobre o painel (rótulo, coluna ou retângulo MAX)? Quem pega eventos da vista consulta isto."""
    if not _in_viewport(context):
        return False
    try:
        if context.window_manager.btm_library.mode == 'MAX':
            return _hit_max(context, event)[1] is not None
        return _hit(context, event)[1] is not None
    except (AttributeError, ReferenceError):
        return False


def _run(op_idname, **props):
    namespace, name = op_idname.split('.')
    operator = getattr(getattr(bpy.ops, namespace, None), name, None)
    if operator is not None and operator.poll():
        operator('INVOKE_DEFAULT', **props)
        return True
    return False


def _bounds(context):
    x_min, x_max, y_min, y_max = get_visible_window_bounds(context.area)
    return (x_min, y_min, x_max - x_min, y_max - y_min)


def dispatch(context, key):
    """O que o item do rótulo ou da coluna faz (também usado pelos testes)."""
    state = context.window_manager.btm_library
    category = layout_core.category_of(key)
    if key == 'LABEL':
        state.open = not state.open
        if state.open:
            categories.invalidate()
        return
    if key == 'MAXIMIZE':
        state.mode = 'MAX'
        return
    state.open = False
    if key == layout_core.CREATE_CABINET:
        _run("caffmob.library_create_cabinet")
    elif key == layout_core.CREATE_CATEGORY:
        _run("caffmob.library_category_create")
    elif key == layout_core.CONVERT_GROUPS:
        _run("caffmob.legacy_groups_convert")
    elif category is not None:
        found = categories.find(category)
        state.category = category
        state.line = found.line if found is not None else 'COZ'
        open_category(context, category)


def open_category(context, category):
    """Conteúdo da categoria na grade do retângulo (T040); o popover fica de reserva (`popover.show`)."""
    state = context.window_manager.btm_library
    state.category, state.tab, state.scroll, state.mode = category, 'BLOCKS', 0.0, 'MAX'


def _toggle_row(state, key):
    """Clique numa linha da coluna de fabricantes ('MAN:<id>' abre/fecha; 'COL:<m>/<c>' filtra a coleção)."""
    if key.startswith('MAN:'):
        man = key[4:]
        state.manufacturer = "" if state.manufacturer == man and not state.collection else man
        state.collection = ""
    elif key.startswith('COL:'):
        man, _sep, col = key[4:].partition('/')
        same = state.manufacturer == man and state.collection == col
        state.manufacturer, state.collection = man, ("" if same else col)
    state.scroll = 0.0


def max_click(context, part, lay, mx, my):
    """Clique numa parte do MAX que não vira modal. Devolve o id da célula pressionada (ou "")."""
    state = context.window_manager.btm_library
    s = draw._scale(context)
    if part == 'CLOSE':
        state.pinned = False
        state.mode = 'MIN'
    elif part == 'MINIMIZE':
        state.mode = 'MIN'
    elif part == 'PIN':
        state.pinned = not state.pinned
    elif part.startswith('TAB:'):
        state.tab, state.scroll = part[4:], 0.0
    elif part == 'SEARCH':
        _run("caffmob.library_search")
    elif part == 'ACCOUNT':
        _run("caffmob.texture_account_menu")
    elif part == 'FOOTER':
        fx, _fy, fw, _fh = lay.footer
        if mx >= fx + fw - 90 * s:
            from ..texture_library import downloads
            downloads.cancel_all()
            draw._catalog().cancel()
    elif part == 'SIDEBAR':
        blocks = state.tab != 'TEXTURES'
        if blocks:
            ctrl = layout_core.hit_blocks_controls(lay.sidebar, mx, my, s)
            if ctrl == layout_core.REPLACE_SELECTED:
                _run("caffmob.library_replace_selected")
                return ""
            if ctrl and ctrl.startswith('MAT:'):
                state.opening_material = ctrl[4:]
                return ""
        rows = layout_core.sidebar_rows(lay.sidebar, draw.sidebar_tree(state), "" if blocks else state.manufacturer,
                                        s)
        key = layout_core.hit_rows(rows, mx, my)
        if key and blocks:
            state.category, state.scroll = key[4:], 0.0
            found = categories.find(state.category)
            state.line = found.line if found is not None else 'COZ'
        elif key:
            _toggle_row(state, key)
    elif part == 'GRID':
        return cell_at(context, lay, mx, my)
    return ""


def cell_at(context, lay, mx, my):
    """Id do item da grade sob o ponto, ou ""."""
    state = context.window_manager.btm_library
    entries = draw.grid_entries(state)
    s = draw._scale(context)
    area = lay.grid
    content = grid_core.content_height(area[2], len(entries), s)
    scroll = grid_core.clamp_scroll(state.scroll, content, area[3])
    index = grid_core.hit_cell(grid_core.visible_cells(area, len(entries), s, scroll), mx, my)
    if index is not None and entries[index]["id"] == draw._more_id:
        draw._catalog().refresh(state.search, state.manufacturer, state.collection, more=True)
        return ""
    return draw.entry_key(entries[index]) if index is not None else ""


class BTM_OT_LibraryClick(bpy.types.Operator):
    """Clique no painel BIBLIOTECA CAFFMOB"""
    bl_idname = "caffmob.library_click"
    bl_label = "Biblioteca CAFFMob"
    bl_options = {'INTERNAL'}

    @classmethod
    def poll(cls, context):
        return _in_viewport(context)

    def invoke(self, context, event):
        state = context.window_manager.btm_library
        if state.mode == 'MAX':
            return self._invoke_max(context, event)
        _lay, key = _hit(context, event)
        if key is None:
            if state.open:
                state.open = False                # clique fora fecha e segue para a seleção
                draw.tag_redraw(context)
            return {'PASS_THROUGH'}
        dispatch(context, key)
        draw.tag_redraw(context)
        return {'FINISHED'}

    def _invoke_max(self, context, event):
        state = context.window_manager.btm_library
        lay, part = _hit_max(context, event)
        mx, my = event.mouse_region_x, event.mouse_region_y
        if part is None:
            state.mode = grid_core.next_mode(state.mode, 'OUTSIDE', state.pinned)
            draw.tag_redraw(context)
            return {'PASS_THROUGH'}              # fixo ou não, o clique fora segue para a cena
        self.start = (mx, my)
        self.rect = tuple(lay.rect)
        self.cell = ""
        if part in ('HEADER', 'LEFT', 'RIGHT', 'TOP', 'BOTTOM'):
            self.action = 'MOVE' if part == 'HEADER' else part
        else:
            self.cell = max_click(context, part, lay, mx, my)
            draw.tag_redraw(context)
            if not self.cell:
                return {'FINISHED'}
            draw._selected['id'] = self.cell
            self.action = 'CELL'
        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}

    def modal(self, context, event):
        if event.type == 'ESC' or (event.type == 'RIGHTMOUSE' and event.value == 'PRESS'):
            if self.action != 'CELL':
                context.window_manager.btm_library.rect = self.rect
            draw.tag_redraw(context)
            return {'CANCELLED'}
        if event.type == 'LEFTMOUSE' and event.value == 'RELEASE':
            draw.tag_redraw(context)
            return {'FINISHED'}
        if event.type != 'MOUSEMOVE':
            return {'RUNNING_MODAL'}
        mx, my = event.mouse_region_x, event.mouse_region_y
        dx, dy = mx - self.start[0], my - self.start[1]
        s = draw._scale(context)
        if self.action == 'CELL':
            if (dx * dx + dy * dy) ** 0.5 >= DRAG_THRESHOLD * s and \
                    _run("caffmob.library_drag", key=self.cell, start_x=mx, start_y=my):
                return {'FINISHED'}              # o arraste segue no modal dele (T032)
            return {'RUNNING_MODAL'}
        bounds, hud = _bounds(context), draw.hud_rects(context, context.area)
        if self.action == 'MOVE':
            rect = grid_core.move(self.rect, dx, dy, bounds, hud, s)
        else:
            rect = grid_core.resize(self.rect, self.action, dx, dy, bounds, hud, s)
        context.window_manager.btm_library.rect = rect
        draw.tag_redraw(context)
        return {'RUNNING_MODAL'}


class BTM_OT_LibraryHover(bpy.types.Operator):
    bl_idname = "caffmob.library_hover"
    bl_label = "Biblioteca CAFFMob (hover)"
    bl_options = {'INTERNAL'}

    @classmethod
    def poll(cls, context):
        return _in_viewport(context)

    def invoke(self, context, event):
        state = context.window_manager.btm_library
        pos = (event.mouse_region_x, event.mouse_region_y)
        same_region = draw._mouse['region'] == context.region.as_pointer()
        if state.mode == 'MAX':
            x, y, w, h = draw.max_rect(context, context.area, state)
            was = same_region and x <= draw._mouse['pos'][0] <= x + w and y <= draw._mouse['pos'][1] <= y + h
            now = x <= pos[0] <= x + w and y <= pos[1] <= y + h
            changed = was or now
        else:
            lay, key = _hit(context, event)
            before = layout_core.hit(lay, *draw._mouse['pos'], maximize_scale=draw._scale(context)) \
                if same_region else None
            changed = key != before
        draw._mouse['pos'] = pos
        draw._mouse['region'] = context.region.as_pointer()
        if changed:
            context.region.tag_redraw()
        return {'PASS_THROUGH'}


class BTM_OT_LibraryScroll(bpy.types.Operator):
    """Rola a grade da BIBLIOTECA CAFFMOB pela roda do mouse"""
    bl_idname = "caffmob.library_scroll"
    bl_label = "Rolar biblioteca"
    bl_options = {'INTERNAL'}

    @classmethod
    def poll(cls, context):
        return _in_viewport(context) and context.window_manager.btm_library.mode == 'MAX'

    def invoke(self, context, event):
        state = context.window_manager.btm_library
        lay, part = _hit_max(context, event)
        if part is None:
            return {'PASS_THROUGH'}              # fora do retângulo: zoom da vista como sempre
        if part != 'GRID':
            return {'FINISHED'}                  # dentro do retângulo, a roda não dá zoom na cena
        s = draw._scale(context)
        step = WHEEL_STEP * s
        delta = -step if event.type == 'WHEELUPMOUSE' else step
        entries = draw.grid_entries(state)
        content = grid_core.content_height(lay.grid[2], len(entries), s)
        state.scroll = grid_core.clamp_scroll(state.scroll + delta, content, lay.grid[3])
        draw.tag_redraw(context)
        return {'FINISHED'}


class BTM_OT_LibraryClose(bpy.types.Operator):
    """Fecha o painel BIBLIOTECA CAFFMOB"""
    bl_idname = "caffmob.library_close"
    bl_label = "Fechar biblioteca"
    bl_options = {'INTERNAL'}

    @classmethod
    def poll(cls, context):
        return _in_viewport(context) and context.window_manager.btm_library.open

    def invoke(self, context, event):
        return self.execute(context)

    def execute(self, context):
        state = context.window_manager.btm_library
        new = grid_core.next_mode(state.mode, 'ESC', state.pinned)
        if new == state.mode:
            return {'PASS_THROUGH'}              # fixo: o Esc segue para quem precisa dele
        state.mode = new
        draw.tag_redraw(context)
        return {'FINISHED'}


class BTM_OT_LibraryBlock(bpy.types.Operator):
    """Botão direito, do meio e gestos do trackpad sobre o painel não chegam à cena"""
    # BUG-20261023-NS3U
    bl_idname = "caffmob.library_block"
    bl_label = "Biblioteca CAFFMob (bloqueio)"
    bl_options = {'INTERNAL'}

    @classmethod
    def poll(cls, context):
        return _in_viewport(context)

    def invoke(self, context, event):
        return {'FINISHED'} if covers(context, event) else {'PASS_THROUGH'}


classes = (BTM_OT_LibraryClick, BTM_OT_LibraryHover, BTM_OT_LibraryScroll, BTM_OT_LibraryClose, BTM_OT_LibraryBlock)

# Mapas processados antes do "3D View" (os mesmos do Mover Sobre): sem os atalhos neles, o clique direito abre o
# menu da cena e o botão do meio gira a vista por cima do painel (BUG-20261023-NS3U).
_EVENTS = ((BTM_OT_LibraryClick.bl_idname, 'LEFTMOUSE', 'PRESS'),
           (BTM_OT_LibraryScroll.bl_idname, 'WHEELUPMOUSE', 'PRESS'),
           (BTM_OT_LibraryScroll.bl_idname, 'WHEELDOWNMOUSE', 'PRESS'),
           (BTM_OT_LibraryBlock.bl_idname, 'RIGHTMOUSE', 'PRESS'),
           (BTM_OT_LibraryBlock.bl_idname, 'MIDDLEMOUSE', 'PRESS'),
           (BTM_OT_LibraryBlock.bl_idname, 'TRACKPADPAN', 'ANY'),
           (BTM_OT_LibraryBlock.bl_idname, 'TRACKPADZOOM', 'ANY'))


def register():
    from ..move_over.ops_drag import VIEW3D_MODE_KEYMAPS
    for cls in classes:
        bpy.utils.register_class(cls)
    wm = bpy.context.window_manager
    kc = wm.keyconfigs.addon if wm else None
    if kc is None:
        return
    km = kc.keymaps.new(name='3D View', space_type='VIEW_3D')
    for idname, event, value in _EVENTS[:3] + ((BTM_OT_LibraryHover.bl_idname, 'MOUSEMOVE', 'ANY'),
                                               (BTM_OT_LibraryClose.bl_idname, 'ESC', 'PRESS')) + _EVENTS[3:]:
        kmi = km.keymap_items.new(idname, event, value, any=(event in ('LEFTMOUSE', 'MOUSEMOVE')), head=True)
        _addon_keymaps.append((km, kmi))
    for name in VIEW3D_MODE_KEYMAPS:
        km = kc.keymaps.new(name=name, space_type='EMPTY')
        for idname, event, value in _EVENTS:
            kmi = km.keymap_items.new(idname, event, value, any=(event == 'LEFTMOUSE'), head=True)
            _addon_keymaps.append((km, kmi))


def unregister():
    for km, kmi in _addon_keymaps:
        try:
            km.keymap_items.remove(kmi)
        except (ReferenceError, RuntimeError):
            pass
    _addon_keymaps.clear()
    for cls in reversed(classes):
        if cls.is_registered:
            bpy.utils.unregister_class(cls)
