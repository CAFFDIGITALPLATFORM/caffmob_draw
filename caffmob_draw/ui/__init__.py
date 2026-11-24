from . import context_menu, header_collision, object_properties, ops_resize, panels, save_feedback, sidebar, sidebar_props, sidebar_selection, standards_tree

# Ordem de registro: a UIList antes dos painéis que a usam; o estado da barra lateral antes do painel hospedeiro.
_MODULES = (standards_tree, panels, object_properties, save_feedback, sidebar_props, sidebar, sidebar_selection,
            ops_resize, context_menu, header_collision)


def register():
    for module in _MODULES:
        module.register()


def unregister():
    for module in reversed(_MODULES):
        module.unregister()
