"""Face por clique, prévia sem dados temporários e confirmação em um passo de Desfazer."""
import copy
from dataclasses import fields
from pathlib import Path
from types import SimpleNamespace

import bpy  # type: ignore
import gpu  # type: ignore
from bpy_extras import view3d_utils  # type: ignore
from gpu_extras.batch import batch_for_shader  # type: ignore
from mathutils import Vector  # type: ignore

from ..collision import guard
from ..data.i18n import tr
from . import core, ops_adopt, presets, props, region, sync

_live = set()
PARAM_FIELDS = [f.name for f in fields(core.Params)]
EXTRA_FIELDS = ['texture', 'texture_size_mm', 'grain_angle', 'material', 'backing_material',
                'environment', 'material_kind', 'overrides']


def copy_settings(source, target):
    for name in PARAM_FIELDS + EXTRA_FIELDS:
        setattr(target, name, getattr(source, name))


def preset_from(data, name):
    from dataclasses import asdict
    value = dict(name=name, material_kind=data.material_kind, params=asdict(props.parameters(data)),
                 texture=data.texture, texture_size_mm=data.texture_size_mm, grain_angle=data.grain_angle)
    for attribute, key in (('material', 'finish'), ('backing_material', 'backing_finish')):
        mat = getattr(data, attribute)
        if mat is not None:
            value[key] = dict(name=mat.name, color=list(mat.diffuse_color))
    return value


def apply_preset(data, value):
    presets.validate(value)
    for name, item in value['params'].items():
        setattr(data, name, item)
    for name in ('material_kind', 'texture', 'texture_size_mm', 'grain_angle'):
        setattr(data, name, value[name])
    for attribute, key in (('material', 'finish'), ('backing_material', 'backing_finish')):
        finish = value.get(key)
        if finish:
            mat = bpy.data.materials.get(finish['name'])
            if mat is None:
                mat = bpy.data.materials.new(finish['name'])
                mat.diffuse_color = finish['color']
                bsdf = next(n for n in mat.node_tree.nodes if n.type == 'BSDF_PRINCIPLED')
                bsdf.inputs['Base Color'].default_value = finish['color']
            setattr(data, attribute, mat)
        else:
            setattr(data, attribute, None)


def preview_geometry(data):
    """Prévia geométrica compartilhada pelo modal e pelo ensaio de desempenho, sem mutações."""
    basis, triangles = region.extract(data)
    lines = []
    for piece in core.layout(region.bounds(triangles), props.parameters(data)):
        for triangle in triangles:
            polygon = core.intersection(triangle, piece.polygon)
            for a, b in zip(polygon, polygon[1:] + polygon[:1]):
                lines.extend([basis @ Vector((a[0]/1000, a[1]/1000, .0005)),
                              basis @ Vector((b[0]/1000, b[1]/1000, .0005))])
    return lines


