"""Janela própria do V-Ray Mesh Measure (027, T010 a T014; RF-02).

Abre uma janela do sistema pelo caminho comum dos editores (`canvas2d.window.open_window`) e desenha a malha medida no
handler `POST_PIXEL` do Image Editor. O painel lateral é a interface inteira: malha e camadas (partes soltas), medidas,
representação, projeção, snap, unidades, views e impressão.

Sem seleção na cena, a janela não abre: o painel da Vista 3D mostra o aviso e o conta-gotas (`Conta-gotas: escolher
malha`), que escolhe a malha com um clique e já abre a janela. A escolha fica na cena (`btm_mesh_measure_target`), para
o projeto lembrar o que estava sendo medido.

Toda a leitura da malha está em `scene.py`, a projeção em `camera.py`, o desenho em `draw.py` e as contas em `core.py`.
"""

import math

import bpy  # type: ignore
from bpy_extras import view3d_utils  # type: ignore

from ..canvas2d import window as canvas_window
from ..data.i18n import N_, tr
from . import core
from . import draw as draw_mod
from . import scene as scene_mod

CATEGORIA = "Mesh Measure"
PASSO_ZOOM = 1.2
ORBIT_GRAUS_POR_PIXEL = 0.35
ARRASTE_MIN_PX = 3.0
PICK_PX = 14.0                  # raio do encaixe no vértice, em pixels
PARTE_PX = 70.0                 # raio para escolher a parte pelo centro, em pixels


# Janela -----------------------------------------------------------------------------------------------------------

def open_window(context, obj=None):
    """Abre (ou reaproveita) a janela para a malha dada. Levanta RuntimeError sem malha ou sem janela."""
    obj = obj or scene_mod.target(context)
    if obj is None or obj.type != 'MESH':
        raise RuntimeError(tr("Selecione uma malha para medir."))
    malha = scene_mod.snapshot(obj)
    if not malha.parts:
        raise RuntimeError(tr("A malha selecionada não tem vértices para medir."))
    session = scene_mod.sessao()
    if session is not None and not canvas_window.window_alive(context, session):
        scene_mod.forget()
        session = None
    if session is None:
        session = scene_mod.keep(scene_mod.Sessao(malha))
        canvas_window.open_window(context, session, _message_missing())
        canvas_window.focus_tab(canvas_window.editor_area(context, session)[1], CATEGORIA)
    else:
        session.malha = malha
        session.fitted = False
        session.hover = session.selected = None
        session.hits.clear()
    scene_mod.set_target(context, obj.name)
    session.obj_name = obj.name
    return session


def _message_missing():
    return tr("O V-Ray Mesh Measure precisa de uma janela do Blender aberta.")


def close(context, session=None):
    """Fecha a janela (ou devolve o tipo da área, quando ela ocupou a janela atual)."""
    session = session or scene_mod.sessao()
    if session is None:
        return
    canvas_window.close_later(session.window_ptr, session.area_ptr, session.restore_area_type)
    scene_mod.forget()


def reload(context, session=None):
    """Relê a malha do objeto escolhido, mantendo câmera, medidas e views."""
    session = session or scene_mod.sessao()
    if session is None:
        return None
    obj = bpy.data.objects.get(session.obj_name) or scene_mod.target(context)
    if obj is None or obj.type != 'MESH':
        return session
    session.malha = scene_mod.snapshot(obj)
    session.obj_name = obj.name
    session.fitted = False
    session.hover = session.selected = None
    session.pending = None
    return session


def go_to_print(session, value=None):
    """Liga ou desliga a visualização de impressão (sem valor, alterna)."""
    session.print_preview = (not session.print_preview) if value is None else bool(value)
    return session.print_preview


# Escolha no desenho -----------------------------------------------------------------------------------------------

