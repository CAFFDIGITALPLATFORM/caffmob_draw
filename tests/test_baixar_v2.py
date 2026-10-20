"""065 T118: escolha de contrato, ordem real dos passos e descarte sem Blender."""
import copy
import importlib.util
import json
from pathlib import Path
import sys
import types
import unittest
from unittest.mock import Mock, patch
import _bootstrap
from caffmob_draw.mobi.baixar_v2 import Preparo, lista_v2, relatorio, revisao, rotulo, schema_do_item
from caffmob_draw.mobi.api_v2_core import SCHEMA_V1, SCHEMA_V2

ROOT = Path(__file__).resolve().parents[1]
DOC = json.loads((ROOT / 'tests/casos_ouro_v2/obra/referencia-obra.json').read_text())['entrada']


class MontagemFalsa:
    def __init__(self, erro=None):
        self.erro, self.executados, self.limpezas = erro, [], 0
        self.preparo, self.cena = [], ['local', 'ambiente anterior']

    def passos(self):
        for etapa in ('pavimentos', 'paredes', 'paredes', 'obra', 'moveis', 'texturas'):
            def passo(etapa=etapa):
                self.preparo.append(etapa)
                self.executados.append(etapa)
                if etapa == self.erro:
                    raise RuntimeError('Erro forçado')
            yield etapa, passo

    def cancelar(self):
        self.preparo.clear()
        self.limpezas += 1


