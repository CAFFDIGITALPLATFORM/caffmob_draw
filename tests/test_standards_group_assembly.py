"""Testes da montagem por grupo e das medidas novas no Padrão de Dimensões (feature 015, T012; D-07, D-08).

Contrato: `_reversa_forward/015-construtor-armario-promob/interfaces/padrao-dimensoes-io.md`.
"""

import json
import tempfile
import unittest
from pathlib import Path

import _bootstrap  # noqa: F401
from caffmob_draw.data import dimension_schema as ds
from caffmob_draw.standards import group_assembly as ga
from caffmob_draw.standards import io_json, io_promob

FIXTURE = _bootstrap.FIXTURES / "dimensionexport_me_moveis.xml"
GROUPS = {
    'INFERIOR': {'assembly': 'BASE', 'back_kind': 'REBAIXADO', 'rear_stretcher': 'VERTICAL'},
    'DESPENSEIRO': {'assembly': 'LATERAL', 'back_kind': 'TRAVESSAS', 'rear_stretcher': 'HORIZONTAL'},
}
NEW_VALUES = {
    'COZ.external.stretcher_width': 120.0,
    'COZ.external.shelf_setback': 15.0,
    'COZ.external.hanger_rod_drop': 80.0,
    'DOR.external.hanger_rod_drop': 65.5,
}


def tmpdir():
    return Path(tempfile.mkdtemp())


class GroupAssemblyCoreTest(unittest.TestCase):
    def test_normalize_valido(self):
        clean, warnings = ga.normalize(GROUPS)
        self.assertEqual(clean, GROUPS)
        self.assertEqual(warnings, [])
        self.assertEqual(ga.normalize(json.dumps(GROUPS))[0], GROUPS)

    def test_vazio(self):
        for empty in ("", "  ", {}, None):
            self.assertEqual(ga.normalize(empty), ({}, []))
        self.assertEqual(ga.dumps({}), "")

    def test_grupo_desconhecido_ignorado_com_aviso(self):
        clean, warnings = ga.normalize({'ILHA': {'assembly': 'BASE'}, 'SUPERIOR': {'assembly': 'BASE'}})
        self.assertEqual(clean, {'SUPERIOR': {'assembly': 'BASE'}})
        self.assertEqual(len(warnings), 1)
        self.assertIn('ILHA', warnings[0])

    def test_campo_invalido_cai_no_da_estrutura(self):
        data = {'INFERIOR': {'assembly': 'DIAGONAL', 'back_kind': 'PREGADO'}}
        clean, warnings = ga.normalize(data)
        self.assertEqual(clean, {'INFERIOR': {'back_kind': 'PREGADO'}})
        self.assertEqual(len(warnings), 1)
        self.assertIn('DIAGONAL', warnings[0])
        merged = ga.resolve(data, 'INFERIOR', {'assembly': 'BASE', 'rear_stretcher': 'VERTICAL'})
        self.assertEqual(merged, {'assembly': 'BASE', 'back_kind': 'PREGADO', 'rear_stretcher': 'VERTICAL'})

    def test_resolve_grupo_ausente_vale_a_estrutura(self):
        merged = ga.resolve(GROUPS, 'SUPERIOR', {'back_kind': 'PREGADO'})
        self.assertEqual(merged, {'assembly': 'LATERAL', 'back_kind': 'PREGADO', 'rear_stretcher': 'HORIZONTAL'})
        self.assertEqual(ga.resolve(GROUPS, 'INFERIOR', {'back_kind': 'PREGADO'}), GROUPS['INFERIOR'])

    def test_dumps_estavel(self):
        text = ga.dumps(GROUPS)
        self.assertEqual(json.loads(text), GROUPS)
        self.assertEqual(text, ga.dumps(json.loads(text)))

    def test_xml_ida_e_volta(self):
        pairs = ga.to_xml_attributes(GROUPS)
        self.assertEqual(pairs, [('CAFF_GRUPO_INFERIOR', 'BASE;REBAIXADO;VERTICAL'),
                                 ('CAFF_GRUPO_DESPENSEIRO', 'LATERAL;TRAVESSAS;HORIZONTAL')])
        for attr_id, value in pairs:
            group, fields, warnings = ga.from_xml_attribute(attr_id, value)
            self.assertEqual(fields, GROUPS[group])
            self.assertEqual(warnings, [])

    def test_xml_com_duas_partes_avisa(self):
        group, fields, warnings = ga.from_xml_attribute('CAFF_GRUPO_INFERIOR', 'BASE;PREGADO')
        self.assertEqual(group, 'INFERIOR')
        self.assertEqual(fields, {'assembly': 'BASE', 'back_kind': 'PREGADO'})
        self.assertEqual(len(warnings), 1)

    def test_xml_grupo_desconhecido(self):
        group, fields, warnings = ga.from_xml_attribute('CAFF_GRUPO_ILHA', 'BASE;PREGADO;VERTICAL')
        self.assertIsNone(group)
        self.assertEqual(fields, {})
        self.assertEqual(len(warnings), 1)


