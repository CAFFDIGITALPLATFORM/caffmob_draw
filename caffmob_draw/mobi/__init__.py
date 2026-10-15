# (063 RF-01; D-03) Registro do MOBI sem criar outra aba ou painel.
from . import estado, tarefas, ops_conta, ops_ambientes, ops_biblioteca

MODULES = (estado, tarefas, ops_conta, ops_ambientes, ops_biblioteca)


def register():
    for module in MODULES:
        module.register()


def unregister():
    for module in reversed(MODULES):
        module.unregister()
