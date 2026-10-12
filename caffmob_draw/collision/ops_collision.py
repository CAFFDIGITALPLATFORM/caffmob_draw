"""Operadores de colisão (feature 004, T039, T040; RF-20, RF-21, RF-26, D-14, D-18, D-19)."""

import bpy  # type: ignore
from mathutils import Vector  # type: ignore

from ..data.i18n import tr
from . import scan


def _ancestors(obj):
    current = obj.parent
    while current is not None:
        yield current
        current = current.parent


def _state(context):
    return context.window_manager.btm_collision


class BTM_OT_CheckCollisions(bpy.types.Operator):
    """Procura itens que ocupam o mesmo espaço e itens que entram em parede, piso ou teto (encostar não conta)"""
    bl_idname = "caffmob.check_collisions"
    bl_label = "Verificar colisões"
    bl_options = {'REGISTER'}

    scope: bpy.props.EnumProperty(
        name="Escopo", items=[('ALL', "Cena", "Todos os itens da cena"),
                              ('SELECTED', "Selecionado", "Só o item selecionado e o que ele toca")],
        default='ALL')  # type: ignore

    def execute(self, context):
        if not scan.enabled(context.scene):
            self.report({'WARNING'}, tr("Colisão desligada (Evitar Sobreposição)"))
            return {'CANCELLED'}
        if self.scope == 'SELECTED' and not context.selected_objects:
            self.report({'WARNING'}, tr("Selecione um item"))
            return {'CANCELLED'}
        found = scan.check_all(context, self.scope)
        state = _state(context)
        if found is None:
            self.report({'ERROR'}, tr("Não foi possível calcular a colisão: {}").format(state.error))
            return {'CANCELLED'}
        if found:
            self.report({'WARNING'}, tr("{} colisão(ões) em {} item(ns)").format(len(found), state.checked))
        else:
            self.report({'INFO'}, tr("Sem colisões em {} item(ns)").format(state.checked))
        return {'FINISHED'}


class BTM_OT_CollisionGoto(bpy.types.Operator):
    """Seleciona os dois itens da colisão e enquadra a vista neles"""
    bl_idname = "caffmob.collision_goto"
    bl_label = "Ir para a colisão"
    bl_options = {'REGISTER'}

    index: bpy.props.IntProperty()  # type: ignore

    def execute(self, context):
        state = _state(context)
        if not (0 <= self.index < len(state.items)):
            return {'CANCELLED'}
        row = state.items[self.index]
        state.index = self.index
        objs = [bpy.data.objects.get(n) for n in (row.name_a, row.name_b)]
        objs = [o for o in objs if o is not None and o.visible_get()]
        if not objs:
            self.report({'WARNING'}, tr("Os itens da colisão não estão visíveis"))
            return {'CANCELLED'}
        for obj in context.selected_objects:
            obj.select_set(False)
        for obj in objs:
            obj.select_set(True)
        context.view_layer.objects.active = objs[0]
        window = context.window
        for area in (window.screen.areas if window is not None else ()):
            if area.type != 'VIEW_3D':
                continue
            region = next((r for r in area.regions if r.type == 'WINDOW'), None)
            if region is None:
                continue
            with context.temp_override(window=window, area=area, region=region):
                bpy.ops.view3d.view_selected()
        return {'FINISHED'}


class BTM_OT_CollisionClear(bpy.types.Operator):
    """Limpa a lista de colisões e o destaque na viewport"""
    bl_idname = "caffmob.collision_clear"
    bl_label = "Limpar colisões"
    bl_options = {'REGISTER'}

    def execute(self, context):
        state = _state(context)
        state.items.clear()
        state.checked = -1
        state.checked_names = ""
        state.stale = False
        state.error = ""
        scan._redraw(context)
        return {'FINISHED'}


class BTM_OT_CollisionPushOut(bpy.types.Operator):
    """Afasta o item pelo menor caminho até ele só encostar no outro (item grudado anda só no plano da face)"""
    bl_idname = "caffmob.collision_push_out"
    bl_label = "Afastar até encostar"
    bl_options = {'REGISTER', 'UNDO'}

    index: bpy.props.IntProperty()  # type: ignore

    def execute(self, context):
        state = _state(context)
        if not (0 <= self.index < len(state.items)):
            return {'CANCELLED'}
        if state.stale:                   # o resultado não vale mais (pergunta 32)
            self.report({'WARNING'}, tr("Desatualizado, verifique de novo"))
            return {'CANCELLED'}
        row = state.items[self.index]
        name, push = row.name_a, Vector(row.push)
        chosen = {o.name for sel in context.selected_objects for o in [sel] + list(_ancestors(sel))}
        if row.name_b in chosen and row.name_a not in chosen:
            name, push = row.name_b, -push        # o selecionado é o segundo do par: ele é que sai
        obj = bpy.data.objects.get(name)
        if obj is None:
            return {'CANCELLED'}
        from ..stick import apply as stick_apply
        if stick_apply.linked(obj):
            st = obj.btm_stick
            fr, _extent = stick_apply.face_of(obj)
            normal = (st.host.matrix_world.to_3x3() @ Vector(fr[3])).normalized()
            push -= normal * push.dot(normal)            # só no plano da face
            if push.length < 1e-6:
                self.report({'WARNING'}, tr("O item grudado não pode sair da face; mova o outro item"))
                return {'CANCELLED'}
        obj.matrix_world.translation += push
        context.view_layer.update()
        if stick_apply.linked(obj):
            stick_apply.project(obj)
        scan.check_moved([obj])
        self.report({'INFO'}, tr("{} afastado {:.1f} mm").format(obj.name, push.length * 1000.0))
        return {'FINISHED'}


classes = (BTM_OT_CheckCollisions, BTM_OT_CollisionGoto, BTM_OT_CollisionClear, BTM_OT_CollisionPushOut)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        if cls.is_registered:
            bpy.utils.unregister_class(cls)
