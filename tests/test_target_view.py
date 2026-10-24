"""ViewModel da janela de propriedades (feature 067, T015; RF-003, RF-004).

Para cada tipo: as seções esperadas, o Essencial contido na Completa e a Completa com todo o inventário da 1.8.0
(`tests/data/067_inventario_1_8_0.json`, T004). Um campo da 1.8.0 só pode faltar se foi trocado pelo campo certo
(SUBSTITUIDOS) ou retirado por um requisito (RETIRADOS), sempre com o requisito citado.
"""

import json
import unittest
from pathlib import Path

import _bootstrap  # noqa: F401
import _target_stubs as stubs
from caffmob_draw.target import resolver as r
from caffmob_draw.target import view as v

INVENTORY = json.loads((Path(__file__).resolve().parent / "data" / "067_inventario_1_8_0.json").read_text())
SHEET = ('part', 'front', 'member', 'leaf')
# Campo da 1.8.0 -> campo que o substitui, por tipo (com o requisito).
SUBSTITUIDOS = {
    **{(t, 'BTM_PG_SelectionEdit.width'): 'BTM_PG_SelectionEdit.part_a' for t in SHEET},          # RF-006
    **{(t, 'BTM_PG_SelectionEdit.height'): 'BTM_PG_SelectionEdit.part_b' for t in SHEET},         # RF-006
    **{(t, 'BTM_PG_SelectionEdit.depth'): 'BTM_PG_SelectionEdit.part_thickness' for t in SHEET},  # RF-006
    ('geometry', 'BTM_PG_GeometryProps.width'): 'BTM_PG_SelectionEdit.part_a',                      # RF-011
    ('geometry', 'BTM_PG_GeometryProps.depth'): 'BTM_PG_SelectionEdit.part_b',                      # RF-011
    ('geometry', 'BTM_PG_GeometryProps.thickness'): 'BTM_PG_SelectionEdit.part_thickness',          # RF-011
    # Um só modelo de cotas (RF-015, RF-027 a RF-030); as antigas viram ação na Completa (RF-030, T094).
    **{(t, 'BTM_PG_SelectionEdit.inferior'): 'BTM_PG_SelectionEdit.cota_inferior'
       for t in ('btm_module', 'hb_module', 'authored') + SHEET},
    **{(t, 'BTM_PG_SelectionEdit.superior'): 'BTM_PG_SelectionEdit.cota_superior'
       for t in ('btm_module', 'hb_module', 'authored') + SHEET},
}
# Mover Sobre num tipo que não se move era botão sem executor (RF-002, RF-019, RF-020, RF-022, RF-023, RF-025).
_MOVE_OVER = ('BTM_PG_MoveOverState.enabled', 'BTM_PG_MoveOverState.show_relative', 'BTM_PG_MoveOverState.step')
RETIRADOS = {(t, p) for t in ('light', 'camera', 'annotation', 'cladding', 'room_door', 'window') for p in _MOVE_OVER}


def _props(view):
    return {f"{v.DATA_OWNERS[f.data]}.{f.prop}" for f in v.fields(view)}


def _operators(view):
    return {a.operator for a in v.actions(view)}


class ViewTest(unittest.TestCase):
    def setUp(self):
        self.s = stubs.scene()

    def target(self, name):
        return r.resolve(getattr(self.s, name))

    def test_essencial_contido_na_completa(self):
        for name in INVENTORY:
            target = self.target(name)
            essential, complete = v.build(target, v.ESSENTIAL), v.build(target, v.COMPLETE)
            with self.subTest(tipo=name):
                self.assertTrue(v.fields(essential), "Essencial sem nenhum campo")
                self.assertLessEqual(_props(essential), _props(complete))
                self.assertLessEqual(_operators(essential), _operators(complete))

    def test_completa_contem_o_inventario_da_1_8_0(self):
        for name, entry in INVENTORY.items():
            complete = v.build(self.target(name), v.COMPLETE)
            props, operators = _props(complete), _operators(complete)
            with self.subTest(tipo=name):
                self.assertEqual(sorted(set(entry['operators']) - operators), [])
                missing = []
                for prop in entry['props']:
                    if (name, prop) in RETIRADOS:
                        continue
                    wanted = SUBSTITUIDOS.get((name, prop), prop)
                    if wanted not in props:
                        missing.append(f"{prop} -> {wanted}")
                self.assertEqual(missing, [])

    def test_secoes_por_tipo(self):
        expected = {
            'btm_module': {'dimensions', 'cotas', 'position'}, 'part': {'sheet', 'cotas', 'module'},
            'member': {'sheet', 'member'}, 'geometry': {'sheet', 'material', 'geometry'},
            'front': {'sheet', 'front'}, 'leaf': {'leaf', 'sheet'}, 'wall': {'wall', 'cotas'},
            'room_door': {'opening'}, 'cladding': {'cladding'}, 'floor': {'surface', 'cotas'},
            'light': {'light', 'cotas'}, 'camera': {'camera', 'cotas'}, 'annotation': {'position'},
            'free': {'position', 'cotas'},
        }
        for name, ids in expected.items():
            sections = {s.id for s in v.build(self.target(name), v.COMPLETE).sections}
            with self.subTest(tipo=name):
                self.assertLessEqual(ids, sections)

    def test_nenhum_campo_da_chapa_mostra_o_modulo(self):
        for name in SHEET + ('geometry',):
            props = _props(v.build(self.target(name), v.COMPLETE))
            with self.subTest(tipo=name):
                self.assertFalse({'BTM_PG_SelectionEdit.width', 'BTM_PG_SelectionEdit.height',
                                  'BTM_PG_SelectionEdit.depth'} & props)

    def test_peca_de_biblioteca_somente_leitura_com_motivo(self):
        sheet = next(s for s in v.build(self.target('part'), v.COMPLETE).sections if s.id == 'sheet')
        dims = [f for f in sheet.items if isinstance(f, v.Field) and f.prop.startswith('part_')]
        self.assertTrue(dims and all(f.read_only and f.reason for f in dims))
        self.assertIn('caffmob_draw.authored_adopt', _operators(v.build(self.target('part'), v.ESSENTIAL)))
        member = next(s for s in v.build(self.target('member'), v.COMPLETE).sections if s.id == 'sheet')
        self.assertFalse(any(f.read_only for f in member.items if isinstance(f, v.Field)))

    def test_cabecalho(self):
        header = v.build(self.target('member')).header
        self.assertEqual((header.kind_label, header.scope_label), ("Peça", "Peça"))
        self.assertEqual(header.path, ("Armário Torre", "Prateleira 2"))
        self.assertIsNotNone(header.select_owner)
        self.assertIsNone(v.build(self.target('wall')).header.select_owner)
        multiple = v.build(r.resolve(self.s.part, [self.s.part, self.s.free])).header
        self.assertEqual((multiple.scope_label, multiple.scope_args), ("{} objetos", (2,)))

    def test_estado_vazio_e_calculando(self):
        self.assertEqual(v.build(None).empty, v.EMPTY_SELECTION)
        self.assertEqual(v.build(None, calculating=True).empty, v.CALCULATING)

    def test_anotacao_sem_mover_sobre_nem_colisao(self):
        complete = v.build(self.target('annotation'), v.COMPLETE)
        self.assertFalse(any(p.startswith('BTM_PG_MoveOverState') for p in _props(complete)))
        self.assertNotIn('caffmob.check_collisions', _operators(complete))


if __name__ == '__main__':
    unittest.main()