def pick_part(session, x, y):
    """Parte visível mais próxima do ponto (pelo centro projetado), dentro do raio de escolha."""
    best, best_distance = None, PARTE_PX
    for part in session.visible_parts():
        point = session.camera.project(part.center, session.rect)
        if point is None:
            continue
        distance = math.hypot(point[0] - x, point[1] - y)
        if distance <= best_distance:
            best, best_distance = part, distance
    return best


def pick_point(session, x, y):
    """Vértice mais próximo do cursor, dentro do raio de encaixe (as extremidades das medidas manuais)."""
    best, best_distance = None, PICK_PX
    for vertex in session.malha.vertices:
        point = session.camera.project(vertex, session.rect)
        if point is None:
            continue
        distance = math.hypot(point[0] - x, point[1] - y)
        if distance <= best_distance:
            best, best_distance = vertex, distance
    return best


def _is_area(context):
    return canvas_window.is_editor_area(context, scene_mod.sessao())


def _draw():
    if _is_area(bpy.context):
        draw_mod.draw_window(bpy.context)


# Modal ------------------------------------------------------------------------------------------------------------

class BTM_OT_MeshMeasureModal(bpy.types.Operator):
    """Navegação da janela: arraste orbita, Shift+arraste move, roda dá zoom, Ctrl+clique mede, Esc fecha"""
    bl_idname = "caffmob.mesh_measure_modal"
    bl_label = "V-Ray Mesh Measure"
    bl_options = {'REGISTER', 'INTERNAL'}

    _press = None
    _last = None
    _modo = 'ORBIT'
    _ctrl = False

    def invoke(self, context, event):
        session = scene_mod.sessao()
        if session is None or not canvas_window.is_editor_area(context, session):
            return {'CANCELLED'}
        self._press = self._last = None
        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}

    def _click(self, session, area, x, y, ctrl):
        if session.print_preview:
            return
        if ctrl:
            point = pick_point(session, x, y)
            if point is None:
                return
            point, _snapped = session.snap(point)
            if session.pending is None:
                session.pending = point
            else:
                session.add_measure(session.pending, point)
        else:
            session.selected = pick_part(session, x, y)
        area.tag_redraw()

    def modal(self, context, event):
        session = scene_mod.sessao()
        if session is None or not canvas_window.window_alive(context, session):
            return {'CANCELLED'}
        area = context.area
        x, y = event.mouse_region_x, event.mouse_region_y
        if event.type == 'ESC' and event.value == 'PRESS':
            close(context, session)
            return {'CANCELLED'}
        if event.type == 'MOUSEMOVE':
            if self._press is not None:
                dx, dy = x - self._last[0], y - self._last[1]
                self._last = (x, y)
                if self._modo == 'PAN':
                    session.camera.pan(dx, dy, session.rect)
                else:
                    session.camera.orbit(dx * ORBIT_GRAUS_POR_PIXEL, dy * ORBIT_GRAUS_POR_PIXEL)
                area.tag_redraw()
                return {'RUNNING_MODAL'}
            part = pick_part(session, x, y) if not session.print_preview else None
            if part is not session.hover:
                session.hover = part
                area.tag_redraw()
            return {'PASS_THROUGH'}
        if event.type == 'MIDDLEMOUSE':
            if event.value == 'PRESS':
                self._press, self._last, self._modo = (x, y), (x, y), 'PAN'
            else:
                self._press = None
            return {'RUNNING_MODAL'}
        if event.type == 'LEFTMOUSE':
            if event.value == 'PRESS':
                self._press, self._last = (x, y), (x, y)
                self._modo = 'PAN' if event.shift else 'ORBIT'
                self._ctrl = bool(event.ctrl)
            elif self._press is not None:
                moved = abs(x - self._press[0]) + abs(y - self._press[1]) >= ARRASTE_MIN_PX
                if not moved:
                    self._click(session, area, x, y, self._ctrl)
                self._press = None
            return {'RUNNING_MODAL'}
        if event.type in {'WHEELUPMOUSE', 'WHEELDOWNMOUSE'}:
            factor = PASSO_ZOOM if event.type == 'WHEELUPMOUSE' else 1.0 / PASSO_ZOOM
            if session.print_preview:
                session.sheet_zoom = max(0.2, min(4.0, session.sheet_zoom * factor))
            else:
                session.camera.zoom(factor)
            area.tag_redraw()
            return {'RUNNING_MODAL'}
        if event.type == 'P' and event.value == 'PRESS':
            go_to_print(session)
            area.tag_redraw()
            return {'RUNNING_MODAL'}
        if event.type == 'F' and event.value == 'PRESS':
            session.fitted = False
            area.tag_redraw()
            return {'RUNNING_MODAL'}
        if event.value == 'PRESS' and event.type in {'ONE', 'TWO', 'THREE', 'FOUR', 'FIVE'}:
            index = {'ONE': 0, 'TWO': 1, 'THREE': 2, 'FOUR': 3, 'FIVE': 4}[event.type]
            session.representation = core.REPRESENTATIONS[index]
            area.tag_redraw()
            return {'RUNNING_MODAL'}
        return {'PASS_THROUGH'}


