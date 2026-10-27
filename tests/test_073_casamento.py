"""073 (T009; RN-04, RN-05, D-10, D-12; clarify Q4): o material do Promob vira textura PBR pelo nome.

- a primeira parte do nome que é palavra de uma textura escolhe o grupo;
- a variação vence quando o nome tem a parte que só ela tem no slug (granito *preto*, laminado *nogueira*);
- sem a variação, a cor do nome aproxima pelo tom (`granito verde ubatuba` → granito escuro), marcada como
  aproximada; sem cor, a `padrao` do grupo;
- chapa de fabricante e código sem palavra conhecida não casam aqui.
"""
import unittest

import _pbr_sintetico as ps
from caffmob_draw.texture_library import pbr_core


def casar(nome):
    t, aproximada = pbr_core.casar(nome, ps.manifesto())
    return (t['slug'] if t else None), aproximada


class CasamentoTest(unittest.TestCase):
    def test_exatos(self):
        self.assertEqual(casar('par_tijolos_tijolos 003'), ('tijolo-aparente', False))
        self.assertEqual(casar('granito_preto_ouro preto'), ('granito-preto', False))
        self.assertEqual(casar('Laminado Nogueira'), ('laminado-nogueira', False))
        self.assertEqual(casar('piso_travertino_romano'), ('travertino', False))
        self.assertEqual(casar('inox escovado'), ('inox-escovado', False))
        self.assertEqual(casar('dec_met_lis_cro'), ('inox-escovado', False))
        self.assertEqual(casar('Cobre'), ('cobre', False))

    def test_aproximados_pelo_tom(self):
        self.assertEqual(casar('granito verde ubatuba'), ('granito-preto', True))
        self.assertEqual(casar('granito branco itaunas'), ('granito-bege', True))
        self.assertEqual(casar('laminado imbuia'), ('laminado-nogueira', True))
        self.assertEqual(casar('tijolinho branco tijolo'), ('tijolo-aparente-claro', True))

    def test_padrao_sem_cor(self):
        self.assertEqual(casar('granito_sao_gabriel'), ('granito-cinza', False))

    def test_sem_casamento(self):
        for nome in ('cin_cor_000', 'dur_des_hor_nogueira_caiena', '', 'vidro_fume'):
            with self.subTest(nome):
                self.assertEqual(casar(nome), (None, False))

    def test_acento(self):
        self.assertEqual(casar('Granito Cinza Corumbá'), ('granito-cinza', False))


if __name__ == '__main__':
    unittest.main()
