"""Redimensionar (menu do botão direito): digita a nova largura do elemento selecionado.

A regra fica em `selection/resize.py`: o pai muda pela medida própria dele e os agregados são esticados na proporção.
Na porta, a largura é a da folha (como o campo da porta); depois mostra o aviso com as medidas novas.
"""

import bpy  # type: ignore

from ..data.i18n import tr


def _element(context):
    from ..selection import element_size
    obj = context.active_object
    return element_size.element(obj) if obj is not None and obj.select_get() else None


class BTM_OT_ResizeWidth(bpy.types.Operator):
    """Muda a largura do elemento selecionado; os agregados dele se adaptam à nova largura"""
    bl_idname = "caffmob.resize_width"
    bl_label = "Redimensionar"
    bl_options = {'REGISTER', 'UNDO'}

    width: bpy.props.FloatProperty(name="Largura", subtype='DISTANCE', unit='LENGTH', min=0.01, max=100.0,
                                   precision=5)  # type: ignore

    @classmethod
    def poll(cls, context):
        from ..selection import resize
        try:
            return resize.can_resize(_element(context))
        except Exception:
            return False

    def invoke(self, context, event):
        from ..selection import element_size
        self.width = element_size.size(_element(context))[0]
        return context.window_manager.invoke_props_dialog(self, width=260, title=tr("Redimensionar"))

    def draw(self, context):
        el = _element(context)
        if el is not None:
            self.layout.label(text=el.obj.name)
        self.layout.prop(self, "width")

    def execute(self, context):
        from ..overlays import element_toast
        from ..selection import resize
        el = _element(context)
        try:
            resize.resize(context, el, self.width)
        except ValueError as exc:
            self.report({'ERROR'}, str(exc))
            return {'CANCELLED'}
        obj = context.active_object
        element_toast.show(obj if obj is not None and obj.name in bpy.data.objects else el.obj)
        return {'FINISHED'}


classes = (BTM_OT_ResizeWidth,)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        if cls.is_registered:
            bpy.utils.unregister_class(cls)
