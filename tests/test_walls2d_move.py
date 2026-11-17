"""Reprodução e regressão do BUG-20261117-EELF: mover parede no editor (`model.WallPlan.move_segments`).

Run: py -3 tests/test_walls2d_move.py

O modelo é Python puro: a translação das paredes ativas é provada aqui, fora do Blender. Regra aprovada pelo titular em
2026-11-17: mover uma parede leva junto o nó compartilhado com uma parede não ativa, e a vizinha estica (muda de
comprimento e de ângulo), mantendo o encadeamento.
"""

import math
import unittest

import _bootstrap  # noqa: F401
from caffmob_draw.walls2d import model as m


class MoverParedeTest(unittest.TestCase):
    def aberta(self):
        # Cadeia aberta em L: 3,0 m na horizontal, 2,0 m na vertical, espessura padrão.
        return m.WallPlan([m.Chain([(0.0, 0.0), (3.0, 0.0), (3.0, 2.0)], [m.Segment(), m.Segment()])])

    def sala(self):
        return m.WallPlan([m.rectangle(3.6, 2.4, thickness=0.15)])

    def test_move_um_trecho_desloca_os_dois_nos(self):
        plan = self.aberta()
        chain = plan.chains[0]
        comprimento = chain.length(0)
        plan.move_segments([(0, 0)], 0.5, 0.0)
        self.assertAlmostEqual(chain.nodes[0][0], 0.5, places=9)
        self.assertAlmostEqual(chain.nodes[0][1], 0.0, places=9)
        self.assertAlmostEqual(chain.nodes[1][0], 3.5, places=9)
        self.assertAlmostEqual(chain.nodes[1][1], 0.0, places=9)
        # a parede anda; não muda de comprimento
        self.assertAlmostEqual(chain.length(0), comprimento, places=9)

    def test_vizinha_estica_com_o_no_compartilhado(self):
        plan = self.aberta()
        chain = plan.chains[0]
        angulo_antes = chain.direction(1)
        plan.move_segments([(0, 0)], 0.5, 0.0)
        # o nó compartilhado (1) andou junto: o trecho vizinho estica e muda de ângulo
        self.assertAlmostEqual(chain.length(1), math.hypot(0.5, 2.0), places=9)
        self.assertNotAlmostEqual(chain.direction(1), angulo_antes, places=3)
        self.assertAlmostEqual(chain.nodes[2][0], 3.0, places=9)      # o nó do outro lado fica
        self.assertAlmostEqual(chain.nodes[2][1], 2.0, places=9)

    def test_move_dois_trechos_juntos(self):
        plan = m.WallPlan([m.Chain([(0.0, 0.0), (3.0, 0.0), (3.0, 2.0), (0.0, 2.0)],
                                   [m.Segment() for _ in range(3)])])
        chain = plan.chains[0]
        plan.move_segments([(0, 0), (0, 1)], 0.0, 0.4)
        for k in (0, 1, 2):
            self.assertAlmostEqual(chain.nodes[k][1], (0.0, 0.0, 2.0)[k] + 0.4, places=9)
        self.assertAlmostEqual(chain.nodes[3][1], 2.0, places=9)      # o trecho 2 estica
        self.assertAlmostEqual(chain.length(0), 3.0, places=9)
        self.assertAlmostEqual(chain.length(1), 2.0, places=9)

    def test_move_nao_muda_espessura_altura_nem_tipo(self):
        plan = self.sala()
        chain = plan.chains[0]
        chain.set_segment_value(0, "wall_type", "MURETA")        # o tipo aplica o padrão dele primeiro
        chain.set_segment_value(0, "thickness", 0.2)
        chain.set_segment_value(0, "height", 2.8)
        plan.move_segments([(0, 0)], 0.1, 0.1)
        seg = chain.segments[0]
        self.assertAlmostEqual(seg.thickness, 0.2, places=9)
        self.assertAlmostEqual(seg.height, 2.8, places=9)
        self.assertEqual(seg.wall_type, "MURETA")

    def test_move_zero_nao_muda_o_rascunho(self):
        plan = self.aberta()
        antes = m.plan_signature(plan)
        plan.move_segments([(0, 1)], 0.0, 0.0)
        self.assertEqual(m.plan_signature(plan), antes)

    def test_indice_invalido_levanta(self):
        plan = self.aberta()
        with self.assertRaises(ValueError):
            plan.move_segments([(0, 9)], 0.1, 0.0)
        with self.assertRaises(ValueError):
            plan.move_segments([(7, 0)], 0.1, 0.0)


if __name__ == "__main__":
    unittest.main()
