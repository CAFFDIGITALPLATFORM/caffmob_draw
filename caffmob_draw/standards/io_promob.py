"""Importação e exportação do `DIMENSIONEXPORT` do Promob (T017; RF-058).

Contrato: `_reversa_forward/001-addon-moveis-planejados/interfaces/promob-dimensionexport.md`.

Python puro (sem `bpy`): lê/escreve o XML e converte para um dicionário de definição
(`values` por chave do esquema + `raw_attributes` na ordem original). A gravação nas PropertyGroups fica em
`operators/ops_standards.py`, via `standards/api.py`.
"""

import os
import tempfile
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field

from ..data.i18n import tr
from ..data import dimension_schema as schema
from . import group_assembly as ga


class PromobFormatError(Exception):
    """Arquivo que não é um DIMENSIONEXPORT válido (mensagem pronta para o usuário)."""


@dataclass
class PromobDocument:
    name: str
    version: str = "-1"
    is_system: str = "False"
    changed: str = "True"
    attributes: list = field(default_factory=list)   # [(id, valor original)], na ordem do arquivo


def read_dimensionexport(path):
    """Lê um arquivo `.xml`/`.dimensionExport` do Promob."""
    try:
        tree = ET.parse(str(path))
    except ET.ParseError as exc:
        line, column = getattr(exc, 'position', (0, 0))
        raise PromobFormatError(tr("Arquivo XML inválido (linha {}, coluna {}).").format(line, column)) from None
    except OSError as exc:
        raise PromobFormatError(tr("Não foi possível ler o arquivo: {}").format(exc)) from None
    root = tree.getroot()
    if root.tag != 'DIMENSIONEXPORT':
        raise PromobFormatError(tr("Não é uma configuração de dimensões do Promob (raiz <{}>).").format(root.tag))
    definition = root.find('DEFINITION')
    name = " ".join((definition.get('DESCRIPTION', '') if definition is not None else '').split())
    doc = PromobDocument(
        name=name or "Configuração importada do Promob",
        version=root.get('VERSION', '-1'),
        is_system=definition.get('ISSYSTEM', 'False') if definition is not None else 'False',
        changed=definition.get('CHANGED', 'True') if definition is not None else 'True',
    )
    for attr in root.iter('ATTRIBUTE'):
        attr_id = attr.get('ID')
        if attr_id:
            doc.attributes.append((attr_id, attr.get('VALUE', '')))
    if not doc.attributes:
        raise PromobFormatError(tr("O arquivo não contém atributos de dimensão."))
    return doc


ASSEMBLY_ID = 'CAFF_MONTAGEM'          # feature 012 (D-27): montagem do CAFFMob, sem equivalente no Promob
ASSEMBLY_VALUES = ('LATERAL', 'BASE')
# Feature 015 (D-07): medidas das estruturas de caixa por linha, sem equivalente no Promob (`<PREFIXO><LINHA>`).
EXTRA_PREFIXES = (
    ('CAFF_SARRAFO_', 'stretcher_width'),
    ('CAFF_RECUO_PRAT_', 'shelf_setback'),
    ('CAFF_CABIDEIRO_', 'hanger_rod_drop'),
)


def _is_caff_id(attr_id):
    """IDs que o CAFFMob acrescenta no fim do arquivo: lidos à parte e nunca reexportados como crus."""
    return (attr_id == ASSEMBLY_ID or attr_id.startswith(ga.XML_PREFIX)
            or any(attr_id.startswith(prefix) for prefix, _field in EXTRA_PREFIXES))


def _read_extra(attr_id, text, values, warnings):
    """Lê um `CAFF_SARRAFO_<LINHA>`/`CAFF_RECUO_PRAT_<LINHA>`/`CAFF_CABIDEIRO_<LINHA>` para `values`."""
    for prefix, field_name in EXTRA_PREFIXES:
        if not attr_id.startswith(prefix):
            continue
        line = attr_id[len(prefix):]
        if line not in schema.LINE_CODES:
            warnings.append(tr("Linha desconhecida ignorada: {}").format(attr_id))
            return
        key = schema.external_key(line, field_name)
        try:
            value = _parse_number(text or "")
        except ValueError:
            value = None
        if value is not None and schema.validate(schema.PARAMS[key], value)[0]:
            values[key] = value
        else:
            warnings.append(tr("Valores inválidos ignorados: {}").format(f"{attr_id}={text}"))
        return


def _parse_number(text):
    return float(text.strip().replace(',', '.'))


