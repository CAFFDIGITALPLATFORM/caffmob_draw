"""Coleções do Editor de Paredes: as paredes moram em Arquitetura > Parede (BUG-20261117-4MF7).

O construtor do Home Builder linka todo objeto de geometria na coleção mestre da cena
(`hb_types.GeoNodeObject.create`), então o editor organiza a parede depois de criá-la ou atualizá-la. A hierarquia do
usuário é reaproveitada pelo caminho: `Arquitetura` de topo e a filha `Parede`. Coleção existente nunca é renomeada,
movida nem apagada.
"""

import bpy  # type: ignore

ARQUITETURA = "Arquitetura"
PAREDE = "Parede"


def ensure(scene):
    """Devolve a coleção `Parede` dentro de `Arquitetura`, criando só o que faltar."""
    arquitetura = scene.collection.children.get(ARQUITETURA)
    if arquitetura is None:
        arquitetura = bpy.data.collections.new(ARQUITETURA)
        scene.collection.children.link(arquitetura)
    parede = arquitetura.children.get(PAREDE)
    if parede is None:
        parede = bpy.data.collections.new(PAREDE)
        arquitetura.children.link(parede)
    return parede


def place(obj, colecao, scene):
    """Põe `obj` em `colecao` e o tira das outras coleções desta cena. Devolve True se mudou algo.

    Objeto de biblioteca linkada (`obj.library`) não pode ser relinkado pelo Blender e fica como está.
    """
    if obj.library is not None:
        return False
    da_cena = {scene.collection.as_pointer()}
    da_cena.update(c.as_pointer() for c in scene.collection.children_recursive)
    mudou = colecao not in obj.users_collection or len(obj.users_collection) > 1
    if colecao not in obj.users_collection:
        colecao.objects.link(obj)
    for outra in list(obj.users_collection):
        if outra is not colecao and outra.as_pointer() in da_cena:
            outra.objects.unlink(obj)
    return mudou