# Operadores -------------------------------------------------------------------------------------------------------

def _mesh_items(_self, context):
    """Itens do seletor de malha: os objetos de malha da cena."""
    items = [(obj.name, obj.name, "") for obj in scene_mod.mesh_objects(context)]
    return items or [('NENHUMA', tr("Nenhuma malha na cena"), "")]


class BTM_OT_MeshMeasureWindow(bpy.types.Operator):
    """Abre a janela de medição da malha selecionada"""
    bl_idname = "caffmob.mesh_measure_window"
    bl_label = "Abrir V-Ray Mesh Measure"
    bl_options = {'REGISTER'}

    def execute(self, context):
        try:
            open_window(context)
        except RuntimeError as exc:
            self.report({'ERROR'}, str(exc))
            return {'CANCELLED'}
        return {'FINISHED'}


class BTM_OT_MeshMeasureEyedropper(bpy.types.Operator):
    """Escolhe a malha a medir com um clique na Vista 3D"""
    bl_idname = "caffmob.mesh_measure_eyedropper"
    bl_label = "Conta-gotas: escolher malha"
    bl_options = {'REGISTER'}

    @classmethod
    def poll(cls, context):
        return context.area is not None and context.area.type == 'VIEW_3D'

    def invoke(self, context, event):
        context.window_manager.modal_handler_add(self)
        context.window.cursor_set('EYEDROPPER')
        return {'RUNNING_MODAL'}

    def _end(self, context):
        if context.window is not None:
            context.window.cursor_set('DEFAULT')

    def cancel(self, context):
        self._end(context)

    def modal(self, context, event):
        if event.type == 'LEFTMOUSE' and event.value == 'PRESS':
            coord = (event.mouse_region_x, event.mouse_region_y)
            origin = view3d_utils.region_2d_to_origin_3d(context.region, context.region_data, coord)
            direction = view3d_utils.region_2d_to_vector_3d(context.region, context.region_data, coord)
            hit, _location, _normal, _index, obj, _matrix = context.scene.ray_cast(
                context.evaluated_depsgraph_get(), origin, direction)
            self._end(context)
            if not hit or obj is None or obj.type != 'MESH':
                self.report({'WARNING'}, tr("Nenhuma malha sob o cursor."))
                return {'CANCELLED'}
            scene_mod.set_target(context, obj.name)
            try:
                open_window(context, obj)
            except RuntimeError as exc:
                self.report({'ERROR'}, str(exc))
                return {'CANCELLED'}
            return {'FINISHED'}
        if event.type in {'ESC', 'RIGHTMOUSE'} and event.value == 'PRESS':
            self._end(context)
            return {'CANCELLED'}
        return {'PASS_THROUGH'} if event.type in {'MIDDLEMOUSE', 'WHEELUPMOUSE', 'WHEELDOWNMOUSE'} \
            else {'RUNNING_MODAL'}

    def execute(self, context):
        self.report({'WARNING'}, tr("Clique na malha com o conta-gotas, na Vista 3D."))
        return {'CANCELLED'}


