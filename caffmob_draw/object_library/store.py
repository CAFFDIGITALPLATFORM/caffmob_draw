"""Pastas e listagem da biblioteca de objetos (feature 009, T015; D-08, D-11). Sem `bpy` (as pastas vêm de fora).

Duas pastas: a embutida (`object_library/items`, só leitura) e a do usuário (`extension_path_user`). Cada item são
três arquivos com o mesmo nome-base (`<item_id>.blend|.json|.png`) na pasta da categoria.
"""

import json
import os
from dataclasses import dataclass

from . import catalog

BUNDLED_DIR = os.path.join(os.path.dirname(__file__), "items")


@dataclass
class Item:
    entry: catalog.Entry
    user: bool
    blend: str
    manifest: str
    thumb: str = None


def paths_for(folder, category, item_id):
    base = os.path.join(folder, category, item_id)
    return {"blend": base + ".blend", "json": base + ".json", "png": base + ".png"}


def _scan(folder, user, warnings):
    found = []
    if not folder or not os.path.isdir(folder):
        return found
    for category in sorted(os.listdir(folder)):
        cat_dir = os.path.join(folder, category)
        if not os.path.isdir(cat_dir):
            continue
        for name in sorted(os.listdir(cat_dir)):
            if not name.endswith(".json"):
                continue
            path = os.path.join(cat_dir, name)
            try:
                with open(path, encoding="utf-8") as handle:
                    entry = catalog.read_manifest(json.load(handle))
            except (OSError, ValueError, TypeError, KeyError, AttributeError) as exc:   # tipo inesperado (EC-01)
                warnings.append("{}: {}".format(path, exc))
                continue
            paths = paths_for(folder, category, entry.item_id)
            if not os.path.isfile(paths["blend"]):
                warnings.append("{}: falta o .blend".format(path))
                continue
            found.append(Item(entry, user, paths["blend"], path,
                              paths["png"] if os.path.isfile(paths["png"]) else None))
    return found


def list_items(bundled_dir, user_dir):
    """(itens embutidos e depois os do usuário, avisos de arquivos ignorados)."""
    warnings = []
    return _scan(bundled_dir, False, warnings) + _scan(user_dir, True, warnings), warnings


def by_category(items, category):
    return [i for i in items if i.entry.category == category]


def unique_name(existing, name):
    """Renomear (D-11): "Mesa" → "Mesa 2", "Mesa 3"… até não repetir."""
    taken = set(existing)
    if name not in taken:
        return name
    n = 2
    while f"{name} {n}" in taken:
        n += 1
    return f"{name} {n}"


def delete(item):
    """Apaga os três arquivos de um item do usuário; um item embutido não pode ser apagado."""
    if not item.user:
        raise PermissionError("item embutido")
    base = item.blend[:-len(".blend")]
    for ext in (".blend", ".json", ".png", ".blend1"):
        if os.path.isfile(base + ext):
            os.remove(base + ext)


def check_bundled(entries):
    """Itens embutidos com origem proibida (RN-09); vazio = pacote limpo."""
    return [e.item_id for e in entries if e.source.strip().lower().startswith(
        catalog.FORBIDDEN_BUNDLED_SOURCE.lower())]
