"""Internos na cena: painel p/ eletro com recorte, eletros de referência, apoio e pistão (feature 008, T025; RN-13a,
D-17).

Cada item inserido fica gravado no próprio objeto (`btm_extra`: catálogo, subvão). `sync` recalcula a posição de
todos a partir do subvão atual (as divisões da 006 dão os subvãos). O recorte do painel é um `CPM_CUTOUT` com o
prefixo de agregado, que o plano de corte já leva para a usinagem da peça.
"""

from .. import compat, hb_types
from ..cutting import machining
from . import appliances as ap
from . import catalog, divisions as dv, scene_divisions, scene_parts

KINDS = {'APPLIANCE_PANEL', 'APPLIANCE', 'APPLIANCE_SUPPORT', 'PISTON',
         'HANGER_ROD', 'PANTS_RACK', 'SHOE_RACK', 'BELT_RACK'}           # roupeiro (feature 015, T032)
APPLIANCE_NAMES = {'OVEN': "Forno", 'MICRO': "Microondas", 'COFFEE': "Cafeteira"}
PANEL_THICKNESS = 0.018
PISTON_BOX = (0.02, 0.25, 0.02)


def entries(root):
    """[{uid, catalog_id, space}] dos internos inseridos (um por item, pela peça principal)."""
    seen, out = set(), []
    for obj in scene_parts.extras_of(root, KINDS):
        data = obj.btm_extra
        key = (data.catalog_id, data.space, data.slot)
        if key in seen:
            continue
        seen.add(key)
        out.append({"catalog_id": data.catalog_id, "space": data.space, "slot": data.slot})
    return sorted(out, key=lambda e: (e["space"], e["catalog_id"], e["slot"]))


def _leaves(context, root):
    roots = scene_divisions.roots(context, root)
    return dv.resolve(roots, scene_divisions.core(context.scene, root))[0]


def _cutout(panel, cut, panel_box):
    mod = hb_types.GeoNodeCutpart(panel).add_part_modifier('CPM_CUTOUT', machining.AGGREGATE_PREFIX + panel.name).mod
    (px0, _py0, pz0) = panel_box[0]
    (cx0, _a, cz0), (cx1, _b, cz1) = cut
    for socket, value in (('X', cx0 - px0), ('End X', cx1 - px0), ('Y', cz0 - pz0), ('End Y', cz1 - pz0),
                          ('Route Depth', PANEL_THICKNESS), ('Flip Z', False)):
        compat.try_set_gn_input(mod, socket, value)
    mod.show_viewport = mod.show_render = True


def _rod_drop(context, root):
    """Distância do tubo do cabideiro à prateleira de cima (m), do Padrão de Dimensões na linha do módulo."""
    from ..standards import api, cabinet_defaults
    definition = api.active_definition(context.scene)
    values = api.definition_values(definition) if definition is not None else {}
    line = scene_divisions.line_of(root)
    return cabinet_defaults.structure_params(values, line)['hanger_rod_drop']


def _build_wardrobe(context, root, item, box, tag):
    """Internos de roupeiro (feature 015, RN-16): chapa vira `CabinetPart`; ferragem vira caixa com `btm_hardware`."""
    from . import wardrobe
    kind = item.param('kind')
    out = []
    for piece in wardrobe.layout(kind, (box.lo, box.hi), rod_drop=_rod_drop(context, root),
                                 material=item.param('material') or 'WOOD'):
        if piece.hardware:
            maker = scene_parts.make_cylinder if kind == 'HANGER_ROD' else scene_parts.make_box
            out.append(maker(root, item.label, piece.box, piece.kind, hardware=piece.hardware, **tag))
        else:
            out.append(scene_parts.make_part(root, item.label, piece.box, piece.kind, piece.component, **tag))
    return out


def _build(context, root, item, space_path, box, slot):
    tag = dict(catalog_id=item.id, space=space_path, slot=slot)
    if item.action == 'INSERT_WARDROBE':
        return _build_wardrobe(context, root, item, box, tag)
    if item.id == 'SUPPORT':
        _m, t = scene_divisions.configured(context.scene, root)
        z = box.lo[2] + box.size(2) / 3.0
        return [scene_parts.make_part(root, "Apoio de Eletro", ((box.lo[0], box.lo[1], z),
                                                                (box.hi[0], box.hi[1], z + t)),
                                      'APPLIANCE_SUPPORT', 'PRAT', **tag)]
    if item.id == 'PISTON':
        w, d, h = PISTON_BOX
        x = box.lo[0] + 0.03
        z = box.hi[2] - h - 0.03
        return [scene_parts.make_box(root, "Pistão", ((x, box.lo[1] + 0.03, z), (x + w, box.lo[1] + 0.03 + d, z + h)),
                                     'PISTON', hardware='PISTAO', **tag)]
    lay = ap.layout(box, item.id, PANEL_THICKNESS)
    out = []
    if lay.panel is not None:
        panel = scene_parts.make_part(root, item.label, lay.panel.box, 'APPLIANCE_PANEL', 'FRE_FORNO', **tag)
        if lay.cutout is not None:
            _cutout(panel, lay.cutout, lay.panel.box)
        out.append(panel)
    for code, abox in lay.appliances:
        out.append(scene_parts.make_box(root, APPLIANCE_NAMES.get(code, code), abox, 'APPLIANCE', **tag))
    return out


def apply(context, root, wanted):
    """Deixa os internos iguais a `wanted` ([{catalog_id, space, slot}]); devolve avisos (item que não cabe)."""
    scene_parts.delete(scene_parts.extras_of(root, KINDS))
    leaves = _leaves(context, root)
    warnings = []
    for entry in wanted:
        item = catalog.get(entry["catalog_id"])
        box = leaves.get(entry["space"])
        if item is None or box is None:
            warnings.append(entry["catalog_id"])
            continue
        _build(context, root, item, entry["space"], box, entry.get("slot", 0))
    return warnings


def reflow(context, root):
    return apply(context, root, entries(root))
