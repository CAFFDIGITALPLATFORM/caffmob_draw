"""Manifesto do módulo salvo pelo usuário (feature 003, T002; D-10). Python puro, sem `bpy`.

Contrato: `_reversa_forward/003-modulos-agregados-reposicionar/interfaces/user-module-file.md`; a 1.1.0 (feature 006)
acrescenta `structure` e `divisions`, opcionais: `_reversa_forward/006-editor-armario-abas/interfaces/user-module-file.md`.
"""

import json
import math
import re

from ..data.i18n import tr
from . import spec as spec_mod

FORMAT = "caffmob_draw.user-module"
SCHEMA_VERSION = "1.1.0"
SUPPORTED_MAJOR = 1
LIBRARIES = ('FRAMELESS', 'FACE_FRAME', 'CLOSETS', 'BTM', 'AUTHORED')
ROLES = ('TOP', 'BOTTOM', 'BACK', 'LEFT', 'RIGHT')
MODES = ('KEEP', 'EXTEND', 'SHRINK')
ORIENTATIONS = ('VERTICAL', 'HORIZONTAL')
_SPACE = re.compile(r'^s\d+(\.[ab])*$')
_FORBIDDEN = re.compile(r'[<>:"/\\|?*\x00-\x1f]')


def file_stem(name):
    """Nome de arquivo seguro em Windows/Linux; o nome original fica no manifesto."""
    stem = _FORBIDDEN.sub("_", str(name)).strip().rstrip(".")
    return stem or "modulo"


def build(name, category, library, root_object, spec, *, created="", addon_version="", dimensions_mm=None,
          styles=None, materials=(), pulls=(), structure=None, divisions=None, authored=None):
    data = {
        "format": FORMAT,
        "schema_version": "1.2.0" if library == "AUTHORED" else SCHEMA_VERSION,
        "name": str(name),
        "category": str(category),
        "library": str(library),
        "root_object": str(root_object),
        "created": str(created),
        "addon_version": str(addon_version),
        "dimensions_mm": dict(dimensions_mm or {}),
        "styles": dict(styles or {}),
        "materials": sorted({str(m) for m in materials if m}),
        "pulls": sorted({str(p) for p in pulls if p and p != spec_mod.NO_PULL}),
        "spec": spec_mod.to_dict(spec),
    }
    if library == "AUTHORED":
        data["authored"] = authored
        return data
    if structure:
        data["structure"] = {role: {"removed": bool(v.get("removed")), "mode": v.get("mode") or 'KEEP',
                                    "thickness_mm": _mm(v.get("thickness")), "material": str(v.get("material") or "")}
                             for role, v in sorted(structure.items())}
    if divisions:
        data["divisions"] = [{"uid": str(d.get("uid", "")), "space": d["space"], "orientation": d["orientation"],
                              "offset_mm": _mm(d.get("offset")), "use_front": bool(d.get("use_front")),
                              "front_mm": _mm(d.get("front")), "use_back": bool(d.get("use_back")),
                              "back_mm": _mm(d.get("back")), "thickness_mm": _mm(d.get("thickness")),
                              "material": str(d.get("material") or "")} for d in divisions]
    return data


def _mm(value):
    return round(float(value or 0.0) * 1000.0, 3)


def _m(value):
    return float(value or 0.0) / 1000.0


def structure_of(data):
    """Estrutura do manifesto em metros: {papel: {removed, mode, thickness, material}} (vazio na 1.0.0)."""
    return {role: {"removed": bool(v.get("removed")), "mode": v.get("mode") or 'KEEP',
                   "thickness": _m(v.get("thickness_mm")), "material": str(v.get("material") or "")}
            for role, v in (data.get("structure") or {}).items()}


def divisions_of(data):
    """Divisões do manifesto em metros (vazio na 1.0.0)."""
    return [{"uid": str(d.get("uid", "")), "space": d["space"], "orientation": d["orientation"],
             "offset": _m(d.get("offset_mm")), "use_front": bool(d.get("use_front")), "front": _m(d.get("front_mm")),
             "use_back": bool(d.get("use_back")), "back": _m(d.get("back_mm")),
             "thickness": _m(d.get("thickness_mm")), "material": str(d.get("material") or "")}
            for d in (data.get("divisions") or [])]


