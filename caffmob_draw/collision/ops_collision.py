"""Operadores do diagnóstico técnico de colisão (feature 004, T039, T040; feature 066, T075, D-07, RF-024).

O diagnóstico só existe sob pedido: `caffmob.collision_diagnose` calcula na hora e abre a lista num popup, com "Ir para"
e "Afastar até encostar". Nada fica desenhado na viewport, e nada é avisado ao mover: quem impede a penetração é o
guarda (`guard.py`), em silêncio.
"""

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
        row = state.items[self.index]
        current = _current(context, row.name_a, row.name_b)     # a lista é de quando foi aberta: vale a cena de agora
        if current is None:
            self.report({'WARNING'}, tr("Esses itens não colidem mais"))
            scan.check_all(context, state.scope)
            return {'CANCELLED'}
        name, push = current.name_a, Vector(current.push)
        chosen = {o.name for sel in context.selected_objects for o in [sel] + list(_ancestors(sel))}
        other = current.name_b
        if other in chosen and name not in chosen:
            name, push = other, -push             # o selecionado é o segundo do par: ele é que sai
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
        context.view_layer.update()                  # o guarda confere o afastamento como qualquer movimento
        scan.check_all(context, state.scope)
        self.report({'INFO'}, tr("{} afastado {:.1f} mm").format(obj.name, push.length * 1000.0))
        return {'FINISHED'}


def _current(context, name_a, name_b):
    """A ocorrência do par na cena de agora (ou None, quando não colidem mais)."""
    found, _entries = scan.find(context, {name_a, name_b})
    return next((c for c in found if {c.name_a, c.name_b} == {name_a, name_b}), None)


class BTM_OT_CollisionDiagnose(bpy.types.Operator):
    """Diagnóstico técnico: calcula agora as colisões da cena e mostra a lista, com Ir para e Afastar"""
    bl_idname = "caffmob.collision_diagnose"
    bl_label = "Diagnóstico técnico"
    bl_options = {'REGISTER'}

    scope: bpy.props.EnumProperty(
        name="Escopo", items=[('ALL', "Cena", "Todos os itens da cena"),
                              ('SELECTED', "Selecionado", "Só o item selecionado e o que ele toca")],
        default='ALL')  # type: ignore

    def _run(self, context):
        if self.scope == 'SELECTED' and not context.selected_objects:
            self.report({'WARNING'}, tr("Selecione um item"))
            return False
        return scan.check_all(context, self.scope) is not None or bool(_state(context).error)

    def invoke(self, context, event):
        if not self._run(context):
            return {'CANCELLED'}
        return context.window_manager.invoke_popup(self, width=480)

    def execute(self, context):
        return {'FINISHED'} if self._run(context) else {'CANCELLED'}

    def draw(self, context):
        from . import panels
        panels.draw_collisions(self.layout, context)


classes = (BTM_OT_CheckCollisions, BTM_OT_CollisionGoto, BTM_OT_CollisionClear, BTM_OT_CollisionPushOut,
           BTM_OT_CollisionDiagnose)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        if cls.is_registered:
            bpy.utils.unregister_class(cls)
