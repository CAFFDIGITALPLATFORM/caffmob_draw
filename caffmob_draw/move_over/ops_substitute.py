"""Substituir no "Mover Sobre" (feature 003, T058; RF-27, D-23).

Troca o objeto movido (A) por um módulo da biblioteca do usuário, no mesmo lugar: o novo recebe a rotação de A e
encosta no mesmo canto de referência (o lado de B em que A estava, a frente e a base); A é apagado. Um passo de
desfazer. Nesta versão a busca cobre a biblioteca de módulos do usuário (`customize/library_io`).
"""

import bpy  # type: ignore
from mathutils import Vector  # type: ignore

from ..data.i18n import N_, tr
from ..customize import library_io
from . import reposition
from .scene import _frame, _local_box, tree_corners

_ITEMS = []


def _module_items(self, context):
    global _ITEMS
    _ITEMS = [(e["blend"], f"{e['category']} / {e['name']}", "") for e in library_io.list_modules()]
    return _ITEMS or [("", N_("Nenhum módulo salvo"), "")]


def _tree_box(frame_inv, root):
    """Caixa da árvore visível no referencial dado: a mesma do Mover Sobre, sem peças vazias (pergunta 16)."""
    corners = [frame_inv @ c for c in tree_corners(root, bpy.context.evaluated_depsgraph_get())]
    return (tuple(min(c[i] for c in corners) for i in range(3)), tuple(max(c[i] for c in corners) for i in range(3)))


def substitute(context, a, b, entry):
    """Insere o módulo de `entry` no lugar de `a` (referência `b`); devolve (novo, avisos)."""
    root, loaded, warnings = library_io.load(context, entry)
    if root is None:
        for obj in loaded:
            if obj.name in bpy.data.objects:
                bpy.data.objects.remove(obj, do_unlink=True)
        return None, warnings
    frame = _frame(b)
    frame_inv = frame.inverted()
    place = _frame(a)                       # posição e rotação de A, sem a escala (questions.md, pergunta 19)
    root.matrix_world = place
    root.parent = a.parent
    if a.parent is not None:
        root.matrix_parent_inverse = a.matrix_parent_inverse.copy()
        root.matrix_world = place
    context.view_layer.update()
    box_a, box_b, box_new = _tree_box(frame_inv, a), _local_box(b, context.evaluated_depsgraph_get()), \
        _tree_box(frame_inv, root)
    side = reposition.side_of(box_a, box_b)
    dx = (box_a[0][0] - box_new[0][0]) if side == 'RIGHT' else (box_a[1][0] - box_new[1][0])
    delta = Vector((dx, box_a[0][1] - box_new[0][1], box_a[0][2] - box_new[0][2]))
    root.matrix_world.translation += frame.to_3x3() @ delta
    for obj in [a] + list(a.children_recursive)[::-1]:
        if obj.name in bpy.data.objects:
            bpy.data.objects.remove(obj, do_unlink=True)
    return root, warnings


class BTM_OT_MoveOverSubstitute(bpy.types.Operator):
    """Troca o objeto por um módulo da biblioteca, no mesmo lugar e com a mesma rotação"""
    bl_idname = "caffmob.move_over_substitute"
    bl_label = "Substituir"
    bl_options = {'REGISTER', 'UNDO'}

    a_name: bpy.props.StringProperty(options={'HIDDEN'})  # type: ignore
    b_name: bpy.props.StringProperty(options={'HIDDEN'})  # type: ignore
    module: bpy.props.EnumProperty(name="Módulo", items=_module_items)  # type: ignore

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, width=360, title="Substituir por")

    def execute(self, context):
        a, b = bpy.data.objects.get(self.a_name), bpy.data.objects.get(self.b_name)
        entry = next((e for e in library_io.list_modules() if e["blend"] == self.module), None)
        if a is None or b is None or entry is None:
            self.report({'WARNING'}, "Escolha um módulo da biblioteca do usuário")
            return {'CANCELLED'}
        name = a.name
        new, warnings = substitute(context, a, b, entry)
        if new is None:
            self.report({'WARNING'}, " | ".join(warnings))
            return {'CANCELLED'}
        for obj in context.selected_objects:
            obj.select_set(False)
        new.select_set(True)
        context.view_layer.objects.active = new
        self.report({'WARNING'} if warnings else {'INFO'},
                    " | ".join(warnings) if warnings else tr("{} substituído por {}").format(name, new.name))
        return {'FINISHED'}


classes = (BTM_OT_MoveOverSubstitute,)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        if cls.is_registered:
            bpy.utils.unregister_class(cls)
