"""U: criar componente a partir da seleção (feature 067, T064, T099; D-19, RF-045 a RF-048, CMP-01).

`caffmob.component_from_selection` cria um armário autoral (`ops_authored.adopt`) num passo de Undo, planejando só a
seleção estrutural:
- as raízes são os selecionados sem ancestral selecionado; a decoração filha fica na hierarquia, sem cadastro e sem
  varredura de RNA;
- parentesco em lote, com o guarda de colisão suspenso, um `view_layer.update` no fim e rollback em exceção;
- limite explícito de 512 selecionados.

Recusa com motivo (`CANCELLED`, hierarquia intacta): menos de 2 malhas, dado linked, peça de módulo ou de outro
armário autoral, pai fora da seleção, constraint, animação, modificador apontando para fora da seleção. Com um armário
autoral ativo, o diálogo pede a escolha entre agregar ao ativo e criar um conjunto pai.

O atalho U mora no keymap "Object Mode" (nunca no "3D View" genérico: Edit Mode continua com o UV Unwrap, e campo de
texto não chega ao keymap). Sem seleção compatível, o evento passa ao Blender (`PASS_THROUGH`). O registro é
idempotente: recarregar o addon deixa um único item, que o usuário pode remapear.
"""

import bpy  # type: ignore

from ..data.i18n import N_, tr
from . import ops_authored

MAX_SELECTED = 512
_keymaps = []

MODE_ITEMS = (
    ('NEW', N_("Novo componente"), N_("Cria um armário autoral com as raízes selecionadas")),
    ('AGGREGATE', N_("Agregar ao ativo"), N_("As outras raízes entram como membros do armário ativo")),
    ('PARENT', N_("Criar conjunto pai"), N_("Um vazio novo vira pai de tudo, sem cadastro de membros")),
)


def structural_roots(selected):
    """Selecionados sem ancestral selecionado, na ordem da seleção."""
    chosen = set(selected)
    roots = []
    for obj in selected:
        parent = obj.parent
        while parent is not None and parent not in chosen:
            parent = parent.parent
        if parent is None:
            roots.append(obj)
    return roots


def _authored_of(obj):
    if obj is None:
        return None
    if obj.get('IS_AUTHORED_CABINET'):
        return obj
    return obj.btm_member.owner


def refusals(selected, roots, existing=None):
    """Motivos de recusa (msgids com `{}`), vazio = pode criar."""
    from ..selection import classify
    out = []
    if len(selected) > MAX_SELECTED:
        return [(N_("Seleção grande demais: {} objetos (o limite é {})"), (len(selected), MAX_SELECTED))]
    if sum(1 for o in selected if o.type == 'MESH') < 2:
        return [(N_("Selecione 2 ou mais chapas"), ())]
    chosen = set(selected)
    for obj in roots:
        if obj is existing:
            continue
        if obj.library is not None or obj.override_library is not None or (obj.data is not None
                                                                            and obj.data.library is not None):
            out.append((N_("{}: vem de outro arquivo (linked)"), (obj.name,)))
        if obj.parent is not None:
            out.append((N_("{}: tem pai fora da seleção ({})"), (obj.name, obj.parent.name)))
        if classify.module_root(obj)[0] is not None and not obj.get('IS_AUTHORED_CABINET'):
            out.append((N_("{}: já pertence a um módulo"), (obj.name,)))
        owner = obj.btm_member.owner
        if owner is not None and owner is not existing:
            out.append((N_("{}: já é membro de {}"), (obj.name, owner.name)))
        if obj.constraints:
            out.append((N_("{}: tem constraint"), (obj.name,)))
        anim = obj.animation_data
        if anim is not None and (anim.action is not None or len(anim.drivers)):
            out.append((N_("{}: tem animação ou driver"), (obj.name,)))
        for mod in obj.modifiers:
            for prop in mod.bl_rna.properties:
                if prop.type == 'POINTER':
                    target = getattr(mod, prop.identifier, None)
                    if isinstance(target, bpy.types.Object) and target not in chosen:
                        out.append((N_("{}: o modificador {} usa {}, fora da seleção"),
                                    (obj.name, mod.name, target.name)))
    return out


def _text(item):
    msgid, args = item
    return tr(msgid).format(*args)


