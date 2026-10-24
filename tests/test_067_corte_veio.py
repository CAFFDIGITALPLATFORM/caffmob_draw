"""Veio da peça no plano de corte (feature 067, T017; RF-010, D-13, interfaces/plano-de-corte.md).

`part_sources` lê `btm_part.grain` por `part_roles.part_grain` e o passa a `PartRecord.grain`; daqui em diante o
caminho até o CSV e o JSON é o de sempre (`record_to_part` copia `grain` para `grain_direction`).
"""

import types
import unittest

import _bootstrap  # noqa: F401
from caffmob_draw.cutting import csv_exporter, json_exporter, part_roles
from caffmob_draw.cutting.nesting import NestingPart


def _obj(grain=None):
    obj = types.SimpleNamespace()
    if grain is not None:
        obj.btm_part = types.SimpleNamespace(grain=grain)
    return obj


def _part(uid, grain_direction):
    return NestingPart(id=uid, uid=uid, name=uid, width=400, height=800, thickness=18, quantity=1, material="MDF",
                       grain_direction=grain_direction, module_ref="", component="LAT", edges=[0, 0, 0, 0])


class GrainTest(unittest.TestCase):
    def test_leitura_da_peca(self):
        self.assertEqual(part_roles.part_grain(_obj('V')), 'VERTICAL')
        self.assertEqual(part_roles.part_grain(_obj('H')), 'HORIZONTAL')
        self.assertEqual(part_roles.part_grain(_obj('NONE')), 'NONE')
        self.assertEqual(part_roles.part_grain(_obj()), 'NONE')          # arquivo antigo, sem btm_part

    def test_csv_e_json_so_na_peca_marcada(self):
        marked = _part("HB/LAT/0", part_roles.part_grain(_obj('V')))
        free = _part("G1/PLACA/0", part_roles.part_grain(_obj('NONE')))
        old = _part("G2/PLACA/0", part_roles.part_grain(_obj()))
        rows = {r["id"]: r["veio"] for r in csv_exporter.part_rows([marked, free, old])}
        self.assertEqual(rows, {"HB/LAT/0": "COMPRIMENTO", "G1/PLACA/0": "NENHUM", "G2/PLACA/0": "NENHUM"})
        grains = {p.uid: json_exporter._part_entry(p, 1)["grain"] for p in (marked, free, old)}
        self.assertEqual(grains, {"HB/LAT/0": "LENGTH", "G1/PLACA/0": "NONE", "G2/PLACA/0": "NONE"})

    def test_exportar_duas_vezes_da_o_mesmo_texto(self):
        parts = [_part("A", 'VERTICAL'), _part("B", 'NONE')]
        self.assertEqual(csv_exporter.parts_csv_text(parts), csv_exporter.parts_csv_text(parts))


if __name__ == '__main__':
    unittest.main()
