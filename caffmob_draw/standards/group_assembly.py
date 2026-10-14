"""Montagem por grupo de estrutura no Padrão de Dimensões (feature 015, T003; RN-08, D-08). Python puro.

A definição guarda, para cada grupo (INFERIOR, SUPERIOR, DESPENSEIRO), a montagem da caixa, o tipo de fundo e a
posição do sarrafo traseiro. Grupo ausente = vale o que a estrutura de caixa traz. O texto gravado é JSON
(`BTM_PG_StandardDefinition.group_assembly`); no XML do Promob vai como `CAFF_GRUPO_<GRUPO>` = "a;b;c".

Valor inválido cai só naquele campo, com aviso (como `CAFF_MONTAGEM`, RN-STANDARDS-19).
"""

import json

from ..data.i18n import tr

GROUPS = ('INFERIOR', 'SUPERIOR', 'DESPENSEIRO')
FIELDS = ('assembly', 'back_kind', 'rear_stretcher')
CHOICES = {
    'assembly': ('LATERAL', 'BASE'),
    'back_kind': ('ENCAIXADO', 'REBAIXADO', 'PREGADO', 'TRAVESSAS'),
    'rear_stretcher': ('HORIZONTAL', 'VERTICAL'),
}
XML_PREFIX = 'CAFF_GRUPO_'


def normalize(data):
    """({grupo: {campo: valor}} só com o que é válido, [avisos]). Aceita dict ou texto JSON; vazio = {}."""
    warnings = []
    if isinstance(data, str):
        text = data.strip()
        if not text:
            return {}, warnings
        try:
            data = json.loads(text)
        except ValueError:
            return {}, [tr("Montagem por grupo ilegível: ignorada")]
    if not isinstance(data, dict):
        return {}, ([tr("Montagem por grupo ilegível: ignorada")] if data else [])
    out = {}
    for group, fields in data.items():
        if group not in GROUPS:
            warnings.append(tr("Grupo de montagem desconhecido: {}").format(group))
            continue
        if not isinstance(fields, dict):
            warnings.append(tr("Grupo {}: valor ilegível").format(group))
            continue
        clean = {}
        for name in FIELDS:
            value = fields.get(name)
            if value is None:
                continue
            if value in CHOICES[name]:
                clean[name] = value
            else:
                warnings.append(tr("Grupo {}: {} inválido ({}); vale o da estrutura").format(group, name, value))
        if clean:
            out[group] = clean
    return out, warnings


def dumps(data):
    """Texto JSON estável (chaves ordenadas) do que é válido; {} vira ""."""
    clean, _warnings = normalize(data)
    return json.dumps(clean, sort_keys=True) if clean else ""


def resolve(data, group, structure_defaults):
    """Valores de `group`: os do padrão por cima dos da estrutura (`structure_defaults` = {campo: valor})."""
    clean, _warnings = normalize(data)
    merged = {'assembly': 'LATERAL', 'back_kind': 'ENCAIXADO', 'rear_stretcher': 'HORIZONTAL'}
    merged.update({k: v for k, v in (structure_defaults or {}).items() if k in FIELDS and v in CHOICES[k]})
    merged.update(clean.get(group, {}))
    return merged


def to_xml_attributes(data):
    """[(ID, VALOR)] para o XML do Promob, na ordem dos grupos."""
    clean, _warnings = normalize(data)
    out = []
    for group in GROUPS:
        fields = clean.get(group)
        if fields:
            out.append((XML_PREFIX + group, ";".join(fields.get(name, "") for name in FIELDS)))
    return out


def from_xml_attribute(attr_id, value):
    """(grupo, {campo: valor}, [avisos]) de um `CAFF_GRUPO_*`; partes vazias ou a menos ficam fora, com aviso."""
    group = attr_id[len(XML_PREFIX):] if attr_id.startswith(XML_PREFIX) else ""
    if group not in GROUPS:
        return None, {}, [tr("Grupo de montagem desconhecido: {}").format(group or attr_id)]
    parts = [p.strip() for p in str(value or "").split(";")]
    warnings = []
    if len(parts) < len(FIELDS):
        warnings.append(tr("Grupo {}: {} de {} campos; o resto vale o da estrutura").format(
            group, len([p for p in parts if p]), len(FIELDS)))
    raw = {name: parts[i] for i, name in enumerate(FIELDS) if i < len(parts) and parts[i]}
    clean, more = normalize({group: raw})
    return group, clean.get(group, {}), warnings + more


def differs(a, b):
    """Duas montagens por grupo diferem (para o rascunho do Configurador)?"""
    return normalize(a)[0] != normalize(b)[0]
