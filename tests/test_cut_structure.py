"""Regressão do corte com estrutura de caixa (feature 015, T013): `cutting/part_sources.synthetic_records`.

Módulos falsos (sem `bpy`). O módulo sem `structure_id` tem de gerar os mesmos registros de antes da 015 (fixture
`fixtures/cut_legacy_015.json`, gravada antes da mudança); o módulo com estrutura gera um registro por peça de
`structure.carcass_parts`, com nome e componente do `data-delta.md#4`.
"""

import json
import unittest
from types import SimpleNamespace

import _bootstrap  # noqa: F401


def _import_part_sources():
    """`part_sources` importa `compat`, que importa `bpy`: um `bpy` mínimo só durante a importação, retirado logo
    depois (o `tr()` dos outros testes depende de `bpy` não existir fora do Blender)."""
    import sys
    import types
    if 'bpy' in sys.modules:
        from caffmob_draw.cutting import part_sources
        return part_sources
    sys.modules['bpy'] = types.SimpleNamespace(app=types.SimpleNamespace(version=(5, 2, 0)))
    try:
        from caffmob_draw.cutting import part_sources
    finally:
        del sys.modules['bpy']
    return part_sources


ps = _import_part_sources()

FIXTURE = _bootstrap.FIXTURES / "cut_legacy_015.json"
SHEETS = {"LAT": 15.0, "BAS": 15.0, "FUN_INF": 6.0, "FUN_SUP": 6.0, "FUN_ALT": 6.0, "PRAT": 15.0, "POR": 18.0,
          "SAR": 15.0, "ROD": 15.0, "TAMP": 15.0, "TRA": 15.0, "DIV": 15.0}


def cabinet(structure_id="", **over):
    data = dict(width=0.8, height=0.72, depth=0.55, thickness=0.015, door_swing='DOUBLE', assembly='LATERAL',
                structure_id=structure_id, line='COZ', shelves=0, cabinet_type='BASE')
    for role in ('top', 'bottom', 'back', 'left', 'right'):
        data['has_' + role] = True
        data['thickness_' + role] = 0.0
        data['mode_' + role] = 'KEEP'
    data.update(over)
    return SimpleNamespace(**data)


def module(cab):
    obj = SimpleNamespace(btm_cabinet=cab, children_recursive=[], children=[], users_scene=[SimpleNamespace()])
    return SimpleNamespace(obj=obj, uid="m1", name="Módulo", line="COZ", type='BTM')


def rows(records):
    return [[r.uid, r.name, r.component, round(r.length, 3), round(r.width, 3), round(r.thickness, 3)]
            for r in records]


def legacy_cases():
    return {
        "balcao_2p": rows(ps.synthetic_records(module(cabinet()), SHEETS.get)),
        "sem_tampo": rows(ps.synthetic_records(module(cabinet(has_top=False)), SHEETS.get)),
        "base_passante": rows(ps.synthetic_records(module(cabinet(assembly='BASE', door_swing='LEFT')), SHEETS.get)),
    }


class LegadoTest(unittest.TestCase):
    def test_modulo_sem_estrutura_igual_a_antes(self):
        if not FIXTURE.exists():                       # primeira execução: grava a referência de antes da 015
            FIXTURE.write_text(json.dumps(legacy_cases(), ensure_ascii=False, indent=1), encoding='utf-8')
        self.assertEqual(legacy_cases(), json.loads(FIXTURE.read_text(encoding='utf-8')))


class EstruturaTest(unittest.TestCase):
    def test_inferior_com_sarrafos_sem_base_superior(self):
        cab = cabinet('coz_inferior_divisoria', width=0.5, has_top=False)
        names = [r.name for r in ps.synthetic_records(module(cab), SHEETS.get)]
        self.assertIn("Sarrafo frontal", names)
        self.assertIn("Sarrafo traseiro", names)
        self.assertNotIn("Base superior", names)
        front = next(r for r in ps.synthetic_records(module(cab), SHEETS.get) if r.name == "Sarrafo frontal")
        self.assertEqual((front.component, round(front.length, 3), round(front.width, 3)), ('SAR', 470.0, 100.0))

    def test_registros_iguais_as_pecas_da_estrutura(self):
        from caffmob_draw.cabinet_editor import structure as st
        from caffmob_draw.cabinet_editor import structures_core as sc
        cab = cabinet('coz_superior_divisoria', door_swing='NONE')
        records = ps.synthetic_records(module(cab), SHEETS.get)
        parts, _inner = st.carcass_parts(sc.load(sc.CATALOG).by_id('coz_superior_divisoria'), 800, 720, 550,
                                         {'LEFT': 15, 'RIGHT': 15, 'BOTTOM': 15, 'TOP': 15, 'BACK': 6, 'SAR': 15,
                                          'ROD': 15, 'TAMP': 15, 'TRA': 15}, params=st.default_params())
        self.assertEqual(sorted((p.name, p.component) for p in parts),
                         sorted((r.name, r.component) for r in records if r.name != "Prateleira"))

    def test_estrutura_desconhecida_cai_na_construcao_antiga(self):
        a = rows(ps.synthetic_records(module(cabinet('nao_existe')), SHEETS.get))
        self.assertEqual(a, legacy_cases()["balcao_2p"])


if __name__ == '__main__':
    unittest.main()
