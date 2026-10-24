"""Regras estáticas da 067 (RF-001, RNF, D-35): leitura só de snapshot, sem nome de objeto como regra, campos
virtuais não animáveis e ensaios sem o banco real do Padrão de Dimensões.

Cada regra tem um controle positivo: o detector precisa acusar um trecho que a viola, senão o teste não prova nada.
"""
import ast
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / 'caffmob_draw'
TESTS = ROOT / 'tests'
TARGET = PACKAGE / 'target'
OBJECT_PROPERTIES = PACKAGE / 'ui' / 'object_properties.py'
SELF = Path(__file__).resolve()

_ACCESSOR_NAMES = {'get', 'set', 'set_'}
_ACCESSOR_PREFIXES = ('draw', 'get_', 'set_', '_get_', '_set_')
_ACCESSOR_SUFFIXES = ('_getter', '_setter')
_FIXTURE_NAME = re.compile(r'^(Placa\.|box$|Box$)')
_ABSOLUTE_PATH = re.compile(r'^(/home/|/root/|/tmp/claude|/opt/|[A-Za-z]:\\)')


def _target_sources():
    return sorted(TARGET.rglob('*.py'))


def _tests_067():
    names = ('test_067_*.py', 'blender_067_*.py', '_fixtures_067.py', 'test_target_*.py', 'test_standards_store*.py')
    found = {p for pattern in names for p in TESTS.glob(pattern)}
    return sorted(p for p in found if p.resolve() != SELF)


def _is_accessor(name):
    return name in _ACCESSOR_NAMES or name.startswith(_ACCESSOR_PREFIXES) or name.endswith(_ACCESSOR_SUFFIXES)


def active_object_in_accessors(source):
    """Linhas de getter, setter ou draw que leem `active_object` (atributo ou `getattr(..., 'active_object')`)."""
    hits = []
    for node in ast.walk(ast.parse(source)):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) or not _is_accessor(node.name):
            continue
        for inner in ast.walk(node):
            if isinstance(inner, ast.Attribute) and inner.attr == 'active_object':
                hits.append((node.name, inner.lineno))
            elif isinstance(inner, ast.Constant) and inner.value == 'active_object':
                hits.append((node.name, inner.lineno))
    return sorted(set(hits), key=lambda h: h[1])


def fixture_names_and_paths(source):
    hits = []
    for node in ast.walk(ast.parse(source)):
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            if _FIXTURE_NAME.match(node.value) or _ABSOLUTE_PATH.match(node.value):
                hits.append((node.value, node.lineno))
    return hits


def _options_of(call):
    for keyword in call.keywords:
        if keyword.arg == 'options':
            return keyword.value
    return None


def _is_props_call(node):
    return (isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
            and isinstance(node.func.value, ast.Attribute) and node.func.value.attr == 'props')


def animatable_fields(source, class_name):
    """Campos da classe que podem ser animados: `options` ausente (o padrão do Blender inclui ANIMATABLE) ou com
    'ANIMATABLE'. Segue uma chamada a uma função auxiliar do mesmo módulo até o `bpy.props.*` que ela devolve."""
    tree = ast.parse(source)
    helpers = {n.name: n for n in tree.body if isinstance(n, ast.FunctionDef)}

    def props_call(value):
        if _is_props_call(value):
            return value
        if isinstance(value, ast.Call) and isinstance(value.func, ast.Name) and value.func.id in helpers:
            for inner in ast.walk(helpers[value.func.id]):
                if isinstance(inner, ast.Return) and _is_props_call(inner.value):
                    return inner.value
        return None

    bad = []
    for node in tree.body:
        if not (isinstance(node, ast.ClassDef) and node.name == class_name):
            continue
        for item in node.body:
            if not isinstance(item, ast.AnnAssign):
                continue
            call = props_call(item.annotation)
            if call is None:
                continue
            options = _options_of(call)
            if options is None or any(isinstance(c, ast.Constant) and c.value == 'ANIMATABLE' for c in ast.walk(options)):
                bad.append(item.target.id)
    return bad


def opens_real_standards_db(source):
    """O ensaio toca o banco do Padrão de Dimensões sem `banco_temporario()` nem `CAFFMOB_DRAW_STANDARDS_DB`."""
    touches = ('padroes.sqlite3' in source or re.search(r'standards(\.|\s+import\s+)store\b', source) is not None)
    guarded = 'banco_temporario' in source or 'CAFFMOB_DRAW_STANDARDS_DB' in source
    return touches and not guarded


class ControlesPositivos(unittest.TestCase):
    def test_caminhos_existem(self):
        self.assertTrue((TARGET / '__init__.py').is_file())
        self.assertTrue(OBJECT_PROPERTIES.is_file())

    def test_detectores_acusam_violacao(self):
        self.assertEqual(active_object_in_accessors(
            "def _g(f):\n    def get(s):\n        return bpy.context.active_object\n    return get\n"), [('get', 3)])
        self.assertTrue(active_object_in_accessors(
            "def draw(self, context):\n    getattr(context, 'active_object', None)\n"))
        self.assertEqual(active_object_in_accessors("def _info():\n    return bpy.context.active_object\n"), [])
        self.assertEqual(len(fixture_names_and_paths("a = 'Placa.001'\nb = '/home/x'\nc = 'box'\n")), 3)
        self.assertEqual(animatable_fields(
            "def h():\n    return bpy.props.FloatProperty(options={'ANIMATABLE'})\n"
            "class P:\n    a: h()\n    b: bpy.props.IntProperty()\n    c: bpy.props.IntProperty(options=set())\n", 'P'),
            ['a', 'b'])
        self.assertTrue(opens_real_standards_db("from caffmob_draw.standards import store\nstore.open()\n"))
        self.assertFalse(opens_real_standards_db("from caffmob_draw.standards import store\nwith banco_temporario():\n"))


class RegrasDoPacoteTarget(unittest.TestCase):
    def test_sem_active_object_em_getter_setter_ou_draw(self):
        for path in _target_sources():
            with self.subTest(arquivo=path.relative_to(ROOT)):
                self.assertEqual(active_object_in_accessors(path.read_text(encoding='utf-8')), [])

    def test_sem_nome_de_fixture_nem_caminho_absoluto(self):
        for path in _target_sources() + [OBJECT_PROPERTIES] + _tests_067():
            with self.subTest(arquivo=path.relative_to(ROOT)):
                self.assertEqual(fixture_names_and_paths(path.read_text(encoding='utf-8')), [])

    def test_campos_de_btm_selection_nao_animaveis(self):
        source = OBJECT_PROPERTIES.read_text(encoding='utf-8')
        self.assertIn('class BTM_PG_SelectionEdit', source)
        self.assertEqual(animatable_fields(source, 'BTM_PG_SelectionEdit'), [])

    def test_ensaios_sem_o_banco_real(self):
        for path in _tests_067():
            with self.subTest(arquivo=path.relative_to(ROOT)):
                self.assertFalse(opens_real_standards_db(path.read_text(encoding='utf-8')))


class RegraDaJanelaDePropriedades(unittest.TestCase):
    # Os getters de cota e o draw do painel ainda leem o objeto ativo. A T087 (draw do ViewModel) os tira daí;
    # quando isso acontecer, o "sucesso inesperado" reprova a suíte e obriga a retirar esta marca.
    @unittest.expectedFailure
    def test_sem_active_object_em_getter_setter_ou_draw(self):
        self.assertEqual(active_object_in_accessors(OBJECT_PROPERTIES.read_text(encoding='utf-8')), [])


if __name__ == '__main__':
    unittest.main()
