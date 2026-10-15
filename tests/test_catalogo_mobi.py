# (063 RF-03; D-07) Correspondência e cache das páginas.
import tempfile
import unittest
import _bootstrap
from caffmob_draw.texture_library import catalog, catalog_core

ITEM = {'id': 'uuid', 'fabricante': 'Berneck', 'linha': 'Linha', 'nome': 'Madeira', 'largura': 2400,
        'altura': 1200, 'formato': 'jpeg', 'sha256_trabalho': 'a'*64, 'sha256_miniatura': 'b'*64, 'mapas': ['bump']}


class Catalogo(unittest.TestCase):
    def test_correspondencia(self):
        result = catalog.from_mobi(ITEM)
        self.assertEqual(result['size-mm'], catalog_core.size_mm([2400, 1200]))
        self.assertEqual(result['ext'], 'jpg')
        self.assertTrue(result['bump'])
        self.assertEqual(result['sha256'], ITEM['sha256_trabalho'])
        self.assertEqual(result['bytes'], 0)
        self.assertIn('tamanho=miniatura', catalog.thumb_entry(result)['url'])
        self.assertEqual(catalog.thumb_entry(result)['sha256'], 'b'*64)
        result = catalog.from_mobi(dict(ITEM, formato='png', mapas=[]))
        self.assertEqual(result['ext'], 'png')
        self.assertFalse(result['bump'])

    def test_cache_persistente_por_chave_sem_colisao_de_filtro(self):
        with tempfile.TemporaryDirectory() as directory:
            cache = catalog.PageCache(directory)
            cache.write('/texturas?cursor=a', {'itens': [ITEM], 'proximo': 'b'}, '"pagina"')
            self.assertEqual(catalog.PageCache(directory).read('/texturas?cursor=a')['etag'], '"pagina"')
            self.assertEqual(cache.read('/texturas?cursor=b'), {})
