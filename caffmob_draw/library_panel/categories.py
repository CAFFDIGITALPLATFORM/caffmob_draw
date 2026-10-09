"""Categorias do usuário em disco (feature 012, T019; D-17).

`categories.json` fica na pasta de módulos do usuário (`customize/library_io.modules_root`), ao lado das pastas de
cada categoria. Leitura tolerante (`categories_core.parse`); gravação atômica. Pastas de módulos que ainda não são
categoria entram como Cozinha (COZ) na primeira leitura.
"""

import os
import tempfile

from ..customize import library_io
from . import categories_core as cc

FILE_NAME = "categories.json"
_cache = [None]          # (categorias, avisos): o desenho do painel não lê o disco a cada quadro (princípio IX)


def invalidate():
    _cache[0] = None


def _path():
    return os.path.join(library_io.modules_root(), FILE_NAME)


def _folders(root):
    try:
        return sorted(name for name in os.listdir(root) if os.path.isdir(os.path.join(root, name)))
    except OSError:
        return []


def load():
    """(categorias do usuário, avisos), já com as pastas soltas migradas. Usa o cache até `invalidate()`."""
    if _cache[0] is not None:
        return _cache[0]
    try:
        with open(_path(), encoding='utf-8') as handle:
            text = handle.read()
    except FileNotFoundError:
        text = ""
    except OSError as exc:
        return [], [str(exc)]
    user, warnings = cc.parse(text)
    merged = cc.merge_folders(user, _folders(library_io.modules_root()))
    if merged != user and not warnings:
        save(merged)
    _cache[0] = (merged, warnings)
    return merged, warnings


def save(user):
    path = _path()
    directory = os.path.dirname(path)
    os.makedirs(directory, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=directory, suffix=".tmp")
    try:
        with os.fdopen(fd, 'w', encoding='utf-8') as handle:
            handle.write(cc.dump(user))
        os.replace(tmp, path)
        _cache[0] = (list(user), [])
    except BaseException:
        if os.path.exists(tmp):
            os.unlink(tmp)
        raise


def create(name, line):
    """Cria a categoria (e a pasta). Devolve None ou o motivo da recusa."""
    user, _warnings = load()
    reason = cc.validate_name(name, user)
    if reason:
        return reason
    clean = name.strip()
    os.makedirs(os.path.join(library_io.modules_root(), clean), exist_ok=True)
    save(user + [cc.Category(clean, line if line in cc.LINES else cc.DEFAULT_LINE, False)])
    return None


def set_line(name, line):
    user, _warnings = load()
    save(cc.with_line(user, name, line))


def all_categories():
    user, _warnings = load()
    return cc.all_categories(user)


def find(name):
    return next((c for c in all_categories() if c.name == name), None)