class BaixarV2(unittest.TestCase):
    def test_lista_v2_so_com_capacidade_explicita(self):
        for caps in (None, {}, {'ambientes_v2': False}, {'ambientes_v2': 1}):
            self.assertFalse(lista_v2(caps))
        self.assertTrue(lista_v2({'ambientes_v2': True}))

    def test_lista_distingue_os_dois_contratos_por_texto(self):
        self.assertEqual(rotulo(SCHEMA_V1), 'v 1')
        self.assertEqual(rotulo(SCHEMA_V2), 'v 2')

    def test_escolha_do_download_pelo_item_com_v1_como_padrao(self):
        itens = [types.SimpleNamespace(id='antigo', schema=SCHEMA_V1),
                 types.SimpleNamespace(id='studio', schema=SCHEMA_V2)]
        self.assertEqual(schema_do_item(itens, 'antigo', SCHEMA_V2), SCHEMA_V1)
        self.assertEqual(schema_do_item(itens, 'studio'), SCHEMA_V2)
        self.assertEqual(schema_do_item(itens, 'fora da lista'), SCHEMA_V1)
        self.assertEqual(schema_do_item(itens, 'fora da lista', SCHEMA_V2), SCHEMA_V2)

    def test_revisao_forte_igual_ao_documento(self):
        self.assertEqual(revisao({'version': 7}, {'eTaG': '"7"'}), '"7"')
        for headers in ({}, {'ETag':'W/"7"'}, {'ETag':'"8"'}):
            with self.assertRaises(ValueError):
                revisao({'version':7}, headers)
        with self.assertRaises(ValueError):
            revisao({'version':True}, {'ETag':'"True"'})

    def test_relatorio_conserva_caminhos_e_codigos(self):
        self.assertEqual(relatorio([dict(caminho='paredes[0].segmentos[1]', mensagem='Inválido', codigo='LIMITE')]),
                         'paredes[0].segmentos[1]: Inválido (LIMITE)')

    def test_um_passo_por_chamada_e_progresso_em_ordem(self):
        montagem, progresso = MontagemFalsa(), []
        fluxo = Preparo(montagem, lambda e,v: progresso.append((e,v)))
        while fluxo.avancar():
            self.assertEqual(len(montagem.executados), len(progresso))
        self.assertTrue(fluxo.pronto)
        self.assertEqual([p[0] for p in progresso], montagem.executados)
        self.assertEqual([p[1] for p in progresso], sorted(p[1] for p in progresso))
        self.assertEqual(len(fluxo.medicoes), 6)
        self.assertEqual(montagem.cena, ['local', 'ambiente anterior'])

    def test_cancelar_entre_todos_os_passos_remove_preparo_uma_vez(self):
        for limite in range(8):
            with self.subTest(limite=limite):
                montagem = MontagemFalsa()
                fluxo = Preparo(montagem)
                for _ in range(limite):
                    fluxo.avancar()
                fluxo.cancelar()
                fluxo.cancelar()
                self.assertFalse(fluxo.avancar())
                self.assertEqual(montagem.limpezas, 1)
                self.assertEqual(montagem.preparo, [])
                self.assertEqual(montagem.cena, ['local', 'ambiente anterior'])

    def test_erro_em_cada_etapa_descarta_tambem_os_dados_parciais(self):
        for etapa in ('pavimentos', 'paredes', 'obra', 'moveis', 'texturas'):
            with self.subTest(etapa=etapa):
                montagem = MontagemFalsa(etapa)
                fluxo = Preparo(montagem)
                with self.assertRaises(RuntimeError):
                    while fluxo.avancar():
                        pass
                self.assertEqual(montagem.preparo, [])
                self.assertEqual(montagem.limpezas, 1)
                self.assertEqual(montagem.cena, ['local', 'ambiente anterior'])

    def test_ordem_do_montador_real_pavimentos_paredes_obra_moveis_texturas(self):
        import caffmob_draw.mobi as mobi
        import caffmob_draw.openings as openings
        stubs = {name: types.ModuleType(name) for name in ('bpy', 'bmesh',
            'caffmob_draw.mobi.cena', 'caffmob_draw.mobi.materiais_v2', 'caffmob_draw.openings.build')}
        stubs['caffmob_draw.mobi.cena'].NOME_DA_COLECAO = 'CAFF MOB'
        spec = importlib.util.spec_from_file_location('caffmob_draw.mobi.cena_v2_ensaio', ROOT / 'caffmob_draw/mobi/cena_v2.py')
        mod = importlib.util.module_from_spec(spec)
        with patch.dict(sys.modules, stubs), \
             patch.object(mobi, 'cena', stubs['caffmob_draw.mobi.cena'], create=True), \
             patch.object(mobi, 'materiais_v2', stubs['caffmob_draw.mobi.materiais_v2'], create=True), \
             patch.object(openings, 'build', stubs['caffmob_draw.openings.build'], create=True):
            spec.loader.exec_module(mod)
            montagem = mod.Montagem(None, copy.deepcopy(DOC))
            montagem.colecoes = {p['id']:Mock() for p in DOC['pavimentos']}
            etapas = [e for e, _passo in montagem.passos()]
            self.assertEqual(list(dict.fromkeys(etapas)), ['pavimentos', 'paredes', 'obra', 'moveis', 'texturas'])
            self.assertGreater(etapas.count('paredes'), len(DOC['paredes']))
            # A limpeza real só recebe os dados registrados pelo preparo.
            local, temporario = Mock(name='local'), Mock(name='preparo')
            montagem.criados['objects'].add(temporario)
            mod.bpy.data = types.SimpleNamespace(objects=Mock())
            montagem.cancelar()
            mod.bpy.data.objects.remove.assert_called_once_with(temporario, do_unlink=True)
            self.assertNotIn(local, montagem.criados['objects'])
            montagem.cancelar()
            self.assertEqual(mod.bpy.data.objects.remove.call_count, 1)


