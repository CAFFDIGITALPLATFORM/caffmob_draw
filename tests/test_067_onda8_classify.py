"""Onda 8 da 067 (T182; RF-164, RF-166, RN-17, D-41): parede e abertura do CAFF MOBI reconhecidas."""
import unittest

import _bootstrap  # noqa: F401
from caffmob_draw.selection import classify as c
from caffmob_draw.selection import component


class Obj(dict):
    def __init__(self, name, parent=None, type='MESH', **props):
        super().__init__(props)
        self.name = name
        self.parent = parent
        self.type = type


parede = Obj('Parede 0680', caffmob_tipo='parede', caffmob_id='p1')
portao = Obj('Abertura 0680', type='EMPTY', caffmob_tipo='abertura', caffmob_id='a1',
             caffmob_entidade_v2='{"id":"a1","tipo":"DOOR"}')
janela = Obj('Abertura 0681', type='EMPTY', caffmob_tipo='abertura', caffmob_id='a2',
             caffmob_entidade_v2='{"id":"a2","tipo":"WINDOW"}')
vidro = Obj('Vidro', janela, caffmob_tipo='abertura_peca', caffmob_id='a2')
folha = Obj('Folha 1', portao, caffmob_tipo='abertura_peca', caffmob_id='a1')
macaneta = Obj('Maçaneta', folha, caffmob_tipo='abertura_peca', caffmob_id='a1')
modulo_mobi = Obj('Balcão', caffmob_tipo='modulo', caffmob_id='m1')


class ClassifyMobiTest(unittest.TestCase):
    def check(self, obj, kind, root):
        info = c.classify(obj)
        self.assertEqual((info.kind, info.root.name, info.library), (kind, root, 'MOBI'))

    def test_abertura_e_pecas(self):
        # A porta do MOBI é Porta também para quem lê o `classify` (aviso de tamanho na viewport, Mover Sobre).
        self.check(portao, c.ROOM_DOOR, portao.name)
        self.check(folha, c.ROOM_DOOR, portao.name)
        self.check(macaneta, c.ROOM_DOOR, portao.name)
        self.check(janela, c.WINDOW, janela.name)
        self.check(vidro, c.WINDOW, janela.name)

    def test_parede(self):
        self.check(parede, c.WALL, parede.name)

    def test_rotulo_da_biblioteca(self):
        self.assertIn('MOBI', c.LIBRARY_LABELS)

    def test_nao_se_movem(self):
        for obj in (parede, portao, folha):
            self.assertIsNone(c.movable_root(obj))
            self.assertIn('Parede', c.move_over_denial(obj))

    def test_peca_sobe_ate_a_raiz_da_abertura(self):
        self.assertTrue(component.is_opening_root(portao))
        self.assertFalse(component.is_opening_root(folha))
        self.assertIs(component.component_root(folha), portao)
        self.assertIs(component.component_root(macaneta), portao)

    def test_outros_tipos_do_mobi_seguem_como_antes(self):
        self.assertNotEqual(c.classify(modulo_mobi).library, 'MOBI')


if __name__ == '__main__':
    unittest.main()
