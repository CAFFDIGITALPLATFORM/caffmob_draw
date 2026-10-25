"""Serviço de veio (feature 067, T065; D-20, D-30; RF-060 a RF-065).

- `ensure_graph(mat)`: no material de imagem, a coordenada (Object na projeção BOX, UV na UV) passa por um Vector
  Rotate em Euler XYZ cujo giro vem do nó Attribute (tipo Object) `btm_grain_rot`, e só depois pela escala métrica do
  Mapping (o giro acontece em metros, antes da conversão anisotrópica da imagem). Todas as imagens do material (cor,
  rugosidade, normal, relevo) leem o mesmo Mapping. Idempotente.
- `sync(obj)`: grava em `obj["btm_grain_rot"]` o giro que leva o veio da imagem ao veio pedido em `btm_part.grain`,
  na face semântica da peça (`grain_core.rotation`), e liga o grafo nos materiais de imagem dela. Peça sem material
  guarda só a intenção (`btm_part.grain`); o giro entra quando o material chega (`finish.apply_to` chama `sync`).
  Material antigo `<nome> ROTATED` (M-05) volta ao de origem na primeira edição de veio.
- `calibrate(mat, axis)`: o eixo do veio na imagem fonte (H ou V), gravado no material (RF-061).
"""

import bpy  # type: ignore

from . import grain_core as gc

ATTR = 'btm_grain_rot'
CALIBRATION = 'btm_image_grain_axis'
ROTATE_NODE = 'btm_grain_rotate'
ATTR_NODE = 'btm_grain_attribute'
ROTATED_SUFFIX = " ROTATED"
_suspended = [False]


class suspended:
    """Bloco em que mudar `btm_part.grain` não chama `sync` (migração M-05)."""
    def __enter__(self):
        self.previous = _suspended[0]
        _suspended[0] = True

    def __exit__(self, *_exc):
        _suspended[0] = self.previous


def on_grain_changed(part, _context=None):
    """`update` de `btm_part.grain`: o veio visual acompanha o de corte (RF-064)."""
    if _suspended[0]:
        return
    try:
        sync(part.id_data)
    except (AttributeError, ReferenceError, RuntimeError) as exc:
        print(f"CAFFMob Draw: veio não sincronizado: {exc}")


def _nodes(mat):
    tree = mat.node_tree if mat is not None and mat.use_nodes else None
    return tree


def is_image_material(mat):
    tree = _nodes(mat)
    return tree is not None and any(n.type == 'TEX_IMAGE' for n in tree.nodes) and \
        any(n.type == 'MAPPING' for n in tree.nodes)


def projection(mat):
    tree = _nodes(mat)
    if tree is None:
        return gc.BOX
    for link in tree.links:
        if link.from_node.type == 'TEX_COORD' and link.from_socket.name == 'UV':
            return gc.UV
    return gc.BOX


def image_axis(mat):
    value = mat.get(CALIBRATION, 'H') if mat is not None else 'H'
    return value if value in ('H', 'V') else 'H'


def calibrate(mat, axis):
    if mat is not None and axis in ('H', 'V'):
        mat[CALIBRATION] = axis


def ensure_graph(mat):
    """Liga o giro por objeto no material de imagem; devolve True se o grafo está pronto."""
    tree = _nodes(mat)
    if tree is None or not is_image_material(mat):
        return False
    mapping = next(n for n in tree.nodes if n.type == 'MAPPING')
    rotate = tree.nodes.get(ROTATE_NODE)
    if rotate is None:
        source = next((link for link in tree.links if link.to_node == mapping
                       and link.to_socket.name == 'Vector'), None)
        if source is None:
            return False
        rotate = tree.nodes.new('ShaderNodeVectorRotate')
        rotate.name = rotate.label = ROTATE_NODE
        rotate.rotation_type = 'EULER_XYZ'
        attribute = tree.nodes.new('ShaderNodeAttribute')
        attribute.name = attribute.label = ATTR_NODE
        attribute.attribute_type = 'OBJECT'
        attribute.attribute_name = ATTR
        rotate.location = (mapping.location.x - 200, mapping.location.y)
        attribute.location = (mapping.location.x - 420, mapping.location.y - 220)
        from_socket = source.from_socket
        tree.links.remove(source)
        tree.links.new(from_socket, rotate.inputs['Vector'])
        tree.links.new(attribute.outputs['Vector'], rotate.inputs['Rotation'])
        tree.links.new(rotate.outputs['Vector'], mapping.inputs['Vector'])
    for node in tree.nodes:
        if node.type == 'TEX_IMAGE' and not any(link.from_node == mapping for link in node.inputs['Vector'].links):
            tree.links.new(mapping.outputs['Vector'], node.inputs['Vector'])
    return True


def _measure(obj):
    """(eixo da espessura, {eixo: rótulo}) da peça no referencial do dono (o mesmo da janela de propriedades)."""
    from ..target import part_geometry
    from ..customize import finish
    if obj is None or obj.type != 'MESH':
        return None, {}
    corners = [tuple(c) for c in obj.bound_box]
    low = tuple(min(c[i] for c in corners) for i in range(3))
    high = tuple(max(c[i] for c in corners) for i in range(3))
    owner = finish.owner_of(obj)
    reference = owner.matrix_world.to_3x3().normalized() if owner is not None and owner is not obj else None
    try:
        measures = part_geometry.measure(low, high, obj.matrix_world, reference)
    except part_geometry.PartGeometryError:
        return None, {}
    return measures.thickness.axis, {f.axis: f.field for f in measures.face}


def _restore_legacy(obj):
    """M-05: a variante `<nome> ROTATED` volta ao material de origem (que ganha o grafo do giro)."""
    if obj.type != 'MESH':
        return
    materials = obj.data.materials
    for index, mat in enumerate(materials):
        if mat is not None and mat.name.endswith(ROTATED_SUFFIX):
            base = bpy.data.materials.get(mat.name[:-len(ROTATED_SUFFIX)])
            if base is not None and is_image_material(base):
                materials[index] = base


def image_materials(obj):
    if obj.type != 'MESH':
        return []
    from ..customize.adapters import common
    out = [m for m in obj.data.materials if m is not None and is_image_material(m)]
    mod = common.gn_modifier(obj, 'GeoNodeCutpart')
    if mod is not None:
        from .. import compat
        for socket in ('Top Surface', 'Bottom Surface'):
            mat = compat.get_gn_input(mod, socket)
            if mat is not None and is_image_material(mat) and mat not in out:
                out.append(mat)
    return out


def sync(obj):
    """Grava o giro do veio da peça e liga o grafo nos materiais de imagem dela; devolve o giro gravado."""
    part = getattr(obj, 'btm_part', None)
    if obj is None or part is None:
        return gc.ZERO
    if part.grain != 'NONE':
        _restore_legacy(obj)
    materials = image_materials(obj)
    mat = materials[0] if materials else None
    thickness, fields = _measure(obj)
    value = gc.rotation(part.grain, thickness, fields, image_axis(mat), projection(mat)) if mat is not None \
        else gc.ZERO
    for material in materials:
        ensure_graph(material)
    if tuple(obj.get(ATTR, gc.ZERO)) != tuple(value) or ATTR not in obj:
        obj[ATTR] = list(value)
        obj.update_tag()                    # propriedade customizada não avisa o depsgraph sozinha
    return value
