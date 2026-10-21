"""Pacote autoral fechado e remapeamento de identidade (066, T057/T058)."""

from contextlib import contextmanager

from ..stable_id import remap


def remap_block(block):
    """Renova a identidade do manifesto e todas as suas referências, sem alterar a origem."""
    import copy
    result = copy.deepcopy(block)
    mapping = remap([block['uid']] + [m['uid'] for m in block['members']])
    result['uid'] = mapping[block['uid']]
    for member in result['members']:
        member['uid'] = mapping[member['uid']]
        member['refs'] = [mapping[uid] for uid in member['refs']]
    for entry in result['leaves']:
        entry['uid'] = mapping[entry['uid']]
        entry['members'] = [mapping[uid] for uid in entry['members']]
        entry['pivot_uid'] = mapping[entry['pivot_uid']]
    return result, mapping


@contextmanager
def closed(context, root):
    """Fecha sem colisão durante o pacote e restaura exatamente as matrizes e valores, inclusive em falha."""
    from ..aggregates import leaf
    from ..collision import guard
    from ..aggregates.apply import _write
    objects = [root] + list(root.children_recursive)
    state = [(o, o.matrix_basis.copy(), o.btm_aggregate.open_value,
              o.get(leaf.OPEN_KEY), leaf.OPEN_KEY in o) for o in objects]
    with guard.suspended():
        try:
            for obj in objects:
                if obj.btm_aggregate.is_aggregate and obj.btm_aggregate.kind == 'LEAF':
                    _write(obj, 'open_value', 0.0)
                    leaf.apply_fraction(obj, 0.0)
            context.view_layer.update()
            yield
        finally:
            for obj, matrix, value, fraction, existed in state:
                _write(obj, 'open_value', value)
                if existed:
                    obj[leaf.OPEN_KEY] = fraction
                elif leaf.OPEN_KEY in obj:
                    del obj[leaf.OPEN_KEY]
                if obj.matrix_basis != matrix:
                    obj.matrix_basis = matrix
            context.view_layer.update()


def build(root):
    from ..aggregates import leaf, ops_authored
    objects = [root] + list(root.children_recursive)
    external = ops_authored.external_references(objects)
    inside = set(objects)
    for obj in objects:
        for ref in obj.btm_member.refs:
            if ref.target is not None and ref.target not in inside:
                external.append((obj, 'Regra', ref.target))
        for constraint in obj.constraints:
            target = getattr(constraint, 'target', None)
            if target is not None and target not in inside:
                external.append((obj, 'Restrição', target))
    if external:
        raise ValueError('; '.join('{}: {} → {}'.format(o.name, kind, target.name)
                                   for o, kind, target in external))
    members, leaves = [], []
    for obj in objects:
        if obj == root:
            continue
        data = obj.btm_member
        if data.owner != root or not data.uid:
            raise ValueError('Membro sem identidade ou dono: ' + obj.name)
        members.append({'uid': data.uid, 'role': data.role, 'rule': data.rule,
                        'refs': [ref.target.btm_member.uid if ref.target else ref.uid for ref in data.refs],
                        'params': {'axis': data.axis, 'offset_mm': data.offset_mm, 'count': data.count,
                                   'faces': [ref.face for ref in data.refs]}})
        agg = obj.btm_aggregate
        if agg.is_aggregate and agg.kind == 'LEAF':
            pivot = leaf.pivot_of(obj)
            matrix = leaf.front_frame(agg.parent_ref) @ leaf.rest_matrix(obj)
            leaves.append({'uid': data.uid, 'members': [o.btm_member.uid for o in [obj] + list(obj.children_recursive)],
                           'construction': agg.construction,
                           'motion': 'FLIP' if agg.motion == 'SWING' and agg.hinge in ('TOP', 'BOTTOM') else agg.motion,
                           'hinge': agg.hinge, 'sign': agg.swing_sign, 'max_angle': agg.max_angle,
                           'travel_mm': agg.travel * 1000 if agg.motion == 'SLIDE' else None,
                           'pivot_uid': pivot.btm_member.uid,
                           'rest_matrix_parent': [list(row) for row in matrix]})
    data = root.btm_authored
    axis = {'NEG_Y': '-Y', 'POS_Y': '+Y', 'NEG_X': '-X', 'POS_X': '+X'}[data.front_axis]
    return {'uid': data.uid, 'asset_version': max(1, data.asset_version), 'front_axis': axis,
            'size_local_mm': list(ops_authored.local_size(root, objects)), 'members': members,
            'leaves': leaves, 'external_refs': []}


def renew(root, block):
    from ..aggregates import leaf
    from ..aggregates.apply import _write
    objects = [root] + list(root.children_recursive)
    by_uid = {o.btm_member.uid: o for o in objects if o != root}
    if (len(by_uid) != len(objects) - 1 or set(by_uid) != {m['uid'] for m in block['members']}
            or root.btm_authored.uid != block['uid']):
        raise ValueError('Identidades do arquivo não correspondem ao manifesto')
    result, mapping = remap_block(block)
    root.btm_authored.uid = result['uid']
    root.btm_authored.asset_uid = block['uid']
    root.btm_authored.asset_version = block['asset_version']
    root.btm_authored.size_local = block['size_local_mm']
    for member in block['members']:
        obj = by_uid[member['uid']]
        obj.btm_member.uid = mapping[member['uid']]
        obj.btm_member.owner = root
        for ref in obj.btm_member.refs:
            old = ref.uid
            # O ponteiro remapeado pelo append também é conferido contra o manifesto.
            if old not in mapping:
                raise ValueError('Referência ausente no pacote')
            ref.target = by_uid[old]
            ref.uid = mapping[old]
    for entry in block['leaves']:
        obj = by_uid[entry['uid']]
        obj.btm_aggregate.pivot = by_uid[entry['pivot_uid']]
        _write(obj, 'open_value', 0.0)
        leaf.apply_fraction(obj, 0.0)


@contextmanager
def packed_images(root):
    """O asset leva as imagens locais; REMOVE desfaz só o pacote em memória, sem escrever no disco."""
    images = set()
    for obj in [root] + list(root.children_recursive):
        for slot in obj.material_slots:
            tree = slot.material.node_tree if slot.material else None
            if tree:
                images.update(n.image for n in tree.nodes if n.type == 'TEX_IMAGE' and n.image)
    packed = []
    try:
        for img in images:
            if not img.packed_file and img.source == 'FILE':
                img.pack()
                packed.append(img)
        yield
    finally:
        for img in packed:
            img.unpack(method='REMOVE')
