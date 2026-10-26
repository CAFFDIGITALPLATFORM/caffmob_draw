"""Projeto do Promob no Blender (071, onda A): leitura do `.promob`, documento do CAFF MOBI e complemento local."""


def register():
    from . import ops
    ops.register()


def unregister():
    from . import ops
    ops.unregister()