class IntegracaoJob(unittest.TestCase):
    """Mecanismo real da 063, com timers e transporte substituídos em memória."""
    def setUp(self):
        import caffmob_draw.texture_library as biblioteca
        class Scene(dict):
            name = 'Cena de ensaio'
        self.state = types.SimpleNamespace(ocupado=False, progresso=0.0, situacao='')
        self.context = types.SimpleNamespace(scene=Scene(), window_manager=types.SimpleNamespace(btm_caffmob=self.state))
        self.timers, self.callbacks, self.cancelados = [], [], []
        timers = types.SimpleNamespace(register=lambda f, **kw:self.timers.append(f),
            is_registered=lambda f:f in self.timers, unregister=lambda f:self.timers.remove(f))
        self.bpy = types.SimpleNamespace(context=self.context, app=types.SimpleNamespace(timers=timers,
            translations=types.SimpleNamespace(pgettext_iface=lambda s,*a:s)), types=types.SimpleNamespace(Operator=object),
            props=types.SimpleNamespace(StringProperty=lambda:None))
        handlers = types.ModuleType('bpy.app.handlers')
        handlers.persistent = lambda f:f
        bridge = types.SimpleNamespace(request=lambda *a,**kw:self.callbacks.append(kw['callback']) or {'rid':1},
            cancel_request=self.cancelados.append)
        spec = importlib.util.spec_from_file_location('caffmob_draw.mobi.tarefas_t118_ensaio', ROOT / 'caffmob_draw/mobi/tarefas.py')
        self.mod = importlib.util.module_from_spec(spec)
        self.patch_modules = patch.dict(sys.modules, {'bpy':self.bpy, 'bpy.app.handlers':handlers})
        self.patch_bridge = patch.object(biblioteca, 'downloads', bridge, create=True)
        self.patch_modules.start()
        self.patch_bridge.start()
        self.addCleanup(self.patch_modules.stop)
        self.addCleanup(self.patch_bridge.stop)
        spec.loader.exec_module(self.mod)

    def tick(self):
        callback = self.timers.pop(0)
        again = callback()
        if again is not None:
            self.timers.append(callback)

    def iniciar(self, montagem=None):
        self.job = self.mod.Job(self.context, 'Ensaio')
        self.fluxo = Preparo(montagem or MontagemFalsa())
        self.commit = Mock()
        self.job.apply = self.commit
        self.job.preparar_em_passos(self.fluxo, lambda context:None)

    def test_timer_cede_entre_unidades_e_so_aplica_quando_pronto(self):
        self.iniciar()
        for n in range(6):
            self.tick()
            self.assertEqual(len(self.fluxo.montagem.executados), n+1)
            self.commit.assert_not_called()
        self.tick()
        self.assertTrue(self.fluxo.pronto)
        self.commit.assert_called_once()
        self.assertEqual(self.timers, [])

    def test_cancelar_apos_parede_limpa_e_suprime_callback_atrasado(self):
        self.iniciar()
        callback = Mock()
        self.job.request('GET', '/ambiente', callback=callback)
        self.tick()
        self.tick()
        self.job.cancel()
        self.callbacks[0](200, {}, {})
        callback.assert_not_called()
        self.commit.assert_not_called()
        self.assertEqual(self.cancelados, [{'rid':1}])
        self.assertEqual(self.timers, [])
        self.assertEqual(self.fluxo.montagem.preparo, [])
        self.assertEqual(self.fluxo.montagem.limpezas, 1)

    def test_erro_no_tick_mostra_erro_e_limpa(self):
        self.iniciar(MontagemFalsa('obra'))
        while self.timers:
            self.tick()
        self.assertFalse(self.state.ocupado)
        self.assertIn('Erro forçado', self.state.situacao)
        self.assertEqual(self.fluxo.montagem.preparo, [])
        self.assertEqual(self.fluxo.montagem.limpezas, 1)
        self.commit.assert_not_called()

    def test_troca_de_cena_descarta_sem_aplicar(self):
        self.iniciar()
        self.tick()
        self.context.scene.name = 'Outra cena'
        self.tick()
        self.assertEqual(self.timers, [])
        self.assertEqual(self.fluxo.montagem.preparo, [])
        self.commit.assert_not_called()

    def test_load_e_novo_job_recolhem_preparo_anterior(self):
        self.iniciar()
        self.tick()
        self.mod.on_load_pre()
        self.assertEqual(self.fluxo.montagem.preparo, [])
        self.assertEqual(self.timers, [])
        self.iniciar()
        self.tick()
        self.mod.Job(self.context, 'Outro pedido')
        self.assertTrue(self.fluxo.cancelado)
        self.assertEqual(self.fluxo.montagem.preparo, [])
        self.assertEqual(self.timers, [])


if __name__ == '__main__':
    unittest.main()
