"""Testes da raiz do componente (feature 011, T004): `caffmob_draw/selection/component.py` (nota D-01)."""

import types
import unittest

import _bootstrap  # noqa: F401
from caffmob_draw.selection import component as c


class Obj(dict):
    """Objeto simulado: idprops via dict, `name`, `parent`, `children` e as marcas da camada nova."""

    def __init__(self, name, parent=None, kind=None, aggregate=None, leaf_of=None, stuck=False, group=None,
                 item=False, **props):
        super().__init__(props)
        self.name = name
        self.parent = parent
        self.children = []
        if parent is not None:
            parent.children.append(self)
        if kind:
            self.btm_plane = types.SimpleNamespace(object_kind=kind)
        self.btm_aggregate = types.SimpleNamespace(is_aggregate=bool(aggregate), kind=aggregate or 'AGGREGATE',
                                                   parent_ref=leaf_of)
        self.btm_stick = types.SimpleNamespace(is_stuck=stuck)
        self.btm_group = types.SimpleNamespace(is_group=group is not None, kind=group or 'PLAIN')
        self.btm_object_item = types.SimpleNamespace(is_item=item)

    def __repr__(self):
        return self.name


wall = Obj("Parede", IS_WALL_BP=True)
# Porta real (010): vão → FRAME → pivô → folha LEAF → maçaneta; símbolo e texto 2D no vão.
porta = Obj("Porta", wall, IS_ENTRY_DOOR_BP=True)
frame = Obj("Marco", porta, group='FRAME')
pivo = Obj("Pivô", frame)
folha = Obj("Folha", pivo, aggregate='LEAF', leaf_of=frame)
macaneta = Obj("Maçaneta", folha)
simbolo = Obj("Door Swing", porta, IS_2D_ANNOTATION=True)
janela = Obj("Janela", wall, IS_WINDOW_BP=True)
vidro = Obj("Vidro", Obj("Folha J", janela, aggregate='LEAF'))
# Armário frameless com agregado e item grudado.
balcao = Obj("Balcao", wall, IS_FRAMELESS_CABINET_CAGE=True)
frente = Obj("Left Door", balcao, IS_DOOR_FRONT=True)
puxador = Obj("Pull", frente)
agregado = Obj("Fruteira", balcao, aggregate='AGGREGATE')
peca_agregado = Obj("Fruteira peça", agregado)
grudado = Obj("Vaso", balcao, stuck=True)
cota = Obj("Dimension", balcao, IS_2D_ANNOTATION=True)
rapido = Obj("BTM_Cabinet", kind='MODULE')
rapido_porta = Obj("BTM_Cabinet_Door_L", rapido)
# Item da biblioteca e SketchUp aninhado; janela montada de OBJ, ainda sem parede.
item = Obj("Cadeira", item=True, group='PLAIN')
pe = Obj("Pé", item)
skp = Obj("Porta SKP", group='PLAIN')
skp_folha = Obj("Folha SKP", skp, group='PLAIN')
dobradica = Obj("Dobradiça", skp_folha)
esquadria = Obj("Esquadria", group='FRAME')
esquadria_folha = Obj("Folha OBJ", esquadria, aggregate='LEAF', leaf_of=esquadria)
solta = Obj("Malha solta")
piso = Obj("Piso", IS_FLOOR_BP=True)


class RootTest(unittest.TestCase):
    def test_porta_e_janela(self):
        for obj in (porta, frame, folha, macaneta, simbolo):
            self.assertIs(c.component_root(obj), porta, obj)
        self.assertIs(c.component_root(vidro), janela)

    def test_agregado_e_grudado(self):
        self.assertIs(c.component_root(agregado), agregado)
        self.assertIs(c.component_root(peca_agregado), agregado)
        self.assertIs(c.component_root(grudado), grudado)

    def test_armario_pelo_modo(self):
        self.assertIs(c.component_root(puxador), balcao)
        self.assertIs(c.component_root(puxador, {'FRAMELESS': True}), balcao)
        self.assertIs(c.component_root(puxador, {'FRAMELESS': False}), puxador)
        self.assertIs(c.component_root(frente, {'FRAMELESS': False}), frente)
        self.assertIs(c.component_root(rapido_porta, {'FRAMELESS': False}), rapido)   # módulo rápido sobe sempre

    def test_item_grupo_e_soltos(self):
        self.assertIs(c.component_root(pe), item)
        self.assertIs(c.component_root(dobradica), skp)
        self.assertIs(c.component_root(skp_folha), skp)
        self.assertIs(c.component_root(esquadria_folha), esquadria)   # folha de esquadria sobe ao marco
        self.assertIs(c.component_root(solta), solta)
        self.assertIs(c.component_root(wall), wall)
        self.assertIs(c.component_root(piso), piso)
        self.assertIs(c.component_root(cota), cota)                   # cota solta não sobe
        self.assertIsNone(c.component_root(None))

    def test_collapse(self):
        objs = [macaneta, folha, pe, dobradica, porta, solta]
        self.assertEqual(c.collapse(objs), [porta, item, skp, solta])
        self.assertEqual(c.collapse([]), [])


if __name__ == "__main__":
    unittest.main()