def to_definition_data(doc):
    """Converte o documento em dados de definição.

    Retorna dict com `name`, `values` (chave → valor em mm ou texto), `raw_attributes`
    (lista de {id, value, key} na ordem original; `key` vazio = não reconhecido), `assembly`, `group_assembly`
    ({grupo: {campo: valor}}, feature 015) e `report` (`total`, `mapped`, `unrecognized`, `invalid`, `duplicates`,
    `confirmed_without_equivalent`, `assembly_warning`, `caff_warnings`).
    Os atributos `CAFF_*` ficam fora dos crus e da contagem: são regravados no fim pela exportação.
    """
    values = {}
    extras = {}
    raw = []
    assembly = 'LATERAL'
    groups = {}
    attributes = []
    report = {'total': 0, 'mapped': 0, 'unrecognized': [], 'invalid': [], 'duplicates': [],
              'confirmed_without_equivalent': [], 'assembly_warning': None, 'caff_warnings': []}
    for attr_id, text in doc.attributes:
        if not _is_caff_id(attr_id):
            attributes.append((attr_id, text))
        elif attr_id == ASSEMBLY_ID:
            value = (text or "").strip().upper()
            if value in ASSEMBLY_VALUES:
                assembly = value
            else:
                assembly = 'LATERAL'
                report['assembly_warning'] = tr("Montagem desconhecida: {}; usada lateral passante").format(text)
        elif attr_id.startswith(ga.XML_PREFIX):
            group, fields, warnings = ga.from_xml_attribute(attr_id, text)
            report['caff_warnings'].extend(warnings)
            if group and fields:
                groups[group] = fields
            elif group:
                groups.pop(group, None)
        else:
            _read_extra(attr_id, text, extras, report['caff_warnings'])
    report['total'] = len(attributes)
    seen = {}
    for attr_id, text in attributes:
        if attr_id in seen:
            report['duplicates'].append(attr_id)
        seen[attr_id] = text

    for attr_id, text in attributes:
        key = schema.PROMOB_INDEX.get(attr_id, "")
        if key:
            param = schema.PARAMS[key]
            current = seen[attr_id]   # ID duplicado: vale o último
            try:
                value = current.strip() if param.type == 'ENUM' else _parse_number(current)
            except ValueError:
                value = None
            ok = value is not None and schema.validate(param, value)[0]
            if ok:
                values[key] = value
                report['mapped'] += 1
            else:
                report['invalid'].append(attr_id)
                report['unrecognized'].append(attr_id)
                key = ""
        else:
            report['unrecognized'].append(attr_id)
            if schema.parse_promob_id(attr_id):
                report['confirmed_without_equivalent'].append(attr_id)
        raw.append({'id': attr_id, 'value': text, 'key': key})
    values.update(extras)
    return {'name': doc.name, 'values': values, 'raw_attributes': raw, 'report': report, 'assembly': assembly,
            'group_assembly': groups}


def _format_number(value):
    text = f"{float(value):.4f}".rstrip('0').rstrip('.')
    return (text or '0').replace('.', ',')


def build_attributes(values, raw_attributes):
    """Lista (id, valor) para exportação: atributos mapeados recebem o valor atual; os demais, o original."""
    pairs = []
    for raw in raw_attributes:
        key = raw.get('key') or ""
        original = raw.get('value', '')
        if key and key in values:
            param = schema.PARAMS[key]
            current = values[key]
            if param.type == 'ENUM':
                text = str(current)
            else:
                try:
                    same = abs(_parse_number(original) - float(current)) < 1e-6
                except ValueError:
                    same = False
                text = original if same else _format_number(current)
            pairs.append((raw['id'], text))
        else:
            pairs.append((raw['id'], original))
    return pairs


def caff_attributes(values, assembly=None, group_assembly=None):
    """[(ID, VALOR)] do CAFFMob para o fim do arquivo: montagem, montagem por grupo e medidas novas por linha."""
    pairs = []
    if assembly in ASSEMBLY_VALUES:
        pairs.append((ASSEMBLY_ID, assembly))
    pairs.extend(ga.to_xml_attributes(group_assembly or {}))
    for line in schema.LINE_CODES:
        for prefix, field_name in EXTRA_PREFIXES:
            key = schema.external_key(line, field_name)
            if key in values:
                pairs.append((prefix + line, _format_number(values[key])))
    return pairs


def write_dimensionexport(path, name, values, raw_attributes, assembly=None, group_assembly=None):
    """Grava o DIMENSIONEXPORT (escrita atômica). `raw_attributes` define a ordem e os IDs exportados.

    `assembly` (feature 012): quando dado, `CAFF_MONTAGEM` vai no fim; o Promob ignora o ID desconhecido.
    Depois dele (feature 015): `CAFF_GRUPO_*` de `group_assembly` e, por linha, `CAFF_SARRAFO_<LINHA>`,
    `CAFF_RECUO_PRAT_<LINHA>` e `CAFF_CABIDEIRO_<LINHA>` com os valores presentes em `values`.

    Para uma definição criada no BlenderToMob (sem arquivo de origem), use `attributes_from_values`.
    """
    root = ET.Element('DIMENSIONEXPORT', VERSION="-1")
    definition = ET.SubElement(root, 'DEFINITION', DESCRIPTION=name, ISSYSTEM="False", CHANGED="True")
    attributes = ET.SubElement(definition, 'ATTRIBUTES')
    for attr_id, text in build_attributes(values, raw_attributes):
        if not _is_caff_id(attr_id):
            ET.SubElement(attributes, 'ATTRIBUTE', ID=attr_id, VALUE=text)
    for attr_id, text in caff_attributes(values, assembly, group_assembly):
        ET.SubElement(attributes, 'ATTRIBUTE', ID=attr_id, VALUE=text)
    ET.indent(root, space="  ")
    data = ET.tostring(root, encoding='unicode')
    directory = os.path.dirname(os.path.abspath(str(path))) or "."
    fd, tmp = tempfile.mkstemp(dir=directory, suffix=".tmp")
    try:
        with os.fdopen(fd, 'w', encoding='utf-8') as handle:
            handle.write('<?xml version="1.0" encoding="utf-8"?>\n')
            handle.write(data)
        os.replace(tmp, str(path))
    except BaseException:
        if os.path.exists(tmp):
            os.unlink(tmp)
        raise


def attributes_from_values(values):
    """`raw_attributes` sintéticos (um por código Promob conhecido) para exportar uma definição sem origem Promob."""
    raw = []
    for key, param in schema.PARAMS.items():
        if key not in values:
            continue
        for code in param.promob_codes:
            raw.append({'id': code, 'value': '', 'key': key})
    return raw
