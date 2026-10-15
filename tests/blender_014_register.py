"""Registro do pacote de texturas e handler de abertura (feature 014, T037, T038; D-09, princípio VII).

Roda em segundo plano:
    blender --background --factory-startup --python-exit-code 1 --python tests/blender_014_register.py

- os operadores da feature existem depois do `register`; os handlers `load_post`/`load_pre` estão registrados;
- `relink` aponta a imagem de um material do catálogo para o cache deste computador e lista ids fora do catálogo;
- `unregister` tira operadores e handlers e não deixa processo nem timer; registrar de novo funciona.
"""

import os
import sys
import traceback
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _blender_env  # noqa: E402,F401
import bpy  # noqa: E402
from caffmob_draw import texture_library  # noqa: E402
from caffmob_draw.object_library import retexture  # noqa: E402
from caffmob_draw.texture_library import catalog, downloads, handlers  # noqa: E402

from _mobi_texture_fixture import TextureServer

server = TextureServer()
FAILURES = []
OPS = ("texture_login", "texture_logout", "texture_download_cancel", "texture_account_menu",
       "texture_apply", "texture_size", "library_drag", "library_search", "library_scroll")


def check(name, ok, detail=""):
    print(("OK   " if ok else "FALHA ") + name, detail, flush=True)
    if not ok:
        FAILURES.append(name)


def _registered(name):
    try:
        getattr(bpy.ops.caffmob, name).get_rna_type()
        return True
    except (KeyError, AttributeError):
        return False


def main():
    missing = [op for op in OPS if not _registered(op)]
    check("operadores da feature registrados", not missing, str(missing))
    check("handlers load_post e load_pre registrados", handlers.on_load_post in bpy.app.handlers.load_post
          and handlers.on_load_pre in bpy.app.handlers.load_pre)

    entries = server.connect()
    tid = entries[0]['id']
    entry = catalog.item(tid)
    dest = server.download(tid)
    old = os.path.join(os.path.dirname(dest), "outro_computador.png")
    Path(old).write_bytes(Path(dest).read_bytes())
    mat = retexture.image_material(old, 600.0, texture_id=tid)
    mat['btm_texture_sha256'] = entry['sha256']
    mat['btm_texture_formato'] = entry['formato']
    legacy = bpy.data.materials.new("Textura antiga da 014")
    legacy[retexture.TEXTURE_ID_PROP] = "fabricante/antigo"
    legacy[retexture.PATH_PROP] = old
    fixed, unknown = handlers.relink([mat, legacy])
    image = next(n.image for n in mat.node_tree.nodes if n.type == 'TEX_IMAGE')
    check("relink aponta pelo sha para o cache deste computador", fixed == 1 and mat[retexture.PATH_PROP] == dest
          and bpy.path.abspath(image.filepath) == dest, f"{fixed} {image.filepath}")
    check("material da 014 preserva o caminho, sem buscar catálogo", legacy[retexture.PATH_PROP] == old and unknown == [])
    check("Baixar tudo foi retirado", not _registered("texture_download_all"))
    handlers.on_load_post(None)                         # avisa uma vez, sem erro

    server.close()
    texture_library.unregister()
    left = [op for op in OPS if op.startswith("texture_") and _registered(op)]
    check("unregister tira os operadores de textura", not left, str(left))
    check("unregister tira os handlers", handlers.on_load_post not in bpy.app.handlers.load_post
          and handlers.on_load_pre not in bpy.app.handlers.load_pre)
    check("unregister sem processo nem timer de rede", not downloads.process_alive()
          and not bpy.app.timers.is_registered(downloads._tick))
    texture_library.register()
    check("registrar de novo funciona", _registered("texture_login"))


try:
    main()
except Exception:
    traceback.print_exc()
    FAILURES.append("exceção")
print(f"blender_014_register: {'OK' if not FAILURES else 'FALHAS: ' + ', '.join(FAILURES)}", flush=True)
sys.exit(1 if FAILURES else 0)
