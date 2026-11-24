"""Detecção e sincronização de texturas perdidas do addon (feature 021, T019; RF-03, RN-03).

Localiza imagens em `bpy.data.images` pertencentes ao catálogo do CAFFMob Draw cujo arquivo no disco esteja ausente ou
vazio, e dispara o re-download assíncrono com timeout (15 s), até 2 retentativas e escrita atômica via
`texture_library/downloads.py`, reconectando os materiais afetados na cena.
"""

import os
from typing import Dict, List, Tuple

TIMEOUT_SECONDS = 15.0
MAX_RETRIES = 2

_active_sync = {
    'running': False,
    'cancelled': False,
    'total': 0,
    'synced': 0,
    'failed': 0,
    'already_ok': 0,
    'tickets': [],
}


def is_file_missing_or_corrupt(filepath: str) -> bool:
    """Retorna True se o caminho está vazio, não existe no disco ou tem 0 bytes."""
    if not filepath:
        return True
    try:
        return (not os.path.isfile(filepath)) or os.path.getsize(filepath) == 0
    except OSError:
        return True


def find_missing_addon_textures() -> Tuple[List[Dict[str, object]], int]:
    """Inspeciona `bpy.data.images` buscando texturas do catálogo do addon ausentes no disco.

    Retorna `(lista_ausentes, total_ja_presentes)`.
    """
    import bpy  # type: ignore

    missing: List[Dict[str, object]] = []
    present = 0
    seen_ids = set()

    for img in bpy.data.images:
        tex_id = img.get('caffmob_texture_id') or img.get('btm_texture_id') or ""
        if not tex_id:
            continue
        abs_path = bpy.path.abspath(img.filepath) if img.filepath else ""
        if not is_file_missing_or_corrupt(abs_path):
            present += 1
            continue
        if tex_id in seen_ids:
            continue
        seen_ids.add(tex_id)
        missing.append({'id': str(tex_id), 'image_name': img.name, 'filepath': abs_path})

    return missing, present


def cancel_sync():
    """Cancela a sincronização de texturas em andamento, se houver."""
    _active_sync['cancelled'] = True
    try:
        from . import downloads
        for tid in list(_active_sync['tickets']):
            downloads.cancel(tid)
    except Exception:
        pass
    _active_sync['tickets'].clear()
    _active_sync['running'] = False


def sync_missing_textures(on_complete=None):
    """Dispara o re-download assíncrono das texturas ausentes e reconecta `bpy.data.images`."""
    import bpy  # type: ignore
    from . import catalog, downloads

    missing, present = find_missing_addon_textures()
    if not missing:
        summary = {'synced': 0, 'failed': 0, 'already_ok': present, 'message': "Todas as texturas do addon já estão presentes localmente."}
        if on_complete:
            on_complete(summary)
        return summary

    _active_sync.update({
        'running': True,
        'cancelled': False,
        'total': len(missing),
        'synced': 0,
        'failed': 0,
        'already_ok': present,
        'tickets': [],
    })

    pending = {'count': len(missing)}
    entries_by_id = {}
    try:
        for entry in catalog.all_entries():
            if entry.get('id'):
                entries_by_id[str(entry['id'])] = entry
    except Exception:
        pass

    def _finish_one():
        pending['count'] -= 1
        if pending['count'] <= 0:
            _active_sync['running'] = False
            summary = {
                'synced': _active_sync['synced'],
                'failed': _active_sync['failed'],
                'already_ok': _active_sync['already_ok'],
                'message': f"{_active_sync['synced']} textura(s) sincronizada(s), {_active_sync['failed']} com falha, {_active_sync['already_ok']} já presente(s).",
            }
            if on_complete:
                on_complete(summary)

    def _relink_image(tex_id: str, new_path: str):
        for img in bpy.data.images:
            if (img.get('caffmob_texture_id') or img.get('btm_texture_id')) == tex_id:
                img.filepath = new_path
                try:
                    img.reload()
                except Exception:
                    pass

    def _attempt_fetch(item: Dict[str, object], retries_left: int):
        if _active_sync['cancelled']:
            _finish_one()
            return
        tid = str(item['id'])
        entry = entries_by_id.get(tid)

        def _done(path, error):
            if _active_sync['cancelled']:
                _finish_one()
                return
            if path and not is_file_missing_or_corrupt(path):
                _relink_image(tid, path)
                _active_sync['synced'] += 1
                _finish_one()
            elif retries_left > 0:
                bpy.app.timers.register(lambda: (_attempt_fetch(item, retries_left - 1), None)[1], first_interval=1.0)
            else:
                _active_sync['failed'] += 1
                _finish_one()

        _active_sync['tickets'].append(tid)
        downloads.fetch(tid, _done, entry=entry)

    for item in missing:
        _attempt_fetch(item, MAX_RETRIES)

    return {'running': True, 'total': len(missing), 'already_ok': present}