class BTM_OT_MeshMeasurePick(bpy.types.Operator):
    """Escolhe qual malha da cena medir e abre a janela"""
    bl_idname = "caffmob.mesh_measure_pick"
    bl_label = "Escolher malha para medir"
    bl_options = {'REGISTER'}

    mesh: bpy.props.EnumProperty(name="Malha", items=_mesh_items)  # type: ignore

    def execute(self, context):
        obj = bpy.data.objects.get(self.mesh)
        if obj is None or obj.type != 'MESH':
            self.report({'WARNING'}, tr("Nenhuma malha na cena."))
            return {'CANCELLED'}
        scene_mod.set_target(context, obj.name)
        try:
            open_window(context, obj)
        except RuntimeError as exc:
            self.report({'ERROR'}, str(exc))
            return {'CANCELLED'}
        return {'FINISHED'}


class BTM_OT_MeshMeasureOption(bpy.types.Operator):
    """Muda uma opção da janela de medição: representação, projeção, snap, unidade ou folha"""
    bl_idname = "caffmob.mesh_measure_option"
    bl_label = "Opção da medição"
    bl_options = {'REGISTER', 'INTERNAL'}

    option: bpy.props.EnumProperty(
        name="Opção",
        items=[('REPRESENTATION', "Representação", ""), ('PROJECTION', "Projeção", ""), ('SNAP', "Snap", ""),
               ('UNIT', "Unidade", ""), ('ROUNDING', "Arredondamento", ""), ('SHEET', "Folha", ""),
               ('PRINT', "Impressão", ""), ('LABELS', "Medidas na tela", "")],
        default='REPRESENTATION',
    )  # type: ignore
    value: bpy.props.StringProperty(default="")  # type: ignore
    number: bpy.props.FloatProperty(default=0.0)  # type: ignore

    def execute(self, context):
        session = scene_mod.sessao()
        if session is None:
            return {'CANCELLED'}
        if self.option == 'REPRESENTATION' and self.value in core.REPRESENTATIONS:
            session.representation = self.value
        elif self.option == 'PROJECTION' and self.value in core.PROJECTIONS:
            session.set_projection(self.value)
        elif self.option == 'SNAP':
            if self.value in core.SNAP_MODES:
                session.snap_mode = self.value
            if self.number > 0.0:
                session.snap_threshold_mm = self.number
        elif self.option == 'UNIT' and self.value in core.UNITS:
            session.unit = self.value
        elif self.option == 'ROUNDING':
            session.rounded = self.value == 'ROUNDED'
        elif self.option == 'SHEET' and self.value in core.SHEETS:
            session.sheet = self.value
        elif self.option == 'PRINT':
            go_to_print(session, None if not self.value else self.value == 'ON')
        elif self.option == 'LABELS':
            session.mostrar_medidas = (not session.mostrar_medidas) if not self.value else self.value == 'ON'
        else:
            return {'CANCELLED'}
        if context.area is not None:
            context.area.tag_redraw()
        return {'FINISHED'}


class BTM_OT_MeshMeasurePart(bpy.types.Operator):
    """Mostra, esconde, escolhe ou troca a cor sólida de uma parte solta"""
    bl_idname = "caffmob.mesh_measure_part"
    bl_label = "Parte da malha"
    bl_options = {'REGISTER', 'INTERNAL'}

    action: bpy.props.EnumProperty(
        name="Ação",
        items=[('TOGGLE', "Mostrar ou esconder", ""), ('SELECT', "Escolher", ""), ('COLOR', "Cor sólida", "")],
        default='SELECT',
    )  # type: ignore
    index: bpy.props.IntProperty(default=0)  # type: ignore

    def execute(self, context):
        session = scene_mod.sessao()
        part = session.malha.part(self.index) if session is not None else None
        if part is None:
            return {'CANCELLED'}
        if self.action == 'TOGGLE':
            part.visible = not part.visible
        elif self.action == 'COLOR':
            part.cycle_color()
        else:
            session.selected = part
        if context.area is not None:
            context.area.tag_redraw()
        return {'FINISHED'}


