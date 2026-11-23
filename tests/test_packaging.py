"""Testes do empacotamento (BUG-20261006-SCVF): só o pacote `caffmob_draw/` é uma extensão do Blender.

- Reprodução: nenhum `blender_manifest.toml` fora de `caffmob_draw/` (a raiz do repositório não pode parecer uma
  extensão com o mesmo id).
- Regressão: o manifesto do pacote existe e tem o id da extensão; o zip gerado pelo `build.py` leva o manifesto na raiz
  do arquivo (instalável por Edit › Preferences › Get Extensions › Install from Disk).
- BUG-20261006-KFAR: os .blend do pacote estão no git, e o build recusa um pacote sem os .blend que o código usa.
"""

import os
import pathlib
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
import zipfile

ROOT = pathlib.Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "caffmob_draw"
IGNORED_DIRS = {".git", ".kilo", ".claude", ".agents", "docs", "_reversa_sdd", "_reversa_forward", "_reversa_bugs",
                "node_modules", "__pycache__"}


def manifests():
    found = []
    for dirpath, dirnames, filenames in os.walk(ROOT):
        dirnames[:] = [d for d in dirnames if d not in IGNORED_DIRS]
        if "blender_manifest.toml" in filenames:
            found.append(pathlib.Path(dirpath, "blender_manifest.toml"))
    return found


class EmpacotamentoTest(unittest.TestCase):
    def test_raiz_nao_e_extensao(self):
        """Reprodução: o único manifesto de extensão do repositório é o do pacote."""
        outside = [str(p.relative_to(ROOT)) for p in manifests() if PACKAGE not in p.parents]
        self.assertEqual(outside, [], "manifesto de extensão fora de caffmob_draw/ (a raiz parece instalável)")

    def test_manifesto_do_pacote(self):
        """Regressão: o pacote continua com manifesto válido."""
        text = (PACKAGE / "blender_manifest.toml").read_text()
        data = dict(re.findall(r'^(\w+)\s*=\s*"([^"]*)"', text, re.M))
        self.assertEqual(data["id"], "caffmob_draw")
        self.assertEqual(data["type"], "add-on")
        self.assertTrue(data["blender_version_min"].startswith("5."))

    def test_zip_tem_manifesto_na_raiz(self):
        """Regressão: o build.py gera um zip com o manifesto na raiz do arquivo."""
        with tempfile.TemporaryDirectory() as tmp:
            shutil.copytree(PACKAGE, os.path.join(tmp, "caffmob_draw"))   # cópia: link exige permissão no Windows
            shutil.copy(ROOT / "build.py", tmp)
            subprocess.run([sys.executable, "build.py"], cwd=tmp, check=True, capture_output=True)
            with zipfile.ZipFile(os.path.join(tmp, "caffmob_draw.zip")) as zf:
                names = zf.namelist()
            self.assertIn("blender_manifest.toml", names)
            self.assertIn("__init__.py", names)
            self.assertFalse(any("__pycache__" in n for n in names))
            # BUG-20261123-RW3G: dotfiles e caches de ferramenta não vão no pacote
            self.assertEqual([n for n in names if any(p.startswith(".") for p in n.split("/"))], [])
            self.assertEqual([n for n in names if n.endswith((".pyc", ".pyo"))], [])

    def test_entradas_excluidas_do_pacote(self):
        """Reprodução (BUG-20261123-RW3G): o filtro do zip barra dotfile, dot-dir, cache e o catalog/ da raiz."""
        sys.path.insert(0, str(ROOT))
        import build
        for nome in (".impeccable", ".git", ".env", "__pycache__", "x.pyc", "x.pyo"):
            self.assertTrue(build.entrada_excluida(nome, ""), nome)
            self.assertTrue(build.entrada_excluida(nome, "product_libraries/common"), nome)
        self.assertTrue(build.entrada_excluida("catalog", ""))
        self.assertFalse(build.entrada_excluida("catalog", "product_libraries"))   # só o da raiz sai
        for nome in ("__init__.py", "blender_manifest.toml", "assets", "wheels", "GeoNodeWall.blend"):
            self.assertFalse(build.entrada_excluida(nome, ""), nome)
            self.assertFalse(build.entrada_excluida(nome, "geometry_nodes"), nome)

    def test_blends_do_pacote_estao_no_git(self):
        """Reprodução (BUG-20261006-KFAR): todo .blend do pacote está no git; um clone do GitHub gera o plugin completo."""
        on_disk = sorted(str(p.relative_to(ROOT)).replace(os.sep, "/") for p in PACKAGE.rglob("*.blend"))
        self.assertTrue(on_disk, "o pacote deveria ter arquivos .blend (geometry_nodes etc.)")
        tracked = set(subprocess.run(["git", "ls-files", "caffmob_draw"], cwd=ROOT, capture_output=True, text=True,
                                     check=True).stdout.split("\n"))
        missing = [p for p in on_disk if p not in tracked]
        self.assertEqual(missing, [], f"{len(missing)} .blend do pacote fora do git (o clone gera um plugin quebrado)")

    def test_build_recusa_pacote_sem_blend(self):
        """Regressão (BUG-20261006-KFAR): sem um .blend que o código usa, o build.py falha e diz qual falta."""
        with tempfile.TemporaryDirectory() as tmp:
            shutil.copytree(PACKAGE, os.path.join(tmp, "caffmob_draw"), ignore=shutil.ignore_patterns("__pycache__"))
            shutil.copy(ROOT / "build.py", tmp)
            os.remove(os.path.join(tmp, "caffmob_draw", "geometry_nodes", "GeoNodeWall.blend"))
            result = subprocess.run([sys.executable, "build.py"], cwd=tmp, capture_output=True, text=True)
            self.assertNotEqual(result.returncode, 0, "o build não pode gerar pacote sem GeoNodeWall.blend")
            self.assertIn("GeoNodeWall.blend", result.stdout + result.stderr)
            self.assertFalse(os.path.exists(os.path.join(tmp, "caffmob_draw.zip")))


if __name__ == "__main__":
    unittest.main()
