"""Mapa de partes do conta-gotas (T005; RN-11, RF-10), sem `bpy`.

Porta, Exterior e Interior são os domínios de acabamento da 067: `FRONTS`, `EXTERNAL` e `INTERNAL`, sem criar um
segundo vocabulário. Fita (`EDGE`), cota e peça sem papel ficam fora de qualquer parte, e o mesmo alvo não é
aplicado duas vezes.
"""

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import _bootstrap  # noqa: E402,F401  (carrega o pacote sem `bpy`)
from caffmob_draw.customize import finish_core as fc  # noqa: E402
from caffmob_draw.texture_library import uv_core  # noqa: E402


class TestPartesParaDominios(unittest.TestCase):
    def test_cada_parte_vira_o_dominio_da_067(self):
        self.assertEqual(uv_core.partes_para_dominios("PORTA"), (fc.FRONTS,))
        self.assertEqual(uv_core.partes_para_dominios("EXTERIOR"), (fc.EXTERNAL,))
        self.assertEqual(uv_core.partes_para_dominios("INTERIOR"), (fc.INTERNAL,))

    def test_varias_partes_sem_repetir(self):
        self.assertEqual(uv_core.partes_para_dominios(["INTERIOR", "PORTA", "PORTA"]), (fc.FRONTS, fc.INTERNAL))

    def test_fita_e_cota_ficam_fora(self):
        for marca in ("FITA", "COTA", "EDGE", "", None):
            self.assertEqual(uv_core.partes_para_dominios(marca), ())
        self.assertEqual(uv_core.partes_para_dominios(("FITA", "COTA")), ())


class TestDominiosDoAlvo(unittest.TestCase):
    def test_porta_e_exterior_e_interior(self):
        self.assertEqual(uv_core.dominios_do_alvo("PORTA", fc.PIECE_FRONT), (fc.EXTERNAL, fc.FRONTS))
        self.assertEqual(uv_core.dominios_do_alvo("LATERAL", fc.PIECE_EXTERNAL), (fc.EXTERNAL,))
        self.assertEqual(uv_core.dominios_do_alvo("PRATELEIRA", fc.PIECE_INTERNAL), (fc.INTERNAL,))

    def test_peca_sem_papel_nao_entra_em_nenhuma_parte(self):
        self.assertEqual(uv_core.dominios_do_alvo("", fc.PIECE_UNKNOWN), ())
        self.assertEqual(uv_core.dominios_do_alvo("  ", fc.PIECE_EXTERNAL), ())
        self.assertEqual(uv_core.dominios_do_alvo("LATERAL", fc.PIECE_UNKNOWN), ())

    def test_fita_fica_fora_de_qualquer_parte(self):
        self.assertEqual(uv_core.dominios_do_alvo("PORTA", fc.PIECE_FRONT, excluido=True), ())


class TestParteDoAlvo(unittest.TestCase):
    """A parte que o destaque do conta-gotas mostra (T019)."""

    def test_porta_vence_o_exterior(self):
        self.assertEqual(uv_core.parte_do_alvo("PORTA", fc.PIECE_FRONT), uv_core.PORTA)

    def test_peca_aparente_e_peca_interna(self):
        self.assertEqual(uv_core.parte_do_alvo("LATERAL", fc.PIECE_EXTERNAL), uv_core.EXTERIOR)
        self.assertEqual(uv_core.parte_do_alvo("PRATELEIRA", fc.PIECE_INTERNAL), uv_core.INTERIOR)

    def test_parte_de_dominios_escolhe_a_mais_especifica(self):
        self.assertEqual(uv_core.parte_de_dominios((fc.EXTERNAL, fc.FRONTS)), uv_core.PORTA)
        self.assertEqual(uv_core.parte_de_dominios((fc.INTERNAL,)), uv_core.INTERIOR)
        self.assertEqual(uv_core.parte_de_dominios(()), "")
        self.assertEqual(uv_core.parte_de_dominios((fc.EDGE,)), "")

    def test_sem_parte_nao_desenha_destaque(self):
        self.assertEqual(uv_core.parte_do_alvo("", fc.PIECE_UNKNOWN), "")
        self.assertEqual(uv_core.parte_do_alvo("LATERAL", fc.PIECE_UNKNOWN), "")
        self.assertEqual(uv_core.parte_do_alvo("PORTA", fc.PIECE_FRONT, excluido=True), "")


class TestAlvosUnicos(unittest.TestCase):
    def test_alvo_repetido_nao_aplica_duas_vezes(self):
        self.assertEqual(uv_core.alvos_unicos(["Porta", "Lateral", "Porta", "", "Lateral"]),
                         ["Porta", "Lateral"])

    def test_sem_alvos(self):
        self.assertEqual(uv_core.alvos_unicos(None), [])
        self.assertEqual(uv_core.alvos_unicos([]), [])


if __name__ == "__main__":
    unittest.main()
