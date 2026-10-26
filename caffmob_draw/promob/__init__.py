"""Projeto do Promob no Blender (071, onda A): leitura do `.promob`, documento do CAFF MOBI e complemento local."""


def register():
    from . import cameras, ops
    ops.register()
    cameras.register()


def unregister():
    from . import cameras, ops
    cameras.unregister()
    ops.unregister()
