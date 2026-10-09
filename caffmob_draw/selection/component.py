"""Componente: raiz e exclusão em profundidade (feature 011, T006 e T008; roadmap D-01, D-05, D-07).

Componente é uma raiz com todos os seus descendentes. `component_root(obj, modes)` responde "qual é a raiz?" pela
precedência da nota D-01 (a primeira regra que casa vale):

1. vão de porta ou janela (`IS_ENTRY_DOOR_BP`, `IS_WINDOW_BP`, `btm_plane OPENING`), inclusive folhas, ferragens,
   símbolo e texto 2D filhos dele;
2. cota ou anotação solta: ela mesma;
3. agregado ou item grudado: ele mesmo (RN-03). A folha de uma esquadria (LEAF com o marco FRAME por pai) é peça da
   esquadria e segue subindo;
4. módulo (armário), só com o modo de seleção da biblioteca em gabinete: `modes = {biblioteca: bool}`, ausente vale
   True (o módulo rápido não tem modo e sobe sempre);
5. raiz de item da biblioteca de objetos (`btm_object_item.is_item`);
6. grupo de peças mais alto (`btm_group`: SketchUp, OBJ importado);
7. senão, o próprio objeto (parede, piso, malha solta).

Só usa `.get()`, `.parent`, `.children` e atributos simples, então funciona com objetos simulados nos testes.
"""

from collections import namedtuple

from . import classify

DeletePlan = namedtuple('DeletePlan', 'remove openings')


def is_opening_root(node):
    return bool(node.get('IS_ENTRY_DOOR_BP') or node.get('IS_WINDOW_BP')) or classify.btm_kind(node) == 'OPENING'


def _is_stuck(node):
    return bool(getattr(getattr(node, 'btm_stick', None), 'is_stuck', False))


def _is_frame_leaf(node):
    agg = node.btm_aggregate
    ref = getattr(agg, 'parent_ref', None)
    if agg.kind != 'LEAF' or ref is None:
        return False
    data = getattr(ref, 'btm_group', None)
    return bool(getattr(data, 'is_group', False)) and getattr(data, 'kind', '') == 'FRAME'


def _is_own_aggregate(node):
    agg = getattr(node, 'btm_aggregate', None)
    return bool(getattr(agg, 'is_aggregate', False)) and not _is_frame_leaf(node)


def _is_item(node):
    return bool(getattr(getattr(node, 'btm_object_item', None), 'is_item', False))


def component_root(obj, modes=None):
    if obj is None:
        return None
    chain = list(classify._ancestors(obj))
    for node in chain:
        if is_opening_root(node):
            return node
    if obj.get('IS_2D_ANNOTATION'):
        return obj
    for node in chain:
        if classify.module_library(node):
            break                                   # agregado e grudado ficam abaixo do hospedeiro
        if _is_stuck(node) or _is_own_aggregate(node):
            return node
    root, library = classify.module_root(obj)
    if root is not None:
        return root if (modes or {}).get(library, True) else obj
    for node in chain:
        if _is_item(node):
            return node
    group = classify.free_group(obj)
    return group if group is not None else obj


def collapse(objs, modes=None):
    """Raízes de `objs`, sem repetir, na ordem em que aparecem."""
    roots, seen = [], set()
    for obj in objs:
        root = component_root(obj, modes)
        if root is not None and id(root) not in seen:
            seen.add(id(root))
            roots.append(root)
    return roots


def own_aggregates(target):
    """Agregados que são componentes próprios abaixo de `target` (os da pergunta "levar os agregados junto?").

    A folha da porta, da janela ou da esquadria é peça delas, não entra.
    """
    found = []

    def walk(node):
        for child in node.children:
            if is_opening_root(child):
                continue
            if _is_own_aggregate(child) and component_root(child) is child:
                found.append(child)
                continue
            walk(child)

    if not is_opening_root(target) and not _is_frame_group(target):
        walk(target)
    return found


def _is_frame_group(node):
    data = getattr(node, 'btm_group', None)
    return bool(getattr(data, 'is_group', False)) and getattr(data, 'kind', '') == 'FRAME'


def deletes_subtree(obj):
    """Excluir `obj` leva a subárvore? Não para parede, piso e teto: o que está preso neles é outro componente."""
    info = classify.classify(obj)
    return info is None or info.obj is not obj or info.kind not in (classify.WALL, classify.FLOOR, classify.CEILING)


def delete_plan(targets, keep_aggregates=False):
    """O que apagar ao excluir `targets`: a subárvore inteira, filhos antes dos pais, sem repetir.

    Itens grudados nunca entram (são soltos no lugar); com `keep_aggregates`, os agregados próprios e as peças deles
    também ficam. Parede, piso e teto saem sozinhos (`deletes_subtree`). `openings` lista os vãos de porta e janela que saem, para tirar o furo da parede.
    """
    keep = set()
    for target in targets:
        if keep_aggregates:
            keep.update(id(a) for a in own_aggregates(target))
    remove, seen = [], set()

    def walk(node, is_target):
        if id(node) in seen:
            return
        if not is_target and (_is_stuck(node) or id(node) in keep):
            return
        seen.add(id(node))
        if not is_target or deletes_subtree(node):
            for child in list(node.children):
                walk(child, False)
        remove.append(node)

    for target in targets:
        walk(target, True)
    openings = [node for node in remove if is_opening_root(node)]
    return DeletePlan(remove, openings)
