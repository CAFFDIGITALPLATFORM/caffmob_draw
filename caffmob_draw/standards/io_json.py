"""Exportação e importação de definições `.btmdim.json` (T016; RF-057).

Contrato: `_reversa_forward/001-addon-moveis-planejados/interfaces/dimension-definition.md`.
Python puro na leitura/escrita do arquivo; a criação da definição na cena usa `standards/api.py`.
"""

import json
import os
import tempfile

from ..data.i18n import tr
from ..data import dimension_schema as schema

FORMAT = "caffmob_draw.dimension-standard"
# Arquivos exportados antes da identidade CAFFMob Draw continuam válidos na leitura (BUG-20261006-QAVK).
ACCEPTED_FORMATS = (FORMAT, "blendertomob.dimension-standard")
SCHEMA_VERSION = 1


class StandardFileError(Exception):
    """Arquivo de definição inválido (mensagem pronta para o usuário)."""


def user_folder():
    """Pasta das definições do usuário: extension_path_user(…/standards)."""
    import bpy
    package = __package__.rsplit('.', 1)[0]
    return bpy.utils.extension_path_user(package, path="standards", create=True)


# ----------------------------------------------------------------------------------------------------------------
# Conversão valores ↔ estrutura do arquivo
# ----------------------------------------------------------------------------------------------------------------

ASSEMBLIES = ('LATERAL', 'BASE')


def document_assembly(document):
    """Montagem do arquivo; ausente ou desconhecida (arquivo antigo) → LATERAL (questions.md, pergunta 48)."""
    value = document.get("assembly") if isinstance(document, dict) else None
    return value if value in ASSEMBLIES else 'LATERAL'


def values_to_document(name, uid, market, source, version, updated_at, values, raw_attributes=(), assembly='LATERAL'):
    """Monta o dicionário do arquivo a partir de valores planos (chave → valor em mm ou texto)."""
    lines = {}
    max_measures = {}
    for key, value in values.items():
        param = schema.get_param(key)
        if param is None:
            continue
        if param.group == schema.GROUP_MAX:
            max_measures[param.field] = value
            continue
        line = lines.setdefault(param.line, {'external': {}, 'sheets': {}, 'components': {}})
        if param.group == schema.GROUP_EXTERNAL:
            line['external'][param.field] = value
        else:
            comp = schema.COMPONENTS_BY_CODE[param.component]
            bucket = line['sheets'] if comp.tree == schema.TREE_SHEETS else line['components']
            entry = bucket.setdefault(param.component, {'edges': [0.0, 0.0, 0.0, 0.0]})
            if param.field in schema.EDGE_FIELDS:
                entry['edges'][int(param.field[-1]) - 1] = value
            else:
                entry[param.field] = value
    return {
        "schema": FORMAT,
        "schema_version": SCHEMA_VERSION,
        "uid": uid,
        "name": name,
        "market": market,
        "source": 'USER' if source == 'BUILTIN' else source,
        "version": version,
        "updated_at": updated_at,
        "unit": "mm",
        "assembly": assembly,
        "max_measures": max_measures,
        "lines": lines,
        "raw_attributes": [{"id": r['id'], "value": r['value'], "key": r.get('key', '')} for r in raw_attributes],
    }


