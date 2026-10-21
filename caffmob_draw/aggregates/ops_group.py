"""Operadores de grupo de peças e "Montar esquadria" (feature 007, T020, T021; RN-04 a RN-07a, D-03, D-06).

- `caffmob.group_create`: as malhas selecionadas viram um grupo (Empty) que se move junto.
- `caffmob.group_dissolve`: desfaz o grupo (se ele foi convertido, desconverte antes, voltando à pose do arquivo).
- `caffmob.window_assemble`: sugere os grupos pelo nome das peças (`grouping`), o projetista confirma ou muda o papel
  de cada um e o plugin cria a esquadria e as folhas (já convertidas) num passo de desfazer.
"""

import bpy  # type: ignore

from ..data.i18n import tr
from . import convert, group, grouping, leaf

ROLE_ITEMS = [('FRAME', "Esquadria", "Parte fixa"), ('SLIDE', "Folha de correr", "Desliza no trilho"),
              ('SWING', "Folha de giro", "Gira num eixo"), ('IGNORE', "Ignorar", "Fica solta")]


def _meshes(context):
    return [o for o in context.selected_objects if o.type in group.MEMBER_TYPES
            and not group.is_group(o) and not group.is_group(o.parent)]


def _import_groups(context):
    """Grupos simples selecionados (o OBJ importado vira um, feature 011 D-09): a esquadria se monta com as peças."""
    return [o for o in context.selected_objects if group.is_group(o) and o.btm_group.kind == 'PLAIN']


def _assemble_meshes(context):
    meshes = _meshes(context)
    for source in _import_groups(context):
        meshes += [m for m in group.members(source) if m.type in group.MEMBER_TYPES and m not in meshes]
    return meshes


class BTM_OT_GroupCreate(bpy.types.Operator):
    """Junta as peças selecionadas num grupo que se move como uma coisa só (as peças continuam separadas)"""
    bl_idname = "caffmob.group_create"
    bl_label = "Criar grupo"
    bl_options = {'REGISTER', 'UNDO'}

    name: bpy.props.StringProperty(name="Nome", default="Grupo")  # type: ignore

    @classmethod
    def poll(cls, context):
        if not _meshes(context):
            cls.poll_message_set(tr("Selecione as peças do grupo"))
            return False
        return True

    def invoke(self, context, event):
        names = [o.name for o in _meshes(context)]
        suggested = grouping.suggest(names)
        self.name = suggested[0][0] if len(suggested) == 1 else "Grupo"
        return context.window_manager.invoke_props_dialog(self)

    def execute(self, context):
        objs = _meshes(context)
        created = group.create_group(objs, 'PLAIN', self.name or "Grupo")
        if created is None:
            return {'CANCELLED'}
        for obj in context.selected_objects:
            obj.select_set(False)
        created.select_set(True)
        context.view_layer.objects.active = created
        self.report({'INFO'}, tr("Grupo {} com {} peça(s)").format(created.name, len(objs)))
        return {'FINISHED'}


def _active_group(context):
    obj = context.active_object
    if obj is not None:
        obj = next((c for c in obj.children if leaf.pivot_of(c) == obj), obj)
    while obj is not None and not group.is_group(obj):
        obj = obj.parent
    return obj


class BTM_OT_GroupDissolve(bpy.types.Operator):
    """Desfaz o grupo: as peças voltam soltas, com nome e material intactos"""
    bl_idname = "caffmob.group_dissolve"
    bl_label = "Desfazer grupo"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return _active_group(context) is not None

    def execute(self, context):
        target = _active_group(context)
        name = target.name
        inner = [o for o in target.children_recursive if group.is_group(o)]   # esquadria: as folhas (sob o pivô)
        for obj in inner + [target]:
            if obj.btm_aggregate.is_aggregate:
                convert.unconvert(obj)
        count = 0
        for obj in inner + [target]:
            count += len(group.ungroup(obj))
        self.report({'INFO'}, tr("Grupo {} desfeito: {} peça(s)").format(name, count))
        return {'FINISHED'}


