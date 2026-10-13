"""Operadores da biblioteca de objetos (feature 009, T027-T029; RN-10 a RN-12, D-10 a D-12).

- `caffmob.object_insert`: insere um item no cursor 3D; interativo, a raiz acompanha o mouse no plano do chão, o
  clique solta (um passo de desfazer), e Esc ou o botão direito cancelam e removem o item (RF-06);
- `caffmob.object_library_remove`: apaga um item do usuário (os embutidos não saem);
- `caffmob.object_library_add`: acrescenta a seleção ou um arquivo à biblioteca do usuário (categoria, nome, origem,
  licença; nome repetido: Renomear ou Substituir);
- `caffmob.object_retexture_finish` / `caffmob.object_retexture_image`: acabamento do plugin ou imagem própria, na
  parte selecionada ou no item inteiro.

Um item é indicado por uma chave de texto: `"<U|B>:<categoria>:<item_id>"` (U = do usuário, B = embutido).
"""

import os

import bpy  # type: ignore
from bpy_extras import view3d_utils  # type: ignore
from bpy_extras.io_utils import ImportHelper  # type: ignore
from mathutils import Vector, geometry  # type: ignore

from ..data.i18n import tr
from . import catalog, item_io, retexture, store


def item_key(item):
    return "{}:{}:{}".format('U' if item.user else 'B', item.entry.category, item.entry.item_id)


def _window_region(area, x, y):
    """Região WINDOW da área sob o mouse (na vista quádrupla, a que contém o ponto); senão a maior."""
    regions = [r for r in area.regions if r.type == 'WINDOW']
    inside = [r for r in regions if r.x <= x < r.x + r.width and r.y <= y < r.y + r.height]
    return (inside or sorted(regions, key=lambda r: r.width * r.height, reverse=True) or [None])[0]


def find_item(key):
    items, _warnings = item_io.all_items()
    return next((i for i in items if item_key(i) == key), None)


def _scope_objects(context, scope):
    """Malhas da parte selecionada ou do item inteiro do objeto ativo."""
    active = context.active_object
    if scope == 'ITEM' and active is not None:
        root = item_io.root_of(active) or active
        return item_io.tree(root)
    return list(context.selected_objects) or ([active] if active is not None else [])


SCOPE_ITEMS = [('PART', "Parte selecionada", "Só as peças selecionadas"),
               ('ITEM', "Item inteiro", "Todas as peças do item do objeto ativo")]


# Inserir -------------------------------------------------------------------------------------------------------

class BTM_OT_ObjectInsert(bpy.types.Operator):
    """Insere o objeto da biblioteca: ele acompanha o mouse, um clique solta e Esc cancela"""
    bl_idname = "caffmob.object_insert"
    bl_label = "Inserir objeto"
    bl_options = {'REGISTER', 'UNDO'}

    key: bpy.props.StringProperty(options={'HIDDEN'})  # type: ignore
    # Feature 014 (T033): vindo do arraste da biblioteca, o botão já está pressionado e a soltura confirma.
    from_drag: bpy.props.BoolProperty(default=False, options={'HIDDEN', 'SKIP_SAVE'})  # type: ignore

    def _load(self, context):
        item = find_item(self.key)
        if item is None:
            self.report({'ERROR'}, tr("Objeto não encontrado na biblioteca"))
            return None
        try:
            root, self._loaded = item_io.insert(context, item, location=context.scene.cursor.location.copy())
        except ValueError as exc:
            self.report({'ERROR'}, str(exc))
            return None
        for obj in context.selected_objects:
            obj.select_set(False)
        root.select_set(True)
        context.view_layer.objects.active = root
        self._root, self._name = root, item.entry.name
        return root

    def execute(self, context):
        """Sem interação (scripts e testes): insere no cursor 3D."""
        if self._load(context) is None:
            return {'CANCELLED'}
        self.report({'INFO'}, tr("{} inserido").format(self._name))
        return {'FINISHED'}

    def invoke(self, context, event):
        if context.area is None or context.area.type != 'VIEW_3D':
            return self.execute(context)
        if self._load(context) is None:
            return {'CANCELLED'}
        self._plane_z = context.scene.cursor.location.z
        context.area.header_text_set(tr("Mova para posicionar · Clique solta · Esc cancela"))
        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}

    def _follow(self, context, event):
        region, rv3d = context.region, context.region_data
        coord = (event.mouse_region_x, event.mouse_region_y)
        if rv3d is None and context.area is not None:      # invocado pela barra lateral: a região da vista (DT-01)
            region = _window_region(context.area, event.mouse_x, event.mouse_y)
            rv3d = region.data if region is not None else None
            if region is not None:
                coord = (event.mouse_x - region.x, event.mouse_y - region.y)
        if region is None or rv3d is None:
            return
        origin = view3d_utils.region_2d_to_origin_3d(region, rv3d, coord)
        direction = view3d_utils.region_2d_to_vector_3d(region, rv3d, coord)
        hit = geometry.intersect_line_plane(origin, origin + direction * 1000.0, Vector((0, 0, self._plane_z)),
                                            Vector((0, 0, 1)))
        if hit is not None:
            self._root.location = (hit.x, hit.y, self._plane_z)

    def _end(self, context):
        if context.area is not None:
            context.area.header_text_set(None)

    def modal(self, context, event):
        if event.type == 'MOUSEMOVE':
            self._follow(context, event)
            return {'RUNNING_MODAL'}
        if event.type == 'LEFTMOUSE' and (event.value == 'PRESS' or (self.from_drag and event.value == 'RELEASE')):
            self._end(context)
            self.report({'INFO'}, tr("{} inserido").format(self._name))
            return {'FINISHED'}
        if event.type in {'ESC', 'RIGHTMOUSE'} and event.value == 'PRESS':
            self._discard(context)
            return {'CANCELLED'}
        if event.type in {'MIDDLEMOUSE', 'WHEELUPMOUSE', 'WHEELDOWNMOUSE'}:
            return {'PASS_THROUGH'}             # girar e aproximar a vista continua funcionando
        return {'RUNNING_MODAL'}

    def _discard(self, context):
        self._end(context)
        for obj in reversed(self._loaded):
            try:
                if obj.name in bpy.data.objects:
                    bpy.data.objects.remove(obj, do_unlink=True)
            except ReferenceError:
                pass

    def cancel(self, context):
        """O Blender interrompeu o modal: sai como no Esc, sem deixar os objetos carregados (DT-03)."""
        self._discard(context)


