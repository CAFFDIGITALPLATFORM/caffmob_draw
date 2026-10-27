"""073 (T008; RN-02, D-02, D-03): o manifesto das texturas PBR do pacote.

- UUID = uuid5(NAMESPACE_PBR, slug), recalculado; slug único e em kebab-case;
- uma textura `padrao` por palavra de grupo; metal exige o mapa metálico; tamanho real inteiro de 1 a 10000 mm;
- origem com id, url e licença CC0-1.0;
- o manifesto real do pacote, quando existir, passa nas mesmas regras e confere os arquivos e o sha256.
"""
import copy
import hashlib
import os
import unittest

import _pbr_sintetico as ps
from caffmob_draw.texture_library import pbr_core

PACOTE_PBR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'caffmob_draw', 'pbr')


def sha256(caminho):
    with open(caminho, 'rb') as f:
        return hashlib.sha256(f.read()).hexdigest()


class ManifestoTest(unittest.TestCase):
    def test_sintetico_valido(self):
        self.assertEqual(pbr_core.validar_manifesto(ps.manifesto()), [])

    def test_uuid_estavel(self):
        self.assertEqual(pbr_core.uuid_de('tijolo-aparente'), pbr_core.uuid_de('tijolo-aparente'))
        self.assertEqual(pbr_core.uuid_de('tijolo-aparente'), '60744c13-2829-5105-8936-7417a8a586c3')

    def _com(self, mudar):
        dados = copy.deepcopy(ps.manifesto())
        mudar(dados['texturas'])
        return pbr_core.validar_manifesto(dados)

    def test_regras(self):
        casos = {
            'uuid': lambda ts: ts[0].update(uuid='00000000-0000-0000-0000-000000000000'),
            'repetido': lambda ts: ts[1].update(slug=ts[0]['slug'], uuid=ts[0]['uuid']),
            'padrão': lambda ts: ts[0].update(padrao=True),
            'metalico': lambda ts: ts[9]['mapas'].pop('metalico'),
            'tamanho_mm': lambda ts: ts[0].update(tamanho_mm=dict(largura=0, altura=1200)),
            'origem': lambda ts: ts[0]['origem'].update(licenca='CC-BY-4.0'),
            'palavras': lambda ts: ts[0].update(palavras=['Tijolo']),
            'tom': lambda ts: ts[0].update(tom='rosado'),
            'mapa normal': lambda ts: ts[0]['mapas']['normal'].update(arquivo='../fora.jpg'),
        }
        for trecho, mudar in casos.items():
            with self.subTest(trecho):
                problemas = self._com(mudar)
                self.assertTrue(any(trecho in p for p in problemas), problemas)

    def test_licenca_do_manifesto(self):
        dados = ps.manifesto()
        dados['licenca'] = 'GPL-3.0'
        self.assertTrue(pbr_core.validar_manifesto(dados))

    @unittest.skipUnless(os.path.isfile(os.path.join(PACOTE_PBR, 'manifest.json')), 'pacote ainda sem texturas PBR')
    def test_manifesto_do_pacote(self):
        dados = pbr_core.carregar(PACOTE_PBR)
        self.assertEqual(pbr_core.validar_manifesto(dados, PACOTE_PBR, sha256), [])
        self.assertEqual(len(dados['texturas']), 26)


if __name__ == '__main__':
    unittest.main()
