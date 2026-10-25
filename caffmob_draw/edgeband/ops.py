"""Operadores da fita de borda (feature 067, T072; RF-080, RF-082, RF-084).

`caffmob.edgeband_apply`, num passo de Undo:
- sem fita no escopo: "Criar e aplicar fita de borda" cria as faixas das bordas expostas e aplica o material;
- com fita em todas as bordas: "Mudar cor da fita" só troca o material ou a cor lisa;
- caso misto: lista as bordas faltantes, cria nelas e muda a cor das existentes.
Repetir não duplica: a faixa é identificada pelas bordas que cobre. O diálogo mostra as bordas com realce na viewport
e deixa escolher quais entram antes de gerar. O escopo é o componente ou só a peça selecionada.
"""

import bpy  # type: ignore
from mathutils import Vector  # type: ignore

from ..data.i18n import N_, tr
from . import build, core, pieces, sync

LABELS = {core.CREATE: N_("Criar e aplicar fita de borda"), core.CHANGE: N_("Mudar cor da fita"),
          core.MIXED: N_("Criar nas bordas faltantes ({}) e mudar a cor")}
_preview = {'handle': None, 'tris': []}


def scope_keys(owner, piece=None, faces=None):
    faces = sync.exposed_faces(owner) if faces is None else faces
    if piece is None or piece is owner:
        return sorted(faces)
    from ..cutting import part_sources
    uid = str(piece.get(part_sources.UID_PROP) or piece.name)
    return sorted(k for k in faces if k.split('|')[0] == uid)


def existing_keys(owner):
    return {k for obj in pieces.bands_of(owner) for k in core.loads(obj.btm_edgeband.edge_keys)}


def state_for(owner, piece=None):
    """(estado, faltantes) do botão da fita no escopo (para o painel e o rótulo)."""
    if owner is None or not pieces.bands_of(owner):
        return core.CREATE, []           # sem faixa nenhuma: criar, sem precisar das bordas (fora do custo do painel)
    return core.label_state(scope_keys(owner, piece), existing_keys(owner))


def label(state, missing):
    return tr(LABELS[state]).format(len(missing)) if state == core.MIXED else tr(LABELS[state])


def _face_tris(owner, faces):
    out = []
    world = owner.matrix_world
    for face in faces:
        a, b = face.plane_axes
        corners = []
        for u, v in ((0, 0), (1, 0), (1, 1), (0, 1)):
            co = [0.0, 0.0, 0.0]
            co[face.axis] = face.pos + face.sign * build.OFFSET
            co[a], co[b] = face.rect[0][u], face.rect[1][v]
            corners.append(tuple(world @ Vector(co)))
        out += [corners[0], corners[1], corners[2], corners[0], corners[2], corners[3]]
    return out


def _draw():
    import gpu  # type: ignore
    from gpu_extras.batch import batch_for_shader  # type: ignore
    if not _preview['tris']:
        return
    shader = gpu.shader.from_builtin('UNIFORM_COLOR')
    batch = _preview.get('batch')
    if batch is None:
        batch = _preview['batch'] = batch_for_shader(shader, 'TRIS', {"pos": _preview['tris']})
    gpu.state.blend_set('ALPHA')
    shader.uniform_float("color", (1.0, 0.75, 0.1, 0.6))
    batch.draw(shader)
    gpu.state.blend_set('NONE')


def _stop_preview():
    if _preview['handle'] is not None:
        bpy.types.SpaceView3D.draw_handler_remove(_preview['handle'], 'WINDOW')
        _preview['handle'] = None
    _preview['tris'], _preview['batch'] = [], None


class BTM_PG_EdgeChoice(bpy.types.PropertyGroup):
    key: bpy.props.StringProperty()  # type: ignore
    label: bpy.props.StringProperty()  # type: ignore
    include: bpy.props.BoolProperty(name=N_("Incluir"), default=True)  # type: ignore


