import bpy  # type: ignore
from ..data.i18n import tr
from ..geometry.mesh_gen import generate_cabinet_mesh
from ..geometry import door_controller
from ..data import units

_TYPE_ITEMS = [('BASE', "Balcão", ""), ('WALL', "Aéreo", ""), ('TALL', "Torre", "")]
_LINE_ITEMS = [('COZ', "Cozinha", ""), ('DOR', "Dormitório", ""), ('BAN', "Banheiro", ""), ('SAL', "Sala", ""),
               ('ESC', "Escritório", "")]
_ASSEMBLY_ITEMS = [('LATERAL', "Lateral passante", ""), ('BASE', "Base passante", "")]
_SWING_ITEMS = [('NONE', "Sem porta", ""), ('LEFT', "Porta à esquerda", ""), ('RIGHT', "Porta à direita", ""),
                ('DOUBLE', "Duas portas", ""), ('FLIP', "Basculante", "")]
_ROLE_PROPS = {'TOP': 'thickness_top', 'BOTTOM': 'thickness_bottom', 'BACK': 'thickness_back',
               'LEFT': 'thickness_left', 'RIGHT': 'thickness_right'}


def standard_defaults(context, line, cabinet_type):
    """Medidas do Padrão de Dimensões ativo para a linha e o tipo (`standards/cabinet_defaults`), e o padrão."""
    from ..standards import api, cabinet_defaults
    definition = api.active_definition(context.scene) if hasattr(context.scene, "btm_standards") else None
    values = api.definition_values(definition) if definition is not None else None
    return cabinet_defaults.defaults(values, line, cabinet_type), definition


def build_module(context, *, width, height, depth, carcass, cabinet_type, line, assembly, door_swing, shelves,
                 role_thickness, definition=None, collection=None, location=None):
    """Cria o módulo CAFFMob (malha, portas e marcas); devolve o objeto. Usado pelo operador e pela conversão."""
    mesh = bpy.data.meshes.new(name="BTM_Cabinet_Mesh")
    obj = bpy.data.objects.new("BTM_Cabinet", mesh)
    (collection or context.collection).objects.link(obj)
    obj.btm_plane.object_kind = 'MODULE'
    cab = obj.btm_cabinet
    from ..data.properties import back_setback_of, structure_of, suspended_geometry
    with suspended_geometry():
        cab.width, cab.height, cab.depth, cab.thickness = width, height, depth, carcass
        cab.cabinet_type = cabinet_type
        cab.line = line
        cab.assembly = assembly
        cab.door_open = 0.0
        cab.door_swing = door_swing
        cab.shelves = shelves
        for role, prop in _ROLE_PROPS.items():
            value = role_thickness.get(role, carcass)
            setattr(cab, prop, 0.0 if abs(value - carcass) < 1e-9 else value)   # 0 = segue a chapa da caixa
    obj['btm_line'] = line
    if definition is not None:
        obj['btm_standard_uid'] = definition.uid
    if location is not None:
        obj.location = location
    generate_cabinet_mesh(obj, width, height, depth, carcass, shelves, structure=structure_of(cab),
                          back_setback=back_setback_of(obj), assembly=assembly)
    door_controller.update_door_geometry_and_controller(obj)
    return obj


class BTM_OT_CabinetBuilder(bpy.types.Operator):
    """Cria um módulo de armário CAFFMob com as medidas, as chapas e a montagem do Padrão de Dimensões"""
    bl_idname = "caffmob.cabinet_builder"
    bl_label = "Inserir Armário"
    bl_options = {'REGISTER', 'UNDO'}

    # Feature 012 (T026; D-11): os valores abaixo só valem quando o chamador os passa; os que não forem passados vêm
    # do padrão ativo (`standards/cabinet_defaults`, com fallback nomeado lá). Nada de medida fixa aqui.
    width: bpy.props.FloatProperty(name="Largura", default=0.8, min=0.1, subtype='DISTANCE')  # type: ignore
    height: bpy.props.FloatProperty(name="Altura", default=0.72, min=0.1, subtype='DISTANCE')  # type: ignore
    depth: bpy.props.FloatProperty(name="Profundidade", default=0.55, min=0.1, subtype='DISTANCE')  # type: ignore
    thickness: bpy.props.FloatProperty(name="Espessura MDF", default=0.018, min=0.006, subtype='DISTANCE')  # type: ignore
    cabinet_type: bpy.props.EnumProperty(name="Tipo", items=_TYPE_ITEMS, default='BASE')  # type: ignore
    line: bpy.props.EnumProperty(name="Linha", items=_LINE_ITEMS, default='COZ')  # type: ignore
    assembly: bpy.props.EnumProperty(name="Montagem", items=_ASSEMBLY_ITEMS, default='LATERAL')  # type: ignore
    door_swing: bpy.props.EnumProperty(name="Frente", items=_SWING_ITEMS, default='LEFT')  # type: ignore
    shelves: bpy.props.IntProperty(name="Prateleiras", default=0, min=0, max=20)  # type: ignore

    def _given(self, name):
        return self.properties.is_property_set(name)

    def invoke(self, context, event):
        return self.execute(context)

    def execute(self, context):
        from ..standards import api
        found, definition = standard_defaults(context, self.line, self.cabinet_type)
        if found.warning:
            self.report({'WARNING'}, found.warning)
        width = self.width if self._given('width') else found.width
        height = self.height if self._given('height') else found.height
        depth = self.depth if self._given('depth') else found.depth
        carcass = self.thickness if self._given('thickness') else found.carcass
        assembly = self.assembly if self._given('assembly') else api.active_assembly(context.scene)

        cursor = context.scene.cursor.location.copy()
        if self.cabinet_type == 'WALL' and abs(cursor.z) < 1e-9:
            cursor.z = found.z                    # aéreo na altura de instalação do padrão
        obj = build_module(context, width=width, height=height, depth=depth, carcass=carcass,
                           cabinet_type=self.cabinet_type, line=self.line, assembly=assembly,
                           door_swing=self.door_swing, shelves=self.shelves, role_thickness=found.thickness,
                           definition=definition, location=cursor)
        for other in context.selected_objects:
            other.select_set(False)
        context.view_layer.objects.active = obj
        obj.select_set(True)

        w_str = units.format_value(width, context.scene)
        h_str = units.format_value(height, context.scene)
        d_str = units.format_value(depth, context.scene)
        self.report({'INFO'}, tr("Módulo de Armário inserido: {} x {} x {}").format(w_str, h_str, d_str))
        return {'FINISHED'}
