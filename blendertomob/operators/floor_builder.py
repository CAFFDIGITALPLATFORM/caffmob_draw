import bpy  # type: ignore
from ..geometry.mesh_gen import generate_floor_from_walls, generate_floor_mesh
from ..data import units


class BTM_OT_AdjustFloor(bpy.types.Operator):
    """Ajusta os limites do piso para acompanhar o contorno das paredes"""
    bl_idname = "btm.adjust_floor"
    bl_label = "Ajustar Limites do Piso"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return any(
            obj.btm_plane.object_kind == 'WALL'
            for obj in context.scene.objects
            if hasattr(obj, 'btm_plane')
        )

    def execute(self, context):
        # Coleta todas as paredes
        wall_objects = [
            obj for obj in context.scene.objects
            if hasattr(obj, 'btm_plane') and obj.btm_plane.object_kind == 'WALL'
        ]

        if not wall_objects:
            self.report({'WARNING'}, "Nenhuma parede encontrada na cena.")
            return {'CANCELLED'}

        # 061: parede do contrato tem o piso pelo polígono real da face interna, gerado com ela.
        do_contrato = [obj for obj in wall_objects if obj.get("caffmob_parede")]
        if do_contrato:
            import json
            from .caffmob_sync import regenerar_parede
            for obj in do_contrato:
                regenerar_parede(context, obj, json.loads(obj["caffmob_parede"]), [])
            fechadas = sum(1 for obj in do_contrato if json.loads(obj["caffmob_parede"])["fechada"])
            self.report({'INFO'}, f"Piso pelo contorno interno de {fechadas} parede(s) fechada(s).")
            return {'FINISHED'}

        # Encontra ou cria o piso
        floor_obj = None
        for obj in context.scene.objects:
            if hasattr(obj, 'btm_plane') and obj.btm_plane.object_kind == 'FLOOR':
                floor_obj = obj
                break

        if floor_obj is None:
            mesh = bpy.data.meshes.new(name="BTM_Floor_Mesh")
            floor_obj = bpy.data.objects.new("BTM_Floor", mesh)
            context.collection.objects.link(floor_obj)
            floor_obj.btm_plane.object_kind = 'FLOOR'

        context.view_layer.objects.active = floor_obj
        floor_obj.select_set(True)

        success = generate_floor_from_walls(floor_obj, wall_objects)

        if success:
            self.report({'INFO'}, "Piso ajustado ao contorno das paredes.")
        else:
            self._generate_bounding_floor(floor_obj, wall_objects)
            self.report({'INFO'}, "Piso gerado com base no contorno geral das paredes.")

        return {'FINISHED'}

    def _generate_bounding_floor(self, floor_obj, wall_objects):
        min_x = float('inf')
        min_y = float('inf')
        max_x = float('-inf')
        max_y = float('-inf')

        for wall_obj in wall_objects:
            if wall_obj.type != 'MESH' or not wall_obj.data.vertices:
                continue
            for v in wall_obj.data.vertices:
                world_co = wall_obj.matrix_world @ v.co
                min_x = min(min_x, world_co.x)
                min_y = min(min_y, world_co.y)
                max_x = max(max_x, world_co.x)
                max_y = max(max_y, world_co.y)

        if min_x == float('inf'):
            generate_floor_mesh(floor_obj, 5.0, 5.0)
            return

        width = (max_x - min_x)
        depth = (max_y - min_y)

        # Adiciona pequena margem
        width = max(width, 0.5)
        depth = max(depth, 0.5)

        generate_floor_mesh(floor_obj, width, depth)

        # Centraliza o piso no ponto médio
        floor_obj.location.x = (min_x + max_x) / 2.0
        floor_obj.location.y = (min_y + max_y) / 2.0
        floor_obj.location.z = 0.0


class BTM_OT_FloorBuilder(bpy.types.Operator):
    """Cria o piso base para o ambiente 3D (modo manual)"""
    bl_idname = "btm.floor_builder"
    bl_label = "Criar Piso Manual"
    bl_options = {'REGISTER', 'UNDO'}

    size_x: bpy.props.FloatProperty(name="Largura X", default=5.0, subtype='DISTANCE')
    size_y: bpy.props.FloatProperty(name="Comprimento Y", default=5.0, subtype='DISTANCE')

    def execute(self, context):
        mesh = bpy.data.meshes.new(name="BTM_Floor_Mesh")
        obj = bpy.data.objects.new("BTM_Floor", mesh)

        context.collection.objects.link(obj)
        context.view_layer.objects.active = obj
        obj.select_set(True)

        obj.btm_plane.object_kind = 'FLOOR'

        generate_floor_mesh(obj, self.size_x, self.size_y)

        x_str = units.format_value(self.size_x, context.scene)
        y_str = units.format_value(self.size_y, context.scene)
        self.report({'INFO'}, f"Piso base criado: {x_str} x {y_str}")
        return {'FINISHED'}
