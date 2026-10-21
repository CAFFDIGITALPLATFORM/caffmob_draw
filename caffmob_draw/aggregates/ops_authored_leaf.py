"""Folha composta autoral, configuração fechada e prévia reversível (066, T054)."""

import bpy  # type: ignore

from ..data.i18n import tr

from ..collision import guard
from ..selection import component_select
from ..stable_id import new_uid
from ..inspection.adapters.aggregate_leaf import front_for_object
from . import apply, group, leaf
from .ops_members import owner_of, set_member
from .props import HINGE_ITEMS, MOTION_ITEMS, SLIDE_ITEMS, SWING_ITEMS


def leaf_of(obj):
    front = front_for_object(obj, bpy.context.scene) if obj else None
    return front.obj if front else None


def validate(objects, owner, pivot=None, closed_pose=False):
    if not owner or not owner.get('IS_AUTHORED_CABINET'):
        raise ValueError("Selecione membros de um armário autoral")
    if not closed_pose:
        raise ValueError("Confirme explicitamente a pose fechada")
    if any(a in b.children_recursive for a in objects for b in objects if a != b):
        raise ValueError("Selecione as peças ou o conjunto, sem repetir descendentes")
    if not objects or any(o == owner or owner_of(o) != owner for o in objects):
        raise ValueError("Todos os membros móveis devem ter o mesmo dono")
    for obj in objects:
        existing = leaf_of(obj)
        if existing and leaf.current_fraction(existing) > 1e-6:
            raise ValueError("Feche a folha antes de configurar")
        if obj.btm_member.role == 'FIXED_FRONT':
            raise ValueError("Retire a parte fixa da seleção móvel")
    if pivot is not None and (pivot in objects or pivot.type != 'EMPTY' or pivot == owner or owner_of(pivot) != owner):
        raise ValueError("O pivô deve ser um controle deste armário")


@guard.suspended()
def configure(objects, owner, construction='PANEL', motion='SWING', hinge='LEFT', swing_sign='OUT',
              max_angle=95, slide_dir='POS_X', travel_mm=500, pivot=None, closed_pose=False):
    objects = list(objects)
    validate(objects, owner, pivot, closed_pose)
    existing = list(dict.fromkeys(leaf_of(o) for o in objects))
    if len(existing) == 1 and existing[0] is not None:
        obj = existing[0]
    elif len(objects) == 1:
        obj = objects[0]
    else:
        # Não cria um segundo grupo ao reconfigurar: a descoberta acima sobe das peças até a folha.
        obj = group.create_group(objects, name='Folha composta')
        set_member(obj, owner, 'LEAF_PART')
    obj.btm_aggregate.construction = construction
    if construction == 'FIXED':
        obj.btm_aggregate.is_aggregate = False
        obj.btm_aggregate.kind = 'AGGREGATE'
        for part in [obj] + list(obj.children_recursive):
            set_member(part, owner, 'FIXED_FRONT', reparent=False)
        return obj
    for part in [obj] + list(obj.children_recursive):
        set_member(part, owner, 'LEAF_PART', reparent=False)
    if pivot is not None:
        obj['btm_leaf_manual_base'] = list(leaf.base_from_pivot(pivot, owner))
        obj.btm_aggregate.pivot = pivot
    leaf.make_leaf(obj, owner, motion, hinge, swing_sign, max_angle, slide_dir, travel_mm / 1000)
    set_member(leaf.pivot_of(obj), owner, 'HARDWARE', reparent=False)
    return obj


class Snapshot:
    """Estado anterior da montagem: a prévia só cria grupos/pivôs e altera estas propriedades."""

    def __init__(self):
        self.objects = set(bpy.data.objects)
        self.state = []
        self.selected = set(bpy.context.selected_objects)
        self.active = bpy.context.view_layer.objects.active
        for obj in self.objects:
            agg = obj.btm_aggregate
            attrs = {}
            for prop in agg.bl_rna.properties:
                if prop.identifier == 'rna_type' or prop.is_readonly:
                    continue
                value = getattr(agg, prop.identifier)
                attrs[prop.identifier] = tuple(value) if getattr(prop, 'is_array', False) else value
            self.state.append((obj, obj.parent, obj.matrix_parent_inverse.copy(), obj.matrix_basis.copy(), attrs,
                               obj.btm_member.owner, obj.btm_member.role, obj.btm_member.uid,
                               {k: obj[k].to_list() if hasattr(obj[k], 'to_list') else obj[k]
                                for k in (leaf.REST_KEY, leaf.OPEN_KEY, 'btm_leaf_base', 'btm_leaf_manual_base')
                                if k in obj}))

    @guard.suspended()
    @component_select.suspended()
    def restore(self):
        for obj, parent, inverse, basis, attrs, owner, role, uid, custom in self.state:
            for key, value in attrs.items():
                apply._write(obj, key, value)
            obj.btm_member.owner, obj.btm_member.role, obj.btm_member.uid = owner, role, uid
            obj.parent = parent
            obj.matrix_parent_inverse = inverse
            obj.matrix_basis = basis
            for key in (leaf.REST_KEY, leaf.OPEN_KEY, 'btm_leaf_base', 'btm_leaf_manual_base'):
                if key in custom:
                    obj[key] = custom[key]
                elif key in obj:
                    del obj[key]
        for obj in set(bpy.data.objects) - self.objects:
            bpy.data.objects.remove(obj, do_unlink=True)
        for obj in self.objects:
            obj.select_set(obj in self.selected)
        bpy.context.view_layer.objects.active = self.active
        bpy.context.view_layer.update()


_live = {}


