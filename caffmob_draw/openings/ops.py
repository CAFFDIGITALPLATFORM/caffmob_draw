"""Atualizar portas e janelas (feature 010, T022; RN-04, D-16) e inverter a porta pela tecla I.

Caixas de porta e janela de arquivos antigos (sem a porta real) ou de uma versão anterior do gerador são montadas de
novo, nas mesmas posições e medidas. Nunca roda sozinho: a barra lateral só avisa.

Tecla I com uma porta selecionada (a caixa, a folha ou qualquer peça dela): troca a dobradiça de lado, o que inverte o
giro (horário ↔ anti-horário) mantendo o lado da parede para onde ela abre. Sem porta selecionada, o I segue o
padrão do Blender (o `poll` falha e o evento passa adiante).
"""

import bpy  # type: ignore

from ..data.i18n import tr
from . import sync


class BTM_OT_OpeningsUpdate(bpy.types.Operator):
    """Troca as portas e janelas em caixa deste arquivo pelas portas e janelas reais"""
    bl_idname = "caffmob.openings_update"
    bl_label = "Atualizar portas e janelas"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.scene is not None

    def execute(self, context):
        cages = sync.outdated(context.scene)
        done, failed = sync.sync_each(context, cages, force=True)
        if failed:
            self.report({'WARNING'}, tr("Não foi possível montar a porta ou janela real de: {}").format(", ".join(failed)))
        elif not cages:
            self.report({'INFO'}, tr("Todas as portas e janelas já estão atualizadas"))
        else:
            self.report({'INFO'}, tr("{} porta(s) e janela(s) atualizada(s)").format(done))
        return {'FINISHED'}


def door_of(obj):
    """Caixa da porta (com símbolo de giro) que contém `obj`, ou None."""
    while obj is not None:
        if obj.get(sync.DOOR_FLAG):
            swing_obj = sync._swing(obj)[0]
            return obj if swing_obj is not None else None
        obj = obj.parent
    return None


class BTM_OT_DoorInvertHand(bpy.types.Operator):
    """Troca a dobradiça da porta de lado: inverte o giro (horário ↔ anti-horário)"""
    bl_idname = "btm.door_invert_hand"
    bl_label = "Inverter giro da porta"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        obj = context.active_object
        return obj is not None and obj.select_get() and door_of(obj) is not None

    def execute(self, context):
        from .. import hb_types
        door = door_of(context.active_object)
        swing = hb_types.GeoNodeObject(sync._swing(door)[0])
        swing.set_input('Is Left', not bool(swing.get_input('Is Left')))
        sync.sync(context, door)
        if context.view_layer.objects.active is None:       # a folha selecionada foi refeita: seleciona a nova
            assembly = door.btm_opening_real.assembly
            target = next((o for o in assembly.children_recursive if o.type == 'MESH'), None) if assembly else None
            target = target or door
            target.select_set(True)
            context.view_layer.objects.active = target
        self.report({'INFO'}, tr("Giro da porta invertido"))
        return {'FINISHED'}


classes = (BTM_OT_OpeningsUpdate, BTM_OT_DoorInvertHand)
_addon_keymaps = []


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    wm = bpy.context.window_manager
    kc = wm.keyconfigs.addon if wm else None
    if kc is not None:
        km = kc.keymaps.new(name='Object Mode', space_type='EMPTY')
        kmi = km.keymap_items.new(BTM_OT_DoorInvertHand.bl_idname, 'I', 'PRESS', head=True)
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
