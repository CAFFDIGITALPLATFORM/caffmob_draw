"""Identidade estável (uid) de portas, folhas, membros e revestimentos (feature 066, D-02, RN-01).

Nome e proximidade não identificam: cada entidade guarda um `uid` (uuid4 em hexadecimal) num PropertyGroup e os
vínculos dentro do arquivo usam `PointerProperty`, que o Blender remapeia no Shift+D e no append (medido em
`tests/blender_066_pointer_remap.py`). O uid serve para achar a duplicata e para o manifesto da biblioteca.

Módulo puro: recebe os `holders` (qualquer objeto com o atributo `uid`) e não importa `bpy`.
"""

import uuid

UID_LENGTH = 32


def new_uid():
    return uuid.uuid4().hex


def is_uid(value):
    text = str(value or "")
    return len(text) == UID_LENGTH and all(c in "0123456789abcdef" for c in text)


def ensure_uid(holder):
    """Devolve o uid do `holder`, gravando um novo quando falta ou é inválido."""
    if not is_uid(getattr(holder, "uid", "")):
        holder.uid = new_uid()
    return holder.uid


def short(uid):
    """Rótulo curto para nomes visíveis (ex.: `Boolean_<uid8>`); nunca usado para achar nada."""
    return str(uid or "")[:8]


def renew_duplicates(entries):
    """Renova o uid repetido: o dono mais antigo fica com ele, as cópias recebem um novo.

    `entries` é uma sequência de `(ordem, holder)`; `ordem` é o `session_uid` do objeto (o Blender dá o menor ao que
    existia antes da cópia). Holders sem uid válido também recebem um. Devolve os holders que mudaram.
    """
    seen = set()
    renewed = []
    for _order, holder in sorted(entries, key=lambda entry: entry[0]):
        uid = getattr(holder, "uid", "")
        if not is_uid(uid) or uid in seen:
            holder.uid = new_uid()
            renewed.append(holder)
        seen.add(holder.uid)
    return renewed


def remap(uids):
    """Mapa `{uid antigo: uid novo}` para a inserção de uma cópia da biblioteca (BI-04): nenhuma ref aponta à origem."""
    return {old: new_uid() for old in dict.fromkeys(uids) if old}