def _preview(self, context):
    self = _live.get(self.preview_token)
    if self is None:
        return
    self._snapshot.restore()
    self.preview_error = ''
    try:
        obj = self._configure()
        if self.construction != 'FIXED':
            obj.btm_aggregate.open_value = self.preview
        context.view_layer.update()
    except ValueError as exc:
        self.preview_error = str(exc)
        self._snapshot.restore()


class BTM_OT_AuthoredLeaf(bpy.types.Operator):
    """Configura os membros móveis como uma única folha deste armário"""
    bl_idname = 'caffmob_draw.authored_leaf'
    bl_label = "Definir porta deste armário"
    bl_options = {'REGISTER', 'UNDO'}

    construction: bpy.props.EnumProperty(name="Construção", items=[
        ('PANEL', "Chapa", ''), ('GLASS', "Vidro", ''), ('GLASS_FRAMED', "Vidro com perfil", ''),
        ('FIXED', "Frente fixa", '')])  # type: ignore
    motion: bpy.props.EnumProperty(name="Movimento", items=MOTION_ITEMS)  # type: ignore
    hinge: bpy.props.EnumProperty(name="Eixo", items=HINGE_ITEMS)  # type: ignore
    swing_sign: bpy.props.EnumProperty(name="Sentido", items=SWING_ITEMS)  # type: ignore
    max_angle: bpy.props.FloatProperty(name="Ângulo máximo", default=95, min=1, max=180)  # type: ignore
    slide_dir: bpy.props.EnumProperty(name="Sentido", items=SLIDE_ITEMS)  # type: ignore
    travel_mm: bpy.props.FloatProperty(name="Curso (mm)", default=500, min=1)  # type: ignore
    pivot: bpy.props.StringProperty(name="Pivô existente")  # type: ignore
    closed_pose: bpy.props.BoolProperty(name="Esta é a pose fechada", default=False)  # type: ignore
    preview_token: bpy.props.StringProperty(options={'HIDDEN', 'SKIP_SAVE'})  # type: ignore
    preview_error: bpy.props.StringProperty(options={'HIDDEN', 'SKIP_SAVE'})  # type: ignore
    preview: bpy.props.FloatProperty(name="Prévia", min=0, max=1, update=_preview)  # type: ignore

    def _configure(self):
        objects = getattr(self, '_objects', list(bpy.context.selected_objects))
        owner = owner_of(objects[0]) if objects else None
        return configure(objects, owner, **{key: getattr(self, key) for key in (
            'construction', 'motion', 'hinge', 'swing_sign', 'max_angle', 'slide_dir', 'travel_mm', 'pivot',
            'closed_pose') if key != 'pivot'}, pivot=bpy.data.objects.get(self.pivot))

    def invoke(self, context, event):
        self._objects = list(context.selected_objects)
        owner = owner_of(context.object)
        try:
            validate(self._objects, owner, closed_pose=True)
        except ValueError as exc:
            self.report({'ERROR'}, tr(str(exc)))
            return {'CANCELLED'}
        existing = leaf_of(context.object)
        if existing:
            for key in ('construction', 'motion', 'hinge', 'swing_sign', 'max_angle', 'slide_dir'):
                setattr(self, key, getattr(existing.btm_aggregate, key))
            self.travel_mm = existing.btm_aggregate.travel * 1000
            self.pivot = leaf.pivot_of(existing).name if 'btm_leaf_manual_base' in existing else ''
        self._snapshot = Snapshot()
        self.preview_token = new_uid()
        _live[self.preview_token] = self
        return context.window_manager.invoke_props_dialog(self, width=500)

    def draw(self, context):
        self.layout.prop_search(self, 'pivot', bpy.data, 'objects')
        for key in ('construction', 'closed_pose'):
            self.layout.prop(self, key)
        if self.construction != 'FIXED':
            self.layout.prop(self, 'motion')
            for key in (('hinge', 'swing_sign', 'max_angle') if self.motion == 'SWING' else ('slide_dir', 'travel_mm')):
                self.layout.prop(self, key)
            self.layout.prop(self, 'preview', slider=True)
            if self.preview_error:
                self.layout.label(text=tr(self.preview_error), icon='ERROR')

    def execute(self, context):
        _live.pop(self.preview_token, None)
        if hasattr(self, '_snapshot'):
            self._snapshot.restore()
        try:
            self._configure()
        except ValueError as exc:
            self.report({'ERROR'}, tr(str(exc)))
            return {'CANCELLED'}
        return {'FINISHED'}

    def cancel(self, context):
        _live.pop(self.preview_token, None)
        if hasattr(self, '_snapshot'):
            self._snapshot.restore()


class BTM_OT_AuthoredLeavesOpen(bpy.types.Operator):
    """Abre ou fecha somente as folhas do armário ativo"""
    bl_idname = 'caffmob_draw.authored_leaves_open'
    bl_label = "Abrir/fechar portas deste armário"
    bl_options = {'REGISTER', 'UNDO'}
    opening: bpy.props.FloatProperty(name="Abertura", min=0, max=1, default=1)  # type: ignore

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)

    def execute(self, context):
        owner = owner_of(context.object)
        if owner is None:
            return {'CANCELLED'}
        for obj in context.scene.objects:
            if obj.btm_member.owner == owner and obj.btm_aggregate.is_aggregate and obj.btm_aggregate.kind == 'LEAF':
                obj.btm_aggregate.open_value = self.opening
        return {'FINISHED'}


classes = (BTM_OT_AuthoredLeaf, BTM_OT_AuthoredLeavesOpen)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for op in list(_live.values()):
        op.cancel(bpy.context)
    _live.clear()
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