class BTM_OT_MeshMeasureView(bpy.types.Operator):
    """Cria uma view da impressão, muda o tamanho ou a proporção, ou remove a view"""
    bl_idname = "caffmob.mesh_measure_view"
    bl_label = "View da impressão"
    bl_options = {'REGISTER', 'INTERNAL'}

    action: bpy.props.EnumProperty(
        name="Ação",
        items=[('CREATE', "Criar view", ""), ('SIZE', "Tamanho", ""), ('PROPORTION', "Proporção", ""),
               ('REMOVE', "Remover view", "")],
        default='CREATE',
    )  # type: ignore
    index: bpy.props.IntProperty(default=0)  # type: ignore
    delta: bpy.props.FloatProperty(default=10.0)  # type: ignore
    value: bpy.props.StringProperty(default="")  # type: ignore

    def execute(self, context):
        session = scene_mod.sessao()
        if session is None:
            return {'CANCELLED'}
        if self.action == 'CREATE':
            session.create_view()
        elif not 0 <= self.index < len(session.views):
            return {'CANCELLED'}
        elif self.action == 'SIZE':
            view = session.views[self.index]
            view['size_pct'] = max(10.0, min(100.0, float(view.get('size_pct', 100.0)) + self.delta))
        elif self.action == 'PROPORTION':
            if self.value in core.PROPORTIONS:
                session.views[self.index]['proportion'] = self.value
        elif self.action == 'REMOVE':
            session.views.pop(self.index)
        if context.area is not None:
            context.area.tag_redraw()
        return {'FINISHED'}


class BTM_OT_MeshMeasureClear(bpy.types.Operator):
    """Apaga as medidas manuais da janela"""
    bl_idname = "caffmob.mesh_measure_clear"
    bl_label = "Limpar medidas manuais"
    bl_options = {'REGISTER', 'INTERNAL'}

    def execute(self, context):
        session = scene_mod.sessao()
        if session is None:
            return {'CANCELLED'}
        session.clear_measures()
        if context.area is not None:
            context.area.tag_redraw()
        return {'FINISHED'}


class BTM_OT_MeshMeasureFit(bpy.types.Operator):
    """Reenquadra a malha na janela"""
    bl_idname = "caffmob.mesh_measure_fit"
    bl_label = "Enquadrar a malha"
    bl_options = {'REGISTER', 'INTERNAL'}

    def execute(self, context):
        session = scene_mod.sessao()
        if session is None:
            return {'CANCELLED'}
        session.fitted = False
        if context.area is not None:
            context.area.tag_redraw()
        return {'FINISHED'}


class BTM_OT_MeshMeasureReload(bpy.types.Operator):
    """Relê a malha do objeto escolhido"""
    bl_idname = "caffmob.mesh_measure_reload"
    bl_label = "Reler a malha"
    bl_options = {'REGISTER'}

    def execute(self, context):
        if reload(context) is None:
            self.report({'ERROR'}, tr("A janela de medição não está aberta."))
            return {'CANCELLED'}
        return {'FINISHED'}


class BTM_OT_MeshMeasureClose(bpy.types.Operator):
    """Fecha a janela de medição"""
    bl_idname = "caffmob.mesh_measure_close"
    bl_label = "Fechar medição"
    bl_options = {'REGISTER', 'INTERNAL'}

    def execute(self, context):
        close(context)
        return {'FINISHED'}


# Painéis ----------------------------------------------------------------------------------------------------------

REPRESENTATION_LABELS = (
    ('ARAMADO', N_("Aramado")),
    ('LINHAS_OCULTAS', N_("Linhas Ocultas")),
    ('SOLIDO', N_("Sólido")),
    ('RAIO_X', N_("Raio-X")),
    ('MATERIAL', N_("Material")),
)


