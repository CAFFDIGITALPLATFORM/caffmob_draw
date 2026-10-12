"""Catálogo da biblioteca de objetos do ambiente (feature 009, T014; RN-08, D-08). Python puro, sem `bpy`.

Categorias, entrada do manifesto (ler, validar, escrever), id estável e busca.
Contrato: `_reversa_forward/009-mira-calculo-skp-biblioteca/interfaces/object-library-item.md`.
"""

import re
import secrets
import unicodedata
from dataclasses import dataclass, field

from ..data.i18n import N_

FORMAT = "caffmob_draw.object_item"
VERSION = 1
BUNDLED_SOURCE = "CAFFMob Draw"
FORBIDDEN_BUNDLED_SOURCE = "3D Warehouse"         # licença do 3D Warehouse proíbe redistribuir (RN-09)

# (chave, rótulo, ícone do Blender)
CATEGORIES = (
    ('DOORS', N_("Portas"), 'MESH_PLANE'),
    ('WINDOWS', N_("Janelas"), 'MESH_GRID'),
    ('COOKTOPS', N_("Cooktops e eletros"), 'MESH_CIRCLE'),
    ('TABLES', N_("Mesas"), 'MESH_CUBE'),
    ('SEATING', N_("Cadeiras e assentos"), 'MESH_CONE'),
    ('DECOR', N_("Decoração"), 'MESH_MONKEY'),
    ('OTHER', N_("Outros"), 'MESH_ICOSPHERE'),
)
CATEGORY_KEYS = tuple(c[0] for c in CATEGORIES)
CATEGORY_ITEMS = [(key, label, "", icon, i) for i, (key, label, icon) in enumerate(CATEGORIES)]
FEATURES = ('GROUP', 'FRAME', 'LEAF_SWING', 'LEAF_SLIDE', 'AGGREGATE', 'PRODUCTION_PART', 'TEXTURED')
_ID = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")


class ManifestError(ValueError):
    pass


@dataclass
class Entry:
    item_id: str
    name: str
    category: str
    root: str
    source: str = ""
    author: str = ""
    license: str = ""
    size_mm: list = field(default_factory=lambda: [0.0, 0.0, 0.0])
    features: list = field(default_factory=list)
    materials: list = field(default_factory=list)
    created_at: str = ""
    addon_version: str = ""


def slug(text):
    text = unicodedata.normalize('NFKD', str(text)).encode('ascii', 'ignore').decode('ascii').lower()
    return re.sub(r"[^a-z0-9]+", "-", text).strip("-") or "item"


def new_item_id(name, token=None):
    return "{}-{}".format(slug(name), token or secrets.token_hex(3))


def read_manifest(data):
    """`Entry` do dicionário do JSON; `ManifestError` se o formato, a versão ou um campo obrigatório falhar."""
    if not isinstance(data, dict) or data.get("format") != FORMAT:
        raise ManifestError("formato desconhecido")
    if data.get("version") != VERSION:
        raise ManifestError("versão {} não suportada".format(data.get("version")))
    for key in ("item_id", "name", "root"):
        if not isinstance(data.get(key), str) or not data[key].strip():
            raise ManifestError("campo obrigatório ausente: " + key)
    if not _ID.fullmatch(data["item_id"]):       # "$" aceitaria um "\n" final
        raise ManifestError("item_id inválido: " + data["item_id"])
    category = data.get("category") if data.get("category") in CATEGORY_KEYS else 'OTHER'
    size = [float(v) for v in (data.get("size_mm") or [0.0, 0.0, 0.0])][:3]
    return Entry(data["item_id"], data["name"], category, data["root"], str(data.get("source", "")),
                 str(data.get("author", "")), str(data.get("license", "")), size,
                 [f for f in data.get("features", []) if f in FEATURES], list(data.get("materials", [])),
                 str(data.get("created_at", "")), str(data.get("addon_version", "")))


def to_manifest(entry):
    return {"format": FORMAT, "version": VERSION, "item_id": entry.item_id, "name": entry.name,
            "category": entry.category, "root": entry.root, "source": entry.source, "author": entry.author,
            "license": entry.license, "size_mm": [float(v) for v in entry.size_mm], "features": list(entry.features),
            "materials": list(entry.materials), "created_at": entry.created_at, "addon_version": entry.addon_version}


def search(entries, text):
    needle = slug(text) if text and text.strip() else ""
    return [e for e in entries if not needle or needle in slug(e.name)]
