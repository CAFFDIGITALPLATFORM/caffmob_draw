"""Testes do casamento de portas e janelas na importação de `.promob` sintético (`promob/para_v2.py`, feature 078, T009)."""

import unittest

import _promob_sintetico as ps
from caffmob_draw.caffmob.v2.validacao import validar_documento
from caffmob_draw.promob import leitor, para_v2

FURA = '<HOLE PRICK="Y" DEPTH="150" />'


def converter_itens(hospedados):
    parede = ps._parede([(0, 0, 150), (12000, 0, 150)], 2700, hospedados)
    principal = ps._ambiente([parede], nome='Aberturas Promob 078')
    return para_v2.converter(leitor.abrir(ps.zip_de(ps.entradas(principal=principal))).projeto(0), catalogo=[])


class PromobAberturas078Test(unittest.TestCase):
    def test_casamento_de_portas_giro_correr_e_blindex(self):
        itens = [
            ps._item('MODULO', 'p1', base=(400, 150, 0), dim=(800, 2100, 150),
                     nome='Porta Giro Lisa Freijó', camada='Decore-Aberturas', material='madeira_freijo', extra=FURA),
            ps._item('MODULO', 'p2', base=(1600, 150, 0), dim=(1600, 2100, 150),
                     nome='Porta de Correr 2 Folhas Alumínio', camada='Decore-Aberturas', material='alu_preto', extra=FURA),
            ps._item('MODULO', 'p3', base=(3600, 150, 0), dim=(2400, 2100, 150),
                     nome='Porta de Correr 4 Folhas Blindex', camada='Decore-Aberturas', material='vidro_incolor', extra=FURA),
            ps._item('MODULO', 'p4', base=(6400, 150, 0), dim=(1400, 2100, 150),
                     nome='Porta Dupla de Giro', camada='Decore-Aberturas', material='mogno', extra=FURA),
        ]
        r = converter_itens(itens)
        self.assertEqual(r['erros'], [])
        self.assertEqual(validar_documento(r['documento']), [])
        aberturas = sorted(r['documento']['aberturas'], key=lambda a: a['posicao'])
        self.assertEqual(
            [(a['tipo'], a['modelo'], a['material']) for a in aberturas],
            [
                ('DOOR', 'porta_giro_lisa', 'madeira'),
                ('DOOR', 'porta_correr_2f', 'aluminio'),
                ('DOOR', 'porta_correr_4f', 'blindex'),
                ('DOOR', 'porta_giro_dupla', 'madeira'),
            ],
        )

    def test_casamento_de_janelas_correr_veneziana_maximar_e_fixa(self):
        itens = [
            ps._item('MODULO', 'j1', base=(400, 150, 1000), dim=(1200, 1200, 150),
                     nome='Janela de Correr Veneziana Alumínio', camada='Decore-Aberturas', material='alu_branco', extra=FURA),
            ps._item('MODULO', 'j2', base=(2000, 150, 1500), dim=(800, 600, 150),
                     nome='Janela Maxim-Ar 2 Módulos', camada='Decore-Aberturas', material='aluminio', extra=FURA),
            ps._item('MODULO', 'j3', base=(3200, 150, 900), dim=(1200, 1200, 150),
                     nome='Janela de Abrir 2 Folhas Madeira', camada='Decore-Aberturas', material='madeira', extra=FURA),
            ps._item('MODULO', 'j4', base=(4800, 150, 900), dim=(1500, 1200, 150),
                     nome='Janela Quadro Fixo Blindex', camada='Decore-Aberturas', material='vidro_temperado', extra=FURA),
        ]
        r = converter_itens(itens)
        self.assertEqual(r['erros'], [])
        self.assertEqual(validar_documento(r['documento']), [])
        aberturas = sorted(r['documento']['aberturas'], key=lambda a: a['posicao'])
        self.assertEqual(
            [(a['tipo'], a['modelo'], a['material']) for a in aberturas],
            [
                ('WINDOW', 'janela_correr_veneziana', 'aluminio'),
                ('WINDOW', 'janela_maximar_2m', 'aluminio'),
                ('WINDOW', 'janela_abrir_2f', 'madeira'),
                ('WINDOW', 'janela_fixa', 'blindex'),
            ],
        )


if __name__ == '__main__':
    unittest.main()
