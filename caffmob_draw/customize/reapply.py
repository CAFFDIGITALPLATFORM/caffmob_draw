"""Reaplicar a personalização depois que a biblioteca reconstrói frentes ou materiais (feature 003, T026; D-04).

As bibliotecas chamam `after_rebuild(context, obj)` no fim das operações que recriam frentes ou reatribuem materiais;
o adaptador relê `btm_custom` (vãos, peças e raiz) e reaplica estilo, puxador e materiais. Módulo sem personalização
sai sem custo.

Feature 006 (T029; D-07, D-10): módulo com estrutura editada (`btm_structure`) ou com divisões também conta como
personalizado; depois de reaplicar, o adaptador reafirma remoções e espessuras e as divisões são reposicionadas.

Feature 008 (T045; D-11, D-12): peças das abas novas (extras, internos, deslizantes) e o fundo recuado também contam;
com "Inserir automaticamente", o recuo do fundo é reafirmado, e as peças novas voltam ao lugar. Um fundo removido
pelo projetista continua removido (a remoção é uma escolha explícita).

Feature 067 (onda 2, D-15): os acabamentos por domínio (`btm_finish`, fora os migrados) também contam e voltam depois
do adaptador, pela `customize/finish.reapply`.
"""

from . import adapters

_running = set()


DIVISION_SIGNATURE = 'btm_division_sig'     # = cabinet_editor.scene_divisions.SIGNATURE_PROP


def has_structure(root):
    structure = getattr(root, 'btm_structure', None)
    if structure is not None and (structure.components or structure.back_mode == 'RECESSED'):
        return True
    return DIVISION_SIGNATURE in root or any(getattr(o, 'btm_extra', None) is not None and o.btm_extra.is_extra
                                             for o in root.children)


def has_custom(root):
    if has_structure(root):
        return True
    if root.btm_custom.group_materials or root.btm_custom.pull_all_fronts:
        return True
    for obj in [root] + list(root.children_recursive):
        if any(item.source != 'MIGRATED' for item in getattr(obj, 'btm_finish', ())):
            return True
        custom = getattr(obj, 'btm_custom', None)
        if custom is None:
            continue
        if (custom.door_style or custom.drawer_style or custom.pull_model or custom.pull_position != 'DEFAULT'
                or custom.front_material or custom.material or custom.interior):
            return True
    return False


def reapply(context, root):
    """Reaplica pelo adaptador da biblioteca; devolve a lista de avisos."""
    adapter = adapters.for_root(root)
    if adapter is None or root.name in _running:
        return []
    _running.add(root.name)
    try:
        messages = adapter.reapply(context, root)
        from . import finish
        finish.reapply(root)
        return messages
    finally:
        _running.discard(root.name)


def after_rebuild(context, obj):
    """Gancho das bibliotecas: `obj` é a raiz ou qualquer objeto do módulo."""
    root = adapters.module_root(obj)
    if root is None or not hasattr(root, 'btm_custom') or not has_custom(root):
        return []
    messages = reapply(context, root)
    if has_structure(root) and root.name not in _running:
        _running.add(root.name)
        try:
            from ..cabinet_editor import scene_divisions, scene_extras, scene_interiors, scene_slides
            from .adapters import common
            adapter = adapters.for_root(root)
            messages += common.call(adapter, 'reaffirm', context, root)
            holder = root.btm_structure
            if holder.auto_back and holder.back_mode == 'RECESSED':
                messages += common.call(adapter, 'set_back_recess', context, root, holder.back_setback)
            scene_divisions.reflow(context, root)
            scene_extras.sync(context, root)
            scene_interiors.reflow(context, root)
            scene_slides.reflow(context, root)
        finally:
            _running.discard(root.name)
    return messages
