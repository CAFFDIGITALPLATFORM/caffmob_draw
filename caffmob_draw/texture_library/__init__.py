"""Texturas dos fabricantes de chapas (feature 014): catálogo, download, conta CAF Mob e aplicação.

- `catalog_core`, `catalog`: catálogo remoto do MOBI e correspondência com a grade (063 D-07);
- `download_core`, `downloader`, `downloads`: download em subprocesso, sem travar o Blender (D-11);
- `auth_core`, `auth`: conta CAF Mob por código de dispositivo (D-12, D-13);
- `ops_finish_drop`: o diálogo do soltar textura, por domínio (067 onda 2);
- `apply`, `ops_apply`, `bump`: aplicar textura (com o relevo, quando há) e ajustar o tamanho real; `ops_account`: entrar, revogar e cancelar downloads;
- `handlers`: caminhos das imagens ao abrir um arquivo e encerramento da rede ao trocar de arquivo.

O `unregister` desfaz tudo (princípio VII): operadores, handlers, timers e o subprocesso de rede.
"""


def _modules():
    from . import handlers, ops_account, ops_apply, ops_finish_drop
    return (ops_account, ops_apply, ops_finish_drop, handlers)


def register():
    for module in _modules():
        module.register()


def unregister():
    from . import auth, downloads
    downloads.shutdown()
    auth.shutdown()
    for module in reversed(_modules()):
        module.unregister()
