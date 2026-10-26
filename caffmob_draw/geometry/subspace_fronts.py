"""Frentes do módulo rápido por vão (feature 067, T073, T074; D-23; RF-103, RF-104).

O módulo rápido tem as portas do construtor (`door_controller`, pelo `btm_cabinet.door_swing`) para o módulo
inteiro. Além delas, cada vão pode ter frentes próprias, geradas aqui no retângulo do vão (o módulo inteiro, caminho
`module`, ou um subvão do editor, caminho `s0/…`):
- portas (esquerda, direita, duas, basculante) e gavetas reais, como folhas agregadas do módulo (`aggregates/leaf`),
  com o mecanismo pelos dados (dobradiça, `DRAWER` para a gaveta), nunca pelo nome;
- a gaveta é a frente e uma caixa de verdade (fundo, laterais e traseira), que corre em profundidade junto com ela.
  Com o spec do construtor de gavetas (072, `gaveta` no pedido), a caixa sai do núcleo `drawers.core` com a corrediça
  escolhida e as peças do plano de corte; pedido sem `gaveta` (arquivos anteriores) segue a caixa simples de antes.

O pedido de cada vão fica gravado na raiz (`btm_space_fronts`, JSON `{caminho: {front, count}}`) e o vão do editor
tem um vazio escondido (`btm_space_path`) que o adaptador usa como vão da biblioteca. Refazer um vão não mexe nas
frentes de outro; depois do rebuild do módulo, `rebuild_all` refaz todas pelas medidas novas.
"""

import json

import bpy  # type: ignore
from mathutils import Matrix  # type: ignore

from .mesh_gen import generate_door_mesh

SPEC_PROP = 'btm_space_fronts'
PATH_PROP = 'btm_space_path'
HOLDER_PROP = 'btm_space_holder'
MARGIN = 0.002
MAX_DRAWERS = 8
SUPPORTED = ('DOOR_LEFT', 'DOOR_RIGHT', 'DOUBLE_DOORS', 'FLIP_UP', 'DRAWERS', 'OPEN')


def specs(root):
    try:
        data = json.loads(root.get(SPEC_PROP, "{}"))
    except (TypeError, ValueError):
        return {}
    return data if isinstance(data, dict) else {}


def _save(root, data):
    root[SPEC_PROP] = json.dumps(data, sort_keys=True)


def fronts_of(root, path):
    """As frentes geradas do vão (as folhas, com as caixas e pivôs delas)."""
    return [o for o in root.children_recursive if o.get(PATH_PROP) == path and not o.get(HOLDER_PROP)]


def holder(root, path, create=True):
    """O vazio escondido do vão (o vão da biblioteca que o editor endereça)."""
    for obj in root.children:
        if obj.get(HOLDER_PROP) and obj.get(PATH_PROP) == path:
            return obj
    if not create:
        return None
    obj = bpy.data.objects.new(f"{root.name} vão {path}", None)
    for collection in root.users_collection or (bpy.context.collection,):
        collection.objects.link(obj)
        break
    obj.parent = root
    obj.empty_display_size = 0.01
    obj.hide_viewport = obj.hide_render = True
    obj[HOLDER_PROP] = True
    obj[PATH_PROP] = path
    return obj


def holders(root):
    return [o for o in root.children if o.get(HOLDER_PROP)]


def clear(root, path):
    from ..aggregates import leaf
    names = [o.name for o in fronts_of(root, path)]
    for name in names:
        obj = bpy.data.objects.get(name)
        if obj is None:                            # já saiu junto com a frente dona (a caixa da gaveta)
            continue
        pivot = leaf.pivot_of(obj) if getattr(obj, 'btm_aggregate', None) is not None else None
        pivot_name = pivot.name if pivot is not None else None
        for child_name in [c.name for c in obj.children_recursive]:
            child = bpy.data.objects.get(child_name)
            if child is not None:
                bpy.data.objects.remove(child, do_unlink=True)
        bpy.data.objects.remove(obj, do_unlink=True)
        if pivot_name and bpy.data.objects.get(pivot_name) is not None:
            bpy.data.objects.remove(bpy.data.objects[pivot_name], do_unlink=True)


