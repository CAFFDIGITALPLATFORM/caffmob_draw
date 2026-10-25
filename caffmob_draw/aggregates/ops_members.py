"""Membros do componente: parentesco sem prisão à face, mantendo a pose mundial (066, T053)."""

import bpy  # type: ignore

from ..data.i18n import tr

from ..stable_id import ensure_uid
from ..selection.classify import module_root
from . import group
from .authored_props import ROLE_ITEMS


def owner_of(obj):
    if obj is None:
        return None
    owner = obj.btm_member.owner
    return owner if owner is not None else module_root(obj)[0]


def validate_member(obj, owner):
    if owner is None or not owner.get('IS_AUTHORED_CABINET'):
        raise ValueError("Defina um armário autoral como dono")
    if obj == owner or owner in obj.children_recursive:
        raise ValueError("O membro não pode conter o dono")
    if obj.type not in group.MEMBER_TYPES:
        raise ValueError("Tipo de objeto não aceito no componente")
    if obj.get('IS_AUTHORED_CABINET'):
        raise ValueError("Um armário não pode ser membro de outro")


def set_member(obj, owner, role='CARCASS', reparent=True):
    validate_member(obj, owner)
    world = obj.matrix_world.copy()
    old_owner = obj.btm_member.owner
    if reparent:
        # Uma folha registrada transfere também seu pivô e suas partes, fechada e sem salto.
        agg = obj.btm_aggregate
        if agg.is_aggregate and agg.kind == 'LEAF':
            from . import leaf
            if leaf.current_fraction(obj) > 1e-6:
                raise ValueError("Feche a folha antes de transferir")
            pivot = leaf.pivot_of(obj)
            if pivot is not None:
                pivot_world = pivot.matrix_world.copy()
                pivot.parent = owner
                pivot.matrix_world = pivot_world
                agg.parent_ref = owner
                obj[leaf.REST_KEY] = [v for row in (leaf.front_frame(owner).inverted() @
                                                  owner.matrix_world.inverted_safe() @ world) for v in row]
                obj['btm_leaf_manual_base'] = list(leaf.base_from_pivot(pivot, owner))
                leaf.rebuild_pivot(obj)
                pivot.btm_member.owner = owner
                reparent = False
        for child in obj.children_recursive:
            if child.btm_member.owner == old_owner and old_owner is not None:
                child.btm_member.owner = owner
    if reparent:
        obj.parent = owner
        obj.matrix_world = world
    obj.btm_member.owner = owner
    obj.btm_member.role = role
    ensure_uid(obj.btm_member)


def remove_member(obj):
    world = obj.matrix_world.copy()
    obj.parent = None
    obj.matrix_world = world
    obj.btm_member.owner = None
    for child in obj.children_recursive:
        child.btm_member.owner = None
    if obj.btm_aggregate.is_aggregate and obj.btm_aggregate.kind == 'LEAF':
        from . import leaf
        pivot = leaf.pivot_of(obj)
        if pivot is not None:
            pivot.btm_member.owner = None
        obj.btm_aggregate.is_aggregate = False
        obj.btm_aggregate.parent_ref = None
        obj.btm_aggregate.pivot = None


class BTM_OT_MemberAdd(bpy.types.Operator):
    """Adiciona ou transfere os objetos selecionados para o armário indicado"""
    bl_idname = 'caffmob_draw.member_add'
    bl_label = "Adicionar ao componente"
    bl_options = {'REGISTER', 'UNDO'}

    owner: bpy.props.StringProperty(name="Armário dono")  # type: ignore
    role: bpy.props.EnumProperty(name="Papel", items=ROLE_ITEMS, default='CARCASS')  # type: ignore

    @classmethod
    def poll(cls, context):
        # (067 D-08) Habilitado só onde executa; o motivo aparece na dica do botão.
        from ..target import capabilities, snapshot
        return capabilities.poll(cls, 'member_add', snapshot.current(context))

    def invoke(self, context, event):
        owner = owner_of(context.object)
        self.owner = owner.name if owner else ''
        return context.window_manager.invoke_props_dialog(self)

    def draw(self, context):
        self.layout.prop_search(self, 'owner', bpy.data, 'objects')
        self.layout.prop(self, 'role')

    def execute(self, context):
        owner = bpy.data.objects.get(self.owner) if self.owner else owner_of(context.object)
        objects = [o for o in context.selected_objects if o != owner]
        try:
            for obj in objects:
                validate_member(obj, owner)
                if obj.btm_aggregate.is_aggregate and obj.btm_aggregate.kind == 'LEAF':
                    from . import leaf
                    if leaf.current_fraction(obj) > 1e-6:
                        raise ValueError("Feche a folha antes de transferir")
        except ValueError as exc:
            self.report({'ERROR'}, tr(str(exc)))
            return {'CANCELLED'}
        for obj in objects:
            set_member(obj, owner, self.role)
        return {'FINISHED'}


class BTM_OT_MemberTransfer(BTM_OT_MemberAdd):
    """Transfere membros para outro armário, mantendo a posição"""
    bl_idname = 'caffmob_draw.member_transfer'
    bl_label = "Transferir membro"

    @classmethod
    def poll(cls, context):
        # (067 D-08) Transferir vale só para quem já é membro; o motivo aparece na dica do botão.
        from ..target import capabilities, snapshot
        return capabilities.poll(cls, 'member_transfer', snapshot.current(context))


class BTM_OT_MemberRemove(bpy.types.Operator):
    """Desvincula membros mantendo posição e materiais"""
    bl_idname = 'caffmob_draw.member_remove'
    bl_label = "Remover do componente"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        # (067 D-08) Habilitado só onde executa; sem membro, o motivo aparece na dica do botão.
        from ..target import capabilities, snapshot
        return capabilities.poll(cls, 'member_remove', snapshot.current(context))

    def execute(self, context):
        members = [obj for obj in context.selected_objects if obj.btm_member.owner is not None]
        if not members:
            self.report({'WARNING'}, tr("Nenhum selecionado é membro de armário autoral."))
            return {'CANCELLED'}
        for obj in members:
            remove_member(obj)
        return {'FINISHED'}


classes = (BTM_OT_MemberAdd, BTM_OT_MemberTransfer, BTM_OT_MemberRemove)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
