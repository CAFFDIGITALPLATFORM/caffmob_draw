"""Catálogo de texturas do pacote em tempo de uso (feature 014, T016; D-02, D-17).

Lê `caffmob_draw/textures/catalog.json` uma vez por sessão (cache até `invalidate()`); o desenho do painel nunca lê o
disco. Arquivo ausente vira catálogo vazio com o aviso "Texturas não instaladas"; inválido, com "Catálogo de
texturas inválido" (`catalog_core.parse_catalog`).
"""

import os

from ..data.i18n import N_
from . import catalog_core

TEXTURES_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "textures")
CATALOG_FILE = os.path.join(TEXTURES_DIR, "catalog.json")
NOT_INSTALLED = N_("Texturas não instaladas")

_cache = {"catalog": None, "warnings": [], "by_id": {}}


def invalidate():
    _cache.update(catalog=None, warnings=[], by_id={})


def load():
    """(catálogo, avisos), lido uma vez."""
    if _cache["catalog"] is None:
        try:
            with open(CATALOG_FILE, encoding="utf-8") as handle:
                catalog, warnings = catalog_core.parse_catalog(handle.read())
        except OSError:
            catalog, warnings = catalog_core.empty_catalog(), [NOT_INSTALLED]
        _cache["catalog"], _cache["warnings"] = catalog, warnings
        _cache["by_id"] = {item["id"]: item for item in catalog_core.iter_items(catalog)}
    return _cache["catalog"], _cache["warnings"]


def manufacturers():
    catalog, _warnings = load()
    return [(m["id"], m["name"]) for m in catalog["manufacturers"]]


def collections(manufacturer_id):
    catalog, _warnings = load()
    for man in catalog["manufacturers"]:
        if man["id"] == manufacturer_id:
            return [(c["id"], c["name"]) for c in man["collections"]]
    return []


def item(item_id):
    load()
    return _cache["by_id"].get(item_id)


def search(text="", manufacturer="", collection=""):
    catalog, _warnings = load()
    return catalog_core.search(catalog, text, manufacturer=manufacturer, collection=collection)


def thumb_path(entry):
    """Caminho absoluto da miniatura de um item (vem no pacote)."""
    return os.path.join(TEXTURES_DIR, entry["thumb"])


def default_size(entry):
    """(largura, altura) em mm do catálogo (RN-04)."""
    width, height = entry.get("size-mm") or (catalog_core.DEFAULT_SIZE_MM, catalog_core.DEFAULT_SIZE_MM)
    return float(width), float(height)
