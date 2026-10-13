"""Importa as texturas dos fabricantes de chapas para o catálogo do plugin (feature 014, T014; RN-01 a RN-04, D-03).

Roda no Blender em segundo plano (usa o leitor de imagens do Blender para as dimensões e as miniaturas):

    blender --background --factory-startup --python tools/texturas_importar.py -- \\
        /home/theleoinfo/Downloads/materials/textures [--limite N]

Entrada: a pasta raiz no layout da biblioteca de texturas do Promob (`<raiz>/fabrica/<Fabricante>/...`).
Saídas (interfaces/catalogo-texturas.md):
- `caffmob_draw/textures/catalog.json` e `caffmob_draw/textures/thumbs/<id>.png` (256 px): vão no git e no pacote;
- `dist/texturas-servidor/files/<id>.<ext>` + `manifest.json`: imagens em tamanho real para o servidor da CAF Mob,
  fora do git e do pacote.

Idempotente: mesmos ids, mesma ordem e mesmos sha256; imagem e miniatura iguais não são refeitas. Itens que saíram da
raiz saem do catálogo, das miniaturas e do pacote do servidor.
"""

import hashlib
import json
import os
import shutil
import sys
import time
from datetime import datetime, timezone, timedelta

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(REPO, "tests"))
import _bootstrap  # noqa: E402,F401  (importa os núcleos puros sem registrar a extensão)
from caffmob_draw.texture_library import catalog_core  # noqa: E402

PACKAGE_DIR = os.path.join(REPO, "caffmob_draw", "textures")
SERVER_DIR = os.path.join(REPO, "dist", "texturas-servidor")
THUMB_PX = 256


def _args():
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    if not argv:
        sys.exit("Uso: blender --background --python tools/texturas_importar.py -- <raiz> [--limite N]")
    limit = int(argv[argv.index("--limite") + 1]) if "--limite" in argv else 0
    return argv[0], limit


def _sha256(path):
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _list(fabrica):
    files = []
    for base, dirs, names in os.walk(fabrica):
        dirs[:] = sorted(d for d in dirs if not d.startswith("."))
        for name in sorted(names):
            files.append(os.path.relpath(os.path.join(base, name), fabrica).replace(os.sep, "/"))
    return files


def _accepted(files):
    return [f for f in files if f.split("/")[0].casefold() in catalog_core.MANUFACTURERS]


def _dimensions(bpy, path):
    """(largura, altura) pelo leitor do Blender, ou None se a imagem for ilegível."""
    try:
        image = bpy.data.images.load(path, check_existing=False)
    except RuntimeError:
        return None
    try:
        width, height = image.size[:]
        return (width, height) if width and height else None
    finally:
        bpy.data.images.remove(image)


def _thumbnail(bpy, source, dest):
    image = bpy.data.images.load(source, check_existing=False)
    try:
        width, height = image.size[:]
        factor = THUMB_PX / float(max(width, height))
        if factor < 1.0:
            image.scale(max(1, round(width * factor)), max(1, round(height * factor)))
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        image.filepath_raw, image.file_format = dest, 'PNG'
        image.save()
    finally:
        bpy.data.images.remove(image)


def _fresh(source, dest):
    return os.path.exists(dest) and os.path.getmtime(dest) >= os.path.getmtime(source)


def _prune(root, keep):
    """Apaga arquivos de `root` que não estão em `keep` (itens que saíram da raiz)."""
    if not os.path.isdir(root):
        return 0
    removed = 0
    for base, _dirs, names in os.walk(root):
        for name in names:
            path = os.path.join(base, name)
            if path not in keep:
                os.remove(path)
                removed += 1
    return removed


