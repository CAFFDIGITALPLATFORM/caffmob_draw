"""Gerenciamento centralizado de camadas (coleções) do CAFFMob Draw (feature 021, T002; RN-05, RN-06).

Organiza elementos gerados pelo addon em duas camadas principais:
- `Arquitetura` com subcoleções por tipo: `Parede`, `Piso`, `Teto`, `Aberturas`
- `Marcenaria` para armários, módulos e gaveteiros

Coleções criadas pelo usuário nunca são renomeadas, movidas ou removidas.
"""

ARQUITETURA = "Arquitetura"
MARCENARIA = "Marcenaria"

ARCH_SUBCOLLECTIONS = {
    'WALL': "Parede",
    'PAREDE': "Parede",
    'FLOOR': "Piso",
    'PISO': "Piso",
    'CEILING': "Teto",
    'TETO': "Teto",
    'OPENING': "Aberturas",
    'ABERTURAS': "Aberturas",
}


def arch_subcollection_name(kind):
    """Retorna o nome da subcoleção dentro de `Arquitetura` para `kind`, ou `None` para a raiz `Arquitetura`."""
    if not kind:
        return None
    return ARCH_SUBCOLLECTIONS.get(str(kind).upper())


def floor_z_bounds(base_z, thickness, direction='DOWN'):
    """Calcula `(z_min, z_max)` do piso a partir do plano de referência `base_z` (RN-05, RF-06).

    - `DOWN`: face superior em `base_z`, espessura cresce para baixo (`base_z - thickness` até `base_z`).
    - `UP`: face inferior em `base_z`, espessura cresce para cima (`base_z` até `base_z + thickness`).
    """
    t = max(float(thickness), 0.001)
    z0 = float(base_z)
    if str(direction).upper() == 'UP':
        return (z0, z0 + t)
    return (z0 - t, z0)


def _get_or_create_child(parent_collection, name):
    import bpy  # type: ignore

    col = parent_collection.children.get(name)
    if col is None:
        col = bpy.data.collections.get(name)
        if col is None:
            col = bpy.data.collections.new(name)
        parent_collection.children.link(col)
    return col


def ensure_arquitetura(scene, kind=None):
    """Devolve a coleção `Arquitetura` (ou a subcoleção de `kind`), criando apenas o que faltar."""
    arq = _get_or_create_child(scene.collection, ARQUITETURA)
    sub = arch_subcollection_name(kind)
    if sub is None:
        return arq
    return _get_or_create_child(arq, sub)


def ensure_marcenaria(scene):
    """Devolve a coleção `Marcenaria` na cena, criando-a se não existir."""
    return _get_or_create_child(scene.collection, MARCENARIA)


def place(obj, colecao, scene):
    """Vincula `obj` exclusivamente a `colecao` dentro da árvore de coleções de `scene`."""
    if obj is None or getattr(obj, 'library', None) is not None:
        return
    if colecao not in obj.users_collection:
        colecao.objects.link(obj)
    da_cena = {scene.collection.as_pointer()}
    da_cena.update(c.as_pointer() for c in scene.collection.children_recursive)
    for outra in list(obj.users_collection):
        if outra is not colecao and outra.as_pointer() in da_cena:
            outra.objects.unlink(obj)


def place_hierarchy(root, colecao, scene):
    """Vincula `root` e todos os seus descendentes diretos/indiretos à coleção `colecao`."""
    if root is None:
        return
    place(root, colecao, scene)
    for child in list(getattr(root, 'children_recursive', ())):
        place(child, colecao, scene)
