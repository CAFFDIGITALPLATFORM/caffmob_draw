"""Domínios de acabamento (feature 067, T023; RF-041, D-14, data-delta M-03)."""

import unittest

import _bootstrap  # noqa: F401
from caffmob_draw.customize import finish_core as fc


class DomainsTest(unittest.TestCase):
    def test_faces_por_dominio(self):
        self.assertEqual(fc.domains_for_faces(fc.FACE_INTERNAL), (fc.INTERNAL,))
        self.assertEqual(fc.domains_for_faces(fc.FACE_EXTERNAL), (fc.EXTERNAL,))
        self.assertEqual(fc.domains_for_faces(fc.FACE_EDGE), (fc.EDGE,))
        self.assertEqual(fc.domains_for_faces(fc.FACE_UNKNOWN), ())       # face desconhecida não é pintada

    def test_pecas_por_dominio(self):
        # Externo cobre a caixa aparente e as frentes; Frentes só as frentes; Interno não toca a frente.
        self.assertEqual(fc.domains_for_piece(fc.PIECE_FRONT), (fc.EXTERNAL, fc.FRONTS))
        self.assertEqual(fc.domains_for_piece(fc.PIECE_EXTERNAL), (fc.EXTERNAL,))
        self.assertEqual(fc.domains_for_piece(fc.PIECE_INTERNAL), (fc.INTERNAL,))
        self.assertEqual(fc.domains_for_piece(fc.PIECE_UNKNOWN), ())
        for domain in fc.DOMAINS:
            self.assertNotIn(fc.PIECE_UNKNOWN, fc.DOMAIN_PIECES[domain])
        self.assertEqual(fc.DOMAIN_PIECES[fc.EDGE], ())                     # a fita é um domínio independente

    def test_grupos_viram_papel(self):
        self.assertEqual(fc.piece_role_of_component('POR'), fc.PIECE_FRONT)
        self.assertEqual(fc.piece_role_of_component('PRAT'), fc.PIECE_INTERNAL)
        self.assertEqual(fc.piece_role_of_component('DIV'), fc.PIECE_INTERNAL)
        self.assertEqual(fc.piece_role_of_component('LAT'), fc.PIECE_EXTERNAL)
        self.assertEqual(fc.piece_role_of_component('BACK'), fc.PIECE_EXTERNAL)   # o fundo segue a caixa
        self.assertEqual(fc.piece_role_of_component(''), fc.PIECE_UNKNOWN)
        self.assertEqual(fc.piece_role_of_component('LAT', is_front=True), fc.PIECE_FRONT)

    def test_frentes_nascem_com_veio_vertical(self):
        self.assertEqual(fc.DEFAULT_GRAIN[fc.FRONTS], 'V')
        self.assertEqual(fc.DEFAULT_GRAIN[fc.EXTERNAL], 'NONE')


class MigrationTest(unittest.TestCase):
    def test_caixa_vira_os_dois_dominios(self):
        self.assertEqual(fc.migrate_groups({'CAIXA': 'Carvalho'}),
                         {fc.EXTERNAL: 'Carvalho', fc.INTERNAL: 'Carvalho'})

    def test_fundo_segue_a_caixa_e_frentes(self):
        out = fc.migrate_groups({'FUNDO': 'Branco', 'FRENTES': 'Freijó'})
        self.assertEqual(out, {fc.EXTERNAL: 'Branco', fc.INTERNAL: 'Branco', fc.FRONTS: 'Freijó'})

    def test_front_material_vence_o_grupo(self):
        self.assertEqual(fc.migrate_groups({'FRENTES': 'A'}, 'B')[fc.FRONTS], 'B')

    def test_caixa_ganha_do_interno_no_mesmo_dominio(self):
        out = fc.migrate_groups({'CAIXA': 'Carvalho', 'INTERNO': 'Branco', 'FUNDO': 'Cinza'})
        self.assertEqual(out[fc.INTERNAL], 'Carvalho')
        self.assertEqual(out[fc.EXTERNAL], 'Carvalho')

    def test_sem_grupos_nada_migra(self):
        self.assertEqual(fc.migrate_groups({}), {})
        self.assertEqual(fc.migrate_groups({'CAIXA': ''}), {})

    def test_aparencia_igual_com_um_material_so(self):
        # Com a caixa só, o domínio migrado dá a cada face o mesmo material do caminho antigo (M-03).
        groups = {'CAIXA': 'Carvalho'}
        migrated = fc.migrate_groups(groups)
        for slot in (0, 1, 2):
            legacy = fc.legacy_face_material(slot, groups)
            role = fc.piece_role_of_legacy_slot(slot)
            domain = fc.domains_for_piece(role)[0]
            self.assertEqual(migrated[domain], legacy)

    def test_slot_antigo_vira_papel(self):
        self.assertEqual(fc.piece_role_of_legacy_slot(0), fc.PIECE_EXTERNAL)
        self.assertEqual(fc.piece_role_of_legacy_slot(1), fc.PIECE_INTERNAL)
        self.assertEqual(fc.piece_role_of_legacy_slot(2), fc.PIECE_EXTERNAL)


class SummaryTest(unittest.TestCase):
    def test_multiplos(self):
        self.assertEqual(fc.summarize(['A', 'A']), 'A')
        self.assertEqual(fc.summarize(['A', 'B']), fc.MULTIPLE)
        self.assertEqual(fc.summarize(['', None]), '')


class BoxFacesTest(unittest.TestCase):
    INNER = ((0.018, 0.0, 0.018), (0.582, 0.56, 0.682))

    def test_lateral_esquerda(self):
        roles = fc.box_face_roles((0.0, 0.0, 0.0), (0.018, 0.58, 0.7), *self.INNER)
        # base, topo, frente, direita (+X, para dentro), trás, esquerda (−X, para fora)
        self.assertEqual(roles, (fc.FACE_EDGE, fc.FACE_EDGE, fc.FACE_EDGE, fc.FACE_INTERNAL, fc.FACE_EDGE,
                                 fc.FACE_EXTERNAL))

    def test_fundo_tem_face_de_tras_aparente(self):
        roles = fc.box_face_roles((0.018, 0.56, 0.018), (0.582, 0.58, 0.682), *self.INNER)
        self.assertEqual(roles[2], fc.FACE_INTERNAL)      # frente do fundo olha para o vão
        self.assertEqual(roles[4], fc.FACE_EXTERNAL)      # trás do fundo é aparente
        self.assertEqual(roles.count(fc.FACE_EDGE), 4)

    def test_prateleira_tem_as_duas_faces_internas(self):
        low, high = (0.018, 0.02, 0.3), (0.582, 0.56, 0.318)
        self.assertTrue(fc.inside_box(low, high, *self.INNER))
        roles = fc.box_face_roles(low, high, *self.INNER, inside=True)
        self.assertEqual(roles[:2], (fc.FACE_INTERNAL, fc.FACE_INTERNAL))

    def test_base_tem_a_face_de_baixo_aparente(self):
        roles = fc.box_face_roles((0.018, 0.0, 0.0), (0.582, 0.56, 0.018), *self.INNER)
        self.assertEqual(roles[:2], (fc.FACE_EXTERNAL, fc.FACE_INTERNAL))


if __name__ == '__main__':
    unittest.main()
