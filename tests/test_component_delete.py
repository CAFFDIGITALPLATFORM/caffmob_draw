"""Testes da exclusão por componente (feature 011, T003): `delete_plan` e `own_aggregates` (nota D-05)."""

import unittest

import _bootstrap  # noqa: F401
from caffmob_draw.selection import component as c
from test_component_core import agregado, balcao, esquadria, folha, macaneta, piso, porta, wall


class DeleteTest(unittest.TestCase):
    def names(self, objs):
        return [o.name for o in objs]

    def test_porta_inteira_de_baixo_para_cima(self):
        plan = c.delete_plan([porta])
        removed = self.names(plan.remove)
        self.assertEqual(set(removed), {"Porta", "Marco", "Pivô", "Folha", "Maçaneta", "Door Swing"})
        self.assertLess(removed.index("Maçaneta"), removed.index("Folha"))
        self.assertLess(removed.index("Folha"), removed.index("Marco"))
        self.assertEqual(removed[-1], "Porta")
        self.assertEqual(plan.openings, [porta])

    def test_sem_repetir(self):
        plan = c.delete_plan([porta, folha, macaneta])
        self.assertEqual(len(plan.remove), len(set(map(id, plan.remove))))
        self.assertEqual(len(plan.remove), 6)

    def test_agregados_e_grudados(self):
        com = self.names(c.delete_plan([balcao]).remove)
        self.assertIn("Fruteira peça", com)
        self.assertNotIn("Vaso", com)                       # grudado é solto no lugar, nunca apagado
        sem = self.names(c.delete_plan([balcao], keep_aggregates=True).remove)
        self.assertNotIn("Fruteira", sem)
        self.assertNotIn("Fruteira peça", sem)
        self.assertIn("Pull", sem)
        self.assertEqual(c.delete_plan([balcao]).openings, [])

    def test_parede_sai_sozinha(self):
        self.assertFalse(c.deletes_subtree(wall))
        self.assertFalse(c.deletes_subtree(piso))
        self.assertTrue(c.deletes_subtree(porta))
        self.assertEqual(self.names(c.delete_plan([wall]).remove), ["Parede"])   # porta e balcão ficam
        self.assertIn("Maçaneta", self.names(c.delete_plan([wall, porta]).remove))

    def test_agregados_proprios(self):
        self.assertEqual(c.own_aggregates(balcao), [agregado])
        self.assertEqual(c.own_aggregates(porta), [])        # folha da porta é peça da porta, sem pergunta
        self.assertEqual(c.own_aggregates(esquadria), [])


if __name__ == "__main__":
    unittest.main()