def main():
    import bpy  # noqa: PLC0415  (só existe dentro do Blender)
    root, limit = _args()
    fabrica = os.path.join(root, "fabrica")
    if not os.path.isdir(fabrica):
        print(f"Pasta de texturas não encontrada: {fabrica}")
        sys.exit(1)
    t0 = time.perf_counter()
    files = _list(fabrica)
    images = [f for f in _accepted(files) if f.lower().endswith(catalog_core.IMAGE_EXT)
              and "/bumps/" not in f.casefold() + "/"]
    if limit:
        images = images[:limit]
    sizes, meta = {}, {}
    for n, rel in enumerate(images, 1):
        path = os.path.join(fabrica, rel)
        dims = _dimensions(bpy, path)
        if dims is not None:
            sizes[rel] = dims
            meta[rel] = (_sha256(path), os.path.getsize(path))
        if n % 100 == 0:
            print(f"  lidas {n}/{len(images)}", flush=True)
    generated = datetime.now(timezone(timedelta(hours=-3))).isoformat(timespec="seconds")
    keep_files = set(images) | {f for f in files if f.endswith(".bump")}
    catalog, warnings = catalog_core.build_catalog([f for f in files if f in keep_files], sizes, meta=meta,
                                                   generated_at=generated)
    keep_thumbs, keep_server, manifest = set(), set(), {"version": catalog["catalog-version"], "items": {}}
    for item in catalog_core.iter_items(catalog):
        source = os.path.join(fabrica, item["file"])
        thumb = os.path.join(PACKAGE_DIR, item["thumb"])
        if not _fresh(source, thumb):
            _thumbnail(bpy, source, thumb)
        keep_thumbs.add(thumb)
        server_file = os.path.join(SERVER_DIR, "files", f"{item['id']}.{item['ext']}")
        if not (os.path.exists(server_file) and os.path.getsize(server_file) == item["bytes"]):
            os.makedirs(os.path.dirname(server_file), exist_ok=True)
            shutil.copy2(source, server_file)
        keep_server.add(server_file)
        manifest["items"][item["id"]] = {"sha256": item["sha256"], "bytes": item["bytes"],
                                         "file": os.path.relpath(server_file, SERVER_DIR).replace(os.sep, "/")}
        if item.get("bump"):                    # relevo do fabricante: item próprio no servidor (T045)
            bump_source = os.path.join(fabrica, item["bump"])
            bump_file = os.path.join(SERVER_DIR, "files", f"{item['id']}.bump.jpg")
            if not (os.path.exists(bump_file) and os.path.getsize(bump_file) == os.path.getsize(bump_source)):
                shutil.copy2(bump_source, bump_file)
            keep_server.add(bump_file)
            manifest["items"][item["id"] + ".bump"] = {
                "sha256": _sha256(bump_source), "bytes": os.path.getsize(bump_source),
                "file": os.path.relpath(bump_file, SERVER_DIR).replace(os.sep, "/")}
    removed = _prune(os.path.join(PACKAGE_DIR, "thumbs"), keep_thumbs)
    removed += _prune(os.path.join(SERVER_DIR, "files"), keep_server)
    os.makedirs(PACKAGE_DIR, exist_ok=True)
    with open(os.path.join(PACKAGE_DIR, "catalog.json"), "w", encoding="utf-8") as handle:
        json.dump(catalog, handle, ensure_ascii=False, indent=1)
        handle.write("\n")
    os.makedirs(SERVER_DIR, exist_ok=True)
    with open(os.path.join(SERVER_DIR, "manifest.json"), "w", encoding="utf-8") as handle:
        json.dump(manifest, handle, ensure_ascii=False, indent=1)
        handle.write("\n")
    total = 0
    for man in catalog["manufacturers"]:
        count = sum(len(c["items"]) for c in man["collections"])
        total += count
        print(f"{man['name']:<18} {count:>5} texturas  {len(man['collections']):>3} coleções")
    print(f"TOTAL {total} texturas de {len(catalog['manufacturers'])} fabricantes; {len(warnings)} avisos; "
          f"{removed} arquivos antigos removidos; {time.perf_counter() - t0:.0f} s")
    for warning in warnings:
        print("AVISO", warning)


if __name__ == "__main__":
    main()
