"""Plano de assar a escala e faixas físicas (feature 080, T004; CA-02, CA-04)."""

import math
import unittest
from pathlib import Path

import _bootstrap  # noqa: F401
from caffmob_draw.target import module_geometry as mg

PARAMS = (0.8, 0.55, 0.7)
GENERAL = (0.01, 10.0)
BTM_WIDTH = (0.1, 3.0)


class BakePlanTest(unittest.TestCase):
    def test_650_to_800(self):
        plan = mg.bake_plan(PARAMS, (0.8125, 1, 1), (0.8125, 1, 1), {'width': 0.8})
        self.assertAlmostEqual(plan.params[0], 0.8)
        self.assertEqual(plan.scale, (1.0, 1.0, 1.0))
        self.assertTrue(plan.changed)

    def test_sign_kept(self):
        plan = mg.bake_plan(PARAMS, (-0.75, 1, -1), (0.75, 1, 1), {'width': 0.9})
        self.assertEqual(plan.scale, (-1.0, 1.0, -1.0))
        self.assertAlmostEqual(plan.params[0], 0.9)

    def test_other_axes_keep_physical(self):
        plan = mg.bake_plan(PARAMS, (0.8125, 1.2, 0.5), (0.8125, 1.2, 0.5), {'width': 0.8})
        self.assertAlmostEqual(plan.params[1], 0.55 * 1.2)
        self.assertAlmostEqual(plan.params[2], 0.35)
        self.assertAlmostEqual(plan.physical[1], 0.66)
        self.assertAlmostEqual(plan.physical[2], 0.35)

    def test_parent_scale_compensated(self):
        # Pai com escala 2 em X; raiz sem escala própria: 1000 mm físicos = parâmetro 500 mm.
        plan = mg.bake_plan(PARAMS, (1, 1, 1), (2, 1, 1), {'width': 1.0})
        self.assertAlmostEqual(plan.params[0], 0.5)
        self.assertEqual(plan.scale, (1.0, 1.0, 1.0))
        self.assertAlmostEqual(plan.physical[0], 1.0)

    def test_parent_and_own(self):
        plan = mg.bake_plan(PARAMS, (0.5, 1, 1), (1.0, 1, 1), {})     # pai 2 × própria 0,5 = mundo 1
        self.assertAlmostEqual(plan.params[0], 0.4)                    # 800 mm físicos ÷ ancestral 2
        self.assertAlmostEqual(plan.physical[0], 0.8)

    def test_repeat_is_noop(self):
        plan = mg.bake_plan(PARAMS, (1, 1, 1), (1, 1, 1), {'width': 0.8})
        self.assertFalse(plan.changed)
        self.assertEqual(plan.params, PARAMS)

    def test_bake_without_edit_changes(self):
        plan = mg.bake_plan(PARAMS, (0.8125, 1, 1), (0.8125, 1, 1), {})
        self.assertTrue(plan.changed)
        self.assertAlmostEqual(plan.params[0], 0.65)

    def test_unknown_field(self):
        with self.assertRaises(mg.ModuleGeometryError):
            mg.bake_plan(PARAMS, (1, 1, 1), (1, 1, 1), {'length': 1.0})


