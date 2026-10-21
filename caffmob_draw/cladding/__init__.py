"""Revestimentos locais do Blender, sem contrato externo (RN-16)."""


def register():
    from . import props, ops, sync
    for module in (props, ops, sync):
        module.register()


def unregister():
    from . import props, ops, sync
    for module in (sync, ops, props):
        module.unregister()
