"""Handlers de arquivo das texturas (feature 014, T037, T038; D-09, princípio VII).

- `load_post`: o caminho da imagem muda entre computadores. Cada material com `btm_texture_id` tem a imagem
  apontada de novo para o cache do usuário (`downloads.cache_path`). Imagem ainda não baixada: o material fica como
  está e a textura é baixada na próxima vez que for usada. Ids fora do catálogo do pacote são avisados uma vez.
- `load_pre`: encerra o subprocesso de rede e esquece a fila e o login em andamento (os pedidos eram do arquivo que
  está fechando).
"""

import os

import bpy  # type: ignore
from bpy.app.handlers import persistent  # type: ignore

from ..data.i18n import N_, tr
from ..object_library import retexture
from . import auth, catalog, downloads

UNKNOWN_IDS = N_("{} textura(s) deste projeto não estão no catálogo instalado: {}")
_warned = set()


def relink(materials=None):
    """Aponta as imagens do catálogo para o cache; devolve (refeitas, ids fora do catálogo)."""
    fixed, unknown = 0, []
    for mat in (materials if materials is not None else bpy.data.materials):
        tid = mat.get(retexture.TEXTURE_ID_PROP)
        if not tid:
            continue
        entry = catalog.item(tid)
        if entry is None:
            unknown.append(str(tid))
            continue
        path = downloads.cache_path(entry)
        if not os.path.isfile(path) or mat.get(retexture.PATH_PROP) == path:
            continue
        mat[retexture.PATH_PROP] = path
        for node in (mat.node_tree.nodes if mat.node_tree else []):
            if node.type == 'TEX_IMAGE' and node.image is not None:
                node.image.filepath = path
                node.image.reload()
        fixed += 1
    return fixed, unknown


@persistent
def on_load_post(_filepath=None, *_args):
    try:
        _fixed, unknown = relink()
    except (ReferenceError, RuntimeError, OSError):
        return
    new = sorted(set(unknown) - _warned)
    if new:
        _warned.update(new)
        from ..ui import save_feedback
        save_feedback.show(tr(UNKNOWN_IDS).format(len(new), ", ".join(new[:3]) + ("…" if len(new) > 3 else "")))


@persistent
def on_load_pre(_filepath=None, *_args):
    downloads.shutdown()
    auth.shutdown()


def register():
    if on_load_post not in bpy.app.handlers.load_post:
        bpy.app.handlers.load_post.append(on_load_post)
    if on_load_pre not in bpy.app.handlers.load_pre:
        bpy.app.handlers.load_pre.append(on_load_pre)


def unregister():
    for handlers, fn in ((bpy.app.handlers.load_post, on_load_post), (bpy.app.handlers.load_pre, on_load_pre)):
        if fn in handlers:
            handlers.remove(fn)