class BTM_OT_ObjectLibraryRemove(bpy.types.Operator):
    """Apaga o objeto da sua biblioteca (os objetos que vêm com o plugin não saem)"""
    bl_idname = "caffmob.object_library_remove"
    bl_label = "Remover da biblioteca"
    bl_options = {'REGISTER'}

    key: bpy.props.StringProperty(options={'HIDDEN'})  # type: ignore

    @classmethod
    def poll(cls, context):
        return True

    def invoke(self, context, event):
        return context.window_manager.invoke_confirm(self, event, title=tr("Remover da biblioteca"),
                                                     message=tr("Apagar este objeto da sua biblioteca?"),
                                                     confirm_text=tr("Remover"), icon='WARNING')

    def execute(self, context):
        item = find_item(self.key)
        if item is None:
            self.report({'ERROR'}, tr("Objeto não encontrado na biblioteca"))
            return {'CANCELLED'}
        try:
            store.delete(item)
        except PermissionError:
            self.report({'ERROR'}, tr("Os objetos que vêm com o plugin não podem ser removidos"))
            return {'CANCELLED'}
        except OSError as exc:
            self.report({'ERROR'}, str(exc))
            return {'CANCELLED'}
        self.report({'INFO'}, tr("{} removido da biblioteca").format(item.entry.name))
        return {'FINISHED'}


# Acrescentar ---------------------------------------------------------------------------------------------------

class BTM_OT_ObjectLibraryAdd(bpy.types.Operator):
    """Acrescenta a seleção (ou um arquivo 3D) à sua biblioteca de objetos, com a folha, as chapas e as texturas"""
    bl_idname = "caffmob.object_library_add"
    bl_label = "Acrescentar à biblioteca"
    bl_options = {'REGISTER', 'UNDO'}

    name: bpy.props.StringProperty(name="Nome", default="Meu objeto")  # type: ignore
    category: bpy.props.EnumProperty(name="Categoria", items=catalog.CATEGORY_ITEMS, default='OTHER')  # type: ignore
    source: bpy.props.StringProperty(name="Origem", default="Uso próprio",
                                     description="De onde veio o modelo (ex.: 3D Warehouse: autor)")  # type: ignore
    license_text: bpy.props.StringProperty(name="Licença", default="Uso próprio")  # type: ignore
    author: bpy.props.StringProperty(name="Autor")  # type: ignore
    filepath: bpy.props.StringProperty(name="Arquivo", subtype='FILE_PATH',
                                       description="Vazio = usa a seleção atual")  # type: ignore
    duplicate: bpy.props.EnumProperty(
        name="Nome repetido",
        items=[('RENAME', "Renomear", "Salva como \"<nome> 2\""), ('REPLACE', "Substituir", "Regrava o objeto")],
        default='RENAME')  # type: ignore

    def invoke(self, context, event):
        active = context.active_object
        if active is not None and not self.filepath:
            root = item_io.root_of(active)
            self.name = (root or active).name.split(".")[0]
            if root is not None:
                self.category = root.btm_object_item.category
        return context.window_manager.invoke_props_dialog(self, width=360)

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        for prop in ("name", "category", "source", "author", "license_text", "filepath"):
            layout.prop(self, prop)
        if self.name in item_io.existing_names(self.category):
            layout.prop(self, "duplicate")

    def _objects(self, context):
        if not self.filepath:
            return list(context.selected_objects)
        path = bpy.path.abspath(self.filepath)
        before = set(bpy.data.objects)
        result = bpy.ops.caffmob.import_model(filepath=path)
        if 'FINISHED' not in result:
            return []
        return [o for o in bpy.data.objects if o not in before]

    def execute(self, context):
        name = self.name.strip()
        if not name:
            self.report({'ERROR'}, tr("Dê um nome ao objeto"))
            return {'CANCELLED'}
        objs = self._objects(context)
        if not objs:
            self.report({'ERROR'}, tr("Selecione o objeto ou escolha um arquivo"))
            return {'CANCELLED'}
        replace_id = None
        existing = item_io.existing_names(self.category)
        if name in existing:
            if self.duplicate == 'REPLACE':
                items, _w = item_io.all_items()
                replace_id = next(i.entry.item_id for i in items if i.user and i.entry.category == self.category
                                  and i.entry.name == name)
            else:
                name = store.unique_name(existing, name)
        root = item_io.prepare_root(objs, name)
        if root is None:
            self.report({'ERROR'}, tr("A seleção não tem malhas"))
            return {'CANCELLED'}
        item, errors = item_io.save(context, root, name, self.category, self.source, self.license_text, self.author,
                                    replace_id=replace_id)
        if errors:
            self.report({'ERROR'}, "; ".join(errors))
            return {'CANCELLED'}
        self.report({'INFO'}, tr("{} acrescentado à biblioteca em {}").format(
            item.entry.name, tr(dict((c[0], c[1]) for c in catalog.CATEGORIES)[self.category])))
        return {'FINISHED'}


