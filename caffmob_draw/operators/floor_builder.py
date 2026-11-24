import json

import bmesh  # type: ignore
import bpy  # type: ignore
from mathutils import Matrix, Vector  # type: ignore

from ..data.i18n import tr
from ..geometry import floor_outline
from ..geometry.mesh_gen import generate_floor_mesh
from ..data import units


def scene_walls(scene):
    """Paredes reais da cena: do Home Builder 5 (`IS_WALL_BP`) e da camada nova (com `btm_wall_segments`).

    Não usa `btm_plane.object_kind == 'WALL'`, que é o valor padrão de todo objeto (BUG-20261007-A2G7).
    """
    hb, layer = [], []
    for obj in scene.objects:
        if obj.get('caffmob_parede'):
            continue
        if obj.get('IS_WALL_BP'):
            hb.append(obj)
        elif obj.type == 'MESH' and obj.get("btm_wall_segments"):
            layer.append(obj)
    return hb, layer


def _hb_thickness(wall):
    from .. import compat
    for mod in wall.modifiers:
        if mod.type == 'NODES' and mod.node_group:
            value = compat.try_get_gn_input(mod, 'Thickness')
            if value is not None:
                return float(value)
    return 0.0


def _layer_segments(obj):
    try:
        raw = json.loads(obj.get("btm_wall_segments", ""))
    except (TypeError, ValueError):
        return []
    world = obj.matrix_world
    segments = []
    for seg in raw:
        a = world @ Vector((float(seg['start'][0]), float(seg['start'][1]), 0.0))
        b = world @ Vector((float(seg['end'][0]), float(seg['end'][1]), 0.0))
        segments.append({'start': (a.x, a.y), 'end': (b.x, b.y), 'thickness': float(seg.get('thickness', 0.15)),
                         'height': float(seg.get('height', 2.6))})
    return segments


def room_outlines(scene):
    """(polígonos das salas pela face interna, pontas das paredes); os polígonos em ordem anti-horária."""
    from .walls import find_wall_chains, get_room_boundary_points, get_wall_endpoints, is_closed_loop
    hb, layer = scene_walls(scene)
    polygons, ends = [], []
    if hb:
        for chain in find_wall_chains():
            points = get_room_boundary_points(chain)
            for wall in chain:
                ends.extend(get_wall_endpoints(wall))
            if len(points) >= 4 and is_closed_loop(points):
                nodes = [(p.x, p.y) for p in points[:-1]]
                polygons.append(floor_outline.hb_loop_inner(nodes, [_hb_thickness(w) for w in chain]))
    segments = [seg for obj in layer for seg in _layer_segments(obj)]
    polygons.extend(floor_outline.segments_inner_loops(segments))
    ends.extend(p for seg in segments for p in (seg['start'], seg['end']))
    return polygons, [tuple(p[:2]) for p in ends]


def build_floor_mesh(floor_obj, polygons, thickness=0.0, direction='DOWN'):
    """Um n-gono por sala (aceita sala côncava), com espessura opcional para baixo (−Z) ou para cima (+Z) (RN-05, RF-06)."""
    from ..data import layers

    bm = bmesh.new()
    if thickness and float(thickness) > 1e-4:
        z_min, z_max = layers.floor_z_bounds(0.0, float(thickness), direction)
        for polygon in polygons:
            bottom = [bm.verts.new((x, y, z_min)) for x, y in polygon]
            top = [bm.verts.new((x, y, z_max)) for x, y in polygon]
            try:
                bm.faces.new(top)
                bm.faces.new(list(reversed(bottom)))
            except ValueError:
                continue
            n = len(polygon)
            for i in range(n):
                j = (i + 1) % n
                try:
                    bm.faces.new([bottom[i], bottom[j], top[j], top[i]])
                except ValueError:
                    pass
        floor_obj['btm_floor_thickness'] = float(thickness)
        floor_obj['btm_floor_direction'] = str(direction).upper()
    else:
        for polygon in polygons:
            verts = [bm.verts.new((x, y, 0.0)) for x, y in polygon]
            try:
                bm.faces.new(verts)
            except ValueError:
                continue
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(floor_obj.data)
    bm.free()
    floor_obj.data.update()
    floor_obj.matrix_world = Matrix.Identity(4)