class RangeTest(unittest.TestCase):
    def test_generator_range_converted(self):
        self.assertEqual(mg.physical_range(GENERAL, BTM_WIDTH, 2.0), (0.2, 6.0))
        self.assertEqual(mg.physical_range(GENERAL, BTM_WIDTH, 1.0), (0.1, 3.0))

    def test_general_limits_win(self):
        self.assertEqual(mg.physical_range(GENERAL, BTM_WIDTH, 5.0), (0.5, 10.0))

    def test_without_generator_range(self):
        self.assertEqual(mg.physical_range(GENERAL, None, 2.0), GENERAL)

    def test_btm_3500_refused_with_range(self):
        with self.assertRaises(mg.PhysicalRangeError) as caught:
            mg.check_value('width', 3.5, GENERAL, BTM_WIDTH, 1.0)
        self.assertEqual((caught.exception.low, caught.exception.high), (0.1, 3.0))
        self.assertEqual(caught.exception.field, 'width')

    def test_boundaries_accepted(self):
        self.assertEqual(mg.check_value('width', 3.0, GENERAL, BTM_WIDTH, 1.0), 3.0)
        self.assertEqual(mg.check_value('width', 0.1, GENERAL, BTM_WIDTH, 1.0), 0.1)

    def test_invalid_values(self):
        for bad in (0, -0.01, math.nan, math.inf, -math.inf, "abc", None):
            with self.assertRaises(mg.ModuleGeometryError, msg=repr(bad)):
                mg.check_value('width', bad, GENERAL, BTM_WIDTH, 1.0)


class MasterRangeEntryTest(unittest.TestCase):
    """A2 (D-15, clarify de 2026-11-27): a faixa de ENTRADA é só a do master (RN-SELECTION-11).

    O `hard_min/hard_max` do gerador deixa de estreitar a entrada e fica só no diagnóstico da recusa; quem barra o
    valor que o gerador não representa é a pós-condição (D-07), nunca um corte silencioso.
    """

    GENERAL_DEPTH = (0.005, 10.0)

    def test_master_range_without_narrowing(self):
        for ancestor in (0.5, 1.0, 2.0, 5.0):
            self.assertEqual(mg.physical_range(GENERAL, None, ancestor), GENERAL)
            self.assertEqual(mg.physical_range(self.GENERAL_DEPTH, None, ancestor), self.GENERAL_DEPTH)

    def test_values_outside_generator_range_are_accepted_at_entry(self):
        # 3,5 m e 0,05 m estão dentro do master e fora do BTM (0,1–3,0 m): a entrada aceita.
        self.assertEqual(mg.check_value('width', 3.5, GENERAL, None, 1.0), 3.5)
        self.assertEqual(mg.check_value('width', 0.05, GENERAL, None, 1.0), 0.05)
        self.assertEqual(mg.check_value('depth', 0.05, self.GENERAL_DEPTH, None, 1.0), 0.05)

    def test_master_range_still_refuses(self):
        for field, general, bad in (('width', GENERAL, 0.005), ('width', GENERAL, 10.5),
                                    ('depth', self.GENERAL_DEPTH, 0.004), ('depth', self.GENERAL_DEPTH, 10.5)):
            with self.assertRaises(mg.PhysicalRangeError, msg=f"{field}={bad}") as caught:
                mg.check_value(field, bad, general, None, 1.0)
            self.assertEqual((caught.exception.low, caught.exception.high), general)

    def test_generator_range_remains_available_for_diagnosis(self):
        self.assertEqual(mg.physical_range(GENERAL, BTM_WIDTH, 1.0), BTM_WIDTH)

    def test_transaction_entry_uses_master_range_only(self):
        # Guarda de regressão no ponto real (module_resize importa bpy, então a conferência é estática):
        # `physical_ranges` e `_validate` não podem voltar a passar a faixa do gerador como limite de entrada.
        import ast
        source = (Path(__file__).resolve().parents[1] / 'caffmob_draw' / 'selection' / 'module_resize.py').read_text(
            encoding='utf-8')
        tree = ast.parse(source)
        for name, position in (('physical_ranges', 1), ('_validate', 3)):
            function = next(n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef) and n.name == name)
            calls = [n for n in ast.walk(function) if isinstance(n, ast.Call)
                     and isinstance(n.func, ast.Attribute) and n.func.attr in ('physical_range', 'check_value')]
            self.assertTrue(calls, name)
            for call in calls:
                argument = call.args[position]
                self.assertIsInstance(argument, ast.Constant, f"{name}: faixa de entrada não é constante")
                self.assertIsNone(argument.value, f"{name}: a faixa do gerador voltou a limitar a entrada")


if __name__ == '__main__':
    unittest.main()