def _session():
    return scene_mod.sessao()


def _size_text(part, session):
    """As três medidas da parte na unidade escolhida: `600 × 720 × 18 mm`."""
    values = [core.format_mm(value, session.unit, session.rounded, suffix=False) for value in part.size_mm]
    return f"{' × '.join(values)} {session.unit.lower()}"


class BTM_PT_MeshMeasureHeader(bpy.types.Panel):
    """Malha medida, representação, projeção, impressão e fechar."""
    bl_idname = "BTM_PT_MeshMeasureHeader"
    bl_label = "◎ V-Ray Mesh Measure"
    bl_space_type = 'IMAGE_EDITOR'
    bl_region_type = 'UI'
    bl_category = CATEGORIA

    def draw(self, context):
        layout = self.layout
        session = _session()
        if session is None:
            layout.label(text=tr("Nenhuma malha medida."), icon='INFO')
            return
        col = layout.column(align=True)
        col.label(text=session.malha.name, icon='MESH_DATA')
        col.label(text=tr("{} parte(s) · {} triângulo(s)").format(len(session.malha.parts),
                                                                session.malha.triangle_count()))

        box = layout.box()
        box.label(text=tr("Representação"), icon='SHADING_SOLID')
        grid = box.grid_flow(row_major=True, columns=3, even_columns=True, align=True)
        for code, label in REPRESENTATION_LABELS:
            op = grid.operator("caffmob.mesh_measure_option", text=tr(label), depress=session.representation == code)
            op.option = 'REPRESENTATION'
            op.value = code

        row = layout.row(align=True)
        for code, label in (('PERSP', N_("Perspectiva")), ('ORTHO', N_("Ortográfica"))):
            op = row.operator("caffmob.mesh_measure_option", text=tr(label), depress=session.camera.projection == code)
            op.option = 'PROJECTION'
            op.value = code

        row = layout.row(align=True)
        row.operator("caffmob.mesh_measure_fit", text="Enquadrar", icon='FULLSCREEN_ENTER')
        op = row.operator("caffmob.mesh_measure_option", text="Impressão", icon='IMAGE_DATA',
                          depress=session.print_preview)
        op.option = 'PRINT'
        row.operator("caffmob.mesh_measure_close", text="Fechar", icon='CANCEL')


class BTM_PT_MeshMeasureLayers(bpy.types.Panel):
    """Partes soltas como camadas: mostrar/esconder, escolher, medidas e cor sólida."""
    bl_idname = "BTM_PT_MeshMeasureLayers"
    bl_label = "Camadas (partes soltas)"
    bl_space_type = 'IMAGE_EDITOR'
    bl_region_type = 'UI'
    bl_category = CATEGORIA
    bl_parent_id = "BTM_PT_MeshMeasureHeader"

    def draw(self, context):
        layout = self.layout
        session = _session()
        if session is None:
            return
        layout.label(text=tr("{} parte(s)").format(len(session.malha.parts)))
        col = layout.column(align=True)
        for part in session.malha.parts:
            row = col.row(align=True)
            op = row.operator("caffmob.mesh_measure_part", text="",
                              icon='HIDE_OFF' if part.visible else 'HIDE_ON')
            op.action = 'TOGGLE'
            op.index = part.index
            op = row.operator("caffmob.mesh_measure_part", text=part.name, depress=part is session.selected)
            op.action = 'SELECT'
            op.index = part.index
            row.label(text=_size_text(part, session))
            op = row.operator("caffmob.mesh_measure_part", text="", icon='MATERIAL')
            op.action = 'COLOR'
            op.index = part.index


