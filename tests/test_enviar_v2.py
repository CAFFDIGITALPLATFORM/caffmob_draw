"""065 T119/T120: montagem e protocolo sem Blender ou rede."""
import copy
import json
import math
from pathlib import Path
import unittest
import _bootstrap
from caffmob_draw.mobi.enviar_v2_core import (montar_documento, novo_documento, schema_da_cena,
    aplicar_delta, SCHEMA_V1, SCHEMA_V2, _girar)
from caffmob_draw.mobi.api_v2_core import ClienteV2, Conflito
from caffmob_draw.mobi.api_v2 import ArmazenamentoCena
from caffmob_draw.caffmob.v2.validacao import validar_documento
from caffmob_draw.caffmob.v2.serializacao import DocumentoInvalido

DOC = json.loads((Path(__file__).parent / 'casos_ouro_v2/referencia-rica.json').read_text())['entrada']
CAPS = dict(versao_api=2, schemas=[SCHEMA_V1, SCHEMA_V2], ambientes_v2=True)


def objeto(tipo='modulo', familia='modulos', indice=0):
    e = copy.deepcopy(DOC[familia][indice])
    p = e.get('posicao', dict(x=0, y=0, z=0))
    posicao = [p[k] for k in 'xyz'] if isinstance(p, dict) else [0, 0, 0]
    r = e.get('rotacao_z', 0)
    if tipo == 'modulo':
        x, y = _girar(e['parametros']['largura']/2, e['parametros']['profundidade'], r)
        posicao[0] += x
        posicao[1] += y
    lugar = dict(posicao=posicao, rotacao=[0, 0, r], escala=[1, 1, 1])
    return dict(chave=1, nome='Reconhecido', tipo=tipo, id=e['id'], original=e,
                editada=copy.deepcopy(e), lugar=copy.deepcopy(lugar), inicial=lugar)


