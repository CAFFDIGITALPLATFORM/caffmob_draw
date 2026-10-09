"""Grupos salvos das bibliotecas herdadas (feature 012, T066; D-29, D-30, RN-16). Python puro.

O marcador `legacy_groups.json` (na biblioteca do usuário) guarda se a oferta já foi feita e quais arquivos foram
convertidos. Marcador inválido vale como ausente: a oferta volta, sem perder nada.
"""

import json

SCHEMA_VERSION = 1


def pending(files, marker):
    done = set(marker.get('converted', []))
    return [name for name in files if name not in done]


def should_offer(files, marker):
    return bool(pending(files, marker)) and not marker.get('offered', False)


def parse_marker(text):
    try:
        data = json.loads(text or "")
    except ValueError:
        return {}
    if not isinstance(data, dict) or not isinstance(data.get('offered', False), bool):
        return {}
    converted = data.get('converted', [])
    if not isinstance(converted, list) or not all(isinstance(n, str) for n in converted):
        return {}
    return {"offered": data.get('offered', False), "converted": list(converted)}


def mark(marker, converted=()):
    """Marcador com a oferta feita e os arquivos convertidos somados."""
    done = list(marker.get('converted', []))
    done += [name for name in converted if name not in done]
    return {"offered": True, "converted": done}


def dump_marker(marker):
    return json.dumps({"schema-version": SCHEMA_VERSION, "offered": bool(marker.get('offered')),
                       "converted": list(marker.get('converted', []))}, ensure_ascii=False, indent=2)


def target_name(name, existing):
    """Nome sem colidir com os módulos que já existem (`existing` em minúsculas)."""
    if name.casefold() not in existing:
        return name
    index = 2
    while f"{name} ({index})".casefold() in existing:
        index += 1
    return f"{name} ({index})"
