"""Arquivos das texturas (063 RF-04; D-07).

load_post reaponta materiais com sha para o cache único; slugs antigos da 014 mantêm o caminho original.
load_pre encerra os pedidos e o login do arquivo anterior.
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
        sha = mat.get("btm_texture_sha256")
        if not sha:
            continue                                # slug da 014 mantém o caminho original
        formato = mat.get("btm_texture_formato", "jpeg")
        path = os.path.join(downloads.cache_dir(), sha + (".jpg" if formato == "jpeg" else "." + formato))
        if not os.path.isfile(path) or mat.get(retexture.PATH_PROP) == path:
            continue
        mat[retexture.PATH_PROP] = path
        for node in (mat.node_tree.nodes if mat.node_tree else []):
            if node.type == 'TEX_IMAGE' and node.image is not None and node.image.colorspace_settings.name != 'Non-Color':
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