class BTM_PG_AssembleRow(bpy.types.PropertyGroup):
    label: bpy.props.StringProperty()  # type: ignore
    names: bpy.props.StringProperty()  # type: ignore        # nomes das peças separados por "\n"
    count: bpy.props.IntProperty()  # type: ignore
    role: bpy.props.EnumProperty(name="Papel", items=ROLE_ITEMS)  # type: ignore


class BTM_OT_WindowAssemble(bpy.types.Operator):
    """Monta a janela ou porta a partir das peças selecionadas: sugere a esquadria e as folhas pelo nome das peças"""
    bl_idname = "caffmob.window_assemble"
    bl_label = "Montar esquadria"
    bl_options = {'REGISTER', 'UNDO'}

    rows: bpy.props.CollectionProperty(type=BTM_PG_AssembleRow)  # type: ignore
    name: bpy.props.StringProperty(name="Nome", default="Janela")  # type: ignore

    @classmethod
    def poll(cls, context):
        if not _assemble_meshes(context):
            cls.poll_message_set(tr("Selecione as peças do grupo"))
            return False
        return True

    def invoke(self, context, event):
        self._suggest(context)
        return context.window_manager.invoke_props_dialog(self, width=380)

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "name")
        col = layout.column(align=True)
        for row in self.rows:
            line = col.row(align=True)
            line.label(text=tr("{} ({} peças)").format(row.label, row.count))
            line.prop(row, "role", text="")

    def execute(self, context):
        if not self.rows:            # chamada sem diálogo (scripts e testes): usa a sugestão
            self._suggest(context)
        frame_names = [n for r in self.rows if r.role == 'FRAME' for n in r.names.split("\n")]
        objs = {o.name: o for o in _assemble_meshes(context)}
        for source in _import_groups(context):
            group.ungroup(source)            # as peças saem do grupo da importação para não sobrar um grupo vazio
        frame = group.create_group([objs[n] for n in frame_names if n in objs], 'FRAME', self.name or "Janela")
        if frame is None:
            self.report({'WARNING'}, tr("Escolha ao menos um grupo como esquadria"))
            return {'CANCELLED'}
        leaves = []
        for row in self.rows:
            if row.role not in ('SLIDE', 'SWING'):
                continue
            parts = [objs[n] for n in row.names.split("\n") if n in objs]
            sash = group.create_group(parts, 'LEAF', row.label)
            if sash is None:
                continue
            world = sash.matrix_world.copy()
            sash.parent = frame
            sash.matrix_parent_inverse = frame.matrix_world.inverted()
            sash.matrix_world = world
            leaves.append((sash, row.role))
        context.view_layer.update()
        for sash, role in leaves:
            if role == 'SLIDE':
                leaf.make_leaf(sash, frame, 'SLIDE', slide_dir='POS_X', travel=0.5)
                direction = leaf.default_slide_dir(sash)
                if direction != sash.btm_aggregate.slide_dir:
                    sash.btm_aggregate.slide_dir = direction        # o update refaz o pivô e mede o curso livre
            else:
                leaf.make_leaf(sash, frame, 'SWING')
        for obj in context.selected_objects:
            obj.select_set(False)
        frame.select_set(True)
        context.view_layer.objects.active = frame
        self.report({'INFO'}, tr("{}: esquadria com {} peça(s) e {} folha(s)").format(
            frame.name, len(frame_names), len(leaves)))
        return {'FINISHED'}

    def _suggest(self, context):
        self.rows.clear()
        for label, role, names in grouping.suggest([o.name for o in _assemble_meshes(context)]):
            row = self.rows.add()
            row.label, row.names, row.count = label, "\n".join(names), len(names)
            row.role = 'FRAME' if role == 'FRAME' else 'SLIDE'


classes = (BTM_OT_GroupCreate, BTM_OT_GroupDissolve, BTM_PG_AssembleRow, BTM_OT_WindowAssemble)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        if cls.is_registered:
            bpy.utils.unregister_class(cls)
