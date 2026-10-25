"""Migração M-05 (feature 067, T102; data-delta §5): variante `<nome> ROTATED` → veio na peça.

No `load_post`, o objeto que usa um material `<nome> ROTATED` com o material de origem no arquivo, e ainda sem veio
gravado, recebe `btm_part.grain = V` e `btm_grain_rot` equivalente ao giro antigo (90° em Z no Mapping). O material
antigo continua até a primeira edição de veio da peça (`grain.sync` troca pelo de origem). Idempotente: peça que já
tem veio fica como está. Os `ROTATED` internos das bibliotecas HB (montantes e travessas) não têm o material de imagem
de origem e ficam fora.
"""

import bpy  # type: ignore
from bpy.app.handlers import persistent  # type: ignore

from . import grain, grain_core as gc


def _legacy(obj):
    if obj.type != 'MESH' or obj.data is None:
        return False
    for mat in grain.image_materials(obj) + [m for m in obj.data.materials if m is not None]:
        if mat.name.endswith(grain.ROTATED_SUFFIX):
            base = bpy.data.materials.get(mat.name[:-len(grain.ROTATED_SUFFIX)])
            if base is not None and grain.is_image_material(base):
                return True
    return False


def migrate_object(obj):
    part = getattr(obj, 'btm_part', None)
    if part is None or part.grain != 'NONE' or grain.ATTR in obj or not _legacy(obj):
        return False
    with grain.suspended():                 # V sem o update: o material antigo fica até a 1ª edição de veio
        part.grain = 'V'
    obj[grain.ATTR] = list(gc.legacy_rotated())
    return True


def run():
    return sum(1 for obj in bpy.data.objects if migrate_object(obj))


@persistent
def _on_load(*_args):
    try:
        run()
    except (AttributeError, ReferenceError, RuntimeError) as exc:
        print(f"CAFFMob Draw: migração do veio (M-05) não rodou: {exc}")


def register():
    if _on_load not in bpy.app.handlers.load_post:
        bpy.app.handlers.load_post.append(_on_load)


def unregister():
    if _on_load in bpy.app.handlers.load_post:
        bpy.app.handlers.load_post.remove(_on_load)
