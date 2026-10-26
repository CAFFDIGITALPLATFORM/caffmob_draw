"""Editor de escadas de marcenaria (071, onda B), trazido do OpenMob."""


def register():
    from . import ops, preview, props
    props.register()
    ops.register()
    preview.register()


def unregister():
    from . import ops, preview, props
    preview.unregister()
    ops.unregister()
    props.unregister()