class SchemaNewFieldsTest(unittest.TestCase):
    def test_padroes_de_fabrica(self):
        for line in ds.LINE_CODES:
            self.assertEqual(ds.PARAMS[ds.external_key(line, 'stretcher_width')].default_br, 100.0)
            self.assertEqual(ds.PARAMS[ds.external_key(line, 'shelf_setback')].default_br, 20.0)
            self.assertEqual(ds.PARAMS[ds.external_key(line, 'hanger_rod_drop')].default_br, 70.0)


class JsonRoundTripTest(unittest.TestCase):
    def document(self, group_assembly=GROUPS, values=None):
        values = dict(NEW_VALUES if values is None else values)
        return io_json.values_to_document("Teste", "uid-1", 'BR', 'USER', 1, "2026-10-14T00:00:00", values,
                                          assembly='BASE', group_assembly=group_assembly)

    def test_ida_e_volta(self):
        path = tmpdir() / "padrao.btmdim.json"
        io_json.write_document(path, self.document())
        document = io_json.read_document(path)
        self.assertEqual(list(document).index("group_assembly"), list(document).index("assembly") + 1)
        values, warnings = io_json.document_to_values(document)
        self.assertEqual(warnings, [])
        self.assertEqual(values, NEW_VALUES)
        groups, group_warnings = io_json.document_group_assembly(document)
        self.assertEqual(groups, GROUPS)
        self.assertEqual(group_warnings, [])
        self.assertEqual(io_json.document_assembly(document), 'BASE')

    def test_texto_json_aceito_e_vazio_omitido(self):
        self.assertEqual(self.document(group_assembly=ga.dumps(GROUPS))["group_assembly"], GROUPS)
        self.assertNotIn("group_assembly", self.document(group_assembly=""))
        self.assertNotIn("group_assembly", self.document(group_assembly={'ILHA': {'assembly': 'BASE'}}))

    def test_arquivo_antigo_sem_campos_novos(self):
        document = self.document(group_assembly=None, values={'COZ.external.base_height': 700.0})
        self.assertNotIn("group_assembly", document)
        values, _warnings = io_json.document_to_values(document)
        self.assertNotIn('COZ.external.stretcher_width', values)      # fica o padrão de fábrica (fill_from_schema)
        self.assertEqual(io_json.document_group_assembly(document), ({}, []))
        self.assertEqual(ga.dumps(io_json.document_group_assembly(document)[0]), "")

    def test_grupo_invalido_no_arquivo_avisa(self):
        document = self.document()
        document["group_assembly"] = {'ILHA': {}, 'INFERIOR': {'assembly': 'X', 'back_kind': 'PREGADO'}}
        groups, warnings = io_json.document_group_assembly(document)
        self.assertEqual(groups, {'INFERIOR': {'back_kind': 'PREGADO'}})
        self.assertEqual(len(warnings), 2)

    def test_valor_novo_fora_da_faixa_recusado(self):
        document = self.document(values={'COZ.external.stretcher_width': 10.0})
        with self.assertRaises(io_json.StandardFileError):
            io_json.document_to_values(document)