def _negative(entry, keys):
    return any(float(entry.get(k) or 0.0) < 0.0 for k in keys)


def _validate_structure(data):
    errors = []
    for role, entry in (data.get("structure") or {}).items():
        if role not in ROLES:
            errors.append(tr("componente desconhecido: {!r}").format(role))
            continue
        if entry.get("mode", 'KEEP') not in MODES:
            errors.append(tr("modo desconhecido: {!r}").format(entry.get("mode")))
        if _negative(entry, ("thickness_mm",)):
            errors.append(tr("medida negativa em {}").format(role))
    for entry in data.get("divisions") or []:
        if not _SPACE.match(str(entry.get("space", ""))):
            errors.append(tr("vão mal formado: {!r}").format(entry.get("space")))
        if entry.get("orientation") not in ORIENTATIONS:
            errors.append(tr("orientação desconhecida: {!r}").format(entry.get("orientation")))
        if _negative(entry, ("offset_mm", "front_mm", "back_mm", "thickness_mm")):
            errors.append(tr("medida negativa numa divisão"))
    return errors


def _major(version):
    try:
        return int(str(version).split(".")[0])
    except ValueError:
        return None


def validate(data):
    errors = []
    if not isinstance(data, dict):
        return [tr("o manifesto não é um objeto JSON")]
    if data.get("format") != FORMAT:
        errors.append(tr("formato desconhecido: {!r}").format(data.get('format')))
    major = _major(data.get("schema_version", ""))
    if major is None or major > SUPPORTED_MAJOR:
        errors.append(tr("schema_version {!r} não suportada (máximo {}.x)").format(data.get('schema_version'), SUPPORTED_MAJOR))
    if data.get("library") not in LIBRARIES:
        errors.append(tr("biblioteca desconhecida: {!r}").format(data.get('library')))
    if not str(data.get("name", "")).strip():
        errors.append(tr("nome vazio"))
    if not str(data.get("root_object", "")).strip():
        errors.append(tr("objeto raiz não informado"))
    if not errors:
        if data.get("library") == "AUTHORED":
            errors += _validate_authored(data)
        else:
            errors += spec_mod.validate(spec_mod.from_dict(data.get("spec")))
            errors += _validate_structure(data)
    return errors


def dumps(data):
    return json.dumps(data, ensure_ascii=False, indent=2, sort_keys=False) + "\n"


def loads(text):
    """Lê e valida; devolve (dados, spec, erros). Com erro, `spec` é None."""
    try:
        data = json.loads(text)
    except ValueError as exc:
        return None, None, [tr("JSON inválido: {}").format(exc)]
    errors = validate(data)
    if errors:
        return data, None, errors
    current = (spec_mod.Spec(library="AUTHORED") if data.get("library") == "AUTHORED"
               else spec_mod.from_dict(data.get("spec")))
    return data, current, []