class BTM_PT_MeshMeasureUnits(bpy.types.Panel):
    """Unidade (absoluta ou arredondada) e snap nas extremidades."""
    bl_idname = "BTM_PT_MeshMeasureUnits"
    bl_label = "Unidades e snap"
    bl_space_type = 'IMAGE_EDITOR'
    bl_region_type = 'UI'
    bl_category = CATEGORIA
    bl_parent_id = "BTM_PT_MeshMeasureHeader"

    def draw(self, context):
        layout = self.layout
        session = _session()
        if session is None:
            return
        row = layout.row(align=True)
        for code in core.UNITS:
            op = row.operator("caffmob.mesh_measure_option", text=code.lower(), depress=session.unit == code)
            op.option = 'UNIT'
            op.value = code
        row = layout.row(align=True)
        for code, label in (('EXACT', N_("Absoluta")), ('ROUNDED', N_("Arredondada"))):
            op = row.operator("caffmob.mesh_measure_option", text=tr(label), depress=(session.rounded == (code == 'ROUNDED')))
            op.option = 'ROUNDING'
            op.value = code

        box = layout.box()
        box.label(text=tr("Snap nas extremidades"), icon='SNAP_ON')
        row = box.row(align=True)
        for code, label in (('OFF', N_("Desligado")), ('OBJETO', N_("Objeto")), ('PARTES', N_("Partes")),
                            ('AMBOS', N_("Ambos"))):
            op = row.operator("caffmob.mesh_measure_option", text=tr(label), depress=session.snap_mode == code)
            op.option = 'SNAP'
            op.value = code
        row = box.row(align=True)
        for step in (5.0, 10.0, 20.0, 50.0):
            op = row.operator("caffmob.mesh_measure_option",
                              text=tr("{} mm").format(f"{step:.0f}"),
                              depress=abs(session.snap_threshold_mm - step) < 1e-6)
            op.option = 'SNAP'
            op.value = session.snap_mode
            op.number = step
        op = box.operator("caffmob.mesh_measure_option",
                          text=tr("Medidas na tela: {}").format(tr("ligadas") if session.mostrar_medidas
                                                              else tr("desligadas")),
                          depress=session.mostrar_medidas)
        op.option = 'LABELS'


class BTM_PT_MeshMeasureMeasures(bpy.types.Panel):
    """Medidas de cada parte solta e as medidas manuais."""
    bl_idname = "BTM_PT_MeshMeasureMeasures"
    bl_label = "Medidas"
    bl_space_type = 'IMAGE_EDITOR'
    bl_region_type = 'UI'
    bl_category = CATEGORIA
    bl_parent_id = "BTM_PT_MeshMeasureHeader"

    def draw(self, context):
        layout = self.layout
        session = _session()
        if session is None:
            return
        visible = session.visible_parts()
        box = layout.box()
        box.label(text=tr("Caixa de cada parte"), icon='DRIVER_DISTANCE')
        col = box.column(align=True)
        for part in visible[:12]:
            col.label(text=tr("{}: {}").format(part.name, _size_text(part, session)))
        if len(visible) > 12:
            box.label(text=tr("… e mais {}").format(len(visible) - 12))

        box = layout.box()
        box.label(text=tr("Medidas manuais: {}").format(len(session.medidas)), icon='ARROW_LEFTRIGHT')
        if not session.medidas:
            box.label(text=tr("Ctrl+clique em duas extremidades para medir."))
        for item in session.medidas:
            box.label(text=item['label'])
        if session.pending is not None:
            box.label(text=tr("Clique na outra extremidade."), icon='INFO')
        row = layout.row(align=True)
        row.operator("caffmob.mesh_measure_clear", text="Limpar medidas", icon='TRASH')
        row.operator("caffmob.mesh_measure_reload", text="Reler malha", icon='FILE_REFRESH')


