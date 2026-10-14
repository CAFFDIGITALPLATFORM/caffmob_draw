"""Entradas de `structure.carcass_parts` lidas de um módulo `btm` com estrutura (feature 015, T026/T027; D-02).

A malha (`geometry/mesh_gen.py`) e o plano de corte (`cutting/part_sources.synthetic_records`) chamam
`carcass_parts_for`: as duas leem aqui a receita, as espessuras, os parâmetros e a montagem do Padrão de Dimensões, as
peças marcadas na árvore e os cortes das divisórias "Corta Sar". Assim o 3D e o corte não divergem.

Módulo sem `structure_id`, ou com um id que o catálogo não tem, devolve None: quem chama segue a construção antiga.
"""

from . import structures_core

_BACK_COMPONENT = {'INFERIOR': 'FUN_INF', 'SUPERIOR': 'FUN_SUP', 'DESPENSEIRO': 'FUN_ALT'}


def _scene_of(obj, scene):
    if scene is not None:
        return scene
    users = getattr(obj, 'users_scene', ())
    if users:
        return users[0]
    try:
        import bpy  # type: ignore
    except ImportError:
        return None
    return bpy.context.scene


def _standard(scene):
    """(valores do padrão ativo, texto da montagem por grupo); sem padrão = ({}, "")."""
    if scene is None:
        return {}, ""
    try:
        from ..standards import api
        definition = api.active_definition(scene)
    except (AttributeError, ImportError):
        return {}, ""
    if definition is None:
        return {}, ""
    return api.definition_values(definition), getattr(definition, 'group_assembly', "")


def _roles(cab):
    """{PAPEL: (presente, modo, espessura em m)}, como `data.properties.structure_of` (que importa `bpy`)."""
    return {role.upper(): (bool(getattr(cab, 'has_' + role)), getattr(cab, 'mode_' + role),
                           float(getattr(cab, 'thickness_' + role)) or float(cab.thickness))
            for role in ('top', 'bottom', 'back', 'left', 'right')}


def _back_setback(obj):
    """Recuo do fundo "Inteiro Recuado" (008), como `data.properties.back_setback_of`."""
    structure = getattr(obj, 'btm_structure', None)
    if structure is None or structure.back_mode != 'RECESSED':
        return 0.0
    return float(structure.back_setback)


def recipe_of(obj):
    cab = getattr(obj, 'btm_cabinet', None)
    return structures_core.get(getattr(cab, 'structure_id', "")) if cab is not None else None


def _stretcher_cuts(obj, default_thickness):
    """[(x0, x1)] em m das divisórias verticais "Corta Sar" filhas do módulo."""
    out = []
    for child in getattr(obj, 'children', ()):
        division = getattr(child, 'btm_division', None)
        if division is None or not division.is_division or division.variant != 'CORTA_SAR':
            continue
        if division.orientation != 'VERTICAL':
            continue
        x0 = float(child.location.x)
        out.append((x0, x0 + (float(division.thickness) or default_thickness)))
    return out


def carcass_parts_for(obj, scale=1.0, scene=None):
    """(peças, vão interno) da caixa do módulo, com medidas multiplicadas por `scale` (1 = m, 1000 = mm); ou None."""
    from ..standards import cabinet_defaults
    from . import structure as st
    recipe = recipe_of(obj)
    if recipe is None:
        return None
    cab = obj.btm_cabinet
    values, group_text = _standard(_scene_of(obj, scene))
    found = cabinet_defaults.defaults_for_structure(values, recipe, group_text)
    line = cab.line

    def sheet(component, default):
        try:
            return float(values[f"{line}.sheets.{component}.thickness"]) / 1000.0
        except (KeyError, TypeError, ValueError):
            return default

    roles = _roles(cab)
    thick = {role: float(t) for role, (_present, _mode, t) in roles.items()}
    if not getattr(cab, 'thickness_back', 0.0):
        thick['BACK'] = sheet(_BACK_COMPONENT.get(recipe.group, 'FUN_INF'), thick['BACK'])
    for component in ('SAR', 'ROD', 'TAMP', 'TRA'):
        thick[component] = sheet(component, float(cab.thickness))
    present = {role: bool(p) for role, (p, _mode, _t) in roles.items()}
    holder = getattr(obj, 'btm_structure', None)
    settings = holder.extras_dict() if holder is not None else {}
    division_t = sheet('DIV', float(cab.thickness))
    cuts = _stretcher_cuts(obj, division_t)
    s = float(scale)
    settings = {k: dict(v, value=(float(v['value']) * s if v.get('value') else v.get('value')))
                for k, v in settings.items()}
    return st.carcass_parts(
        recipe, cab.width * s, cab.height * s, cab.depth * s, {k: v * s for k, v in thick.items()},
        settings=settings, params={k: v * s for k, v in found.params.items()}, present=present,
        back_setback=_back_setback(obj) * s, assembly=cab.assembly, back_kind=found.back_kind,
        rear_stretcher=found.rear_stretcher, stretcher_cuts=[(a * s, b * s) for a, b in cuts])
