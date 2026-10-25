"""Ambiente comum dos testes de fumaça da feature 003 no Blender (sem a extensão instalada).

- `extension_path_user` cai numa pasta temporária quando o pacote não é uma extensão instalada;
- preferências do add-on (cores) com valores neutros, como nos testes da 002;
- interface em pt_BR (as mensagens conferidas pelos smokes estão em português).
"""

import os
import sys
import tempfile
from pathlib import Path

import bpy

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
USER_DIR = os.environ.get("CAFFMOB_TEST_USER_DIR") or tempfile.mkdtemp(prefix="caffmob_user_")   # 009: compartilhada com um 2º Blender
_original = bpy.utils.extension_path_user


def _extension_path_user(package, path="", create=False):
    try:
        return _original(package, path=path, create=create)
    except ValueError:
        folder = os.path.join(USER_DIR, path)
        if create:
            os.makedirs(folder, exist_ok=True)
        return folder


bpy.utils.extension_path_user = _extension_path_user


def _install_wheels():
    """Feature 009: o Blender instala as wheels do manifesto ao instalar a extensão; aqui, sem instalar, as da
    plataforma são descompactadas numa pasta temporária no `sys.path` (o `openskp` e as dependências dele)."""
    import platform
    import zipfile
    machine = platform.machine().lower()
    marks = {'linux': ('manylinux',), 'win32': ('win_amd64',), 'darwin': ('macosx',)}.get(sys.platform, ())
    arch = 'arm64' if machine in ('arm64', 'aarch64') and sys.platform == 'darwin' else (
        'aarch64' if machine in ('arm64', 'aarch64') else ('x86_64' if sys.platform != 'win32' else 'amd64'))
    import hashlib
    import shutil
    wheels = [w for w in sorted((ROOT / "caffmob_draw" / "wheels").glob("*.whl"))
              if w.name.endswith("-none-any.whl") or (any(m in w.name for m in marks) and arch in w.name)]
    # (067) Uma pasta por conjunto de wheels, reaproveitada entre os ensaios: uma pasta nova a cada ensaio (9,7 MB)
    # encheu o disco da máquina, porque os ensaios com janela saem por `os._exit` e nada era apagado.
    key = hashlib.sha256("|".join(f"{w.name}:{w.stat().st_size}" for w in wheels).encode()).hexdigest()[:12]
    target = os.path.join(tempfile.gettempdir(), f"caffmob_wheels_cache_{key}")
    if not os.path.isdir(target):
        staging = tempfile.mkdtemp(prefix="caffmob_wheels_")
        for wheel in wheels:
            with zipfile.ZipFile(wheel) as archive:
                archive.extractall(staging)
        try:
            os.rename(staging, target)
        except OSError:                  # outro Blender chegou antes
            shutil.rmtree(staging, ignore_errors=True)
    sys.path.insert(0, target)


_install_wheels()

# Os smokes conferem comportamento com as mensagens em português; o Blender de fábrica abre em inglês e, com a
# tradução da interface (BUG-20261007-FLZO), as mensagens seguiriam o inglês. O idioma é testado à parte
# (`blender_bug_FLZO_i18n.py`, que troca a língua por conta própria).
bpy.context.preferences.view.language = 'pt_BR'
bpy.context.preferences.view.use_translate_new_dataname = False   # "Cube" continua "Cube"

import caffmob_draw as addon  # noqa: E402

addon.register()
addon.load_file_post(None)


class _Prefs:
    def __getattr__(self, _name):
        return (0.5, 0.5, 0.5, 1.0)


type(bpy.context.window_manager.home_builder).get_user_preferences = lambda self, c: _Prefs()


def clean_scene():
    for obj in list(bpy.context.scene.objects):
        bpy.data.objects.remove(obj, do_unlink=True)


def settle(times=3):
    for _ in range(times):
        bpy.context.view_layer.update()
