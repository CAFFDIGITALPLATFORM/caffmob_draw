"""071 (T011; D-02, D-03, RF-13): arquivos maliciosos, vazios ou corrompidos."""
import os
import tempfile
import unittest
from unittest import mock

import _promob_sintetico as ps
from caffmob_draw.promob import leitor


class SegurancaTest(unittest.TestCase):
    def test_caminhos_invalidos_sao_recusados(self):
        mapa = ps.entradas()
        mapa['..\\..\\fora.py'] = 'print(1)'
        mapa['/absoluto.txt'] = 'x'
        mapa['C:\\Windows\\x.dll'] = 'x'
        antes = set(os.listdir(tempfile.gettempdir()))
        p = leitor.abrir(ps.zip_de(mapa))
        self.assertEqual(len(p.avisos), 3)
        self.assertFalse([n for n in p.nomes() if 'fora' in n or 'absoluto' in n or 'Windows' in n])
        p.projeto()
        self.assertEqual(set(os.listdir(tempfile.gettempdir())) - antes, set())

    def test_limites(self):
        with mock.patch.object(leitor, 'MAX_ENTRADAS', 3):
            with self.assertRaises(leitor.PromobErro):
                leitor.abrir(ps.promob())
        with mock.patch.object(leitor, 'MAX_TOTAL', 100):
            with self.assertRaisesRegex(leitor.PromobErro, 'grande demais'):
                leitor.abrir(ps.promob())

    def test_xml_com_entidades(self):
        mau = ('<?xml version="1.0"?><!DOCTYPE a [<!ENTITY x "xxxxxxxx"><!ENTITY y "&x;&x;&x;">]>'
               '<AMBIENT3D>&y;</AMBIENT3D>')
        p = leitor.abrir(ps.zip_de(ps.entradas(principal=mau)))
        with self.assertRaisesRegex(leitor.PromobErro, 'declarações'):
            p.ambientes()

    def test_sem_ambiente(self):
        mapa = {k: v for k, v in ps.entradas().items() if not k.endswith('.ambient3d')}
        with self.assertRaisesRegex(leitor.PromobErro, 'não tem ambiente 3D'):
            leitor.abrir(ps.zip_de(mapa)).ambientes()

    def test_nao_e_zip(self):
        with self.assertRaisesRegex(leitor.PromobErro, 'não é um projeto do Promob'):
            leitor.abrir(b'isto nao e um zip')

    def test_zip_corrompido(self):
        dados = bytearray(ps.promob())
        meio = len(dados) // 3
        dados[meio:meio + 200] = b'\x00' * 200
        with self.assertRaises(leitor.PromobErro):
            p = leitor.abrir(bytes(dados))
            p.ambientes()
            p.materiais()


if __name__ == '__main__':
    unittest.main()