def _panel(root, name, width, height, thickness, location, path, role, hinge=None):
    mesh = bpy.data.meshes.new(name)
    obj = bpy.data.objects.new(name, mesh)
    for collection in root.users_collection or (bpy.context.collection,):
        collection.objects.link(obj)
        break
    generate_door_mesh(obj, width, height, thickness)
    obj.parent = root
    obj.matrix_parent_inverse = Matrix.Identity(4)
    obj.location = location
    obj[PATH_PROP] = path
    obj['hb_part_role'] = role
    if hinge:
        obj['btm_front_hinge'] = hinge
    return obj


def _drawer_box(root, front, width, height, depth, thickness, path):
    """Caixa real da gaveta (fundo, duas laterais e traseira), filha da frente: corre junto com ela."""
    import bmesh  # type: ignore
    mesh = bpy.data.meshes.new(front.name + " caixa")
    box = bpy.data.objects.new(front.name + " caixa", mesh)
    for collection in front.users_collection:
        collection.objects.link(box)
        break
    bm = bmesh.new()
    t = thickness
    inset = 0.013                                  # folga da corrediça em cada lado
    x0, x1, z0, z1 = inset, width - inset, 0.02, max(0.04, height - 0.03)
    y0, y1 = t, t + depth
    for lo, hi in (((x0, y0, z0), (x1, y1, z0 + t)), ((x0, y0, z0), (x0 + t, y1, z1)),
                   ((x1 - t, y0, z0), (x1, y1, z1)), ((x0, y1 - t, z0), (x1, y1, z1))):
        verts = [bm.verts.new(co) for co in ((lo[0], lo[1], lo[2]), (hi[0], lo[1], lo[2]), (hi[0], hi[1], lo[2]),
                                              (lo[0], hi[1], lo[2]), (lo[0], lo[1], hi[2]), (hi[0], lo[1], hi[2]),
                                              (hi[0], hi[1], hi[2]), (lo[0], hi[1], hi[2]))]
        for a, b, c, d in ((0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)):
            bm.faces.new((verts[a], verts[b], verts[c], verts[d]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(mesh)
    bm.free()
    box.parent = front
    box.matrix_parent_inverse = Matrix.Identity(4)
    box[PATH_PROP] = path
    box['hb_part_role'] = 'CLOSET_DRAWER_BOX'
    return box


def _leaf(obj, root, motion, hinge='LEFT', travel=0.4):
    from ..aggregates import leaf
    bpy.context.view_layer.update()
    leaf.make_leaf(obj, root, motion=motion, hinge=hinge, travel=travel)


def _especificacoes(gaveta, gavetas, n):
    """Spec de cada gaveta do vão: a lista própria (troca de corrediça por gaveta) ou o spec do vão."""
    from ..drawers import core
    base = core.Gaveta.de_dict(gaveta) if gaveta else None
    lista = list(gavetas or [])
    return [core.Gaveta.de_dict(lista[i]) if i < len(lista) and lista[i] else base for i in range(n)]


def _validar_gavetas(box, specs_, alturas):
    from ..drawers import build as drawer_build, catalogo, core
    lo, hi = box
    espaco = core.Espaco((hi[0] - lo[0]) * 1000, (hi[2] - lo[2]) * 1000, (hi[1] - lo[1]) * 1000)
    pasta = drawer_build.pasta_do_usuario()
    for g, h in zip(specs_, alturas):
        if g is None:
            continue
        motivos = core.motivos(espaco, g, catalogo.por_id(g.corredica, pasta), h * 1000)
        if motivos:
            return espaco, motivos
    return espaco, []


def build(root, path, box, front, count=1, gaveta=None, gavetas=None):
    """Refaz as frentes do vão `path` no retângulo `box` (lo, hi no referencial da raiz); devolve mensagens.

    `gaveta` é o spec do construtor (072) para todas as gavetas do vão; `gavetas`, a lista por gaveta (troca de
    corrediça de uma só). Sem eles, a gaveta sai com a caixa simples de antes.
    """
    from ..data.i18n import tr
    if front not in SUPPORTED:
        return [tr("O módulo paramétrico não tem a frente '{}'").format(front)]
    if front == 'DRAWERS' and not 1 <= int(count) <= MAX_DRAWERS:
        return [tr("Quantidade de gavetas fora de 1 a {}").format(MAX_DRAWERS)]
    if front == 'DRAWERS' and (gaveta or gavetas):
        n = int(count)
        alturas = [((box[1][2] - box[0][2]) - 2 * MARGIN - MARGIN * (n - 1)) / n] * n
        _espaco, motivos = _validar_gavetas(box, _especificacoes(gaveta, gavetas, n), alturas)
        if motivos:
            return motivos
    clear(root, path)
    data = specs(root)
    if front == 'OPEN':
        data.pop(path, None)
        _save(root, data)
        return []
    cab = root.btm_cabinet
    t = cab.thickness
    lo, hi = box
    x0, x1, z0, z1 = lo[0] + MARGIN, hi[0] - MARGIN, lo[2] + MARGIN, hi[2] - MARGIN
    width, height = x1 - x0, z1 - z0
    front_y = -cab.depth - t                       # face externa da frente fechada (como em `door_controller`)
    depth = max(0.1, (hi[1] - lo[1]) - 0.03)
    label = f"{root.name} {path}"
    if front == 'DRAWERS':
        n = int(count)
        gap = MARGIN
        each = (height - gap * (n - 1)) / n
        especs = _especificacoes(gaveta, gavetas, n)
        for i in range(n):
            z = z0 + i * (each + gap)
            g = especs[i]
            if g is None:
                panel = _panel(root, f"{label} gaveta {i + 1}", width, each, t, (x0, front_y, z), path, 'DRAWER_FRONT')
                _drawer_box(root, panel, width, each, depth, t, path)
                _leaf(panel, root, 'DRAWER', travel=depth * 0.8)
                continue
            tf = g.frente_espessura / 1000
            panel = _panel(root, f"{label} gaveta {i + 1}", width, each, tf, (x0, -cab.depth - tf, z), path,
                           'DRAWER_FRONT')
            panel['btm_drawer_index'] = i
            from ..drawers import build as drawer_build, core
            caixa = drawer_build.aplicar(panel, core.Espaco((hi[0] - lo[0]) * 1000, each * 1000, (hi[1] - lo[1]) * 1000),
                                         g, each * 1000, MARGIN * 1000, g.frente_espessura)
            for filho in panel.children:
                filho[PATH_PROP] = path
            _leaf(panel, root, 'DRAWER', travel=caixa.comprimento / 1000)
    elif front == 'DOUBLE_DOORS':
        half = (width - MARGIN) / 2.0
        for side, x, hinge in (('L', x0, 'LEFT'), ('R', x0 + half + MARGIN, 'RIGHT')):
            panel = _panel(root, f"{label} porta {side}", half, height, t, (x, front_y, z0), path, 'DOOR', side)
            _leaf(panel, root, 'SWING', hinge)
    elif front == 'FLIP_UP':
        panel = _panel(root, f"{label} basculante", width, height, t, (x0, front_y, z0), path, 'TILT_OUT', 'FLIP')
        _leaf(panel, root, 'SWING', 'TOP')
    else:
        side, hinge = ('L', 'LEFT') if front == 'DOOR_LEFT' else ('R', 'RIGHT')
        panel = _panel(root, f"{label} porta", width, height, t, (x0, front_y, z0), path, 'DOOR', side)
        _leaf(panel, root, 'SWING', hinge)
    data[path] = {'front': front, 'count': int(count) if front == 'DRAWERS' else 1, 'box': _key(box)}
    if front == 'DRAWERS' and gaveta:
        data[path]['gaveta'] = gaveta
    if front == 'DRAWERS' and gavetas:
        data[path]['gavetas'] = list(gavetas)
    _save(root, data)
    return []


def _key(box):
    return [[round(v, 5) for v in box[0]], [round(v, 5) for v in box[1]]]


def front_type(root, path):
    item = specs(root).get(path)
    if not item:
        return None
    return item.get('front', 'OPEN'), int(item.get('count', 1)) if item.get('front') == 'DRAWERS' else 0


def rebuild_all(root, boxes):
    """Depois do rebuild do módulo: refaz cada vão gravado com o retângulo novo (`boxes` = {caminho: (lo, hi)})."""
    messages = []
    for path, item in sorted(specs(root).items()):
        box = boxes.get(path)
        if box is None or item.get('box') == _key(box):
            continue                              # vão do mesmo tamanho: as frentes (e a abertura delas) ficam
        messages += build(root, path, box, item.get('front', 'OPEN'), item.get('count', 1), item.get('gaveta'),
                          item.get('gavetas'))
    return messages
