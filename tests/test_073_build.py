"""073 (T010; RN-03, D-06): o empacotamento aceita só textura PBR CC0 registrada no manifesto.

- pasta `pbr/` válida (manifesto, arquivos, sha256, licença CC0 no pacote) passa;
- arquivo sem registro, licença errada, sha256 divergente, arquivo listado ausente ou sem `LICENSES/CC0-1.0.txt`
  reprovam;
- o pacote real passa, e a regra da 014 (`texture_problems`) continua recusando imagem de fabricante.
"""
import json
import os
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

import _pbr_sintetico as ps

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import build  # noqa: E402


class PbrPackageTest(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.dir)
        shutil.copytree(ROOT / 'caffmob_draw' / 'texture_library', os.path.join(self.dir, 'texture_library'),
                        ignore=shutil.ignore_patterns('__pycache__'))
        os.makedirs(os.path.join(self.dir, 'LICENSES'))
        Path(self.dir, 'LICENSES', 'CC0-1.0.txt').write_text('CC0 1.0 Universal')
        self.pbr = os.path.join(self.dir, 'pbr')
        os.makedirs(self.pbr)
        self.dados = ps.gravar(self.pbr)

    def problems(self):
        return build.pbr_problems(self.dir)

    def test_valido(self):
        self.assertEqual(self.problems(), [])

    def test_sem_pasta_nao_cobra(self):
        shutil.rmtree(self.pbr)
        self.assertEqual(self.problems(), [])

    def test_arquivo_sem_registro(self):
        Path(self.pbr, 'tijolo-aparente', 'altura.jpg').write_bytes(ps.JPEG)
        self.assertTrue(any('altura.jpg' in p for p in self.problems()))

    def test_licenca_errada(self):
        self.dados['texturas'][0]['origem']['licenca'] = 'CC-BY-4.0'
        Path(self.pbr, 'manifest.json').write_text(json.dumps(self.dados))
        self.assertTrue(any('CC0-1.0' in p for p in self.problems()))

    def test_sha256_divergente(self):
        Path(self.pbr, 'cobre', 'cor.jpg').write_bytes(ps.JPEG + b'x')
        self.assertTrue(any('sha256' in p for p in self.problems()))

    def test_arquivo_listado_ausente(self):
        os.remove(os.path.join(self.pbr, 'cobre', 'metalico.jpg'))
        self.assertTrue(any('falta o arquivo cobre/metalico.jpg' in p for p in self.problems()))

    def test_sem_licenca_no_pacote(self):
        os.remove(os.path.join(self.dir, 'LICENSES', 'CC0-1.0.txt'))
        self.assertTrue(any('LICENSES/CC0-1.0.txt' in p for p in self.problems()))

    def test_pacote_real(self):
        package = str(ROOT / 'caffmob_draw')
        self.assertEqual(build.pbr_problems(package), [])
        self.assertEqual(build.texture_problems(package), [])

    def test_fabricante_continua_recusado(self):
        with tempfile.TemporaryDirectory() as d:
            shutil.copytree(ROOT / 'caffmob_draw' / 'textures', os.path.join(d, 'textures'))
            Path(d, 'textures', 'duratex_inteira.jpg').write_bytes(ps.JPEG)
            self.assertTrue(any('duratex_inteira.jpg' in p for p in build.texture_problems(d)))


if __name__ == '__main__':
    unittest.main()