def document_to_values(document):
    """Valida o documento e devolve (valores planos, avisos). Levanta StandardFileError se algo for inválido."""
    if not isinstance(document, dict) or document.get("schema") not in ACCEPTED_FORMATS:
        raise StandardFileError(tr("O arquivo não é uma definição de dimensões do CAFFMob Draw."))
    version = document.get("schema_version")
    if not isinstance(version, int) or isinstance(version, bool):
        raise StandardFileError(tr("Versão do formato ausente."))
    if version > SCHEMA_VERSION:
        raise StandardFileError(tr("Arquivo criado por uma versão mais nova da extensão: atualize o CAFFMob Draw."))
    if document.get("unit", "mm") != "mm":
        raise StandardFileError(tr("Unidade do arquivo deve ser mm."))
    values, warnings, errors = {}, [], []

    def put(key, value):
        param = schema.get_param(key)
        if param is None:
            warnings.append(tr("Parâmetro desconhecido ignorado: {}").format(key))
            return
        ok, message = schema.validate(param, value)
        if ok:
            values[key] = value if param.type == 'ENUM' else float(value)
        else:
            errors.append(message)

    def table(value, where):
        """Bloco do arquivo que precisa ser um objeto JSON; forma errada vira erro do arquivo (EC-05)."""
        if value is None:
            return {}
        if not isinstance(value, dict):
            raise StandardFileError(tr("Estrutura do arquivo inválida em {}.").format(where))
        return value

    for fname, value in table(document.get("max_measures"), "max_measures").items():
        put(schema.max_key(fname), value)
    for line, data in table(document.get("lines"), "lines").items():
        if line not in schema.LINE_CODES:
            warnings.append(tr("Linha desconhecida ignorada: {}").format(line))
            continue
        data = table(data, f"lines.{line}")
        for fname, value in table(data.get("external"), f"lines.{line}.external").items():
            put(schema.external_key(line, fname), value)
        for bucket in ("sheets", "components"):
            for comp, entry in table(data.get(bucket), f"lines.{line}.{bucket}").items():
                for fname, value in table(entry, f"lines.{line}.{bucket}.{comp}").items():
                    if fname == 'edges':
                        if value is not None and not isinstance(value, list):
                            raise StandardFileError(tr("Estrutura do arquivo inválida em {}.").format(
                                f"lines.{line}.{bucket}.{comp}.edges"))
                        for side, edge in enumerate(value or [], start=1):
                            put(schema.sheet_key(line, comp, f"edge_{side}"), edge)
                    else:
                        put(schema.sheet_key(line, comp, fname), value)
    if errors:
        raise StandardFileError(tr("Valores fora do domínio:\n{}").format("\n".join(errors)))
    return values, warnings


# ----------------------------------------------------------------------------------------------------------------
# Arquivo
# ----------------------------------------------------------------------------------------------------------------

def write_document(path, document):
    """Escrita atômica, UTF-8 sem BOM."""
    directory = os.path.dirname(os.path.abspath(str(path))) or "."
    fd, tmp = tempfile.mkstemp(dir=directory, suffix=".tmp")
    try:
        with os.fdopen(fd, 'w', encoding='utf-8') as handle:
            json.dump(document, handle, ensure_ascii=False, indent=2, sort_keys=False)
            handle.write("\n")
        os.replace(tmp, str(path))
    except BaseException:
        if os.path.exists(tmp):
            os.unlink(tmp)
        raise


def read_document(path):
    try:
        with open(str(path), encoding='utf-8') as handle:
            return json.load(handle)
    except json.JSONDecodeError as exc:
        raise StandardFileError(tr("JSON inválido (linha {}, coluna {}).").format(exc.lineno, exc.colno)) from None
    except OSError as exc:
        raise StandardFileError(tr("Não foi possível ler o arquivo: {}").format(exc)) from None


# ----------------------------------------------------------------------------------------------------------------
# Integração com as definições da cena (usa bpy por meio de standards/api.py)
# ----------------------------------------------------------------------------------------------------------------

def export_definition(path, definition):
    from . import api
    values = api.definition_values(definition)
    raw = [{"id": r.attr_id, "value": r.value, "key": r.key} for r in definition.raw_attributes]
    document = values_to_document(definition.name, definition.uid, definition.market, definition.source,
                                  definition.version, definition.updated_at, values, raw,
                                  assembly=getattr(definition, 'assembly', 'LATERAL'))
    write_document(path, document)
    return document


def import_definition(scene, path, on_conflict='rename'):
    """Cria a definição a partir do arquivo. `on_conflict`: 'rename' | 'replace'. Devolve (definição, avisos)."""
    from . import api, builtin
    document = read_document(path)
    values, warnings = document_to_values(document)
    data = api.ensure_ready(scene)
    name = str(document.get("name") or "Definição importada")
    existing = api.find_definition(scene, name=name)
    if existing is not None and on_conflict == 'replace' and not existing.builtin:
        api.remove_definition(scene, existing)
    elif existing is not None:
        name = api.unique_name(scene, name)
    definition = data.definitions.add()
    definition.uid = api.new_uid()
    definition.name = name
    definition.market = document.get("market") if document.get("market") in ('BR', 'US') else 'BR'
    definition.source = 'USER'
    definition.version = int(document.get("version") or 1)
    definition.updated_at = str(document.get("updated_at") or builtin.now_iso())
    builtin.fill_from_schema(definition, definition.market)
    definition.assembly = document_assembly(document)
    for key, value in values.items():
        api.set_value(definition, key, value)
    for raw in document.get("raw_attributes") or []:
        item = definition.raw_attributes.add()
        item.attr_id, item.value, item.key = str(raw.get("id", "")), str(raw.get("value", "")), str(raw.get("key", ""))
    return definition, warnings