class Montagem(unittest.TestCase):
    def test_sem_edicao_igualdade_profunda_todos_os_campos(self):
        objs = [objeto(t, f, i) for t, f in (('modulo','modulos'),('parede','paredes'),
            ('peca_avulsa','pecas_avulsas'),('primitiva','primitivas'),('escada','escadas'),('item_externo','itens_externos'))
            for i in range(len(DOC[f]))]
        saida, avisos = montar_documento(DOC, objs)
        self.assertEqual(saida, DOC)
        self.assertEqual(avisos, [])
        self.assertIsNot(saida['modulos'][0], DOC['modulos'][0])

    def test_delta_move_modulo_mantem_vinculos_materiais_e_parametros(self):
        obj = objeto()
        obj['lugar']['posicao'][0] += 123.456789
        esperado = copy.deepcopy(DOC)
        esperado['modulos'][0]['posicao']['x'] += 123.456789
        saida, _ = montar_documento(DOC, [obj])
        self.assertAlmostEqual(saida['modulos'][0]['posicao']['x'], esperado['modulos'][0]['posicao']['x'], places=10)
        saida['modulos'][0]['posicao'] = esperado['modulos'][0]['posicao']
        self.assertEqual(saida, esperado)
        self.assertEqual(validar_documento(saida), [])

    def test_ruido_float32_nao_altera_campo(self):
        obj = objeto()
        obj['lugar']['posicao'][0] += 0.0002
        obj['lugar']['rotacao'][2] += 0.000001
        saida, _ = montar_documento(DOC, [obj])
        self.assertEqual(saida, DOC)

    def test_rotacao_modulo_em_torno_do_pivo(self):
        obj = objeto()
        obj['lugar']['rotacao'][2] += 90
        saida, _ = montar_documento(DOC, [obj])
        e = saida['modulos'][0]
        self.assertAlmostEqual(e['rotacao_z'], 127)
        x,y = _girar(400,600,127)
        self.assertAlmostEqual(e['posicao']['x'], obj['lugar']['posicao'][0]-x)
        self.assertAlmostEqual(e['posicao']['y'], obj['lugar']['posicao'][1]-y)

    def test_escala_edita_so_dimensoes_editaveis(self):
        obj = objeto()
        obj['lugar']['escala'] = [1.1, 1.2, 1.3]
        saida, _ = montar_documento(DOC, [obj])
        p = saida['modulos'][0]['parametros']
        self.assertAlmostEqual(p['largura'], 880)
        self.assertAlmostEqual(p['profundidade'], 720)
        self.assertAlmostEqual(p['altura'], 1066)
        self.assertEqual(p['chapas_editadas'], DOC['modulos'][0]['parametros']['chapas_editadas'])

    def test_pavimento_elevado_posicao_relativa(self):
        obj = objeto('primitiva','primitivas')
        obj['inicial']['posicao'][2] += 2750
        obj['lugar']['posicao'][2] += 2873
        saida, _ = montar_documento(DOC, [obj], {obj['original']['pavimento_id']:2750})
        self.assertAlmostEqual(saida['primitivas'][0]['posicao']['z'], 130)

    def test_parede_editada_pelo_contrato_sem_perder_material(self):
        obj = objeto('parede','paredes')
        obj['editada']['segmentos'][0]['espessura'] = 175
        saida, _ = montar_documento(DOC, [obj])
        esperado = copy.deepcopy(DOC)
        esperado['paredes'][0]['segmentos'][0]['espessura'] = 175
        self.assertEqual(saida, esperado)
        self.assertEqual(validar_documento(saida), [])

    def test_parametro_editado_mantem_o_restante(self):
        obj = objeto()
        obj['editada']['parametros']['construcao']['prateleiras']['quantidade'] = 3
        saida,_ = montar_documento(DOC,[obj])
        esperado=copy.deepcopy(DOC)
        esperado['modulos'][0]['parametros']['construcao']['prateleiras']['quantidade']=3
        self.assertEqual(saida,esperado)

    def test_repetir_montagem_sobre_base_atualizada_nao_soma_movimento(self):
        obj=objeto()
        obj['lugar']['posicao'][0]+=150
        primeira,_=montar_documento(DOC,[obj])
        segunda,_=montar_documento(primeira,[obj])
        self.assertEqual(primeira,segunda)

    def test_externo_pai_e_descendentes_uma_caixa_mundial(self):
        locais=[dict(chave=10,pai=None,nome='Pai',tipo_blender='EMPTY',externo_id='00000000-0000-4000-8000-000000000010'),
                dict(chave=11,pai=10,nome='Filho 1',tipo_blender='MESH',cantos=[[-120.123,20,30],[200,320,430]]),
                dict(chave=12,pai=10,nome='Filho 2',tipo_blender='MESH',cantos=[[300,-450.456,200],[900,20,1000.789]])]
        saida,avisos=montar_documento(DOC,locais)
        self.assertEqual(len(saida['itens_externos']),2)
        item=saida['itens_externos'][-1]
        self.assertEqual(item['posicao'],dict(x=-120.123,y=-450.456,z=30))
        self.assertEqual(item['dimensoes'],dict(largura=1020.123,profundidade=770.456,altura=970.789))
        self.assertEqual(avisos,[])
        self.assertEqual(validar_documento(saida),[])
        repetido,_=montar_documento(saida,locais)
        self.assertEqual(saida,repetido)

    def test_reverter_apos_sucesso_restaura_posicao_e_parametro(self):
        obj=objeto()
        obj['lugar']['posicao'][0]+=150
        obj['editada']['parametros']['altura']=900
        primeira,_=montar_documento(DOC,[obj])
        obj['ultimo_envio']=copy.deepcopy(primeira['modulos'][0])
        obj['lugar']=copy.deepcopy(obj['inicial'])
        obj['editada']=copy.deepcopy(obj['original'])
        segunda,_=montar_documento(primeira,[obj])
        self.assertEqual(segunda,DOC)

    def test_peca_dimensoes_recortes_e_materiais_preservados(self):
        obj=objeto('peca_avulsa','pecas_avulsas')
        obj['lugar']['escala']=[2,3,4]
        saida,_=montar_documento(DOC,[obj])
        e=saida['pecas_avulsas'][0]
        self.assertEqual(e['dimensoes'],dict(largura=1400,profundidade=1200,altura=2000))
        for k in ('recortes','veio','fitas','material_id','espessura'):
            self.assertEqual(e[k],DOC['pecas_avulsas'][0][k])

    def test_filho_derivado_nao_vira_externo(self):
        saida,_=montar_documento(DOC,[dict(chave=1,nome='Frente',tipo='modulo_frentes')])
        self.assertEqual(saida,DOC)

    def test_sem_malha_e_perfil_desconhecido_relata_preservando_base(self):
        obj=objeto()
        obj['editada']['perfil_construcao']='outro/2'
        saida,avisos=montar_documento(DOC,[obj,dict(chave=2,pai=None,nome='Luz',tipo_blender='LIGHT',externo_id='x')])
        self.assertEqual(saida,DOC)
        self.assertEqual([a['codigo'] for a in avisos],['PRESERVADO','SEM_MALHA'])

    def test_identidade_adulterada_e_duplicada_recusada(self):
        for objs in ([objeto(),objeto()],[{**objeto(),'id':'outro'}],
                     [{**objeto(),'editada':{**DOC['modulos'][0],'id':'outro'}}]):
            with self.assertRaises(DocumentoInvalido): montar_documento(DOC,objs)

    def test_rotacao_xy_cisalhamento_escala_negativa_recusados(self):
        for campo,valor in (('rotacao',[10,0,37]),('escala',[-1,1,1])):
            obj=objeto()
            obj['lugar'][campo]=valor
            with self.assertRaises(DocumentoInvalido): montar_documento(DOC,[obj])
        obj=objeto()
        obj['lugar']['posicao'][0]+=1
        obj['cisalhamento']=True
        with self.assertRaises(DocumentoInvalido): montar_documento(DOC,[obj])

    def test_novo_documento_uuid_novo_valido_sem_download(self):
        a,b=novo_documento(),novo_documento()
        self.assertNotEqual(a['id'],b['id'])
        self.assertEqual(validar_documento(a),[])

    def test_schema_v1_v2_e_cena_nova(self):
        for schema in (SCHEMA_V1,SCHEMA_V2):
            self.assertEqual(schema_da_cena({'caffmob_ambiente':json.dumps({'schema':schema}), 'caffmob_base_v2':'antiga'}),schema)
        self.assertEqual(schema_da_cena({}),SCHEMA_V2)

    def test_delta_conserva_campo_aditivo_da_base(self):
        base=dict(a=dict(x=1,y=2),campo_novo=3)
        aplicar_delta(base,dict(a=dict(x=1)),dict(a=dict(x=8)))
        self.assertEqual(base,dict(a=dict(x=8,y=2),campo_novo=3))


