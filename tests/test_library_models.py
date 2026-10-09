"""Testes do catálogo de modelos prontos CAFFMob (feature 012, T047; D-16, RN-15)."""

import json
import unittest

import _bootstrap  # noqa: F401
from caffmob_draw.library_panel import models_core as mc


class ModelsTest(unittest.TestCase):
    def test_catalogo_do_pacote(self):
        models, warnings = mc.load_default()
        self.assertEqual(warnings, [])
        self.assertEqual([m.id for m in models], ['balcao_1p', 'balcao_2p', 'aereo_1p', 'aereo_2p', 'torre'])
        self.assertEqual({m.cabinet_type for m in models}, {'BASE', 'WALL', 'TALL'})

    def test_itens_invalidos(self):
        text = json.dumps({"models": [
            {"id": "ok", "label": "Ok", "cabinet_type": "BASE", "width_mm": 0, "door_swing": "LEFT", "shelves": 1},
            {"id": "tipo", "label": "Tipo", "cabinet_type": "ILHA", "door_swing": "LEFT"},
            {"id": "porta", "label": "Porta", "cabinet_type": "BASE", "door_swing": "GAVETA"},
            {"label": "Sem id", "cabinet_type": "BASE"},
        ]})
        models, warnings = mc.parse(text)
        self.assertEqual([m.id for m in models], ["ok"])
        self.assertEqual(models[0].width_mm, 0)
        self.assertEqual(len(warnings), 3)
        self.assertEqual(mc.parse("nada")[0], [])


if __name__ == "__main__":
    unittest.main()