class BTM_OT_AdjustFloor(bpy.types.Operator):
    """Ajusta o piso à face interna das paredes do ambiente"""
    bl_idname = "caffmob.adjust_floor"
    bl_label = "Ajustar Limites do Piso"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        hb, layer = scene_walls(context.scene)
        return bool(hb or layer or any(o.get("caffmob_parede") for o in context.scene.objects))

    def execute(self, context):
        # (063 D-10) O piso do contrato vem antes das salas das outras fontes.
        from ..mobi.cena import regenerar_parede
        contratos = [o for o in context.scene.objects if o.get("caffmob_parede")]
        for obj in contratos:
            regenerar_parede(context, obj, json.loads(obj["caffmob_parede"]),
                             json.loads(obj.get("caffmob_aberturas", "[]")))
        hb, layer = scene_walls(context.scene)
        if contratos and not (hb or layer):
            self.report({'INFO'}, tr("Piso atualizado pelo contrato do MOBI"))
            return {'FINISHED'}
        polygons, ends = room_outlines(context.scene)
        if not polygons:
            rect = floor_outline.bounding_rect(ends)
            if rect is None:
                self.report({'WARNING'}, "Nenhuma parede encontrada na cena.")
                return {'CANCELLED'}
            polygons = [rect]
            message = tr("Nenhuma sala fechada: piso pelo retângulo das paredes.")
        else:
            message = tr("Piso ajustado à face interna das paredes ({} sala(s)).").format(len(polygons))

        # Encontra ou cria o piso
        floor_obj = None
        for obj in context.scene.objects:
            if not obj.get('caffmob_tipo') and hasattr(obj, 'btm_plane') and obj.btm_plane.object_kind == 'FLOOR':
                floor_obj = obj
                break

        from ..data import layers
        if floor_obj is None:
            mesh = bpy.data.meshes.new(name="BTM_Floor_Mesh")
            floor_obj = bpy.data.objects.new("BTM_Floor", mesh)
            floor_obj.btm_plane.object_kind = 'FLOOR'

        layers.place(floor_obj, layers.ensure_arquitetura(context.scene, 'FLOOR'), context.scene)
        settings = getattr(context.scene, 'btm_settings', None)
        thickness = getattr(settings, 'floor_thickness', 0.15) if settings else 0.15
        direction = getattr(settings, 'floor_thickness_direction', 'DOWN') if settings else 'DOWN'
        build_floor_mesh(floor_obj, polygons, thickness=thickness, direction=direction)
        context.view_layer.objects.active = floor_obj
        floor_obj.select_set(True)
        self.report({'INFO'}, message)
        return {'FINISHED'}


class BTM_OT_FloorBuilder(bpy.types.Operator):
    """Cria o piso base para o ambiente 3D (modo manual)"""
    bl_idname = "caffmob.floor_builder"
    bl_label = "Criar Piso Manual"
    bl_options = {'REGISTER', 'UNDO'}

    size_x: bpy.props.FloatProperty(name="Largura X", default=5.0, subtype='DISTANCE')
    size_y: bpy.props.FloatProperty(name="Comprimento Y", default=5.0, subtype='DISTANCE')

    def execute(self, context):
        from ..data import layers
        mesh = bpy.data.meshes.new(name="BTM_Floor_Mesh")
        obj = bpy.data.objects.new("BTM_Floor", mesh)

        layers.place(obj, layers.ensure_arquitetura(context.scene, 'FLOOR'), context.scene)
        context.view_layer.objects.active = obj
        obj.select_set(True)

        obj.btm_plane.object_kind = 'FLOOR'

        settings = getattr(context.scene, 'btm_settings', None)
        thickness = getattr(settings, 'floor_thickness', 0.15) if settings else 0.15
        direction = getattr(settings, 'floor_thickness_direction', 'DOWN') if settings else 'DOWN'
        hx, hy = self.size_x * 0.5, self.size_y * 0.5
        build_floor_mesh(obj, [[(-hx, -hy), (hx, -hy), (hx, hy), (-hx, hy)]], thickness=thickness, direction=direction)

        x_str = units.format_value(self.size_x, context.scene)
        y_str = units.format_value(self.size_y, context.scene)
        self.report({'INFO'}, tr("Piso base criado: {} x {}").format(x_str, y_str))
        return {'FINISHED'}
