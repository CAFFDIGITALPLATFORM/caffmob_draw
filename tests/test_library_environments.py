"""Acervo da Biblioteca por ambiente (item 2 do relatório de capacidades, 2026-11-25).

Cada modelo do catálogo declara em `environments` onde aparece (COZ, DOR, BAN, SAL, ESC); sem a chave, aparece em
todos — o que mantém catálogo antigo funcionando. A categoria da Biblioteca escolhe a linha do Padrão de Dimensões e a
grade passa a mostrar só o acervo daquele ambiente.
"""

import json
import unittest

import _bootstrap  # noqa: F401
from caffmob_draw.library_panel import categories_core as cc
from caffmob_draw.library_panel import models_core as mc


def _ids(models):
    return {model.id for model in models}


class EnvironmentsTest(unittest.TestCase):
    def test_catalogo_do_pacote_declara_ambiente(self):
        cabinets, warnings = mc.load_all_cabinets()
        self.assertEqual(warnings, [])
        self.assertTrue(all(model.environments for model in cabinets),
                        [model.id for model in cabinets if not model.environments])

    def test_cada_ambiente_tem_acervo_proprio(self):
        cabinets, _warnings = mc.load_all_cabinets()
        by_line = {line: _ids(mc.by_environment(cabinets, line)) for line in cc.LINES}
        self.assertIn("balcao_pia", by_line['COZ'])
        self.assertIn("roupeiro_2p", by_line['DOR'])
        self.assertIn("gabinete_banho", by_line['BAN'])
        self.assertIn("buffet_sala", by_line['SAL'])
        self.assertIn("armario_arquivo", by_line['ESC'])
        # Cozinha e banheiro não repetem o mesmo acervo.
        self.assertFalse(by_line['COZ'] & by_line['BAN'])
        self.assertFalse(by_line['COZ'] & by_line['DOR'])
        self.assertNotIn("balcao_pia", by_line['BAN'])
        self.assertNotIn("gabinete_banho", by_line['COZ'])

    def test_sem_ambiente_aparece_em_todos(self):
        text = json.dumps({"models": [
            {"id": "livre", "label": "Livre", "cabinet_type": "BASE", "door_swing": "LEFT"},
        ]})
        models, warnings = mc.parse(text)
        self.assertEqual(warnings, [])
        self.assertEqual(models[0].environments, ())
        for line in cc.LINES:
            self.assertEqual(_ids(mc.by_environment(models, line)), {"livre"})
        self.assertEqual(_ids(mc.by_environment(models, "")), {"livre"})

    def test_ambiente_desconhecido_e_recusado(self):
        text = json.dumps({"models": [
            {"id": "errado", "label": "Errado", "cabinet_type": "BASE", "environments": ["XYZ"]},
            {"id": "certo", "label": "Certo", "cabinet_type": "BASE", "environments": ["BAN"]},
        ]})
        models, warnings = mc.parse(text)
        self.assertEqual([model.id for model in models], ["certo"])
        self.assertEqual(len(warnings), 1)

    def test_categorias_do_documento_da_biblioteca(self):
        """Feature 026: a navegação segue o documento — Armários, Portas, Janelas, Armários autorais."""
        sidebar = [category.name for category in cc.sidebar_categories([])]
        self.assertEqual(sidebar[:4], ["Armários", "Portas", "Janelas", "Armários autorais"])
        self.assertEqual(cc.LINE_LABELS['DOR'], "Dormitório")   # o ambiente continua no card de detalhe


if __name__ == "__main__":
    unittest.main()
