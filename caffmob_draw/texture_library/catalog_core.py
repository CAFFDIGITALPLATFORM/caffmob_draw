"""Catálogo das texturas dos fabricantes de chapas (feature 014, T013; RN-01 a RN-04, D-02). Python puro.

Entrada: os caminhos relativos à pasta `fabrica/` da biblioteca de texturas do titular (layout do Promob) e as
dimensões em pixels das imagens legíveis. Saída: o dicionário do `catalog.json` (data-delta §1) e os avisos.

- RN-01: só os 12 fabricantes de chapas de móveis planejados (`MANUFACTURERS`), pelo nome da pasta sem caixa;
- RN-02: coleção = subpasta de primeiro nível ("Geral" para imagem solta); subcoleção entra no nome do item;
- RN-03: entram JPG/JPEG/PNG; relevos (`.bump`), auxiliares, pastas "Bumps" e ocultos ficam fora;
- RN-04: imagem de chapa inteira vale 1 px = 1 mm; senão o maior lado vale `DEFAULT_SIZE_MM`.
"""

import json
import re
import unicodedata

from ..data.i18n import N_, tr

SCHEMA_VERSION = 1
CATALOG_VERSION = 1
DEFAULT_SIZE_MM = 600.0
FULL_SHEET_PX = (1830, 2750)            # RN-04: os dois lados dentro desta faixa = chapa inteira
IMAGE_EXT = ('.jpg', '.jpeg', '.png')
GENERAL = "Geral"
INVALID = N_("Catálogo de texturas inválido")

# RN-01: pasta (sem caixa) → nome mostrado
MANUFACTURERS = {
    'arauco': "Arauco", 'berneck': "Berneck", 'duratex': "Duratex", 'eucatex': "Eucatex",
    'fibraplac': "Fibraplac", 'floraplac': "Floraplac", 'formica': "Formica", 'greenplac': "Greenplac",
    'guararapes': "Guararapes", 'lopar': "Lopar", 'placas_do_brasil': "Placas do Brasil", 'sudati': "Sudati",
}


def fold(text):
    """Minúsculas sem acento (busca e ordenação)."""
    text = unicodedata.normalize('NFKD', str(text)).encode('ascii', 'ignore').decode()
    return text.casefold()


def slug(text):
    return re.sub(r"[^a-z0-9]+", "-", fold(text)).strip("-") or "item"


def display_name(text):
    """Nome legível: `_` vira espaço, espaços repetidos somem, capitalização original."""
    return re.sub(r"\s+", " ", str(text).replace("_", " ")).strip()


def size_mm(px, default=DEFAULT_SIZE_MM, full=FULL_SHEET_PX):
    """[largura, altura] em mm pela regra RN-04 (uma casa decimal)."""
    width, height = float(px[0]), float(px[1])
    lo, hi = full
    if lo <= width <= hi and lo <= height <= hi:
        return [round(width, 1), round(height, 1)]
    biggest = max(width, height) or 1.0
    return [round(width * default / biggest, 1), round(height * default / biggest, 1)]


def _is_image(name):
    return name.lower().endswith(IMAGE_EXT)


def _skipped(parts):
    return any(part.startswith(".") or part.casefold() == "bumps" for part in parts)