class BTM_OT_CladdingFace(bpy.types.Operator):
    """Escolha a face, revise a prévia e confirme com Enter; Esc preserva a cena"""
    bl_idname = 'caffmob.cladding_face'
    bl_label = 'Aplicar revestimento'
    bl_options = {'REGISTER', 'UNDO'}
    mode: bpy.props.EnumProperty(items=[('CREATE', 'Gerar', ''), ('ADOPT', 'Adotar', ''),
                                       ('REASSOCIATE', 'Reassociar', '')])  # type: ignore

    def invoke(self, context, _event):
        if context.area is None or context.area.type != 'VIEW_3D':
            return {'CANCELLED'}
        self._root = ops_adopt.controller_for(context.object)
        self._objects = list(context.selected_objects)
        self._face = None
        self._locked = False
        self._lines = []
        self._area = context.area
        self._region = next(r for r in self._area.regions if r.type == 'WINDOW')
        self._handle = bpy.types.SpaceView3D.draw_handler_add(self._draw, (), 'WINDOW', 'POST_VIEW')
        _live.add(self)
        context.window_manager.modal_handler_add(self)
        self._area.header_text_set(tr('Clique na face | Enter: confirmar | Esc: cancelar'))
        return {'RUNNING_MODAL'}

    def _draw(self):
        if bpy.context.area != self._area or not self._lines:
            return
        shader = gpu.shader.from_builtin('UNIFORM_COLOR')
        shader.bind()
        shader.uniform_float('color', (0.2, .8, 1, 1))
        batch_for_shader(shader, 'LINES', {'pos': self._lines}).draw(shader)

    def _end(self):
        if getattr(self, '_handle', None) is not None:
            bpy.types.SpaceView3D.draw_handler_remove(self._handle, 'WINDOW')
            self._handle = None
        if getattr(self, '_area', None):
            self._area.header_text_set(None)
            self._area.tag_redraw()
        _live.discard(self)

    def cancel(self, _context):
        self._end()

    def _pick(self, context, event):
        coord = event.mouse_x - self._region.x, event.mouse_y - self._region.y
        rv3d = self._area.spaces.active.region_3d
        origin = view3d_utils.region_2d_to_origin_3d(self._region, rv3d, coord)
        direction = view3d_utils.region_2d_to_vector_3d(self._region, rv3d, coord)
        hit, _location, _normal, index, host, _matrix = context.scene.ray_cast(
            context.evaluated_depsgraph_get(), origin, direction)
        if not hit or host.type != 'MESH' or host.get('btm_cladding_piece'):
            return
        # A origem vem de um vértice da face, e não do ponto do mouse: a grade não desliza na prévia.
        evaluated = host.evaluated_get(context.evaluated_depsgraph_get())
        mesh = evaluated.to_mesh()
        try:
            face = mesh.polygons[index]
            local_origin = mesh.vertices[face.vertices[0]].co.copy()
            n = face.normal.copy()
            candidates = [Vector((1, 0, 0)), Vector((0, 1, 0)), Vector((0, 0, 1))]
            u = max(candidates, key=lambda axis: (axis - n*axis.dot(n)).length)
            u = (u - n*u.dot(n)).normalized()
        finally:
            evaluated.to_mesh_clear()
        self._face = (host, tuple(local_origin), tuple(n), tuple(u))
        self._preview(context)

    def _preview(self, context):
        if not self._face:
            return
        host, origin, normal, u = self._face
        data = SimpleNamespace(**{name: getattr(context.scene.btm_cladding_settings, name)
                                  for name in PARAM_FIELDS + EXTRA_FIELDS})
        data.host, data.plane_origin, data.plane_normal, data.plane_u = host, origin, normal, u
        self._lines = preview_geometry(data)
        self._area.tag_redraw()

    def execute(self, context):
        if not getattr(self, '_face', None):
            return {'CANCELLED'}
        host, origin, normal, u = self._face
        with guard.suspended():
            if self.mode == 'ADOPT':
                root = ops_adopt.adopt(self._objects, host, origin, normal, u)
            elif self.mode == 'REASSOCIATE':
                if self._root is None:
                    return {'CANCELLED'}
                root = self._root
                ops_adopt.reassociate(root, host, origin, normal, u)
                sync.sync(root)
            else:
                props.parameters(context.scene.btm_cladding_settings).validate()
                root = ops_adopt.create(host, origin, normal, u)
                try:
                    copy_settings(context.scene.btm_cladding_settings, root.btm_cladding)
                    sync.sync(root)
                except Exception:
                    bpy.data.objects.remove(root, do_unlink=True)
                    raise
            for obj in context.selected_objects:
                obj.select_set(False)
            root.select_set(True)
            context.view_layer.objects.active = root
        return {'FINISHED'}

    def modal(self, context, event):
        if event.value == 'PRESS' and event.type in {'ESC', 'RIGHTMOUSE'}:
            self._end()
            return {'CANCELLED'}
        if event.type in {'MIDDLEMOUSE', 'WHEELUPMOUSE', 'WHEELDOWNMOUSE'}:
            return {'PASS_THROUGH'}
        try:
            if event.type == 'MOUSEMOVE' and not self._locked:
                self._pick(context, event)
            if event.type == 'LEFTMOUSE' and event.value == 'PRESS':
                self._pick(context, event)
                self._locked = bool(self._face)
            if event.type in {'RET', 'NUMPAD_ENTER'} and event.value == 'PRESS' and self._face:
                result = self.execute(context)
                self._end()
                return result
        except (ValueError, RuntimeError) as exc:
            self.report({'WARNING'}, str(exc))
        except Exception:
            self._end()
            raise
        return {'RUNNING_MODAL'}