def _validate_authored(data):
    """Valida o pacote inteiro, inclusive dependências, sem depender do Blender."""
    from ..stable_id import is_uid
    errors = []

    def fail(path, reason):
        errors.append(tr("Autoral inválido em {}: {}").format(path, reason))

    def positive(value):
        return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value) and value > 0

    block = data.get('authored')
    if data.get('schema_version') != '1.2.0':
        fail('schema_version', 'esperado 1.2.0')
    if 'structure' in data or 'divisions' in data:
        fail('authored', 'estrutura e divisões nativas não se aplicam')
    if not isinstance(block, dict):
        fail('authored', 'bloco ausente')
        return errors
    if block.get('front_axis') not in ('-X', '+X', '-Y', '+Y'):
        fail('authored.front_axis', 'eixo desconhecido')
    size = block.get('size_local_mm')
    if not isinstance(size, list) or len(size) != 3 or not all(positive(v) for v in size):
        fail('authored.size_local_mm', 'medidas devem ser positivas e finitas')
    version = block.get('asset_version')
    if not isinstance(version, int) or isinstance(version, bool) or version < 1:
        fail('authored.asset_version', 'versão deve ser inteira positiva')
    if block.get('external_refs') != []:
        fail('authored.external_refs', 'referência externa não permitida')
    members, leaves = block.get('members'), block.get('leaves')
    if not isinstance(members, list) or not isinstance(leaves, list):
        fail('authored', 'members e leaves devem ser listas')
        return errors
    seen = set()

    def identity(uid, path):
        if not is_uid(uid):
            fail(path, 'uid inválido')
        elif uid in seen:
            fail(path, 'uid repetido')
        seen.add(str(uid))

    identity(block.get('uid'), 'authored.uid')
    roles = ('CARCASS', 'SHELF', 'BACK', 'LEAF_PART', 'FIXED_FRONT', 'HARDWARE', 'LED', 'LIGHT', 'CUTTER', 'FILLER')
    rules = ('FIXED', 'ANCHORED', 'FIT_BETWEEN', 'DISTRIBUTE')
    graph = {}
    for i, member in enumerate(members):
        path = 'authored.members[{}]'.format(i)
        if not isinstance(member, dict):
            fail(path, 'membro deve ser objeto')
            continue
        uid = member.get('uid')
        identity(uid, path + '.uid')
        if member.get('role') not in roles:
            fail(path + '.role', 'papel desconhecido')
        if member.get('rule') not in rules:
            fail(path + '.rule', 'regra desconhecida')
        refs = member.get('refs')
        if not isinstance(refs, list) or any(not isinstance(ref, str) for ref in refs):
            fail(path + '.refs', 'refs deve ser lista de uids')
            refs = []
        graph[str(uid)] = refs
        params = member.get('params')
        if not isinstance(params, dict) or params.get('axis') not in ('X', 'Y', 'Z'):
            fail(path + '.params', 'eixo desconhecido')
        elif (not isinstance(params.get('offset_mm', 0), (float, int))
              or not math.isfinite(params.get('offset_mm', 0))):
            fail(path + '.params.offset_mm', 'medida inválida')
        elif not isinstance(params.get('count', 1), int) or params.get('count', 1) < 1:
            fail(path + '.params.count', 'quantidade inválida')
    # A folha é uma vista do membro móvel: compartilha o uid dele, sem criar outra entidade.
    leaf_ids = set()
    for i, entry in enumerate(leaves):
        path = 'authored.leaves[{}]'.format(i)
        if not isinstance(entry, dict):
            fail(path, 'folha deve ser objeto')
            continue
        uid = entry.get('uid')
        if not isinstance(uid, str) or uid not in graph or uid in leaf_ids:
            fail(path + '.uid', 'uid ausente ou repetido')
        leaf_ids.add(str(uid))
        for key, values in (('construction', ('PANEL', 'GLASS', 'GLASS_FRAMED')),
                            ('motion', ('SWING', 'FLIP', 'SLIDE')), ('hinge', ('LEFT', 'RIGHT', 'TOP', 'BOTTOM')),
                            ('sign', ('OUT', 'IN'))):
            if entry.get(key) not in values:
                fail(path + '.' + key, 'valor desconhecido')
        if entry.get('motion') == 'SLIDE':
            if not positive(entry.get('travel_mm')):
                fail(path + '.travel_mm', 'curso deve ser positivo')
        elif not positive(entry.get('max_angle')) or entry['max_angle'] > 180:
            fail(path + '.max_angle', 'ângulo inválido')
        refs = entry.get('members')
        if not isinstance(refs, list) or not refs or any(not isinstance(ref, str) or ref not in graph for ref in refs):
            fail(path + '.members', 'membro ausente')
        if not isinstance(entry.get('pivot_uid'), str) or entry.get('pivot_uid') not in graph:
            fail(path + '.pivot_uid', 'pivô ausente')
        matrix = entry.get('rest_matrix_parent')
        if (not isinstance(matrix, list) or len(matrix) != 4 or any(
                not isinstance(row, list) or len(row) != 4 or any(
                    not isinstance(v, (float, int)) or not math.isfinite(v) for v in row) for row in matrix)):
            fail(path + '.rest_matrix_parent', 'matriz inválida')
    for uid, refs in graph.items():
        for ref in refs:
            if ref not in graph:
                fail('authored.members[{}].refs'.format(uid), 'uid ausente: ' + ref)
    pending, done = set(), set()

    def visit(uid):
        if uid in pending:
            fail('authored.members[{}].refs'.format(uid), 'ciclo entre regras')
            return
        if uid in done:
            return
        pending.add(uid)
        for ref in graph.get(uid, ()):
            if ref in graph:
                visit(ref)
        pending.remove(uid)
        done.add(uid)

    for uid in graph:
        visit(uid)
    return errors
