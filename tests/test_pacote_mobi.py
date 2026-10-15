# (063 RN-12; D-08) Retirada do catálogo embutido sem afetar os assets de geometria.
import ast
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class Pacote(unittest.TestCase):
    def test_sem_catalogo_importador_ou_download_em_lote(self):
        self.assertFalse((ROOT / 'caffmob_draw/textures').exists())
        self.assertFalse((ROOT / 'tools/texturas_importar.py').exists())
        tree = ast.parse((ROOT / 'caffmob_draw/texture_library/ops_account.py').read_text())
        self.assertFalse(any(isinstance(n, ast.ClassDef) and 'DownloadAll' in n.name for n in ast.walk(tree)))
        self.assertFalse(any(isinstance(n, ast.FunctionDef) and n.name == 'start_download_all' for n in ast.walk(tree)))
        build = ast.parse((ROOT / 'build.py').read_text())
        self.assertFalse(any(isinstance(n, ast.Name) and n.id == 'texture_problems' for n in ast.walk(build)))
        self.assertTrue(any(isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id == 'missing_node_files' for n in ast.walk(build)))

    def test_nucleo_preservado_da_061(self):
        reference = ROOT.parent / 'referencia-061/blendertomob/caffmob'
        if not reference.exists():
            self.skipTest('referência disponível apenas na pasta de entrega')
        for name in ('__init__','contrato','geometria','derivar','prismas','validacao','chapas'):
            original = ast.dump(ast.parse((reference / (name+'.py')).read_text()))
            texto = (ROOT / 'caffmob_draw/caffmob' / (name+'.py')).read_text()
            if name == 'validacao':
                # Única mudança deliberada depois do porte: a referência do modelo com a regra do MOBI (063 T059).
                inicio = texto.index('        # Mesma regra do MOBI')
                fim = texto.index('erro(f"modulos[{m}].modelo", "ESQUEMA")\n') + len('erro(f"modulos[{m}].modelo", "ESQUEMA")\n')
                texto = texto[:inicio] + texto[fim:]
            current = ast.dump(ast.parse(texto))
            self.assertEqual(original,current,name)