class BTM_PT_MeshMeasurePrint(bpy.types.Panel):
    """Folha de impressão, views com badge, tamanho e proporção de cada view."""
    bl_idname = "BTM_PT_MeshMeasurePrint"
    bl_label = "Impressão"
    bl_space_type = 'IMAGE_EDITOR'
    bl_region_type = 'UI'
    bl_category = CATEGORIA
    bl_parent_id = "BTM_PT_MeshMeasureHeader"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        session = _session()
        if session is None:
            return
        row = layout.row(align=True)
        for code in core.SHEETS:
            op = row.operator("caffmob.mesh_measure_option", text=tr(code.lower().replace('_', ' ')),
                              depress=session.sheet == code)
            op.option = 'SHEET'
            op.value = code
        op = layout.operator("caffmob.mesh_measure_option", text=tr("Ver a folha"), icon='IMAGE_DATA',
                             depress=session.print_preview)
        op.option = 'PRINT'
        op.value = 'OFF' if session.print_preview else 'ON'
        layout.operator("caffmob.mesh_measure_view", text="Criar view com badge",
                        icon='ADD').action = 'CREATE'
        if not session.views:
            layout.label(text=tr("Nenhuma view: a folha fica vazia."), icon='INFO')
        col = layout.column(align=True)
        for index, view in enumerate(session.views):
            box = col.box()
            row = box.row(align=True)
            row.label(text=f"{view['name']} · {view.get('proportion', 'LIVRE')} · "
                           f"{float(view.get('size_pct', 100.0)):.0f}%")
            op = row.operator("caffmob.mesh_measure_view", text="-")
            op.action = 'SIZE'
            op.index = index
            op.delta = -10.0
            op = row.operator("caffmob.mesh_measure_view", text="+")
            op.action = 'SIZE'
            op.index = index
            op.delta = 10.0
            op = row.operator("caffmob.mesh_measure_view", text="", icon='REMOVE')
            op.action = 'REMOVE'
            op.index = index
            row = box.row(align=True)
            for code in core.PROPORTIONS:
                op = row.operator("caffmob.mesh_measure_view", text=code,
                                  depress=view.get('proportion', 'LIVRE') == code)
                op.action = 'PROPORTION'
                op.index = index
                op.value = code


class BTM_PT_MeshMeasure3D(bpy.types.Panel):
    """Abre a medição da malha selecionada, ou mostra o aviso e o conta-gotas."""
    bl_idname = "BTM_PT_MeshMeasure3D"
    bl_label = "V-Ray Mesh Measure"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "CAFFMob Draw"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        obj = scene_mod.target(context)
        if obj is None:
            box = layout.box()
            box.alert = True
            box.label(text=tr("Nenhuma malha selecionada."), icon='ERROR')
            box.label(text=tr("Use o conta-gotas para escolher a malha."))
            row = box.row(align=True)
            row.operator("caffmob.mesh_measure_eyedropper", text="Conta-gotas", icon='EYEDROPPER')
            row.operator_menu_enum("caffmob.mesh_measure_pick", "mesh", text=tr("Escolher malha"))
            return
        col = layout.column(align=True)
        col.label(text=tr("Malha: {}").format(obj.name), icon='MESH_DATA')
        col.operator("caffmob.mesh_measure_window", text="Abrir V-Ray Mesh Measure", icon='WINDOW')
        row = col.row(align=True)
        row.operator("caffmob.mesh_measure_eyedropper", text="Conta-gotas", icon='EYEDROPPER')
        row.operator("caffmob.mesh_measure_reload", text="Reler", icon='FILE_REFRESH')


classes = (
    BTM_OT_MeshMeasureWindow,
    BTM_OT_MeshMeasureEyedropper,
    BTM_OT_MeshMeasurePick,
    BTM_OT_MeshMeasureOption,
    BTM_OT_MeshMeasurePart,
    BTM_OT_MeshMeasureView,
    BTM_OT_MeshMeasureClear,
    BTM_OT_MeshMeasureFit,
    BTM_OT_MeshMeasureReload,
    BTM_OT_MeshMeasureClose,
    BTM_OT_MeshMeasureModal,
    BTM_PT_MeshMeasureHeader,
    BTM_PT_MeshMeasureLayers,
    BTM_PT_MeshMeasureUnits,
    BTM_PT_MeshMeasureMeasures,
    BTM_PT_MeshMeasurePrint,
    BTM_PT_MeshMeasure3D,
)

_draw_handle = []


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
