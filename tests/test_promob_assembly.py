"""Testes da montagem no `.dimensionExport` (feature 012, T009; D-27; interfaces/promob-dimensionexport.md)."""

import tempfile
import unittest
from pathlib import Path

import _bootstrap  # noqa: F401
from caffmob_draw.standards import io_promob

FIXTURE = _bootstrap.FIXTURES / "dimensionexport_me_moveis.xml"


class AssemblyTest(unittest.TestCase):
    def test_arquivo_do_promob_le_lateral(self):
        data = io_promob.to_definition_data(io_promob.read_dimensionexport(FIXTURE))
        self.assertEqual(data['assembly'], 'LATERAL')
        self.assertEqual(len(data['raw_attributes']), 692)
        self.assertIsNone(data['report']['assembly_warning'])

    def roundtrip(self, assembly):
        data = io_promob.to_definition_data(io_promob.read_dimensionexport(FIXTURE))
        path = Path(tempfile.mkdtemp()) / "saida.dimensionExport"
        io_promob.write_dimensionexport(path, data['name'], data['values'], data['raw_attributes'], assembly=assembly)
        return path, io_promob.read_dimensionexport(path)

    def test_exportar_acrescenta_so_a_montagem(self):
        _path, doc = self.roundtrip('BASE')
        self.assertEqual(len(doc.attributes), 693)
        self.assertEqual(doc.attributes[-1], ('CAFF_MONTAGEM', 'BASE'))
        original = io_promob.read_dimensionexport(FIXTURE).attributes
        self.assertEqual(doc.attributes[:-1], original)
        again = io_promob.to_definition_data(doc)
        self.assertEqual(again['assembly'], 'BASE')
        self.assertEqual(len(again['raw_attributes']), 692)          # CAFF_MONTAGEM fora dos crus

    def test_valor_desconhecido(self):
        doc = io_promob.read_dimensionexport(FIXTURE)
        doc.attributes.append(('CAFF_MONTAGEM', 'Diagonal'))
        data = io_promob.to_definition_data(doc)
        self.assertEqual(data['assembly'], 'LATERAL')
        self.assertIn('Diagonal', data['report']['assembly_warning'])
        doc.attributes[-1] = ('CAFF_MONTAGEM', 'base')
        self.assertEqual(io_promob.to_definition_data(doc)['assembly'], 'BASE')


if __name__ == "__main__":
    unittest.main()
