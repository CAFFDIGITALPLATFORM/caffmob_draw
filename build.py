#!/usr/bin/env python3
import os
import re
import sys
import zipfile

# Arquivos de nós que o código carrega por nome (hb_types: GeoNodeObject.create, CabinetPartModifier.add_node).
NODE_PATTERNS = (
    (re.compile(r"create\(\s*['\"](GeoNode\w+)['\"]"), "geometry_nodes"),
    (re.compile(r"add_part_modifier\(\s*['\"](CPM_\w+)['\"]"), os.path.join("geometry_nodes", "CabinetPartModifiers")),
)


def missing_node_files(source_dir):
    """`.blend` de nós usados no código e ausentes no pacote (BUG-20261006-KFAR: pacote gerado de um clone sem eles)."""
    wanted = set()
    for root, dirs, files in os.walk(source_dir):
        dirs[:] = [d for d in dirs if d != "__pycache__"]
        for file in files:
            if file.endswith(".py"):
                with open(os.path.join(root, file), encoding="utf-8", errors="ignore") as handle:
                    text = handle.read()
                for pattern, folder in NODE_PATTERNS:
                    wanted |= {os.path.join(folder, name + ".blend") for name in pattern.findall(text)}
    return sorted(path for path in wanted if not os.path.exists(os.path.join(source_dir, path)))


def package_problems(source_dir):
    """Feature 009 (T035): wheels do manifesto presentes e biblioteca embutida completa e sem modelos do 3D
    Warehouse (a licença deles proíbe redistribuir, RN-09)."""
    import json
    problems = []
    manifest = open(os.path.join(source_dir, "blender_manifest.toml"), encoding="utf-8").read()
    for wheel in re.findall(r'"\./(wheels/[^"]+\.whl)"', manifest):
        if not os.path.isfile(os.path.join(source_dir, wheel)):
            problems.append(f"falta {wheel} (rode python3 tools/fetch_wheels.py)")
    for asset in ("nogueira_cor.jpg", "nogueira_rugosidade.jpg"):          # feature 010: textura da porta real
        if not os.path.isfile(os.path.join(source_dir, "openings", "assets", asset)):
            problems.append(f"falta openings/assets/{asset} (rode tools/build_openings_assets.py no Blender)")
    items = os.path.join(source_dir, "object_library", "items")
    if not os.path.isdir(items):
        problems.append("falta object_library/items (rode tools/build_object_library.py no Blender)")
        return problems
    for root, _dirs, files in os.walk(items):
        for file in files:
            if not file.endswith(".json"):
                continue
            path = os.path.join(root, file)
            data = json.load(open(path, encoding="utf-8"))
            if not os.path.isfile(path[:-len(".json")] + ".blend"):
                problems.append(f"falta o .blend de {os.path.relpath(path, source_dir)}")
            if str(data.get("source", "")).strip().lower().startswith("3d warehouse"):
                problems.append(f"{os.path.relpath(path, source_dir)}: modelo do 3D Warehouse não pode ir no pacote")
    return problems


def build_zip():
    zip_filename = "caffmob_draw.zip"
    source_dir = "caffmob_draw"

    if not os.path.exists(source_dir):
        print(f"Error: Source directory '{source_dir}' does not exist.")
        return

    missing = missing_node_files(source_dir)
    if missing:
        print("Error: arquivos .blend que o plugin usa estão faltando no pacote (o plugin não criaria paredes nem "
              "módulos):")
        for path in missing:
            print(f"  - {source_dir}/{path}")
        print("Atualize o repositório (git pull) ou copie os arquivos antes de empacotar.")
        sys.exit(1)

    problems = package_problems(source_dir)
    if problems:
        print("Error: o pacote não está pronto:")
        for problem in problems:
            print(f"  - {problem}")
        sys.exit(1)

    print(f"Packaging {source_dir}/ into {zip_filename}...")

    # Remove existing zip if it exists
    if os.path.exists(zip_filename):
        os.remove(zip_filename)

    with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(source_dir):
            # Skip python cache directories
            if "__pycache__" in dirs:
                dirs.remove("__pycache__")
            # `catalog/` não é registrado pela extensão (código morto; feature 005, D-16): fica fora do pacote
            if os.path.abspath(root) == os.path.abspath(source_dir) and "catalog" in dirs:
                dirs.remove("catalog")

            for file in files:
                file_path = os.path.join(root, file)
                # Keep file path relative to source directory (root of zip)
                arcname = os.path.relpath(file_path, source_dir)
                zipf.write(file_path, arcname)
                print(f"  Added: {arcname}")

    print(f"Successfully created '{zip_filename}'!")

if __name__ == "__main__":
    build_zip()