class PromobRoundTripTest(unittest.TestCase):
    def export_and_read(self, group_assembly=GROUPS):
        data = io_promob.to_definition_data(io_promob.read_dimensionexport(FIXTURE))
        values = dict(data['values'], **NEW_VALUES)
        path = tmpdir() / "saida.xml"
        io_promob.write_dimensionexport(path, data['name'], values, data['raw_attributes'], assembly='BASE',
                                        group_assembly=group_assembly)
        return values, io_promob.read_dimensionexport(path)

    def test_atributos_caff_no_fim(self):
        _values, doc = self.export_and_read()
        original = io_promob.read_dimensionexport(FIXTURE).attributes
        self.assertEqual(doc.attributes[:len(original)], original)
        self.assertEqual(doc.attributes[len(original):], [
            ('CAFF_MONTAGEM', 'BASE'),
            ('CAFF_GRUPO_INFERIOR', 'BASE;REBAIXADO;VERTICAL'),
            ('CAFF_GRUPO_DESPENSEIRO', 'LATERAL;TRAVESSAS;HORIZONTAL'),
            ('CAFF_SARRAFO_COZ', '120'), ('CAFF_RECUO_PRAT_COZ', '15'), ('CAFF_CABIDEIRO_COZ', '80'),
            ('CAFF_CABIDEIRO_DOR', '65,5'),
        ])

    def test_ida_e_volta(self):
        values, doc = self.export_and_read()
        data = io_promob.to_definition_data(doc)
        self.assertEqual(data['group_assembly'], GROUPS)
        self.assertEqual(data['assembly'], 'BASE')
        self.assertEqual(data['values'], values)
        self.assertEqual(data['report']['caff_warnings'], [])
        self.assertEqual(len(data['raw_attributes']), 692)           # CAFF_* fora dos crus
        self.assertFalse(any(r['id'].startswith('CAFF_') for r in data['raw_attributes']))
        # Reexportar o que foi lido não duplica os atributos CAFF_*.
        path = tmpdir() / "de_novo.xml"
        io_promob.write_dimensionexport(path, data['name'], data['values'], data['raw_attributes'],
                                        assembly=data['assembly'], group_assembly=data['group_assembly'])
        self.assertEqual(io_promob.read_dimensionexport(path).attributes, doc.attributes)

    def test_crus_com_caff_nao_duplicam(self):
        _values, doc = self.export_and_read()
        raw = [{'id': i, 'value': v, 'key': ''} for i, v in doc.attributes]
        path = tmpdir() / "crus.xml"
        io_promob.write_dimensionexport(path, "x", {}, raw, group_assembly=GROUPS)
        ids = [i for i, _v in io_promob.read_dimensionexport(path).attributes]
        self.assertEqual(ids.count('CAFF_GRUPO_INFERIOR'), 1)
        self.assertNotIn('CAFF_SARRAFO_COZ', ids)
        self.assertNotIn('CAFF_MONTAGEM', ids)

    def test_arquivo_antigo_sem_campos_novos(self):
        data = io_promob.to_definition_data(io_promob.read_dimensionexport(FIXTURE))
        self.assertEqual(data['group_assembly'], {})
        self.assertEqual(ga.dumps(data['group_assembly']), "")
        self.assertNotIn('COZ.external.stretcher_width', data['values'])
        self.assertEqual(data['report']['caff_warnings'], [])

    def test_campos_invalidos_avisam(self):
        doc = io_promob.read_dimensionexport(FIXTURE)
        doc.attributes += [('CAFF_GRUPO_INFERIOR', 'BASE;XX'), ('CAFF_GRUPO_ILHA', 'BASE;PREGADO;VERTICAL'),
                           ('CAFF_SARRAFO_COZ', '5'), ('CAFF_RECUO_PRAT_XYZ', '10'), ('CAFF_CABIDEIRO_DOR', 'abc'),
                           ('CAFF_RECUO_PRAT_BAN', '30,5')]
        data = io_promob.to_definition_data(doc)
        self.assertEqual(data['group_assembly'], {'INFERIOR': {'assembly': 'BASE'}})
        self.assertNotIn('COZ.external.stretcher_width', data['values'])
        self.assertNotIn('DOR.external.hanger_rod_drop', data['values'])
        self.assertEqual(data['values']['BAN.external.shelf_setback'], 30.5)
        # INFERIOR: 2 partes + XX inválido; ILHA desconhecido; SARRAFO fora da faixa; linha XYZ; CABIDEIRO ilegível.
        self.assertEqual(len(data['report']['caff_warnings']), 6)
        self.assertEqual(data['report']['total'], 692)
        self.assertFalse(any(i.startswith('CAFF_') for i in data['report']['unrecognized']))


if __name__ == "__main__":
    unittest.main()
