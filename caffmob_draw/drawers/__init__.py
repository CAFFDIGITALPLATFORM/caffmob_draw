"""Construtor de gavetas e catálogo de corrediças (072)."""


def register():
    from . import construtor, ops, props
    ops.register()
    props.register()
    construtor.register()      # onda B: espaço livre, gaveteiro e modelos


def unregister():
    from . import construtor, ops, props
    construtor.unregister()
    props.unregister()
    ops.unregister()
