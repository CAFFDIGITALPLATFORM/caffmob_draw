"""Construtor de gavetas e catálogo de corrediças (072)."""


def register():
    from . import ops, props
    ops.register()
    props.register()


def unregister():
    from . import ops, props
    props.unregister()
    ops.unregister()
