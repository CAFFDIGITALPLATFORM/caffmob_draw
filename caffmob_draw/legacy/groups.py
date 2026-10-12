"""Converter os grupos salvos das bibliotecas herdadas (feature 012, T067; D-29, D-30, RN-16).

Os grupos de "Meus módulos" do frameless e do face frame são `.blend` na pasta `cabinet_groups/` da biblioteca do
usuário (as duas bibliotecas usam a mesma pasta). Cada grupo pendente é carregado numa coleção temporária da cena,
seus armários são convertidos (`legacy/convert.py`) e cada módulo CAFFMob resultante é salvo na categoria "Geral"
(`customize/library_io.save`, com miniatura). Um grupo com vários armários vira um módulo por armário ("Nome 1",
"Nome 2"…), porque a biblioteca do usuário guarda um módulo por arquivo. Tudo o que foi carregado ou criado sai no
fim; o `.blend` original fica (RN-14). O marcador `legacy_groups.json` guarda a oferta e os convertidos.
"""

import os
import tempfile

import bpy  # type: ignore

from ..data.i18n import tr
from . import gate, groups_core

TARGET_CATEGORY = "Geral"
MARKER_FILE = "legacy_groups.json"
_DATA_KINDS = ('objects', 'meshes', 'materials', 'node_groups', 'images', 'curves', 'collections', 'textures',
               'lights', 'cameras', 'actions')
_offer_cache = [None]


def invalidate():
    _offer_cache[0] = None


def group_items():
    """[(nome, caminho)] dos grupos salvos nas bibliotecas herdadas."""
    from ..product_libraries.frameless.operators import ops_library
    try:
        return [(item['name'], item['filepath']) for item in ops_library.get_user_library_items()]
    except OSError:
        return []


def _marker_path():
    from ..customize import library_io
    return os.path.join(library_io.modules_root(), MARKER_FILE)


def read_marker():
    try:
        with open(_marker_path(), encoding='utf-8') as handle:
            return groups_core.parse_marker(handle.read())
    except OSError:
        return {}


def write_marker(marker):
    path = _marker_path()
    fd, tmp = tempfile.mkstemp(dir=os.path.dirname(path), suffix=".tmp")
    try:
        with os.fdopen(fd, 'w', encoding='utf-8') as handle:
            handle.write(groups_core.dump_marker(marker))
        os.replace(tmp, path)
    except Exception:
        if os.path.exists(tmp):             # o marcador antigo continua valendo; o temporário não fica (EC-09)
            os.remove(tmp)
        raise
    invalidate()


def pending_files():
    return groups_core.pending([path for _name, path in group_items()], read_marker())


def should_offer():
    """Oferecer "Converter grupos antigos" no painel? Em cache até `invalidate()` (o painel desenha a cada quadro)."""
    if _offer_cache[0] is None:
        _offer_cache[0] = (not gate.legacy_ui()
                           and groups_core.should_offer([path for _name, path in group_items()], read_marker()))
    return _offer_cache[0]


def _snapshot():
    return {kind: set(getattr(bpy.data, kind)) for kind in _DATA_KINDS}


def _cleanup(before, keep=()):
    """Remove o que foi carregado ou criado depois de `before` (objetos primeiro), menos `keep`."""
    keep = set(keep)
    for kind in _DATA_KINDS:
        collection = getattr(bpy.data, kind)
        for block in [b for b in collection if b not in before[kind] and b not in keep]:
            try:
                collection.remove(block)
            except (ReferenceError, RuntimeError):
                pass


def _existing_names():
    from ..customize import library_io
    return {entry["name"].casefold() for entry in library_io.list_modules() if entry["category"] == TARGET_CATEGORY}


def convert_group(context, name, filepath):
    """Converte um grupo salvo. Devolve (nomes dos módulos salvos, linhas do relatório, erro ou None)."""
    from ..customize import library_io
    from . import convert
    before = _snapshot()
    scene = context.scene
    holder = bpy.data.collections.new("CAFFMob conversão")
    scene.collection.children.link(holder)
    saved, lines, error = [], [], None
    try:
        with bpy.data.libraries.load(filepath, link=False) as (data_from, data_to):
            data_to.objects = list(data_from.objects)
        for obj in data_to.objects:
            if obj is not None:
                holder.objects.link(obj)
        context.view_layer.update()
        roots = [obj for obj in holder.objects if gate.is_legacy(obj) and obj in gate.legacy_roots(scene)]
        results = convert.convert_scene(context, roots)
        lines = [tr("Grupo {}").format(name)] + ["  " + line for line in convert.report_lines(results)]
        modules = [bpy.data.objects[r.module_name] for r in results if r.module_name in bpy.data.objects]
        existing = _existing_names()
        for index, module in enumerate(modules, start=1):
            base = name if len(modules) == 1 else f"{name} {index}"
            target = groups_core.target_name(base, existing)
            existing.add(target.casefold())
            paths, errors = library_io.save(context, module, target, TARGET_CATEGORY)
            if errors:
                lines += ["  " + e for e in errors]
            else:
                saved.append(target)
        if not results:
            lines.append("  " + tr("nenhum armário de biblioteca antiga no grupo"))
    except (OSError, RuntimeError) as exc:
        error = tr("Não foi possível abrir o grupo {}: {}").format(name, exc)
    finally:
        _cleanup(before, keep=(holder,))
        bpy.data.collections.remove(holder)
    return saved, lines, error


def convert_pending(context):
    """Converte todos os grupos pendentes e grava o marcador. Devolve (salvos, linhas)."""
    marker = read_marker()
    pending = set(groups_core.pending([path for _name, path in group_items()], marker))
    saved, lines, done = [], [], []
    for name, path in group_items():
        if path not in pending:
            continue
        names, group_lines, error = convert_group(context, name, path)
        saved += names
        lines += group_lines
        if error:
            lines.append(error)
        else:
            done.append(path)
    write_marker(groups_core.mark(marker, done))
    return saved, lines


def dismiss():
    write_marker(groups_core.mark(read_marker(), []))
