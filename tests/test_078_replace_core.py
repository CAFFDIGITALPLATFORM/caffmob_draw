"""Testes puros de `replace_core.py` para "Substituir pelo selecionado" (feature 078, T011; D-11, D-13, RF-10 a RF-12)."""

import unittest

import _bootstrap  # noqa: F401
from caffmob_draw.library_panel import models_core as mc
from caffmob_draw.library_panel import replace_core as rc


class ReplaceCore078Test(unittest.TestCase):
    def test_compatibilidade_estrita_de_familia(self):
        door_target = rc.SelectionTarget(family='DOOR', width_mm=820, height_mm=2100, sill_mm=0, wall_thickness_mm=150)
        win_target = rc.SelectionTarget(family='WINDOW', width_mm=1500, height_mm=1100, sill_mm=950, wall_thickness_mm=150)
        mod_target = rc.SelectionTarget(family='MODULE', width_mm=750, height_mm=720, depth_mm=550, line='COZ')

        door_model = mc.find_any("porta_correr_2f")
        win_model = mc.find_any("janela_maximar_2m")
        mod_model = mc.find_any("gaveteiro_4g")

        self.assertTrue(rc.can_replace(door_target, door_model))
        self.assertFalse(rc.can_replace(door_target, win_model))
        self.assertFalse(rc.can_replace(door_target, mod_model))

        self.assertTrue(rc.can_replace(win_target, win_model))
        self.assertFalse(rc.can_replace(win_target, door_model))
        self.assertFalse(rc.can_replace(win_target, mod_model))

        self.assertTrue(rc.can_replace(mod_target, mod_model))
        self.assertFalse(rc.can_replace(mod_target, door_model))
        self.assertFalse(rc.can_replace(mod_target, win_model))

    def test_recusas_selecao_vazia_multipla_ou_fora_de_limites(self):
        door_model = mc.find_any("porta_giro_lisa")
        ok, msg = rc.validate_replacement([], door_model)
        self.assertFalse(ok)
        self.assertIn("Selecione", msg)

        t1 = rc.SelectionTarget(family='DOOR', width_mm=800, height_mm=2100)
        ok, msg = rc.validate_replacement([t1, t1], door_model)
        self.assertFalse(ok)
        self.assertIn("apenas um", msg)

        wall_target = rc.SelectionTarget(family='WALL', width_mm=3000, height_mm=2700)
        ok, msg = rc.validate_replacement([wall_target], door_model)
        self.assertFalse(ok)
        self.assertIn("não é uma porta", msg)

        tiny_door = rc.SelectionTarget(family='DOOR', width_mm=100, height_mm=2100)
        ok, msg = rc.validate_replacement([tiny_door], door_model)
        self.assertFalse(ok)
        self.assertIn("limites", msg)

    def test_substituicao_abertura_preserva_medidas_e_aplica_material(self):
        target = rc.SelectionTarget(family='DOOR', width_mm=920, height_mm=2150, sill_mm=0, wall_thickness_mm=180)
        cand = mc.find_any("porta_correr_4f")
        plan = rc.plan_replacement(target, cand, active_material="aluminio")
        self.assertEqual(plan.family, 'DOOR')
        self.assertEqual(plan.opening_model, "porta_correr_4f")
        self.assertEqual(plan.opening_material, "aluminio")
        self.assertEqual(plan.width_mm, 920.0)
        self.assertEqual(plan.height_mm, 2150.0)
        self.assertEqual(plan.wall_thickness_mm, 180.0)

    def test_regra_do_braco_principal_em_armarios_de_canto(self):
        # Reto -> Canto em L: width e depth vão para o braço principal; segundo braço usa o padrão da linha
        straight = rc.SelectionTarget(
            family='MODULE', width_mm=850, height_mm=720, depth_mm=580,
            right_width_mm=0, corner_kind='NONE', line='COZ'
        )
        canto_l = mc.find_any("canto_l_balcao")
        plan_l = rc.plan_replacement(straight, canto_l, standard_width_mm=800.0)
        self.assertEqual(plan_l.corner_kind, 'L')
        self.assertEqual(plan_l.width_mm, 850.0)
        self.assertEqual(plan_l.depth_mm, 580.0)
        self.assertEqual(plan_l.right_width_mm, 800.0)

        # Canto em L -> Canto Oblíquo: preserva tanto o braço principal quanto o segundo braço
        corner_target = rc.SelectionTarget(
            family='MODULE', width_mm=950, height_mm=720, depth_mm=580,
            right_width_mm=1050, corner_kind='L', line='COZ'
        )
        canto_ob = mc.find_any("canto_obliquo_balcao")
        plan_ob = rc.plan_replacement(corner_target, canto_ob, standard_width_mm=800.0)
        self.assertEqual(plan_ob.corner_kind, 'OBLIQUE')
        self.assertEqual(plan_ob.width_mm, 950.0)
        self.assertEqual(plan_ob.right_width_mm, 1050.0)

        # Canto -> Gaveteiro reto: preserva width, height e depth do braço principal e zera right_width_mm
        gav = mc.find_any("gaveteiro_3g")
        plan_straight = rc.plan_replacement(corner_target, gav, standard_width_mm=800.0)
        self.assertEqual(plan_straight.corner_kind, 'NONE')
        self.assertEqual(plan_straight.drawers, 3)
        self.assertEqual(plan_straight.width_mm, 950.0)
        self.assertEqual(plan_straight.depth_mm, 580.0)
        self.assertEqual(plan_straight.right_width_mm, 0.0)


if __name__ == "__main__":
    unittest.main()
