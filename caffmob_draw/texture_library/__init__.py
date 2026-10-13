"""Texturas dos fabricantes de chapas (feature 014): catálogo, download, conta CAF Mob e aplicação.

- `catalog_core`, `catalog`: catálogo do pacote (miniaturas e tamanhos; as imagens ficam no servidor);
- `download_core`, `downloader`, `downloads`: download em subprocesso, sem travar o Blender (D-11);
- `auth_core`, `auth`: conta CAF Mob por código de dispositivo (D-12, D-13);
- `apply`, `ops_apply`, `bump`: aplicar textura (com o relevo, quando há) e ajustar o tamanho real; `ops_account`: entrar, sair e baixar tudo;
- `handlers`: caminhos das imagens ao abrir um arquivo e encerramento da rede ao trocar de arquivo.

O `unregister` desfaz tudo (princípio VII): operadores, handlers, timers e o subprocesso de rede.
"""


def _modules():
    from . import handlers, ops_account, ops_apply
    return (ops_account, ops_apply, handlers)


def register():
    for module in _modules():
        module.register()


def unregister():
    from . import auth, downloads
    downloads.shutdown()
    auth.shutdown()
    for module in reversed(_modules()):
        module.unregister()
