from . import draw_handlers, element_toast, selection_cotas, side_cotas

_MODULES = (draw_handlers, selection_cotas, side_cotas, element_toast)


def register():
    for module in _MODULES:
        module.register()


def unregister():
    for module in reversed(_MODULES):
        module.unregister()