# Retexturizar --------------------------------------------------------------------------------------------------

def _finish_items(self, context):
    return [(name, name, "") for name in retexture.finish_names()] or [('NONE', tr("Nenhum acabamento"), "")]


class BTM_OT_ObjectRetextureFinish(bpy.types.Operator):
    """Troca o material pelo acabamento escolhido (das bibliotecas do plugin ou do arquivo)"""
    bl_idname = "caffmob.object_retexture_finish"
    bl_label = "Retexturizar com acabamento"
    bl_options = {'REGISTER', 'UNDO'}
    bl_property = "finish"

    finish: bpy.props.EnumProperty(name="Acabamento", items=_finish_items)  # type: ignore
    scope: bpy.props.EnumProperty(name="Aplicar em", items=SCOPE_ITEMS, default='PART')  # type: ignore

    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    def invoke(self, context, event):
        context.window_manager.invoke_search_popup(self)
        return {'RUNNING_MODAL'}

    def execute(self, context):
        changed = retexture.apply_finish(_scope_objects(context, self.scope), self.finish)
        if not changed:
            self.report({'WARNING'}, tr("Nada mudou: acabamento ausente ou seleção sem malhas"))
            return {'CANCELLED'}
        self.report({'INFO'}, tr("{} peça(s) com {}").format(changed, self.finish))
        return {'FINISHED'}


class BTM_OT_ObjectRetextureImage(bpy.types.Operator, ImportHelper):
    """Aplica uma imagem sua como textura, em escala real (projeção em caixa, não precisa de UV)"""
    bl_idname = "caffmob.object_retexture_image"
    bl_label = "Retexturizar com imagem"
    bl_options = {'REGISTER', 'UNDO'}

    filter_glob: bpy.props.StringProperty(default="*.png;*.jpg;*.jpeg;*.tif;*.tiff;*.webp",
                                          options={'HIDDEN'})  # type: ignore
    size_mm: bpy.props.FloatProperty(name="Tamanho da imagem (mm)", default=600.0, min=1.0, max=100000.0,
                                     description="Quanto a imagem mede de verdade")  # type: ignore
    scope: bpy.props.EnumProperty(name="Aplicar em", items=SCOPE_ITEMS, default='PART')  # type: ignore

    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    def execute(self, context):
        if not os.path.isfile(self.filepath):
            self.report({'ERROR'}, tr("Escolha uma imagem"))
            return {'CANCELLED'}
        try:
            changed = retexture.apply_image(_scope_objects(context, self.scope), self.filepath, self.size_mm)
        except RuntimeError as exc:
            self.report({'ERROR'}, tr("Não foi possível abrir a imagem: {}").format(exc))
            return {'CANCELLED'}
        if not changed:
            self.report({'WARNING'}, tr("A seleção não tem malhas"))
            return {'CANCELLED'}
        self.report({'INFO'}, tr("{} peça(s) com a textura {}").format(changed, os.path.basename(self.filepath)))
        return {'FINISHED'}


classes = (BTM_OT_ObjectInsert, BTM_OT_ObjectLibraryRemove, BTM_OT_ObjectLibraryAdd, BTM_OT_ObjectRetextureFinish,
           BTM_OT_ObjectRetextureImage)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        if cls.is_registered:
            bpy.utils.unregister_class(cls)