class BTM_OT_CladdingEdit(bpy.types.Operator):
    """Carrega os parâmetros ou confirma a atualização do revestimento selecionado"""
    bl_idname = 'caffmob.cladding_edit'
    bl_label = 'Atualizar revestimento'
    bl_options = {'REGISTER', 'UNDO'}
    load: bpy.props.BoolProperty(default=False)  # type: ignore

    @classmethod
    def poll(cls, context):
        return ops_adopt.controller_for(context.object) is not None

    def execute(self, context):
        root = ops_adopt.controller_for(context.object)
        if self.load:
            copy_settings(root.btm_cladding, context.scene.btm_cladding_settings)
        else:
            props.parameters(context.scene.btm_cladding_settings).validate()
            previous = SimpleNamespace()
            copy_settings(root.btm_cladding, previous)
            try:
                copy_settings(context.scene.btm_cladding_settings, root.btm_cladding)
                sync.sync(root)
            except Exception:
                copy_settings(previous, root.btm_cladding)
                raise
        return {'FINISHED'}


class BTM_OT_CladdingPreset(bpy.types.Operator):
    """Grava ou reaplica um preset local de revestimento"""
    bl_idname = 'caffmob.cladding_preset'
    bl_label = 'Preset de revestimento'
    bl_options = {'REGISTER', 'UNDO'}
    action: bpy.props.EnumProperty(items=[('LOAD', 'Abrir', ''), ('SAVE', 'Salvar', ''),
                                         ('COMPANY', 'Preset da empresa', '')])  # type: ignore
    preset: bpy.props.EnumProperty(items=[('tabuas_castanhas', 'Tábuas castanhas', ''),
        ('ripado_mdf', 'Ripado com MDF', ''), ('painel_horizontal', 'Painel de veio horizontal', '')])  # type: ignore
    filepath: bpy.props.StringProperty(subtype='FILE_PATH')  # type: ignore
    name: bpy.props.StringProperty(name='Nome do preset', default='Meu revestimento')  # type: ignore

    def invoke(self, context, _event):
        if self.action == 'COMPANY':
            return self.execute(context)
        self.filepath = str(Path(bpy.utils.extension_path_user(__package__.rsplit('.', 1)[0],
                           path='cladding', create=True)) / 'revestimento.json')
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

    def execute(self, context):
        data = context.scene.btm_cladding_settings
        if self.action == 'SAVE':
            presets.save(bpy.path.abspath(self.filepath), preset_from(data, self.name))
        else:
            value = copy.deepcopy(presets.COMPANY[self.preset]) if self.action == 'COMPANY' else \
                presets.load(bpy.path.abspath(self.filepath))
            apply_preset(data, value)
        return {'FINISHED'}


class BTM_PT_Cladding(bpy.types.Panel):
    bl_label = 'Revestimentos'
    bl_idname = 'BTM_PT_cladding'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'CAFFMob Draw'

    def draw(self, context):
        layout = self.layout
        data = context.scene.btm_cladding_settings
        root = ops_adopt.controller_for(context.object)
        if root:
            if root.btm_cladding.host is None:
                layout.label(text='Vínculo quebrado', icon='ERROR')
                layout.operator('caffmob.cladding_face', text='Reassociar').mode = 'REASSOCIATE'
            layout.operator('caffmob.cladding_edit', text='Carregar parâmetros').load = True
        for name in ('kind', 'material_kind', 'width_mm', 'thickness_mm', 'joint_mm', 'min_gap_mm',
                     'orientation', 'angle', 'band', 'band_from', 'band_mm', 'backing', 'backing_material',
                     'sheet_w_mm', 'sheet_h_mm', 'sheet_t_mm', 'material', 'texture', 'texture_size_mm',
                     'grain_angle', 'environment'):
            layout.prop(data, name)
        layout.operator('caffmob.cladding_face')
        layout.operator('caffmob.cladding_face', text='Adotar revestimento').mode = 'ADOPT'
        if root:
            layout.operator('caffmob.cladding_edit')
        for key, label in (('tabuas_castanhas', 'Tábuas castanhas'), ('ripado_mdf', 'Ripado com MDF'),
                           ('painel_horizontal', 'Painel de veio horizontal')):
            op = layout.operator('caffmob.cladding_preset', text=label)
            op.action, op.preset = 'COMPANY', key
        layout.operator('caffmob.cladding_preset', text='Salvar preset').action = 'SAVE'
        layout.operator('caffmob.cladding_preset', text='Abrir preset').action = 'LOAD'


classes = (BTM_OT_CladdingFace, BTM_OT_CladdingEdit, BTM_OT_CladdingPreset, BTM_PT_Cladding)


def register():
    bpy.types.Scene.btm_cladding_settings = bpy.props.PointerProperty(type=props.BTM_PG_Cladding)
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for op in list(_live):
        op._end()
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    del bpy.types.Scene.btm_cladding_settings
