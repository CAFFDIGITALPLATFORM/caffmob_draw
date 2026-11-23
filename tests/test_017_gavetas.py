"""017 (T008; RN-07, RN-09, RF-09, RF-11): o bloco de gavetas, os dez modelos, o separador e os afastadores.

Contrato de `armario_v2/gavetas.py` (T016): `Gaveta` (frozen, campos do `data-delta.md` §2.2), `MODELOS`,
`FOLGA = 3.0`, `alturas(altura_bloco, quantidade)`, `bloco(altura_bloco, quantidade, modelo=..., modelos=...)` e
`chapas(gaveta, largura_caixa, profundidade_caixa, espessura)`. Medidas em milímetros.
"""
import importlib
import unittest
from dataclasses import replace

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


gavetas = _modulo('gavetas')
PENDENTE = 'caffmob_draw/armario_v2/gavetas.py ainda não existe (T016)'


@unittest.skipIf(gavetas is None, PENDENTE)
class GavetasTest(unittest.TestCase):
    def test_quatro_gavetas_em_760_mm_com_folga_de_3(self):
        alturas = gavetas.alturas(760.0, 4)
        self.assertEqual(len(alturas), 4)
        for altura in alturas:
            self.assertAlmostEqual(altura, 186.25)                   # (760 − 5 × 3) / 4
        self.assertAlmostEqual(sum(alturas) + 5 * gavetas.FOLGA, 760.0)
        self.assertEqual(gavetas.FOLGA, 3.0)

    def test_dez_modelos_de_frente(self):
        self.assertEqual(len(gavetas.MODELOS), 10)
        self.assertEqual(len([m for m in gavetas.MODELOS if m.startswith('s_cf_')]), 5)
        self.assertEqual(len([m for m in gavetas.MODELOS if m.startswith('c_cf_')]), 5)
        unico = gavetas.bloco(760.0, 4, modelo='c_cf_vidro')
        self.assertEqual([g.modelo for g in unico], ['c_cf_vidro'] * 4)
        individuais = gavetas.bloco(760.0, 4, modelos=['s_cf_reta', 'c_cf_cava', 's_cf_gola', 'c_cf_vidro'])
        self.assertEqual([g.modelo for g in individuais], ['s_cf_reta', 'c_cf_cava', 's_cf_gola', 'c_cf_vidro'])
        self.assertEqual([g.indice for g in individuais], [0, 1, 2, 3])
        with self.assertRaises(ValueError):
            gavetas.bloco(760.0, 2, modelo='x_cf_reta')

    def test_separador_por_colunas_e_linhas(self):
        gaveta = replace(gavetas.bloco(760.0, 1)[0], separador_colunas=3, separador_linhas=2)
        pecas = gavetas.chapas(gaveta, largura_caixa=904.0, profundidade_caixa=500.0, espessura=15.0)
        separadores = [p for p in pecas if p['papel'] == 'SEPARADOR']
        self.assertEqual(len(separadores), 3)                        # 2 verticais + 1 horizontal
        self.assertTrue(all(p['espessura'] == 6.0 for p in separadores))
        sem_separador = gavetas.chapas(gavetas.bloco(760.0, 1)[0], largura_caixa=904.0,
                                       profundidade_caixa=500.0, espessura=15.0)
        self.assertEqual([p for p in sem_separador if p['papel'] == 'SEPARADOR'], [])

    def test_quatro_afastadores_independentes(self):
        gaveta = gavetas.bloco(760.0, 1)[0]
        todas = [p for p in gavetas.chapas(gaveta, largura_caixa=904.0, profundidade_caixa=500.0, espessura=15.0)
                 if p['papel'] == 'AFASTADOR']
        self.assertEqual(len(todas), 4)
        self.assertEqual(sorted(p['lado'] for p in todas), ['dir', 'esq', 'frente', 'tras'])
        sem_direito = replace(gaveta, afastador_dir=False)
        restantes = [p for p in gavetas.chapas(sem_direito, largura_caixa=904.0, profundidade_caixa=500.0,
                                               espessura=15.0) if p['papel'] == 'AFASTADOR']
        self.assertEqual(len(restantes), 3)
        self.assertEqual(sorted(p['lado'] for p in restantes), ['esq', 'frente', 'tras'])


if __name__ == '__main__':
    unittest.main()
