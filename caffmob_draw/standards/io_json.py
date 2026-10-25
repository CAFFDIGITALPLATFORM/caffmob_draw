"""Exportação e importação de definições `.btmdim.json` (T016; RF-057).

Contrato: `_reversa_forward/001-addon-moveis-planejados/interfaces/dimension-definition.md`.
Python puro na leitura/escrita do arquivo; a criação da definição na cena usa `standards/api.py`.
"""

import json
import os
import tempfile

from ..data.i18n import tr
from ..data import dimension_schema as schema
from . import group_assembly as ga

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


def document_group_assembly(document):
    """(montagem por grupo normalizada, avisos) do arquivo; ausente (arquivo de antes da 015) → ({}, [])."""
    value = document.get("group_assembly") if isinstance(document, dict) else None
    return ga.normalize(value) if value else ({}, [])


def values_to_document(name, uid, market, source, version, updated_at, values, raw_attributes=(), assembly='LATERAL',
                       group_assembly=None):
    """Monta o dicionário do arquivo a partir de valores planos (chave → valor em mm ou texto).

    `group_assembly` (feature 015, D-08): dict ou texto JSON; vai ao lado de `assembly`, omitido quando vazio.
    """
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
    document = {
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
    groups, _warnings = ga.normalize(group_assembly or {})
    if groups:
        ordered = {}
        for k, v in document.items():
            ordered[k] = v
            if k == "assembly":
                ordered["group_assembly"] = groups
        document = ordered
    return document


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
# Pacote com todas as definições (feature 067, D-28): `.btmdim-pack.json`
# ----------------------------------------------------------------------------------------------------------------

PACK_FORMAT = "caffmob_draw.dimension-standards-pack"
PACK_SCHEMA_VERSION = 1
PACK_EXTENSION = ".btmdim-pack.json"


def pack_documents(documents, exported_at):
    """Pacote de exportação: a lista dos mesmos documentos de um `.btmdim.json`."""
    return {
        "schema": PACK_FORMAT,
        "schema_version": PACK_SCHEMA_VERSION,
        "exported_at": exported_at,
        "definitions": list(documents),
    }


def unpack_documents(document):
    """Documentos de um pacote ou de um `.btmdim.json` solto, cada um validado por `document_to_values`."""
    if isinstance(document, dict) and document.get("schema") == PACK_FORMAT:
        version = document.get("schema_version")
        if not isinstance(version, int) or isinstance(version, bool):
            raise StandardFileError(tr("Versão do formato ausente."))
        if version > PACK_SCHEMA_VERSION:
            raise StandardFileError(tr("Arquivo criado por uma versão mais nova da extensão: atualize o CAFFMob Draw."))
        items = document.get("definitions")
        if not isinstance(items, list):
            raise StandardFileError(tr("Estrutura do arquivo inválida em {}.").format("definitions"))
    else:
        items = [document]
    for item in items:
        document_to_values(item)
    return items


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

def definition_document(definition):
    """O documento `.btmdim.json` de uma definição da cena (também o que o banco local guarda, feature 067)."""
    from . import api
    values = api.definition_values(definition)
    raw = [{"id": r.attr_id, "value": r.value, "key": r.key} for r in definition.raw_attributes]
    return values_to_document(definition.name, definition.uid, definition.market, definition.source,
                              definition.version, definition.updated_at, values, raw,
                              assembly=getattr(definition, 'assembly', 'LATERAL'),
                              group_assembly=getattr(definition, 'group_assembly', ""))


def export_definition(path, definition):
    document = definition_document(definition)
    write_document(path, document)
    return document


def fill_definition(definition, document, values, groups):
    """Preenche uma definição nova da cena com o documento já validado (`document_to_values`)."""
    from . import api, builtin
    definition.market = document.get("market") if document.get("market") in ('BR', 'US') else 'BR'
    definition.source = 'USER'
    definition.version = int(document.get("version") or 1)
    definition.updated_at = str(document.get("updated_at") or builtin.now_iso())
    builtin.fill_from_schema(definition, definition.market)
    definition.assembly = document_assembly(document)
    definition.group_assembly = ga.dumps(groups)                # feature 015 (D-08)
    for key, value in values.items():
        api.set_value(definition, key, value)
    for raw in document.get("raw_attributes") or []:
        item = definition.raw_attributes.add()
        item.attr_id, item.value, item.key = str(raw.get("id", "")), str(raw.get("value", "")), str(raw.get("key", ""))


def definition_from_document(scene, document):
    """Cria na cena a definição do documento com o MESMO uid (vinda do banco local, feature 067 D-27)."""
    from . import api
    values, _warnings = document_to_values(document)
    groups, _group_warnings = document_group_assembly(document)
    data = api.ensure_ready(scene)
    definition = data.definitions.add()
    definition.uid = str(document["uid"])
    name = str(document.get("name") or "Definição")
    definition.name = name if api.find_definition(scene, name=name) in (None, definition) else api.unique_name(scene, name)
    fill_definition(definition, document, values, groups)
    return definition


def import_definition(scene, path, on_conflict='rename'):
    """Cria a definição a partir do arquivo. `on_conflict`: 'rename' | 'replace'. Devolve (definição, avisos)."""
    from . import api
    document = read_document(path)
    values, warnings = document_to_values(document)
    groups, group_warnings = document_group_assembly(document)
    warnings = warnings + group_warnings
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
    fill_definition(definition, document, values, groups)
    return definition, warnings
