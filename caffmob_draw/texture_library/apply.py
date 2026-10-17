"""Aplicar uma textura do catálogo a um alvo (feature 014, T025; RN-05, RN-06, RN-12, RN-13).

- `targets(obj)`: o que muda quando a textura cai sobre `obj` (`selection.classify`): a peça, a frente inteira, as
  peças do módulo ou o próprio objeto. Cota e anotação não recebem textura.
- `apply(objs, item_id)`: com a imagem no cache, cria (ou reaproveita) o material de imagem
  (`object_library.retexture.image_material`, com o tamanho do catálogo, D-08) e aplica por
  `common.set_cutpart_material`. A escolha fica gravada na personalização, para sobreviver a refazer o módulo
  (`_reversa_sdd/customize/requirements.md#RN-05`): peça das bibliotecas herdadas em `btm_custom.material` (vence o
  grupo e o vão); armário CAFFMob na caixa (grupo "CAIXA") ou nas frentes (`front_material`, todas as portas dele).
  Sem a imagem, enfileira o download (`downloads.fetch`) e aplica ao concluir, numa etapa de desfazer própria.
- Veio (RN-06, 🟡): a peça tem o comprimento no eixo X local; o veio da imagem segue o lado maior dela. Imagem em pé
  (mais alta que larga) numa peça usa a variante girada `<nome> ROTATED`, a mesma convenção da personalização.
"""

import bpy  # type: ignore

from ..customize.adapters import common
from ..data.i18n import N_, tr
from ..object_library import retexture
from ..selection import classify as classify_mod
from . import bump, catalog, downloads

APPLIED, QUEUED, ERROR = 'APPLIED', 'QUEUED', 'ERROR'
NO_TARGET = N_("Solte a textura sobre uma peça, frente, módulo ou objeto")
UNKNOWN = N_("Textura fora do catálogo")
DONE_LATER = N_("Textura {} aplicada em {} peça(s)")
FAILED_LATER = N_("Textura {} não aplicada: {}")
DOWNLOADING = N_("Baixando {}… a textura entra quando o download terminar")


def _meshes(objs):
    seen, out = set(), []
    for obj in objs:
        if obj is not None and obj.type == 'MESH' and obj.name not in seen:
            seen.add(obj.name)
            out.append(obj)
    return out


def targets(obj):
    """Malhas que recebem a textura solta sobre `obj` (RN-05)."""
    found = classify_mod.classify(obj)
    if found is None or found.kind == classify_mod.ANNOTATION:
        return []
    if found.kind == classify_mod.FRONT:
        if found.library == 'BTM':
            from ..geometry import door_controller
            return _meshes(door_controller.doors_of(found.root))
        return _meshes([found.obj] + list(found.obj.children_recursive))
    if found.kind == classify_mod.MODULE:
        return [o for o in found.root.children_recursive if common.is_cutpart(o)] or _meshes([found.root])
    return _meshes([obj])


def _set_group(custom, group, name):
    for item in custom.group_materials:
        if item.group == group:
            item.material = name
            return
    item = custom.group_materials.add()
    item.group, item.material = group, name


def _remember(obj, mat):
    """Grava a textura na personalização do módulo (RN-05), para refazer o módulo não desfazer a escolha."""
    root, library = classify_mod.module_root(obj)
    if root is None:
        return
    if library == 'BTM':
        found = classify_mod.classify(obj)
        if found is not None and found.kind == classify_mod.FRONT:
            root.btm_custom.front_material = mat.name
        elif obj is root:
            _set_group(root.btm_custom, 'CAIXA', mat.name)
        return
    custom = getattr(obj, 'btm_custom', None)
    if custom is not None and common.is_cutpart(obj):
        custom.material = mat.name                     # precedência peça > grupo > vão


def size_mm(item_id):
    entry = catalog.item(item_id)
    return catalog.default_size(entry) if entry else (catalog.catalog_core.DEFAULT_SIZE_MM,) * 2


def grain_rotated(obj, entry):
    """Variante de veio girado para esta peça? (RN-06: só peça; imagem em pé)."""
    if not common.is_cutpart(obj):
        return False
    px = entry.get("px") or (0, 0)
    return float(px[1]) > float(px[0])


def apply_cached(objs, item_id, path, size=None):
    """Aplica a imagem já baixada; devolve quantas malhas mudaram."""
    entry = catalog.item(item_id) or {}
    width, height = size or size_mm(item_id)
    changed = 0
    for obj in _meshes(objs):
        mat = retexture.image_material(path, width, height, rotated=grain_rotated(obj, entry), texture_id=item_id)
        if entry.get("sha256"):
            mat["btm_texture_sha256"] = entry["sha256"]
            mat["btm_texture_formato"] = entry.get("formato", entry.get("ext", "jpg"))
        bump.request(mat, entry)                       # relevo, quando o fabricante tem (T045)
        if common.set_cutpart_material(obj, mat):
            changed += 1
            if obj.get("caffmob_modulo"):
                from ..mobi.texturas import remember
                remember(obj, item_id)
            else:
                _remember(obj, mat)
    return changed


def _notify(text):
    from ..ui import save_feedback
    save_feedback.show(text)


def apply(objs, item_id, size=None):
    """(APPLIED, n) com a imagem no cache; (QUEUED, 0) quando o download começou; (ERROR, mensagem)."""
    entry = catalog.item(item_id)
    if entry is None:
        return ERROR, tr(UNKNOWN)
    if entry.get('mobi_id'):
        result = []
        def resolved(remote, error):
            if error:
                result.append((ERROR, tr(error['message'])))
                _notify(tr(error['message']))
            else:
                result.append(apply(objs, remote['id'], size))
        catalog.resolve(item_id, resolved)
        return result[0] if result else (QUEUED, 0)
    objs = _meshes(objs)
    if not objs:
        return ERROR, tr(NO_TARGET)
    path = downloads.cached(item_id)
    if path:
        return APPLIED, apply_cached(objs, item_id, path, size)
    reason = downloads.unavailable_reason()
    if reason:
        return ERROR, tr(reason)
    names = [o.name for o in objs]
    label = entry.get("name", item_id)
    now = {"inside": True}                             # `fetch` pode responder na hora (sem conta, por exemplo)

    def done(path, error):
        if error:
            if now["inside"]:
                now["error"] = error
            elif error.get("code") != "cancelled":
                _notify(tr(FAILED_LATER).format(label, tr(error.get("message") or "")))
            return
        alive = [o for o in (bpy.data.objects.get(n) for n in names) if o is not None]
        changed = apply_cached(alive, item_id, path, size)
        if now["inside"]:
            now["changed"] = changed
            return
        if changed:
            try:
                bpy.ops.ed.undo_push(message=tr("Aplicar textura"))
            except RuntimeError:
                pass
        _notify(tr(DONE_LATER).format(label, changed))
    downloads.fetch(item_id, done)
    now["inside"] = False
    if "error" in now:
        return ERROR, tr(now["error"].get("message") or "")
    if "changed" in now:
        return APPLIED, now["changed"]
    _notify(tr(DOWNLOADING).format(label))
    return QUEUED, 0
