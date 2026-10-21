"""Adoção explícita preserva malha, materiais, hierarquia e matriz de mundo (RF-090/RF-091)."""
import bpy  # type: ignore
from .. import stable_id
from . import region


def controller_for(obj):
    if obj is None:
        return None
    if obj.btm_cladding.uid:
        return obj
    mark = obj.get('btm_cladding_piece')
    if mark:
        return next((o for o in bpy.context.scene.objects if o.btm_cladding.uid == mark.get('owner')), None)
    return None


def create(host, origin=(0, 0, 0), normal=(0, -1, 0), axis_u=(1, 0, 0)):
    # Validar o plano antes de criar qualquer dado.
    basis = region.frame(host, origin, normal, axis_u)
    root = bpy.data.objects.new('Revestimento', None)
    bpy.context.collection.objects.link(root)
    root.empty_display_type = 'PLAIN_AXES'
    root.empty_display_size = .15
    root.matrix_world = basis
    data = root.btm_cladding
    data.uid = stable_id.new_uid()
    data.host = host
    data.plane_origin, data.plane_normal, data.plane_u = origin, normal, axis_u
    return root


def adopt(objects, host, origin=(0, 0, 0), normal=(0, -1, 0), axis_u=(1, 0, 0)):
    objects = list(objects)
    if not objects or any(o.type != 'MESH' or o == host or o.get('btm_cladding_piece') for o in objects):
        raise ValueError('Selecione malhas sem vínculo e uma face hospedeira distinta')
    root = create(host, origin, normal, axis_u)
    # Revestimento adotado é manual. Sincronizar não o converte nem gera uma segunda camada sobre ele.
    root['btm_cladding_adopted'] = True
    for index, obj in enumerate(objects):
        obj['btm_cladding_piece'] = dict(owner=root.btm_cladding.uid, key=f'MANUAL:{index}', generated=False)
        obj.btm_plane.collision_override = 'OFF'
    return root


def reassociate(root, host, origin, normal, axis_u):
    region.frame(host, origin, normal, axis_u)
    data = root.btm_cladding
    data.host = host
    data.plane_origin, data.plane_normal, data.plane_u = origin, normal, axis_u
    data.link_missing = False
    data.diagnostic = ''
    data.params_hash = ''