def build_catalog(files, sizes, meta=None, generated_at=""):
    """(catálogo, avisos). `files`: caminhos relativos a `fabrica/`; `sizes`: caminho → (largura, altura) em px das
    imagens legíveis; `meta`: caminho → (sha256, bytes)."""
    meta = meta or {}
    present = set(files)
    warnings = []
    tree = {}                                   # fabricante → coleção → [itens]
    for path in sorted(set(files), key=fold):
        parts = path.replace("\\", "/").split("/")
        if len(parts) < 2 or not _is_image(parts[-1]) or _skipped(parts):
            continue
        manufacturer = MANUFACTURERS.get(parts[0].casefold())
        if manufacturer is None:
            continue
        if path not in sizes:
            warnings.append(tr("Imagem ilegível ignorada: {}").format(path))
            continue
        stem = parts[-1].rsplit(".", 1)[0]
        collection = display_name(parts[1]) if len(parts) > 2 else GENERAL
        name = display_name(stem)
        if len(parts) > 3:
            name = "{} ({})".format(name, " / ".join(display_name(p) for p in parts[2:-1]))
        sub = "-".join(slug(p) for p in parts[2:-1])
        bump = path + ".bump" if path + ".bump" in present else None
        sha, size = meta.get(path, (None, None))
        tree.setdefault(manufacturer, {}).setdefault(collection, []).append(dict(
            stem=(sub + "-" if sub else "") + slug(stem), name=name, file=path, ext=parts[-1].rsplit(".", 1)[1].lower(),
            px=[int(sizes[path][0]), int(sizes[path][1])], bump=bump, sha256=sha, bytes=size))
    manufacturers = []
    for manufacturer in sorted(tree, key=fold):
        man_id = slug(manufacturer)
        collections = []
        for collection in sorted(tree[manufacturer], key=fold):
            col_id = slug(collection)
            items, used = [], set()
            for raw in sorted(tree[manufacturer][collection], key=lambda i: (fold(i["name"]), i["file"])):
                base = f"{man_id}/{col_id}/{raw['stem']}"
                item_id, n = base, 1
                while item_id in used:
                    n += 1
                    item_id = f"{base}-{n}"
                if n > 1:
                    warnings.append(tr("Textura com o mesmo nome na coleção, renomeada: {}").format(item_id))
                used.add(item_id)
                items.append({"id": item_id, "name": raw["name"], "file": raw["file"], "ext": raw["ext"],
                              "thumb": f"thumbs/{item_id}.png", "px": raw["px"], "size-mm": size_mm(raw["px"]),
                              "sha256": raw["sha256"], "bytes": raw["bytes"], "bump": raw["bump"]})
            collections.append({"id": col_id, "name": collection, "items": items})
        manufacturers.append({"id": man_id, "name": manufacturer, "collections": collections})
    catalog = {"schema-version": SCHEMA_VERSION, "catalog-version": CATALOG_VERSION, "generated-at": generated_at,
               "default-size-mm": DEFAULT_SIZE_MM, "full-sheet-px": list(FULL_SHEET_PX),
               "manufacturers": manufacturers}
    return catalog, warnings


def empty_catalog():
    return {"schema-version": SCHEMA_VERSION, "catalog-version": 0, "manufacturers": []}


def parse_catalog(text):
    """(catálogo, avisos). Inválido ou de outra versão vira catálogo vazio com o aviso `INVALID`."""
    try:
        data = json.loads(text)
    except (ValueError, TypeError):
        return empty_catalog(), [INVALID]
    if not isinstance(data, dict) or data.get("schema-version") != SCHEMA_VERSION \
            or not isinstance(data.get("manufacturers"), list):
        return empty_catalog(), [INVALID]
    for manufacturer in data["manufacturers"]:
        if not isinstance(manufacturer, dict) or not isinstance(manufacturer.get("collections"), list) or \
                not all(isinstance(c, dict) and isinstance(c.get("items"), list) for c in manufacturer["collections"]):
            return empty_catalog(), [INVALID]
    return data, []


def iter_items(catalog, manufacturer="", collection=""):
    for man in catalog.get("manufacturers", []):
        if manufacturer and man["id"] != manufacturer:
            continue
        for col in man["collections"]:
            if collection and col["id"] != collection:
                continue
            yield from col["items"]


def search(catalog, text, manufacturer="", collection=""):
    """Itens cujo nome (ou fabricante e coleção) contém todos os termos da busca, sem caixa e sem acento."""
    terms = fold(text).split()
    found = []
    for man in catalog.get("manufacturers", []):
        if manufacturer and man["id"] != manufacturer:
            continue
        for col in man["collections"]:
            if collection and col["id"] != collection:
                continue
            for item in col["items"]:
                haystack = fold(" ".join((item["name"], man["name"], col["name"])))
                if all(term in haystack for term in terms):
                    found.append(item)
    return found
