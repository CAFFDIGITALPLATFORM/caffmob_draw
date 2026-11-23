"""017 (T035; D-17, RN-24, RF-19): o módulo convertido não pode aparecer duas vezes no plano de corte.

Teste puro: `cutting.part_sources` importa `compat`, que importa `bpy` no topo, então o teste injeta um `bpy` mínimo só
para a importação e o remove em seguida (nenhuma função exercitada aqui chama `bpy`). A cena é falsa, no molde das
demais suítes puras da 017.

A contagem imita o que `part_extractor.extract_production_parts` faz com as duas fontes envolvidas: os módulos de
`iter_modules` pelo caminho sintético e as peças com `btm_armario_parte`. Um módulo `btm` visível contribui com as
chapas sintéticas; depois de `Gerar` a partir dele (o que a ponte faz: ocultar e marcar com `btm_cut_exclude`), ele some
da contagem e só as peças do armário v2 ficam — sem duplicar o mesmo móvel com medidas diferentes.
"""

import importlib
import sys
import types
import unittest

import _bootstrap  # noqa: F401


def _importar_com_bpy_falso(nome):
    """Importa um módulo de `cutting` com um `bpy` mínimo, tirando o falso do `sys.modules` depois."""
    proprio = 'bpy' not in sys.modules
    if proprio:
        falso = types.ModuleType('bpy')
        falso.app = types.SimpleNamespace(version=(5, 2, 0))
        sys.modules['bpy'] = falso
    try:
        return importlib.import_module(nome)
    finally:
        if proprio:
            sys.modules.pop('bpy', None)


part_sources = _importar_com_bpy_falso('caffmob_draw.cutting.part_sources')


class _Parte:
    """`BTM_PG_ArmarioParte` mínima."""

    def __init__(self, papel='LATERAL', componente='LAT'):
        self.papel, self.componente = papel, componente
        self.comprimento_mm, self.largura_mm, self.espessura_mm = 1000.0, 560.0, 15.0
        self.material, self.uid, self.veio = 'CHAPA', 'Armário v2/LATERAL/0', 'VERTICAL'
        self.fita_l1, self.fita_l2, self.fita_w1, self.fita_w2 = True, False, False, False
        self.movel, self.curso_mm, self.eixo = False, 0.0, 'Y'


class _Cabinet:
    def __init__(self):
        self.width, self.height, self.depth, self.thickness = 0.8, 0.9, 0.55, 0.015
        self.door_swing, self.assembly = 'NONE', 'LATERAL'


class _Plano:
    def __init__(self, object_kind=''):
        self.object_kind = object_kind


class _Objeto:
    """Objeto de cena falso: `btm_plane` de módulo, `btm_cabinet` e, opcionalmente, `btm_armario_parte`."""

    def __init__(self, nome, tipo='MESH', parent=None, parte=None, armario=False, modulo=False):
        self.name, self.type, self.parent = nome, tipo, parent
        self.hide_viewport, self._oculto = False, False
        self.btm_cut_exclude = False
        self.btm_plane = _Plano('MODULE' if modulo else '')     # só o móvel antigo é módulo
        self.btm_cabinet = _Cabinet()
        self.btm_structure = None
        self.btm_armario = object() if armario else None
        self.btm_armario_parte = parte
        self.modifiers, self.children_recursive = [], []
        self.dimensions = types.SimpleNamespace(x=0.8, y=0.55, z=0.9)
        self._props = {}

    def hide_get(self):
        return self._oculto

    def get(self, key, default=None):
        return self._props.get(key, default)

    def __setitem__(self, key, value):
        self._props[key] = value

    def __getitem__(self, key):
        return self._props[key]


class _Cena:
    def __init__(self, objetos):
        self.objects = objetos


def _cena(convertido=False):
    """Módulo `btm` (o caso do A001) e o armário v2 que saiu dele, num armário vazio da cena."""
    raiz = _Objeto('Armário v2', tipo='EMPTY', armario=True)
    pecas = [_Objeto('Lateral esquerda', parent=raiz, parte=_Parte()),
             _Objeto('Base inferior', parent=raiz, parte=_Parte('BASE_INF', 'BAS'))]
    raiz.children_recursive = pecas
    modulo = _Objeto('Módulo antigo', modulo=True)
    if convertido:
        modulo.hide_viewport = True
        modulo.btm_cut_exclude = True
    return _Cena([raiz, *pecas, modulo]), modulo


def _contar(cena):
    """Mesma composição de `extract_production_parts` para as duas fontes do caso: módulos + peças do armário v2."""
    registros = []
    for modulo in part_sources.iter_modules(cena):
        registros.extend(part_sources.synthetic_records(modulo, lambda _c: 15.0))
    registros.extend(part_sources.armario_v2_records(cena))
    return registros


class ModuloConvertidoTest(unittest.TestCase):
    def test_modulo_visivel_entra_como_sintetico_e_duplica_o_movel(self):
        cena, _modulo = _cena(convertido=False)
        registros = _contar(cena)
        sinteticos = [r for r in registros if r.source == "SYNTHETIC"]
        self.assertTrue(sinteticos)                                   # o caminho sintético emite o módulo antigo
        self.assertEqual(len([r for r in registros if r.source == "ARMARIO_V2"]), 2)
        self.assertGreaterEqual(len(registros), 4)                    # duas vezes o mesmo móvel: o defeito do A001

    def test_modulo_oculto_e_marcado_sai_do_corte(self):
        cena, modulo = _cena(convertido=True)
        self.assertFalse([m for m in part_sources.iter_modules(cena) if m.obj is modulo])
        registros = _contar(cena)
        self.assertFalse([r for r in registros if r.source == "SYNTHETIC"], "módulo convertido ainda no corte")
        self.assertEqual(sorted(r.name for r in registros), ['Base inferior', 'Lateral esquerda'])

    def test_contagem_cai_para_as_pecas_do_armario_depois_de_gerar(self):
        antes = _contar(_cena(convertido=False)[0])
        depois = _contar(_cena(convertido=True)[0])
        self.assertGreater(len(antes), len(depois))
        self.assertEqual(len(depois), 2)

    def test_ocultar_sem_marcar_ja_basta(self):
        cena, modulo = _cena()
        modulo._oculto = True
        self.assertFalse([m for m in part_sources.iter_modules(cena) if m.obj is modulo])

    def test_marcar_sem_ocultar_ja_basta(self):
        cena, modulo = _cena()
        modulo.btm_cut_exclude = True
        self.assertFalse([m for m in part_sources.iter_modules(cena) if m.obj is modulo])

    def test_modulo_da_biblioteca_continua_visivel(self):
        cena, modulo = _cena()
        vivo = [m for m in part_sources.iter_modules(cena) if m.obj is modulo]
        self.assertEqual(len(vivo), 1)
        self.assertEqual(vivo[0].library, "BTM")


if __name__ == '__main__':
    unittest.main()
