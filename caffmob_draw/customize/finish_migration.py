"""Migração M-03 (feature 067, T097; data-delta §5): grupos de material antigos → `btm_finish`.

No `load_post`, cada objeto com `btm_custom.group_materials` ou `front_material` e sem `btm_finish` ganha as entradas
de `finish_core.migrate_groups` com origem MIGRATED. Nada muda na malha nem nos materiais: a aparência continua a
mesma, pelo caminho antigo (`customize/finish.reapply` não reaplica as migradas). Idempotente: objeto que já tem
`btm_finish` fica como está.
"""

import bpy  # type: ignore
from bpy.app.handlers import persistent  # type: ignore

from . import finish_core as fc


def migrate_object(obj):
    """Grava as entradas migradas de um objeto; devolve quantas."""
    custom = getattr(obj, 'btm_custom', None)
    if custom is None or len(obj.btm_finish):
        return 0
    groups = {item.group: item.material for item in custom.group_materials if item.material}
    domains = fc.migrate_groups(groups, custom.front_material)
    count = 0
    for domain in fc.DOMAINS:
        material = bpy.data.materials.get(domains.get(domain, '')) if domain in domains else None
        if material is None:
            continue
        item = obj.btm_finish.add()
        item.domain, item.material, item.source = domain, material, 'MIGRATED'
        item.grain = fc.DEFAULT_GRAIN[domain]
        count += 1
    return count


def run():
    return sum(migrate_object(obj) for obj in bpy.data.objects
               if getattr(obj, 'btm_custom', None) is not None
               and (obj.btm_custom.group_materials or obj.btm_custom.front_material))


@persistent
def _on_load(*_args):
    try:
        run()
    except (AttributeError, ReferenceError, RuntimeError) as exc:
        print(f"CAFFMob Draw: migração dos acabamentos (M-03) não rodou: {exc}")


def register():
    if _on_load not in bpy.app.handlers.load_post:
        bpy.app.handlers.load_post.append(_on_load)


def unregister():
    if _on_load in bpy.app.handlers.load_post:
        bpy.app.handlers.load_post.remove(_on_load)
