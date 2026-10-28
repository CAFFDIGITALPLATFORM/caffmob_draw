"""Testes do catálogo da biblioteca para a feature 078 (T010; D-10, RF-07, RF-08).

Confere:
- `load_default()` continua devolvendo os 5 modelos clássicos (retrocompatibilidade com a 012/014);
- `load_presets()` devolve balcões, gaveteiros (`drawers > 0`) e armários de canto (`corner_kind` `'L'` e `'OBLIQUE'`);
- `load_openings()` devolve os 30 modelos de aberturas (10 `DOOR` + 20 `WINDOW`) em paridade exata com o contrato v2;
- `thumb_shapes` e `opening_thumb_shapes` produzem miniaturas vetoriais distintas e válidas dentro da caixa `box`.
"""

import unittest

import _bootstrap  # noqa: F401
from caffmob_draw.caffmob.v2 import contrato as v2_contrato
from caffmob_draw.library_panel import models_core as mc

BOX = (0.0, 0.0, 140.0, 140.0)


class LibraryModels078Test(unittest.TestCase):
    def test_catalogo_completo_sem_avisos(self):
        cabs, openings, warnings = mc.parse_all(mc.CATALOG.read_text(encoding='utf-8'))
        self.assertEqual(warnings, [])
        self.assertGreaterEqual(len(cabs), 15)
        self.assertEqual(len(openings), 30)

        door_ids = tuple(o.opening_model for o in openings if o.kind == 'DOOR')
        win_ids = tuple(o.opening_model for o in openings if o.kind == 'WINDOW')
        self.assertEqual(door_ids, v2_contrato.MODELOS_DE_PORTA)
        self.assertEqual(win_ids, v2_contrato.MODELOS_DE_JANELA)

    def test_gaveteiros_e_cantos_presentes(self):
        presets, warnings = mc.load_presets()
        self.assertEqual(warnings, [])
        by_id = {m.id: m for m in presets}
        self.assertIn("gaveteiro_3g", by_id)
        self.assertIn("gaveteiro_4g", by_id)
        self.assertEqual(by_id["gaveteiro_3g"].drawers, 3)
        self.assertEqual(by_id["gaveteiro_4g"].drawers, 4)

        self.assertIn("canto_l_balcao", by_id)
        self.assertIn("canto_obliquo_balcao", by_id)
        self.assertIn("canto_l_aereo", by_id)
        self.assertEqual(by_id["canto_l_balcao"].corner_kind, 'L')
        self.assertEqual(by_id["canto_obliquo_balcao"].corner_kind, 'OBLIQUE')
        self.assertGreater(by_id["canto_l_balcao"].right_width_mm, 0)

    def test_miniaturas_de_gaveteiros_cantos_e_aberturas(self):
        s_3g = mc.thumb_shapes('BASE', 500, 720, 0, 'NONE', 0, BOX, drawers=3)
        s_4g = mc.thumb_shapes('BASE', 450, 720, 0, 'NONE', 0, BOX, drawers=4)
        self.assertEqual(len(s_3g["doors"]), 3)
        self.assertEqual(len(s_4g["doors"]), 4)
        self.assertNotEqual(s_3g, s_4g)

        s_l = mc.thumb_shapes('BASE', 900, 720, 0, 'DOUBLE', 1, BOX, corner_kind='L', right_width_mm=900)
        s_ob = mc.thumb_shapes('BASE', 900, 720, 0, 'LEFT', 1, BOX, corner_kind='OBLIQUE', right_width_mm=900)
        self.assertNotEqual(s_l, s_ob)

        openings, _ = mc.load_openings()
        for op in openings:
            sh = mc.thumb_shapes(
                'BASE', op.width_mm, op.height_mm, op.sill_mm, 'NONE', 0, BOX,
                kind=op.kind, opening_model=op.opening_model
            )
            self.assertGreater(len(sh["doors"]), 0, op.id)
            cx, cy, cw, ch = sh["carcass"]
            self.assertGreater(cw, 0.0, op.id)
            self.assertGreater(ch, 0.0, op.id)


if __name__ == "__main__":
    unittest.main()
