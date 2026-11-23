"""017 (T010; RN-13, RF-12): internos do vão, posição inicial do mockup, faixa editável e desempate.

Contrato de `armario_v2/internos.py` (T018): `Interno`, `TIPOS`, `ALTURA_BAIXA = 480.0`,
`MALEIRO_ABAIXO_TOPO = 420.0`, `PASSO_DESEMPATE = 50.0`, `altura_inicial(tipo, altura_vao)`,
`faixa(altura_vao, espessura)`, `inserir(internos, vao, tipo, altura_vao, espessura, altura=None, uid=None)` e
`resolver(internos, altura_vao, espessura)`. Medidas em milímetros.

A regra de desempate é premissa 🟡 do roadmap §4: fica isolada aqui para ser corrigida sem tocar nas abas.
"""
import importlib
import unittest

import _bootstrap  # noqa: F401


def _modulo(nome):
    """Módulo do núcleo da Fase 3, ou `None` enquanto a ação que o cria não rodou."""
    completo = f'caffmob_draw.armario_v2.{nome}'
    try:
        return importlib.import_module(completo)
    except ModuleNotFoundError as erro:
        if erro.name == completo:
            return None
        raise


internos = _modulo('internos')
PENDENTE = 'caffmob_draw/armario_v2/internos.py ainda não existe (T018)'


@unittest.skipIf(internos is None, PENDENTE)
class InternosTest(unittest.TestCase):
    def test_posicoes_iniciais_do_mockup(self):
        self.assertEqual(internos.ALTURA_BAIXA, 480.0)
        self.assertEqual(internos.MALEIRO_ABAIXO_TOPO, 420.0)
        self.assertEqual(set(internos.TIPOS), {'CABIDEIRO', 'CALCEIRO', 'SAPATEIRA', 'MALEIRO'})
        self.assertEqual(internos.altura_inicial('CALCEIRO', 2000.0), 480.0)
        self.assertEqual(internos.altura_inicial('SAPATEIRA', 2000.0), 480.0)
        self.assertEqual(internos.altura_inicial('MALEIRO', 2000.0), 1580.0)   # 2000 − 420
        self.assertEqual(internos.altura_inicial('CABIDEIRO', 2000.0), 0.0)

    def test_faixa_editavel(self):
        self.assertEqual(internos.faixa(2000.0, 15.0), (0.0, 1985.0))
        _, novo = internos.inserir([], 's0', 'CALCEIRO', altura_vao=2000.0, espessura=15.0)
        self.assertEqual(novo.altura, 480.0)
        _, alto = internos.inserir([], 's0', 'CALCEIRO', altura_vao=2000.0, espessura=15.0, altura=3000.0)
        self.assertEqual(alto.altura, 1985.0)
        _, baixo = internos.inserir([], 's0', 'CALCEIRO', altura_vao=2000.0, espessura=15.0, altura=-30.0)
        self.assertEqual(baixo.altura, 0.0)

    def test_interno_preso_ao_vao_escolhido(self):
        _, novo = internos.inserir([], 's0.b', 'MALEIRO', altura_vao=2000.0, espessura=15.0)
        self.assertEqual(novo.vao, 's0.b')
        self.assertEqual(novo.altura, 1580.0)

    def test_desempate_de_dois_internos_na_mesma_altura(self):
        lista, primeiro = internos.inserir([], 's0', 'CALCEIRO', altura_vao=2000.0, espessura=15.0)
        lista, segundo = internos.inserir(lista, 's0', 'SAPATEIRA', altura_vao=2000.0, espessura=15.0)
        self.assertEqual(len(lista), 2)
        resolvidos = internos.resolver(lista, altura_vao=2000.0, espessura=15.0)
        self.assertEqual(len(resolvidos), 2)
        por_uid = {item.uid: item for item in resolvidos}
        self.assertEqual(por_uid[segundo.uid].altura, 480.0)         # o último vence
        self.assertEqual(por_uid[primeiro.uid].altura, 530.0)        # o outro sobe 50 mm
        self.assertEqual(internos.PASSO_DESEMPATE, 50.0)
        # resolver é idempotente: rodar de novo no resultado não muda nada
        self.assertEqual(internos.resolver(resolvidos, altura_vao=2000.0, espessura=15.0), resolvidos)


if __name__ == '__main__':
    unittest.main()