class BTM_OT_EdgeBandApply(bpy.types.Operator):
    """Cria a fita de borda visual nas bordas expostas e aplica o material, ou muda a cor da fita existente"""
    bl_idname = 'caffmob.edgeband_apply'
    bl_label = N_("Fita de borda")
    bl_options = {'REGISTER', 'UNDO'}

    material: bpy.props.StringProperty(name=N_("Material"))  # type: ignore
    use_color: bpy.props.BoolProperty(name=N_("Cor lisa"), default=False)  # type: ignore
    color: bpy.props.FloatVectorProperty(name=N_("Cor"), subtype='COLOR', size=4, min=0.0, max=1.0,
                                         default=(0.9, 0.9, 0.9, 1.0))  # type: ignore
    thickness: bpy.props.FloatProperty(name=N_("Espessura"), default=0.001, min=0.0001, max=0.01,
                                       unit='LENGTH')  # type: ignore
    scope: bpy.props.EnumProperty(name=N_("Escopo"), items=(
        ('COMPONENT', N_("Componente"), N_("Todas as bordas expostas do componente")),
        ('PART', N_("Peça selecionada"), N_("Só as bordas da peça selecionada"))), default='COMPONENT')  # type: ignore
    edge_keys: bpy.props.StringProperty(options={'HIDDEN', 'SKIP_SAVE'})  # type: ignore
    choices: bpy.props.CollectionProperty(type=BTM_PG_EdgeChoice, options={'SKIP_SAVE'})  # type: ignore

    @classmethod
    def poll(cls, context):
        if pieces.owner_for(context.active_object) is None:
            cls.poll_message_set(tr("Selecione um móvel, uma peça ou um objeto"))
            return False
        return True

    def _scope(self, context):
        obj = context.active_object
        owner = pieces.owner_for(obj)
        band = getattr(obj, 'btm_edgeband', None)
        piece = None if (band is not None and band.visual) or self.scope == 'COMPONENT' else obj
        return owner, piece

    def invoke(self, context, event):
        owner, piece = self._scope(context)
        faces = sync.exposed_faces(owner, create_uids=True)
        have = existing_keys(owner)
        self.choices.clear()
        names = {}
        for box, obj in pieces.boxes(owner):
            names[box.uid] = obj.name
        for key in scope_keys(owner, piece, faces):
            item = self.choices.add()
            uid, side = key.split('|')
            item.key, item.label = key, f"{names.get(uid, uid)} · {side}" + (" ✓" if key in have else "")
        _preview['tris'], _preview['batch'] = _face_tris(owner, [faces[c.key] for c in self.choices]), None
        if not bpy.app.background and _preview['handle'] is None:
            _preview['handle'] = bpy.types.SpaceView3D.draw_handler_add(_draw, (), 'WINDOW', 'POST_VIEW')
        return context.window_manager.invoke_props_dialog(self, width=420)

    def draw(self, context):
        layout = self.layout
        owner, piece = self._scope(context)
        state, missing = state_for(owner, piece)
        layout.label(text=label(state, missing), icon='MOD_EDGESPLIT')
        if state == core.MIXED:
            layout.label(text=tr("Bordas sem fita: {}").format(len(missing)), icon='INFO')
        layout.prop(self, 'use_color')
        if self.use_color:
            layout.prop(self, 'color')
        else:
            layout.prop_search(self, 'material', bpy.data, 'materials')
        layout.prop(self, 'thickness')
        col = layout.column(align=True)
        for item in self.choices:
            col.prop(item, 'include', text=item.label)

    def cancel(self, context):
        _stop_preview()

    def execute(self, context):
        _stop_preview()
        owner, piece = self._scope(context)
        if owner is None:
            return {'CANCELLED'}
        faces = sync.exposed_faces(owner, create_uids=True)
        wanted = core.loads(self.edge_keys) if self.edge_keys else (
            [c.key for c in self.choices if c.include] if len(self.choices) else scope_keys(owner, piece, faces))
        wanted = [k for k in wanted if k in faces]
        if not wanted:
            self.report({'WARNING'}, tr("Nenhuma borda exposta no escopo"))
            return {'CANCELLED'}
        material = bpy.data.materials.get(self.material) if self.material else None
        if material is None and not self.use_color:
            self.report({'WARNING'}, tr("Escolha o material ou a cor lisa da fita"))
            return {'CANCELLED'}
        state, missing = core.label_state(wanted, existing_keys(owner))
        known = {obj.btm_edgeband.uid for obj in pieces.bands_of(owner)}
        created = 0
        for band in core.merge([faces[k] for k in missing]):
            if band.uid in known:
                continue
            build.create(owner, band, self.thickness, material, tuple(self.color) if self.use_color else None)
            created += 1
        changed = 0
        for obj in pieces.bands_of(owner):
            data = obj.btm_edgeband
            if not set(core.loads(data.edge_keys)) & set(wanted):
                continue
            data.use_color = self.use_color
            if self.use_color:
                data.color = self.color
            elif material is not None:
                data.material = material
            build.apply_material(obj)
            changed += 1
        self.report({'INFO'}, tr("Fita: {} faixa(s) criada(s), {} com o acabamento novo").format(created, changed))
        return {'FINISHED'}


classes = (BTM_PG_EdgeChoice, BTM_OT_EdgeBandApply)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    _stop_preview()
    for cls in reversed(classes):
        if cls.is_registered:
            bpy.utils.unregister_class(cls)