class Protocolo(unittest.TestCase):
    def setUp(self):
        self.scene={}
        self.storage=ArmazenamentoCena(self.scene)
        self.pedidos=[]
        self.retorno=[]
        def transporte(metodo,path,corpo=None,headers=None,callback=None):
            self.assertIsNotNone(self.storage.ler())
            self.pedidos.append((metodo,path,copy.deepcopy(corpo),headers,callback))
        self.client=ClienteV2(transporte,self.storage,{'capacidades':CAPS})

    def test_resposta_perdida_reabre_estado_e_reenvia_mesmo_pedido(self):
        self.client.enviar(DOC,'PUT',1,self.retorno.append)
        self.pedidos[-1][-1](None,{}, {})
        chave=self.storage.ler().chave
        reaberto=ArmazenamentoCena(json.loads(json.dumps(self.scene)))
        self.assertEqual(reaberto.ler().chave,chave)
        self.client.reenviar(self.retorno.append)
        self.assertEqual(self.pedidos[0][0:4],self.pedidos[1][0:4])
        self.assertEqual(self.pedidos[1][3]['If-Match'],'"1"')
        self.pedidos[-1][-1](200,dict(id=DOC['id'],version=2),{'ETag':'"2"'})
        self.assertIsNone(self.storage.ler())

    def test_409_preserva_duas_versoes_tres_escolhas_chaves_novas(self):
        self.client.enviar(DOC,'PUT',1,self.retorno.append)
        antiga=self.storage.ler().chave
        remota=copy.deepcopy(DOC)
        remota['version']=2
        self.pedidos[-1][-1](409,dict(erro='VERSAO_DIVERGENTE',versao_atual=2,documento_atual=remota),{})
        conflito=self.retorno[-1].conflito
        self.assertEqual(conflito.escolhas,('remota','local','copia'))
        self.assertEqual(conflito.local,DOC)
        self.assertEqual(conflito.escolher('remota'),remota)
        local,copia=conflito.escolher('local'),conflito.escolher('copia')
        self.assertEqual(local.revisao_base,2)
        self.assertNotEqual(local.chave,antiga)
        self.assertNotEqual(copia.ambiente_id,DOC['id'])
        self.assertEqual(copia.metodo,'POST')

    def test_invalido_nao_chama_transporte_e_aponta_caminho(self):
        bad=copy.deepcopy(DOC)
        bad['modulos'][0]['parametros']['largura']=-1
        with self.assertRaises(DocumentoInvalido) as exc:
            self.client.enviar(bad,'PUT',1,self.retorno.append)
        self.assertTrue(any('largura' in e['caminho'] for e in exc.exception.erros))
        self.assertEqual(self.pedidos,[])

    def test_servidor_antigo_recusa_v2_sem_fallback(self):
        self.client.sessao['capacidades']=dict(versao_api=1,schemas=[SCHEMA_V1],ambientes_v2=False)
        with self.assertRaisesRegex(ValueError,'somente ambientes v1'):
            self.client.enviar(DOC,'PUT',1,self.retorno.append)
        self.assertEqual(self.pedidos,[])


if __name__=='__main__': unittest.main()