class BTM_OT_ComponentFromSelection(bpy.types.Operator):
    """Cria um componente (armário autoral) com as chapas selecionadas, num passo de desfazer (U)"""
    bl_idname = 'caffmob.component_from_selection'
    bl_label = N_("Criar componente")
    bl_options = {'REGISTER', 'UNDO'}

    name: bpy.props.StringProperty(name=N_("Nome"), default="Componente")  # type: ignore
    mode: bpy.props.EnumProperty(name=N_("Componente existente"), items=MODE_ITEMS, default='NEW')  # type: ignore

    @classmethod
    def poll(cls, context):
        if context.mode != 'OBJECT':
            cls.poll_message_set(tr("Disponível em Object Mode"))
            return False
        # Sem duas chapas, o poll falha e o U do keymap passa ao Blender (RF-046).
        from ..target import capabilities, snapshot
        return capabilities.poll(cls, 'component_u', snapshot.current(context))

    def invoke(self, context, event):
        selected = list(context.selected_objects)
        if event is not None and event.type == 'U' and sum(1 for o in selected if o.type == 'MESH') < 2:
            return {'PASS_THROUGH'}             # sem seleção compatível, o U é do Blender
        existing = _authored_of(context.active_object)
        self.mode = 'AGGREGATE' if existing is not None else 'NEW'
        problems = refusals(selected, structural_roots(selected), existing)
        if problems:
            self.report({'ERROR'}, "; ".join(_text(p) for p in problems[:4]))
            return {'CANCELLED'}
        return context.window_manager.invoke_props_dialog(self, width=420)

    def draw(self, context):
        layout = self.layout
        selected = list(context.selected_objects)
        roots = structural_roots(selected)
        layout.prop(self, 'name')
        if _authored_of(context.active_object) is not None:
            layout.prop(self, 'mode', expand=True)
        layout.label(text=tr("Raiz: {}").format(tr("vazio novo") if self.mode != 'AGGREGATE'
                                                 else _authored_of(context.active_object).name))
        col = layout.column(align=True)
        col.label(text=tr("Peças ({}):").format(len(roots)))
        for obj in roots[:12]:
            col.label(text=obj.name, icon='MESH_CUBE' if obj.type == 'MESH' else 'OBJECT_DATA')
        if len(roots) > 12:
            col.label(text=tr("… e mais {}").format(len(roots) - 12))
        dependents = len(selected) - len(roots)
        layout.label(text=tr("Dependentes que seguem na hierarquia: {}").format(dependents), icon='OUTLINER')

    def execute(self, context):
        from ..collision import guard
        selected = list(context.selected_objects)
        roots = structural_roots(selected)
        existing = _authored_of(context.active_object) if self.mode != 'NEW' else None
        problems = refusals(selected, roots, existing)
        if problems:
            self.report({'ERROR'}, "; ".join(_text(p) for p in problems[:4]))
            return {'CANCELLED'}
        saved = {o: (o.parent, o.matrix_world.copy(), o.btm_member.owner, o.btm_member.role) for o in roots}
        created = []
        try:
            with guard.suspended():
                root = self._build(context, roots, existing, created)
            context.view_layer.update()
        except (ValueError, RuntimeError) as exc:
            for obj, (parent, world, owner, role) in saved.items():
                obj.parent = parent
                obj.matrix_world = world
                obj.btm_member.owner = owner
                obj.btm_member.role = role
            for obj in created:
                bpy.data.objects.remove(obj)
            self.report({'ERROR'}, tr(str(exc)))
            return {'CANCELLED'}
        for obj in selected:
            obj.select_set(False)
        root.select_set(True)
        context.view_layer.objects.active = root
        guard.accept(root)
        self.report({'INFO'}, tr("Componente {} criado com {} peça(s)").format(root.name, len(roots)))
        return {'FINISHED'}

    def _build(self, context, roots, existing, created):
        members = [o for o in roots if o is not existing]
        if self.mode == 'PARENT':
            root = bpy.data.objects.new(self.name or "Conjunto", None)
            context.collection.objects.link(root)
            created.append(root)
            for obj in members:
                world = obj.matrix_world.copy()
                obj.parent = root
                obj.matrix_world = world
            return root
        if existing is not None:
            for obj in members:
                ops_authored.set_member(obj, existing, 'CARCASS', reparent=True)
            return existing
        before = set(bpy.data.objects)
        root = ops_authored.adopt(None, members)
        created.extend(o for o in bpy.data.objects if o not in before)
        root.name = self.name or root.name
        return root


classes = (BTM_OT_ComponentFromSelection,)


def register_keymap():
    """Um único U no "Object Mode", também depois de recarregar o addon (RF-046)."""
    unregister_keymap()
    wm = bpy.context.window_manager
    kc = wm.keyconfigs.addon if wm else None
    if kc is None:
        return
    km = kc.keymaps.new(name='Object Mode', space_type='EMPTY')
    for item in [i for i in km.keymap_items if i.idname == BTM_OT_ComponentFromSelection.bl_idname]:
        km.keymap_items.remove(item)
    _keymaps.append((km, km.keymap_items.new(BTM_OT_ComponentFromSelection.bl_idname, 'U', 'PRESS')))


def unregister_keymap():
    for km, kmi in _keymaps:
        try:
            km.keymap_items.remove(kmi)
        except (ReferenceError, RuntimeError):
            pass
    _keymaps.clear()


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    register_keymap()


def unregister():
    unregister_keymap()
    for cls in reversed(classes):
        if cls.is_registered:
            bpy.utils.unregister_class(cls)
