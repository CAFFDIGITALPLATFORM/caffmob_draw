"""Aplicar textura à seleção e ajustar o tamanho real dela (feature 014, T046; RN-04, RF-06).

- `caffmob.texture_apply`: aplica uma textura do catálogo aos alvos da seleção (`apply.targets`), como o arraste;
- `caffmob.texture_size`: muda a largura e a altura em mm da textura do objeto ativo, mantendo a proporção por
  padrão. Cria (ou reaproveita) o material de imagem com o tamanho novo e troca nas peças selecionadas que usam o
  material antigo. Vale para a textura do catálogo e para a imagem própria.
"""

import bpy  # type: ignore

from .. import compat
from ..customize.adapters import common
from ..data.i18n import N_, tr
from ..object_library import retexture
from . import apply

NO_TEXTURE = N_("O objeto ativo não tem textura de imagem")


def current_material(obj):
    """Material da peça (`Top Surface` da `GeoNodeCutpart`) ou do primeiro slot."""
    if obj is None:
        return None
    mod = common.gn_modifier(obj, 'GeoNodeCutpart')
    if mod is not None:
        mat = compat.get_gn_input(mod, 'Top Surface')
        if isinstance(mat, bpy.types.Material):
            return mat
    if obj.type == 'MESH' and obj.data.materials:
        return obj.data.materials[0]
    return None


def image_info(mat):
    """(caminho, largura, altura, girada, id do catálogo) de um material de imagem, ou None."""
    if mat is None or not mat.get(retexture.PATH_PROP):
        return None
    width, height = retexture._size_of(mat)
    return (mat[retexture.PATH_PROP], width, height, bool(mat.get(retexture.ROTATED_PROP, False)),
            str(mat.get(retexture.TEXTURE_ID_PROP, "")))


class BTM_OT_TextureApply(bpy.types.Operator):
    """Aplica a textura do catálogo à seleção (baixa antes, se precisar)"""
    bl_idname = "caffmob.texture_apply"
    bl_label = "Aplicar textura"
    bl_options = {'REGISTER', 'UNDO'}

    item_id: bpy.props.StringProperty(options={'HIDDEN'})  # type: ignore

    @classmethod
    def poll(cls, context):
        return bool(context.selected_objects)

    def execute(self, context):
        targets = []
        for obj in context.selected_objects:
            targets += apply.targets(obj)
        status, value = apply.apply(targets, self.item_id)
        if status == apply.ERROR:
            self.report({'WARNING'}, value)
            return {'CANCELLED'}
        if status == apply.QUEUED:
            return {'CANCELLED'}                          # aplica ao concluir o download, com o desfazer dele
        self.report({'INFO'}, tr("{} peça(s) com a textura").format(value))
        return {'FINISHED'}


def _update_width(self, context):
    if self.keep_ratio and self.ratio > 0 and not self.updating:
        self.updating = True
        self.height_mm = self.width_mm / self.ratio
        self.updating = False


def _update_height(self, context):
    if self.keep_ratio and self.ratio > 0 and not self.updating:
        self.updating = True
        self.width_mm = self.height_mm * self.ratio
        self.updating = False


class BTM_OT_TextureSize(bpy.types.Operator):
    """Muda quanto a textura mede de verdade (largura e altura em mm) nas peças selecionadas"""
    bl_idname = "caffmob.texture_size"
    bl_label = "Tamanho real da textura"
    bl_options = {'REGISTER', 'UNDO'}

    width_mm: bpy.props.FloatProperty(name="Largura (mm)", min=1.0, max=100000.0, default=600.0,
                                      update=_update_width)  # type: ignore
    height_mm: bpy.props.FloatProperty(name="Altura (mm)", min=1.0, max=100000.0, default=600.0,
                                       update=_update_height)  # type: ignore
    keep_ratio: bpy.props.BoolProperty(name="Manter a proporção", default=True)  # type: ignore
    ratio: bpy.props.FloatProperty(default=0.0, options={'HIDDEN', 'SKIP_SAVE'})  # type: ignore  # 0: sem diálogo
    updating: bpy.props.BoolProperty(default=False, options={'HIDDEN', 'SKIP_SAVE'})  # type: ignore

    @classmethod
    def poll(cls, context):
        return image_info(current_material(context.active_object)) is not None

    def invoke(self, context, event):
        _path, width, height, _rot, _tid = image_info(current_material(context.active_object))
        self.updating = True
        self.width_mm, self.height_mm = width, height
        self.updating = False
        self.ratio = width / height if height else 1.0
        return context.window_manager.invoke_props_dialog(self)

    def execute(self, context):
        old = current_material(context.active_object)
        info = image_info(old)
        if info is None:
            self.report({'WARNING'}, tr(NO_TEXTURE))
            return {'CANCELLED'}
        path, _w, _h, rotated, texture_id = info
        new = retexture.image_material(path, self.width_mm, self.height_mm, rotated=rotated, texture_id=texture_id)
        objs = {o.name: o for o in list(context.selected_objects) + [context.active_object] if o is not None}
        changed = 0
        for obj in objs.values():
            if current_material(obj) is old and common.set_cutpart_material(obj, new):
                apply._remember(obj, new)
                changed += 1
        self.report({'INFO'}, tr("{} peça(s) com a textura em {:g} × {:g} mm").format(changed, self.width_mm,
                                                                                    self.height_mm))
        return {'FINISHED'}


classes = (BTM_OT_TextureApply, BTM_OT_TextureSize)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        if cls.is_registered:
            bpy.utils.unregister_class(cls)
