"""017 (T005; RN-04, RN-05, RN-15): o contrato do spec em milímetros, o encontro das chapas e o fundo.

Fixado antes do núcleo (Fase 2 antes da Fase 3): este arquivo define o contrato que `armario_v2/spec.py`
precisa cumprir em T012. Enquanto o módulo não existir, a suíte inteira fica em skip declarado.
"""
import importlib
import unittest

import _bootstrap  # noqa: F401


def _modulo(nome):
    """Módulo do núcleo da Fase 3, ou `None` enquanto a ação que o cria não rodou."""
    completo = f'caffmob_draw.armario_v2.{nome}'
    try:
        return importlib.import_module(completo)
    except ModuleNotFoundError as erro:
        if erro.name == completo:
            return None
        raise


spec = _modulo('spec')
PENDENTE = 'caffmob_draw/armario_v2/spec.py ainda não existe (T012)'


def _spec(**campos):
    """Armário de 1000 × 2000 × 560 mm com as quatro chapas da caixa presentes."""
    base = dict(largura=1000.0, altura=2000.0, profundidade=560.0,
                lateral_esq_ativa=True, lateral_dir_ativa=True,
                base_inf_ativa=True, base_sup_ativa=True)
    base.update(campos)
    return spec.Spec(**base)


@unittest.skipIf(spec is None, PENDENTE)
class SpecTest(unittest.TestCase):
    def test_faixas_das_medidas(self):
        self.assertEqual(spec.RANGES['largura'], (100.0, 6000.0))
        self.assertEqual(spec.RANGES['altura'], (100.0, 3000.0))
        self.assertEqual(spec.RANGES['profundidade'], (100.0, 1200.0))
        self.assertEqual(spec.RANGES['porta_folhas'], (1, 4))
        self.assertEqual(spec.RANGES['deslizante_folhas'], (2, 4))
        self.assertEqual(spec.RANGES['deslizante_sobreposicao'], (10.0, 60.0))
        self.assertEqual(spec.RANGES['trilho_profundidade'], (30.0, 120.0))
        self.assertEqual(spec.RANGES['fundo_recuo'], (0.0, 40.0))
        self.assertEqual(spec.validate(spec.Spec()), [])
        self.assertTrue(spec.validate(spec.Spec(largura=50.0)))
        self.assertTrue(spec.validate(spec.Spec(altura=4000.0)))
        self.assertTrue(spec.validate(spec.Spec(profundidade=50.0)))
        self.assertTrue(spec.validate(spec.Spec(porta_folhas=5)))
        self.assertTrue(spec.validate(spec.Spec(deslizante_folhas=5)))
        self.assertTrue(spec.validate(spec.Spec(deslizante_sobreposicao=70.0)))
        self.assertTrue(spec.validate(spec.Spec(trilho_profundidade=20.0)))
        self.assertTrue(spec.validate(spec.Spec(fundo_recuo=50.0)))

    def test_todas_as_medidas_do_delta(self):
        """As nove espessuras do armário (§2) e as oito medidas com faixa do `data-delta.md`.

        O `actions.md` fala em "dezesseis medidas"; o delta lista dezessete (9 + 8). O delta é a verdade.
        """
        self.assertEqual(len(spec.THICKNESS_FIELDS), 9)
        self.assertEqual(len(spec.RANGES), 8)
        for campo in spec.THICKNESS_FIELDS:
            self.assertIn(campo, spec.Spec.__dataclass_fields__)

    def test_encontro_das_chapas_em_lateral_passante(self):
        s = _spec()
        self.assertEqual(spec.carcass_lengths(s),
                         {'LEFT': 2000.0, 'RIGHT': 2000.0, 'BOTTOM': 970.0, 'TOP': 970.0})
        self.assertEqual(spec.lateral_offset_z(s), 0.0)

    def test_encontro_das_chapas_em_base_passante(self):
        s = _spec(tipo_montagem='BASE_PASSANTE')
        self.assertEqual(spec.carcass_lengths(s),
                         {'LEFT': 1970.0, 'RIGHT': 1970.0, 'BOTTOM': 1000.0, 'TOP': 1000.0})
        self.assertEqual(spec.lateral_offset_z(s), 15.0)

    def test_orientacao_troca_altura_por_profundidade(self):
        em_pe = _spec()
        self.assertEqual(spec.contra_frente(em_pe), {'comprimento': 970.0, 'altura': 2000.0})
        self.assertEqual(spec.peca_de_tras(em_pe), {'comprimento': 970.0, 'altura': 2000.0})
        deitada = _spec(orientacao_frente='DEITADA', orientacao_tras='DEITADA')
        self.assertEqual(spec.contra_frente(deitada), {'comprimento': 970.0, 'altura': 560.0})
        self.assertEqual(spec.peca_de_tras(deitada), {'comprimento': 970.0, 'altura': 560.0})

    def test_espessuras_aceitas_e_padroes(self):
        self.assertEqual(spec.THICKNESSES, (6, 15, 18, 25))
        padrao = spec.Spec()
        self.assertEqual(padrao.espessura_fundo, 6.0)
        for campo in spec.THICKNESS_FIELDS:
            if campo != 'espessura_fundo':
                self.assertEqual(getattr(padrao, campo), 15.0, campo)
        self.assertTrue(spec.thickness_ok(18.0))
        self.assertFalse(spec.thickness_ok(12.0))
        self.assertTrue(spec.validate(spec.Spec(espessura_lateral=12.0)))

    def test_fundo_encaixado_e_sobreposto(self):
        canal = _spec(fundo_ativo=True, fundo_fixacao='CANAL', fundo_recuo=10.0)
        self.assertEqual(spec.fundo(canal), {'comprimento': 970.0, 'largura': 1970.0, 'recuo': 10.0})
        self.assertEqual(spec.profundidade_util(canal), 554.0)      # 560 − 6: o recuo não consome o vão
        sobreposto = _spec(fundo_ativo=True, fundo_fixacao='SOBREPOSTO', fundo_recuo=10.0)
        self.assertEqual(spec.fundo(sobreposto), {'comprimento': 1000.0, 'largura': 2000.0, 'recuo': 10.0})
        self.assertEqual(spec.profundidade_util(sobreposto), 544.0)  # 560 − 10 − 6


if __name__ == '__main__':
    unittest.main()
