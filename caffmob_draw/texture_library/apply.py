"""Aplicar uma textura do catálogo a um alvo (feature 014, T025; RN-05, RN-06, RN-12, RN-13).

- `targets(obj)`: o que muda quando a textura cai sobre `obj` (`selection.classify`): a peça, a frente inteira, as
  peças do módulo ou o próprio objeto. Cota e anotação não recebem textura.
- `apply_domains(objs, item_id, path, size, domains)`: o mesmo funil, só nos domínios de parte escolhidos
  (`FRONTS`/`EXTERNAL`/`INTERNAL`) e com a contagem por domínio (018, T023, RN-11, D-08).
- `apply(objs, item_id)`: com a imagem no cache, cria (ou reaproveita) o material de imagem
  (`object_library.retexture.image_material`, com o tamanho do catálogo, D-08) e aplica por
  `common.set_cutpart_material`. A escolha fica gravada na personalização, para sobreviver a refazer o módulo
  (`_reversa_sdd/customize/requirements.md#RN-05`): peça das bibliotecas herdadas em `btm_custom.material` (vence o
  grupo e o vão); armário CAFFMob na caixa (grupo "CAIXA") ou nas frentes (`front_material`, todas as portas dele).
  Sem a imagem, enfileira o download (`downloads.fetch`) e aplica ao concluir, numa etapa de desfazer própria.
- Veio (067 onda 3, RF-063, RF-065): um material só por textura; o giro é por objeto (`texture_library/grain`), a
  partir de `btm_part.grain` e da calibração da imagem. A variante `<nome> ROTATED` não é mais criada.
"""

import bpy  # type: ignore

from ..customize import finish
from ..customize.adapters import common
from ..data.i18n import N_, tr
from ..object_library import retexture
from ..selection import classify as classify_mod
from . import bump, catalog, downloads, grain, pick, uv_core

APPLIED, QUEUED, ERROR = 'APPLIED', 'QUEUED', 'ERROR'
NO_TARGET = N_("Solte a textura sobre uma peça, frente, módulo ou objeto")
UNKNOWN = N_("Textura fora do catálogo")
DONE_LATER = N_("Textura {} aplicada em {} peça(s)")
FAILED_LATER = N_("Textura {} não aplicada: {}")
DOWNLOADING = N_("Baixando {}… a textura entra quando o download terminar")
NO_UV = N_("A malha não tem UV: a textura entra em projeção de caixa")


def _meshes(objs):
    seen, out = set(), []
    for obj in objs:
        if getattr(obj, 'btm_cut_exclude', False):         # fita visual não é alvo de textura (067 RN-11)
            continue
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


def material_for(obj, item_id, path, size=None):
    """Material de imagem do alvo, com a projeção que ele aceita e os dados do fabricante.

    A chapa tem UV próprio: textura retangular só mantém a escala real por UV (018, T012, T023).
    """
    entry = catalog.item(item_id) or {}
    width, height = size or size_mm(item_id)
    mat = retexture.image_material(path, width, height, texture_id=item_id, projection=retexture.projection_for(obj))
    if entry.get("sha256"):
        mat["btm_texture_sha256"] = entry["sha256"]
        mat["btm_texture_formato"] = entry.get("formato", entry.get("ext", "jpg"))
    bump.request(mat, entry)                           # relevo, quando o fabricante tem (T045)
    return mat


def _copiar_giro(obj, angulo):
    """Leva o giro do veio da origem para a peça; a sincronia é uma só, feita depois do material (T020, RN-10)."""
    for dono in (getattr(obj, 'btm_armario_parte', None), getattr(obj, 'btm_part', None)):
        if getattr(dono, 'grain_angle', None) is not None:
            with grain.suspended():
                dono.grain_angle = float(angulo)
            return


def apply_domains(objs, item_id, path, size=None, domains=(), angle=None):
    """Aplica a imagem já baixada só nos domínios de parte pedidos (018, T023; RN-11, D-08).

    Devolve `(APPLIED, {domínio: peças})` ou `(ERROR, NO_TARGET)`. O plano é resolvido antes de tocar na cena: peça
    que não cobre nenhum domínio marcado (fita, cota, peça sem papel) fica de fora e nada é aplicado quando o plano
    sai vazio — não existe aplicação parcial. A escolha fica em `btm_finish` e em `btm_armario_parte.material`
    (D-11), o giro `angle` entra na peça junto com a textura e o veio é sincronizado uma vez por peça.
    """
    plano = []
    for obj in _meshes(objs):
        cobertos = tuple(dominio for dominio in pick.dominios_do_objeto(obj) if dominio in domains)
        if cobertos:
            plano.append((obj, cobertos))
    if not plano:
        return ERROR, tr(NO_TARGET)
    contagem = {dominio: 0 for dominio in domains}
    aplicados = []
    for obj, cobertos in plano:
        mat = material_for(obj, item_id, path, size)
        if not common.set_cutpart_material(obj, mat):
            continue
        aplicados.append(obj)
        for dominio in cobertos:
            finish.remember(obj, dominio, mat)
            contagem[dominio] += 1
        parte = getattr(obj, 'btm_armario_parte', None)
        if parte is not None and str(parte.papel or ''):
            parte.material = mat.name
        if angle is not None:
            _copiar_giro(obj, angle)
        grain.sync(obj)
    mudou = sum(contagem.values())
    _avisar_projecao(aplicados)
    return (APPLIED, contagem) if mudou else (ERROR, tr(NO_TARGET))


def apply_cached(objs, item_id, path, size=None):
    """Aplica a imagem já baixada; devolve quantas malhas mudaram."""
    changed = 0
    aplicados = []
    for obj in _meshes(objs):
        mat = material_for(obj, item_id, path, size)
        if common.set_cutpart_material(obj, mat):
            changed += 1
            aplicados.append(obj)
            grain.sync(obj)                            # a intenção de veio da peça entra no material (D-30)
            if obj.get("caffmob_modulo"):
                from ..mobi.texturas import remember
                remember(obj, item_id)
            else:
                _remember(obj, mat)
    _avisar_projecao(aplicados)
    return changed


def _notify(text):
    from ..ui import save_feedback
    save_feedback.show(text)


def _avisar_projecao(aplicados):
    """Avisa quando a textura entrou em projeção de caixa: o UV Editor não mexe nessa malha (018, RN-15, D-14)."""
    if any(retexture.projection_for(obj) == uv_core.BOX for obj in aplicados):
        _notify(tr(NO_UV))


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
